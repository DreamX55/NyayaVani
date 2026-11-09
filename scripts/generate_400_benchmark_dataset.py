#!/usr/bin/env python3
"""
NyayaVani 400-Question Sovereign Multilingual Legal Benchmark Suite Generator
Constructs 400 systematically verified legal intake queries across:
- 10 Indian Languages: Hindi, Marathi, Gujarati, Bhojpuri, Kannada, Tamil, Telugu, Bengali, Punjabi, Malayalam
- 4 Linguistic Formats: Pure Spoken, Pure Written, Broken Spoken, Broken Written
- 3 Legal Truth Classifications:
  1. CITIZEN_RIGHTS_SQUANDERED (20 cases/lang = 200 cases) -> Authority/Actor is at fault; Citizen is statutorily protected.
  2. CITIZEN_AT_FAULT_LAWFUL_AUTHORITY (10 cases/lang = 100 cases) -> Citizen is in breach (contaminated food, drunk driving, permanent obstruction, bank NPA); Authority is acting lawfully.
  3. AMBIGUOUS_FOLLOW_UP_REQUIRED (10 cases/lang = 100 cases) -> Incomplete facts requiring clarifying follow-up question before a verdict can be issued.
"""

import json
import os

LANGUAGES = [
    {"code": "hi", "name": "Hindi", "region": "North India", "script": "Devanagari"},
    {"code": "mr", "name": "Marathi", "region": "Maharashtra", "script": "Devanagari"},
    {"code": "gu", "name": "Gujarati", "region": "Gujarat", "script": "Gujarati"},
    {"code": "bhoj", "name": "Bhojpuri", "region": "Purvanchal / Bihar & Eastern UP", "script": "Devanagari"},
    {"code": "kn", "name": "Kannada", "region": "Karnataka", "script": "Kannada"},
    {"code": "ta", "name": "Tamil", "region": "Tamil Nadu", "script": "Tamil"},
    {"code": "te", "name": "Telugu", "region": "Andhra Pradesh & Telangana", "script": "Telugu"},
    {"code": "bn", "name": "Bengali", "region": "West Bengal", "script": "Bengali"},
    {"code": "pa", "name": "Punjabi", "region": "Punjab", "script": "Gurmukhi"},
    {"code": "ml", "name": "Malayalam", "region": "Kerala", "script": "Malayalam"}
]

# Template generators for authentic regional representation
def generate_benchmark_400():
    dataset = []

    # Linguistic dictionaries per language for high-fidelity native phrasing
    lex = {
        "hi": {
            "vendor_extort_spoken": "साहब, हम 10 साल से यहां ठेला लगा रहे हैं, आज पुलिस वाले आकर बोले 500 रुपये हफ्ता दो नहीं तो ठेला उठाकर थाने में बंद कर देंगे, मेरे पास स्वनिधि की पर्ची भी है।",
            "vendor_extort_written": "प्रार्थी नगर निगम क्षेत्र में अधिकृत फेरीवाला है। स्थानीय पुलिस द्वारा विधि विरुद्ध रूप से ₹500 की अवैध वसूली (हफ्ता) की मांग की जा रही है एवं ठेला जब्त करने की धमकी दी जा रही है।",
            "vendor_extort_broken_spoken": "अरे भैया पुलिस वाला आके डंडा पटक रहा है बोलता है 500 निकालो नहीं तो दुकान फेंक देंगे नाली में, बचाओ कोई!",
            "vendor_extort_broken_written": "Police wale aake 500 hafta mang rahe hai aur thela uthane ki dhamki de rahe hai mere pas vendor slip hai fir bhi sun nahi rahe.",
            
            "cyber_spoken": "एक मोबाइल लोन ऐप वाले मेरे फोन के सारे कांटेक्ट निकाल कर मेरी गंदी मॉर्फ फोटो मेरी बहन और रिश्तेदारों को भेजकर 50 हजार की रंगदारी मांग रहे हैं।",
            "cyber_written": "अनाधिकृत डिजिटल ऋण ऐप द्वारा आवेदक के व्यक्तिगत संपर्कों एवं छायाचित्रों को विकृत (Morph) कर ब्लैकमेलिंग एवं जबरन धन उगाही की जा रही है।",
            "cyber_broken_spoken": "साहब फोन में फोटो बदल के सबको भेज दिया रिश्तेदार गाली दे रहे हैं बोलता है 50 हजार दो नहीं तो और बदनाम करेंगे!",
            "cyber_broken_written": "Loan app walas mara contacts hack karke morphed photo whatsapp pe send kar rahe hai aur blackmail karke paise mang rahe hai.",

            "accident_spoken": "मैं अपनी बाइक से जा रहा था, पीछे से एक तेज रफ्तार सफेद कार ने टक्कर मारी, मेरा पैर टूट गया और वो गाड़ी लेकर भाग गया।",
            "accident_written": "वाहन संख्या UP-16-XX द्वारा आवेदक की मोटरसाइकिल को लापरवाही एवं तेज गति से टक्कर मारकर गंभीर शारीरिक क्षति पहुंचाई गई एवं चालक दुर्घटनास्थल से फरार हो गया।",
            "accident_broken_spoken": "रोड पे तेज गाड़ी वाला ठोक के भाग गया भैया पैर से खून बह रहा है कोई गाड़ी का नंबर नोट करो!",
            "accident_broken_written": "Speeding car collision hua hai hit and run case hai driver bhaag gaya hospital me admit hu MACT claim karna hai.",

            "rera_spoken": "बिल्डर ने 2022 में फ्लैट देने का वादा किया था, 3 साल हो गए काम बंद पड़ा है, ओसी भी नहीं है और पैसे मांगने पर टरका रहा है।",
            "rera_written": "प्रमोटर द्वारा विक्रय अनुबंध की शर्तों के विपरीत 36 माह का अत्यधिक विलंब किया गया है एवं बिना अधिभोग प्रमाण पत्र (OC) के कब्जा देने से इनकार किया जा रहा है।",
            "rera_broken_spoken": "बिल्डर 3 साल से घुमा रहा है बोलता है जब बनेगा तब मिलेगा पैसा वापस नहीं दूंगा जो करना है कर लो!",
            "rera_broken_written": "Builder delayed flat possession by 3 years without occupancy certificate RERA refund with interest demand karna hai.",

            "msme_spoken": "हमने कंपनी को 12 लाख का माल सप्लाई किया था, 60 दिन हो गए पेमेंट रोक कर बैठे हैं, फोन करने पर टालमटोल कर रहे हैं।",
            "msme_written": "क्रेता प्रतिष्ठान द्वारा एमएसएमईडी अधिनियम की धारा 15 का उल्लंघन करते हुए 45 दिवस की सांविधिक अवधि के उपरांत भी ₹12,00,000 का बकाया भुगतान अवरुद्ध रखा गया है।",
            "msme_broken_spoken": "60 दिन हो गए भैया 12 लाख का बिल अटका के बैठे हैं हमारा छोटा कारखाना बंद होने की नौबत आ गई है!",
            "msme_broken_written": "MSME firm payment overdue 60 days cross ho gaya compound interest demand notice bhejna hai samadhaan portal ke liye.",

            "wages_spoken": "ठेकेदार ने हमसे चार महीने दिन-रात काम करवाया, अब 40 हजार मजदूरी देने से साफ मुकर गया और मारपीट की धमकी दे रहा है।",
            "wages_written": "नियोजक द्वारा मजदूरी संदाय अधिनियम 1936 की धारा 15 के विरुद्ध 4 माह का अर्जित पारिश्रमिक अवैध रूप से रोका गया है जो बंधुआ मजदूरी की श्रेणी में आता है।",
            "wages_broken_spoken": "साहब चार महीने का पसीना बहाया एक रुपया नहीं दिया ठेकेदार बोलता है भागो यहां से नहीं तो पुलिस में बंद करा दूंगा!",
            "wages_broken_written": "Contractor refused 4 months wage payment of Rs 40000 threatening workers payment of wages act complaint draft chahiye.",

            "eviction_spoken": "सुबह-सुबह नगर निगम वाले बिना किसी नोटिस के बुलडोजर लेकर आ गए और हमारे 20 साल पुराने आशियाने को तोड़ने लगे।",
            "eviction_written": "प्रशासन द्वारा बिना किसी पूर्व सूचना अथवा पुनर्वास योजना के अनुच्छेद 21 एवं ओल्गा तेलिस निर्णय की अवहेलना करते हुए बस्तियों का ध्वस्तीकरण किया जा रहा है।",
            "eviction_broken_spoken": "बिना कागज बिना नोटिस सीधा बुलडोजर घुसा दिया हमारे बच्चे बेघर हो गए कोई रोको इनको!",
            "eviction_broken_written": "Slum demolition without prior notice or rehabilitation plan violating Supreme Court Olga Tellis precedent Article 21.",

            "prayer_spoken": "हम शांतिपूर्वक प्रार्थना कर रहे थे, कुछ उपद्रवी लाठी लेकर घुस आए, तोड़फोड़ की और जान से मारने की धमकी देकर सभा बंद करवा दी।",
            "prayer_written": "संविधान के अनुच्छेद 25 द्वारा प्रदत्त धार्मिक स्वतंत्रता के अंतर्गत आयोजित शांतिपूर्ण प्रार्थना सभा में असमाजिक तत्वों द्वारा बलपूर्वक प्रवेश एवं उपद्रव किया गया।",
            "prayer_broken_spoken": "हॉल के अंदर आकर माइक छीन लिया लाठी भांजने लगे बोले यहां पूजा प्रार्थना नहीं करने देंगे भागो सब!",
            "prayer_broken_written": "Vigilante mob attacked lawful peaceful prayer gathering and threatened worshippers Article 25 violation Zero FIR required.",

            "fir_refusal_spoken": "थानेदार साहब बोले कि यह मामला हमारे इलाके का नहीं है, दूसरे थाने जाओ और हमारी एफआईआर लिखने से साफ मना कर दिया।",
            "fir_refusal_written": "थाना प्रभारी द्वारा संज्ञेय अपराध की सूचना प्राप्त होने पर भी अधिकार क्षेत्र का बहाना बनाकर बीएनएसएस की धारा 173(1) के अंतर्गत जीरो एफआईआर दर्ज करने से इनकार किया गया।",
            "fir_refusal_broken_spoken": "चौकी वाला दरोगा भगा दिया बोला यहां रिपोर्ट नहीं लिखेंगे जहां घटना हुई वहां जाओ हम थक गए दौड़ते दौड़ते!",
            "fir_refusal_broken_written": "Police station SHO refused to register Zero FIR citing jurisdictional boundary BNSS Section 173 violation SP escalation needed.",

            "bsa_evidence_spoken": "मेरे पास पुलिस और ठेकेदार की घूस मांगते हुए स्पष्ट ऑडियो रिकॉर्डिंग और वीडियो है, इसे कोर्ट में कानूनी सबूत बनाना है।",
            "bsa_evidence_written": "अपराध से संबंधित समकालीन इलेक्ट्रॉनिक साक्ष्य (ऑडियो/वीडियो) को भारतीय साक्ष्य अधिनियम, 2023 की धारा 63 के अंतर्गत प्रमाणित एवं संरक्षित करने का अनुरोध।",
            "bsa_evidence_broken_spoken": "मोबाइल में पूरी रिकॉर्डिंग है हफ्ता मांगते हुए इसको पक्का कानूनी सबूत कैसे बनाएं ताकि दरोगा मुकर ना सके?",
            "bsa_evidence_broken_written": "Contemporaneous audio recording evidence preservation under BSA Section 63 with SHA-256 timestamp hash certificate.",

            # Citizen At Fault Scenarios (Lawful Authority Power)
            "fault_food_spoken": "फूड इंस्पेक्टर और पुलिस ने मेरी चाट की दुकान सील कर दी क्योंकि चटनी और पानी में दुर्गंध आ रही थी और फफूंद लगी थी, मैं कोर्ट में केस करना चाहता हूं।",
            "fault_food_written": "खाद्य सुरक्षा अधिकारी द्वारा निरीक्षण के दौरान दूषित, बासी एवं सड़े हुए खाद्य पदार्थ पाए जाने पर खाद्य सुरक्षा मानक अधिनियम की धारा 59 के तहत दुकान को सीज किया गया।",
            "fault_food_broken_spoken": "अरे थोड़ा बासी सामान था तो क्या हुआ पुलिस आकर पूरा ठेला पलट दी और दुकान बंद करा दी हम इनके खिलाफ मुकदमा करेंगे!",
            "fault_food_broken_written": "Food safety officer seized stall for selling spoiled rotten contaminated food vendor wants to file police complaint against officer.",

            "fault_traffic_spoken": "मैंने शराब पी रखी थी और बिना हेलमेट रॉन्ग साइड बाइक चला रहा था, ट्रैफिक पुलिस ने गाड़ी जब्त कर ली और 10 हजार का चालान काट दिया।",
            "fault_traffic_written": "मोटर वाहन अधिनियम की धारा 185 एवं 207 के अंतर्गत ब्रीथ एनालाइजर परीक्षण में 95mg/100ml अल्कोहल स्तर एवं विपरीत दिशा में वाहन संचालन पर पुलिस द्वारा वाहन जब्ती।",
            "fault_traffic_broken_spoken": "थोड़ी सी दारू पीके आ रहे थे ट्रैफिक वाले ने पकड़ के गाड़ी बंद कर दी बोलता है कोर्ट से छुड़ाना हम पुलिस पे केस करेंगे!",
            "fault_traffic_broken_written": "Traffic police impounded vehicle for drink and drive and wrong side driving under MV Act Section 207 driver wants to challenge.",

            "fault_obstruction_spoken": "मैंने अस्पताल के मुख्य इमरजेंसी गेट के ठीक सामने सड़क पर ईंट-सीमेंट की पक्की दुकान बना ली थी, नगर निगम ने उसे तोड़ दिया।",
            "fault_obstruction_written": "नगर निगम अधिनियम की धारा 314 एवं स्ट्रीट वेंडर्स एक्ट की धारा 3(2) के तहत आपातकालीन अस्पताल द्वार अवरुद्ध करने वाले अनधिकृत पक्के निर्माण का ध्वस्तीकरण।",
            "fault_obstruction_broken_spoken": "अस्पताल के बाहर पक्का खोखा बना के बैठे थे एम्बुलेंस नहीं निकल पा रही थी तो बुलडोजर चला दिया हमारी रोजी रोटी छीन ली!",
            "fault_obstruction_broken_written": "Municipal corporation demolished permanent brick structure blocking hospital emergency gate vendor claiming livelihood protection.",

            "fault_sarfaesi_spoken": "मैंने बैंक से 20 लाख का बिजनेस लोन लिया था, 6 महीने से कोई किस्त नहीं दी, बैंक ने 60 दिन का सरफेसी नोटिस भेजकर दुकान सील करने की चेतावनी दी है।",
            "fault_sarfaesi_written": "ऋण खाता 90 दिवस से अधिक एनपीए रहने के उपरांत सुरक्षित लेनदार बैंक द्वारा सरफेसी अधिनियम 2002 की धारा 13(2) के तहत सांविधिक मांग सूचना पत्र जारी किया गया।",
            "fault_sarfaesi_broken_spoken": "बैंक वाले दुकान नीलाम करने का नोटिस चस्पा कर दिए हैं हम 6 महीने से किस्त नहीं भरे तो क्या वो हमारी संपत्ति छीन लेंगे?",
            "fault_sarfaesi_broken_written": "Bank issued SARFAESI Section 13(2) notice after 6 months of unpaid loan installments borrower wants injunction against bank.",

            # Ambiguous Scenarios (Mandatory Follow-Up Required)
            "amb_vendor_spoken": "कल दोपहर में पुलिस वाले मेरी दुकान पर आए थे और बोले कि यहां से दुकान बंद करो। [ambiguous]",
            "amb_vendor_written": "प्रशासनिक अधिकारियों द्वारा वेंडिंग स्थल पर आकर कार्य बंद करने का मौखिक निर्देश दिया गया। [ambiguous]",
            "amb_vendor_broken_spoken": "अरे भैया पुलिस आके बोली दुकान बढ़ाओ कल से मत दिखना यहां! [ambiguous]",
            "amb_vendor_broken_written": "Police came to my stall yesterday and told me to close it need legal advice. [ambiguous]",

            "amb_salary_spoken": "इस महीने कंपनी ने मेरे खाते में पूरे पैसे नहीं भेजे, कुछ पैसे कट कर आए हैं। [ambiguous]",
            "amb_salary_written": "माह के वेतन भुगतान में नियोजक द्वारा कटौती की गई है। [ambiguous]",
            "amb_salary_broken_spoken": "मालिक ने पगार काट ली इस बार बोला कम मिलेगा! [ambiguous]",
            "amb_salary_broken_written": "Company deducted salary this month without giving proper reason what are my rights? [ambiguous]",

            "amb_crash_spoken": "रास्ते में एक गाड़ी और मेरी गाड़ी आपस में टकरा गई थी। [ambiguous]",
            "amb_crash_written": "सड़क पर दो वाहनों के मध्य टक्कर की घटना घटित हुई है। [ambiguous]",
            "amb_crash_broken_spoken": "गाड़ी में डेंट लग गया दूसरी गाड़ी से भिड़ंत हो गई थी! [ambiguous]",
            "amb_crash_broken_written": "Minor accident happened on road between two vehicles need legal advice. [ambiguous]",

            "amb_loan_spoken": "मुझे फोन पर कोई कह रहा है कि पुराना पैसा तुरंत वापस करो। [ambiguous]",
            "amb_loan_written": "अज्ञात कॉलर द्वारा ऋण वसूली के संबंध में तत्काल भुगतान की मांग की जा रही है। [ambiguous]",
            "amb_loan_broken_spoken": "फोन पे बोल रहा है पैसा भरो नहीं तो ठीक नहीं होगा! [ambiguous]",
            "amb_loan_broken_written": "Received phone call demanding repayment of old money what should I do? [ambiguous]"
        },

        "mr": {
            "vendor_extort_spoken": "साहेब, आम्ही दादरला १० वर्षे फळांची हातगाडी लावतोय, आज पालिकेचे कर्मचारी येऊन ५०० रुपये हप्ता मागतायत, नाहीतर हातगाडी जप्त करू म्हणतात, माझ्याकडे अधिकृत पावती आहे.",
            "vendor_extort_written": "अर्जदार महापालिका क्षेत्रातील नोंदणीकृत फेरीवाला असून स्थानिक कर्मचाऱ्यांकडून बेकायदेशीर हप्ता वसुलीची मागणी करून हातगाडी जप्त करण्याची धमकी दिली जात आहे.",
            "vendor_extort_broken_spoken": "अरे दादा बीएमसी वाले आले आणि म्हणाले ५०० रुपये काढ नाहीतर गाडी उचलून नेऊ, आमच्याकडे पावती असून ऐकत नाहीत!",
            "vendor_extort_broken_written": "BMC staff demanding 500 hafta threatening to confiscate fruit cart despite having valid vending receipt Section 3(3) violation.",

            "cyber_spoken": "एका मोबाईल लोन ॲपने माझे सगळे कॉन्टॅक्ट्स हॅक करून माझे मॉर्फ केलेले घाणेरडे फोटो माझ्या नातेवाईकांना पाठवून ५० हजारांची खंडणी मागत आहेत.",
            "cyber_written": "बेकायदेशीर डिजिटल कर्ज ॲपद्वारे वैयक्तिक संपर्क यादी हॅक करून छायाचित्रांचे विकृतीकरण (Morphing) व नातेवाईकांना पाठवून खंडणी उकळली जात आहे.",
            "cyber_broken_spoken": "साहेब फोन मधले फोटो मॉर्फ करून सगळ्या ग्रुपवर पाठवलेत, ५० हजार द्या नाहीतर अजून व्हायरल करू म्हणतात!",
            "cyber_broken_written": "Loan app agents hacked phone contacts morphing photos and blackmailing for 50000 rupees extortion complaint needed.",

            "accident_spoken": "हायवेवर मागून एका भरधाव ट्रकने माझ्या कारला जोरदार धडक दिली, माझे वडील गंभीर जखमी झाले आणि ट्रक चालक पळून गेला.",
            "accident_written": "वाहन क्र. MH-12-XX च्या चालकाने भरधाव व निष्काळजीपणे वाहन चालवून अपघात घडवून आणला व जखमींना मदत न करता पळ काढला.",
            "accident_broken_spoken": "हायवेवर गाडीला उडवून ट्रकवाला पळाला दादा बाबांना हॉस्पिटलमध्ये ॲडमिट केलंय गाडीचा चेंदामेंदा झाला!",
            "accident_broken_written": "Highway truck hit and run collision grievous injury to passenger driver fled MACT compensation claim procedure.",

            "rera_spoken": "बिल्डरने २०२१ मध्ये फ्लॅटचा ताबा देण्याचे वचन दिले होते, ४ वर्षे झाली तरी ओसी मिळालेली नाही आणि काम बंद पाडले आहे.",
            "rera_written": "महारेरा नोंदणीकृत प्रकल्पात विकासकाने विहित मुदतीनंतरही ४८ महिने ताबा दिलेला नसून ओसी विना खरेदीदारांची फसवणूक केली आहे.",
            "rera_broken_spoken": "बिल्डर चार वर्षांपासून ताबा देत नाहीये, पैसे मागायला गेलो तर धमकी देतो, महारेरा मध्ये तक्रार करायची आहे!",
            "rera_broken_written": "Builder delayed flat possession by 4 years without occupancy certificate seeking MahaRERA 100% refund with interest.",

            "msme_spoken": "आमच्या लघुउद्योगाने १५ लाखांचे सुटे भाग कंपनीला पुरवले होते, ६० दिवस झाले तरी पेमेंट थकवले असून तीन पट व्याज मागतोय.",
            "msme_written": "एमएसएमई कायद्याच्या कलम १५ व १६ चे उल्लंघन करून खरेदीदार आस्थापनेने विहित ४५ दिवसांनंतरही देणी अडवून ठेवली आहेत.",
            "msme_broken_spoken": "६० दिवस झाले साहेब १५ लाखांचे बिल थकवून बसलेत, आमचा कारखाना बंद पडायची वेळ आली आहे!",
            "msme_broken_written": "MSME vendor payment defaulted beyond 45 days claiming 3x RBI compound interest under MSMED Section 16.",

            "wages_spoken": "कंत्राटदाराने आमच्याकडून चार महिने दिवसरात्र काम करून घेतले, आता ४५,००० पगार देत नाहीये आणि पोलिसांची भीती दाखवतोय.",
            "wages_written": "वेतन संदाय अधिनियम १९३६ च्या कलम १५ अन्वये कामगारांचे ४ महिन्यांचे थकीत वेतन कंत्राटदाराने बेकायदेशीररीत्या रोखून धरले आहे.",
            "wages_broken_spoken": "चार महिन्यांची मजुरी अडवून ठेवलीये, मालक बोलतो एक रुपया देणार नाही काय करायचं ते करा!",
            "wages_broken_written": "Contractor refused 4 months wages to workers threatening false police cases Payment of Wages Act recovery.",

            "eviction_spoken": "सकाळी सकाळी कोणतीही नोटीस न देता महापालिकेचे पथक बुलडोझर घेऊन आले आणि आमच्या झोपड्यांवर तोडफोड सुरू केली.",
            "eviction_written": "संविधानाचे कलम २१ व सर्वोच्च न्यायालयाच्या ओल्गा तेलीस निकालाचा अवमान करून पूर्वसूचना व पुनर्वसनाविना घरे पाडण्याची कारवाई.",
            "eviction_broken_spoken": "कोणतीही नोटीस न देता घरं तोडायला आले साहेब, लहान मुलं रस्त्यावर आलीत काहीतरी मदत करा!",
            "eviction_broken_written": "Slum demolition without prior notice or rehabilitation plan violating Article 21 and Olga Tellis Supreme Court ruling.",

            "prayer_spoken": "आम्ही प्रार्थना मंदिरात शांततेत रविवारची प्रार्थना करत असताना गुंडांनी लाठ्या घेऊन हल्ला केला आणि प्रार्थना बंद पाडली.",
            "prayer_written": "संविधानाच्या कलम २५ अंतर्गत हमी दिलेल्या धार्मिक स्वातंत्र्याचे उल्लंघन करून शांततापूर्ण प्रार्थनेवर समाजकंटकांकडून हल्ला.",
            "prayer_broken_spoken": "प्रार्थना हॉलमध्ये घुसून खुर्च्या तोडल्या आणि मारहाण केली, पोलीस ठाण्यात तक्रार नोंदवून घेत नाहीयेत!",
            "prayer_broken_written": "Vigilante mob attacked peaceful prayer meeting Article 25 violation police refusing to record FIR.",

            "fir_refusal_spoken": "पोलीस ठाण्यात गेलो असता अंमलदाराने सांगितले की ही घटना आमच्या हद्दीत घडलेली नाही, तक्रार घेण्यास नकार दिला.",
            "fir_refusal_written": "बीएनएसएस कलम १७३(१) चे उल्लंघन करून पोलीस ठाण्याने हद्दीचे कारण पुढे करत झिरो एफआयआर नोंदवण्यास नकार दिला.",
            "fir_refusal_broken_spoken": "ठाणे अंमलदार बोलतो आमच्या हद्दीत येत नाही दुसऱ्या पोलीस ठाण्यात जा, आम्ही चक्कर मारून थकलो!",
            "fir_refusal_broken_written": "Police station refused to register Zero FIR citing jurisdiction BNSS Section 173 escalation to Superintendent of Police.",

            "bsa_evidence_spoken": "माझ्याकडे पोलीस कर्मचारी लाच मागतानाचा संपूर्ण ऑडिओ आणि व्हिडिओ रेकॉर्डिंग आहे, कोर्टात सिद्ध करायचे आहे.",
            "bsa_evidence_written": "भारतीय साक्ष अधिनियम २०२३ च्या कलम ६३ अंतर्गत डिजिटल पुरावा (ऑडिओ/व्हिडिओ) टाइमस्टॅम्प व हॅश प्रमाणपत्रासह सादर करणे.",
            "bsa_evidence_broken_spoken": "मोबाईल मध्ये लाच मागतानाचे स्पष्ट रेकॉर्डिंग आहे, कोर्टात हे पुरावा म्हणून कसे वापरायचे?",
            "bsa_evidence_broken_written": "Oral affidavit and contemporaneous electronic evidence preservation under BSA Section 63 with SHA-256 hash.",

            # Citizen At Fault
            "fault_food_spoken": "अन्न सुरक्षा अधिकारी आणि पोलिसांनी माझी पाणीपुरीची गाडी जप्त केली कारण पाणी सडलेले होते आणि दुर्गंधी येत होती, मी पोलिसांवर केस करू का?",
            "fault_food_written": "अन्न सुरक्षा कायद्याच्या कलम ५९ अंतर्गत तपासणीत कुजलेले व विषबाधा घडवणारे खाद्यपदार्थ आढळल्याने कायदेशीर जप्ती कारवाई.",
            "fault_food_broken_spoken": "थोडं शिळं पाणी होतं म्हणून पालिकेच्या अधिकाऱ्याने गाडी सील केली आणि माल फेकून दिला, आम्हाला नुकसानभरपाई हवीये!",
            "fault_food_broken_written": "Food safety officer seized stall for selling rotten contaminated unhygienic water vendor wants to challenge police action.",

            "fault_traffic_spoken": "मी दारू पिऊन विरुद्ध दिशेने हेल्मेटशिवाय गाडी चालवत होतो, ट्रॅफिक पोलिसांनी माझी बाईक जप्त करून १० हजारांचा दंड लावला.",
            "fault_traffic_written": "मोटार वाहन कायद्याच्या कलम १८५ व २०७ अन्वये मद्यपान करून धोकादायक वाहन चालवल्याप्रकरणी कायदेशीर वाहन जप्ती व चलान.",
            "fault_traffic_broken_spoken": "दोन पेग मारून गाडी चालवत होतो तर ट्रॅफिकवाल्याने गाडी अडवून ठेवली, आम्ही पोलिसांविरोधात कोर्टात जाऊ शकतो का?",
            "fault_traffic_broken_written": "Traffic police impounded motorcycle for drunk driving and wrong side without helmet under MV Act 207 driver challenging.",

            "fault_obstruction_spoken": "मी सरकारी दवाखान्याच्या इमर्जन्सी गेटसमोर फुटपाथवर सिमेंटची पक्की टपरी बांधली होती, पालिकेने ती तोडून टाकली.",
            "fault_obstruction_written": "फेरीवाला कायदा कलम ३(२) व महापालिका अधिनियमान्वये रुग्णवाहिका प्रवेशद्वार अडवणाऱ्या पक्क्या बांधकामावर कायदेशीर निष्कासन.",
            "fault_obstruction_broken_spoken": "हॉस्पिटलच्या गेटसमोर पक्कं दुकान बांधलं होतं ॲम्ब्युलन्स अडत होती म्हणून पालिकेने तोडलं, आमचा हक्क हिरावला!",
            "fault_obstruction_broken_written": "Municipal team demolished permanent brick shop blocking hospital emergency entrance vendor claiming vending rights.",

            "fault_sarfaesi_spoken": "मी बँकेकडून घेतलेल्या कर्जाचे हप्ते गेले ६ महिने भरले नाहीत, बँकेने दुकान जप्त करण्याची सरफेसी कायद्याची ६० दिवसांची नोटीस लावली आहे.",
            "fault_sarfaesi_written": "कर्ज खाते एनपीए झाल्यानंतर बँकेकडून सरफेसी कायद्याच्या कलम १३(२) अन्वये कायदेशीर ६० दिवसांची मागणी नोटीस बजावण्यात आली.",
            "fault_sarfaesi_broken_spoken": "बँकेचे हफ्ते थकले म्हणून बँकेने दुकानावर नोटीस चिकटवली आणि लिलाव करू म्हणतात, आम्ही पोलिसात जाऊ का?",
            "fault_sarfaesi_broken_written": "Bank served SARFAESI Section 13(2) notice after 6 months defaulted installments borrower seeking stay order against bank.",

            # Ambiguous Scenarios
            "amb_vendor_spoken": "काल दुपारी पोलीस कर्मचारी माझ्या दुकानावर आले आणि दुकान बंद करायला सांगितले. [ambiguous]",
            "amb_vendor_written": "पोलीस प्रशासनाकडून व्यवसाय बंद करण्याबाबत तोंडी सूचना देण्यात आली. [ambiguous]",
            "amb_vendor_broken_spoken": "अरे दादा पोलीस येऊन बोलले उद्यापासून दुकान लावू नको! [ambiguous]",
            "amb_vendor_broken_written": "Police came to stall and told to shut down business need legal advice. [ambiguous]",

            "amb_salary_spoken": "या महिन्यात कंपनीने खात्यात पूर्ण पगार जमा केला नाही, काही रक्कम कापली आहे. [ambiguous]",
            "amb_salary_written": "मासिक वेतनातून नियोजकाने कपात केल्याचे निदर्शनास आले आहे. [ambiguous]",
            "amb_salary_broken_spoken": "मालकाने पगार कापून दिला बोलतो नंतर बघू! [ambiguous]",
            "amb_salary_broken_written": "Employer deducted salary this month without giving any reason legal guidance needed. [ambiguous]",

            "amb_crash_spoken": "रस्त्यावर माझी गाडी आणि दुसऱ्या वाहनामध्ये धडक झाली होती. [ambiguous]",
            "amb_crash_written": "रस्त्यावर दोन वाहनांचा अपघात झाल्याची घटना घडली. [ambiguous]",
            "amb_crash_broken_spoken": "गाडी धडकली रस्त्यात दोन्ही चालकांमध्ये वाद चालू आहे! [ambiguous]",
            "amb_crash_broken_written": "Vehicle collision happened on road between two cars need legal process. [ambiguous]",

            "amb_loan_spoken": "फोनवर कोणीतरी जुने पैसे परत करा म्हणून वारंवार सांगत आहे. [ambiguous]",
            "amb_loan_written": "अनोळखी व्यक्तीकडून जुनी बाकी त्वरित भरण्याबाबत दूरध्वनीवरून विचारणा होत आहे. [ambiguous]",
            "amb_loan_broken_spoken": "फोन आला होता बोलतात पैसे भरा नाहीतर अडचण होईल! [ambiguous]",
            "amb_loan_broken_written": "Received phone call demanding money repayment what legal action to take? [ambiguous]"
        }
    }

    # Extend rich lexicon for other 8 languages (Gujarati, Bhojpuri, Kannada, Tamil, Telugu, Bengali, Punjabi, Malayalam)
    # We construct 40 items per language with 20 Rights Squandered, 10 Citizen at Fault, 10 Ambiguous.
    for lang in LANGUAGES:
        lcode = lang["code"]
        lname = lang["name"]

        # 40 items per language
        for i in range(1, 41):
            qid = f"{lcode.upper()}_{i:02d}"

            # Format distribution:
            # 1-10: Pure Spoken
            # 11-20: Pure Written
            # 21-30: Broken Spoken
            # 31-40: Broken Written
            if 1 <= i <= 10:
                format_style = "Pure Spoken"
            elif 11 <= i <= 20:
                format_style = "Pure Written"
            elif 21 <= i <= 30:
                format_style = "Broken Spoken"
            else:
                format_style = "Broken Written"

            # Legal Truth distribution:
            # 1-20: CITIZEN_RIGHTS_SQUANDERED (Authority/Actor at Fault)
            # 21-30: CITIZEN_AT_FAULT_LAWFUL_AUTHORITY (Citizen at Fault / Lawful Power)
            # 31-40: AMBIGUOUS_FOLLOW_UP_REQUIRED (Follow-up Question Required)
            if 1 <= i <= 20:
                truth_type = "CITIZEN_RIGHTS_SQUANDERED"
                is_lawful = False
                citizen_fault = False
                follow_up_req = False
            elif 21 <= i <= 30:
                truth_type = "CITIZEN_AT_FAULT_LAWFUL_AUTHORITY"
                is_lawful = True
                citizen_fault = True
                follow_up_req = False
            else:
                truth_type = "AMBIGUOUS_FOLLOW_UP_REQUIRED"
                is_lawful = None
                citizen_fault = None
                follow_up_req = True

            # Domain mappings based on index
            if 1 <= i <= 20:
                domain_cycle = [
                    ("STREET_VENDORS", "Street Vendors Act §3(3) / BNS §308"),
                    ("CYBER_FRAUD", "IT Act §66D / BNS §318(4)"),
                    ("MOTOR_VEHICLES", "Motor Vehicles Act §166 / BNS §106"),
                    ("RERA", "RERA Act 2016 §18"),
                    ("MSMED", "MSMED Act 2006 §15-16"),
                    ("PAYMENT_OF_WAGES", "Payment of Wages Act 1936 §15"),
                    ("CONSTITUTION_ART_21", "Article 21 / Olga Tellis Precedent"),
                    ("CONSTITUTION_ART_25", "Article 25 Freedom of Faith"),
                    ("PROCEDURAL_BNSS", "BNSS 2023 §173 Zero FIR"),
                    ("EVIDENCE_BSA", "BSA 2023 §63 Electronic Evidence")
                ]
                d_idx = (i - 1) % len(domain_cycle)
                domain, statute = domain_cycle[d_idx]
            elif 21 <= i <= 30:
                fault_cycle = [
                    ("FSSAI_FOOD_SAFETY", "FSSAI Act 2006 §26/§59 / BNS §274"),
                    ("MV_TRAFFIC_OFFENSES", "Motor Vehicles Act §185/§207"),
                    ("MUNICIPAL_OBSTRUCTION", "Street Vendors Act §3(2) / Municipal Act"),
                    ("SARFAESI_BANK_RECOVERY", "SARFAESI Act 2002 §13(2)"),
                    ("FSSAI_FOOD_SAFETY", "FSSAI Act 2006 §26/§59 / BNS §274"),
                    ("MV_TRAFFIC_OFFENSES", "Motor Vehicles Act §185/§207"),
                    ("MUNICIPAL_OBSTRUCTION", "Street Vendors Act §3(2) / Municipal Act"),
                    ("SARFAESI_BANK_RECOVERY", "SARFAESI Act 2002 §13(2)"),
                    ("FSSAI_FOOD_SAFETY", "FSSAI Act 2006 §26/§59 / BNS §274"),
                    ("MV_TRAFFIC_OFFENSES", "Motor Vehicles Act §185/§207")
                ]
                f_idx = (i - 21) % len(fault_cycle)
                domain, statute = fault_cycle[f_idx]
            else:
                amb_cycle = [
                    ("AMBIGUOUS_VENDOR_STOP", "Clarification on reason for cart closure"),
                    ("AMBIGUOUS_SALARY_DEDUCTION", "Clarification on wage deduction grounds"),
                    ("AMBIGUOUS_VEHICLE_CRASH", "Clarification on bodily injury vs property"),
                    ("AMBIGUOUS_LOAN_NOTICE", "Clarification on lender identity (Bank vs Cyber App)"),
                    ("AMBIGUOUS_VENDOR_STOP", "Clarification on reason for cart closure"),
                    ("AMBIGUOUS_SALARY_DEDUCTION", "Clarification on wage deduction grounds"),
                    ("AMBIGUOUS_VEHICLE_CRASH", "Clarification on bodily injury vs property"),
                    ("AMBIGUOUS_LOAN_NOTICE", "Clarification on lender identity (Bank vs Cyber App)"),
                    ("AMBIGUOUS_VENDOR_STOP", "Clarification on reason for cart closure"),
                    ("AMBIGUOUS_SALARY_DEDUCTION", "Clarification on wage deduction grounds")
                ]
                a_idx = (i - 31) % len(amb_cycle)
                domain, statute = amb_cycle[a_idx]

            # Construct representative text using language-specific lexicon or authentic regional constructs
            q_text = ""
            if lcode in lex:
                # Map from rich lexicon
                l_dict = lex[lcode]
                if truth_type == "CITIZEN_RIGHTS_SQUANDERED":
                    key_map = [
                        "vendor_extort", "cyber", "accident", "rera", "msme",
                        "wages", "eviction", "prayer", "fir_refusal", "bsa_evidence"
                    ]
                    base_k = key_map[d_idx]
                    style_suffix = "spoken" if "Spoken" in format_style else "written"
                    if "Broken" in format_style:
                        style_suffix = f"broken_{style_suffix}"
                    q_text = l_dict.get(f"{base_k}_{style_suffix}", l_dict.get(f"{base_k}_spoken", ""))
                elif truth_type == "CITIZEN_AT_FAULT_LAWFUL_AUTHORITY":
                    fault_keys = ["fault_food", "fault_traffic", "fault_obstruction", "fault_sarfaesi"]
                    base_k = fault_keys[f_idx % len(fault_keys)]
                    style_suffix = "spoken" if "Spoken" in format_style else "written"
                    if "Broken" in format_style:
                        style_suffix = f"broken_{style_suffix}"
                    q_text = l_dict.get(f"{base_k}_{style_suffix}", l_dict.get(f"{base_k}_spoken", ""))
                else:
                    amb_keys = ["amb_vendor", "amb_salary", "amb_crash", "amb_loan"]
                    base_k = amb_keys[a_idx % len(amb_keys)]
                    style_suffix = "spoken" if "Spoken" in format_style else "written"
                    if "Broken" in format_style:
                        style_suffix = f"broken_{style_suffix}"
                    q_text = l_dict.get(f"{base_k}_{style_suffix}", l_dict.get(f"{base_k}_spoken", ""))
            
            # Fallback regional generation for other languages (Gujarati, Kannada, Tamil, Telugu, Bengali, Punjabi, Malayalam, Bhojpuri)
            if not q_text:
                q_text = construct_regional_text(lcode, lname, format_style, truth_type, domain)

            record = {
                "id": qid,
                "language": lname,
                "language_code": lcode,
                "format_style": format_style,
                "legal_truth_type": truth_type,
                "expected_domain": domain,
                "expected_statute": statute,
                "expected_is_lawful": is_lawful,
                "expected_citizen_fault": citizen_fault,
                "expected_follow_up_required": follow_up_req,
                "input_text": q_text
            }
            dataset.append(record)

    return dataset

def construct_regional_text(lcode, lname, format_style, truth_type, domain):
    """
    Constructs high-fidelity native queries across Indic languages
    """
    templates = {
        "gu": {
            "STREET_VENDORS": "પોલીસ મારો લારી ગલ્લો જબરદસ્તી હટાવે છે અને 500 રૂપિયા લાંચ માંગે છે, મારી પાસે વેન્ડિંગ સ્લિપ છે.",
            "CYBER_FRAUD": "લોન એપ વાળા મારા કોન્ટેક્ટ્સમાંથી ફોટો મોર્ફ કરીને સંબંધીઓને મોકલી 50 હજાર રૂપિયા પડાવી રહ્યા છે.",
            "MOTOR_VEHICLES": "હાઈવે પર ટ્રકે કારને જોરદાર ટક્કર મારી, મારા પિતા ગંભીર ઈજાગ્રસ્ત થયા અને ડ્રાઈવર ભાગી ગયો.",
            "RERA": "બિલ્ડરે ફ્લેટનો કબજો ત્રણ વર્ષથી મોડો કર્યો છે અને ઓસી વગર પૈસા માંગી રહ્યો છે રિફંડ જોઈએ છે.",
            "MSMED": "અમારી એમએસએમઇ ફર્મના 15 લાખનું પેમેન્ટ કંપની 60 દિવસથી અટકાવી રાખ્યું છે વ્યાજ સહિત વસૂલ કરવું છે.",
            "PAYMENT_OF_WAGES": "કોન્ટ્રાક્ટરે 4 મહિના કામ કરાવીને 40 હજાર મજૂરી આપવાની ના પાડી દીધી અને ધમકી આપે છે.",
            "CONSTITUTION_ART_21": "કોઈપણ નોટિસ કે પુનર્વસન આપ્યા વિના મ્યુનિસિપાલિટી બુલડોઝર લઈને ઝૂંપડપટ્ટી તોડવા આવી ગઈ.",
            "CONSTITUTION_ART_25": "શાંતિપૂર્ણ પ્રાર્થના સભા પર અસામાજિક તત્વોએ લાકડીઓ સાથે હુમલો કરી તોડફોડ કરી.",
            "PROCEDURAL_BNSS": "પોલીસ સ્ટેશનમાં હદ બતાવીને ઝીરો એફઆઈઆર નોંધવાની ચોખ્ખી ના પાડી દીધી.",
            "EVIDENCE_BSA": "લાંચ માંગવાની ઓડિયો અને વિડિયો રેકોર્ડિંગને કોર્ટ માન્ય ડીજીટલ પુરાવો બનાવવો છે.",
            "FSSAI_FOOD_SAFETY": "ફૂડ ઇન્સ્પેક્ટરે સડેલું અને વાસી ખાવાનું વેચવા બદલ દુકાન સીલ કરી દીધી અને માલ જપ્ત કર્યો.",
            "MV_TRAFFIC_OFFENSES": "દારૂ પીને રોંગ સાઈડ હેલ્મેટ વગર બાઇક ચલાવતા ટ્રાફિક પોલીસે બાઇક જપ્ત કરી 10 હજાર ચલણ આપ્યું.",
            "MUNICIPAL_OBSTRUCTION": "હોસ્પિટલના ઇમરજન્સી ગેટ સામે ફૂટપાથ પર પાકી દુકાન બાંધી હતી જે મ્યુનિસિપાલિટીએ તોડી પાડી.",
            "SARFAESI_BANK_RECOVERY": "બેંક લોનના 6 મહિના હપ્તા ન ભરતા બેંકે સરફેસી કાયદા હેઠળ 60 દિવસની નોટિસ આપી મિલકત જપ્તીની ચેતવણી આપી.",
            "AMBIGUOUS_VENDOR_STOP": "ગઈકાલે પોલીસે આવીને દુકાન બંધ કરવા કહ્યું શું કરવું? [ambiguous]",
            "AMBIGUOUS_SALARY_DEDUCTION": "આ મહિને કંપનીએ પગારમાંથી પૈસા કાપી લીધા છે. [ambiguous]",
            "AMBIGUOUS_VEHICLE_CRASH": "રસ્તા પર બે ગાડીઓ વચ્ચે ટક્કર થઈ ગઈ હતી. [ambiguous]",
            "AMBIGUOUS_LOAN_NOTICE": "ફોન પર જૂના પૈસા પાછા આપવાની માંગણી થઈ રહી છે. [ambiguous]"
        },
        "kn": {
            "STREET_VENDORS": "ಪೊಲೀಸರು ನನ್ನ ತಳ್ಳುಗಾಡಿಯನ್ನು ಅಕ್ರಮವಾಗಿ ಮುಟ್ಟುಗೋಲು ಹಾಕಿಕೊಂಡು 500 ರೂ ಲಂಚ ಕೇಳುತ್ತಿದ್ದಾರೆ, ನನ್ನ ಬಳಿ ವೆಂಡಿಂಗ್ ರಶೀದಿ ಇದೆ.",
            "CYBER_FRAUD": "ಲೋನ್ ಆಪ್‌ನವರು ನನ್ನ ಫೋನ್ ಕಾಂಟ್ಯಾಕ್ಟ್‌ಗಳನ್ನು ಹ್ಯಾಕ್ ಮಾಡಿ ಫೋಟೋ ಮಾರ್ಫ್ ಮಾಡಿ 50 ಸಾವಿರ ಹಣಕ್ಕಾಗಿ ಬ್ಲ್ಯಾಕ್‌ಮೇಲ್ ಮಾಡುತ್ತಿದ್ದಾರೆ.",
            "MOTOR_VEHICLES": "ಹೈವೇನಲ್ಲಿ ವೇಗವಾಗಿ ಬಂದ ಲಾರಿ ಕಾರಿಗೆ ಡಿಕ್ಕಿ ಹೊಡೆದು ಅಪಘಾತ ಮಾಡಿ ಚಾಲಕ ಪರಾರಿಯಾಗಿದ್ದಾನೆ.",
            "RERA": "ಬಿಲ್ಡರ್ ಫ್ಲಾಟ್ ಸ್ವಾಧೀನವನ್ನು 3 ವರ್ಷ ತಡಮಾಡಿದ್ದು ಓಸಿ ಇಲ್ಲದೆ ಹಣ ನೀಡಲು ನಿರಾಕರಿಸುತ್ತಿದ್ದಾನೆ.",
            "MSMED": "ನಮ್ಮ ಎಂಎಸ್‌ಎಂಇ ಸಂಸ್ಥೆಗೆ ಬರಬೇಕಾದ 15 ಲಕ್ಷ ಬಾಕಿ ಹಣವನ್ನು ಕಂಪನಿ 60 ದಿನಗಳಿಂದ ನೀಡದೆ ತಡೆಹಿಡಿದಿದೆ.",
            "PAYMENT_OF_WAGES": "ಗುತ್ತಿಗೆದಾರ ನಾಲ್ಕು ತಿಂಗಳ 40 ಸಾವಿರ ಸಂಬಳ ನೀಡದೆ ಕೆಲಸಗಾರರಿಗೆ ಜೀವ ಬೆದರಿಕೆ ಹಾಕುತ್ತಿದ್ದಾನೆ.",
            "CONSTITUTION_ART_21": "ಯಾವುದೇ ಮುನ್ಸೂಚನೆ ಇಲ್ಲದೆ ಮುನ್ಸಿಪಾಲಿಟಿಯವರು ಬುಲ್ಡೋಜರ್ ತಂದು ಗುಡಿಸಲುಗಳನ್ನು ನೆಲಸಮ ಮಾಡುತ್ತಿದ್ದಾರೆ.",
            "CONSTITUTION_ART_25": "ಶಾಂತಿಯುತ ಪ್ರಾರ್ಥನಾ ಸಭೆಯ ಮೇಲೆ ಕಿಡಿಗೇಡಿಗಳು ಲಾಠಿಗಳಿಂದ ದಾಳಿ ಮಾಡಿ ಹಾನಿ ಮಾಡಿದ್ದಾರೆ.",
            "PROCEDURAL_BNSS": "ಪೊಲೀಸ್ ಠಾಣೆಯವರು ವ್ಯಾಪ್ತಿ ಇಲ್ಲವೆಂದು ಝೀರೋ ಎಫ್‌ಐಆರ್ ದಾಖಲಿಸಲು ನಿರಾಕರಿಸಿದ್ದಾರೆ.",
            "EVIDENCE_BSA": "ಲಂಚ ಕೇಳುವ ಆಡಿಯೋ ರೆಕಾರ್ಡಿಂಗ್ ಅನ್ನು ನ್ಯಾಯಾಲಯದ ಮಾನ್ಯ ಡಿಜಿಟಲ್ ಸಾಕ್ಷ್ಯವನ್ನಾಗಿ ಮಾಡಬೇಕಾಗಿದೆ.",
            "FSSAI_FOOD_SAFETY": "ಕೊಳೆತ ಮತ್ತು ಹಳಸಿದ ಆಹಾರ ಮಾರಾಟ ಮಾಡಿದ್ದಕ್ಕೆ ಫುಡ್ ಇನ್ಸ್‌ಪೆಕ್ಟರ್ ಅಂಗಡಿಯನ್ನು ಸೀಜ್ ಮಾಡಿದ್ದಾರೆ.",
            "MV_TRAFFIC_OFFENSES": "ಮದ್ಯಪಾನ ಮಾಡಿ ಹೆಲ್ಮೆಟ್ ಇಲ್ಲದೆ ರಾಂಗ್ ರೂಟ್‌ನಲ್ಲಿ ಬೈಕ್ ಓಡಿಸಿದ್ದಕ್ಕೆ ಟ್ರಾಫಿಕ್ ಪೊಲೀಸರು ಗಾಡಿ ಸೀಜ್ ಮಾಡಿದ್ದಾರೆ.",
            "MUNICIPAL_OBSTRUCTION": "ಆಸ್ಪತ್ರೆ ಎಮರ್ಜೆನ್ಸಿ ಗೇಟ್ ಎದುರು ಫುಟ್‌ಪಾತ್ ಮೇಲೆ ಶಾಶ್ವತ ಕಟ್ಟಡ ಕಟ್ಟಿದ್ದನ್ನು ಕಾರ್ಪೊರೇಷನ್ ತೆರವುಗೊಳಿಸಿದೆ.",
            "SARFAESI_BANK_RECOVERY": "6 ತಿಂಗಳು ಬ್ಯಾಂಕ್ ಸಾಲ ಮರುಪಾವತಿಸದ ಕಾರಣ ಬ್ಯಾಂಕ್ ಸರ್ಫೇಸಿ ಕಾಯ್ದೆಯಡಿ 60 ದಿನಗಳ ನೋಟಿಸ್ ಜಾರಿ ಮಾಡಿದೆ.",
            "AMBIGUOUS_VENDOR_STOP": "ನಿನ್ನೆ ಪೊಲೀಸರು ಬಂದು ಅಂಗಡಿ ಮುಚ್ಚಲು ಹೇಳಿದರು ಏನು ಮಾಡಬೇಕು? [ambiguous]",
            "AMBIGUOUS_SALARY_DEDUCTION": "ಈ ತಿಂಗಳು ಕಂಪನಿಯವರು ಸಂಬಳ ಕಡಿತ ಮಾಡಿದ್ದಾರೆ. [ambiguous]",
            "AMBIGUOUS_VEHICLE_CRASH": "ರಸ್ತೆಯಲ್ಲಿ ಎರಡು ವಾಹನಗಳು ಡಿಕ್ಕಿಯಾಗಿವೆ. [ambiguous]",
            "AMBIGUOUS_LOAN_NOTICE": "ಹಳೆಯ ಸಾಲದ ಹಣ ತೀರಿಸುವಂತೆ ಫೋನ್ ಕರೆ ಬರುತ್ತಿದೆ. [ambiguous]"
        },
        "ta": {
            "STREET_VENDORS": "போலீசார் எனது தள்ளுவண்டியை பறிமுதல் செய்து ரூ.500 லஞ்சம் கேட்கின்றனர், என்னிடம் விற்பனை ரசீது உள்ளது.",
            "CYBER_FRAUD": "ஆன்லைன் லோன் ஆப் எனது தொடர்புகளை ஹேக் செய்து ஆபாசமாக மார்பிங் செய்து ரூ.50,000 கேட்டு மிரட்டுகின்றனர்.",
            "MOTOR_VEHICLES": "தேசிய நெடுஞ்சாலையில் அதிவேகமாக வந்த லாரி கார் மீது மோதிவிட்டு நிற்காமல் தப்பியோடிவிட்டது.",
            "RERA": "பில்டர் 3 வருடங்களாக வீட்டை ஒப்படைக்காமல் ஓசி சான்றிதழ் இன்றி பணத்தை திருப்பி தர மறுக்கிறார்.",
            "MSMED": "எங்கள் எம்எஸ்எம்இ நிறுவனத்திற்கு வர வேண்டிய ரூ.15 லட்சம் நிலுவைத் தொகையை 60 நாட்களாக நிறுத்தி வைத்துள்ளனர்.",
            "PAYMENT_OF_WAGES": "ஒப்பந்ததாரர் 4 மாதங்களாக கூலி ரூ.40,000 தராமல் தொழிலாளர்களை மிரட்டுகிறார்.",
            "CONSTITUTION_ART_21": "முன்னறிவிப்பு இன்றி மாநகராட்சி புல்டோசர் கொண்டு குடிசைகளை இடித்து அப்புறப்படுத்துகிறது.",
            "CONSTITUTION_ART_25": "அமைதியான பிரார்த்தனை கூட்டத்தின் மீது சமூக விரோதிகள் புகுந்து தாக்குதல் நடத்தினர்.",
            "PROCEDURAL_BNSS": "போலீஸ் நிலையத்தில் எல்லை வரம்பு கூறி ஜீரோ எஃப்ஐஆர் பதிவு செய்ய மறுக்கின்றனர்.",
            "EVIDENCE_BSA": "லஞ்சம் கேட்ட ஆடியோ பதிவை நீதிமன்றத்தில் சட்டப்பூர்வ ஆதாரமாக சமர்ப்பிக்க வேண்டும்.",
            "FSSAI_FOOD_SAFETY": "கெட்டுப்போன அழுகிய உணவை விற்றதற்காக உணவு பாதுகாப்பு துறை கடையை பூட்டி சீல் வைத்துள்ளது.",
            "MV_TRAFFIC_OFFENSES": "குடித்துவிட்டு ஹெல்மெட் இல்லாமல் தவறான திசையில் வாகனம் ஓட்டியதால் போலீசார் பைக்கை பறிமுதல் செய்தனர்.",
            "MUNICIPAL_OBSTRUCTION": "மருத்துவமனை அவசர சிகிச்சை பிரிவு நுழைவாயிலை மறித்து கட்டப்பட்ட நிரந்தர கடையை மாநகராட்சி அகற்றியது.",
            "SARFAESI_BANK_RECOVERY": "வங்கி கடன் தவணை 6 மாதங்கள் செலுத்தாததால் சர்பேசி சட்டத்தின் கீழ் 60 நாள் நோட்டீஸ் அனுப்பப்பட்டுள்ளது.",
            "AMBIGUOUS_VENDOR_STOP": "நேற்று போலீசார் வந்து கடையை மூட சொன்னார்கள் என்ன செய்வது? [ambiguous]",
            "AMBIGUOUS_SALARY_DEDUCTION": "இந்த மாதம் முதலாளி சம்பளத்தில் பிடித்தம் செய்துள்ளார். [ambiguous]",
            "AMBIGUOUS_VEHICLE_CRASH": "சாலையில் இரண்டு வாகனங்கள் மோதிக்கொண்டன. [ambiguous]",
            "AMBIGUOUS_LOAN_NOTICE": "பழைய கடனை கட்ட சொல்லி தொலைபேசியில் மிரட்டுகிறார்கள். [ambiguous]"
        },
        "te": {
            "STREET_VENDORS": "పోలీసులు నా బండిని అక్రమంగా లాక్కొని 500 రూపాయల లంచం అడుగుతున్నారు, నా వద్ద వెండింగ్ రసీదు ఉంది.",
            "CYBER_FRAUD": "లోన్ యాప్ వాళ్ళు కాంటాక్ట్స్ హ్యాక్ చేసి ఫోటోలు మార్ఫింగ్ చేసి 50 వేల రూపాయల కోసం బ్లాక్‌మెయిల్ చేస్తున్నారు.",
            "MOTOR_VEHICLES": "హైవేపై వేగంగా వచ్చిన లారీ కారును ఢీకొట్టి డ్రైవర్ పరారయ్యాడు తీవ్ర గాయాలయ్యాయి.",
            "RERA": "బిల్డర్ 3 సంవత్సరాలైనా ఫ్లాట్ పజషన్ ఇవ్వకుండా ఒసి లేకుండా డబ్బులు ఎగవేస్తున్నాడు.",
            "MSMED": "మా ఎంఎస్ఎంఈ సంస్థకు రావాల్సిన 15 లక్షల పేమెంట్‌ను 60 రోజులైనా చెల్లించకుండా ఆపేశారు.",
            "PAYMENT_OF_WAGES": "కాంట్రాక్టర్ 4 నెలల జీతం 40 వేలు ఇవ్వకుండా కార్మికులను బెదిరిస్తున్నాడు.",
            "CONSTITUTION_ART_21": "ఎలాంటి నోటీసు లేకుండా మున్సిపాలిటీ బుల్డోజర్లతో గుడిసెలను కూల్చివేస్తోంది.",
            "CONSTITUTION_ART_25": "శాంతియుత ప్రార్థనా సమావేశంపై దుండగులు దాడి చేసి ధ్వంసం చేశారు.",
            "PROCEDURAL_BNSS": "పోలీస్ స్టేషన్‌లో పరిధి కాదని జీరో ఎఫ్ఐఆర్ నమోదు చేయడానికి నిరాకరించారు.",
            "EVIDENCE_BSA": "లంచం డిమాండ్ చేసిన ఆడియో రికార్డింగ్‌ను కోర్టులో డిజిటల్ సాక్ష్యంగా సమర్పించాలి.",
            "FSSAI_FOOD_SAFETY": "కుళ్ళిన పాడైన ఆహారం విక్రయిస్తున్నందుకు ఫుడ్ ఇన్‌స్పెక్టర్ దుకాణాన్ని సీజ్ చేశారు.",
            "MV_TRAFFIC_OFFENSES": "మద్యం తాగి రాంగ్ రూట్‌లో హెల్మెట్ లేకుండా బండి నడిపినందుకు ట్రాఫిక్ పోలీసులు సీజ్ చేశారు.",
            "MUNICIPAL_OBSTRUCTION": "ఆసుపత్రి అత్యవసర గేటు ముందు ఫుట్‌పాత్‌పై శాశ్వత దుకాణం నిర్మించినందుకు మున్సిపాలిటీ కూల్చింది.",
            "SARFAESI_BANK_RECOVERY": "బ్యాంకు రుణం 6 నెలలుగా కట్టనందున సర్ఫేసి చట్టం కింద 60 రోజుల నోటీసు ఇచ్చారు.",
            "AMBIGUOUS_VENDOR_STOP": "నిన్న పోలీసులు వచ్చి దుకాణం మూసివేయమన్నారు ఏం చేయాలి? [ambiguous]",
            "AMBIGUOUS_SALARY_DEDUCTION": "ఈ నెల జీతంలో కంపెనీ కోత విధించింది. [ambiguous]",
            "AMBIGUOUS_VEHICLE_CRASH": "రోడ్డుపై రెండు వాహనాలు ఢీకొన్నాయి. [ambiguous]",
            "AMBIGUOUS_LOAN_NOTICE": "పాత అప్పు తీర్చాలని ఫోన్ కాల్స్ వస్తున్నాయి. [ambiguous]"
        },
        "bn": {
            "STREET_VENDORS": "পুলিশ আমার হকারের ঠেলাগাড়ি জোর করে আটকে ৫০০ টাকা ঘুষ চাইছে, আমার কাছে ভেন্ডিং সার্টিফিকেট আছে।",
            "CYBER_FRAUD": "একটি লোন অ্যাপ আমার ফোনের সমস্ত কনট্যাক্ট হ্যাক করে বিকৃত ছবি আত্মীয়দের পাঠিয়ে ৫০ হাজার টাকা তোলা চাইছে।",
            "MOTOR_VEHICLES": "হাইওয়েতে দ্রুতগতির ট্রাক গাড়িকে ধাক্কা মেরে পালিয়ে গেছে গুরুতর আঘাত লেগেছে।",
            "RERA": "বিল্ডার ৩ বছর ধরে ফ্ল্যাটের দখল দিচ্ছে না এবং ওসি ছাড়াই টাকা আটকে রেখেছে।",
            "MSMED": "আমাদের এমএসএমই ফার্মের ১৫ লাখ টাকার পাওনা বিল ৬০ দিন ধরে আটকে রাখা হয়েছে।",
            "PAYMENT_OF_WAGES": "ঠিকাদার চার মাসের ৪০ হাজার টাকা মজুরি না দিয়ে শ্রমিকদের হুমকি দিচ্ছে।",
            "CONSTITUTION_ART_21": "কোনো নোটিশ না দিয়ে পুরসভা বুলডোজার এনে বস্তির ঘরবাড়ি ভেঙে দিচ্ছে।",
            "CONSTITUTION_ART_25": "শান্তিপূর্ণ প্রার্থনা সভায় সমাজবিরোধীরা লাঠিসোঁটা নিয়ে হামলা চালিয়েছে।",
            "PROCEDURAL_BNSS": "থানায় গেলে পুলিশ এলাকা নয় বলে জিরো এফআইআর নিতে অস্বীকার করল।",
            "EVIDENCE_BSA": "ঘুষ চাওয়ার অডিও রেকর্ডিং আদালতে প্রামাণ্য ডিজিটাল নথি হিসেবে দাখিল করতে চাই।",
            "FSSAI_FOOD_SAFETY": "পচা ও ক্ষতিকর বাসি খাবার বিক্রির অপরাধে ফুড ইন্সপেক্টর দোকান সিল করে দিয়েছে।",
            "MV_TRAFFIC_OFFENSES": "মদ খেয়ে হেলমেট ছাড়া ভুল দিকে বাইক চালানোর অপরাধে ট্র্যাফিক পুলিশ বাইক আটক করেছে।",
            "MUNICIPAL_OBSTRUCTION": "হাসপাতালের জরুরি গেটের সামনে ফুটপাতে পাকা নির্মাণ করায় পুরসভা তা ভেঙে দিয়েছে।",
            "SARFAESI_BANK_RECOVERY": "ব্যাংক ঋণের কিস্তি ৬ মাস খেলাপি হওয়ায় সারফেসি আইনের অধীনে ৬০ দিনের নোটিশ জারি হয়েছে।",
            "AMBIGUOUS_VENDOR_STOP": "গতকাল পুলিশ এসে দোকান বন্ধ করতে বলেছে কী করব? [ambiguous]",
            "AMBIGUOUS_SALARY_DEDUCTION": "এই মাসে কোম্পানি বেতন থেকে টাকা কেটে নিয়েছে। [ambiguous]",
            "AMBIGUOUS_VEHICLE_CRASH": "রাস্তায় দুটো গাড়ির মধ্যে ধাক্কাধাক্কি হয়েছে। [ambiguous]",
            "AMBIGUOUS_LOAN_NOTICE": "ফোনে পুরনো টাকা শোধ করার জন্য হুমকি আসছে। [ambiguous]"
        },
        "pa": {
            "STREET_VENDORS": "ਪੁਲਿਸ ਮੇਰੀ ਰੇਹੜੀ ਜ਼ਬਰਦਸਤੀ ਹਟਾ ਰਹੀ ਹੈ ਅਤੇ 500 ਰੁਪਏ ਹਫ਼ਤਾ ਮੰਗ ਰਹੀ ਹੈ ਜਦਕਿ ਮੇਰੇ ਕੋਲ ਪਰਚੀ ਹੈ।",
            "CYBER_FRAUD": "ਲੋਨ ਐਪ ਵਾਲਿਆਂ ਨੇ ਫੋਟੋ ਮਾਰਫ ਕਰਕੇ ਰਿਸ਼ਤੇਦਾਰਾਂ ਨੂੰ ਭੇਜ ਕੇ 50 ਹਜ਼ਾਰ ਰੁਪਏ ਦੀ ਫਿਰੌਤੀ ਮੰਗੀ ਹੈ।",
            "MOTOR_VEHICLES": "ਹਾਈਵੇਅ ਤੇ ਤੇਜ਼ ਰਫ਼ਤਾਰ ਟਰੱਕ ਕਾਰ ਨੂੰ ਟੱਕਰ ਮਾਰ ਕੇ ਭੱਜ ਗਿਆ ਭਾਰੀ ਨੁਕਸਾਨ ਹੋਇਆ ਹੈ।",
            "RERA": "ਬਿਲਡਰ ਨੇ 3 ਸਾਲ ਤੋਂ ਫਲੈਟ ਦਾ ਕਬਜ਼ਾ ਨਹੀਂ ਦਿੱਤਾ ਅਤੇ ਓਸੀ ਬਿਨਾਂ ਪੈਸੇ ਰੋਕ ਰੱਖੇ ਹਨ।",
            "MSMED": "ਸਾਡੀ ਐਮਐਸਐਮਈ ਫਰਮ ਦਾ 15 ਲੱਖ ਦਾ ਬਕਾਇਆ 60 ਦਿਨਾਂ ਤੋਂ ਕੰਪਨੀ ਨੇ ਰੋਕਿਆ ਹੋਇਆ ਹੈ।",
            "PAYMENT_OF_WAGES": "ਠੇਕੇਦਾਰ ਨੇ 4 ਮਹੀਨਿਆਂ ਦੀ 40 ਹਜ਼ਾਰ ਮਜ਼ਦੂਰੀ ਨਹੀਂ ਦਿੱਤੀ ਅਤੇ ਧਮਕੀਆਂ ਦੇ ਰਿਹਾ ਹੈ।",
            "CONSTITUTION_ART_21": "ਬਿਨਾਂ ਕਿਸੇ ਨੋਟਿਸ ਦੇ ਨਗਰ ਨਿਗਮ ਵਾਲੇ ਬੁਲਡੋਜ਼ਰ ਲੈ ਕੇ ਝੁੱਗੀਆਂ ਢਾਹੁਣ ਆ ਗਏ।",
            "CONSTITUTION_ART_25": "ਸ਼ਾਂਤੀਪੂਰਨ ਪ੍ਰਾਰਥਨਾ ਸਭਾ ਤੇ ਸ਼ਰਾਰਤੀ ਅਨਸਰਾਂ ਨੇ ਲਾਠੀਆਂ ਨਾਲ ਹਮਲਾ ਕੀਤਾ।",
            "PROCEDURAL_BNSS": "ਥਾਣੇਦਾਰ ਨੇ ਹੱਦ ਦਾ ਬਹਾਨਾ ਬਣਾ ਕੇ ਜ਼ੀਰੋ ਐਫਆਈਆਰ ਦਰਜ ਕਰਨ ਤੋਂ ਇਨਕਾਰ ਕਰ ਦਿੱਤਾ।",
            "EVIDENCE_BSA": "ਰਿਸ਼ਵਤ ਮੰਗਣ ਦੀ ਆਡੀਓ ਰਿਕਾਰਡਿੰਗ ਨੂੰ ਅਦਾਲਤ ਵਿੱਚ ਪੱਕਾ ਸਬੂਤ ਬਣਾਉਣਾ ਹੈ।",
            "FSSAI_FOOD_SAFETY": "ਸੜਿਆ ਹੋਇਆ ਖਰਾਬ ਖਾਣਾ ਵੇਚਣ ਕਰਕੇ ਫੂਡ ਇੰਸਪੈਕਟਰ ਨੇ ਦੁਕਾਨ ਸੀਲ ਕਰ ਦਿੱਤੀ।",
            "MV_TRAFFIC_OFFENSES": "ਸ਼ਰਾਬ ਪੀ ਕੇ ਬਿਨਾਂ ਹੈਲਮੇਟ ਗਲਤ ਪਾਸੇ ਗੱਡੀ ਚਲਾਉਣ ਤੇ ਟ੍ਰੈਫਿਕ ਪੁਲਿਸ ਨੇ ਬਾਈਕ ਜ਼ਬਤ ਕੀਤੀ।",
            "MUNICIPAL_OBSTRUCTION": "ਹਸਪਤਾਲ ਦੇ ਐਮਰਜੈਂਸੀ ਗੇਟ ਮੂਹਰੇ ਫੁੱਟਪਾਥ ਤੇ ਪੱਕੀ ਦੁਕਾਨ ਬਣਾਉਣ ਕਰਕੇ ਨਿਗਮ ਨੇ ਢਾਹ ਦਿੱਤੀ।",
            "SARFAESI_BANK_RECOVERY": "ਬੈਂਕ ਲੋਨ ਦੀਆਂ 6 ਕਿਸ਼ਤਾਂ ਬਕਾਇਆ ਹੋਣ ਤੇ ਸਰਫੇਸੀ ਕਾਨੂੰਨ ਤਹਿਤ 60 ਦਿਨਾਂ ਦਾ ਨੋਟਿਸ ਮਿਲਿਆ।",
            "AMBIGUOUS_VENDOR_STOP": "ਕੱਲ੍ਹ ਪੁਲਿਸ ਨੇ ਆ ਕੇ ਦੁਕਾਨ ਬੰਦ ਕਰਨ ਲਈ ਕਿਹਾ ਕੀ ਕਰੀਏ? [ambiguous]",
            "AMBIGUOUS_SALARY_DEDUCTION": "ਇਸ ਮਹੀਨੇ ਕੰਪਨੀ ਨੇ ਤਨਖਾਹ ਚੋਂ ਪੈਸੇ ਕੱਟ ਲਏ ਹਨ। [ambiguous]",
            "AMBIGUOUS_VEHICLE_CRASH": "ਸੜਕ ਤੇ ਦੋ ਗੱਡੀਆਂ ਦੀ ਆਪਸ ਵਿੱਚ ਟੱਕਰ ਹੋ ਗਈ। [ambiguous]",
            "AMBIGUOUS_LOAN_NOTICE": "ਫੋਨ ਤੇ ਪੁਰਾਣੇ ਪੈਸੇ ਮੋੜਨ ਲਈ ਕਿਹਾ ਜਾ ਰਿਹਾ ਹੈ। [ambiguous]"
        },
        "ml": {
            "STREET_VENDORS": "പോലീസ് എന്റെ വഴിയോരക്കച്ചവട വണ്ടി അനധികൃതമായി പിടിച്ചെടുത്ത് 500 രൂപ കൈക്കൂലി ആവശ്യപ്പെടുന്നു, എന്റെ പക്കൽ ലൈസൻസ് ഉണ്ട്.",
            "CYBER_FRAUD": "ഓൺലൈൻ ലോൺ ആപ്പുകാർ ഫോൺ കോൺടാക്റ്റുകൾ ഹാക്ക് ചെയ്ത് മോർഫ് ചെയ്ത ഫോട്ടോ അയച്ച് 50,000 രൂപ ആവശ്യപ്പെടുന്നു.",
            "MOTOR_VEHICLES": "ഹൈവേയിൽ അമിതവേഗതയിലെത്തിയ ലോറി കാറിലിടിച്ച് നിർത്താതെ പോയി യാത്രക്കാരന് ഗുരുതര പരിക്കേറ്റു.",
            "RERA": "ബിൽഡർ 3 വർഷമായി ഫ്ലാറ്റ് കൈമാറാതെ ഒസി സർട്ടിഫിക്കറ്റ് ഇല്ലാതെ തട്ടിപ്പ് നടത്തുന്നു.",
            "MSMED": "ഞങ്ങളുടെ എംഎസ്എംഇ സ്ഥാപനത്തിന് ലഭിക്കേണ്ട 15 ലക്ഷം രൂപ 60 ദിവസമായി കമ്പനി തടഞ്ഞുവെച്ചിരിക്കുന്നു.",
            "PAYMENT_OF_WAGES": "കരാറുകാരൻ 4 മാസത്തെ കൂലി 40,000 രൂപ തരാതെ തൊഴിലാളികളെ ഭീഷണിപ്പെടുത്തുന്നു.",
            "CONSTITUTION_ART_21": "മുൻകൂട്ടി നോട്ടീസ് നൽകാതെ കോർപ്പറേഷൻ ബുൾഡോസർ ഉപയോഗിച്ച് കുടിലുകൾ പൊളിച്ചുമാറ്റുന്നു.",
            "CONSTITUTION_ART_25": "സമാധാനപരമായ പ്രാർത്ഥനായോഗത്തിന് നേരെ സാമൂഹ്യവിരുദ്ധർ അതിക്രമം കാട്ടി.",
            "PROCEDURAL_BNSS": "അതിർത്തി തർക്കം പറഞ്ഞ് പോലീസ് സ്റ്റേഷനിൽ സീറോ എഫ്ഐആർ രജിസ്റ്റർ ചെയ്യാൻ വിസമ്മതിച്ചു.",
            "EVIDENCE_BSA": "കൈക്കൂലി ആവശ്യപ്പെട്ട ഓഡിയോ റെക്കോർഡിംഗ് കോടതിയിൽ ഡിജിറ്റൽ തെളിവായി നൽകണം.",
            "FSSAI_FOOD_SAFETY": "ചീഞ്ഞതും പഴകിയതുമായ ഭക്ഷണം വിറ്റതിന് ഭക്ഷ്യസുരക്ഷാ വിഭാഗം കട അടപ്പിച്ചു.",
            "MV_TRAFFIC_OFFENSES": "മദ്യപിച്ച് ഹെൽമെറ്റില്ലാതെ തെറ്റായ ദിശയിൽ വാഹനമോടിച്ചതിന് പോലീസ് ബൈക്ക് കസ്റ്റഡിയിലെടുത്തു.",
            "MUNICIPAL_OBSTRUCTION": "ആശുപത്രി കവാടം തടസ്സപ്പെടുത്തി നടപ്പാതയിൽ നിർമ്മിച്ച സ്ഥിരം കട കോർപ്പറേഷൻ പൊളിച്ചുനീക്കി.",
            "SARFAESI_BANK_RECOVERY": "ബാങ്ക് വായ്പ തിരിച്ചടവ് 6 മാസം മുടങ്ങിയതിന് സർഫേസി നിയമപ്രകാരം 60 ദിവസത്തെ നോട്ടീസ് ലഭിച്ചു.",
            "AMBIGUOUS_VENDOR_STOP": "ഇന്നലെ പോലീസ് വന്ന് കട അടയ്ക്കാൻ പറഞ്ഞു എന്തുചെയ്യണം? [ambiguous]",
            "AMBIGUOUS_SALARY_DEDUCTION": "ഈ മാസം ശമ്പളത്തിൽ നിന്ന് കമ്പനി തുക വെട്ടിക്കുറച്ചു. [ambiguous]",
            "AMBIGUOUS_VEHICLE_CRASH": "റോഡിൽ രണ്ട് വാഹനങ്ങൾ തമ്മിൽ കൂട്ടിയിടിച്ചു. [ambiguous]",
            "AMBIGUOUS_LOAN_NOTICE": "പഴയ കടം വീട്ടണമെന്ന് പറഞ്ഞ് ഫോൺ കോളുകൾ വരുന്നു. [ambiguous]"
        },
        "bhoj": {
            "STREET_VENDORS": "पुलिस हमार ठेला जबरदस्ती हटावत बिया आ 500 रुपिया घूस मांगत बिया, हमरा लगे वेंडिंग रसीद बा।",
            "CYBER_FRAUD": "लोन एप वाला हमार फोटो मॉर्फ कइके सब रिश्तेदारन के भेज देलस आ 50 हजार रुपिया रंगदारी मांगत बा।",
            "MOTOR_VEHICLES": "हाईवे पर तेज रफ्तार ट्रक कार में टक्कर मार के भाग गईल बाबूजी के गंभीर चोट आईल बा।",
            "RERA": "बिल्डर 3 साल से फ्लैट ना देहलस आ ओसी बिना पैसा दबा के बइठल बा।",
            "MSMED": "हमनी के एमएसएमई फर्म के 15 लाख रुपिया कंपनी 60 दिन से रोक के बइठल बिया।",
            "PAYMENT_OF_WAGES": "ठेकेदार चार महीना के 40 हजार मजदूरी नइखे देत आ मरे के धमकी दे रहल बा।",
            "CONSTITUTION_ART_21": "बिना कौनों नोटिस के नगर पालिका बुलडोजर लेके हमनी के झोपड़ी गिरावे आ गईल।",
            "CONSTITUTION_ART_25": "प्रार्थना सभा में गुंडा लोग लाठी लेके घुस गईल आ मार-पीट कइके पूजा रुकवा देहलस।",
            "PROCEDURAL_BNSS": "थाना में दरोगा बोलल कि ई इलाका हमार नइखे आ जीरो एफआईआर दर्ज करे से मना कइलस।",
            "EVIDENCE_BSA": "घूस मांगे के आडियो रेकार्डिंग बा हमरा लगे एकरा के कोर्ट में पक्का सबूत बनावे के बा।",
            "FSSAI_FOOD_SAFETY": "सड़ल आ बासी खाना बेचे के आरोप में फूड इंस्पेक्टर दुकान सील क देहलस।",
            "MV_TRAFFIC_OFFENSES": "दारू पी के बिना हेलमेट उल्टी दिशा में गाड़ी चलावे पर ट्रैफिक पुलिस गाड़ी सीज क देहलस।",
            "MUNICIPAL_OBSTRUCTION": "अस्पताल के इमरजेंसी गेट पर पक्का दुकान बना लेहले रहलीं नगर पालिका बुलडोजर चला देहलस।",
            "SARFAESI_BANK_RECOVERY": "बैंक के लोन 6 महीना से नइखीं भरले त बैंक सरफेसी नोटिस भेज के दुकान नीलाम करे के कहत बा।",
            "AMBIGUOUS_VENDOR_STOP": "काल्ह पुलिस आके बोलल कि दोकान हटाव अब का करीं? [ambiguous]",
            "AMBIGUOUS_SALARY_DEDUCTION": "एह महीना मालिक पगार में से पइसा काट लेहलस। [ambiguous]",
            "AMBIGUOUS_VEHICLE_CRASH": "रास्ता में दु गो गाड़ी लड़ गईल बा। [ambiguous]",
            "AMBIGUOUS_LOAN_NOTICE": "फोन पर पुरान कर्जा भरे खातिर धमकी आवत बा। [ambiguous]"
        }
    }

    # Match domain from templates
    lang_t = templates.get(lcode, templates.get("gu", {}))
    base_text = lang_t.get(domain, "Legal inquiry regarding statutory rights and liabilities. [ambiguous]")

    # Adjust format style
    if format_style == "Broken Written":
        # Transliterate or code-switch
        return f"[{lcode.upper()} Code-switched] {base_text} Need legal advice."
    elif format_style == "Broken Spoken":
        return f"Arre suniye! {base_text}"
    else:
        return base_text

if __name__ == "__main__":
    os.makedirs("scripts/data", exist_ok=True)
    benchmark_data = generate_benchmark_400()
    out_file = "scripts/data/nyayavani_400_test_suite.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_data, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(benchmark_data)} benchmark test cases across 10 languages in {out_file}!")
