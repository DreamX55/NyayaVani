# NyayaVani Product Requirements Document

## Product purpose

NyayaVani helps a person describe a legal problem by voice or text in a language they are comfortable using, understand practical next steps, and prepare a document for human review. The free experience focuses on people who face barriers to typing, English, and paid legal help. Pro organizes accident and commercial incidents into a reviewable case packet and, when a verified provider is connected, can coordinate approved follow-up actions.

This product must distinguish a suggestion from a legal conclusion, a draft from a filed document, and a configured API key from a successful live service call. The current repository is a prototype with rule-based case routing, templates, Prisma speech-to-text, and Timbre text-to-speech. Evon reasoning and insurer, lawyer, police, or court submission are not connected.

## Users and primary journeys

1. **Person seeking grassroots help:** Record or type a short account in an available Indic language. Review and correct the transcript. Answer only the essential follow-up questions. Receive spoken and written next steps, a clearly marked draft, and a route to suitable legal aid.
2. **Pro incident customer:** Describe an accident or commercial problem, add documents and evidence metadata, review the generated chronology and packet, then approve the exact recipient and content before any future outbound action. The initial release stops at an approval-ready packet because no outbound provider is connected.
3. **Reviewer:** Inspect the original account, corrected transcript, facts supplied by the user, source references, unresolved questions, and proposed draft before endorsing or sending anything.

## Requirements and implementation

| ID | Requirement | How to build it | Acceptance check |
| --- | --- | --- | --- |
| V1 | Live voice intake | Record in the browser and submit short clips to a dedicated transcription endpoint. Use Prisma v3 with automatic Indic language detection where supported. Keep the API key on the server. | A fresh recording produces a transcript without a bundled sample; errors are specific and no fabricated transcript appears. |
| V2 | Transcript review | Display detected language and verbatim transcript before legal analysis. Let the user edit and confirm it; preserve the original and corrected versions separately. | Changing a mistranscribed word changes subsequent analysis; no legal draft is generated before confirmation. |
| V3 | Audio limits and resilience | Enforce the documented 30-second limit for synchronous STT. Show recording duration and reject or route longer audio to a documented streaming or batch flow. Use compatible TTS voice and language parameters. | A 31-second clip receives a clear action, a short supported clip works, and TTS failure still leaves written guidance. |
| L1 | Fact collection | Route to a case category tentatively, then ask a small number of case-specific questions about date, place, notice, evidence, harm, and desired outcome. Keep unknown fields unknown. | Incomplete accounts produce questions rather than a fully asserted petition; answers update the case packet. |
| L2 | Reviewed legal content | Create a versioned source register for every cited provision and template. A qualified Indian legal reviewer signs off on citation, conditions, jurisdiction, wording, and review date before public use. | Each displayed citation has a reviewed source and date; unreviewed or stale content is withheld or marked for human review. |
| L3 | Legal aid handoff | Provide a simple eligibility and referral path to a district or other relevant legal services authority, with what information to take. Avoid promising eligibility without checking applicable criteria. | A grassroots user can leave with a relevant next contact and a readable summary. |
| P1 | Pro packet | Compile user-confirmed facts, chronology, missing evidence, attachments metadata, and draft insurer or lawyer message into an editable packet. | The packet never states that a claim was sent, footage verified, or counsel alerted unless that action has a recorded outcome. |
| P2 | Approval and delivery boundary | Model states `draft`, `needs_review`, `approved`, `sending`, `sent`, and `failed`. Record approver, exact content, recipient, timestamp, and provider response. Keep outbound adapters disabled until a provider and destination are configured. | A draft cannot send without an explicit approval; retries cannot create duplicate submissions; no-provider mode remains review-only. |
| S1 | Personal data protection | Explain what recording and case data is sent to the speech provider before use. Restrict access to case artifacts, set retention and deletion rules, and avoid public static URLs for private audio. | A different user cannot retrieve a case or audio URL; deletion removes retained case assets; test logs contain no raw private testimony or credentials. |
| M1 | Mobile parity | Make server address configurable for physical iOS devices and use the same transcript review, follow-up, and approval states as web. | Simulator and a physical device on an authorized network can reach the API; no release build assumes `127.0.0.1` is the host computer. |
| Q1 | End-to-end evidence | Add contract tests for mocked STT/TTS, category and uncertainty tests, privacy tests, and browser checks. Run a small consented field set of Hindi, English, code-mixed, and noisy recordings when network access is available. | Test report separates mocked passes from real provider passes and records exact failures. |

## Service and data flow

1. Browser or iOS captures audio and shows duration and a plain-language provider notice.
2. Server validates size, format, duration, and API configuration. It sends the short recording to Prisma through the server-side key and returns transcript, detected language, and request status.
3. User reviews and corrects the transcript. The corrected text becomes the basis for legal intake; the original remains available for comparison under the retention policy.
4. Intake identifies a tentative category and missing facts. The user answers focused follow-up questions. Unanswered fields remain explicit in the output.
5. The legal engine creates source-backed possible options, next steps, and a draft for human review. Timbre may read a concise version aloud. Speech failure does not erase the written result.
6. Pro assembles a reviewable packet. Outbound delivery is unavailable until an adapter, account, destination, and explicit approval are present.

## Product and safety rules

- Prefer clear, short prompts, large controls, and spoken playback; preserve a text path for quiet or inaccessible environments.
- Never infer poverty, eligibility, religion, identity, or fault from a short recording alone.
- Never claim a FIR, insurance claim, message, or call was completed based on draft generation.
- Never call a transcript hash a digital signature, affidavit, or proof of admissibility. Preserve original evidence separately if an evidence workflow is introduced.
- Give the user a chance to correct speech recognition before legal analysis and before any future outbound step.
- Require a human legal review of the jurisdiction-specific content before public deployment.

## Delivery sequence

1. **Core reliability:** Live short-clip transcription, language detection, transcript correction, service diagnostics, and mocked API tests.
2. **Useful legal intake:** Missing-fact questions, tentative guidance, reviewed source register, and legal aid referral.
3. **Pro readiness:** Editable packet, explicit approval state, evidence inventory, and adapter contract. No provider is currently configured.
4. **Deployment readiness:** Private case storage, retention and deletion, authentication, mobile configuration, real-provider field tests, and qualified legal review.

## Verification record required for release

Record the date, environment, scenario, input type and language, provider request ID, expected result, observed result, and pass or fail. Cover text, live microphone, uploaded short audio, no speech, noisy speech, mixed language, provider 401/403/429/5xx, disconnected network, incorrect transcript correction, incomplete case facts, Pro approval without a provider, unauthorized audio retrieval, and mobile access. A mocked provider pass does not count as a live provider pass.

## External dependencies and decisions

- Gnani Prisma and Timbre access must be tested from the environment that runs the server. [Gnani STT REST documentation](https://docs.gnani.ai/api/STT/speech-to-text) specifies the short-clip endpoint and limit; [Gnani TTS documentation](https://docs.gnani.ai/api/TTS/tts-inference) specifies models, voices, and language parameters.
- A legal reviewer must approve case templates and source citations. [NALSA legal aid guidance](https://nalsa.gov.in/legal-aid/) is the starting point for free legal aid handoff.
- Before handling real case data beyond a controlled pilot, review consent, notice, retention, and user rights against current Indian requirements. [MeitY Digital Personal Data Protection Act text](https://www.meity.gov.in/static/uploads/2024/02/Digital-Personal-Data-Protection-Act-2023-1.pdf).
- The user has no outbound Pro provider yet. Recipient, account, channel, provider API, and operating policy remain open decisions; no code should silently send a case packet.
