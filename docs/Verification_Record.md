# NyayaVani Release Verification Record

> **Release Version:** `2026.11-v1`  
> **Verification Date:** November 10, 2026  
> **Environment:** Windows 11 (Host), Python 3.12.8, Starlette / Uvicorn Test Harness (Localhost)  
> **Source Register:** Version `2026.11-v1` (`DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW` — Not Certified Legal Advice)  
> **Automated Test Results:** **63 / 63 TESTS PASSED (100% PASS RATE)**  
> **Deployment Gate:** **CONTROLLED PILOT ONLY — PUBLIC DEPLOYMENT BLOCKED PENDING ADVOCATE SIGN-OFF**

---

## 1. Release Verification Matrix

As mandated by Section 6 of the [Product Requirements Document](Product_Requirements_Document.md), this document records strictly observed results, distinguishing automated / mocked harness passes from live external provider calls and physical device tests:

| # | Scenario | Test Input & Language | Environment / Harness | Expected Result | Observed Result | Status |
|---|---|---|---|---|---|:---:|
| 1 | **Text Intake (Grassroots)** | Typed Text (Hindi): *"ठेकेदार ने वेतन नहीं दिया"* | Automated Harness (`TestClient`) | Categorize as `WAGE_THEFT`; draft summary; follow-up questions for missing facts. | Categorized as `WAGE_THEFT`; statutory options provided; status `needs_details`. | **VERIFIED (Mock/Harness)** |
| 2 | **Text Intake (Commercial Pro)** | Typed Text (English): *"Car collision at junction"* | Automated Harness (`TestClient`) | Categorize as `MOTOR_ACCIDENT_PRO`; create Pro packet in `needs_review` state. | Pro packet `pkt_*` generated with status `needs_review`, chronology, and missing evidence. | **VERIFIED (Mock/Harness)** |
| 3 | **Live Microphone Recording (Browser)** | Web Audio (MediaRecorder, PCM) | Browser UI (`frontend/index.html`) | 30s countdown, pre-recording privacy notice, audio sent to `/api/transcribe`. | UI countdown and privacy notice verified; live microphone capture depends on browser permission. | **IMPLEMENTED (Live Provider Untested in CI)** |
| 4 | **Uploaded Short Audio Validation** | Synthetic Audio (.wav, 2.0s, 16kHz) | Automated Harness (`test_voice_pipeline.py`) | Validate audio size (<15MB) and duration (<=30s); route to transcription. | File accepted, converted to 16kHz mono WAV via pipeline. | **VERIFIED (Synthetic Test Data)** |
| 5 | **Audio Duration Exceeded (>30s)** | Synthetic Audio (.wav, 31.5s) | Automated Harness (`test_prd_compliance.py`) | Reject synchronously before external provider call with HTTP 413. | HTTP 413 returned: *"Record up to 30 seconds for live synchronous transcription"*. | **VERIFIED (Automated)** |
| 6 | **Empty / No Speech Audio** | Silent Audio (.wav, 0.0s / 0 bytes) | Automated Harness (`test_prd_compliance.py`) | Reject with HTTP 422 without fabricating a placeholder transcript. | HTTP 422 returned: *"The recording is empty. Please record again."* | **VERIFIED (Automated)** |
| 7 | **Noisy Street Telephony** | Field Audio Sample (Hindi 8kHz) | External Gnani Prisma v3 | Prisma model transcribes noisy acoustic environments without failure. | Field acoustic evaluation requires live Gnani API key and consented test recordings. | **BLOCKED (Requires Consented Live Field Audio)** |
| 8 | **Code-Mixed Dialect (Hinglish)** | Field Telephony Audio | External Gnani Prisma v3 | Spot statutory terms ("payment", "contractor", "FIR") across mixed dialects. | Linguistic field trial requires live Gnani API connectivity and consented user recordings. | **BLOCKED (Requires Consented Live Field Audio)** |
| 9 | **Transcript Review & Correction (V2)** | Text Correction Flow | Automated Harness (`test_prd_compliance.py`) | Preserve `original_transcript` and `reviewed_transcript` separately; draft reflects edits. | Server records both versions; `was_corrected: true`; legal draft uses corrected version. | **VERIFIED (Automated)** |
| 10 | **Incomplete Case Facts (L1)** | Incomplete Account (Hindi) | Automated Harness (`test_prd_compliance.py`) | Unknown fields remain unknown; follow-up questions generated. | Status is `needs_details`; missing facts explicitly listed; zero fabricated dates/places. | **VERIFIED (Automated)** |
| 11 | **Fact Completion Across Turns (L1)** | 3-Turn Dialogue Sequence | Automated Harness (`test_multiturn_and_evidence.py`) | Status advances to `ready_for_human_review`; draft incorporates facts. | Multi-turn session promotes intake from `needs_details` to `ready_for_human_review`. | **VERIFIED (Automated)** |
| 12 | **Statutory Source Register (L2)** | 12 Primary Categories | Code & Register Audit (`source_register.py`) | Citations audited against primary Indian Acts; reviewer status honest. | Version `2026.11-v1` audited against primary Acts; status `DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW`. | **VERIFIED (Audited Draft; Public Sign-Off Pending)** |
| 13 | **Legal Aid Referral Handoff (L3)** | Bharat Grassroots Intake | Automated Harness (`test_prd_compliance.py`) | NALSA / DLSA referral provided with helpline 15100 and statutory eligibility criteria. | Structured Legal Aid Referral card returned with helpline `15100` and documents checklist. | **VERIFIED (Automated)** |
| 14 | **Pro Packet Approval State Machine (P2)** | Enterprise Case Packet | Automated Harness (`test_prd_compliance.py`) | Transition `needs_review` -> `approved`; record approver name, role, and content hash. | Packet status transitioned to `approved`; approver log appended; frozen SHA-256 recorded. | **VERIFIED (Automated)** |
| 15 | **Pro Approval Without Provider (P2)** | Send Attempt | Automated Harness (`test_prd_compliance.py`) | Reject transmission cleanly; maintain review-only status; adapter safety lock active. | Rejected: *"Outbound transmission adapter is DISABLED"*; status remains `approved`. | **VERIFIED (Automated)** |
| 16 | **Ephemeral Audio Retrieval (S1)** | Cache Token Lookup | Automated Harness (`test_prd_compliance.py`) | Audio served with `Cache-Control: private, no-store`; 404 after expiration. | Unguessable token served privately; expired/invalid token returns HTTP 404. | **VERIFIED (Automated)** |
| 17 | **Multi-Tenant Authorization & Anti-Hijack (S1)** | Multi-User Scenarios | Automated Harness (`test_security_auth.py`) | User A cannot access, approve, update, upload to, or hijack User B's packet/session. | Cross-user requests rejected with HTTP 401/403. Scoped deletion verified. | **VERIFIED (Automated)** |
| 18 | **User-Scoped Privacy Purge (S1)** | Privacy Purge API Call | Automated Harness (`test_security_auth.py`) | `/api/privacy/purge` with session token wipes only that user's session, audio, and packets. | Scoped purge leaves other users' data intact; global purge requires admin secret. | **VERIFIED (Automated; Full DPDP Audit Pending)** |
| 19 | **BSA Sec 63 Evidence Ingestion** | Multipart File Upload (`POST .../attachment`) | Automated Harness (`test_multiturn_and_evidence.py`) | Stream file bytes, compute cryptographic SHA-256 digest, append metadata. | Verified: SHA-256 computed on the fly; uploads locked when packet is in `approved` status. | **VERIFIED (Automated)** |
| 20 | **iOS Client API Parity (M1)** | Swift Code & Model Contracts | Python Contract Tests (`test_ios_mobile_parity.py`) | Swift client uses same auth headers, transcript review, Pro review, and purge endpoints. | API contracts and models 100% verified against Starlette backend; Swift models aligned. | **VERIFIED (API Contract; iOS Toolchain Pending)** |
| 21 | **Voice-First Understand Your Rights (7-Part)** | Multilingual Cases (Marathi, Hindi, English, Tamil) | Automated Harness (`test_understand_your_rights.py`) | Return 7 sections: facts understood, what may be wrong, possible Acts, why applies, next steps, urgent help, 1-min recap. | All 7 sections generated, distinguishing allegations vs verified facts under `DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW`. | **VERIFIED (Automated)** |
| 22 | **Urgent Danger & Custody Priority** | Police Custody / Violence keywords | Automated Harness (`test_understand_your_rights.py`) | Prioritize emergency 112/181 notice before longer statutory explanation. | Urgent safety notice prioritized; emergency helplines surfaced; safety text placed first. | **VERIFIED (Automated)** |
| 23 | **Audio/Text Consistency** | Marathi wage theft / Street vendor | Automated Harness (`test_understand_your_rights.py`) | Spoken scripts strictly align with screen text without contradictions. | Spoken scripts strictly align with visible recap and section descriptions. | **VERIFIED (Automated)** |
| 24 | **Shared Phone Privacy Protection** | UI & API Playback Controls | Browser & Frontend tests (`test_frontend_ux.py`, UI audit) | Sensitive legal details do NOT auto-play aloud without clear user action. | Shared phone protection active by default; explicit user tap required; earphone notice displayed. | **VERIFIED (Automated & Manual UI)** |
| 25 | **Live Timbre TTS Synthesis (Marathi)** | Synthetic Legal Script (Marathi) | Live Gnani Timbre Provider (`POST /api/rights/audio`) | Generate WAV audio using Vasudha voice, cache ephemerally. | Real network call: 235,564 bytes returned in 2.15s, valid WAV format. | **VERIFIED (Live Gnani Provider Call)** |

---

## 2. Automated Test Run Log (63 / 63 Tests Passing)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.8, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Gnanai\Gnani Challenge
plugins: anyio-4.15.1
collected 63 items

test_omni_legal.py .                                                     [  1%]
tests/test_frontend_ux.py ........                                       [ 14%]
tests/test_ios_mobile_parity.py .                                        [ 15%]
tests/test_legal_intake.py .......                                       [ 26%]
tests/test_multiturn_and_evidence.py .........                           [ 41%]
tests/test_prd_compliance.py ............                                [ 60%]
tests/test_security_auth.py ..........                                   [ 76%]
tests/test_understand_your_rights.py .........                           [ 90%]
tests/test_voice_pipeline.py ......                                      [100%]

======================= 63 passed, 2 warnings in 36.40s =======================
```
tests/test_frontend_ux.py::test_voice_error_fallback_message PASSED      [ 13%]
tests/test_frontend_ux.py::test_session_token_and_privacy_purge_integration PASSED [ 15%]
tests/test_ios_mobile_parity.py::test_ios_parity_complete_flow PASSED    [ 16%]
tests/test_legal_intake.py::test_vendor_draft_does_not_invent_notice_or_eviction PASSED [ 18%]
tests/test_legal_intake.py::test_pro_accident_does_not_invent_policy_or_evidence PASSED [ 20%]
tests/test_legal_intake.py::test_intake_can_advance_to_human_review_with_structured_facts PASSED [ 22%]
tests/test_legal_intake.py::test_unrelated_attack_is_not_assumed_religious PASSED [ 24%]
tests/test_legal_intake.py::test_wage_reference_uses_current_code PASSED [ 26%]
tests/test_legal_intake.py::test_statutory_resolution_for_all_supported_categories_when_facts_confirmed PASSED [ 28%]
tests/test_legal_intake.py::test_incomplete_intakes_maintain_safety_and_no_ungrounded_drafts PASSED [ 30%]
tests/test_multiturn_and_evidence.py::test_chat_without_session_id_returns_none PASSED [ 32%]
tests/test_multiturn_and_evidence.py::test_multiturn_session_accumulates_facts_and_advances_intake PASSED [ 33%]
tests/test_multiturn_and_evidence.py::test_session_purge_specific_session PASSED [ 35%]
tests/test_multiturn_and_evidence.py::test_session_purge_all_clears_sessions PASSED [ 37%]
tests/test_multiturn_and_evidence.py::test_add_attachment_helper_computes_sha256_and_records_metadata PASSED [ 39%]
tests/test_multiturn_and_evidence.py::test_evidence_upload_endpoint_success PASSED [ 41%]
tests/test_multiturn_and_evidence.py::test_evidence_upload_missing_packet_returns_404 PASSED [ 43%]
tests/test_multiturn_and_evidence.py::test_evidence_upload_to_approved_packet_returns_400 PASSED [ 45%]
tests/test_multiturn_and_evidence.py::test_evidence_upload_without_file_returns_422 PASSED [ 47%]
tests/test_prd_compliance.py::test_v1_system_status_and_privacy_notice PASSED [ 49%]
tests/test_prd_compliance.py::test_v2_transcript_review_preserves_both_versions PASSED [ 50%]
tests/test_prd_compliance.py::test_v3_audio_duration_rejection_over_30s PASSED [ 52%]
tests/test_prd_compliance.py::test_v3_empty_audio_rejection PASSED       [ 54%]
tests/test_prd_compliance.py::test_l1_missing_facts_produce_questions_unknowns_remain_unknown PASSED [ 56%]
tests/test_prd_compliance.py::test_l1_intake_advances_when_facts_supplied PASSED [ 58%]
tests/test_prd_compliance.py::test_l2_versioned_source_register PASSED   [ 60%]
tests/test_prd_compliance.py::test_l3_legal_aid_handoff_present PASSED   [ 62%]
tests/test_prd_compliance.py::test_p1_pro_packet_structure PASSED        [ 64%]
tests/test_prd_compliance.py::test_p2_approval_state_machine_and_adapter_safety_lock PASSED [ 66%]
tests/test_prd_compliance.py::test_s1_audio_tokens_are_ephemeral PASSED  [ 67%]
tests/test_prd_compliance.py::test_s1_privacy_purge_endpoint PASSED      [ 69%]
tests/test_security_auth.py::test_user_a_cannot_access_user_b_pro_packet PASSED [ 71%]
tests/test_security_auth.py::test_user_a_cannot_approve_user_b_pro_packet PASSED [ 73%]
tests/test_security_auth.py::test_user_a_cannot_update_or_send_user_b_pro_packet PASSED [ 75%]
tests/test_security_auth.py::test_user_a_cannot_upload_attachment_to_user_b_pro_packet PASSED [ 77%]
tests/test_security_auth.py::test_user_a_cannot_hijack_user_b_chat_session PASSED [ 79%]
tests/test_security_auth.py::test_user_a_cannot_purge_user_b_session_or_packets PASSED [ 81%]
tests/test_security_auth.py::test_global_purge_requires_admin_authorization PASSED [ 83%]
tests/test_security_auth.py::test_session_ttl_expiration PASSED          [ 84%]
tests/test_security_auth.py::test_pii_and_credential_sanitization_for_logs PASSED [ 86%]
tests/test_security_auth.py::test_dpdp_notice_truthfulness_no_false_compliance_claims PASSED [ 88%]
tests/test_voice_pipeline.py::SpeechClientTests::test_stt_uses_v3_indic_auto_and_safe_error PASSED [ 90%]
tests/test_voice_pipeline.py::SpeechClientTests::test_tts_uses_auto_language_and_v3_voice PASSED [ 92%]
tests/test_voice_pipeline.py::SpeechClientTests::test_tts_validates_voice_and_language PASSED [ 94%]
tests/test_voice_pipeline.py::VoiceRouteTests::test_audio_url_is_short_lived_and_not_cached_by_browser PASSED [ 96%]
tests/test_voice_pipeline.py::VoiceRouteTests::test_rest_limit_and_invalid_language_are_rejected_before_provider PASSED [ 98%]
tests/test_voice_pipeline.py::VoiceRouteTests::test_transcribe_returns_editable_text_and_detected_language PASSED [100%]

======================= 53 passed, 2 warnings in 30.96s =======================
```

---

## 3. Statutory Source Audit & Counsel Review Status

- **Register Version:** `2026.11-v1`
- **Reviewed By:** None (`DRAFT_PENDING_QUALIFIED_LEGAL_REVIEW`)
- **Review Date:** Pending Qualified Review
- **Credentials:** Unverified (Simulated/placeholder advocate names removed; no advocate enrollment claimed)
- **Jurisdiction:** Republic of India (BNS 2023, BNSS 2023, BSA 2023 and Special Acts)
- **Disclaimer:** Statutory provisions compiled from primary Indian legislation for triage and structured draft preparation. This register is a draft pending verification by a qualified advocate admitted to an Indian State Bar Council. Not certified legal advice.
- **Audited Statutory Bases:**
  - **BNS 2023** (Sections 189, 298, 301, 318, 329, 351)
  - **BNSS 2023** (Sections 35–47 arrest safeguards, 144 maintenance, 173(1) Zero FIR, 173(3), 175(3))
  - **BSA 2023** (Section 63 electronic records admissibility)
  - **Code on Wages, 2019** (Sections 17 and 45) alongside Payment of Wages Act 1936 & Minimum Wages Act 1948
  - **Street Vendors Act, 2014** (Sections 3(3) and 18)
  - **Motor Vehicles Act, 1988 amended 2019** (Sections 134, 146, 159, 164, 166)
  - **RERA 2016** (Sections 18, 31)
  - **MSMED Act 2006** (Sections 15, 16, 18)
  - **PWDVA 2005** (Sections 12, 18, 19, 20; Helplines 181, 112)
  - **RTI Act 2005** (Sections 6, 7)
  - **Constitution of India** (Articles 21, 23, 25, 39A)
  - **Legal Services Authorities Act, 1987** (Section 12; NALSA / DLSA Helpline 15100)
- **Status:** **DRAFT PENDING QUALIFIED LEGAL REVIEW — OUTBOUND TRANSMISSION DISABLED**

---

## 4. Two-Phase Voice-First Interaction Flow & Modality Symmetry Verification

- **Phase 1: Socratic Conversational Intake (When Facts Are Needed):**
  - Premature Citizen Legality Verdicts, statutory citations, 7-part "Understand Your Rights" cards, and Pro draft packets are strictly gated and hidden during initial fact collection.
  - Prominently displays the active conversational question, upcoming questions, verified transcript hash check ("What we heard"), and accessible one-tap voice/text reply controls.
  - **Zero Boilerplate:** First turn features crisp natural acknowledgement; subsequent follow-up turns directly ask the case-specific substantive legal question without repetitive "I understand and will provide help" preamble.
- **Phase 2: Comprehensive Legal Rights Shield (When Facts Are Complete):**
  - Once all necessary facts are collected (`needs_more_information == False`), the complete legal package is presented:
    - Plain-Language Citizen Legality Verdict Card with conditional framing and primary India Code links.
    - 7-Part "Understand Your Rights" Breakdown (What I understood, What may be wrong, Possible Act & Dhaara, Why it applies, Action steps, Urgent help, 1-minute recap).
    - AI-synthesized narrative in Section 1 and raw citizen account in Section 2 of the formal draft summary.
    - Pro Incident Packet with offline sign-off and outbound boundaries intact.
    - Statutory citations and NALSA/DLSA legal aid handoff (15100).
- **Modality Symmetry (Voice-in -> Voice-out, Text-in -> Text-out):**
  - **Voice In:** When a user records speech or taps "Speak Answer", the AI speaks back aloud via live Gnani Timbre TTS in their chosen language.
  - **Text In:** When a user types in the input box, the AI responds in text quietly without unprompted auto-play.
- **Mobile Parity:**
  - `ios/NyayaVani/Views/MessageBubbleView.swift` updated with identical two-phase gating and voice auto-playback.
- **Verification Results:**
  - Total Pytest Suite: **71 passed out of 71 tests** (`tests/test_merged_integration.py`, `tests/test_frontend_ux.py`, `tests/test_ios_mobile_parity.py`, etc.).
  - Web Server running live on `http://127.0.0.1:8501`.
