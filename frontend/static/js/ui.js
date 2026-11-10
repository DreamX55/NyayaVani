/**
 * NyayaVani (न्यायवाणी) — UI Rendering & Interaction Module
 * Decouples presentation logic, conversational message rendering,
 * and user interactions from network and audio drivers.
 */

import { ThemeManager } from './theme.js';
import { AudioEngine, rightsDataStore } from './audio.js';

export const presetsData = [
  { id: 'vendor', title: 'My street stall is being removed', category: 'STREET_VENDOR', tier: 'BHARAT_GRASSROOTS_AID', icon: '🏛️', text: 'My street stall is being removed. What should I do?', client_name: '', location: '' },
  { id: 'wages', title: 'My wages have not been paid', category: 'WAGE_THEFT', tier: 'BHARAT_GRASSROOTS_AID', icon: '⚖️', text: 'My employer has not paid my wages. What information should I collect?', client_name: '', location: '' },
  { id: 'loan', title: 'A loan app is threatening me', category: 'LOAN_FRAUD', tier: 'BHARAT_GRASSROOTS_AID', icon: '📱', text: 'A loan app is threatening me and contacting my family. What can I do?', client_name: '', location: '' },
  { id: 'accident', title: 'I was in a road accident', category: 'MOTOR_ACCIDENT', tier: 'ENTERPRISE_LEGAL_SUITE', icon: '🚗', text: 'I was in a road accident. Help me organize what happened and prepare an insurance claim draft.', client_name: '', location: '' }
];

export const UI_LANG = {
  en: {
    talkingTitle: "🎙️ AI Talking Agent · Socratic Intake",
    talkingSub: "Please answer the single active question below to clarify your account:",
    currentQuestion: "Current Question (Speak or Type to Answer):",
    upcomingQuestions: "Upcoming in conversation:",
    speakBtn: "🎙️ Speak Answer (Tap to talk)",
    speakChangesBtn: "🎙️ Speak Changes (e.g. 'Change date to...')",
    sendBtn: "Send",
    placeholder: "Speak your answer or type here...",
    draftPending: "⏳ Draft incident summary will compile once your facts are gathered",
    draftReady: "✅ Information Recorded · Draft Prepared for Review (Not Legal Advice)",
    spokenTitle: "🔊 Spoken Guidance",
    actionsTitle: "// IMMEDIATE RECOMMENDED NEXT ACTIONS",
    draftBoxTitle: "📄 Draft Incident Summary for Review — Not Legal Advice",
    rightsTitle: "Understand Your Rights & Applicable Dhaara",
    listenRights: "Listen to Rights",
    recap1Min: "1-Min Recap",
    simplerWords: "In Simpler Words",
    card1NoticeTitle: "Drafted Formal Notice & Representation",
    outboundDisabled: "Outbound transmission disabled (Review only)",
    copyTextBtn: "Copy Text",
    printPdfBtn: "Print / Save PDF",
    approvedSignoff: "Approved Signoff Roles:",
    signoffNotice: "Signing does <strong>NOT</strong> transmit this document to police, insurer, or court. It creates an internal timestamped review record.",
    whatNextTitle: "📌 What You Should Do Next",
    dlsaTitle: "🏛️ DLSA National Legal Services Authority Helpline: 15100",
    dlsaCallBtn: "Call 15100",
    revisionPrompt: "Need to change a detail or add facts?",
    editDetails: "✏️ Edit Details",
    orSpeak: "or tap the sphere to speak.",
    orbStatusReady: "Living Voice Sphere · Ready"
  },
  hi: {
    talkingTitle: "🎙️ बोलता कानूनी सहायक · बातचीत एवं सवाल",
    talkingSub: "कृपया नीचे दिए गए सवाल का जवाब दें:",
    currentQuestion: "वर्तमान प्रश्न (बोलकर या लिखकर उत्तर दें):",
    upcomingQuestions: "आगामी प्रश्न:",
    speakBtn: "🎙️ बोलकर जवाब दें (माइक दबाएं)",
    speakChangesBtn: "🎙️ बोलकर बदलाव बताएं (उदा: 'तारीख बदलकर...')",
    sendBtn: "भेजें",
    placeholder: "अपना जवाब बोलें या यहाँ लिखें...",
    draftPending: "⏳ पूरी जानकारी मिलने के बाद ड्राफ्ट सारांश तैयार होगा",
    draftReady: "✅ पूरी जानकारी दर्ज · ड्राफ्ट सारांश समीक्षा के लिए तैयार (कानूनी सलाह नहीं)",
    spokenTitle: "🔊 बोलकर बताई गई सलाह",
    actionsTitle: "// तुरंत क्या करना है · जरूरी कदम",
    draftBoxTitle: "📄 ड्राफ्ट घटना सारांश (समीक्षा हेतु - कानूनी सलाह नहीं)",
    rightsTitle: "अपने कानूनी अधिकार एवं धाराएं समझें",
    listenRights: "अधिकार सुनें",
    recap1Min: "1-मिनट सारांश",
    simplerWords: "सरल शब्दों में समझें",
    card1NoticeTitle: "प्रारूपित औपचारिक विधिक नोटिस एवं अभ्यावेदन",
    outboundDisabled: "बाह्य प्रेषण निष्क्रिय (केवल समीक्षा)",
    copyTextBtn: "कॉपी करें",
    printPdfBtn: "प्रिंट / PDF सहेजें",
    approvedSignoff: "अनुमोदित हस्ताक्षरकर्ता भूमिकाएं:",
    signoffNotice: "हस्ताक्षर करने से यह दस्तावेज पुलिस, बीमाकर्ता या न्यायालय को <strong>नहीं</strong> भेजा जाता। यह केवल एक आंतरिक समीक्षा रिकॉर्ड बनाता है।",
    whatNextTitle: "📌 आपको आगे क्या करना चाहिए",
    dlsaTitle: "🏛️ DLSA राष्ट्रीय विधिक सेवा प्राधिकरण हेल्पलाइन: 15100",
    dlsaCallBtn: "15100 पर कॉल करें",
    revisionPrompt: "क्या कोई विवरण बदलना है या तथ्य जोड़ने हैं?",
    editDetails: "✏️ विवरण बदलें",
    orSpeak: "या बोलने के लिए गोले को स्पर्श करें।",
    orbStatusReady: "सजीव वॉयस गोला · तैयार"
  },
  mr: {
    talkingTitle: "🎙️ बोलणारा कायदेशीर सहाय्यक · विचारपूस",
    talkingSub: "कृपया खालील प्रश्नाचे उत्तर द्या:",
    currentQuestion: "सध्याचा प्रश्न (बोलून किंवा लिहून उत्तर द्या):",
    upcomingQuestions: "पुढील प्रश्न:",
    speakBtn: "🎙️ बोलून उत्तर द्या (माइक दाबा)",
    speakChangesBtn: "🎙️ बोलून बदल सांगा (उदा: 'तारीख बदला...')",
    sendBtn: "पाठवा",
    placeholder: "बोलून उत्तर द्या किंवा येथे लिहा...",
    draftPending: "⏳ संपूर्ण माहिती मिळाल्यावर मसुदा सारांश तयार होईल",
    draftReady: "✅ सर्व माहिती नोंदवली · मसुदा पुनरावलोकनार्थ तयार (कायदेशीर सल्ला नाही)",
    spokenTitle: "🔊 बोलून दिलेला सल्ला",
    actionsTitle: "// ताबडतोब काय करावे · महत्त्वाचे पाऊल",
    draftBoxTitle: "📄 मसुदा घटना सारांश (पुनरावलोकनार्थ - कायदेशीर सल्ला नाही)",
    rightsTitle: "आपले कायदेशीर हक्क आणि कलम समजून घ्या",
    listenRights: "हक्क ऐका",
    recap1Min: "1-मिनिट सारांश",
    simplerWords: "सोप्या शब्दांत समजून घ्या",
    card1NoticeTitle: "तयार केलेली औपचारिक कायदेशीर नोटीस व निवेदन",
    outboundDisabled: "बाहेर पाठवणे बंद (केवळ पुनरावलोकन)",
    copyTextBtn: "प्रत बनवा",
    printPdfBtn: "मुद्रित करा / PDF साठवा",
    approvedSignoff: "मान्यताप्राप्त स्वाक्षरीकर्ता भूमिका:",
    signoffNotice: "स्वाक्षरी केल्याने हा दस्तऐवज पोलीस, विमा कंपनी किंवा न्यायालयात <strong>पाठवला जात नाही</strong>. हा फक्त अंतर्गत पुनरावलोकन नोंद तयार करतो.",
    whatNextTitle: "📌 तुम्ही पुढे काय केले पाहिजे",
    dlsaTitle: "🏛️ DLSA राष्ट्रीय विधी सेवा प्राधिकरण हेल्पलाइन: 15100",
    dlsaCallBtn: "15100 वर कॉल करा",
    revisionPrompt: "काही तपशील बदलायचा आहे किंवा माहिती जोडायची आहे का?",
    editDetails: "✏️ तपशील बदला",
    orSpeak: "किंवा बोलण्यासाठी गोलाला स्पर्श करा.",
    orbStatusReady: "सजीव व्हॉइस गोल · सज्ज"
  },
  gu: {
    talkingTitle: "🎙️ બોલતો કાનૂની સહાયક",
    talkingSub: "નીચેના પ્રશ્નનો જવાબ આપો:",
    currentQuestion: "હાલનો પ્રશ્ન (બોલીને અથવા લખીને જવાબ આપો):",
    upcomingQuestions: "આગામી પ્રશ્નો:",
    speakBtn: "🎙️ બોલીને જવાબ આપો (Tap to talk)",
    speakChangesBtn: "🎙️ બોલીને ફેરફાર જણાવો",
    sendBtn: "મોકલો",
    placeholder: "બોલીને જવાબ આપો અથવા અહીં લખો...",
    draftPending: "⏳ સંપૂર્ણ વિગતો મળ્યા પછી ડ્રાફ્ટ તૈયાર થશે",
    draftReady: "✅ તમામ માહિતી નોંધાઈ ગઈ છે · ડ્રાફ્ટ તૈયાર છે (કાનૂની સલાહ નથી)",
    spokenTitle: "🔊 બોલીને આપેલી સલાહ",
    actionsTitle: "// તાત્કાલિક કરવાના પગલાં",
    draftBoxTitle: "📄 ડ્રાફ્ટ ઘટના સારાંશ (સમીક્ષા માટે - કાનૂની સલાહ નથી)",
    rightsTitle: "તમારા કાનૂની અધિકારો અને લાગુ કલમો સમજો",
    listenRights: "અધિકારો સાંભળો",
    recap1Min: "૧-મિનિટ સારાંશ",
    simplerWords: "સરળ શબ્દોમાં સમજો",
    card1NoticeTitle: "તૈયાર કરેલ કાનૂની નોટિસ અને રજૂઆત",
    outboundDisabled: "માત્ર ચકાસણી માટે (બાહ્ય મોકલવું બંધ)",
    copyTextBtn: "નકલ કરો",
    printPdfBtn: "પ્રિન્ટ / PDF સાચવો",
    approvedSignoff: "મંજૂર સહીકર્તા ભૂમિકાઓ:",
    signoffNotice: "આ દસ્તાવેજ પર સહી કરવાથી તે પોલીસ કે કોર્ટમાં <strong>જતો નથી</strong>. આ આંતરિક સમીક્ષા રેકોર્ડ બનાવે છે.",
    whatNextTitle: "📌 આગળ શું પગલાં લેવા",
    dlsaTitle: "🏛️ DLSA રાષ્ટ્રીય કાનૂની સેવા સત્તામંડળ હેલ્પલાઇન: ૧૫૧૦૦",
    dlsaCallBtn: "૧૫૧૦૦ પર કૉલ કરો",
    revisionPrompt: "વિગતો બદલવી છે કે નવી હકીકત ઉમેરવી છે?",
    editDetails: "✏️ વિગતો સુધારો",
    orSpeak: "અથવા બોલવા માટે ગોળાને સ્પર્શ કરો.",
    orbStatusReady: "સજીવ અવાજ ગોળ · તૈયાર"
  },
  ta: {
    talkingTitle: "🎙️ பேசும் சட்ட உதவியாளர்",
    talkingSub: "கீழே உள்ள கேள்விக்கு பதிலளிக்கவும்:",
    currentQuestion: "தற்போதைய கேள்வி (பேசி அல்லது எழுதி பதிலளிக்கவும்):",
    upcomingQuestions: "அடுத்த கேள்விகள்:",
    speakBtn: "🎙️ பேசி பதிலளிக்கவும் (Tap to talk)",
    speakChangesBtn: "🎙️ பேசி மாற்றங்களை கூறவும்",
    sendBtn: "அனுப்புக",
    placeholder: "பேசி பதிலளிக்கவும் அல்லது எழுதவும்...",
    draftPending: "⏳ முழு விவரங்கள் கிடைத்தவுடன் வரைவு ஆவணம் தோன்றும்",
    draftReady: "✅ அனைத்து விவரங்களும் பெறப்பட்டன · வரைவு தயார் (சட்ட ஆலோசனை அல்ல)",
    spokenTitle: "🔊 வாய்மொழி சட்ட ஆலோசனை",
    actionsTitle: "// உடனடியாக செய்ய வேண்டியவை",
    draftBoxTitle: "📄 வரைவு நிகழ்வு சுருக்கம் (சட்ட ஆலோசனை அல்ல)",
    rightsTitle: "உங்கள் சட்ட உரிமைகள் மற்றும் சட்டப்பிரிவுகள்",
    listenRights: "உரிமைகளைக் கேளுங்கள்",
    recap1Min: "1-நிமிட சுருக்கம்",
    simplerWords: "எளிய வார்த்தைகளில்",
    card1NoticeTitle: "சட்டபூர்வ அறிவிப்பு மற்றும் மனு",
    outboundDisabled: "வெளியே அனுப்புவது முடக்கப்பட்டது (மதிப்பாய்வுக்கு மட்டும்)",
    copyTextBtn: "நகலெடுக்க",
    printPdfBtn: "அச்சிட / PDF சேமிக்க",
    approvedSignoff: "அங்கீகரிக்கப்பட்ட கையொப்பமிடும் பொறுப்புகள்:",
    signoffNotice: "கையொப்பமிடுவதால் இது காவல்துறைக்கோ நீதிமன்றத்திற்கோ அனுப்பப்படாது.",
    whatNextTitle: "📌 அடுத்து என்ன செய்ய வேண்டும்",
    dlsaTitle: "🏛️ DLSA தேசிய சட்ட சேவைகள் ஆணைய உதவி எண்: 15100",
    dlsaCallBtn: "15100 ஐ அழைக்கவும்",
    revisionPrompt: "விவரங்களை மாற்ற வேண்டுமா?",
    editDetails: "✏️ விவரங்களை மாற்று",
    orSpeak: "அல்லது பேச கோளத்தைத் தொடவும்.",
    orbStatusReady: "வாழும் குரல் கோளம் · தயார்"
  },
  te: {
    talkingTitle: "🎙️ మాట్లాడే న్యాయ సహాయకుడు",
    talkingSub: "క్రింది ప్రశ్నకు సమాధానం ఇవ్వండి:",
    currentQuestion: "ప్రస్తుత ప్రశ్న (మాట్లాడి లేదా టైప్ చేసి సమాధానం ఇవ్వండి):",
    upcomingQuestions: "రాబోయే ప్రశ్నలు:",
    speakBtn: "🎙️ మాట్లాడి సమాధానం ఇవ్వండి (Tap to talk)",
    speakChangesBtn: "🎙️ మాట్లాడి మార్పులు చెప్పండి",
    sendBtn: "పంపండి",
    placeholder: "మాట్లాడండి లేదా ఇక్కడ టైప్ చేయండి...",
    draftPending: "⏳ పూర్తి వివరాలు వచ్చిన తర్వాత డ్రాఫ్ట్ సారాంశం వస్తుంది",
    draftReady: "✅ పూర్తి వివరాలు సేకరించబడ్డాయి · డ్రాఫ్ట్ సిద్ధం (చట్టపరమైన సలహా కాదు)",
    spokenTitle: "🔊 వాయిస్ సలహా",
    actionsTitle: "// తక్షణమే చేయవలసిన పనులు",
    draftBoxTitle: "📄 డ్రాఫ్ట్ ఇన్సిడెంట్ సారాంశం (చట్టపరమైన సలహా కాదు)",
    rightsTitle: "మీ చట్టపరమైన హక్కులు మరియు సెక్షన్లు",
    listenRights: "హక్కులను వినండి",
    recap1Min: "1-నిమిషం సారాంశం",
    simplerWords: "సరళమైన పదాలలో",
    card1NoticeTitle: "చట్టపరమైన నోటీసు మరియు ప్రాతినిధ్యం",
    outboundDisabled: "బయటకు పంపడం నిలిపివేయబడింది (సమీక్ష కొరకు మాత్రమే)",
    copyTextBtn: "కాపీ చేయండి",
    printPdfBtn: "ప్రింట్ / PDF",
    approvedSignoff: "ఆమోదించబడిన సంతకం పాత్రలు:",
    signoffNotice: "సంతకం చేయడం ద్వారా ఇది పోలీసులకు లేదా కోర్టుకు పంపబడదు.",
    whatNextTitle: "📌 తరువాత మీరు ఏమి చేయాలి",
    dlsaTitle: "🏛️ DLSA నేషనల్ లీగల్ సర్వీసెస్ అథారిటీ హెల్ప్‌లైన్: 15100",
    dlsaCallBtn: "15100 కి కాల్ చేయండి",
    revisionPrompt: "వివరాలను మార్చాలనుకుంటున్నారా?",
    editDetails: "✏️ వివరాలు మార్చండి",
    orSpeak: "లేదా మాట్లాడటానికి గోళాన్ని తాకండి.",
    orbStatusReady: "సజీవ వాయిస్ గోళం · సిద్ధం"
  },
  kn: {
    talkingTitle: "🎙️ ಮಾತನಾಡುವ ಕಾನೂನು ಸಹಾಯಕ",
    talkingSub: "ಕೆಳಗಿನ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸಿ:",
    currentQuestion: "ಪ್ರಸ್ತುತ ಪ್ರಶ್ನೆ (ಮಾತನಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ ಉತ್ತರಿಸಿ):",
    upcomingQuestions: "ಮುಂದಿನ ಪ್ರಶ್ನೆಗಳು:",
    speakBtn: "🎙️ ಮಾತನಾಡಿ ಉತ್ತರಿಸಿ (Tap to talk)",
    speakChangesBtn: "🎙️ ಮಾತನಾಡಿ ಬದಲಾವಣೆ ತಿಳಿಸಿ",
    sendBtn: "ಕಳುಹಿಸಿ",
    placeholder: "ಮಾತನಾಡಿ ಅಥವಾ ಇಲ್ಲಿ ಬರೆಯಿರಿ...",
    draftPending: "⏳ ಸಂಪೂರ್ಣ ಮಾಹಿತಿ ಸಿಕ್ಕ ನಂತರ ಕರಡು ಸಿದ್ಧವಾಗುತ್ತದೆ",
    draftReady: "✅ ಎಲ್ಲಾ ವಿವರಗಳು ದಾಖಲಾಗಿವೆ · ಕರಡು ಸಿದ್ಧವಾಗಿದೆ (ಕಾನೂನು ಸಲಹೆಯಲ್ಲ)",
    spokenTitle: "🔊 ಧ್ವನಿ ಸಲಹೆ",
    actionsTitle: "// ತಕ್ಷಣ ಕೈಗೊಳ್ಳಬೇಕಾದ ಕ್ರಮಗಳು",
    draftBoxTitle: "📄 ಕರಡು ಘಟನಾ ಸಾರಾಂಶ (ಕಾನೂನು ಸಲಹೆಯಲ್ಲ)",
    rightsTitle: "ನಿಮ್ಮ ಕಾನೂನು ಹಕ್ಕುಗಳು ಮತ್ತು ಕಲಮುಗಳು",
    listenRights: "ಹಕ್ಕುಗಳನ್ನು ಕೇಳಿ",
    recap1Min: "1-ನಿಮಿಷದ ಸಾರಾಂಶ",
    simplerWords: "ಸರಳ ಪದಗಳಲ್ಲಿ",
    card1NoticeTitle: "ಕರಡು ಕಾನೂನು ನೋಟಿಸ್",
    outboundDisabled: "ಬಾಹ್ಯ ರವಾನೆ ನಿಷ್ಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ (ಪರಿಶೀಲನೆಗೆ ಮಾತ್ರ)",
    copyTextBtn: "ನಕಲಿಸಿ",
    printPdfBtn: "ಮುದ್ರಿಸಿ / PDF",
    approvedSignoff: "ಅನುಮೋದಿತ ಸಹಿದಾರರ ಪಾತ್ರಗಳು:",
    signoffNotice: "ಸಹಿ ಮಾಡುವುದರಿಂದ ಇದು ಪೊಲೀಸರಿಗೆ ಅಥವಾ ನ್ಯಾಯಾಲಯಕ್ಕೆ ಹೋಗುವುದಿಲ್ಲ.",
    whatNextTitle: "📌 ನೀವು ಮುಂದೆ ಏನು ಮಾಡಬೇಕು",
    dlsaTitle: "🏛️ DLSA ರಾಷ್ಟ್ರೀಯ ಕಾನೂನು ಸೇವೆಗಳ ಪ್ರಾಧಿಕಾರ ಸಹಾಯವಾಣಿ: 15100",
    dlsaCallBtn: "15100 ಗೆ ಕರೆ ಮಾಡಿ",
    revisionPrompt: "ವಿವರಗಳನ್ನು ಬದಲಾಯಿಸಬೇಕೇ?",
    editDetails: "✏️ ವಿವರಗಳನ್ನು ಬದಲಿಸಿ",
    orSpeak: "ಅಥವಾ ಮಾತನಾಡಲು ಗೋಳವನ್ನು ಸ್ಪರ್ಶಿಸಿ.",
    orbStatusReady: "ಸಜೀವ ಧ್ವನಿ ಗೋಳ · ಸಿದ್ಧ"
  },
  bn: {
    talkingTitle: "🎙️ কথা বলা আইনি সহকারী",
    talkingSub: "নিচের প্রশ্নের উত্তর দিন:",
    currentQuestion: "বর্তমান প্রশ্ন (কথা বলে বা লিখে উত্তর দিন):",
    upcomingQuestions: "পরবর্তী প্রশ্নসমূহ:",
    speakBtn: "🎙️ কথা বলে উত্তর দিন (Tap to talk)",
    speakChangesBtn: "🎙️ কথা বলে পরিবর্তন জানান",
    sendBtn: "পাঠান",
    placeholder: "কথা বলুন বা এখানে টাইপ করুন...",
    draftPending: "⏳ সম্পূর্ণ তথ্য পাওয়ার পর খসড়া তৈরি হবে",
    draftReady: "✅ সমস্ত তথ্য রেকর্ড করা হয়েছে · খসড়া প্রস্তুত (আইনি পরামর্শ নয়)",
    spokenTitle: "🔊 মৌখিক পরামর্শ",
    actionsTitle: "// অবিলম্বে করণীয় পদক্ষেপ",
    draftBoxTitle: "📄 খসড়া ঘটনার সারসংক্ষেপ (পর্যালোচনার জন্য - আইনি পরামর্শ নয়)",
    rightsTitle: "আপনার আইনি অধিকার ও ধারাগুলি বুঝুন",
    listenRights: "অধিকার শুনুন",
    recap1Min: "১-মিনিটের সারসংক্ষেপ",
    simplerWords: "সহজ কথায় বুঝুন",
    card1NoticeTitle: "প্রস্তুতকৃত আনুষ্ঠানিক আইনি নোটিশ",
    outboundDisabled: "বাইরে পাঠানো নিষ্ক্রিয় (কেবল পর্যালোচনার জন্য)",
    copyTextBtn: "কপি করুন",
    printPdfBtn: "প্রিন্ট / PDF",
    approvedSignoff: "অনুমোদিত স্বাক্ষরকারী ভূমিকা:",
    signoffNotice: "স্বাক্ষর করার মাধ্যমে এটি পুলিশ বা আদালতে পাঠানো হয় না।",
    whatNextTitle: "📌 আপনার পরবর্তী পদক্ষেপ",
    dlsaTitle: "🏛️ DLSA জাতীয় আইনি সেবা কর্তৃপক্ষ হেল্পলাইন: 15100",
    dlsaCallBtn: "15100 এ কল করুন",
    revisionPrompt: "কোনো বিবরণ পরিবর্তন করতে চান?",
    editDetails: "✏️ বিবরণ পরিবর্তন",
    orSpeak: "বা কথা বলতে গোলকে স্পর্শ করুন।",
    orbStatusReady: "সজীব ভয়েস গোলক · প্রস্তুত"
  },
  ml: {
    talkingTitle: "🎙️ സംസാരിക്കുന്ന നിയമ സഹായി",
    talkingSub: "താഴെയുള്ള ചോദ്യത്തിന് മറുപടി നൽകുക:",
    currentQuestion: "നിലവിലെ ചോദ്യം (സംസാരിച്ചോ എഴുതിയോ മറുപടി നൽകുക):",
    upcomingQuestions: "അടുത്ത ചോദ്യങ്ങൾ:",
    speakBtn: "🎙️ സംസാരിച്ചു മറുപടി നൽകുക (Tap to talk)",
    speakChangesBtn: "🎙️ സംസാരിച്ച് മാറ്റങ്ങൾ വരുത്തുക",
    sendBtn: "അയക്കുക",
    placeholder: "സംസാരിക്കുക അല്ലെങ്കിൽ ഇവിടെ എഴുതുക...",
    draftPending: "⏳ വിവരങ്ങൾ പൂർണ്ണമാകുമ്പോൾ കരട് രേഖ തയ്യാറാകും",
    draftReady: "✅ എല്ലാ വിവരങ്ങളും ശേഖരിച്ചു · കരട് രേഖ തയ്യാറാണ് (നിയമോപദേശമല്ല)",
    spokenTitle: "🔊 വോയ്‌സ് ഉപദേശം",
    actionsTitle: "// ഉടൻ ചെയ്യേണ്ട കാര്യങ്ങൾ",
    draftBoxTitle: "📄 കരട് സംഭവ സംഗ്രഹം (നിയമോപദേശമല്ല)",
    rightsTitle: "നിങ്ങളുടെ നിയമപരമായ അവകാശങ്ങൾ",
    listenRights: "അവകാശങ്ങൾ കേൾക്കുക",
    recap1Min: "1-മിനിറ്റ് സംഗ്രഹം",
    simplerWords: "ലളിതമായ വാക്കുകളിൽ",
    card1NoticeTitle: "കരട് ലീഗൽ നോട്ടീസ്",
    outboundDisabled: "പുറത്തേക്ക് അയക്കുന്നത് പ്രവർത്തനരഹിതമാക്കി (പരിശോധനയ്ക്ക് മാത്രം)",
    copyTextBtn: "പകർപ്പുക",
    printPdfBtn: "പ്രിന്റ് / PDF",
    approvedSignoff: "അംഗീകൃത ഒപ്പുവെക്കൽ റോളുകൾ:",
    signoffNotice: "ഒപ്പുവെക്കുന്നത് ഇത് പോലീസിലേക്കോ കോടതിയിലേക്കോ അയക്കില്ല.",
    whatNextTitle: "📌 ഇനി എന്തുചെയ്യണം",
    dlsaTitle: "🏛️ DLSA ദേശീയ ലീഗൽ സർവീസസ് അതോറിറ്റി ഹെൽപ്പ്‌ലൈൻ: 15100",
    dlsaCallBtn: "15100 ലേക്ക് വിളിക്കുക",
    revisionPrompt: "വിവരങ്ങൾ മാറ്റണോ?",
    editDetails: "✏️ മാറ്റം വരുത്തുക",
    orSpeak: "അല്ലെങ്കിൽ സംസാരിക്കാൻ ഗോളത്തിൽ തൊടുക.",
    orbStatusReady: "വോയ്‌സ് ഗോളം · സജ്ജം"
  },
  pa: {
    talkingTitle: "🎙️ ਬੋਲਣ ਵਾਲਾ ਕਾਨੂੰਨੀ ਸਹਾਇਕ",
    talkingSub: "ਹੇਠਾਂ ਦਿੱਤੇ ਸਵਾਲ ਦਾ ਜਵਾਬ ਦਿਓ:",
    currentQuestion: "ਮੌਜੂਦਾ ਸਵਾਲ (ਬੋਲ ਕੇ ਜਾਂ ਲਿਖ ਕੇ ਜਵਾਬ ਦਿਓ):",
    upcomingQuestions: "ਅਗਲੇ ਸਵਾਲ:",
    speakBtn: "🎙️ ਬੋਲ ਕੇ ਜਵਾਬ ਦਿਓ (Tap to talk)",
    speakChangesBtn: "🎙️ ਬੋਲ ਕੇ ਬਦਲਾਅ ਦੱਸੋ",
    sendBtn: "ਭੇਜੋ",
    placeholder: "ਬੋਲ ਕੇ ਜਵਾਬ ਦਿਓ ਜਾਂ ਇੱਥੇ ਲਿਖੋ...",
    draftPending: "⏳ ਸਾਰੀ ਜਾਣਕਾਰੀ ਮਿਲਣ ਤੋਂ ਬਾਅਦ ਡਰਾਫਟ ਤਿਆਰ ਹੋਵੇਗਾ",
    draftReady: "✅ ਸਾਰੀ ਜਾਣਕਾਰੀ ਦਰਜ · ਡਰਾਫਟ ਸਮੀਖਿਆ ਲਈ ਤਿਆਰ (ਕਾਨੂੰਨੀ ਸਲਾਹ ਨਹੀਂ)",
    spokenTitle: "🔊 ਬੋਲ ਕੇ ਦਿੱਤੀ ਸਲਾਹ",
    actionsTitle: "// ਤੁਰੰਤ ਕੀਤੇ ਜਾਣ ਵਾਲੇ ਕਦਮ",
    draftBoxTitle: "📄 ਡਰਾਫਟ ਘਟਨਾ ਸਾਰ (ਕਾਨੂੰਨੀ ਸਲਾਹ ਨਹੀਂ)",
    rightsTitle: "ਆਪਣੇ ਕਾਨੂੰਨੀ ਅਧਿਕਾਰ ਅਤੇ ਧਾਰਾਵਾਂ ਸਮਝੋ",
    listenRights: "ਅਧਿਕਾਰ ਸੁਣੋ",
    recap1Min: "1-ਮਿੰਟ ਸਾਰ",
    simplerWords: "ਸੌਖੇ ਸ਼ਬਦਾਂ ਵਿੱਚ",
    card1NoticeTitle: "ਤਿਆਰ ਕੀਤਾ ਕਾਨੂੰਨੀ ਨੋਟਿਸ",
    outboundDisabled: "ਬਾਹਰ ਭੇਜਣਾ ਬੰਦ (ਸਿਰਫ਼ ਸਮੀਖਿਆ ਲਈ)",
    copyTextBtn: "ਕਾਪੀ ਕਰੋ",
    printPdfBtn: "ਪ੍ਰਿੰਟ / PDF",
    approvedSignoff: "ਮਨਜ਼ੂਰਸ਼ੁਦਾ ਹਸਤਾਖਰਕਾਰ ਭੂਮਿਕਾਵਾਂ:",
    signoffNotice: "ਹਸਤਾਖਰ ਕਰਨ ਨਾਲ ਇਹ ਪੁਲਿਸ ਜਾਂ ਅਦਾਲਤ ਨੂੰ ਨਹੀਂ ਭੇਜਿਆ ਜਾਂਦਾ।",
    whatNextTitle: "📌 ਅੱਗੇ ਕੀ ਕਰਨਾ ਹੈ",
    dlsaTitle: "🏛️ DLSA ਰਾਸ਼ਟਰੀ ਕਾਨੂੰਨੀ ਸੇਵਾਵਾਂ ਅਥਾਰਟੀ ਹੈਲਪਲਾਈਨ: 15100",
    dlsaCallBtn: "15100 ਤੇ ਕਾਲ ਕਰੋ",
    revisionPrompt: "ਵੇਰਵੇ ਬਦਲਣੇ ਹਨ?",
    editDetails: "✏️ ਵੇਰਵੇ ਬਦਲੋ",
    orSpeak: "ਜਾਂ ਬੋਲਣ ਲਈ ਗੋਲੇ ਨੂੰ ਛੂਹੋ।",
    orbStatusReady: "ਸਜੀਵ ਆਵਾਜ਼ ਗੋਲਾ · ਤਿਆਰ"
  }
};

export const UIRenderer = {
  escapeHtml(string) {
    if (!string) return '';
    const entityMap = {
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;', '/': '&#x2F;'
    };
    return String(string).replace(/[&<>"'/]/g, s => entityMap[s]);
  },

  scrollToChat() {
    const el = document.getElementById('chat-section');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  },

  scrollToLanding() {
    const el = document.getElementById('landing-section');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  },

  syncLanguageUI(langCode) {
    if (!langCode) return;
    const clean = langCode.toLowerCase().trim();
    let norm = 'en';
    for (const code of ['gu', 'hi', 'mr', 'ta', 'te', 'kn', 'bn', 'ml', 'pa']) {
      if (clean.startsWith(code) || clean.includes(code)) {
        norm = code;
        break;
      }
    }
    const L = UI_LANG[norm] || UI_LANG['en'];

    const lSel = document.getElementById('select-language');
    const vSel = document.getElementById('select-voice');
    const voiceMap = {
      'hi': 'Shivani', 'mr': 'Vasudha', 'ta': 'Kalpana', 'te': 'Lakshmi',
      'kn': 'Chetana', 'bn': 'Riyaa', 'gu': 'Tarika', 'ml': 'Lakshmi', 'pa': 'Tarika', 'en': 'Shivani'
    };
    if (lSel) lSel.value = norm === 'en' ? 'en-IN' : (norm + '-IN');
    if (vSel && voiceMap[norm]) vSel.value = voiceMap[norm];

    // Localize interactive input & status elements
    const input = document.getElementById('chat-input');
    if (input && L.placeholder) input.placeholder = L.placeholder;

    const micBtn = document.getElementById('orb-mic-btn');
    if (micBtn && L.speakBtn) {
      micBtn.innerHTML = `<span>🎙️</span><span>${L.speakBtn.replace('🎙️ ', '')}</span>`;
    }

    const sendBtn = document.getElementById('btn-send');
    if (sendBtn && L.sendBtn) {
      sendBtn.innerHTML = `<span>${L.sendBtn}</span>`;
    }

    const orbStatus = document.getElementById('orb-status-text');
    if (orbStatus && L.orbStatusReady) {
      orbStatus.innerText = L.orbStatusReady;
    }
  },

  renderSidebarPresets() {
    const container = document.getElementById('presets-container');
    if (!container) return;
    container.innerHTML = presetsData.map(p => `
      <button onclick="window.NyayaVaniApp.selectPreset('${p.id}')" class="w-full text-left p-2 rounded-lg border border-[var(--border-subtle)] hover:border-[var(--accent)] bg-[var(--bg-subtle)] hover:bg-[var(--accent-subtle)] transition text-xs flex items-center space-x-2 group">
        <span>${p.icon}</span>
        <span class="truncate text-[var(--text-secondary)] group-hover:text-[var(--accent)] font-mono text-[11px] font-medium">${this.escapeHtml(p.title)}</span>
      </button>
    `).join('');
  },

  renderModalPresets() {
    const container = document.getElementById('modal-presets-list');
    if (!container) return;
    container.innerHTML = presetsData.map(p => `
      <div onclick="window.NyayaVaniApp.selectPreset('${p.id}'); window.NyayaVaniApp.closePresetsModal();" class="p-3.5 rounded-xl border-2 border-[var(--border-subtle)] hover:border-[var(--accent)] bg-[var(--bg-card)] hover:bg-[var(--accent-subtle)] transition cursor-pointer flex items-start space-x-3 group shadow-sm">
        <span class="text-2xl mt-0.5">${p.icon}</span>
        <div class="flex-1 min-w-0">
          <div class="font-bold text-xs text-[var(--text-primary)] group-hover:text-[var(--accent)] mb-1">${this.escapeHtml(p.title)}</div>
          <div class="text-[11px] text-[var(--text-muted)] line-clamp-2">${this.escapeHtml(p.text)}</div>
          <span class="inline-block mt-2 text-[9px] font-mono px-2 py-0.5 rounded-full bg-[var(--accent-subtle)] text-[var(--accent)] border border-[var(--accent-border)] font-bold">${p.category}</span>
        </div>
      </div>
    `).join('');
  },

  appendUserMessage(text) {
    const container = document.getElementById('messages-container');
    const msgHtml = `
      <div class="flex justify-end">
        <div class="max-w-2xl themed-user-bubble p-4 text-sm shadow-md">
          <div class="text-[10px] font-mono text-[var(--text-muted)] mb-1">YOUR ACCOUNT</div>
          <div class="leading-relaxed font-normal">${this.escapeHtml(text)}</div>
        </div>
      </div>
    `;
    container.insertAdjacentHTML('beforeend', msgHtml);
    container.scrollTop = container.scrollHeight;
  },

  showLoadingAssistant(loadingText = "Analyzing facts and statutory protections...") {
    const container = document.getElementById('messages-container');
    const loadingHtml = `
      <div id="loading-indicator" class="flex justify-start">
        <div class="themed-chat-bubble p-4 text-sm max-w-2xl flex items-center space-x-3 border-2 border-[var(--accent)] shadow-md">
          <span class="pulse-indicator-contrast"></span>
          <span class="font-mono text-xs text-[var(--accent)] font-bold">${loadingText}</span>
        </div>
      </div>
    `;
    container.insertAdjacentHTML('beforeend', loadingHtml);
    container.scrollTop = container.scrollHeight;
  },

  removeLoadingAssistant() {
    document.getElementById('loading-indicator')?.remove();
  },

  appendAssistantMessage(data, originalAccount = '') {
    const container = document.getElementById('messages-container');
    const intake = data.intake || {};
    const questions = intake.follow_up_questions || data.follow_up_questions || [];
    const needsFacts = Boolean(data.needs_more_information || intake.status === 'needs_more_information' || intake.status === 'needs_details' || (questions && questions.length > 0));
    const caseId = `case-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
    rightsDataStore[caseId] = data;

    // Purge conversational intake clutter on final legal package completion
    if (!needsFacts && container) {
      container.innerHTML = '';
    }

    const activeQuestion = questions.length ? questions[0] : (data.spoken_text || '');
    const otherQuestions = questions.slice(1);

    const curLang = data.language || 'en';
    let norm = 'en';
    for (const code of ['gu', 'hi', 'mr', 'ta', 'te', 'kn', 'bn', 'ml', 'pa']) {
      if (curLang.startsWith(code) || curLang.includes(code)) {
        norm = code;
        break;
      }
    }
    const L = UI_LANG[norm] || UI_LANG['en'];
    const cardTitle = L.talkingTitle;
    const cardSub = L.talkingSub;
    const micBtnLabel = needsFacts ? L.speakBtn : L.speakChangesBtn;
    const inputPh = L.placeholder;
    const sendBtnLabel = L.sendBtn;
    const spokenTitle = L.spokenTitle;
    const actionTitle = L.actionsTitle;

    // Talking Agent Voice Conversational UI (Rich Contrasting Colors)
    const followupHtml = needsFacts ? `
      <div class="mb-5 rounded-3xl border-2 border-[var(--accent)] bg-[var(--accent-subtle)] p-5 sm:p-6 shadow-md" style="box-shadow: var(--accent-glow);">
        <div class="flex items-center justify-between mb-3 pb-2 border-b border-[var(--accent-border)]">
          <div class="flex items-center space-x-2">
            <span class="text-2xl animate-pulse">🎙️</span>
            <h4 class="text-sm font-bold text-[var(--accent)] font-syne">${cardTitle}</h4>
          </div>
          <span class="text-[10px] font-mono px-3 py-1 rounded-full bg-[var(--accent-subtle)] text-[var(--accent)] border border-[var(--accent-border)] font-bold tracking-wider animate-pulse">VOICE INTERACTIVE</span>
        </div>
        
        <p class="text-xs text-[var(--text-secondary)] mb-3 leading-relaxed">${cardSub}</p>
        
        <div class="mb-4 p-4 sm:p-5 rounded-2xl bg-[var(--bg-surface)] border-2 border-[var(--accent)] shadow-sm">
          <div class="flex items-center space-x-2 text-xs font-mono text-[var(--accent)] font-bold uppercase tracking-wider mb-2">
            <span class="w-2.5 h-2.5 rounded-full bg-[var(--accent)] animate-ping"></span>
            <span>${this.escapeHtml(L.currentQuestion)}</span>
          </div>
          <p class="text-base sm:text-lg font-bold text-[var(--text-primary)] leading-relaxed">${this.escapeHtml(activeQuestion)}</p>
        </div>

        ${otherQuestions.length ? `
          <div class="mb-4 px-4 py-2.5 rounded-xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)] text-[11px] text-[var(--text-muted)]">
            <span class="font-mono font-semibold">${this.escapeHtml(L.upcomingQuestions)}</span>
            ${otherQuestions.map(q => `<div class="truncate mt-1">• ${this.escapeHtml(q)}</div>`).join('')}
          </div>
        ` : ''}

        <div class="p-4 sm:p-5 rounded-2xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
          <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <button type="button"
                    onclick="window.NyayaVaniApp.startVoiceReply('${caseId}')"
                    role="button"
                    aria-label="${micBtnLabel}"
                    class="cta-primary-btn w-full sm:w-auto">
              <span class="text-lg">🎙️</span>
              <span class="text-xs font-bold uppercase tracking-wider">${micBtnLabel}</span>
            </button>

            <div class="flex-1 min-w-[200px] w-full">
              <label for="quick-reply-${caseId}" class="sr-only">${this.escapeHtml(inputPh)}</label>
              <div class="flex items-center space-x-2">
                <input id="quick-reply-${caseId}"
                       type="text"
                       placeholder="${this.escapeHtml(inputPh)}"
                       onkeydown="if(event.key==='Enter') window.NyayaVaniApp.submitQuickReply('${caseId}')"
                       class="w-full rounded-xl border-2 border-[var(--accent-border)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] focus:border-[var(--accent)] outline-none leading-relaxed min-h-[44px]">
                <button type="button"
                        onclick="window.NyayaVaniApp.submitQuickReply('${caseId}')"
                        class="cta-primary-btn px-4 py-3 text-xs min-h-[44px]">
                  <span>${sendBtnLabel}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>` : '';

    // Understand Your Rights Card
    const uyr = data.understand_your_rights;
    let rightsHtml = '';
    if (uyr) {
      const urgent = uyr.urgent_help;
      const acts = uyr.possible_acts || [];
      const nextSteps = uyr.what_you_can_do_next?.options || [];
      const recap = uyr.one_minute_recap;
      const simpler = uyr.simpler_words_explanation;

      rightsHtml = `
      <div class="mb-5 rounded-3xl border-2 border-[var(--primary-border)] bg-[var(--bg-card)] p-5 sm:p-6 shadow-md">
        
        <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[var(--border-subtle)] mb-4 gap-2">
          <div class="flex items-center space-x-2.5">
            <span class="text-2xl">⚖️</span>
            <div>
              <h3 class="text-base font-bold text-[var(--primary-text)] font-syne">${this.escapeHtml(L.rightsTitle)}</h3>
              <div class="text-[10px] font-mono text-[var(--text-muted)]">Structured Statutory Analysis · Plain Language Legal Literacy</div>
            </div>
          </div>
          <span class="text-[10px] font-mono px-3 py-1 rounded-full bg-[var(--primary-subtle)] text-[var(--primary-text)] border border-[var(--primary-border)] font-bold tracking-wider self-start sm:self-auto">DRAFT PENDING QUALIFIED REVIEW</span>
        </div>

        ${urgent ? `
          <div class="mb-5 p-4 rounded-2xl bg-red-50 border-2 border-red-500 shadow-sm text-red-900">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-2">
                <span class="text-xl animate-bounce">🚨</span>
                <span class="font-bold text-red-700 text-sm font-syne">${this.escapeHtml(urgent.heading || 'Urgent Safety & Human Help')}</span>
              </div>
              <a href="tel:${this.escapeHtml(urgent.helpline)}" class="px-3 py-1.5 rounded-full bg-red-600 hover:bg-red-500 text-white font-black text-xs font-mono shadow-md transition flex items-center space-x-1">
                <span>📞 Call ${this.escapeHtml(urgent.helpline)}</span>
              </a>
            </div>
            <p class="text-xs font-semibold mb-2 leading-relaxed">${this.escapeHtml(urgent.message)}</p>
            <div class="text-[11px] bg-red-100 p-2.5 rounded-xl border border-red-200">
              <span class="font-bold">Immediate action:</span> ${this.escapeHtml(urgent.immediate_action || 'Ensure physical safety first.')}
            </div>
          </div>
        ` : ''}

        <div class="mb-5 p-4 rounded-2xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
          <div class="flex items-center justify-between mb-2 pb-2 border-b border-[var(--border-subtle)] text-[11px]">
            <div class="flex items-center space-x-1.5 text-[var(--primary-text)] font-mono">
              <span>🛡️</span>
              <span class="font-semibold">${this.escapeHtml(uyr.shared_phone_privacy_notice || 'Shared phone notice')}</span>
            </div>
            <span class="text-[10px] font-mono text-[var(--text-muted)]">Voice Guidance Available</span>
          </div>

          <div class="flex flex-wrap items-center justify-between gap-3 pt-1">
            <div class="flex flex-wrap items-center gap-2">
              <button type="button"
                      id="btn-play-full-${caseId}"
                      onclick="window.NyayaVaniApp.playRightsAudio('${caseId}', 'full')"
                      class="cta-primary-btn px-4 py-2 text-xs">
                <span id="play-icon-full-${caseId}">▶️</span>
                <span id="play-text-full-${caseId}">${this.escapeHtml(L.listenRights)}</span>
              </button>

              <button type="button"
                      id="btn-play-recap-${caseId}"
                      onclick="window.NyayaVaniApp.playRightsAudio('${caseId}', 'recap')"
                      class="cta-secondary-btn px-3.5 py-2 text-xs">
                <span id="play-icon-recap-${caseId}">⏱️</span>
                <span>${this.escapeHtml(L.recap1Min)}</span>
              </button>

              <button type="button"
                      id="btn-play-simpler-${caseId}"
                      onclick="window.NyayaVaniApp.playRightsAudio('${caseId}', 'simplified')"
                      class="cta-secondary-btn px-3.5 py-2 text-xs">
                <span id="play-icon-simpler-${caseId}">💡</span>
                <span>${this.escapeHtml(L.simplerWords)}</span>
              </button>

              <button type="button"
                      onclick="window.NyayaVaniApp.replayRightsAudio('${caseId}')"
                      class="cta-secondary-btn px-3 py-2 text-xs"
                      title="Replay from start">
                <span>🔄 Replay</span>
              </button>
            </div>

            <div class="flex items-center space-x-1 bg-[var(--bg-card)] p-1 rounded-xl border border-[var(--border-subtle)]">
              <span class="text-[10px] font-mono text-[var(--text-muted)] px-1.5">Speed:</span>
              <button type="button" onclick="window.NyayaVaniApp.setPlaybackSpeed('${caseId}', 0.85)" data-speed="0.85" class="speed-btn-${caseId} px-2 py-1 rounded-lg text-[10px] font-mono transition bg-[var(--bg-subtle)] text-[var(--text-secondary)]">0.85x</button>
              <button type="button" onclick="window.NyayaVaniApp.setPlaybackSpeed('${caseId}', 1.0)" data-speed="1.0" class="speed-btn-${caseId} px-2 py-1 rounded-lg text-[10px] font-mono transition bg-[var(--primary)] text-[var(--text-inverse)] font-bold">1.0x</button>
              <button type="button" onclick="window.NyayaVaniApp.setPlaybackSpeed('${caseId}', 1.15)" data-speed="1.15" class="speed-btn-${caseId} px-2 py-1 rounded-lg text-[10px] font-mono transition bg-[var(--bg-subtle)] text-[var(--text-secondary)]">1.15x</button>
            </div>
          </div>
          <div id="audio-notice-${caseId}" class="mt-2 text-[11px] font-mono text-[var(--primary)] hidden"></div>
        </div>

        <!-- 1. What I Understood -->
        <div class="mb-4 p-4 rounded-2xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
          <div class="flex items-center space-x-2 text-xs font-bold text-[var(--primary-text)] mb-1.5">
            <span class="text-base">📋</span>
            <span class="font-syne">${this.escapeHtml(uyr.what_i_understood?.heading || '1. What I understood')}</span>
          </div>
          <p class="text-xs text-[var(--text-secondary)] leading-relaxed">${this.escapeHtml(uyr.what_i_understood?.text || '')}</p>
        </div>

        <!-- 2. What May Be Wrong -->
        <div class="mb-4 p-4 rounded-2xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
          <div class="flex items-center justify-between mb-1.5">
            <div class="flex items-center space-x-2 text-xs font-bold text-[var(--primary-text)]">
              <span class="text-base">⚠️</span>
              <span class="font-syne">${this.escapeHtml(uyr.what_may_be_wrong?.heading || '2. What may be wrong')}</span>
            </div>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-[var(--accent-subtle)] text-[var(--accent-text)] border border-[var(--accent-border)] font-bold">ALLEGATION VS FACT</span>
          </div>
          <p class="text-xs text-[var(--text-primary)] font-medium mb-2 leading-relaxed">${this.escapeHtml(uyr.what_may_be_wrong?.improper_conduct_description || '')}</p>
          <div class="text-[11px] text-[var(--primary-text)] italic bg-[var(--primary-subtle)] p-2.5 rounded-xl border border-[var(--primary-border)] leading-relaxed">
            ⚖️ ${this.escapeHtml(uyr.what_may_be_wrong?.allegation_vs_fact_note || '')}
          </div>
        </div>

        <!-- 3. Possible Act and Sections -->
        <div class="mb-4 p-4 rounded-2xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center space-x-2 text-xs font-bold text-[var(--primary-text)]">
              <span class="text-base">📖</span>
              <span class="font-syne">${this.escapeHtml(uyr.possible_acts?.[0] ? '3. Possible Act and Sections' : '3. Statutory Provisions')}</span>
            </div>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-[var(--primary-subtle)] text-[var(--primary)] border border-[var(--primary-border)]">PRIMARY SOURCES</span>
          </div>
          <div class="space-y-3">
            ${acts.map(act => `
              <div class="p-3 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1">
                  <div class="font-mono text-xs font-bold text-[var(--text-primary)]">${this.escapeHtml(act.section || act.act_name)}</div>
                  <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-[var(--primary-subtle)] text-[var(--primary-text)] border border-[var(--primary-border)] self-start sm:self-auto">${this.escapeHtml(act.review_status || 'DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW')}</span>
                </div>
                <p class="text-xs text-[var(--text-secondary)] mb-1 leading-relaxed"><strong>Coverage:</strong> ${this.escapeHtml(act.coverage_explanation || '')}</p>
                <p class="text-[11px] text-[var(--text-muted)] mb-1.5 leading-relaxed"><strong>Conditions:</strong> ${this.escapeHtml(act.conditions_to_check || '')}</p>
                ${act.source_url ? `
                  <a href="${this.escapeHtml(act.source_url)}" target="_blank" rel="noopener noreferrer" class="text-[11px] font-mono text-[var(--primary)] underline inline-flex items-center space-x-1">
                    <span>View Official Statutory Text</span> ↗
                  </a>
                ` : ''}
              </div>
            `).join('')}
          </div>
        </div>

        <!-- 4. Why It Might Apply -->
        <div class="mb-4 p-4 rounded-2xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
          <div class="flex items-center space-x-2 text-xs font-bold text-[var(--primary-text)] mb-1.5">
            <span class="text-base">🔍</span>
            <span class="font-syne">${this.escapeHtml(uyr.why_it_might_apply?.heading || '4. Why it might apply here')}</span>
          </div>
          <p class="text-xs text-[var(--text-secondary)] mb-2 leading-relaxed">${this.escapeHtml(uyr.why_it_might_apply?.connection_to_facts || '')}</p>
          ${uyr.why_it_might_apply?.clarification_needed ? `
            <div class="text-[11px] text-[var(--accent-text)] bg-[var(--accent-subtle)] p-2.5 rounded-xl border border-[var(--accent-border)] leading-relaxed">
              ⚠️ ${this.escapeHtml(uyr.why_it_might_apply.clarification_needed)}
            </div>
          ` : ''}
        </div>

        <!-- 5. What You Can Do Next -->
        <div class="mb-4 p-4 rounded-2xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
          <div class="flex items-center space-x-2 text-xs font-bold text-[var(--primary-text)] mb-2">
            <span class="text-base">🚀</span>
            <span class="font-syne">${this.escapeHtml(uyr.what_you_can_do_next?.heading || '5. What you can do next')}</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-3">
            ${nextSteps.map(step => `
              <div class="p-3 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
                <div class="text-xs font-bold text-[var(--text-primary)] mb-1">${this.escapeHtml(step.title)}</div>
                <div class="text-[11px] text-[var(--text-secondary)] leading-relaxed">${this.escapeHtml(step.details)}</div>
              </div>
            `).join('')}
          </div>
          <div class="text-[10px] font-mono text-[var(--text-muted)] italic bg-[var(--bg-card)] p-2.5 rounded-xl border border-[var(--border-subtle)] leading-relaxed">
            ${this.escapeHtml(uyr.what_you_can_do_next?.filing_disclaimer || '')}
          </div>
        </div>

        <!-- 6 & 7: Recap & Simpler Words -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="p-4 rounded-2xl bg-[var(--primary-subtle)] border border-[var(--primary-border)]">
            <div class="flex items-center space-x-2 text-xs font-bold text-[var(--primary-text)] mb-1.5">
              <span>⏱️</span>
              <span class="font-syne">${this.escapeHtml(recap?.heading || 'One-Minute Recap')}</span>
            </div>
            <p class="text-xs text-[var(--text-secondary)] font-medium leading-relaxed">${this.escapeHtml(recap?.recap_text || '')}</p>
          </div>

          <div class="p-4 rounded-2xl bg-[var(--accent-subtle)] border border-[var(--accent-border)]">
            <div class="flex items-center space-x-2 text-xs font-bold text-[var(--accent-text)] mb-1.5">
              <span>💡</span>
              <span class="font-syne">${this.escapeHtml(simpler?.heading || 'In Simpler Words')}</span>
            </div>
            <p class="text-xs text-[var(--text-secondary)] leading-relaxed">${this.escapeHtml(simpler?.explanation || '')}</p>
          </div>
        </div>

      </div>`;
    }

    // Pro Incident Packet Card
    const packet = data.pro_packet;
    const proHtml = packet ? `
      <div class="mb-5 rounded-2xl border border-[var(--primary-border)] bg-[var(--primary-subtle)] p-4 sm:p-5">
        <div class="flex items-center justify-between mb-2">
          <h4 class="text-sm font-bold text-[var(--primary-text)]">Pro Incident Packet · Review & Approval</h4>
          <span id="packet-badge-${caseId}" class="text-[10px] font-mono px-2.5 py-0.5 rounded bg-[var(--primary-subtle)] text-[var(--primary)] border border-[var(--primary-border)] font-bold">STATUS: ${(packet.status || 'needs_review').toUpperCase()}</span>
        </div>
        <p class="text-xs text-[var(--text-secondary)] mb-3 leading-relaxed">
          Compiled user-confirmed facts and draft communication. <strong>Draft Incident Summary for Review — Not Legal Advice.</strong> Outbound transmission disabled (Review only).
        </p>
        
        <div class="mb-3 p-2.5 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] text-xs font-mono">
          <span class="text-[var(--text-muted)]">Packet ID:</span> <span class="text-[var(--primary)]">${this.escapeHtml(packet.packet_id || 'pkt-local')}</span> | 
          <span class="text-[var(--text-muted)]">Content Hash:</span> <span class="text-[var(--accent)]">${this.escapeHtml((packet.content_hash || '').slice(0, 16))}...</span>
        </div>

        <p class="text-xs text-[var(--text-muted)] mb-1 font-semibold">Incident summary</p>
        <p class="text-xs text-[var(--text-primary)] mb-3 bg-[var(--bg-surface)] p-2.5 rounded-lg border border-[var(--border-subtle)] leading-relaxed">${this.escapeHtml(packet.incident_summary || '')}</p>
        
        ${(packet.missing_evidence || []).length ? `<p class="text-xs text-[var(--text-muted)] mb-1 font-semibold">Evidence checklist to gather</p><ul class="list-disc pl-5 text-xs text-[var(--text-secondary)] mb-3">${packet.missing_evidence.map(e => `<li>${this.escapeHtml(e)}</li>`).join('')}</ul>` : ''}
        
        <label class="block text-xs text-[var(--text-primary)] mb-1 font-semibold" for="draft-${caseId}">Editable draft communication</label>
        <textarea id="draft-${caseId}" rows="6" class="w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] p-3 text-xs text-[var(--text-primary)] focus:border-[var(--primary)] outline-none leading-relaxed">${this.escapeHtml(packet.draft_message || '')}</textarea>
        
        <div class="mt-3 p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
          <div class="text-xs font-mono font-bold text-[var(--primary)] mb-1">Formal Approver Sign-Off</div>
          <p class="text-[11px] text-[var(--text-muted)] mb-3 leading-relaxed">
            Signing approves this document for <strong>human review and offline export</strong>. Signing does <strong>NOT</strong> transmit this document to police, insurer, or court. Outbound transmission is disabled.
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
            <div>
              <label for="approver-name-${caseId}" class="block text-[11px] font-mono text-[var(--text-muted)] mb-1">Approver Full Name *</label>
              <input id="approver-name-${caseId}" type="text" placeholder="Full legal name" value="${this.escapeHtml(data.pro_packet?.client_name || '')}" class="w-full p-2.5 rounded-lg bg-[var(--bg-input)] border border-[var(--border-subtle)] text-xs text-[var(--text-primary)] focus:border-[var(--primary)] outline-none">
            </div>
            <div>
              <label for="approver-role-${caseId}" class="block text-[11px] font-mono text-[var(--text-muted)] mb-1">Approver Role *</label>
              <select id="approver-role-${caseId}" class="w-full p-2.5 rounded-lg bg-[var(--bg-input)] border border-[var(--border-subtle)] text-xs text-[var(--text-primary)] focus:border-[var(--primary)] outline-none">
                <option value="Client">Client</option>
                <option value="Authorized Representative">Authorized Representative</option>
                <option value="Independent Legal Counsel">Independent Legal Counsel</option>
              </select>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <button type="button" onclick="window.NyayaVaniApp.approveProPacket('${packet.packet_id}', '${caseId}')" class="cta-primary-btn px-4 py-2 text-xs">Sign & Approve for Offline Export</button>
            <button type="button" id="btn-send-packet-${caseId}" onclick="window.NyayaVaniApp.testOutboundBoundary('${packet.packet_id}', '${caseId}')" class="cta-secondary-btn px-3.5 py-2 text-xs">Test Outbound Boundary</button>
            <button type="button" onclick="window.NyayaVaniApp.copyPacket('${caseId}')" class="cta-secondary-btn px-3.5 py-2 text-xs">Copy Draft</button>
          </div>
        </div>
        
        <p id="packet-status-${caseId}" class="text-xs text-[var(--primary)] mt-2 font-mono">Status: Awaiting sign-off. Outbound transmission disabled (Review only).</p>
      </div>` : '';

    const statutesHtml = (data.statutory_sections || []).map(s => `
      <li class="mb-2">
        <span class="font-bold text-[var(--text-primary)] font-mono text-xs">${this.escapeHtml(s.law)}:</span>
        <span class="text-xs text-[var(--text-secondary)]">${this.escapeHtml(s.details)}</span>
      </li>
    `).join('');

    const stepsHtml = (data.action_steps || []).map(step => `
      <div class="text-xs text-[var(--text-secondary)] py-1 flex items-start space-x-2">
        <span class="text-[var(--primary)]">▸</span>
        <span>${this.escapeHtml(step)}</span>
      </div>
    `).join('');

    // Verdict Card
    const lv = data.legality_verdict;
    let verdictHtml = '';
    if (lv && lv.status) {
      const isLawful = Boolean(lv.is_lawful);
      const verdictBg = isLawful ? 'bg-emerald-50 border-emerald-500/50' : 'bg-[var(--primary-subtle)] border-[var(--primary-border)]';
      const badgeColor = isLawful ? 'bg-emerald-100 text-emerald-700 border-emerald-300' : 'bg-[var(--primary-subtle)] text-[var(--primary-text)] border-[var(--primary-border)]';
      const statutes = lv.legal_source_statutes || [];
      
      verdictHtml = `
        <div class="mb-5 rounded-3xl border-2 ${verdictBg} p-5 sm:p-6 shadow-sm">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[var(--border-subtle)] mb-3 gap-2">
            <div class="flex items-center space-x-2">
              <span class="text-xl">${isLawful ? '🛡️' : '⚖️'}</span>
              <span class="text-xs font-mono font-bold tracking-wider uppercase text-[var(--text-primary)]">${this.escapeHtml(lv.status.replace(/_/g, ' '))}</span>
            </div>
            <span class="text-[9px] font-mono px-2.5 py-0.5 rounded-full border ${badgeColor} font-bold">${this.escapeHtml(lv.review_status || 'DRAFT PENDING QUALIFIED REVIEW')}</span>
          </div>

          <div class="text-sm font-bold text-[var(--text-primary)] mb-2 leading-relaxed bg-[var(--bg-surface)] p-3 rounded-xl border border-[var(--border-subtle)]">
            ${this.escapeHtml(lv.verdict_summary || '')}
          </div>

          ${lv.plain_explanation ? `
            <div class="text-xs text-[var(--text-secondary)] leading-relaxed mb-2.5">
              <strong class="text-[var(--primary-text)] font-mono">📢 IN PLAIN WORDS:</strong> ${this.escapeHtml(lv.plain_explanation)}
            </div>
          ` : ''}

          ${lv.what_to_do ? `
            <div class="text-xs text-[var(--text-secondary)] leading-relaxed mb-2.5">
              <strong class="text-emerald-600 font-mono">🛡️ WHAT YOU SHOULD DO:</strong> ${this.escapeHtml(lv.what_to_do)}
            </div>
          ` : ''}

          ${lv.citizen_standing ? `
            <div class="text-[11px] text-[var(--text-muted)] leading-relaxed mb-2.5">
              <strong class="text-[var(--accent)] font-mono">⚖️ CITIZEN STANDING:</strong> ${this.escapeHtml(lv.citizen_standing)}
            </div>
          ` : ''}

          ${statutes.length > 0 ? `
            <div class="mt-3 pt-3 border-t border-[var(--border-subtle)]">
              <div class="text-[10px] font-mono text-[var(--text-muted)] uppercase tracking-wider mb-1.5 font-bold">Governing Statutory Citations:</div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                ${statutes.map(s => `
                  <div class="p-2.5 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] text-xs">
                    <div class="font-bold text-[var(--primary-text)] font-mono">${this.escapeHtml(s.act || '')}</div>
                    <div class="text-[var(--accent)] font-mono text-[11px] font-semibold">${this.escapeHtml(s.section || '')}</div>
                    <div class="text-[10px] text-[var(--text-muted)] mt-0.5 leading-relaxed">${this.escapeHtml(s.rule || '')}</div>
                    ${s.source_url ? `<a href="${this.escapeHtml(s.source_url)}" target="_blank" rel="noopener noreferrer" class="text-[10px] text-[var(--primary)] underline mt-1.5 inline-block">Official Source ↗</a>` : ''}
                  </div>
                `).join('')}
              </div>
            </div>
          ` : ''}
        </div>
      `;
    }

    const msgHtml = `
      <div id="${caseId}" data-account="${encodeURIComponent(originalAccount)}" class="flex justify-start">
        <div class="w-full max-w-3xl themed-chat-bubble p-5 sm:p-6 text-sm text-[var(--text-primary)] shadow-md">
          
          <div class="mb-4 px-3.5 py-2 rounded-xl bg-[var(--primary-subtle)] border border-[var(--primary-border)] text-[var(--primary-text)] text-xs font-mono flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
            <span class="font-bold">⚠️ Draft Incident Summary for Review — Not Legal Advice</span>
            <span class="text-[10px] text-[var(--text-muted)]">Outbound transmission disabled (Review only)</span>
          </div>

          <div class="flex items-center justify-between pb-3 border-b border-[var(--border-subtle)] mb-4">
            <div class="flex items-center space-x-2.5">
              <div class="w-6 h-6 rounded-lg bg-[var(--primary-subtle)] border border-[var(--primary-border)] flex items-center justify-center text-xs">⚖️</div>
              <span class="font-mono text-xs font-bold text-[var(--text-primary)]">${this.escapeHtml(data.statutory_title || 'Incident guidance')}</span>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--primary-subtle)] text-[var(--primary-text)] font-bold">${needsFacts ? 'MORE FACTS NEEDED' : 'DRAFT FOR REVIEW'}</span>
          </div>

          ${needsFacts ? `
            ${followupHtml}

            ${data.transcript ? `<div class="mb-4 p-3 rounded-xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)]"><div class="text-[10px] font-mono text-[var(--primary)] mb-1">WHAT WE HEARD · PLEASE CHECK</div><p class="text-sm text-[var(--text-secondary)]">${this.escapeHtml(data.transcript)}</p></div>` : ''}
            ${data.sha256 ? `<div class="mb-4 p-2.5 rounded-xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)] flex flex-col sm:flex-row sm:items-center justify-between text-[11px] font-mono gap-1"><span class="text-[var(--text-muted)]">Electronic Record Integrity Hash (SHA-256):</span><span class="text-[var(--accent)] font-bold truncate max-w-xs">${this.escapeHtml(data.sha256)}</span></div>` : ''}

            <div class="mb-5 p-4 rounded-2xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-mono font-bold text-[var(--primary)] flex items-center space-x-2">
                  <span>🎙️ ${spokenTitle}</span>
                </span>
                <span class="text-[10px] font-mono text-[var(--text-muted)]">${data.audio_url ? 'GENERATED AUDIO' : 'AUDIO UNAVAILABLE'}</span>
              </div>
              <p class="text-xs text-[var(--text-secondary)] italic mb-3 leading-relaxed">${this.escapeHtml(data.spoken_text || '')}</p>
              ${data.audio_url ? `<audio controls src="${this.escapeHtml(encodeURI(data.audio_url))}" class="w-full h-8 rounded-lg outline-none"></audio>` : '<p class="text-xs text-[var(--primary)]">Spoken audio is unavailable. You can read the question above.</p>'}
            </div>
          ` : `
            <!-- CARD 1: DRAFTED FORMAL NOTICE & REPRESENTATION (Single-Stage Final Presentation) -->
            <div class="mb-6 border-2 border-[var(--accent)] rounded-2xl overflow-hidden bg-[var(--bg-card)] shadow-xl" style="box-shadow: var(--accent-glow);">
              <div class="p-4 bg-[var(--accent-subtle)] border-b border-[var(--accent-border)] flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span class="text-sm font-mono font-bold text-[var(--accent)] flex items-center space-x-2">
                    <span class="text-lg">📝</span>
                    <span>${this.escapeHtml(L.card1NoticeTitle)}</span>
                  </span>
                  <div class="text-[10px] font-mono text-[var(--text-muted)] mt-0.5">${this.escapeHtml(L.outboundDisabled)}</div>
                </div>
                <div class="flex items-center space-x-2">
                  <button type="button" onclick="window.NyayaVaniApp.startVoiceReply('${caseId}')" class="cta-primary-btn px-3 py-1.5 text-xs">
                    <span>🎙️</span>
                    <span>${L.speakChangesBtn}</span>
                  </button>
                  <button onclick="window.NyayaVaniApp.copyDocument(this)" data-content="${encodeURIComponent(data.formal_document || data.draft_document || data.formal_notice || '')}" class="cta-contrast-btn px-3 py-1.5 text-xs font-mono">
                    <span>📋 ${this.escapeHtml(L.copyTextBtn)}</span>
                  </button>
                  <button onclick="window.print()" class="cta-contrast-btn px-3 py-1.5 text-xs font-mono">
                    <span>🖨️ ${this.escapeHtml(L.printPdfBtn)}</span>
                  </button>
                </div>
              </div>
              <pre class="p-5 text-xs font-mono text-[var(--text-primary)] max-h-96 overflow-y-auto whitespace-pre-wrap leading-relaxed select-text bg-[var(--bg-card)]">${this.escapeHtml(data.formal_document || data.draft_document || data.formal_notice || 'Document draft compiled.')}</pre>
              
              <!-- Approved Signoff Roles & Statutory Safeguards -->
              <div class="p-4 bg-[var(--bg-subtle)] border-t border-[var(--border-subtle)] text-[11px] font-mono space-y-2">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="text-[var(--text-muted)] font-bold">${this.escapeHtml(L.approvedSignoff)}</span>
                  <span class="px-2.5 py-0.5 rounded bg-[var(--bg-card)] border border-[var(--border-subtle)] text-[var(--text-primary)] font-bold">Client</span>
                  <span class="px-2.5 py-0.5 rounded bg-[var(--bg-card)] border border-[var(--border-subtle)] text-[var(--text-primary)] font-bold">Authorized Representative</span>
                  <span class="px-2.5 py-0.5 rounded bg-[var(--bg-card)] border border-[var(--border-subtle)] text-[var(--text-primary)] font-bold">Independent Legal Counsel</span>
                </div>
                <div class="text-[10px] text-[var(--text-muted)] leading-relaxed">
                  ${L.signoffNotice}
                </div>
              </div>
            </div>

            <!-- CARD 2: UNDERSTAND YOUR RIGHTS & APPLICABLE DHAARA -->
            ${rightsHtml}
            ${verdictHtml}
            ${proHtml}

            <!-- Governing Citations Grid -->
            <div class="mb-5 p-4 rounded-2xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
              <div class="flex items-center justify-between mb-2">
                <h4 class="text-xs font-mono font-bold uppercase text-[var(--text-muted)]">// STATUTORY CITATIONS PENDING ADVOCATE VERIFICATION</h4>
              </div>
              <ul class="list-disc pl-4 space-y-1">
                ${statutesHtml}
              </ul>
            </div>

            ${data.transcript ? `<div class="mb-4 p-3 rounded-xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)]"><div class="text-[10px] font-mono text-[var(--primary)] mb-1">WHAT WE HEARD · PLEASE CHECK</div><p class="text-sm text-[var(--text-secondary)]">${this.escapeHtml(data.transcript)}</p></div>` : ''}
            ${data.sha256 ? `<div class="mb-4 p-2.5 rounded-xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)] flex flex-col sm:flex-row sm:items-center justify-between text-[11px] font-mono gap-1"><span class="text-[var(--text-muted)]">Electronic Record Integrity Hash (SHA-256):</span><span class="text-[var(--accent)] font-bold truncate max-w-xs">${this.escapeHtml(data.sha256)}</span></div>` : ''}

            <!-- Spoken Guidance Player (If audio present) -->
            ${data.audio_url ? `
              <div class="mb-5 p-4 rounded-2xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-mono font-bold text-[var(--primary)] flex items-center space-x-2">
                    <span>${spokenTitle}</span>
                  </span>
                  <span class="text-[10px] font-mono text-[var(--text-muted)]">GENERATED AUDIO</span>
                </div>
                <p class="text-xs text-[var(--text-secondary)] italic mb-3 leading-relaxed">${this.escapeHtml(data.spoken_text || '')}</p>
                <audio controls src="${this.escapeHtml(encodeURI(data.audio_url))}" class="w-full h-8 rounded-lg outline-none"></audio>
              </div>
            ` : ''}

            <!-- CARD 3: RECOMMENDED NEXT ACTIONS -->
            <div class="mb-5 p-4 rounded-2xl bg-[var(--accent-subtle)] border-2 border-[var(--accent)] shadow-md" style="box-shadow: var(--accent-glow);">
              <div class="flex items-center space-x-2 mb-2">
                <span class="text-base">🎯</span>
                <h4 class="text-xs font-mono font-bold uppercase text-[var(--accent)]">${this.escapeHtml(L.whatNextTitle || actionTitle)}</h4>
              </div>
              <div class="space-y-1">
                ${stepsHtml}
              </div>
            </div>

            <!-- CARD 4: FREE LEGAL AID HANDOFF -->
            ${data.legal_aid_referral ? `
              <div class="mb-5 p-4 rounded-2xl bg-[var(--accent-subtle)] border-2 border-[var(--accent-border)]">
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center space-x-2">
                    <span class="text-[var(--accent)] font-bold text-xs font-mono">${this.escapeHtml(L.dlsaTitle)}</span>
                  </div>
                  <a href="tel:15100" class="px-3 py-1 rounded-full bg-[var(--accent)] text-white font-bold text-[11px] font-mono hover:opacity-90 transition">${this.escapeHtml(L.dlsaCallBtn)}</a>
                </div>
                <p class="text-xs text-[var(--text-secondary)] mb-2">${this.escapeHtml(data.legal_aid_referral.eligibility_summary || '')}</p>
                <div class="text-[11px] font-mono text-[var(--text-muted)] mb-1">Documents to bring to your District Legal Services Authority:</div>
                <ul class="list-disc pl-5 text-[11px] text-[var(--text-secondary)] mb-2">
                  ${(data.legal_aid_referral.documents_to_carry || []).map(doc => `<li>${this.escapeHtml(doc)}</li>`).join('')}
                </ul>
                <div class="text-[10px] font-mono text-[var(--text-muted)] italic">Notice: ${this.escapeHtml(data.legal_aid_referral.disclaimer || '')}</div>
              </div>
            ` : ''}

            <!-- CARD 5: REVISION PROMPT -->
            <div class="p-4 rounded-2xl bg-[var(--bg-subtle)] border border-[var(--border-subtle)] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono">
              <div class="text-[var(--text-secondary)]">
                <span class="font-bold text-[var(--text-primary)]">${this.escapeHtml(L.revisionPrompt)}</span>
                <span class="text-[var(--text-muted)] sm:ml-1">${this.escapeHtml(L.orSpeak)}</span>
              </div>
              <button type="button" onclick="window.NyayaVaniApp.startVoiceReply('${caseId}')" class="cta-primary-btn px-3 py-1.5 text-xs">
                <span>${this.escapeHtml(L.editDetails)}</span>
              </button>
            </div>
          `}

        </div>
      </div>
    `;

    container.insertAdjacentHTML('beforeend', msgHtml);
    container.scrollTop = container.scrollHeight;
  },

  appendErrorMessage(err) {
    const container = document.getElementById('messages-container');
    const errHtml = `
      <div class="flex justify-start">
        <div class="themed-chat-bubble rounded-2xl p-4 text-sm text-red-600 border border-red-300 max-w-2xl bg-red-50">
          <div class="font-mono text-xs font-bold mb-1">Notice / Voice Fallback</div>
          <div class="leading-relaxed">${this.escapeHtml(err)}</div>
        </div>
      </div>
    `;
    if (container) {
      container.insertAdjacentHTML('beforeend', errHtml);
      container.scrollTop = container.scrollHeight;
    }
  },

  /**
   * Renders the Complete End-to-End Legal Guideline & Case Dossier in Pro Mode
   */
  renderProGuideline(data, container) {
    if (!container) return;

    const intake = data.intake || {};
    const missing = intake.missing_facts || [];
    const questions = intake.follow_up_questions || data.follow_up_questions || [];
    const statutes = data.statutory_sections || [];
    const steps = data.action_steps || [];
    const lv = data.legality_verdict || {};
    const packet = data.pro_packet || {};
    const packetId = packet.packet_id || `pkt_${Date.now().toString(16)}`;
    const caseId = `pro-${packetId}`;
    rightsDataStore[caseId] = data;

    // Update Step Cards in Stepper
    ['pro-step-1', 'pro-step-2', 'pro-step-3', 'pro-step-4'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.className = 'p-3.5 rounded-xl border-2 border-[var(--primary)] bg-[var(--bg-card)] shadow-md transition';
      }
    });

    const statutesHtml = statutes.map(s => `
      <div class="p-3.5 rounded-xl bg-[var(--bg-card)] border border-[var(--primary-border)] shadow-sm">
        <div class="font-bold text-[var(--primary)] font-mono text-xs">${this.escapeHtml(s.law)}</div>
        <div class="text-[var(--text-secondary)] text-xs mt-1 leading-relaxed">${this.escapeHtml(s.details)}</div>
      </div>
    `).join('');

    const stepsHtml = steps.map((st, i) => `
      <div class="flex items-start space-x-3 p-3 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] text-xs">
        <span class="w-6 h-6 rounded-lg bg-[var(--primary-subtle)] border border-[var(--primary)] text-[var(--primary)] font-mono font-bold flex items-center justify-center shrink-0 text-[11px]">${i + 1}</span>
        <div class="text-[var(--text-primary)] leading-relaxed pt-0.5">${this.escapeHtml(st)}</div>
      </div>
    `).join('');

    const html = `
      <div class="space-y-6 animate-fadeIn">
        
        <!-- Case Intelligence Executive Summary Banner -->
        <div class="p-5 rounded-2xl themed-card border-2 border-[var(--primary)] shadow-lg" style="box-shadow: var(--gold-glow);">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[var(--border-subtle)] mb-3 gap-2">
            <div class="flex items-center space-x-2.5">
              <span class="text-xl">🏛️</span>
              <div>
                <span class="font-mono text-xs font-bold text-[var(--primary)] uppercase tracking-wider">${this.escapeHtml(data.category || 'COMMERCIAL & STATUTORY DISPUTE')}</span>
                <span class="text-[10px] font-mono text-emerald-400 ml-2 font-bold px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-500/40">● AUTONOMOUS GUIDELINE COMPILED</span>
              </div>
            </div>
            <div class="text-[10px] font-mono text-[var(--text-muted)]">
              Case Ref: <span class="font-bold text-[var(--primary)]">${packetId}</span>
            </div>
          </div>
          <div class="text-xs text-[var(--text-secondary)] leading-relaxed">
            ${data.spoken_text ? `<p class="italic mb-2 text-[var(--primary-text)] font-semibold">"${this.escapeHtml(data.spoken_text)}"</p>` : ''}
            Autonomous statutory verification active. Below is the multi-stage legal guideline covering facts, governing acts, strategic action, and the cryptographic court-ready dossier.
          </div>
        </div>

        <!-- STAGE 01: Fact Timeline & Evidence Gap Matrix -->
        <div class="p-6 rounded-2xl themed-card border border-[var(--border-subtle)] shadow-sm">
          <div class="flex items-center space-x-2 text-xs font-mono font-bold text-[var(--primary)] uppercase tracking-wider mb-3">
            <span class="w-2.5 h-2.5 rounded-full bg-[var(--primary)]"></span>
            <span>STAGE 01 // Chronological Fact Audit & Evidence Gaps</span>
          </div>
          
          <div class="p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] mb-4 text-xs text-[var(--text-primary)] leading-relaxed">
            <strong>Intake Summary:</strong> ${this.escapeHtml(data.ai_synthesized_summary || data.spoken_text || 'Case account verified.')}
          </div>

          ${questions.length > 0 ? `
            <div class="p-4 rounded-xl bg-[var(--primary-subtle)] border border-[var(--primary-border)] text-xs">
              <div class="font-mono font-bold text-[var(--primary)] uppercase text-[11px] mb-2">Critical Evidentiary Clarifications Required:</div>
              <ul class="space-y-1 text-[var(--text-secondary)]">
                ${questions.map(q => `<li class="flex items-start space-x-1.5"><span class="text-[var(--primary)] font-bold">?</span><span>${this.escapeHtml(q)}</span></li>`).join('')}
              </ul>
            </div>
          ` : '<div class="text-xs text-emerald-400 font-mono">✅ Initial fact chronology verified with no immediate blocking gaps.</div>'}
        </div>

        <!-- STAGE 02: Statutory Provisions & Citation Authority -->
        <div id="pro-stage-section-2" class="p-6 rounded-2xl themed-card border border-[var(--border-subtle)] shadow-sm">
          <div class="flex items-center space-x-2 text-xs font-mono font-bold text-[var(--primary)] uppercase tracking-wider mb-3">
            <span class="w-2.5 h-2.5 rounded-full bg-[var(--primary)]"></span>
            <span>STAGE 02 // Governing Statutes & Precedent Authority</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
            ${statutesHtml || '<div class="text-xs text-[var(--text-muted)]">Statutory sections mapped to national legislative repositories.</div>'}
          </div>

          ${lv.verdict_summary ? `
            <div class="p-3.5 rounded-xl bg-[var(--bg-surface)] border border-[var(--primary-border)] text-xs">
              <span class="font-mono font-bold text-[var(--primary)] text-[11px] uppercase block mb-1">Legality & Standing Verdict:</span>
              <p class="text-[var(--text-secondary)] leading-relaxed">${this.escapeHtml(lv.verdict_summary)}</p>
            </div>
          ` : ''}
        </div>

        <!-- STAGE 03: Multi-Stage Strategic Action Roadmap & Calling Rehearsal -->
        <div id="pro-stage-section-3" class="p-6 rounded-2xl themed-card border border-[var(--border-subtle)] shadow-sm space-y-5">
          <div>
            <div class="flex items-center space-x-2 text-xs font-mono font-bold text-[var(--primary)] uppercase tracking-wider mb-3">
              <span class="w-2.5 h-2.5 rounded-full bg-[var(--primary)]"></span>
              <span>STAGE 03 // Sequential Defense Plan & Calling Rehearsal</span>
            </div>
            <div class="space-y-2 mb-4">
              ${stepsHtml}
            </div>
            ${data.legal_aid_referral ? `
              <div class="p-3.5 rounded-xl bg-[var(--accent-subtle)] border border-[var(--accent-border)] text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <span class="font-bold text-[var(--accent)] font-mono block">🏛️ Statutory Forum Referral (NALSA / DLSA / MACT Lok Adalat):</span>
                  <span class="text-[var(--text-secondary)]">${this.escapeHtml(data.legal_aid_referral.eligibility_summary || 'Eligible for pre-litigation settlement.')}</span>
                </div>
                <a href="tel:15100" class="px-3 py-1.5 rounded-full bg-[var(--accent)] text-white font-mono font-bold text-xs hover:opacity-90 transition whitespace-nowrap self-start sm:self-auto">Call 15100</a>
              </div>
            ` : ''}
          </div>

          <!-- Interactive Simulated Legal Calling Sandbox -->
          <div class="p-5 rounded-2xl bg-[var(--bg-surface)] border-2 border-[var(--primary)] shadow-md" style="box-shadow: var(--gold-glow);">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[var(--border-subtle)] mb-3 gap-2">
              <div class="flex items-center space-x-2">
                <span class="text-xl">📞</span>
                <div>
                  <span class="font-mono text-xs font-bold text-[var(--primary)] uppercase tracking-wider">SIMULATED OPPONENT CALL & REBUTTAL SANDBOX</span>
                  <span class="text-[10px] font-mono text-amber-400 ml-2 font-bold px-2 py-0.5 rounded-full bg-amber-950/50 border border-amber-500/40">● IN-MEMORY SIMULATION (SAFETY BOUNDARY: REAL OUTBOUND PSTN DISABLED)</span>
                </div>
              </div>
              <span class="text-[10px] font-mono text-[var(--text-muted)]">Audio: Synthetic Roleplay</span>
            </div>

            <!-- Parameters -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4 text-xs font-mono">
              <div>
                <label class="block text-[10px] text-[var(--text-muted)] uppercase mb-1">Simulated Opponent Entity:</label>
                <input id="pro-call-target" type="text" value="${this.escapeHtml(data.category === 'MOTOR_ACCIDENT_PRO' ? 'Commercial Truck Insurer Claims Dept' : (data.category === 'WAGE_THEFT' ? 'InfraTech Construction Management' : 'Opposing Entity / Landlord Legal Rep'))}" class="w-full p-2.5 rounded-lg bg-[var(--bg-input)] border border-[var(--border-subtle)] text-[var(--text-primary)] text-xs outline-none focus:border-[var(--primary)]">
              </div>
              <div>
                <label class="block text-[10px] text-[var(--text-muted)] uppercase mb-1">Simulation Negotiation Goal:</label>
                <input id="pro-call-goal" type="text" value="Demand immediate statutory acknowledgment and negotiate pre-litigation settlement." class="w-full p-2.5 rounded-lg bg-[var(--bg-input)] border border-[var(--border-subtle)] text-[var(--text-primary)] text-xs outline-none focus:border-[var(--primary)]">
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-wrap items-center gap-2 mb-4">
              <button type="button" id="btn-start-pro-call" onclick="window.NyayaVaniApp.startSimulatedProCall('${caseId}')" class="cta-primary-btn px-4 py-2 text-xs flex items-center space-x-2">
                <span>▶</span>
                <span>START SIMULATED NEGOTIATION CALL</span>
              </button>
              <button type="button" id="btn-conclude-pro-call" onclick="window.NyayaVaniApp.concludeSimulatedProCall('${caseId}')" class="cta-contrast-btn px-4 py-2 text-xs hidden">
                <span>⏹</span>
                <span>CONCLUDE & SIGN DIGEST</span>
              </button>
            </div>

            <!-- Live Dialogue Console -->
            <div id="pro-call-dialogue-box-${caseId}" class="hidden space-y-3 p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]">
              <div id="pro-call-turns-${caseId}" class="space-y-2.5 max-h-64 overflow-y-auto pr-1 text-xs">
                <!-- Dialogue turns populate here -->
              </div>
              
              <div class="pt-3 border-t border-[var(--border-subtle)] flex items-center gap-2">
                <button type="button" onclick="window.NyayaVaniApp.toggleCallVoiceReply('${caseId}')" id="btn-call-mic-${caseId}" class="px-3 py-2 rounded-lg border border-[var(--primary-border)] bg-[var(--primary-subtle)] text-[var(--primary)] text-xs font-mono font-bold flex items-center space-x-1 shrink-0">
                  <span>🎙️</span>
                  <span>Speak Rebuttal</span>
                </button>
                <input id="pro-call-reply-input-${caseId}" type="text" placeholder="Speak or type counter-rebuttal based on statutory provisions..." class="flex-1 p-2.5 rounded-lg bg-[var(--bg-input)] border border-[var(--border-subtle)] text-xs text-[var(--text-primary)] outline-none focus:border-[var(--primary)]" onkeydown="if(event.key==='Enter') window.NyayaVaniApp.sendSimulatedCallReply('${caseId}')">
                <button type="button" onclick="window.NyayaVaniApp.sendSimulatedCallReply('${caseId}')" class="cta-primary-btn px-3.5 py-2 text-xs">Send</button>
              </div>
            </div>

            <div id="pro-call-digest-${caseId}" class="hidden mt-3 p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-xs font-mono text-emerald-200">
            </div>
          </div>
        </div>

        <!-- STAGE 04: Court-Ready Legal Dossier & Cryptographic Hash -->
        <div id="pro-stage-section-4" class="p-6 rounded-2xl themed-card border-2 border-[var(--primary-border)] shadow-xl" style="box-shadow: var(--gold-glow);">
          <div class="flex items-center justify-between pb-3 border-b border-[var(--border-subtle)] mb-4">
            <div class="flex items-center space-x-2 text-xs font-mono font-bold text-[var(--primary)] uppercase tracking-wider">
              <span class="w-2.5 h-2.5 rounded-full bg-[var(--primary)] animate-ping"></span>
              <span>STAGE 04 // Court-Ready Legal Packet & Hash Seal</span>
            </div>
            <span class="text-[10px] font-mono font-bold text-amber-400 px-2 py-0.5 rounded-full bg-amber-950/50 border border-amber-500/40">FROZEN INTEGRITY SEAL</span>
          </div>

          <!-- Hash Banner -->
          <div class="p-3 rounded-xl bg-[var(--bg-input)] border border-[var(--border-subtle)] font-mono text-[11px] text-[var(--text-muted)] mb-4 flex flex-wrap items-center justify-between gap-1">
            <span>🔒 SHA-256 HASH: <span class="text-[var(--primary)] font-bold">${packet.content_hash || 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}</span></span>
            <span class="text-emerald-400 font-bold">VERIFIED UNTAMPERED</span>
          </div>

          <!-- Document Box -->
          <div class="border border-[var(--border-subtle)] rounded-xl overflow-hidden bg-[var(--bg-card)] mb-4">
            <div class="p-3 bg-[var(--bg-surface)] border-b border-[var(--border-subtle)] flex items-center justify-between">
              <div>
                <span class="text-xs font-mono font-bold text-[var(--primary)]">Draft Incident Summary for Review — Not Legal Advice</span>
                <div class="text-[10px] font-mono text-[var(--text-muted)]">Statutory citations pending advocate verification · Outbound transmission disabled (Review only)</div>
              </div>
              <button onclick="window.NyayaVaniApp.copyDocument(this)" data-content="${encodeURIComponent(data.formal_document || data.draft_document || data.formal_notice || '')}" class="cta-contrast-btn px-3 py-1 text-xs">
                Copy Full Dossier
              </button>
            </div>
            <pre class="p-4 text-xs font-mono text-[var(--text-primary)] max-h-80 overflow-y-auto whitespace-pre-wrap leading-relaxed">${this.escapeHtml(data.formal_document || data.draft_document || data.formal_notice || 'Dossier compiled.')}</pre>
          </div>

          <!-- Advocate Sign-off Boundary -->
          <div class="p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)]">
            <div class="text-xs font-mono font-bold text-[var(--primary)] mb-1">Advocate / Client Freeze Boundary Sign-Off</div>
            <p class="text-[11px] text-[var(--text-muted)] mb-3 leading-relaxed">
              Signing does <strong>NOT</strong> transmit this document to police, insurer, or court. It approves this structured dossier for human review, filing submission, and offline export.
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
              <div>
                <label for="approver-name-${caseId}" class="block text-[11px] font-mono text-[var(--text-muted)] mb-1">Approver Full Name *</label>
                <input id="approver-name-${caseId}" type="text" placeholder="Full legal name" value="${this.escapeHtml(packet.client_name || '')}" class="w-full p-2.5 rounded-lg bg-[var(--bg-input)] border border-[var(--border-subtle)] text-xs text-[var(--text-primary)] focus:border-[var(--primary)] outline-none">
              </div>
              <div>
                <label for="approver-role-${caseId}" class="block text-[11px] font-mono text-[var(--text-muted)] mb-1">Approver Role *</label>
                <select id="approver-role-${caseId}" class="w-full p-2.5 rounded-lg bg-[var(--bg-input)] border border-[var(--border-subtle)] text-xs text-[var(--text-primary)] focus:border-[var(--primary)] outline-none">
                  <option value="Client">Client</option>
                  <option value="Authorized Representative">Authorized Representative</option>
                  <option value="Independent Legal Counsel">Independent Legal Counsel</option>
                </select>
              </div>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <button type="button" onclick="window.NyayaVaniApp.approveProPacket('${packetId}', '${caseId}')" class="cta-primary-btn px-4 py-2 text-xs">Sign & Freeze Packet</button>
              <button type="button" onclick="window.NyayaVaniApp.copyPacket('${caseId}')" class="cta-contrast-btn px-3.5 py-2 text-xs">Copy Dossier</button>
            </div>
            <p id="packet-status-${caseId}" class="text-xs text-[var(--primary)] mt-2 font-mono">Status: Awaiting sign-off. Outbound transmission disabled (Review only).</p>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;
    container.scrollIntoView({ behavior: 'smooth' });
  }
};
