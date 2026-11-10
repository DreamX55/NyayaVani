import pytest
from backend.services.legal_engine import NyayaVaniEngine

@pytest.fixture
def engine():
    return NyayaVaniEngine()

def test_gujarati_street_vendor_questions_not_english(engine):
    transcript = "હું શાકભાજીની લારી ચલાવું છું અને ગઈકાલે મહાનગરપાલિકાના અધિકારીઓએ નોટિસ આપ્યા વિના મારી લારી જપ્ત કરી લીધી."
    res = engine.process_case(transcript, meta={"language": "gu", "language_code": "gu-IN"})
    
    assert res.get("language") == "gu"
    assert res.get("needs_more_information") is True
    
    questions = res.get("follow_up_questions", [])
    assert len(questions) > 0
    # None of the follow-up questions should be in English
    for q in questions:
        assert not q.startswith("What work was done")
        assert not q.startswith("Are you vending at this site")
        assert not q.startswith("Who was your immediate employer")
        assert not q.startswith("On what date")
        # Should contain Gujarati characters
        assert any("\u0A80" <= ch <= "\u0AFF" for ch in q)

    spoken = res.get("spoken_text", "")
    assert any("\u0A80" <= ch <= "\u0AFF" for ch in spoken)
    assert not spoken.startswith("Understood.")

def test_gujarati_formal_legal_notice_format(engine):
    transcript = "હું શાકભાજીની લારી ચલાવું છું અને ગઈકાલે મહાનગરપાલિકાના અધિકારીઓએ નોટિસ આપ્યા વિના મારી લારી જપ્ત કરી લીધી."
    res = engine.process_case(transcript, meta={"language": "gu", "language_code": "gu-IN"})
    
    doc = res.get("formal_document", "")
    assert "કાનૂની નોટિસ / વૈધાનિક રજૂઆત" in doc
    assert "LEGAL NOTICE / FORMAL STATUTORY REPRESENTATION" in doc
    assert "૧. ઘટના વિગતો અને તથ્યો" in doc
    assert "૪. માગણીઓ અને રાહત" in doc
    assert "૧૫ દિવસની વૈધાનિક નોટિસ" in doc

@pytest.mark.parametrize("lang,sample_text", [
    ("ta", "நான் ஒரு காய்கறி கடை வைத்துள்ளேன், அதிகாரிகள் எனது கடையை நோட்டீஸ் இன்றி பறிமுதல் செய்தனர்."),
    ("te", "నేను కూరగాયల బండి నడుపుతున్నాను, అధికారులు నోటీసు ఇవ్వకుండా నా బండిని స్వాధీనం చేసుకున్నారు."),
    ("kn", "ನಾನು ತರಕಾರಿ ಅಂಗಡಿ ನಡೆಸುತ್ತಿದ್ದೇನೆ, ಅಧಿಕಾರಿಗಳು ನೋಟಿಸ್ ನೀಡದೆ ನನ್ನ ಅಂಗಡಿಯನ್ನು ವશಪಡಿಸಿಕೊಂಡರು."),
    ("bn", "আমি একটি সবজির দোকান চালাই, আধিকারিকরা কোনো নোটিশ ছাড়াই আমার দোকান বাজেয়াপ্ত করেছে।"),
    ("pa", "ਮੈਂ ਇੱਕ ਸਬਜ਼ੀ ਦੀ ਰੇਹੜੀ ਲਗਾਉਂਦਾ ਹਾਂ, ਅਧਿਕਾਰੀਆਂ ਨੇ ਬਿਨਾਂ ਨੋਟਿਸ ਦਿੱਤੇ ਮੇਰੀ ਰੇਹੜੀ ਜ਼ਬਤ ਕਰ ਲਈ।"),
])
def test_all_indic_languages_ask_in_native_language(engine, lang, sample_text):
    res = engine.process_case(sample_text, meta={"language": lang, "language_code": f"{lang}-IN"})
    assert res.get("language") == lang
    questions = res.get("follow_up_questions", [])
    assert len(questions) > 0
    # Must not fall back to English
    for q in questions:
        assert not q.startswith("What ")
        assert not q.startswith("Who ")
        assert not q.startswith("Where ")
        assert not q.startswith("When ")
