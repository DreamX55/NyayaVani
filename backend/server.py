import os
import sys
import time
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.gnani_client import GnaniClient
from backend.services.legal_engine import NyayaVaniEngine
from backend.services.geo_service import GeoLanguageService

app = FastAPI(title="NyayaVani Legal AI", version="3.0.0")

# Mount audio samples for static streaming
os.makedirs("audio_samples", exist_ok=True)
app.mount("/audio_samples", StaticFiles(directory="audio_samples"), name="audio_samples")

# Mount frontend assets
os.makedirs("frontend/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Initialize AI Services
client = GnaniClient()
engine = NyayaVaniEngine()

def convert_to_wav(input_path: str, output_path: str) -> str:
    """
    Converts browser audio (WebM, OGG, MP4) to 16kHz mono 16-bit PCM WAV using FFmpeg.
    """
    ffmpeg_bin = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"
    cmd = [
        ffmpeg_bin, "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        output_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion failed: {res.stderr.decode('utf-8', errors='ignore')}")
    return output_path

class ChatRequest(BaseModel):
    message: str
    tier: Optional[str] = "AUTO_DETECT"
    voice: Optional[str] = "Shivani"
    client_name: Optional[str] = "Citizen / Applicant"
    location: Optional[str] = "India"
    meta: Optional[Dict[str, Any]] = None

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join("frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>NyayaVani Frontend Ready</h1>")

@app.get("/api/status")
async def get_system_status():
    masked_key = client.api_key[:8] + "..." + client.api_key[-6:] if client.api_key else "NOT_CONFIGURED"
    return {
        "status": "online",
        "api_key_active": bool(client.api_key),
        "api_key_masked": masked_key,
        "base_url": client.base_url,
        "models": {
            "asr": "Prisma v2.5 / v3.0 (https://api.vachana.ai/stt/v3)",
            "tts": "Timbre v3.0 (https://api.vachana.ai/api/v1/tts/inference)",
            "reasoning": "Evon 30B MoE"
        }
    }

@app.get("/api/geo/resolve")
async def resolve_geo(city: Optional[str] = "delhi", lat: Optional[float] = None, lon: Optional[float] = None):
    coords = (lat, lon) if lat is not None and lon is not None else None
    profile = GeoLanguageService.resolve_city_profile(city or "delhi", coords=coords)
    return profile

@app.get("/api/presets")
async def get_presets():
    return {
        "presets": [
            {
                "id": "vendor_eviction",
                "title": "Street Vendor Cart Seizure (Juhu, Mumbai)",
                "category": "STREET_VENDOR",
                "tier": "BHARAT_GRASSROOTS_AID",
                "text": "नमस्ते साहब, मैं जुहू बीच पर 10 साल से फल का ठेला लगाता हूँ। आज बीएमसी और पुलिस वाले आए और बोले कि दुकान तुरंत हटाओ। उन्होंने मेरा ठेला जब्त करने की धमकी दी। मेरे पास पीएम स्वनिधि की पर्ची है लेकिन वो सुनने को तैयार नहीं हैं।",
                "client_name": "Ramesh Kumar Gupta",
                "location": "Juhu Beach, Ward K-West, Mumbai",
                "audio_sample": "/audio_samples/sample_vendor_eviction_juhu.wav",
                "icon": "🏛️"
            },
            {
                "id": "wage_theft",
                "title": "Labor Wage Theft & Contractor Default",
                "category": "WAGE_THEFT",
                "tier": "BHARAT_GRASSROOTS_AID",
                "text": "ठेकेदार ने हमसे 3 महीने दिन-रात काम करवाया, अब 45,000 रुपये मजदूरी रोक रखी है और मांगने पर गाली-गलौज कर रहा है और जान से मारने की धमकी दे रहा है।",
                "client_name": "Suresh Yadav",
                "location": "Noida Industrial Area, UP",
                "audio_sample": None,
                "icon": "⚖️"
            },
            {
                "id": "loan_app_fraud",
                "title": "Predatory Loan App Morphing & Blackmail",
                "category": "LOAN_FRAUD",
                "tier": "BHARAT_GRASSROOTS_AID",
                "text": "एक मोबाइल लोन ऐप ने मेरे सारे फोन कॉन्टैक्ट्स हैक कर लिए और अब फोटो मॉर्फ करके रिश्तेदारों को भेजने की धमकी देकर 50 हजार रुपये जबरन वसूली मांग रहे हैं।",
                "client_name": "Pooja Sharma",
                "location": "Jaipur, Rajasthan",
                "audio_sample": None,
                "icon": "📱"
            },
            {
                "id": "church_disruption",
                "title": "Disruption of Peaceful Prayer Gathering",
                "category": "RELIGIOUS_GATHERING",
                "tier": "BHARAT_GRASSROOTS_AID",
                "text": "हम अपने प्रार्थना हॉल में शांतिपूर्वक रविवार की प्रार्थना कर रहे थे। कुछ लोग लाठी-डंडे लेकर अंदर घुस आए, कुर्सियां तोड़ीं और जान से मारने की धमकी देकर प्रार्थना रुकवा दी।",
                "client_name": "Pastor Samuel & Community",
                "location": "Civil Lines, Kanpur, UP",
                "audio_sample": "/audio_samples/sample_church_attack.wav",
                "icon": "🛡️"
            },
            {
                "id": "car_crash_pro",
                "title": "Motor Vehicle Highway Crash (MACT & GIC Claim)",
                "category": "MOTOR_ACCIDENT",
                "tier": "ENTERPRISE_LEGAL_SUITE",
                "text": "I was driving through the signal at Outer Ring Road when a speeding white SUV ran the red light and smashed into my front right bumper. I have clear dashcam footage recording the entire incident and the driver admitting he was on his phone.",
                "client_name": "Vikramaditya Sharma",
                "location": "Marathahalli Junction, Bengaluru",
                "audio_sample": "/audio_samples/sample_car_crash.wav",
                "icon": "🚗"
            },
            {
                "id": "rera_delay_pro",
                "title": "RERA Real Estate Possession Delay & Interest Notice",
                "category": "REAL_ESTATE_RERA",
                "tier": "ENTERPRISE_LEGAL_SUITE",
                "text": "I purchased a luxury 3BHK with promised possession in December 2023. The builder has delayed possession by 35 months without an Occupancy Certificate and refuses compensation.",
                "client_name": "Aditya Singhania",
                "location": "Gurugram, Haryana",
                "audio_sample": None,
                "icon": "🏢"
            }
        ]
    }

@app.post("/api/chat")
async def chat_text(req: ChatRequest):
    case_meta = req.meta or {}
    case_meta["client_name"] = req.client_name
    case_meta["location"] = req.location

    # 1. Resolve City & Dynamic Language
    city_prof = GeoLanguageService.resolve_city_profile(req.location or "India")
    detected_lang, detected_voice = GeoLanguageService.adapt_language_from_text(
        req.message, current_lang=city_prof["primary_language"]
    )
    target_voice = req.voice if (req.voice and req.voice != "Shivani") else detected_voice
    lang = detected_lang

    # 2. Process through Legal GraphRAG reasoning engine
    case_res = engine.process_case(req.message, suite_tier=req.tier, meta=case_meta)

    # 3. Live Gnani Timbre TTS API Call using X-API-Key-ID
    shield_text = case_res.get("spoken_rights_shield_hi") or case_res.get("spoken_guidance_en", "")

    audio_filename = f"tts_live_{int(time.time() * 1000)}.wav"
    audio_path = os.path.join("audio_samples", audio_filename)

    try:
        tts_res = client.synthesize(
            text=shield_text,
            language=lang,
            voice=target_voice,
            output_path=audio_path
        )
        audio_url = f"/audio_samples/{audio_filename}"
        tts_telemetry = {
            "status": "LIVE_API_SUCCESS",
            "voice": tts_res.get("voice"),
            "model": tts_res.get("model"),
            "bytes": tts_res.get("bytes"),
            "elapsed_seconds": tts_res.get("elapsed_seconds")
        }
    except Exception as err:
        raise HTTPException(
            status_code=502,
            detail=f"Gnani Timbre TTS Live API Call Failed: {str(err)}"
        )

    return {
        "status": "success",
        "api_mode": "LIVE_GNANI_API_CALL",
        "category": case_res.get("category"),
        "tier": case_res.get("tier"),
        "legality_verdict": case_res.get("legality_verdict", {}),
        "statutory_title": case_res.get("statutory_title"),
        "statutory_sections": case_res.get("statutory_sections", []),
        "spoken_text": shield_text,
        "audio_url": audio_url,
        "formal_document": case_res.get("formal_document", ""),
        "action_steps": case_res.get("action_steps", []),
        "sha256": case_res.get("affidavit_evidence", {}).get("sha256", ""),
        "certificate": case_res.get("affidavit_evidence", {}).get("certificate", ""),
        "timestamp": case_res.get("affidavit_evidence", {}).get("timestamp", ""),
        "tts_telemetry": tts_telemetry
    }

@app.post("/api/chat/voice")
async def chat_voice(
    audio: UploadFile = File(...),
    tier: str = Form("AUTO_DETECT"),
    voice: str = Form("Shivani"),
    client_name: str = Form("Citizen / Applicant"),
    location: str = Form("India")
):
    # 1. Save uploaded live audio chunk
    ts_now = int(time.time() * 1000)
    raw_filename = f"live_upload_{ts_now}_{audio.filename}"
    raw_path = os.path.join("audio_samples", raw_filename)

    content = await audio.read()
    with open(raw_path, "wb") as f:
        f.write(content)

    # 2. Convert to standard 16kHz WAV for Gnani Prisma STT if needed
    wav_filename = f"live_ingest_{ts_now}.wav"
    wav_path = os.path.join("audio_samples", wav_filename)

    try:
        convert_to_wav(raw_path, wav_path)
    except Exception as e:
        # If conversion fails, fallback to passing raw file
        wav_path = raw_path

    # 3. Live Gnani Prisma STT API Call via X-API-Key-ID
    target_lang = "en-IN" if tier == "ENTERPRISE_LEGAL_SUITE" else "hi-IN"
    try:
        stt_res = client.transcribe(wav_path, language_code=target_lang)
        transcript = stt_res.get("transcript", "")
        if not transcript and "output" in stt_res:
            transcript = stt_res["output"].get("literal", "")
    except Exception as err:
        raise HTTPException(
            status_code=502,
            detail=f"Gnani Prisma STT Live API Call Failed: {str(err)}"
        )

    stt_telemetry = {
        "status": "LIVE_API_SUCCESS",
        "request_id": stt_res.get("request_id"),
        "processing_time": stt_res.get("processing_time"),
        "end_to_end_latency": stt_res.get("end_to_end_latency"),
        "client_elapsed_seconds": stt_res.get("client_elapsed_seconds"),
        "model": stt_res.get("model", "prisma-v2.5")
    }

    # 4. Pass transcript into legal reasoning and live Timbre TTS synthesis
    req = ChatRequest(
        message=transcript,
        tier=tier,
        voice=voice,
        client_name=client_name,
        location=location
    )
    result = await chat_text(req)
    result["transcript"] = transcript
    result["input_audio_url"] = f"/audio_samples/{os.path.basename(wav_path)}"
    result["stt_telemetry"] = stt_telemetry
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8501, reload=True)
