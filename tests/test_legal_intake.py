from backend.services.legal_engine import NyayaVaniEngine
from backend.services.source_register import STATUTORY_REGISTER


def test_vendor_draft_does_not_invent_notice_or_eviction():
    result = NyayaVaniEngine().process_case("Police came near my street cart.")
    assert result["category"] == "STREET_VENDOR"
    assert result["needs_more_information"] is True
    assert "did you receive" in " ".join(result["follow_up_questions"]).lower()
    draft = result["formal_document"].lower()
    assert "without serving" not in draft
    assert "forcibly remove" not in draft
    assert "police came near my street cart" in draft
    assert "15100" in " ".join(result["action_steps"])


def test_pro_accident_does_not_invent_policy_or_evidence():
    result = NyayaVaniEngine().process_case("My car was hit yesterday.")
    assert result["category"] == "MOTOR_ACCIDENT_PRO"
    draft = result["formal_document"]
    assert "POL-MOT-2026-8841" not in draft
    assert "KA-01-XX-0000" not in draft
    assert "dashcam footage" not in draft
    assert result["statutory_sections"] == []


def test_intake_can_advance_to_human_review_with_structured_facts():
    result = NyayaVaniEngine().process_case(
        "A municipal officer asked me to move my vending cart.",
        meta={
            "incident_date": "2026-11-09",
            "incident_location": "Guwahati, Assam",
            "other_party": "municipal officer",
            "specific_details": "No written notice was handed to me; certificate status unknown.",
        },
    )
    assert result["needs_more_information"] is False
    assert result["follow_up_questions"] == []
    assert result["intake"]["status"] == "ready_for_human_review"
    assert result["intake"]["review_required"] is True
    assert "No written notice was handed to me" in result["formal_document"]
    assert len(result["statutory_sections"]) >= 1
    assert len(result["remedies"]) >= 1
    assert len(result["authorities"]) >= 1


def test_unrelated_attack_is_not_assumed_religious():
    result = NyayaVaniEngine().process_case("Someone attacked me near my home.")
    assert result["category"] == "GENERAL_CITIZEN_AID"
    assert result["statutory_sections"] == []


def test_wage_reference_uses_current_code():
    result = NyayaVaniEngine().process_case("My employer has not paid my wages.")
    assert result["category"] == "WAGE_THEFT"
    assert "Code on Wages, 2019" in result["statutory_sections"][0]["law"]
    assert "Payment of Wages Act, 1936" not in str(result["statutory_sections"])


def test_statutory_resolution_for_all_supported_categories_when_facts_confirmed():
    """Verify that when structured facts are provided, all 10 supported categories
    resolve statutory_sections, remedies, and authorities directly from source_register.py,
    and meta is preserved on the returned response.
    """
    engine = NyayaVaniEngine()
    supported_categories = [
        "WAGE_THEFT",
        "STREET_VENDOR",
        "REAL_ESTATE_RERA",
        "COMMERCIAL_CONTRACT_MSME",
        "POLICE_CUSTODY",
        "LAND_GRABBING",
        "LOAN_FRAUD",
        "DOMESTIC_VIOLENCE",
        "CORRUPTION_RTI",
        "RELIGIOUS_GATHERING",
    ]

    for category in supported_categories:
        meta = {
            "category": category,
            "incident_date": "2026-11-09",
            "incident_location": "New Delhi",
            "other_party": "Opposite Entity",
            "specific_details": f"Confirmed structured test facts for {category}.",
        }
        result = engine.process_case(f"Test statement for {category}", meta=meta)

        assert result["category"] == category
        assert result["needs_more_information"] is False
        assert result["intake"]["status"] == "ready_for_human_review"
        assert result["meta"]["incident_location"] == "New Delhi"
        assert result["meta"]["other_party"] == "Opposite Entity"

        # Direct verification against source_register.py
        expected = STATUTORY_REGISTER[category]
        assert len(result["statutory_sections"]) == len(expected["references"])
        assert len(result["remedies"]) == len([r for r in expected["references"] if "remedy" in r])
        assert len(result["authorities"]) >= 1
        assert result["authorities"][0] == expected["jurisdiction"]

        for i, ref in enumerate(expected["references"]):
            assert result["statutory_sections"][i]["law"] == ref["law"]
            assert result["statutory_sections"][i]["source_url"] == ref["source_url"]
            assert result["statutory_sections"][i]["is_verified"] is False
            assert result["statutory_sections"][i]["review_status"] == "PENDING_QUALIFIED_LEGAL_REVIEW" 


def test_incomplete_intakes_maintain_safety_and_no_ungrounded_drafts():
    """Verify that incomplete intakes for non-potential categories do not invent statutes,
    remedies, or authorities, and follow-up questions are strictly preserved.
    """
    engine = NyayaVaniEngine()
    incomplete_cases = [
        ("The police locked me up and hit me.", "POLICE_CUSTODY"),
        ("Someone occupied my land without permission.", "LAND_GRABBING"),
        ("A loan app is blackmailing me with morphed photos.", "LOAN_FRAUD"),
        ("Husband beat me and threw me out.", "DOMESTIC_VIOLENCE"),
        ("Ration officer asked for bribe.", "CORRUPTION_RTI"),
        ("Mob disrupted our prayer meeting.", "RELIGIOUS_GATHERING"),
    ]

    for text, expected_category in incomplete_cases:
        result = engine.process_case(text)
        assert result["category"] == expected_category
        assert result["needs_more_information"] is True
        assert result["intake"]["status"] == "needs_details"
        assert len(result["follow_up_questions"]) > 0
        assert result["statutory_sections"] == []
        assert result["remedies"] == []
        assert result["authorities"] == []
        assert "DRAFT INCIDENT SUMMARY" in result["formal_document"]
