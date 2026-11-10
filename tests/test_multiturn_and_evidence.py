"""Unit tests for Multi-Turn Session Memory and Real Evidence Upload capabilities.

Validates:
1. Multi-turn session memory and authorization in backend/server.py:
   - In-memory session store mapping session_id to facts, history, category, and session token.
   - Session token generation and validation across multi-turn interactions.
   - Protection against session hijacking (403 on invalid or missing token).
   - Merging structured facts across turns.
   - Session preservation of category and advancement of intake status.
   - Privacy purge of specific sessions and all sessions with authorization.
2. Real evidence upload in backend/services/pro_workflow.py and backend/server.py:
   - add_attachment helper with SHA-256 fingerprinting and metadata tracking.
   - POST /api/pro/packet/{packet_id}/attachment multipart upload endpoint.
   - Error handling: 404 on missing packet, 400 on approved packet, 422 on missing file.
"""

import hashlib
import pytest
from starlette.testclient import TestClient

from backend.server import app, _session_store, get_session, _audio_cache, ADMIN_PURGE_TOKEN
from backend.services.legal_engine import NyayaVaniEngine
from backend.services.pro_workflow import (
    build_pro_packet,
    get_pro_packet,
    approve_pro_packet,
    add_attachment,
    _packet_store,
)


@pytest.fixture
def client():
    return TestClient(app)


# ============================================================================
# Multi-Turn Session Memory Tests
# ============================================================================

def test_chat_without_session_id_returns_none(client):
    """Chat request without session_id processes normally and returns session_id as None."""
    payload = {
        "message": "My boss refuses to pay my wages.",
        "client_name": "Ramesh Kumar",
        "location": "Delhi"
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] is None
    assert data["category"] == "WAGE_THEFT"


def test_multiturn_session_accumulates_facts_and_advances_intake(client):
    """
    Multi-turn test:
    Turn 1: Initial complaint (facts missing -> needs_details), generates session_token.
    Hijack check: Turn 2 without matching token is blocked with 403.
    Turn 2: Provide other_party and incident_date with valid session_token (category preserved).
    Turn 3: Provide specific_details (intake advances to ready_for_human_review).
    """
    session_id = "test_session_turn_accum_001"

    # Turn 1
    t1_payload = {
        "message": "My boss refuses to pay my wages for October.",
        "client_name": "Sunil Sharma",
        "location": "Bengaluru",
        "session_id": session_id
    }
    t1_res = client.post("/api/chat", json=t1_payload)
    assert t1_res.status_code == 200
    t1_data = t1_res.json()
    assert t1_data["session_id"] == session_id
    assert t1_data["category"] == "WAGE_THEFT"
    assert t1_data["needs_more_information"] is True
    assert t1_data["intake"]["status"] == "needs_details"
    session_token = t1_data.get("session_token")
    assert session_token is not None

    # Verify session store state after Turn 1
    session = get_session(session_id)
    assert session is not None
    assert session["category"] == "WAGE_THEFT"
    assert session["facts"]["client_name"] == "Sunil Sharma"
    assert session["facts"]["location"] == "Bengaluru"
    assert len(session["history"]) == 2  # 1 user + 1 assistant

    # Anti-Hijacking check: Attempt Turn 2 without token or with bad token -> 403
    t2_payload = {
        "message": "The company is Apex Infra and this happened on 2026-11-01.",
        "session_id": session_id,
        "meta": {
            "other_party": "Apex Infra Pvt Ltd",
            "incident_date": "2026-11-01"
        }
    }
    hijack_res = client.post("/api/chat", json=t2_payload)
    assert hijack_res.status_code == 403

    bad_token_res = client.post(
        "/api/chat",
        json=t2_payload,
        headers={"Authorization": "Bearer fraudulent_intruder_token"}
    )
    assert bad_token_res.status_code == 403

    # Turn 2: Authorized with session token
    t2_res = client.post(
        "/api/chat",
        json=t2_payload,
        headers={"Authorization": f"Bearer {session_token}"}
    )
    assert t2_res.status_code == 200
    t2_data = t2_res.json()
    # Category MUST remain WAGE_THEFT from session memory
    assert t2_data["category"] == "WAGE_THEFT"
    assert t2_data["needs_more_information"] is True

    session = get_session(session_id)
    assert session["facts"]["other_party"] == "Apex Infra Pvt Ltd"
    assert session["facts"]["incident_date"] == "2026-11-01"
    assert session["facts"]["client_name"] == "Sunil Sharma"
    assert len(session["history"]) == 4

    # Turn 3: Complete remaining required fact with authorization
    t3_payload = {
        "message": "The pending amount is 42,000 INR for masonry work.",
        "session_id": session_id,
        "meta": {
            "specific_details": "42,000 INR unpaid wages for masonry work."
        }
    }
    t3_res = client.post(
        "/api/chat",
        json=t3_payload,
        headers={"X-Session-Token": session_token}
    )
    assert t3_res.status_code == 200
    t3_data = t3_res.json()
    # Now all required facts are present in accumulated session memory!
    assert t3_data["needs_more_information"] is False
    assert t3_data["intake"]["status"] == "ready_for_human_review"
    assert "42,000 INR" in t3_data["formal_document"]
    assert "Apex Infra Pvt Ltd" in t3_data["formal_document"]
    assert "Sunil Sharma" in t3_data["formal_document"]
    assert len(get_session(session_id)["history"]) == 6


def test_session_purge_specific_session(client):
    """Purge request with session_id purges only authorized session and prevents cross-user purge."""
    s1 = "sess_purge_a"
    s2 = "sess_purge_b"
    r1 = client.post("/api/chat", json={"message": "Unpaid salary issue", "session_id": s1})
    r2 = client.post("/api/chat", json={"message": "Traffic collision issue", "session_id": s2})
    t1 = r1.json()["session_token"]
    t2 = r2.json()["session_token"]

    assert get_session(s1) is not None
    assert get_session(s2) is not None

    # Cross-user unauthorized purge attempt: User 1 tries to purge User 2's session -> 403
    cross_res = client.post(
        "/api/privacy/purge",
        json={"session_id": s2},
        headers={"Authorization": f"Bearer {t1}"}
    )
    assert cross_res.status_code == 403
    assert get_session(s2) is not None

    # Purge s1 with User 1's token
    purge_res = client.post(
        "/api/privacy/purge",
        json={"session_id": s1},
        headers={"Authorization": f"Bearer {t1}"}
    )
    assert purge_res.status_code == 200
    purge_data = purge_res.json()
    assert purge_data["status"] == "purged"
    assert purge_data["session_id"] == s1
    assert purge_data["purged"] is True

    # s1 is gone, s2 remains
    assert get_session(s1) is None
    assert get_session(s2) is not None

    # Purge s2 via query parameter with User 2's token
    purge_res2 = client.post(
        f"/api/privacy/purge?session_id={s2}",
        headers={"X-Session-Token": t2}
    )
    assert purge_res2.status_code == 200
    assert get_session(s2) is None


def test_session_purge_all_clears_sessions(client):
    """Global purge requires admin authorization; unauthorized global purge is rejected."""
    client.post("/api/chat", json={"message": "Unpaid salary", "session_id": "sess_all_1"})
    client.post("/api/chat", json={"message": "Car accident", "session_id": "sess_all_2"})
    assert len(_session_store) >= 2

    # Unauthenticated global purge attempt when user sessions exist -> 401
    unauth_res = client.post("/api/privacy/purge")
    assert unauth_res.status_code == 401

    # Authorized global purge via admin secret
    purge_res = client.post(
        "/api/privacy/purge",
        headers={"Authorization": f"Bearer {ADMIN_PURGE_TOKEN}"}
    )
    assert purge_res.status_code == 200
    data = purge_res.json()
    assert data["status"] == "purged"
    assert data["sessions_cleared"] >= 2
    assert len(_session_store) == 0


# ============================================================================
# Real Evidence Upload Tests
# ============================================================================

def test_add_attachment_helper_computes_sha256_and_records_metadata():
    """add_attachment computes SHA-256 digest, byte size, timestamp, and appends to packet."""
    engine = NyayaVaniEngine()
    case_res = engine.process_case("Accident on ring road", suite_tier="ENTERPRISE_LEGAL_SUITE")
    packet = build_pro_packet("Accident on ring road", case_res)
    pkt_id = packet["packet_id"]

    file_bytes = b"Sample dashcam video footage bytes"
    expected_hash = hashlib.sha256(file_bytes).hexdigest()

    record = add_attachment(
        packet_id=pkt_id,
        filename="dashcam_front.mp4",
        mime_type="video/mp4",
        file_bytes=file_bytes,
        description="Front bumper impact camera recording"
    )

    assert record["id"].startswith("att_")
    assert record["filename"] == "dashcam_front.mp4"
    assert record["mime_type"] == "video/mp4"
    assert record["file_size_bytes"] == len(file_bytes)
    assert record["sha256_hash"] == expected_hash
    assert "uploaded_at" in record
    assert record["description"] == "Front bumper impact camera recording"
    assert record["verified"] is False
    assert record["verification_status"] == "unverified_pending_counsel_review"

    # Verify attachment is in packet
    updated_pkt = get_pro_packet(pkt_id)
    assert len(updated_pkt["attachments"]) == 1
    assert updated_pkt["attachments"][0]["sha256_hash"] == expected_hash


def test_evidence_upload_endpoint_success(client):
    """POST /api/pro/packet/{packet_id}/attachment successfully uploads evidence item."""
    engine = NyayaVaniEngine()
    case_res = engine.process_case("Rear-end collision at traffic signal", suite_tier="ENTERPRISE_LEGAL_SUITE")
    packet = build_pro_packet("Rear-end collision", case_res)
    pkt_id = packet["packet_id"]

    photo_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    expected_hash = hashlib.sha256(photo_bytes).hexdigest()

    res = client.post(
        f"/api/pro/packet/{pkt_id}/attachment",
        files={"file": ("damage_bumper.png", photo_bytes, "image/png")},
        data={"description": "High resolution photograph of rear bumper dent"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["packet_id"] == pkt_id
    att = data["attachment"]
    assert att["filename"] == "damage_bumper.png"
    assert att["mime_type"] == "image/png"
    assert att["file_size_bytes"] == len(photo_bytes)
    assert att["sha256_hash"] == expected_hash
    assert att["description"] == "High resolution photograph of rear bumper dent"

    # Confirm retrieval via GET /api/pro/packet/{packet_id}
    get_res = client.get(f"/api/pro/packet/{pkt_id}")
    assert get_res.status_code == 200
    pkt_data = get_res.json()
    assert len(pkt_data["attachments"]) == 1
    assert pkt_data["attachments"][0]["sha256_hash"] == expected_hash


def test_evidence_upload_missing_packet_returns_404(client):
    """Attempting to upload evidence to a non-existent packet ID returns 404."""
    res = client.post(
        "/api/pro/packet/non_existent_pkt_999/attachment",
        files={"file": ("evidence.pdf", b"%PDF-1.4 dummy", "application/pdf")},
        data={"description": "Police receipt"}
    )
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_evidence_upload_to_approved_packet_returns_400(client):
    """Attempting to upload evidence after packet has been approved is blocked with 400."""
    engine = NyayaVaniEngine()
    case_res = engine.process_case("Accident claim", suite_tier="ENTERPRISE_LEGAL_SUITE")
    packet = build_pro_packet("Accident claim", case_res)
    pkt_id = packet["packet_id"]

    # Approve packet
    approve_pro_packet(pkt_id, approver_name="Anil Kumar")

    # Attempt attachment upload on approved packet
    res = client.post(
        f"/api/pro/packet/{pkt_id}/attachment",
        files={"file": ("late_evidence.pdf", b"%PDF data", "application/pdf")}
    )
    assert res.status_code == 400
    assert "approved" in res.json()["detail"].lower()


def test_evidence_upload_without_file_returns_422(client):
    """Posting to attachment endpoint without any file returns 422."""
    engine = NyayaVaniEngine()
    case_res = engine.process_case("Accident claim", suite_tier="ENTERPRISE_LEGAL_SUITE")
    packet = build_pro_packet("Accident claim", case_res)
    pkt_id = packet["packet_id"]

    res = client.post(
        f"/api/pro/packet/{pkt_id}/attachment",
        data={"description": "Description without file"}
    )
    assert res.status_code == 422
