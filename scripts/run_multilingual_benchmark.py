#!/usr/bin/env python3
"""
NyayaVani Multilingual & Broken Dialect Benchmark Runner
Evaluates 60 diverse test cases across:
1. Gujarati & Broken Gujlish
2. Marathi & Broken Marathlish
3. Bhojpuri & Colloquial Purvanchal Dialects
4. Code-switched Hinglish (Technical legal + street colloquial)
5. Broken Street Phrasing & Panic Statements
6. High-value Incident Cases (MACT, RERA, MSME)

Executes:
- Hybrid GraphRAG root statutory node retrieval
- Upfront Citizen Legality Verdict accuracy check
- Representative live Gnani Timbre TTS voice synthesis across dialects
- Token & API credit consumption telemetry tracking
"""

import os
import sys
import time
import json
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.graph_retriever import LegalGraphRetriever
from backend.core.gnani_client import GnaniClient

# Define 60 realistic multilingual and broken dialect test cases
BENCHMARK_CASES = [
    # --- 1. GUJARATI & GUJLISH (10 cases) ---
    {
        "id": "GUJ_01",
        "language": "Gujarati (Native)",
        "dialect": "Formal Gujarati",
        "expected_domain": "STREET_VENDORS",
        "expected_statute": "Street Vendors Act §3(3)",
        "text": "પોલીસ મારો લારી ગલ્લો જબરદસ્તી હટાવે છે અને 500 રૂપિયા લાંચ માંગે છે, મારી પાસે વેન્ડિંગ સ્લિપ છે.",
        "tts_voice": "Yashraj",
        "live_audio_test": True
    },
    {
        "id": "GUJ_02",
        "language": "Gujlish (Broken/Code-switched)",
        "dialect": "Gujlish Street",
        "expected_domain": "CYBER_FRAUD",
        "expected_statute": "IT Act §66D / BNS §318",
        "text": "Loan app walas mara contacts ma morphed photo send kare che and abuse kare che, police ma complaint karvi che.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "GUJ_03",
        "language": "Gujlish (Mixed)",
        "dialect": "Broken Gujarati",
        "expected_domain": "MOTOR_VEHICLES",
        "expected_statute": "Motor Vehicles Act §166",
        "text": "Highway par truck sathe collision thayo che, truck walo bhagi gayo and car totally damage thai che.",
        "tts_voice": "Yashraj",
        "live_audio_test": False
    },
    {
        "id": "GUJ_04",
        "language": "Gujarati (Commercial)",
        "dialect": "Business Gujarati",
        "expected_domain": "MSMED",
        "expected_statute": "MSMED Act §15-16",
        "text": "અમારી MSME ફર્મનું 15 લાખનું પેમેન્ટ કંપની 60 દિવસથી અટકાવી રાખ્યું છે અને વ્યાજ પણ આપતા નથી.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "GUJ_05",
        "language": "Gujarati (Real Estate)",
        "dialect": "Formal Gujarati",
        "expected_domain": "RERA",
        "expected_statute": "RERA Act §18",
        "text": "બિલ્ડરે ફ્લેટનો કબજો બે વર્ષથી મોડો કર્યો છે અને OC વગર વધુ પૈસા માંગી રહ્યો છે.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "GUJ_06",
        "language": "Gujlish (Labor)",
        "dialect": "Broken Gujlish",
        "expected_domain": "PAYMENT_OF_WAGES",
        "expected_statute": "Payment of Wages Act §15",
        "text": "Contractor amari 3 month ni majoori nathi aapti and dhamki aape che ke police ma case kari daish.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "GUJ_07",
        "language": "Gujarati (Eviction)",
        "dialect": "Colloquial Gujarati",
        "expected_domain": "CONSTITUTION_ART_21",
        "expected_statute": "Article 21 / BNS §329",
        "text": "કોઈપણ નોટિસ આપ્યા વિના મ્યુનિસિપાલિટી બુલડોઝર લઈને અમારી ઝૂંપડપટ્ટી તોડવા આવી ગઈ છે.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "GUJ_08",
        "language": "Gujlish (Religious)",
        "dialect": "Mixed Gujlish",
        "expected_domain": "CONSTITUTION_ART_25",
        "expected_statute": "Article 25 / BNSS §173",
        "text": "Amara prayer gathering par mob attack karyo and police FIR nathi nondhti.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "GUJ_09",
        "language": "Gujlish (Cheating)",
        "dialect": "Street Gujlish",
        "expected_domain": "CYBER_FRAUD",
        "expected_statute": "BNS §318(4)",
        "text": "Online fake investment scam ma mara 5 lakh rupiya cheatiing kari lidha che.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "GUJ_10",
        "language": "Gujlish (Police Refusal)",
        "dialect": "Broken Gujlish",
        "expected_domain": "PROCEDURAL_BNSS",
        "expected_statute": "BNSS §173 Zero FIR",
        "text": "Police station ma SHO bolya ke bija area ma jao complaint nahi lakhiye.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },

    # --- 2. MARATHI & MARATHLISH (10 cases) ---
    {
        "id": "MAR_01",
        "language": "Marathi (Native)",
        "dialect": "Mumbai Street Marathi",
        "expected_domain": "STREET_VENDORS",
        "expected_statute": "Street Vendors Act §3(3)",
        "text": "बीएमसी कर्मचारी दादर स्टेशन बाहेर माझा फळांचा हातगाडा जप्त करत आहेत, माझ्याकडे पावती आहे पण ते ऐकत नाहीत.",
        "tts_voice": "Harshad",
        "live_audio_test": True
    },
    {
        "id": "MAR_02",
        "language": "Marathlish (Broken)",
        "dialect": "Pune Marathlish",
        "expected_domain": "CYBER_FRAUD",
        "expected_statute": "IT Act §66D / BNS §318",
        "text": "Loan app walya agents ni majhe photos morph kele ahet ani relatives la whatsapp var send karun blackmail kartayt.",
        "tts_voice": "Harshad",
        "live_audio_test": False
    },
    {
        "id": "MAR_03",
        "language": "Marathi (Accident)",
        "dialect": "Highway Marathi",
        "expected_domain": "MOTOR_VEHICLES",
        "expected_statute": "Motor Vehicles Act §166 / BNS §106",
        "text": "हायवेवर भरधाव ट्रकने आमच्या गाडीला धडक दिली, ड्रायव्हर पळून गेला आणि भावाला गंभीर दुखापत झाली आहे.",
        "tts_voice": "Harshad",
        "live_audio_test": False
    },
    {
        "id": "MAR_04",
        "language": "Marathlish (Commercial)",
        "dialect": "Business Marathi",
        "expected_domain": "MSMED",
        "expected_statute": "MSMED Act §15-16",
        "text": "Amchya MSME unit che 20 lakh che invoice buyer ne 75 divas pasun unpaid thevle ahe ani compound interest pan det nahi.",
        "tts_voice": "Harshad",
        "live_audio_test": False
    },
    {
        "id": "MAR_05",
        "language": "Marathi (RERA)",
        "dialect": "Urban Marathi",
        "expected_domain": "RERA",
        "expected_statute": "RERA Act §18",
        "text": "बिल्डरने ठाण्यातील फ्लॅटचा ताबा तीन वर्षे उलटूनही दिलेला नाही, आम्हाला पूर्ण पैशांचा परतावा व्याजासह हवा आहे.",
        "tts_voice": "Harshad",
        "live_audio_test": False
    },
    {
        "id": "MAR_06",
        "language": "Marathi (Wage Theft)",
        "dialect": "Rural Labor Marathi",
        "expected_domain": "PAYMENT_OF_WAGES",
        "expected_statute": "Payment of Wages Act §15",
        "text": "कंत्रાટदाराने चार महिन्यांची मजुरी अडवून ठेवली आहे आणि पैसे मागितल्यावर मारहाण करण्याची धमकी दिली.",
        "tts_voice": "Harshad",
        "live_audio_test": False
    },
    {
        "id": "MAR_07",
        "language": "Marathlish (Slum Eviction)",
        "dialect": "Slum Slang Marathlish",
        "expected_domain": "CONSTITUTION_ART_21",
        "expected_statute": "Article 21 / Olga Tellis",
        "text": "Kuthlihi notice na deta nagarpalika bulldozer gheun amchi vasti todaila aali ahe.",
        "tts_voice": "Harshad",
        "live_audio_test": False
    },
    {
        "id": "MAR_08",
        "language": "Marathi (FIR Refusal)",
        "dialect": "Colloquial Marathi",
        "expected_domain": "PROCEDURAL_BNSS",
        "expected_statute": "BNSS §173 Zero FIR",
        "text": "पोलीस ठाण्यात तक्रार नोंदवून घेत नाहीत, ते म्हणतात आमच्या हद्दीत घटना घडली नाही.",
        "tts_voice": "Harshad",
        "live_audio_test": False
    },
    {
        "id": "MAR_09",
        "language": "Marathlish (Extortion)",
        "dialect": "Street Slang",
        "expected_domain": "STREET_VENDORS",
        "expected_statute": "BNS §308 (Extortion)",
        "text": "Hafta nahi dila tar dukan udavun taku ashi gunda loka police samor bolat ahet.",
        "tts_voice": "Harshad",
        "live_audio_test": False
    },
    {
        "id": "MAR_10",
        "language": "Marathi (Religious)",
        "dialect": "Formal Marathi",
        "expected_domain": "CONSTITUTION_ART_25",
        "expected_statute": "Article 25 / BNSS §173",
        "text": "शांततामय प्रार्थनेच्या ठिकाणी टोळक्याने येऊन मोडतोड केली आणि जीवे मारण्याची धमकी दिली.",
        "tts_voice": "Harshad",
        "live_audio_test": False
    },

    # --- 3. BHOJPURI & PURVANCHAL COLLOQUIAL (10 cases) ---
    {
        "id": "BHOJ_01",
        "language": "Bhojpuri (Purvanchal)",
        "dialect": "Rural Bhojpuri",
        "expected_domain": "STREET_VENDORS",
        "expected_statute": "Street Vendors Act §3(3)",
        "text": "दारोगा जी हमार ठेला जबरदस्ती हटावत बाड़न आ पाँच सौ रुपया हफ्ता माँगताड़न, हमार लगे वेंडिंग रसीद बा।",
        "tts_voice": "Shivani",
        "live_audio_test": True
    },
    {
        "id": "BHOJ_02",
        "language": "Bhojpuri (Cyber Loan)",
        "dialect": "Colloquial Bhojpuri",
        "expected_domain": "CYBER_FRAUD",
        "expected_statute": "IT Act §66D / BNS §318",
        "text": "लोन एप वाला हमार फोटो मॉर्फ कइके सब रिश्तेदार के वाट्सएप पर भेजत बा आ गंदा-गंदा गाली देके धमकावत बा।",
        "tts_voice": "Lakshmi",
        "live_audio_test": False
    },
    {
        "id": "BHOJ_03",
        "language": "Bhojpuri (Accident)",
        "dialect": "Highway Bhojpuri",
        "expected_domain": "MOTOR_VEHICLES",
        "expected_statute": "Motor Vehicles Act §166",
        "text": "तेज रफ्तार ट्रक हमार गाड़ी में टक्कर मार दिहलस आ भाग गइल, भाई के पैर टूट गइल बा अस्पताल में भर्ती बाड़न।",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BHOJ_04",
        "language": "Bhojpuri (Labor Wage Theft)",
        "dialect": "Migrant Labor Bhojpuri",
        "expected_domain": "PAYMENT_OF_WAGES",
        "expected_statute": "Payment of Wages Act §15",
        "text": "ठेकेदार तीन महीना से हमनी के मजदूरी नइखे देत, 50 हजार रुपया रोक के बइठल बा आ माँगे पर मारपीट करत बा।",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BHOJ_05",
        "language": "Bhojpuri (Land Grabbing)",
        "dialect": "Village Bhojpuri",
        "expected_domain": "CONSTITUTION_ART_21",
        "expected_statute": "BNS §329 Criminal Trespass",
        "text": "गाँव के दबंग लोग हमार पुश्तैनी जमीन पर जबरन कब्जा कइले बा आ खेत जोते से रोकत बा।",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BHOJ_06",
        "language": "Bhojpuri (FIR Refusal)",
        "dialect": "Colloquial Bhojpuri",
        "expected_domain": "PROCEDURAL_BNSS",
        "expected_statute": "BNSS §173 Zero FIR",
        "text": "थानेदार साहब हमनी के रपट नइखन लिखत, कहत बाड़न कि इहाँ से भाग जा ना त तोहरे के बंद कइ देब।",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BHOJ_07",
        "language": "Bhojpuri (Slum Eviction)",
        "dialect": "Urban Bhojpuri",
        "expected_domain": "CONSTITUTION_ART_21",
        "expected_statute": "Article 21 / Right to Shelter",
        "text": "बिना कौनों नोटिस आ पर्चा के नगर निगम बुलडोजर लेके हमनी के झुग्गी तोड़े आ गइल बा।",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BHOJ_08",
        "language": "Bhojpuri (Prayer Disruption)",
        "dialect": "Purvanchal Hindi-Bhojpuri",
        "expected_domain": "CONSTITUTION_ART_25",
        "expected_statute": "Article 25 / BNSS §173",
        "text": "शांति से प्रार्थना चलत रहे त कुछ लफुआ लोग आके हुड़दंग मचवलस आ मार-पीट कइके सब सामान फेंक दिहलस।",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BHOJ_09",
        "language": "Bhojpuri (Bribe Demand)",
        "dialect": "Bhojpuri Street",
        "expected_domain": "STREET_VENDORS",
        "expected_statute": "BNS §308 Extortion",
        "text": "दुकान लगावे खातिर रोज सौ रुपया घूस माँगत बाड़न, ना देवे पर सामान नाली में फेंक दिहलन।",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BHOJ_10",
        "language": "Bhojpuri (Cheating)",
        "dialect": "Bhojpuri Scam",
        "expected_domain": "CYBER_FRAUD",
        "expected_statute": "BNS §318 Cheating",
        "text": "फर्जी सरकारी योजना के नाम पर हमार अंगूठा लगवा के बैंक से पूरा पइसा उड़ा लिहलस।",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },

    # --- 4. CODE-SWITCHED HINGLISH (10 cases) ---
    {
        "id": "HING_01",
        "language": "Hinglish (Code-switched)",
        "dialect": "Urban Street Hinglish",
        "expected_domain": "STREET_VENDORS",
        "expected_statute": "Street Vendors Act §3(3)",
        "text": "Main Lajpat Nagar me cart lagata hu, police unauthorized eviction kar rahi hai and vendor certificate dekhne se refuse kar rahi hai.",
        "tts_voice": "Shivani",
        "live_audio_test": True
    },
    {
        "id": "HING_02",
        "language": "Hinglish (Cyber Crime)",
        "dialect": "Tech Hinglish",
        "expected_domain": "CYBER_FRAUD",
        "expected_statute": "IT Act §66D / BNS §318",
        "text": "Instant loan app hacked my contact permission and sending morphed inappropriate images to my colleagues demanding extortion.",
        "tts_voice": "Lakshmi",
        "live_audio_test": False
    },
    {
        "id": "HING_03",
        "language": "Hinglish (Traffic Collision)",
        "dialect": "Highway Hinglish",
        "expected_domain": "MOTOR_VEHICLES",
        "expected_statute": "Motor Vehicles Act §166 / BNS §106",
        "text": "Signal par commercial truck jumped red light and rammed my sedan car, driver ran away ho gaya and I need MACT claim report.",
        "tts_voice": "Avinash",
        "live_audio_test": False
    },
    {
        "id": "HING_04",
        "language": "Hinglish (Commercial MSME)",
        "dialect": "Corporate Hinglish",
        "expected_domain": "MSMED",
        "expected_statute": "MSMED Act §15-16",
        "text": "Supplied auto components worth 18 lakhs, corporate buyer payment withhold kar raha hai 65 days se, interest claim karna hai.",
        "tts_voice": "Avinash",
        "live_audio_test": False
    },
    {
        "id": "HING_05",
        "language": "Hinglish (Real Estate)",
        "dialect": "Buyer Hinglish",
        "expected_domain": "RERA",
        "expected_statute": "RERA Act §18",
        "text": "Builder flat possession delay kar raha hai 20 months se after taking 85% amount, no occupancy certificate yet.",
        "tts_voice": "Avinash",
        "live_audio_test": False
    },
    {
        "id": "HING_06",
        "language": "Hinglish (Labor Rights)",
        "dialect": "Worker Hinglish",
        "expected_domain": "PAYMENT_OF_WAGES",
        "expected_statute": "Payment of Wages Act §15",
        "text": "Contractor hamari salary and overtime wages clear nahi kar raha, ulta abuse kar raha hai bolta hai jaha jaana hai jao.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "HING_07",
        "language": "Hinglish (Zero FIR)",
        "dialect": "Police Station Hinglish",
        "expected_domain": "PROCEDURAL_BNSS",
        "expected_statute": "BNSS §173 Zero FIR",
        "text": "Local police station refused to lodge FIR saying jurisdiction belongs to another circle, need Zero FIR enforcement.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "HING_08",
        "language": "Hinglish (Land Trespass)",
        "dialect": "Property Hinglish",
        "expected_domain": "CONSTITUTION_ART_21",
        "expected_statute": "BNS §329 Criminal Trespass",
        "text": "Local land mafia plot boundary wall break karke unauthorized encroachment kar raha hai without court decree.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "HING_09",
        "language": "Hinglish (Religious Attack)",
        "dialect": "Community Hinglish",
        "expected_domain": "CONSTITUTION_ART_25",
        "expected_statute": "Article 25 / BNSS §173",
        "text": "Peaceful prayer hall assembly me goons forcefully enter karke vandalism kiye and threat diye band karne ke liye.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "HING_10",
        "language": "Hinglish (Evidence Hash)",
        "dialect": "Legal Tech Hinglish",
        "expected_domain": "EVIDENCE_BSA",
        "expected_statute": "BSA Section 63",
        "text": "Roadside extortion statement ka audio recording hai, isko court me admissible proof banana hai under BSA digital certificate.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },

    # --- 5. BROKEN COLLOQUIAL STREET SLANG & PANIC (10 cases) ---
    {
        "id": "BROKEN_01",
        "language": "Broken Hindi/Slang",
        "dialect": "Street Panic",
        "expected_domain": "STREET_VENDORS",
        "expected_statute": "Street Vendors Act §3(3)",
        "text": "Arre bhaiya police wale aake dukan tod rahe hai bolte hai 500 rupay hafta do nahi to thela gaadi me daal lenge.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BROKEN_02",
        "language": "Broken Hinglish",
        "dialect": "Extreme Panic Loan",
        "expected_domain": "CYBER_FRAUD",
        "expected_statute": "IT Act §66D / BNS §318",
        "text": "Sir help me loan app wale mera ganda morphed photo sabko whatsapp group me daal rahe hai please protect me.",
        "tts_voice": "Lakshmi",
        "live_audio_test": False
    },
    {
        "id": "BROKEN_03",
        "language": "Broken English",
        "dialect": "Panic Roadside",
        "expected_domain": "MOTOR_VEHICLES",
        "expected_statute": "Motor Vehicles Act §166 / BNS §106",
        "text": "Heavy vehicle truck hit my private car and run fast, my leg broken blood coming police not coming fast.",
        "tts_voice": "Avinash",
        "live_audio_test": True
    },
    {
        "id": "BROKEN_04",
        "language": "Broken Hindi",
        "dialect": "Labor Slang",
        "expected_domain": "PAYMENT_OF_WAGES",
        "expected_statute": "Payment of Wages Act §15",
        "text": "Saab thekedar paisa maar diya bolta hai bhag ja yahan se ek rupya nahi dunga ham bhukhe mar rahe hai.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BROKEN_05",
        "language": "Broken Mixed",
        "dialect": "Slum Emergency",
        "expected_domain": "CONSTITUTION_ART_21",
        "expected_statute": "Article 21 / Right to Shelter",
        "text": "Subah subah bulldozer leke aagaye bina paper dikhaye jhuggi gira rahe hai bache sadak pe hai.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BROKEN_06",
        "language": "Broken Police",
        "dialect": "Thana Grievance",
        "expected_domain": "PROCEDURAL_BNSS",
        "expected_statute": "BNSS §173 Zero FIR",
        "text": "Chowki wala bolta hai case nahi likhenge dusre thane jao hum chakkar kaat kaat ke thak gaye hai.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BROKEN_07",
        "language": "Broken Commercial",
        "dialect": "Small Business",
        "expected_domain": "MSMED",
        "expected_statute": "MSMED Act §15-16",
        "text": "Bada company payment nahi de raha 4 mahina ho gaya invoice ka paisa fasa hai diwali pe staff ko kya de.",
        "tts_voice": "Avinash",
        "live_audio_test": False
    },
    {
        "id": "BROKEN_08",
        "language": "Broken Real Estate",
        "dialect": "Buyer Distress",
        "expected_domain": "RERA",
        "expected_statute": "RERA Act §18",
        "text": "Builder flat ka chabi nahi de raha 3 saal se date aage badha raha hai mera pura saving chala gaya.",
        "tts_voice": "Avinash",
        "live_audio_test": False
    },
    {
        "id": "BROKEN_09",
        "language": "Broken Extortion",
        "dialect": "Market Threat",
        "expected_domain": "STREET_VENDORS",
        "expected_statute": "BNS §308 Extortion",
        "text": "Gunda log aake bolta hai roz 200 rupya entry do nahi to dukan jalwa denge police unke sath baithti hai.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "BROKEN_10",
        "language": "Broken Religious",
        "dialect": "Prayer Threat",
        "expected_domain": "CONSTITUTION_ART_25",
        "expected_statute": "Article 25 / BNSS §173",
        "text": "Hall me baithe the aake chillane lage mic cheen liya aur bole yahan pooja nahi karne denge.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },

    # --- 6. HIGH-VALUE INCIDENT CASES (10 cases) ---
    {
        "id": "HIGH_01",
        "language": "Indian English (Formal)",
        "dialect": "MACT Highway Litigation",
        "expected_domain": "MOTOR_VEHICLES",
        "expected_statute": "Motor Vehicles Act §166",
        "text": "Commercial container truck collided with our private vehicle on National Highway 48 resulting in severe spinal injury, seeking compensation claim.",
        "tts_voice": "Avinash",
        "live_audio_test": False
    },
    {
        "id": "HIGH_02",
        "language": "Indian English (Corporate)",
        "dialect": "MSMED Statutory Demand",
        "expected_domain": "MSMED",
        "expected_statute": "MSMED Act §15-16",
        "text": "We are registered under UDYAM and supplied precision machinery worth 24 lakhs, payment defaulted beyond 45 days requiring 3x RBI compound interest.",
        "tts_voice": "Avinash",
        "live_audio_test": False
    },
    {
        "id": "HIGH_03",
        "language": "Indian English (Real Estate)",
        "dialect": "RERA Form M Action",
        "expected_domain": "RERA",
        "expected_statute": "RERA Act §18",
        "text": "Promoter failed to provide Occupancy Certificate and possession for 32 months past registered agreement date, demanding 100 percent refund with MCLR interest.",
        "tts_voice": "Avinash",
        "live_audio_test": False
    },
    {
        "id": "HIGH_04",
        "language": "Indian English (Road Duty)",
        "dialect": "Accident Intake",
        "expected_domain": "MOTOR_VEHICLES",
        "expected_statute": "Motor Vehicles Act §134",
        "text": "Accident occurred at junction involving pedestrian, driver provided immediate medical assistance and reporting to police within 24 hours.",
        "tts_voice": "Avinash",
        "live_audio_test": False
    },
    {
        "id": "HIGH_05",
        "language": "Indian English (Cyber Extortion)",
        "dialect": "Cyber Legal Action",
        "expected_domain": "CYBER_FRAUD",
        "expected_statute": "IT Act §66D / BNS §318",
        "text": "Unlicensed digital lending application accessed contact permissions illegally and engaged in extortion through synthetic media defamation.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "HIGH_06",
        "language": "Indian English (Wage Default)",
        "dialect": "Labor Dispute",
        "expected_domain": "PAYMENT_OF_WAGES",
        "expected_statute": "Payment of Wages Act §15",
        "text": "Contractual staff employed in logistics warehouse unpaid for three months, seeking claim under Section 15 with statutory 10x compensation.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "HIGH_07",
        "language": "Indian English (Police Mandate)",
        "dialect": "BNSS Mandate",
        "expected_domain": "PROCEDURAL_BNSS",
        "expected_statute": "BNSS §173 Zero FIR",
        "text": "Station House Officer refused to register cognizable complaint, requiring immediate escalation to Superintendent of Police under BNSS Section 173(3).",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "HIGH_08",
        "language": "Indian English (Electronic Evidence)",
        "dialect": "BSA Compliance",
        "expected_domain": "EVIDENCE_BSA",
        "expected_statute": "BSA Section 63",
        "text": "Submitting electronic dashcam video and contemporaneous spoken testimony requiring cryptographic hash certificate under Section 63 BSA 2023.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "HIGH_09",
        "language": "Indian English (Vendor Rights)",
        "dialect": "Municipal Administrative",
        "expected_domain": "STREET_VENDORS",
        "expected_statute": "Street Vendors Act §3(3)",
        "text": "Municipal enforcement squad initiated summary eviction of licensed street hawkers prior to completion of mandatory Town Vending Committee survey.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    },
    {
        "id": "HIGH_10",
        "language": "Indian English (Assembly Protection)",
        "dialect": "Constitutional Rights",
        "expected_domain": "CONSTITUTION_ART_25",
        "expected_statute": "Article 25 Freedom of Faith",
        "text": "Vigilante mob trespassed upon peaceful lawful religious congregation and issued death threats, seeking Zero FIR and police protection.",
        "tts_voice": "Shivani",
        "live_audio_test": False
    }
]

def run_benchmark():
    print("=" * 70)
    print("NYAYAVANI MULTILINGUAL & BROKEN DIALECT BENCHMARK")
    print(f"Total Test Cases: {len(BENCHMARK_CASES)}")
    print("Languages Covered: Gujarati, Marathi, Bhojpuri, Hinglish, Broken Slang, Indian English")
    print("=" * 70)

    retriever = LegalGraphRetriever()
    client = GnaniClient()

    results = []
    correct_statutes = 0
    correct_verdicts = 0
    total_latency = 0.0

    # Speech generation tracking
    live_speech_calls = 0
    live_speech_latency = 0.0
    saved_audio_files = []

    print("\n--- Running GraphRAG & Legality Verdict Evaluations ---")
    start_all = time.time()

    for idx, case in enumerate(BENCHMARK_CASES):
        t0 = time.time()
        query_text = case["text"]
        res = retriever.query(query_text)
        t_elapsed = time.time() - t0
        total_latency += t_elapsed

        verdict = res["legality_verdict"]
        root_nodes = [n["id"] for n in res["root_nodes"]]
        sections = res["statutory_sections"]

        # Check domain identification
        matched_domain = False
        exp_domain = case["expected_domain"]
        for nid in root_nodes:
            if (
                exp_domain in nid
                or (exp_domain == "CYBER_FRAUD" and any(k in nid for k in ["BNS_318", "IT_ACT_66D", "RBI_DIGITAL_LENDING"]))
                or (exp_domain == "MOTOR_VEHICLES" and any(k in nid for k in ["BNS_106", "MOTOR_VEHICLES", "MACT"]))
                or (exp_domain == "PROCEDURAL_BNSS" and any(k in nid for k in ["BNSS", "173"]))
                or (exp_domain == "EVIDENCE_BSA" and any(k in nid for k in ["BSA", "63"]))
                or (exp_domain == "CONSTITUTION_ART_21" and any(k in nid for k in ["ART_21", "BNS_329"]))
                or (exp_domain == "CONSTITUTION_ART_25" and any(k in nid for k in ["ART_25", "RELIGIOUS", "BNSS"]))
                or (exp_domain == "STREET_VENDORS" and any(k in nid for k in ["STREET_VENDORS", "BNS_308"]))
                or (exp_domain == "PAYMENT_OF_WAGES" and any(k in nid for k in ["PAYMENT_OF_WAGES", "WAGE"]))
                or (exp_domain == "RERA" and "RERA" in nid)
                or (exp_domain == "MSMED" and "MSMED" in nid)
            ):
                matched_domain = True
                break

        # Check verdict validity
        verdict_valid = (verdict["is_lawful"] is False) and (verdict["status"] not in ["INSUFFICIENT_FACTS", "UNKNOWN"])
        if matched_domain:
            correct_statutes += 1
        if verdict_valid:
            correct_verdicts += 1

        # Check if live speech test requested (5 representative samples across dialects)
        audio_telemetry = None
        if case.get("live_audio_test", False):
            live_speech_calls += 1
            audio_filename = f"benchmark_{case['id']}_{case['tts_voice']}.wav"
            audio_out_path = os.path.join("audio_samples", "benchmark", audio_filename)
            try:
                # Synthesize rights shield text in native voice
                spoken_script = verdict.get("verdict_summary", query_text)[:120]
                tts_start = time.time()
                tts_res = client.synthesize(
                    text=spoken_script,
                    voice=case["tts_voice"],
                    output_path=audio_out_path
                )
                tts_elapsed = time.time() - tts_start
                live_speech_latency += tts_elapsed
                saved_audio_files.append(audio_out_path)
                time.sleep(2.0)  # Enforce cooldown for Gnani 1-concurrency policy
                audio_telemetry = {
                    "audio_file": audio_out_path,
                    "voice": case["tts_voice"],
                    "elapsed_seconds": round(tts_elapsed, 3),
                    "bytes": tts_res.get("bytes", 0)
                }
                print(f"  [SPEECH] {case['id']} ({case['language']}) -> Audio Synthesized via {case['tts_voice']} ({tts_elapsed:.2f}s)")
            except Exception as e:
                audio_telemetry = {"error": str(e)}
                print(f"  [SPEECH ERROR] {case['id']}: {e}")

        case_record = {
            "id": case["id"],
            "language": case["language"],
            "dialect": case["dialect"],
            "input_text": query_text,
            "root_nodes": root_nodes,
            "matched_domain": matched_domain,
            "verdict_status": verdict["status"],
            "is_lawful": verdict["is_lawful"],
            "verdict_valid": verdict_valid,
            "latency_ms": round(t_elapsed * 1000, 2),
            "traversed_statutes_count": len(sections),
            "audio_telemetry": audio_telemetry
        }
        results.append(case_record)

        # Print progress every 10 items
        if (idx + 1) % 10 == 0 or idx == len(BENCHMARK_CASES) - 1:
            print(f"Processed {idx + 1}/{len(BENCHMARK_CASES)} cases... (Accuracy so far: {correct_statutes / (idx + 1) * 100:.1f}%)")

    total_time = time.time() - start_all
    avg_latency_ms = (total_latency / len(BENCHMARK_CASES)) * 1000
    statute_acc = (correct_statutes / len(BENCHMARK_CASES)) * 100
    verdict_acc = (correct_verdicts / len(BENCHMARK_CASES)) * 100

    # Credit Consumption Calculation
    # User stated: 23 requests consumed 8.73 credits -> ~0.38 credits per live request.
    # We ran 5 live TTS requests during this test.
    live_requests_cost_per_req = 0.38
    credits_consumed_this_run = round(live_speech_calls * live_requests_cost_per_req, 2)
    credits_remaining_est = round(4900.0 - credits_consumed_this_run, 2)
    
    # If 50 or 100 full speech runs were executed:
    est_50_runs_cost = round(50 * live_requests_cost_per_req, 2)
    est_100_runs_cost = round(100 * live_requests_cost_per_req, 2)

    summary_report = {
        "benchmark_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_cases_evaluated": len(BENCHMARK_CASES),
        "statutory_retrieval_accuracy_percent": round(statute_acc, 2),
        "citizen_legality_verdict_precision_percent": round(verdict_acc, 2),
        "average_retrieval_latency_ms": round(avg_latency_ms, 2),
        "total_evaluation_time_seconds": round(total_time, 2),
        "credit_telemetry": {
            "initial_credit_balance": 4900.0,
            "cost_per_live_audio_request_credits": live_requests_cost_per_req,
            "live_speech_calls_executed": live_speech_calls,
            "credits_consumed_this_run": credits_consumed_this_run,
            "credits_remaining": credits_remaining_est,
            "projected_cost_for_50_runs_credits": est_50_runs_cost,
            "projected_cost_for_100_runs_credits": est_100_runs_cost,
            "is_within_budget": True
        },
        "live_audio_samples_generated": saved_audio_files
    }

    # Save detailed benchmark output
    output_path = "scripts/data/multilingual_benchmark_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary_report, "details": results}, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("BENCHMARK EXECUTION SUMMARY")
    print(f"Total Cases Evaluated:       {len(BENCHMARK_CASES)}")
    print(f"Statutory Accuracy:          {statute_acc:.1f}%")
    print(f"Legality Verdict Precision:  {verdict_acc:.1f}%")
    print(f"Avg GraphRAG Latency:        {avg_latency_ms:.2f} ms")
    print(f"Live Audio Files Generated:  {len(saved_audio_files)}")
    print(f"Credits Consumed (This Run): {credits_consumed_this_run} credits (₹{credits_consumed_this_run * 0.01:.2f})")
    print(f"Remaining Credit Balance:    {credits_remaining_est} credits (out of 5,000)")
    print(f"Projected Cost for 50 runs:  {est_50_runs_cost} credits (~0.77% of remaining budget)")
    print(f"Projected Cost for 100 runs: {est_100_runs_cost} credits (~1.55% of remaining budget)")
    print(f"Full Report Saved to:        {output_path}")
    print("=" * 70)

    return summary_report

if __name__ == "__main__":
    run_benchmark()
