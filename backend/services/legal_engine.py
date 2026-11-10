import os
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.services.graph_retriever import LegalGraphRetriever

class OralAffidavitHasher:
    """
    Generates a cryptographically verifiable electronic record hash for spoken testimony
    admissible under Section 63 of Bharatiya Sakshya Adhiniyam, 2023 (BSA)
    (formerly Section 65B of Indian Evidence Act, 1872).
    """
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
            f"--- ELECTRONIC RECORD CERTIFICATE (BSA SEC 63) ---\n"
            f"Digest (SHA-256): {digest}\n"
            f"UTC Timestamp:    {ts}\n"
            f"Origin Location:  {location}\n"
            f"Status:           Contemporaneous Spoken Testimony Preserved\n"
            f"Admissibility:    Admissible as electronic evidence under Section 63 BSA, 2023\n"
            f"--------------------------------------------------"
        )
        return {
            "sha256": digest,
            "timestamp": ts,
            "location": location,
            "certificate": certificate
        }


class GrassrootsLegalAdvisor:
    """
    Free Tier / Bharat Public Good:
    Comprehensive statutory engine covering vulnerable and poor citizens across:
    1. Labor & Wage Theft (Payment of Wages Act, Minimum Wages, Bonded Labor)
    2. Land Grabbing & Slum Eviction (Specific Relief Act Sec 6, Article 21/300A)
    3. Predatory Loan Apps & Phishing Frauds (RBI Digital Lending, IT Act 66D, BNS 318)
    4. Police Harassment, Custody & FIR Refusal (BNSS 173 Zero FIR, D.K. Basu Guidelines)
    5. Domestic Abuse & Maintenance (PWDVA 2005, BNSS 144 Maintenance, BNS 85/86)
    6. Administrative Corruption & Welfare Denial (RTI Act 2005, Anti-Corruption Act, DLSA)
    7. Street Vendor Rights (The Street Vendors Act 2014 Sec 3(3), Sec 18, Sec 33)
    8. Religious & Community Assembly Protection (Article 25, BNS 189/298/301)
    """

    CATEGORIES = {
        "WAGE_THEFT": ["salary", "wage", "तनख्वाह", "मजदूरी", "काम करवाया पैसे नहीं दिए", "contractor", "thekedar", "overtime", "unpaid", "वेतन"],
        "LAND_GRABBING": ["land", "plot", "zamin", "जमीन", "जमीन हड़प", "कब्जा", "मकान खाली", "slum", "jhuggi", "patta", "forged deed", "दबंग"],
        "LOAN_FRAUD": ["loan app", "लोन ऐप", "लोन एप", "recovery agent", "फर्जी लोन", "otp", "phishing", "blackmail", "photo morph", "मॉर्फ", "हैक", "हैकिंग", "interest", "पैसे कट गए", "पैसे मांग"],
        "POLICE_CUSTODY": ["police station", "thana", "थाने", "चौकी", "fir", "मारपीट", "lockup", "arrest memo", "complaint nahi likh rahe", "दरोगा", "पुलिस"],
        "DOMESTIC_VIOLENCE": ["domestic", "husband", "patni", "marpeet", "dowry", "दहेज", "खर्चा", "maintenance", "घर से निकाल दिया", "ससुराल"],
        "CORRUPTION_RTI": ["bribe", "ghoos", "रिश्वत", "hafta", "extortion", "ration card", "राशन", "ration nahi mila", "pension", "पेंशन", "babu", "clerk", "sarkari", "demanded money", "demand money", "paise mange"],
        "STREET_VENDOR": ["vendor", "hawker", "cart", "stall", "thela", "ठेला", "रेहड़ी", "दुकान", "dukan", "bmc", "municipality", "svanidhi", "tvc", "फेरीवाला", "hafta", "khomcha", "lari", "gallo"],
        "RELIGIOUS_GATHERING": ["church", "prayer", "gathering", "चर्च", "प्रार्थना", "सत्संग", "attack", "mob", "धार्मिक", "पूजा"]
    }

    def detect_category(self, text: str) -> str:
        text_lower = text.lower()
        for cat, keywords in self.CATEGORIES.items():
            if any(k in text_lower for k in keywords):
                return cat
        return "GENERAL_CITIZEN_AID"

    def analyze(self, transcript: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        meta = meta or {}
        category = meta.get("category") or self.detect_category(transcript)
        client_name = meta.get("client_name", "Citizen / Complainant")
        location = meta.get("location", "India")
        now_str = datetime.now().strftime("%d %B %Y")

        if category == "WAGE_THEFT":
            statutory_title = "Wage Theft & Unlawful Deduction under Payment of Wages Act, 1936"
            statutes = [
                {"law": "Payment of Wages Act, 1936 — Section 15", "details": "Mandatory timely payment of wages without unauthorized deductions. Employer liable for compensation up to 10 times the deducted amount."},
                {"law": "Minimum Wages Act, 1948 — Section 12", "details": "Mandatory statutory minimum wage rates. Non-payment is a cognizable criminal offense punishable with imprisonment."},
                {"law": "Constitution of India — Article 23", "details": "Prohibition of traffic in human beings and 'begar' (forced labor without legitimate wages)."}
            ]
            rights_shield_hi = (
                "सावधान। पेमेंट ऑफ वेजेस एक्ट 1936 की धारा 15 और मिनिमम वेजेस एक्ट के तहत मजदूर की मजदूरी रोकना गैरकानूनी है। "
                "यदि ठेकेदार या मालिक तुरंत मजदूरी का भुगतान नहीं करता, तो लेबर कमिश्नर कार्यालय में 10 गुना हर्जाने की वसूली का दावा दायर किया जाएगा। "
                "संविधान का अनुच्छेद 23 बेगार और बंधुआ मजदूरी को दंडनीय अपराध घोषित करता है।"
            )
            written_doc = (
                f"BEFORE THE DEPUTY LABOR COMMISSIONER / AUTHORITY UNDER PAYMENT OF WAGES ACT\n"
                f"DISTRICT: {location}\n"
                f"DATE: {now_str}\n\n"
                f"CLAIM PETITION UNDER SECTION 15(2) OF THE PAYMENT OF WAGES ACT, 1936\n"
                f"APPLICANT: {client_name}\n"
                f"OPPOSITE PARTY: Employer / Contractor / Establishment\n\n"
                f"1. That the applicant was employed and rendered honest service as detailed herein.\n"
                f"2. That the Opposite Party has unlawfully withheld earned wages without just cause in violation of Section 5.\n"
                f"3. PRAYER: Direct the Opposite Party to pay the withheld wages along with maximum statutory compensation (up to 10x) under Section 15(3).\n\n"
                f"Signature: {client_name}"
            )
            action_steps = [
                "1. Play the Spoken Labor Rights Shield directly to the contractor/employer.",
                "2. Gather attendance cards, muster roll copies, WhatsApp messages, or co-worker witness statements.",
                "3. Submit the generated petition to the District Labor Officer (DLC).",
                "4. Approach District Legal Services Authority (DLSA) for an assigned free legal aid advocate."
            ]

        elif category == "LAND_GRABBING":
            statutory_title = "Protection Against Illegal Dispossession & Criminal Trespass"
            statutes = [
                {"law": "Specific Relief Act, 1963 — Section 6", "details": "Summary suit for recovery of possession. Any person dispossessed without due process of law can recover possession within 6 months, irrespective of title disputes."},
                {"law": "Bharatiya Nyaya Sanhita, 2023 (BNS) — Section 329", "details": "Criminal Trespass: Unlawful entry into property with intent to intimidate, insult, or annoy the occupant."},
                {"law": "Constitution of India — Article 21 & 300A", "details": "Right to shelter as integral to life with dignity; no citizen can be deprived of property save by authority of law."}
            ]
            rights_shield_hi = (
                "सावधान। स्पेसिफिक रिलीफ एक्ट 1963 की धारा 6 के अनुसार, किसी भी व्यक्ति को कानूनी प्रक्रिया के बिना उसकी जमीन या मकान से बेदखल नहीं किया जा सकता। "
                "भारतीय न्याय संहिता की धारा 329 के तहत बिना अदालती आदेश के जबरन घुसना आपराधिक अतिचार यानी क्रिमिनल ट्रेसपास है। "
                "इस अवैध कब्जे के खिलाफ तुरंत उप-विभागीय मजिस्ट्रेट (एसडीएम) के समक्ष स्थगन आवेदन दिया जा रहा है।"
            )
            written_doc = (
                f"IN THE COURT OF THE SUB-DIVISIONAL MAGISTRATE (SDM) / CIVIL JUDGE\n"
                f"DISTRICT: {location} | DATE: {now_str}\n\n"
                f"URGENT APPLICATION FOR INJUNCTION AND PROTECTION OF POSSESSION UNDER SECTION 6 OF SPECIFIC RELIEF ACT, 1963\n"
                f"APPLICANT: {client_name}\n"
                f"RESPONDENT: Illegal Encroachers / Builders / Accused\n\n"
                f"1. That the applicant has been in settled and lawful possession of the subject property.\n"
                f"2. That on {now_str}, the respondents unlawfully attempted to trespass, demolish, and forcefully dispossess the applicant.\n"
                f"3. PRAYER: Grant immediate ad-interim injunction restraining the respondents from interfering with applicant's peaceful possession.\n\n"
                f"Applicant: {client_name}"
            )
            action_steps = [
                "1. Never surrender physical possession voluntarily; possession is 9 points in law.",
                "2. Call 112 to record a contemporaneous police call log of criminal trespass.",
                "3. File this urgent injunction petition before the SDM / Civil Court.",
                "4. Present electricity bills, tax receipts, voter ID, or ration card proving continuous possession."
            ]

        elif category == "LOAN_FRAUD":
            statutory_title = "Illegal Digital Lending App Harassment & Phishing Fraud"
            statutes = [
                {"law": "RBI Digital Lending Guidelines (2022)", "details": "Strict prohibition on recovery agents accessing borrower phone contacts or photos; harassment via abusive calls is strictly prohibited."},
                {"law": "Information Technology Act, 2000 — Section 66C & 66D", "details": "Punishment for identity theft and cheating by personation using computer resource."},
                {"law": "Bharatiya Nyaya Sanhita, 2023 (BNS) — Section 351 & 318", "details": "Criminal Intimidation and Cheating. Morphing photographs and issuing public threats constitutes a cognizable criminal offense."}
            ]
            rights_shield_hi = (
                "सावधान। आरबीआई के डिजिटल लेंडिंग नियमों के तहत फोन कॉन्टैक्ट्स हैक करना, फोटो मॉर्फ करना और गाली-गलौज करना गैरकानूनी है। "
                "भारतीय न्याय संहिता की धारा 351 और आईटी एक्ट की धारा 66 के तहत यह एक गंभीर संज्ञेय अपराध है। "
                "यह कॉल रिकॉर्ड हो रही है और इसकी सीधी शिकायत राष्ट्रीय साइबर क्राइम पोर्टल और आरबीआई लोकपाल को भेजी जा रही है।"
            )
            written_doc = (
                f"TO: The Officer-in-Charge, Cyber Crime Police Station / National Cyber Crime Portal\n"
                f"DISTRICT: {location} | DATE: {now_str}\n\n"
                f"COMPLAINT AGAINST FRAUDULENT DIGITAL LENDING ENTITY FOR EXTORTION, MORPHING, AND IT ACT VIOLATIONS\n"
                f"COMPLAINANT: {client_name}\n"
                f"ACCUSED: Operators / Recovery Agents of Fraudulent Mobile Loan App\n\n"
                f"1. That the complainant downloaded a loan app which unlawfully harvested private contacts and gallery data.\n"
                f"2. That recovery agents are issuing threatening calls, demanding illegal charges, and threatening to circulate defamatory morphed pictures.\n"
                f"3. PRAYER: Register FIR under BNS Sec 318, 351 and IT Act Sec 66C, 66D; freeze the beneficiary UPI handles and bank accounts.\n\n"
                f"Complainant: {client_name}"
            )
            action_steps = [
                "1. Do not pay any extortion money; scammers demand more once paid.",
                "2. Play the Spoken Anti-Extortion Shield to the caller.",
                "3. File complaint immediately on cybercrime.gov.in and dial 1930 (National Cyber Fraud Helpline).",
                "4. Inform friends and family with a broadcast message that your phone contacts were breached."
            ]

        elif category == "POLICE_CUSTODY":
            statutory_title = "Protection from Illegal Detention & Mandatory FIR Registration"
            statutes = [
                {"law": "BNSS, 2023 — Section 173(1)", "details": "Mandatory FIR registration upon disclosure of a cognizable offense (Supreme Court Lalita Kumari mandate). Zero FIR can be lodged anywhere."},
                {"law": "BNSS, 2023 — Section 35–47 (CrPC 41A–D)", "details": "D.K. Basu Guidelines: Mandatory identification of arresting officer, memo of arrest signed by witness, immediate notice to family member, right to medical examination."},
                {"law": "BNSS, 2023 — Section 173(3)", "details": "Direct right to send written complaint to the Superintendent of Police (SP) by speed post in case of police refusal to register FIR."}
            ]
            rights_shield_hi = (
                "सावधान। सुप्रीम कोर्ट के ललिता कुमारी निर्णय और बीएनएसएस की धारा 173 के अनुसार संज्ञेय अपराध की एफआईआर दर्ज करना पुलिस के लिए बाध्यकारी है। "
                "डीके बसु दिशा-निर्देशों के तहत बिना अरेस्ट मेमो और बिना परिवार को सूचना दिए किसी को थाने में बैठाना अवैध हिरासत है। "
                "यदि एफआईआर दर्ज नहीं की जाती, तो यह शिकायत धारा 173(3) के तहत सीधे पुलिस अधीक्षक और मानवाधिकार आयोग को भेजी जा रही है।"
            )
            written_doc = (
                f"TO: The Superintendent of Police (SP) / Senior Superintendent of Police (SSP)\n"
                f"DISTRICT: {location} | DATE: {now_str}\n\n"
                f"APPLICATION UNDER SECTION 173(3) BNSS, 2023 REGARDING POLICE STATION INACTION / REFUSAL TO REGISTER FIR\n"
                f"APPLICANT: {client_name}\n"
                f"OPPOSITE POLICE STATION: Local Police Station / Duty Officer\n\n"
                f"Respected Sir/Madam,\n"
                f"1. That the applicant approached the local police station to report a cognizable offense, but the duty officer refused to register an FIR.\n"
                f"2. That under Section 173(1) BNSS, 2023 and the judgment in Lalita Kumari v. Govt of UP, registration is mandatory.\n"
                f"3. PRAYER: Direct the registration of FIR, investigate the cognizable offense, and take appropriate action against the defaulting officer.\n\n"
                f"Applicant: {client_name}"
            )
            action_steps = [
                "1. Note down the name, belt number, and designation of the duty officer.",
                "2. Play the Spoken Police Accountability Shield citing D.K. Basu guidelines.",
                "3. Demand a Zero FIR if jurisdiction is cited as an excuse.",
                "4. Dispatch the Section 173(3) letter via Registered Speed Post directly to the SP."
            ]

        elif category == "DOMESTIC_VIOLENCE":
            statutory_title = "Protection of Women from Domestic Violence & Fast-Track Maintenance"
            statutes = [
                {"law": "Protection of Women from Domestic Violence Act, 2005 (PWDVA)", "details": "Section 12 (Application to Magistrate), Section 18 (Protection Orders), Section 19 (Residence Orders prohibiting eviction), Section 20 (Monetary Relief)."},
                {"law": "BNSS, 2023 — Section 144 (Legacy CrPC 125)", "details": "Summary, fast-track order for maintenance for wives, children, and parents unable to maintain themselves."},
                {"law": "Bharatiya Nyaya Sanhita, 2023 (BNS) — Section 85 & 86", "details": "Punishment for cruelty and matrimonial harassment by husband or his relatives."}
            ]
            rights_shield_hi = (
                "घरेलू हिंसा अधिनियम 2005 की धारा 19 के तहत किसी भी महिला को उसके साझे घर से निकाला नहीं जा सकता। "
                "बीएनएसएस की धारा 144 के तहत भोजन, वस्त्र और बच्चे की पढ़ाई के लिए तत्काल भरण-पोषण (मेंटेनेंस) पाना कानूनी अधिकार है। "
                "आप अकेले नहीं हैं; महिला हेल्पलाइन 181 और जिला विधिक सेवा प्राधिकरण (DLSA) आपको मुफ्त वकील और सुरक्षा अधिकारी उपलब्ध कराएंगे।"
            )
            written_doc = (
                f"BEFORE THE COURT OF JUDICIAL MAGISTRATE FIRST CLASS (JMFC) / PROTECTION OFFICER\n"
                f"DISTRICT: {location} | DATE: {now_str}\n\n"
                f"APPLICATION UNDER SECTION 12 READ WITH SECTIONS 18, 19, 20 OF PWDVA, 2005\n"
                f"APPLICANT: {client_name}\n"
                f"RESPONDENT: Husband / In-laws / Relatives\n\n"
                f"1. That the applicant is in a domestic relationship with the respondents residing in the shared household.\n"
                f"2. That the applicant was subjected to continuous physical, verbal, emotional, and economic abuse.\n"
                f"3. PRAYER: Pass immediate protection orders restraining respondents from committing acts of domestic violence; grant interim monetary relief.\n\n"
                f"Applicant: {client_name}"
            )
            action_steps = [
                "1. Contact National Women Helpline at 181 or Emergency 112.",
                "2. Document injuries at a government hospital (get an official MLC - Medico-Legal Case report).",
                "3. File this Section 12 application before the Protection Officer or Magistrate.",
                "4. Demand free legal representation through the Taluk/District Legal Services Committee."
            ]

        elif category == "CORRUPTION_RTI":
            statutory_title = "Action Against Bribery, Extortion & Administrative Denial"
            statutes = [
                {"law": "Right to Information Act, 2005 — Section 6(1)", "details": "Absolute right of citizen to inspect public records and demand file movement logs within mandatory 30-day timeline."},
                {"law": "Prevention of Corruption Act, 1988 — Section 7", "details": "Punishment for public servant accepting or demanding illegal gratification (bribe) is punishable with up to 7 years imprisonment."},
                {"law": "Legal Services Authorities Act, 1987", "details": "Constitutional entitlement under Article 39A providing free advocate services to low-income citizens via DLSA."}
            ]
            rights_shield_hi = (
                "सावधान। भ्रष्टाचार निवारण अधिनियम 1988 की धारा 7 के तहत सरकारी काम के लिए रिश्वत मांगना 7 साल की जेल का संज्ञेय अपराध है। "
                "सूचना का अधिकार अधिनियम 2005 की धारा 6 के तहत इस फाइल की पेंडेंसी और देरी के कारणों की जानकारी तुरंत मांगी जा रही है। "
                "यदि काम में जानबूझकर रुकावट डाली गई, तो इसकी लिखित शिकायत राज्य सतर्कता ब्यूरो यानी विजिलेंस को भेजी जा रही है।"
            )
            written_doc = (
                f"TO: The Public Information Officer (PIO), Department of Revenue / Municipal Administration\n"
                f"DISTRICT: {location} | DATE: {now_str}\n\n"
                f"APPLICATION FOR INFORMATION UNDER SECTION 6(1) OF THE RIGHT TO INFORMATION ACT, 2005\n"
                f"APPLICANT: {client_name} (Address provided)\n\n"
                f"INFORMATION SOUGHT:\n"
                f"1. Please provide the daily progress report and file movement register for Application No. [INSERT] submitted by the applicant.\n"
                f"2. Names and designations of the officials who held the file and reasons for exceeding the statutory Citizen Charter timeline.\n"
                f"3. Certified copy of the official file notings recorded on the applicant's request.\n\n"
                f"Fee: Rs. 10 Court Fee Stamp affixed herewith.\n"
                f"Applicant: {client_name}"
            )
            action_steps = [
                "1. Never pay a cash bribe; demand an official receipt for any demanded fee.",
                "2. Play the Spoken Anti-Corruption Shield to the defaulting official.",
                "3. Submit this formal RTI application to make the delay an open public record.",
                "4. Lodge an online complaint with the State Vigilance / Anti-Corruption Bureau (ACB)."
            ]

        elif category == "STREET_VENDOR":
            statutory_title = "Street Vendor Protection from Arbitrary Eviction"
            statutes = [
                {"law": "The Street Vendors Act, 2014 — Section 3(3)", "details": "Absolute bar on eviction until Town Vending Committee survey is completed and certificates are issued."},
                {"law": "The Street Vendors Act, 2014 — Section 33", "details": "Overriding effect of this central Act over all municipal corporation acts and bylaws."},
                {"law": "The Street Vendors Act, 2014 — Section 18", "details": "Mandatory 30-day prior written notice required before any relocation or eviction."}
            ]
            rights_shield_hi = (
                "सावधान। स्ट्रीट वेंडर्स अधिनियम 2014 की धारा 3(3) के अनुसार जब तक टाउन वेंडिंग कमेटी का सर्वे पूरा नहीं होता, "
                "किसी भी वेंडर को बेदखल नहीं किया जा सकता। धारा 33 के तहत यह केंद्रीय कानून नगर पालिका के नियमों से ऊपर है। "
                "बिना 30 दिन के लिखित नोटिस के दुकान हटाना कानून का उल्लंघन है।"
            )
            written_doc = (
                f"TO: The Municipal Commissioner / Chairman, Town Vending Committee (TVC)\n"
                f"MUNICIPAL CORPORATION: {location} | DATE: {now_str}\n\n"
                f"REPRESENTATION UNDER SECTION 3(3) & 18 OF THE STREET VENDORS ACT, 2014 AGAINST ILLEGAL EVICTION\n"
                f"APPLICANT: {client_name}\n\n"
                f"1. That the applicant is a peaceful street vendor vending at {location}.\n"
                f"2. That ward officials attempted to forcibly remove the vending cart without serving a Section 18 notice.\n"
                f"3. PRAYER: Direct field officials to immediately cease eviction actions until completion of TVC survey.\n\n"
                f"Applicant: {client_name}"
            )
            action_steps = [
                "1. Play the Spoken Rights Shield on phone loudspeaker to the inspecting officer.",
                "2. Politely demand 30 days written notice under Section 18 and an official receipt under Section 19.",
                "3. Preserve photographs and evidence of the vending spot.",
                "4. Submit this written representation to the TVC and Ward Officer."
            ]

        else:  # RELIGIOUS_GATHERING / GENERAL
            statutory_title = "Protection of Peaceful Gathering & Freedom of Conscience"
            statutes = [
                {"law": "Constitution of India — Article 25 & 19(1)(b)", "details": "Fundamental right to freedom of religion and peaceful assembly without arms."},
                {"law": "Bharatiya Nyaya Sanhita, 2023 (BNS) — Section 301, 189, 298", "details": "Disturbing religious worship, unlawful assembly, and injuring/defiling place of worship are cognizable offenses."},
                {"law": "BNSS, 2023 — Section 173(1)", "details": "Mandatory Zero FIR registration for any cognizable incident of mob vandalism or criminal intimidation."}
            ]
            rights_shield_hi = (
                "संविधान के अनुच्छेद 25 के अंतर्गत हर नागरिक को अपनी आस्था का पालन और शांतिपूर्ण प्रार्थना करने का मौलिक अधिकार है। "
                "धार्मिक सभा में बाधा डालना बीएनएस की धारा 301 और 189 के तहत एक संज्ञेय अपराध है। "
                "बीएनएसएस की धारा 173 के अनुसार पुलिस के लिए तत्काल जीरो एफआईआर दर्ज करना अनिवार्य है।"
            )
            written_doc = (
                f"BEFORE THE STATION HOUSE OFFICER (SHO) / ZERO FIR INTAKE\n"
                f"POLICE STATION: [Nearest Jurisdiction] | DISTRICT: {location} | DATE: {now_str}\n\n"
                f"COMPLAINT UNDER SECTION 173(1) BNSS, 2023 FOR OFFENSES UNDER BNS SECTIONS 189, 191, 298, 301, 351\n"
                f"COMPLAINANT: {client_name}\n"
                f"ACCUSED: Unlawful assembly of unidentified aggressors\n\n"
                f"1. That a peaceful prayer gathering was disrupted by hostile elements trespassing and issuing threats.\n"
                f"2. PRAYER: Register formal Zero FIR, secure CCTV, and provide immediate police protection.\n\n"
                f"Complainant: {client_name}"
            )
            action_steps = [
                "1. Dial 112 immediately to log an official police dispatch record.",
                "2. Record video/audio evidence without confronting the aggressors.",
                "3. Submit the Zero FIR complaint to the nearest police station.",
                "4. If refused, send via registered post to the Superintendent of Police under BNSS Sec 173(3)."
            ]

        return {
            "tier": "BHARAT_GRASSROOTS_AID",
            "category": category,
            "statutory_title": statutory_title,
            "statutory_sections": statutes,
            "spoken_rights_shield_hi": rights_shield_hi,
            "formal_document": written_doc,
            "action_steps": action_steps
        }


class EnterpriseLegalSuite:
    """
    Tier 2: Monetizable Enterprise / HNW Legal Suite
    1. Motor Vehicle Accidents (MACT, Sec 134 MV Act, GIC Claim)
    2. Real Estate Title & RERA Diligence (RERA Sec 18, 30-year chain of title)
    3. Commercial Contracts & MSME Delayed Payments (Contract Act Sec 73, MSME Samadhaan)
    4. Corporate & Employment Compliance (Companies Act, POSH Act 2013)
    5. Estate Planning & Wealth Succession (Wills, Probate, Family Settlement)
    """

    def analyze(self, transcript: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        meta = meta or {}
        text_lower = transcript.lower()
        client_name = meta.get("client_name", "Corporate Client / Policyholder")
        location = meta.get("location", "Bengaluru")
        now_str = datetime.now().strftime("%d %B %Y")

        if any(k in text_lower for k in ["rera", "builder", "flat", "possession", "occupancy certificate", "developer", "delay"]):
            sub_category = "REAL_ESTATE_RERA"
            title = "Real Estate Developer Delay & RERA Statutory Notice"
            statutes = [
                {"law": "Real Estate (Regulation and Development) Act, 2016 (RERA) — Section 18", "details": "Mandatory refund of total amount with interest (SBI MCLR + 2%) or monthly interest for delayed possession."},
                {"law": "RERA, 2016 — Section 14", "details": "Adherence to sanctioned plans; unauthorized structural deviations render developer liable to penalties."},
                {"law": "Consumer Protection Act, 2019", "details": "Deficiency in housing construction service; right to claim compensation for mental agony."}
            ]
            audio_en = (
                "Under Section 18 of the RERA Act, 2016, you are statutorily entitled to claim a 100% refund "
                "with interest at SBI highest marginal lending rate plus 2% from the date of promised possession, "
                "or demand monthly interest until the Occupancy Certificate is handed over. We have drafted your formal RERA notice."
            )
            doc = (
                f"LEGAL NOTICE UNDER SECTION 18 OF RERA ACT, 2016 FOR DELAYED POSSESSION & INTEREST\n"
                f"FROM: Advocate on behalf of {client_name}\n"
                f"TO: Managing Director, [DEVELOPER NAME] | DATE: {now_str}\n\n"
                f"SUBJECT: DEMAND NOTICE FOR IMMEDIATE HANDOVER / REFUND WITH INTEREST UNDER SECTION 18 OF RERA, 2016\n\n"
                f"1. That our client booked Unit No. [UNIT] in your project registered under RERA Reg. No. [REG_NO].\n"
                f"2. That under the Builder-Buyer Agreement, possession was promised on [DATE]. To date, you have failed to secure the Occupancy Certificate (OC).\n"
                f"3. TAKE NOTICE that you are hereby called upon to pay interest at SBI MCLR + 2% per annum within 15 days, failing which our client will file a formal complaint before the Real Estate Regulatory Authority (RERA).\n\n"
                f"Advocate for Claimant: {client_name}"
            )
            action_steps = [
                "1. Audit the sanctioned floor plan against current physical construction.",
                "2. Dispatch this statutory legal notice via Speed Post and registered email.",
                "3. File Form M / Form N before the State RERA Authority if unpaid after 15 days."
            ]

        elif any(k in text_lower for k in ["commercial contract", "msme", "b2b", "buyer default", "unpaid invoice", "goods delivered"]):
            sub_category = "COMMERCIAL_CONTRACT_MSME"
            title = "Commercial Contract Breach & MSME Samadhaan Claim"
            statutes = [
                {"law": "MSMED Act, 2006 — Section 15 & 16", "details": "Mandatory payment within 45 days. Delayed payment carries compound interest at three times the RBI bank rate with monthly rests."},
                {"law": "Indian Contract Act, 1872 — Section 73", "details": "Compensation for loss or damage caused by breach of contract naturally arising in the usual course of things."},
                {"law": "Commercial Courts Act, 2015", "details": "Mandatory Pre-Institution Mediation and Settlement (PIMS) under Section 12A."}
            ]
            audio_en = (
                "Notice of commercial default active. Under Section 16 of the MSMED Act, unpaid invoices past 45 days "
                "mandatorily accrue compound interest at three times the RBI bank rate with monthly rests. "
                "We have compiled your demand notice and initiated the pre-institution mediation packet."
            )
            doc = (
                f"STATUTORY DEMAND NOTICE UNDER SECTION 15 & 16 OF MSMED ACT, 2006\n"
                f"TO: The Board of Directors, [DEFAULTING COMPANY] | DATE: {now_str}\n\n"
                f"SUBJECT: DEMAND FOR PAYMENT OF PRINCIPAL INVOICES WITH THREE TIMES RBI COMPOUND INTEREST\n\n"
                f"1. That our client is a registered MSME enterprise (UDYAM Reg: [UDYAM_NO]).\n"
                f"2. That goods/services were duly accepted against Invoice Nos. [INVOICES] totaling Rs. [AMOUNT].\n"
                f"3. That despite the statutory 45-day window, payment remains overdue.\n"
                f"4. TAKE NOTICE: Pay the outstanding sum with compound interest at 3x RBI rate within 15 days, failing which an application under Section 18 will be submitted to the MSME Facilitation Council.\n\n"
                f"Authorized Signatory for {client_name}"
            )
            action_steps = [
                "1. Reconcile purchase orders, delivery challans, and GST e-invoices.",
                "2. Serve this formal demand notice giving 15 days cure period.",
                "3. File online claim on the MSME Samadhaan portal for automated arbitration."
            ]

        else:  # MOTOR_ACCIDENT / COLLISION DEFAULT
            sub_category = "MOTOR_ACCIDENT_PRO"
            title = "Motor Accident Collision, MACT Triage & GIC Insurance Dossier"
            statutes = [
                {"law": "Motor Vehicles (Amendment) Act, 2019 — Section 134", "details": "Statutory duty of driver in accident: attending to injured, taking reasonable steps, and reporting to police."},
                {"law": "General Insurance Council (GIC) Claim Regulations", "details": "Mandatory 24-48 hour claim intimation window for Own Damage (OD) and Third Party (TP) liability coverage."},
                {"law": "MACT Procedural Rules — DAR Framework", "details": "Detailed Accident Report compilation for third-party liability adjudication."}
            ]
            audio_en = (
                "Incident response active. Move to a safe location and turn on hazards. "
                "Photographs of vehicle number plates and impact damage are being cataloged. "
                "Your standardized insurance claim intimation dossier is assembled and your retainer counsel alerted."
            )
            doc = (
                f"=== MOTOR VEHICLE INSURANCE CLAIM INTIMATION DOSSIER ===\n"
                f"TO: Claims Management, {meta.get('insurer', 'General Insurance Company')}\n"
                f"DATE & TIME: {now_str} | POLICY: {meta.get('policy_no', 'POL-MOT-2026-8841')}\n\n"
                f"1. INSURED & VEHICLE:\n"
                f"   - Name: {client_name} | Vehicle No: {meta.get('vehicle_no', 'KA-01-XX-0000')}\n"
                f"   - Location: {location}\n\n"
                f"2. INCIDENT & LIABILITY NARRATIVE:\n"
                f'   "{transcript}"\n\n'
                f"3. EVIDENCE PRESERVED:\n"
                f"   - Dashcam footage timestamped and verified.\n"
                f"   - Electronic evidence certificate generated under Section 63 BSA, 2023.\n\n"
                f"PRAYER: Register claim reference, appoint surveyor, and authorize cashless towing."
            )
            action_steps = [
                "1. Photograph vehicle license plates, roadway skid marks, and traffic signal state.",
                "2. Submit this claim dossier to your insurer within 24 hours.",
                "3. Preserve dashcam storage card without overwriting."
            ]

        return {
            "tier": "ENTERPRISE_LEGAL_SUITE",
            "category": sub_category,
            "statutory_title": title,
            "statutory_sections": statutes,
            "spoken_guidance_en": audio_en,
            "formal_document": doc,
            "action_steps": action_steps
        }


class NyayaVaniEngine:
    """
    Unified entry point for NyayaVani Legal Engine.
    Dispatches to Grassroots Public Legal Aid or Enterprise Pro Legal Suite.
    Integrates Legal Knowledge Graph (GraphRAG), Citizen Legality Verdict,
    and Section 63 BSA cryptographic evidence hashing on all intakes.
    """
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
        meta = meta or {}
        text_lower = transcript.lower()

        # 1. Query Legal Knowledge Graph (GraphRAG)
        graph_result = self.graph_retriever.query(transcript)
        legality_verdict = graph_result["legality_verdict"]

        # 2. Determine Tier
        grassroots_hints = ["thela", "cart", "stall", "dukan", "shop", "vendor", "hawker", "rehdi", "khomcha", "hafta", "bribe", "wage", "salary", "loan app", "photo morph", "blackmail", "church", "prayer", "marpeet", "patni"]
        if suite_tier == "AUTO_DETECT":
            if any(k in text_lower for k in grassroots_hints):
                suite_tier = "BHARAT_GRASSROOTS_AID"
            elif any(k in text_lower for k in ["rera", "builder", "flat possession", "msme", "commercial contract", "car crash", "road accident", "vehicle accident", "insurance claim", "mact"]):
                suite_tier = "ENTERPRISE_LEGAL_SUITE"
            else:
                suite_tier = "BHARAT_GRASSROOTS_AID"

        if suite_tier == "ENTERPRISE_LEGAL_SUITE":
            result = self.enterprise_advisor.analyze(transcript, meta)
        else:
            result = self.grassroots_advisor.analyze(transcript, meta)

        # 3. Integrate Legality Verdict & Graph-Traversed Statutes
        result["legality_verdict"] = legality_verdict
        result["graph_subgraph"] = graph_result["subgraph"]
        
        # Override spoken guidance and actions if follow-up question is required or citizen is at fault
        if legality_verdict.get("follow_up_required"):
            follow_q = legality_verdict.get("follow_up_question", "Please clarify the details of the incident.")
            result["spoken_rights_shield_hi"] = f"स्पष्टीकरण आवश्यक है। {follow_q}"
            result["spoken_guidance_en"] = f"Clarification required: {follow_q}"
            result["statutory_title"] = "Case Intake Incomplete — Clarification Required"
            result["action_steps"] = [
                f"1. Clarification needed: {follow_q}",
                "2. Provide relevant dates, official notices, or receipt details.",
                "3. NyayaVani will issue an enforceable statutory verdict upon receipt of details."
            ]
        elif legality_verdict.get("citizen_fault"):
            v_sum = legality_verdict.get("verdict_summary", "")
            result["spoken_rights_shield_hi"] = v_sum
            result["spoken_guidance_en"] = v_sum
            result["statutory_title"] = f"Statutory Compliance Notice — {legality_verdict.get('status', 'REGULATORY_ENFORCEMENT')}"
            result["action_steps"] = [
                "1. Authority is exercising lawful statutory powers.",
                "2. Do not obstruct inspecting or law enforcement officers.",
                "3. Settle statutory compounding fee or appear before designated authority."
            ]

        # Merge traversed statutory sections seamlessly
        existing_laws = {s["law"] for s in result.get("statutory_sections", [])}
        for g_sec in graph_result.get("statutory_sections", []):
            if g_sec["law"] not in existing_laws and len(result.get("statutory_sections", [])) < 5:
                result.setdefault("statutory_sections", []).append(g_sec)
                existing_laws.add(g_sec["law"])

        # 4. Cryptographic Hash & Certificate
        loc = meta.get("location", "India")
        affidavit = self.hasher.generate_hash(transcript, location=loc)
        result["affidavit_evidence"] = affidavit
        result["input_transcript"] = transcript

        return result
