import os
import time
import requests
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

GNANI_API_KEY = os.getenv("GNANI_API_KEY")
GNANI_BASE_URL = os.getenv("GNANI_BASE_URL", "https://api.vachana.ai")

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
        language_code: str = "hi-IN",
        model: str = "prisma-v2.5",
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
                "keyterms": json.dumps(boost_terms)
            }
            response = requests.post(
                endpoint,
                headers=self.headers,
                files=files,
                data=data,
                timeout=60
            )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            res_json = response.json()
            res_json["client_elapsed_seconds"] = round(elapsed, 3)
            return res_json
        else:
            raise RuntimeError(
                f"Gnani Prisma STT API returned HTTP {response.status_code}: {response.text}"
            )

    def synthesize(
        self,
        text: str,
        language: str = "hi-IN",
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
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
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
            raise RuntimeError(
                f"Gnani Timbre TTS API returned HTTP {response.status_code}: {response.text}"
            )

if __name__ == "__main__":
    client = GnaniClient()
    masked_key = client.api_key[:8] + "..." + client.api_key[-6:] if client.api_key else "NONE"
    print("GnaniClient ready with API key:", masked_key)
