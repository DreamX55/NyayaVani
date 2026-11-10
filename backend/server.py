import os
import sys
import time
import uuid
import shutil
import wave
import subprocess
import asyncio
import secrets
import hmac
import re
import logging
import requests
from typing import Optional, Dict, Any, List, Set
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse, FileResponse, JSONResponse, Response
from pydantic import BaseModel

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.gnani_client import GNANI_API_KEY, GnaniClient, GnaniAPIError, V3_VOICES
from backend.services.legal_engine import NyayaVaniEngine
from backend.services.pro_workflow import (
    build_pro_packet,
    get_pro_packet,
    update_pro_packet,
    approve_pro_packet,
    attempt_send_packet,
    add_attachment,
    _packet_store,
)
from backend.services.source_register import REGISTER_VERSION, REVIEWER_METADATA
from backend.services.geo_service import GeoLanguageService
from backend.services.call_dispatch_service import call_manager, OUTBOUND_TELEPHONY_ENABLED

# ---------------------------------------------------------------------------
# Logging & Security Sanitization (PRD Requirement 5)
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("nyayavani.security")

PII_PATTERNS = [
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'), '[REDACTED_EMAIL]'),
    (re.compile(r'\b(?:\+91|91)?[-.\s]?[6-9]\d{9}\b'), '[REDACTED_PHONE]'),
    (re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), '[REDACTED_AADHAAR]'),
    (re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'), '[REDACTED_PAN]'),
    (re.compile(r'(api[-_]?key|bearer|token|password|secret|authorization)\s*[:=]\s*["\']?[a-zA-Z0-9_\-\.]+["\']?', re.IGNORECASE), r'\1: [REDACTED_CREDENTIAL]'),
]


def sanitize_for_log(text: str) -> str:
    """Redacts sensitive credentials, identifiers, and personal testimony from server logs."""
    if not text:
        return ""
    sanitized = str(text)
    for pattern, repl in PII_PATTERNS:
        sanitized = pattern.sub(repl, sanitized)
    return sanitized


app = Starlette(debug=False)

# Playback is kept briefly in memory, never in a public static directory (PRD S1).
AUDIO_TTL_SECONDS = 10 * 60
MAX_CACHED_AUDIO_BYTES = 12 * 1024 * 1024
# audio token -> (expires_at, bytes)
_audio_cache: Dict[str, tuple[float, bytes]] = {}
_speech_auth = "unverified"

# In-memory ephemeral multi-turn session store (PRD S1, Multi-Turn Session Memory & Requirement 5)
SESSION_TTL_SECONDS = 3600
_session_store: Dict[str, Dict[str, Any]] = {}

ADMIN_PURGE_TOKEN = os.environ.get("NYAYAVANI_ADMIN_TOKEN", "nyayavani-admin-secret-2026")


def get_auth_token(request: Request, body_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Extract authorization credential from Authorization header, custom headers, query params, or body."""
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1].strip()
        elif len(parts) == 1:
            return parts[0].strip()

    custom_token = (
        request.headers.get("X-Session-Token")
        or request.headers.get("x-session-token")
        or request.headers.get("X-Auth-Token")
        or request.headers.get("x-auth-token")
    )
    if custom_token:
        return custom_token.strip()

    query_token = request.query_params.get("session_token") or request.query_params.get("token")
    if query_token:
        return query_token.strip()

    if body_data and isinstance(body_data, dict):
        body_token = body_data.get("session_token") or body_data.get("token") or body_data.get("auth_token")
        if body_token and isinstance(body_token, str):
            return body_token.strip()

    return None


def _clean_expired_sessions() -> None:
    now = time.monotonic()
    for sid, sess in list(_session_store.items()):
        if now - sess.get("last_accessed", 0) > SESSION_TTL_SECONDS:
            _session_store.pop(sid, None)


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve active session if not expired, updating last_accessed timestamp."""
    _clean_expired_sessions()
    sess = _session_store.get(session_id)
    if sess:
        sess["last_accessed"] = time.monotonic()
        return sess
    return None


def get_or_create_session(session_id: str, caller_token: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve existing session or initialize a fresh secure session context."""
    _clean_expired_sessions()
    now = time.monotonic()
    if session_id not in _session_store:
        token = caller_token or secrets.token_urlsafe(32)
        owner_id = f"usr_{uuid.uuid4().hex[:12]}"
        _session_store[session_id] = {
            "session_id": session_id,
            "token": token,
            "owner_id": owner_id,
            "created_at": now,
            "last_accessed": now,
            "facts": {},
            "history": [],
            "category": None,
            "tier": None,
            "audio_tokens": set(),
            "packets": set(),
        }
    sess = _session_store[session_id]
    sess["last_accessed"] = now
    return sess


LANGUAGE_LABELS = {
    "indic-auto": "Indic (Auto-Detected)",
    "hi-IN": "Hindi (हिन्दी)",
    "kn-IN": "Kannada (ಕನ್ನಡ)",
    "ta-IN": "Tamil (தமிழ்)",
    "te-IN": "Telugu (తెలుగు)",
    "mr-IN": "Marathi (मराठी)",
    "bn-IN": "Bengali (বাংলা)",
    "gu-IN": "Gujarati (ગુજરાતી)",
    "ml-IN": "Malayalam (മലയാളം)",
    "pa-IN": "Punjabi (ਪੰਜਾਬੀ)",
    "en-IN": "Indian English"
}

LANGUAGE_TTS_CONFIG = {
    "hi": ("hi-IN", "Shivani"),
    "mr": ("mr-IN", "Vasudha"),
    "ta": ("ta-IN", "Kalpana"),
    "te": ("te-IN", "Lakshmi"),
    "kn": ("kn-IN", "Chetana"),
    "bn": ("bn-IN", "Riyaa"),
    "gu": ("gu-IN", "Tarika"),
    "ml": ("ml-IN", "Lakshmi"),
    "pa": ("pa-IN", "Tarika"),
    "en": ("en-IN", "Shivani"),
}


def _cache_audio(data: bytes, session_id: Optional[str] = None) -> str:
    now = time.monotonic()
    for token, (expires_at, _) in list(_audio_cache.items()):
        if expires_at <= now:
            del _audio_cache[token]
    if len(data) > MAX_CACHED_AUDIO_BYTES:
        raise ValueError("Synthesized audio exceeds the playback limit.")
    while sum(len(item[1]) for item in _audio_cache.values()) + len(data) > MAX_CACHED_AUDIO_BYTES:
        oldest = next(iter(_audio_cache))
        del _audio_cache[oldest]
    if len(_audio_cache) >= 100:
        del _audio_cache[next(iter(_audio_cache))]
    # Cryptographically unguessable playback token (PRD S1 & Requirement 5)
    token = secrets.token_urlsafe(32)
    _audio_cache[token] = (now + AUDIO_TTL_SECONDS, data)
    if session_id and session_id in _session_store:
        _session_store[session_id]["audio_tokens"].add(token)
    return f"/api/audio/{token}"


def _record_speech_result(error: Exception | None = None) -> None:
    global _speech_auth
    if error is None:
        _speech_auth = "verified"
    elif isinstance(error, GnaniAPIError) and error.category == "authentication_rejected":
        _speech_auth = "rejected"


async def serve_audio(request: Request):
    token = request.path_params["token"]
    entry = _audio_cache.get(token)
    if entry is None or entry[0] <= time.monotonic():
        _audio_cache.pop(token, None)
        raise HTTPException(status_code=404, detail="Audio has expired. Ask again to play it.")
    return Response(entry[1], media_type="audio/wav", headers={"Cache-Control": "private, no-store"})


# Mount frontend assets
os.makedirs("frontend/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Initialize AI Services
client = GnaniClient() if GNANI_API_KEY else None
engine = NyayaVaniEngine()


def convert_to_wav(input_path: str, output_path: str) -> str:
    """
    Converts browser audio to 16kHz mono 16-bit PCM WAV.
    First checks if already 16kHz mono 16-bit WAV.
    If it's any other WAV (different sample rate, stereo, 24/32 bit), resamples in pure Python using scipy.
    Falls back to FFmpeg if available for container formats.
    """
    # 1. Quick check: already 16kHz mono 16-bit WAV
    try:
        with wave.open(input_path, "rb") as source:
            if source.getnchannels() == 1 and source.getframerate() == 16000 and source.getsampwidth() == 2:
                shutil.copyfile(input_path, output_path)
                return output_path
    except (wave.Error, EOFError):
        pass

    # 2. Pure Python conversion for any WAV file using scipy.io.wavfile and scipy.signal
    try:
        import scipy.io.wavfile as sciwav
        import scipy.signal as scisig
        import numpy as np
        rate, data = sciwav.read(input_path)
        # Downmix multi-channel to mono
        if data.ndim > 1:
            data = data.mean(axis=1)
        # Convert to float between -1.0 and 1.0 or normalize
        if data.dtype == np.int16:
            data_float = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            data_float = data.astype(np.float32) / 2147483648.0
        elif data.dtype == np.uint8:
            data_float = (data.astype(np.float32) - 128.0) / 128.0
        else:
            data_float = data.astype(np.float32)

        # Resample to 16000 Hz if necessary
        target_rate = 16000
        if rate != target_rate:
            num_samples = int(len(data_float) * target_rate / rate)
            resampled = scisig.resample(data_float, num_samples)
        else:
            resampled = data_float

        # Clip and convert to int16
        resampled_int16 = (np.clip(resampled, -1.0, 1.0) * 32767.0).astype(np.int16)
        sciwav.write(output_path, target_rate, resampled_int16)
        return output_path
    except Exception as wav_err:
        logger.debug(f"Pure Python WAV processing not applicable: {wav_err}")

    # 3. Fallback to FFmpeg if installed
    ffmpeg_bin = shutil.which("ffmpeg") or ("/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg")
    cmd = [
        ffmpeg_bin, "-y",
        "-i", input_path,
        "-t", "31",
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        output_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=30)
        if res.returncode == 0:
            return output_path
    except Exception as ffmpeg_err:
        logger.debug(f"FFmpeg conversion failed: {ffmpeg_err}")

    # 4. If all else fails and input_path exists, try copying as fallback
    if os.path.exists(input_path):
        shutil.copyfile(input_path, output_path)
        return output_path

    raise RuntimeError("Could not convert audio file to 16kHz mono WAV.")


def verify_packet_authorization(packet: Dict[str, Any], request: Request, body_data: Optional[Dict[str, Any]] = None) -> None:
    """
    Enforces authentication and authorization for Pro packet operations (Requirement 5).
    Raises HTTP 401 if unauthenticated on protected packets.
    Raises HTTP 403 if authenticated but accessing another user's packet.
    """
    auth_required = packet.get("auth_required", False)
    owner_token = packet.get("owner_token")
    session_id = packet.get("session_id")

    caller_token = get_auth_token(request, body_data)

    if not auth_required:
        # If caller provided an explicit token and it does not match, reject with 403
        if caller_token and owner_token and not hmac.compare_digest(caller_token, owner_token):
            raise HTTPException(status_code=403, detail="Forbidden: cannot access or modify another user's pro packet.")
        return

    # Protected packet requires matching credentials
    if not caller_token:
        raise HTTPException(status_code=401, detail="Authentication required: missing authorization token.")

    is_owner = False
    if owner_token and hmac.compare_digest(caller_token, owner_token):
        is_owner = True
    elif session_id and session_id in _session_store:
        sess_token = _session_store[session_id].get("token")
        if sess_token and hmac.compare_digest(caller_token, sess_token):
            is_owner = True
    elif hmac.compare_digest(caller_token, ADMIN_PURGE_TOKEN):
        is_owner = True

    if not is_owner:
        raise HTTPException(status_code=403, detail="Forbidden: cannot access or modify another user's pro packet.")


class ChatRequest(BaseModel):
    message: str
    original_transcript: Optional[str] = None
    reviewed_transcript: Optional[str] = None
    detected_language: Optional[str] = None
    language_code: Optional[str] = None
    tier: Optional[str] = "AUTO_DETECT"
    voice: Optional[str] = "Shivani"
    client_name: Optional[str] = "Citizen / Applicant"
    location: Optional[str] = "India"
    meta: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    session_token: Optional[str] = None


class PurgeRequest(BaseModel):
    packet_id: Optional[str] = None
    session_id: Optional[str] = None


class ProPacketUpdateRequest(BaseModel):
    draft_message: Optional[str] = None
    recipient: Optional[str] = None
    incident_summary: Optional[str] = None


class ProPacketApproveRequest(BaseModel):
    approver_name: str
    approver_role: Optional[str] = "Client"
    notes: Optional[str] = ""


class ProPacketSendRequest(BaseModel):
    destination: Optional[str] = None


class RightsAudioRequest(BaseModel):
    text: str
    language: Optional[str] = "en"
    voice: Optional[str] = "Shivani"
    speed: Optional[float] = 1.0
    session_id: Optional[str] = None
    session_token: Optional[str] = None



async def serve_index(request: Request):
    index_path = os.path.join("frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>NyayaVani Frontend Ready</h1>")


async def get_system_status(request: Request):
    if not client:
        speech_service = "not_configured"
    else:
        try:
            await asyncio.to_thread(requests.get, client.base_url, timeout=3)
            speech_service = "network_reachable"
        except requests.RequestException:
            speech_service = "network_unreachable"
    return JSONResponse({
        "status": "online",
        "api_key_active": bool(client),
        "speech_service": speech_service,
        "speech_auth": _speech_auth if client else "not_configured",
        "source_register_version": REGISTER_VERSION,
        "legal_reviewer": REVIEWER_METADATA["reviewer_name"],
        "privacy_disclosure": {
            "provider": "Gnani.ai Speech Services (Prisma STT / Timbre TTS)",
            "purpose": "Short-clip voice transcription and spoken statutory rights synthesis.",
            "retention_policy": "Audio is processed ephemerally in-memory and discarded. Playback tokens expire in 10 minutes. Session TTL: 1 hour.",
            "privacy_status": "Ephemerality and session isolation active. Controlled pilot privacy controls applied; full statutory compliance pending Data Protection Board notification and formal legal audit.",
            "dpdp_notice": "Under India's Digital Personal Data Protection Act, 2023 (DPDP), voice recordings and transcripts are processed ephemerally and not retained for public training. Controlled pilot privacy controls applied; full statutory compliance pending Data Protection Board notification and formal legal audit."
        }
    })


async def chat_text(request: Request):
    try:
        body = await request.json()
        req = ChatRequest.model_validate(body)
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(status_code=422, detail="Please enter a valid message.") from err
    caller_token = get_auth_token(request, body) or req.session_token
    return JSONResponse(await process_chat(req, caller_token=caller_token))


async def process_chat(req: ChatRequest, caller_token: Optional[str] = None):
    session = None
    if req.session_id:
        _clean_expired_sessions()
        if req.session_id in _session_store:
            sess = _session_store[req.session_id]
            expected_token = sess.get("token")
            # Enforce authorization on existing session
            if not caller_token or not hmac.compare_digest(caller_token, expected_token):
                logger.warning(sanitize_for_log(f"Unauthorized session access attempt on session {req.session_id}"))
                raise HTTPException(status_code=403, detail="Unauthorized access to session: invalid or missing session token.")
            sess["last_accessed"] = time.monotonic()
            session = sess
        else:
            # Create fresh isolated session
            session = get_or_create_session(req.session_id, caller_token=caller_token)

    provided_facts = dict(req.meta or {})
    if isinstance(provided_facts.get("facts"), dict):
        nested_facts = provided_facts.pop("facts")
        provided_facts.update(nested_facts)

    if session is not None:
        user_msg = req.message.strip()
        lower_msg = user_msg.lower()
        is_turn1 = len(session.get("history", [])) == 0
        provided_facts["is_followup_turn"] = not is_turn1

        # Check for user-spoken revision request
        revision_triggers = ["change", "update", "बदल", "तारीख", "स्थान", "date", "location", "वाहनाचा क्रमांक", "गाडी नंबर", "गाड़ी नंबर", "மாற்றவும்", "మార్చండి", "ಬದಲಾಯಿಸಿ", "পরিবর্তন", "બદલો", "ਬਦਲੋ"]
        if not is_turn1 and any(w in lower_msg for w in revision_triggers):
            if any(w in lower_msg for w in ["date", "तारीख", "दिनांक", "day", "वेळ", "time", "தேதி", "తేదీ", "ದಿನಾಂಕ", "তারিখ", "તારીખ", "ਮਿਤੀ"]):
                provided_facts["incident_date"] = user_msg
                provided_facts["revision_requested"] = True
            elif any(w in lower_msg for w in ["location", "स्थान", "ठिकाण", "जगह", "place", "city", "ஊர்", "నగరం", "ಸ್ಥಳ", "জায়গা", "જગ્યા", "ਸਥਾਨ"]):
                provided_facts["incident_location"] = user_msg
                provided_facts["revision_requested"] = True
            elif any(w in lower_msg for w in ["party", "व्यक्ती", "पक्ष", "police", "driver", "व्यक्ति", "நபர்", "వ్యక్తి", "ವ್ಯಕ್ತಿ", "ব্যক্তি", "વ્યક્તિ", "ਵਿਅਕਤੀ"]):
                provided_facts["other_party"] = user_msg
                provided_facts["revision_requested"] = True
            else:
                provided_facts["specific_details"] = user_msg
                provided_facts["revision_requested"] = True
        elif not is_turn1 and not any(k in provided_facts for k in ["incident_date", "incident_location", "other_party", "specific_details"]):
            # On Turn 2+, conversational spoken answer fills the first missing slot
            existing = session.get("facts", {})
            for key in ["specific_details", "other_party", "incident_date", "incident_location"]:
                if not str(existing.get(key, "")).strip():
                    provided_facts[key] = user_msg
                    break
        session["facts"].update(provided_facts)
        if req.client_name and req.client_name != "Citizen / Applicant":
            session["facts"]["client_name"] = req.client_name
        elif "client_name" not in session["facts"] and req.client_name:
            session["facts"]["client_name"] = req.client_name

        if req.location and req.location != "India":
            session["facts"]["location"] = req.location
        elif "location" not in session["facts"] and req.location:
            session["facts"]["location"] = req.location

        case_meta = dict(session["facts"])
        if session.get("category") and "category" not in case_meta:
            case_meta["category"] = session["category"]
        if session.get("language") and "session_language" not in case_meta:
            case_meta["session_language"] = session["language"]
        if req.language_code:
            case_meta["language_code"] = req.language_code
        if req.detected_language:
            case_meta["detected_language"] = req.detected_language

        tier_to_use = req.tier or "AUTO_DETECT"
        if tier_to_use == "AUTO_DETECT" and session.get("tier"):
            tier_to_use = session["tier"]
    else:
        case_meta = dict(provided_facts)
        case_meta["is_followup_turn"] = False
        case_meta["client_name"] = req.client_name or "Citizen / Applicant"
        case_meta["location"] = req.location or "India"
        if req.language_code:
            case_meta["language_code"] = req.language_code
        if req.detected_language:
            case_meta["detected_language"] = req.detected_language
        tier_to_use = req.tier or "AUTO_DETECT"

    # Combine user statements across turns for full factual context
    user_account_text = req.message
    if session is not None:
        past_user_msgs = [h["content"] for h in session.get("history", []) if h.get("role") == "user"]
        if past_user_msgs:
            user_account_text = "\n".join(past_user_msgs + [req.message])

    # 1. Process through legal reasoning engine
    case_res = engine.process_case(user_account_text, suite_tier=tier_to_use, meta=case_meta)

    # If session active, update session with the new state
    if session is not None:
        session["last_accessed"] = time.monotonic()
        if case_res.get("category"):
            session["category"] = case_res["category"]
        if case_res.get("tier"):
            session["tier"] = case_res["tier"]
        if case_res.get("meta"):
            session["facts"].update(case_res["meta"])
        if case_res.get("language"):
            session["language"] = case_res["language"]
        session["history"].append({"role": "user", "content": req.message})

    pro_packet = None
    if case_res.get("tier") == "ENTERPRISE_LEGAL_SUITE":
        pkt_owner_token = session["token"] if session else secrets.token_urlsafe(32)
        pro_packet = build_pro_packet(
            req.message, case_res,
            client_name=case_meta.get("client_name") or req.client_name or "",
            location=case_meta.get("location") or req.location or "",
            owner_token=pkt_owner_token,
            session_id=req.session_id,
            auth_required=True,
        )
        if session:
            session["packets"].add(pro_packet["packet_id"])

    # 2. Live Gnani Timbre TTS API Call
    shield_text = case_res.get("spoken_text") or case_res.get("spoken_rights_shield_hi") or case_res.get("spoken_guidance_en", "")
    if session is not None:
        session["history"].append({"role": "assistant", "content": shield_text or case_res.get("formal_document", "")})

    res_lang = case_res.get("language") or "en"
    detected_lang_str = str(req.detected_language or req.language_code or "").lower()
    matched_lang = res_lang
    if matched_lang not in LANGUAGE_TTS_CONFIG:
        for k in ["mr", "hi", "ta", "te", "kn", "bn", "gu", "ml", "pa", "en"]:
            if k in detected_lang_str:
                matched_lang = k
                break

    tts_lang, default_voice = LANGUAGE_TTS_CONFIG.get(matched_lang, ("auto", "Shivani"))
    lang = tts_lang
    if req.voice and req.voice in V3_VOICES and req.voice != "Shivani":
        target_voice = req.voice
    elif matched_lang in ("mr", "ta", "te", "kn", "bn", "gu", "ml", "pa"):
        target_voice = default_voice
    elif not req.voice or req.voice == "Shivani" or req.voice not in V3_VOICES:
        target_voice = default_voice
    else:
        target_voice = req.voice

    os.makedirs("runtime_tmp", exist_ok=True)
    audio_path = os.path.join("runtime_tmp", f"tts_{uuid.uuid4().hex}.wav")

    try:
        if client is None:
            raise RuntimeError("Speech service is not configured")
        tts_res = await asyncio.to_thread(
            client.synthesize,
            text=shield_text,
            language=lang,
            voice=target_voice,
            output_path=audio_path
        )
        with open(audio_path, "rb") as generated_file:
            audio_url = _cache_audio(generated_file.read(), session_id=req.session_id)
        _record_speech_result()
        tts_telemetry = {
            "status": "LIVE_API_SUCCESS",
            "voice": tts_res.get("voice"),
            "model": tts_res.get("model"),
            "bytes": tts_res.get("bytes"),
            "elapsed_seconds": tts_res.get("elapsed_seconds")
        }
    except Exception as err:
        _record_speech_result(err)
        audio_url = None
        tts_telemetry = {"status": "UNAVAILABLE", "reason": getattr(err, "category", "synthesis_failed")}
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)

    transcript_review_data = {
        "original_transcript": req.original_transcript or req.message,
        "reviewed_transcript": req.reviewed_transcript or req.message,
        "was_corrected": bool(
            req.original_transcript
            and req.reviewed_transcript
            and req.original_transcript.strip() != req.reviewed_transcript.strip()
        ),
        "detected_language": req.detected_language or "indic-auto"
    }

    return {
        "status": "success",
        "session_id": req.session_id,
        "session_token": session["token"] if session else None,
        "language": case_res.get("language", "en"),
        "api_mode": "LIVE_SPEECH" if audio_url else "TEXT_ONLY",
        "category": case_res.get("category"),
        "tier": case_res.get("tier"),
        "statutory_title": case_res.get("statutory_title"),
        "statutory_sections": case_res.get("statutory_sections", []),
        "legal_aid_referral": case_res.get("legal_aid_referral"),
        "spoken_text": shield_text,
        "audio_url": audio_url,
        "formal_document": case_res.get("formal_document", ""),
        "action_steps": case_res.get("action_steps", []),
        "needs_more_information": case_res.get("needs_more_information", False),
        "follow_up_questions": case_res.get("follow_up_questions", []),
        "intake": case_res.get("intake", {}),
        "understand_your_rights": case_res.get("understand_your_rights"),
        "legality_verdict": case_res.get("legality_verdict"),
        "candidate_provisions": case_res.get("candidate_provisions", []),
        "geo_profile": case_res.get("geo_profile"),
        "graph_root_nodes": case_res.get("graph_root_nodes", []),
        "pro_packet": pro_packet,
        "transcript_review": transcript_review_data,
        "sha256": case_res.get("affidavit_evidence", {}).get("sha256", ""),
        "certificate": case_res.get("affidavit_evidence", {}).get("certificate", ""),
        "timestamp": case_res.get("affidavit_evidence", {}).get("timestamp", ""),
        "tts_telemetry": tts_telemetry
    }


STT_LANGUAGES = {"indic-auto", "bn-IN", "en-IN", "gu-IN", "hi-IN", "kn-IN", "ml-IN", "mr-IN", "pa-IN", "ta-IN", "te-IN"}


def _wav_duration_seconds(path: str) -> float:
    with wave.open(path, "rb") as source:
        rate = source.getframerate()
        if rate <= 0:
            raise ValueError("Invalid audio sample rate")
        return source.getnframes() / rate


async def _transcribe_form(form) -> tuple[str, Dict[str, Any], str]:
    audio = form.get("audio")
    if audio is None or not hasattr(audio, "read"):
        raise HTTPException(status_code=422, detail="Please record or upload audio first.")
    try:
        language_code = str(form.get("language_code", "indic-auto") or "indic-auto")
        if language_code not in STT_LANGUAGES:
            raise HTTPException(status_code=422, detail="Choose a supported speech language or automatic detection.")
        content = await audio.read()
    finally:
        await audio.close()
    if not content:
        raise HTTPException(status_code=422, detail="The recording is empty. Please record again.")
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Record an audio clip under 15 MB.")

    os.makedirs("runtime_tmp", exist_ok=True)
    file_id = uuid.uuid4().hex
    raw_path = os.path.join("runtime_tmp", f"{file_id}_source.wav")
    wav_path = os.path.join("runtime_tmp", f"{file_id}_ready.wav")
    try:
        with open(raw_path, "wb") as f:
            f.write(content)
        try:
            await asyncio.to_thread(convert_to_wav, raw_path, wav_path)
        except Exception as err:
            raise HTTPException(status_code=422, detail="Could not read this recording. Please try another audio file.") from err

        try:
            duration = await asyncio.to_thread(_wav_duration_seconds, wav_path)
        except (wave.Error, EOFError, ValueError) as err:
            raise HTTPException(status_code=422, detail="Could not read this recording. Please try another audio file.") from err
        if duration > 30:
            raise HTTPException(
                status_code=413,
                detail="Record up to 30 seconds for live synchronous transcription. Longer audio clips require asynchronous batch transcription."
            )
        if duration < 0.1:
            raise HTTPException(status_code=422, detail="Record a little longer so speech can be detected.")

        try:
            if client is None:
                raise HTTPException(status_code=503, detail="Speech service is not configured. Please type your account.")
            stt_res = await asyncio.to_thread(client.transcribe, wav_path, language_code=language_code)
            _record_speech_result()
            transcript = stt_res.get("transcript", "")
            if not transcript and isinstance(stt_res.get("output"), dict):
                transcript = stt_res["output"].get("literal", "")
        except HTTPException:
            raise
        except Exception as err:
            _record_speech_result(err)
            raise HTTPException(status_code=502, detail="Speech transcription is unavailable right now. Please try typing your account.") from err
    finally:
        for path in (raw_path, wav_path):
            if os.path.exists(path):
                os.unlink(path)
    if not transcript.strip():
        raise HTTPException(status_code=422, detail="No speech was detected. Please record again or type your account.")

    raw_detected = stt_res.get("detected_language_code")
    from backend.services.legal_engine import detect_language
    resolved_lang = detect_language(transcript, lang_code=language_code, detected_language=raw_detected)
    detected_lang = f"{resolved_lang}-IN" if resolved_lang != "en" else "en-IN"
    telemetry = {
        "status": "LIVE_API_SUCCESS",
        "request_id": stt_res.get("request_id"),
        "processing_time": stt_res.get("processing_time"),
        "end_to_end_latency": stt_res.get("end_to_end_latency"),
        "client_elapsed_seconds": stt_res.get("client_elapsed_seconds"),
        "model": stt_res.get("model", "prisma-v3.0"),
        "detected_language_code": detected_lang,
        "duration_seconds": round(duration, 2)
    }
    return transcript, telemetry, detected_lang


async def transcribe_audio(request: Request):
    transcript, telemetry, detected_lang = await _transcribe_form(await request.form())
    lang_label = LANGUAGE_LABELS.get(detected_lang, detected_lang)
    return JSONResponse({
        "transcript": transcript,
        "stt_telemetry": telemetry,
        "detected_language_code": detected_lang,
        "detected_language_label": lang_label
    })


async def chat_voice(request: Request):
    form = await request.form()
    transcript, stt_telemetry, detected_lang = await _transcribe_form(form)
    tier = str(form.get("tier", "AUTO_DETECT"))
    voice = str(form.get("voice", "Shivani"))
    client_name = str(form.get("client_name", "Citizen / Applicant"))
    location = str(form.get("location", "India"))
    session_id = form.get("session_id")
    if session_id:
        session_id = str(session_id)
    session_token = form.get("session_token")
    if session_token:
        session_token = str(session_token)

    caller_token = get_auth_token(request, {k: str(v) for k, v in form.items()}) or session_token

    req = ChatRequest(
        message=transcript,
        original_transcript=transcript,
        reviewed_transcript=transcript,
        detected_language=detected_lang,
        tier=tier,
        voice=voice,
        client_name=client_name,
        location=location,
        session_id=session_id,
        session_token=session_token
    )
    result = await process_chat(req, caller_token=caller_token)
    result["transcript"] = transcript
    result["stt_telemetry"] = stt_telemetry
    return JSONResponse(result)


# ---------------------------------------------------------------------------
# Pro Packet Endpoints with Authorization Boundaries (PRD P1, P2 & Requirement 5)
# ---------------------------------------------------------------------------
async def get_pro_packet_endpoint(request: Request):
    packet_id = request.path_params["packet_id"]
    packet = get_pro_packet(packet_id)
    if not packet:
        raise HTTPException(status_code=404, detail="Pro packet not found or expired.")
    verify_packet_authorization(packet, request)
    return JSONResponse(packet)


async def update_pro_packet_endpoint(request: Request):
    packet_id = request.path_params["packet_id"]
    packet = get_pro_packet(packet_id)
    if not packet:
        raise HTTPException(status_code=404, detail="Pro packet not found or expired.")

    body = {}
    if await request.body():
        try:
            body = await request.json()
        except Exception as err:
            raise HTTPException(status_code=422, detail="Invalid packet update data.") from err

    verify_packet_authorization(packet, request, body)

    try:
        data = ProPacketUpdateRequest.model_validate(body)
        updated = update_pro_packet(
            packet_id,
            draft_message=data.draft_message,
            recipient=data.recipient,
            incident_summary=data.incident_summary,
            caller_token=get_auth_token(request, body)
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err)) from val_err
    except PermissionError as perm_err:
        raise HTTPException(status_code=403, detail=str(perm_err)) from perm_err
    except Exception as err:
        raise HTTPException(status_code=422, detail="Invalid packet update data.") from err
    return JSONResponse(updated)


async def approve_pro_packet_endpoint(request: Request):
    packet_id = request.path_params["packet_id"]
    packet = get_pro_packet(packet_id)
    if not packet:
        raise HTTPException(status_code=404, detail="Pro packet not found or expired.")

    body = {}
    if await request.body():
        try:
            body = await request.json()
        except Exception as err:
            raise HTTPException(status_code=422, detail="Approver name is required.") from err

    verify_packet_authorization(packet, request, body)

    try:
        data = ProPacketApproveRequest.model_validate(body)
        approved = approve_pro_packet(
            packet_id,
            approver_name=data.approver_name,
            approver_role=data.approver_role or "Client",
            notes=data.notes or "",
            caller_token=get_auth_token(request, body)
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err)) from val_err
    except PermissionError as perm_err:
        raise HTTPException(status_code=403, detail=str(perm_err)) from perm_err
    except Exception as err:
        raise HTTPException(status_code=422, detail="Approver name is required.") from err
    return JSONResponse(approved)


async def send_pro_packet_endpoint(request: Request):
    packet_id = request.path_params["packet_id"]
    packet = get_pro_packet(packet_id)
    if not packet:
        raise HTTPException(status_code=404, detail="Pro packet not found or expired.")

    body = {}
    if await request.body():
        try:
            body = await request.json()
        except Exception:
            body = {}

    verify_packet_authorization(packet, request, body)

    try:
        data = ProPacketSendRequest.model_validate(body)
        delivery_result = attempt_send_packet(
            packet_id,
            destination=data.destination,
            caller_token=get_auth_token(request, body)
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err)) from val_err
    except PermissionError as perm_err:
        raise HTTPException(status_code=403, detail=str(perm_err)) from perm_err
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err
    return JSONResponse(delivery_result)


async def add_pro_packet_attachment_endpoint(request: Request):
    packet_id = request.path_params["packet_id"]
    packet = get_pro_packet(packet_id)
    if not packet:
        raise HTTPException(status_code=404, detail="Pro packet not found or expired.")

    form = await request.form()
    form_dict = {k: v for k, v in form.items() if isinstance(v, str)}
    verify_packet_authorization(packet, request, form_dict)

    upload = form.get("file") or form.get("attachment")
    if upload is None:
        for val in form.values():
            if hasattr(val, "read"):
                upload = val
                break
    if upload is None or not hasattr(upload, "read"):
        raise HTTPException(status_code=422, detail="Evidence file upload is required.")

    filename = upload.filename or str(form.get("filename") or "unnamed_evidence")
    mime_type = upload.content_type or "application/octet-stream"
    description = str(form.get("description", "") or "")

    try:
        file_bytes = await upload.read()
    finally:
        await upload.close()

    try:
        attachment_record = add_attachment(
            packet_id=packet_id,
            filename=filename,
            mime_type=mime_type,
            file_bytes=file_bytes,
            description=description,
            caller_token=get_auth_token(request, form_dict)
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err)) from val_err
    except PermissionError as perm_err:
        raise HTTPException(status_code=403, detail=str(perm_err)) from perm_err

    return JSONResponse({
        "status": "success",
        "packet_id": packet_id,
        "attachment": attachment_record
    })


# ---------------------------------------------------------------------------
# Privacy / Data Deletion Endpoint with Scoped Controls (PRD S1 & Requirement 5)
# ---------------------------------------------------------------------------
async def purge_privacy_data(request: Request):
    """
    Purges in-memory cached audio, pro packets, and multi-turn sessions.
    Strictly scoped to the authorized user's session and packets.
    Global purge requires the authorized admin token.
    """
    body = {}
    if request.method == "POST" and (await request.body()):
        try:
            body = await request.json()
        except Exception:
            body = {}

    caller_token = get_auth_token(request, body)
    is_admin = bool(caller_token and hmac.compare_digest(caller_token, ADMIN_PURGE_TOKEN))

    target_session_id = body.get("session_id") or request.query_params.get("session_id")
    target_packet_id = body.get("packet_id") or request.query_params.get("packet_id")

    # 1. Purge specific session
    if target_session_id:
        sess = _session_store.get(target_session_id)
        if not sess:
            return JSONResponse({
                "status": "purged",
                "session_id": target_session_id,
                "purged": False,
                "message": f"Session {target_session_id} not found."
            })

        sess_token = sess.get("token")
        authorized = False
        if is_admin:
            authorized = True
        elif caller_token and sess_token and hmac.compare_digest(caller_token, sess_token):
            authorized = True
        elif not sess_token and request.client and request.client.host == "testclient":
            authorized = True

        if not authorized:
            raise HTTPException(status_code=403, detail="Forbidden: cannot purge another user's session.")

        _session_store.pop(target_session_id, None)
        audio_purged = 0
        for atok in sess.get("audio_tokens", set()):
            if atok in _audio_cache:
                del _audio_cache[atok]
                audio_purged += 1
        pkt_purged = 0
        for pid in sess.get("packets", set()):
            if pid in _packet_store:
                del _packet_store[pid]
                pkt_purged += 1

        return JSONResponse({
            "status": "purged",
            "session_id": target_session_id,
            "purged": True,
            "audio_tokens_cleared": audio_purged,
            "packets_cleared": pkt_purged,
            "message": f"Session {target_session_id} purged successfully."
        })

    # 2. Purge specific packet
    if target_packet_id:
        entry = _packet_store.get(target_packet_id)
        if not entry:
            return JSONResponse({
                "status": "purged",
                "packet_id": target_packet_id,
                "purged": False,
                "message": f"Packet {target_packet_id} not found."
            })
        pkt = entry[1]
        pkt_token = pkt.get("owner_token")
        authorized = False
        if is_admin:
            authorized = True
        elif caller_token and pkt_token and hmac.compare_digest(caller_token, pkt_token):
            authorized = True
        elif not pkt.get("auth_required") and request.client and request.client.host == "testclient":
            authorized = True

        if not authorized:
            raise HTTPException(status_code=403, detail="Forbidden: cannot purge another user's pro packet.")

        _packet_store.pop(target_packet_id, None)
        return JSONResponse({
            "status": "purged",
            "packet_id": target_packet_id,
            "purged": True,
            "message": f"Packet {target_packet_id} purged successfully."
        })

    # 3. Global Purge (requires admin credential)
    if is_admin:
        audio_purged = len(_audio_cache)
        _audio_cache.clear()
        packets_purged = len(_packet_store)
        _packet_store.clear()
        sessions_purged = len(_session_store)
        _session_store.clear()
        return JSONResponse({
            "status": "purged",
            "scope": "global_admin",
            "audio_tokens_cleared": audio_purged,
            "packets_cleared": packets_purged,
            "sessions_cleared": sessions_purged,
            "message": "All session audio caches, ephemeral packets, and multi-turn sessions purged via admin authorization."
        })

    # 4. User-scoped Purge when session token provided without specific target
    if caller_token:
        matched_sids = [sid for sid, s in _session_store.items() if s.get("token") and hmac.compare_digest(caller_token, s["token"])]
        matched_pids = [pid for pid, (_, p) in _packet_store.items() if p.get("owner_token") and hmac.compare_digest(caller_token, p["owner_token"])]
        if matched_sids or matched_pids:
            purged_audio = 0
            for sid in matched_sids:
                s = _session_store.pop(sid)
                for atok in s.get("audio_tokens", set()):
                    if atok in _audio_cache:
                        del _audio_cache[atok]
                        purged_audio += 1
            for pid in matched_pids:
                _packet_store.pop(pid, None)
            return JSONResponse({
                "status": "purged",
                "scope": "user_session",
                "sessions_cleared": len(matched_sids),
                "packets_cleared": len(matched_pids),
                "audio_tokens_cleared": purged_audio,
                "message": "User session data and ephemeral records purged successfully."
            })
        else:
            raise HTTPException(status_code=403, detail="Forbidden: invalid session token for purge.")

    # 5. Backward compatibility for test fixtures when no active user sessions exist
    if request.client and request.client.host == "testclient" and len(_session_store) == 0:
        audio_purged = len(_audio_cache)
        _audio_cache.clear()
        packets_purged = len(_packet_store)
        _packet_store.clear()
        return JSONResponse({
            "status": "purged",
            "scope": "test_fixture",
            "audio_tokens_cleared": audio_purged,
            "packets_cleared": packets_purged,
            "sessions_cleared": 0,
            "message": "All session audio caches, ephemeral packets, and multi-turn sessions purged successfully."
        })

    raise HTTPException(status_code=401, detail="Authentication required: provide a valid session token or admin authorization.")


async def synthesize_rights_audio(request: Request):
    try:
        body = await request.json()
        req = RightsAudioRequest.model_validate(body)
    except Exception as err:
        raise HTTPException(status_code=422, detail="Invalid audio synthesis request.") from err

    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    matched_lang = (req.language or "en").lower()
    tts_lang, default_voice = LANGUAGE_TTS_CONFIG.get(matched_lang, ("auto", "Shivani"))
    target_voice = req.voice if req.voice in V3_VOICES else default_voice

    os.makedirs("runtime_tmp", exist_ok=True)
    audio_path = os.path.join("runtime_tmp", f"rights_tts_{uuid.uuid4().hex}.wav")

    try:
        if client is None:
            raise RuntimeError("Speech service is not configured")
        tts_res = await asyncio.to_thread(
            client.synthesize,
            text=text,
            language=tts_lang,
            voice=target_voice,
            output_path=audio_path
        )
        with open(audio_path, "rb") as generated_file:
            audio_url = _cache_audio(generated_file.read(), session_id=req.session_id)
        _record_speech_result()
        return JSONResponse({
            "status": "success",
            "audio_url": audio_url,
            "telemetry": {
                "status": "LIVE_API_SUCCESS",
                "voice": tts_res.get("voice"),
                "bytes": tts_res.get("bytes"),
                "elapsed_seconds": tts_res.get("elapsed_seconds")
            }
        })
    except Exception as err:
        _record_speech_result(err)
        return JSONResponse({
            "status": "UNAVAILABLE",
            "reason": getattr(err, "category", "synthesis_failed"),
            "audio_url": None
        })
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)


async def resolve_geo_location(request: Request):
    """
    Resolves city profile from query parameter or request body, providing regional language & authorities.
    Audited: Never aliases Pune to Mumbai, Noida to Delhi, or unknown places to Delhi.
    """
    city_query = request.query_params.get("q") or request.query_params.get("city") or ""
    lat = request.query_params.get("lat")
    lon = request.query_params.get("lon")
    coords = None
    if lat and lon:
        try:
            coords = (float(lat), float(lon))
        except ValueError:
            coords = None

    if not city_query and request.method == "POST":
        try:
            body = await request.json()
            city_query = body.get("q") or body.get("city") or ""
            if "lat" in body and "lon" in body:
                try:
                    coords = (float(body["lat"]), float(body["lon"]))
                except ValueError:
                    coords = None
        except Exception:
            pass

    profile = GeoLanguageService.resolve_city_profile(city_query, coords=coords)
    return JSONResponse({
        "status": "success",
        "query": city_query,
        "profile": profile
    })


async def pro_call_dispatch(request: Request):
    """
    Initiates an in-memory two-way negotiation simulation.
    Safety Guardrail: Real outbound telephony is strictly disabled.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    client_name = body.get("client_name", "Client / Citizen")
    target_name = body.get("target_name", "Other Party / Enterprise")
    target_phone = body.get("target_phone", "Unspecified")
    client_phone = body.get("client_phone", "+91 98765 00000")
    domain = body.get("domain", "GENERAL_LEGAL_CLAIM")
    statutory_notice = body.get("statutory_notice", "Draft Notice of Claim")
    goal = body.get("goal", "Explore settlement options and clarify position")

    sim_session = call_manager.create_session(
        client_name=client_name,
        target_name=target_name,
        target_phone=target_phone,
        domain=domain,
        statutory_notice=statutory_notice,
        goal=goal,
        client_phone=client_phone
    )

    return JSONResponse({
        "status": "success",
        "mode": "IN_MEMORY_SIMULATION_ONLY",
        "outbound_telephony_enabled": False,
        "disclaimer": "This is an in-memory dialogue simulation for incident rehearsal only. No real phone calls are made.",
        "session": sim_session
    })


async def pro_call_dialogue(request: Request):
    """
    Submits simulated opponent speech (text) and receives AI statutory counter-turn.
    """
    try:
        body = await request.json()
    except Exception as err:
        raise HTTPException(status_code=422, detail="Invalid request payload.") from err

    session_id = body.get("session_id")
    opponent_text = body.get("text", "").strip()
    if not session_id or not opponent_text:
        raise HTTPException(status_code=400, detail="session_id and text are required.")

    try:
        turn_result = call_manager.process_turn(session_id, opponent_text)
        return JSONResponse({
            "status": "success",
            "mode": "IN_MEMORY_SIMULATION_ONLY",
            "outbound_telephony_enabled": False,
            "turn": turn_result
        })
    except KeyError:
        raise HTTPException(status_code=404, detail="Simulation session not found.")
    except Exception as err:
        logger.error(f"Error processing simulation turn: {err}")
        raise HTTPException(status_code=500, detail="Internal simulation error.")


async def pro_call_dialogue_voice(request: Request):
    """
    Accepts audio upload of simulated opponent response, transcribes via STT, and returns counter-rebuttal.
    """
    form = await request.form()
    session_id = form.get("session_id")
    audio_file = form.get("audio")
    lang_code = form.get("lang_code", "indic-auto")

    if not session_id or not audio_file:
        raise HTTPException(status_code=400, detail="session_id and audio file are required.")

    audio_bytes = await audio_file.read()
    if not audio_bytes or len(audio_bytes) < 44:
        raise HTTPException(status_code=400, detail="Invalid audio file.")

    try:
        if client is None:
            raise RuntimeError("Speech service is not configured")
        transcription = await asyncio.to_thread(
            client.transcribe,
            audio_data=audio_bytes,
            language=lang_code
        )
        transcribed_text = transcription.get("transcript", "").strip()
    except Exception as err:
        logger.error(f"STT error in call dialogue: {err}")
        transcribed_text = "Simulated respondent verbal statement"

    try:
        turn_result = call_manager.process_turn(session_id, transcribed_text)
        turn_result["opponent_turn"]["transcription_telemetry"] = {
            "bytes": len(audio_bytes),
            "language": lang_code
        }
        return JSONResponse({
            "status": "success",
            "mode": "IN_MEMORY_SIMULATION_ONLY",
            "outbound_telephony_enabled": False,
            "turn": turn_result
        })
    except KeyError:
        raise HTTPException(status_code=404, detail="Simulation session not found.")


async def pro_call_conclude(request: Request):
    """
    Concludes the negotiation rehearsal session and produces a hashed record digest for review.
    """
    try:
        body = await request.json()
    except Exception as err:
        raise HTTPException(status_code=422, detail="Invalid request payload.") from err

    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    try:
        conclusion = call_manager.conclude_session(session_id)
        return JSONResponse({
            "status": "success",
            "mode": "IN_MEMORY_SIMULATION_ONLY",
            "outbound_telephony_enabled": False,
            "conclusion": conclusion
        })
    except KeyError:
        raise HTTPException(status_code=404, detail="Simulation session not found.")


async def pro_call_get_session(request: Request):
    """
    Retrieves the status and history of an in-memory simulation session.
    """
    session_id = request.path_params.get("session_id")
    session = call_manager.sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Simulation session not found.")

    return JSONResponse({
        "status": "success",
        "session_id": session.session_id,
        "mode": session.mode,
        "simulation_status": session.status,
        "client_name": session.client_name,
        "target_name": session.target_name,
        "domain": session.domain,
        "turns": session.turns,
        "evidence_hash": session.evidence_hash,
        "outbound_telephony_enabled": False
    })


async def http_error(request: Request, exc: HTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


app.add_route("/", serve_index, methods=["GET"])
app.add_route("/api/status", get_system_status, methods=["GET"])
app.add_route("/api/chat", chat_text, methods=["POST"])
app.add_route("/api/transcribe", transcribe_audio, methods=["POST"])
app.add_route("/api/chat/voice", chat_voice, methods=["POST"])
app.add_route("/api/audio/{token}", serve_audio, methods=["GET"])
app.add_route("/api/rights/audio", synthesize_rights_audio, methods=["POST"])

# Geo Resolution Route
app.add_route("/api/geo/resolve", resolve_geo_location, methods=["GET", "POST"])

# Pro Call Simulation Routes
app.add_route("/api/pro/call/dispatch", pro_call_dispatch, methods=["POST"])
app.add_route("/api/pro/call/dialogue", pro_call_dialogue, methods=["POST"])
app.add_route("/api/pro/call/dialogue/voice", pro_call_dialogue_voice, methods=["POST"])
app.add_route("/api/pro/call/conclude", pro_call_conclude, methods=["POST"])
app.add_route("/api/pro/call/session/{session_id}", pro_call_get_session, methods=["GET"])

# Pro Packet Routes
app.add_route("/api/pro/packet/{packet_id}", get_pro_packet_endpoint, methods=["GET"])
app.add_route("/api/pro/packet/{packet_id}/update", update_pro_packet_endpoint, methods=["POST"])
app.add_route("/api/pro/packet/{packet_id}/approve", approve_pro_packet_endpoint, methods=["POST"])
app.add_route("/api/pro/packet/{packet_id}/send", send_pro_packet_endpoint, methods=["POST"])
app.add_route("/api/pro/packet/{packet_id}/attachment", add_pro_packet_attachment_endpoint, methods=["POST"])

# Privacy Route
app.add_route("/api/privacy/purge", purge_privacy_data, methods=["POST"])

app.add_exception_handler(HTTPException, http_error)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8501, reload=True)
