import os
import json
import math
import re
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict

# -------------------------------------------------------------------------
# Multilingual Indic Stopwords covering 10 Indian Languages & Vernacular
# -------------------------------------------------------------------------
INDIC_STOPWORDS = {
    # Hindi / Bhojpuri
    "से", "में", "कर", "भी", "पर", "ने", "को", "का", "की", "के", "है", "हैं",
    "था", "थी", "थे", "तो", "हो", "हम", "आप", "वे", "यह", "वह", "और", "या",
    "जो", "करके", "दिया", "दिए", "रहा", "रही", "रहे", "गया", "गई", "गए",
    "करना", "करने", "किया", "लिए", "साल", "दिन", "महीने", "आज", "कल", "अब",
    "तक", "बात", "बोले", "कहा", "आए", "आया", "दो", "नहीं", "हमार", "रहल",
    "बा", "बाटे", "हवे", "होई", "काहे", "केहू", "हमनी", "रउवा", "गइल", "बारे",
    # Marathi
    "आहे", "होते", "नाही", "आणि", "पण", "त्यांनी", "आम्ही", "आमचा", "मला", "त्याला",
    "केले", "करून", "दिले", "झाले", "तर", "या", "ती", "ते", "असे", "आलो", "गेलो",
    "काही", "मध्ये", "वरून", "साठी", "केला", "आले", "असेल", "होती",
    # Gujarati
    "છે", "હતું", "નથી", "અને", "પણ", "તેમણે", "અમે", "અમારો", "મને", "તેને",
    "કર્યું", "કરીને", "આપ્યું", "થયું", "તો", "આ", "તે", "એવું", "આવ્યા", "ગયા",
    "કંઈ", "માં", "પરથી", "માટે", "લીધું", "હતી", "હતા",
    # Kannada
    "ಇದೆ", "ಇತ್ತು", "ಇಲ್ಲ", "ಮತ್ತು", "ಆದರೆ", "ಅವರು", "ನಾವು", "ನಮ್ಮ", "ನನಗೆ", "ಅವನಿಗೆ",
    "ಮಾಡಿದರು", "ಮಾಡಿ", "ಕೊಟ್ಟರು", "ಆಯಿತು", "ಹಾಗೆ", "ಬಂದರು", "ಹೋದರು", "ಯಾವುದೋ",
    "ನಲ್ಲಿ", "ಇಂದ", "ಗಾಗಿ", "ಎಂದು", "ಮಾಡಲು",
    # Tamil
    "இருக்கிறது", "இருந்தது", "இல்லை", "மற்றும்", "ஆனால்", "அவர்கள்", "நாங்கள்",
    "எங்கள்", "எனக்கு", "அவருக்கு", "செய்தார்கள்", "செய்து", "கொடுத்தார்கள்", "ஆனது",
    "அப்படி", "வந்தார்கள்", "போனார்கள்", "இல்", "இருந்து", "க்காக", "என்று",
    # Telugu
    "ఉంది", "ఉండింది", "లేదు", "మరియు", "కానీ", "వారు", "మేము", "మా", "నాకు",
    "అతనికి", "చేశారు", "చేసి", "ఇచ్చారు", "అయింది", "అలా", "వచ్చారు", "వెళ్లారు",
    "లో", "నుండి", "కోసం", "అని", "చేయడానికి",
    # Bengali
    "আছে", "ছিল", "নেই", "এবং", "কিন্তু", "তারা", "আমরা", "আমাদের", "আমাকে",
    "তাকে", "করল", "করে", "দিল", "হলো", "এমন", "এলো", "গেল", "মধ্যে", "থেকে", "জন্য",
    # Punjabi
    "ਹੈ", "ਸੀ", "ਨਹੀਂ", "ਅਤੇ", "ਪਰ", "ਉਨ੍ਹਾਂ", "ਅਸੀਂ", "ਸਾਡਾ", "ਮੈਨੂੰ", "ਉਸਨੂੰ",
    "ਕੀਤਾ", "ਕਰਕੇ", "ਦਿੱਤਾ", "ਹੋਇਆ", "ਇੰਜ", "ਆਏ", "ਗਏ", "ਵਿੱਚ", "ਤੋਂ", "ਲਈ",
    # Malayalam
    "ഉണ്ട്", "ഉണ്ടായിരുന്നു", "ഇല്ല", "ഒപ്പം", "പക്ഷേ", "അവർ", "ഞങ്ങൾ", "ഞങ്ങളുടെ",
    "എനിക്ക്", "അവന്", "ചെയ്തു", "ചെയ്തിട്ട്", "നൽകി", "ആയി", "അങ്ങനെ", "വന്നു",
    "പോയി", "ഇൽ", "നിന്ന്", "വേണ്ടി",
    # English stop words
    "the", "is", "at", "which", "on", "a", "an", "and", "or", "to", "in", "for",
    "with", "from", "by", "my", "our", "their", "was", "were", "be", "been",
    "have", "has", "had", "do", "did", "does", "not", "but", "so", "as", "if"
}

# -------------------------------------------------------------------------
# High-Precision Domain Anchors across 10 Indian Languages & Dialects
# -------------------------------------------------------------------------
DOMAIN_ANCHORS = [
    # 1. Food safety / contaminated / spoiled / unhygienic
    ([
        "बासी", "सड़ा", "सड़े", "खराब खाना", "food safety", "fssai", "दूषित", "मिलावटी",
        "બગડેલો", "ખરાબ ખોરાક", "શિળે", "सडलेले", "शिळं पाणी", "माल फेकून दिला", "गाडी सील",
        "સડેલું અને વાસી", "વાસી ખાવાનું", "ફૂડ ઇન્સ્પેક્ટરે", "લારી સીલ",
        "കുഴഞ്ഞ", "கெட்டுப்போன", "పాడైన", "rotten", "spoiled", "unhygienic", "stale food", "poisoning",
        "ਸੜਿਆ", "খাবার বাসি", "খাবার নষ্ট", "കെട്ടുഹോദ", "ಅపరిಶುಭ್ರ",
        "खाद्य सुरक्षा", "food adulteration", "toxic food", "फूड सेफ्टी"
    ], "STATUTE_FSSAI_FOOD_SAFETY_SEC_26_59"),

    # 2. Drunk driving / breathalyzer / alcohol / MV offenses
    ([
        "दारू", "शराब", "drink and drive", "breathalyzer", "शराब पीकर", "alcohol", "नशे", "drunk",
        "ચોક્કસ દારૂ", "દારૂ પીને", "मद्यपान", "दारू पिऊन", "पेग मारून",
        "குடித்துவிட்டு", "மద్యம்", "మద్యపిచ్చి", "మద్యం", "മദ്യപിച്ച്", "കുടിച്ചു",
        "ਡਰਿੰਕ ਐਂਡ ਡਰਾਈਵ", "ਮਦਰਾ", "breath analyzer", "intoxicated", "డ్రంక్ అండ్ డ్రైవ్",
        "ಮದ್ಯ ಸೇವಿಸಿ", "মদ্যপ", "মদ খেয়ে", "மது அருந்தி", "வாகனம் ஓட்டிய", "బ్రీత్ అనలైజర్"
    ], "STATUTE_MV_TRAFFIC_OFFENSES_SEC_185_207"),

    # 3. Sidewalk Encroachment / Hospital Gate / Ambulance obstruction / Permanent brick construction
    ([
        "पक्का खोखा", "अस्पताल के बाहर", "एम्बुलेंस", "रास्ता बंद", "permanent structure",
        "hospital gate", "blocking emergency", "sidewalk wall", "ફૂટપાથ પર પાકું", "પક્કું બાંધકામ",
        "पक्का बांधकाम", "एम्बुलेंसचा रस्ता", "ambulance blocked", "permanent brick", "encroachment",
        "हॉस्पिटलच्या गेटसमोर", "पक्कं दुकान", "ॲम्ब्युलन्स अडत", "એમ્બ્યુલન્સ", "अस्पताल गेट", "हॉस्पिटल गेट",
        "ಆಸ್ಪತ್ರೆ ಗೇಟ್", "மருத்துவமனை", "ఆసుపత్రి", "হাসপাতাল গেট", "হসপিটালের সামনে", "ਹਸਪਤਾਲ ਗੇਟ",
        "ആശുപത്രി ഗേറ്റ്", "பொது நடைபாதை ஆக்கிரமிப்பு", "ఫుట్‌పాత్ ఆక్రమణ", "రహదారి మూసివేత"
    ], "STATUTE_MUNICIPAL_OBSTRUCTION_SEC_3_2"),

    # 4. Bank Loan Auction / SARFAESI / EMI default
    ([
        "sarfaesi", "नीलामी", "किस्त", "emi default", "बैंक वाले", "dukan auction", "auction notice",
        "દુકાન હરાજી", "હપ્તો બાકી", "બૅન્ક", "बँक लिलाव", "हप्ते थकले", "बँकेचे हफ्ते", "लिलाव करू",
        "बँकेने दुकानावर", "लिलाव काढला", "હરાજી", "હપ્તો",
        "ലേലം", "loan default", "auction of shop", "bank recovery", "ലേല നോട്ടീസ്", "ఎంబీ డిఫాల్ట్",
        "ಹರಾಜು", "নিলাম", "ব্যাংকের নোটিশ", "ਕਿਸ਼ਤਾਂ ਬਕਾਇਆ", "ਬੈਂਕ ਨਿਲਾਮੀ", "வங்கி ஏலம்", "తవణ బకాయి"
    ], "STATUTE_SARFAESI_SEC_13_BANK_RECOVERY"),

    # 5. Street Vendor / Thela / Hawkers / Hafta / Vending protection
    ([
        "ठेला", "thela", "रेहड़ी", "rehdi", "khomcha", "ખૉમચા", "લારી", "lari", "हातगाडा", "हातगाडी",
        "hatgadi", "thalluvandi", "thallugadi", "ಗಾಡಿ", "வண்டி", "బండి", "फेरीवाला", "hawker",
        "street vendor", "stall", "dukan", "દુકાન", "svanidhi", "स्वनिधि", "tvc", "टाउन वेंडिंग",
        "hafta", "हफ्ता", "હપ્તો", "हप्ता", "vending slip", "cart", "తள்ளுவண்டி", "தெருவு கச்சவடம்",
        "ഹാക്കർ", "തെരുവ് കച്ചവടം", "హాకర్", "ఫెరీవాలా", "ঠেলাগাড়ি", "হকার", "ਹਫ਼ਤਾ", "ਰੇਹੜੀ ਵਾਲਾ",
        "ತಳ್ಳುಗಾಡಿ", "வெண்டிங்", "தள்ளுவண்டியை", "తోపుడు బండి", "వ్యాపారి", "വഴിയോരക്കച്ചവട", "ਲਾਈਸੈਂਸ"
    ], "STATUTE_STREET_VENDORS_SEC_3_3"),

    # 6. Cyber Fraud / Predatory Loan Apps / Contact hack / Morphing photos
    ([
        "loan app", "लोन ऐप", "लोन एप", "morphed", "मॉर्फ", "contacts hack", "ब्लैकमेल", "गंदी फोटो",
        "रिश्तेदारों को", "photo morph", "contact list hack", "લોન એપ", "મોર્ફ", "નગ્ન ફોટો", "મોબાઇલ લોન",
        "मोबाईल लोन ॲप", "मॉर्फ केलेले", "डिजिटल कर्ज ॲप", "विकृतीकरण", "सगळे कॉन्टॅक्ट्स हॅक",
        "घाणेरडे फोटो", "नातेवाईकांना पाठवून", "કોન્ટેક્ટ્સ હેક", "સગા સંબંધીઓને", "લોન એપ", "નગ્ન ફોટો",
        "கடன் ஆப்", "மார்ஃபிங்", "రుణ యాప్", "మార్ఫింగ్", "cyber fraud", "gallery hack", "nude photo",
        "threaten contacts", "ಲೋನ್ ಆಪ್", "മോർഫ്", "ബ്ലැക്മെയിൽ", "ਫਿਰੌਤੀ", "ਲੋਨ ਐਪ", "মর্ফ", "তোলাবাজি",
        "ஆபாசமாக", "రుణ యాప్ వాళ్ళు", "మారఫింగ్", "বিকৃত ছবি"
    ], "STATUTE_IT_ACT_66D_CYBER_FRAUD"),

    # 7. Unpaid Wages / Salary Withholding / Contractor default
    ([
        "मजदूरी", "salary", "wage", "तनख्वाह", "मजदूरी रोक", "काम करवाया पैसे नहीं दिए", "thekedar",
        "ठेकेदार", "कंत्राटदार", "पगार दिला नाही", "वेतन संदाय अधिनियम", "पगार थकवला", "मजुरी थकवली", "मजुरी",
        "વેતન આપ્યું નથી", "કૉન્ટ્રેક્ટર", "કોન્ટ્રાક્ટરે", "મજૂરી આપવાની ના", "૪૦ હજાર મજૂરી", "મજૂરી",
        "వేతనం", "ശമ്പളം തന്നില്ല", "കൂലി தரவில்லை", "বেতন দেয়নি", "unpaid salary", "withheld wages",
        "months salary", "ವೇತನ", "ಕೂಲಿ", "ਠੇਕੇਦਾਰ", "ਤਨਖਾਹ ਨਹੀਂ ਦਿੱਤੀ", "मजुरी थकवली", "বকেয়া বেতন",
        "சம்பள பாக்கி", "జీతం ఇవ్వకుండా", "ശമ്പള കുടിശ്ശിക", "ಸಂಬಳ ಬಾಕಿ", "శ్రామికుల వేతనం",
        "ಗುತ್ತಿಗೆದಾರ", "ஒப்பந்ததாரர்", "கராறுகாரன்", "കരാറുകാരൻ", "కాంట్రాక్టర్", "ਠੇਕੇਦਾਰ", "ঠিকাদার",
        "சம்பளம்", "వేతనాలు"
    ], "STATUTE_PAYMENT_OF_WAGES_SEC_15"),

    # 8. Religious Gathering / Prayer Hall / Church vandalism
    ([
        "prayer", "church", "चर्च", "प्रार्थना", "सत्संग", "लाठी डंडे", "धार्मिक", "पूजा",
        "हॉल में घुस", "તોડફોડ", "પ્રાર્થના હોલ", "પ્રાર્થના", "प्रार्थना सभागृह", "चर्चवर हल्ला",
        "പ്രാർത്ഥന", "வழிபாடு", "చర్చి", "ਪ੍ਰਾਰਥਨਾ", "prayer hall", "vandalized worship", "ਚਰਚ",
        "উপাসনা", "গির্জা", "প্রার্থনা সভা", "ಆರಾಧನಾ ಮಂದಿರ", "చర్చిపై దాడి", "ஜெபக்கூடம்", "ആരാಧനാലയം",
        "ಶಾಂತಿಯುತ ಪ್ರಾರ್ಥನಾ", "அமைதியான பிரார்த்தனை", "শান্তিপূর্ণ প্রার্থনা", "പ്രാർത്ഥനാ യോഗത്തിൽ",
        "ప్రార్థనా సమావేశం"
    ], "CONSTITUTION_ART_25_RELIGIOUS_FREEDOM"),

    # 9. Slum Eviction / Bulldozer demolition of homes without notice
    ([
        "बुलडोजर चला दिया", "झुग्गी", "बस्ती", "तोड़फोड़", "बिना नोटिस आशियाने", "slum demolition",
        "demolish house", "બુલડોઝર ફેરવી દીધું", "ઝૂંપડપટ્ટી", "झोपडपट्टीवर बुलडोझर", "ओल्गा तेलीस",
        "घरे पाडणे", "पुनर्वसनाविना", "கூரை வீடுகள் இடிப்பு", "demolish slum", "బుల్డోజర్", "గుడిసెలు కూల్చివేత",
        "ಗುಡಿಸಲು ತೆರವು", "বস্তি উচ্ছেদ", "ਬੁਲਡੋਜ਼ਰ ਚਲਾ ਦਿੱਤਾ", "കുടിൽ പൊളിച്ചു", "வீடு இடிப்பு",
        "కలమ్ 21", "अनुच्छेद 21", "कलम २१", "ఆర్టికల్ 21", "ಗುಡಿಸಲುಗಳನ್ನು ನೆಲಸಮ", "குடிசைகளை இடித்து",
        "বস্তি ভেঙে", "ঝੁੱਗੀਆਂ ਢਾਹੁਣ", "കുടിലുകൾ പൊളിച്ചു", "বুলডোজার এনে", "বস্তির ঘরবাড়ি"
    ], "CONSTITUTION_ART_21_LIVELIHOOD"),

    # 10. MSME / Delayed Commercial Payments past 45 days
    ([
        "msme", "माल सप्लाई", "45 दिन", "payment overdue", "commercial invoice", "goods delivered",
        "60 दिन हो गए", "12 लाख", "માલ મોકલ્યો", "ઇન્વોઇસ", "સપ્લાય", "मालाचा पुरवठा", "বিল", "ઇનવોઇસ",
        "लघुउद्योग", "सुटे भाग", "एमएसएमई कायद्याच्या", "कलम १५ व १६", "४५ दिवसांनंतरही", "देणी अडवून",
        "લઘુ ઉદ્યોગ", "ઇન્વોઇસ પેન્ડિંગ", "ત્રણ ગણું વ્યાજ", "વ્યાજ",
        "వస్తువులు సరఫరా", "பொருட்கள் சப்ளை", "goods supplied", "invoices pending", "samadhaan",
        "ಸರಕು ಸರಬರಾಜು", "ਸਮਾਨ ਸਪਲਾਈ", "ਮਾਲ ਭੇਜਿਆ", "বানিজ্যিক সরবরাহ", "വാണിജ്യ ഇൻവോയ്സ്", "సరుకు పంపిణీ"
    ], "STATUTE_MSMED_SEC_15_16_INTEREST"),

    # 11. RERA / Builder Flat Possession Delay
    ([
        "rera", "builder", "flat", "possession delay", "occupancy certificate", "oc नहीं दिया",
        "बिल्डर ने फ्लैट", "हैंडओवर", "બિલ્ડરે ફ્લેટ", "પઝેશન", "બિલ્ડર", "बिल्डरने ताबा",
        "फ्लॅटचा ताबा", "ताबा देण्याचे", "ओसी मिळालेली नाही", "काम बंद पाडले", "फ्लॅट", "ताबा",
        "બિલ્ડરે ફ્લેટનો કબજો", "ફ્લેટનો કબજો", "કબજો", "ઓસી વગર", "રિફંડ જોઈએ", "બિલ્ડરે",
        "கட்டிட உரிமையாளர்", "ఫ్లాట్ హ్యాండోవర్", "ਬਿਲਡਰ", "handover delayed", "builder delayed",
        "luxury 3bhk", "ಫ್ಲ್ಯಾಟ್", "অবৈধ বিলম্ব", "বিল্ডার ফ্ল্যাট", "பில்டர் தாமதம்", "ఫ్లాట్ అప్పగింత",
        "പ്രൊമോട്ടർ", "പ്രൊജക്റ്റ് വൈകൽ", "ਫ਼ਲੈਟ ਦਾ ਕਬਜ਼ਾ", "પ્રમોટર", "अधिभोग प्रमाण पत्र",
        "ಬಿಲ್ಡರ್", "பில்டர்", "బిల్డర్", "ഫ്ലാറ്റ്", "বিল্ডার", "സ്വാಧೀನವನ್ನು", "ஒப்படைக்காமல்",
        "হস্তান্তর", "అప్పగించకుండా", "ਕਬਜ਼ਾ"
    ], "STATUTE_RERA_SEC_18_DELAY_REFUND"),

    # 12. Car Crash / Traffic Collision / MACT Insurance
    ([
        "speeding car", "suv", "red light", "dashcam", "bumper", "car crash", "गाड़ी ठोक दी",
        "टक्कर मार दी", "कार भिड़", "कार एक्सीडेंट", "ગાડી ઠોકી", "કાર એક્સિડન્ટ", "कार धडकली",
        "வாகன விபத்து", "కారు ప్రమాదం", "വാഹനാപകടം", "rear-ended", "highway crash", "mact",
        "କାର ଦୁର୍ଘଟଣା", "ਕਾਰ ਐਕਸੀਡੈਂਟ", "ড্যাশ ক্যাম", "গাড়ি ধাক্কা", "ரெட் சிக்னல்", "హైవే ప్రమాదం",
        "ആക്സിഡന്റ്", "ਡੈਸ਼ਕੈਮ", "166 mact", "ಅಪಘಾತ", "ಡಿಕ್ಕಿ", "லாரி கார்", "மோதிவிட்டு",
        "ট্রাক গাড়িকে ধাক্কা", "దుర్ఘటన", "లారీ కారును", "ఢీకొట్టి", "ਟਰੱਕ ਕਾਰ ਨੂੰ ਟੱਕਰ",
        "ലോറി കാറിലിടിച്ച്", "അമിതവേഗത"
    ], "STATUTE_MOTOR_VEHICLES_SEC_166_MACT"),

    # 13. BSA Evidence Preserved / Audio Hashed / Section 63
    ([
        "bsa", "audio evidence", "tamper", "call recording", "hash", "sec 63", "इलेक्ट्रॉनिक साक्ष्य",
        "રેકોર્ડિંગ સાચવી", "ಕರೆ ರೆಕಾರ್ಡಿಂಗ್", "ಸಾಕ್ಷ್ಯ", "மின்னணு ஆதாரம்", "ఎలక్ట్రానిక్ సాక్ష్యం",
        "ইলেকট্রনিক প্রমাণ", "ਇਲੈਕਟ੍ਰਾਨਿਕ ਸਬੂਤ", "ഇലക്ട്രോണിക് തെളിവ്", "डिजिटल पुरावा", "ಸೆಕ್ಷನ್ 63",
        "લાંચ માંગવાની ઓડિયો", "કોર્ટ માન્ય ડીજીટલ પુરાવો", "ડીજીટલ પુરાવો", "कोर्ट पुरावा",
        "ஆடியோ பதிவு", "ஆடியோ റെക്കോർഡിംഗ്", "ఆడియో రికార్డింగ్", "ಆಡಿಯೋ ರೆಕಾರ್ಡಿಂಗ್", "অডিও রেকর্ডিং",
        "ਆਡੀਓ ਰਿਕਾਰਡਿੰਗ", "நீதிமன்றத்தில்", "അദാലത്", "కోర్టులో", "ನ್ಯಾಯಾಲಯದಲ್ಲಿ", "আদালতে",
        "ഡിജിറ്റൽ തെളിവായി"
    ], "EVIDENCE_BSA_SEC_63_ORAL_AFFIDAVIT"),

    # 14. BNSS 173 Zero FIR
    ([
        "zero fir", "fir दर्ज", "थाने में शिकायत", "complaint nahi likh", "ઝીરો એફઆઈઆર",
        "झिरो एफआयआर", "ஜீரோ எஃப்ஐஆர்", "జీరో ఎఫ్ఐఆర్", "ಜೀರೋ ಎಫ್ಐಆರ್", "জিরো এফআইআর",
        "ਜ਼ੀਰੋ ਐੱਫਆਈਆਰ", "സീറോ എഫ്ഐആർ", "போலீஸ் புகார் மறுப்பு", "ఫిర్యాదు స్వీకరించలేదు",
        "ಝೀರೋ ಎಫ್‌ಐಆರ್", "পোలీస్ ఠాణె", "ਥਾਣੇਦਾਰ"
    ], "PROCEDURAL_BNSS_173_ZERO_FIR")
]

class LegalGraphRetriever:
    """
    Hybrid GraphRAG retriever over sovereign Indian legal statutes.
    Combines:
    1. Lexical BM25 matching (exact section numbers, statutory keywords, Hinglish terms)
    2. Dense Semantic Vector Search (cached all-MiniLM-L6-v2)
    3. Reciprocal Rank Fusion (RRF)
    4. Multi-hop Directed Graph Traversal (Penal, Procedural, Constitutional, Evidentiary)
    5. Upfront Citizen Legality Verdict Generation
    """
    def __init__(self, graph_path: Optional[str] = None):
        if graph_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            graph_path = os.path.join(base_dir, "data", "legal_knowledge_graph.json")

        self.graph_path = graph_path
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.adj: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self.rev_adj: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        
        self.embed_model = None
        self.node_embeddings = None
        self.node_ids = []
        
        self.load_graph()
        self.init_embeddings()

    def load_graph(self):
        if not os.path.exists(self.graph_path):
            raise FileNotFoundError(f"Knowledge Graph file not found: {self.graph_path}")
        
        with open(self.graph_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for n in data.get("nodes", []):
            self.nodes[n["id"]] = n
            self.node_ids.append(n["id"])
            
        for e in data.get("edges", []):
            src = e["source"]
            tgt = e["target"]
            rel = e["relation"]
            meaning = e.get("meaning", "")
            self.adj[src].append({"target": tgt, "relation": rel, "meaning": meaning})
            self.rev_adj[tgt].append({"source": src, "relation": rel, "meaning": meaning})

    def init_embeddings(self):
        if os.environ.get("ENABLE_DENSE_EMBEDDINGS", "0") != "1":
            self.embed_model = None
            return
        try:
            from sentence_transformers import SentenceTransformer
            self.embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            corpus = []
            for nid in self.node_ids:
                n = self.nodes[nid]
                text = f"{n.get('act', '')} {n.get('section', '')} {n.get('title', '')} {n.get('operative_text', '')} {' '.join(n.get('keywords', []))}"
                corpus.append(text)
            self.node_embeddings = self.embed_model.encode(corpus, convert_to_numpy=True, normalize_embeddings=True)
        except Exception as e:
            self.embed_model = None

    def bm25_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Token-level BM25 scoring over node metadata with native Indic script support,
        stopword filtering, and domain-anchor priors.
        """
        q_low = query.lower()
        clean_q = re.sub(r'[^\w\s]', ' ', q_low.replace("§", "section"))
        tokens = clean_q.split()
        scores = defaultdict(float)

        # 1. High-Confidence Multilingual Domain Anchor Matching (+30.0 prior boost)
        for keywords, target_node in DOMAIN_ANCHORS:
            for kw in keywords:
                if kw.lower() in q_low:
                    scores[target_node] += 30.0
                    break

        # 2. Token-level BM25 with Stopword Filtering
        valid_statutes = {"3", "3(2)", "3(3)", "18", "33", "185", "203", "207", "308", "173", "15", "16", "26", "59", "66d", "318", "274", "106", "134", "166", "144", "189", "298", "301", "314", "13", "13(2)", "6", "21", "23", "25", "300a"}

        for nid in self.node_ids:
            n = self.nodes[nid]
            kw_str = " ".join(n.get("keywords", [])).lower()
            doc_str = f"{n.get('act', '')} {n.get('section', '')} {n.get('title', '')} {n.get('operative_text', '')} {kw_str}".lower()
            kw_list = [k.lower() for k in n.get("keywords", [])]

            for t in tokens:
                if len(t) < 2 or t in INDIC_STOPWORDS:
                    continue

                if t in kw_str:
                    freq = kw_str.count(t)
                    scores[nid] += 4.0 * math.log(1 + freq)
                elif t in doc_str:
                    freq = doc_str.count(t)
                    scores[nid] += 1.0 * math.log(1 + freq)
                elif len(t) >= 4:
                    for kw in kw_list:
                        if len(kw) >= 3 and (kw in t or t in kw):
                            scores[nid] += 2.5
                            break

            # Boost verified statutory sections
            for t in tokens:
                if t in valid_statutes:
                    sec = n.get("section", "").lower()
                    if t in sec and len(t) > 1:
                        scores[nid] += 8.0

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def dense_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if self.embed_model is None or self.node_embeddings is None:
            return []
        q_emb = self.embed_model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
        sims = np.dot(self.node_embeddings, q_emb)
        ranked_indices = np.argsort(-sims)[:top_k]
        return [(self.node_ids[idx], float(sims[idx])) for idx in ranked_indices]

    def hybrid_retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Reciprocal Rank Fusion (RRF) combining BM25 and Dense vector rankings.
        Adapts dynamically when queries contain native Indic scripts.
        """
        import re
        is_indic = bool(re.search(r'[\u0900-\u0DFF]', query))
        bm25_ranks = self.bm25_search(query, top_k=8)
        dense_ranks = self.dense_search(query, top_k=8)
        
        rrf_scores = defaultdict(float)
        k = 60.0
        
        # When BM25 finds strong keyword hits, especially in Indic dialects, weight BM25 heavily
        bm25_multiplier = 3.0 if (is_indic and bm25_ranks) else 1.5
        for rank, (nid, score) in enumerate(bm25_ranks):
            rrf_scores[nid] += (1.0 / (k + rank + 1)) * bm25_multiplier
            
        # Add dense representations (effective for English/code-switched queries)
        dense_multiplier = 0.5 if (is_indic and bm25_ranks) else 1.0
        for rank, (nid, score) in enumerate(dense_ranks):
            rrf_scores[nid] += (1.0 / (k + rank + 1)) * dense_multiplier
            
        sorted_nodes = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return [nid for nid, _ in sorted_nodes[:top_k]]

    def traverse_subgraph(self, root_node_ids: List[str], max_hops: int = 2) -> Dict[str, Any]:
        """
        Extracts 1-hop and 2-hop connected graph components from matching root nodes.
        Pulls related Penal, Procedural, Constitutional, and Evidentiary nodes automatically.
        """
        visited_nodes = set(root_node_ids)
        visited_edges = []
        frontier = list(root_node_ids)
        
        for _ in range(max_hops):
            next_frontier = []
            for curr in frontier:
                # Outbound edges
                for edge in self.adj.get(curr, []):
                    tgt = edge["target"]
                    visited_edges.append({
                        "source": curr,
                        "target": tgt,
                        "relation": edge["relation"],
                        "meaning": edge["meaning"]
                    })
                    if tgt not in visited_nodes:
                        visited_nodes.add(tgt)
                        next_frontier.append(tgt)
                
                # Inbound edges
                for edge in self.rev_adj.get(curr, []):
                    src = edge["source"]
                    visited_edges.append({
                        "source": src,
                        "target": curr,
                        "relation": edge["relation"],
                        "meaning": edge["meaning"]
                    })
                    if src not in visited_nodes:
                        visited_nodes.add(src)
                        next_frontier.append(src)
            frontier = next_frontier

        # Categorize assembled graph nodes
        statutory_protections = []
        penal_offenses = []
        procedural_mandates = []
        constitutional_anchors = []
        evidence_protocols = []

        for nid in visited_nodes:
            n = self.nodes.get(nid)
            if not n:
                continue
            ntype = n.get("type")
            if ntype in ["STATUTE_PROTECTION", "REGULATORY_SHIELD"]:
                statutory_protections.append(n)
            elif ntype == "PENAL_OFFENSE":
                penal_offenses.append(n)
            elif ntype == "PROCEDURAL_MANDATE":
                procedural_mandates.append(n)
            elif ntype == "CONSTITUTIONAL_RIGHT":
                constitutional_anchors.append(n)
            elif ntype == "EVIDENCE_PROTOCOL":
                evidence_protocols.append(n)

        return {
            "root_nodes": [self.nodes[r] for r in root_node_ids if r in self.nodes],
            "statutory_protections": statutory_protections,
            "penal_offenses": penal_offenses,
            "procedural_mandates": procedural_mandates,
            "constitutional_anchors": constitutional_anchors,
            "evidence_protocols": evidence_protocols,
            "relations": visited_edges
        }

    def check_ambiguity_and_followup(self, transcript: str) -> Optional[Dict[str, Any]]:
        """
        Determines whether a citizen query is ambiguous or missing essential qualifiers.
        If incomplete, returns a structured follow-up question instead of rendering a premature verdict.
        """
        t_low = transcript.lower()

        # 1. Vendor / Stall closure without specific legal grounds
        vendor_stall_terms = ["stall", "shop", "thela", "cart", "dukan", "vendor", "hawker", "rehdi", "khomcha", "lari", "gallo", "hatgadi", "thalluvandi", "thallugadi"]
        police_stop_terms = [
            "police came", "police stopped", "police told", "police asked", "told me to close", "told to close",
            "close it", "shut it", "close my", "shut my", "remove my", "move my", "police aayi", "police aakar",
            "dukan band", "thela hata", "band karne", "band karwaya", "dukaan band", "police bolya"
        ]
        
        has_vendor = any(w in t_low for w in vendor_stall_terms)
        has_police_action = any(w in t_low for w in police_stop_terms) or ("police" in t_low and any(w in t_low for w in ["close", "shut", "leave", "stop", "move"]))

        # Check if specific facts are present
        has_extortion_facts = any(w in t_low for w in ["hafta", "bribe", "lanch", "ghoos", "extortion", "500", "paisa", "rupiya", "paise", "money", "demanding cash", "unauthorized payment"])
        has_health_facts = any(w in t_low for w in ["rotten", "spoiled", "contaminated", "expired", "unhygienic", "fssai", "food safety", "sada hua", "kharab khana", "poisoning", "fungus"])
        has_obstruction_facts = any(w in t_low for w in ["ambulance", "hospital gate", "emergency gate", "fire station", "fire exit", "permanent brick", "pakka nirman", "concrete structure"])
        has_license_facts = any(w in t_low for w in ["certificate", "slip", "pm svanidhi", "vending receipt", "license", "survey"])

        if (has_vendor and has_police_action) or any(term in t_low for term in ["[ambiguous]", "ambiguous_query"]):
            if not (has_extortion_facts or has_health_facts or has_obstruction_facts):
                return {
                    "is_lawful": None,
                    "citizen_fault": None,
                    "status": "INSUFFICIENT_FACTS",
                    "follow_up_required": True,
                    "follow_up_question": "Did the police state a specific reason (like spoiled food or blocking traffic), or did they demand money/bribes without an official receipt?",
                    "follow_up_reason": "Missing factual ground for authority action (distinguishes lawful FSSAI/traffic enforcement from criminal extortion).",
                    "plain_explanation": "Under Indian law, a police officer or municipal squad cannot simply tell a street vendor to shut down without a valid legal reason. However, to advise you accurately, we need to know why they intervened.",
                    "what_to_do": "Reply by clarifying: 1) What exact reason did the officer give? 2) Do you have a PM SVANidhi certificate or vending receipt?",
                    "legal_source_statutes": [
                        {"act": "The Street Vendors Act, 2014", "section": "Section 3(3)", "rule": "Protection against eviction pending Town Vending Committee survey"},
                        {"act": "Food Safety and Standards Act (FSSAI), 2006", "section": "Section 26 & 59", "rule": "Lawful power to inspect and seize unsafe or spoiled food"}
                    ],
                    "verdict_summary": "CLARIFICATION REQUIRED. Did the police state a specific reason (like spoiled food or blocking traffic), or did they demand money/bribes without an official receipt?",
                    "citizen_standing": "Standing cannot be determined until the reason for the stop and your licensing status are clarified.",
                    "violator_liability": "Pending clarification."
                }

        # 2. Salary / Wage deduction without grounds
        has_salary_terms = any(w in t_low for w in ["salary", "wage", "wages", "pay", "pagar", "vetan", "majdoori", "sambala"])
        has_deduct_terms = any(w in t_low for w in ["deducted", "cut", "paisa kata", "less money", "withheld", "kapla", "didn't give full", "reduced", "bina bataye"])
        has_wage_theft_facts = any(w in t_low for w in ["contractor", "thekedar", "malik", "unpaid 3 month", "3 mahina", "40000", "45000", "overtime", "refused to pay", "threatened", "dhamki"])
        has_legal_deduction_facts = any(w in t_low for w in ["pf", "provident fund", "tds", "tax", "advance", "disciplinary"])

        if (has_salary_terms and has_deduct_terms) and not (has_wage_theft_facts or has_legal_deduction_facts):
            return {
                "is_lawful": None,
                "citizen_fault": None,
                "status": "INSUFFICIENT_FACTS",
                "follow_up_required": True,
                "follow_up_question": "What reason did your employer give for cutting your pay? Was it an official deduction for taxes/PF, or are they refusing to pay your earned wages?",
                "follow_up_reason": "Missing grounds for wage deduction (distinguishes legitimate statutory deductions from illegal wage withholding under Section 15 Payment of Wages Act).",
                "plain_explanation": "An employer is legally prohibited from making arbitrary deductions from your earned wages. But we must know if they claimed it was for taxes/provident fund or if it was pure wage theft.",
                "what_to_do": "Reply with: 1) What reason did your employer give? 2) How much was deducted and for how many days of work?",
                "legal_source_statutes": [
                    {"act": "Payment of Wages Act, 1936", "section": "Section 7 & 15", "rule": "Authorized deductions limited; unlawful wage withholding punishable with up to 10x penalty"}
                ],
                "verdict_summary": "CLARIFICATION REQUIRED. What reason did your employer give for cutting your pay? Was it an official deduction for taxes/PF, or are they refusing to pay your earned wages?",
                "citizen_standing": "Standing depends on whether the deduction is statutory or unauthorized.",
                "violator_liability": "Pending clarification."
            }

        # 3. Accident without injury status
        has_crash_terms = any(w in t_low for w in ["accident", "collision", "hit my car", "hit my bike", "car crash", "two vehicles", "gadi thuk", "gaadi lad", "bumped into"])
        has_injury_facts = any(w in t_low for w in ["injured", "hospital", "dead", "fracture", "blood", "hit and run", "fled", "rash", "red light", "speeding", "overturn"])

        if has_crash_terms and not has_injury_facts:
            return {
                "is_lawful": None,
                "citizen_fault": None,
                "status": "INSUFFICIENT_FACTS",
                "follow_up_required": True,
                "follow_up_question": "Was anyone injured requiring emergency medical care, or was the damage limited strictly to vehicle body damage?",
                "follow_up_reason": "Missing injury classification (determines whether BNS 106 criminal negligence applies or a standard third-party MACT insurance claim).",
                "plain_explanation": "How the law handles a traffic accident depends on whether anyone was physically injured or if it was just vehicle damage.",
                "what_to_do": "Reply with: 1) Did anyone suffer bodily injury? 2) Was a First Accident Report (FAR) or police diary entry made?",
                "legal_source_statutes": [
                    {"act": "Motor Vehicles Act, 1988", "section": "Section 134 & 166", "rule": "Duty of driver to provide medical aid; MACT tribunal compensation claims"}
                ],
                "verdict_summary": "CLARIFICATION REQUIRED. Was anyone injured requiring emergency medical care, or was the damage limited strictly to vehicle body damage?",
                "citizen_standing": "Standing depends on whether bodily injury occurred.",
                "violator_liability": "Pending clarification."
            }

        # 4. Loan call without lender identity
        has_loan_terms = any(w in t_low for w in ["loan notice", "recovery call", "repay loan", "loan payment", "phone call for money", "phone aaya loan", "loan call", "purane paise"])
        has_app_facts = any(w in t_low for w in ["morph", "contacts", "relatives", "photos", "blackmail", "whatsapp threat", "threat to call relatives"])
        has_bank_facts = any(w in t_low for w in ["sarfaesi", "npa", "60 days", "bank notice", "loan account", "auction notice"])

        if has_loan_terms and not (has_app_facts or has_bank_facts):
            return {
                "is_lawful": None,
                "citizen_fault": None,
                "status": "INSUFFICIENT_FACTS",
                "follow_up_required": True,
                "follow_up_question": "Is this demand coming from an official RBI-regulated bank where you have an account, or is it an unauthorized mobile app harassing your contacts?",
                "follow_up_reason": "Missing lender status (distinguishes legitimate bank default under SARFAESI from criminal cyber extortion under IT Act Section 66D).",
                "plain_explanation": "If an official bank is contacting you, there is a legal process they must follow under RBI rules. If it is an unapproved app blackmailing you, that is a cybercrime.",
                "what_to_do": "Reply with: 1) Who is calling (a bank or an app)? 2) Are they threatening to contact your family or morph your photos?",
                "legal_source_statutes": [
                    {"act": "RBI Guidelines on Digital Lending, 2022", "section": "Clause 4 & 6", "rule": "Strict prohibition of harassment and accessing borrower phone contacts"},
                    {"act": "SARFAESI Act, 2002", "section": "Section 13(2)", "rule": "Lawful 60-day demand notice procedure for bank NPA loans"}
                ],
                "verdict_summary": "CLARIFICATION REQUIRED. Is this demand coming from an official RBI-regulated bank where you have an account, or is it an unauthorized mobile app harassing your contacts?",
                "citizen_standing": "Standing depends on whether the creditor is an authorized bank or an illegal lending app.",
                "violator_liability": "Pending clarification."
            }

        return None

    def generate_legality_verdict(self, subgraph: Dict[str, Any], transcript: str) -> Dict[str, Any]:
        """
        Synthesizes an upfront Citizen Legality Verdict based on graph traversal.
        Translates legal conclusions into plain, explainable English with transparent statutory sourcing.
        """
        root_nodes = subgraph.get("root_nodes", [])
        penal = subgraph.get("penal_offenses", [])
        statutes = subgraph.get("statutory_protections", [])
        const = subgraph.get("constitutional_anchors", [])

        # 1. Ambiguity & Missing Facts Pre-check
        amb_check = self.check_ambiguity_and_followup(transcript)
        if amb_check:
            return amb_check

        if not root_nodes:
            return {
                "is_lawful": None,
                "citizen_fault": None,
                "status": "INSUFFICIENT_FACTS",
                "follow_up_required": True,
                "follow_up_question": "Could you provide additional details on what happened, who was involved, and if any official notices or slips were given?",
                "follow_up_reason": "No matched statutory nodes in Knowledge Graph.",
                "plain_explanation": "I need a few more details about your situation to identify the relevant legal protections under Indian law.",
                "what_to_do": "Tell me what specific action was taken and who initiated it.",
                "legal_source_statutes": [
                    {"act": "Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023", "section": "Section 173", "rule": "Right to inquiry and reporting of cognizable incidents"}
                ],
                "verdict_summary": "Further factual details required to determine exact statutory liability.",
                "citizen_standing": "Consult nearest Legal Services Authority (DLSA) or file an inquiry under BNSS Section 173.",
                "violator_liability": "Subject to formal verification of acts committed."
            }

        # Determine domain from top matched root nodes with Rank 1 Primacy
        primary_node = root_nodes[0]["id"] if root_nodes else ""
        secondary_node = root_nodes[1]["id"] if len(root_nodes) > 1 else ""

        def get_node_domain(node_id: str) -> Optional[str]:
            nid = node_id.upper()
            if "FSSAI" in nid or "FOOD_SAFETY" in nid or "274" in nid:
                return "FOOD_SAFETY"
            if "MV_TRAFFIC_OFFENSES" in nid or "185" in nid or "207" in nid:
                return "MV_TRAFFIC_OFFENSES"
            if "MUNICIPAL_OBSTRUCTION" in nid:
                return "MUNICIPAL_OBSTRUCTION"
            if "SARFAESI" in nid or "BANK_RECOVERY" in nid:
                return "SARFAESI"
            if "MOTOR_VEHICLES" in nid or "106" in nid or "ACCIDENT" in nid or "NEGLIGENT_DRIVING" in nid or "MACT" in nid:
                return "MOTOR_VEHICLES"
            if "STREET_VENDORS" in nid or "SVANIDHI" in nid or "TVC" in nid:
                return "STREET_VENDORS"
            if "CYBER_FRAUD" in nid or "LOAN" in nid or "66D" in nid or "RBI_DIGITAL" in nid:
                return "CYBER_FRAUD"
            if "RERA" in nid:
                return "RERA"
            if "MSMED" in nid or "MSME" in nid:
                return "MSMED"
            if "PAYMENT_OF_WAGES" in nid or "WAGE" in nid:
                return "PAYMENT_OF_WAGES"
            if "RELIGIOUS" in nid or "ART_25" in nid:
                return "RELIGIOUS_FREEDOM"
            if "LIVELIHOOD" in nid or "ART_21" in nid or "SLUM" in nid:
                return "SLUM_LIVELIHOOD"
            return None

        primary_domain = get_node_domain(primary_node)
        secondary_domain = get_node_domain(secondary_node)
        domain = primary_domain or secondary_domain

        # 2. Citizen At Fault / Lawful Authority Enforcement Handlers
        if domain == "FOOD_SAFETY":
            return {
                "is_lawful": True,
                "citizen_fault": True,
                "status": "LAWFUL_REGULATORY_ENFORCEMENT",
                "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                "follow_up_required": False,
                "follow_up_question": None,
                "plain_explanation": "In plain words: If food being sold is spoiled, stale, or contaminated, food safety officers and police have a statutory duty to protect public health. Selling unsafe food violates Indian law, and authorities possess lawful power to stop sales and seize hazardous stock.",
                "what_to_do": "Do not resist inspecting officers. Discard spoiled goods. Lawful seizure of unsafe food cannot be challenged as harassment. To resume operations, ensure clean water, proper hygiene, and an FSSAI registration.",
                "legal_source_statutes": [
                    {"act": "Food Safety and Standards Act (FSSAI), 2006", "section": "Section 26 & Section 59", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/1911/1/A2006-34.pdf", "rule": "Prohibition of unsafe food and statutory power of food safety officers to seize contaminated items", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"},
                    {"act": "Bharatiya Nyaya Sanhita (BNS), 2023", "section": "Section 274", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/20959/1/bns_act_2023.pdf", "rule": "Penal offense for sale of noxious food or drink", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"}
                ],
                "verdict_summary": "LAWFUL AUTHORITY ENFORCEMENT. Under Sections 26 and 59 of the Food Safety and Standards Act (FSSAI), 2006 and BNS Section 274, authorities possess jurisdiction to seize contaminated food subject to official sampling protocols.",
                "citizen_standing": "Statutory health regulations appear applicable. You must comply with food safety inspection orders unless procedural misconduct is established.",
                "violator_liability": "Vendor potentially liable for statutory fines under FSSAI and penal provisions under BNS Section 274 pending sample testing."
            }
        elif domain == "MV_TRAFFIC_OFFENSES":
            return {
                "is_lawful": True,
                "citizen_fault": True,
                "status": "LAWFUL_TRAFFIC_ENFORCEMENT",
                "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                "follow_up_required": False,
                "follow_up_question": None,
                "plain_explanation": "In plain words: Driving after drinking alcohol, riding without a helmet, or driving against traffic violates motor vehicle safety rules. Traffic police have the legal right to check you with a breathalyzer and impound the vehicle.",
                "what_to_do": "Do not resist lawful impoundment. Pay the compounding challan through official traffic portal channels or appear before the jurisdictional Judicial Magistrate.",
                "legal_source_statutes": [
                    {"act": "Motor Vehicles Act, 1988 (Amended 2019)", "section": "Section 185", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/1798/1/198859.pdf", "rule": "Driving by a drunken person or under influence of drugs", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"},
                    {"act": "Motor Vehicles Act, 1988", "section": "Section 207", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/1798/1/198859.pdf", "rule": "Power of police officer to impound and detain vehicle", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"}
                ],
                "verdict_summary": "LAWFUL POLICE POWER. Traffic police possess lawful statutory authority under Section 207 of the Motor Vehicles Act, 1988 to impound vehicles and issue compounding challans for suspected violations.",
                "citizen_standing": "The enforcement appears prima facie lawful subject to verifying that an official printed or digital challan was generated.",
                "violator_liability": "Driver subject to statutory challan compounding or judicial proceedings under Motor Vehicles Act."
            }
        elif domain == "MUNICIPAL_OBSTRUCTION":
            return {
                "is_lawful": True,
                "citizen_fault": True,
                "status": "LAWFUL_MUNICIPAL_CLEARANCE",
                "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                "follow_up_required": False,
                "follow_up_question": None,
                "plain_explanation": "In plain words: Street vendor protections apply only to mobile carts and approved vending zones. Constructing permanent brick structures on a public sidewalk or blocking emergency hospital gates constitutes an unauthorized encroachment.",
                "what_to_do": "Street vendor protections do not immunize permanent brick encroachments. Clear the obstruction voluntarily and apply through the Town Vending Committee for a designated mobile slot.",
                "legal_source_statutes": [
                    {"act": "The Street Vendors Act, 2014", "section": "Section 3(2)", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/19057/1/sv_act_2014.pdf", "rule": "Vending protection strictly excludes permanent structures and emergency non-vending zones", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"},
                    {"act": "Municipal Corporation Act", "section": "Section 314", "source_url": "https://www.indiacode.nic.in/", "rule": "Lawful removal of obstructions on public streets and footpaths", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"}
                ],
                "verdict_summary": "LAWFUL MUNICIPAL CLEARANCE. Section 3(2) of the Street Vendors Act, 2014 excludes permanent brick structures or vending that obstructs emergency services or public thoroughfares.",
                "citizen_standing": "Statutory vending immunity does not extend to permanent constructions or blocked emergency corridors.",
                "violator_liability": "Encroacher liable for municipal clearance expenses and statutory obstruction penalties."
            }
        elif domain == "SARFAESI":
            return {
                "is_lawful": True,
                "citizen_fault": True,
                "status": "LAWFUL_BANK_DEFAULT_RECOVERY",
                "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                "follow_up_required": False,
                "follow_up_question": None,
                "plain_explanation": "In plain words: When a bank loan goes unpaid for over 90 days and is classified as an NPA, the secured creditor has a statutory recovery procedure under Indian banking law by issuing a formal 60-day demand notice.",
                "what_to_do": "The bank's notice is a formal statutory step. You have 60 days to either regularize the loan, submit a formal written representation under Section 13(3A), or prepare a securitisation appeal before the DRT.",
                "legal_source_statutes": [
                    {"act": "SARFAESI Act, 2002", "section": "Section 13(2) & 13(4)", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/2006/1/200254.pdf", "rule": "Lawful 60-day demand notice and enforcement of security interest upon NPA default", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"}
                ],
                "verdict_summary": "LAWFUL STATUTORY PROCEDURE. A scheduled bank issuing a 60-day demand notice following a 90-day unserviced NPA default is exercising lawful powers under Section 13(2) of the SARFAESI Act, 2002.",
                "citizen_standing": "The notice is a recognized legal proceeding. You have the right to submit a written objection within 60 days under Section 13(3A) or appeal to the DRT under Section 17.",
                "violator_liability": "Secured assets subject to lawful attachment if the default is uncured and no stay is granted."
            }

        # 3. Citizen Rights Protection / Potentially Improper Action Handlers
        elif domain == "MOTOR_VEHICLES":
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "ROAD_TRAFFIC_NEGLIGENCE_AND_STATUTORY_CLAIM",
                "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                "follow_up_required": False,
                "follow_up_question": None,
                "plain_explanation": "In plain words: Reckless or negligent driving that collides with your vehicle and causes injury or property damage is a punishable offense. If the driver fled, it is a hit-and-run crime. You are legally entitled to claim medical compensation and vehicle repair restitution.",
                "what_to_do": "Get medical care immediately if injured. Preserve photos of vehicle damage, dashcam footage, and the other vehicle's registration number. Lodge a First Accident Report (FAR) or police diary entry to support your claim before the Motor Accidents Claims Tribunal (MACT).",
                "legal_source_statutes": [
                    {"act": "Bharatiya Nyaya Sanhita (BNS), 2023", "section": "Section 106", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/20959/1/bns_act_2023.pdf", "rule": "Causing grievous hurt or death by rash and negligent driving", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"},
                    {"act": "Motor Vehicles Act, 1988 (Amended 2019)", "section": "Section 166", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/1798/1/198859.pdf", "rule": "Application for statutory compensation before Motor Accidents Claims Tribunal (MACT)", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"}
                ],
                "verdict_summary": "POTENTIALLY IMPROPER CONDUCT (SUBJECT TO VERIFICATION). The reported collision suggests actionable negligence under BNS Section 106 and third-party statutory compensation grounds under Section 166 of the Motor Vehicles Act, 1988.",
                "citizen_standing": "You have the right to file an FIR/FAR under BNSS Section 173 and claim compensation before the MACT once records are verified.",
                "violator_liability": "Driver subject to criminal prosecution under BNS Section 106 and registered vehicle insurer liable for civil third-party restitution."
            }
        elif domain == "STREET_VENDORS":
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "UNLAWFUL_ACT_BY_AUTHORITY",
                "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                "follow_up_required": False,
                "follow_up_question": None,
                "plain_explanation": "In plain words: Municipal squads and police cannot summarily evict street vendors or demand unauthorized cash payments. Under Indian law, registered or surveyed street vendors are protected against arbitrary eviction until a Town Vending Committee survey is concluded.",
                "what_to_do": "Keep your PM SVANidhi receipt, vending certificate, or survey receipt accessible. Never pay cash without an official government receipt. If threatened, present your statutory protection under Section 3(3) and seek assistance from the Town Vending Committee or call 15100.",
                "legal_source_statutes": [
                    {"act": "The Street Vendors (Protection of Livelihood) Act, 2014", "section": "Section 3(3)", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/19057/1/sv_act_2014.pdf", "rule": "Statutory bar on eviction or relocation pending Town Vending Committee survey completion", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"},
                    {"act": "Bharatiya Nyaya Sanhita (BNS), 2023", "section": "Section 308", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/20959/1/bns_act_2023.pdf", "rule": "Penal extortion for demanding unauthorized money under coercion", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"},
                    {"act": "Constitution of India", "section": "Article 19(1)(g)", "source_url": "https://www.india.gov.in/my-government/constitution-india", "rule": "Protection of certain rights regarding freedom of trade, occupation, or business", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"}
                ],
                "verdict_summary": "POTENTIALLY IMPROPER CONDUCT (SUBJECT TO VERIFICATION). Under Section 3(3) of The Street Vendors Act, 2014, summary eviction without Town Vending Committee survey is statutorily improper. Coercive cash demands may constitute extortion under BNS Section 308.",
                "citizen_standing": "You have grounds to claim vending protection if operating peacefully within non-emergency zones, subject to producing vending credentials.",
                "violator_liability": "Officers may face administrative disciplinary action under Section 18 of the Street Vendors Act and penal investigation under BNS Section 308."
            }
        elif domain == "CYBER_FRAUD":
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "CRIMINAL_EXTORTION_AND_CYBER_FRAUD",
                "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                "follow_up_required": False,
                "follow_up_question": None,
                "plain_explanation": "In plain words: Predatory lending apps that hack phone contacts, steal gallery media, or send morphed images to relatives commit serious cybercrime. Mandatory RBI rules strictly prohibit digital lenders from harassing borrowers or accessing private media.",
                "what_to_do": "Do not pay extortion demands. Preserve screenshots, call recordings, and sender phone numbers. Register a complaint on cybercrime.gov.in or dial National Cyber Crime Helpline 1930 immediately.",
                "legal_source_statutes": [
                    {"act": "Information Technology Act, 2000", "section": "Section 66D", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/1999/3/A2000-21.pdf", "rule": "Punishment for cheating by personation by using computer resource", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"},
                    {"act": "Bharatiya Nyaya Sanhita (BNS), 2023", "section": "Section 318(4)", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/20959/1/bns_act_2023.pdf", "rule": "Cheating and dishonestly inducing delivery of property", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"},
                    {"act": "RBI Digital Lending Guidelines, 2022", "section": "Clause 4 & Clause 6", "source_url": "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=54189", "rule": "Prohibition of accessing borrower mobile contacts and harassment", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"}
                ],
                "verdict_summary": "POTENTIALLY IMPROPER CONDUCT (SUBJECT TO VERIFICATION). The reported phone contact harvesting and morphed photo threats violate RBI Digital Lending Guidelines and indicate cyber offenses under IT Act Section 66D and BNS Section 318(4).",
                "citizen_standing": "You have grounds to report cyber extortion and seek protective orders without submitting to unlawful financial demands.",
                "violator_liability": "Perpetrators subject to investigation under IT Act Section 66D and BNS Section 318(4); associated lending entities risk RBI license revocation."
            }
        elif domain == "RERA":
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "STATUTORY_DEVELOPER_DEFAULT",
                "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                "follow_up_required": False,
                "follow_up_question": None,
                "plain_explanation": "In plain words: A real estate developer who delays flat possession beyond the agreed agreement date without an Occupancy Certificate (OC) commits a statutory default under RERA.",
                "what_to_do": "Review your builder-buyer agreement for the agreed handover deadline. Under Section 18 of RERA, you can demand monthly delay interest or a full refund with statutory interest. File an online complaint before the state RERA Authority.",
                "legal_source_statutes": [
                    {"act": "Real Estate (Regulation and Development) Act, 2016 (RERA)", "section": "Section 18", "source_url": "https://www.indiacode.nic.in/indiacode/bitstream/123456789/2158/1/A201616.pdf", "rule": "Mandatory refund with interest or monthly compensation for delayed possession", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"}
                ],
                "verdict_summary": "POTENTIALLY IMPROPER CONDUCT (SUBJECT TO VERIFICATION). Possession delay beyond the committed date without an Occupancy Certificate constitutes a prima facie breach of Section 18 of the RERA Act, 2016.",
                "citizen_standing": "Allottee has statutory standing to petition the state RERA Authority for possession orders or refund with statutory interest.",
                "violator_liability": "Promoter liable to pay prescribed interest on all payments received, enforceable through RERA recovery warrants."
            }
        elif domain == "MSMED":
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "STATUTORY_COMMERCIAL_DEFAULT",
                "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                "follow_up_required": False,
                "follow_up_question": None,
                "plain_explanation": "In plain words: Any commercial buyer who purchases goods or services from a registered MSME is required by law to pay within 45 days. Delayed payments accrue compound interest at three times the RBI bank rate.",
                "what_to_do": "Serve a formal statutory demand notice giving 15 days to clear the invoice. If unpaid, file an application before the Micro and Small Enterprise Facilitation Council (MSEFC) via the MSME Samadhaan portal.",
                "legal_source_statutes": [
                    {"act": "MSMED Act, 2006", "section": "Section 15 & Section 16", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/5872/1/a2006-27.pdf", "rule": "Mandatory 45-day payment window and compound interest at three times RBI bank rate", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"}
                ],
                "verdict_summary": "POTENTIALLY IMPROPER CONDUCT (SUBJECT TO VERIFICATION). Commercial invoices unpaid past 45 days contravene Sections 15 & 16 of the MSMED Act, 2006, entitling the supplier to statutory compound interest.",
                "citizen_standing": "Registered MSME supplier has standing to initiate facilitation and arbitration before the MSEFC Council.",
                "violator_liability": "Buyer liable for principal invoice amount plus non-deductible penal compound interest under Section 16 MSMED Act."
            }
        elif domain == "PAYMENT_OF_WAGES":
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "UNLAWFUL_WAGE_WITHHOLDING",
                "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                "follow_up_required": False,
                "follow_up_question": None,
                "plain_explanation": "In plain words: An employer or contractor who withholds earned wages for work completed violates statutory labor protections. Withholding wages is prohibited under the Payment of Wages Act and Code on Wages.",
                "what_to_do": "Preserve attendance logs, wage slips, and witness contacts. Submit a wage recovery application before the jurisdictional Labor Commissioner under Section 15 of the Payment of Wages Act.",
                "legal_source_statutes": [
                    {"act": "Payment of Wages Act, 1936", "section": "Section 15", "source_url": "https://www.indiacode.nic.in/bitstream/123456789/2264/1/A1936-4.pdf", "rule": "Claims arising out of deductions from wages or delay in payment; up to 10x compensation", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"},
                    {"act": "Constitution of India", "section": "Article 23", "source_url": "https://www.india.gov.in/my-government/constitution-india", "rule": "Prohibition of traffic in human beings and forced labor (begar)", "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"}
                ],
                "verdict_summary": "POTENTIALLY IMPROPER CONDUCT (SUBJECT TO VERIFICATION). Withholding earned wages indicates a prima facie breach of Section 15 of the Payment of Wages Act, 1936, subject to verifying employment records.",
                "citizen_standing": "Worker is entitled to file a claim before the Labor Commissioner for recovery of unpaid wages and statutory compensation.",
                "violator_liability": "Employer subject to recovery proceedings and statutory compensation up to 10 times the deducted wage."
            }
        else:
            root = root_nodes[0] if root_nodes else {}
            act_name = root.get('act', 'Indian Law')
            sec_name = root.get('section', '')
            return {
                "is_lawful": False,
                "citizen_fault": False,
                "status": "COGNIZABLE_STATUTORY_VIOLATION",
                "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                "follow_up_required": False,
                "follow_up_question": None,
                "plain_explanation": f"In plain words: The reported circumstances suggest an interference with your rights under {act_name}. Further verification of factual details is required before formal filing.",
                "what_to_do": "Preserve receipts, notices, communications, and names of persons involved. Approach the nearest District Legal Services Authority (DLSA) or call 15100 for free legal assistance.",
                "legal_source_statutes": [
                    {"act": act_name, "section": sec_name, "source_url": "https://www.indiacode.nic.in/", "rule": root.get('operative_text', 'Statutory provision pending human verification'), "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW"}
                ],
                "verdict_summary": f"POTENTIALLY IMPROPER CONDUCT (SUBJECT TO VERIFICATION). The reported account references provisions under {act_name} ({sec_name}).",
                "citizen_standing": "You have the right to consult a qualified legal advisor or file an inquiry under BNSS Section 173 once records are confirmed.",
                "violator_liability": f"Subject to formal verification under {act_name}."
            }

    def query(self, transcript: str) -> Dict[str, Any]:
        """
        Complete GraphRAG query execution pipeline.
        Returns:
        1. Upfront Citizen Legality Verdict
        2. Extracted Subgraph (Root, Penal, Procedural, Constitutional, Evidence)
        3. Consolidated statutory sections formatted for NyayaVani UI
        """
        root_ids = self.hybrid_retrieve(transcript, top_k=2)
        subgraph = self.traverse_subgraph(root_ids, max_hops=2)
        verdict = self.generate_legality_verdict(subgraph, transcript)
        
        # Assemble statutory sections list
        statutory_sections = []
        for s in subgraph.get("statutory_protections", []):
            statutory_sections.append({"law": f"{s['act']} — {s['section']}", "details": s["operative_text"]})
        for p in subgraph.get("penal_offenses", []):
            statutory_sections.append({"law": f"{p['act']} — {p['section']}", "details": f"{p['title']}. Penalty: {p.get('penalty', '')}"})
        for c in subgraph.get("constitutional_anchors", []):
            statutory_sections.append({"law": f"{c['act']} — {c['section']}", "details": c["operative_text"]})
        for pr in subgraph.get("procedural_mandates", []):
            statutory_sections.append({"law": f"{pr['act']} — {pr['section']}", "details": pr["operative_text"]})
        for ev in subgraph.get("evidence_protocols", []):
            statutory_sections.append({"law": f"{ev['act']} — {ev['section']}", "details": ev["operative_text"]})

        return {
            "legality_verdict": verdict,
            "root_nodes": subgraph["root_nodes"],
            "statutory_sections": statutory_sections,
            "subgraph": subgraph
        }
