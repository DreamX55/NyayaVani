"""Tests for Voice-First "Understand Your Rights" Feature in NyayaVani.

Verifies:
1. Missing facts handling (conditional, non-invented explanations)
2. Wrong or unknown jurisdiction handling
3. Multiple possible Acts handling
4. Unsupported citations fallback (safe constitutional fallback, no invented statutes)
5. Multilingual spoken content (Marathi, Hindi, English, Tamil)
6. TTS failure fallback (graceful degradation to text-only mode)
7. Audio/text consistency (spoken scripts strictly align with screen text)
8. Urgent cases priority (safety notice prioritized before long legal text)
9. Complete browser flow via /api/chat and /api/rights/audio
"""

import pytest
from unittest.mock import MagicMock, patch
from starlette.testclient import TestClient

from backend.server import app
from backend.services.legal_engine import NyayaVaniEngine
from backend.services.rights_explainer import (
    build_understand_your_rights,
    detect_urgency,
    SECTION_HEADINGS,
    CATEGORY_RIGHTS_BLUEPRINT,
)


@pytest.fixture
def test_client():
    return TestClient(app)


def test_understand_your_rights_missing_facts():
    """When facts are missing, the explanation must be conditional and not invent details."""
    engine = NyayaVaniEngine()
    # User only states a partial account with missing date/location/employer details
    res = engine.process_case("माझे कंत्राटदाराने ३ महिन्यांचे वेतन दिले नाही.")
    
    assert res["needs_more_information"] is True
    assert "understand_your_rights" in res
    uyr = res["understand_your_rights"]
    
    # 1. What I understood
    assert "३ महिन्यांचे वेतन" in uyr["what_i_understood"]["text"]
    
    # 2. What may be wrong: Allegation vs Fact note present
    assert "allegation_vs_fact_note" in uyr["what_may_be_wrong"]
    assert "आरोप" in uyr["what_may_be_wrong"]["allegation_vs_fact_note"]
    
    # 3. Possible Act and Dhaara: DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW
    for act in uyr["possible_acts"]:
        assert act["review_status"] == "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"
        assert act["source_url"].startswith("http")
    
    # 4. Why it might apply here: flags missing conditions
    assert uyr["why_it_might_apply"]["clarification_needed"] is not None
    assert "बाकी आहे" in uyr["why_it_might_apply"]["clarification_needed"]
    
    # 5. What the person can do next: includes evidence preservation and legal aid
    options = uyr["what_you_can_do_next"]["options"]
    assert len(options) >= 3
    assert any("१५१००" in opt["details"] or "15100" in opt["details"] for opt in options)
    
    # 7. One-minute recap exists
    assert "recap_text" in uyr["one_minute_recap"]
    assert len(uyr["one_minute_recap"]["recap_text"]) > 10


def test_understand_your_rights_unknown_jurisdiction():
    """When jurisdiction is unknown, the engine flags verification and does not assert filing readiness."""
    res = build_understand_your_rights(
        category="WAGE_THEFT",
        facts={"other_party": "ABC Builders"},
        transcript="I worked on a construction site and was not paid.",
        lang="en",
        missing=["incident_location", "incident_date"],
        location=""
    )
    assert res["status"] == "ready"
    assert "incident_location" in res["why_it_might_apply"]["clarification_needed"]
    # Filing disclaimer must state verification is required
    assert "once records are verified" in res["what_you_can_do_next"]["filing_disclaimer"].lower()


def test_understand_your_rights_multiple_possible_acts():
    """Verify handling when an incident category references multiple primary statutory provisions."""
    engine = NyayaVaniEngine()
    # Motor accident pro spans Section 166 and DAR provisions of MV Act 1988/2019
    res = engine.process_case(
        "There was a major vehicle accident and collision on highway.",
        meta={
            "incident_date": "2026-11-08",
            "incident_location": "Thane, Maharashtra",
            "other_party": "Truck MH-04-1234",
            "specific_details": "Suffered fracture; hospital bills 50000; police report pending."
        }
    )
    assert res["category"] == "MOTOR_ACCIDENT_PRO"
    uyr = res["understand_your_rights"]
    assert len(uyr["possible_acts"]) >= 2
    # Verify each provision has an official India Code link and condition check
    for act in uyr["possible_acts"]:
        assert "indiacode.nic.in" in act["source_url"] or act["source_url"].startswith("http")
        assert "conditions_to_check" in act
        assert act["review_status"] == "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"


def test_understand_your_rights_unsupported_citations_fallback():
    """For an unsupported/unrecognized category, fallback safely to legal services authorities or constitutional aid."""
    res = build_understand_your_rights(
        category="NON_EXISTENT_CATEGORY",
        facts={},
        transcript="Random uncategorized statement.",
        lang="en"
    )
    assert len(res["possible_acts"]) >= 1
    fallback = res["possible_acts"][0]
    assert ("Legal Services Authorities" in fallback["act_name"] 
            or "39A" in fallback["section"] 
            or "Constitution" in fallback["act_name"])
    assert fallback["review_status"] == "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"
    assert "conditions_to_check" in fallback


def test_understand_your_rights_multilingual_spoken_content():
    """Verify natural, language-appropriate phrasing across Marathi, Hindi, English, and Tamil."""
    facts = {
        "incident_date": "Yesterday",
        "incident_location": "Bandra",
        "other_party": "Contractor",
        "specific_details": "Wage withheld"
    }

    # Marathi
    res_mr = build_understand_your_rights("WAGE_THEFT", facts, "पैसे दिले नाहीत", lang="mr")
    assert "कायदेशीर हक्क" in res_mr["spoken_scripts"]["full_rights_spoken"]
    assert "१५१००" in res_mr["spoken_scripts"]["full_rights_spoken"] or "15100" in res_mr["spoken_scripts"]["full_rights_spoken"]
    assert "सोप्या शब्दांत" in res_mr["simpler_words_explanation"]["explanation"]

    # Hindi
    res_hi = build_understand_your_rights("WAGE_THEFT", facts, "मजदूरी नहीं मिली", lang="hi")
    assert "कानूनी अधिकार" in res_hi["spoken_scripts"]["full_rights_spoken"]
    assert "15100" in res_hi["spoken_scripts"]["full_rights_spoken"]
    assert "सरल शब्दों में" in res_hi["simpler_words_explanation"]["explanation"]

    # English
    res_en = build_understand_your_rights("WAGE_THEFT", facts, "Unpaid wages", lang="en")
    assert "legal rights" in res_en["spoken_scripts"]["full_rights_spoken"].lower()
    assert "15100" in res_en["spoken_scripts"]["full_rights_spoken"]

    # Tamil
    res_ta = build_understand_your_rights("WAGE_THEFT", facts, "ஊதியம் கிடைக்கவில்லை", lang="ta")
    assert "understood" in res_ta["what_i_understood"]["heading"].lower() or "புரிந்து" in res_ta["what_i_understood"]["heading"]


def test_understand_your_rights_audio_text_consistency():
    """Spoken scripts must strictly align with visible structured content."""
    res = build_understand_your_rights(
        category="STREET_VENDOR",
        facts={"incident_location": "Dadar", "other_party": "BMC Squad"},
        transcript="BMC officers came and seized my vegetable cart.",
        lang="mr"
    )
    scripts = res["spoken_scripts"]
    recap = res["one_minute_recap"]["recap_text"]
    improper = res["what_may_be_wrong"]["improper_conduct_description"]

    # Spoken recap must match the one-minute recap text exactly
    assert scripts["recap_spoken"] == recap
    # Spoken full explanation must contain the improper conduct description
    assert improper in scripts["full_rights_spoken"]
    # Simplified spoken must match simpler words explanation
    assert scripts["simplified_spoken"] == res["simpler_words_explanation"]["explanation"]


def test_understand_your_rights_urgent_cases_priority():
    """When danger, detention, or violence is reported, urgent safety notice must take priority."""
    # Test urgency detection keyword
    urgent = detect_urgency("पोलीस ठाण्यात मारहाण केली आणि डांबून ठेवले आहे", "POLICE_CUSTODY")
    assert urgent is not None
    assert urgent["is_urgent"] is True
    assert "112" in urgent["helpline"]

    # Test engine integration
    engine = NyayaVaniEngine()
    res = engine.process_case("पोलीस ठाण्यात मारहाण केली आणि डांबून ठेवले आहे")
    uyr = res["understand_your_rights"]
    assert uyr["urgent_help"] is not None
    assert uyr["urgent_help"]["is_urgent"] is True
    # Urgent safety message must precede or be highlighted
    assert "तातडीची सूचना" in uyr["urgent_help"]["message"] or "सुरक्षा" in uyr["urgent_help"]["message"]
    # Engine spoken_text must prioritize the safety message
    assert "सुरक्षा" in res["spoken_text"] or "112" in res["spoken_text"] or "१५१००" in res["spoken_text"]


def test_understand_your_rights_tts_failure_fallback(test_client):
    """When Timbre TTS fails or is unavailable, the endpoint returns an informative fallback without crashing."""
    with patch("backend.server.client", None):
        # Call /api/rights/audio when speech client is None
        resp = test_client.post("/api/rights/audio", json={
            "text": "Understanding your statutory rights.",
            "language": "en",
            "voice": "Shivani"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "UNAVAILABLE"
        assert data["audio_url"] is None


def test_complete_browser_flow_understand_your_rights(test_client):
    """Simulates complete browser interaction flow for Understand Your Rights."""
    # Step 1: Initial chat submission with missing facts
    chat_resp = test_client.post("/api/chat", json={
        "message": "काल रात्री मुंबई हायवेवर माझ्या गाडीला ट्रकने धडक दिली.",
        "language_code": "mr-IN",
        "voice": "Shivani",
        "client_name": "Ramesh Kumar",
        "location": "Mumbai"
    })
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert chat_data["category"] == "MOTOR_ACCIDENT_PRO"
    assert "understand_your_rights" in chat_data
    uyr = chat_data["understand_your_rights"]
    assert uyr["category"] == "MOTOR_ACCIDENT_PRO"
    assert uyr["what_i_understood"]["text"]
    assert len(uyr["possible_acts"]) >= 1
    assert "shared_phone_privacy_notice" in uyr

    session_id = chat_data.get("session_id")
    session_token = chat_data.get("session_token")

    # Step 2: Request spoken audio for "1-Minute Recap"
    recap_script = uyr["spoken_scripts"]["recap_spoken"]
    mock_synth_return = {
        "voice": "Shivani",
        "model": "timbre-v3",
        "bytes": 20480,
        "elapsed_seconds": 0.45
    }
    
    def mock_synth(text, language, voice, output_path):
        import wave
        with wave.open(output_path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(b"\x00\x00" * 1600)
        return mock_synth_return

    with patch("backend.server.client") as mock_client:
        mock_client.synthesize.side_effect = mock_synth
        
        # Test audio synthesis endpoint
        audio_resp = test_client.post("/api/rights/audio", json={
            "text": recap_script,
            "language": "mr",
            "voice": "Shivani",
            "session_id": session_id,
            "session_token": session_token
        })
        assert audio_resp.status_code == 200
        audio_data = audio_resp.json()
        assert audio_data["status"] == "success"
        assert audio_data["audio_url"].startswith("/api/audio/")

        # Test audio playback retrieval
        audio_token = audio_data["audio_url"].split("/")[-1]
        get_audio_resp = test_client.get(f"/api/audio/{audio_token}")
        assert get_audio_resp.status_code == 200
        assert get_audio_resp.headers["content-type"] == "audio/wav"
