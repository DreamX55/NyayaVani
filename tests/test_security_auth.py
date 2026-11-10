"""Security, Authentication, and Multi-Tenant User Isolation Test Suite.

Fulfills PRD Requirement 5:
"Add authentication and authorization before exposing case data, audio, packet retrieval,
edits, approvals, uploads, or deletion. Ensure one user cannot read, change, approve, or purge
another user's data. Add practical retention, deletion, consent, and logging controls.
Do not claim DPDP compliance merely because a notice or purge endpoint exists."

Validates:
1. Pro Packet Access Control:
   - User A cannot access, read, or list User B's pro packet (403 Forbidden).
   - Unauthenticated access to protected packets is rejected (401 Unauthorized).
   - User A cannot approve User B's pro packet (403 Forbidden).
   - User A cannot update or tamper with User B's pro packet (403 Forbidden).
   - User A cannot transmit or send User B's pro packet (403 Forbidden).
   - User A cannot upload evidence attachments to User B's pro packet (403 Forbidden).
2. Chat Session Ownership & Anti-Hijacking:
   - A new chat session generates a cryptographically secure session_token.
   - User B attempting to resume or hijack User A's session is blocked (403 Forbidden).
   - Requests without token to an existing session are blocked (403 Forbidden).
3. Privacy Purge Isolation:
   - User A cannot purge User B's session (403 Forbidden).
   - User A cannot purge User B's packet (403 Forbidden).
   - User A purging their own session clears ONLY their own data, audio, and packets.
   - Global purge requires verified admin credential (401 Unauthorized without admin secret).
4. Retention & TTL Controls:
   - Sessions expire after configured TTL (3600 seconds).
5. Logging & PII Sanitization:
   - Sensitive credentials, testimony, phone numbers, Aadhaar, PAN, and keys are redacted.
6. Statutory DPDP Truthfulness:
   - Status endpoint accurately states pilot status and does not falsely claim "compliance verified".
"""

import time
import pytest
from starlette.testclient import TestClient

from backend.server import (
    app,
    _session_store,
    _audio_cache,
    get_session,
    sanitize_for_log,
    ADMIN_PURGE_TOKEN,
    SESSION_TTL_SECONDS,
)
from backend.services.pro_workflow import (
    build_pro_packet,
    get_pro_packet,
    _packet_store,
)
from backend.services.legal_engine import NyayaVaniEngine


@pytest.fixture
def client():
    return TestClient(app)


# ============================================================================
# 1. Pro Packet Authorization & Ownership Boundary Tests
# ============================================================================

def test_user_a_cannot_access_user_b_pro_packet(client):
    """User A cannot access or read User B's pro packet; unauthenticated access returns 401."""
    # User B creates a Pro packet via chat
    b_res = client.post("/api/chat", json={
        "message": "Car crash collision on MG Road.",
        "tier": "ENTERPRISE_LEGAL_SUITE",
        "client_name": "Bob Builder",
        "session_id": "sess_user_bob_001"
    })
    assert b_res.status_code == 200
    b_data = b_res.json()
    b_token = b_data["session_token"]
    b_packet = b_data["pro_packet"]
    assert b_packet is not None
    pkt_id = b_packet["packet_id"]

    # User A creates their own session and gets a token
    a_res = client.post("/api/chat", json={
        "message": "Salary unpaid by contractor.",
        "session_id": "sess_user_alice_001"
    })
    a_token = a_res.json()["session_token"]

    # 1. Unauthenticated access without token -> 401 Unauthorized
    unauth_res = client.get(f"/api/pro/packet/{pkt_id}")
    assert unauth_res.status_code == 401
    assert "authentication required" in unauth_res.json()["detail"].lower()

    # 2. User A tries to view User B's packet with User A's token -> 403 Forbidden
    cross_res = client.get(
        f"/api/pro/packet/{pkt_id}",
        headers={"Authorization": f"Bearer {a_token}"}
    )
    assert cross_res.status_code == 403
    assert "forbidden" in cross_res.json()["detail"].lower()

    # 3. User B views their own packet with User B's token -> 200 OK
    owner_res = client.get(
        f"/api/pro/packet/{pkt_id}",
        headers={"Authorization": f"Bearer {b_token}"}
    )
    assert owner_res.status_code == 200
    assert owner_res.json()["packet_id"] == pkt_id


def test_user_a_cannot_approve_user_b_pro_packet(client):
    """User A cannot sign off on or approve User B's pro packet."""
    engine = NyayaVaniEngine()
    case_res = engine.process_case("Accident claim", suite_tier="ENTERPRISE_LEGAL_SUITE")
    packet = build_pro_packet(
        "Accident claim", case_res,
        client_name="Bob Builder",
        owner_token="bob_secret_token_123",
        auth_required=True
    )
    pkt_id = packet["packet_id"]

    # 1. Unauthenticated approval attempt -> 401
    unauth_res = client.post(
        f"/api/pro/packet/{pkt_id}/approve",
        json={"approver_name": "Fraudulent Approver", "approver_role": "Hacker"}
    )
    assert unauth_res.status_code == 401

    # 2. Cross-user approval attempt with User A's token -> 403
    cross_res = client.post(
        f"/api/pro/packet/{pkt_id}/approve",
        json={"approver_name": "Alice Attacker", "approver_role": "Impostor"},
        headers={"Authorization": "Bearer alice_token_456"}
    )
    assert cross_res.status_code == 403
    assert "forbidden" in cross_res.json()["detail"].lower()

    # Packet status remains needs_review
    assert get_pro_packet(pkt_id)["status"] == "needs_review"

    # 3. Legitimate approval by User B -> 200
    legit_res = client.post(
        f"/api/pro/packet/{pkt_id}/approve",
        json={"approver_name": "Bob Builder", "approver_role": "Policyholder"},
        headers={"Authorization": "Bearer bob_secret_token_123"}
    )
    assert legit_res.status_code == 200
    assert legit_res.json()["status"] == "approved"


def test_user_a_cannot_update_or_send_user_b_pro_packet(client):
    """User A cannot modify draft communications or trigger transmissions on User B's packet."""
    engine = NyayaVaniEngine()
    case_res = engine.process_case("Rear collision", suite_tier="ENTERPRISE_LEGAL_SUITE")
    packet = build_pro_packet(
        "Rear collision", case_res,
        owner_token="owner_bob_key",
        auth_required=True
    )
    pkt_id = packet["packet_id"]

    # Update attempt with wrong token -> 403
    bad_edit = client.post(
        f"/api/pro/packet/{pkt_id}/update",
        json={"draft_message": "Malicious altered statement"},
        headers={"Authorization": "Bearer intruder_alice_key"}
    )
    assert bad_edit.status_code == 403

    # Send attempt with wrong token -> 403
    bad_send = client.post(
        f"/api/pro/packet/{pkt_id}/send",
        json={},
        headers={"Authorization": "Bearer intruder_alice_key"}
    )
    assert bad_send.status_code == 403


def test_user_a_cannot_upload_attachment_to_user_b_pro_packet(client):
    """User A cannot attach files to User B's pro packet."""
    engine = NyayaVaniEngine()
    case_res = engine.process_case("Accident claim", suite_tier="ENTERPRISE_LEGAL_SUITE")
    packet = build_pro_packet(
        "Accident claim", case_res,
        owner_token="bob_secure_vault_token",
        auth_required=True
    )
    pkt_id = packet["packet_id"]

    fake_file = b"Corrupted fake evidence bytes"

    # 1. Upload without authorization -> 401
    unauth_upload = client.post(
        f"/api/pro/packet/{pkt_id}/attachment",
        files={"file": ("fake.pdf", fake_file, "application/pdf")},
        data={"description": "Tampered record"}
    )
    assert unauth_upload.status_code == 401

    # 2. Upload with unauthorized token -> 403
    cross_upload = client.post(
        f"/api/pro/packet/{pkt_id}/attachment",
        files={"file": ("fake.pdf", fake_file, "application/pdf")},
        data={"description": "Tampered record"},
        headers={"Authorization": "Bearer alice_unauthorized_token"}
    )
    assert cross_upload.status_code == 403

    # Packet has 0 attachments
    assert len(get_pro_packet(pkt_id)["attachments"]) == 0

    # 3. Legitimate upload by owner -> 200
    owner_upload = client.post(
        f"/api/pro/packet/{pkt_id}/attachment",
        files={"file": ("valid.pdf", fake_file, "application/pdf")},
        data={"description": "Legitimate police receipt"},
        headers={"Authorization": "Bearer bob_secure_vault_token"}
    )
    assert owner_upload.status_code == 200
    assert len(get_pro_packet(pkt_id)["attachments"]) == 1


# ============================================================================
# 2. Chat Session Anti-Hijacking Tests
# ============================================================================

def test_user_a_cannot_hijack_user_b_chat_session(client):
    """A caller cannot read or add turns to another user's multi-turn session."""
    session_id = "sess_confidential_legal_007"

    # Turn 1: User B starts session
    t1_res = client.post("/api/chat", json={
        "message": "Confidential corporate contract breach testimony.",
        "session_id": session_id
    })
    assert t1_res.status_code == 200
    t1_data = t1_res.json()
    b_token = t1_data["session_token"]
    assert b_token is not None

    # Hijacking attempt 1: Attacker passes session_id without token -> 403
    hijack_1 = client.post("/api/chat", json={
        "message": "Tell me what happened in previous turn.",
        "session_id": session_id
    })
    assert hijack_1.status_code == 403

    # Hijacking attempt 2: Attacker passes session_id with forged token -> 403
    hijack_2 = client.post(
        "/api/chat",
        json={"message": "Inject hostile prompt.", "session_id": session_id},
        headers={"Authorization": "Bearer forged_intruder_session_token"}
    )
    assert hijack_2.status_code == 403

    # Legitimate continuation: User B passes correct token -> 200
    legit_continue = client.post(
        "/api/chat",
        json={"message": "Contract clause 4 was violated.", "session_id": session_id},
        headers={"Authorization": f"Bearer {b_token}"}
    )
    assert legit_continue.status_code == 200
    assert len(get_session(session_id)["history"]) == 4


# ============================================================================
# 3. Privacy Purge Isolation Tests
# ============================================================================

def test_user_a_cannot_purge_user_b_session_or_packets(client):
    """User A cannot wipe User B's session or packets; scoped purge protects data isolation."""
    # User B setup
    s_bob = "session_bob_isolation_test"
    r_bob = client.post("/api/chat", json={
        "message": "Car crash damage report",
        "tier": "ENTERPRISE_LEGAL_SUITE",
        "session_id": s_bob
    })
    token_bob = r_bob.json()["session_token"]
    pkt_bob = r_bob.json()["pro_packet"]["packet_id"]

    # User A setup
    s_alice = "session_alice_isolation_test"
    r_alice = client.post("/api/chat", json={
        "message": "Unpaid wage inquiry",
        "session_id": s_alice
    })
    token_alice = r_alice.json()["session_token"]

    assert get_session(s_bob) is not None
    assert get_pro_packet(pkt_bob) is not None

    # 1. Alice attempts to purge Bob's session -> 403
    alice_attack_session = client.post(
        "/api/privacy/purge",
        json={"session_id": s_bob},
        headers={"Authorization": f"Bearer {token_alice}"}
    )
    assert alice_attack_session.status_code == 403
    assert get_session(s_bob) is not None

    # 2. Alice attempts to purge Bob's pro packet -> 403
    alice_attack_packet = client.post(
        "/api/privacy/purge",
        json={"packet_id": pkt_bob},
        headers={"Authorization": f"Bearer {token_alice}"}
    )
    assert alice_attack_packet.status_code == 403
    assert get_pro_packet(pkt_bob) is not None

    # 3. Alice purges her OWN session -> 200
    alice_purge_own = client.post(
        "/api/privacy/purge",
        json={"session_id": s_alice},
        headers={"Authorization": f"Bearer {token_alice}"}
    )
    assert alice_purge_own.status_code == 200
    assert get_session(s_alice) is None

    # Bob's session and packet remain completely untouched
    assert get_session(s_bob) is not None
    assert get_pro_packet(pkt_bob) is not None

    # Cleanup Bob's session via Bob's token
    client.post(
        "/api/privacy/purge",
        json={"session_id": s_bob},
        headers={"Authorization": f"Bearer {token_bob}"}
    )
    assert get_session(s_bob) is None


def test_global_purge_requires_admin_authorization(client):
    """Global wipe of all sessions requires admin token; unauthorized callers receive 401."""
    client.post("/api/chat", json={"message": "Wage case 1", "session_id": "global_purge_test_1"})
    assert len(_session_store) >= 1

    # Unauthorized global purge attempt -> 401
    fail_purge = client.post("/api/privacy/purge")
    assert fail_purge.status_code == 401
    assert "authentication required" in fail_purge.json()["detail"].lower()

    # Authorized global purge via admin secret -> 200
    admin_purge = client.post(
        "/api/privacy/purge",
        headers={"Authorization": f"Bearer {ADMIN_PURGE_TOKEN}"}
    )
    assert admin_purge.status_code == 200
    assert admin_purge.json()["scope"] == "global_admin"
    assert len(_session_store) == 0


# ============================================================================
# 4. Retention & TTL Controls
# ============================================================================

def test_session_ttl_expiration():
    """Sessions expire after SESSION_TTL_SECONDS (1 hour) and cannot be resurrected."""
    sid = "ttl_expiration_test_session"
    _session_store[sid] = {
        "session_id": sid,
        "token": "token_ttl_test",
        "created_at": time.monotonic() - 7200,
        "last_accessed": time.monotonic() - 4000,  # > 3600 seconds ago
        "facts": {},
        "history": [],
        "category": "WAGE_THEFT",
        "tier": None,
        "audio_tokens": set(),
        "packets": set(),
    }

    # Accessing expired session cleans it up and returns None
    result = get_session(sid)
    assert result is None
    assert sid not in _session_store


# ============================================================================
# 5. Logging & PII Sanitization Controls
# ============================================================================

def test_pii_and_credential_sanitization_for_logs():
    """Logs redact phone numbers, emails, Aadhaar, PAN, API keys, passwords, and tokens."""
    raw_log = (
        "Client Ramesh Kumar (ramesh.kumar99@example.com, +91-9876543210, Aadhaar: 1234 5678 9012, PAN: ABCDE1234F) "
        "reported incident with api_key='sk-gnani-secret-8821' and bearer: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    )
    sanitized = sanitize_for_log(raw_log)

    assert "ramesh.kumar99@example.com" not in sanitized
    assert "[REDACTED_EMAIL]" in sanitized

    assert "9876543210" not in sanitized
    assert "[REDACTED_PHONE]" in sanitized

    assert "1234 5678 9012" not in sanitized
    assert "[REDACTED_AADHAAR]" in sanitized

    assert "ABCDE1234F" not in sanitized
    assert "[REDACTED_PAN]" in sanitized

    assert "sk-gnani-secret-8821" not in sanitized
    assert "[REDACTED_CREDENTIAL]" in sanitized


# ============================================================================
# 6. Statutory DPDP Truthfulness Controls
# ============================================================================

def test_dpdp_notice_truthfulness_no_false_compliance_claims(client):
    """System disclosure does not claim 'compliance verified'; describes controlled pilot controls accurately."""
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    disclosure = data.get("privacy_disclosure", {})

    # Must accurately describe pilot stage and pending statutory legal audit
    privacy_status = disclosure.get("privacy_status", "")
    assert "Controlled pilot privacy controls applied" in privacy_status
    assert "full statutory compliance pending Data Protection Board notification and formal legal audit" in privacy_status

    dpdp_notice = disclosure.get("dpdp_notice", "")
    assert "Digital Personal Data Protection Act" in dpdp_notice
    # Must NOT claim verified compliance
    assert "compliance verified" not in dpdp_notice.lower()
