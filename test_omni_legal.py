from backend.services.legal_engine import NyayaVaniEngine

def test_omni():
    engine = NyayaVaniEngine()
    test_cases = [
        {
            "name": "Labor Wage Theft",
            "tier": "BHARAT_GRASSROOTS_AID",
            "text": "ठेकेदार ने हमसे 3 महीने दिन-रात काम करवाया, अब 45,000 रुपये मजदूरी रोक रखी है और मांगने पर गाली-गलौज कर रहा है।",
            "meta": {"client_name": "Suresh Yadav", "location": "Noida, UP"}
        },
        {
            "name": "Predatory Loan App Harassment",
            "tier": "BHARAT_GRASSROOTS_AID",
            "text": "एक मोबाइल लोन ऐप ने मेरे सारे फोन कॉन्टैक्ट्स हैक कर लिए और अब फोटो मॉर्फ करके रिश्तेदारों को भेजने की धमकी देकर पैसे मांग रहे हैं।",
            "meta": {"client_name": "Pooja Sharma", "location": "Jaipur, Rajasthan"}
        },
        {
            "name": "RERA Builder Possession Delay",
            "tier": "ENTERPRISE_LEGAL_SUITE",
            "text": "I purchased a premium apartment with promised possession in December 2023. The builder has delayed possession by 35 months without an Occupancy Certificate and refuses compensation.",
            "meta": {"client_name": "Aditya Singhania", "location": "Gurugram, Haryana"}
        },
        {
            "name": "MSME Unpaid Invoices Default",
            "tier": "ENTERPRISE_LEGAL_SUITE",
            "text": "Our registered MSME enterprise delivered 50 lakh rupees worth of industrial components against signed purchase orders. The client has withheld payment past 60 days without dispute.",
            "meta": {"client_name": "Precision Engineering Ltd.", "location": "Pune, Maharashtra"}
        }
    ]

    for tc in test_cases:
        print(f"\n[*] Testing: {tc['name']}")
        res = engine.process_case(tc["text"], suite_tier=tc["tier"], meta=tc["meta"])
        print(f"    Category: {res.get('category')}")
        print(f"    Title: {res.get('statutory_title')}")
        print(f"    SHA-256 Hash: {res['affidavit_evidence']['sha256'][:16]}...")
        assert "statutory_sections" in res
        assert res["needs_more_information"] or res["statutory_sections"]
        assert "formal_document" in res
        print("    ✓ Passed verification!")

    print("\n=== All Omni-Legal Scenarios Passed! ===")

if __name__ == "__main__":
    test_omni()
