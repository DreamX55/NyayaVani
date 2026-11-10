import os
import re
import pytest
from starlette.testclient import TestClient
from backend.server import app, _session_store, _audio_cache

client = TestClient(app)


def test_index_page_loads_and_contains_no_misleading_labels():
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # Prohibited misleading claims
    assert "verified legal counsel" not in html.lower()
    assert "certified legal draft" not in html.lower()
    assert "legal certificate" not in html.lower()
    assert "D/1482/2015" not in html
    assert "Adv. S. Sharma" not in html


def test_index_page_contains_accurate_legal_notices():
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    assert "Draft Incident Summary for Review — Not Legal Advice" in html
    assert "Statutory citations pending advocate verification" in html
    assert "Outbound transmission disabled (Review only)" in html


def test_live_recording_privacy_and_countdown_ui():
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # Explicit privacy notice before and during recording
    privacy_notice = "Your speech is transcribed securely. Audio is processed ephemerally on the server for live transcription. You can edit the transcript before legal triage."
    assert privacy_notice in html

    # Visible countdown elements for 30s limit
    assert 'id="recording-toast"' in html
    assert 'id="record-countdown"' in html
    assert 'id="record-timer"' in html
    assert 'id="record-progress"' in html


def test_transcript_review_and_preservation_flow():
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # Transcript review function and editable textarea
    assert "showTranscriptReview" in html
    assert "submitReviewedTranscript" in html
    assert 'id="reviewed-transcript"' in html
    assert "original_transcript" in html
    assert "reviewed_transcript" in html


def test_voice_conversational_ui_and_accessibility():
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # Talking agent UI controls
    assert "🎙️ Speak Answer" in html or "Speak Answer" in html
    assert 'role="button"' in html
    assert 'role="textbox"' in html
    assert "quick-reply-" in html
    assert "Enter" in html


def test_pro_packet_signoff_roles_and_safeguards():
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # Approved roles
    assert "Client" in html
    assert "Authorized Representative" in html
    assert "Independent Legal Counsel" in html

    # Clear safeguard that signing does not transmit to police, insurer, or court
    assert "Signing does <strong>NOT</strong> transmit this document to police, insurer, or court" in html or "Signing does NOT transmit this document to police, insurer, or court" in html


def test_voice_error_fallback_message():
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    fallback_msg = "Voice unavailable in this browser or network. You can type your account directly below."
    assert fallback_msg in html


def test_session_token_and_privacy_purge_integration():
    session_id = "test-session-ux-12345"
    session_token = "test-token-ux-12345"

    # Send chat message with session token in header and session_id in payload
    chat_res = client.post(
        "/api/chat",
        headers={"X-Session-Token": session_token, "Authorization": f"Bearer {session_token}"},
        json={
            "session_id": session_id,
            "message": "Street vendor cart evicted without survey notice",
            "tier": "BHARAT_GRASSROOTS_AID"
        }
    )
    assert chat_res.status_code == 200
    assert session_id in _session_store
    assert _session_store[session_id]["token"] == session_token

    # Purge session with session token header and session_id
    purge_res = client.post(
        "/api/privacy/purge",
        headers={"X-Session-Token": session_token},
        json={"session_id": session_id}
    )
    assert purge_res.status_code == 200
    purge_data = purge_res.json()
    assert purge_data["status"] == "purged"
    assert purge_data["session_id"] == session_id
    assert session_id not in _session_store
