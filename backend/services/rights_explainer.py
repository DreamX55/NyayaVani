"""Understand Your Rights - Voice-First Structured Legal Intelligence Service.

Implements the Voice-First "Understand Your Rights" feature for NyayaVani:
1. What I understood (Confirmed facts summary)
2. What may be wrong (Plain language improper conduct, distinguishing allegations from verified facts)
3. Possible Act and dhaara (Act name, section, official primary URL, coverage summary, conditions to check)
4. Why it might apply here (Connection to confirmed facts, highlighting missing facts/questions)
5. What the person can do next (Practical ordered steps: evidence preservation, authority, DLSA legal aid, lawyer review)
6. Urgent help (Immediate safety & human-help notice prioritized when danger/custody/imminent eviction is detected)
7. One-minute recap (Concise spoken summary of the single most important next step)
8. Simpler words explanation (Jargon-free, conversational explanation for "repeat that in simpler words")

Generates matching spoken scripts in the user's chosen language for synthesis via Gnani Timbre TTS.
All citations maintain DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW status.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.services.source_register import (
    STATUTORY_REGISTER,
    REGISTER_VERSION,
    REVIEWER_METADATA,
    get_source_register_entry,
)

# Urgent triggers requiring immediate safety triage before legal explanation
URGENT_KEYWORDS = {
    "danger", "arrest", "arrested", "custody", "detained", "lockup", "police station",
    "threat", "beaten", "attack", "violence", "kill", "suicide", "kidnap", "evicting right now",
    "मारहाण", "धमकी", "हल्ला", "मारपीट", "जान से मारने", "कस्टडी", "अटक", "पोलीस ठाणे", "लॉकर",
    "काढत आहेत", "तोडफोड", "काढून टाकले", "हाकलून दिले", "அடி", "தாக்குதல்", "கைது", "ஹிம்சை",
    "దాడి", "అరెస్ట్", "హింస", "ಹಲ್ಲೆ", "ಬಂಧನ", "মারধর", "হামলা", "গ্রেপ্তার", "હુમલો", "ધમકી"
}

# Multilingual UI & Speech Headings
SECTION_HEADINGS = {
    "mr": {
        "understood": "१. मी काय समजलो (तथ्यांचा सारांश)",
        "wrong": "२. काय चुकीचे असू शकते (आरोप वि. कायदेशीर वास्तव)",
        "acts": "३. संभाव्य कायदा आणि कलमे (अधिकृत संदर्भ)",
        "why": "४. हे येथे का लागू होऊ शकते",
        "next": "५. आपण पुढे काय करू शकता (कृती आराखडा)",
        "urgent": "🚨 तातडीची सुरक्षा आणि मदत",
        "recap": "⏱️ एका मिनिटाचा सारांश",
        "simpler": "💡 अधिक सोप्या शब्दांत स्पष्टीकरण",
        "filing_disclaimer": "नोंद: कागदपत्रे व पुराव्यांची पडताळणी झाल्यानंतरच औपचारिक अर्ज किंवा नोटीस पाठवता येते. न्यायावाणीतर्फे थेट कोणताही खटला दाखल केला जात नाही आणि निकालाची हमी दिली जात नाही.",
        "allegation_disclaimer": "ही माहिती तुम्ही दिलेल्या निवेदनावर आधारित आहे. कायदेशीर दृष्टीने ही कृती चुकीची असू शकते, परंतु ठोस पुरावे समोर येईपर्यंत हा आरोप मानला जाईल."
    },
    "hi": {
        "understood": "1. मैंने क्या समझा (तथ्यों का सारांश)",
        "wrong": "2. क्या गलत हो सकता है (आरोप बनाम कानूनी तथ्य)",
        "acts": "3. संभावित कानून और धाराएं (सरकारी संदर्भ)",
        "why": "4. यह यहाँ क्यों लागू हो सकता है",
        "next": "5. आप आगे क्या कर सकते हैं (कार्य योजना)",
        "urgent": "🚨 आपातकालीन सुरक्षा और सहायता",
        "recap": "⏱️ एक मिनट का सार",
        "simpler": "💡 सरल शब्दों में समझें",
        "filing_disclaimer": "नोट: सभी दस्तावेजों और सबूतों के सत्यापन के बाद ही कोई औपचारिक शिकायत या नोटिस भेजा जा सकता है। न्यायावाणी कोई केस फाइल नहीं करती है और न ही किसी कानूनी नतीजे की गारंटी देती है।",
        "allegation_disclaimer": "यह आपके द्वारा दिए गए बयान पर आधारित है। कानूनन यह आचरण अनुचित हो सकता है, लेकिन आवश्यक रिकॉर्ड जांचे बिना इसे अभी आपका आरोप माना जाएगा।"
    },
    "en": {
        "understood": "1. What I understood (Summary of facts)",
        "wrong": "2. What may be wrong (Allegation vs Verified Fact)",
        "acts": "3. Possible Acts and Sections (Primary statutory sources)",
        "why": "4. Why it might apply here",
        "next": "5. What you can do next (Action options)",
        "urgent": "🚨 Urgent Safety & Human Help",
        "recap": "⏱️ One-minute recap",
        "simpler": "💡 In Simpler Words",
        "filing_disclaimer": "Notice: A formal notice, claim, or petition may be possible once records are verified. NyayaVani does not file cases on your behalf, nor can any legal outcome be guaranteed.",
        "allegation_disclaimer": "This is based on your account. Legally, the improper nature depends on verifying records; until substantiated, this remains an allegation requiring supporting evidence."
    },
    "ta": {
        "understood": "1. நான் புரிந்து கொண்டது",
        "wrong": "2. இதில் என்ன தவறு இருக்கலாம்",
        "acts": "3. பொருந்தக்கூடிய சட்டப் பிரிவுகள்",
        "why": "4. இது ஏன் இங்கு பொருந்தக்கூடும்",
        "next": "5. நீங்கள் அடுத்து என்ன செய்யலாம்",
        "urgent": "🚨 அவசர உதவி & பாதுகாப்பு",
        "recap": "⏱️ ஒரு நிமிட சுருக்கம்",
        "simpler": "💡 எளிய விளக்கவுரை",
        "filing_disclaimer": "குறிப்பு: ஆவணங்கள் சரிபார்க்கப்பட்ட பின்னரே முறையான புகார் செய்ய முடியும். முடிவுகளுக்கு உத்தரவாதம் இல்லை.",
        "allegation_disclaimer": "இது நீங்கள் கூறிய தகவல்களின் அடிப்படையிலானது. முழுமையான விசாரணைக்கு பின்னரே இது உறுதிப்படுத்தப்படும்."
    },
    "te": {
        "understood": "1. నేను అర్థం చేసుకున్నది",
        "wrong": "2. చట్టపరంగా ఏమి తప్పు ఉండవచ్చు",
        "acts": "3. వర్తించే చట్టాలు మరియు సెక్షన్లు",
        "why": "4. ఇది ఇక్కడ ఎందుకు వర్తిస్తుంది",
        "next": "5. మీరు తదుపరి ఏమి చేయవచ్చు",
        "urgent": "🚨 అత్యవసర సహాయం",
        "recap": "⏱️ ఒక నిమిషం సారాంశం",
        "simpler": "💡 సులభమైన మాటల్లో",
        "filing_disclaimer": "గమనిక: సాక్ష్యాధారాలు నిర్ధారించబడిన తర్వాత మాత్రమే అధికారిక నోటీసు సాధ్యమవుతుంది.",
        "allegation_disclaimer": "ఇది మీ వివరణ ఆధారంగా చెప్పబడింది. ఆధారాలు లేకుండా దీన్ని నేరుగా ధృవీకరించలేము."
    },
    "kn": {
        "understood": "1. ನಾನು ಅರ್ಥಮಾಡಿಕೊಂಡದ್ದು",
        "wrong": "2. ಇದರಲ್ಲಿ ಏನು ತಪ್ಪಾಗಿರಬಹುದು",
        "acts": "3. ಅನ್ವಯಿಸಬಹುದಾದ ಕಾನೂನು ಮತ್ತು ಕಲಂಗಳು",
        "why": "4. ಇದು ಇಲ್ಲಿ ಏಕೆ ಅನ್ವಯಿಸಬಹುದು",
        "next": "5. ನೀವು ಮುಂದೆ ಏನು ಮಾಡಬಹುದು",
        "urgent": "🚨 ತುರ್ತು ಸಹಾಯ",
        "recap": "⏱️ ಒಂದು ನಿಮಿಷದ ಸಾರಾಂಶ",
        "simpler": "💡 ಸರಳ ಮಾತುಗಳಲ್ಲಿ",
        "filing_disclaimer": "ಗಮನಿಸಿ: ದಾಖಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿದ ನಂತರವೇ ದೂರು ದಾಖಲಿಸಲು ಸಾಧ್ಯ.",
        "allegation_disclaimer": "ಇದು ನಿಮ್ಮ ಹೇಳಿಕೆಯನ್ನು ಆಧರಿಸಿದೆ. ದಾಖಲೆಗಳ ಪರಿಶೀಲನೆ ಅಗತ್ಯವಿದೆ."
    },
    "bn": {
        "understood": "১. আমি যা বুঝতে পেরেছি",
        "wrong": "২. এতে কী অন্যায় হতে পারে",
        "acts": "৩. সম্ভাব্য আইন ও ধারা",
        "why": "৪. এটি এখানে কেন প্রযোজ্য হতে পারে",
        "next": "৫. আপনি পরবর্তীতে কী করতে পারেন",
        "urgent": "🚨 জরুরি সাহায্য ও সুরক্ষা",
        "recap": "⏱️ এক মিনিটের সারসংক্ষেপ",
        "simpler": "💡 সহজ কথায় শুনুন",
        "filing_disclaimer": "বিজ্ঞপ্তি: নথিপত্র যাচাইয়ের পরেই আনুষ্ঠানিক পদক্ষেপ নেওয়া যেতে পারে।",
        "allegation_disclaimer": "এটি আপনার বক্তব্যের ওপর ভিত্তি করে প্রস্তুত। প্রমাণের ভিত্তিতেই এটি প্রমাণিত হবে।"
    },
    "gu": {
        "understood": "1. હું શું સમજ્યો",
        "wrong": "2. કાયદાકીય રીતે શું ખોટું હોઈ શકે",
        "acts": "3. સંભવિત કાયદા અને કલમો",
        "why": "4. આ અહીં શા માટે લાગુ થઈ શકે",
        "next": "5. તમે આગળ શું કરી શકો છો",
        "urgent": "🚨 તાત્કાલિક સહાય",
        "recap": "⏱️ એક મિનિટનો સારાંશ",
        "simpler": "💡 સરળ શબ્દોમાં",
        "filing_disclaimer": "નોંધ: પુરાવાઓની ચકાસણી પછી જ ઔપચારિક ફરિયાદ કરી શકાય છે.",
        "allegation_disclaimer": "આ તમારા નિવેદન પર આધારિત છે. પુરાવા તપાસ્યા વિના આને આક્ષેપ માનવામાં આવશે."
    },
    "ml": {
        "understood": "1. ഞാൻ മനസ്സിലാക്കിയത്",
        "wrong": "2. ഇതിൽ എന്ത് തെറ്റായിരിക്കാം",
        "acts": "3. ബാധകമായ നിയമ വകുപ്പുകൾ",
        "why": "4. ഇത് ഇവിടെ എന്തുക്കൊണ്ട് ബാധകമാകാം",
        "next": "5. ഇനി നിങ്ങൾ എന്ത് ചെയ്യണം",
        "urgent": "🚨 അടിയന്തര സഹായം",
        "recap": "⏱️ ഒരു മിനിറ്റ് സംഗ്രഹം",
        "simpler": "💡 ലളിതമായ വാക്കുകളിൽ",
        "filing_disclaimer": "ശ്രദ്ധിക്കുക: രേഖകൾ പരിശോധിച്ച ശേഷം മാത്രമേ നിയമനടപടികൾ സാധ്യമാകൂ.",
        "allegation_disclaimer": "ഇത് താങ്കൾ നൽകിയ വിവരങ്ങളെ അടിസ്ഥാനമാക്കിയുള്ളതാണ്."
    },
    "pa": {
        "understood": "1. ਮੈਂ ਕੀ ਸਮਝਿਆ",
        "wrong": "2. ਕਾਨੂੰਨ ਅਨੁਸਾਰ ਕੀ ਗਲਤ ਹੋ ਸਕਦਾ ਹੈ",
        "acts": "3. ਸੰਭਾਵੀ ਕਾਨੂੰਨ ਅਤੇ ਧਾਰਾਵਾਂ",
        "why": "4. ਇਹ ਇੱਥੇ ਕਿਉਂ ਲਾਗੂ ਹੋ ਸਕਦਾ ਹੈ",
        "next": "5. ਤੁਸੀਂ ਅੱਗੇ ਕੀ ਕਰ ਸਕਦੇ ਹੋ",
        "urgent": "🚨 ਐਮਰਜੈਂਸੀ ਸਹਾਇਤਾ",
        "recap": "⏱️ ਇੱਕ ਮਿੰਟ ਦਾ ਸਾਰ",
        "simpler": "💡 ਸਰਲ ਸ਼ਬਦਾਂ ਵਿੱਚ",
        "filing_disclaimer": "ਨੋਟ: ਸਬੂਤਾਂ ਦੀ ਪੁਸ਼ਟੀ ਤੋਂ ਬਾਅਦ ਹੀ ਕੋਈ ਕਾਨੂੰਨੀ ਕਦਮ ਚੁੱਕਿਆ ਜਾ ਸਕਦਾ ਹੈ।",
        "allegation_disclaimer": "ਇਹ ਤੁਹਾਡੇ ਬਿਆਨ 'ਤੇ ਆਧਾਰਿਤ ਹੈ। ਬਿਨਾਂ ਪੁਖਤਾ ਰਿਕਾਰਡ ਦੇ ਇਹ ਸਿਰਫ ਇਕ ਦੋਸ਼ ਹੈ।"
    }
}

# Domain substantive legal explanations
CATEGORY_RIGHTS_BLUEPRINT = {
    "WAGE_THEFT": {
        "improper_conduct": {
            "en": "Withholding or delaying payment of earned wages for work already completed beyond the statutory wage period.",
            "mr": "काम पूर्ण झाल्यानंतरही ठरलेल्या वेळेत कामगाराचे वेतन न देणे किंवा वेतनातून बेकायदेशीर कपात करणे.",
            "hi": "काम पूरा होने के बाद भी तय समय सीमा के भीतर मजदूरी या वेतन का भुगतान न करना अथवा अवैध कटौती करना।"
        },
        "why_applicable": {
            "en": "If you performed labor or services in an establishment or under a contractor and the agreed wage remains unpaid.",
            "mr": "जर तुम्ही कंत्राटदाराकडे किंवा कंपनीत काम केले असेल आणि तुमचे वेतन अद्याप थकवले असेल, तर वेतनाचा हक्क लागू होतो.",
            "hi": "यदि आपने किसी कंपनी, साइट या ठेकेदार के तहत काम किया है और आपकी मेहनत का पारिश्रमिक नहीं दिया गया है।"
        },
        "simpler_words": {
            "en": "In simple terms: if you worked, nobody has the right to keep your money. The law requires full payment on time. Save proof like site photos or attendance cards, don't sign blank papers, and call 15100 for a free legal aid advocate.",
            "mr": "सोप्या शब्दांत: तुम्ही घाम गाळून काम केले असल्यास तुमचे पैसे अडवून ठेवण्याचा कोणालाही अधिकार नाही. हजेरी कार्ड किंवा कामाचे पुरावे सांभाळून ठेवा, कोऱ्या कागदावर सही करू नका आणि १५१०० वर फोन करून मोफत सरकारी वकिलाची मदत घ्या.",
            "hi": "सरल शब्दों में: अगर आपने मेहनत से काम किया है, तो कोई आपके पैसे नहीं रोक सकता। काम के सबूत और अटेंडेंस कार्ड संभाल कर रखें, खाली कागज पर हस्ताक्षर न करें और 15100 पर कॉल करके मुफ्त कानूनी मदद पाएं।"
        },
        "recap": {
            "en": "Keep attendance records, issue a written wage demand, and approach the Labor Commissioner or call 15100 for free legal aid.",
            "mr": "हजेरी आणि मेसेजचे पुरावे सांभाळा, कंत्राटदाराला लेखी नोटीस द्या आणि मोफत मदतीसाठी १५१०० वर संपर्क साधा.",
            "hi": "हाजिरी और संदेशों के सबूत सुरक्षित रखें, लिखित मांग पत्र दें और मुफ्त कानूनी सहायता हेतु 15100 पर कॉल करें।"
        },
        "urgent_helpline": "15100",
        "action_authority": "Labor Commissioner / DLSA Legal Aid"
    },
    "STREET_VENDOR": {
        "improper_conduct": {
            "en": "Evicting, relocating, or seizing goods of an active street vendor without conducting a Town Vending Committee survey or serving 30-day prior notice.",
            "mr": "टाऊन वेंडिंग कमिटीचा (TVC) सर्व्हे न करता आणि ३० दिवसांची पूर्वसूचना न देता फेरीवाल्याचा गाडा किंवा सामान जप्त करणे अगर हटवणे.",
            "hi": "टाउन वेंडिंग कमेटी का सर्वे किए बिना और 30 दिन का लिखित नोटिस दिए बिना रेहड़ी-पटरी या सामान को जब्त करना या हटाना।"
        },
        "why_applicable": {
            "en": "If you vend in an urban area and hold a survey receipt, PM SVANidhi record, or have operated continuously prior to formal survey completion.",
            "mr": "जर तुम्ही सार्वजनिक जागी व्यवसाय करत असाल आणि तुमच्याकडे पीएम स्वनिधी किंवा वेंडिंग पावती असेल, तर कायद्याचे संरक्षण लागू होते.",
            "hi": "यदि आप शहरी इलाके में वेंडिंग करते हैं और आपके पास पीएम स्वनिधि रसीद या पहचान पत्र है, तो वैधानिक सुरक्षा लागू होती है।"
        },
        "simpler_words": {
            "en": "In simple terms: municipal staff or police cannot arbitrarily evict your cart without notice. Keep your PM SVANidhi receipt and stall photos ready, show them politely, and approach the Town Vending Committee.",
            "mr": "सोप्या शब्दांत: नोटीस न देता पालिकेला किंवा पोलिसांना तुमचा गाडा हटवण्याचा अधिकार नाही. स्वनिधी पावती सोबत ठेवा, वाद घालू नका आणि १५१०० वर कॉल करून संरक्षण मिळवा.",
            "hi": "सरल शब्दों में: बिना 30 दिन के नोटिस के कोई भी आपका ठेला या दुकान जबरन नहीं हटा सकता। अपनी रसीदें पास रखें और 15100 पर कॉल करके मुफ्त विधिक सहायता लें।"
        },
        "recap": {
            "en": "Keep survey receipts and stall photos, cite Section 3(3) of Street Vendors Act, and contact DLSA on 15100.",
            "mr": "स्वनिधी पावती व स्टॉलचे फोटो जपून ठेवा, कलम ३(३) चा संदर्भ द्या आणि १५१०० वर मोफत वकिलाची मदत घ्या.",
            "hi": "स्वनिधि रसीद और स्टॉल की फोटो रखें, धारा 3(3) का हवाला दें और 15100 पर मुफ्त कानूनी मदद लें।"
        },
        "urgent_helpline": "15100",
        "action_authority": "Town Vending Committee (TVC) / Municipal Ward Office"
    },
    "POLICE_CUSTODY": {
        "improper_conduct": {
            "en": "Detaining an individual without serving grounds of arrest or arrest memo, denying access to an advocate, or refusing to register a mandatory Zero FIR for a cognizable crime.",
            "mr": "अटकेचे कारण न सांगता किंवा अरेस्ट मेमो न देता डांबून ठेवणे, वकिलाशी बोलू न देणे किंवा दखलपात्र गुन्ह्यात झिरो एफआयआर नोंदवण्यास नकार देणे.",
            "hi": "गिरफ्तारी का कारण या मेमो दिए बिना हिरासत में रखना, वकील से मिलने से रोकना, या संज्ञेय अपराध में जीरो एफआईआर दर्ज न करना।"
        },
        "why_applicable": {
            "en": "Applies directly to any questioning, detention, or formal custody at a police station or checkpost under Bharatiya Nagarik Suraksha Sanhita (BNSS).",
            "mr": "पोलीस ठाण्यात चौकशी, ताब्यात घेणे किंवा एफआयआर नोंदवण्याबाबत भारतीय नागरिक सुरक्षा संहितेच्या (BNSS) तरतुदी थेट लागू होतात.",
            "hi": "पुलिस स्टेशन में पूछताछ, हिरासत या एफआईआर दर्ज कराने के संबंध में भारतीय नागरिक सुरक्षा संहिता (BNSS) सीधे लागू होती है।"
        },
        "simpler_words": {
            "en": "In simple terms: police cannot hold anyone secretly. They must prepare an arrest memo, let the person inform family, and arrange a free legal aid lawyer. You have the right to medical examination.",
            "mr": "सोप्या शब्दांत: पोलिसांना कोणालाही गुपचूप डांबून ठेवता येत नाही. अरेस्ट मेमो मागण्याचा, नातेवाईकांना फोन करण्याचा आणि मोफत सरकारी वकील मिळवण्याचा तुमचा हक्क आहे.",
            "hi": "सरल शब्दों में: पुलिस किसी को बिना लिखा-पढ़ी के बंद नहीं रख सकती। अरेस्ट मेमो मांगना, परिवार को सूचना देना और मुफ्त वकील पाना आपका संवैधानिक अधिकार है।"
        },
        "recap": {
            "en": "Ensure immediate family is notified, demand an arrest memo and medical exam, and call 15100 for a 24x7 DLSA duty magistrate lawyer.",
            "mr": "नातेवाईकांना तात्काळ कळवा, अरेस्ट मेमोची मागणी करा आणि १५१०० वर फोन करून ड्युटी वकील मिळवा.",
            "hi": "परिवार को तुरंत सूचित करवाएं, अरेस्ट मेमो की मांग करें और 15100 पर 24 घंटे उपलब्ध ड्यूटी वकील मांगें।"
        },
        "urgent_helpline": "112 / 15100",
        "action_authority": "Judicial Magistrate / Superintendent of Police (SP)"
    },
    "DOMESTIC_VIOLENCE": {
        "improper_conduct": {
            "en": "Inflicting physical, verbal, emotional, sexual, or economic abuse, or threatening eviction from the shared matrimonial or domestic household.",
            "mr": "शारीरिक, मानसिक, शाब्दिक किंवा आर्थिक छळ करणे अथवा सामायिक घरातून बेकायदेशीरपणे हाकलून देणे.",
            "hi": "शारीरिक, मानसिक, मौखिक या आर्थिक प्रताड़ना करना अथवा साझे घर से बेदखल करने की धमकी देना।"
        },
        "why_applicable": {
            "en": "Applies to any woman living in a domestic relationship with respondent in a shared household under Protection of Women from Domestic Violence Act, 2005.",
            "mr": "कौटुंबिक हिंसाचार कायद्यानुसार (PWDVA 2005) सामायिक घरात राहणाऱ्या कोणत्याही महिलेस निवारा व संरक्षणाचा पूर्ण अधिकार आहे.",
            "hi": "घरेलू हिंसा अधिनियम, 2005 के तहत साझे घर में रहने वाली महिला को संरक्षण, निवास और भरण-पोषण का पूर्ण अधिकार है।"
        },
        "simpler_words": {
            "en": "In simple terms: nobody has the right to abuse you or throw you out of your house. You have a legal right to residence and monthly maintenance. Dial 181 or 112 immediately if unsafe.",
            "mr": "सोप्या शब्दांत: तुम्हाला मारहाण करण्याचा किंवा घरातून बाहेर काढण्याचा कोणालाही अधिकार नाही. तुम्हाला घरात राहण्याचा व खर्चाचा हक्क आहे. धोका असल्यास त्वरित १८१ किंवा ११२ वर फोन करा.",
            "hi": "सरल शब्दों में: किसी को भी आपके साथ दुर्व्यवहार करने या घर से निकालने का अधिकार नहीं है। आपको घर में रहने और खर्चे का हक है। खतरे में तुरंत 181 या 112 डायल करें।"
        },
        "recap": {
            "en": "Prioritize physical safety, call 181/112 in danger, remember you cannot be evicted from the shared home under Section 19, and call 15100 for free legal aid.",
            "mr": "आधी स्वतःची सुरक्षा बघा, धोक्यात १८१ किंवा ११२ वर कॉल करा, कलम १९ नुसार घर सोडण्याची सक्ती करता येत नाही, आणि १५१०० वर मोफत वकिलाची मदत घ्या.",
            "hi": "पहले अपनी सुरक्षा सुनिश्चित करें, खतरे में 181/112 मिलाएं, धारा 19 के तहत आपको घर से नहीं निकाला जा सकता, और 15100 पर मुफ्त वकील पाएं।"
        },
        "urgent_helpline": "181 / 112",
        "action_authority": "Protection Officer / Judicial Magistrate First Class"
    },
    "MOTOR_ACCIDENT_PRO": {
        "improper_conduct": {
            "en": "Fleeing the accident scene, failing to secure medical aid, or denying statutory third-party insurance compensation after a vehicular collision.",
            "mr": "अपघातानंतर मदत न करता पळून जाणे, किंवा विमा कंपनीने कायदेशीर नुकसानभरपाई देण्यास टाळाटाळ करणे.",
            "hi": "दुर्घटना के बाद बिना मदद किए भाग जाना, या वैध बीमा होने पर भी क्लेम देने में आनाकानी करना।"
        },
        "why_applicable": {
            "en": "Motor Vehicles Act (amended 2019) mandates immediate Detailed Accident Report (DAR) filing and provides no-fault liability and MACT claim remedies.",
            "mr": "मोटर वाहन कायद्यानुसार अपघात झाल्यास ९० दिवसांत पोलिसांचा डार (DAR) अहवाल आवश्यक असून नुकसानभरपाई न्यायाधिकरणात (MACT) दावा करता येतो.",
            "hi": "मोटर वाहन अधिनियम के तहत दुर्घटना की 90 दिनों में पुलिस रिपोर्ट (DAR) जरूरी है और क्लेम ट्रिब्यूनल (MACT) में मुआवजे का अधिकार है।"
        },
        "simpler_words": {
            "en": "In simple terms: if an accident caused injury or vehicle damage, third-party insurance must compensate you. Photograph the vehicles and number plates, demand a police DAR report, and file your claim in MACT within 6 months.",
            "mr": "सोप्या शब्दांत: अपघात झाला असल्यास दुसऱ्या वाहनाचा विमा तुम्हाला नुकसानभरपाई देण्यास बांधील आहे. दोन्ही गाड्यांचे फोटो घ्या, पोलिसांकडून डार रिपोर्ट घ्या आणि न्यायाधिकरणात दावा करा.",
            "hi": "सरल शब्दों में: सड़क दुर्घटना में चोट या नुकसान होने पर थर्ड-पार्टी बीमा से मुआवजा मिलता है। गाड़ियों के फोटो लें, पुलिस से रिपोर्ट लें और ट्रिब्यूनल में केस लगाएं।"
        },
        "recap": {
            "en": "Photograph the crash and number plates, obtain police Detailed Accident Report (DAR), preserve hospital bills, and consult MACT counsel or DLSA.",
            "mr": "गाड्यांचे फोटो आणि नंबर प्लेट टिपून घ्या, पोलिसांचा डार रिपोर्ट मिळवा आणि नुकसानभरपाईसाठी मोफत कायदेशीर मदत घ्या.",
            "hi": "गाड़ियों के फोटो लें, पुलिस से विस्तृत दुर्घटना रिपोर्ट लें, अस्पताल के बिल संभालें और क्लेम हेतु 15100 पर संपर्क करें।"
        },
        "urgent_helpline": "112 (Ambulance/Police)",
        "action_authority": "Motor Accident Claims Tribunal (MACT)"
    },
    "LAND_GRABBING": {
        "improper_conduct": {
            "en": "Dispossessing settled occupants by force, fraud, or forged title documents without judicial eviction decree.",
            "mr": "न्यायालयाचा कोणताही आदेश नसताना बळाचा वापर करून किंवा खोट्या कागदपत्रांच्या आधारे जागेचा ताबा घेणे.",
            "hi": "बिना कानूनी अदालती आदेश के जबरन या फर्जी कागजात बनाकर जमीन या मकान पर अवैध कब्जा करना।"
        },
        "why_applicable": {
            "en": "Specific Relief Act Section 6 protects settled peaceful possession against forcible dispossession within a 6-month statutory window.",
            "mr": "स्पेसिफिक रिलीफ कायद्याच्या कलम ६ नुसार शांततापूर्ण ताबा असलेल्या व्यक्तीला बळाने बेदखल केल्यास ६ महिन्यांत ताबा परत मागता येतो.",
            "hi": "विशिष्ट अनुतोष अधिनियम की धारा 6 के तहत 6 महीने के भीतर जबरन छीना गया कब्जा वापस पाने का सीधा अधिकार है।"
        },
        "simpler_words": {
            "en": "In simple terms: even if someone claims ownership, they cannot throw you out by force without a court order. Keep electricity bills, tax receipts, or tenancy papers safe, and file a Section 6 suit within 6 months.",
            "mr": "सोप्या शब्दांत: कोणाचेही मालकी हक्क असले तरी न्यायालयाच्या हुकूमनाम्याशिवाय कोणालाही बळाने बाहेर काढता येत नाही. वीज बिल आणि पावत्या जतन करा.",
            "hi": "सरल शब्दों में: कोई भी व्यक्ति अदालत के आदेश के बिना आपको ताकत के बल पर बेदखल नहीं कर सकता। अपने कब्जे के दस्तावेज और बिल संभाल कर रखें।"
        },
        "recap": {
            "en": "Gather possession evidence (bills, tax receipts), report criminal trespass under BNS 329, and file a Section 6 suit within 6 months.",
            "mr": "ताब्याचे पुरावे गोळा करा, पोलिसांत तक्रार नोंदवा आणि ६ महिन्यांच्या आत कलम ६ नुसार दावा दाखल करा.",
            "hi": "कब्जे के साक्ष्य सुरक्षित करें, पुलिस में शिकायत दर्ज कराएं और 6 माह के भीतर धारा 6 का वाद दायर करें।"
        },
        "urgent_helpline": "112 / 15100",
        "action_authority": "Civil Court / Sub-Divisional Magistrate (SDM)"
    },
    "LOAN_FRAUD": {
        "improper_conduct": {
            "en": "Harassing borrowers through unapproved digital apps, accessing phone contacts without consent, or using abusive recovery tactics prohibited by RBI.",
            "mr": "बेकायदेशीर लोन ॲप्सद्वारे फोनमधील कॉन्टॅक्ट हॅक करून धमकावणे, अश्लील फोटो मॉर्फ करणे किंवा आरबीआय नियमांचे उल्लंघन करून वसुली करणे.",
            "hi": "अवैध लोन ऐप द्वारा फोन डेटा चुराकर परिजनों को ब्लैकमेल करना, फोटो मॉर्फ करना या आरबीआई नियमों के खिलाफ जाकर प्रताड़ित करना।"
        },
        "why_applicable": {
            "en": "RBI Digital Lending Guidelines 2022 strictly prohibit accessing borrower contacts and mandate regulated Recovery Agent practices under penal laws.",
            "mr": "आरबीआयच्या २०२२ च्या डिजिटल लेंडिंग नियमांनुसार कॉन्टॅक्ट लिस्ट ॲक्सेस करण्यास सक्त बंदी असून धमकावणे हा फौजदारी गुन्हा आहे.",
            "hi": "आरबीआई की 2022 गाइडलाइन्स के तहत कॉन्टैक्ट्स चुराना और ब्लैकमेल करना गैरकानूनी और संज्ञेय अपराध है।"
        },
        "simpler_words": {
            "en": "In simple terms: recovery agents have zero right to threaten you or message your contacts. Take screenshots of threatening messages, do not pay extortion demands, and report immediately to 1930 and cybercrime.gov.in.",
            "mr": "सोप्या शब्दांत: लोन एजंटला तुमच्या नातेवाईकांना फोन करण्याचा किंवा धमकावण्याचा अधिकार नाही. मेसेजचे स्क्रीनशॉट ठेवा, पैसे देऊ नका आणि १९३० वर सायबर तक्रार करा.",
            "hi": "सरल शब्दों में: लोन एजेंट को आपके रिश्तेदारों को फोन करने या धमकाने का कोई हक नहीं है। स्क्रीनशॉट लें, डरकर पैसे न दें और 1930 पर साइबर रिपोर्ट करें।"
        },
        "recap": {
            "en": "Save all threat screenshots and transaction IDs, block unauthorized apps, and report to National Cyber Crime Helpline 1930.",
            "mr": "धमकीचे स्क्रीनशॉट आणि व्यवहार तपशील सेव्ह करा आणि राष्ट्रीय सायबर क्राईम हेल्पलाइन १९३० वर त्वरित तक्रार नोंदवा.",
            "hi": "धमकियों के स्क्रीनशॉट सुरक्षित रखें, डरें नहीं और राष्ट्रीय साइबर हेल्पलाइन 1930 पर तत्काल शिकायत दर्ज करें।"
        },
        "urgent_helpline": "1930 (National Cyber Crime)",
        "action_authority": "Cyber Crime Cell / RBI Ombudsman"
    },
    "REAL_ESTATE_RERA": {
        "improper_conduct": {
            "en": "Failing to deliver possession of real estate by promised agreement date, diverting project funds, or altering sanctioned building plans without consent.",
            "mr": "ठरलेल्या मुदतीत घराचा ताबा न देणे किंवा खरेदीदाराची संमती न घेता प्रकल्पाच्या आराखड्यात परस्पर बदल करणे.",
            "hi": "अनुबंध में तय तारीख पर मकान का कब्जा न देना, प्रोजेक्ट फंड्स में हेराफेरी करना या बिना सहमति नक्शा बदलना।"
        },
        "why_applicable": {
            "en": "RERA Act Section 18 grants statutory entitlement to complete refund with interest at SBI MCLR + 2% or monthly delayed possession interest.",
            "mr": "रेरा (RERA) कायद्याच्या कलम १८ नुसार ताबा लांबल्यास व्याज मिळवण्याचा किंवा व्याजासह पूर्ण परतावा मागण्याचा खरेदीदाराचा हक्क आहे.",
            "hi": "रेरा अधिनियम की धारा 18 के अनुसार कब्जा देरी पर ब्याज पाने या ब्याज सहित पूरा पैसा वापस लेने का वैधानिक अधिकार है।"
        },
        "simpler_words": {
            "en": "In simple terms: if the builder delayed handing over your flat beyond the agreement date, you are entitled to statutory monthly interest until possession. File a complaint on your State RERA portal.",
            "mr": "सोप्या शब्दांत: बिल्डरने करारातील मुदतीत ताबा न दिल्यास तुम्हाला दरमहा कायदेशीर व्याज मिळण्याचा हक्क आहे. राज्य रेरा प्राधिकरणाकडे तक्रार करा.",
            "hi": "सरल शब्दों में: यदि बिल्डर ने तय समय पर फ्लैट नहीं दिया, तो आपको ब्याज सहित मुआवजा पाने का हक है। राज्य के रेरा पोर्टल पर शिकायत करें।"
        },
        "recap": {
            "en": "Collate builder agreement and payment receipts, calculate delayed possession period, and file under Section 31 before your State RERA Authority.",
            "mr": "खरेदी करार आणि बँक पावत्या जमा करा आणि राज्य रेरा प्राधिकरणाकडे कलम ३१ अंतर्गत ऑनलाईन तक्रार नोंदवा.",
            "hi": "बिल्डर एग्रीमेंट और बैंक भुगतान रसीदें इकट्ठा करें और राज्य रेरा अथॉरिटी में धारा 31 के तहत शिकायत दर्ज करें।"
        },
        "urgent_helpline": "15100",
        "action_authority": "State Real Estate Regulatory Authority (RERA)"
    },
    "COMMERCIAL_CONTRACT_MSME": {
        "improper_conduct": {
            "en": "Delaying payment to micro and small suppliers beyond the statutory maximum 45-day window after delivery of goods or services.",
            "mr": "सूक्ष्म व लघु उद्योगांकडून (MSME) माल अथवा सेवा घेतल्यानंतर ४५ दिवसांच्या आत देयके अदा न करणे.",
            "hi": "एमएसएमई सप्लायर से माल या सेवा लेने के बाद वैधानिक 45 दिन की अवधि के भीतर भुगतान न करना।"
        },
        "why_applicable": {
            "en": "MSMED Act Section 15 & 16 mandates payment within 45 days and penal compound interest at 3 times RBI bank rate on delayed payments.",
            "mr": "एमएसएमई कायद्याच्या कलम १५ व १६ नुसार ४५ दिवसांनंतर आरबीआयच्या बँक दराच्या तिप्पट चक्रवाढ व्याज मिळवण्याचा हक्क आहे.",
            "hi": "एमएसएमई कानून की धारा 15 और 16 के तहत 45 दिन बाद आरबीआई बैंक दर के तीन गुना चक्रवृદ્ધિ ब्याज का कानूनी प्रावधान है।"
        },
        "simpler_words": {
            "en": "In simple terms: buyers cannot delay paying registered MSMEs. After 45 days, statutory compound interest accumulates automatically. You can file a case on the MSME Samadhaan portal without court fees.",
            "mr": "सोप्या शब्दांत: मोठ्या कंपन्यांना एमएसएमईचे पैसे अडकवून ठेवता येत नाहीत. ४५ दिवसांनंतर तिप्पट व्याज लागू होते. समाधान पोर्टलवर तक्रार दाखल करा.",
            "hi": "सरल शब्दों में: खरीदार एमएसएमई का भुगतान नहीं रोक सकते। 45 दिन बाद तीन गुना ब्याज जुड़ता है। समाधान पोर्टल पर बिना कोर्ट फीस मामला दर्ज करें।"
        },
        "recap": {
            "en": "Verify Udyam registration date, compile purchase orders and delivery challans, and register on MSME Samadhaan portal.",
            "mr": "उद्यम नोंदणी, खरेदी आदेश आणि पोचपावती गोळा करा आणि एमएसएमई समाधान पोर्टलवर दावा दाखल करा.",
            "hi": "उद्यम पंजीकरण और डिलीवरी चालान सुरक्षित रखें और एमएसएमई समाधान पोर्टल पर केस फाइल करें।"
        },
        "urgent_helpline": "15100",
        "action_authority": "Micro & Small Enterprise Facilitation Council (MSEFC)"
    },
    "CORRUPTION_RTI": {
        "improper_conduct": {
            "en": "Demanding bribes or illicit gratification for public services, or unlawfully refusing public records and benefit delivery.",
            "mr": "शासकीय सेवा किंवा अनुदानासाठी लाच मागणे अथवा माहिती अधिकारात शासकीय कागदपत्रे देण्यास जाणीवपूर्वक नकार देणे.",
            "hi": "सरकारी योजनाओं या सेवाओं के लिए रिश्वत मांगना या सूचना के अधिकार में सरकारी रिकॉर्ड देने से इनकार करना।"
        },
        "why_applicable": {
            "en": "Right to Information Act Section 6 & 7 guarantees records within 30 days; Prevention of Corruption Act criminalizes bribe demands.",
            "mr": "माहिती अधिकाराच्या कलम ६ व ७ नुसार ३० दिवसांत माहिती मिळणे हा तुमचा अधिकार असून लाच मागणे हा फौजदारी गुन्हा आहे.",
            "hi": "आरटीआई कानून की धारा 6 और 7 के तहत 30 दिन में सूचना पाना नागरिक का हक है और रिश्वत मांगना गंभीर अपराध है।"
        },
        "simpler_words": {
            "en": "In simple terms: public officials cannot demand money for government duties. File a 10-rupee RTI application to trace your file, and report bribe demands to Anti-Corruption Bureau.",
            "mr": "सोप्या शब्दांत: शासकीय कामासाठी लाच देण्याची गरज नाही. फाईल कुठे अडकली आहे हे शोधण्यासाठी १० रुपयांचा आरटीआय अर्ज करा.",
            "hi": "सरल शब्दों में: सरकारी काम के लिए रिश्वत देने की जरूरत नहीं है। फाइल की स्थिति जानने के लिए 10 रुपये का आरटीआई लगाएं।"
        },
        "recap": {
            "en": "File a targeted RTI application under Section 6, obtain application receipt, and report bribe solicitations to the Vigilance/ACB helpline.",
            "mr": "कलम ६ अंतर्गत आरटीआय अर्ज करा, पोचपावती ठेवा आणि लाच मागितल्यास लाचलुचपत प्रतिबंधक विभागाकडे तक्रार करा.",
            "hi": "धारा 6 में आरटीआई आवेदन दें, पावती सुरक्षित रखें और रिश्वत की मांग पर एंटी करप्शन ब्यूरो में शिकायत दर्ज कराएं।"
        },
        "urgent_helpline": "1064 (Anti-Corruption Helpline) / 15100",
        "action_authority": "Public Information Officer (PIO) / Anti-Corruption Bureau"
    },
    "RELIGIOUS_GATHERING": {
        "improper_conduct": {
            "en": "Unlawfully disrupting peaceful worship, damaging religious property, or using force against attendees at a constitutionally protected gathering.",
            "mr": "शांततापूर्ण धार्मिक सभेमध्ये किंवा प्रार्थनेमध्ये बेकायदेशीरपणे अडथळा आणणे, धमकावणे अथवा मालमत्तेचे नुकसान करणे.",
            "hi": "शांतिपूर्ण प्रार्थना सभा या धार्मिक आयोजन में अवैध रूप से बाधा डालना, धमकी देना या संपत्ति को नुकसान पहुंचाना।"
        },
        "why_applicable": {
            "en": "Constitution of India Article 25 guarantees freedom of conscience and peaceful worship, protected by penal sections of BNS 2023.",
            "mr": "भारतीय संविधानाच्या कलम २५ नुसार शांततापूर्ण प्रार्थनेचा मूलभूत हक्क असून त्यात अडथळा आणणे हा भारतीय न्याय संहितेनुसार दखलपात्र गुन्हा आहे.",
            "hi": "संविधान के अनुच्छेद 25 के तहत शांतिपूर्ण प्रार्थना का मौलिक अधिकार है और इसमें व्यवधान डालना बीएनएस के तहत संज्ञेय अपराध है।"
        },
        "simpler_words": {
            "en": "In simple terms: everyone has the constitutional right to peaceful worship. If anyone threatens or disrupts a gathering, police are required to register a Zero FIR immediately.",
            "mr": "सोप्या शब्दांत: प्रत्येकाला शांततेने प्रार्थना करण्याचा घटनात्मक हक्क आहे. कोणी अडथळा आणल्यास पोलिसांना तात्काळ गुन्हा नोंदवणे बंधनकारक आहे.",
            "hi": "सरल शब्दों में: प्रत्येक नागरिक को शांतिपूर्ण प्रार्थना का हक है। व्यवधान होने पर पुलिस तुरंत एफआईआर दर्ज करने के लिए बाध्य है।"
        },
        "recap": {
            "en": "Document event permissions and any audio/video recordings of threats, and demand a Zero FIR under BNSS Section 173.",
            "mr": "कार्यक्रमाची परवानगी व घटनेचे व्हिडिओ सुरक्षित ठेवा आणि पोलिसांकडून कलम १७३ अन्वये तात्काळ कारवाईची मागणी करा.",
            "hi": "आयोजन की अनुमति और वीडियो साक्ष्य सुरक्षित रखें और बीएनएसएस की धारा 173 के तहत तत्काल एफआईआर की मांग करें।"
        },
        "urgent_helpline": "112 / 15100",
        "action_authority": "Superintendent of Police / Jurisdictional Police Station"
    },
    "GENERAL_CITIZEN_AID": {
        "improper_conduct": {
            "en": "Denying access to justice, fair hearing, or public statutory rights guaranteed under constitutional and administrative remedies.",
            "mr": "कायदेशीर संरक्षणापासून किंवा न्यायापासून वंचित ठेवणे अथवा शासकीय प्रक्रियेमध्ये अन्याय होणे.",
            "hi": "न्याय तक पहुंच, निष्पक्ष सुनवाई या प्रशासनिक अधिकारों से वंचित किया जाना।"
        },
        "why_applicable": {
            "en": "Legal Services Authorities Act, 1987 Section 12 provides 100% free legal representation to eligible citizens across all civil and criminal forums.",
            "mr": "विधी सेवा प्राधिकरण कायदा, १९८७ च्या कलम १२ नुसार गरजू नागरिकांना सर्व न्यायालयांत मोफत वकील मिळण्याचा अधिकार आहे.",
            "hi": "विधिक सेवा प्राधिकरण अधिनियम, 1987 की धारा 12 के तहत पात्र नागरिकों को सभी अदालतों में पूर्णतः मुफ्त वकील पाने का हक है।"
        },
        "simpler_words": {
            "en": "In simple terms: poverty or lack of money is never a barrier to legal help in India. You have the right to a free government-appointed lawyer through NALSA and DLSA. Call 15100.",
            "mr": "सोप्या शब्दांत: भारतात पैशांअभावी न्याय थांबत नाही. विधी सेवा प्राधिकरणातर्फे (DLSA) तुम्हाला मोफत वकील मिळण्याचा कायदेशीर अधिकार आहे. १५१०० वर फोन करा.",
            "hi": "सरल शब्दों में: पैसों की कमी न्याय में बाधा नहीं बन सकती। नालसा और डालसा के माध्यम से मुफ्त सरकारी वकील पाना आपका अधिकार है। 15100 डायल करें।"
        },
        "recap": {
            "en": "Organize your grievance documents and identity proof, and dial National Legal Aid Helpline 15100 for free assistance.",
            "mr": "आपली कागदपत्रे व ओळखपत्र सोबत ठेवा आणि मोफत मदतीसाठी राष्ट्रीय विधी सेवा हेल्पलाइन १५१०० वर संपर्क साधा.",
            "hi": "अपने दस्तावेज और पहचान पत्र तैयार रखें और मुफ्त विधिक सहायता के लिए 15100 पर संपर्क करें।"
        },
        "urgent_helpline": "15100 (NALSA/DLSA 24x7)",
        "action_authority": "District Legal Services Authority (DLSA)"
    }
}


def detect_urgency(transcript: str, category: str) -> Optional[Dict[str, Any]]:
    """Determine if account suggests immediate danger, custody, violence, or imminent loss."""
    t_lower = transcript.lower()
    is_urgent = False
    urgent_reason = ""
    helpline = "112 / 15100"

    if category in ("POLICE_CUSTODY", "DOMESTIC_VIOLENCE"):
        is_urgent = True
        urgent_reason = "Custody / Domestic Safety Safeguards Active"
        helpline = "181 / 112" if category == "DOMESTIC_VIOLENCE" else "112 / 15100"
    elif any(k in t_lower for k in URGENT_KEYWORDS):
        is_urgent = True
        urgent_reason = "Immediate threat, detention, or imminent eviction detected"
        helpline = "112 / 15100"

    if not is_urgent:
        return None

    return {
        "is_urgent": True,
        "reason": urgent_reason,
        "helpline": helpline,
        "immediate_action": "Ensure physical safety first. Do not resist violently. Call emergency helplines immediately if in danger."
    }


def build_understand_your_rights(
    category: str,
    facts: Dict[str, Any],
    transcript: str,
    lang: str = "en",
    missing: Optional[List[str]] = None,
    client_name: str = "",
    location: str = ""
) -> Dict[str, Any]:
    """Generates the full 7-part structured 'Understand Your Rights' explanation."""
    lang = lang if lang in SECTION_HEADINGS else "en"
    H = SECTION_HEADINGS[lang]
    blueprint = CATEGORY_RIGHTS_BLUEPRINT.get(category, CATEGORY_RIGHTS_BLUEPRINT["GENERAL_CITIZEN_AID"])
    missing = missing or []
    name = client_name or facts.get("client_name") or "You"
    loc = location or facts.get("incident_location") or facts.get("location") or "the stated place"
    dt = facts.get("incident_date") or "recently"
    other = facts.get("other_party") or "the other party"
    spec = facts.get("specific_details") or ""

    # 1. What I understood
    if lang == "mr":
        understood_text = f"तुम्ही दिलेल्या माहितीनुसार, {loc} येथे {dt} रोजी {other} सोबत घटना घडली. तुम्ही सांगितले की: {transcript.strip() or 'तपशील उपलब्ध नाही.'}"
        if spec:
            understood_text += f" नोंदवलेले महत्त्वाचे तपशील: {spec}."
    elif lang == "hi":
        understood_text = f"आपकी दी गई जानकारी के अनुसार, {loc} में {dt} को {other} के साथ यह घटना हुई। आपने बताया: {transcript.strip() or 'विवरण उपलब्ध नहीं है।'}"
        if spec:
            understood_text += f" मुख्य दर्ज तथ्य: {spec}."
    else:
        understood_text = f"Based on what you stated, on {dt} at {loc}, an incident occurred involving {other}. Specifically: {transcript.strip() or 'No account provided yet.'}"
        if spec:
            understood_text += f" Recorded specifics: {spec}."

    # 2. What may be wrong (Allegation vs Verified Fact)
    improper_desc = blueprint["improper_conduct"].get(lang, blueprint["improper_conduct"]["en"])
    what_may_be_wrong = {
        "heading": H["wrong"],
        "improper_conduct_description": improper_desc,
        "allegation_vs_fact_note": H["allegation_disclaimer"]
    }

    # 3. Possible Act and dhaara (from Source Register)
    reg_entry = get_source_register_entry(category)
    possible_acts = []
    for ref in reg_entry.get("references", []):
        possible_acts.append({
            "act_name": ref.get("act", ref.get("law", "")),
            "section": ref.get("law", ""),
            "source_url": ref.get("source_url", ""),
            "coverage_explanation": ref.get("remedy", ""),
            "conditions_to_check": ref.get("conditions", "Statutory provision compiled from primary sources pending qualified legal review."),
            "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"
        })

    # If no reliable references exist
    if not possible_acts:
        possible_acts.append({
            "act_name": "General Administrative Law & Natural Justice",
            "section": "Constitution of India Article 39A",
            "source_url": "https://www.india.gov.in/my-government/constitution-india",
            "coverage_explanation": "Access to free legal aid and fair administrative hearing.",
            "conditions_to_check": "No specific Act could be matched reliably from available facts. A qualified advocate must review this case.",
            "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"
        })

    # 4. Why it might apply here
    why_base = blueprint["why_applicable"].get(lang, blueprint["why_applicable"]["en"])
    clarifications = []
    if missing:
        if lang == "mr":
            clarifications.append(f"अजून काही आवश्यक माहिती निश्चित करणे बाकी आहे: ({', '.join(missing)}). ही माहिती मिळाल्यानंतरच तरतुदींची अचूकता निश्चित करता येईल.")
        elif lang == "hi":
            clarifications.append(f"अभी कुछ आवश्यक तथ्य सत्यापित होने शेष हैं: ({', '.join(missing)})। इनके मिलने पर ही विधिक स्थिति पूर्णतः स्पष्ट होगी।")
        else:
            clarifications.append(f"Certain factual conditions still require confirmation: ({', '.join(missing)}) before a conclusive legal position can be established.")

    why_it_applies = {
        "heading": H["why"],
        "connection_to_facts": why_base,
        "clarification_needed": " ".join(clarifications) if clarifications else None
    }

    # 5. What the person can do next (Ordered practical options)
    options = []
    if lang == "mr":
        options = [
            {"step": 1, "title": "१. पुरावे सुरक्षित ठेवा", "details": "घटनेचे फोटो, पावती, हजेरी पत्रक, मेसेज, कॉल्स किंवा व्हिडिओ रेकॉर्ड सुरक्षित ठेवा. कोऱ्या कागदावर स्वाक्षरी करू नका."},
            {"step": 2, "title": "२. सक्षम प्राधिकरणाकडे लेखी दाद मागा", "details": f"संबंधित विभागाकडे ({blueprint.get('action_authority', 'सक्षम अधिकारी')}) कायदेशीर तरतुदींचा हवाला देऊन लेखी अर्ज सादर करा."},
            {"step": 3, "title": "३. मोफत कायदेशीर मदत (DLSA)", "details": "राष्ट्रीय विधी सेवा प्राधिकरण (NALSA) च्या १५१०० या २४ तास मोफत हेल्पलाइनवर संपर्क करून मोफत वकील मिळवा."},
            {"step": 4, "title": "४. वकिलाचा सल्ला घ्या", "details": "दावा किंवा नोटीस पाठवण्यापूर्वी स्थानिक न्यायालयातील अधिकृत वकिलाकडून मसुदा तपासून घ्या."}
        ]
    elif lang == "hi":
        options = [
            {"step": 1, "title": "1. सबूत और रिकॉर्ड सुरक्षित रखें", "details": "घटना के फोटो, रसीद, हाजिरी कार्ड, संदेश या वीडियो सुरक्षित रखें। किसी भी खाली कागज पर दस्तखत न करें।"},
            {"step": 2, "title": "2. संबंधित प्राधिकारी को लिखित आवेदन दें", "details": f"संबंधित कार्यालय ({blueprint.get('action_authority', 'सक्षम प्राधिकारी')}) में विधिक धाराओं का उल्लेख करते हुए लिखित शिकायत दें।"},
            {"step": 3, "title": "3. मुफ्त कानूनी सहायता (नालसा/डालसा)", "details": "राष्ट्रीय विधिक सेवा प्राधिकरण के 24x7 टोल-फ्री हेल्पलाइन नंबर 15100 पर कॉल करके मुफ्त वकील प्राप्त करें।"},
            {"step": 4, "title": "4. वकील से परामर्श व सत्यापन", "details": "कोई भी कोर्ट केस या लीगल नोटिस भेजने से पहले अधिकृत वकील से ड्राफ्ट का परीक्षण करवाएं।"}
        ]
    else:
        options = [
            {"step": 1, "title": "1. Preserve Evidence", "details": "Preserve contemporaneous receipts, muster logs, photographs, audio/video, and messages. Never sign blank documents."},
            {"step": 2, "title": "2. Approach the Relevant Authority", "details": f"Submit a written representation to the competent forum ({blueprint.get('action_authority', 'Competent Authority')}) invoking applicable statutory provisions."},
            {"step": 3, "title": "3. Seek Free Legal Aid (NALSA / DLSA)", "details": "Call National Legal Aid Helpline 15100 (24x7 toll-free) for a free panel advocate under Section 12 of the Legal Services Authorities Act, 1987."},
            {"step": 4, "title": "4. Formal Legal Counsel Review", "details": "Have a qualified advocate review the facts and verify local jurisdiction and filing deadlines before filing notices or petitions."}
        ]

    what_you_can_do_next = {
        "heading": H["next"],
        "options": options,
        "filing_disclaimer": H["filing_disclaimer"]
    }

    # 6. Urgent help
    urgent_data = detect_urgency(transcript, category)
    urgent_block = None
    if urgent_data:
        helpline_str = urgent_data["helpline"]
        if lang == "mr":
            msg = f"तातडीची सूचना: तुमच्या सुरक्षिततेला तात्काळ धोका किंवा बेकायदेशीर कारवाई होत असल्यास आधी स्वतःची सुरक्षा बघा. तात्काळ मदत व मोफत वकिलासाठी {helpline_str} वर संपर्क करा."
        elif lang == "hi":
            msg = f"आपातकालीन सूचना: यदि आपकी सुरक्षा को तुरंत कोई खतरा है या अवैध हिरासत है, तो पहले अपनी जान-माल की रक्षा करें। तुरंत सहायता व मुफ्त वकील हेतु {helpline_str} पर कॉल करें।"
        else:
            msg = f"Immediate Safety Alert: If you or your family face imminent physical danger, unlawful arrest, or eviction right now, prioritize personal safety. Call {helpline_str} immediately."
        
        urgent_block = {
            "is_urgent": True,
            "heading": H["urgent"],
            "message": msg,
            "helpline": helpline_str,
            "immediate_action": urgent_data["immediate_action"]
        }

    # 7. One-minute recap
    recap_text = blueprint["recap"].get(lang, blueprint["recap"]["en"])
    one_minute_recap = {
        "heading": H["recap"],
        "recap_text": recap_text
    }

    # 8. Simpler words explanation
    simpler_text = blueprint["simpler_words"].get(lang, blueprint["simpler_words"]["en"])
    simpler_words = {
        "heading": H["simpler"],
        "explanation": simpler_text
    }

    # Generate Spoken Scripts matching the structured content
    acts_spoken_parts = []
    for pa in possible_acts[:2]:  # Short enough for listening
        acts_spoken_parts.append(f"{pa['section']}. {pa['coverage_explanation']}")
    acts_spoken_str = " ".join(acts_spoken_parts)

    urgent_spoken = urgent_block["message"] if urgent_block else ""

    if lang == "mr":
        full_rights_spoken = (
            f"{urgent_spoken + ' ' if urgent_spoken else ''}"
            f"आपले कायदेशीर हक्क समजून घ्या. {improper_desc} "
            f"कायद्यानुसार: {acts_spoken_str} "
            f"आपण पुढील पावले उचलू शकता: पुरावे जपून ठेवा, आणि मोफत सरकारी वकिलासाठी १५१०० वर संपर्क करा. "
            f"थोडक्यात: {recap_text}"
        )
    elif lang == "hi":
        full_rights_spoken = (
            f"{urgent_spoken + ' ' if urgent_spoken else ''}"
            f"अपने कानूनी अधिकार समझें। {improper_desc} "
            f"कानूनी प्रावधान: {acts_spoken_str} "
            f"आगे के कदम: साक्ष्य सुरक्षित रखें, और मुफ्त सरकारी वकील के लिए 15100 पर संपर्क करें। "
            f"संक्षेप में: {recap_text}"
        )
    else:
        full_rights_spoken = (
            f"{urgent_spoken + ' ' if urgent_spoken else ''}"
            f"Understanding your legal rights. {improper_desc} "
            f"Under applicable law: {acts_spoken_str} "
            f"Recommended steps: preserve your records, and call 15100 for free legal aid. "
            f"In recap: {recap_text}"
        )

    spoken_scripts = {
        "full_rights_spoken": full_rights_spoken.strip(),
        "recap_spoken": recap_text.strip(),
        "simplified_spoken": simpler_text.strip(),
        "urgent_spoken": urgent_spoken.strip() if urgent_spoken else None
    }

    return {
        "status": "ready",
        "category": category,
        "language": lang,
        "what_i_understood": {"heading": H["understood"], "text": understood_text},
        "what_may_be_wrong": what_may_be_wrong,
        "possible_acts": possible_acts,
        "why_it_might_apply": why_it_applies,
        "what_you_can_do_next": what_you_can_do_next,
        "urgent_help": urgent_block,
        "one_minute_recap": one_minute_recap,
        "simpler_words_explanation": simpler_words,
        "spoken_scripts": spoken_scripts,
        "shared_phone_privacy_notice": (
            "सामायिक फोन सुरक्षा सूचना: सार्वजनिक ठिकाणी किंवा सामायिक फोन वापरत असल्यास, "
            "इतरांना ऐकू जाऊ नये म्हणून इयरफोन वापरा किंवा एकांतात ऐका." if lang == "mr"
            else ("साझा फोन सुरक्षा सूचना: यदि आप किसी सार्वजनिक स्थान या साझा फोन पर हैं, "
                  "तो गोपनीयता बनाए रखने हेतु इयरफोन लगाएं या एकांत में सुनें।" if lang == "hi"
                  else "Shared Phone Privacy Notice: If you are in a public space or on a shared device, connect earphones or ensure privacy before playing audio aloud.")
        )
    }
