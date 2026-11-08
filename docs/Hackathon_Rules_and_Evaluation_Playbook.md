# Hackathon Rules, Evaluation Criteria & Strategic Playbook

> **Event:** The Great Indian AI Internship Challenge by **Gnani.ai**  
> **Registration Confirmation Date:** November 8, 2026  
> **Hard Deadline:** November 10, 2026, 11:59 PM IST (Strict cutoff, no extensions)  
> **Official Submission Form:** [Microsoft Form Submission](https://forms.cloud.microsoft/r/dfFShbp7W7)  
> **Official Documentation & Portal:** [Gnani Voice Portal](https://app.gnani.ai/voice) | [API Docs](https://docs.gnani.ai/api/introduction/introduction)

---

## 1. Challenge Overview & Eligibility

* **Core Premise:** Build any application, workflow, or solution demonstrating practical, real-world utility using Gnani AI's proprietary sovereign Indic speech and language models.
* **Eligibility:**
  - Must be a student currently enrolled in an Indian higher educational institution (Colleges, Universities, Training institutes).
  - Minimum age: 18 years.
  - Verification: Student ID card and institutional or personal email used during registration.
  - Team Size: Solo or teams of up to 2 members.
* **Allocated Resources:**
  - **5,000 Programme Credits** deposited into the primary registrant's Gnani platform account (`app.gnani.ai/voice`).
  - **3 Free API Keys** generated via the developer dashboard.
  - Discord and Email Support: `internshipscontest@gnani.ai` / Gnani Discord Community.

---

## 2. Prizes, Stakes & Offer Structure

### The Grand Prize: 100 Paid 6-Month Internships
* **Stipend:** Up to **₹1,00,000 per month per intern** (₹1 Lakh/month).
* **Payment Terms:** Paid individually to each intern; stipends are **not split** across teams.
* **Selection Independence:** In a 2-person team, offers are issued individually based on personal technical interviews. One teammate may receive an offer even if the other does not.
* **Start Date:** Scheduled for **January 1, 2027**.

### 10 Specialized Category Awards (₹50,000 Cash Prize Each)
Gnani AI has instituted 10 award categories to reward technical excellence across specific niches:
1. **Regional Languages:** Deepest utility and accuracy across non-Hindi Indian languages (e.g. Kannada, Tamil, Telugu, Marathi).
2. **Hinglish and Code-Mixed Voice Experiences:** Handling rapid intra-sentence language switching between English and Indic vernacular.
3. **Noisy Telephonic Audio:** Accurate speech recognition on band-limited (8kHz) acoustic channels with background street/office noise.
4. **Real-World Impact:** Solutions solving verified, high-volume enterprise or societal pain points.
5. **Best Solo Project:** Top-rated project engineered by a single contributor.
6. **Best Duo Project:** Top-rated project engineered by a two-member team.
7. **Creativity & Novelty:** Unconventional or breakthrough applications of speech models.
8. **Tier 2 and Tier 3 Regional Representation:** Outstanding entries originating from outside metro cities.
9. **Best 60-Second Demo:** The most compelling, concise, and high-clarity video walkthrough under 60 seconds.
10. **Public-Vote Crowd Favourite:** Highest verified engagement and community acclaim on LinkedIn / X.

---

## 3. Evaluation & Selection Workflow

The competition follows a two-tier evaluation mechanism:

```
[Phase 1: Build & Deploy] ──> [Phase 2: Public Demo on Socials] ──> [Phase 3: Engagement Audit] ──> [Phase 4: Gnani AI Review] ──> [Phase 5: 1-on-1 Technical Interview] ──> [Written Offer]
```

1. **Public Social Proof (Prerequisite for Shortlisting):**
   - Participants must post a video demonstration of their working project on **LinkedIn** or **X (Twitter)**.
   - Mandatory hashtags: `#GnaniAI` and `#GreatIndianAIInternshipChallenge`.
   - Mentions: Tag `@Gnani.ai` (LinkedIn) or `@gnaniai` (X).
   - Post nomination: The post URLs must be submitted into the official Microsoft Form before Nov 10, 2026.
2. **Engagement & Authenticity Verification:**
   - Gnani AI evaluates both organic reach, technical feedback from industry professionals, and popular community engagement.
   - Automated engagement bots or fake upvoting lead to immediate disqualification.
3. **Internal Review & Shortlisting:**
   - Gnani AI engineering evaluators inspect the codebase, API usage logs (verifying actual calls to Prisma/Timbre/Evon), and product polish.
4. **Individual Technical Interviews:**
   - Every shortlisted applicant sits for an independent 1-on-1 technical interview.
   - Topics: System architecture, audio processing pipelines, model trade-offs, handling real-world latency, and domain knowledge.
5. **Written Internship Offer:**
   - Official written offer confirming role, monthly stipend (up to ₹1L/month), and onboarding schedule starting Jan 1, 2027.

---

## 4. Strategic Positioning for VachanAudit

To maximize probability across both the **Internship Shortlist** and the **₹50,000 Category Awards**, VachanAudit is engineered to hit a **triple-category sweet spot**:

| Target Award Track | How VachanAudit Captures It | Supporting Evidence in Repository |
| :--- | :--- | :--- |
| **Noisy Telephonic Audio** | Targets 8kHz narrowband telephony recordings containing acoustic degradation, line noise, and call-center background chatter. | `backend/core/gnani_client.py` uses Prisma v2.5/v3.0 tuned for telephony audio streams. |
| **Hinglish & Code-Mixed Voice** | Specifically audits debt collection and customer support calls conducted in conversational Hinglish ("Aapka EMI payment pending hai, please call back right now"). | `backend/services/compliance_auditor.py` handles dual-script and romanized Indic keyword auditing. |
| **Real-World Impact (BFSI)** | Solves a massive enterprise blindspot: Indian banks process tens of millions of collection calls/month, reviewing <2% manually and risking heavy RBI non-compliance penalties. | Dynamic 0–100 compliance scoring based on the RBI Fair Practices Code for recovery agents. |
| **Best 60-Second Demo** | The UI layout is designed for a fast 45–55 second live demonstration showing audio upload, instant transcription, compliance flag trigger, and TTS synthesis. | Clean Streamlit dual-column dashboard with clear visual status tags (`COMPLIANT`, `NON_COMPLIANT_RISK`). |

---

## 5. Risk Assessment & Mitigation

1. **Credit Exhaustion (5,000 Credit Limit):**
   - *Risk:* Excessive test calls running full audio STT could drain the 5,000 credit grant.
   - *Mitigation:* Cache STT JSON responses locally in `audio_samples/cache/` for repeated UI development. Only make live API requests during smoke tests and final screen recordings.
2. **Social Media Algorithm Lag:**
   - *Risk:* Posting late on Nov 10 may result in lower organic reach before Gnani's review cutoff.
   - *Mitigation:* Publish the LinkedIn and X posts early on **November 9, 2026 (Evening)**. Share the link immediately with college peer networks, IEEE members, and faculty mentors for early organic traction.
3. **API Downtime / Network Latency During Recording:**
   - *Risk:* Screen recording stalling on network latency during live API call.
   - *Mitigation:* Keep a pre-audited fallback sample loaded in the UI toggle (`use pre-generated test audio`) to ensure smooth 60fps recording without stutter.
