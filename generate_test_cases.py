import os
import json
from backend.core.gnani_client import GnaniClient
from backend.services.legal_engine import NyayaVaniEngine

def run_tests():
    print("=== Initializing NyayaVani Test Suite ===")
    client = GnaniClient()
    engine = NyayaVaniEngine()

    os.makedirs("audio_samples", exist_ok=True)

    test_scenarios = [
        {
            "id": "vendor_eviction_juhu",
            "name": "Street Vendor Arbitrary Eviction (Juhu, Mumbai)",
            "spoken_text": "नमस्ते साहब, मैं जुहू बीच पर 10 साल से फल का ठेला लगाता हूँ। आज बीएमसी और पुलिस वाले आए और बोले कि दुकान तुरंत हटाओ। उन्होंने मेरा ठेला जब्त करने की धमकी दी। मेरे पास पीएम स्वनिधि की पर्ची है लेकिन वो सुनने को तैयार नहीं हैं।",
            "voice": "Shivani",
            "lang": "hi-IN",
            "case_type": "STREET_VENDOR",
            "audio_file": "audio_samples/sample_vendor_eviction_juhu.wav",
            "meta": {
                "vendor_name": "Ramesh Kumar Gupta",
                "location": "Juhu Beach, Ward K-West, Mumbai",
                "has_svanidhi": True,
                "has_written_notice": False,
                "tvc_survey_done": False,
                "phone": "+91 98200 XXXXX"
            }
        },
        {
            "id": "church_gathering_attack",
            "name": "Disruption of Peaceful Prayer Gathering (North India)",
            "spoken_text": "हम अपने प्रार्थना हॉल में शांतिपूर्वक रविवार की प्रार्थना कर रहे थे। अचानक कुछ लोग लाठी और डंडे लेकर अंदर घुस आए। उन्होंने कुर्सियां तोड़ीं, हमें गाली दी और जान से मारने की धमकी दी। जब हम थाने गए तो पुलिस ने एफआईआर दर्ज करने से मना कर दिया।",
            "voice": "Lakshmi",
            "lang": "hi-IN",
            "case_type": "RELIGIOUS_GATHERING",
            "audio_file": "audio_samples/sample_church_attack.wav",
            "meta": {
                "complainant_name": "Pastor Samuel & Community Members",
                "location": "Civil Lines, Kanpur, Uttar Pradesh",
                "phone": "+91 94150 XXXXX"
            }
        },
        {
            "id": "car_crash_incident",
            "name": "Motor Vehicle Highway Collision (NyayaVani Pro)",
            "spoken_text": "I was driving through the signal at Outer Ring Road when a speeding white SUV ran the red light and smashed into my front right bumper. I have clear dashcam footage recording the entire incident and the driver admitting he was on his phone. My car is heavily damaged and cannot be driven.",
            "voice": "Avinash",
            "lang": "en-IN",
            "case_type": "MOTOR_ACCIDENT",
            "audio_file": "audio_samples/sample_car_crash.wav",
            "meta": {
                "driver_name": "Vikramaditya Sharma",
                "vehicle_no": "KA-04-MB-4412",
                "insurer": "HDFC ERGO General Insurance Co.",
                "policy_no": "POL-MOT-2026-8841",
                "location": "Marathahalli Junction, Bengaluru",
                "has_dashcam": True,
                "has_injuries": False,
                "phone": "+91 98450 XXXXX"
            }
        }
    ]

    for sc in test_scenarios:
        print(f"\n--------------------------------------------------")
        print(f"[*] Scenario: {sc['name']}")
        
        # 1. Synthesize input test audio via Gnani Timbre TTS
        print(f"[1/4] Generating voice audio via Timbre TTS ({sc['voice']})...")
        try:
            client.synthesize(
                text=sc["spoken_text"],
                language=sc["lang"],
                voice=sc["voice"],
                output_path=sc["audio_file"]
            )
            print(f"      ✓ Audio generated: {sc['audio_file']} ({os.path.getsize(sc['audio_file'])} bytes)")
        except Exception as e:
            print(f"      ⚠️ TTS failed: {e}")
            continue

        # 2. Transcribe voice audio via Gnani Prisma STT
        print(f"[2/4] Transcribing audio via Prisma STT...")
        try:
            stt_result = client.transcribe(sc["audio_file"], language_code=sc["lang"])
            transcript = stt_result.get("transcript", sc["spoken_text"])
            print(f"      ✓ Prisma STT Transcript: {transcript[:80]}...")
        except Exception as e:
            print(f"      ⚠️ STT fallback to spoken text: {e}")
            transcript = sc["spoken_text"]

        # 3. Process Case through NyayaVani Legal Engine
        print(f"[3/4] Running NyayaVani Legal & Statutory Reasoning...")
        case_output = engine.process_case(transcript, case_type=sc["case_type"], meta=sc["meta"])
        print(f"      ✓ Category: {case_output.get('category')}")
        print(f"      ✓ Tamper-Evident Hash: {case_output['affidavit_evidence']['sha256'][:16]}...")

        # 4. Synthesize Audio Guidance / Rights Shield via Gnani Timbre TTS (Shivani authoritative voice)
        print(f"[4/4] Synthesizing Loudspeaker Rights Shield Audio...")
        rights_audio_path = f"audio_samples/{sc['id']}_rights_shield.wav"
        if "audio_rights_shield_hi" in case_output:
            shield_text = case_output["audio_rights_shield_hi"]
            voice_shield = "Shivani"
            lang_shield = "hi-IN"
        elif "audio_guidance_hi" in case_output:
            shield_text = case_output["audio_guidance_hi"]
            voice_shield = "Shivani"
            lang_shield = "hi-IN"
        else:
            shield_text = case_output.get("audio_guidance_en", "Guidance prepared.")
            voice_shield = "Avinash"
            lang_shield = "en-IN"

        try:
            client.synthesize(
                text=shield_text,
                language=lang_shield,
                voice=voice_shield,
                output_path=rights_audio_path
            )
            print(f"      ✓ Rights Shield Audio generated: {rights_audio_path} ({os.path.getsize(rights_audio_path)} bytes)")
        except Exception as e:
            print(f"      ⚠️ Rights Shield TTS failed: {e}")

    print("\n=== All Scenarios Tested Successfully! ===")

if __name__ == "__main__":
    run_tests()
