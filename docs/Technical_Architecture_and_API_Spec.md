# Technical Architecture & API Specification

> **Project:** VachanAudit — Indic Telephony Compliance & Quality Assurance Engine  
> **Target Framework:** Gnani Sovereign Indic AI Stack (Prisma STT, Timbre TTS, Evon MoE LLM)  
> **Domain:** BFSI Telephony Compliance, Indian Narrowband Speech Processing, Automated QA

---

## 1. System Architecture Overview

```
                                      +---------------------------------------------+
                                      |   Inbound Audio (8kHz/16kHz Narrowband)     |
                                      |   - Debt Recovery / Loan Tele-marketing     |
                                      |   - Code-Mixed (Hinglish, Kanglish, English)|
                                      +----------------------+----------------------+
                                                             |
                                                             v
                                      +---------------------------------------------+
                                      |        Gnani Prisma ASR (v2.5 / v3.0)       |
                                      |   - Endpoint: /stt/v3                       |
                                      |   - Auto-Language ID (indic-auto)           |
                                      |   - Domain Keyterms Boosting                |
                                      +----------------------+----------------------+
                                                             |
                                           Full Transcript (Text / JSON)
                                                             |
                                                             v
                      +--------------------------------------+--------------------------------------+
                      |                                                                             |
                      v                                                                             v
+---------------------------------------------+                             +-----------------------------------------------+
|    Layer 1: Deterministic Compliance Engine |                             |      Layer 2: Semantic LLM Reasoning (Evon)   |
|    - RBI Fair Practices Code                |                             |      - Gnani Evon v3.3 30B MoE (3.5B active)  |
|    - Mandatory Disclosures (Consent, ID)    |                             |      - Implicit Threat & Coercion Detection   |
|    - Prohibited Words (Threats, Jail)       |                             |      - Contextual Sarcasm & Intimidation Check|
|    - Deterministic 0-100 Scoring            |                             |      - Automated Compliant Script Synthesis   |
+---------------------+-----------------------+                             +-----------------------+-----------------------+
                      |                                                                             |
                      +--------------------------------------+--------------------------------------+
                                                             |
                                            Consolidated Audit Payload
                                                             |
                      +--------------------------------------+--------------------------------------+
                      |                                                                             |
                      v                                                                             v
+---------------------------------------------+                             +-----------------------------------------------+
|      Interactive Operational Workbench      |                             |        Gnani Timbre TTS (v3.0 Engine)         |
|      - Streamlit High-Performance UI        |                             |        - Endpoint: /api/v1/tts/inference      |
|      - Risk Status Badges (Red/Orange/Green)|                             |        - Voices: Shivani, Priya, Rahul        |
|      - Real-Time Waveform & Flag Explorer   |                             |        - Audio Briefing for Call Supervisors  |
+---------------------------------------------+                             +-----------------------------------------------+
```

---

## 2. Speech-to-Text Pipeline (Gnani Prisma ASR)

### API Contract
* **Base URL:** `https://api.vachana.ai`
* **Endpoint:** `POST /stt/v3`
* **Authentication Header:** `X-API-Key-ID: <GNANI_API_KEY>`
* **Content-Type:** `multipart/form-data`

### Request Parameters

| Parameter | Type | Required | Description | Value in VachanAudit |
| :--- | :--- | :--- | :--- | :--- |
| `audio_file` | Binary | Yes | Audio payload (WAV, MP3, FLAC, M4A) | Raw telephony audio (8kHz/16kHz) |
| `model` | String | No | Model architecture version | `prisma-v3.0` (fallback to `prisma-v2.5`) |
| `language_code` | String | Yes | Indic language locale or auto detector | `indic-auto`, `hi-IN`, `en-IN`, `kn-IN`, `te-IN` |
| `format` | String | No | Formatting and transcription style | `codemix` (preserves Hinglish phrasing) |
| `keyterms` | String | No | Comma-separated or JSON array of domain terms | `["EMI", "RBI", "disclaimer", "recording", "loan", "settlement"]` |

### Raw Response Schema
```json
{
  "transcript": "नमस्ते, मैं एचडीएफसी बैंक से बात कर रहा हूँ। आपका ईएमआई पेमेंट पेंडिंग है। This call is recorded for quality purposes.",
  "confidence": 0.942,
  "detected_language": "hi-IN",
  "utterances": [
    {
      "start_time": 0.0,
      "end_time": 4.2,
      "text": "नमस्ते, मैं एचडीएफसी बैंक से बात कर रहा हूँ।"
    },
    {
      "start_time": 4.5,
      "end_time": 7.8,
      "text": "This call is recorded for quality purposes."
    }
  ]
}
```

### Telephony Acoustic Optimization
Telephony audio routed through Indian public switched telephone networks (PSTN) or VoIP typically uses G.711 or AMR codecs bandlimited to 300Hz–3400Hz (8kHz sampling rate). Generic Western ASR models (e.g. Whisper) experience severe Word Error Rate (WER) degradation on 8kHz Indian telephony due to lack of high-frequency acoustic cues and non-standard English accents. Prisma v2.5/v3.0 uses acoustic representations specifically pre-trained on noisy Indian cellular streams, maintaining robust token extraction under low SNR (Signal-to-Noise Ratio).

---

## 3. Compliance Rule Engine (Deterministic Layer)

The compliance auditor operates as an uncompromising, deterministic validation barrier modeled directly on the **Reserve Bank of India (RBI) Fair Practices Code for Lenders and Recovery Agents (Master Direction - DNBR.PD.008/03.10.119/2016-17)**.

### Rule Hierarchy

```
                               [Audit Ingest]
                                      │
          ┌───────────────────────────┴───────────────────────────┐
          ▼                                                       ▼
[Mandatory Disclosures]                                 [Prohibited Conduct]
  ├─ RECORDING_CONSENT (-15 pts)                          ├─ ABUSIVE_THREAT (-35 pts)
  ├─ AGENT_IDENTITY (-15 pts)                             ├─ FALSE_INTEREST_RATE (-20 pts)
  └─ REASON_FOR_CALL (-15 pts)                            └─ PRESSURE_TIMELIMIT (-20 pts)
          │                                                       │
          └───────────────────────────┬───────────────────────────┘
                                      ▼
                        Score = 100 - Penalties
                        [0 to 100 Health Score]
```

#### 1. Mandatory Disclosures (Omission Penalty: 15 pts each)
* **`RECORDING_CONSENT`:** Agent must inform customer that the call is being recorded.
  - Matches: `call is recorded`, `कॉल रिकॉर्ड`, `quality purposes`, `recording`.
* **`AGENT_IDENTITY`:** Agent must identify themselves and their lending institution.
  - Matches: `calling from`, `से बात कर रहा`, `से बोल रहा`, `bank`, `finance`, `agency`.
* **`REASON_FOR_CALL`:** Agent must state the loan/card account reason.
  - Matches: `regarding your`, `के संबंध में`, `loan`, `emi`, `किस्त`, `खाता`, `overdue`.

#### 2. Prohibited Conduct (Violation Penalties: 20–35 pts each)
* **`ABUSIVE_THREAT` (Severity: HIGH, -35 pts):** Coercion, threats of physical harm, police, or jail.
  - Matches: `police`, `court`, `जेल`, `धमकी`, `बकवास`, `चोर`, `मारूंगा`, `सजा`, `fucker`, `bastard`.
* **`FALSE_INTEREST_RATE` (Severity: MEDIUM, -20 pts):** Deceptive marketing or unapproved zero-interest claims.
  - Matches: `0% interest`, `बिना ब्याज`, `zero percent`, `free loan`.
* **`PRESSURE_TIMELIMIT` (Severity: MEDIUM, -20 pts):** Illegal immediate coercion.
  - Matches: `अभी के अभी`, `right this second`, `immediately or else`.

### Scoring Function
$$\text{Score} = \max\left(0, \, 100 - \sum_{d \in D_{\text{missing}}} 15 - \sum_{v \in V_{\text{found}}} \text{Penalty}(v)\right)$$

* **Score $\ge 85$:** `COMPLIANT` (Green)
* **$60 \le \text{Score} < 85$:** `NEEDS_REVIEW` (Amber)
* **$\text{Score} < 60$:** `NON_COMPLIANT_RISK` (Red)

---

## 4. Text-to-Speech Engine (Gnani Timbre TTS)

### API Contract
* **Endpoint:** `POST /api/v1/tts/inference`
* **Authentication Header:** `X-API-Key-ID: <GNANI_API_KEY>`
* **Content-Type:** `application/json`

### Request Payload
```json
{
  "text": "कॉल ऑडिट समाप्त हुआ। यह कॉल नॉन-कम्प्लायंट है। एजेंट ने रिकॉर्डिंग डिस्क्लोजर नहीं दिया और धमकी भरे शब्दों का इस्तेमाल किया।",
  "voice": "Shivani",
  "model": "timbre-v3.0",
  "language": "hi-IN",
  "speed": 1.0,
  "audio_config": {
    "encoding": "linear_pcm",
    "container": "wav",
    "sample_rate": 16000
  }
}
```

### Voice Catalog
* **`Shivani`:** Female, Hindi / Indian English. Authoritative, neutral articulation suitable for formal executive audits.
* **`Priya`:** Female, warm conversational cadence. Suitable for customer-facing agent debriefs.
* **`Rahul`:** Male, baritone, formal professional tone.

---

## 5. Sovereign Reasoning Layer (Gnani Evon v3.3 30B MoE)

* **Repository:** `gnani/gnani-evon-v3.3-30B-A3B` on Hugging Face.
* **Architecture:** Hybrid Mamba–Transformer Mixture-of-Experts with 30 Billion total parameters and 3.5 Billion active parameters per token.
* **Context Window:** 128,000 tokens.
* **Indic Native Tokenizer:** High-compression ratio for Devanagari, Dravidian scripts, and Romanized code-mixing, eliminating standard Byte-Pair Encoding bloat.
* **Application in VachanAudit:**
  - Evaluates contextual coercion where an agent avoids explicit blacklisted words but applies implicit intimidation (e.g. "We know where your children go to school").
  - Auto-synthesizes a compliant remediation script showing how the agent should have handled the situation legally.
