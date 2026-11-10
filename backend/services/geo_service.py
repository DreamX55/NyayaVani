"""City-based Geolocation and Adaptive Multilingual Resolver for NyayaVani.

Audited and Corrected according to Sovereign Indian Jurisdictions:
- Distinct profiles for Pune (PMC / Maharashtra), Noida (Noida Authority / UP),
  Gurugram (MCG / Haryana), Bengaluru (BBMP / Karnataka), Mumbai (BMC / Maharashtra),
  Delhi (MCD / Delhi NCT), Chennai (GCC / TN), Hyderabad (GHMC / Telangana), Kolkata (KMC / WB).
- NEVER defaults unknown locations to Delhi. Uses a National Jurisdiction Pending profile.
- NEVER aliases Pune to Mumbai, Noida to Delhi, or Gurugram to Delhi.
"""

import re
from typing import Dict, Any, Optional, Tuple

class GeoLanguageService:
    """
    City-based Geolocation and Adaptive Multilingual Resolver for NyayaVani.
    Round 1: Defaults to the detected city's regional language, authority bodies, and native Timbre voice.
    Round 2+: Automatically detects spoken/written language script to adapt seamlessly if user speaks another language.
    """

    CITY_PROFILES: Dict[str, Dict[str, Any]] = {
        "bengaluru": {
            "city_display": "Bengaluru, Karnataka",
            "primary_language": "kn-IN",
            "primary_voice": "Chetana",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "Bruhat Bengaluru Mahanagara Palike (BBMP)",
            "legal_aid_authority": "Karnataka State Legal Services Authority (KSLSA) / Bengaluru DLSA",
            "police_emergency": "Bengaluru City Police (112)",
            "vernacular_greeting": "ನಮಸ್ಕಾರ, ನ್ಯಾಯವಾಣಿಗೆ ಸುಸ್ವಾಗತ. ನಿಮ್ಮ ಕಾನೂನು ಸಮಸ್ಯೆಯನ್ನು ಮಾತನಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ ತಿಳಿಸಿ."
        },
        "mumbai": {
            "city_display": "Mumbai, Maharashtra",
            "primary_language": "mr-IN",
            "primary_voice": "Vasudha",
            "secondary_language": "hi-IN",
            "secondary_voice": "Shivani",
            "municipal_body": "Brihanmumbai Municipal Corporation (BMC)",
            "legal_aid_authority": "Maharashtra State Legal Services Authority (MSLSA) / Mumbai DLSA",
            "police_emergency": "Mumbai Police Control Room (112)",
            "vernacular_greeting": "नमस्कार, न्यायवाणी मध्ये आपले स्वागत आहे. तुमची कायदेशीर समस्या बोला किंवा टाईप करा."
        },
        "pune": {
            "city_display": "Pune, Maharashtra",
            "primary_language": "mr-IN",
            "primary_voice": "Vasudha",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "Pune Municipal Corporation (PMC)",
            "legal_aid_authority": "Maharashtra State Legal Services Authority (MSLSA) / Pune DLSA",
            "police_emergency": "Pune City Police Control Room (112)",
            "vernacular_greeting": "नमस्कार, न्यायवाणी मध्ये आपले स्वागत आहे. तुमची कायदेशीर समस्या बोला किंवा टाईप करा."
        },
        "delhi": {
            "city_display": "New Delhi, NCT of Delhi",
            "primary_language": "hi-IN",
            "primary_voice": "Shivani",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "Municipal Corporation of Delhi (MCD)",
            "legal_aid_authority": "Delhi State Legal Services Authority (DSLSA)",
            "police_emergency": "Delhi Police Dispatch (112)",
            "vernacular_greeting": "नमस्कार, न्यायवाणी में आपका स्वागत है। अपनी कानूनी समस्या बोलकर या लिखकर बताएं।"
        },
        "noida": {
            "city_display": "Noida, Gautam Buddha Nagar, Uttar Pradesh",
            "primary_language": "hi-IN",
            "primary_voice": "Shivani",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "New Okhla Industrial Development Authority (NOIDA)",
            "legal_aid_authority": "Uttar Pradesh State Legal Services Authority (UPSLSA) / Gautam Buddha Nagar DLSA",
            "police_emergency": "Noida Police Commissionerate (112)",
            "vernacular_greeting": "नमस्कार, न्यायवाणी में आपका स्वागत है। अपनी कानूनी समस्या बोलकर या लिखकर बताएं।"
        },
        "gurugram": {
            "city_display": "Gurugram, Haryana",
            "primary_language": "hi-IN",
            "primary_voice": "Shivani",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "Municipal Corporation of Gurugram (MCG)",
            "legal_aid_authority": "Haryana State Legal Services Authority (HALSA) / Gurugram DLSA",
            "police_emergency": "Gurugram Police Control (112)",
            "vernacular_greeting": "नमस्कार, न्यायवाणी में आपका स्वागत है। अपनी कानूनी समस्या बोलकर या लिखकर बताएं।"
        },
        "chennai": {
            "city_display": "Chennai, Tamil Nadu",
            "primary_language": "ta-IN",
            "primary_voice": "Kalpana",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "Greater Chennai Corporation (GCC)",
            "legal_aid_authority": "Tamil Nadu State Legal Services Authority (TNSLSA) / Chennai DLSA",
            "police_emergency": "Chennai Police Central Control (112)",
            "vernacular_greeting": "வணக்கம், நியாயவாணிக்கு நல்வரவு. உங்கள் சட்டப் பிரச்சனையைப் பேசி அல்லது தட்டச்சு செய்து தெரிவிக்கவும்."
        },
        "hyderabad": {
            "city_display": "Hyderabad, Telangana",
            "primary_language": "te-IN",
            "primary_voice": "Lakshmi",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "Greater Hyderabad Municipal Corporation (GHMC)",
            "legal_aid_authority": "Telangana State Legal Services Authority (TSLSA) / Hyderabad DLSA",
            "police_emergency": "Hyderabad City Police (112)",
            "vernacular_greeting": "నమస్కారం, న్యాయవాణికి స్వాగతం. మీ న్యాయపరమైన సమస్యను మాట్లాడి లేదా టైప్ చేసి చెప్పండి."
        },
        "kolkata": {
            "city_display": "Kolkata, West Bengal",
            "primary_language": "bn-IN",
            "primary_voice": "Riyaa",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "Kolkata Municipal Corporation (KMC)",
            "legal_aid_authority": "West Bengal State Legal Services Authority (WBSLSA) / Kolkata DLSA",
            "police_emergency": "Kolkata Police Headquarters (112)",
            "vernacular_greeting": "নমস্কার, ন্যায়বাণীতে আপনাকে স্বাগতম। আপনার আইনি समस्या বলুন বা লিখে জানান।"
        },
        "national_default": {
            "city_display": "India (Local Jurisdiction Pending Confirmation)",
            "primary_language": "indic-auto",
            "primary_voice": "Shivani",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "Local Municipal Authority / Ward Office (Pending Confirmation)",
            "legal_aid_authority": "National Legal Services Authority (NALSA) / Nearest District Legal Services Authority (DLSA) — 15100",
            "police_emergency": "National Emergency Response Support System (112)",
            "vernacular_greeting": "Welcome to NyayaVani. Please state your legal problem in your preferred language."
        }
    }

    # Strict geographical alias mapping - NEVER maps Pune to Mumbai, Noida to Delhi, or Gurugram to Delhi
    CITY_ALIASES: Dict[str, str] = {
        "bangalore": "bengaluru",
        "blr": "bengaluru",
        "karnataka": "bengaluru",
        "bombay": "mumbai",
        "thane": "mumbai",
        "navi mumbai": "mumbai",
        "pune": "pune",
        "pimpri": "pune",
        "chinchwad": "pune",
        "delhi": "delhi",
        "new delhi": "delhi",
        "dilli": "delhi",
        "noida": "noida",
        "greater noida": "noida",
        "gautam buddha nagar": "noida",
        "gurugram": "gurugram",
        "gurgaon": "gurugram",
        "madras": "chennai",
        "tamil nadu": "chennai",
        "hyderabad": "hyderabad",
        "secunderabad": "hyderabad",
        "telangana": "hyderabad",
        "calcutta": "kolkata",
        "kolkata": "kolkata",
        "west bengal": "kolkata"
    }

    @classmethod
    def resolve_city_profile(cls, city_or_query: str, coords: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """
        Resolves city profile from name, coordinates, or query text.
        Returns the National Default profile if location is unmapped, unknown, or generic.
        """
        q_lower = (city_or_query or "").lower().strip()
        target = None

        # Check coordinate bounds if provided
        if coords:
            lat, lon = coords
            if 12.8 <= lat <= 13.2 and 77.4 <= lon <= 77.8:
                target = "bengaluru"
            elif 18.4 <= lat <= 18.7 and 73.7 <= lon <= 74.0:
                target = "pune"
            elif 18.8 <= lat <= 19.3 and 72.7 <= lon <= 73.1:
                target = "mumbai"
            elif 28.4 <= lat <= 28.6 and 77.3 <= lon <= 77.5:
                target = "noida"
            elif 28.3 <= lat <= 28.5 and 76.9 <= lon <= 77.1:
                target = "gurugram"
            elif 28.5 <= lat <= 28.9 and 77.0 <= lon <= 77.3:
                target = "delhi"
            elif 12.9 <= lat <= 13.2 and 80.1 <= lon <= 80.4:
                target = "chennai"
            elif 17.2 <= lat <= 17.6 and 78.3 <= lon <= 78.6:
                target = "hyderabad"
            elif 22.4 <= lat <= 22.7 and 88.2 <= lon <= 88.5:
                target = "kolkata"

        # Check direct city profiles
        if not target and q_lower:
            for city_key in cls.CITY_PROFILES.keys():
                if city_key != "national_default" and city_key in q_lower:
                    target = city_key
                    break

        # Check text aliases
        if not target and q_lower:
            for alias, mapped_city in cls.CITY_ALIASES.items():
                if alias in q_lower:
                    target = mapped_city
                    break

        # Safe fallback: return national default if unmapped
        if not target or target not in cls.CITY_PROFILES:
            return cls.CITY_PROFILES["national_default"]

        return cls.CITY_PROFILES[target]

    @classmethod
    def adapt_language_from_text(cls, text: str, current_lang: str) -> Tuple[str, str]:
        """
        Turn 2+ Adaptive Language Detection:
        Inspects Unicode script ranges and vocabulary to dynamically switch language and voice if the user
        replies in a different language than their city default.
        """
        if not text:
            return current_lang or "indic-auto", "Shivani"

        try:
            from backend.services.legal_engine import detect_language
            base_lang = detect_language(text, lang_code=current_lang, detected_language=current_lang)
            voice_map = {
                "mr": ("mr-IN", "Vasudha"),
                "hi": ("hi-IN", "Shivani"),
                "ta": ("ta-IN", "Kalpana"),
                "te": ("te-IN", "Lakshmi"),
                "kn": ("kn-IN", "Chetana"),
                "bn": ("bn-IN", "Riyaa"),
                "gu": ("gu-IN", "Tarika"),
                "pa": ("pa-IN", "Tarika"),
                "ml": ("ml-IN", "Lakshmi"),
                "en": ("en-IN", "Avinash" if any(w in text.lower() for w in ["court", "police", "money", "delay", "lawyer", "notice"]) else "Shivani"),
            }
            if base_lang in voice_map:
                return voice_map[base_lang]
        except Exception:
            pass

        # Fallback to direct script inspection
        if re.search(r"[\u0C80-\u0CFF]", text):
            return "kn-IN", "Chetana"
        if re.search(r"[\u0B80-\u0BFF]", text):
            return "ta-IN", "Kalpana"
        if re.search(r"[\u0C00-\u0C7F]", text):
            return "te-IN", "Lakshmi"
        if re.search(r"[\u0980-\u09FF]", text):
            return "bn-IN", "Riyaa"
        if re.search(r"[\u0A80-\u0AFF]", text):
            return "gu-IN", "Tarika"
        if re.search(r"[\u0A00-\u0A7F]", text):
            return "pa-IN", "Tarika"
        if re.search(r"[\u0D00-\u0D7F]", text):
            return "ml-IN", "Lakshmi"
        if re.search(r"[\u0900-\u097F]", text):
            marathi_markers = ["आहे", "नाही", "केले", "दिले", "झाले", "पगार", "कंत्राटदार", "पोलीस", "पैसे", "काम", "झाला", "आले", "होते", "माझे", "माझ्या", "ठाणे", "पुणे", "मुंबई", "तक्रार", "गाडी"]
            if current_lang in ("mr", "mr-IN") or any(m in text for m in marathi_markers):
                return "mr-IN", "Vasudha"
            return "hi-IN", "Shivani"

        return current_lang or "en-IN", "Shivani"
