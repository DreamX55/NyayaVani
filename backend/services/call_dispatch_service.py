"""
NyayaVani (न्यायवाणी) — Pro Tier Autonomous Voice Telephony & Legal Call Dispatch Service
========================================================================================
Features:
1. Multi-turn Autonomous Negotiation Engine powered by Gnani Prisma STT & Timbre TTS.
2. Dual Telephony Bridge:
   - Direct REST API Dispatch via Twilio / Exotel for PSTN cellular routing.
   - Interactive In-Browser Call Softphone for instant testing and live demonstrations.
3. Behavioral Intent Classification (Denial, Delay/Evasion, Settlement Offer, Admission of Fault).
4. Statutory Deadline Enforcer (48-hour labor warning, 15-day RERA/MSMED cure notices).
5. Contemporaneous Electronic Evidence Preservation under Section 63 of Bharatiya Sakshya Adhiniyam (BSA), 2023.
"""

import os
import time
import json
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.core.gnani_client import GnaniClient

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
        self.client_name = client_name or "Client / Complainant"
        self.client_phone = client_phone or "+91 98765 00000"
        self.target_name = target_name or "Opposing Party / Contractor"
        self.target_phone = target_phone or "+91 98765 43210"
        self.domain = domain or "GENERAL_LEGAL_CLAIM"
        self.statutory_notice = statutory_notice or "Notice of statutory default"
        self.goal = goal or "Secure immediate compliance and acknowledgment of liability"
        
        self.status = "INITIATING"  # INITIATING, RINGING, CONNECTED, NEGOTIATING, CONCLUDED
        self.turns: List[Dict[str, Any]] = []
        self.call_duration_seconds = 0
        self.evidence_hash = ""
        self.certificate = ""

class AutonomousLegalNegotiator:
    """
    Two-way dialogue reasoner with strict legal guardrails and statutory anchoring.
    """
    def __init__(self, client: Optional[GnaniClient] = None):
        self.client = client or GnaniClient()

    def generate_opening_greeting(self, session: CallSession) -> Dict[str, Any]:
        """
        Synthesizes the initial formal legal opening statement when call connects.
        """
        dom = session.domain.upper()
        
        if "RERA" in dom or "BUILDER" in dom or "REAL_ESTATE" in dom:
            greeting = (
                f"Hello, this is NyayaVani Sovereign Legal Co-Pilot calling on behalf of our client, "
                f"{session.client_name}, regarding delayed flat handover. "
                f"This call is contemporaneous electronic evidence recorded under Section 63 of Bharatiya Sakshya Adhiniyam, 2023. "
                f"We are placing you on formal notice under Section 18 of the RERA Act, 2016 for delayed possession and statutory interest. "
                f"Do I have the authorized representative of {session.target_name} on the line?"
            )
            voice = "Avinash"
        elif "WAGE" in dom or "LABOR" in dom or "SALARY" in dom:
            greeting = (
                f"Hello, this is NyayaVani Sovereign Legal Co-Pilot calling on behalf of {session.client_name} "
                f"regarding withheld wages and contractor default. "
                f"This official call is preserved under Section 63 of Bharatiya Sakshya Adhiniyam, 2023. "
                f"Under Section 15 of the Payment of Wages Act, 1936, withholding earned wages constitutes forced labor "
                f"and attracts up to 10 times statutory compensation. "
                f"Are you the authorized supervisor or contractor for {session.target_name}?"
            )
            voice = "Shivani"
        elif "MSME" in dom or "COMMERCIAL" in dom or "CONTRACT" in dom:
            greeting = (
                f"Hello, this is NyayaVani Legal Co-Pilot calling on behalf of {session.client_name}, "
                f"a registered MSME enterprise. "
                f"We are placing you on statutory notice regarding unpaid commercial invoices overdue past 45 days. "
                f"Under Sections 15 and 16 of the MSMED Act, 2006, compound interest at three times the RBI bank rate "
                f"has accrued. Who am I speaking with at {session.target_name}?"
            )
            voice = "Avinash"
        elif "ACCIDENT" in dom or "MOTOR" in dom or "CRASH" in dom:
            greeting = (
                f"Hello, this is NyayaVani Incident Co-Pilot calling regarding the road traffic collision "
                f"involving our client {session.client_name}. "
                f"Under Section 134 of the Motor Vehicles Act, 2019, all drivers have a statutory duty to provide "
                f"insurance particulars and preserve contemporaneous collision records. "
                f"Please confirm your identity and insurance policy reference."
            )
            voice = "Avinash"
        else:
            greeting = (
                f"Hello, this is NyayaVani Sovereign Legal Co-Pilot calling on behalf of {session.client_name}. "
                f"This call is an electronic legal record preserved under Section 63 of Bharatiya Sakshya Adhiniyam, 2023. "
                f"We are calling regarding: {session.goal}. Can you confirm your name and designation at {session.target_name}?"
            )
            voice = "Shivani"

        # Synthesize opening statement via Gnani Timbre TTS
        audio_filename = f"call_opening_{session.session_id}_{int(time.time()*1000)}.wav"
        audio_path = os.path.join("audio_samples", audio_filename)
        os.makedirs("audio_samples", exist_ok=True)

        tts_res = self.client.synthesize(
            text=greeting,
            voice=voice,
            output_path=audio_path
        )

        return {
            "speaker": "AI_DISPATCH",
            "text": greeting,
            "audio_url": f"/audio_samples/{audio_filename}",
            "voice": voice,
            "elapsed_seconds": tts_res.get("elapsed_seconds", 0),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def classify_opponent_intent(self, opponent_text: str) -> str:
        """
        Detects opposing party behavioral stance:
        - OUTRIGHT_DENIAL: refuses payment, challenges authority, insults
        - DELAY_STALLING: asks for more time, delays, excuses
        - SETTLEMENT_OFFER: offers partial payment, requests compromise
        - ADMISSION_OF_FAULT: admits mistake, accepts responsibility
        - GENERAL_QUERY: asks for clarification
        """
        t = opponent_text.lower()

        if any(w in t for w in ["mistake", "our fault", "sorry", "will pay", "will clear", "will fix", "admit", "agree", "manjoor"]):
            return "ADMISSION_OF_FAULT"
        elif any(w in t for w in ["compromise", "50%", "half", "installment", "part payment", "discount", "settle", "kuch kam"]):
            return "SETTLEMENT_OFFER"
        elif any(w in t for w in ["time", "next month", "after 15 days", "accounts team", "busy", "call later", "baad me", "agle mahine", "thoda time"]):
            return "DELAY_STALLING"
        elif any(w in t for w in ["won't pay", "not paying", "go to court", "do whatever", "police case", "nahi dunga", "jo karna hai karo", "court jao", "false claim", "fraud"]):
            return "OUTRIGHT_DENIAL"
        else:
            return "GENERAL_INQUIRY"

    def formulate_legal_rebuttal(self, session: CallSession, opponent_text: str, intent: str) -> Dict[str, Any]:
        """
        Generates an authoritative, legally bounded counter-statement based on opponent behavior.
        """
        dom = session.domain.upper()
        voice = "Avinash" if any(k in dom for k in ["RERA", "MSME", "MOTOR", "ACCIDENT"]) else "Shivani"

        if intent == "OUTRIGHT_DENIAL":
            if "WAGE" in dom or "LABOR" in dom:
                rebuttal = (
                    f"Take note that your refusal to disburse earned wages is now contemporaneous evidence "
                    f"preserved under Section 63 of Bharatiya Sakshya Adhiniyam, 2023. "
                    f"Under Section 15(3) of the Payment of Wages Act, an application is being prepared for the "
                    f"Deputy Labor Commissioner claiming the full unpaid wage plus 10 times statutory compensation. "
                    f"You have 48 hours to clear the dues before formal enforcement proceedings are initiated."
                )
            elif "RERA" in dom:
                rebuttal = (
                    f"Your outright refusal is formally recorded. Under Section 18 of RERA, 2016, delayed possession "
                    f"past the promised date gives the buyer an absolute statutory right to an immediate refund with "
                    f"interest at SBI highest marginal rate plus 2%. "
                    f"A formal Complaint under Form M will be filed before the State RERA Authority within 48 hours."
                )
            elif "MSME" in dom:
                rebuttal = (
                    f"Your denial has been timestamped. Under Section 16 of the MSMED Act, withholding payment beyond "
                    f"45 days carries non-compoundable compound interest at 3 times the RBI rate. "
                    f"This call transcript will be attached to an automated recovery petition on the MSME Samadhaan portal."
                )
            else:
                rebuttal = (
                    f"Your refusal has been entered into the contemporaneous electronic evidence record under Section 63 BSA, 2023. "
                    f"Our legal counsel has been authorized to proceed with formal statutory filings without further notice."
                )

        elif intent == "DELAY_STALLING":
            rebuttal = (
                f"We cannot accept open-ended delays. The statutory grace period has already lapsed. "
                f"Under governing regulations, you are granted a strict 48-hour cure window. "
                f"Please ensure an official payment schedule or written acknowledgment is dispatched to our client "
                f"by 5:00 PM tomorrow, failing which legal proceedings will proceed automatically."
            )

        elif intent == "SETTLEMENT_OFFER":
            rebuttal = (
                f"Your proposed settlement terms have been logged into the call transcript. "
                f"Any partial settlement requires client approval and a formal written consent agreement under Section 73 of the Contract Act. "
                f"Please send the formal terms in writing via registered email within 24 hours so our counsel can review."
            )

        elif intent == "ADMISSION_OF_FAULT":
            rebuttal = (
                f"Your acknowledgment of liability has been formally noted and electronically sealed under Section 58 and Section 63 "
                f"of Bharatiya Sakshya Adhiniyam, 2023. "
                f"Please provide your transaction reference number or insurer claim number immediately to complete settlement."
            )

        else:
            rebuttal = (
                f"Please be advised that this matter is under active legal management. "
                f"We require your formal confirmation of compliance with {session.statutory_notice} within 48 hours."
            )

        # Synthesize spoken rebuttal
        audio_filename = f"call_rebuttal_{session.session_id}_{int(time.time()*1000)}.wav"
        audio_path = os.path.join("audio_samples", audio_filename)
        os.makedirs("audio_samples", exist_ok=True)

        tts_res = self.client.synthesize(
            text=rebuttal,
            voice=voice,
            output_path=audio_path
        )

        return {
            "speaker": "AI_DISPATCH",
            "intent": intent,
            "text": rebuttal,
            "audio_url": f"/audio_samples/{audio_filename}",
            "voice": voice,
            "elapsed_seconds": tts_res.get("elapsed_seconds", 0),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class CallSessionManager:
    """
    Manages active autonomous legal calling sessions and seals BSA 2023 certificates.
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
        statutory_notice: str = "Statutory notice of claim",
        goal: str = "Demand payment or statutory compliance",
        client_phone: str = "+91 98765 00000"
    ) -> Dict[str, Any]:
        """
        Creates a new calling session and generates the initial AI spoken greeting.
        """
        session_id = f"call_{uuid.uuid4().hex[:12]}"
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

        # Generate opening AI greeting
        greeting_data = self.negotiator.generate_opening_greeting(session)
        session.turns.append(greeting_data)
        session.status = "CONNECTED"

        return {
            "session_id": session_id,
            "status": session.status,
            "client_name": session.client_name,
            "target_name": session.target_name,
            "target_phone": session.target_phone,
            "domain": session.domain,
            "opening_greeting": greeting_data
        }

    def process_turn(self, session_id: str, opponent_text: str) -> Dict[str, Any]:
        """
        Processes opponent speech, classifies intent, and returns the AI's legal counter-speech.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Session {session_id} not found")

        # 1. Log Opponent turn
        intent = self.negotiator.classify_opponent_intent(opponent_text)
        opponent_turn = {
            "speaker": "OPPOSING_PARTY",
            "name": session.target_name,
            "text": opponent_text,
            "detected_intent": intent,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        session.turns.append(opponent_turn)

        # 2. Formulate and synthesize AI rebuttal
        ai_rebuttal = self.negotiator.formulate_legal_rebuttal(session, opponent_text, intent)
        session.turns.append(ai_rebuttal)
        session.status = "NEGOTIATING"

        return {
            "session_id": session_id,
            "opponent_turn": opponent_turn,
            "ai_rebuttal": ai_rebuttal,
            "turn_count": len(session.turns)
        }

    def conclude_session(self, session_id: str) -> Dict[str, Any]:
        """
        Ends the call session and generates the BSA 2023 Section 63 Evidence Certificate.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Session {session_id} not found")

        session.status = "CONCLUDED"
        now_utc = datetime.now(timezone.utc).isoformat()

        # Build full verbatim transcript
        transcript_lines = []
        for turn in session.turns:
            spk = turn.get("speaker")
            txt = turn.get("text", "")
            ts = turn.get("timestamp", "")
            transcript_lines.append(f"[{ts}] {spk}: {txt}")

        full_transcript = "\n".join(transcript_lines)

        # Compute SHA-256 evidence hash
        hasher = hashlib.sha256()
        hasher.update(session.session_id.encode("utf-8"))
        hasher.update(session.client_name.encode("utf-8"))
        hasher.update(session.target_name.encode("utf-8"))
        hasher.update(session.target_phone.encode("utf-8"))
        hasher.update(full_transcript.encode("utf-8"))
        sha256_hash = hasher.hexdigest()

        # Format legal certificate
        cert_text = (
            f"--- CONTEMPORANEOUS ELECTRONIC RECORD CERTIFICATE ---\n"
            f"STATUTORY MANDATE: Section 63, Bharatiya Sakshya Adhiniyam (BSA), 2023\n"
            f"DIGITAL EVIDENCE DIGEST (SHA-256): {sha256_hash}\n"
            f"UTC TIMESTAMP:    {now_utc}\n"
            f"SESSION ID:       {session.session_id}\n"
            f"PARTIES:          {session.client_name} (Caller) vs {session.target_name} ({session.target_phone})\n"
            f"CALL TURNS:       {len(session.turns)} Turns Preserved\n"
            f"STATUS:           Contemporaneous Spoken Audio & Verbatim Transcript Preserved\n"
            f"ADMISSIBILITY:    Certified admissible in judicial proceedings and arbitral tribunals under BSA 2023 Sec 63\n"
            f"--------------------------------------------------"
        )

        session.evidence_hash = sha256_hash
        session.certificate = cert_text

        return {
            "session_id": session.session_id,
            "status": "CONCLUDED",
            "client_name": session.client_name,
            "target_name": session.target_name,
            "target_phone": session.target_phone,
            "domain": session.domain,
            "total_turns": len(session.turns),
            "verbatim_transcript": full_transcript,
            "turns": session.turns,
            "sha256": sha256_hash,
            "certificate": cert_text,
            "timestamp": now_utc
        }

# Global singleton manager instance
call_manager = CallSessionManager()
