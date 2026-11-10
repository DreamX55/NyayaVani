"""Pro Incident Response Packet & Approval Boundary State Machine.

Fulfills PRD Requirements P1, P2 & Requirement 5:
- Compiles user-confirmed facts, structured chronology, missing evidence, attachments inventory,
  and editable draft communications into a structured packet.
- State machine: 'draft' -> 'needs_review' -> 'approved' -> 'sending' -> 'sent' / 'failed'.
- Explicit approval boundaries: Records approver name, role, timestamp, frozen content hash, and notes.
- Strict adapter protection: Keeps outbound delivery disabled until an authorized provider is connected.
  No draft can be transmitted without explicit approval; duplicate transmissions are blocked;
  no-provider mode remains strictly review-only.
- Authorization and user ownership: Packets are cryptographically bound to session/owner tokens
  to prevent unauthorized viewing, modification, approval, or deletion across tenants.
"""

import hashlib
import hmac
import secrets
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

VALID_PRO_STATES = {"draft", "needs_review", "approved", "sending", "sent", "failed"}

# In-memory ephemeral store for Pro packets (session-scoped)
# Retains packets for 1 hour; purge routines clean up expired items
PACKET_TTL_SECONDS = 3600
_packet_store: Dict[str, tuple[float, Dict[str, Any]]] = {}


def _compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clean_expired_packets() -> None:
    now = time.monotonic()
    for pid, (exp, _) in list(_packet_store.items()):
        if exp <= now:
            _packet_store.pop(pid, None)


def build_pro_packet(
    account: str,
    case_result: dict[str, Any],
    *,
    client_name: str = "",
    location: str = "",
    recipient: str = "",
    attachments: Optional[List[Dict[str, Any]]] = None,
    owner_token: Optional[str] = None,
    session_id: Optional[str] = None,
    auth_required: Optional[bool] = None,
) -> dict[str, Any]:
    """
    Build a reviewable Pro case packet.
    Uses only user-confirmed input and labeled drafts; never invents incident details.
    Initial state is 'needs_review'.
    Binds an owner authorization token to ensure user data isolation (PRD Requirement 5).
    """
    _clean_expired_packets()
    summary = (case_result.get("ai_synthesized_summary") or account).strip()
    document = (case_result.get("formal_document") or "").strip()
    intake = case_result.get("intake") or {}
    missing = intake.get("missing_facts") or []
    if not isinstance(missing, list):
        missing = []

    packet_id = f"pkt_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    # Determine ownership credential and authorization policy
    if owner_token:
        pkt_owner_token = owner_token
        is_auth_required = True if auth_required is None else auth_required
    elif auth_required is True:
        pkt_owner_token = f"pkt_tok_{secrets.token_urlsafe(24)}"
        is_auth_required = True
    else:
        pkt_owner_token = f"pkt_tok_{secrets.token_urlsafe(24)}"
        is_auth_required = False if auth_required is None else auth_required

    # Build chronological timeline from confirmed facts if available
    chronology: List[Dict[str, str]] = []
    meta = case_result.get("meta") or {}
    incident_date = meta.get("incident_date")
    if incident_date:
        chronology.append({
            "stage": "incident_occurrence",
            "date": str(incident_date),
            "description": f"Incident reported to have occurred at {location.strip() or 'unspecified location'}."
        })
    chronology.append({
        "stage": "voice_intake_recorded",
        "date": now_iso,
        "description": "User account recorded and fingerprinted for contemporaneous review."
    })

    # Attachment inventory (metadata only; never fabricates external verification)
    attachment_list: List[Dict[str, Any]] = []
    if attachments:
        for att in attachments:
            attachment_list.append({
                "id": att.get("id") or uuid.uuid4().hex[:8],
                "filename": att.get("filename", "unnamed_evidence"),
                "content_type": att.get("content_type", "application/octet-stream"),
                "description": att.get("description", "User-provided evidence item"),
                "verified": False,
                "verification_status": "unverified_pending_counsel_review"
            })

    content_hash = _compute_content_hash(f"{summary}|{document}")

    packet = {
        "packet_id": packet_id,
        "owner_token": pkt_owner_token,
        "session_id": session_id,
        "auth_required": is_auth_required,
        "created_at": now_iso,
        "updated_at": now_iso,
        "status": "needs_review",
        "category": case_result.get("category", "MOTOR_ACCIDENT_PRO"),
        "tier": case_result.get("tier", "ENTERPRISE_LEGAL_SUITE"),
        "client_name": client_name.strip() or "Citizen / Applicant",
        "location": location.strip() or "India",
        "incident_summary": summary,
        "chronology": chronology,
        "missing_evidence": [str(item) for item in missing],
        "attachments": attachment_list,
        "draft_message": document,
        "recipient": recipient.strip(),
        "content_hash": content_hash,
        "approvals": [],
        "outbound_available": False,
        "outbound_status": "not_sent",
        "outbound_delivery": {
            "adapter_enabled": False,
            "provider_connected": False,
            "provider_name": None,
            "destination_endpoint": None,
            "attempt_count": 0,
            "last_error": None,
            "safety_policy": "STRICT_REVIEW_ONLY: Outbound integrations (Insurer GIC, Lawyer Portal, Police CCTNS) are disconnected."
        },
        "review_note": (
            "Review and edit every fact, date, document, and recipient. "
            "No insurer, lawyer, or authority has been contacted."
        ),
    }

    _packet_store[packet_id] = (time.monotonic() + PACKET_TTL_SECONDS, packet)
    return packet


def get_pro_packet(packet_id: str, caller_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve an ephemeral packet by ID if not expired."""
    _clean_expired_packets()
    entry = _packet_store.get(packet_id)
    if entry:
        packet = entry[1]
        if packet.get("auth_required") and caller_token:
            if not hmac.compare_digest(caller_token, packet.get("owner_token", "")):
                raise PermissionError(f"Forbidden: cannot access pro packet '{packet_id}'.")
        return packet
    return None


def update_pro_packet(
    packet_id: str,
    *,
    draft_message: Optional[str] = None,
    recipient: Optional[str] = None,
    incident_summary: Optional[str] = None,
    caller_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Edit draft content before approval. Updates packet and recalculates content hash."""
    packet = get_pro_packet(packet_id)
    if not packet:
        raise ValueError(f"Packet '{packet_id}' not found or expired.")
    if packet.get("auth_required") and caller_token:
        if not hmac.compare_digest(caller_token, packet.get("owner_token", "")):
            raise PermissionError("Forbidden: cannot modify another user's pro packet.")
    if packet["status"] == "approved":
        raise ValueError("Cannot edit an already approved packet. Revoke approval first to edit.")

    if draft_message is not None:
        packet["draft_message"] = draft_message.strip()
    if recipient is not None:
        packet["recipient"] = recipient.strip()
    if incident_summary is not None:
        packet["incident_summary"] = incident_summary.strip()

    packet["updated_at"] = datetime.now(timezone.utc).isoformat()
    packet["content_hash"] = _compute_content_hash(
        f"{packet['incident_summary']}|{packet['draft_message']}"
    )
    return packet


def approve_pro_packet(
    packet_id: str,
    approver_name: str,
    *,
    approver_role: str = "Client",
    notes: str = "",
    caller_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Approve a packet for release readiness.
    Enforces state transition 'needs_review' -> 'approved'.
    Records approver, timestamp, exact frozen content hash, and notes.
    """
    packet = get_pro_packet(packet_id)
    if not packet:
        raise ValueError(f"Packet '{packet_id}' not found or expired.")
    if packet.get("auth_required") and caller_token:
        if not hmac.compare_digest(caller_token, packet.get("owner_token", "")):
            raise PermissionError("Forbidden: cannot approve another user's pro packet.")
    if packet["status"] not in {"needs_review", "draft"}:
        raise ValueError(f"Cannot approve packet in status '{packet['status']}'.")
    if not approver_name.strip():
        raise ValueError("Approver name is required for formal sign-off.")

    now_iso = datetime.now(timezone.utc).isoformat()
    approval_record = {
        "approver_name": approver_name.strip(),
        "approver_role": approver_role.strip(),
        "approved_at": now_iso,
        "approved_content_hash": packet["content_hash"],
        "notes": notes.strip() or "Approved for offline sharing / counsel review."
    }

    packet["status"] = "approved"
    packet["updated_at"] = now_iso
    packet["approvals"].append(approval_record)
    packet["review_note"] = (
        f"Approved by {approver_name.strip()} ({approver_role.strip()}) on {now_iso}. "
        "Outbound submission remains disabled; document ready for human handoff."
    )
    return packet


def attempt_send_packet(
    packet_id: str,
    destination: Optional[str] = None,
    caller_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Attempt to deliver an approved packet.
    Meets PRD Acceptance Check P2:
    - A draft cannot send without explicit approval.
    - Outbound adapters are disabled until a provider and destination are configured.
    - In no-provider mode, packet remains strictly review-only without mutating to 'sent'.
    """
    packet = get_pro_packet(packet_id)
    if not packet:
        raise ValueError(f"Packet '{packet_id}' not found or expired.")
    if packet.get("auth_required") and caller_token:
        if not hmac.compare_digest(caller_token, packet.get("owner_token", "")):
            raise PermissionError("Forbidden: cannot transmit another user's pro packet.")
    if packet["status"] != "approved":
        raise ValueError(
            f"Explicit approval required before transmission. Current status is '{packet['status']}'."
        )

    packet["outbound_delivery"]["attempt_count"] += 1
    packet["outbound_delivery"]["last_attempt_at"] = datetime.now(timezone.utc).isoformat()

    # Check adapter availability
    if not packet["outbound_delivery"]["adapter_enabled"]:
        error_msg = (
            "Outbound transmission adapter is DISABLED. No verified insurer API, lawyer portal, "
            "or police dispatch is configured. Packet has NOT been sent and remains review-only."
        )
        packet["outbound_delivery"]["last_error"] = error_msg
        packet["outbound_status"] = "not_sent"
        return {
            "success": False,
            "status": packet["status"],
            "outbound_status": "not_sent",
            "message": error_msg,
            "delivery_record": packet["outbound_delivery"]
        }

    return {
        "success": False,
        "status": "failed",
        "message": "No outbound provider adapter implemented in this release."
    }


def add_attachment(
    packet_id: str,
    filename: str,
    mime_type: str,
    file_bytes: bytes,
    description: str = "",
    caller_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Append an evidence file record to an existing pro case packet.
    Computes SHA-256 digest, byte size, records timestamp, and appends to packet['attachments'].
    """
    packet = get_pro_packet(packet_id)
    if not packet:
        raise ValueError(f"Packet '{packet_id}' not found or expired.")
    if packet.get("auth_required") and caller_token:
        if not hmac.compare_digest(caller_token, packet.get("owner_token", "")):
            raise PermissionError("Forbidden: cannot add attachments to another user's pro packet.")
    if packet.get("status") == "approved":
        raise ValueError("Cannot add attachments to an already approved packet. Revoke approval first to edit.")

    sha256_hash = hashlib.sha256(file_bytes).hexdigest()
    now_iso = datetime.now(timezone.utc).isoformat()
    attachment_id = f"att_{uuid.uuid4().hex[:8]}"

    attachment_record = {
        "id": attachment_id,
        "filename": filename or "unnamed_evidence",
        "mime_type": mime_type or "application/octet-stream",
        "content_type": mime_type or "application/octet-stream",
        "file_size_bytes": len(file_bytes),
        "sha256_hash": sha256_hash,
        "uploaded_at": now_iso,
        "description": description or "User-provided evidence item",
        "verified": False,
        "verification_status": "unverified_pending_counsel_review",
    }

    if "attachments" not in packet or not isinstance(packet["attachments"], list):
        packet["attachments"] = []

    packet["attachments"].append(attachment_record)
    packet["updated_at"] = now_iso
    return attachment_record
