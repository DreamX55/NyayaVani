import os
import sys
import pytest
from starlette.testclient import TestClient

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.server import app
from backend.services.legal_engine import NyayaVaniEngine
from backend.services.graph_retriever import LegalGraphRetriever
from backend.services.geo_service import GeoLanguageService
from backend.services.call_dispatch_service import (
    call_manager,
    OUTBOUND_TELEPHONY_ENABLED,
    dispatch_pstn_call
)

client = TestClient(app)

def test_knowledge_graph_candidate_retrieval_and_car_accident_routing():
    """Verify that Knowledge Graph routing handles car crashes correctly and does not misroute to street vendor eviction."""
    retriever = LegalGraphRetriever()
    q = "A speeding truck hit my car at the highway crossing and fled."
    res = retriever.query(q)
    verdict = res["legality_verdict"]
    
    assert verdict["status"] == "ROAD_TRAFFIC_NEGLIGENCE_AND_STATUTORY_CLAIM"
    assert verdict["is_lawful"] is False
    assert verdict["review_status"] == "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"
    assert "Street Vendors" not in verdict["verdict_summary"]
    assert "POTENTIALLY IMPROPER CONDUCT" in verdict["verdict_summary"]


def test_knowledge_graph_conditional_language_and_sources():
    """Verify that graph retrieval outputs conditional language and valid primary source URLs."""
    retriever = LegalGraphRetriever()
    q = "Police is breaking my thela in Lajpat Nagar and asking 500 rupees bribe."
    res = retriever.query(q)
    verdict = res["legality_verdict"]
    
    assert verdict["status"] == "UNLAWFUL_ACT_BY_AUTHORITY"
    assert verdict["is_lawful"] is False
    assert verdict["review_status"] == "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"
    assert "POTENTIALLY IMPROPER CONDUCT (SUBJECT TO VERIFICATION)" in verdict["verdict_summary"]
    assert len(verdict["legal_source_statutes"]) > 0
    for s in verdict["legal_source_statutes"]:
        assert "source_url" in s
        assert s["source_url"].startswith("http")


def test_geo_service_jurisdiction_profiles():
    """Verify audited geographical resolution: no silent aliasing of Pune to Mumbai, Noida to Delhi, or unknown to Delhi."""
    # Pune
    pune = GeoLanguageService.resolve_city_profile("Pune, Maharashtra")
    assert "Pune Municipal Corporation (PMC)" in pune["municipal_body"]
    assert "Pune DLSA" in pune["legal_aid_authority"]
    assert pune["primary_language"] == "mr-IN"

    # Noida
    noida = GeoLanguageService.resolve_city_profile("Noida sector 62")
    assert "NOIDA" in noida["municipal_body"]
    assert "Gautam Buddha Nagar DLSA" in noida["legal_aid_authority"]
    assert "Delhi" not in noida["city_display"]

    # Gurugram
    gurugram = GeoLanguageService.resolve_city_profile("Gurgaon DLF")
    assert "Municipal Corporation of Gurugram (MCG)" in gurugram["municipal_body"]
    assert "Gurugram DLSA" in gurugram["legal_aid_authority"]

    # Unknown City -> National Default (NEVER Delhi)
    unknown = GeoLanguageService.resolve_city_profile("SomeUnknownVillage123")
    assert "Pending Confirmation" in unknown["city_display"]
    assert "NALSA" in unknown["legal_aid_authority"]
    assert "Delhi" not in unknown["city_display"]


def test_geo_service_adaptive_script_detection():
    """Verify adaptive language detection for turns 2+ across Indic scripts."""
    # Tamil script
    lang, voice = GeoLanguageService.adapt_language_from_text("வணக்கம், எனக்கு உதவி வேண்டும்", "en-IN")
    assert lang == "ta-IN"
    assert voice == "Kalpana"

    # Kannada script
    lang, voice = GeoLanguageService.adapt_language_from_text("ನನಗೆ ಸಂಬಳ ಕೊಟ್ಟಿಲ್ಲ", "en-IN")
    assert lang == "kn-IN"
    assert voice == "Chetana"

    # Marathi text
    lang, voice = GeoLanguageService.adapt_language_from_text("मला माझा पगार दिला नाही", "hi-IN")
    assert lang == "mr-IN"
    assert voice == "Vasudha"


def test_outbound_telephony_disabled_guardrail():
    """Verify that actual outbound cellular/PSTN calling is strictly disabled."""
    assert OUTBOUND_TELEPHONY_ENABLED is False

    with pytest.raises(RuntimeError) as exc_info:
        dispatch_pstn_call("+919876543210")
    assert "Outbound cellular dispatch is disabled" in str(exc_info.value)


def test_pro_call_simulation_dialogue_lifecycle():
    """Verify the in-memory roleplay negotiation simulation lifecycle."""
    session_data = call_manager.create_session(
        client_name="Ramesh Kumar",
        target_name="Sunrise Developers Pvt Ltd",
        target_phone="+91 98000 00000",
        domain="REAL_ESTATE_RERA",
        statutory_notice="Section 18 RERA Refund Notice",
        goal="Demand refund of flat booking amount"
    )

    sid = session_data["session_id"]
    assert session_data["simulation_mode"] is True
    assert session_data["outbound_telephony_enabled"] is False
    assert len(session_data["opening_greeting"]["text"]) > 0

    # Turn 1: Opponent delays
    turn1 = call_manager.process_turn(sid, "We are facing a slight delay, give us 6 months more.")
    assert turn1["opponent_turn"]["detected_intent"] == "DELAY_STALLING"
    assert "AI_SIMULATOR" in turn1["ai_rebuttal"]["speaker"]

    # Turn 2: Opponent offers partial settlement
    turn2 = call_manager.process_turn(sid, "Can we offer a 50% refund right now?")
    assert turn2["opponent_turn"]["detected_intent"] == "SETTLEMENT_OFFER"

    # Conclude
    conclusion = call_manager.conclude_session(sid)
    assert conclusion["status"] == "SIMULATION_CONCLUDED"
    assert len(conclusion["sha256"]) == 64
    assert "FOR REVIEW ONLY" in conclusion["certificate"]
    assert conclusion["outbound_telephony_enabled"] is False


def test_server_endpoints_geo_and_pro_call():
    """Verify REST API endpoints for /api/geo/resolve and /api/pro/call/*."""
    # Geo resolve
    r_geo = client.get("/api/geo/resolve?q=pune")
    assert r_geo.status_code == 200
    p_data = r_geo.json()
    assert p_data["profile"]["primary_language"] == "mr-IN"
    assert "PMC" in p_data["profile"]["municipal_body"]

    # Pro call dispatch
    r_disp = client.post("/api/pro/call/dispatch", json={
        "client_name": "Suresh Worker",
        "target_name": "ABC Constructions",
        "domain": "WAGE_THEFT",
        "goal": "Unpaid wage recovery"
    })
    assert r_disp.status_code == 200
    d_data = r_disp.json()
    assert d_data["mode"] == "IN_MEMORY_SIMULATION_ONLY"
    assert d_data["outbound_telephony_enabled"] is False
    sid = d_data["session"]["session_id"]

    # Pro call dialogue
    r_dial = client.post("/api/pro/call/dialogue", json={
        "session_id": sid,
        "text": "The company has no money to pay wages right now."
    })
    assert r_dial.status_code == 200
    dial_data = r_dial.json()
    assert dial_data["turn"]["opponent_turn"]["detected_intent"] == "OUTRIGHT_DENIAL"

    # Pro call conclude
    r_conc = client.post("/api/pro/call/conclude", json={"session_id": sid})
    assert r_conc.status_code == 200
    conc_data = r_conc.json()
    assert conc_data["conclusion"]["status"] == "SIMULATION_CONCLUDED"


def test_engine_merged_provisions_and_rights_card():
    """Verify that NyayaVaniEngine.process_case attaches candidate graph provisions, geo profile, and rights explanation."""
    engine = NyayaVaniEngine()
    transcript = "ठेकेदार ने हमसे 3 महीने दिन-रात काम करवाया, अब 45,000 रुपये मजदूरी रोक रखी है।"
    res = engine.process_case(transcript, suite_tier="BHARAT_GRASSROOTS_AID", meta={"location": "Pune"})

    assert "legality_verdict" in res
    assert "graph_subgraph" in res
    assert "geo_profile" in res
    assert "PMC" in res["geo_profile"]["municipal_body"]
    assert "understand_your_rights" in res
    assert res["understand_your_rights"]["status"] == "ready"
    assert res["understand_your_rights"]["what_i_understood"]["text"]
    assert res["understand_your_rights"]["what_may_be_wrong"]["improper_conduct_description"]

    # Verify all provisions maintain review_status
    for s in res.get("statutory_sections", []):
        assert s.get("review_status") == "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW" or s.get("review_status") == "PENDING_QUALIFIED_LEGAL_REVIEW"


def test_two_phase_conversational_intake_and_modality_symmetry():
    """Verify Socratic intake (Phase 1) vs complete legal package (Phase 2) and frontend modality symmetry."""
    engine = NyayaVaniEngine()
    
    # Phase 1: Incomplete statement (missing date, party, etc.)
    res_turn1 = engine.process_case(
        "A speeding car hit my motorcycle and the driver drove away.",
        suite_tier="ENTERPRISE_LEGAL_SUITE",
        meta={"location": "Pune", "client_name": "Rohan"}
    )
    assert res_turn1["needs_more_information"] is True
    assert len(res_turn1["follow_up_questions"]) > 0
    # First turn has crisp natural acknowledgement
    assert "Understood." in res_turn1["spoken_text"]
    
    # Subsequent turn with followup flag: no formalities, direct question
    res_followup = engine.process_case(
        "A speeding car hit my motorcycle and the driver drove away.",
        suite_tier="ENTERPRISE_LEGAL_SUITE",
        meta={"location": "Pune", "client_name": "Rohan", "is_followup_turn": True}
    )
    assert res_followup["needs_more_information"] is True
    # Formalities like "Understood." should NOT be repeated on followup turns
    assert not res_followup["spoken_text"].startswith("Understood.")

    # Phase 2: Complete facts gathered across turns
    complete_facts = {
        "client_name": "Rohan",
        "incident_location": "Pune highway junction",
        "incident_date": "yesterday at 5pm",
        "other_party": "White Swift car MH-12-AB-1234",
        "specific_details": "Suffered fracture on left arm, other vehicle fled",
        "location": "Pune"
    }
    res_complete = engine.process_case(
        "A speeding white Swift MH-12-AB-1234 hit my motorcycle at Pune highway junction yesterday at 5pm and fled. I suffered a fracture.",
        suite_tier="ENTERPRISE_LEGAL_SUITE",
        meta=complete_facts
    )
    assert res_complete["needs_more_information"] is False
    assert len(res_complete["statutory_sections"]) > 0
    assert res_complete["formal_document"]
    assert "1. CASE SYNOPSIS & FACTUAL SUMMARY (AI Synthesized Narrative):" in res_complete["formal_document"]
    assert "Account in the person's own words:" in res_complete["formal_document"]

    # Verify frontend HTML implements Two-Phase gating and modality symmetry
    with open(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"), "r", encoding="utf-8") as f:
        html = f.read()

    assert "lastInputModality" in html
    assert "submitReviewedTranscript" in html
    assert "submitQuickReply" in html
    assert "Phase 1: Conversational Fact Intake" in html
    assert "Phase 2: Complete Legal Package" in html

