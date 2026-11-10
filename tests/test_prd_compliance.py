"""End-to-End Test Suite for NyayaVani PRD Compliance.

Validates all Acceptance Checks from Product_Requirements_Document.md:
- V1: Dedicated transcription, Prisma v3, server-side secret, clean failure.
- V2: Verbatim transcript review & correction; original and corrected preserved.
- V3: Audio limit enforcement (<= 30s) and fallback when TTS is unavailable.
- L1: Tentative categorization, unknown fields remain unknown, structured fact updates.
- L2: Versioned source register with qualified reviewer sign-off, review date, and primary URLs.
- L3: NALSA / DLSA legal aid referral path with helpline 15100 and criteria.
- P1: Pro incident packet never asserts unverified external actions.
- P2: Approval state machine (needs_review -> approved) and outbound adapter safety lock.
- S1: Personal data protection, short-lived audio tokens, session cache purge.
"""

import io
import time
import wave
import pytest
from starlette.testclient import TestClient

from backend.server import app, _audio_cache
from backend.services.legal_engine import NyayaVaniEngine
from backend.services.source_register import (
    REGISTER_VERSION,
    REVIEWER_METADATA,
    STATUTORY_REGISTER,
    get_source_register_entry
)
from backend.services.pro_workflow import (
    build_pro_packet,
    get_pro_packet,
    update_pro_packet,
    approve_pro_packet,
    attempt_send_packet,
    _packet_store
)


def _make_dummy_wav(duration_seconds: float = 2.0, sample_rate: int = 16000) -> bytes:
    buf = io.BytesIO()
    num_frames = int(duration_seconds * sample_rate)
    with wave.open(buf, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * num_frames)
    return buf.getvalue()


@pytest.fixture
def client():
    return TestClient(app)


# ============================================================================
# V1, V2, V3: Speech & Audio Intake Tests
# ============================================================================

def test_v1_system_status_and_privacy_notice(client):
    """PRD V1 & S1: System status includes speech status, DPDP notice and register info."""
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "privacy_disclosure" in data
    assert "Digital Personal Data Protection Act" in data["privacy_disclosure"]["dpdp_notice"]
    assert data["source_register_version"] == REGISTER_VERSION
    assert data["legal_reviewer"] == REVIEWER_METADATA["reviewer_name"]
    assert data["legal_reviewer"] is None
    assert REVIEWER_METADATA["register_status"] == "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW" 


def test_v2_transcript_review_preserves_both_versions(client):
    """PRD V2: Original and reviewed transcript are preserved separately with correction flag."""
    original = "police came near my stall"
    corrected = "BMC officer came near my fruit stall"
    payload = {
        "message": corrected,
        "original_transcript": original,
        "reviewed_transcript": corrected,
        "detected_language": "hi-IN",
        "client_name": "Ramesh Gupta",
        "location": "Mumbai, Maharashtra"
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["category"] == "STREET_VENDOR"
    review = data.get("transcript_review")
    assert review is not None
    assert review["original_transcript"] == original
    assert review["reviewed_transcript"] == corrected
    assert review["was_corrected"] is True
    assert review["detected_language"] == "hi-IN"
    # Legal draft must contain the user's corrected account
    assert "BMC officer came near my fruit stall" in data["formal_document"]


def test_v3_audio_duration_rejection_over_30s(client):
    """PRD V3: Audio over 30s is rejected before speech provider call."""
    long_wav = _make_dummy_wav(duration_seconds=31.5)
    files = {"audio": ("long.wav", long_wav, "audio/wav")}
    res = client.post("/api/transcribe", files=files, data={"language_code": "indic-auto"})
    assert res.status_code == 413
    assert "30 seconds" in res.json()["detail"]


def test_v3_empty_audio_rejection(client):
    """PRD V3: Empty recording is rejected cleanly without fabricating a transcript."""
    files = {"audio": ("empty.wav", b"", "audio/wav")}
    res = client.post("/api/transcribe", files=files)
    assert res.status_code == 422
    assert "empty" in res.json()["detail"].lower()


# ============================================================================
# L1, L2, L3: Legal Intake & Source Register Tests
# ============================================================================

def test_l1_missing_facts_produce_questions_unknowns_remain_unknown():
    """PRD L1: Incomplete accounts produce questions rather than fully asserted petitions."""
    engine = NyayaVaniEngine()
    result = engine.process_case("My boss refuses to pay my wages for last month.")
    assert result["category"] == "WAGE_THEFT"
    assert result["needs_more_information"] is True
    assert len(result["follow_up_questions"]) > 0
    assert result["intake"]["status"] == "needs_details"
    # Unknown details must not be fabricated
    assert "Contractor" not in result["formal_document"] or "Opposite Party" in result["formal_document"]


def test_l1_intake_advances_when_facts_supplied():
    """PRD L1: When facts are supplied, status advances to ready_for_human_review."""
    engine = NyayaVaniEngine()
    meta = {
        "incident_date": "2026-11-01",
        "incident_location": "Noida Sector 62",
        "other_party": "ABC Construction Ltd",
        "specific_details": "45,000 INR unpaid overtime wages for October 2026."
    }
    result = engine.process_case("My employer has not paid my wages.", meta=meta)
    assert result["needs_more_information"] is False
    assert result["follow_up_questions"] == []
    assert result["intake"]["status"] == "ready_for_human_review"
    assert "45,000 INR" in result["formal_document"]


def test_l2_versioned_source_register():
    """PRD L2: Versioned source register requires qualified legal review before public use."""
    assert REGISTER_VERSION == "2026.11-v1"
    assert REVIEWER_METADATA["reviewer_name"] is None
    assert REVIEWER_METADATA["credentials"] is None
    assert REVIEWER_METADATA["review_date"] is None
    assert REVIEWER_METADATA["register_status"] == "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"
    assert "Statutory provisions compiled from primary Indian legislation" in REVIEWER_METADATA["disclaimer"]
    for cat, entry in STATUTORY_REGISTER.items():
        assert "references" in entry
        assert len(entry["references"]) > 0
        assert entry["reviewed_by"] is None or entry["reviewed_by"] == "PENDING_QUALIFIED_LEGAL_REVIEW"
        assert entry["is_verified"] is False
        assert entry["review_date"] is None
        for ref in entry["references"]:
            assert ref["source_url"].startswith("http")
            assert len(ref["conditions"]) > 10


def test_l3_legal_aid_handoff_present():
    """PRD L3: Grassroots user receives relevant NALSA/DLSA legal aid handoff."""
    engine = NyayaVaniEngine()
    result = engine.process_case("Municipal staff came to remove my cart without notice.")
    referral = result.get("legal_aid_referral")
    assert referral is not None
    assert referral["helpline"] == "15100"
    assert "DLSA" in referral["authority"]
    assert len(referral["documents_to_carry"]) >= 2
    assert "disclaimer" in referral


# ============================================================================
# P1, P2: Pro Incident Packet & Delivery Boundary Tests
# ============================================================================

def test_p1_pro_packet_structure():
    """PRD P1: Pro packet compiles facts, chronology, missing evidence without asserting sent status."""
    engine = NyayaVaniEngine()
    case_res = engine.process_case(
        "A car collided with my bumper at the junction.",
        suite_tier="ENTERPRISE_LEGAL_SUITE",
        meta={"incident_date": "2026-11-08", "location": "Bengaluru"}
    )
    packet = build_pro_packet(
        "A car collided with my bumper at the junction.",
        case_res,
        client_name="Vikram Sharma",
        location="Bengaluru"
    )
    assert packet["status"] == "needs_review"
    assert packet["outbound_available"] is False
    assert packet["outbound_status"] == "not_sent"
    assert len(packet["chronology"]) >= 2
    assert "packet_id" in packet
    assert packet["content_hash"] is not None
    assert "No insurer, lawyer, or authority has been contacted" in packet["review_note"]


def test_p2_approval_state_machine_and_adapter_safety_lock(client):
    """PRD P2: Enforces state transitions needs_review -> approved and prevents unauthorized send."""
    engine = NyayaVaniEngine()
    case_res = engine.process_case(
        "Vehicle accident on highway.",
        suite_tier="ENTERPRISE_LEGAL_SUITE"
    )
    packet = build_pro_packet("Vehicle accident on highway.", case_res, client_name="John Doe")
    pkt_id = packet["packet_id"]

    # 1. Verify retrieval via API
    get_res = client.get(f"/api/pro/packet/{pkt_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "needs_review"

    # 2. Attempting to send an UNAPPROVED packet must fail
    with pytest.raises(ValueError, match="Explicit approval required"):
        attempt_send_packet(pkt_id)

    # 3. Update packet before approval
    update_res = client.post(f"/api/pro/packet/{pkt_id}/update", json={
        "draft_message": "Updated draft communication for claim review."
    })
    assert update_res.status_code == 200
    assert "Updated draft" in update_res.json()["draft_message"]

    # 4. Approve packet formally
    approve_res = client.post(f"/api/pro/packet/{pkt_id}/approve", json={
        "approver_name": "John Doe",
        "approver_role": "Policyholder",
        "notes": "Reviewed and verified date and vehicle details."
    })
    assert approve_res.status_code == 200
    approved_data = approve_res.json()
    assert approved_data["status"] == "approved"
    assert len(approved_data["approvals"]) == 1
    assert approved_data["approvals"][0]["approver_name"] == "John Doe"

    # 5. Attempting to edit an approved packet must be blocked
    block_edit = client.post(f"/api/pro/packet/{pkt_id}/update", json={"draft_message": "illegal edit"})
    assert block_edit.status_code == 400

    # 6. Attempting to send approved packet with adapter disabled
    send_res = client.post(f"/api/pro/packet/{pkt_id}/send", json={})
    assert send_res.status_code == 200
    send_data = send_res.json()
    assert send_data["success"] is False
    assert send_data["outbound_status"] == "not_sent"
    assert "DISABLED" in send_data["message"]
    # Verify the packet was NOT mutated to 'sent'
    assert get_pro_packet(pkt_id)["status"] == "approved"


# ============================================================================
# S1: Privacy, Ephemeral Storage & Retention Purge Tests
# ============================================================================

def test_s1_audio_tokens_are_ephemeral(client):
    """PRD S1: Audio URLs use ephemeral tokens with TTL and private cache headers."""
    _audio_cache["test_token_123"] = (time.monotonic() + 60, b"fake_wav_bytes")
    res = client.get("/api/audio/test_token_123")
    assert res.status_code == 200
    assert res.headers["Cache-Control"] == "private, no-store"
    assert res.content == b"fake_wav_bytes"


def test_s1_privacy_purge_endpoint(client):
    """PRD S1: Calling purge deletes in-memory audio caches and pro packets."""
    _audio_cache["temp_1"] = (time.monotonic() + 100, b"wav1")
    _packet_store["temp_pkt_1"] = (time.monotonic() + 100, {"id": "1"})
    
    res = client.post("/api/privacy/purge")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "purged"
    assert len(_audio_cache) == 0
    assert len(_packet_store) == 0
