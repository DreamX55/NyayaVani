import os
import json
from typing import Dict, Any, List

class ComplianceAuditor:
    """
    Audits telephony transcripts against Indian Enterprise / BFSI guidelines
    (e.g., RBI fair practices code, mandatory recording disclosures, threat detection).
    """

    MANDATORY_DISCLOSURES = [
        {"id": "RECORDING_CONSENT", "keywords": ["call is recorded", "कॉल रिकॉर्ड", "record", "recording"]},
        {"id": "AGENT_IDENTITY", "keywords": ["calling from", "से बात कर रहा", "से बोल रहा", "bank", "finance"]},
        {"id": "REASON_FOR_CALL", "keywords": ["regarding your", "के संबंध में", "loan", "payment", "emi", "किस्त", "खाता"]}
    ]

    PROHIBITED_VIOLATIONS = [
        {"id": "ABUSIVE_THREAT", "severity": "HIGH", "keywords": ["police", "court", "जेल", "धमकी", "बकवास", "चोर", "मारूंगा", "सजा"]},
        {"id": "FALSE_INTEREST_RATE", "severity": "MEDIUM", "keywords": ["0% interest", "बिना ब्याज", "zero percent", "free loan"]},
        {"id": "PRESSURE_TIMELIMIT", "severity": "MEDIUM", "keywords": ["अभी के अभी", "right this second", "immediately or else"]}
    ]

    def audit_transcript(self, transcript: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        text_lower = transcript.lower()

        # Check Disclosures
        disclosures_met = []
        disclosures_missing = []
        for disc in self.MANDATORY_DISCLOSURES:
            if any(kw.lower() in text_lower for kw in disc["keywords"]):
                disclosures_met.append(disc["id"])
            else:
                disclosures_missing.append(disc["id"])

        # Check Violations
        violations_found = []
        for viol in self.PROHIBITED_VIOLATIONS:
            detected_keywords = [kw for kw in viol["keywords"] if kw.lower() in text_lower]
            if detected_keywords:
                violations_found.append({
                    "id": viol["id"],
                    "severity": viol["severity"],
                    "matched_keywords": detected_keywords
                })

        # Calculate Compliance Score (0-100)
        base_score = 100
        # Deduct 15 for each missing disclosure
        base_score -= len(disclosures_missing) * 15
        # Deduct for violations
        for v in violations_found:
            if v["severity"] == "HIGH":
                base_score -= 35
            elif v["severity"] == "MEDIUM":
                base_score -= 20

        score = max(0, min(100, base_score))

        # Status Tag
        if score >= 85:
            status = "COMPLIANT"
            color = "green"
        elif score >= 60:
            status = "NEEDS_REVIEW"
            color = "orange"
        else:
            status = "NON_COMPLIANT_RISK"
            color = "red"

        return {
            "transcript": transcript,
            "compliance_score": score,
            "status": status,
            "status_color": color,
            "disclosures_met": disclosures_met,
            "disclosures_missing": disclosures_missing,
            "violations_found": violations_found,
            "word_count": len(transcript.split()),
            "metadata": metadata or {}
        }
