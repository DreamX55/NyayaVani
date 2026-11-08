# Project Context Setup

This project is for: **The Great Indian AI Internship Challenge (Gnani.ai)** — Building **NyayaVani (न्यायवाणी)**, a Sovereign Indic Voice Legal Navigator & Incident Response Suite powered by Gnani.ai's sovereign AI stack (Prisma STT, Timbre TTS, and Evon LLM).

Who I am: See my `About Me.md` document in this project's files.

---

## What matters here right now:

### Current Goal
Secure an individual 6-month AI Internship offer (stipend up to ₹1,00,000/month starting January 1, 2027) and capture top honors among the 10 specialized award categories (specifically targeting *Noisy Telephonic/Street Audio*, *Hinglish and Vernacular Voice Experiences*, *Real-World Impact*, and *Best 60-Second Demo*, ₹50,000 cash prizes) before the hard cutoff on **November 10, 2026, 11:59 PM IST**.

### Active Projects & Current Build State
* **NyayaVani Repository (`/Users/apple/Documents/Jonath/Hackathons/Gnani Challenge`):**
  - **Prisma v2.5 / v3.0 Speech-to-Text Pipeline (`backend/core/gnani_client.py`):** REST API client integrating with `https://api.vachana.ai/stt/v3` using API key authentication (`X-API-Key-ID`). Custom legal terminology boosting enabled (`keyterms` for Section 3, TVC, FIR, Article 25, BNS, BNSS, MACT).
  - **Core Legal Engine (`backend/services/legal_engine.py`):**
    1. *Tier 1 (Bharat Grassroots Legal Aid):*
       - Street Vendor Eviction Defense: Evaluates arbitrary removal against Section 3(3) and Section 18 of The Street Vendors Act, 2014; synthesizes spoken Loudspeaker Rights Shield in formal Hindi; drafts formal representation to Municipal Commissioner & TVC.
       - Religious Assembly & Community Protection: Identifies violations under Article 25 & 19(1)(b) of the Constitution; maps penal offences under BNS Sections 189, 191, 298, 299, 301, 351; generates mandatory Zero FIR draft under BNSS Section 173(1) and escalation letter to Superintendent of Police under BNSS Section 173(3).
    2. *Tier 2 (NyayaVani Pro - Incident Response & Enterprise Suite):*
       - Motor Vehicle Accident Co-Pilot: Hands-free spoken crash intake assessing liability, collision dynamics, dashcam proof, and injuries under Section 134 Motor Vehicles Act 2019.
       - Automated Insurance Claim Intimation: Assembles General Insurance Council (GIC) / IRDAI standardized claim dossiers for immediate filing.
       - Retainer Attorney Privileged Memorandum: Formats confidential legal dispatch briefs for panel counsel.
    3. *Cryptographic Evidence Preservation:* Oral Affidavit Hasher generating SHA-256 digital record certificates under Section 63 of Bharatiya Sakshya Adhiniyam, 2023 (BSA).
  - **Timbre v3.0 Text-to-Speech Engine (`backend/core/gnani_client.py`):** Synthetic Indic speech generation via `https://api.vachana.ai/api/v1/tts/inference` in `Shivani` (authoritative Hindi for Rights Shields), `Lakshmi` (empathetic Hindi for victim guidance), and `Avinash` (professional English/Hindi for enterprise incident co-pilot).
  - **Interactive Streamlit Dashboard (`frontend/app.py`):** Dual-mode operational workbench featuring 1-click test scenarios, live audio playback, statutory violation breakdowns, spoken rights intercom, and document downloads.

### Deadlines & Hackathon Roadmap
* **November 8, 2026 (Today):** Completed architecture pivot to NyayaVani. Core legal engine built, multi-voice test cases generated, and Streamlit app tested.
* **November 9, 2026:** Record high-impact 60-second screen recording demo highlighting:
  1. Juhu street vendor voice input -> Prisma STT -> Section 3(3) violation flag -> Timbre loudspeaker Rights Shield playback.
  2. Motor accident voice intake -> Automated insurance claim dossier -> Tamper-evident SHA-256 hash.
  Draft and schedule viral LinkedIn and X posts.
* **November 10, 2026 (11:59 PM IST — Hard Deadline, No Extensions):** Publish the demo video publicly on LinkedIn and X tagging Gnani AI and using `#GnaniAI` and `#GreatIndianAIInternshipChallenge`. Mobilize peer network for verified engagement. Submit project via the official Microsoft Form (`https://forms.cloud.microsoft/r/dfFShbp7W7`).
* **Post-Submission:** Technical shortlisting, individual 1-on-1 interviews with Gnani AI engineering leadership, and written internship offers.
* **January 1, 2027:** Scheduled internship commencement.

---

## How to help me in this project:

* **Hackathon execution triage (Speed + Architectural Elegance):**
  Deliver fully functional, drop-in scripts and clean architectural enhancements. Never hand off half-finished diffs or pseudo-code. Keep code clean and free of obvious inline comment clutter. Explain folder structures and architectural choices directly in chat.
* **Direct, grounded communication (No AI fluff):**
  Do not use canned flattery, sycophantic validation, or banned AI vocabulary (*delve, bolster, foster, tapestry, testament, beacon, realm, pivotal, nuanced, robust, multifaceted, crucial, meticulously, additionally*). Avoid triads and negative parallelisms.
* **Strengthen the Indic Voice & Sovereign Moat:**
  Highlight why NyayaVani uniquely exploits Gnani's proprietary strengths: generic Western models fail on noisy Indian street vernacular and 8kHz phone audio, whereas Prisma and Timbre deliver sub-second, accent-accurate performance.
* **Target the Gnani AI scoring and award rubric:**
  Position the project squarely for the top award tracks: *Noisy Telephonic/Street Audio*, *Hinglish and Vernacular Voice Experiences*, *Real-World Impact*, and *Best 60-Second Demo*.
* **Demo and virality first:**
  Ensure all UI elements, audio waveforms, and outputs are visually striking and immediately legible for screen recording. Lead with engineering architecture, statutory ground truth, and clear product utility.
