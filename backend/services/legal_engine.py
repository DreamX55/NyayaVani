# -*- coding: utf-8 -*-

import os

import hashlib

import json

import re

from datetime import datetime, timezone

from typing import Dict, Any, List, Optional



from backend.services.source_register import (
    REGISTER_VERSION,
    REVIEWER_METADATA,
    get_source_register_entry
)
from backend.services.graph_retriever import LegalGraphRetriever
from backend.services.geo_service import GeoLanguageService





# Only show provisions verified against current primary sources.

POTENTIAL_LEGAL_REFERENCES = {

    "WAGE_THEFT": [("Code on Wages, 2019 — sections 17 and 45", "https://www.indiacode.nic.in/bitstream/123456789/15793/1/aA2019-29.pdf")],

    "STREET_VENDOR": [("Street Vendors Act, 2014 — sections 3 and 18", "https://www.indiacode.nic.in/bitstream/123456789/19057/1/sv_act_2014.pdf")],

    "REAL_ESTATE_RERA": [("Real Estate (Regulation and Development) Act, 2016 — section 18", "https://www.indiacode.nic.in/indiacode/bitstream/123456789/2158/1/A201616.pdf")],

    "COMMERCIAL_CONTRACT_MSME": [("MSMED Act, 2006 — sections 15 and 16", "https://www.indiacode.nic.in/bitstream/123456789/5872/1/a2006-27.pdf")],

}



FIELDS = {

    "en": {

        "incident_date": "When did this happen?",

        "incident_location": "Where exactly did it happen?",

        "other_party": "Who was involved? A name or role is enough if you know it.",

    },

    "hi": {

        "incident_date": "यह घटना कब (किस तारीख या दिन) हुई थी?",

        "incident_location": "यह घटना किस जगह या शहर में हुई थी?",

        "other_party": "इसमें दूसरा पक्ष कौन था (कोई व्यक्ति, पुलिस, अधिकारी, या ठेकेदार)?",

    },

    "mr": {

        "incident_date": "ही घटना केव्हा (कोणत्या तारखेला किंवा दिवशी) घडली?",

        "incident_location": "ही घटना कोणत्या ठिकाणी किंवा शहरात घडली?",

        "other_party": "यात दुसरी व्यक्ती किंवा पक्ष कोण होता (कोणती व्यक्ती, पोलीस, अधिकारी किंवा कंत्राटदार)?",

    },

    "ta": {

        "incident_date": "இந்த சம்பவம் எப்போது நடந்தது (தேதி அல்லது நாள்)?",

        "incident_location": "இந்த சம்பவம் எந்த இடத்தில் அல்லது ஊரில் நடந்தது?",

        "other_party": "இதில் சம்பந்தப்பட்ட எதிர் தரப்பினர் யார் (நபர், போலீஸ், அதிகாரி அல்லது ஒப்பந்ததாரர்)?",

    },

    "te": {

        "incident_date": "ఈ సంఘటన ఎప్పుడు (ఏ తేదీన లేదా రోజున) జరిగింది?",

        "incident_location": "ఈ సంఘటన ఏ ప్రదేశంలో లేదా నగరంలో జరిగింది?",

        "other_party": "ఇందులో ఉన్న రెండవ పక్షం ఎవరు (వ్యక్తి, పోలీసులు, అధికారి లేదా కాంట్రాక్టర్)?",

    },

    "kn": {

        "incident_date": "ಈ ಘಟನೆ ಯಾವಾಗ (ಯಾವ ದಿನಾಂಕ ಅಥವಾ ದಿನ) ನಡೆಯಿತು?",

        "incident_location": "ಈ ಘಟನೆ ಯಾವ ಸ್ಥಳದಲ್ಲಿ ಅಥವಾ ನಗರದಲ್ಲಿ ನಡೆಯಿತು?",

        "other_party": "ಇದರಲ್ಲಿ ಭಾಗಿಯಾದ ಇನ್ನೊಂದು ಪಕ್ಷ ಯಾರು (ವ್ಯಕ್ತಿ, ಪೊಲೀಸ್, ಅಧಿಕಾರಿ ಅಥವಾ ಗುತ್ತಿಗೆದಾರ)?",

    },

    "bn": {

        "incident_date": "এই ঘটনাটি কখন (কোন তারিখে বা দিনে) ঘটেছিল?",

        "incident_location": "এই ঘটনাটি কোন স্থানে বা শহরে ঘটেছিল?",

        "other_party": "এতে অন্য পক্ষ কে ছিল (কোনো ব্যক্তি, পুলিশ, কর্মকর্তা বা ঠিকাদার)?",

    },

    "gu": {

        "incident_date": "આ ઘટના ક્યારે (કઈ તારીખે અથવા દિવસે) બની હતી?",

        "incident_location": "આ ઘટના કઈ જગ્યાએ અથવા શહેરમાં બની હતી?",

        "other_party": "આમાં સામેનો પક્ષ કોણ હતો (કોઈ વ્યક્તિ, પોલીસ, અધિકારી અથવા કોન્ટ્રાક્ટર)?",

    },

    "ml": {

        "incident_date": "ഈ സംഭവം എപ്പോഴാണ് നടന്നത് (തീയതി അല്ലെങ്കിൽ ദിവസം)?",

        "incident_location": "ഈ സംഭവം എവിടെയാണ് അല്ലെങ്കിൽ ഏത് നഗരത്തിലാണ് നടന്നത്?",

        "other_party": "ഇതിൽ ഉൾപ്പെട്ട എതിർ കക്ഷി ആരാണ് (വ്യക്തി, പോലീസ്, ഉദ്യോഗസ്ഥൻ അല്ലെങ്കിൽ കരാറുകാരൻ)?",

    },

    "pa": {

        "incident_date": "ਇਹ ਘਟਨਾ ਕਦੋਂ (ਕਿਸ ਤਾਰੀਖ ਜਾਂ ਦਿਨ) ਵਾਪਰੀ ਸੀ?",

        "incident_location": "ਇਹ ਘਟਨਾ ਕਿਸ ਥਾਂ ਜਾਂ ਸ਼ਹਿਰ ਵਿੱਚ ਵਾਪਰੀ ਸੀ?",

        "other_party": "ਇਸ ਵਿੱਚ ਦੂਜੀ ਧਿਰ ਕੌਣ ਸੀ (ਕੋਈ ਵਿਅਕਤੀ, ਪੁਲਿਸ, ਅਧਿਕਾਰੀ ਜਾਂ ਠੇਕੇਦਾਰ)?",

    },

}



ISSUE_QUESTIONS = {

    "en": {

        "WAGE_THEFT": "What work was done, for which employer, and what wages are unpaid?",

        "STREET_VENDOR": "Are you vending at this site, and did you receive a survey certificate or written notice?",

        "REAL_ESTATE_RERA": "What are the project registration number, promised possession date, and payment records?",

        "COMMERCIAL_CONTRACT_MSME": "Was the supplier registered as a micro or small enterprise when the order was accepted, and when were the goods or services accepted?",

        "MOTOR_ACCIDENT_PRO": "Was anyone injured, which vehicles were involved, and what insurer and policy details are confirmed?",

        "POLICE_CUSTODY": "Was anyone arrested or detained, and what did the police say or provide in writing?",

        "LAND_GRABBING": "Who occupies the property now, and are there title, tenancy, or eviction papers?",

        "LOAN_FRAUD": "Which app or person contacted you, what was requested, and what messages or transactions can you document?",

        "DOMESTIC_VIOLENCE": "Is anyone in immediate danger, and what support or safe contact method do you want?",

        "CORRUPTION_RTI": "Which office or benefit is involved, and do you have an application or receipt number?",

        "RELIGIOUS_GATHERING": "What occurred at the gathering, and were there threats, injuries, or a police report?",

        "GENERAL_CITIZEN_AID": "What happened, and what help do you want first?",

    },

    "hi": {

        "WAGE_THEFT": "आप किस कंपनी या ठेकेदार के पास काम करते थे, और आपकी कितनी मजदूरी बकाया है?",

        "STREET_VENDOR": "क्या आपके पास वेंडिंग सर्टिफिकेट है, और क्या नगर निगम या पुलिस ने कोई लिखित नोटिस दिया?",

        "REAL_ESTATE_RERA": "प्रोजेक्ट का रेरा नंबर क्या है और बिल्डर ने किस तारीख को कब्जा देने का वादा किया था?",

        "COMMERCIAL_CONTRACT_MSME": "क्या आपकी फर्म MSME में रजिस्टर्ड है और माल की डिलीवरी किस तारीख को की गई थी?",

        "MOTOR_ACCIDENT_PRO": "यह हादसा कब और कहां हुआ? क्या किसी को चोट आई है, और क्या दूसरी गाड़ी का नंबर आपके पास है?",

        "POLICE_CUSTODY": "क्या पुलिस ने कोई लिखित अरेस्ट मेमो या रसीद दी है? क्या कोई थाने में बंद है?",

        "LAND_GRABBING": "जमीन पर किसका कब्जा है और क्या आपके पास जमीन के कागजात या रजिस्ट्री है?",

        "LOAN_FRAUD": "लोन ऐप का क्या नाम है और वो आपको किस तरह परेशान या ब्लैकमेल कर रहे हैं?",

        "DOMESTIC_VIOLENCE": "क्या आप इस समय सुरक्षित स्थान पर हैं? क्या आपको तुरंत कानूनी या चिकित्सीय सहायता चाहिए?",

        "CORRUPTION_RTI": "किस सरकारी दफ्तर का मामला है, और क्या आपके पास आवेदन या रसीद संख्या है?",

        "RELIGIOUS_GATHERING": "प्रार्थना सभा में क्या हुआ था, और क्या किसी को चोट आई या पुलिस में शिकायत हुई?",

        "GENERAL_CITIZEN_AID": "क्या घटना घटी, और आपको सबसे पहले किस प्रकार की कानूनी मदद चाहिए?",

    },

    "mr": {

        "WAGE_THEFT": "तुम्ही कोणत्या कंपनीत किंवा कंत्राटदाराकडे काम करत होतात, आणि तुमचा किती पगार थकला आहे?",

        "STREET_VENDOR": "तुमच्याकडे फेरीवाला प्रमाणपत्र (वेंडिंग सर्टिफिकेट) आहे का, आणि महापालिका किंवा पोलिसांनी काही लेखी नोटीस दिली का?",

        "REAL_ESTATE_RERA": "प्रकल्पाचा रेरा (RERA) नोंदणी क्रमांक काय आहे आणि बिल्डरने कोणत्या तारखेला ताबा देण्याचे आश्वासन दिले होते?",

        "COMMERCIAL_CONTRACT_MSME": "तुमची संस्था MSME मध्ये नोंदणीकृत आहे का आणि मालाची डिलिव्हरी कोणत्या तारखेला झाली होती?",

        "MOTOR_ACCIDENT_PRO": "हा अपघात केव्हा आणि कुठे झाला? कोणाला दुखापत झाली आहे का, आणि दुसऱ्या वाहनाचा क्रमांक तुमच्याकडे आहे का?",

        "POLICE_CUSTODY": "पोलिसांनी काही लेखी अटक पंचनामा (अरेस्ट मेमो) किंवा पावती दिली आहे का? कोणी पोलीस कोठडीत आहे का?",

        "LAND_GRABBING": "जमिनीवर कोणाचा ताबा आहे आणि तुमच्याकडे जमिनीची कागदपत्रे किंवा सातबारा/रजिस्ट्री आहे का?",

        "LOAN_FRAUD": "कर्ज (लोन) ॲपचे नाव काय आहे आणि ते तुम्हाला कशा प्रकारे धमकावत किंवा ब्लॅकमेल करत आहेत?",

        "DOMESTIC_VIOLENCE": "तुम्ही सध्या सुरक्षित ठिकाणी आहात का? तुम्हाला तात्काळ कायदेशीर किंवा वैद्यकीय मदतीची आवश्यकता आहे का?",

        "CORRUPTION_RTI": "हे प्रकरण कोणत्या शासकीय कार्यालयाशी संबंधित आहे, आणि तुमच्याकडे अर्जाचा किंवा पावतीचा क्रमांक आहे का?",

        "RELIGIOUS_GATHERING": "प्रार्थना सभेत किंवा कार्यक्रमात काय घडले, आणि कोणाला दुखापत झाली किंवा पोलिसात तक्रार झाली आहे का?",

        "GENERAL_CITIZEN_AID": "नेमकी काय घटना घडली आहे, आणि तुम्हाला सर्वप्रथम कोणत्या प्रकारची कायदेशीर मदत हवी आहे?",

    },

    "ta": {

        "WAGE_THEFT": "நீங்கள் எந்த நிறுவனம் அல்லது ஒப்பந்ததாரரிடம் வேலை செய்தீர்கள், எவ்வளவு சம்பள பாக்கி உள்ளது?",

        "STREET_VENDOR": "உங்களிடம் விற்பனை சான்றிதழ் உள்ளதா, நகராட்சி அல்லது காவல்துறை எழுத்துப்பூர்வ நோட்டீஸ் கொடுத்ததா?",

        "REAL_ESTATE_RERA": "திட்டத்தின் ரேரா (RERA) எண் என்ன, வீடு ஒப்படைக்க உறுதியளிக்கப்பட்ட தேதி என்ன?",

        "COMMERCIAL_CONTRACT_MSME": "உங்கள் நிறுவனம் MSME-ல் பதிவு செய்யப்பட்டுள்ளதா, பொருட்கள் எப்போது வழங்கப்பட்டன?",

        "MOTOR_ACCIDENT_PRO": "விபத்தில் யாருக்காவது காயம் ஏற்பட்டதா, என்ன வாகனங்கள் சம்பந்தப்பட்டன, காப்பீட்டு விவரங்கள் உள்ளதா?",

        "POLICE_CUSTODY": "காவல்துறை கைது குறிப்பு (Arrest Memo) கொடுத்துள்ளதா, யாராவது காவலில் வைக்கப்பட்டுள்ளார்களா?",

        "LAND_GRABBING": "நிலத்தை தற்போது யார் ஆக்கிரமித்துள்ளனர், உங்களிடம் பட்டா அல்லது பதிவு ஆவணங்கள் உள்ளதா?",

        "LOAN_FRAUD": "கடன் செயலியில் என்ன பெயர், அவர்கள் உங்களை எவ்வாறு அச்சுறுத்துகிறார்கள்?",

        "DOMESTIC_VIOLENCE": "நீங்கள் தற்போது பாதுகாப்பான இடத்தில் உள்ளீர்களா, அவசர மருத்துவ அல்லது சட்ட உதவி தேவையா?",

        "CORRUPTION_RTI": "இது எந்த அரசு அலுவலகம் சார்ந்தது, உங்களிடம் மனு அல்லது ரசீது எண் உள்ளதா?",

        "RELIGIOUS_GATHERING": "கூட்டத்தில் என்ன நடந்தது, அச்சுறுத்தல்கள் அல்லது காயங்கள் ஏற்பட்டு புகார் அளிக்கப்பட்டுள்ளதா?",

        "GENERAL_CITIZEN_AID": "என்ன நடந்தது, உங்களுக்கு முதலில் என்ன சட்ட உதவி தேவை?",

    },

    "te": {

        "WAGE_THEFT": "మీరు ఏ కంపెనీ లేదా కాంట్రాక్టర్ వద్ద పనిచేశారు, ఎంత జీతం బకాయి ఉంది?",

        "STREET_VENDOR": "మీ వద్ద వెండింగ్ సర్టిఫికేట్ ఉందా, మున్సిపాలిటీ లేదా పోలీసులు లిఖితపూర్వక నోటీసు ఇచ్చారా?",

        "REAL_ESTATE_RERA": "ప్రాజెక్ట్ రెరా (RERA) రిజిస్ట్రేషన్ నంబర్ ఏమిటి మరియు స్వాధీనం తేదీ ఏది?",

        "COMMERCIAL_CONTRACT_MSME": "మీ సంస్థ MSMEలో నమోదై ఉందా మరియు వస్తువులు ఎప్పుడు డెలివరీ చేయబడ్డాయి?",

        "MOTOR_ACCIDENT_PRO": "ప్రమాదంలో ఎవరికైనా గాయాలయ్యాయా, ఏ వాహనాలు ఉన్నాయి, ఇన్సూరెన్స్ వివరాలు ఏమైనా ఉన్నాయా?",

        "POLICE_CUSTODY": "పోలీసులు ఏదైనా అరెస్ట్ మెమో ఇచ్చారా, ఎవరైనా స్టేషన్‌లో ఉన్నారా?",

        "LAND_GRABBING": "భూమిపై ప్రస్తుతం ఎవరి ఆధీనం ఉంది, మీ వద్ద పట్టా లేదా రిజిస్ట్రేషన్ పత్రాలు ఉన్నాయా?",

        "LOAN_FRAUD": "లోన్ యాప్ పేరు ఏమిటి మరియు వారు మిమ్మల్ని ఎలా బ్లాక్‌మెయిల్ చేస్తున్నారు?",

        "DOMESTIC_VIOLENCE": "మీరు ప్రస్తుతం సురక్షిత ప్రదేశంలో ఉన్నారా, తక్షణ చట్టపరమైన లేదా వైద్య సహాయం కావాలా?",

        "CORRUPTION_RTI": "ఇది ఏ ప్రభుత్వ కార్యాలయానికి సంబంధించినది, రసీదు నంబర్ ఉందా?",

        "RELIGIOUS_GATHERING": "సభలో ఏమి జరిగింది, బెదిరింపులు లేదా గాయాలు జరిగాయా?",

        "GENERAL_CITIZEN_AID": "ఏం జరిగింది, మీకు మొదట ఎలాంటి న్యాయ సహాయం కావాలి?",

    },

    "kn": {

        "WAGE_THEFT": "ನೀವು ಯಾವ ಕಂಪನಿ ಅಥವಾ ಗುತ್ತಿಗೆದಾರರ ಬಳಿ ಕೆಲಸ ಮಾಡಿದ್ದೀರಿ, ಮತ್ತು ಎಷ್ಟು ವೇತನ ಬಾಕಿ ಇದೆ?",

        "STREET_VENDOR": "ನಿಮ್ಮ ಬಳಿ ಮಾರಾಟ ಪ್ರಮಾಣಪತ್ರವಿದೆಯೇ, ಪಾಲಿಕೆ ಅಥವಾ ಪೊಲೀಸರು ಲಿಖಿತ ನೋಟಿಸ್ ನೀಡಿದ್ದಾರೆಯೇ?",

        "REAL_ESTATE_RERA": "ಯೋಜನೆಯ ರೇರಾ (RERA) ನೋಂದಣಿ ಸಂಖ್ಯೆ ಏನು ಮತ್ತು ಸ್ವಾಧೀನ ದಿನಾಂಕ ಯಾವಾಗ?",

        "COMMERCIAL_CONTRACT_MSME": "ನಿಮ್ಮ ಸಂಸ್ಥೆ MSME ನಲ್ಲಿ ನೋಂದಾಯಿಸಲಾಗಿದೆಯೇ ಮತ್ತು ಸರಕುಗಳು ಯಾವಾಗ ವಿತರಿಸಲ್ಪಟ್ಟವು?",

        "MOTOR_ACCIDENT_PRO": "ಅಪಘಾತದಲ್ಲಿ ಯಾರಿಗಾದರೂ ಗಾಯವಾಗಿದೆಯೇ, ಯಾವ ವಾಹನಗಳು ಭಾಗಿಯಾಗಿದ್ದವು ಮತ್ತು ವಿಮಾ ವಿವರಗಳಿವೆಯೇ?",

        "POLICE_CUSTODY": "ಪೊಲೀಸರು ಲಿಖಿತ ಅರೆಸ್ಟ್ ಮೆಮೊ ನೀಡಿದ್ದಾರೆಯೇ, ಯಾರಾದರೂ ಪೊಲೀಸ್ ವಶದಲ್ಲಿದ್ದಾರೆಯೇ?",

        "LAND_GRABBING": "ಜಮೀನು ಪ್ರಸ್ತುತ ಯಾರ ವಶದಲ್ಲಿದೆ, ನಿಮ್ಮ ಬಳಿ ಪಹಣಿ ಅಥವಾ ನೋಂದಣಿ ದಾಖಲೆಗಳಿವೆಯೇ?",

        "LOAN_FRAUD": "ಸಾಲದ ಆ್ಯಪ್ ಹೆಸರು ಏನು ಮತ್ತು ಅವರು ನಿಮಗೆ ಹೇಗೆ ಬೆದರಿಕೆ ಹಾಕುತ್ತಿದ್ದಾರೆ?",

        "DOMESTIC_VIOLENCE": "ನೀವು ಪ್ರಸ್ತುತ ಸುರಕ್ಷಿತ ಸ್ಥಳದಲ್ಲಿದ್ದೀರಾ, ತಕ್ಷಣದ ಕಾನೂನು ಅಥವಾ ವೈದ್ಯಕೀಯ ನೆರವು ಬೇಕೇ?",

        "CORRUPTION_RTI": "ಇದು ಯಾವ ಸರ್ಕಾರಿ ಕಚೇರಿಗೆ ಸಂಬಂಧಿಸಿದೆ, ರಸೀದಿ ಸಂಖ್ಯೆ ಇದೆಯೇ?",

        "RELIGIOUS_GATHERING": "ಸಭೆಯಲ್ಲಿ ಏನಾಯಿತು, ಬೆದರಿಕೆಗಳು ಅಥವಾ ಗಾಯಗಳಾಗಿವೆಯೇ?",

        "GENERAL_CITIZEN_AID": "ಏನು ನಡೆದಿದೆ, ನಿಮಗೆ ಮೊದಲಿಗೆ ಯಾವ ರೀತಿಯ ಕಾನೂನು ಸಹಾಯ ಬೇಕು?",

    },

    "bn": {

        "WAGE_THEFT": "আপনি কোন কোম্পানি বা ঠিকাদারের কাছে কাজ করেছেন এবং কত মজুরি বকেয়া রয়েছে?",

        "STREET_VENDOR": "আপনার কাছে কি ভেন্ডিং সার্টিফিকেট আছে, এবং পুরসভা বা পুলিশ কি লিখিত নোটিশ দিয়েছে?",

        "REAL_ESTATE_RERA": "প্রকল্পের রেরা (RERA) নম্বর কী এবং ডেভেলপার কোন তারিখে হস্তান্তরের প্রতিশ্রুতি দিয়েছিল?",

        "COMMERCIAL_CONTRACT_MSME": "আপনার সংস্থা কি MSME নিবন্ধিত এবং মাল কোন তারিখে সরবরাহ করা হয়েছিল?",

        "MOTOR_ACCIDENT_PRO": "দুর্ঘটনায় কেউ কি আহত হয়েছেন, কোন কোন গাড়ি জড়িত ছিল এবং বীমার বিবরণ আছে কি?",

        "POLICE_CUSTODY": "পুলিশ কি কোনো লিখিত অ্যারেস্ট মেমো দিয়েছে, কেউ কি থানায় আটক আছে?",

        "LAND_GRABBING": "জমিতে বর্তমানে কার দখল রয়েছে এবং আপনার কাছে কি দলিলের কাগজ আছে?",

        "LOAN_FRAUD": "লোন অ্যাপের নাম কী এবং তারা আপনাকে কীভাবে ব্ল্যাকমেল করছে?",

        "DOMESTIC_VIOLENCE": "আপনি কি এখন নিরাপদ স্থানে আছেন, জরুরি আইনি বা চিকিৎসা সহায়তা প্রয়োজন?",

        "CORRUPTION_RTI": "এটি কোন সরকারি দপ্তরের বিষয় এবং রসিদ নম্বর আছে কি?",

        "RELIGIOUS_GATHERING": "সভায় কী ঘটেছিল, কোনো আঘাত বা অভিযোগ দায়ের হয়েছে কি?",

        "GENERAL_CITIZEN_AID": "কী ঘটেছে এবং আপনার প্রথমে কী ধরনের আইনি সহায়তা প্রয়োজন?",

    },

    "gu": {

        "WAGE_THEFT": "તમે કઈ કંપની કે કોન્ટ્રાક્ટર પાસે કામ કરતા હતા, અને તમારો કેટલો પગાર બાકી છે?",

        "STREET_VENDOR": "શું તમારી પાસે વેન્ડિંગ પ્રમાણપત્ર છે, અને શું નગરપાલિકા કે પોલીસે કોઈ લેખિત નોટિસ આપી છે?",

        "REAL_ESTATE_RERA": "પ્રોજેક્ટનો રેરા (RERA) નંબર શું છે અને કબજો આપવાની કઈ તારીખ વચન આપી હતી?",

        "COMMERCIAL_CONTRACT_MSME": "શું તમારી પેઢી MSME માં નોંધાયેલી છે અને માલ કઈ તારીખે પહોંચાડવામાં આવ્યો હતો?",

        "MOTOR_ACCIDENT_PRO": "અકસ્માતમાં કોઈને ઈજા થઈ છે, કયા વાહનો સામેલ હતા અને વીમાની વિગતો છે?",

        "POLICE_CUSTODY": "શું પોલીસે કોઈ લેખિત ધરપકડ મેમો આપ્યો છે, શું કોઈ પોલીસ કસ્ટડીમાં છે?",

        "LAND_GRABBING": "જમીન પર હાલમાં કોનો કબજો છે અને તમારી પાસે દસ્તાવેજો કે રજિસ્ટ્રી છે?",

        "LOAN_FRAUD": "લોન એપ્લિકેશનનું નામ શું છે અને તેઓ તમને કેવી રીતે બ્લેકમેલ કરે છે?",

        "DOMESTIC_VIOLENCE": "શું તમે હાલમાં સુરક્ષિત સ્થાન પર છો, તાત્કાલિક કાનૂની કે તબીબી સહાયની જરૂર છે?",

        "CORRUPTION_RTI": "આ કઈ સરકારી કચેરીનો મામલો છે અને પહોંચ નંબર છે?",

        "RELIGIOUS_GATHERING": "સભામાં શું બન્યું હતું, શું કોઈ ઈજા થઈ કે ફરિયાદ નોંધાઈ?",

        "GENERAL_CITIZEN_AID": "શું ઘટના બની છે અને તમારે પહેલા કયા પ્રકારની કાનૂની સહાય જોઈએ છે?",

    },

    "ml": {

        "WAGE_THEFT": "ഏത് കമ്പനിയിലോ കരാറുകാരന്റെ കീഴിലോ ആണ് ജോലി ചെയ്തത്, എത്ര ശമ്പളം കുടിശ്ശികയുണ്ട്?",

        "STREET_VENDOR": "നിങ്ങളുടെ കൈവശം വെൻഡിംഗ് സർട്ടിഫിക്കറ്റ് ഉണ്ടോ, നഗരസഭയോ പോലീസോ രേഖാമൂലം നോട്ടീസ് നൽകിയിട്ടുണ്ടോ?",

        "REAL_ESTATE_RERA": "പ്രോജക്റ്റിന്റെ റെറ (RERA) നമ്പർ എന്താണ്, കൈവശം നൽകുമെന്ന് വാഗ്ദാനം ചെയ്ത തീയതി ഏതാണ്?",

        "COMMERCIAL_CONTRACT_MSME": "നിങ്ങളുടെ സ്ഥാപനം MSME-ൽ രജിസ്റ്റർ ചെയ്തതാണോ, സാധനങ്ങൾ നൽകിയ തീയതി ഏതാണ്?",

        "MOTOR_ACCIDENT_PRO": "അപകടത്തിൽ ആർക്കെങ്കിലും പരിക്കേറ്റോ, ഏതൊക്കെ വാഹനങ്ങളാണ് ഉൾപ്പെട്ടത്, ഇൻഷുറൻസ് വിവരങ്ങൾ ലഭ്യമാണോ?",

        "POLICE_CUSTODY": "പോലീസ് അറസ്റ്റ് മെമ്മോ നൽകിയിട്ടുണ്ടോ, ആരെങ്കിലും കസ്റ്റഡിയിലുണ്ടോ?",

        "LAND_GRABBING": "ഭൂമിയിൽ ഇപ്പോൾ ആർക്കാണ് കൈവശാവകാശം, നിങ്ങളുടെ കൈവശം പ്രമാണങ്ങൾ ഉണ്ടോ?",

        "LOAN_FRAUD": "ലോൺ ആപ്പിന്റെ പേരെന്താണ്, അവർ നിങ്ങളെ എങ്ങനെയാണ് ഭീഷണിപ്പെടുത്തുന്നത്?",

        "DOMESTIC_VIOLENCE": "നിങ്ങൾ ഇപ്പോൾ സുരക്ഷിതമായ സ്ഥലത്താണോ, അടിയന്തര നിയമസഹായം ആവശ്യമുണ്ടോ?",

        "CORRUPTION_RTI": "ഇത് ഏത് സർക്കാർ ഓഫീസുമായി ബന്ധപ്പെട്ടതാണ്, രസീത് നമ്പർ ഉണ്ടോ?",

        "RELIGIOUS_GATHERING": "യോഗത്തിൽ എന്താണ് സംഭവിച്ചത്, എന്തെങ്കിലും പരിക്കോ പരാതിയോ ഉണ്ടോ?",

        "GENERAL_CITIZEN_AID": "എന്താണ് സംഭവിച്ചത്, നിങ്ങൾക്ക് ആദ്യം എന്ത് നിയമസഹായമാണ് വേണ്ടത്?",

    },

    "pa": {

        "WAGE_THEFT": "ਤੁਸੀਂ ਕਿਸ ਕੰਪਨੀ ਜਾਂ ਠੇਕੇਦਾਰ ਕੋਲ ਕੰਮ ਕਰਦੇ ਸੀ, ਅਤੇ ਤੁਹਾਡੀ ਕਿੰਨੀ ਤਨਖਾਹ ਬਾਕੀ ਹੈ?",

        "STREET_VENDOR": "ਕੀ ਤੁਹਾਡੇ ਕੋਲ ਵੈਂਡਿੰਗ ਸਰਟੀਫਿਕੇਟ ਹੈ, ਅਤੇ ਕੀ ਨਗਰ ਨਿਗਮ ਜਾਂ ਪੁਲਿਸ ਨੇ ਕੋਈ ਲਿਖਤੀ ਨੋਟਿਸ ਦਿੱਤਾ ਹੈ?",

        "REAL_ESTATE_RERA": "ਪ੍ਰੋਜੈਕਟ ਦਾ ਰੇਰਾ (RERA) ਨੰਬਰ ਕੀ ਹੈ ਅਤੇ ਕਬਜ਼ਾ ਦੇਣ ਦਾ ਵਾਅਦਾ ਕਿਸ ਮਿਤੀ ਦਾ ਸੀ?",

        "COMMERCIAL_CONTRACT_MSME": "ਕੀ ਤੁਹਾਡੀ ਫਰਮ MSME ਵਿੱਚ ਰਜਿਸਟਰਡ ਹੈ ਅਤੇ ਸਮਾਨ ਦੀ ਸਪਲਾਈ ਕਦੋਂ ਕੀਤੀ ਗਈ ਸੀ?",

        "MOTOR_ACCIDENT_PRO": "ਹਾਦਸੇ ਵਿੱਚ ਕੀ ਕੋਈ ਜ਼ਖਮੀ ਹੋਇਆ ਹੈ, ਕਿਹੜੇ ਵਾਹਨ ਸ਼ਾਮਲ ਸਨ ਅਤੇ ਬੀਮਾ ਵੇਰਵੇ ਹਨ?",

        "POLICE_CUSTODY": "ਕੀ ਪੁਲਿਸ ਨੇ ਕੋਈ ਲਿਖਤੀ ਗ੍ਰਿਫਤਾਰੀ ਮੈਮੋ ਦਿੱਤਾ ਹੈ, ਕੀ ਕੋਈ ਹਿਰਾਸਤ ਵਿੱਚ ਹੈ?",

        "LAND_GRABBING": "ਜ਼ਮੀਨ 'ਤੇ ਇਸ ਸਮੇਂ ਕਿਸ ਦਾ ਕਬਜ਼ਾ ਹੈ ਅਤੇ ਕੀ ਤੁਹਾਡੇ ਕੋਲ ਰਜਿਸਟਰੀ ਜਾਂ ਦਸਤਾਵੇਜ਼ ਹਨ?",

        "LOAN_FRAUD": "ਲੋਨ ਐਪ ਦਾ ਨਾਮ ਕੀ ਹੈ ਅਤੇ ਉਹ ਤੁਹਾਨੂੰ ਕਿਸ ਤਰ੍ਹਾਂ ਧਮਕਾ ਰਹੇ ਹਨ?",

        "DOMESTIC_VIOLENCE": "ਕੀ ਤੁਸੀਂ ਇਸ ਵੇਲੇ ਸੁਰੱਖਿਅਤ ਥਾਂ 'ਤੇ ਹੋ, ਕੀ ਤੁਹਾਨੂੰ ਤੁਰੰਤ ਕਾਨੂੰਨੀ ਸਹਾਇਤਾ ਚਾਹੀਦੀ ਹੈ?",

        "CORRUPTION_RTI": "ਇਹ ਕਿਸ ਸਰਕਾਰੀ ਦਫ਼ਤਰ ਨਾਲ ਸਬੰਧਤ ਹੈ, ਅਤੇ ਕੀ ਤੁਹਾਡੇ ਕੋਲ ਰਸੀਦ ਨੰਬਰ ਹੈ?",

        "RELIGIOUS_GATHERING": "ਸਭਾ ਵਿੱਚ ਕੀ ਹੋਇਆ ਸੀ, ਕੀ ਕੋਈ ਜ਼ਖਮੀ ਹੋਇਆ ਜਾਂ ਪੁਲਿਸ ਰਿਪੋਰਟ ਹੋਈ?",

        "GENERAL_CITIZEN_AID": "ਕੀ ਘਟਨਾ ਵਾਪਰੀ ਹੈ, ਅਤੇ ਤੁਹਾਨੂੰ ਸਭ ਤੋਂ ਪਹਿਲਾਂ ਕਿਸ ਤਰ੍ਹਾਂ ਦੀ ਕਾਨੂੰਨੀ ਮਦਦ ਚਾਹੀਦੀ ਹੈ?",

    }
}

CATEGORY_QUESTIONS = {
    "en": {
        "WAGE_THEFT": {
            "specific_details": "What work was done, for which employer, and what wages are unpaid?",
            "other_party": "Who was your immediate employer, contractor, or thekedar who refused to pay?",
            "incident_date": "Since when have these wages been pending, or when was the last date of work?",
            "incident_location": "Where was the worksite, construction project, or factory located?",
        },
        "STREET_VENDOR": {
            "specific_details": "Are you vending at this site, and did you receive a survey certificate or written notice?",
            "other_party": "Which municipal ward authority, anti-encroachment squad, or police station carried out the eviction?",
            "incident_date": "On what date and time was your cart or goods removed or seized?",
            "incident_location": "Where was your vending stall located (street, ward, or market area)?",
        },
        "POLICE_CUSTODY": {
            "specific_details": "Was anyone arrested or detained, and what did the police say or provide in writing?",
            "other_party": "Which police station, chowki, or investigating officers are involved?",
            "incident_date": "When (date and approximate time) was the person taken into custody?",
            "incident_location": "At which police station, lockup, or facility is the person being held?",
        },
        "MOTOR_ACCIDENT_PRO": {
            "specific_details": "Was anyone injured, which vehicles were involved, and what insurer and policy details are confirmed?",
            "other_party": "What was the vehicle number, driver name, or insurance company of the other vehicle?",
            "incident_date": "On what date and approximately what time did the accident happen?",
            "incident_location": "Where did the collision occur (highway, road junction, or landmark)?",
        },
        "REAL_ESTATE_RERA": {
            "specific_details": "What are the project registration number, promised possession date, and payment records?",
            "other_party": "What is the name of the builder, developer, or housing promoter entity?",
            "incident_date": "When was the allotment or agreement for sale signed, and what was your last payment date?",
            "incident_location": "In which city, locality, and project site is the property situated?",
        },
        "COMMERCIAL_CONTRACT_MSME": {
            "specific_details": "Was the supplier registered as a micro or small enterprise when the order was accepted, and when were the goods or services accepted?",
            "other_party": "What is the legal name of the corporate buyer or client holding the unpaid invoices?",
            "incident_date": "When were the goods or services delivered, and have 45 days passed?",
            "incident_location": "In which city or state was the commercial contract or delivery executed?",
        },
        "LAND_GRABBING": {
            "specific_details": "Who occupies the property now, and are there title, tenancy, or eviction papers?",
            "other_party": "Who is the trespasser, encroacher, or party attempting illegal possession?",
            "incident_date": "When was boundary demarcation damaged or illegal entry attempted?",
            "incident_location": "Where is the land situated (village, taluka, survey/gat number, or district)?",
        },
        "LOAN_FRAUD": {
            "specific_details": "Which app or person contacted you, what was requested, and what messages or transactions can you document?",
            "other_party": "What is the name of the digital lending app, recovery agency, or caller harassing you?",
            "incident_date": "When did the threats, unauthorized debits, or blackmail begin?",
            "incident_location": "Through which bank account, UPI ID, or digital platform did transactions take place?",
        },
        "DOMESTIC_VIOLENCE": {
            "specific_details": "Is anyone in immediate danger, and what support or safe contact method do you want?",
            "other_party": "Who is the respondent or person causing harm or threats in the shared household?",
            "incident_date": "When did the most recent incident of violence, harassment, or eviction threat occur?",
            "incident_location": "In which city or district is the shared household situated?",
        },
        "CORRUPTION_RTI": {
            "specific_details": "Which office or benefit is involved, and do you have an application or receipt number?",
            "other_party": "Which public official, department, or office demanded bribes or withheld service?",
            "incident_date": "When was your application or grievance submitted, and what was the deadline?",
            "incident_location": "In which municipal office, collectorate, or tehsil is this public office located?",
        },
        "RELIGIOUS_GATHERING": {
            "specific_details": "What occurred at the gathering, and were there threats, injuries, or a police report?",
            "other_party": "Which group, persons, or police personnel interfered with the peaceful gathering?",
            "incident_date": "On what date and time was the prayer or gathering disrupted?",
            "incident_location": "Where was the prayer hall or gathering held (premises address and locality)?",
        },
        "GENERAL_CITIZEN_AID": {
            "specific_details": "What happened, and what help do you want first?",
            "other_party": "Who is the other person, officer, company, or authority involved?",
            "incident_date": "When did this occur (date or time period)?",
            "incident_location": "Where did this happen (city, landmark, or jurisdiction)?",
        },
    },
    "hi": {
        "WAGE_THEFT": {
            "specific_details": "आप किस कंपनी या ठेकेदार के पास क्या काम करते थे, और आपकी कितनी मजदूरी बकाया है?",
            "other_party": "आपको काम पर रखने वाला ठेकेदार, सुपरवाइजर या कंपनी कौन सी है?",
            "incident_date": "यह मजदूरी किस महीने से बकाया है या आपने आखिरी बार काम कब किया था?",
            "incident_location": "काम की जगह, कंस्ट्रक्शन साइट या फैक्ट्री किस इलाके या शहर में थी?",
        },
        "STREET_VENDOR": {
            "specific_details": "क्या आपके पास वेंडिंग सर्टिफिकेट या टीवीसी रसीद है, और क्या नगर निगम ने कोई लिखित नोटिस दिया?",
            "other_party": "किस नगर निगम, अतिक्रमण विरोधी दस्ते या पुलिस थाने ने दुकान हटाई या सामान जब्त किया?",
            "incident_date": "आपकी दुकान या रेहड़ी किस तारीख और समय पर हटाई गई?",
            "incident_location": "आपकी दुकान किस बाजार, सड़क या वेंडिंग जोन में स्थित थी?",
        },
        "POLICE_CUSTODY": {
            "specific_details": "क्या पुलिस ने कोई लिखित अरेस्ट मेमो या कारण बताया, और क्या किसी रिश्तेदार को सूचना दी गई?",
            "other_party": "कौन सा पुलिस थाना, चौकी या जांच अधिकारी इस मामले में शामिल हैं?",
            "incident_date": "उन्हें कब (किस तारीख और समय पर) हिरासत में लिया गया था?",
            "incident_location": "उन्हें इस समय किस पुलिस थाने, लॉकअप या स्थान पर रखा गया है?",
        },
        "MOTOR_ACCIDENT_PRO": {
            "specific_details": "क्या किसी को चोट आई है, गाड़ियों के नंबर क्या हैं, और क्या अस्पताल का मेडिकल/एमएलसी पर्चा बना है?",
            "other_party": "टक्कर मारने वाली गाड़ी का नंबर, चालक का नाम या बीमा कंपनी कौन सी है?",
            "incident_date": "यह दुर्घटना किस तारीख को और लगभग किस समय हुई थी?",
            "incident_location": "हादसा किस सड़क, चौराहे, हाईवे या लैंडमार्क के पास हुआ?",
        },
        "REAL_ESTATE_RERA": {
            "specific_details": "प्रोजेक्ट का रेरा (RERA) रजिस्ट्रेशन नंबर क्या है और एग्रीमेंट में कब्जा देने की क्या तारीख थी?",
            "other_party": "बिल्डर, प्रमोटर या हाउसिंग कंपनी का पंजीकृत नाम क्या है?",
            "incident_date": "फ्लैट का एग्रीमेंट कब हुआ था, और आपने आखिरी किस्त किस तारीख को दी थी?",
            "incident_location": "हाउसिंग प्रोजेक्ट किस शहर, इलाके और पते पर स्थित है?",
        },
        "COMMERCIAL_CONTRACT_MSME": {
            "specific_details": "क्या आपकी फर्म MSME उद्यम में रजिस्टर्ड है, और इनवॉइस की कुल कितनी रकम बकाया है?",
            "other_party": "भुगतान रोकने वाली खरीदार कंपनी या कारोबारी का कानूनी नाम क्या है?",
            "incident_date": "माल या सेवाएं किस तारीख को डिलीवर की गई थीं, और क्या 45 दिन बीत चुके हैं?",
            "incident_location": "यह अनुबंध या डिलीवरी किस शहर अथवा राज्य में हुई थी?",
        },
        "LAND_GRABBING": {
            "specific_details": "जमीन पर किसका कब्जा है और आपके पास 7/12, रजिस्ट्री या मालिकाना हक के क्या दस्तावेज हैं?",
            "other_party": "जमीन पर अवैध कब्जा या अतिक्रमण करने वाला व्यक्ति या संस्था कौन है?",
            "incident_date": "जमीन की मेड़ कब तोड़ी गई या अवैध रूप से घुसने का प्रयास कब हुआ?",
            "incident_location": "यह जमीन किस गांव, तहसील, खसरा/सर्वे नंबर और जिले में स्थित है?",
        },
        "LOAN_FRAUD": {
            "specific_details": "लोन ऐप का नाम क्या है, और क्या वे आपके संपर्कों को फोन करके या फोटो एडिट करके ब्लैकमेल कर रहे हैं?",
            "other_party": "कौन सा लोन ऐप, फर्जी वसूली एजेंट या रिकवरी एजेंसी आपको परेशान कर रही है?",
            "incident_date": "धमकियां, ब्लैकमेलिंग या खाते से गलत कटौती कब शुरू हुई?",
            "incident_location": "पैसे किस बैंक खाते, यूपीआई आईडी या डिजिटल वॉलेट के जरिए ट्रांसफर हुए?",
        },
        "DOMESTIC_VIOLENCE": {
            "specific_details": "क्या आप या बच्चे इस समय किसी खतरे में हैं, और क्या आपको तुरंत सुरक्षित आश्रय या डॉक्टरी सहायता चाहिए?",
            "other_party": "साझा घर में आपको नुकसान या धमकी पहुंचाने वाला मुख्य व्यक्ति कौन है?",
            "incident_date": "हिंसा, मारपीट या घर से निकालने की धमकी की ताजा घटना कब हुई थी?",
            "incident_location": "साझा घर किस शहर या जिले में स्थित है?",
        },
        "CORRUPTION_RTI": {
            "specific_details": "यह किस सरकारी दफ्तर का मामला है, और आपके पास आवेदन या पावती संख्या क्या है?",
            "other_party": "किस अधिकारी, जन सूचना अधिकारी या विभाग ने काम रोका या रिश्वत की मांग की?",
            "incident_date": "आपने आवेदन किस तारीख को दिया था, और क्या 30 दिन की वैधानिक सीमा समाप्त हो गई है?",
            "incident_location": "यह सरकारी दफ्तर, कलेक्टरेट या नगर निगम किस शहर या जिले में है?",
        },
        "RELIGIOUS_GATHERING": {
            "specific_details": "क्या प्रार्थना सभा में बाधा डाली गई या लोगों को धमकाया अथवा हिरासत में लिया गया?",
            "other_party": "प्रार्थना सभा में किस समूह, व्यक्तियों या पुलिसकर्मियों ने हस्तक्षेप किया?",
            "incident_date": "यह घटना किस तारीख और समय पर घटी थी?",
            "incident_location": "प्रार्थना सभा या कार्यक्रम किस जगह या परिसर में आयोजित किया गया था?",
        },
        "GENERAL_CITIZEN_AID": {
            "specific_details": "क्या घटना घटी, और आपको सबसे पहले किस प्रकार की कानूनी मदद या राहत चाहिए?",
            "other_party": "इसमें संबंधित दूसरा व्यक्ति, कंपनी या सरकारी अधिकारी कौन है?",
            "incident_date": "यह घटना या विवाद किस तारीख को हुआ था?",
            "incident_location": "यह घटना किस शहर, इलाके या जगह पर घटी थी?",
        },
    },
    "mr": {
        "WAGE_THEFT": {
            "specific_details": "तुम्ही कोणत्या कंपनीत किंवा कंत्राटदाराकडे काय काम केले, आणि तुमचा किती पगार थकला आहे?",
            "other_party": "तुम्हाला कामावर ठेवणारा कंत्राटदार, सुपरवायझर किंवा मालक कोण आहे?",
            "incident_date": "हा पगार कोणत्या महिन्यांपासून थकला आहे किंवा कामाचा शेवटचा दिवस कोणता होता?",
            "incident_location": "कामाची जागा, बांधकाम साईट किंवा कारखाना कोणत्या भागात किंवा शहरात होता?",
        },
        "STREET_VENDOR": {
            "specific_details": "तुमच्याकडे फेरीवाला प्रमाणपत्र (वेंडिंग सर्टिफिकेट) किंवा पावती आहे का, आणि महापालिकेने काही लेखी नोटीस दिली का?",
            "other_party": "कोणत्या महापालिका प्रभाग अधिकाऱ्यांनी, अतिक्रमण विरोधी पथकाने किंवा पोलिसांनी ही कारवाई केली?",
            "incident_date": "तुमची गाडी कोणत्या तारखेला आणि साधारण किती वाजता हटवली गेली?",
            "incident_location": "तुमचा स्टॉल किंवा गाडी कोणत्या रस्त्यावर, मार्केटमध्ये किंवा प्रभागात होती?",
        },
        "POLICE_CUSTODY": {
            "specific_details": "पोलिसांनी अटकेचे लेखी कारण किंवा अरेस्ट मेमो दिला आहे का, आणि नातेवाईकांना माहिती दिली का?",
            "other_party": "कोणते पोलीस ठाणे, चौकी किंवा कोणते पोलीस अधिकारी यात सहभागी आहेत?",
            "incident_date": "त्यांना कोणत्या तारखेला आणि किती वाजता ताब्यात घेण्यात आले होते?",
            "incident_location": "त्यांना सध्या कोणत्या पोलीस ठाण्यात किंवा कोठडीत ठेवले आहे?",
        },
        "MOTOR_ACCIDENT_PRO": {
            "specific_details": "कोणाला दुखापत झाली आहे का, वाहनांचे क्रमांक काय आहेत, आणि हॉस्पिटलचा रिपोर्ट आहे का?",
            "other_party": "धडक देणाऱ्या दुसऱ्या वाहनाचा क्रमांक, चालक किंवा त्यांची विमा कंपनी कोणती आहे?",
            "incident_date": "हा अपघात कोणत्या दिवशी आणि साधारण किती वाजता घडला होता?",
            "incident_location": "हा अपघात कोणत्या रस्त्यावर, महामार्गावर किंवा चौकात झाला?",
        },
        "REAL_ESTATE_RERA": {
            "specific_details": "प्रकल्पाचा रेरा (RERA) नंबर काय आहे आणि करारनाम्यात ताबा देण्याची कोणती तारीख दिली होती?",
            "other_party": "बिल्डर, डेव्हलपर किंवा बांधकाम कंपनीचे नाव काय आहे?",
            "incident_date": "फ्लॅटचा करारनामा केव्हा झाला होता, आणि तुम्ही शेवटचा हप्ता कधी भरला?",
            "incident_location": "हा गृहनिर्माण प्रकल्प कोणत्या शहरात, भागात किंवा पत्त्यावर आहे?",
        },
        "COMMERCIAL_CONTRACT_MSME": {
            "specific_details": "तुमची संस्था MSME उद्यममध्ये नोंदणीकृत आहे का, आणि बिलाची एकूण किती रक्कम येणे बाकी आहे?",
            "other_party": "पैसे थकवणाऱ्या खरेदीदार कंपनीचे किंवा व्यापाऱ्याचे नाव काय आहे?",
            "incident_date": "माल किंवा सेवा कोणत्या तारखेला दिली होती, आणि ४५ दिवसांची मुदत संपली आहे का?",
            "incident_location": "हा व्यावसायिक करार किंवा डिलिव्हरी कोणत्या शहरात अथवा राज्यात झाली होती?",
        },
        "LAND_GRABBING": {
            "specific_details": "जमिनीवर कोणाचा ताबा आहे आणि तुमच्याकडे सातबारा, खरेदीखत किंवा मालकीहक्काचे काय कागदपत्रे आहेत?",
            "other_party": "जमिनीवर बेकायदेशीर ताबा किंवा अतिक्रमण करणारी व्यक्ती कोण आहे?",
            "incident_date": "जमिनीची हद्द केव्हा तोडली किंवा अतिक्रमण करण्याचा प्रयत्न कधी झाला?",
            "incident_location": "ही जमीन कोणत्या गावात, तालुक्यात, गट/सर्व्हे नंबरवर आणि जिल्ह्यात आहे?",
        },
        "LOAN_FRAUD": {
            "specific_details": "कर्ज ॲपचे नाव काय आहे, आणि ते तुमच्या संपर्कांना फोन करून किंवा खोटे फोटो पाठवून धमकावत आहेत का?",
            "other_party": "कोणते लोन ॲप, वसुली एजंट किंवा कोणती कंपनी तुम्हाला त्रास देत आहे?",
            "incident_date": "धमक्या, ब्लॅकमेलिंग किंवा खात्यातून परस्पर पैसे कापले जाणे केव्हा सुरू झाले?",
            "incident_location": "पैसे कोणत्या बँकेतून, यूपीआय आयडीवरून किंवा ॲपवरून कापले गेले?",
        },
        "DOMESTIC_VIOLENCE": {
            "specific_details": "तुम्हाला किंवा मुलांना सध्या काही धोका आहे का, आणि तुम्हाला सुरक्षित निवारा किंवा वैद्यकीय मदतीची गरज आहे का?",
            "other_party": "सामायिक घरामध्ये तुम्हाला त्रास किंवा इजा पोहोचवणारी व्यक्ती कोण आहे?",
            "incident_date": "हिंसाचाराची, शिवीगाळीची किंवा घराबाहेर काढण्याची ताजी घटना केव्हा घडली?",
            "incident_location": "सामायिक घर कोणत्या शहरात किंवा जिल्ह्यात आहे?",
        },
        "CORRUPTION_RTI": {
            "specific_details": "हे कोणत्या शासकीय कार्यालयाशी संबंधित आहे, आणि तुमच्याकडे अर्जाचा किंवा पावतीचा क्रमांक आहे का?",
            "other_party": "कोणत्या अधिकाऱ्याने किंवा जन माहिती अधिकाऱ्याने माहिती नाकारली किंवा लाच मागितली?",
            "incident_date": "तुम्ही अर्ज कधी केला होता, आणि ३० दिवसांची वैधानिक मुदत संपली आहे का?",
            "incident_location": "हे शासकीय कार्यालय, कलेक्टरेट किंवा महापालिका कोणत्या शहरात/जिल्ह्यात आहे?",
        },
        "RELIGIOUS_GATHERING": {
            "specific_details": "प्रार्थना सभेत कोणी अडथळा आणला किंवा लोकांना धमकावले/ताब्यात घेतले का?",
            "other_party": "प्रार्थना सभेत कोणत्या व्यक्तींनी, जमावाने किंवा पोलिसांनी हस्तक्षेप केला?",
            "incident_date": "ही घटना कोणत्या दिवशी आणि वेळेस घडली?",
            "incident_location": "प्रार्थना सभा कोणत्या सभागृहात किंवा जागेवर आयोजित केली होती?",
        },
        "GENERAL_CITIZEN_AID": {
            "specific_details": "नेमकी काय घटना घडली, आणि तुम्हाला सर्वप्रथम कोणती कायदेशीर मदत किंवा न्याय हवा आहे?",
            "other_party": "यामध्ये संबंधित दुसरी व्यक्ती, कंपनी किंवा शासकीय अधिकारी कोण आहे?",
            "incident_date": "ही घटना किंवा वाद केव्हा घडला होता?",
            "incident_location": "ही घटना कोणत्या शहरात, भागात किंवा ठिकाणी घडली?",
        },
    },
    "gu": {
        "WAGE_THEFT": {
            "specific_details": "તમે કઈ કંપની કે કોન્ટ્રાક્ટર પાસે શું કામ કર્યું હતું, અને તમારો કેટલો પગાર બાકી છે?",
            "other_party": "તમને કામે રાખનાર કોન્ટ્રાક્ટર, સુપરવાઈઝર કે માલિક કોણ છે?",
            "incident_date": "આ પગાર કયા મહિનાથી બાકી છે અથવા તમે છેલ્લે ક્યારે કામ કર્યું હતું?",
            "incident_location": "કામનું સ્થળ, કન્સ્ટ્રક્શન સાઇટ કે ફેક્ટરી કયા વિસ્તાર કે શહેરમાં આવેલી છે?",
        },
        "STREET_VENDOR": {
            "specific_details": "શું તમારી પાસે વેન્ડિંગ સર્ટિફિકેટ કે રસીદ છે, અને શું નગરપાલિકા કે મહાનગરપાલિકાએ કોઈ લેખિત નોટિસ આપી હતી?",
            "other_party": "કયા મ્યુનિસિપલ વોર્ડ અધિકારી, દબાણ હટાવ ટુકડી અથવા પોલીસે આ કાર્યવાહી કરી?",
            "incident_date": "તમારી લારી કે દુકાન કઈ તારીખે અને આશરે કેટલા વાગ્યે હટાવવામાં આવી?",
            "incident_location": "તમારી લારી કે સ્ટોલ કયા રસ્તા, માર્કેટ કે વોર્ડમાં સ્થિત હતી?",
        },
        "POLICE_CUSTODY": {
            "specific_details": "શું પોલીસે કોઈ લેખિત અરેસ્ટ મેમો અથવા કારણ આપ્યું છે, અને શું પરિવારજનોને જાણ કરી છે?",
            "other_party": "કયું પોલીસ સ્ટેશન, ચોકી અથવા કયા તપાસ અધિકારી આમાં સામેલ છે?",
            "incident_date": "તેમને ક્યારે (કઈ તારીખ અને સમયે) અટકમાં લેવામાં આવ્યા હતા?",
            "incident_location": "તેમને હાલમાં કયા પોલીસ સ્ટેશન, લોકઅપ કે સ્થળે રાખવામાં આવ્યા છે?",
        },
        "MOTOR_ACCIDENT_PRO": {
            "specific_details": "શું કોઈને ઈજા થઈ છે, વાહનોના નંબર શું છે, અને શું હોસ્પિટલનો મેડિકલ રિપોર્ટ છે?",
            "other_party": "ટક્કર મારનાર વાહનનો નંબર, ડ્રાઇવરનું નામ અથવા વીમા કંપની કઈ છે?",
            "incident_date": "આ અકસ્માત કઈ તારીખે અને આશરે કેટલા વાગ્યે થયો હતો?",
            "incident_location": "અકસ્માત કયા રસ્તા, હાઇવે અથવા ચાર રસ્તા પાસે થયો હતો?",
        },
        "REAL_ESTATE_RERA": {
            "specific_details": "પ્રોજેક્ટનો રેરા (RERA) નંબર શું છે અને કરારમાં કબજો આપવાની કઈ તારીખ આપી હતી?",
            "other_party": "બિલ્ડર, ડેવલપર અથવા કન્સ્ટ્રક્શન કંપનીનું કાનૂની નામ શું છે?",
            "incident_date": "ફ્લેટનો કરાર ક્યારે થયો હતો અને તમે છેલ્લો હપ્તો કઈ તારીખે ચૂકવ્યો હતો?",
            "incident_location": "આ હાઉસિંગ પ્રોજેક્ટ કયા શહેરમાં અને કયા સરનામે સ્થિત છે?",
        },
        "COMMERCIAL_CONTRACT_MSME": {
            "specific_details": "શું તમારી પેઢી MSME ઉદ્યોગમાં નોંધાયેલી છે, અને બિલની કુલ કેટલી રકમ બાકી છે?",
            "other_party": "ચૂકવણી રોકનાર ખરીદનાર કંપની અથવા વેપારીનું કાનૂની નામ શું છે?",
            "incident_date": "માલ કે સેવાઓ કઈ તારીખે પહોંચાડવામાં આવી હતી, અને શું ૪૫ દિવસનો સમય વીતી ગયો છે?",
            "incident_location": "આ વ્યાપારિક કરાર અથવા ડિલિવરી કયા શહેરમાં થઈ હતી?",
        },
        "LAND_GRABBING": {
            "specific_details": "જમીન પર કોનો કબજો છે અને તમારી પાસે ૭/૧૨, દસ્તાવેજ કે માલિકી હકના કયા પુરાવા છે?",
            "other_party": "જમીન પર ગેરકાયદે કબજો કે દબાણ કરનાર વ્યક્તિ કે સંસ્થા કોણ છે?",
            "incident_date": "જમીનની સીમ ક્યારે તોડવામાં આવી અથવા ગેરકાયદેસર પ્રવેશનો પ્રયાસ ક્યારે થયો?",
            "incident_location": "આ જમીન કયા ગામ, તાલુકા, સર્વે નંબર અને જિલ્લામાં આવેલી છે?",
        },
        "LOAN_FRAUD": {
            "specific_details": "લોન એપનું નામ શું છે, અને શું તેઓ તમારા સંપર્કોને ફોન કરીને કે ખોટા ફોટા મોકલીને બ્લેકમેલ કરે છે?",
            "other_party": "કઈ લોન એપ, રિકવરી એજન્ટ અથવા કંપની તમને હેરાન કરી રહી છે?",
            "incident_date": "ધમકીઓ, બ્લેકમેલિંગ અથવા ખાતામાંથી પૈસા કપાવાના ક્યારે શરૂ થયા?",
            "incident_location": "પૈસા કઈ બેંકમાંથી, યુપીઆઈ આઈડી અથવા એપ દ્વારા ટ્રાન્સફર થયા હતા?",
        },
        "DOMESTIC_VIOLENCE": {
            "specific_details": "શું તમે કે બાળકો અત્યારે કોઈ જોખમમાં છો, અને શું તમને તાત્કાલિક સુરક્ષિત આશ્રય કે તબીબી સહાયની જરૂર છે?",
            "other_party": "સામાયિક ઘરમાં તમને નુકસાન કે ધમકી આપનાર મુખ્ય વ્યક્તિ કોણ છે?",
            "incident_date": "હિંસા, મારપીટ અથવા ઘર બહાર કાઢવાની તાજી ઘટના ક્યારે બની હતી?",
            "incident_location": "આ ઘર કયા શહેરમાં કે જિલ્લામાં આવેલું છે?",
        },
        "CORRUPTION_RTI": {
            "specific_details": "આ કઈ સરકારી કચેરીનો કેસ છે, અને તમારી પાસે અરજી અથવા પહોંચ નંબર છે?",
            "other_party": "કયા અધિકારી કે જાહેર માહિતી અધિકારીએ કામ અટકાવ્યું અથવા લાંચ માંગી?",
            "incident_date": "તમે અરજી કઈ તારીખે કરી હતી, અને શું ૩૦ દિવસની કાનૂની મુદત પૂરી થઈ ગઈ છે?",
            "incident_location": "આ સરકારી કચેરી કયા શહેરમાં અથવા જિલ્લામાં આવેલી છે?",
        },
        "RELIGIOUS_GATHERING": {
            "specific_details": "પ્રાર્થના સભામાં કોઈએ વિક્ષેપ પાડ્યો કે લોકોને ધમકી આપી અથવા અટકમાં લીધા હતા?",
            "other_party": "પ્રાર્થના સભામાં કયા જૂથ, વ્યક્તિઓ અથવા પોલીસે હસ્તક્ષેપ કર્યો?",
            "incident_date": "આ ઘટના કઈ તારીખે અને કયા સમયે બની હતી?",
            "incident_location": "પ્રાર્થના સભા કયા સ્થળે કે મકાનમાં આયોજિત કરવામાં આવી હતી?",
        },
        "GENERAL_CITIZEN_AID": {
            "specific_details": "ખરેખર શું બન્યું હતું, અને તમને સૌથી પહેલા કયા પ્રકારની કાનૂની મદદ કે રાહત જોઈએ છે?",
            "other_party": "આમાં સામેલ બીજી વ્યક્તિ, કંપની અથવા સરકારી અધિકારી કોણ છે?",
            "incident_date": "આ ઘટના અથવા વિવાદ ક્યારે બન્યો હતો?",
            "incident_location": "આ ઘટના કયા શહેરમાં અથવા વિસ્તારમાં બની હતી?",
        },
    },
}



SPOKEN_TEMPLATES = {

    "en": {

        "first_turn": "Understood. {spec_q}",

        "incomplete": "Understood. {spec_q}",

        "complete": "All essential facts have been gathered. I have prepared your structured incident draft. You can preview it below or tell me any changes by voice.",

        "revised": "I have updated your incident summary per your instructions. Here is the revised draft for your review."

    },

    "hi": {

        "first_turn": "समझ गया। {spec_q}",

        "incomplete": "समझ गया। {spec_q}",

        "complete": "आपकी सभी जरूरी जानकारियां दर्ज हो गई हैं। हमने आपके लिए कानूनी ड्राफ्ट तैयार कर दिया है। आप इसे नीचे देख सकते हैं और कोई बदलाव हो तो बोलकर बता सकते हैं।",

        "revised": "मैंने आपके बताए अनुसार ड्राफ्ट में संशोधन कर दिया है। संशोधित ड्राफ्ट नीचे उपलब्ध है।"

    },

    "mr": {

        "first_turn": "समजले. {spec_q}",

        "incomplete": "समजले. {spec_q}",

        "complete": "तुमची सर्व आवश्यक माहिती नोंदवून घेण्यात आली आहे. आम्ही तुमच्यासाठी कायदेशीर मसुदा तयार केला आहे. आपण खाली तो पाहू शकता आणि काही बदल असल्यास बोलून सांगू शकता.",

        "revised": "मी तुमच्या सूचनेनुसार मसुद्यामध्ये बदल केला आहे. सुधारित मसुदा खाली दिला आहे."

    },

    "ta": {

        "first_turn": "புரிந்தது. {spec_q}",

        "incomplete": "புரிந்தது. {spec_q}",

        "complete": "உங்கள் விவரங்கள் அனைத்தும் பெறப்பட்டன. உங்களுக்கான சட்ட வரைவு ஆவணம் தயார் செய்யப்பட்டுள்ளது. கீழே அதை சரிபார்க்கலாம், மாற்றங்கள் இருந்தால் பேசலாம்.",

        "revised": "உங்கள் அறிவுறுத்தலின்படி வரைவு திருத்தப்பட்டது. புதுப்பிக்கப்பட்ட ஆவணம் கீழே உள்ளது."

    },

    "te": {

        "first_turn": "అర్థమైంది. {spec_q}",

        "incomplete": "అర్థమైంది. {spec_q}",

        "complete": "మీ పూర్తి వివరాలు నమోదు చేయబడ్డాయి. మేము మీ కోసం చట్టపరమైన డ్రాఫ్ట్ సిద్ధం చేసాము. మీరు క్రింద దాన్ని సమీక్షించవచ్చు మరియు మార్పులు ఉంటే మాట్లాడవచ్చు.",

        "revised": "మీ సూచనల ప్రకారం డ్రాఫ్ట్ అప్‌డేట్ చేయబడింది. సవరించిన డ్రాఫ్ట్ క్రింద సమీక్షించండి."

    },

    "kn": {

        "first_turn": "ತಿಳಿಯಿತು. {spec_q}",

        "incomplete": "ತಿಳಿಯಿತು. {spec_q}",

        "complete": "ನಿಮ್ಮ ಎಲ್ಲಾ ಅಗತ್ಯ ವಿವರಗಳನ್ನು ದಾಖಲಿಸಲಾಗಿದೆ. ನಿಮಗಾಗಿ ಕಾನೂನು ಕರಡು ಸಿದ್ಧಪಡಿಸಲಾಗಿದೆ. ನೀವು ಕೆಳಗೆ ಅದನ್ನು ಪರಿಶೀಲಿಸಬಹುದು ಮತ್ತು ಬದಲಾವಣೆಗಳಿದ್ದರೆ ಮಾತನಾಡಿ ತಿಳಿಸಬಹುದು.",

        "revised": "ನಿಮ್ಮ ಸೂಚನೆಗಳಂತೆ ಕರಡನ್ನು ನವೀಕರಿಸಲಾಗಿದೆ. ಪರಿಷ್ಕೃತ ಕರಡು ಕೆಳಗೆ ಲಭ್ಯವಿದೆ."

    },

    "bn": {

        "first_turn": "বুঝতে পেরেছি। {spec_q}",

        "incomplete": "বুঝতে পেরেছি। {spec_q}",

        "complete": "আপনার সমস্ত প্রয়োজনীয় তথ্য রেকর্ড করা হয়েছে। আমরা আপনার জন্য আইনি খসড়া প্রস্তুত করেছি। আপনি নিচে এটি দেখতে পারেন এবং কোনো পরিবর্তন থাকলে বলতে পারেন।",

        "revised": "আপনার নির্দেশনা অনুযায়ী খসড়া সংশোধন করা হয়েছে। সংশোধিত খসড়া নিচে দেখুন।"

    },

    "gu": {

        "first_turn": "સમજી ગયો. {spec_q}",

        "incomplete": "સમજી ગયો. {spec_q}",

        "complete": "તમારી બધી જરૂરી માહિતી નોંધી લેવામાં આવી છે. અમે તમારા માટે કાનૂની ડ્રાફ્ટ તૈયાર કર્યો છે. તમે નીચે તેની સમીક્ષા કરી શકો છો અને ફેરફાર હોય તો બોલી શકો છો.",

        "revised": "તમારી સૂચના મુજબ ડ્રાફ્ટમાં સુધારો કરવામાં આવ્યો છે. સુધારેલ ડ્રાફ્ટ નીચે જુઓ."

    },

    "ml": {

        "first_turn": "മനസ്സിലായി. {spec_q}",

        "incomplete": "മനസ്സിലായി. {spec_q}",

        "complete": "നിങ്ങളുടെ ആവശ്യമായ എല്ലാ വിവരങ്ങളും രേഖപ്പെടുത്തിയിട്ടുണ്ട്. നിങ്ങൾക്കായി നിയമപരമായ കരട് തയ്യാറാക്കിയിട്ടുണ്ട്. നിങ്ങൾക്ക് താഴെ അത് പരിശോധിക്കാം, മാറ്റങ്ങളുണ്ടെങ്കിൽ സംസാരിക്കാം.",

        "revised": "നിങ്ങളുടെ നിർദ്ദേശപ്രകാരം കരട് പുതുക്കി തയ്യാറാക്കിയിട്ടുണ്ട്. പുതുക്കിയ പകർപ്പ് താഴെ കാണാം."

    },

    "pa": {

        "first_turn": "ਸਮਝ ਗਿਆ। {spec_q}",

        "incomplete": "ਸਮਝ ਗਿਆ। {spec_q}",

        "complete": "ਤੁਹਾਡੀ ਸਾਰੀ ਲੋੜੀਂਦੀ ਜਾਣਕਾਰੀ ਦਰਜ ਕਰ ਲਈ ਗਈ ਹੈ। ਅਸੀਂ ਤੁਹਾਡੇ ਲਈ ਕਾਨੂੰਨੀ ਡਰਾਫਟ ਤਿਆਰ ਕਰ ਦਿੱਤਾ ਹੈ। ਤੁਸੀਂ ਹੇਠਾਂ ਇਸ ਦੀ ਜਾਂਚ ਕਰ ਸਕਦੇ ਹੋ ਅਤੇ ਤਬਦੀਲੀ ਲਈ ਬੋਲ ਸਕਦੇ ਹੋ।",

        "revised": "ਤੁਹਾਡੀ ਹਦਾਇਤ ਅਨੁਸਾਰ ਡਰਾਫਟ ਵਿੱਚ ਸੋਧ ਕੀਤੀ ਗਈ ਹੈ। ਸੋਧਿਆ ਹੋਇਆ ਡਰਾਫਟ ਹੇਠਾਂ ਦਿੱਤਾ ਗਿਆ ਹੈ।"

    }
}

CATEGORY_QUESTIONS = {
    "en": {
        "WAGE_THEFT": {
            "specific_details": "What work was done, for which employer, and what wages are unpaid?",
            "other_party": "Who was your immediate employer, contractor, or thekedar who refused to pay?",
            "incident_date": "Since when have these wages been pending, or when was the last date of work?",
            "incident_location": "Where was the worksite, construction project, or factory located?",
        },
        "STREET_VENDOR": {
            "specific_details": "Are you vending at this site, and did you receive a survey certificate or written notice?",
            "other_party": "Which municipal ward authority, anti-encroachment squad, or police station carried out the eviction?",
            "incident_date": "On what date and time was your cart or goods removed or seized?",
            "incident_location": "Where was your vending stall located (street, ward, or market area)?",
        },
        "POLICE_CUSTODY": {
            "specific_details": "Was anyone arrested or detained, and what did the police say or provide in writing?",
            "other_party": "Which police station, chowki, or investigating officers are involved?",
            "incident_date": "When (date and approximate time) was the person taken into custody?",
            "incident_location": "At which police station, lockup, or facility is the person being held?",
        },
        "MOTOR_ACCIDENT_PRO": {
            "specific_details": "Was anyone injured, which vehicles were involved, and what insurer and policy details are confirmed?",
            "other_party": "What was the vehicle number, driver name, or insurance company of the other vehicle?",
            "incident_date": "On what date and approximately what time did the accident happen?",
            "incident_location": "Where did the collision occur (highway, road junction, or landmark)?",
        },
        "REAL_ESTATE_RERA": {
            "specific_details": "What are the project registration number, promised possession date, and payment records?",
            "other_party": "What is the name of the builder, developer, or housing promoter entity?",
            "incident_date": "When was the allotment or agreement for sale signed, and what was your last payment date?",
            "incident_location": "In which city, locality, and project site is the property situated?",
        },
        "COMMERCIAL_CONTRACT_MSME": {
            "specific_details": "Was the supplier registered as a micro or small enterprise when the order was accepted, and when were the goods or services accepted?",
            "other_party": "What is the legal name of the corporate buyer or client holding the unpaid invoices?",
            "incident_date": "When were the goods or services delivered, and have 45 days passed?",
            "incident_location": "In which city or state was the commercial contract or delivery executed?",
        },
        "LAND_GRABBING": {
            "specific_details": "Who occupies the property now, and are there title, tenancy, or eviction papers?",
            "other_party": "Who is the trespasser, encroacher, or party attempting illegal possession?",
            "incident_date": "When was boundary demarcation damaged or illegal entry attempted?",
            "incident_location": "Where is the land situated (village, taluka, survey/gat number, or district)?",
        },
        "LOAN_FRAUD": {
            "specific_details": "Which app or person contacted you, what was requested, and what messages or transactions can you document?",
            "other_party": "What is the name of the digital lending app, recovery agency, or caller harassing you?",
            "incident_date": "When did the threats, unauthorized debits, or blackmail begin?",
            "incident_location": "Through which bank account, UPI ID, or digital platform did transactions take place?",
        },
        "DOMESTIC_VIOLENCE": {
            "specific_details": "Is anyone in immediate danger, and what support or safe contact method do you want?",
            "other_party": "Who is the respondent or person causing harm or threats in the shared household?",
            "incident_date": "When did the most recent incident of violence, harassment, or eviction threat occur?",
            "incident_location": "In which city or district is the shared household situated?",
        },
        "CORRUPTION_RTI": {
            "specific_details": "Which office or benefit is involved, and do you have an application or receipt number?",
            "other_party": "Which public official, department, or office demanded bribes or withheld service?",
            "incident_date": "When was your application or grievance submitted, and what was the deadline?",
            "incident_location": "In which municipal office, collectorate, or tehsil is this public office located?",
        },
        "RELIGIOUS_GATHERING": {
            "specific_details": "What occurred at the gathering, and were there threats, injuries, or a police report?",
            "other_party": "Which group, persons, or police personnel interfered with the peaceful gathering?",
            "incident_date": "On what date and time was the prayer or gathering disrupted?",
            "incident_location": "Where was the prayer hall or gathering held (premises address and locality)?",
        },
        "GENERAL_CITIZEN_AID": {
            "specific_details": "What happened, and what help do you want first?",
            "other_party": "Who is the other person, officer, company, or authority involved?",
            "incident_date": "When did this occur (date or time period)?",
            "incident_location": "Where did this happen (city, landmark, or jurisdiction)?",
        },
    },
    "hi": {
        "WAGE_THEFT": {
            "specific_details": "आप किस कंपनी या ठेकेदार के पास क्या काम करते थे, और आपकी कितनी मजदूरी बकाया है?",
            "other_party": "आपको काम पर रखने वाला ठेकेदार, सुपरवाइजर या कंपनी कौन सी है?",
            "incident_date": "यह मजदूरी किस महीने से बकाया है या आपने आखिरी बार काम कब किया था?",
            "incident_location": "काम की जगह, कंस्ट्रक्शन साइट या फैक्ट्री किस इलाके या शहर में थी?",
        },
        "STREET_VENDOR": {
            "specific_details": "क्या आपके पास वेंडिंग सर्टिफिकेट या टीवीसी रसीद है, और क्या नगर निगम ने कोई लिखित नोटिस दिया?",
            "other_party": "किस नगर निगम, अतिक्रमण विरोधी दस्ते या पुलिस थाने ने दुकान हटाई या सामान जब्त किया?",
            "incident_date": "आपकी दुकान या रेहड़ी किस तारीख और समय पर हटाई गई?",
            "incident_location": "आपकी दुकान किस बाजार, सड़क या वेंडिंग जोन में स्थित थी?",
        },
        "POLICE_CUSTODY": {
            "specific_details": "क्या पुलिस ने कोई लिखित अरेस्ट मेमो या कारण बताया, और क्या किसी रिश्तेदार को सूचना दी गई?",
            "other_party": "कौन सा पुलिस थाना, चौकी या जांच अधिकारी इस मामले में शामिल हैं?",
            "incident_date": "उन्हें कब (किस तारीख और समय पर) हिरासत में लिया गया था?",
            "incident_location": "उन्हें इस समय किस पुलिस थाने, लॉकअप या स्थान पर रखा गया है?",
        },
        "MOTOR_ACCIDENT_PRO": {
            "specific_details": "क्या किसी को चोट आई है, गाड़ियों के नंबर क्या हैं, और क्या अस्पताल का मेडिकल/एमएलसी पर्चा बना है?",
            "other_party": "टक्कर मारने वाली गाड़ी का नंबर, चालक का नाम या बीमा कंपनी कौन सी है?",
            "incident_date": "यह दुर्घटना किस तारीख को और लगभग किस समय हुई थी?",
            "incident_location": "हादसा किस सड़क, चौराहे, हाईवे या लैंडमार्क के पास हुआ?",
        },
        "REAL_ESTATE_RERA": {
            "specific_details": "प्रोजेक्ट का रेरा (RERA) रजिस्ट्रेशन नंबर क्या है और एग्रीमेंट में कब्जा देने की क्या तारीख थी?",
            "other_party": "बिल्डर, प्रमोटर या हाउसिंग कंपनी का पंजीकृत नाम क्या है?",
            "incident_date": "फ्लैट का एग्रीमेंट कब हुआ था, और आपने आखिरी किस्त किस तारीख को दी थी?",
            "incident_location": "हाउसिंग प्रोजेक्ट किस शहर, इलाके और पते पर स्थित है?",
        },
        "COMMERCIAL_CONTRACT_MSME": {
            "specific_details": "क्या आपकी फर्म MSME उद्यम में रजिस्टर्ड है, और इनवॉइस की कुल कितनी रकम बकाया है?",
            "other_party": "भुगतान रोकने वाली खरीदार कंपनी या कारोबारी का कानूनी नाम क्या है?",
            "incident_date": "माल या सेवाएं किस तारीख को डिलीवर की गई थीं, और क्या 45 दिन बीत चुके हैं?",
            "incident_location": "यह अनुबंध या डिलीवरी किस शहर अथवा राज्य में हुई थी?",
        },
        "LAND_GRABBING": {
            "specific_details": "जमीन पर किसका कब्जा है और आपके पास 7/12, रजिस्ट्री या मालिकाना हक के क्या दस्तावेज हैं?",
            "other_party": "जमीन पर अवैध कब्जा या अतिक्रमण करने वाला व्यक्ति या संस्था कौन है?",
            "incident_date": "जमीन की मेड़ कब तोड़ी गई या अवैध रूप से घुसने का प्रयास कब हुआ?",
            "incident_location": "यह जमीन किस गांव, तहसील, खसरा/सर्वे नंबर और जिले में स्थित है?",
        },
        "LOAN_FRAUD": {
            "specific_details": "लोन ऐप का नाम क्या है, और क्या वे आपके संपर्कों को फोन करके या फोटो एडिट करके ब्लैकमेल कर रहे हैं?",
            "other_party": "कौन सा लोन ऐप, फर्जी वसूली एजेंट या रिकवरी एजेंसी आपको परेशान कर रही है?",
            "incident_date": "धमकियां, ब्लैकमेलिंग या खाते से गलत कटौती कब शुरू हुई?",
            "incident_location": "पैसे किस बैंक खाते, यूपीआई आईडी या डिजिटल वॉलेट के जरिए ट्रांसफर हुए?",
        },
        "DOMESTIC_VIOLENCE": {
            "specific_details": "क्या आप या बच्चे इस समय किसी खतरे में हैं, और क्या आपको तुरंत सुरक्षित आश्रय या डॉक्टरी सहायता चाहिए?",
            "other_party": "साझा घर में आपको नुकसान या धमकी पहुंचाने वाला मुख्य व्यक्ति कौन है?",
            "incident_date": "हिंसा, मारपीट या घर से निकालने की धमकी की ताजा घटना कब हुई थी?",
            "incident_location": "साझा घर किस शहर या जिले में स्थित है?",
        },
        "CORRUPTION_RTI": {
            "specific_details": "यह किस सरकारी दफ्तर का मामला है, और आपके पास आवेदन या पावती संख्या क्या है?",
            "other_party": "किस अधिकारी, जन सूचना अधिकारी या विभाग ने काम रोका या रिश्वत की मांग की?",
            "incident_date": "आपने आवेदन किस तारीख को दिया था, और क्या 30 दिन की वैधानिक सीमा समाप्त हो गई है?",
            "incident_location": "यह सरकारी दफ्तर, कलेक्टरेट या नगर निगम किस शहर या जिले में है?",
        },
        "RELIGIOUS_GATHERING": {
            "specific_details": "क्या प्रार्थना सभा में बाधा डाली गई या लोगों को धमकाया अथवा हिरासत में लिया गया?",
            "other_party": "प्रार्थना सभा में किस समूह, व्यक्तियों या पुलिसकर्मियों ने हस्तक्षेप किया?",
            "incident_date": "यह घटना किस तारीख और समय पर घटी थी?",
            "incident_location": "प्रार्थना सभा या कार्यक्रम किस जगह या परिसर में आयोजित किया गया था?",
        },
        "GENERAL_CITIZEN_AID": {
            "specific_details": "क्या घटना घटी, और आपको सबसे पहले किस प्रकार की कानूनी मदद या राहत चाहिए?",
            "other_party": "इसमें संबंधित दूसरा व्यक्ति, कंपनी या सरकारी अधिकारी कौन है?",
            "incident_date": "यह घटना या विवाद किस तारीख को हुआ था?",
            "incident_location": "यह घटना किस शहर, इलाके या जगह पर घटी थी?",
        },
    },
    "mr": {
        "WAGE_THEFT": {
            "specific_details": "तुम्ही कोणत्या कंपनीत किंवा कंत्राटदाराकडे काय काम केले, आणि तुमचा किती पगार थकला आहे?",
            "other_party": "तुम्हाला कामावर ठेवणारा कंत्राटदार, सुपरवायझर किंवा मालक कोण आहे?",
            "incident_date": "हा पगार कोणत्या महिन्यांपासून थकला आहे किंवा कामाचा शेवटचा दिवस कोणता होता?",
            "incident_location": "कामाची जागा, बांधकाम साईट किंवा कारखाना कोणत्या भागात किंवा शहरात होता?",
        },
        "STREET_VENDOR": {
            "specific_details": "तुमच्याकडे फेरीवाला प्रमाणपत्र (वेंडिंग सर्टिफिकेट) किंवा पावती आहे का, आणि महापालिकेने काही लेखी नोटीस दिली का?",
            "other_party": "कोणत्या महापालिका प्रभाग अधिकाऱ्यांनी, अतिक्रमण विरोधी पथकाने किंवा पोलिसांनी ही कारवाई केली?",
            "incident_date": "तुमची गाडी कोणत्या तारखेला आणि साधारण किती वाजता हटवली गेली?",
            "incident_location": "तुमचा स्टॉल किंवा गाडी कोणत्या रस्त्यावर, मार्केटमध्ये किंवा प्रभागात होती?",
        },
        "POLICE_CUSTODY": {
            "specific_details": "पोलिसांनी अटकेचे लेखी कारण किंवा अरेस्ट मेमो दिला आहे का, आणि नातेवाईकांना माहिती दिली का?",
            "other_party": "कोणते पोलीस ठाणे, चौकी किंवा कोणते पोलीस अधिकारी यात सहभागी आहेत?",
            "incident_date": "त्यांना कोणत्या तारखेला आणि किती वाजता ताब्यात घेण्यात आले होते?",
            "incident_location": "त्यांना सध्या कोणत्या पोलीस ठाण्यात किंवा कोठडीत ठेवले आहे?",
        },
        "MOTOR_ACCIDENT_PRO": {
            "specific_details": "कोणाला दुखापत झाली आहे का, वाहनांचे क्रमांक काय आहेत, आणि हॉस्पिटलचा रिपोर्ट आहे का?",
            "other_party": "धडक देणाऱ्या दुसऱ्या वाहनाचा क्रमांक, चालक किंवा त्यांची विमा कंपनी कोणती आहे?",
            "incident_date": "हा अपघात कोणत्या दिवशी आणि साधारण किती वाजता घडला होता?",
            "incident_location": "हा अपघात कोणत्या रस्त्यावर, महामार्गावर किंवा चौकात झाला?",
        },
        "REAL_ESTATE_RERA": {
            "specific_details": "प्रकल्पाचा रेरा (RERA) नंबर काय आहे आणि करारनाम्यात ताबा देण्याची कोणती तारीख दिली होती?",
            "other_party": "बिल्डर, डेव्हलपर किंवा बांधकाम कंपनीचे नाव काय आहे?",
            "incident_date": "फ्लॅटचा करारनामा केव्हा झाला होता, आणि तुम्ही शेवटचा हप्ता कधी भरला?",
            "incident_location": "हा गृहनिर्माण प्रकल्प कोणत्या शहरात, भागात किंवा पत्त्यावर आहे?",
        },
        "COMMERCIAL_CONTRACT_MSME": {
            "specific_details": "तुमची संस्था MSME उद्यममध्ये नोंदणीकृत आहे का, आणि बिलाची एकूण किती रक्कम येणे बाकी आहे?",
            "other_party": "पैसे थकवणाऱ्या खरेदीदार कंपनीचे किंवा व्यापाऱ्याचे नाव काय आहे?",
            "incident_date": "माल किंवा सेवा कोणत्या तारखेला दिली होती, आणि ४५ दिवसांची मुदत संपली आहे का?",
            "incident_location": "हा व्यावसायिक करार किंवा डिलिव्हरी कोणत्या शहरात अथवा राज्यात झाली होती?",
        },
        "LAND_GRABBING": {
            "specific_details": "जमिनीवर कोणाचा ताबा आहे आणि तुमच्याकडे सातबारा, खरेदीखत किंवा मालकीहक्काचे काय कागदपत्रे आहेत?",
            "other_party": "जमिनीवर बेकायदेशीर ताबा किंवा अतिक्रमण करणारी व्यक्ती कोण आहे?",
            "incident_date": "जमिनीची हद्द केव्हा तोडली किंवा अतिक्रमण करण्याचा प्रयत्न कधी झाला?",
            "incident_location": "ही जमीन कोणत्या गावात, तालुक्यात, गट/सर्व्हे नंबरवर आणि जिल्ह्यात आहे?",
        },
        "LOAN_FRAUD": {
            "specific_details": "कर्ज ॲपचे नाव काय आहे, आणि ते तुमच्या संपर्कांना फोन करून किंवा खोटे फोटो पाठवून धमकावत आहेत का?",
            "other_party": "कोणते लोन ॲप, वसुली एजंट किंवा कोणती कंपनी तुम्हाला त्रास देत आहे?",
            "incident_date": "धमक्या, ब्लॅकमेलिंग किंवा खात्यातून परस्पर पैसे कापले जाणे केव्हा सुरू झाले?",
            "incident_location": "पैसे कोणत्या बँकेतून, यूपीआय आयडीवरून किंवा ॲपवरून कापले गेले?",
        },
        "DOMESTIC_VIOLENCE": {
            "specific_details": "तुम्हाला किंवा मुलांना सध्या काही धोका आहे का, आणि तुम्हाला सुरक्षित निवारा किंवा वैद्यकीय मदतीची गरज आहे का?",
            "other_party": "सामायिक घरामध्ये तुम्हाला त्रास किंवा इजा पोहोचवणारी व्यक्ती कोण आहे?",
            "incident_date": "हिंसाचाराची, शिवीगाळीची किंवा घराबाहेर काढण्याची ताजी घटना केव्हा घडली?",
            "incident_location": "सामायिक घर कोणत्या शहरात किंवा जिल्ह्यात आहे?",
        },
        "CORRUPTION_RTI": {
            "specific_details": "हे कोणत्या शासकीय कार्यालयाशी संबंधित आहे, आणि तुमच्याकडे अर्जाचा किंवा पावतीचा क्रमांक आहे का?",
            "other_party": "कोणत्या अधिकाऱ्याने किंवा जन माहिती अधिकाऱ्याने माहिती नाकारली किंवा लाच मागितली?",
            "incident_date": "तुम्ही अर्ज कधी केला होता, आणि ३० दिवसांची वैधानिक मुदत संपली आहे का?",
            "incident_location": "हे शासकीय कार्यालय, कलेक्टरेट किंवा महापालिका कोणत्या शहरात/जिल्ह्यात आहे?",
        },
        "RELIGIOUS_GATHERING": {
            "specific_details": "प्रार्थना सभेत कोणी अडथळा आणला किंवा लोकांना धमकावले/ताब्यात घेतले का?",
            "other_party": "प्रार्थना सभेत कोणत्या व्यक्तींनी, जमावाने किंवा पोलिसांनी हस्तक्षेप केला?",
            "incident_date": "ही घटना कोणत्या दिवशी आणि वेळेस घडली?",
            "incident_location": "प्रार्थना सभा कोणत्या सभागृहात किंवा जागेवर आयोजित केली होती?",
        },
        "GENERAL_CITIZEN_AID": {
            "specific_details": "नेमकी काय घटना घडली, आणि तुम्हाला सर्वप्रथम कोणती कायदेशीर मदत किंवा न्याय हवा आहे?",
            "other_party": "यामध्ये संबंधित दुसरी व्यक्ती, कंपनी किंवा शासकीय अधिकारी कोण आहे?",
            "incident_date": "ही घटना किंवा वाद केव्हा घडला होता?",
            "incident_location": "ही घटना कोणत्या शहरात, भागात किंवा ठिकाणी घडली?",
        },
    },
}



ACTION_STEPS = {

    "en": [

        "1. Answer the follow-up question by voice or text to complete the case intake.",

        "2. Preserve any notices, photographs, messages, receipts, and witness details safely.",

        "3. Ask the District Legal Services Authority (DLSA) about eligibility for free legal aid, or call NALSA at 15100.",

        "4. Have a qualified adviser check the law and filing deadline before sending the draft."

    ],

    "hi": [

        "1. ऊपर पूछे गए सवाल का जवाब बोलकर या लिखकर दें ताकि केस आगे बढ़ सके।",

        "2. घटना से जुड़े सभी सबूत, मैसेज, फोटो और रसीदें सुरक्षित रखें।",

        "3. मुफ्त सरकारी कानूनी सलाह और वकील के लिए तुरंत 15100 (नालसा / डीएलएसए) पर कॉल करें।",

        "4. किसी भी समझौते या पुलिस कागजात पर बिना वकील की सलाह के हस्ताक्षर न करें।"

    ],

    "mr": [

        "1. वरील प्रश्नाचे उत्तर बोलून किंवा लिहून द्या, जेणेकरून केस पुढे नेता येईल.",

        "2. घटनेशी संबंधित सर्व पुरावे, मेसेज, फोटो आणि पावत्या सुरक्षित ठेवा.",

        "3. मोफत सरकारी कायदेशीर सल्ला आणि वकिलासाठी तात्काळ 15100 (नालसा / डीएलएसए) वर कॉल करा.",

        "4. वकिलाच्या सल्ल्याशिवाय कोणत्याही तडजोडीच्या किंवा पोलीस कागदपत्रांवर स्वाक्षरी करू नका."

    ],

    "ta": [

        "1. வழக்கை தொடர மேலே கேட்கப்பட்ட கேள்விக்கு பேசி அல்லது எழுதி பதிலளிக்கவும்.",

        "2. சம்பவம் தொடர்பான அனைத்து ஆதாரங்கள், புகைப்படங்கள் மற்றும் ரசீதுகளை பாதுகாக்கவும்.",

        "3. இலவச அரசு சட்ட உதவிக்கு 15100 (DLSA / NALSA) என்ற எண்ணை அழைக்கவும்.",

        "4. வழக்கறிஞர் ஆலோசனையின்றி எந்த சமரச ஆவணத்திலும் கையெழுத்திட வேண்டாம்."

    ],

    "te": [

        "1. కేసును ముందుకు తీసుకెళ్లడానికి పైన అడిగిన ప్రశ్నకు మాట్లాడి లేదా రాసి సమాధానం ఇవ్వండి.",

        "2. సంఘటనకు సంబంధించిన అన్ని ఆధారాలు, ఫోటోలు మరియు రసీదులను భద్రపరచండి.",

        "3. ఉచిత ప్రభుత్వ న్యాయ సలహా కోసం 15100 (DLSA / NALSA) కు కాల్ చేయండి.",

        "4. న్యాయవాది సలహా లేకుండా ఎలాంటి రాజీ పత్రాలపై సంతకం చేయవద్దు."

    ],

    "kn": [

        "1. ಪ್ರಕರಣವನ್ನು ಮುಂದುವರಿಸಲು ಮೇಲೆ ಕೇಳಿದ ಪ್ರಶ್ನೆಗೆ ಮಾತನಾಡಿ ಅಥವಾ ಬರೆದು ಉತ್ತರಿಸಿ.",

        "2. ಘಟನೆಗೆ ಸಂಬಂಧಿಸಿದ ಎಲ್ಲಾ ಸಾಕ್ಷ್ಯಗಳು, ಫೋಟೋಗಳು ಮತ್ತು ರಸೀದಿಗಳನ್ನು ಸುರಕ್ಷಿತವಾಗಿರಿಸಿ.",

        "3. ಉಚಿತ ಸರ್ಕಾರಿ ಕಾನೂನು ನೆರವಿಗಾಗಿ 15100 (DLSA / NALSA) ಗೆ ಕರೆ ಮಾಡಿ.",

        "4. ವಕೀಲರ ಸಲಹೆಯಿಲ್ಲದೆ ಯಾವುದೇ ರಾಜಿ ಪತ್ರಗಳಿಗೆ ಸಹಿ ಮಾಡಬೇಡಿ."

    ],

    "bn": [

        "1. কেস এগিয়ে নিতে উপরের প্রশ্নের উত্তর কথা বলে বা লিখে দিন।",

        "2. ঘটনার সমস্ত প্রমাণ, ছবি এবং রসিদ নিরাপদে রাখুন।",

        "3. বিনামূল্যে সরকারি আইনি সহায়তার জন্য অবিলম্বে 15100 (DLSA / NALSA) নম্বরে কল করুন।",

        "4. আইনজীবীর পরামর্শ ছাড়া কোনো আপস বা সমঝোতা পত্রে স্বাক্ষর করবেন না।"

    ],

    "gu": [

        "1. કેસ આગળ વધારવા માટે ઉપર પૂછેલા પ્રશ્નનો જવાબ બોલીને અથવા લખીને આપો.",

        "2. ઘટના સંબંધિત તમામ પુરાવા, ફોટા અને રસીદો સુરક્ષિત રાખો.",

        "3. મફત સરકારી કાનૂની સલાહ માટે તાત્કાલિક 15100 (DLSA / NALSA) પર કૉલ કરો.",

        "4. વકીલની સલાહ વિના કોઈપણ સમાધાન દસ્તાવેજ પર સહી ન કરો."

    ],

    "ml": [

        "1. കേസ് മുന്നോട്ട് കൊണ്ടുപോകാൻ മുകളിൽ ചോദിച്ച ചോദ്യത്തിന് സംസാരിച്ചോ എഴുതിയോ മറുപടി നൽകുക.",

        "2. സംഭവവുമായി ബന്ധപ്പെട്ട എല്ലാ തെളിവുകളും ഫോട്ടോകളും രസീതുകളും സുരക്ഷിതമായി സൂക്ഷിക്കുക.",

        "3. സൗജന്യ നിയമസഹಾಯത്തിനായി 15100 (DLSA / NALSA) എന്ന നമ്പറിൽ വിളിക്കുക.",

        "4. അഭിഭാഷകന്റെ ഉപദേശമില്ലാതെ യാതൊരു ഒത്തുതീർപ്പ് രേഖകളിലും ഒപ്പിടരുത്."

    ],

    "pa": [

        "1. ਕੇਸ ਨੂੰ ਅੱਗੇ ਵਧਾਉਣ ਲਈ ਉੱਪਰ ਪੁੱਛੇ ਗਏ ਸਵਾਲ ਦਾ ਜਵਾਬ ਬੋਲ ਕੇ ਜਾਂ ਲਿਖ ਕੇ ਦਿਓ।",

        "2. ਘਟਨਾ ਨਾਲ ਸਬੰਧਤ ਸਾਰੇ ਸਬੂਤ, ਫੋਟੋਆਂ ਅਤੇ ਰਸੀਦਾਂ ਸੁਰੱਖਿਅਤ ਰੱਖੋ।",

        "3. ਮੁਫ਼ਤ ਸਰਕਾਰੀ ਕਾਨੂੰਨੀ ਸਹਾਇਤਾ ਲਈ ਤੁਰੰਤ 15100 (DLSA / NALSA) 'ਤੇ ਕਾਲ ਕਰੋ।",

        "4. ਵਕੀਲ ਦੀ ਸਲਾਹ ਤੋਂ ਬਿਨਾਂ ਕਿਸੇ ਵੀ ਸਮਝੌਤੇ ਦੇ ਦਸਤਾਵੇਜ਼ 'ਤੇ ਦਸਤਖਤ ਨਾ ਕਰੋ।"

    ]

}



def detect_language(text: str, lang_code: Optional[str] = None, detected_language: Optional[str] = None, session_language: Optional[str] = None) -> str:
    """Accurately detects one of the 10 supported Indic languages or English:
    'mr', 'hi', 'ta', 'te', 'kn', 'bn', 'gu', 'ml', 'pa', 'en'.
    Prioritizes actual spoken/transcribed text and explicit ASR acoustic detection over fallback defaults.
    """
    text = text or ""
    lower_text = text.lower()

    # 1. Distinct Non-Devanagari Unicode script block detection (most definitive)
    if any("\u0B80" <= ch <= "\u0BFF" for ch in text): return "ta"
    if any("\u0C00" <= ch <= "\u0C7F" for ch in text): return "te"
    if any("\u0C80" <= ch <= "\u0CFF" for ch in text): return "kn"
    if any("\u0D00" <= ch <= "\u0D7F" for ch in text): return "ml"
    if any("\u0980" <= ch <= "\u09FF" for ch in text): return "bn"
    if any("\u0A80" <= ch <= "\u0AFF" for ch in text): return "gu"
    if any("\u0A00" <= ch <= "\u0A7F" for ch in text): return "pa"

    def _extract_base_lang(val: Optional[str]) -> Optional[str]:
        if not val:
            return None
        v = str(val).lower().strip()
        if v in ("indic-auto", "auto", "default", "none"):
            return None
        for code in ["mr", "hi", "ta", "te", "kn", "bn", "gu", "ml", "pa", "en"]:
            if code in v:
                return code
        return None

    explicit_user_lang = _extract_base_lang(lang_code)
    asr_detected_lang = _extract_base_lang(detected_language)
    sess_lang = _extract_base_lang(session_language)

    # 2. Devanagari script: Marathi vs Hindi discrimination
    has_devanagari = any("\u0900" <= ch <= "\u097F" for ch in text)

    if has_devanagari:
        # Unique Marathi phonetic characters (never present in standard Hindi)
        if "ळ" in text or "ऱ" in text:
            return "mr"

        distinct_mr_markers = {
            "आहे", "आहेत", "आहोत", "नाही", "नाहीत", "नका",
            "झाला", "झाली", "झाले", "झालं", "झाल्या", "झालेलो",
            "केले", "केला", "केली", "केलं", "केल्या",
            "दिले", "दिला", "दिली", "दिलं", "दिल्या",
            "नेले", "नेला", "नेली", "नेलं", "नेल्या",
            "आणले", "आणला", "आणली", "आणलं",
            "ठेवले", "ठेवला", "ठेवली", "ठेवलं",
            "हटवले", "हटवला", "हटवली", "हटवलं",
            "तोडले", "तोडला", "तोडली", "तोडलं",
            "काढले", "काढला", "काढली", "काढलं",
            "मागितले", "मागितला", "मागितली",
            "सांगितले", "सांगितला", "सांगितली", "सांगा", "सांग",
            "गेलो", "गेला", "गेली", "गेले", "गेलं",
            "होतो", "होती", "होते", "होता", "नव्हते", "नव्हता", "नव्हती", "नव्हतं",
            "पाहिजे", "पाहिजेत",
            "माझा", "माझी", "माझे", "माझ्या", "माझं",
            "मला", "मी", "आम्ही", "आम्हाला", "आमचे", "आमची", "आमच्या", "आमचं",
            "त्यांनी", "त्याला", "तिला", "त्यांना", "त्याचे", "त्याची", "त्यांच्या",
            "आपले", "आपली", "आपल्या",
            "मध्ये", "साठी", "आणि", "किंवा", "परंतु",
            "केव्हा", "कुठे", "कोणी", "कशा", "कसे", "कशी", "कसा",
            "तक्रार", "मारहाण", "सातबारा", "वाजता", "रस्त्यावर", "धडकली"
        }

        distinct_hi_markers = {
            "है", "हैं", "हूँ", "हो", "था", "थी", "थे", "रहा", "रही", "रहे",
            "नहीं", "नही", "मत", "ना",
            "हुआ", "हुई", "हुए",
            "किया", "किए", "की", "कर", "करता", "करती", "करते",
            "दिया", "दिए", "दी", "दे", "देता", "देती", "देते",
            "लिया", "लिए", "ली", "ले", "लेता", "लेती", "लेते",
            "गया", "गई", "गए", "जा", "जाता", "जाती", "जाते",
            "कहा", "कही", "कहे", "बोला", "बोली", "बोले", "बोल",
            "तोड़ा", "तोड़ी", "तोड़े", "हटाया", "हटाई", "हटाए",
            "रखा", "रखी", "रखे", "लाया", "लाई", "लाए",
            "छीना", "छीनी", "छीने", "मारा", "मारी", "मारे",
            "मांगा", "मांगी", "मांगे",
            "चाहिए", "सकता", "सकती", "सकते",
            "मेरा", "मेरी", "मेरे",
            "मुझे", "मुझको", "मैं", "मुझसे",
            "हम", "हमें", "हमारा", "हमारी", "हमारे", "हमसे",
            "उसने", "उसको", "उसे", "उसका", "उसकी", "उसके", "उससे",
            "उन्होंने", "उनको", "उन्हें", "उनका", "उनकी", "उनके", "उनसे",
            "इसने", "इसको", "इसे", "इसका", "इसकी", "इसके",
            "इन्होंने", "इनको", "इन्हें", "इनका", "इनकी", "इनके",
            "आप", "आपको", "आपका", "आपकी", "आपके",
            "में", "पर", "से", "को", "का", "के", "और", "लेकिन", "किन्तु", "या", "ताकि", "क्योंकि", "कि",
            "क्या", "कब", "कहाँ", "कैसे", "कैसा", "कैसी", "किसने", "किसको", "किसे", "क्यों",
            "साहब", "नमस्ते", "प्रणाम", "जी", "भैया", "बाबू",
            "तनख्वाह", "ठेला", "रेहड़ी", "झगड़ा", "मारपीट", "थाने"
        }

        words = set(re.findall(r"[\u0900-\u097F]+", text))
        mr_score = len(words.intersection(distinct_mr_markers))
        hi_score = len(words.intersection(distinct_hi_markers))

        # Check explicit prior signals (ASR acoustic detection or user dropdown)
        prior_lang = asr_detected_lang or explicit_user_lang or sess_lang

        if prior_lang == "hi":
            # Honor Hindi unless unambiguous Marathi markers strongly outweigh Hindi
            if mr_score > hi_score and mr_score >= 2:
                return "mr"
            return "hi"

        if prior_lang == "mr":
            # Honor Marathi unless unambiguous Hindi markers strongly outweigh Marathi
            if hi_score > mr_score and hi_score >= 2:
                return "hi"
            return "mr"

        # If no prior bias:
        if mr_score > hi_score:
            return "mr"
        elif hi_score > mr_score:
            return "hi"

        # Tied score or 0 score Devanagari:
        if prior_lang in ("mr", "hi"):
            return prior_lang

        # Default neutral Devanagari to Hindi (India's primary lingua franca)
        return "hi"

    # 3. Transliterated / Romanized Indic vocabulary markers
    english_markers = {
        "the", "is", "at", "without", "giving", "reasons", "and", "to", "in", "of",
        "for", "with", "on", "that", "this", "from", "by", "an", "be", "are", "was", "were",
        "they", "their", "them", "brother", "sister", "police", "detained", "court", "officer",
        "station", "arrested", "custody", "contractor", "wages", "vehicle", "driver", "insurance",
        "please", "help", "hello", "sir", "madam", "report", "complaint", "money", "accident"
    }
    distinct_mr_roman = {
        "majha", "majhi", "majhe", "majhyavar", "jhala", "jhali", "jhale", "jhal",
        "aahe", "aahet", "kela", "keli", "kele",
        "thukli", "thanayt", "kamavar", "bhandan", "marhan", "kasa", "kashi",
        "kevha", "kuthe", "sanga", "sangitla", "aani", "pahije", "bagha", "nighala"
    }
    distinct_hi_roman = {
        "mera", "meri", "mere", "mujhe", "mujhko", "hum", "humko", "humara", "humari",
        "hua", "hui", "hue", "kiya", "kiye", "diya", "diye", "liya", "liye",
        "hai", "hain", "hoon", "tha", "thi", "nahi", "nahin", "mat",
        "takkar", "paisa", "paise", "pulis", "thana", "maalik", "vetan",
        "batao", "namaste", "madat", "thela", "tod", "chahiye", "bol", "bola", "bole", "kaha"
    }

    roman_words = set(re.findall(r"\b[a-z]+\b", lower_text))
    en_r_score = len(roman_words.intersection(english_markers))
    mr_r_score = len(roman_words.intersection(distinct_mr_roman))
    hi_r_score = len(roman_words.intersection(distinct_hi_roman))

    if en_r_score >= 3 and en_r_score > (hi_r_score + mr_r_score):
        return "en"
    if mr_r_score > hi_r_score and mr_r_score > en_r_score:
        return "mr"
    elif hi_r_score > mr_r_score and hi_r_score > en_r_score:
        return "hi"

    ta_roman = ["enna", "ennoda", "aachu", "aayidichu", "illa", "vandhu", "kaaru", "thala", "panam", "udhavi", "vanakkam", "sollunga"]
    if any(re.search(rf"\b{w}\b", lower_text) for w in ta_roman):
        return "ta"

    te_roman = ["naaku", "ayyindi", "kaaru", "ledu", "sahayam", "emiti", "cheppandi", "namaskaram", "dhanyavadalu"]
    if any(re.search(rf"\b{w}\b", lower_text) for w in te_roman):
        return "te"

    kn_roman = ["nanna", "nannadu", "aayitu", "illa", "sahaya", "hege", "namaskara", "dhanyavada"]
    if any(re.search(rf"\b{w}\b", lower_text) for w in kn_roman):
        return "kn"

    bn_roman = ["aamar", "hoyechhe", "gaari", "taka", "sahajjo", "ki", "bolun", "nomoshkar"]
    if any(re.search(rf"\b{w}\b", lower_text) for w in bn_roman):
        return "bn"

    gu_roman = [
        "maru", "mari", "maro", "mara", "mane", "ame", "amne", "amaro", "amari",
        "thayu", "thayo", "thaya", "thayel", "nathi", "kem", "aabhar", "chhe", "chho", "chhiye",
        "paisa", "rakam", "aapyu", "aapya", "laavya", "joyiye", "saheb", "tamne", "tamaro", "tamari",
        "pagar", "feriwala", "lariyawala", "dokan", "nokari", "sheth", "bapuji", "shikayat"
    ]
    if any(re.search(rf"\b{w}\b", lower_text) for w in gu_roman):
        return "gu"

    pa_roman = ["hoya", "hoyi", "tussi", "assi", "kade", "paaji", "sat sri akal"]
    if any(re.search(rf"\b{w}\b", lower_text) for w in pa_roman):
        return "pa"

    # 4. Check explicit selections/ASR signals if text has no script indicators
    if asr_detected_lang:
        return asr_detected_lang
    if explicit_user_lang:
        return explicit_user_lang
    if sess_lang:
        return sess_lang

    return "en"



def is_indic_text(text: str, lang_code: Optional[str] = None) -> bool:

    return detect_language(text, lang_code) in ["hi", "mr", "ta", "te", "kn", "bn", "gu", "ml", "pa"]





def _build_ai_synthesized_narrative(category: str, facts: Dict[str, Any], transcript: str, lang: str) -> str:

    """Synthesizes a coherent, professional legal incident summary in the AI's own words.

    Does not invent unconfirmed facts; organizes what transpired into an articulate synopsis.

    """

    name = facts.get("client_name") or "The aggrieved citizen"

    date_str = facts.get("incident_date") or "the stated date"

    loc_str = facts.get("incident_location") or "the stated location"

    party_str = facts.get("other_party") or "the adverse party"

    spec_str = facts.get("specific_details") or ""



    cat_narratives = {

        "MOTOR_ACCIDENT_PRO": (

            f"The complainant, {name}, was involved in a motor vehicle collision occurring on or about {date_str} "

            f"at {loc_str}. The incident involved {party_str}. "

            + (f"Substantive facts established during intake indicate that: {spec_str} " if spec_str else "The collision resulted in vehicular impact and damages requiring urgent claim documentation and liability determination. ")

            + "Statutory provisions under the Motor Vehicles Act, 2019 apply."

        ),

        "STREET_VENDOR": (

            f"The complainant, {name}, an urban street vendor operating at {loc_str}, experienced an eviction action on or about {date_str} "

            f"involving {party_str}. "

            + (f"Specific facts recorded: {spec_str} " if spec_str else "Municipal authorities or law enforcement attempted arbitrary eviction or cart confiscation. ")

            + "Under Section 3(3) of The Street Vendors Act, 2014, vendors are shielded from eviction until statutory Town Vending Committee surveys are completed."

        ),

        "WAGE_THEFT": (

            f"The complainant, {name}, engaged in employment services at {loc_str}, reports unlawful withholding of earned remuneration by {party_str} "

            f"in relation to the period around {date_str}. "

            + (f"Substantive wage details: {spec_str} " if spec_str else "Earned wages have been withheld without lawful deduction justification. ")

            + "Under the Code on Wages, 2019, wages must be disbursed on time without unauthorized deductions."

        ),

        "LOAN_FRAUD": (

            f"The complainant, {name}, reports coercive harassment and unlawful recovery practices occurring on or about {date_str} "

            f"associated with {party_str}. "

            + (f"Incident specifics: {spec_str} " if spec_str else "The lending entity engaged in unauthorized contact access and extortion. ")

            + "Such practices violate RBI Digital Lending Guidelines and provisions of the Information Technology Act, 2000."

        ),

        "POLICE_CUSTODY": (

            f"The complainant, {name}, reports detention and police action occurring on or about {date_str} at {loc_str} "

            f"involving {party_str}. "

            + (f"Custodial specifics: {spec_str} " if spec_str else "Detention occurred requiring adherence to statutory procedural safeguards. ")

            + "Mandatory arrest memo execution and production before a Magistrate within 24 hours are governed by BNSS Sections 36, 47 and Article 22(2)."

        ),

        "DOMESTIC_VIOLENCE": (

            f"The complainant, {name}, reports domestic abuse and threats to safety occurring on or about {date_str} at {loc_str} "

            f"involving {party_str}. "

            + (f"Specific circumstances: {spec_str} " if spec_str else "Safety and residence protections are sought. ")

            + "The Protection of Women from Domestic Violence Act, 2005 provides urgent statutory remedies including protection and residence orders."

        ),

        "REAL_ESTATE_RERA": (

            f"The complainant, {name}, an allottee at {loc_str}, reports failure of timely possession handover around {date_str} "

            f"by {party_str}. "

            + (f"Transaction particulars: {spec_str} " if spec_str else "The promoter defaulted on agreed handover timelines. ")

            + "Section 18 of RERA, 2016 entitles allottees to claim delay compensation and statutory interest."

        ),

        "COMMERCIAL_CONTRACT_MSME": (

            f"The complainant, {name}, reports commercial supply default occurring on or about {date_str} at {loc_str} "

            f"involving {party_str}. "

            + (f"Invoicing particulars: {spec_str} " if spec_str else "Supplied goods or services remain unpaid beyond statutory windows. ")

            + "Section 15 of the MSMED Act, 2006 mandates compound interest on delayed payments beyond 45 days."

        ),

        "LAND_GRABBING": (

            f"The complainant, {name}, reports unlawful property encroachment and dispossession at {loc_str} on or about {date_str} "

            f"involving {party_str}. "

            + (f"Property specifics: {spec_str} " if spec_str else "Adverse occupation has occurred without lawful title or eviction decree. ")

            + "Redress lies under the Specific Relief Act and Bharatiya Nyaya Sanhita criminal trespass provisions."

        ),

        "CORRUPTION_RTI": (

            f"The complainant, {name}, reports corrupt inducement or denial of public service occurring on or about {date_str} at {loc_str} "

            f"involving {party_str}. "

            + (f"Details: {spec_str} " if spec_str else "Public administrative officials demanded unlawful gratification. ")

            + "Governed by the Prevention of Corruption Act, 1988 and the Right to Information Act, 2005."

        ),

        "RELIGIOUS_GATHERING": (

            f"The complainant, {name}, reports unlawful disruption of a peaceful assembly on or about {date_str} at {loc_str} "

            f"involving {party_str}. "

            + (f"Disruption specifics: {spec_str} " if spec_str else "A lawful assembly was intimidated or disrupted. ")

            + "Article 25 of the Constitution and relevant Bharatiya Nyaya Sanhita provisions protect the right to peaceful assembly."

        ),

        "GENERAL_CITIZEN_AID": (

            f"The complainant, {name}, reports a statutory grievance occurring on or about {date_str} at {loc_str} "

            f"involving {party_str}. "

            + (f"Facts noted: {spec_str} " if spec_str else "The matter requires formal legal evaluation. ")

            + "Preliminary evaluation indicates need for legal aid referral and counsel review."

        )

    }



    base_summary = cat_narratives.get(category, cat_narratives["GENERAL_CITIZEN_AID"])



    if lang == "mr":

        return (

            f"प्रस्तुत तक्रार: तक्रारदार {name} यांनी {loc_str} येथे {date_str} च्या सुमारास {party_str} यांच्या संदर्भात तक्रार नोंदवली आहे. "

            + (f"मुख्य वस्तुस्थिती: {spec_str} " if spec_str else "या प्रकरणी कायदेशीर अधिकार आणि संरक्षणाची गरज आहे. ")

            + f"\n\n[English Legal Synopsis for Counsel Review]:\n{base_summary}"

        )

    elif lang == "hi":

        return (

            f"प्रस्तुत शिकायत: शिकायतकर्ता {name} ने {loc_str} में {date_str} के आसपास {party_str} के संबंध में शिकायत दर्ज की है। "

            + (f"मुख्य तथ्य: {spec_str} " if spec_str else "इस मामले में वैधानिक अधिकारों और संरक्षण की आवश्यकता है। ")

            + f"\n\n[English Legal Synopsis for Counsel Review]:\n{base_summary}"

        )
    elif lang == "gu":
        return (
            f"રજૂ કરેલ ફરિયાદ: અરજદાર {name} એ {loc_str} ખાતે {date_str} ની આસપાસ {party_str} સામે ફરિયાદ નોંધાવી છે. "
            + (f"મુખ્ય હકીકત: {spec_str} " if spec_str else "આ બાબતમાં કાનૂની અધિકારો અને રક્ષણની જરૂર છે. ")
            + f"\n\n[English Legal Synopsis for Counsel Review]:\n{base_summary}"
        )

    return base_summary


LEGAL_NOTICE_CATEGORY_DATA = {
    "WAGE_THEFT": {
        "title": {
            "en": "Unlawful Withholding of Earned Wages and Non-Payment of Remuneration",
            "hi": "बकाया मजदूरी का गैरकानूनी भुगतान रोके जाना एवं पारिश्रमिक की अदायगी",
            "mr": "थकबाकी मजुरी रोखून ठेवणे आणि वेतनाचे गैरकायदेशीर उल्लंघन",
        },
        "act": {
            "en": "Code on Wages, 2019 (Sections 17 and 45)",
            "hi": "मजदूरी संहिता, 2019 (धारा 17 एवं 45)",
            "mr": "वेतन संहिता, 2019 (कलम 17 आणि 45)",
        },
        "contraventions": {
            "en": "Unlawful non-payment and withholding of earned wages beyond statutory wage periods without lawful justification, in contravention of Sections 17 and 45 of the Code on Wages, 2019.",
            "hi": "वैधानिक मजदूरी अवधि बीत जाने के बाद भी बिना किसी वैध कारण के बकाया मजदूरी का भुगतान न करना और रोकना, जो मजदूरी संहिता, 2019 की धारा 17 एवं 45 का सीधा उल्लंघन है।",
            "mr": "कायदेशीर मुदत संपल्यानंतरही कोणत्याही वैध कारणाशिवाय कमावलेली मजुरी रोखून ठेवणे, जे वेतन संहिता, 2019 च्या कलम 17 आणि 45 चे थेट उल्लंघन आहे.",
        },
        "reliefs": {
            "en": "Immediate disbursement of full withheld wages and overtime arrears along with statutory interest at the prescribed rate, and issuance of formal wage slips.",
            "hi": "रोकी गई समस्त बकाया मजदूरी एवं ओवरटाइम राशि का वैधानिक ब्याज सहित तत्काल भुगतान, तथा औपचारिक वेतन पर्चियां प्रदान करना।",
            "mr": "रोखून ठेवलेली संपूर्ण थकबाकी मजुरी व ओव्हरटाईम रक्कम वैधानिक व्याजासह त्वरित देणे, आणि अधिकृत वेतन पावती देणे.",
        },
    },
    "STREET_VENDOR": {
        "title": {
            "en": "Unlawful Eviction, Seizure of Vending Goods, and Interference with Vending Rights",
            "hi": "स्ट्रीट वेंडर की गैरकानूनी बेदखली, सामान जब्ती एवं आजीविका के अधिकार का हनन",
            "mr": "फेरीवाल्यांची गैरकायदेशीर बेदखली, माल जप्ती आणि उपजीविकेच्या हक्कावर गदा",
        },
        "act": {
            "en": "Street Vendors (Protection of Livelihood and Regulation of Street Vending) Act, 2014 (Sections 3 and 18)",
            "hi": "स्ट्रीट वेंडर्स (आजीविका संरक्षण और स्ट्रीट वेंडिंग विनियमन) अधिनियम, 2014 (धारा 3 एवं 18)",
            "mr": "स्ट्रीट व्हेंडर्स (उपजीविका संरक्षण आणि नियमन) कायदा, 2014 (कलम 3 आणि 18)",
        },
        "contraventions": {
            "en": "Arbitrary eviction, harassment, and confiscation of vending cart and stock without conducting Town Vending Committee (TVC) survey or statutory notice under Section 3(3) and Section 18 of The Street Vendors Act, 2014.",
            "hi": "टाउन वेंडिंग कमेटी (TVC) सर्वेक्षण और धारा 3(3) व धारा 18 के तहत आवश्यक वैधानिक प्रक्रिया का पालन किए बिना स्ट्रीट वेंडर की गाड़ी व माल को मनमाने ढंग से जब्त करना और बेदखल करना।",
            "mr": "टाऊन व्हेंडिंग कमिटी (TVC) सर्वेक्षण आणि स्ट्रीट व्हेंडर्स कायदा, 2014 च्या कलम 3(3) आणि कलम 18 अंतर्गत वैधानिक प्रक्रियेशिवाय फेरीवाल्याची हातगाडी व माल जप्त करणे आणि बेदखल करणे.",
        },
        "reliefs": {
            "en": "Immediate restoration of vending spot, return of seized vending cart and perishable/non-perishable goods intact, preservation of status quo pending TVC survey, and cessation of coercive eviction.",
            "hi": "वेंडिंग स्थल की तत्काल पुनर्बहाली, जब्त की गई वेंडिंग गाड़ी व सामग्री की वापसी, TVC सर्वेक्षण लंबित रहने तक यथास्थिति बनाए रखना एवं मनमानी बेदखली रोकना।",
            "mr": "फेरीचे मूळ ठिकाण त्वरित पूर्ववत करणे, जप्त केलेली हातगाडी व माल सुस्थितीत परत करणे, TVC सर्वेक्षण पूर्ण होईपर्यंत जैसे थे परिस्थिती ठेवणे आणि कारवाई थांबवणे.",
        },
    },
    "REAL_ESTATE_RERA": {
        "title": {
            "en": "Default in Timely Possession Handover and Breach of Builder-Buyer Obligations",
            "hi": "आवासीय इकाई के कब्जे में अनुचित देरी एवं RERA अधिनियम का उल्लंघन",
            "mr": "घराचा वेळेत ताबा न देणे आणि रेरा कायद्याचे उल्लंघन",
        },
        "act": {
            "en": "Real Estate (Regulation and Development) Act, 2016 (Section 18)",
            "hi": "भू-संपदा (विनियमन एवं विकास) अधिनियम, 2016 (धारा 18)",
            "mr": "रिअल इस्टेट (नियमन आणि विकास) कायदा, 2016 (कलम 18)",
        },
        "contraventions": {
            "en": "Failure to complete construction and hand over lawful physical possession of the booked unit with Occupancy Certificate within the committed statutory date under Section 18 of RERA, 2016.",
            "hi": "रेरा अधिनियम, 2016 की धारा 18 के अंतर्गत निर्धारित समयावधि में वैध अधिभोग प्रमाण-पत्र (OC) के साथ आवासीय इकाई का भौतिक कब्जा सौंपने में विफलता।",
            "mr": "रेरा कायदा, 2016 च्या कलम 18 अन्वये दिलेल्या मुदतीत भोगवटा प्रमाणपत्रासह (OC) घराचा प्रत्यक्ष ताबा देण्यात आलेले अपयश.",
        },
        "reliefs": {
            "en": "Immediate execution of registered possession with Occupancy Certificate or payment of prescribed monthly delay interest from due date until handover, or full refund of deposited consideration with interest under Section 18.",
            "hi": "वैध अधिभोग प्रमाण-पत्र के साथ कब्जे का तत्काल निष्पादन अथवा नियत तिथि से कब्जा मिलने तक निर्धारित मासिक विलंब ब्याज का भुगतान, या धारा 18 के तहत संपूर्ण राशि की वापसी।",
            "mr": "भोगवटा प्रमाणपत्रासह ताबा त्वरित देणे किंवा देय तारखेपासून प्रत्यक्ष ताब्यापर्यंत विहित मासिक विलंब व्याजाची भरपाई, अथवा संपूर्ण भरलेल्या रकमेचा परतावा.",
        },
    },
    "COMMERCIAL_CONTRACT_MSME": {
        "title": {
            "en": "Delayed Commercial Payment and Default on Outstanding MSME Invoices",
            "hi": "MSME बकाया बिलों का विलंबित भुगतान एवं वैधानिक ब्याज देयता",
            "mr": "MSME थकबाकी बिलांचे विलंबित देयक आणि कायदेशीर व्याजाची मागणी",
        },
        "act": {
            "en": "Micro, Small and Medium Enterprises Development Act, 2006 (Sections 15 and 16)",
            "hi": "सूक्ष्म, लघु और मध्यम उद्यम विकास अधिनियम, 2006 (धारा 15 एवं 16)",
            "mr": "सूक्ष्म, लघु आणि मध्यम उद्योग विकास कायदा, 2006 (कलम 15 आणि 16)",
        },
        "contraventions": {
            "en": "Failure to liquidate admitted invoices within 45 days of supply of goods/services, violating mandatory statutory settlement timelines under Section 15 of the MSMED Act, 2006.",
            "hi": "माल अथवा सेवाओं की आपूर्ति के 45 दिनों के भीतर स्वीकृत बिलों का भुगतान न करना, जो MSMED अधिनियम, 2006 की धारा 15 का प्रत्यक्ष उल्लंघन है।",
            "mr": "माल किंवा सेवा पुरवठ्याच्या 45 दिवसांच्या आत बिलांची रक्कम न चुकवणे, जे MSMED कायदा, 2006 च्या कलम 15 चे थेट उल्लंघन आहे.",
        },
        "reliefs": {
            "en": "Immediate liquidation of total principal outstanding along with mandatory compound monthly interest at three times the RBI bank rate as prescribed under Section 16 of the MSMED Act, 2006.",
            "hi": "कुल मूलधन बकाया का तत्काल भुगतान एवं MSMED अधिनियम, 2006 की धारा 16 के तहत RBI बैंक दर के तीन गुना मासिक चक्रवृद्धि ब्याज का भुगतान।",
            "mr": "एकूण मूळ थकबाकीचे त्वरित देयक आणि MSMED कायदा, 2006 च्या कलम 16 अन्वये RBI बँक दराच्या तीन पट मासिक चक्रवाढ व्याजासह रक्कम देणे.",
        },
    },
    "POLICE_CUSTODY": {
        "title": {
            "en": "Procedural Non-Compliance and Violation of Safeguards in Police Custody",
            "hi": "पुलिस हिरासत में प्रक्रियात्मक सुरक्षा एवं वैधानिक अधिकारों का उल्लंघन",
            "mr": "पोलीस कोठडीत वैधानिक सुरक्षेचे आणि मार्गदर्शक तत्त्वांचे उल्लंघन",
        },
        "act": {
            "en": "Bharatiya Nagarik Suraksha Sanhita, 2023 (Sections 36, 47) and Article 22(2)",
            "hi": "भारतीय नागरिक सुरक्षा संहिता, 2023 (धारा 36, 47) एवं संविधान का अनुच्छेद 22(2)",
            "mr": "भारतीय नागरिक सुरक्षा संहिता, 2023 (कलम 36, 47) आणि अनुच्छेद 22(2)",
        },
        "contraventions": {
            "en": "Detention without prompt communication of formal grounds of arrest, failure to prepare arrest memo with independent witness attestation, and failure to produce before Magistrate within 24 hours under BNSS Sections 36, 47 and Article 22(2).",
            "hi": "गिरफ्तारी के लिखित आधार बताए बिना हिरासत में रखना, स्वतंत्र गवाह की उपस्थिति में अरेस्ट मेमो तैयार न करना, और 24 घंटे के भीतर मजिस्ट्रेट के समक्ष पेश न करना।",
            "mr": "अटकेची लेखी कारणे न सांगता ताब्यात ठेवणे, पंचांच्या स्वाक्षरीसह अरेस्ट मेमो तयार न करणे आणि 24 तासांच्या आत दंडाधिकाऱ्यांसमोर हजर न करणे.",
        },
        "reliefs": {
            "en": "Immediate formalization of custody records, provision of legal counsel consultation, mandatory independent medical examination, and strict adherence to D.K. Basu statutory safeguards.",
            "hi": "हिरासत संबंधी अभिलेखों का तत्काल संधारण, विधिक परामर्शदाता से संपर्क की अनुमति, अनिवार्य स्वतंत्र मेडिकल परीक्षण, और डी.के. बसु दिशानिर्देशों का कड़ाई से पालन।",
            "mr": "कोठडीच्या नोंदी त्वरित अधिकृत करणे, वकिलांशी सल्लामसलत करण्याची मुभा, अनिवार्य स्वतंत्र वैद्यकीय तपासणी, आणि डी.के. बसू मार्गदर्शक तत्त्वांचे काटेकोर पालन.",
        },
    },
    "DOMESTIC_VIOLENCE": {
        "title": {
            "en": "Domestic Abuse, Harassment, and Deprivation of Shared Household Rights",
            "hi": "घरेलू हिंसा, प्रताड़ना एवं साझे घर में रहने के अधिकार का हनन",
            "mr": "घरगुती हिंसाचार, मानसिक-शारीरिक छळ आणि सामायिक घरातील हक्क डावलणे",
        },
        "act": {
            "en": "Protection of Women from Domestic Violence Act, 2005 (Sections 12, 18, 19)",
            "hi": "घरेलू हिंसा से महिलाओं का संरक्षण अधिनियम, 2005 (धारा 12, 18, 19)",
            "mr": "घरगुती हिंसाचारापासून महिलांचे संरक्षण कायदा, 2005 (कलम 12, 18, 19)",
        },
        "contraventions": {
            "en": "Infliction of physical, verbal, emotional, and economic abuse, and unlawful threat of dispossession from the shared household under the Protection of Women from Domestic Violence Act, 2005.",
            "hi": "साझे घर में शारीरिक, मानसिक, मौखिक व आर्थिक प्रताड़ना देना एवं अवैध रूप से घर से बेदखल करने की धमकी देना, जो घरेलू हिंसा अधिनियम, 2005 का उल्लंघन है।",
            "mr": "सामायिक घरात शारीरिक, मानसिक, तोंडी आणि आर्थिक छळ करणे आणि बेकायदेशीरपणे घराबाहेर काढण्याची धमकी देणे.",
        },
        "reliefs": {
            "en": "Immediate cessation of all harassment, violence, and intimidation; unhindered right of residence in the shared household; interim maintenance and protection under PWDVA, 2005.",
            "hi": "सभी प्रकार की हिंसा, प्रताड़ना और धमकी पर तत्काल रोक; साझे घर में निर्बाध निवास का अधिकार; तथा धारा 18 व 19 के अंतर्गत अंतरिम भरण-पोषण एवं सुरक्षा।",
            "mr": "सर्व प्रकारचा छळ, हिंसाचार आणि धमक्या त्वरित थांबवणे; सामायिक घरात राहण्याचा निर्वेध हक्क; आणि अंतरिम पोटगी व कायदेशीर संरक्षण.",
        },
    },
    "LAND_GRABBING": {
        "title": {
            "en": "Unlawful Property Encroachment, Dispossession, and Criminal Trespass",
            "hi": "अवैध भूमि कब्जा, अतिक्रमण एवं आपराधिक अतिचार",
            "mr": "जमिनीवर बेकायदेशीर ताबा, अतिक्रमण आणि गुन्हेगारी अतिक्रमण",
        },
        "act": {
            "en": "Specific Relief Act, 1963 (Section 6) and Bharatiya Nyaya Sanhita, 2023",
            "hi": "विनिर्दिष्ट अनुतोष अधिनियम, 1963 (धारा 6) एवं भारतीय न्याय संहिता, 2023",
            "mr": "विशिष्ट दिलासा कायदा, 1963 (कलम 6) आणि भारतीय न्याय संहिता, 2023",
        },
        "contraventions": {
            "en": "Forceful entry, unlawful encroachment, and dispossession of lawful occupant from immovable property without due process of law under Section 6 of Specific Relief Act and BNS criminal trespass provisions.",
            "hi": "कानून की उचित प्रक्रिया के बिना अचल संपत्ति में जबरन प्रवेश, अवैध अतिक्रमण और वैध कब्जेदार को बेदखल करना, जो विनिर्दिष्ट अनुतोष अधिनियम एवं BNS का उल्लंघन है।",
            "mr": "कायदेशीर प्रक्रियेशिवाय अचल संपत्तीवर बळजबरीने ताबा मिळवणे, अतिक्रमण करणे आणि मूळ कब्जादारास बेदखल करणे.",
        },
        "reliefs": {
            "en": "Immediate removal of unlawful structures and encroachments, restoration of unhindered physical possession to complainant, and undertaking not to interfere with peaceful enjoyment.",
            "hi": "अवैध निर्माण व अतिक्रमण को तत्काल हटाना, शिकायतकर्ता को निर्बाध भौतिक कब्जा वापस सौंपना, और शांतिपूर्ण उपभोग में हस्तक्षेप न करने का लिखित वचन देना।",
            "mr": "बेकायदेशीर बांधकामे व अतिक्रमण त्वरित हटवणे, तक्रारदाराला शांततापूर्ण प्रत्यक्ष ताबा परत देणे, आणि मालमत्तेत हस्तक्षेप न करण्याचे लेखी हमीपत्र देणे.",
        },
    },
    "LOAN_FRAUD": {
        "title": {
            "en": "Coercive Digital Lending Harassment, Blackmail, and Unlawful Recovery",
            "hi": "डिजिटल ऋण वसूली में ब्लैकमेल, अवैध प्रताड़ना एवं निजता का हनन",
            "mr": "डिजिटल कर्ज वसुलीत ब्लॅकमेलिंग, बेकायदेशीर छळ आणि गोपनीयतेचे उल्लंघन",
        },
        "act": {
            "en": "RBI Digital Lending Guidelines, Information Technology Act, 2000, and BNS, 2023",
            "hi": "RBI डिजिटल लेंडिंग दिशानिर्देश, सूचना प्रौद्योगिकी अधिनियम, 2000 एवं BNS, 2023",
            "mr": "RBI डिजिटल लेंडिंग मार्गदर्शक तत्त्वे, माहिती तंत्रज्ञान कायदा, 2000 आणि BNS, 2023",
        },
        "contraventions": {
            "en": "Unauthorized harvesting of phone contacts, extortionate threats, morphed photo distribution, and abusive collection methods in gross violation of RBI Digital Lending Guidelines and IT Act Section 66E.",
            "hi": "मोबाइल संपर्कों का अनधिकृत उपयोग, जबरन वसूली, मॉर्फ्ड फोटो के जरिए ब्लैकमेल और अपमानजनक वसूली तरीके, जो RBI दिशानिर्देशों एवं IT एक्ट की धारा 66E का गंभीर उल्लंघन है।",
            "mr": "मोबाईल संपर्कांचा अनधिकृत वापर, खंडणीच्या धमक्या, मॉर्फ्ड फोटोंचा गैरवापर आणि अपमानास्पद वसुली पद्धती, जे RBI मार्गदर्शक तत्त्वांचे आणि IT कायद्याचे उल्लंघन आहे.",
        },
        "reliefs": {
            "en": "Immediate cessation of all harassment, deletion of harvested personal data and contacts, written confirmation of account closure, and compensation for mental agony and reputational harm.",
            "hi": "समस्त प्रकार के उत्पीड़न को तत्काल रोकना, अनधिकृत रूप से एकत्र व्यक्तिगत डेटा व संपर्कों को हटाना, ऋण खाते का पारदर्शी विवरण देना, और मानसिक प्रताड़ना की भरपाई।",
            "mr": "सर्व प्रकारचा छळ त्वरित थांबवणे, अनधिकृतपणे घेतलेला वैयक्तिक डेटा नष्ट करणे, खात्याचा पारदर्शक हिशोब देणे आणि मानसिक त्रासाची भरपाई करणे.",
        },
    },
    "CORRUPTION_RTI": {
        "title": {
            "en": "Solicitation of Unlawful Gratification and Denial of Statutory Public Service",
            "hi": "रिश्वत की अवैध मांग, भ्रष्टाचार एवं वैधानिक लोक सेवा से इनकार",
            "mr": "लाचेची बेकायदेशीर मागणी, भ्रष्टाचार आणि शासकीय सेवेचा नकार",
        },
        "act": {
            "en": "Prevention of Corruption Act, 1988 (Section 7) and Right to Information Act, 2005",
            "hi": "भ्रष्टाचार निवारण अधिनियम, 1988 (धारा 7) एवं सूचना का अधिकार अधिनियम, 2005",
            "mr": "भ्रष्टाचार प्रतिबंधक कायदा, 1988 (कलम 7) आणि माहिती अधिकार कायदा, 2005",
        },
        "contraventions": {
            "en": "Demand for illegal gratification or bribe for the discharge of official public duty, and willful obstruction of citizen's statutory service entitlements under Section 7 of the Prevention of Corruption Act, 1988.",
            "hi": "शासकीय कर्तव्यों के निर्वहन हेतु अवैध रिश्वत की मांग करना और नागरिक के वैधानिक अधिकारों को बाधित करना, जो भ्रष्टाचार निवारण अधिनियम, 1988 की धारा 7 का दंडनीय अपराध है।",
            "mr": "शासकीय कर्तव्य पार पाडण्यासाठी बेकायदेशीर लाचेची मागणी करणे आणि नागरिकांच्या वैधानिक सेवेत अडथळा आणणे, जे भ्रष्टाचार प्रतिबंधक कायद्यानुसार गुन्हा आहे.",
        },
        "reliefs": {
            "en": "Immediate lawful processing and delivery of the pending public entitlement without demand of undue gratification, and initiation of vigilance review against delinquent personnel.",
            "hi": "बिना किसी अनुचित मांग के लंबित सरकारी सेवा अथवा प्रमाण-पत्र का तत्काल निस्तारण, तथा संबंधित कर्मियों के विरुद्ध विभागीय सतर्कता जांच प्रारंभ करना।",
            "mr": "कोणत्याही अनुचित मागणीशिवाय प्रलंबित शासकीय सेवा अथवा प्रमाणपत्र त्वरित देणे, आणि संबंधित दोषींवर विभागीय दक्षता चौकशी सुरू करणे.",
        },
    },
    "RELIGIOUS_GATHERING": {
        "title": {
            "en": "Unlawful Interference with Peaceful Assembly and Disruption of Worship",
            "hi": "शांतिपूर्ण धार्मिक सभा में अवैध व्यवधान, भय एवं उपासना में बाधा",
            "mr": "शांततापूर्ण धार्मिक सभेत बेकायदेशीर अडथळा आणि उपासनेत व्यत्यय",
        },
        "act": {
            "en": "Article 25 of the Constitution of India and Bharatiya Nyaya Sanhita, 2023 (Section 299)",
            "hi": "भारत के संविधान का अनुच्छेद 25 एवं भारतीय न्याय संहिता, 2023 (धारा 299)",
            "mr": "भारतीय संविधानाचे अनुच्छेद 25 आणि भारतीय न्याय संहिता, 2023 (कलम 299)",
        },
        "contraventions": {
            "en": "Unlawful disruption, threat, and intimidation directed at a peaceful religious gathering, violating constitutional religious freedoms guaranteed under Article 25 and Section 299 of BNS, 2023.",
            "hi": "शांतिपूर्ण धार्मिक सभा को बाधित करना, धमकी देना और उपासना में विघ्न डालना, जो संविधान के अनुच्छेद 25 एवं भारतीय न्याय संहिता, 2023 की धारा 299 का उल्लंघन है।",
            "mr": "शांततापूर्ण धार्मिक सभेत व्यत्यय आणणे, धमकावणे आणि उपासना बाधित करणे, जे संविधानाच्या अनुच्छेद 25 चे आणि BNS च्या कलम 299 चे उल्लंघन आहे.",
        },
        "reliefs": {
            "en": "Immediate cessation of disruption, provision of administrative protection for peaceful congregation, and formal undertaking not to interfere with religious worship.",
            "hi": "धार्मिक सभा में व्यवधान को तत्काल रोकना, शांतिपूर्ण सभा हेतु प्रशासनिक सुरक्षा प्रदान करना, और उपासना में कभी भी हस्तक्षेप न करने का वचन देना।",
            "mr": "सभेतील अडथळे त्वरित थांबवणे, शांततापूर्ण उपासनेसाठी प्रशासकीय संरक्षण देणे आणि भविष्यात असा हस्तक्षेप न करण्याचे वचन देणे.",
        },
    },
    "MOTOR_ACCIDENT_PRO": {
        "title": {
            "en": "Motor Vehicle Collision Claims, Insurance Liability, and Statutory Compensation",
            "hi": "मोटर वाहन दुर्घटना दावा, बीमा दायित्व एवं विधिक मुआवजा",
            "mr": "मोटार वाहन अपघात भरपाई, विमा दायित्व आणि कायदेशीर दावा",
        },
        "act": {
            "en": "Motor Vehicles Act, 1988/2019 (Section 166) and Insurance Regulatory Provisions",
            "hi": "मोटर वाहन अधिनियम, 2019 (धारा 166) एवं बीमा विनियामक प्रावधान",
            "mr": "मोटार वाहन कायदा, 2019 (कलम 166) आणि विमा नियमन तरतुदी",
        },
        "contraventions": {
            "en": "Actionable vehicular negligence resulting in collision damages, bodily injury, and failure to timely acknowledge third-party insurance liability under Section 166 of the Motor Vehicles Act, 2019.",
            "hi": "मोटर वाहन के लापरवाहीपूर्ण संचालन से शारीरिक क्षति एवं नुकसान, तथा मोटर वाहन अधिनियम, 2019 की धारा 166 के तहत तृतीय पक्ष देयता का समय पर निपटान न करना।",
            "mr": "वाहनाच्या निष्काळजी चालवण्यामुळे झालेले नुकसान व दुखापत, आणि मोटार वाहन कायदा, 2019 च्या कलम 166 अन्वये विमा भरपाईची त्वरित दखल न घेणे.",
        },
        "reliefs": {
            "en": "Preservation of all incident and collision records, registration of third-party insurance claim, interim reimbursement of medical expenses, and full statutory claim settlement.",
            "hi": "दुर्घटना संबंधी समस्त अभिलेखों का संरक्षण, तृतीय पक्ष बीमा दावे का पंजीकरण, तत्काल चिकित्सा व्यय की प्रतिपूर्ति, तथा पूर्ण वैधानिक दावे का निपटान।",
            "mr": "अपघाताच्या सर्व नोंदी सुरक्षित ठेवणे, तृतीय पक्ष विमा दावा दाखल करणे, तातडीचा वैद्यकीय खर्च देणे आणि संपूर्ण भरपाईचा दावा निकाली काढणे.",
        },
    },
    "GENERAL_CITIZEN_AID": {
        "title": {
            "en": "Citizen Statutory Grievance and Formal Pre-Litigation Legal Representation",
            "hi": "नागरिक विधिक शिकायत एवं औपचारिक पूर्व-मुकदमा विधिक प्रतिनिधित्व",
            "mr": "नागरिक कायदेशीर तक्रार आणि पूर्व-दावा अधिकृत निवेदन",
        },
        "act": {
            "en": "Applicable Statutory Provisions and Legal Services Authorities Act, 1987",
            "hi": "लागू वैधानिक प्रावधान एवं विधिक सेवा प्राधिकरण अधिनियम, 1987",
            "mr": "लागू कायदेशीर तरतुदी आणि विधिक सेवा प्राधिकरण कायदा, 1987",
        },
        "contraventions": {
            "en": "Actionable infringement of statutory citizen rights and fair administrative process causing legal injury to the complainant.",
            "hi": "नागरिक के वैधानिक अधिकारों और निष्पक्ष प्रक्रिया का उल्लंघन, जिससे शिकायतकर्ता को विधिक क्षति पहुंची है।",
            "mr": "नागरिकाच्या कायदेशीर हक्कांचे आणि न्याय्य प्रक्रियेचे उल्लंघन, ज्यामुळे तक्रारदाराचे नुकसान झाले आहे.",
        },
        "reliefs": {
            "en": "Immediate review and rectification of the stated grievance, restoration of status quo, and provision of a reasoned written response within 15 days.",
            "hi": "शिकायत का तत्काल निवारण, यथास्थिति की बहाली, तथा 15 दिनों के भीतर कारण सहित लिखित उत्तर प्रदान करना।",
            "mr": "तक्रारीचे त्वरित निवारण करणे, जैसे थे परिस्थिती पूर्ववत करणे, आणि 15 दिवसांच्या आत सकारण लेखी उत्तर देणे.",
        },
    },
}


def _build_formal_legal_notice(
    category: str,
    facts: Dict[str, Any],
    transcript: str,
    lang: str,
    candidate_statutes: Optional[List[Any]] = None,
    needs_more_information: Optional[bool] = None,
    questions: Optional[List[str]] = None,
    supplied: Optional[List[str]] = None,
) -> str:
    """Generates a complete, formal, pre-litigation legal notice / statutory representation.

    Formatted for pre-litigation review & record with outbound transmission disabled.
    Supports English ('en'), Hindi ('hi'), and Marathi ('mr').
    """
    facts = dict(facts or {})
    lang_code = lang if lang in ["hi", "mr", "gu"] else "en"

    # Determine intake completeness if not explicitly provided
    if needs_more_information is None:
        required_keys = ["incident_date", "incident_location", "other_party", "specific_details"]
        missing_keys = [k for k in required_keys if not str(facts.get(k, "")).strip()]
        needs_more_information = bool(missing_keys)

    # Core metadata extraction
    date_val = str(facts.get("incident_date", "")).strip()
    if not date_val or date_val.lower() in ["the stated date", "none"]:
        date_val = datetime.now().strftime("%d-%m-%Y")

    place_val = str(facts.get("incident_location") or facts.get("location") or "").strip()
    if not place_val or place_val.lower() in ["the stated location", "none"]:
        place_val = "Jurisdiction of Incident / Unspecified"

    other_party_val = str(facts.get("other_party", "")).strip()
    if not other_party_val or other_party_val.lower() in ["the adverse party", "none"]:
        other_party_val = "Opposite Party / Competent Authority (To be identified)"

    client_name_val = str(facts.get("client_name", "")).strip()
    if not client_name_val or client_name_val.lower() in ["the aggrieved citizen", "none"]:
        client_name_val = "Aggrieved Citizen / Complainant"

    # Category specifics lookup
    cat_data = LEGAL_NOTICE_CATEGORY_DATA.get(category, LEGAL_NOTICE_CATEGORY_DATA["GENERAL_CITIZEN_AID"])
    cat_title = cat_data["title"].get(lang_code, cat_data["title"]["en"])
    primary_act = cat_data["act"].get(lang_code, cat_data["act"]["en"])
    primary_contravention = cat_data["contraventions"].get(lang_code, cat_data["contraventions"]["en"])
    primary_relief = cat_data["reliefs"].get(lang_code, cat_data["reliefs"]["en"])

    ai_narrative = _build_ai_synthesized_narrative(category, facts, transcript, lang)
    account = transcript.strip() or "No account provided yet."

    # Build statutory lines from candidate statutes or registry
    statutory_lines = []
    if candidate_statutes:
        for cand in candidate_statutes:
            if isinstance(cand, dict):
                law = cand.get("law") or cand.get("section") or cand.get("act") or ""
                details = cand.get("details") or cand.get("conditions") or cand.get("remedy") or ""
                if law:
                    statutory_lines.append(f"   - {law}: {details}" if details else f"   - {law}")
            elif isinstance(cand, str):
                statutory_lines.append(f"   - {cand}")

    reg_entry = get_source_register_entry(category) if "get_source_register_entry" in globals() else {}
    if not statutory_lines and reg_entry and reg_entry.get("references"):
        for ref in reg_entry["references"]:
            law = ref.get("law", "")
            cond = ref.get("conditions") or ref.get("remedy", "")
            if law:
                statutory_lines.append(f"   - {law}: {cond}" if cond else f"   - {law}")
    elif not statutory_lines:
        possible = POTENTIAL_LEGAL_REFERENCES.get(category, [])
        for law, _ in possible:
            statutory_lines.append(f"   - {law}")

    statutory_extra_str = ("\n" + "\n".join(statutory_lines)) if statutory_lines else f"\n   - {primary_act}"

    # Build structured facts block
    supplied_lines = []
    known_fields = [
        ("specific_details", "Substantive Particulars" if lang_code == "en" else ("विशिष्ट विवरण" if lang_code == "hi" else "विशिष्ट तपशील")),
        ("amount", "Disputed Amount" if lang_code == "en" else ("विवादित राशि" if lang_code == "hi" else "विवादित रक्कम")),
        ("disputed_amount", "Disputed Amount" if lang_code == "en" else ("विवादित राशि" if lang_code == "hi" else "विवादित रक्कम")),
        ("insurer", "Insurer" if lang_code == "en" else ("बीमा कंपनी" if lang_code == "hi" else "विमा कंपनी")),
        ("policy_no", "Policy Number" if lang_code == "en" else ("पॉलिसी संख्या" if lang_code == "hi" else "पॉलिसी क्रमांक")),
        ("vehicle_no", "Vehicle Number" if lang_code == "en" else ("वाहन संख्या" if lang_code == "hi" else "वाहन क्रमांक")),
        ("witnesses", "Witnesses" if lang_code == "en" else ("गवाह" if lang_code == "hi" else "साक्षीदार")),
        ("employer", "Employer" if lang_code == "en" else ("नियोक्ता" if lang_code == "hi" else "मालक / नियोक्ता")),
    ]
    seen_keys = set()
    for k, lbl in known_fields:
        if k in facts and str(facts[k]).strip():
            supplied_lines.append(f"   - {lbl}: {facts[k]}")
            seen_keys.add(k)

    internal_keys = {
        "client_name", "incident_date", "incident_location", "location", "other_party",
        "candidate_statutes", "candidate_provisions", "is_followup_turn", "revision_requested",
        "language", "language_code", "detected_language", "current_utterance", "category",
        "missing", "needs_more_information"
    } | seen_keys
    for k, v in facts.items():
        if k not in internal_keys and str(v).strip():
            supplied_lines.append(f"   - {k.replace('_', ' ').title()}: {v}")

    if supplied:
        for s in supplied:
            if s not in supplied_lines and not any(s in sl for sl in supplied_lines):
                supplied_lines.append(f"   - {s}")

    supplied_extra_str = ("\n" + "\n".join(supplied_lines)) if supplied_lines else ""

    # Facts still to confirm
    if needs_more_information:
        if questions:
            unconfirmed_str = "\n".join(f"   - {q}" for q in questions)
        else:
            unconfirmed_str = "   - Further evidentiary details and primary documentation to be confirmed."
    else:
        unconfirmed_str = "   - Confirm this account and any supporting records."

    # Language-specific template assembly
    if lang_code == "hi":
        status_banner = (
            "[स्थिति: विधिक समीक्षा हेतु प्रारूप घटना सारांश — प्रारंभिक अभ्यावेदन (तथ्यों की पुष्टि लंबित)]"
            if needs_more_information else
            "[स्थिति: विधिक समीक्षा हेतु प्रारूप घटना सारांश — पूर्ण विधिक सूचना अभिलेख (पुष्टीकृत तथ्य)]"
        )
        statutory_status = (
            "   [प्रारंभिक वैधानिक मानचित्रण — साक्ष्य सत्यापन एवं विधिक परामर्श के अधीन]"
            if needs_more_information else
            "   [पुष्टीकृत वैधानिक आधार — पूर्व-मुकदमा विधिक अभ्यावेदन अभिलेख]"
        )
        return (
            "--------------------------------------------------------------------------------\n"
            "विधिक सूचना / औपचारिक वैधानिक अभ्यावेदन\n"
            "LEGAL NOTICE / FORMAL STATUTORY REPRESENTATION\n"
            "(मुकदमा-पूर्व समीक्षा और अभिलेख हेतु जारी — बाह्य प्रेषण निष्क्रिय / DRAFT INCIDENT SUMMARY — Issued for Pre-Litigation Review & Record — Outbound Transmission Disabled)\n"
            f"{status_banner}\n\n"
            f"दिनांक (Date): {date_val}\n"
            f"स्थान (Place): {place_val}\n\n"
            "सेवा में / प्रति (TO):\n"
            f"{other_party_val}\n\n"
            "प्रेषक (FROM):\n"
            f"{client_name_val}\n\n"
            f"विषय (SUBJECT): {primary_act} के अंतर्गत {cat_title} के संबंध में औपचारिक विधिक सूचना\n\n"
            "1. वस्तुस्थिती एवं घटनाक्रम (1. FACTUAL MATRIX & CHRONOLOGY):\n"
            "   1. CASE SYNOPSIS & FACTUAL SUMMARY (AI Synthesized Narrative):\n"
            f"   {ai_narrative}\n\n"
            "   Account in the person's own words (शिकायतकर्ता के अपने शब्द):\n"
            f"   {account}\n\n"
            "2. संरचित घटना विवरण (2. STRUCTURED INCIDENT PARTICULARS):\n"
            f"   - घटना की तिथि (Incident Date): {date_val}\n"
            f"   - घटना का स्थान (Incident Location): {place_val}\n"
            f"   - विरोधी पक्ष (Opposing Party): {other_party_val}\n"
            f"   - शिकायतकर्ता का नाम (Complainant Name): {client_name_val}"
            f"{supplied_extra_str}\n\n"
            "   Facts still to confirm (पुष्टि हेतु शेष तथ्य):\n"
            f"{unconfirmed_str}\n\n"
            "3. वैधानिक उल्लंघन एवं लागू धाराएं (3. STATUTORY CONTRAVENTIONS & APPLICABLE DHAARA):\n"
            f"{statutory_status}\n"
            f"   - संबंधित अधिनियम (Governing Act): {primary_act}\n"
            f"   - विशिष्ट उल्लंघन (Specific Contravention): {primary_contravention}\n"
            f"{statutory_extra_str}\n\n"
            "4. विशिष्ट मांगें एवं आवश्यक अनुतोष (4. SPECIFIC DEMANDS & REQUISITE RELIEFS):\n"
            "   उपर्युक्त उल्लंघनों के आलोक में, आपको एतद्द्वारा निम्नलिखित मांगों का अनुपालन करने हेतु सूचित किया जाता है:\n"
            "   1. यथास्थिति बनाए रखना (Preservation of Status Quo): किसी भी प्रकार की प्रतिकूल, दंडात्मक अथवा जबरन कार्रवाई को तत्काल रोकें।\n"
            f"   2. प्रतिपूर्ति एवं समाधान (Restitution & Settlement): {primary_relief}\n"
            "   3. 15 दिनों का सुधारात्मक नोटिस (15-Day Cure Notice): इस विधिक सूचना की प्राप्ति के 15 दिनों के भीतर इन मांगों का समाधान करें।\n"
            "   4. अभिलेखों की प्रस्तुति (Production of Records): इस विवाद से संबंधित समस्त लिखित कारण, हिसाब-किताब व आवश्यक दस्तावेज प्रस्तुत करें।\n\n"
            "5. अधिकारों का संरक्षण एवं विधिक सहायता (5. RESERVATION OF RIGHTS & LEGAL AID):\n"
            "   कृपया ध्यान दें कि निर्धारित 15 दिनों की समयावधि में इन मांगों का अनुपालन न करने पर:\n"
            "   1. विधिक कार्यवाही (Legal Proceedings): पीड़ित पक्ष आपके अपने खर्च एवं जोखिम पर सक्षम न्यायालय अथवा मंच के समक्ष दीवानी, फौजदारी या उपभोक्ता कार्यवाही प्रारंभ करने का पूर्ण अधिकार सुरक्षित रखता है।\n"
            "   2. निःशुल्क विधिक सहायता (DLSA / NALSA): पीड़ित नागरिक विधिक सेवा प्राधिकरण अधिनियम, 1987 (Legal Services Authorities Act, 1987) की धारा 12 के तहत जिला विधिक सेवा प्राधिकरण (DLSA) / राष्ट्रीय विधिक सेवा प्राधिकरण (NALSA) के माध्यम से निःशुल्क विधिक सहायता प्राप्त करने का अधिकार सुरक्षित रखता है (हेल्पलाइन: 15100, आधिकारिक पोर्टल: https://nalsa.gov.in/legal-aid/)।\n\n"
            "Requested next step: A qualified adviser should review the account, evidence, applicable law, and any filing deadline before a notice or complaint is sent.\n"
            "--------------------------------------------------------------------------------"
        )
    elif lang_code == "mr":
        status_banner = (
            "[स्थिती: कायदेशीर पुनरावलोकनासाठी घटना सारांश मसुदा — प्राथमिक निवेदन (तथ्यांची पुष्टी प्रलंबित)]"
            if needs_more_information else
            "[स्थिती: कायदेशीर पुनरावलोकनासाठी घटना सारांश मसुदा — परिपूर्ण कायदेशीर नोटीस अभिलेख (पुष्टीकृत तथ्य)]"
        )
        statutory_status = (
            "   [प्राथमिक वैधानिक मॅपिंग — पुरावा पडताळणी आणि कायदेशीर सल्ल्याच्या अधीन]"
            if needs_more_information else
            "   [पुष्टीकृत वैधानिक आधार — पूर्व-दावा कायदेशीर निवेदन अभिलेख]"
        )
        return (
            "--------------------------------------------------------------------------------\n"
            "कायदेशीर नोटीस / वैधानिक निवेदन\n"
            "LEGAL NOTICE / FORMAL STATUTORY REPRESENTATION\n"
            "(दावा-पूर्व पुनरावलोकन आणि अभिलेखासाठी जारी — बाह्य पाठवणे अक्षम / DRAFT INCIDENT SUMMARY — Issued for Pre-Litigation Review & Record — Outbound Transmission Disabled)\n"
            f"{status_banner}\n\n"
            f"दिनांक (Date): {date_val}\n"
            f"ठिकाण (Place): {place_val}\n\n"
            "प्रति (TO):\n"
            f"{other_party_val}\n\n"
            "प्रेषक (FROM):\n"
            f"{client_name_val}\n\n"
            f"विषय (SUBJECT): {primary_act} अंतर्गत {cat_title} बाबत औपचारिक कायदेशीर नोटीस\n\n"
            "1. वस्तुस्थिती आणि घटनाक्रम (1. FACTUAL MATRIX & CHRONOLOGY):\n"
            "   1. CASE SYNOPSIS & FACTUAL SUMMARY (AI Synthesized Narrative):\n"
            f"   {ai_narrative}\n\n"
            "   Account in the person's own words (तक्रारदाराचे स्वतःचे शब्द):\n"
            f"   {account}\n\n"
            "2. संरचित घटना तपशील (2. STRUCTURED INCIDENT PARTICULARS):\n"
            f"   - घटनेची तारीख (Incident Date): {date_val}\n"
            f"   - घटनेचे ठिकाण (Incident Location): {place_val}\n"
            f"   - विरोधी पक्ष (Opposing Party): {other_party_val}\n"
            f"   - तक्रारदाराचे नाव (Complainant Name): {client_name_val}"
            f"{supplied_extra_str}\n\n"
            "   Facts still to confirm (पुष्टीकरणासाठी उर्वरित तथ्ये):\n"
            f"{unconfirmed_str}\n\n"
            "3. वैधानिक उल्लंघन आणि लागू कलमे (3. STATUTORY CONTRAVENTIONS & APPLICABLE DHAARA):\n"
            f"{statutory_status}\n"
            f"   - संबंधित कायदा (Governing Act): {primary_act}\n"
            f"   - विशिष्ट उल्लंघन (Specific Contravention): {primary_contravention}\n"
            f"{statutory_extra_str}\n\n"
            "4. विशिष्ट मागण्या आणि आवश्यक दिलासा (4. SPECIFIC DEMANDS & REQUISITE RELIEFS):\n"
            "   उपरोक्त उल्लंघनांच्या पार्श्वभूमीवर, आपणास याद्वारे खालील मागण्यांची पूर्तता करण्याचे सूचित करण्यात येत आहे:\n"
            "   1. जैसे थे परिस्थिती ठेवणे (Preservation of Status Quo): कोणतीही पुढील प्रतिकूल, दडपशाहीची किंवा बेकायदेशीर कारवाई त्वरित थांबवा.\n"
            f"   2. भरपाई आणि निवारण (Restitution & Settlement): {primary_relief}\n"
            "   3. 15 दिवसांची मुदत (15-Day Cure Notice): ही कायदेशीर नोटीस मिळाल्यापासून 15 दिवसांच्या आत मागण्यांची पूर्तता करा.\n"
            "   4. नोंदी सादर करणे (Production of Records): या विवादाशी संबंधित संपूर्ण लेखी कारणे, हिशोब व आवश्यक कागदपत्रे सादर करा.\n\n"
            "5. हक्कांचे आरक्षण आणि कायदेशीर मदत (5. RESERVATION OF RIGHTS & LEGAL AID):\n"
            "   कृपया नोंद घ्यावी की दिलेल्या 15 दिवसांच्या मुदतीत वरील मागण्यांचे पालन न केल्यास:\n"
            "   1. कायदेशीर कारवाई (Legal Proceedings): तक्रारदार आपल्या स्वतःच्या खर्चावर आणि जबाबदारीवर सक्षम न्यायालयात किंवा मंचासमोर योग्य कायदेशीर कारवाई सुरू करण्याचा पूर्ण हक्क राखून ठेवत आहे.\n"
            "   2. मोफत कायदेशीर मदत (DLSA / NALSA): कायदेशीर सेवा प्राधिकरण कायदा, 1987 (Legal Services Authorities Act, 1987) च्या कलम 12 अन्वये जिल्हा विधिक सेवा प्राधिकरण (DLSA) / राष्ट्रीय विधिक सेवा प्राधिकरण (NALSA) कडून मोफत कायदेशीर मदत मिळवण्याचा हक्क राखून ठेवण्यात येत आहे (हेल्पलाइन: 15100, अधिकृत पोर्टल: https://nalsa.gov.in/legal-aid/).\n\n"
            "Requested next step: A qualified adviser should review the account, evidence, applicable law, and any filing deadline before a notice or complaint is sent.\n"
            "--------------------------------------------------------------------------------"
        )
    elif lang_code == "gu":
        status_banner = (
            "[સ્થિતિ: કાનૂની સમીક્ષા માટે ઘટના સારાંશ મસુદો — પ્રારંભિક નિવેદન (તથ્યોની પુષ્ટિ બાકી)]"
            if needs_more_information else
            "[સ્થિતિ: કાનૂની સમીક્ષા માટે ઘટના સારાંશ મસુદો — પરિપૂર્ણ કાનૂની નોટિસ રેકોર્ડ (પુષ્ટિ થયેલ તથ્યો)]"
        )
        statutory_status = (
            "   [પ્રારંભિક વૈધાનિક જોગવાઈ — પુરાવા ચકાસણી અને વકીલની સલાહને આધીન]"
            if needs_more_information else
            "   [પુષ્ટિ થયેલ કાનૂની આધાર — પૂર્વ-દાવો કાનૂની રજૂઆત રેકોર્ડ]"
        )
        return (
            "--------------------------------------------------------------------------------\n"
            "કાનૂની નોટિસ / વૈધાનિક રજૂઆત\n"
            "LEGAL NOTICE / FORMAL STATUTORY REPRESENTATION\n"
            "(દાવા-પૂર્વ પુનરાવલોકન અને અભિલેખ માટે જારી — બાહ્ય મોકલવું અક્ષમ / DRAFT INCIDENT SUMMARY — Issued for Pre-Litigation Review & Record — Outbound Transmission Disabled)\n"
            f"{status_banner}\n\n"
            f"તારીખ (Date): {date_val}\n"
            f"સ્થળ (Place): {place_val}\n\n"
            f"પ્રતિ (TO):\n"
            f"{other_party_val}\n\n"
            f"તરફથી (FROM):\n"
            f"{client_name_val}\n\n"
            f"વિષય (SUBJECT): {cat_title} બાબતે કાનૂની નોટિસ / વૈધાનિક રજૂઆત — {primary_act}\n\n"
            "૧. ઘટના વિગતો અને તથ્યો (1. FACTUAL MATRIX & CHRONOLOGY — AI Synthesized Narrative):\n"
            f"{ai_narrative}\n\n"
            "   અરજદારનું મૂળ નિવેદન (Complainant's Verbatim Statement):\n"
            f'   "{account}"\n\n'
            "૨. નોંધાયેલી ચોક્કસ વિગતો (2. STRUCTURED INCIDENT PARTICULARS):\n"
            f"   - ઘટનાની તારીખ (Incident Date): {date_val}\n"
            f"   - ઘટનાનું સ્થળ (Incident Location): {place_val}\n"
            f"   - સામેનો પક્ષ (Opposing Party): {other_party_val}\n"
            f"   - અરજદારનું નામ (Complainant Name): {client_name_val}"
            f"{supplied_extra_str}\n\n"
            "   Facts still to confirm (ખાતરી માટે બાકી વિગતો):\n"
            f"{unconfirmed_str}\n\n"
            "૩. સંબંધિત કાયદાઓ અને કલમો (3. STATUTORY CONTRAVENTIONS & APPLICABLE DHAARA):\n"
            f"{statutory_status}\n"
            f"   - પ્રાથમિક લાગુ અધિનિયમ: {primary_act}\n"
            f"   - કાનૂની ઉલ્લંઘનનું સ્વરૂપ: {primary_contravention}\n"
            f"{statutory_extra_str}\n\n"
            "૪. માગણીઓ અને રાહત (4. SPECIFIC DEMANDS & REQUISITE RELIEFS):\n"
            f"   - તાત્કાલિક ગેરકાયદેસર કાર્યવાહી બંધ કરવી અને યથાસ્થિતિ જાળવવી.\n"
            f"   - વિશિષ્ટ કાનૂની વળતર: {primary_relief}\n"
            "   - ૧૫ દિવસની વૈધાનિક નોટિસ (15-Day Statutory Cure Notice): આ નોટિસ મળ્યાના ૧૫ દિવસમાં બાકી લેણાં ચૂકવવા અથવા કાનૂની ઉકેલ લાવવો.\n"
            "   - સંબંધિત તમામ દસ્તાવેજો અને રેકોર્ડ સુરક્ષિત રાખવા.\n\n"
            "૫. કાનૂની અધિકારો અને મફત કાનૂની સહાય (5. RESERVATION OF RIGHTS & LEGAL AID):\n"
            "   આ નોટિસનો સંતોષકારક જવાબ ન મળ્યે, સક્ષમ ન્યાયાલય અથવા ફોરમ સમક્ષ દાવો દાખલ કરવાનો સંપૂર્ણ અધિકાર સુરક્ષિત છે.\n"
            "   અરજદારને કાનૂની સેવા સત્તામંડળ અધિનિયમ, ૧૯૮૭ ની કલમ ૧૨ હેઠળ મફત કાનૂની સહાય મેળવવાનો અધિકાર છે (નાલસા હેલ્પલાઇન: ૧૫૧૦૦, પોર્ટલ: https://nalsa.gov.in/legal-aid/).\n\n"
            "આગળનું જરૂરી પગલું: ઔપચારિક નોટિસ અથવા ફરિયાદ મોકલતા પહેલાં કોઈ લાયક વકીલ પાસે પુરાવા અને લાગુ કાયદાઓની ચકાસણી કરાવો.\n"
            "--------------------------------------------------------------------------------"
        )
    else:
        status_banner = (
            "[STATUS: DRAFT INCIDENT SUMMARY FOR LEGAL REVIEW — PRELIMINARY INTAKE RECORD (PENDING FACT CONFIRMATION)]"
            if needs_more_information else
            "[STATUS: DRAFT INCIDENT SUMMARY FOR LEGAL REVIEW — COMPLETE PRE-LITIGATION NOTICE RECORD (FACTS CONFIRMED)]"
        )
        statutory_status = (
            "   [Preliminary Statutory Mapping — Subject to Verification of Evidence and Qualified Counsel Advice]"
            if needs_more_information else
            "   [Verified Statutory Basis from Primary Sources — Pre-Litigation Review Record]"
        )
        return (
            "--------------------------------------------------------------------------------\n"
            "LEGAL NOTICE / FORMAL STATUTORY REPRESENTATION\n"
            "(Issued for Pre-Litigation Review & Record — Outbound Transmission Disabled / DRAFT INCIDENT SUMMARY)\n"
            f"{status_banner}\n\n"
            f"Date: {date_val}\n"
            f"Place: {place_val}\n\n"
            "TO:\n"
            f"{other_party_val}\n\n"
            "FROM:\n"
            f"{client_name_val}\n\n"
            f"SUBJECT: Formal Legal Notice regarding {cat_title} under {primary_act}\n\n"
            "1. FACTUAL MATRIX & CHRONOLOGY:\n"
            "   1. CASE SYNOPSIS & FACTUAL SUMMARY (AI Synthesized Narrative):\n"
            f"   {ai_narrative}\n\n"
            "   Account in the person's own words:\n"
            f"   {account}\n\n"
            "2. STRUCTURED INCIDENT PARTICULARS:\n"
            f"   - Incident Date: {date_val}\n"
            f"   - Incident Location: {place_val}\n"
            f"   - Opposing Party: {other_party_val}\n"
            f"   - Complainant: {client_name_val}"
            f"{supplied_extra_str}\n\n"
            "   Facts still to confirm:\n"
            f"{unconfirmed_str}\n\n"
            "3. STATUTORY CONTRAVENTIONS & APPLICABLE DHAARA:\n"
            f"{statutory_status}\n"
            f"   - Governing Act: {primary_act}\n"
            f"   - Specific Contraventions: {primary_contravention}\n"
            f"{statutory_extra_str}\n\n"
            "4. SPECIFIC DEMANDS & REQUISITE RELIEFS:\n"
            "   In view of the statutory contraventions detailed above, you are hereby called upon to comply with the following demands:\n"
            "   1. Preservation of Status Quo: Immediately cease and desist from any further adverse, coercive, or retaliatory measures.\n"
            f"   2. Restitution & Settlement: {primary_relief}\n"
            "   3. 15-Day Cure Notice: Satisfy the aforementioned requisitions within 15 (fifteen) days from the date of receipt of this notice, failing which appropriate judicial remedies shall be pursued.\n"
            "   4. Production of Records: Furnish full written reasons, certified account statements, and relevant records concerning this dispute.\n\n"
            "5. RESERVATION OF RIGHTS & LEGAL AID:\n"
            "   Take notice that in the event of failure, neglect, or refusal to comply with the demands within the stipulated 15-day window:\n"
            "   1. Legal Proceedings: The complainant reserves all legal rights to institute appropriate civil, criminal, or consumer proceedings before the competent court, tribunal, or authority, at your sole risk as to costs and consequences.\n"
            "   2. Institutional Legal Aid (DLSA / NALSA): The complainant explicitly reserves the statutory right to seek institutional legal representation and aid through the District Legal Services Authority (DLSA) / National Legal Services Authority (NALSA) under Section 12 of the Legal Services Authorities Act, 1987 (NALSA Helpline: 15100, Official Portal: https://nalsa.gov.in/legal-aid/).\n\n"
            "Requested next step: A qualified adviser should review the account, evidence, applicable law, and any filing deadline before a notice or complaint is sent.\n"
            "--------------------------------------------------------------------------------"
        )





def _reviewable_response(result: Dict[str, Any], transcript: str, meta: Dict[str, Any]) -> Dict[str, Any]:

    """Turn a keyword match into a cautious intake, not a legal conclusion."""

    category = result["category"]

    facts = dict(meta)

    if not facts.get("incident_location") and facts.get("location"):

        facts["incident_location"] = facts["location"]



    lang_code = facts.get("language_code") or facts.get("language")
    detected_lang = facts.get("detected_language")
    utterance_for_lang = meta.get("current_utterance") or transcript
    lang = detect_language(utterance_for_lang, lang_code=lang_code, detected_language=detected_lang)
    result["language"] = lang



    lang_fields = FIELDS.get(lang, FIELDS["en"])

    lang_issues = ISSUE_QUESTIONS.get(lang, ISSUE_QUESTIONS["en"])

    spec_q = lang_issues.get(category, lang_issues["GENERAL_CITIZEN_AID"])



    # Opportunistic extraction of already-stated facts from the person's account
    t_lower = transcript.lower()

    if not facts.get("incident_date"):
        date_patterns = [
            ("last night", "Last night"), ("काल रात्री", "काल रात्री"), ("कल रात", "कल रात"),
            ("yesterday", "Yesterday"), ("काल", "काल"), ("कल", "कल"),
            ("today", "Today"), ("आज", "आज"),
            ("last week", "Last week"), ("गेल्या आठवड्यात", "गेल्या आठवड्यात"), ("पिछले हफ्ते", "पिछले हफ्ते"),
            ("last month", "Last month"), ("गेल्या महिन्यात", "गेल्या महिन्यात"), ("पिछले महीने", "पिछले महीने"),
            ("days ago", "Few days ago"), ("दिवसांपूर्वी", "काही दिवसांपूर्वी"), ("दिन पहले", "कुछ दिन पहले")
        ]
        for pat, val in date_patterns:
            if pat in t_lower:
                facts["incident_date"] = val
                break

    if not facts.get("incident_location"):
        loc_patterns = [
            "swargate", "kothrud", "hadapsar", "hinjawadi", "viman nagar", "camp", "deccan",
            "pune", "mumbai", "thane", "nashik", "nagpur", "delhi", "bengaluru", "chennai", "hyderabad",
            "expressway", "highway", "juhu", "bandra", "dadar", "market",
            "पुणे", "मुंबई", "ठाणे", "नाशिक", "नागपूर", "रस्त्यावर", "हायवे", "मार्केट", "चौकात", "स्थानक", "दुकान", "गावात", "घरी"
        ]
        for loc_kw in loc_patterns:
            if loc_kw in t_lower:
                facts["incident_location"] = loc_kw.title()
                break

    if not facts.get("other_party"):
        party_patterns = [
            ("police", "Police"), ("पोलीस", "पोलीस"), ("पोलिस", "पोलीस"), ("थाने", "पोलीस"),
            ("bmc", "BMC / महानगरपालिका"), ("pmc", "PMC / महानगरपालिका"), ("municipality", "Municipality"),
            ("ward officer", "Ward Officer"), ("महापालिक", "महानगरपालिका"), ("नगरपालिक", "नगरपालिका"),
            ("thekedar", "Contractor / ठेकेदार"), ("contractor", "Contractor"), ("कंत्राटदार", "कंत्राटदार"),
            ("builder", "Builder"), ("बिल्डर", "बिल्डर"), ("मालक", "मालक / Employer"),
            ("landlord", "Landlord"), ("घरमालक", "घरमालक"), ("कंपनी", "कंपनी"),
            ("truck", "Truck Driver"), ("ट्रक", "ट्रक चालक"), ("ड्रायव्हर", "चालक"), ("driver", "Driver"),
            ("bank", "Bank"), ("बँक", "बँक"), ("loan app", "Loan App"), ("लोन ॲप", "लोन ॲप"),
            ("सावकार", "सावकार")
        ]
        for p_kw, p_label in party_patterns:
            if p_kw in t_lower:
                facts["other_party"] = p_label
                break

    # Prioritize situation-specific substantive legal questions
    cat_q = (
        CATEGORY_QUESTIONS.get(lang, {}).get(category)
        or (CATEGORY_QUESTIONS.get("en", {}).get(category) if lang == "en" else {})
    )

    fields = (
        ("specific_details", cat_q.get("specific_details") or spec_q),
        ("other_party", cat_q.get("other_party") or lang_fields.get("other_party", "Other party involved")),
        ("incident_date", cat_q.get("incident_date") or lang_fields.get("incident_date", "When did this incident happen?")),
        ("incident_location", cat_q.get("incident_location") or lang_fields.get("incident_location", "Where did this incident occur?")),
    )



    missing = [key for key, _ in fields if not str(facts.get(key, "")).strip()]

    questions = [question for key, question in fields if key in missing]

    account = transcript.strip() or "No account provided yet."

    supplied = [f"{label}: {facts[key]}" for key, label in (

        ("client_name", "Name"), ("incident_date", "Incident date"),

        ("incident_location", "Incident location"), ("other_party", "Other party"),

        ("specific_details", "Additional details"), ("insurer", "Insurer"),

        ("policy_no", "Policy number"), ("vehicle_no", "Vehicle number"),

    ) if str(facts.get(key, "")).strip()]

    reg_entry = get_source_register_entry(category)



    if missing:

        # Structured facts incomplete: ungrounded drafts are NEVER generated

        possible = POTENTIAL_LEGAL_REFERENCES.get(category, [])

        result["statutory_sections"] = [

            {

                "law": law,

                "details": "Potentially relevant; application depends on verified facts and local procedure.",

                "source_url": url,

                "review_date": reg_entry.get("review_date", REVIEWER_METADATA["review_date"]),

                "reviewed_by": reg_entry.get("reviewed_by", REVIEWER_METADATA["reviewer_name"]),

                "register_version": REGISTER_VERSION,

                "is_verified": False,

                "review_status": "PENDING_QUALIFIED_LEGAL_REVIEW",

            }

            for law, url in possible

        ]

        result["remedies"] = []

        result["authorities"] = []

        result["statutory_title"] = f"Initial intake: {category.replace('_', ' ').title()} (unconfirmed)"

        ai_narrative = _build_ai_synthesized_narrative(category, facts, transcript, lang)

        result["ai_synthesized_summary"] = ai_narrative

        cand_statutes = facts.get("candidate_statutes") or result.get("candidate_provisions")

        result["formal_document"] = _build_formal_legal_notice(
            category=category,
            facts=facts,
            transcript=transcript,
            lang=lang,
            candidate_statutes=cand_statutes,
            needs_more_information=True,
            questions=questions,
            supplied=supplied
        )

    else:

        # Structured facts confirmed: populate statutory_sections, remedies, and authorities directly from source register

        result["statutory_sections"] = [

            {

                "law": ref["law"],

                "details": ref.get("conditions", "Statutory provision compiled from primary sources pending qualified legal review."),

                "source_url": ref.get("source_url", ""),

                "act": ref.get("act", ""),

                "remedy": ref.get("remedy", ""),

                "review_date": reg_entry.get("review_date", REVIEWER_METADATA["review_date"]),

                "reviewed_by": reg_entry.get("reviewed_by", REVIEWER_METADATA["reviewer_name"]),

                "register_version": REGISTER_VERSION,

                "is_verified": reg_entry.get("is_verified", False),

                "review_status": "PENDING_QUALIFIED_LEGAL_REVIEW",

            }

            for ref in reg_entry.get("references", [])

        ]

        result["remedies"] = [

            ref["remedy"] for ref in reg_entry.get("references", []) if ref.get("remedy")

        ]

        result["authorities"] = [reg_entry["jurisdiction"]] if reg_entry.get("jurisdiction") else []

        title_prefix = reg_entry.get("category_title", category.replace('_', ' ').title())

        result["statutory_title"] = f"Structured intake: {title_prefix}"

        ai_narrative = _build_ai_synthesized_narrative(category, facts, transcript, lang)

        result["ai_synthesized_summary"] = ai_narrative

        cand_statutes = facts.get("candidate_statutes") or result.get("candidate_provisions")

        result["formal_document"] = _build_formal_legal_notice(
            category=category,
            facts=facts,
            transcript=transcript,
            lang=lang,
            candidate_statutes=cand_statutes,
            needs_more_information=False,
            questions=[],
            supplied=supplied
        )



    result["legal_aid_referral"] = {

        "authority": "District Legal Services Authority (DLSA) / NALSA",

        "helpline": "15100",

        "official_url": "https://nalsa.gov.in/legal-aid/",

        "eligibility_summary": reg_entry.get("legal_aid_path", "Check Section 12 criteria of Legal Services Authorities Act, 1987."),

        "documents_to_carry": [

            "Any photo identity card (Aadhaar / Voter ID / Ration Card)",

            "Income certificate or proof of marginal income (if applicable)",

            "All incident notices, receipts, muster cards, photographs, or call records"

        ],

        "disclaimer": "Eligibility for free legal aid is subject to verification of statutory criteria under the Legal Services Authorities Act, 1987."

    }



    # Voice-First Understand Your Rights Structured Analysis
    from backend.services.rights_explainer import build_understand_your_rights
    client_name = facts.get("client_name") or ""
    location = facts.get("incident_location") or facts.get("location") or ""
    cand_statutes = facts.get("candidate_statutes")
    rights_data = build_understand_your_rights(
        category=category,
        facts=facts,
        transcript=transcript,
        lang=lang,
        missing=missing,
        client_name=client_name,
        location=location,
        candidate_statutes=cand_statutes
    )
    result["understand_your_rights"] = rights_data

    templates = SPOKEN_TEMPLATES.get(lang, SPOKEN_TEMPLATES["en"])
    actions = ACTION_STEPS.get(lang, ACTION_STEPS["en"])
    is_revision = facts.get("revision_requested", False)
    is_followup = facts.get("is_followup_turn", False)

    # Check for urgent safety priority
    urgent_block = rights_data.get("urgent_help")
    urgent_prefix = f"{urgent_block['message']} " if urgent_block and urgent_block.get("is_urgent") else ""

    if missing:
        # Ask first missing question directly and conversationally
        question_to_ask = questions[0] if questions else spec_q
        if is_followup:
            # Subsequent turns: directly ask the question without formalities
            spoken_text = f"{urgent_prefix}{question_to_ask}"
        else:
            # First turn: crisp natural acknowledgement + question
            spoken_text = f"{urgent_prefix}{templates['first_turn'].format(spec_q=question_to_ask)}"
    else:
        if is_revision:
            spoken_text = templates.get("revised", templates["complete"])
        else:
            spoken_text = rights_data.get("spoken_scripts", {}).get("recap_spoken") or templates["complete"]
        if urgent_prefix:
            spoken_text = f"{urgent_prefix}{spoken_text}"



    result["spoken_text"] = spoken_text

    result["spoken_rights_shield_hi"] = spoken_text

    result["spoken_guidance_en"] = spoken_text

    result["action_steps"] = actions

    result["needs_more_information"] = bool(missing)

    result["follow_up_questions"] = questions

    result["meta"] = facts

    result["is_indic"] = (lang in ["hi", "mr", "ta", "te", "kn", "bn", "gu", "ml", "pa"])

    result["intake"] = {

        "status": "needs_details" if missing else "ready_for_human_review",

        "missing_facts": missing,

        "follow_up_questions": questions,

        "review_required": True,

        "category_confirmed": False,

    }

    return result





class OralAffidavitHasher:

    """Generates a SHA-256 fingerprint of the transcript, location, and timestamp."""

    @staticmethod

    def generate_hash(

        transcript: str,

        location: str = "Unspecified Location",

        timestamp_iso: str = None

    ) -> Dict[str, str]:

        ts = timestamp_iso or datetime.now(timezone.utc).isoformat()

        hasher = hashlib.sha256()

        payload = f"{transcript}|{location}|{ts}".encode("utf-8")

        hasher.update(payload)

        digest = hasher.hexdigest()



        certificate = (

            f"--- TRANSCRIPT FINGERPRINT ---\n"

            f"Digest (SHA-256): {digest}\n"

            f"UTC Timestamp:    {ts}\n"

            f"Origin Location:  {location}\n"

            f"Status:           Transcript metadata fingerprinted\n"

            f"Note:             Original audio and legal admissibility require separate review\n"

            f"--------------------------------------------------"

        )

        return {

            "sha256": digest,

            "timestamp": ts,

            "location": location,

            "certificate": certificate

        }





class GrassrootsLegalAdvisor:

    """Free Tier / Bharat Public Good."""



    CATEGORIES = {

        "WAGE_THEFT": [

            "salary", "wage", "तनख्वाह", "मजदूरी", "काम करवाया पैसे नहीं दिए", "contractor", "thekedar", "overtime", "unpaid", "वेतन",

            "पगार", "मजुरी", "சம்பளம்", "கூலி", "జీతం", "కూలీ", "ವೇತನ", "ಸಂಬಳ", "বেতন", "মজুরি", "પગાર", "મજૂરી", "ശമ്പളം", "ਤਨਖਾਹ"

        ],

        "LAND_GRABBING": [

            "land", "plot", "zamin", "जमीन", "जमीन हड़प", "कब्जा", "मकान खाली", "slum", "jhuggi", "patta", "forged deed", "दबंग",

            "सातबारा", "நிலம்", "ஆக்கிரமிப்பு", "భూమి", "ಆಸ್ತಿ", "জমি", "જમીન", "ഭൂമി", "ਜ਼ਮੀਨ"

        ],

        "LOAN_FRAUD": [

            "loan app", "लोन ऐप", "लोन एप", "recovery agent", "फर्जी लोन", "otp", "phishing", "blackmail", "photo morph", "मॉर्फ", "हैक",

            "पैसे कट गए", "कर्ज", "கடன் செயலி", "మోసం", "ಸಾಲ", "লোন", "ચીટિંગ", "തട്ടിപ്പ്", "ਧੋਖਾਧੜੀ"

        ],

        "POLICE_CUSTODY": [

            "police station", "police", "custody", "arrest", "thana", "थाने", "चौकी", "fir", "मारपीट", "lockup", "arrest memo",

            "पोलीस", "ठाण्यात", "காவல்", "கைது", "పోలీస్", "ಅರೆಸ್ಟ್", "থানা", "પોલીસ", "കസ്റ്റഡി", "ਹਿਰਾਸਤ"

        ],

        "DOMESTIC_VIOLENCE": [

            "domestic", "husband", "patni", "marpeet", "dowry", "दहेज", "खर्चा", "maintenance", "घर से निकाल दिया", "ससुराल",

            "नवरा", "बायको", "मारहाण", "குடும்ப வன்முறை", "గృహ హింస", "ದೌರ್ಜನ್ಯ", "গার্হস্থ্য হিংসা", "ઘરેલું હિંસા", "ഗാർഹിക പീഡനം", "ਘਰੇਲੂ ਹਿੰਸਾ"

        ],

        "CORRUPTION_RTI": [

            "bribe", "ghoos", "रिश्वत", "ration card", "राशन", "ration nahi mila", "pension", "पेंशन", "babu", "clerk", "sarkari",

            "लाच", "रेशन", "லஞ்சம்", "రేషన్", "లంచం", "ರೇಷನ್", "ಲಂಚ", "ঘুষ", "લાંચ", "കൈക്കൂലി", "ਵੱਢੀ"

        ],

        "STREET_VENDOR": [
            "street stall", "stall", "cart", "vendor", "hawker", "ठेला", "रेहड़ी", "दुकान", "bmc", "municipality", "svanidhi", "tvc",
            "फेरीवाला", "गाडीवर", "गाडी", "हातगाडी", "सामान", "हटवली", "तोडली", "तोडले", "नेले", "महापालिका", "नगरपालिका", "अतिक्रमण", "हटाया", "तोड़ा",
            "வியாபாரி", "தள்ளுவண்டி", "తోపుడు బండి", "ತಳ್ಳುಗಾಡಿ", "হকার", "લારી", "തട്ടുകട", "ਰੇਹੜੀ"
        ],

        "RELIGIOUS_GATHERING": [

            "church", "prayer", "चर्च", "प्रार्थना", "सत्संग", "धार्मिक", "पूजा", "வழிபாடு", "ప్రార్థన", "ಪೂಜೆ", "উপাসনা", "નમાજ"

        ]

    }



    def detect_category(self, text: str) -> str:

        text_lower = text.lower()

        priority = ["STREET_VENDOR", "RELIGIOUS_GATHERING", "WAGE_THEFT", "LAND_GRABBING", "LOAN_FRAUD", "DOMESTIC_VIOLENCE", "CORRUPTION_RTI", "POLICE_CUSTODY"]

        for cat in priority:

            keywords = self.CATEGORIES[cat]

            if any(k in text_lower for k in keywords):

                return cat

        return "GENERAL_CITIZEN_AID"



    def analyze(self, transcript: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        meta = meta or {}

        category = meta.get("category") or self.detect_category(transcript)

        return _reviewable_response({

            "tier": "BHARAT_GRASSROOTS_AID",

            "category": category,

        }, transcript, meta)





class EnterpriseLegalSuite:

    """Tier 2 / Pro / B2B Corporate Incident Response Suite."""



    def detect_category(self, text: str) -> str:
        text_lower = text.lower()
        if any(k in text_lower for k in ["rera", "builder", "flat", "possession", "occupancy certificate", "developer", "delay", "बिल्डर", "फ्लॅट"]):
            return "REAL_ESTATE_RERA"
        if any(k in text_lower for k in ["contract", "agreement", "msme", "vendor", "payment pending", "breach", "invoice", "करार", "कंत्राट"]):
            return "COMMERCIAL_CONTRACT_MSME"
        collision_terms = [
            "crash", "accident", "collision", "insurance", "hit and run", "अपघात", "धडकली", "ठोकली", "दुर्घटना", "एक्सीडेंट", "टक्कर"
        ]
        is_veh_collision = any(k in text_lower for k in collision_terms) or bool(
            re.search(r"\b(car|vehicle|truck|bike|bus|auto|scooter|गाडी|वाहन)\b.*?\b(hit|crash|struck|damaged|धडक|ठोकली|अपघात)\b", text_lower)
            or re.search(r"\b(hit|struck|damaged|धडक|ठोकली|अपघात)\b.*?\b(car|vehicle|truck|bike|bus|auto|scooter|गाडी|वाहन)\b", text_lower)
        )
        if is_veh_collision:
            return "MOTOR_ACCIDENT_PRO"
        grassroots_cat = GrassrootsLegalAdvisor().detect_category(text)
        return grassroots_cat if grassroots_cat != "GENERAL_CITIZEN_AID" else "MOTOR_ACCIDENT_PRO"



    def analyze(self, transcript: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        meta = meta or {}

        category = meta.get("category") or self.detect_category(transcript)

        return _reviewable_response({

            "tier": "ENTERPRISE_LEGAL_SUITE",

            "category": category,

        }, transcript, meta)





class NyayaVaniEngine:
    """Unified Dual-Tier Sovereign Legal Intelligence Engine."""

    def __init__(self):
        self.grassroots_advisor = GrassrootsLegalAdvisor()
        self.enterprise_advisor = EnterpriseLegalSuite()
        self.hasher = OralAffidavitHasher()
        self.graph_retriever = LegalGraphRetriever()

    def process_case(
        self,
        transcript: str,
        suite_tier: str = "AUTO_DETECT",
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        meta = dict(meta or {})
        text_lower = transcript.lower()

        # Knowledge Graph Candidate Retrieval Layer
        graph_res = self.graph_retriever.query(transcript)
        if "candidate_statutes" not in meta and graph_res.get("statutory_sections"):
            meta["candidate_statutes"] = graph_res.get("statutory_sections")

        # Determine Tier
        if suite_tier == "AUTO_DETECT":
            vendor_indicators = [
                "ठेला", "रेहड़ी", "दुकान", "फेरीवाला", "सामान", "हटवली", "तोडली", "महापालिका", "नगरपालिका",
                "street stall", "stall", "cart", "vendor", "hawker", "tvc", "svanidhi"
            ]
            is_vendor = any(k in text_lower for k in vendor_indicators)

            collision_terms = [
                "crash", "accident", "collision", "insurance claim", "hit and run",
                "अपघात", "धडकली", "ठोकली", "दुर्घटना", "एक्सीडेंट", "टक्कर",
                "விபத்து", "மோதியது", "ప్రమాదం", "ఢీకొంది", "ಅಪಘಾತ", "ಡಿಕ್ಕಿ",
                "দুর্ঘটনা", "ধাক্কা", "અકસ્માત", "ટક્કર", "അപകടം", "ਹਾਦਸਾ"
            ]
            is_collision = any(k in text_lower for k in collision_terms) or bool(
                re.search(r"\b(car|vehicle|truck|bike|bus|auto|scooter|गाडी|वाहन)\b.*?\b(hit|crash|struck|damaged|धडक|ठोकली|अपघात)\b", text_lower)
                or re.search(r"\b(hit|struck|damaged|धडक|ठोकली|अपघात)\b.*?\b(car|vehicle|truck|bike|bus|auto|scooter|गाडी|वाहन)\b", text_lower)
            )
            corporate_terms = ["rera", "builder", "agreement", "msme", "invoice overdue", "बिल्डर", "फ्लॅट", "उद्यम"]
            is_corporate = any(k in text_lower for k in corporate_terms)

            if (is_corporate or is_collision) and not is_vendor:
                suite_tier = "ENTERPRISE_LEGAL_SUITE"
            else:
                suite_tier = "BHARAT_GRASSROOTS_AID"

        if suite_tier == "ENTERPRISE_LEGAL_SUITE":
            result = self.enterprise_advisor.analyze(transcript, meta)
        else:
            result = self.grassroots_advisor.analyze(transcript, meta)

        # Attach Graph Candidate Sourcing and Upfront Legality Verdict
        result["legality_verdict"] = graph_res.get("legality_verdict")
        result["graph_subgraph"] = graph_res.get("subgraph")
        result["graph_root_nodes"] = [n.get("id") for n in graph_res.get("root_nodes", [])]

        # Merge candidate provisions without overriding confirmed statutory facts
        existing_laws = {s.get("law") for s in result.get("statutory_sections", [])}
        candidate_sections = []
        for cand in graph_res.get("statutory_sections", []):
            if cand.get("law") not in existing_laws:
                candidate_sections.append({
                    "law": cand.get("law"),
                    "details": cand.get("details"),
                    "source_url": "https://www.indiacode.nic.in/",
                    "review_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
                    "is_verified": False,
                    "is_candidate": True
                })
                existing_laws.add(cand.get("law"))

        result["candidate_provisions"] = candidate_sections

        # Geo-Resolution for Regional Jurisdiction & Authorities
        loc_str = meta.get("incident_location") or meta.get("location") or ""
        city_profile = GeoLanguageService.resolve_city_profile(loc_str)
        result["geo_profile"] = city_profile

        if result.get("legal_aid_referral") and city_profile:
            result["legal_aid_referral"]["local_authority"] = city_profile.get("legal_aid_authority")
            result["legal_aid_referral"]["municipal_body"] = city_profile.get("municipal_body")
            result["legal_aid_referral"]["police_emergency"] = city_profile.get("police_emergency")

        # Cryptographic Hash & Certificate
        loc = meta.get("location", "India")
        affidavit = self.hasher.generate_hash(transcript, location=loc)
        result["affidavit_evidence"] = affidavit
        result["input_transcript"] = transcript

        return result

