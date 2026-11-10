import io
import os
import wave
import unittest
from unittest.mock import Mock, patch

from starlette.testclient import TestClient

from backend.core.gnani_client import GnaniClient, GnaniAPIError
from backend import server


def wav_bytes(seconds=1):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b"\x00\x00" * int(16000 * seconds))
    return buffer.getvalue()


class SpeechClientTests(unittest.TestCase):
    def test_stt_uses_v3_indic_auto_and_safe_error(self):
        client = GnaniClient(api_key="test-key")
        audio_path = os.path.join("runtime_tmp", "voice_unit_test.wav")
        os.makedirs("runtime_tmp", exist_ok=True)
        try:
            with open(audio_path, "wb") as audio:
                audio.write(wav_bytes())
            with patch("backend.core.gnani_client.requests.post") as post:
                post.return_value = Mock(status_code=200, json=lambda: {"success": True, "transcript": "नमस्ते"})
                result = client.transcribe(audio_path)
                self.assertEqual(result["transcript"], "नमस्ते")
                fields = post.call_args.kwargs["data"]
                self.assertEqual(fields["model"], "prisma-v3.0")
                self.assertEqual(fields["language_code"], "indic-auto")
                self.assertEqual(fields["format"], "codemix")
                post.return_value = Mock(status_code=403, text="secret provider response")
                with self.assertRaises(GnaniAPIError) as error:
                    client.transcribe(audio_path)
                self.assertEqual(error.exception.category, "authentication_rejected")
                self.assertNotIn("secret provider response", str(error.exception))
        finally:
            os.unlink(audio_path)

    def test_tts_validates_voice_and_language(self):
        client = GnaniClient(api_key="test-key")
        with self.assertRaises(ValueError):
            client.synthesize("Hello", voice="not-a-v3-voice")
        with self.assertRaises(ValueError):
            client.synthesize("Hello", language="not-a-language")

    def test_tts_uses_auto_language_and_v3_voice(self):
        client = GnaniClient(api_key="test-key")
        output_path = os.path.join("runtime_tmp", "tts_unit_test.wav")
        try:
            with patch("backend.core.gnani_client.requests.post") as post:
                post.return_value = Mock(status_code=200, content=wav_bytes())
                result = client.synthesize("नमस्ते", output_path=output_path)
                payload = post.call_args.kwargs["json"]
                self.assertEqual(payload["model"], "timbre-v3.0")
                self.assertEqual(payload["voice"], "Shivani")
                self.assertEqual(payload["language"], "auto")
                self.assertEqual(result["bytes"], len(wav_bytes()))
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class VoiceRouteTests(unittest.TestCase):
    def setUp(self):
        self.original_client = server.client
        self.original_auth = server._speech_auth
        self.fake = Mock()
        self.fake.transcribe.return_value = {
            "success": True,
            "transcript": "मेरी दुकान हटाई जा रही है",
            "model": "prisma-v3.0",
            "detected_language_code": "hi-IN",
        }
        server.client = self.fake
        server._speech_auth = "unverified"
        self.web = TestClient(server.app)

    def tearDown(self):
        self.web.close()
        server.client = self.original_client
        server._speech_auth = self.original_auth
        server._audio_cache.clear()

    def test_transcribe_returns_editable_text_and_detected_language(self):
        response = self.web.post("/api/transcribe", files={"audio": ("voice.wav", wav_bytes(), "audio/wav")})
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["transcript"], "मेरी दुकान हटाई जा रही है")
        self.assertEqual(body["stt_telemetry"]["detected_language_code"], "hi-IN")
        self.assertEqual(self.fake.transcribe.call_args.kwargs["language_code"], "indic-auto")
        self.assertEqual(server._speech_auth, "verified")

    def test_rest_limit_and_invalid_language_are_rejected_before_provider(self):
        too_long = self.web.post("/api/transcribe", files={"audio": ("voice.wav", wav_bytes(31), "audio/wav")})
        self.assertEqual(too_long.status_code, 413)
        invalid = self.web.post("/api/transcribe", data={"language_code": "xx-XX"}, files={"audio": ("voice.wav", wav_bytes(), "audio/wav")})
        self.assertEqual(invalid.status_code, 422)
        self.fake.transcribe.assert_not_called()

    def test_audio_url_is_short_lived_and_not_cached_by_browser(self):
        url = server._cache_audio(wav_bytes())
        self.assertTrue(url.startswith("/api/audio/"))
        response = self.web.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["cache-control"], "private, no-store")
        token = url.rsplit("/", 1)[-1]
        server._audio_cache[token] = (0, wav_bytes())
        self.assertEqual(self.web.get(url).status_code, 404)


if __name__ == "__main__":
    unittest.main()
