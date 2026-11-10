"""NyayaVani (न्यायवाणी) — In-Memory Negotiation Roleplay & Incident Preparation Sandbox.
====================================================================================
PROTOTYPE ONLY:
This service models an in-memory two-way negotiation dialogue for citizen incident preparation.
It is an interactive simulation sandbox to help citizens and advocates rehearse conversations.

SAFETY BOUNDARY:
- Actual outbound telephony (cellular / PSTN) is STRICTLY DISABLED.
- Does NOT initiate real phone calls to opponents, employers, insurers, police, or courts.
- All transcripts and digests are simulation records for review, NOT court-certified evidence.
"""

import os
import time
import json
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.core.gnani_client import GnaniClient

# Strict Safety Boundary: Outbound telephony is disabled
OUTBOUND_TELEPHONY_ENABLED = False


def dispatch_pstn_call(*args, **kwargs):
    """Safety boundary: strictly blocks any external PSTN or cellular transmission."""
    raise RuntimeError("Outbound cellular dispatch is disabled. NyayaVani does not initiate real phone calls.")


class CallSession:
    def __init__(
        self,
        session_id: str,
        client_name: str,
        client_phone: str,
        target_name: str,
        target_phone: str,
        domain: str,
        statutory_notice: str,
        goal: str
    ):
        self.session_id = session_id
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.client_name = client_name or "Client / Citizen"
        self.client_phone = client_phone or "Unspecified"
        self.target_name = target_name or "Other Party / Enterprise"
        self.target_phone = target_phone or "Unspecified"
        self.domain = domain or "GENERAL_LEGAL_CLAIM"
        self.statutory_notice = statutory_notice or "Draft Notice of Claim"
        self.goal = goal or "Explore settlement options and clarify position"
        
        self.status = "SIMULATION_CONNECTED"
        self.mode = "IN_MEMORY_SIMULATION_ONLY"
        self.turns: List[Dict[str, Any]] = []
        self.call_duration_seconds = 0
        self.evidence_hash = ""
        self.certificate = ""


class AutonomousLegalNegotiator:
    """
    Two-way in-memory dialogue simulator with statutory anchoring.
    Assists in preparing negotiation points without presenting as completed calls or legal counsel.
    """
    def __init__(self, client: Optional[GnaniClient] = None):
        self.client = client or GnaniClient()

    def generate_opening_greeting(self, session: CallSession) -> Dict[str, Any]:
        """
        Synthesizes the initial simulated opening statement for roleplay preparation.
        """
        dom = session.domain.upper()
        
        if "RERA" in dom or "BUILDER" in dom or "REAL_ESTATE" in dom:
            greeting = (
                f"Hello. This is a simulated legal notice scenario regarding delayed possession for {session.client_name}. "
                f"Under Section 18 of the RERA Act, 2016, delayed handover entitles the allottee to interest or refund. "
                f"Are you the authorized representative for {session.target_name}?"
            )
            voice = "Avinash"
        elif "WAGE" in dom or "LABOR" in dom or "SALARY" in dom:
            greeting = (
                f"Hello. This is a simulated wage inquiry scenario regarding unpaid compensation for {session.client_name}. "
                f"Under Section 15 of the Payment of Wages Act and Code on Wages, withholding earned wages is improper. "
                f"Can you clarify the status of the pending wage disbursement?"
            )
            voice = "Shivani"
        elif "MSME" in dom or "COMMERCIAL" in dom or "CONTRACT" in dom:
            greeting = (
                f"Hello. This is a simulated commercial follow-up scenario on behalf of {session.client_name}, an MSME enterprise. "
                f"Under Sections 15 and 16 of the MSMED Act, 2006, commercial invoices overdue past 45 days accrue interest. "
                f"Who is the finance officer handling payments at {session.target_name}?"
            )
            voice = "Avinash"
        elif "ACCIDENT" in dom or "MOTOR" in dom or "CRASH" in dom:
            greeting = (
                f"Hello. This is a simulated inquiry scenario regarding the motor vehicular collision involving {session.client_name}. "
                f"Under Section 134 of the Motor Vehicles Act, 1988, drivers must share insurance details for third-party claims. "
                f"Please confirm the insurance policy reference for verification."
            )
            voice = "Avinash"
        else:
            greeting = (
                f"Hello. This is an incident inquiry simulation regarding: {session.goal}. "
                f"Can you state your position regarding {session.client_name}'s statement?"
            )
            voice = "Shivani"

        # Generate audio using ephemeral runtime_tmp
        os.makedirs("runtime_tmp", exist_ok=True)
        audio_filename = f"sim_opening_{session.session_id}_{int(time.time()*1000)}.wav"
        audio_path = os.path.join("runtime_tmp", audio_filename)

        try:
            tts_res = self.client.synthesize(
                text=greeting,
                voice=voice,
                output_path=audio_path
            )
            elapsed = tts_res.get("elapsed_seconds", 0)
        except Exception:
            elapsed = 0

        return {
            "speaker": "AI_SIMULATOR",
            "text": greeting,
            "audio_url": f"/runtime_tmp/{audio_filename}" if os.path.exists(audio_path) else None,
            "voice": voice,
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "simulation_mode": True
        }

    def classify_opponent_intent(self, opponent_text: str) -> str:
        """
        Detects opposing party behavioral stance for training:
        - OUTRIGHT_DENIAL: refuses payment, challenges claims
        - DELAY_STALLING: asks for time, gives excuses
        - SETTLEMENT_OFFER: offers partial payment, requests compromise
        - ADMISSION_OF_FAULT: admits mistake, accepts responsibility
        - GENERAL_QUERY: asks for clarification
        """
        t = (opponent_text or "").lower()

        if any(w in t for w in ["mistake", "our fault", "sorry", "will pay", "will clear", "will fix", "admit", "agree", "manjoor"]):
            return "ADMISSION_OF_FAULT"
        elif any(w in t for w in ["compromise", "50%", "half", "installment", "part payment", "discount", "settle", "kuch kam"]):
            return "SETTLEMENT_OFFER"
        elif any(w in t for w in ["time", "delay", "next month", "after 15 days", "accounts team", "busy", "call later", "baad me", "agle mahine", "thoda time", "more time", "months more", "wait"]):
            return "DELAY_STALLING"
        elif any(w in t for w in ["won't pay", "not paying", "no money", "cannot pay", "can't pay", "refuse", "refuses", "go to court", "do whatever", "police case", "nahi dunga", "jo karna hai karo", "court jao", "false claim", "fraud", "paisa nahi"]):
            return "OUTRIGHT_DENIAL"
        else:
            return "GENERAL_INQUIRY"

    def formulate_legal_rebuttal(self, session: CallSession, opponent_text: str, intent: str) -> Dict[str, Any]:
        """
        Generates an authoritative, legally bounded counter-statement for rehearsal.
        """
        dom = session.domain.upper()
        voice = "Avinash" if any(k in dom for k in ["RERA", "MSME", "MOTOR", "ACCIDENT"]) else "Shivani"

        if intent == "OUTRIGHT_DENIAL":
            if "WAGE" in dom or "LABOR" in dom:
                rebuttal = (
                    f"Your position has been noted in this simulation record. Under Section 15 of the Payment of Wages Act, "
                    f"an application may be submitted to the Labor Commissioner claiming unpaid wages. "
                    f"We advise checking official payment records before formal legal steps."
                )
            elif "RERA" in dom:
                rebuttal = (
                    f"Noted. Under Section 18 of RERA, 2016, allottees may file Form M before the RERA Authority if possession is delayed. "
                    f"We advise reviewing the registered agreement for sale terms."
                )
            elif "MSME" in dom:
                rebuttal = (
                    f"Noted. Under Section 16 of the MSMED Act, delayed payments accrue statutory interest. "
                    f"This account will be reviewed for potential filing on the MSME Samadhaan portal."
                )
            else:
                rebuttal = (
                    f"Your response has been noted. If an amicable settlement is not reached, formal legal options "
                    f"will be explored through the competent legal authority."
                )
        elif intent == "DELAY_STALLING":
            rebuttal = (
                f"We note your request for additional time. Please specify an exact date by which the matter will be reviewed, "
                f"so the applicant can decide whether to escalate through official channels."
            )
        elif intent == "SETTLEMENT_OFFER":
            rebuttal = (
                f"Thank you for proposing terms. Any mutual compromise must be confirmed in writing. "
                f"Please share a written draft of the proposed terms for review."
            )
        elif intent == "ADMISSION_OF_FAULT":
            rebuttal = (
                f"Your willingness to resolve this matter is noted. Please provide the transaction or settlement reference "
                f"so the records can be updated accordingly."
            )
        else:
            rebuttal = (
                f"Please be advised that this matter is under active review. "
                f"We recommend clarifying your position in writing regarding {session.statutory_notice}."
            )

        # Synthesize spoken rebuttal into runtime_tmp
        os.makedirs("runtime_tmp", exist_ok=True)
        audio_filename = f"sim_rebuttal_{session.session_id}_{int(time.time()*1000)}.wav"
        audio_path = os.path.join("runtime_tmp", audio_filename)

        try:
            tts_res = self.client.synthesize(
                text=rebuttal,
                voice=voice,
                output_path=audio_path
            )
            elapsed = tts_res.get("elapsed_seconds", 0)
        except Exception:
            elapsed = 0

        return {
            "speaker": "AI_SIMULATOR",
            "intent": intent,
            "text": rebuttal,
            "audio_url": f"/runtime_tmp/{audio_filename}" if os.path.exists(audio_path) else None,
            "voice": voice,
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "simulation_mode": True
        }


class CallSessionManager:
    """
    Manages in-memory dialogue simulation sessions for incident preparation.
    """
    def __init__(self):
        self.sessions: Dict[str, CallSession] = {}
        self.negotiator = AutonomousLegalNegotiator()

    def create_session(
        self,
        client_name: str,
        target_name: str,
        target_phone: str,
        domain: str = "GENERAL_LEGAL_CLAIM",
        statutory_notice: str = "Draft notice of claim",
        goal: str = "Explore dispute resolution options",
        client_phone: str = "+91 98765 00000"
    ) -> Dict[str, Any]:
        """
        Creates a new in-memory simulation session and generates initial dialogue.
        """
        session_id = f"sim_{uuid.uuid4().hex[:12]}"
        session = CallSession(
            session_id=session_id,
            client_name=client_name,
            client_phone=client_phone,
            target_name=target_name,
            target_phone=target_phone,
            domain=domain,
            statutory_notice=statutory_notice,
            goal=goal
        )
        self.sessions[session_id] = session

        greeting_data = self.negotiator.generate_opening_greeting(session)
        session.turns.append(greeting_data)
        session.status = "SIMULATION_ACTIVE"

        return {
            "session_id": session_id,
            "status": session.status,
            "simulation_mode": True,
            "outbound_telephony_enabled": False,
            "client_name": session.client_name,
            "target_name": session.target_name,
            "target_phone": session.target_phone,
            "domain": session.domain,
            "opening_greeting": greeting_data
        }

    def process_turn(self, session_id: str, opponent_text: str) -> Dict[str, Any]:
        """
        Processes simulated opponent statement and returns AI's counter-rebuttal.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Session {session_id} not found")

        intent = self.negotiator.classify_opponent_intent(opponent_text)
        opponent_turn = {
            "speaker": "SIMULATED_RESPONDENT",
            "name": session.target_name,
            "text": opponent_text,
            "detected_intent": intent,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        session.turns.append(opponent_turn)

        ai_rebuttal = self.negotiator.formulate_legal_rebuttal(session, opponent_text, intent)
        session.turns.append(ai_rebuttal)
        session.status = "SIMULATION_NEGOTIATING"

        return {
            "session_id": session_id,
            "opponent_turn": opponent_turn,
            "ai_rebuttal": ai_rebuttal,
            "turn_count": len(session.turns)
        }

    def conclude_session(self, session_id: str) -> Dict[str, Any]:
        """
        Concludes the negotiation rehearsal and generates an incident preparation summary.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Session {session_id} not found")

        session.status = "SIMULATION_CONCLUDED"
        now_utc = datetime.now(timezone.utc).isoformat()

        transcript_lines = []
        for turn in session.turns:
            spk = turn.get("speaker")
            txt = turn.get("text", "")
            ts = turn.get("timestamp", "")
            transcript_lines.append(f"[{ts}] {spk}: {txt}")

        full_transcript = "\n".join(transcript_lines)

        hasher = hashlib.sha256()
        hasher.update(session.session_id.encode("utf-8"))
        hasher.update(session.client_name.encode("utf-8"))
        hasher.update(session.target_name.encode("utf-8"))
        hasher.update(full_transcript.encode("utf-8"))
        sha256_hash = hasher.hexdigest()

        cert_text = (
            f"--- SIMULATED DIALOGUE TRANSCRIPT — FOR REVIEW ONLY ---\n"
            f"NOTICE: In-memory simulation transcript for incident preparation. NOT A COURT-CERTIFIED RECORD.\n"
            f"SESSION ID: {session.session_id}\n"
            f"PARTIES INVOLVED: {session.client_name} vs {session.target_name}\n"
            f"DIGITAL RECORD DIGEST (SHA-256): {sha256_hash}\n"
            f"UTC TIMESTAMP: {now_utc}\n"
            f"OUTBOUND TRANSMISSION: DISABLED (In-memory roleplay simulation only)\n"
            f"-------------------------------------------------------"
        )

        session.evidence_hash = sha256_hash
        session.certificate = cert_text

        return {
            "session_id": session.session_id,
            "status": session.status,
            "full_transcript": full_transcript,
            "sha256": sha256_hash,
            "certificate": cert_text,
            "turns_count": len(session.turns),
            "outbound_telephony_enabled": False
        }


call_manager = CallSessionManager()
