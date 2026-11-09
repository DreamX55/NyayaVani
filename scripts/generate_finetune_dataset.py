import os
import json
import random

def generate_dataset(output_path: str = "scripts/data/nyayavani_finetune_dataset.jsonl"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    cities = [
        ("New Delhi", "Lajpat Nagar", "Delhi Police", "MCD", "hi-IN"),
        ("Bengaluru", "Indiranagar", "Bengaluru City Police", "BBMP", "kn-IN"),
        ("Mumbai", "Dharavi", "Mumbai Police", "BMC", "mr-IN"),
        ("Chennai", "T. Nagar", "Chennai Police", "GCC", "ta-IN"),
        ("Hyderabad", "Charminar", "Hyderabad City Police", "GHMC", "te-IN"),
        ("Kolkata", "Gariahat", "Kolkata Police", "KMC", "bn-IN")
    ]

    templates = [
        # 1. Street Vendor Rights
        {
            "category": "STREET_VENDORS",
            "inputs": [
                "Police is breaking my thela and demanding bribe without any notice.",
                "Municipal van seized my fruit cart despite me holding PM SVANidhi vending slip.",
                "Ward staff telling street vendors to evacuate immediately or face fine.",
                "Hawking stall dismantled by local authorities without Town Vending Committee survey."
            ],
            "statute": "The Street Vendors Act, 2014 — Section 3(3) and BNS Section 308 (Extortion)",
            "verdict": {
                "is_lawful": False,
                "status": "UNLAWFUL_ACT_BY_AUTHORITY",
                "verdict_summary": "ILLEGAL ACTION. Under Section 3(3) of The Street Vendors Act 2014, authorities have NO legal right to evict or seize carts prior to Town Vending Committee survey.",
                "citizen_standing": "You are 100% statutorily protected to conduct vending at this designated spot.",
                "violator_liability": "Cognizable criminal offense under BNS Section 308 (Extortion) and disciplinary violation under Street Vendors Act Section 18."
            },
            "spoken_hi": "स्ट्रीट वेंडर्स एक्ट 2014 की धारा 3(3) के अनुसार जब तक टाउन वेंडिंग कमेटी का सर्वे पूरा नहीं होता, किसी भी पटरी दुकानदार को हटाया नहीं जा सकता। अवैध वसूली बीएनएस की धारा 308 के तहत एक संज्ञेय अपराध है।",
            "action_steps": [
                "1. Display PM SVANidhi receipt and cite Section 3(3) Street Vendors Act.",
                "2. Record audio/video of the inspecting staff as contemporaneous evidence.",
                "3. Submit formal representation to the Town Vending Committee (TVC) and DLSA."
            ]
        },
        # 2. Predatory Loan Apps
        {
            "category": "CYBER_LOAN_EXTORTION",
            "inputs": [
                "Instant loan app agents are sending morphed photos to all my phone contacts.",
                "Online lending app threatening to leak my personal pictures if I don't pay double.",
                "Chinese loan app hacked my contact list and calling family members with abusive slurs.",
                "Paid full loan principal but recovery agents demanding extra money via unknown UPI."
            ],
            "statute": "IT Act Section 66D, BNS Section 318(4) & RBI Digital Lending Guidelines 2022",
            "verdict": {
                "is_lawful": False,
                "status": "CRIMINAL_EXTORTION_AND_CYBER_FRAUD",
                "verdict_summary": "ILLEGAL EXTORTION. Accessing contacts and morphing photos violates mandatory RBI lending rules and constitutes cognizable cyber fraud under IT Act Section 66D and BNS Section 318(4).",
                "citizen_standing": "You are a victim of criminal cyber harassment. You are under zero obligation to pay unauthorized extortion amounts.",
                "violator_liability": "Up to 7 years imprisonment under BNS Section 318(4); immediate freezing of offending bank accounts via National Cyber Crime Reporting Portal."
            },
            "spoken_hi": "आरबीआई की डिजिटल लेंडिंग गाइडलाइंस के अनुसार किसी भी ऐप को कॉन्टैक्ट्स या फोटो एक्सेस करने का अधिकार नहीं है। फोटो मॉर्फ करना आईटी एक्ट की धारा 66D और बीएनएस धारा 318 के तहत गैरकानूनी है। तुरंत 1930 पर साइबर शिकायत दर्ज करें।",
            "action_steps": [
                "1. Dial 1930 immediately or log complaint at cybercrime.gov.in.",
                "2. Preserve screenshots, call recordings, and UPI handles without deleting chats.",
                "3. File Zero FIR under BNSS Section 173 at nearest police station."
            ]
        },
        # 3. Motor Vehicle Accident & MACT
        {
            "category": "MOTOR_ACCIDENT_MACT",
            "inputs": [
                "Commercial truck jumped red light and rammed my sedan at the intersection.",
                "Speeding vehicle hit motorcycle causing multiple fractures and fled the scene.",
                "Private bus collided with our car on highway causing major structural damage.",
                "Accident caused by rash driver; local police station delaying First Accident Report."
            ],
            "statute": "Motor Vehicles Act 2019 Section 166, Section 134 & BNS Section 106",
            "verdict": {
                "is_lawful": False,
                "status": "ROAD_TRAFFIC_NEGLIGENCE_AND_STATUTORY_CLAIM",
                "verdict_summary": "ACTIONABLE LEGAL INJURY. The colliding driver's negligent driving violates BNS Section 106. You are entitled to complete medical, financial, and vehicular compensation under MV Act Section 166.",
                "citizen_standing": "You hold an absolute third-party insurance claim before the Motor Accidents Claims Tribunal (MACT) and statutory right to mandatory FAR registration.",
                "violator_liability": "Criminal prosecution under BNS Section 106 and full financial indemnity enforced against offending vehicle's insurance policy."
            },
            "spoken_hi": "मोटर वाहन अधिनियम की धारा 166 के तहत दुर्घटना के पीड़ितों को अस्पताल खर्च और वाहन नुकसान का पूरा मुआवजा पाने का कानूनी अधिकार है। बीएनएस की धारा 106 के तहत लापरवाह चालक के खिलाफ तत्काल मामला दर्ज किया जाना अनिवार्य है।",
            "action_steps": [
                "1. Secure Medico-Legal Certificate (MLC) from treating hospital immediately.",
                "2. Intimate insurer within 24 hours to preserve insurance claim validity.",
                "3. Request copy of First Accident Report (FAR) from police under Section 159 MV Act."
            ]
        },
        # 4. RERA Builder Delayed Possession
        {
            "category": "REAL_ESTATE_RERA",
            "inputs": [
                "Developer promised flat handover 18 months ago but construction completely stopped.",
                "Builder refusing to give possession or refund after collecting 90% of flat cost.",
                "Apartment complex incomplete without occupancy certificate after promised date.",
                "Real estate promoter demanding extra escalation charges before handing over keys."
            ],
            "statute": "Real Estate (Regulation and Development) Act 2016 (RERA) — Section 18",
            "verdict": {
                "is_lawful": False,
                "status": "STATUTORY_DEVELOPER_DEFAULT",
                "verdict_summary": "ILLEGAL DEFAULT. Failure to deliver flat possession on the agreed date is a direct statutory breach under Section 18 of RERA Act 2016.",
                "citizen_standing": "You are legally entitled to withdraw from the project with 100% refund plus SBI MCLR + 2% compound interest, or demand monthly delay interest.",
                "violator_liability": "Statutory penalties, project freezing, and arrest warrants issued by State RERA Authority."
            },
            "spoken_hi": "रेरा अधिनियम 2016 की धारा 18 के तहत फ्लैट का कब्जा समय पर न मिलने पर बिल्डर से एसबीआई के उच्चतम ब्याज दर जमा दो प्रतिशत के साथ पूरा पैसा वापस लेने का आपका कानूनी अधिकार है। हमने आपका कानूनी नोटिस तैयार कर दिया है।",
            "action_steps": [
                "1. Issue formal 15-day statutory demand notice under Section 18 RERA.",
                "2. File Form M complaint online before the State RERA Regulatory Authority.",
                "3. Seek interim stay on builder escrow withdrawals pending dispute resolution."
            ]
        },
        # 5. MSME Delayed Payments
        {
            "category": "MSME_COMMERCIAL_DEFAULT",
            "inputs": [
                "Supplied engineering parts worth 15 lakhs; corporate buyer defaulted past 60 days.",
                "Private company refusing to clear approved invoices citing internal audit delays.",
                "MSME vendor delivered goods against purchase order but payment withheld for 3 months.",
                "Buyer refusing to pay compound interest on overdue invoices past statutory 45 days."
            ],
            "statute": "MSMED Act 2006 — Sections 15 & 16 (Compound Interest at Three Times RBI Rate)",
            "verdict": {
                "is_lawful": False,
                "status": "STATUTORY_COMMERCIAL_DEFAULT",
                "verdict_summary": "ILLEGAL PAYMENT RETENTION. Section 15 mandates payment within 45 days. Default automatically triggers compound interest at 3x RBI bank rate with monthly rests under Section 16.",
                "citizen_standing": "You hold a non-waivable statutory right to compound interest that overrides any contrary clause in the corporate buyer's contract.",
                "violator_liability": "Mandatory recovery order through MSME Samadhaan Facilitation Council; compound interest cannot be claimed as tax deduction by defaulting buyer."
            },
            "spoken_hi": "एमएसएमई विकास अधिनियम की धारा 16 के अनुसार 45 दिनों से अधिक विलंबित भुगतान पर भारतीय रिजर्व बैंक की बैंक दर के तीन गुना चक्रवृद्धि ब्याज की वसूली का स्पष्ट कानूनी प्रावधान है। आपका वैधानिक दावा तैयार है।",
            "action_steps": [
                "1. Serve statutory 15-day demand notice calculating 3x RBI compound interest.",
                "2. File formal claim petition on MSME Samadhaan online portal (samadhaan.msme.gov.in).",
                "3. Initiate mandatory pre-institution mediation under Section 12A Commercial Courts Act."
            ]
        }
    ]

    records = []
    
    # Generate 300 diverse multi-lingual paired instances
    for i in range(300):
        tmpl = random.choice(templates)
        city_info = random.choice(cities)
        city_name, locality, police_dept, municipal_body, lang_code = city_info
        raw_input = random.choice(tmpl["inputs"])
        
        prompt = (
            f"SYSTEM: You are NyayaVani, a sovereign Indian legal counsel.\n"
            f"Analyze the citizen incident against codified Indian statutes.\n"
            f"Output strictly valid JSON with: legality_verdict, statutory_title, statutory_sections, spoken_rights_shield, formal_document, action_steps.\n\n"
            f"USER INCIDENT:\n"
            f"Location: {locality}, {city_name} (Jurisdiction: {municipal_body} / {police_dept})\n"
            f"Statement: \"{raw_input}\""
        )
        
        response_json = {
            "legality_verdict": tmpl["verdict"],
            "statutory_title": f"{tmpl['category'].replace('_', ' ')} — Statutory Defense Protocol",
            "statutory_sections": [
                {"law": tmpl["statute"], "details": tmpl["verdict"]["verdict_summary"]}
            ],
            "spoken_rights_shield": tmpl["spoken_hi"],
            "formal_document": f"FORMAL LEGAL NOTICE\nLOCATION: {locality}, {city_name}\nRECIPIENT: Inspecting Authority / Defaulting Party\nSUBJECT: Notice under {tmpl['statute']}\n\n1. TAKE NOTICE that your actions violate Indian law.\n2. Comply within statutory deadline.",
            "action_steps": tmpl["action_steps"]
        }
        
        record = {
            "instruction": "You are NyayaVani, a sovereign Indian legal counsel. Output valid JSON containing an explicit legality_verdict, statutory grounding, vernacular spoken shield, and formal legal instrument.",
            "input": f"Location: {locality}, {city_name}. Incident: {raw_input}",
            "output": json.dumps(response_json, ensure_ascii=False)
        }
        records.append(record)

    with open(output_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Successfully generated {len(records)} high-fidelity legal training records at {output_path}")

if __name__ == "__main__":
    generate_dataset()
