import streamlit as st
import os
import time
import json
import hashlib

from agent import AGENT_STAGES, execute_agent_workflow, get_api_key, transcribe_audio_bytes
from services_data import SERVICES_DATABASE


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NextStep AI • v2.2 | Government Navigation & Form Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HELPER FOR SAFE SECRETS ACCESS
# ============================================================

def safe_get_secrets():
    try:
        return st.secrets
    except Exception:
        return None


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"

if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = os.environ.get("GEMINI_API_KEY", "")

if "active_progress" not in st.session_state:
    st.session_state.active_progress = {
        "situation_understood": False,
        "service_identified": False,
        "documents_identified": False,
        "next_action_ready": False,
        "final_submission_completed": False
    }

if "processed_audio_hashes" not in st.session_state:
    st.session_state.processed_audio_hashes = set()

if "voice_status_message" not in st.session_state:
    st.session_state.voice_status_message = None


# ============================================================
# CUSTOM CSS FOR SaaS-STYLE UI
# ============================================================

st.markdown("""
<style>
    /* Main container background */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Force readable text colors for headers and text elements */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }

    /* Button overrides for contrast */
    .stButton > button {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border-color: #38bdf8 !important;
    }

    /* Navbar Header */
    .nav-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-bottom: 1px solid #334155;
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .brand-title {
        font-size: 1.9rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .brand-tagline {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 4px;
        font-style: italic;
    }

    .version-badge {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .badge-telangana {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .badge-central {
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Meta Info Card */
    .meta-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.8rem;
    }

    /* Form Field Mapping Box */
    .form-workspace-card {
        background: #1e293b;
        border: 1px solid #0284c7;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
    }

    .form-field-row {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Progress Visualizer Bar */
    .progress-bar-container {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin: 1rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .progress-step {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
    }

    .progress-step.done {
        color: #34d399;
    }

    .progress-step.current {
        color: #38bdf8;
        font-weight: 700;
    }

    /* Document Card Styling */
    .doc-tag-req {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .doc-tag-opt {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    /* Card Response Container */
    .card-response {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.5rem;
        margin-top: 0.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    /* Disclaimer Banner */
    .disclaimer-banner {
        background: rgba(30, 41, 59, 0.8);
        border-left: 4px solid #38bdf8;
        padding: 0.8rem;
        border-radius: 6px;
        font-size: 0.82rem;
        color: #cbd5e1;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 🏛️ NextStep AI Settings")
    st.caption("AI Public Service Navigation & Form Assistant")

    st.markdown('<span class="version-badge">NextStep AI • v2.2</span>', unsafe_allow_html=True)
    st.divider()

    # Language Selector
    st.markdown("#### 🌐 Language Preference")
    selected_lang = st.selectbox(
        "Choose Interface Language:",
        ["English", "Telugu (తెలుగు)", "Hindi (हिंदी)"],
        index=0
    )
    st.session_state.selected_language = selected_lang

    st.divider()

    st.markdown("#### 🔑 Gemini API Configuration")
    user_key = st.text_input(
        "Enter Gemini API Key (Optional)",
        value=st.session_state.user_api_key,
        type="password",
        help="Provide your Google Gemini API key. If empty, NextStep AI uses its verified local government knowledge base."
    )
    if user_key != st.session_state.user_api_key:
        st.session_state.user_api_key = user_key

    active_key = get_api_key(safe_get_secrets()) or st.session_state.user_api_key
    if active_key:
        st.success("🟢 Gemini API Backend Active")
    else:
        st.info("ℹ️ Using Verified Local Knowledge Engine")

    st.divider()

    st.markdown("#### ⚡ Core Service Categories")
    st.markdown("- 🛂 Passport Services (Central)")
    st.markdown("- 🪪 Aadhaar & UIDAI (Central)")
    st.markdown("- 💳 PAN Card & ITR Filing (Central)")
    st.markdown("- 🗳️ Voter ID / e-EPIC (Central)")
    st.markdown("- 🚗 Driving Licence & RTO (Telangana / Parivahan)")
    st.markdown("- 👶 Birth & Death Certificates (MeeSeva / GHMC)")
    st.markdown("- 📑 Caste & Income Certificates (MeeSeva TS)")
    st.markdown("- 🏠 Property Tax Payment (GHMC / CDMA)")
    st.markdown("- 🎓 Telangana ePASS & Welfare Schemes")
    st.markdown("- 💼 Business Udyam Registration (Central & TS)")

    st.divider()

    if st.button("🔄 Start over / Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.pending_prompt = None
        st.session_state.active_progress = {
            "situation_understood": False,
            "service_identified": False,
            "documents_identified": False,
            "next_action_ready": False,
            "final_submission_completed": False
        }
        st.rerun()

    st.caption("NextStep AI • v2.2 Production Edition")


# ============================================================
# TOP NAVBAR
# ============================================================

st.markdown("""
<div class="nav-header">
    <div>
        <div class="brand-title">🏛️ NextStep AI</div>
        <div class="brand-tagline">"Tell us what happened. We'll help you figure out what to do next."</div>
    </div>
    <div>
        <span class="version-badge">NextStep AI • v2.2</span>
        <span class="badge-telangana" style="margin-left:8px;">Telangana MeeSeva / GHMC</span>
        <span class="badge-central" style="margin-left:8px;">Central Services</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# TASK PROGRESS TRACKER VISUALIZER
# ============================================================

prog = st.session_state.active_progress
p_s1 = "progress-step done" if prog.get("situation_understood") else "progress-step"
p_s2 = "progress-step done" if prog.get("service_identified") else "progress-step"
p_s3 = "progress-step done" if prog.get("documents_identified") else "progress-step"
p_s4 = "progress-step current" if prog.get("next_action_ready") else "progress-step"
p_s5 = "progress-step"

st.markdown(f"""
<div class="progress-bar-container">
    <div class="{p_s1}">{'✓' if prog.get('situation_understood') else '○'} Situation Understood</div>
    <div>→</div>
    <div class="{p_s2}">{'✓' if prog.get('service_identified') else '○'} Service Identified</div>
    <div>→</div>
    <div class="{p_s3}">{'✓' if prog.get('documents_identified') else '○'} Documents Identified</div>
    <div>→</div>
    <div class="{p_s4}">{'➔' if prog.get('next_action_ready') else '○'} Next Action Ready</div>
    <div>→</div>
    <div class="{p_s5}">○ Final Portal Submission</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# QUICK SERVICE TRIGGERS
# ============================================================

st.markdown("##### 🚀 Popular Natural Language Scenarios")

cols = st.columns(4)
with cols[0]:
    if st.button("📍 Moved to Hyderabad\n\nUpdate address in Aadhaar & Voter ID", use_container_width=True):
        st.session_state.pending_prompt = "I moved from another state to Hyderabad and need to update my address in my government documents."
with cols[1]:
    if st.button("👶 New Born Registration\n\nApply for Birth Certificate GHMC", use_container_width=True):
        st.session_state.pending_prompt = "I need to register my newborn child's birth certificate in GHMC Hyderabad."
with cols[2]:
    if st.button("📑 Caste & Income Cert\n\nApply via MeeSeva Telangana", use_container_width=True):
        st.session_state.pending_prompt = "How do I apply for an Income Certificate and Caste Certificate on MeeSeva Telangana?"
with cols[3]:
    if st.button("📝 Form Filling Assistant\n\nHelp fill Passport / Driving Licence Form", use_container_width=True):
        st.session_state.pending_prompt = "My name is K. Rajesh, DOB 15/08/1995, address Jubilee Hills Hyderabad. Help me fill the Passport application form."


# ============================================================
# RENDER RESPONSE CARD COMPONENTS
# ============================================================

def render_response_card(res, index):
    st.markdown('<div class="card-response">', unsafe_allow_html=True)

    # 1. Header & Jurisdiction
    col_res_header, col_res_badge = st.columns([3, 1])
    with col_res_header:
        st.markdown(f"### 🎯 {res.get('service_name', 'Government Service Assistant')}")
        if res.get("situation_understood"):
            st.info(f"💡 **What NextStep AI Understood**: {res.get('situation_understood')}")

    with col_res_badge:
        jurisdiction = res.get('jurisdiction', 'Central')
        j_label = res.get('jurisdiction_label', 'Government Service')
        if jurisdiction.lower() == "telangana":
            st.markdown(f'<div style="text-align:right;"><span class="badge-telangana">{j_label}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="text-align:right;"><span class="badge-central">{j_label}</span></div>', unsafe_allow_html=True)

    # 2. Service Discovery Metadata Box (Eligibility, Fees, Timeline)
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.markdown("<div class='meta-box'><strong>⚖️ Eligibility</strong><br><small>" + str(res.get("eligibility", "Verified eligibility rules apply.")) + "</small></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown("<div class='meta-box'><strong>💰 Fees</strong><br><small>" + str(res.get("fees", "Official portal fees apply.")) + "</small></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown("<div class='meta-box'><strong>⏱️ Processing Time</strong><br><small>" + str(res.get("processing_time", "Standard turnaround timeline.")) + "</small></div>", unsafe_allow_html=True)

    if res.get("uncertainty_note"):
        st.caption(f"ℹ️ **Note on Uncertainty / Verification**: {res.get('uncertainty_note')}")

    # Clarification Alert if crucial details missing
    if res.get("clarification_needed"):
        st.warning(f"❓ **Clarification Needed**: {res.get('clarification_needed')}")

    # 3. AI-Assisted Form Filling Workspace Panel
    if res.get("form_assistant_payload"):
        fp = res["form_assistant_payload"]
        st.markdown('<div class="form-workspace-card">', unsafe_allow_html=True)
        st.markdown(f"#### 📝 AI-Assisted Form Workspace: {fp.get('form_name', 'Official Form')}")
        st.write(f"**Instructions**: {fp.get('portal_fill_instructions', 'Review and transfer details onto the official portal.')}")

        mapped = fp.get("mapped_fields", [])
        if mapped:
            st.markdown("##### Mapped Form Fields:")
            for field in mapped:
                field_label = field.get("label", "Field")
                field_val = field.get("value", "Not provided")
                field_req = field.get("required", False)

                req_str = "🔴 Required" if field_req else "⚪ Optional"
                st.text_input(f"{field_label} ({req_str})", value=field_val, key=f"form_fld_{index}_{field.get('field_id', 'fld')}")

        missing = fp.get("missing_required_fields", [])
        if missing:
            st.warning(f"⚠️ **Missing Required Fields**: {', '.join(missing)}")

        st.caption("🔒 *NextStep AI prepares these details locally for your review. Complete final submission on the official portal.*")
        st.markdown('</div>', unsafe_allow_html=True)

    # Notice Analysis Panel
    if res.get("notice_analysis"):
        na = res["notice_analysis"]
        st.markdown("#### 📜 Government Notice / Letter Decoder")
        st.write(f"**Explanation**: {na.get('simple_explanation', '')}")
        st.write(f"**Action Requested**: {na.get('requested_action', '')}")
        st.write(f"**Important Deadlines**: {na.get('important_dates', 'Check notice header')}")
        st.caption("⚠️ Notice explanation is informational. Verify official requirements against the issuing authority.")

    # "Do It For Me" Workspace Panel
    if res.get("do_it_for_me_workspace"):
        dw = res["do_it_for_me_workspace"]
        st.markdown("#### 🛠️ 'Do It For Me' Action Workspace")
        st.success(f"**Automated Prep Notice**: {dw.get('portal_notice', '')}")
        if dw.get("prepared_draft_fields"):
            st.markdown("##### Prepared Form Field Details:")
            st.json(dw["prepared_draft_fields"])

    st.markdown("---")

    col_docs, col_steps = st.columns([1, 1])

    # Document Checklist Cards
    with col_docs:
        st.markdown("#### 📋 Document Intelligence Checklist")
        docs = res.get("documents", [])
        if docs:
            for i, doc in enumerate(docs):
                doc_name = doc.get("name", "Document")
                is_req = doc.get("required", False)
                status_text = doc.get("status", "Typically required" if is_req else "May be required depending on your case")
                why = doc.get("why_needed", "")
                check_note = doc.get("check_note", "")

                tag_class = "doc-tag-req" if is_req else "doc-tag-opt"

                st.checkbox(f"**{doc_name}**", key=f"chk_{index}_{i}", help=why)
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<span class='{tag_class}'>{status_text}</span>", unsafe_allow_html=True)
                st.caption(f"&nbsp;&nbsp;&nbsp;&nbsp;• *Why needed*: {why}\n&nbsp;&nbsp;&nbsp;&nbsp;• *What to check*: {check_note}")
        else:
            st.info("No specific physical documents required for this step.")

    # Personalized Steps
    with col_steps:
        st.markdown("#### 🗺️ Personalized Action Plan")
        steps = res.get("steps", [])
        for step in steps:
            s_num = step.get("step", 1)
            s_title = step.get("title", f"Step {s_num}")
            s_desc = step.get("description", "")

            with st.expander(f"Step {s_num}: {s_title}", expanded=(s_num == 1)):
                st.write(s_desc)

    # Official Source & Immediate Action
    st.markdown("---")
    col_verif_info, col_verif_link = st.columns([3, 2])

    with col_verif_info:
        if res.get("is_verified_url"):
            st.success(f"✅ **Verified Official Source**: {res.get('portal_name', 'Official Portal')}")
        else:
            st.warning("⚠️ **Unverified Source**: Please confirm on the official government portal.")
        st.write(f"**Verification Notes**: {res.get('verification_notes', '')}")
        st.info(f"👉 **Immediate Next Action**: {res.get('next_action', 'Visit official portal.')}")

    with col_verif_link:
        st.markdown("##### Direct Official Government Portal")
        official_url = res.get("official_url", "https://www.india.gov.in/")
        portal_name = res.get("portal_name", "Official Government Portal")
        st.link_button(f"🌐 Open {portal_name}", official_url, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# CHAT INTERFACE
# ============================================================

st.markdown("### 💬 Conversational AI Assistant")

if not st.session_state.chat_history:
    st.info("👋 **Welcome to NextStep AI!** Describe your situation naturally (e.g. *'I moved to Hyderabad and need to update my documents'* or paste a government notice / ask for form filling assistance).")

for idx, message in enumerate(st.session_state.chat_history):
    role = message.get("role")
    content = message.get("content")
    card_data = message.get("card_data")

    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
    elif role == "assistant":
        with st.chat_message("assistant", avatar="🏛️"):
            if card_data:
                render_response_card(card_data, idx)
            else:
                st.markdown(content)


# ============================================================
# QUICK ACTION BUTTONS BAR
# ============================================================

st.markdown("")
st.caption("💡 Quick Assistant Actions:")
q_cols = st.columns(5)
with q_cols[0]:
    if st.button("🗺️ What should I do next?", use_container_width=True):
        st.session_state.pending_prompt = "What should I do next?"
with q_cols[1]:
    if st.button("📋 Show required documents", use_container_width=True):
        st.session_state.pending_prompt = "Show required documents"
with q_cols[2]:
    if st.button("🔍 Explain this", use_container_width=True):
        st.session_state.pending_prompt = "Explain this process in detail."
with q_cols[3]:
    if st.button("🌐 Find official website", use_container_width=True):
        st.session_state.pending_prompt = "Where is the verified official website link?"
with q_cols[4]:
    if st.button("📝 Help me fill form", use_container_width=True):
        st.session_state.pending_prompt = "Help me fill the application form for this service."


# ============================================================
# CHAT INPUT & VOICE INPUT FALLBACK
# ============================================================

st.markdown("")
input_col, audio_col = st.columns([5, 1], vertical_alignment="bottom")

with input_col:
    chat_prompt = st.chat_input("Describe your situation or enter details to fill a form...")

with audio_col:
    audio_val = st.audio_input("🎙️ Voice", key="audio_mic")

# Process Voice Input if audio is present and hasn't been processed yet
if audio_val is not None:
    try:
        if hasattr(audio_val, "seek"):
            audio_val.seek(0)
        audio_bytes = audio_val.read()
        if hasattr(audio_val, "seek"):
            audio_val.seek(0)
        audio_hash = hashlib.sha256(audio_bytes).hexdigest() if audio_bytes else None

        if audio_hash and audio_hash not in st.session_state.processed_audio_hashes:
            st.session_state.processed_audio_hashes.add(audio_hash)

            api_key_for_transcription = get_api_key(safe_get_secrets()) or st.session_state.user_api_key
            transcription_res = transcribe_audio_bytes(audio_bytes, api_key_for_transcription)

            if transcription_res.get("success"):
                transcribed_text = transcription_res["text"]
                st.session_state.voice_status_message = f"🎙️ Transcribed Voice Question: \"{transcribed_text}\""
                st.session_state.pending_prompt = transcribed_text
            else:
                st.session_state.voice_status_message = None
                st.warning(f"⚠️ {transcription_res.get('message', 'Voice input was empty or unclear. Please try speaking again.')}")
    except Exception as e:
        st.error(f"Error reading voice recording: {e}")

if st.session_state.voice_status_message:
    st.info(st.session_state.voice_status_message)


# ============================================================
# PROCESS AGENT WORKFLOW ON ACTIVE PROMPT
# ============================================================

# Priority order: Typed chat prompt overrides button/voice pending prompt
if chat_prompt:
    active_user_prompt = chat_prompt
    st.session_state.pending_prompt = None
    st.session_state.voice_status_message = None
elif st.session_state.pending_prompt:
    active_user_prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
else:
    active_user_prompt = None

if active_user_prompt:
    # Preserve transcribed voice notice in message content if voice was used
    user_display_content = active_user_prompt
    if st.session_state.voice_status_message:
        user_display_content = f"🎙️ *(Voice Transcribed)* {active_user_prompt}"
        st.session_state.voice_status_message = None

    # Append user message
    st.session_state.chat_history.append({"role": "user", "content": user_display_content})

    with st.chat_message("user", avatar="👤"):
        st.markdown(active_user_prompt)

    # Agent Execution & Animated Stage UI
    with st.chat_message("assistant", avatar="🏛️"):
        progress_container = st.empty()

        def update_stage_ui(active_stage_id, stage_title, stage_desc):
            stage_html = '<div style="background:#1e293b; border:1px solid #334155; border-radius:12px; padding:1rem; margin:1rem 0;">'
            stage_html += '<h5 style="margin-top:0;">Executing 9-Stage Agent Workflow</h5>'
            for s in AGENT_STAGES:
                s_id = s["id"]
                if s_id < active_stage_id:
                    status_style = "color:#34d399; background:rgba(16, 185, 129, 0.1); border:1px solid rgba(16, 185, 129, 0.3);"
                    badge = "✅"
                elif s_id == active_stage_id:
                    status_style = "color:#38bdf8; background:rgba(56, 189, 248, 0.15); border:1px solid rgba(56, 189, 248, 0.5); font-weight:bold;"
                    badge = "⏳"
                else:
                    status_style = "color:#64748b; background:rgba(51, 65, 85, 0.3);"
                    badge = "⚪"

                stage_html += f"""
                <div style="display:flex; align-items:center; padding:0.4rem 0.8rem; border-radius:6px; margin-bottom:0.25rem; {status_style}">
                    <span style="margin-right:8px;">{badge} {s['icon']}</span>
                    <div><strong>Stage {s_id}: {s['title']}</strong> - <span style="font-size:0.82rem;">{s['description']}</span></div>
                </div>
                """
            stage_html += '</div>'
            progress_container.markdown(stage_html, unsafe_allow_html=True)

        api_key_to_use = get_api_key(safe_get_secrets()) or st.session_state.user_api_key

        response = execute_agent_workflow(
            user_query=active_user_prompt,
            api_key=api_key_to_use,
            history=st.session_state.chat_history,
            language=st.session_state.selected_language,
            progress_callback=update_stage_ui
        )

        update_stage_ui(10, "Complete", "Response Rendered")
        time.sleep(0.15)
        progress_container.empty()

        if response.get("success"):
            card_data = response["data"]

            # Update session progress state
            st.session_state.active_progress = {
                "situation_understood": True,
                "service_identified": True,
                "documents_identified": len(card_data.get("documents", [])) > 0,
                "next_action_ready": True,
                "final_submission_completed": False
            }

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": card_data.get("situation_understood", ""),
                "card_data": card_data
            })
            render_response_card(card_data, len(st.session_state.chat_history))
        else:
            st.error("Failed to process request. Please try again.")

    st.rerun()


# MANDATORY DISCLAIMER FOOTER
st.markdown("""
<div class="disclaimer-banner">
    🔒 <strong>NextStep AI Disclaimer</strong>: NextStep AI is an independent AI navigational guidance & form assistant.
    It does not submit government applications on your behalf, bypass OTP/CAPTCHA controls, or access private government databases.
    Always verify official fees and legal requirements directly on official <code>.gov.in</code> websites.
</div>
""", unsafe_allow_html=True)
