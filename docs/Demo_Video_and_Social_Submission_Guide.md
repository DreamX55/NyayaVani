# Demo Video & Social Submission Guide

> **Target:** The Great Indian AI Internship Challenge by **Gnani.ai**  
> **Hard Deadline:** November 10, 2026, 11:59 PM IST  
> **Target Award Categories:** Best 60-Second Demo, Crowd Favourite, Real-World Impact, Noisy Telephonic Audio  
> **Submission URL:** [Microsoft Project Submission Form](https://forms.cloud.microsoft/r/dfFShbp7W7)

---

## 1. 60-Second High-Impact Video Demo Script

This script is structured to maximize retention, demonstrate live working software, and prove compliance with Gnani's model requirements in under 60 seconds.

| Timestamp | Visual Screen State | Spoken Voiceover / Audio Action |
| :--- | :--- | :--- |
| **0:00 – 0:10** | Camera on speaker or screen showing RBI headline: "Indian banks process 50M+ debt collection calls every month. QA teams manually audit less than 2%, leaving lenders blind to severe RBI regulatory penalties." | *"Indian BFSI call centers handle over 50 million recovery calls a month, but less than 2% are ever audited. When recovery agents use illegal intimidation or skip mandatory disclosures, banks face multi-crore RBI penalties. Here is VachanAudit."* |
| **0:10 – 0:25** | Screen switches to VachanAudit Streamlit UI. Click **"Or use pre-generated test audio"** or upload `hinglish_recovery_call.wav`. Click **"Transcribe & Audit Call"**. | *"We ingest an 8kHz noisy narrowband phone call in code-switched Hinglish. In under 500 milliseconds, Gnani's Prisma v2.5 ASR transcribes the speech with high accuracy, preserving colloquial Hindi-English code-mixing."* |
| **0:25 – 0:42** | Camera zooms into the Audit Card. Screen shows Red Status Badge: `NON_COMPLIANT_RISK (Score: 35/100)`. Highlight: Missing `RECORDING_CONSENT`, Detected `ABUSIVE_THREAT` ("पुलिस और कोर्ट"). | *"Our compliance engine evaluates the transcript against the RBI Fair Practices Code. Notice how it instantly flags two critical failures: the agent failed to provide recording consent, and issued an illegal police threat. The call is flagged high risk."* |
| **0:42 – 0:54** | Click **"Synthesize Voice Summary"**. The audio player renders and plays Timbre v3.0 voice (`Shivani`). | *"Finally, Gnani's Timbre v3.0 TTS synthesizes an immediate regional voice briefing for compliance officers, enabling instant remediation before regulators step in."* |
| **0:54 – 1:00** | Screen displays GitHub repo and sovereign Indic architecture diagram. | *"100% automated call audit powered entirely by Gnani AI's sovereign Indic stack. Built by Jonath Jimmi for the Great Indian AI Internship Challenge."* |

---

## 2. LinkedIn Post Copy (Ready to Publish)

```markdown
Indian banks and NBFCs process over 50 million debt collection and loan customer calls every single month.

Yet, traditional quality assurance teams review less than 2% of recorded calls manually.

The cost of that 98% blindspot? Severe regulatory penalties under the RBI Fair Practices Code for unapproved harassment, coercive threats, or omitting mandatory call recording disclosures.

To solve this, I built VachanAudit for the Great Indian AI Internship Challenge by Gnani.ai.

VachanAudit is an automated quality assurance and regulatory compliance engine engineered specifically for noisy Indian enterprise telephony:

1. High-Accuracy Indic STT: Ingests 8kHz narrowband audio and transcribes code-switched Hinglish and regional dialects with sub-500ms latency using Gnani Prisma ASR.
2. Deterministic RBI Compliance Engine: Evaluates every transcript against RBI guidelines—verifying agent identity, consent disclosures, and flagging abusive threats or false interest rate promises.
3. Voice Debrief Generation: Synthesizes immediate natural voice briefings for compliance supervisors using Gnani Timbre TTS in regional voices.

By replacing manual sampling with full-volume automated auditing, VachanAudit brings 100% compliance visibility to Indian enterprise telephony.

Check out the 60-second demo below showing a live Hinglish recovery call audit.

Codebase & Documentation: https://github.com/DreamX55/Gnani-VachanAudit

#GnaniAI #GreatIndianAIInternshipChallenge #VoiceAI #SovereignAI #SpeechAI #FinTech #ArtificialIntelligence #MachineLearning #IndicAI
```

---

## 3. X (Twitter) Post Copy (Ready to Publish)

```markdown
Built VachanAudit for the @gnaniai Great Indian AI Internship Challenge 🎙️🇮🇳

Indian call centers review <2% of recovery calls, exposing lenders to heavy RBI fines. VachanAudit automates 100% call auditing using Gnani's sovereign Indic stack:

- Prisma ASR: Sub-second 8kHz telephony transcription
- Compliance Engine: Real-time RBI Fair Practices scoring
- Timbre TTS: Automated regional supervisor briefings

Demo video below 👇

#GnaniAI #GreatIndianAIInternshipChallenge
```

---

## 4. Microsoft Form Submission Blueprint

When submitting at `https://forms.cloud.microsoft/r/dfFShbp7W7`, use the following pre-formatted answers:

* **Full Name:** Jonath Jimmi
* **Email Address:** `jonath.jimmi@gmail.com` (matching registration)
* **College / University:** Manipal Institute of Technology, Bengaluru (MITB)
* **Degree & Year:** B.Tech Information Technology, 3rd Year (Pre-final year)
* **Project Name:** VachanAudit — Indic Telephony Compliance & QA Engine
* **Project Description (Short):**  
  An automated regulatory compliance and quality assurance pipeline for Indian BFSI telephony. VachanAudit transcribes 8kHz noisy, code-switched Hinglish customer calls using Gnani Prisma ASR, audits them against the RBI Fair Practices Code for illegal harassment and missing disclosures, and synthesizes instant executive audio briefings via Gnani Timbre TTS.
* **Gnani Models Used:**
  - Prisma ASR (`prisma-v2.5` / `prisma-v3.0` via `/stt/v3` REST API)
  - Timbre TTS (`timbre-v3.0` via `/api/v1/tts/inference`)
  - Evon MoE LLM (`gnani/gnani-evon-v3.3-30B-A3B` reasoning framework)
* **GitHub Repository URL:** `https://github.com/DreamX55/Gnani-VachanAudit`
* **Demo Video Post Link (LinkedIn / X):** `<INSERT_LIVE_POST_URL>`
* **Target Award Category:** Noisy Telephonic Audio / Hinglish and Code-Mixed Voice Experiences / Real-World Impact
