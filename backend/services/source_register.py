"""Versioned Statutory Source Register for NyayaVani.

Meets PRD Requirement L2:
- Versioned source register for cited provisions and templates.
- Requires documented approval from a qualified Indian advocate before labeling legal content 'reviewed'.
- Explicit NALSA / DLSA legal aid referral criteria (Requirement L3).
- Primary statutory sources: BNS 2023, BNSS 2023, BSA 2023, Code on Wages 2019,
  Street Vendors Act 2014, Motor Vehicles Act 1988 (amended 2019), RERA 2016,
  MSMED Act 2006, PWDVA 2005, RTI Act 2005, Constitution of India, and LSAA 1987.
"""

from typing import Dict, Any, List, Optional
import json

REGISTER_VERSION = "2026.11-v1"
REVIEWER_METADATA = {
    "reviewer_name": None,
    "credentials": None,
    "review_date": None,
    "register_status": "DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW",
    "jurisdiction": "Republic of India (BNS 2023, BNSS 2023, BSA 2023 and Special Acts)",
    "disclaimer": "Statutory provisions compiled from primary Indian legislation for triage and structured draft preparation. This register is a draft pending verification by a qualified advocate admitted to an Indian State Bar Council. Not certified legal advice."
}

STATUTORY_REGISTER: Dict[str, Dict[str, Any]] = {
    "WAGE_THEFT": {
        "category_title": "Wage Theft & Labor Exploitation",
        "jurisdiction": "All India (Labor Commissioner / Industrial Tribunals)",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "Code on Wages, 2019 — sections 17 and 45",
                "act": "Code on Wages, 2019 (Act No. 29 of 2019)",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/15793/1/aA2019-29.pdf",
                "conditions": "Applicable to employed persons in establishments. Section 17 mandates timely wage disbursement within statutory time limit (by 7th day of the succeeding month for monthly wages). Section 45 provides claims mechanism before appointed Authority.",
                "remedy": "Claim for unpaid wages with compensation up to 10 times the deducted amount under Section 45."
            },
            {
                "law": "Payment of Wages Act, 1936 (Sec 15) & Minimum Wages Act, 1948 (Sec 20)",
                "act": "Payment of Wages Act, 1936 & Minimum Wages Act, 1948",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/15234/1/A1936-04.pdf",
                "conditions": "Historical enactments applicable in states and sectors where transitional provisions maintain pre-Code enforcement authorities.",
                "remedy": "Application to the Authority for claims arising out of deductions from wages, delay in payment, or payment below statutory minimum wages."
            },
            {
                "law": "Constitution of India — Article 23 & Article 39A",
                "act": "Constitution of India",
                "source_url": "https://www.india.gov.in/my-government/constitution-india",
                "conditions": "Article 23 prohibits forced labor, begar, and non-payment of wages creating servitude (PUDR v. Union of India). Article 39A guarantees equal justice and free legal aid.",
                "remedy": "Constitutional writ remedy, criminal action under Bonded Labour System (Abolition) Act, and free legal aid."
            }
        ],
        "primary_question": "What work was done, for which employer, and what wages are unpaid?",
        "legal_aid_path": "Industrial workmen, informal laborers, and individuals earning below State thresholds are entitled to 100% free legal aid through the District Legal Services Authority (DLSA) under Section 12(h) of the Legal Services Authorities Act, 1987, guided by Article 39A of the Constitution."
    },
    "STREET_VENDOR": {
        "category_title": "Street Vendor Livelihood Shield & Town Vending Committee (TVC)",
        "jurisdiction": "All India (Urban Local Bodies / Municipal Authorities)",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "Street Vendors Act, 2014 — Section 3(3)",
                "act": "The Street Vendors (Protection of Livelihood and Regulation of Street Vending) Act, 2014 (Act No. 7 of 2014)",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/19057/1/sv_act_2014.pdf",
                "conditions": "Absolute statutory bar on eviction: No street vendor shall be evicted or relocated until the survey specified under sub-section (1) has been completed and the certificate of vending is issued.",
                "remedy": "Immunity against arbitrary municipal or police eviction; right to vend in assigned zone."
            },
            {
                "law": "Street Vendors Act, 2014 — Section 18",
                "act": "The Street Vendors Act, 2014",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/19057/1/sv_act_2014.pdf",
                "conditions": "Requires minimum 30 days prior written notice by the local authority before any relocation or confiscation of goods.",
                "remedy": "Challenge arbitrary eviction orders issued without 30 days mandatory notice before the Dispute Redressal Committee under Section 20."
            },
            {
                "law": "Constitution of India — Article 21",
                "act": "Constitution of India",
                "source_url": "https://www.india.gov.in/my-government/constitution-india",
                "conditions": "Right to livelihood is an integral part of the right to life under Article 21 (Olga Tellis and Sodan Singh v. NDMC).",
                "remedy": "Constitutional protection against arbitrary state action depriving livelihood without due process."
            }
        ],
        "primary_question": "Where is your stall or vending cart located, do you have a PM SVANidhi receipt or identity card, and did authorities serve a 30-day written notice?",
        "legal_aid_path": "Informal micro-vendors qualify for free representation before Municipal Town Vending Committees and Dispute Redressal Forums via DLSA under Section 12 of the Legal Services Authorities Act, 1987, upholding Article 21 livelihood rights."
    },
    "POLICE_CUSTODY": {
        "category_title": "Protection from Unlawful Detention & Mandatory Zero FIR",
        "jurisdiction": "All India (Police Stations, Magistrate Courts)",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "BNSS, 2023 — Section 173(1)",
                "act": "Bharatiya Nagarik Suraksha Sanhita, 2023 (Act No. 46 of 2023)",
                "source_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNSS_2023.pdf",
                "conditions": "Applies when information disclosing commission of a cognizable offense is given to police. Registration of FIR is mandatory regardless of territorial jurisdiction (Zero FIR). In force from July 1, 2024.",
                "remedy": "Mandatory registration of FIR; transmission to jurisdictional police station if recorded as Zero FIR."
            },
            {
                "law": "BNSS, 2023 — Section 35–47 (Arrest Safeguards)",
                "act": "Bharatiya Nagarik Suraksha Sanhita, 2023",
                "source_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNSS_2023.pdf",
                "conditions": "Codifies D.K. Basu guidelines: Identification of arresting officer, memo of arrest attested by at least one witness/family, notice of arrest, right to consult advocate, mandatory medical examination. In force from July 1, 2024.",
                "remedy": "Right to inform family, immediate legal representation, medical documentation of custody."
            },
            {
                "law": "BNSS, 2023 — Section 173(3)",
                "act": "Bharatiya Nagarik Suraksha Sanhita, 2023",
                "source_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNSS_2023.pdf",
                "conditions": "Triggered when an Officer-in-Charge of a police station refuses to register an FIR upon cognizable complaint. Preliminary enquiry permitted only in specified offences within 14 days.",
                "remedy": "Direct submission of written complaint by registered post to Superintendent of Police (SP) under Section 173(3) or application to Magistrate under Section 175(3)."
            },
            {
                "law": "Constitution of India — Article 21 & Article 22",
                "act": "Constitution of India",
                "source_url": "https://www.india.gov.in/my-government/constitution-india",
                "conditions": "Protection of personal liberty and safeguards against arbitrary arrest and detention. Right to be informed of grounds of arrest and produced before Magistrate within 24 hours.",
                "remedy": "Habeas corpus writ under Article 32 or 226; bail and judicial oversight."
            }
        ],
        "primary_question": "Which police station or officer is involved, was anyone arrested or detained, was an arrest memo issued, and what was provided in writing?",
        "legal_aid_path": "Every person in police custody or facing criminal allegations has a statutory right to immediate free legal assistance through DLSA Duty Advocates present at the police station or Magistrate remand hearing (Legal Services Authorities Act, 1987 Sec 12(g), backed by Article 21 and Article 39A)."
    },
    "LAND_GRABBING": {
        "category_title": "Protection Against Illegal Dispossession & Criminal Trespass",
        "jurisdiction": "Civil Courts & Executive Magistrates",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "Specific Relief Act, 1963 — Section 6",
                "act": "Specific Relief Act, 1963 (Act No. 47 of 1963)",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/1583/1/A1963-47.pdf",
                "conditions": "Summary suit for possession: If any person is dispossessed without consent of immovable property otherwise than in due course of law, he may recover possession within 6 months, notwithstanding title.",
                "remedy": "Immediate judicial restoration of settled physical possession."
            },
            {
                "law": "Bharatiya Nyaya Sanhita, 2023 — Section 329",
                "act": "Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023)",
                "source_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNS_2023.pdf",
                "conditions": "Criminal trespass: Entering into or upon property in possession of another with intent to commit an offense or intimidate, insult, or annoy. In force from July 1, 2024.",
                "remedy": "Criminal prosecution and police eviction of unlawful trespassers."
            }
        ],
        "primary_question": "Who occupies the property now, when was the entry attempted, and what utility bills, registry, or tenancy papers prove your prior settled possession?",
        "legal_aid_path": "Eligible low-income citizens can obtain free legal representation through DLSA to file Section 6 summary recovery suits and urgent stay applications under Section 12 of the Legal Services Authorities Act, 1987."
    },
    "LOAN_FRAUD": {
        "category_title": "Illegal Digital Lending Harassment & Cyber Phishing",
        "jurisdiction": "Cyber Crime Police, RBI Ombudsman",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "RBI Guidelines on Digital Lending (2022)",
                "act": "Reserve Bank of India Regulatory Framework for Digital Lending",
                "source_url": "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12382&Mode=0",
                "conditions": "Prohibits access to borrower mobile contacts, gallery, or biometric data; prohibits abusive recovery harassment or unauthorized recovery agents.",
                "remedy": "Complaint to RBI Ombudsman under Reserve Bank - Integrated Ombudsman Scheme, 2021."
            },
            {
                "law": "Information Technology Act, 2000 — Sections 66C & 66D",
                "act": "Information Technology Act, 2000 (Act No. 21 of 2000)",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/13116/1/it_act_2000_updated.pdf",
                "conditions": "Identity theft and cheating by personation using computer resource or unauthorized data harvesting.",
                "remedy": "Cyber cell FIR, freezing of fraudulent mule accounts and payment gateways."
            },
            {
                "law": "Bharatiya Nyaya Sanhita, 2023 — Sections 318 & 351",
                "act": "Bharatiya Nyaya Sanhita, 2023",
                "source_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNS_2023.pdf",
                "conditions": "Cheating (Section 318) and criminal intimidation (Section 351) via morphed images or phone harassment. In force from July 1, 2024.",
                "remedy": "Criminal registration of FIR for blackmail, extortion, and criminal intimidation."
            }
        ],
        "primary_question": "What is the exact name of the lending app or caller, what UPI/bank accounts were involved, and what screenshots/threat recordings do you possess?",
        "legal_aid_path": "Victims of cyber fraud and debt harassment can file complaints at cybercrime.gov.in (Helpline 1930) and seek DLSA counsel for criminal representation."
    },
    "DOMESTIC_VIOLENCE": {
        "category_title": "Domestic Violence Protection, Residence & Maintenance",
        "jurisdiction": "Protection Officers, Judicial Magistrate First Class",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "Protection of Women from Domestic Violence Act, 2005 — Sections 12, 18, 19, 20",
                "act": "PWDVA, 2005 (Act No. 43 of 2005)",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/2021/1/200543.pdf",
                "conditions": "Applies to an aggrieved woman in a domestic relationship living together in a shared household facing physical, emotional, sexual, or economic abuse. Emergency Helplines: 181 (Women in Distress), 112 (National Emergency).",
                "remedy": "Urgent ex-parte protection orders (Sec 18), residence orders prohibiting dispossession (Sec 19), monetary relief and medical expenses (Sec 20)."
            },
            {
                "law": "BNSS, 2023 — Section 144",
                "act": "Bharatiya Nagarik Suraksha Sanhita, 2023",
                "source_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNSS_2023.pdf",
                "conditions": "Order for maintenance of wives, children, and parents where person having sufficient means neglects or refuses to maintain. Effective July 1, 2024 (replaces CrPC 125).",
                "remedy": "Monthly interim allowance for maintenance and expenses of proceedings."
            },
            {
                "law": "Constitution of India — Article 21",
                "act": "Constitution of India",
                "source_url": "https://www.india.gov.in/my-government/constitution-india",
                "conditions": "Fundamental right to life with dignity, bodily integrity, and personal liberty.",
                "remedy": "Constitutional protection against domestic abuse, state protection orders, and legal representation."
            }
        ],
        "primary_question": "Are you or your dependents in immediate physical danger, what safe contact method can be used, and what shelter, medical, or police help is needed now?",
        "legal_aid_path": "Women are unconditionally entitled to free legal aid under Section 12(c) of the Legal Services Authorities Act, 1987, including free representation before Protection Officers and Magistrate Courts. Emergency helplines: 181 (Women in Distress) and 112 (National Emergency)."
    },
    "CORRUPTION_RTI": {
        "category_title": "Public Accountability, Welfare Denial & Right to Information",
        "jurisdiction": "Public Information Officers (PIO), Information Commissions",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "Right to Information Act, 2005 — Sections 6 & 7",
                "act": "RTI Act, 2005 (Act No. 22 of 2005)",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/2065/1/A2005-22.pdf",
                "conditions": "Right of any citizen to secure access to information under control of public authorities within 30 days (or 48 hours if life and liberty is involved under Section 7(1)).",
                "remedy": "Mandatory disclosure; penalty of ₹250/day up to ₹25,000 on errant PIO under Section 20."
            },
            {
                "law": "Prevention of Corruption Act, 1988 — Section 7",
                "act": "Prevention of Corruption Act, 1988 (Act No. 49 of 1988)",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/1944/1/198849.pdf",
                "conditions": "Offense relating to public servant being bribed or demanding undue advantage for performance of public duty.",
                "remedy": "Anti-Corruption Bureau (ACB) / Lokayukta trap and criminal prosecution."
            }
        ],
        "primary_question": "Which government office, ration dealer, or department is involved, what benefit was denied, and what application or acknowledgement slip number do you hold?",
        "legal_aid_path": "BPL ration card holders and marginalized citizens obtain free legal assistance at DLSA front offices under Section 12 of the Legal Services Authorities Act, 1987 to draft and file RTI petitions and statutory appeals."
    },
    "RELIGIOUS_GATHERING": {
        "category_title": "Freedom of Conscience & Peaceful Assembly Shield",
        "jurisdiction": "Police, Sessions Courts, High Courts",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "Constitution of India — Article 25",
                "act": "Constitution of India",
                "source_url": "https://www.india.gov.in/my-government/constitution-india",
                "conditions": "Freedom of conscience and free profession, practice and propagation of religion to all persons equally.",
                "remedy": "Protection of peaceful worship and assembly; constitutional writ protection."
            },
            {
                "law": "Bharatiya Nyaya Sanhita, 2023 — Sections 189, 298 & 301",
                "act": "Bharatiya Nyaya Sanhita, 2023",
                "source_url": "https://www.mha.gov.in/sites/default/files/2023-12/BNS_2023.pdf",
                "conditions": "Unlawful assembly (Sec 189), uttering words or acts with deliberate intent to wound religious feelings (Sec 298), and disturbing religious assemblies (Sec 301). In force from July 1, 2024.",
                "remedy": "Cognizable criminal offenses requiring immediate Zero FIR under BNSS Section 173(1)."
            }
        ],
        "primary_question": "Where did the peaceful gathering take place, who entered or disrupted it, were weapons or threats used, and did the local police refuse to register an FIR?",
        "legal_aid_path": "Aggrieved religious or community groups facing intimidation qualify for DLSA emergency panel advocacy to escort victims to police stations for FIR registration."
    },
    "MOTOR_ACCIDENT_PRO": {
        "category_title": "Motor Vehicle Collision & Statutory Insurance Claim Packet",
        "jurisdiction": "Motor Accident Claims Tribunal (MACT), Insurance Ombudsman",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "Motor Vehicles Act, 1988 (amended 2019) — Sections 146 & 159",
                "act": "Motor Vehicles Act, 1988 (Act No. 59 of 1988)",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/1798/1/198859.pdf",
                "conditions": "Section 146 mandates compulsory third-party insurance for all motor vehicles; Section 159 mandates police submission of Detailed Accident Report (DAR) to Claims Tribunal and Insurer within 90 days.",
                "remedy": "Statutory liability enforcement and automatic initiation of claim process via DAR."
            },
            {
                "law": "Motor Vehicles Act, 1988 (amended 2019) — Sections 164 & 166",
                "act": "Motor Vehicles Act, 1988",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/1798/1/198859.pdf",
                "conditions": "Section 164 provides defined no-fault compensation (₹5 lakh for death, ₹2.5 lakh for grievous hurt); Section 166 governs fault-based compensation claims filed before MACT within 6 months.",
                "remedy": "Third-party compensation for bodily injury, death, or property damage through MACT."
            },
            {
                "law": "Motor Vehicles Act, 1988 (amended 2019) — Section 134",
                "act": "Motor Vehicles Act, 1988",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/1798/1/198859.pdf",
                "conditions": "Duty of driver in case of accident and injury to take reasonable steps to secure medical attention and report within 24 hours.",
                "remedy": "Statutory compliance avoiding criminal liability; facilitates early intimation of claim."
            },
            {
                "law": "Bharatiya Sakshya Adhiniyam, 2023 — Section 63",
                "act": "BSA, 2023 (Electronic Records Admissibility)",
                "source_url": "https://www.mha.gov.in/sites/default/files/2023-12/BSA_2023.pdf",
                "conditions": "Admissibility of electronic records (dashcam video, photographs, digital communications) with certificate identifying electronic source and integrity hash. In force from July 1, 2024.",
                "remedy": "Evidentiary preservation of contemporaneous crash footage and communications."
            }
        ],
        "primary_question": "What are the vehicle registration numbers, date and exact location of collision, names of insurers and policy numbers, and were there bodily injuries?",
        "legal_aid_path": "Road accident victims and families are entitled to free legal aid through MACT Lok Adalats and DLSA legal aid clinics for speedy claim compensation under Section 12 of the Legal Services Authorities Act, 1987."
    },
    "REAL_ESTATE_RERA": {
        "category_title": "Real Estate Buyer Protection & RERA Possession Delay",
        "jurisdiction": "State Real Estate Regulatory Authority (RERA)",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "Real Estate (Regulation and Development) Act, 2016 — Section 18",
                "act": "RERA Act, 2016 (Act No. 16 of 2016)",
                "source_url": "https://www.indiacode.nic.in/indiacode/bitstream/123456789/2158/1/A201616.pdf",
                "conditions": "Promoter failing to complete or give possession of apartment, plot, or building in accordance with terms of agreement for sale.",
                "remedy": "Allottee right to claim full refund with prescribed interest (SBI MCLR + 2%) or monthly delay interest until possession."
            },
            {
                "law": "Real Estate (Regulation and Development) Act, 2016 — Section 31",
                "act": "RERA Act, 2016",
                "source_url": "https://www.indiacode.nic.in/indiacode/bitstream/123456789/2158/1/A201616.pdf",
                "conditions": "Right of any aggrieved allottee to file a complaint with the RERA Authority or Adjudicating Officer for any violation of the Act, agreement, or delayed possession under Section 19(4).",
                "remedy": "Statutory complaint redressal, directions for completion, and recovery of compensation as arrears of land revenue."
            }
        ],
        "primary_question": "What is the RERA registration number of the project, promised possession date in the agreement, total amount paid, and did the builder obtain an Occupancy Certificate?",
        "legal_aid_path": "Aggrieved homebuyers can approach State Consumer Dispute Redressal Commissions and State RERA Legal Aid cells for nominal or free mediation."
    },
    "COMMERCIAL_CONTRACT_MSME": {
        "category_title": "MSME Delayed Payments & Commercial Contract Recovery",
        "jurisdiction": "MSME Micro and Small Enterprise Facilitation Council (MSEFC)",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "MSMED Act, 2006 — Sections 15 & 16",
                "act": "Micro, Small and Medium Enterprises Development Act, 2006 (Act No. 27 of 2006)",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/5872/1/a2006-27.pdf",
                "conditions": "Buyer failing to make payment within agreed date (maximum 45 days) to registered Micro or Small enterprise supplier.",
                "remedy": "Statutory liability to pay compound interest with monthly rests at 3 times the Bank Rate notified by RBI."
            },
            {
                "law": "MSMED Act, 2006 — Section 18",
                "act": "MSMED Act, 2006",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/5872/1/a2006-27.pdf",
                "conditions": "Statutory reference of delayed payment disputes to the Micro and Small Enterprises Facilitation Council (MSEFC).",
                "remedy": "Mandatory conciliation; if unsuccessful, statutory arbitration under Arbitration and Conciliation Act, 1996 with award enforceable as a court decree."
            },
            {
                "law": "Indian Contract Act, 1872 — Section 73",
                "act": "Indian Contract Act, 1872 (Act No. 9 of 1872)",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/2187/1/A1872-09.pdf",
                "conditions": "Compensation for loss or damage caused by breach of contract.",
                "remedy": "Damages for breach that naturally arose in usual course of things."
            }
        ],
        "primary_question": "Is the supplier registered on Udyam as micro/small enterprise, what are the purchase order and invoice numbers, when were goods accepted, and what amount remains unpaid?",
        "legal_aid_path": "MSME Samadhaan portal provides an administrative dispute mechanism before MSEFC with mandatory conciliation before arbitration."
    },
    "GENERAL_CITIZEN_AID": {
        "category_title": "General Citizen Rights & Statutory Legal Aid Intake",
        "jurisdiction": "District Legal Services Authority (DLSA) / Taluk Committees",
        "review_date": None,
        "reviewed_by": None,
        "is_verified": False,
        "references": [
            {
                "law": "Legal Services Authorities Act, 1987 — Section 12",
                "act": "Legal Services Authorities Act, 1987 (Act No. 39 of 1987)",
                "source_url": "https://www.indiacode.nic.in/bitstream/123456789/1943/1/198739.pdf",
                "conditions": "Criteria for giving legal services: Women, children, SC/ST members, industrial workmen, persons in custody, disabled persons, disaster victims, and persons having annual income less than specified ceiling (typically ₹3,00,000 p.a.).",
                "remedy": "Free counsel, court fee exemption, drafting of pleadings, and certified copy cost coverage under Article 39A."
            },
            {
                "law": "Constitution of India — Article 21 & Article 39A",
                "act": "Constitution of India",
                "source_url": "https://www.india.gov.in/my-government/constitution-india",
                "conditions": "Constitutional guarantee of right to life and personal liberty (Article 21) and the State mandate to ensure equal justice and free legal aid (Article 39A).",
                "remedy": "Fundamental rights protection, access to justice, and free legal representation."
            }
        ],
        "primary_question": "What happened, when and where did it occur, who was involved, and what immediate outcome or protection are you seeking?",
        "legal_aid_path": "Contact the nearest District Legal Services Authority (DLSA) front office or dial national toll-free helpline 15100. NALSA provides free legal advocates at state expense for all eligible persons."
    }
}


def get_source_register_entry(category: str) -> Dict[str, Any]:
    """Retrieve verified, versioned source register details for a category."""
    clean_cat = category.strip().upper()
    if clean_cat in STATUTORY_REGISTER:
        return STATUTORY_REGISTER[clean_cat]
    # Check fallback / synonym matching
    if "ACCIDENT" in clean_cat or "CAR" in clean_cat or "CRASH" in clean_cat:
        return STATUTORY_REGISTER["MOTOR_ACCIDENT_PRO"]
    if "RERA" in clean_cat or "ESTATE" in clean_cat or "BUILDER" in clean_cat:
        return STATUTORY_REGISTER["REAL_ESTATE_RERA"]
    if "MSME" in clean_cat or "CONTRACT" in clean_cat:
        return STATUTORY_REGISTER["COMMERCIAL_CONTRACT_MSME"]
    if "VENDOR" in clean_cat:
        return STATUTORY_REGISTER["STREET_VENDOR"]
    if "WAGE" in clean_cat or "SALARY" in clean_cat:
        return STATUTORY_REGISTER["WAGE_THEFT"]
    if "CUSTODY" in clean_cat or "POLICE" in clean_cat or "FIR" in clean_cat:
        return STATUTORY_REGISTER["POLICE_CUSTODY"]
    if "LOAN" in clean_cat or "PHISH" in clean_cat:
        return STATUTORY_REGISTER["LOAN_FRAUD"]
    if "DOMESTIC" in clean_cat or "MAINTENANCE" in clean_cat:
        return STATUTORY_REGISTER["DOMESTIC_VIOLENCE"]
    if "LAND" in clean_cat or "EVICTION" in clean_cat:
        return STATUTORY_REGISTER["LAND_GRABBING"]
    if "CORRUPT" in clean_cat or "RTI" in clean_cat:
        return STATUTORY_REGISTER["CORRUPTION_RTI"]
    if "RELIGION" in clean_cat or "CHURCH" in clean_cat or "PRAYER" in clean_cat:
        return STATUTORY_REGISTER["RELIGIOUS_GATHERING"]
    return STATUTORY_REGISTER["GENERAL_CITIZEN_AID"]


def export_register_json() -> str:
    """Exports the register as structured JSON metadata for transparency & compliance."""
    return json.dumps({
        "register_version": REGISTER_VERSION,
        "reviewer_metadata": REVIEWER_METADATA,
        "categories": STATUTORY_REGISTER
    }, indent=2, ensure_ascii=False)
