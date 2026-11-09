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
            "legal_aid_authority": "Karnataka State Legal Services Authority (KSLSA)",
            "police_emergency": "Bengaluru City Police (112)",
            "vernacular_greeting": "ನಮಸ್ಕಾರ, ನ್ಯಾಯವಾಣಿಗೆ ಸುಸ್ವಾಗತ. ನಿಮ್ಮ ಕಾನೂನು ಸಮಸ್ಯೆಯನ್ನು ಮಾತನಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ ತಿಳಿಸಿ."
        },
        "mumbai": {
            "city_display": "Mumbai, Maharashtra",
            "primary_language": "mr-IN",
            "primary_voice": "Harshad",
            "secondary_language": "hi-IN",
            "secondary_voice": "Shivani",
            "municipal_body": "Brihanmumbai Municipal Corporation (BMC)",
            "legal_aid_authority": "Maharashtra State Legal Services Authority (MSLSA)",
            "police_emergency": "Mumbai Police Control Room (112)",
            "vernacular_greeting": "नमस्कार, न्यायवाणी मध्ये आपले स्वागत आहे. तुमची कायदेशीर समस्या बोला किंवा टाईप करा."
        },
        "delhi": {
            "city_display": "New Delhi, NCR",
            "primary_language": "hi-IN",
            "primary_voice": "Shivani",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "Municipal Corporation of Delhi (MCD)",
            "legal_aid_authority": "Delhi State Legal Services Authority (DSLSA)",
            "police_emergency": "Delhi Police Dispatch (112)",
            "vernacular_greeting": "नमस्कार, न्यायवाणी में आपका स्वागत है। अपनी कानूनी समस्या बोलकर या लिखकर बताएं।"
        },
        "chennai": {
            "city_display": "Chennai, Tamil Nadu",
            "primary_language": "ta-IN",
            "primary_voice": "Kalpana",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "Greater Chennai Corporation (GCC)",
            "legal_aid_authority": "Tamil Nadu State Legal Services Authority (TNSLSA)",
            "police_emergency": "Chennai Police Central Control (112)",
            "vernacular_greeting": "வணக்கம், நியாயவாணிக்கு நல்வரவு. உங்கள் சட்டப் பிரச்சனையைப் பேசி அல்லது தட்டச்சு செய்து தெரிவிக்கவும்."
        },
        "hyderabad": {
            "city_display": "Hyderabad, Telangana",
            "primary_language": "te-IN",
            "primary_voice": "Vasudha",
            "secondary_language": "en-IN",
            "secondary_voice": "Avinash",
            "municipal_body": "Greater Hyderabad Municipal Corporation (GHMC)",
            "legal_aid_authority": "Telangana State Legal Services Authority (TSLSA)",
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
            "legal_aid_authority": "West Bengal State Legal Services Authority (WBSLSA)",
            "police_emergency": "Kolkata Police Headquarters (112)",
            "vernacular_greeting": "নমস্কার, ন্যায়বাণীতে আপনাকে স্বাগতম। আপনার আইনি সমস্যা বলুন বা লিখে জানান।"
        }
    }

    CITY_ALIASES: Dict[str, str] = {
        "bangalore": "bengaluru",
        "blr": "bengaluru",
        "karnataka": "bengaluru",
        "bombay": "mumbai",
        "pune": "mumbai",
        "maharashtra": "mumbai",
        "delhi": "delhi",
        "new delhi": "delhi",
        "noida": "delhi",
        "gurugram": "delhi",
        "gurgaon": "delhi",
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
        Resolves city from name, coordinates, or query text. Defaults to Delhi if unmapped.
        """
        target = "delhi"
        q_lower = (city_or_query or "").lower().strip()

        # Check coordinate bounds if provided
        if coords:
            lat, lon = coords
            if 12.8 <= lat <= 13.2 and 77.4 <= lon <= 77.8:
                target = "bengaluru"
            elif 18.8 <= lat <= 19.3 and 72.7 <= lon <= 73.1:
                target = "mumbai"
            elif 28.4 <= lat <= 28.9 and 76.9 <= lon <= 77.4:
                target = "delhi"
            elif 12.9 <= lat <= 13.2 and 80.1 <= lon <= 80.4:
                target = "chennai"
            elif 17.2 <= lat <= 17.6 and 78.3 <= lon <= 78.6:
                target = "hyderabad"
            elif 22.4 <= lat <= 22.7 and 88.2 <= lon <= 88.5:
                target = "kolkata"

        # Check direct city profiles
        for city_key in cls.CITY_PROFILES.keys():
            if city_key in q_lower:
                target = city_key
                break

        # Check text aliases
        if target == "delhi":
            for alias, mapped_city in cls.CITY_ALIASES.items():
                if alias in q_lower:
                    target = mapped_city
                    break

        return cls.CITY_PROFILES.get(target, cls.CITY_PROFILES["delhi"])

    @classmethod
    def adapt_language_from_text(cls, text: str, current_lang: str) -> Tuple[str, str]:
        """
        Turn 2+ Adaptive Language Detection:
        Inspects Unicode script ranges to dynamically switch language and voice if the user
        replies in a different language than their city default.
        """
        if not text:
            return current_lang, "Shivani"

        # Check Kannada script
        if re.search(r"[\u0C80-\u0CFF]", text):
            return "kn-IN", "Chetana"

        # Check Tamil script
        if re.search(r"[\u0B80-\u0BFF]", text):
            return "ta-IN", "Kalpana"

        # Check Telugu script
        if re.search(r"[\u0C00-\u0C7F]", text):
            return "te-IN", "Vasudha"

        # Check Bengali script
        if re.search(r"[\u0980-\u09FF]", text):
            return "bn-IN", "Riyaa"

        # Check Devanagari script (Hindi / Marathi)
        if re.search(r"[\u0900-\u097F]", text):
            # If current language was Marathi, stay Marathi; otherwise Hindi
            if current_lang == "mr-IN":
                return "mr-IN", "Harshad"
            return "hi-IN", "Shivani"

        # English Latin script fallback
        if current_lang in ["kn-IN", "ta-IN", "te-IN", "bn-IN", "mr-IN"]:
            # Keep current regional if English query in regional context, or use formal English
            return "en-IN", "Avinash"

        return current_lang, "Shivani"
