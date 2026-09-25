import streamlit as st
import os
import time
import json

from agent import AGENT_STAGES, execute_agent_workflow, get_api_key
from services_data import SERVICES_DATABASE


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NextStep AI | Public Service Navigation Assistant",
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


# ============================================================
# CUSTOM CSS FOR PREMIUM CHAT LOOK
# ============================================================

st.markdown("""
<style>
    /* Main container background */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Primary & secondary button overrides for high contrast */
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

    /* Force readable text colors for headers and text elements */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
    }

    /* Checkbox labels */
    [data-testid="stCheckbox"] label {
        color: #f8fafc !important;
    }

    /* Custom Navbar Header */
    .nav-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-bottom: 1px solid #334155;
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .brand-title {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .brand-subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 2px;
    }

    .badge-telangana {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    .badge-central {
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    /* Agent Stage Progress Panel */
    .stage-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
    }

    .stage-item {
        display: flex;
        align-items: center;
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.3rem;
        transition: all 0.3s ease;
    }

    .stage-item.completed {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
    }

    .stage-item.active {
        background: rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.5);
        color: #38bdf8;
        font-weight: 600;
    }

    .stage-item.pending {
        background: rgba(51, 65, 85, 0.3);
        color: #64748b;
    }

    /* Response Card Container */
    .card-response {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.5rem;
        margin-top: 0.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    /* Official Disclaimer Banner */
    .disclaimer-banner {
        background: rgba(30, 41, 59, 0.8);
        border-left: 4px solid #38bdf8;
        padding: 0.8rem;
        border-radius: 6px;
        font-size: 0.82rem;
        color: #cbd5e1;
        margin-top: 1.5rem;
    }

    /* Quick Reply Chip Buttons */
    .quick-chip {
        background: #334155;
        color: #f8fafc;
        border: 1px solid #475569;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s;
    }

    .quick-chip:hover {
        background: #0284c7;
        border-color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 🏛️ NextStep AI Settings")
    st.caption("AI Navigation Assistant for Indian Government Services")

    st.divider()

    # Language Selector
    st.markdown("#### 🌐 Language Preference")
    selected_lang = st.selectbox(
        "Choose Interface Language:",
        ["English", "Telugu (తెలుగు)", "Hindi (हिंदी)"],
        index=["English", "Telugu (తెలుగు)", "Hindi (हिंदी)"].index(
            "Telugu (తెలుగు)" if "Telugu" in st.session_state.selected_language else
            ("Hindi (हिंदी)" if "Hindi" in st.session_state.selected_language else "English")
        )
    )
    if selected_lang != st.session_state.selected_language:
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
        st.success("🟢 Gemini API Backend Connected")
    else:
        st.info("ℹ️ Using Verified Local Knowledge Engine (No Key Set)")

    st.divider()

    st.markdown("#### ⚡ Core Supported Services")
    st.markdown("- 🛂 **Passport** (Central / MEA)")
    st.markdown("- 🪪 **Aadhaar** (Central / UIDAI)")
    st.markdown("- 💳 **PAN Card** (Central / Income Tax)")
    st.markdown("- 👶 **Birth Certificate** (Telangana / MeeSeva)")
    st.markdown("- 🏠 **Property Tax** (Telangana / GHMC)")

    st.divider()

    if st.button("🔄 Clear Chat Conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.caption("NextStep AI v2.5 • Conversational Edition")


# ============================================================
# TOP NAVBAR
# ============================================================

st.markdown("""
<div class="nav-header">
    <div>
        <div class="brand-title">🏛️ NextStep AI</div>
        <div class="brand-subtitle">AI Public-Service Navigation Assistant • India & Telangana State</div>
    </div>
    <div>
        <span class="badge-telangana">Telangana MeeSeva / GHMC Ready</span>
        <span class="badge-central" style="margin-left: 8px;">Central Services Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# CORE SUPPORTED SERVICE CARDS (1-CLICK QUICK TRIGGERS)
# ============================================================

st.markdown("##### 🚀 Quick Service Triggers")

cols = st.columns(5)

with cols[0]:
    if st.button("Passport\n\nApply/Renew", use_container_width=True):
        st.session_state.pending_prompt = "How do I apply for or renew my Indian Passport in Telangana?"

with cols[1]:
    if st.button("Aadhaar\n\nUpdate/Download", use_container_width=True):
        st.session_state.pending_prompt = "How do I update my mobile number or address in my Aadhaar card?"

with cols[2]:
    if st.button("PAN Card\n\nInstant e-PAN", use_container_width=True):
        st.session_state.pending_prompt = "I need an instant e-PAN card using Aadhaar card."

with cols[3]:
    if st.button("Birth Cert\n\nMeeSeva / GHMC", use_container_width=True):
        st.session_state.pending_prompt = "I need to apply for a birth certificate in Hyderabad, Telangana."

with cols[4]:
    if st.button("Property Tax\n\nGHMC / CDMA", use_container_width=True):
        st.session_state.pending_prompt = "How do I calculate and pay GHMC property tax online in Telangana?"


# ============================================================
# RENDER CHAT HISTORY MESSAGES & STRUCTURED CARDS
# ============================================================

def render_response_card(res, index):
    st.markdown('<div class="card-response">', unsafe_allow_html=True)

    # Header & Jurisdiction Badge
    col_res_header, col_res_badge = st.columns([3, 1])
    with col_res_header:
        st.markdown(f"### 🎯 {res.get('service_name', 'Government Service Navigation')}")
        st.write(f"**Overview**: {res.get('summary', '')}")

    with col_res_badge:
        jurisdiction = res.get('jurisdiction', 'Central')
        j_label = res.get('jurisdiction_label', 'Government Service')
        if jurisdiction.lower() == "telangana":
            st.markdown(f'<div style="text-align:right;"><span class="badge-telangana">{j_label}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="text-align:right;"><span class="badge-central">{j_label}</span></div>', unsafe_allow_html=True)

    st.markdown("---")

    col_docs, col_steps = st.columns([1, 1])

    # 1. Document Checklist
    with col_docs:
        st.markdown("#### 📋 Required Documents Checklist")
        docs = res.get("documents", [])
        if docs:
            for i, doc in enumerate(docs):
                doc_name = doc.get("name", "Document")
                is_req = doc.get("required", False)
                notes = doc.get("notes", "")

                req_badge = "🔴 Mandatory" if is_req else "🟡 Optional / Conditional"
                checkbox_key = f"doc_chk_{index}_{res.get('service_id', 'srv')}_{i}"

                st.checkbox(f"{doc_name}", key=checkbox_key, help=notes)
                st.caption(f"&nbsp;&nbsp;&nbsp;&nbsp;*{req_badge}* — {notes}")
        else:
            st.info("No specific physical documents required for this step.")

    # 2. Personalized Next Steps
    with col_steps:
        st.markdown("#### 🗺️ Personalized Next Steps")
        steps = res.get("steps", [])
        for step in steps:
            s_num = step.get("step", 1)
            s_title = step.get("title", f"Step {s_num}")
            s_desc = step.get("description", "")

            with st.expander(f"Step {s_num}: {s_title}", expanded=(s_num == 1)):
                st.write(s_desc)

    # 3. Verified Portal Source
    st.markdown("---")
    col_verif_info, col_verif_link = st.columns([3, 2])

    with col_verif_info:
        if res.get("is_verified_url"):
            st.success(f"✅ **Verified Official Source**: {res.get('portal_name', 'Official Portal')}")
        else:
            st.warning("⚠️ **Unverified Source**: Please confirm on the official state portal.")
        st.write(f"**Verification Notes**: {res.get('verification_notes', '')}")
        st.info(f"👉 **Immediate Next Step**: {res.get('next_action', 'Visit official portal.')}")

    with col_verif_link:
        st.markdown("##### Direct Official Portal")
        official_url = res.get("official_url", "https://www.india.gov.in/")
        portal_name = res.get("portal_name", "Official Government Portal")
        st.link_button(f"🌐 Open {portal_name}", official_url, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


st.markdown("---")
st.markdown("### 💬 Conversational Navigation Assistant")

# Welcome Banner if Chat is Empty
if not st.session_state.chat_history:
    st.info("👋 **Welcome to NextStep AI!** Describe your government service situation in natural language, or click any quick trigger button above to begin.")

# Display Existing Chat Messages
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
q_cols = st.columns(4)
with q_cols[0]:
    if st.button("📋 Show documents", use_container_width=True):
        st.session_state.pending_prompt = "Show required documents"
with q_cols[1]:
    if st.button("🗺️ What should I do next?", use_container_width=True):
        st.session_state.pending_prompt = "What should I do next?"
with q_cols[2]:
    if st.button("🔍 Explain this", use_container_width=True):
        st.session_state.pending_prompt = "Explain this service process in detail."
with q_cols[3]:
    if st.button("🔄 Start over", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.pending_prompt = None
        st.rerun()


# ============================================================
# INPUT AREA (CHAT INPUT & VOICE INPUT FALLBACK)
# ============================================================

st.markdown("")
input_col, audio_col = st.columns([5, 1], vertical_alignment="bottom")

with input_col:
    chat_prompt = st.chat_input("Ask NextStep AI about any government service or process...")

with audio_col:
    audio_val = st.audio_input("🎙️ Voice Input", key="audio_mic")


if audio_val is not None and "audio_processed" not in st.session_state:
    st.info("🎙️ Voice recorded! (Speech-to-text requires cloud audio API key; processing transcript fallback)")
    st.session_state.pending_prompt = "I need help with a government service application in Telangana."
    st.session_state.audio_processed = True


# Determine active prompt to process
active_user_prompt = chat_prompt or st.session_state.pending_prompt

if active_user_prompt:
    st.session_state.pending_prompt = None

    # Append user message
    st.session_state.chat_history.append({"role": "user", "content": active_user_prompt})

    with st.chat_message("user", avatar="👤"):
        st.markdown(active_user_prompt)

    # Agent Processing & Stage Animation
    with st.chat_message("assistant", avatar="🏛️"):
        progress_container = st.empty()

        def update_stage_ui(active_stage_id, stage_title, stage_desc):
            stage_html = '<div class="stage-box"><h5>Agent Workflow Stages Execution</h5>'
            for s in AGENT_STAGES:
                s_id = s["id"]
                if s_id < active_stage_id:
                    status_class = "stage-item completed"
                    badge = "✅"
                elif s_id == active_stage_id:
                    status_class = "stage-item active"
                    badge = "⏳"
                else:
                    status_class = "stage-item pending"
                    badge = "⚪"

                stage_html += f"""
                <div class="{status_class}">
                    <span style="margin-right:10px; font-size:1.1rem;">{badge} {s['icon']}</span>
                    <div>
                        <strong>Stage {s_id}: {s['title']}</strong> - <span style="font-size:0.85rem;">{s['description']}</span>
                    </div>
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

        update_stage_ui(6, "Completed", "Response Generated")
        time.sleep(0.2)
        progress_container.empty()

        if response.get("success"):
            card_data = response["data"]
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": card_data.get("summary", ""),
                "card_data": card_data
            })
            render_response_card(card_data, len(st.session_state.chat_history))
        else:
            st.error("Failed to process request. Please try again.")

    st.rerun()


# MANDATORY DISCLAIMER FOOTER
st.markdown("""
<div class="disclaimer-banner">
    🔒 <strong>NextStep AI Disclaimer</strong>: NextStep AI is an independent AI navigational guidance assistant.
    It does not submit government applications on your behalf, bypass government authentication/OTP controls, or access private government databases.
    Always verify official fees and final requirements directly on official <code>.gov.in</code> websites.
</div>
""", unsafe_allow_html=True)
