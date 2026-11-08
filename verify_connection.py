import os
import wave
import struct
import math
from backend.core.gnani_client import GnaniClient

def generate_sample_wav(filename: str = "audio_samples/test_sample.wav", duration: float = 2.0, sample_rate: int = 16000):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    n_samples = int(duration * sample_rate)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        # Generate a gentle 440 Hz tone
        for i in range(n_samples):
            val = int(16000.0 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
            data = struct.pack('<h', val)
            wav_file.writeframesraw(data)
    print(f"[✓] Created synthetic test WAV: {filename}")

def main():
    print("=== Testing Gnani.ai API Credentials ===")
    try:
        client = GnaniClient()
        print(f"[✓] Loaded API Key: {client.api_key[:12]}...{client.api_key[-8:]}")

        # 1. Test Text-to-Speech (TTS)
        print("\n--- Testing TTS Endpoint (/api/v1/tts/inference) ---")
        tts_output = "audio_samples/tts_test_output.wav"
        client.synthesize(
            text="नमस्ते, यह ज्ञानि एआई का परीक्षण संदेश है।",
            language="hi-IN",
            output_path=tts_output
        )
        if os.path.exists(tts_output) and os.path.getsize(tts_output) > 0:
            print(f"[✓] TTS Success! Audio written to {tts_output} ({os.path.getsize(tts_output)} bytes)")
        else:
            print("[!] TTS returned empty file.")

        # 2. Test Speech-to-Text (STT)
        print("\n--- Testing STT Endpoint (/stt/v3) ---")
        if os.path.exists(tts_output):
            sample_to_transcribe = tts_output
        else:
            sample_to_transcribe = "audio_samples/test_sample.wav"
            generate_sample_wav(sample_to_transcribe)

        print(f"Transcribing {sample_to_transcribe}...")
        stt_result = client.transcribe(sample_to_transcribe, language_code="hi-IN")
        print("[✓] STT Response received:")
        print(stt_result)

    except Exception as e:
        print(f"[✗] Error during verification: {e}")

if __name__ == "__main__":
    main()
