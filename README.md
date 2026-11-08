# NyayaVani (न्यायवाणी) — Sovereign Indic Voice Legal Navigator & Incident Response Suite

> Built for the **Gnani.ai Great Indian AI Internship Challenge (Nov 2026)**  
> Powered by **Prisma ASR**, **Timbre TTS**, and **Evon 30B MoE LLM**

---

## 1. Problem Statement: The Indian Justice Divide

Over 80% of India's population cannot effectively access legal recourse due to illiteracy, linguistic barriers, fear of police/administrative harassment, and ignorance of statutory protections:

1. **Grassroots Vulnerability (Bharat):**
   * **Street Vendors & Hawkers:** Thousands of street hawkers in cities like Mumbai (Juhu, Dadar, Bandra) face illegal arbitrary evictions, extortion, and cart confiscations by municipal ward staff—completely unaware that **Section 3(3) of The Street Vendors Act, 2014** provides an absolute statutory shield against eviction until Town Vending Committee (TVC) surveys are complete.
   * **Minority & Religious Gatherings:** Lawful prayer meetings and peaceful assemblies in North India face targeted disruption, vandalism, and mob intimidation. Victims lack the legal literacy to invoke **Article 25 of the Constitution**, cite applicable **Bharatiya Nyaya Sanhita (BNS)** offences, or demand a mandatory **Zero FIR** under **BNSS Section 173(1)**.
   * **Language & Literacy Barrier:** Victims cannot read legal text or type English forms. They need a system where they can speak in their native tongue and hear back clear, spoken legal guidance.

2. **Enterprise & High-Net-Worth Gap (Commercial Moat):**
   * In motor vehicle crashes and roadside emergencies, drivers experience panic and confusion. Post-accident procedures require rapid evidence collection (dashcams, witness statements), adherence to Section 134 of the Motor Vehicles Act, 2019, and filing claim intimations within strict 24-hour insurance windows.

---

## 2. Solution: NyayaVani (न्यायवाणी)

**NyayaVani** bridges this divide using a sovereign, dual-tier voice-first architecture:

```
                                      [User Voice Ingest]
                            (Noisy Street Hindi / Vernacular / English)
                                               │
                                               ▼
                                   [Gnani Prisma ASR (/stt/v3)]
                              Sub-second transcription + keyterm boosting
                                               │
                                               ▼
                              [NyayaVani Core Legal Engine & Hash]
                         Electronic Record Hash (BSA 2023 Sec 63 / 65B)
                                               │
                        ┌──────────────────────┴──────────────────────┐
                        ▼                                             ▼
        [Tier 1: Bharat Grassroots Aid]               [Tier 2: NyayaVani Pro Suite]
     • Street Vendor Sec 3(3) TVC Shield           • Motor Accident Collision Intake
     • Religious Assembly Art 25 Protection         • Automated Insurance Claim Dossier
     • Mandatory Zero FIR Generator (BNSS 173)     • Attorney Confidential Memorandum
                        │                                             │
                        └──────────────────────┬──────────────────────┘
                                               │
                                               ▼
                                 [Gnani Timbre TTS (/tts/inference)]
                            • Loudspeaker Spoken Rights Shield (Shivani)
                            • Emergency Crisis Voice Briefing (Avinash)
```

---

## 3. Innovative Voice AI Vectors

1. **Loudspeaker Rights Shield (Audio Intercom):** Synthesizes an authoritative, formal legal statement via Gnani Timbre TTS (`Shivani` voice) citing statutory sections (e.g. Section 3(3) Street Vendors Act) that can be broadcasted on loudspeaker directly to inspecting officials.
2. **Cryptographically Signed Oral Affidavit:** Generates a SHA-256 tamper-evident hash of spoken testimony, GPS location, and UTC timestamp, preserving contemporaneous electronic evidence under Section 63 of Bharatiya Sakshya Adhiniyam, 2023 (BSA).
3. **Automated Zero FIR Engine:** Converts conversational vernacular accounts of communal harassment into structured police complaints citing Lalita Kumari v. Govt of UP and BNSS Section 173.
4. **Hands-Free Post-Crash Co-Pilot:** Real-time driver voice intake that compiles vehicle damage, fault parameters, and auto-drafts the General Insurance Council (GIC) claim intimation.

---

## 4. Repository Structure

```
Gnani Challenge/
├── .env                                  # Gnani API Credentials (active)
├── requirements.txt                      # Python dependencies
├── run_app.sh                            # Single-click Streamlit launcher
├── verify_connection.py                  # API handshake test script
├── generate_test_cases.py                # End-to-end voice test runner
├── audio_samples/                        # Synthesized and recorded audio clips
│   ├── sample_vendor_eviction_juhu.wav   # Input: Juhu street vendor speech (Hindi)
│   ├── vendor_eviction_juhu_rights_shield.wav # Output: Loudspeaker Rights Shield (Hindi)
│   ├── sample_church_attack.wav          # Input: Prayer gathering attack speech (Hindi)
│   ├── church_gathering_attack_rights_shield.wav # Output: Spoken guidance & FIR mandate
│   ├── sample_car_crash.wav              # Input: Motor vehicle collision intake (English)
│   └── car_crash_incident_rights_shield.wav # Output: Hands-free emergency briefing
├── backend/
│   ├── core/
│   │   └── gnani_client.py               # Production client for Prisma STT & Timbre TTS
│   └── services/
│       ├── legal_engine.py               # NyayaVani Core Legal & Statutory Logic
│       └── compliance_auditor.py         # Telephony compliance rule auditor
├── docs/                                 # Complete documentation suite
│   ├── NyayaVani_Comprehensive_Architecture_and_Market_Blueprint.md
│   ├── Project Context Setup.md
│   ├── Hackathon_Rules_and_Evaluation_Playbook.md
│   ├── Technical_Architecture_and_API_Spec.md
│   └── Demo_Video_and_Social_Submission_Guide.md
├── frontend/
│   ├── index.html                        # Mondragon Landing + Claude Chat interface
│   └── app.py                            # Streamlit Operations Dashboard
└── ios/                                  # Native iOS Application (SwiftUI)
    ├── project.yml                       # XcodeGen project specification
    ├── NyayaVani.xcodeproj               # Xcode project file
    └── NyayaVani/
        ├── NyayaVaniApp.swift            # SwiftUI App entry point
        ├── Info.plist                    # Mic & ATS permissions
        ├── Theme/
        │   └── ColorTheme.swift          # Dark luxury palette
        ├── Models/
        │   └── LegalModels.swift         # Statutory, telemetry & chat data models
        ├── Services/
        │   ├── APIClient.swift           # Asynchronous REST & multipart API client
        │   └── AudioService.swift        # 16kHz PCM audio recorder & loudspeaker player
        └── Views/
            ├── LandingView.swift         # Mondragon landing view & metrics grid
            ├── ChatView.swift            # Claude-style centered chat interface
            ├── MessageBubbleView.swift   # Audio playback, telemetry & statutory badges
            ├── ArtifactSheetView.swift   # Legal notice & BSA Sec 63 certificate viewer
            └── PresetsModalView.swift    # Preset scenario picker
```

---

## 5. Quickstart

### 1. Launch the Backend & Web Application
```bash
./run_app.sh
```
Open `http://localhost:8501` to access the Mondragon landing page and Claude-style conversational legal assistant.

### 2. Build & Run Native iOS Application
Requirements: macOS with Xcode 15+ installed.
```bash
# Generate / update Xcode project if needed
cd ios
xcodegen generate

# Build from command line or open in Xcode
xcodebuild -project NyayaVani.xcodeproj -scheme NyayaVani -destination 'platform=iOS Simulator,name=iPhone 17' build
open NyayaVani.xcodeproj
```

---

## 6. 60-Second Demo Walkthrough Guide (LinkedIn / X)

1. **0:00 - 0:12:** Hook — 80% of citizens cannot access legal advice due to illiteracy and fear. Introduce *NyayaVani* powered by Gnani AI.
2. **0:12 - 0:28:** Demonstrate **Street Vendor Eviction Defense**: Play raw Hindi vendor audio. Prisma ASR transcribes in sub-second latency. Engine flags Section 3(3) Street Vendors Act violation.
3. **0:28 - 0:42:** Demonstrate **Loudspeaker Rights Shield**: Play Timbre TTS audio broadcast in formal Hindi warning the municipal officer against illegal eviction.
4. **0:42 - 0:54:** Toggle to **NyayaVani Pro**: Show car crash voice intake generating instant GIC insurance claim dossier and SHA-256 electronic affidavit hash.
5. **0:54 - 1:00:** Close with tech stack summary: *Built on Gnani.ai sovereign Indic AI stack*.
