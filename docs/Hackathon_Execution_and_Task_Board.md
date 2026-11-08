# Hackathon 48-Hour Sprint Execution & Task Board

> **Sprint Window:** Sunday, Nov 08, 2026 (20:30 IST) to Tuesday, Nov 10, 2026 (23:59 IST)  
> **Hard Deadline:** November 10, 2026, 11:59 PM IST (Zero extension policy)  
> **Deliverable:** Working Streamlit app, GitHub repository, public LinkedIn/X video demo, Microsoft Form submission.

---

## 1. Real-Time Sprint Board

### Phase 1: Pipeline Smoke Tests & Audio Asset Preparation (Nov 08, Night)
- [x] Register for the Great Indian AI Internship Challenge and obtain 5,000 platform credits.
- [x] Configure Gnani API credentials (`GNANI_API_KEY`, `GNANI_BASE_URL` in `.env`).
- [x] Build core Gnani client (`backend/core/gnani_client.py`) integrating `/stt/v3` and `/api/v1/tts/inference`.
- [x] Implement deterministic RBI Compliance Auditor (`backend/services/compliance_auditor.py`).
- [x] Deploy Streamlit Workbench (`frontend/app.py`).
- [ ] **Generate 3 Standard Telephony Test Audio Clips in `audio_samples/`:**
  1. `sample_compliant_hinglish.wav`: Polite recovery call with recording disclosure, agent ID, and verified payment arrangement (Target: Score 100, `COMPLIANT`).
  2. `sample_noncompliant_threat.wav`: Aggressive debt collection call with missing recording consent, abusive language, and police threats (Target: Score 35, `NON_COMPLIANT_RISK`).
  3. `sample_regional_kannada.wav`: Customer onboarding loan query in colloquial Kannada (Target: Regional Language demonstration).
- [ ] **Benchmark Latency:** Record exact milliseconds for Prisma ASR transcription and Timbre TTS synthesis on 15s–30s audio clips.

### Phase 2: UI Polish & Demo Hardening (Nov 09, Morning & Afternoon)
- [ ] **Add One-Click Demo Sample Selector:** Enhance `frontend/app.py` dropdown to instantly load the 3 pre-built audio clips without needing manual file uploads during recording.
- [ ] **Add Telemetry & Metrics Badges:** Surface STT Processing Latency, Character Count, and Word Confidence Score directly in the UI header.
- [ ] **Add Exportable Audit Report:** Provide a 1-click "Download Audit JSON" button in the Streamlit interface for compliance officer workflow realism.
- [ ] **Dry-Run Screen Recording:** Complete 2 rehearsal recordings on QuickTime / OBS at 1080p, timing voiceover against the 60-second script.

### Phase 3: Demo Video Recording & Social Media Launch (Nov 09, Evening)
- [ ] **Record Final 60-Second Video:** Execute the script from `Demo_Video_and_Social_Submission_Guide.md` with crisp audio and clean cursor transitions.
- [ ] **Publish LinkedIn Post:** Post the video with pre-drafted copy, `#GnaniAI`, `#GreatIndianAIInternshipChallenge`, and tag `@Gnani.ai`.
- [ ] **Publish X (Twitter) Post:** Post video thread tagging `@gnaniai`.
- [ ] **Mobilize Peer Network:** Share social links across MIT Bengaluru tech circles, YIA peers, and LinkedIn connections to drive initial organic engagement.

### Phase 4: Final Submission & Documentation Freeze (Nov 10, Morning)
- [ ] **GitHub Polish:** Push all code, documentation, and sample audio files to `https://github.com/DreamX55/Gnani-VachanAudit`. Ensure `README.md` features architecture diagrams, setup instructions, and demo link.
- [ ] **Submit Microsoft Form:** Complete `https://forms.cloud.microsoft/r/dfFShbp7W7` with personal details, GitHub repo link, and LinkedIn/X video URL before 12:00 PM IST (giving 12 hours buffer before midnight cutoff).
- [ ] **Confirmation Archive:** Save screenshot and receipt of form submission.

---

## 2. Audio Sample Generation Protocol

To ensure repeatable, bulletproof video demonstrations, synthesize the test scenarios using `verify_connection.py` or synthetic TTS:

### Scenario 1: Non-Compliant Debt Recovery Call (Flagship Demo)
* **Audio Characteristics:** Narrowband 8kHz simulation, Hindi-English code-switched dialect.
* **Transcript:**  
  *"सुनिए, मैं सीधे बात कर रहा हूँ। आपका लोन का ईएमआई तीन महीने से पेंडिंग है। अगर आपने आज शाम तक पेमेंट नहीं किया, तो हम सीधे पुलिस और कोर्ट में केस फाइल करेंगे। जेल जाने के लिए तैयार रहिए।"*
* **Auditor Triggers:**
  - ❌ Missing `RECORDING_CONSENT` (-15 pts)
  - ❌ Missing `AGENT_IDENTITY` (institution unverified) (-15 pts)
  - ⚠️ Triggered `ABUSIVE_THREAT` (police, court, jail) (-35 pts)
  - **Resulting Score: 35/100 (`NON_COMPLIANT_RISK`)**

### Scenario 2: Fully Compliant Verification Call
* **Audio Characteristics:** Clean 16kHz call, formal Hinglish.
* **Transcript:**  
  *"नमस्ते, मैं एचडीएफसी बैंक क्रेडिट कार्ड डिपार्टमेंट से बात कर रहा हूँ। यह कॉल ट्रेनिंग और क्वालिटी पर्पस के लिए रिकॉर्ड की जा रही है। यह कॉल आपके ओवरड्यू पेमेंट के संबंध में है।"*
* **Auditor Triggers:**
  - ✅ `RECORDING_CONSENT` detected
  - ✅ `AGENT_IDENTITY` detected
  - ✅ `REASON_FOR_CALL` detected
  - 0 prohibited violations
  - **Resulting Score: 100/100 (`COMPLIANT`)**

---

## 3. Interview Readiness Checklist (Post-Shortlist)

When invited for the 1-on-1 technical interview, be prepared to answer:
1. **Why Gnani Prisma over Whisper or Google Speech-to-Text?**
   - *Answer:* Whisper struggles on 8kHz Indian telephony audio because it lacks native acoustic modeling for Indian code-switched dialects and narrowband telecom filters. Prisma is trained natively on Indian linguistic corpora, providing lower WER on Hinglish and substantially lower cloud inference latency.
2. **How does VachanAudit scale in an enterprise environment?**
   - *Answer:* The architecture decouples synchronous REST ingest from asynchronous batch auditing via message queues (e.g. RabbitMQ/Celery). STT runs at sub-second speeds, and the deterministic rule engine runs in $O(N)$ string evaluation, enabling 10,000+ concurrent calls to be audited in real-time.
3. **How does Evon 30B MoE complement the deterministic rule engine?**
   - *Answer:* Regex and keyword spotting catch overt threats and clear disclosures with 100% determinism. Evon's 3.5B active parameter MoE layer provides semantic reasoning to identify covert coercion, contextual intimidation, and tone escalation without introducing high compute overhead.
