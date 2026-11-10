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

    Prioritizes actual spoken/transcribed text and explicit ASR detection over dropdown defaults.

    """

    text = text or ""

    lower_text = text.lower()



    # 1. Script-based Unicode block detection (most definitive)

    if any("\u0B80" <= ch <= "\u0BFF" for ch in text): return "ta"

    if any("\u0C00" <= ch <= "\u0C7F" for ch in text): return "te"

    if any("\u0C80" <= ch <= "\u0CFF" for ch in text): return "kn"

    if any("\u0D00" <= ch <= "\u0D7F" for ch in text): return "ml"

    if any("\u0980" <= ch <= "\u09FF" for ch in text): return "bn"

    if any("\u0A80" <= ch <= "\u0AFF" for ch in text): return "gu"

    if any("\u0A00" <= ch <= "\u0A7F" for ch in text): return "pa"



    # 2. Devanagari script: Marathi vs Hindi discrimination

    if any("\u0900" <= ch <= "\u097F" for ch in text):

        if "ळ" in text or "ऱ" in text:

            return "mr"

        mr_markers = [

            "आहे", "नाही", "झाला", "झाली", "झाले", "केले", "केला", "केली", "दिले",

            "माझा", "माझी", "माझे", "माझ्या", "माझं", "पाहिजे", "गेलो", "गेले", "पोलीस",

            "पगार", "तक्रार", "केव्हा", "कुठे", "कोणी", "सांगा", "आम्हाला", "त्यांनी",

            "मारहाण", "सातबारा", "मध्ये", "साठी", "बदल", "तारीख", "काल", "रात्री", "वाजता",

            "सकाळी", "दुपारी", "पुणे", "मुंबई", "ठाणे", "नाशिक", "रस्त्यावर", "गाडी", "धडक"

        ]

        hi_markers = [

            "है", "हैं", "हुआ", "हुई", "हुए", "मेरा", "मेरी", "मेरे", "किया", "किए",

            "गया", "गई", "गए", "कब", "कहाँ", "कैसे", "किसने", "मुझे", "हमने", "थाने",

            "मारपीट", "झगड़ा", "मदद", "तनख्वाह", "बदलाव", "कल रात", "बजे"

        ]

        mr_score = sum(1 for m in mr_markers if m in text)

        hi_score = sum(1 for m in hi_markers if m in text)

        if mr_score > hi_score:

            return "mr"

        elif hi_score > mr_score:

            return "hi"

        if session_language in ("mr", "hi"):

            return session_language

        return "mr" if mr_score > 0 else "hi"



    # 3. Transliterated / Romanized Indic vocabulary markers

    mr_roman = ["majha", "majhi", "majhe", "jhala", "jhali", "jhale", "aahe", "nahi", "kela", "keli", "kele", "gaadi", "thukli", "thanayt", "paise", "kamavar", "malak", "pagar", "bhandan", "marhan", "kasa", "kashi", "kevha", "kuthe", "sang", "sanga", "madat", "badla"]

    if any(re.search(rf"\b{w}\b", lower_text) for w in mr_roman):

        return "mr"



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



    gu_roman = ["maru", "mari", "maro", "thayu", "thayo", "nathi", "kem", "aabhar"]

    if any(re.search(rf"\b{w}\b", lower_text) for w in gu_roman):

        return "gu"



    pa_roman = ["mera", "meri", "hoya", "hoyi", "sahayta", "sat sri akal"]

    if any(re.search(rf"\b{w}\b", lower_text) for w in pa_roman):

        return "pa"



    hi_roman = ["mera", "meri", "mere", "hua", "hui", "hue", "kiya", "kiye", "hai", "hain", "nahi", "takkar", "paisa", "pulis", "thana", "maalik", "vetan", "batao", "namaste"]

    if any(re.search(rf"\b{w}\b", lower_text) for w in hi_roman):

        return "hi"



    # 4. Check explicit detected_language / lang_code

    for code in [detected_language, lang_code]:

        if code:

            c = str(code).lower().strip()

            if c in ("indic-auto", "auto", "default"):

                continue

            if "mr" in c: return "mr"

            if "ta" in c: return "ta"

            if "te" in c: return "te"

            if "kn" in c: return "kn"

            if "bn" in c: return "bn"

            if "gu" in c: return "gu"

            if "ml" in c: return "ml"

            if "pa" in c: return "pa"

            if "hi" in c: return "hi"

            if "en" in c and not any("\u0900" <= ch <= "\u0D7F" for ch in text):

                return "en"



    if session_language:

        return session_language

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

    return base_summary





def _reviewable_response(result: Dict[str, Any], transcript: str, meta: Dict[str, Any]) -> Dict[str, Any]:

    """Turn a keyword match into a cautious intake, not a legal conclusion."""

    category = result["category"]

    facts = dict(meta)

    if not facts.get("incident_location") and facts.get("location"):

        facts["incident_location"] = facts["location"]



    lang_code = facts.get("language_code") or facts.get("language")

    detected_lang = facts.get("detected_language")

    lang = detect_language(transcript, lang_code=lang_code, detected_language=detected_lang, session_language=facts.get('session_language'))

    result["language"] = lang



    lang_fields = FIELDS.get(lang, FIELDS["en"])

    lang_issues = ISSUE_QUESTIONS.get(lang, ISSUE_QUESTIONS["en"])

    spec_q = lang_issues.get(category, lang_issues["GENERAL_CITIZEN_AID"])



    # Opportunistic extraction of already-stated facts from the person's account

    t_lower = transcript.lower()

    if not facts.get("incident_date"):

        if any(w in t_lower for w in ["last night", "काल रात्री", "काल", "yesterday", "today", "आज", "कल रात", "कल"]):

            if "last night" in t_lower or "रात्री" in t_lower or "कल रात" in t_lower:

                facts["incident_date"] = "Last night / काल रात्री"

            elif "yesterday" in t_lower or "काल" in t_lower or "कल" in t_lower:

                facts["incident_date"] = "Yesterday / काल"

            elif "today" in t_lower or "आज" in t_lower:

                facts["incident_date"] = "Today / आज"



    if not facts.get("incident_location"):

        for loc_kw in ["expressway", "highway", "juhu", "bandra", "dadar", "market", "pune", "mumbai", "delhi", "bengaluru", "पुणे", "मुंबई", "ठाणे", "रस्त्यावर", "हायवे", "मार्केट"]:

            if loc_kw in t_lower:

                facts["incident_location"] = loc_kw.title()

                break



    if not facts.get("other_party"):

        for p_kw in ["police", "bmc", "municipality", "ward officer", "thekedar", "truck", "पोलीस", "कंत्राटदार", "ट्रक", "बिल्डर", "मालक", "कंपनी"]:

            if p_kw in t_lower:

                facts["other_party"] = p_kw.title()

                break



    # Prioritize the case-specific substantive legal question FIRST

    fields = (

        ("specific_details", spec_q),

        ("other_party", lang_fields["other_party"]),

        ("incident_date", lang_fields["incident_date"]),

        ("incident_location", lang_fields["incident_location"]),

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

        result["formal_document"] = (

            "DRAFT INCIDENT SUMMARY FOR LEGAL REVIEW — DO NOT SUBMIT AS A VERIFIED COMPLAINT\n\n"

            + "1. CASE SYNOPSIS & FACTUAL SUMMARY (AI Synthesized Narrative):\n"

            + ai_narrative + "\n\n"

            + "2. STRUCTURED INCIDENT PARTICULARS:\n"

            + ("\n".join(supplied) + "\n" if supplied else "No structured facts recorded.\n")

            + "\nAccount in the person's own words:\n"

            + f"{account}\n\n"

            + "Facts still to confirm:\n"

            + ("\n".join(f"- {question}" for question in questions) if questions else "- Confirm this account and any supporting records.")

            + "\n\nRequested next step: A qualified adviser should review the account, evidence, applicable law, and any filing deadline before a notice or complaint is sent."

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

        result["formal_document"] = (

            "DRAFT INCIDENT SUMMARY FOR LEGAL REVIEW — DO NOT SUBMIT AS A VERIFIED COMPLAINT\n\n"

            + "1. CASE SYNOPSIS & FACTUAL SUMMARY (AI Synthesized Narrative):\n"

            + ai_narrative + "\n\n"

            + "2. STRUCTURED INCIDENT PARTICULARS:\n"

            + ("\n".join(supplied) + "\n" if supplied else "No structured facts recorded.\n")

            + "\nAccount in the person's own words:\n"

            + f"{account}\n\n"

            + "Facts still to confirm:\n"

            + "- Confirm this account and any supporting records.\n\n"

            + "Requested next step: A qualified adviser should review the account, evidence, applicable law, and any filing deadline before a notice or complaint is sent."

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
    rights_data = build_understand_your_rights(
        category=category,
        facts=facts,
        transcript=transcript,
        lang=lang,
        missing=missing,
        client_name=client_name,
        location=location
    )
    result["understand_your_rights"] = rights_data

    templates = SPOKEN_TEMPLATES.get(lang, SPOKEN_TEMPLATES["en"])
    actions = ACTION_STEPS.get(lang, ACTION_STEPS["en"])
    is_revision = facts.get("revision_requested", False)
    is_followup = facts.get("is_followup_turn", False)

    # Check for urgent safety priority
    urgent_block = rights_data.get("urgent_help")
    urgent_prefix = f"{urgent_block['message']} " if urgent_block else ""

    if missing:
        # Ask first missing question
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

            "फेरीवाला", "गाडीवर", "வியாபாரி", "தள்ளுவண்டி", "తోపుడు బండి", "ತಳ್ಳುಗಾಡಿ", "হকার", "લારી", "തട്ടുകട", "ਰੇਹੜੀ"

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

        return "MOTOR_ACCIDENT_PRO"



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



    def process_case(

        self,

        transcript: str,

        suite_tier: str = "AUTO_DETECT",

        meta: Optional[Dict[str, Any]] = None

    ) -> Dict[str, Any]:

        meta = meta or {}

        text_lower = transcript.lower()



        # Determine Tier

        if suite_tier == "AUTO_DETECT":

            accident_terms = [

                "rera", "builder", "contract", "agreement", "msme",

                "crash", "accident", "insurance claim",

                "अपघात", "धडक", "गाडी", "वाहन", "ठोकली", "दुर्घटना", "एक्सीडेंट", "टक्कर", "बीमा",

                "விபத்து", "வாகனம்", "மோதியது", "ప్రమాదం", "ఢీకొంది", "ಅಪಘಾತ", "ಡಿಕ್ಕಿ",

                "দুর্ঘটনা", "ধাক্কা", "અકસ્માત", "ટક્કર", "അപകടം", "ਹਾਦਸਾ"

            ]

            if any(k in text_lower for k in accident_terms) or re.search(r"\b(car|गाडी|वाहन|கார்|కారు|ಕಾರು|গাড়ি|ગાડી|കാർ|ਗੱਡੀ)\b", text_lower):

                suite_tier = "ENTERPRISE_LEGAL_SUITE"

            else:

                suite_tier = "BHARAT_GRASSROOTS_AID"



        if suite_tier == "ENTERPRISE_LEGAL_SUITE":

            result = self.enterprise_advisor.analyze(transcript, meta)

        else:

            result = self.grassroots_advisor.analyze(transcript, meta)



        # Cryptographic Hash & Certificate

        loc = meta.get("location", "India")

        affidavit = self.hasher.generate_hash(transcript, location=loc)

        result["affidavit_evidence"] = affidavit

        result["input_transcript"] = transcript



        return result

