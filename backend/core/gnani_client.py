import os
import time
import requests
import json
from typing import Dict, Any, List, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                if "=" in line and not line.lstrip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ.setdefault(key, value)

GNANI_API_KEY = os.getenv("GNANI_API_KEY")
GNANI_BASE_URL = os.getenv("GNANI_BASE_URL", "https://api.vachana.ai")

V3_VOICES = {
    "Avinash", "Shivani", "Lakshmi", "Kalpana", "Shubham", "Prakash",
    "Devansh", "Yashraj", "Chetana", "Vasudha", "Riyaa", "Tarika", "Harshad"
}
TTS_LANGUAGES = {
    "auto", "hi-IN", "en-IN", "hi-en", "ta-IN", "te-IN", "kn-IN",
    "ml-IN", "mr-IN", "pa-IN", "bn-IN", "gu-IN"
}

class GnaniAPIError(RuntimeError):
    def __init__(self, service: str, category: str, status_code: Optional[int] = None):
        self.service = service
        self.category = category
        self.status_code = status_code
        super().__init__(f"{service} {category}" + (f" (HTTP {status_code})" if status_code else ""))

def _response_error(service: str, status_code: int) -> GnaniAPIError:
    if status_code in (401, 403):
        category = "authentication_rejected"
    elif status_code == 429:
        category = "rate_limited"
    elif status_code >= 500:
        category = "provider_unavailable"
    else:
        category = "request_rejected"
    return GnaniAPIError(service, category, status_code)

class GnaniClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or GNANI_API_KEY
        self.base_url = base_url or GNANI_BASE_URL
        if not self.api_key:
            raise ValueError("GNANI_API_KEY is not set. Ensure it is in your .env file.")

        self.headers = {
            "X-API-Key-ID": self.api_key
        }

    def transcribe(
        self,
        audio_file_path: str,
        language_code: str = "indic-auto",
        model: str = "prisma-v3.0",
        keyterms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Live Synchronous Speech-to-Text using Gnani Prisma ASR via X-API-Key-ID.
        """
        endpoint = f"{self.base_url}/stt/v3"
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        default_legal_terms = [
            "Section 3", "TVC", "Town Vending Committee", "vending certificate",
            "FIR", "Zero FIR", "Article 25", "BNS", "BNSS", "MACT", "insurance claim",
            "police", "BMC", "survey", "PM SVANidhi", "dashcam"
        ]
        boost_terms = keyterms or default_legal_terms

        start_time = time.time()
        with open(audio_file_path, "rb") as f:
            files = {
                "audio_file": (os.path.basename(audio_file_path), f, "audio/wav")
            }
            data = {
                "language_code": language_code,
                "model": model,
                "format": "codemix",
                "keyterms": json.dumps(boost_terms, ensure_ascii=False)
            }
            try:
                response = requests.post(endpoint, headers=self.headers, files=files, data=data, timeout=60)
            except requests.RequestException as err:
                raise GnaniAPIError("stt", "network_unavailable") from err

        elapsed = time.time() - start_time

        if response.status_code == 200:
            try:
                res_json = response.json()
            except ValueError as err:
                raise GnaniAPIError("stt", "invalid_response") from err
            if not isinstance(res_json, dict) or res_json.get("success") is False:
                raise GnaniAPIError("stt", "invalid_response")
            res_json["client_elapsed_seconds"] = round(elapsed, 3)
            return res_json
        else:
            raise _response_error("stt", response.status_code)

    def synthesize(
        self,
        text: str,
        language: str = "auto",
        voice: str = "Shivani",
        model: str = "timbre-v3.0",
        speed: float = 1.0,
        sample_rate: int = 16000,
        output_path: str = "audio_samples/tts_output.wav"
    ) -> Dict[str, Any]:
        """
        Live Text-to-Speech synthesis using Gnani Timbre TTS via X-API-Key-ID.
        Supported voices for timbre-v3.0:
        Shivani, Lakshmi, Kalpana, Chetana, Vasudha, Riyaa, Tarika, Avinash, Shubham, Prakash, Devansh, Yashraj, Harshad
        """
        endpoint = f"{self.base_url}/api/v1/tts/inference"
        if model != "timbre-v3.0" or voice not in V3_VOICES:
            raise ValueError("Choose a supported Timbre v3.0 voice.")
        if language not in TTS_LANGUAGES:
            raise ValueError("Choose a supported TTS language.")
        if not 0.85 <= speed <= 1.15:
            raise ValueError("TTS speed must be between 0.85 and 1.15.")
        payload = {
            "text": text,
            "voice": voice,
            "model": model,
            "language": language,
            "speed": speed,
            "audio_config": {
                "encoding": "linear_pcm",
                "container": "wav",
                "sample_rate": sample_rate
            }
        }
        headers = {
            **self.headers,
            "Content-Type": "application/json"
        }

        start_time = time.time()
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        except requests.RequestException as err:
            raise GnaniAPIError("tts", "network_unavailable") from err
        elapsed = time.time() - start_time

        if response.status_code == 200:
            if not response.content.startswith(b"RIFF") or response.content[8:12] != b"WAVE":
                raise GnaniAPIError("tts", "invalid_response")
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)
            return {
                "audio_path": output_path,
                "bytes": len(response.content),
                "elapsed_seconds": round(elapsed, 3),
                "voice": voice,
                "model": model
            }
        else:
            raise _response_error("tts", response.status_code)

if __name__ == "__main__":
    client = GnaniClient()
    masked_key = client.api_key[:8] + "..." + client.api_key[-6:] if client.api_key else "NONE"
    print("GnaniClient ready with API key:", masked_key)
