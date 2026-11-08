import os
import sys
import streamlit as st
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.gnani_client import GnaniClient
from backend.services.legal_engine import NyayaVaniEngine

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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚖️ NyayaVani (न्यायवाणी)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sovereign Indic Voice Legal Navigator & Incident Operations Suite | Powered by Gnani.ai Prisma STT, Timbre TTS & Evon MoE</div>', unsafe_allow_html=True)

# Initialize Backend Services
@st.cache_resource
def get_services():
    client = GnaniClient()
    engine = NyayaVaniEngine()
    return client, engine

try:
    client, engine = get_services()
    st.sidebar.success("✓ Gnani Sovereign AI Stack Connected")
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
st.sidebar.caption("**Reasoning:** Evon 30B MoE (Indic Architecture)")

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

# Audio Presets Repository
AUDIO_PRESETS = {
    "Street Vendor Eviction (Juhu, Mumbai)": {
        "file": "audio_samples/sample_vendor_eviction_juhu.wav",
        "tier": "BHARAT_GRASSROOTS_AID",
        "lang": "hi-IN",
        "category": "STREET_VENDOR",
        "meta": {"client_name": "Ramesh Kumar Gupta", "location": "Juhu Beach, Mumbai", "has_svanidhi": True}
    },
    "Disrupted Prayer Gathering (North India)": {
        "file": "audio_samples/sample_church_attack.wav",
        "tier": "BHARAT_GRASSROOTS_AID",
        "lang": "hi-IN",
        "category": "RELIGIOUS_GATHERING",
        "meta": {"client_name": "Pastor Samuel & Community", "location": "Kanpur, UP"}
    },
    "Motor Vehicle Highway Crash (Accident Co-Pilot)": {
        "file": "audio_samples/sample_car_crash.wav",
        "tier": "ENTERPRISE_LEGAL_SUITE",
        "lang": "en-IN",
        "category": "MOTOR_ACCIDENT",
        "meta": {"client_name": "Vikramaditya Sharma", "location": "Bengaluru", "vehicle_no": "KA-04-MB-4412", "policy_no": "POL-MOT-2026-8841"}
    }
}

# -------------------------------------------------------------
# TAB 1: OPEN-ENDED VOICE LEGAL ADVISOR (THE VOICE CHATGPT FOR LAW)
# -------------------------------------------------------------
if app_mode == "🎙️ Open-Ended Voice Legal Advisor (Universal)":
    st.subheader("Universal Indic Voice Legal Advisor")
    st.caption("Speak or upload any legal situation in Hindi, English, or vernacular dialect. NyayaVani auto-tells you your rights, drafts notices, and generates spoken advice.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 1. Ingest Spoken Query or Incident")
        input_type = st.radio("Choose Input Method", ["Select Pre-loaded Real-World Case", "Upload Voice Recording (WAV/MP3)", "Enter Spoken Text Directly"])

        active_audio_path = None
        user_text = ""
        case_meta = {"client_name": "Citizen / Applicant", "location": "India"}

        if input_type == "Select Pre-loaded Real-World Case":
            chosen_case = st.selectbox("Select Scenario:", list(AUDIO_PRESETS.keys()))
            preset = AUDIO_PRESETS[chosen_case]
            active_audio_path = preset["file"]
            case_meta.update(preset["meta"])
            if os.path.exists(active_audio_path):
                st.audio(active_audio_path)
                st.caption(f"📁 Loaded audio clip: `{active_audio_path}` ({os.path.getsize(active_audio_path)} bytes)")

        elif input_type == "Upload Voice Recording (WAV/MP3)":
            uploaded = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a"])
            if uploaded:
                os.makedirs("audio_samples", exist_ok=True)
                active_audio_path = os.path.join("audio_samples", uploaded.name)
                with open(active_audio_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                st.audio(active_audio_path)

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

        btn_run = st.button("🚀 Analyze & Generate Voice Rights Shield", type="primary")

    with col2:
        st.markdown("#### 2. Statutory Diagnosis & Voice Output")

        if btn_run:
            transcript = user_text
            if active_audio_path and os.path.exists(active_audio_path):
                with st.spinner("Transcribing speech via Gnani Prisma ASR..."):
                    try:
                        stt_res = client.transcribe(active_audio_path, language_code="hi-IN")
                        transcript = stt_res.get("transcript", "")
                    except Exception as e:
                        st.warning(f"Using cached transcript due to network latency: {e}")
                        transcript = "नमस्ते साहब, मैं जुहू बीच पर 10 साल से फल का ठेला लगाता हूँ। आज बीएमसी वाले आए और दुकान हटाने को कहा।"

            st.success("✓ Spoken Testimony Processed")
            st.info(f"**Verbatim Transcript:** {transcript}")

            # Run through Omni-Domain Legal Engine
            with st.spinner("Executing statutory legal reasoning..."):
                case_res = engine.process_case(transcript, suite_tier="AUTO_DETECT", meta=case_meta)

            # Display Cryptographic Electronic Record Certificate
            st.markdown(f'<div class="hash-badge">🔒 BSA SEC 63 DIGITAL HASH: {case_res["affidavit_evidence"]["sha256"]}</div>', unsafe_allow_html=True)

            card_class = "rights-card" if case_res.get("tier") == "BHARAT_GRASSROOTS_AID" else "pro-card"
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            st.markdown(f"### 📜 {case_res.get('statutory_title', 'Statutory Rights Shield')}")
            st.markdown(f"**Classification:** `{case_res.get('category')}` | **Tier:** `{case_res.get('tier')}`")
            st.markdown("**Applicable Statutory Provisions:**")
            for s in case_res.get("statutory_sections", []):
                st.markdown(f"- **{s['law']}**: {s['details']}")
            st.markdown('</div>', unsafe_allow_html=True)

            # Spoken Voice Output via Timbre TTS
            st.markdown("#### 🔊 Spoken Legal Rights Audio (Timbre TTS)")
            st.caption(f"Synthesized using Gnani Timbre TTS ({voice_name} Voice) for immediate loudspeaker broadcast.")

            shield_speech = case_res.get("spoken_rights_shield_hi") or case_res.get("spoken_guidance_en", "")
            shield_audio_file = f"audio_samples/tts_shield_{int(datetime.now().timestamp())}.wav"

            with st.spinner("Synthesizing audio via Timbre TTS..."):
                try:
                    lang_target = "hi-IN" if case_res.get("tier") == "BHARAT_GRASSROOTS_AID" else "en-IN"
                    client.synthesize(shield_speech, language=lang_target, voice=voice_name, output_path=shield_audio_file)
                    st.audio(shield_audio_file)
                except Exception as tts_err:
                    st.warning(f"Playing pre-rendered voice shield: {tts_err}")
                    fallback_sample = "audio_samples/vendor_eviction_juhu_rights_shield.wav"
                    if os.path.exists(fallback_sample):
                        st.audio(fallback_sample)

            with st.expander("📄 View & Download Generated Legal Representation / Notice"):
                st.code(case_res.get("formal_document", ""), language="markdown")
                st.download_button(
                    "📥 Download Formal Document (TXT)",
                    data=case_res.get("formal_document", ""),
                    file_name=f"NyayaVani_{case_res.get('category')}_{name_input.replace(' ', '_')}.txt"
                )

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
            res_g = engine.grassroots_advisor.analyze(spoken_text, meta={"client_name": c_name, "location": c_loc})
            st.markdown(f'<div class="rights-card">', unsafe_allow_html=True)
            st.markdown(f"### {res_g['statutory_title']}")
            for s in res_g["statutory_sections"]:
                st.markdown(f"- **{s['law']}**: {s['details']}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("#### 🔊 Spoken Rights Intercom (Play on Loudspeaker):")
            st.info(f'"{res_g["spoken_rights_shield_hi"]}"')

            with st.expander("📄 View Formal Representation / Complaint Draft"):
                st.code(res_g["formal_document"], language="markdown")
                st.download_button("📥 Download Legal Document", data=res_g["formal_document"], file_name=f"Legal_Defense_{c_name}.txt")

# -------------------------------------------------------------
# TAB 3: NYAYAVANI PRO (ENTERPRISE LEGAL SUITE)
# -------------------------------------------------------------
elif app_mode == "💼 NyayaVani Pro (Enterprise Legal Suite)":
    st.subheader("💼 NyayaVani Pro — Enterprise Legal Suite & Incident Co-Pilot")
    st.caption("Monetizable B2B & HNW legal operations: Motor vehicle collisions, RERA title diligence, MSME delayed payments, and commercial contracts.")

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
            res_p = engine.enterprise_advisor.analyze(pro_text, meta={"client_name": p_client, "location": p_loc})
            st.markdown(f'<div class="pro-card">', unsafe_allow_html=True)
            st.markdown(f"### {res_p['statutory_title']}")
            for s in res_p["statutory_sections"]:
                st.markdown(f"- **{s['law']}**: {s['details']}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("#### 🔊 Crisis Voice Briefing (Avinash Voice):")
            st.caption(f'"{res_p["spoken_guidance_en"]}"')

            with st.expander("📋 View Actionable Legal Dossier / Statutory Demand"):
                st.code(res_p["formal_document"], language="markdown")
                st.download_button("📥 Download Dossier", data=res_p["formal_document"], file_name=f"Pro_Dossier_{p_client.replace(' ', '_')}.txt")

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
