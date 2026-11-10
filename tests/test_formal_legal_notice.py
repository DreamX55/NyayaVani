# -*- coding: utf-8 -*-
"""Unit tests for the dedicated formal legal notice generator and server aliases."""

import pytest
from starlette.testclient import TestClient

from backend.server import app, get_session
from backend.services.legal_engine import NyayaVaniEngine, _build_formal_legal_notice


def test_formal_legal_notice_english_structure():
    facts = {
        "client_name": "Ramesh Kumar",
        "incident_date": "2026-11-05",
        "incident_location": "Bandra, Mumbai",
        "other_party": "Skyline Builders Pvt Ltd",
        "specific_details": "Delay of 18 months in flat handover; OC not received",
        "amount": "15,00,000 INR"
    }
    transcript = "I booked a flat with Skyline Builders and they are 18 months late without giving OC."
    doc = _build_formal_legal_notice(
        category="REAL_ESTATE_RERA",
        facts=facts,
        transcript=transcript,
        lang="en",
        needs_more_information=False
    )

    # Core Header & Meta
    assert "LEGAL NOTICE / FORMAL STATUTORY REPRESENTATION" in doc
    assert "Issued for Pre-Litigation Review & Record — Outbound Transmission Disabled" in doc
    assert "Date: 2026-11-05" in doc
    assert "Place: Bandra, Mumbai" in doc
    assert "TO:\nSkyline Builders Pvt Ltd" in doc
    assert "FROM:\nRamesh Kumar" in doc
    assert "SUBJECT: Formal Legal Notice regarding" in doc
    assert "Real Estate (Regulation and Development) Act, 2016" in doc

    # 5 Structured Sections
    assert "1. FACTUAL MATRIX & CHRONOLOGY:" in doc
    assert "1. CASE SYNOPSIS & FACTUAL SUMMARY (AI Synthesized Narrative):" in doc
    assert "Account in the person's own words:" in doc
    assert transcript in doc

    assert "2. STRUCTURED INCIDENT PARTICULARS:" in doc
    assert "Incident Date: 2026-11-05" in doc
    assert "Incident Location: Bandra, Mumbai" in doc
    assert "Opposing Party: Skyline Builders Pvt Ltd" in doc
    assert "Complainant: Ramesh Kumar" in doc
    assert "15,00,000 INR" in doc

    assert "3. STATUTORY CONTRAVENTIONS & APPLICABLE DHAARA:" in doc
    assert "Section 18" in doc

    assert "4. SPECIFIC DEMANDS & REQUISITE RELIEFS:" in doc
    assert "Preservation of Status Quo" in doc
    assert "Restitution & Settlement" in doc
    assert "15-Day Cure Notice" in doc

    assert "5. RESERVATION OF RIGHTS & LEGAL AID:" in doc
    assert "Legal Services Authorities Act, 1987" in doc
    assert "DLSA / NALSA" in doc
    assert "15100" in doc


def test_formal_legal_notice_hindi_format():
    facts = {
        "client_name": "सुरेश कुमार",
        "incident_date": "01-11-2026",
        "incident_location": "चांदनी चौक, दिल्ली",
        "other_party": "दुकान मालिक गुप्ता जी",
        "specific_details": "दुकान से जबरन सामान बाहर निकाला और किराया रसीद नहीं दी",
    }
    transcript = "दुकान मालिक ने मेरा सामान बाहर फेंक दिया।"
    doc = _build_formal_legal_notice(
        category="LAND_GRABBING",
        facts=facts,
        transcript=transcript,
        lang="hi",
        needs_more_information=False
    )

    assert "विधिक सूचना / औपचारिक वैधानिक अभ्यावेदन" in doc
    assert "LEGAL NOTICE / FORMAL STATUTORY REPRESENTATION" in doc
    assert "मुकदमा-पूर्व समीक्षा और अभिलेख हेतु जारी" in doc
    assert "दिनांक (Date): 01-11-2026" in doc
    assert "स्थान (Place): चांदनी चौक, दिल्ली" in doc
    assert "सेवा में / प्रति (TO):\nदुकान मालिक गुप्ता जी" in doc
    assert "प्रेषक (FROM):\nसुरेश कुमार" in doc
    assert "विषय (SUBJECT):" in doc
    assert "1. वस्तुस्थिती एवं घटनाक्रम (1. FACTUAL MATRIX & CHRONOLOGY):" in doc
    assert "2. संरचित घटना विवरण (2. STRUCTURED INCIDENT PARTICULARS):" in doc
    assert "3. वैधानिक उल्लंघन एवं लागू धाराएं (3. STATUTORY CONTRAVENTIONS & APPLICABLE DHAARA):" in doc
    assert "4. विशिष्ट मांगें एवं आवश्यक अनुतोष (4. SPECIFIC DEMANDS & REQUISITE RELIEFS):" in doc
    assert "5. अधिकारों का संरक्षण एवं विधिक सहायता (5. RESERVATION OF RIGHTS & LEGAL AID):" in doc
    assert "15100" in doc


def test_formal_legal_notice_marathi_format():
    facts = {
        "client_name": "अनिल पवार",
        "incident_date": "काल दुपारी",
        "incident_location": "स्वारगेट, पुणे",
        "other_party": "महापालिका अधिकारी",
        "specific_details": "हातगाडी जप्त केली आणि पावती दिली नाही",
    }
    transcript = "महापालिका अधिकाऱ्यांनी माझी हातगाडी जप्त केली."
    doc = _build_formal_legal_notice(
        category="STREET_VENDOR",
        facts=facts,
        transcript=transcript,
        lang="mr",
        needs_more_information=True,
        questions=["तुम्हाला ३० दिवसांची कोणतीही लेखी नोटीस मिळाली होती का?"]
    )

    assert "कायदेशीर नोटीस / वैधानिक निवेदन" in doc
    assert "LEGAL NOTICE / FORMAL STATUTORY REPRESENTATION" in doc
    assert "दावा-पूर्व पुनरावलोकन आणि अभिलेखासाठी जारी" in doc
    assert "दिनांक (Date): काल दुपारी" in doc
    assert "ठिकाण (Place): स्वारगेट, पुणे" in doc
    assert "प्रति (TO):\nमहापालिका अधिकारी" in doc
    assert "प्रेषक (FROM):\nअनिल पवार" in doc
    assert "विषय (SUBJECT):" in doc
    assert "1. वस्तुस्थिती आणि घटनाक्रम (1. FACTUAL MATRIX & CHRONOLOGY):" in doc
    assert "2. संरचित घटना तपशील (2. STRUCTURED INCIDENT PARTICULARS):" in doc
    assert "3. वैधानिक उल्लंघन आणि लागू कलमे (3. STATUTORY CONTRAVENTIONS & APPLICABLE DHAARA):" in doc
    assert "4. विशिष्ट मागण्या आणि आवश्यक दिलासा (4. SPECIFIC DEMANDS & REQUISITE RELIEFS):" in doc
    assert "5. हक्कांचे आरक्षण आणि कायदेशीर मदत (5. RESERVATION OF RIGHTS & LEGAL AID):" in doc
    assert "तुम्हाला ३० दिवसांची कोणतीही लेखी नोटीस मिळाली होती का?" in doc
    assert "15100" in doc


def test_api_chat_aliases_and_history():
    client = TestClient(app)
    payload = {
        "message": "My contractor withheld 50000 INR salary in Mumbai last week.",
        "session_id": "test_notice_aliases_sess_01"
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Aliases in API response
    assert "formal_document" in data
    assert "draft_document" in data
    assert "formal_notice" in data
    assert data["draft_document"] == data["formal_document"]
    assert data["formal_notice"] == data["formal_document"]
    assert len(data["formal_document"]) > 100
    assert "LEGAL NOTICE / FORMAL STATUTORY REPRESENTATION" in data["formal_document"]

    # Session storage verification
    session = get_session("test_notice_aliases_sess_01")
    assert session is not None
    assert session.get("formal_document") == data["formal_document"]
    assert session.get("draft_document") == data["formal_document"]
    assert session.get("formal_notice") == data["formal_document"]
    assert session["history"][-1]["formal_document"] == data["formal_document"]
    assert session["history"][-1]["formal_notice"] == data["formal_document"]
