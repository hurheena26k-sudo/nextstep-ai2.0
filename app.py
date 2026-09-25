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

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_response" not in st.session_state:
    st.session_state.current_response = None

if "executing_stage" not in st.session_state:
    st.session_state.executing_stage = 0

if "checklist_state" not in st.session_state:
    st.session_state.checklist_state = {}

if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = os.environ.get("GEMINI_API_KEY", "")


# ============================================================
# CUSTOM CSS FOR PREMIUM HACKATHON LOOK
# ============================================================

st.markdown("""
<style>
    /* Main container background */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide standard top header bar background */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* Custom Navbar Header */
    .nav-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-bottom: 1px solid #334155;
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
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

    /* Service Cards Grid */
    .service-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        transition: all 0.2s ease-in-out;
        height: 100%;
        cursor: pointer;
    }

    .service-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.15);
    }

    .card-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.3rem;
    }

    .card-desc {
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.4;
    }

    /* Agent Stage Progress Panel */
    .stage-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1.5rem 0;
    }

    .stage-item {
        display: flex;
        align-items: center;
        padding: 0.6rem 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.4rem;
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

    /* Checklist Section */
    .checklist-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    /* Official Disclaimer Banner */
    .disclaimer-banner {
        background: rgba(30, 41, 59, 0.8);
        border-left: 4px solid #38bdf8;
        padding: 1rem;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #cbd5e1;
        margin-top: 2rem;
    }

    /* Streamlit UI element overrides */
    .stTextInput > div > div > input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%);
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
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

    if st.button("🔄 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_response = None
        st.session_state.checklist_state = {}
        st.rerun()

    st.caption("NextStep AI v2.0 • Hackathon Edition")


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
# CORE SUPPORTED SERVICE CARDS (1-CLICK TRIGGERS)
# ============================================================

st.markdown("##### 🚀 Quick Select Core Government Services")

cols = st.columns(5)

quick_query = None

with cols[0]:
    if st.button("Passport\n\nApply/Renew", use_container_width=True):
        quick_query = "How do I apply for or renew my Indian Passport in Telangana?"

with cols[1]:
    if st.button("Aadhaar\n\nUpdate/Download", use_container_width=True):
        quick_query = "How do I update my mobile number or address in my Aadhaar card?"

with cols[2]:
    if st.button("PAN Card\n\nInstant e-PAN", use_container_width=True):
        quick_query = "I need an instant e-PAN card using Aadhaar card."

with cols[3]:
    if st.button("Birth Cert\n\nMeeSeva / GHMC", use_container_width=True):
        quick_query = "I need to apply for a birth certificate in Hyderabad, Telangana."

with cols[4]:
    if st.button("Property Tax\n\nGHMC / CDMA", use_container_width=True):
        quick_query = "How do I calculate and pay GHMC property tax online in Telangana?"


# ============================================================
# SEARCH / CHAT INPUT FORM
# ============================================================

st.markdown("")
with st.form("query_form", clear_on_submit=True):
    col_input, col_submit = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Describe the service or problem in plain natural language:",
            placeholder="e.g. 'I need to get a birth certificate for my newborn baby in Hyderabad' or 'How to apply for fresh passport?'",
            label_visibility="collapsed"
        )
    with col_submit:
        submitted = st.form_submit_button("Ask Agent ➔", use_container_width=True)


effective_query = user_input if (submitted and user_input) else quick_query


# ============================================================
# AGENT WORKFLOW EXECUTION & PROCESSING
# ============================================================

if effective_query:
    st.session_state.messages.append({"role": "user", "content": effective_query})

    # Render animated Agent Progress Panel during execution
    st.markdown("### 🤖 Agent Execution Workflow")
    progress_container = st.empty()

    def update_stage_ui(active_stage_id, stage_title, stage_desc):
        stage_html = '<div class="stage-box"><h5>Agent Workflow Stages</h5>'
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

    # Execute workflow
    api_key_to_use = get_api_key(safe_get_secrets()) or st.session_state.user_api_key
    response = execute_agent_workflow(
        user_query=effective_query,
        api_key=api_key_to_use,
        progress_callback=update_stage_ui
    )

    # Final stage completion visual update
    update_stage_ui(6, "Completed", "Response Generated")
    time.sleep(0.2)
    progress_container.empty()

    if response.get("success"):
        st.session_state.current_response = response["data"]
    else:
        st.error("Failed to process request. Please try again.")


# ============================================================
# DISPLAY CURRENT NAVIGATION RESPONSE
# ============================================================

if st.session_state.current_response:
    res = st.session_state.current_response

    st.markdown("---")

    # Header & Jurisdiction Badge
    col_res_header, col_res_badge = st.columns([3, 1])
    with col_res_header:
        st.markdown(f"## 🎯 {res.get('service_name', 'Government Service Navigation')}")
        st.markdown(f"**Overview**: {res.get('summary', '')}")

    with col_res_badge:
        jurisdiction = res.get('jurisdiction', 'Central')
        j_label = res.get('jurisdiction_label', 'Government Service')
        if jurisdiction.lower() == "telangana":
            st.markdown(f'<div style="text-align:right;"><span class="badge-telangana">{j_label}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="text-align:right;"><span class="badge-central">{j_label}</span></div>', unsafe_allow_html=True)

    st.markdown("")

    # Two Column Layout: Document Checklist & Step-by-Step Action Plan
    col_docs, col_steps = st.columns([1, 1])

    # 1. DOCUMENT CHECKLIST
    with col_docs:
        st.markdown("### 📋 Required Documents Checklist")
        st.caption("Select items you already have to track your readiness:")

        docs = res.get("documents", [])
        if docs:
            for i, doc in enumerate(docs):
                doc_name = doc.get("name", "Document")
                is_req = doc.get("required", False)
                notes = doc.get("notes", "")

                req_badge = "🔴 Mandatory" if is_req else "🟡 Optional / Conditional"
                checkbox_key = f"doc_chk_{res.get('service_id', 'srv')}_{i}"

                checked = st.checkbox(
                    f"{doc_name}",
                    key=checkbox_key,
                    help=notes
                )
                st.caption(f"&nbsp;&nbsp;&nbsp;&nbsp;*{req_badge}* — {notes}")
        else:
            st.info("No specific physical documents required for this step.")

    # 2. STEP-BY-STEP ACTION PLAN
    with col_steps:
        st.markdown("### 🗺️ Personalized Next Steps")
        steps = res.get("steps", [])

        for step in steps:
            s_num = step.get("step", 1)
            s_title = step.get("title", f"Step {s_num}")
            s_desc = step.get("description", "")

            with st.expander(f"Step {s_num}: {s_title}", expanded=(s_num == 1)):
                st.write(s_desc)

    # 3. VERIFIED OFFICIAL SOURCE & VERIFICATION BADGE
    st.markdown("---")
    st.markdown("### 🛡️ Official Verification & Portal Access")

    col_verif_info, col_verif_link = st.columns([3, 2])

    with col_verif_info:
        if res.get("is_verified_url"):
            st.success(f"✅ **Verified Source**: {res.get('portal_name', 'Official Portal')}")
        else:
            st.warning("⚠️ **Unverified Source**: Please confirm on the official state portal.")

        st.write(f"**Verification Notes**: {res.get('verification_notes', '')}")
        st.info(f"👉 **Immediate Next Step**: {res.get('next_action', 'Visit official portal.')}")

    with col_verif_link:
        st.markdown("#### Direct Portal Link")
        official_url = res.get("official_url", "https://www.india.gov.in/")
        portal_name = res.get("portal_name", "Official Government Portal")

        st.link_button(
            f"🌐 Open {portal_name}",
            official_url,
            use_container_width=True
        )
        st.caption("Note: Links direct strictly to official .gov.in or official government domain portals.")

    # MANDATORY DISCLAIMER
    st.markdown("""
    <div class="disclaimer-banner">
        🔒 <strong>NextStep AI Disclaimer</strong>: NextStep AI is an independent navigational guidance assistant.
        It does not submit government applications on your behalf or access private government databases.
        Always verify official fees and final requirements directly on official <code>.gov.in</code> websites.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# INITIAL WELCOME / HERO VIEW
# ============================================================

else:
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h2 style="font-size: 2.2rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.5rem;">
            Which government service do you need help with today?
        </h2>
        <p style="font-size: 1.1rem; color: #94a3b8; max-width: 750px; margin: 0 auto 2rem auto;">
            Describe your need in simple everyday language. NextStep AI will identify the exact service,
            determine whether it is Central or Telangana State jurisdiction, prepare a document checklist,
            and create a personalized action plan.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="service-card">
            <div class="card-icon">🧠</div>
            <div class="card-title">Natural Language Intent</div>
            <div class="card-desc">No need to know official acronyms or department names. Speak naturally.</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="service-card">
            <div class="card-icon">🏛️</div>
            <div class="card-title">Telangana & Central Focus</div>
            <div class="card-desc">Specialized support for Telangana MeeSeva, GHMC, CDMA alongside Central services.</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="service-card">
            <div class="card-icon">🛡️</div>
            <div class="card-title">100% Verified Links</div>
            <div class="card-desc">Strict anti-hallucination policy for government URLs. Never invents official links.</div>
        </div>
        """, unsafe_allow_html=True)
