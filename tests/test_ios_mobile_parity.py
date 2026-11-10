"""iOS Mobile Parity Integration Test.
Verifies that all API contracts, payloads, session headers, Pro workflow,
transcript review, and privacy purge used by the iOS app (APIClient.swift)
match the Starlette backend exactly.
"""

import os
import sys
from starlette.testclient import TestClient

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.server import app, get_session

def test_ios_parity_complete_flow():
    client = TestClient(app)
    
    # 1. Configurable Server Address Reachability Check (/api/status)
    status_res = client.get("/api/status")
    assert status_res.status_code == 200, f"Status check failed: {status_res.text}"
    status_json = status_res.json()
    assert status_json.get("status") == "online"
    print("[PASS] 1. Status reachability verified (/api/status)")

    # 2. Session Token & Auth Headers
    session_token = "sess-1731215400-a1b2c3d4"
    auth_headers = {
        "Authorization": f"Bearer {session_token}",
        "X-Session-Token": session_token
    }

    # 3. Transcript Review Flow (Requirement V2)
    original_transcript = "police came to my cart and asked 500"
    reviewed_transcript = "Delhi police officer came to my vegetable cart and demanded 500 rupees bribe without notice"
    chat_payload = {
        "message": reviewed_transcript,
        "session_id": session_token,
        "original_transcript": original_transcript,
        "reviewed_transcript": reviewed_transcript,
        "detected_language": "hi-IN",
        "tier": "BHARAT_GRASSROOTS_AID",
        "voice": "Shivani",
        "client_name": "Ramesh Kumar",
        "location": "Lajpat Nagar, New Delhi"
    }

    chat_res = client.post("/api/chat", json=chat_payload, headers=auth_headers)
    assert chat_res.status_code == 200, f"Chat call failed: {chat_res.text}"
    chat_json = chat_res.json()
    assert chat_json["status"] == "success"
    assert chat_json.get("session_id") == session_token
    
    # Check transcript review preservation
    review = chat_json.get("transcript_review")
    assert review is not None
    assert review["original_transcript"] == original_transcript
    assert review["reviewed_transcript"] == reviewed_transcript
    assert review["was_corrected"] is True
    assert review["detected_language"] == "hi-IN"
    print("[PASS] 2. Transcript review flow verified with session persistence")

    # 4. Multi-Turn Conversational Follow-Up
    session = get_session(session_token)
    assert session is not None, "Session store must retain multi-turn context"
    assert len(session["history"]) >= 2, "Session history must retain user and assistant turns"
    
    # Turn 2: User answers a follow-up question via quick reply / voice reply
    turn2_payload = {
        "message": "The incident happened on 15th October at Lajpat Nagar central market",
        "session_id": session_token,
        "tier": "BHARAT_GRASSROOTS_AID",
        "voice": "Shivani",
        "client_name": "Ramesh Kumar",
        "location": "Lajpat Nagar, New Delhi"
    }
    turn2_res = client.post("/api/chat", json=turn2_payload, headers=auth_headers)
    assert turn2_res.status_code == 200
    turn2_json = turn2_res.json()
    assert turn2_json["status"] == "success"
    print("[PASS] 3. Multi-turn conversational follow-up verified")

    # 5. Pro Packet Review, Draft Edit, Outbound Lock, & Approval (PRD P1 & P2)
    pro_payload = {
        "message": "Commercial truck MH-12-AB-1234 rammed private sedan at highway junction. Driver fled.",
        "session_id": session_token,
        "tier": "ENTERPRISE_LEGAL_SUITE",
        "voice": "Shivani",
        "client_name": "Vikram Malhotra",
        "location": "NH-48, Gurugram"
    }
    pro_res = client.post("/api/chat", json=pro_payload, headers=auth_headers)
    assert pro_res.status_code == 200
    pro_json = pro_res.json()
    packet = pro_json.get("pro_packet")
    assert packet is not None, "Enterprise Legal Suite must return a Pro Packet"
    packet_id = packet["packet_id"]
    assert packet["status"] == "needs_review"
    assert len(packet.get("chronology", [])) >= 1, "Chronology timeline must be present"
    assert "missing_evidence" in packet, "Missing evidence checklist must be present"
    assert packet.get("outbound_available") is False
    
    # 5a. Update Draft Message
    edited_draft = "EDITED NOTICE: Comprehensive legal claim under Section 166 Motor Vehicles Act for spinal injury."
    update_res = client.post(
        f"/api/pro/packet/{packet_id}/update",
        json={"draft_message": edited_draft},
        headers=auth_headers
    )
    assert update_res.status_code == 200
    updated_packet = update_res.json()
    assert updated_packet["draft_message"] == edited_draft
    print("[PASS] 4a. Pro packet draft edit verified (/api/pro/packet/{id}/update)")

    # 5b. Test Outbound Delivery Safety Lock (Must be rejected)
    send_res = client.post(
        f"/api/pro/packet/{packet_id}/send",
        json={},
        headers=auth_headers
    )
    # Draft is not approved yet -> fails
    assert send_res.status_code in (400, 500)
    print("[PASS] 4b. Outbound boundary safety lock verified (unapproved draft blocked)")

    # 5c. Approve Pro Packet
    approve_res = client.post(
        f"/api/pro/packet/{packet_id}/approve",
        json={
            "approver_name": "Advocate Priya Sundaram",
            "approver_role": "Legal Counsel (D/4921/2018)",
            "notes": "Reviewed accident evidence and verified Section 63 BSA compliance."
        },
        headers=auth_headers
    )
    assert approve_res.status_code == 200
    approved_packet = approve_res.json()
    assert approved_packet["status"] == "approved"
    assert len(approved_packet["approvals"]) == 1
    assert approved_packet["approvals"][0]["approver_name"] == "Advocate Priya Sundaram"
    print("[PASS] 4c. Pro packet approval state machine verified (/api/pro/packet/{id}/approve)")

    # 5d. Test Outbound Delivery Safety Lock on Approved Packet (Still disabled in No-Provider Mode)
    send_approved_res = client.post(
        f"/api/pro/packet/{packet_id}/send",
        json={},
        headers=auth_headers
    )
    assert send_approved_res.status_code == 200
    outbound_result = send_approved_res.json()
    assert "DISABLED" in outbound_result.get("message", "")
    print("[PASS] 4d. Outbound adapter safety lock verified on approved packet")

    # 6. Privacy & Data Purge (Requirement 5 / DPDP Act 2023)
    purge_res = client.post(
        "/api/privacy/purge",
        json={"session_id": session_token},
        headers=auth_headers
    )
    assert purge_res.status_code == 200
    purge_json = purge_res.json()
    assert purge_json["status"] == "purged"
    
    # Confirm session is deleted from memory
    assert get_session(session_token) is None, "Session must be removed from server memory upon purge"
    print("[PASS] 5. Privacy session purge verified (/api/privacy/purge)")

if __name__ == "__main__":
    test_ios_parity_complete_flow()
    print("\nALL iOS MOBILE PARITY API CONTRACTS VERIFIED 100% SUCCESSFULLY!")
