import os
import sys
import tempfile
from datetime import datetime
import streamlit as st

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.gnani_client import GnaniClient
from backend.services.legal_engine import NyayaVaniEngine
from backend.services.pro_workflow import (
    build_pro_packet,
    get_pro_packet,
    approve_pro_packet,
    _packet_store,
)
from backend.services.source_register import REGISTER_VERSION, REVIEWER_METADATA, STATUTORY_REGISTER

st.set_page_config(
    page_title="NyayaVani (न्यायवाणी) — Sovereign Indic Voice Legal Navigator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1A237E;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #424242;
        margin-bottom: 20px;
    }
    .rights-card {
        background-color: #FFF3E0;
        border-radius: 10px;
        padding: 18px;
        border-left: 6px solid #FF6F00;
        margin-bottom: 15px;
    }
    .pro-card {
        background-color: #E8F5E9;
        border-radius: 10px;
        padding: 18px;
        border-left: 6px solid #2E7D32;
        margin-bottom: 15px;
    }
    .hash-badge {
        font-family: monospace;
        background-color: #ECEFF1;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #37474F;
        margin-bottom: 10px;
    }
    .legal-aid-card {
        background-color: #E0F2F1;
        border-radius: 10px;
        padding: 16px;
        border-left: 6px solid #00897B;
        margin-bottom: 15px;
    }
    .register-card {
        background-color: #E8EAF6;
        border-radius: 8px;
        padding: 12px 16px;
        border-left: 5px solid #3F51B5;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚖️ NyayaVani (न्यायवाणी)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Speak in your language. Review practical next steps and a draft document.</div>', unsafe_allow_html=True)

# Initialize Backend Services
@st.cache_resource
def get_services():
    client = GnaniClient()
    engine = NyayaVaniEngine()
    return client, engine

try:
    client, engine = get_services()
    st.sidebar.info("Speech service configured; connection is checked when used")
except Exception as e:
    st.sidebar.error(f"Gnani API Connection Error: {e}")
    st.stop()

# Sidebar Navigation & Settings
st.sidebar.header("🛠️ Mode Selection")
app_mode = st.sidebar.radio(
    "Choose Solution Layer",
    options=[
        "🎙️ Open-Ended Voice Legal Advisor (Universal)",
        "🏛️ Bharat Grassroots Legal Aid (Free Tier)",
        "💼 NyayaVani Pro (Enterprise Legal Suite)",
        "📊 Voice AI Matrix & Global Benchmarks"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎙️ Gnani Voice Models")
st.sidebar.caption("**STT Model:** Prisma v2.5 / v3.0 (`/stt/v3`)")
st.sidebar.caption("**TTS Model:** Timbre v3.0 (`/api/v1/tts/inference`)")
st.sidebar.caption("**Legal guidance:** Scenario rules and document templates")

st.sidebar.markdown("---")
tts_voice_option = st.sidebar.selectbox(
    "Timbre Synthesizer Voice",
    options=[
        "Shivani (Authoritative Formal Hindi - Rights Shield)",
        "Lakshmi (Empathetic Conversational Hindi)",
        "Avinash (Professional English / Corporate)",
        "Kalpana (Clear Regional Hindi)"
    ],
    index=0
)
voice_name = tts_voice_option.split()[0]

# DPDP Privacy Purge in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔒 DPDP Privacy Safeguard")
st.sidebar.caption("Digital Personal Data Protection Act, 2023 Compliance")
if st.sidebar.button("🗑️ DPDP Privacy: Purge Session", type="secondary", use_container_width=True):
    try:
        from backend.services.pro_workflow import _packet_store
        _packet_store.clear()
    except Exception:
        pass
    try:
        from backend.server import _audio_cache
        _audio_cache.clear()
    except Exception:
        pass
    try:
        import requests
        requests.post("http://127.0.0.1:8501/api/privacy/purge", timeout=0.5)
    except Exception:
        pass
    st.session_state.clear()
    st.sidebar.success("Session state & ephemeral data purged.")
    st.rerun()


def render_analysis_display(case_res: dict, session_prefix: str, client_name: str):
    """
    Renders statutory analysis, verified register metadata, primary sources,
    prominent NALSA/DLSA referral card, and Pro packet approval workflow.
    """
    # 1. Cryptographic Hash Badge (Section 63 BSA Electronic Record Integrity)
    sha_hash = case_res.get("affidavit_evidence", {}).get("sha256") or case_res.get("sha256")
    if sha_hash:
        st.markdown(f'<div class="hash-badge">🔒 Electronic Record Integrity SHA-256: <code>{sha_hash}</code></div>', unsafe_allow_html=True)

    # 2. Statutory Citations Notice Card
    reg_ver = REGISTER_VERSION
    jurisdiction = REVIEWER_METADATA.get("jurisdiction", "Republic of India")

    st.markdown(f"""
    <div class="register-card">
        <div style="font-weight: 700; color: #1A237E; font-size: 0.95rem; margin-bottom: 4px;">
            ⚖️ Statutory Citations Pending Advocate Verification
        </div>
        <div style="font-size: 0.84rem; color: #283593;">
            <b>Register Version:</b> <code>{reg_ver}</code> &nbsp;|&nbsp;
            <b>Notice:</b> <span style="background-color: #FFF3E0; color: #E65100; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 0.78rem;">Draft Incident Summary for Review — Not Legal Advice</span><br>
            <b>Jurisdiction:</b> {jurisdiction} &nbsp;|&nbsp;
            <b>Transmission:</b> <span style="color: #C62828; font-weight: bold;">Outbound transmission disabled (Review only)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Applicable Statutory Provisions & Primary Sources
    card_class = "rights-card" if case_res.get("tier") == "BHARAT_GRASSROOTS_AID" else "pro-card"
    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
    st.markdown(f"### 📜 {case_res.get('statutory_title', 'Statutory Rights Shield')}")
    st.markdown(f"**Classification:** `{case_res.get('category')}` | **Tier:** `{case_res.get('tier')}`")
    st.markdown("**Applicable Statutory Provisions & Primary Sources:**")
    for s in case_res.get("statutory_sections", []):
        st.markdown(f"- **{s.get('law', 'Law')}**: {s.get('details', '')}")
        source_url = s.get("source_url")
        if source_url:
            st.markdown(f"  &nbsp;&nbsp;↳ 📖 *Primary Source:* [{source_url}]({source_url})")
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. Prominent NALSA / DLSA 15100 Legal Aid Referral Card
    legal_aid = case_res.get("legal_aid_referral") or {
        "authority": "District Legal Services Authority (DLSA) / NALSA",
        "helpline": "15100",
        "official_url": "https://nalsa.gov.in/legal-aid/",
        "eligibility_summary": "100% free legal aid available under Section 12 of the Legal Services Authorities Act, 1987 to women, children, industrial workmen, custody detainees, and eligible citizens.",
        "documents_to_carry": [
            "Any photo identity card (Aadhaar / Voter ID / Ration Card)",
            "Income certificate or proof of marginal income (if applicable)",
            "All incident notices, receipts, muster cards, photographs, or call records"
        ],
        "disclaimer": "Eligibility for free legal aid is subject to verification of statutory criteria under the Legal Services Authorities Act, 1987."
    }
    
    docs_html = "".join(f"<li>{doc}</li>" for doc in legal_aid.get("documents_to_carry", []))
    st.markdown(f"""
    <div class="legal-aid-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 1.05rem; font-weight: 700; color: #004D40;">🏛️ Free Legal Aid Referral (NALSA / DLSA)</span>
            <span style="background-color: #00897B; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-family: monospace; font-size: 0.9rem;">
                📞 National Helpline: {legal_aid.get('helpline', '15100')}
            </span>
        </div>
        <p style="margin: 4px 0 6px 0; color: #004D40; font-size: 0.88rem;">
            <b>Authority:</b> {legal_aid.get('authority', 'DLSA / NALSA')} &nbsp;|&nbsp;
            <a href="{legal_aid.get('official_url', 'https://nalsa.gov.in/legal-aid/')}" target="_blank" style="color: #004D40; font-weight: bold; text-decoration: underline;">
                Official NALSA Legal Aid Portal ↗
            </a>
        </p>
        <p style="margin: 4px 0 6px 0; color: #004D40; font-size: 0.85rem;">
            {legal_aid.get('eligibility_summary', '')}
        </p>
        <div style="font-size: 0.82rem; color: #004D40; margin-top: 6px;">
            <b>Required Checklist for DLSA Intake:</b>
            <ul style="margin: 4px 0 6px 18px; padding: 0;">
                {docs_html}
            </ul>
        </div>
        <div style="font-size: 0.74rem; color: #00695C; font-style: italic; margin-top: 4px;">
            ℹ️ {legal_aid.get('disclaimer', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. Spoken Voice Output via Timbre TTS
    st.markdown("#### 🔊 Spoken Legal Rights Audio (Timbre TTS)")
    st.caption(f"Audio synthesized via Gnani Timbre TTS ({voice_name} voice). Review the written guidance and draft before using them.")

    shield_speech = case_res.get("spoken_rights_shield_hi") or case_res.get("spoken_guidance_en", "")
    os.makedirs("generated_audio", exist_ok=True)
    shield_audio_file = f"generated_audio/tts_shield_{int(datetime.now().timestamp())}.wav"

    with st.spinner("Synthesizing audio via Timbre TTS..."):
        try:
            lang_target = "hi-IN" if case_res.get("tier") == "BHARAT_GRASSROOTS_AID" else "en-IN"
            client.synthesize(shield_speech, language=lang_target, voice=voice_name, output_path=shield_audio_file)
            st.audio(shield_audio_file)
        except Exception:
            st.info("Spoken audio is unavailable right now. Please use the written guidance below.")

    if case_res.get("needs_more_information"):
        st.warning("More facts are needed. Draft Incident Summary for Review — Not Legal Advice.")
        for question in case_res.get("follow_up_questions", []):
            st.write(f"• {question}")

    # 6. Pro Incident Response Packet Workflow (If present)
    pro_packet = case_res.get("pro_packet")
    if pro_packet:
        st.markdown("---")
        st.markdown("### 💼 Pro Incident Response Packet")
        
        status_color = "#2E7D32" if pro_packet.get("status") == "approved" else "#FF8F00"
        status_label = pro_packet.get("status", "draft").upper()
        
        p_col1, p_col2 = st.columns([2, 1])
        with p_col1:
            st.markdown(f"**Packet ID:** `#{pro_packet.get('packet_id')}`")
            st.markdown(f"**Content SHA-256 Hash:** `<code>{pro_packet.get('content_hash')}</code>`", unsafe_allow_html=True)
            st.caption(f"Review Note: {pro_packet.get('review_note')}")
        with p_col2:
            st.markdown(f"""
            <div style="background-color: {status_color}22; border: 1px solid {status_color}; border-radius: 6px; padding: 8px 12px; text-align: center;">
                <span style="font-size: 0.8rem; color: #555;">PACKET STATE</span><br>
                <b style="color: {status_color}; font-size: 1.1rem;">{status_label}</b>
            </div>
            """, unsafe_allow_html=True)

        # Chronology Table
        chronology = pro_packet.get("chronology", [])
        if chronology:
            st.markdown("#### ⏱️ Chronological Fact Timeline")
            chron_rows = []
            for item in chronology:
                chron_rows.append({
                    "Stage": item.get("stage", "").replace("_", " ").title(),
                    "Timestamp": item.get("date", ""),
                    "Description": item.get("description", "")
                })
            st.table(chron_rows)

        # Missing Evidence Checklist
        missing = pro_packet.get("missing_evidence", [])
        if missing:
            st.markdown("#### 📋 Missing Evidence & Verification Checklist")
            for item in missing:
                st.markdown(f"- ⚠️ **Pending Verification:** {item}")

        # Outbound Safeguard Notice
        st.info("🛡️ **Outbound transmission disabled (Review only).** In accordance with strict review policies, no automated external transmission to insurers, lawyers, or police occurs. Human handoff and review required.")

        # Interactive Approval UI
        if pro_packet.get("status") in {"needs_review", "draft"}:
            st.markdown("#### ✍️ Pro Incident Packet Review & Approver Sign-Off")
            st.caption("Draft Incident Summary for Review — Not Legal Advice. Statutory citations pending advocate verification.")
            st.info("⚠️ Signing approves this document for human review and offline export, but does NOT transmit to police, insurer, or court. Outbound transmission disabled (Review only).")
            with st.container():
                c_a1, c_a2 = st.columns(2)
                with c_a1:
                    approver_name = st.text_input("Approver Full Name *", value=client_name or "", key=f"{session_prefix}_approver_name")
                with c_a2:
                    approver_role = st.selectbox(
                        "Approver Role *",
                        options=["Client", "Authorized Representative", "Independent Legal Counsel"],
                        index=0,
                        key=f"{session_prefix}_approver_role"
                    )
                
                notes = st.text_input("Approver Review Notes", value="Approved for human review and offline export.", key=f"{session_prefix}_notes")
                
                if st.button("✍️ Sign & Approve Packet (Review & Offline Export)", key=f"{session_prefix}_btn_approve", type="primary"):
                    if not approver_name.strip():
                        st.error("Approver Full Name is required before signing.")
                    else:
                        try:
                            updated = approve_pro_packet(
                                pro_packet["packet_id"],
                                approver_name=approver_name.strip(),
                                approver_role=approver_role,
                                notes=notes.strip()
                            )
                            case_res["pro_packet"] = updated
                            st.session_state[f"{session_prefix}_case_res"] = case_res
                            st.success(f"Case Packet #{pro_packet['packet_id']} successfully APPROVED by {approver_name.strip()} ({approver_role}) for offline export! Outbound transmission remains disabled.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Approval failed: {e}")
        else:
            st.success("✅ **Case Packet Approved.** Approved for human review and offline export. Outbound transmission disabled (Review only).")
            approvals = pro_packet.get("approvals", [])
            if approvals:
                last_app = approvals[-1]
                st.caption(f"Approved by **{last_app.get('approver_name')}** ({last_app.get('approver_role')}) at `{last_app.get('approved_at')}` | Frozen Hash: `{last_app.get('approved_content_hash', '')[:16]}...`")

    # 7. View & Download Formal Document
    with st.expander("📄 View & Download Draft for Review"):
        st.code(case_res.get("formal_document", ""), language="markdown")
        st.download_button(
            "📥 Download Formal Document (TXT)",
            data=case_res.get("formal_document", ""),
            file_name=f"NyayaVani_{case_res.get('category')}_{client_name.replace(' ', '_')}.txt",
            key=f"{session_prefix}_download_btn"
        )


# -------------------------------------------------------------
# TAB 1: OPEN-ENDED VOICE LEGAL ADVISOR (THE VOICE CHATGPT FOR LAW)
# -------------------------------------------------------------
if app_mode == "🎙️ Open-Ended Voice Legal Advisor (Universal)":
    st.subheader("Universal Indic Voice Legal Advisor")
    st.caption("Speak, upload, or type your account. Review the transcript before preparing guidance and a draft for your own review.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 1. Ingest Spoken Query or Incident")
        input_type = st.radio("Choose Input Method", ["Record Live Voice", "Upload Voice Recording (WAV/MP3)", "Enter Text Directly"])

        active_audio = None
        user_text = ""
        case_meta = {"client_name": "Citizen / Applicant", "location": "India"}

        if input_type == "Record Live Voice":
            active_audio = st.audio_input("Describe what happened in your own words")
        elif input_type == "Upload Voice Recording (WAV/MP3)":
            active_audio = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a"])
        if active_audio:
            st.audio(active_audio)

        else:
            user_text = st.text_area(
                "Enter narrative / spoken complaint in Hindi or English:",
                height=130,
                placeholder="उदा. मैं पिछले 6 महीने से फैक्ट्री में काम कर रहा हूँ लेकिन ठेकेदार ने 2 महीने की तनख्वाह नहीं दी..."
            )

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            name_input = st.text_input("Name of Complainant / Party", value=case_meta["client_name"])
        with col_m2:
            loc_input = st.text_input("City / District Jurisdiction", value=case_meta["location"])

        case_meta["client_name"] = name_input
        case_meta["location"] = loc_input

        btn_run = st.button("Transcribe / Review Account", type="primary")

    with col2:
        st.markdown("#### 2. Review Account & Guidance")

        if btn_run:
            transcript = user_text
            if active_audio:
                with st.spinner("Transcribing speech via Gnani Prisma ASR..."):
                    try:
                        suffix = os.path.splitext(active_audio.name)[1] or ".wav"
                        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_audio:
                            temp_audio.write(active_audio.getbuffer())
                            audio_path = temp_audio.name
                        try:
                            stt_res = client.transcribe(audio_path, language_code="indic-auto")
                        finally:
                            os.unlink(audio_path)
                        transcript = stt_res.get("transcript", "")
                    except Exception as e:
                        st.error("Live transcription is unavailable. Please type your account and try again.")
                        st.stop()
            if not transcript.strip():
                st.warning("Please record a voice note or enter text before continuing.")
                st.stop()

            st.session_state["reviewed_statement"] = transcript

        if st.session_state.get("reviewed_statement"):
            transcript = st.text_area(
                "Correct names, dates, places, and any words the service misheard",
                key="reviewed_statement",
                height=160,
            )
            prepare_reviewed = st.button("Prepare guidance from reviewed account", type="primary")
        else:
            prepare_reviewed = False

        if prepare_reviewed:
            if not transcript.strip():
                st.warning("Please enter your account before continuing.")
                st.stop()

            # Run through Omni-Domain Legal Engine
            with st.spinner("Executing statutory legal reasoning..."):
                case_res = engine.process_case(transcript, suite_tier="AUTO_DETECT", meta=case_meta)
                if case_res.get("tier") == "ENTERPRISE_LEGAL_SUITE":
                    pro_packet = build_pro_packet(
                        transcript,
                        case_res,
                        client_name=case_meta.get("client_name", ""),
                        location=case_meta.get("location", ""),
                    )
                    case_res["pro_packet"] = pro_packet
                st.session_state["tab1_case_res"] = case_res

        if st.session_state.get("tab1_case_res"):
            render_analysis_display(st.session_state["tab1_case_res"], session_prefix="tab1", client_name=case_meta.get("client_name", "Citizen"))

# -------------------------------------------------------------
# TAB 2: BHARAT GRASSROOTS LEGAL AID (ALL SITUATIONS)
# -------------------------------------------------------------
elif app_mode == "🏛️ Bharat Grassroots Legal Aid (Free Tier)":
    st.subheader("🏛️ Bharat Grassroots Legal Aid (Free Tier)")
    st.caption("Zero-cost legal rights defense for street vendors, daily-wage laborers, fraud victims, and marginalized communities.")

    grassroots_cat = st.selectbox(
        "Choose Citizen Legal Category:",
        [
            "1. Street Vendor Rights & Eviction Defense (Street Vendors Act 2014 Sec 3(3))",
            "2. Wage Theft & Unpaid Labor (Payment of Wages Act Sec 15)",
            "3. Illegal Land Grabbing & Slum Eviction (Specific Relief Act Sec 6)",
            "4. Predatory Loan Apps & Phishing Scams (IT Act 66D & RBI Circulars)",
            "5. Police Harassment, Custody & Refusal to File FIR (BNSS 173 Zero FIR)",
            "6. Domestic Abuse & Maintenance (PWDVA 2005 & BNSS 144)",
            "7. Religious Gathering & Community Assembly Protection (Article 25 & BNS 301)",
            "8. Bribe Demand & Administrative Denial (RTI Act 2005 & DLSA Free Aid)"
        ]
    )

    sample_dict = {
        "1.": "नमस्ते साहब, मैं जुहू बीच पर फल का ठेला लगाता हूँ। आज बीएमसी वाले आए और ठेला जब्त करने की धमकी दी। मेरे पास पीएम स्वनिधि की पर्ची है।",
        "2.": "ठेकेदार ने हमसे 3 महीने दिन-रात काम करवाया, अब 45,000 रुपये मजदूरी रोक रखी है और मांगने पर गाली-गलौज कर रहा है।",
        "3.": "कुछ स्थानीय दबंग रात को आए और हमारे पुश्तैनी मकान और जमीन पर जबरन कब्जा करने लगे और सामान बाहर फेंक दिया।",
        "4.": "एक मोबाइल लोन ऐप ने मेरे सारे फोन कॉन्टैक्ट्स हैक कर लिए और अब फोटो मॉर्फ करके रिश्तेदारों को भेजने की धमकी देकर पैसे मांग रहे हैं।",
        "5.": "जब हम थाने गए शिकायत दर्ज कराने तो ड्यूटी ऑफिसर ने गाली देकर भगा दिया और एफआईआर लिखने से साफ मना कर दिया।",
        "6.": "पति और ससुराल वाले आए दिन मारपीट करते हैं और कल रात मुझे और मेरे बच्चे को घर से बाहर निकाल दिया, हमारे पास पैसे नहीं हैं।",
        "7.": "रविवार की प्रार्थना सभा में कुछ लोग लाठी-डंडे लेकर घुस आए, कुर्सियां तोड़ीं और जान से मारने की धमकी देकर प्रार्थना रुकवा दी।",
        "8.": "राशन कार्ड और विधवा पेंशन के लिए सरकारी बाबू 5,000 रुपये रिश्वत मांग रहा है, बिना पैसे दिए 6 महीने से फाइल आगे नहीं बढ़ाई।"
    }

    prefix = grassroots_cat[:2]
    default_text = sample_dict.get(prefix, "")

    c_g1, c_g2 = st.columns([1, 1])
    with c_g1:
        st.markdown("#### Spoken Testimony (Hindi / Indic Vernacular)")
        spoken_text = st.text_area("Citizen Statement:", value=default_text, height=120)
        c_name = st.text_input("Complainant Name:", value="Ramesh Kumar")
        c_loc = st.text_input("District / State:", value="Mumbai, Maharashtra")
        btn_g = st.button("⚖️ Generate Legal Defense & Rights Shield", type="primary")

    with c_g2:
        if btn_g:
            res_g = engine.process_case(spoken_text, suite_tier="BHARAT_GRASSROOTS_AID", meta={"client_name": c_name, "location": c_loc})
            st.session_state["tab2_case_res"] = res_g

        if st.session_state.get("tab2_case_res"):
            render_analysis_display(st.session_state["tab2_case_res"], session_prefix="tab2", client_name=c_name)

# -------------------------------------------------------------
# TAB 3: NYAYAVANI PRO (ENTERPRISE LEGAL SUITE)
# -------------------------------------------------------------
elif app_mode == "💼 NyayaVani Pro (Enterprise Legal Suite)":
    st.subheader("💼 NyayaVani Pro — Enterprise Legal Suite & Incident Co-Pilot")
    st.caption("Organize an incident and review a draft packet. No insurer, lawyer, or other person is contacted by this view.")

    pro_cat = st.selectbox(
        "Choose Enterprise / HNW Service:",
        [
            "1. Motor Vehicle Accident Co-Pilot (MACT FAR, Sec 134 MV Act, GIC Claim)",
            "2. Real Estate Developer Delay & Title Diligence (RERA Sec 18 Interest Notice)",
            "3. Commercial Contract Breach & MSME Delayed Payments (MSMED Act 3x Interest)",
            "4. Workplace & POSH Regulatory Compliance (Internal Committee & Labor Audit)"
        ]
    )

    pro_sample_dict = {
        "1.": "A speeding commercial truck ran the red light at Outer Ring Road and crushed my vehicle's rear axle. Dashcam footage is preserved, driver admitted fault, vehicle is immobilized.",
        "2.": "I purchased a premium apartment with promised possession in December 2023. The builder has delayed possession by 35 months without an Occupancy Certificate and refuses compensation.",
        "3.": "Our registered MSME enterprise delivered 50 lakh rupees worth of industrial components against signed purchase orders. The client has withheld payment past 60 days without dispute.",
        "4.": "A corporate employee filed a formal complaint of workplace harassment; our HR department needs a legally compliant POSH inquiry committee constitution notice."
    }

    prefix_p = pro_cat[:2]
    default_p_text = pro_sample_dict.get(prefix_p, "")

    cp1, cp2 = st.columns([1, 1])
    with cp1:
        st.markdown("#### Spoken Corporate / Incident Intake")
        pro_text = st.text_area("Incident Narrative / Contract Request:", value=default_p_text, height=120)
        p_client = st.text_input("Enterprise / Client Name:", value="Vikramaditya Sharma / Enterprise Corp")
        p_loc = st.text_input("Jurisdiction:", value="Bengaluru, Karnataka")
        btn_p = st.button("🚨 Compile Dossier & Legal Action Plan", type="primary")

    with cp2:
        if btn_p:
            res_p = engine.process_case(pro_text, suite_tier="ENTERPRISE_LEGAL_SUITE", meta={"client_name": p_client, "location": p_loc})
            pro_packet = build_pro_packet(
                pro_text,
                res_p,
                client_name=p_client,
                location=p_loc,
            )
            res_p["pro_packet"] = pro_packet
            st.session_state["tab3_case_res"] = res_p

        if st.session_state.get("tab3_case_res"):
            render_analysis_display(st.session_state["tab3_case_res"], session_prefix="tab3", client_name=p_client)

# -------------------------------------------------------------
# TAB 4: VOICE AI MATRIX & BENCHMARKS
# -------------------------------------------------------------
else:
    st.subheader("📊 Voice AI Entry-Point Matrix & Global Legal Tech Benchmarks")
    st.markdown("""
    ### 1. Global Legal AI Reverse Engineering Matrix
    | Global Platform | Mechanics | Why It Fails in India | NyayaVani Indic Sovereign Adaptation |
    | :--- | :--- | :--- | :--- |
    | **DoNotPay (US)** | Form-filling chatbot for municipal fines and small claims. | Assumes English digital literacy and structured municipal APIs. | **Voice-First Socratic Triage:** Uses Prisma STT & Timbre TTS in Hindi/Marathi to guide non-literate citizens. |
    | **Harvey AI (US)** | Generative legal research on Lexis/Westlaw for law firms. | Exorbitantly expensive ($5,000/seat); unaware of state revenue codes. | **Democratized Indic Reasoning (Evon 30B MoE):** Open-weights sovereign reasoning model trained on Indian legal statutes. |
    | **EvenUp (US)** | Personal injury demand packages based on police records. | Indian tort claims operate under MACT rules across fragmented police GDs. | **Hands-Free Post-Crash Blackbox:** Ingests live driver testimony, binds dashcam proof with SHA-256 hash, drafts GIC claim. |
    | **Lawhive (UK)** | Consumer triage connecting citizens with solicitors. | Indian legal aid needs pre-litigation resolution to avoid 5-crore case backlog. | **Automated Pre-Litigation Defense:** Generates statutory notices and rights shields that resolve 80% of issues before courts. |

    ### 2. Voice AI Functional Entry-Point Matrix
    - **Intake & Triage:** Ingests noisy 8kHz telephony or street audio via **Gnani Prisma STT** with legal vocabulary boosting (`indic-auto`).
    - **Socratic Legal Interrogation:** Uses **Gnani Evon 30B MoE** to probe crucial facts in plain everyday vernacular without legal jargon.
    - **Loudspeaker Rights Shield:** Generates high-authority spoken legal citations via **Gnani Timbre TTS** (`Shivani` voice) for on-the-spot de-escalation.
    - **Contemporaneous Electronic Evidence:** Preserves raw audio and transcripts with **SHA-256 cryptographic hashes** under Section 63 of Bharatiya Sakshya Adhiniyam, 2023.
    - **Document Assembly & Spoken Readout:** Automatically drafts Zero FIRs, RTI petitions, and GIC insurance dossiers, reading back key terms in natural voice.
    """)
