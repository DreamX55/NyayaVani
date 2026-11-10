"""Tests for Speech Recognition and Multi-language Identification Fixes (NyayaVani).
Verifies:
1. Accurate discrimination of Marathi vs Hindi in Devanagari script.
2. ASR acoustic detection preservation without fallback override to Hindi.
3. Pure Python resampling of audio without FFmpeg binary dependency.
4. Voice persona mapping across Indic languages.
5. Frontend Web Audio API direct PCM recording & review card language override.
"""

import os
import io
import wave
import struct
import pytest
from starlette.testclient import TestClient

from backend.server import app, convert_to_wav
from backend.services.legal_engine import detect_language
from backend.services.geo_service import GeoLanguageService


def test_marathi_language_identification():
    """Verify Marathi sentences in Devanagari are detected as 'mr', not 'hi'."""
    marathi_samples = [
        "दुकान हटवली आणि सामान नेले",
        "माझा पगार दिला नाही आणि मालकाने कामावरून काढले",
        "पोलीस ठाण्यात माझी तक्रार नोंदवून घेतली नाही",
        "आम्हाला मदत पाहिजे, अपघात झाला आणि गाडी धडकली",
        "सातबारा वर नाव बदल झाले नाही",
    ]
    for text in marathi_samples:
        detected = detect_language(text)
        assert detected == "mr", f"Expected 'mr' for Marathi statement: {text}, got '{detected}'"


def test_acoustic_asr_detected_language_priority():
    """Verify acoustic ASR detected language (e.g. mr-IN) is respected even with neutral Devanagari."""
    neutral_devanagari = "काम झाले"
    # When ASR acoustic detection says Marathi, it must not be forced to Hindi
    result = detect_language(neutral_devanagari, detected_language="mr-IN")
    assert result == "mr"

    # When user explicitly selected Marathi
    result_explicit = detect_language(neutral_devanagari, lang_code="mr-IN")
    assert result_explicit == "mr"


def test_indic_languages_script_identification():
    """Verify non-Devanagari Indic scripts are definitively identified."""
    assert detect_language("வணக்கம், எனக்கு உதவி வேண்டும்") == "ta"
    assert detect_language("ನನಗೆ ಸಂಬಳ ಕೊಟ್ಟಿಲ್ಲ") == "kn"
    assert detect_language("నాకు జీతం ఇవ్వలేదు") == "te"
    assert detect_language("আমার বেতন দেওয়া হয়নি") == "bn"
    assert detect_language("મને પગાર આપ્યો નથી") == "gu"
    assert detect_language("ਮੈਨੂੰ ਤਨਖਾਹ ਨਹੀਂ ਮਿਲੀ") == "pa"
    assert detect_language("എനിക്ക് ശമ്പളം തന്നില്ല") == "ml"


def test_geo_language_service_marathi_persona():
    """Verify GeoLanguageService maps Marathi speech/text to Vasudha voice persona."""
    lang, voice = GeoLanguageService.adapt_language_from_text("दुकान हटवली आणि सामान नेले", "indic-auto")
    assert lang == "mr-IN"
    assert voice == "Vasudha"


def test_convert_to_wav_pure_python_resampling(tmp_path):
    """Verify convert_to_wav resamples 44100Hz stereo WAV to 16000Hz mono WAV in pure Python without FFmpeg."""
    input_wav = tmp_path / "stereo_44k.wav"
    output_wav = tmp_path / "mono_16k.wav"

    # Create a synthetic 44.1kHz stereo WAV file
    sample_rate = 44100
    duration_secs = 0.5
    num_samples = int(sample_rate * duration_secs)

    with wave.open(str(input_wav), "wb") as wf:
        wf.setnchannels(2)  # Stereo
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        # Generate 0.5s of sine wave audio
        frames = bytearray()
        for i in range(num_samples):
            val = int(16000 * (i % 100) / 100)
            frames.extend(struct.pack("<hh", val, val))
        wf.writeframes(frames)

    # Convert without FFmpeg
    converted_path = convert_to_wav(str(input_wav), str(output_wav))
    assert os.path.exists(converted_path)

    with wave.open(converted_path, "rb") as out_wf:
        assert out_wf.getnchannels() == 1, "Must be downmixed to mono"
        assert out_wf.getframerate() == 16000, "Must be resampled to 16000Hz"
        assert out_wf.getsampwidth() == 2, "Must be 16-bit PCM"


def test_frontend_has_review_lang_override_and_v3_voices():
    """Verify frontend/index.html includes review language selector and V3 voice options."""
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert "review-lang-override" in html, "Review card must provide inline language selector"
    assert "Vasudha" in html, "Spoken voice select must include Vasudha for Marathi"
    assert "encodePcmToWav" in html, "Direct PCM recording WAV encoder must be present"
    assert "isRecordingActive" in html, "Robust recording state tracking must be present"


def test_situation_tailored_followup_questions():
    """Verify that different scenarios produce distinct, tailored questions and skip known facts."""
    from backend.services.legal_engine import NyayaVaniEngine
    engine = NyayaVaniEngine()

    # 1. Street vendor with date & municipality pre-stated
    res_vendor = engine.process_case(
        "काल रात्री महापालिकेने माझी फळांची गाडी तोडली आणि सामान नेले",
        meta={"location": "Pune"}
    )
    assert res_vendor["category"] == "STREET_VENDOR"
    vendor_qs = " ".join(res_vendor["follow_up_questions"])
    assert "फेरीवाला प्रमाणपत्र" in vendor_qs or "वेंडिंग सर्टिफिकेट" in vendor_qs
    assert "कोणत्या ठिकाणी" not in vendor_qs  # Location was already Pune

    # 2. Wage theft
    res_wage = engine.process_case(
        "कंत्राटदाराने ३ महिन्यांपासून माझा पगार दिला नाही",
        meta={"location": "Mumbai"}
    )
    assert res_wage["category"] == "WAGE_THEFT"
    wage_qs = " ".join(res_wage["follow_up_questions"])
    assert "पगार" in wage_qs
    assert "फेरीवाला" not in wage_qs

    # 3. Police detention
    res_police = engine.process_case(
        "The police detained my brother at the chowki without giving reasons."
    )
    assert res_police["category"] == "POLICE_CUSTODY"
    police_qs = " ".join(res_police["follow_up_questions"]).lower()
    assert any(w in police_qs for w in ["arrest", "detain", "police", "memo"])
    assert "wages" not in police_qs
    assert "vending" not in police_qs
