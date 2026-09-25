import streamlit as st
import requests
import json
import re
import time


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# OPENROUTER CONFIG
# ============================================================

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL_NAME = "openrouter/free"


# ============================================================
# API KEY
# ============================================================

try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    OPENROUTER_API_KEY = None


# ============================================================
# NEXTSTEP AI SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are NextStep AI, an intelligent public-service assistant.

Your purpose is to help citizens understand and navigate public
services and applications.

You can help with many types of public services, including:

- Birth certificates
- Death certificates
- Income certificates
- Caste certificates
- Residence certificates
- Government scheme applications
- Licenses and permits
- Public grievances
- Municipal services
- Education-related government services
- Welfare services
- Public transport services
- Property tax
- Water connections
- Employment services
- Land services
- Passport services
- Aadhaar services
- Voter services
- Railway services
- Other legitimate public-service requests

IMPORTANT BEHAVIOR:

1. Start by understanding what the citizen needs.

2. Do not assume that the citizen already knows the name
   of the government service.

3. If the citizen describes a problem indirectly, identify
   the possible service they may need.

4. Ask simple follow-up questions when important information
   is missing.

5. Do not ask unnecessary questions.

6. Explain the process in simple step-by-step language.

7. Explain likely required documents only when appropriate.

8. Never invent government rules, fees, deadlines,
   eligibility requirements, or documents.

9. If the exact procedure depends on location, ask for the
   relevant state, city, or country.

10. If reliable information is unavailable, clearly tell the
    citizen what should be verified.

11. Do not restrict yourself to a fixed list of services.

12. If the request is outside public services, politely explain
    that your main purpose is public-service assistance.

RESPONSE FORMAT:

Give helpful answers using this structure when appropriate:

### What you need to do
A short explanation.

### Next steps
1. Step one
2. Step two
3. Step three

### Documents
Only list documents when relevant.

### Important
Mention anything the citizen should verify.

### Your next step
Give one clear action the citizen can take now.

Do NOT create fake government links.

Do NOT claim that a website is official unless it is provided
by the application.

STYLE:

- Friendly
- Professional
- Clear
- Simple
- Helpful
- Not overly long
- Suitable for ordinary citizens

Most importantly, help the citizen understand their NEXT STEP.
"""


# ============================================================
# OFFICIAL SERVICE LINKS
# ============================================================

SERVICE_LINKS = {
    "birth_certificate": {
        "name": "Birth Certificate",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana State Services"
    },

    "death_certificate": {
        "name": "Death Certificate",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana State Services"
    },

    "income_certificate": {
        "name": "Income Certificate",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva"
    },

    "caste_certificate": {
        "name": "Caste Certificate",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva"
    },

    "residence_certificate": {
        "name": "Residence Certificate",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva"
    },

    "driving_license": {
        "name": "Driving Licence",
        "url": "https://transport.telangana.gov.in/",
        "label": "Official Telangana Transport Department"
    },

    "passport": {
        "name": "Passport",
        "url": "https://www.passportindia.gov.in/",
        "label": "Official Passport Seva"
    },

    "aadhaar": {
        "name": "Aadhaar",
        "url": "https://www.uidai.gov.in/",
        "label": "Official UIDAI"
    },

    "government_schemes": {
        "name": "Government Schemes",
        "url": "https://www.india.gov.in/",
        "label": "Official National Government Portal"
    },

    "public_grievance": {
        "name": "Public Grievance",
        "url": "https://www.india.gov.in/",
        "label": "Official National Government Portal"
    },

    "property_tax": {
        "name": "Property Tax",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana State Services"
    },

    "water_connection": {
        "name": "Water Connection",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana State Services"
    },

    "voter_service": {
        "name": "Voter Services",
        "url": "https://www.india.gov.in/",
        "label": "Official National Government Portal"
    },

    "education_scholarship": {
        "name": "Education / Scholarship",
        "url": "https://telanganaepass.cgg.gov.in/",
        "label": "Official Telangana ePASS"
    },

    "employment": {
        "name": "Employment Services",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva"
    },

    "railway": {
        "name": "Railway Services",
        "url": "https://www.irctc.co.in/",
        "label": "Official IRCTC"
    },

    "land_services": {
        "name": "Land Services",
        "url": "https://www.telangana.gov.in/",
        "label": "Official Telangana State Portal"
    },

    "other_government_service": {
        "name": "Government Services",
        "url": "https://www.india.gov.in/",
        "label": "Official National Government Portal"
    }
}


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0

if "request_count" not in st.session_state:
    st.session_state.request_count = 0


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f7f9fc;
    }

    [data-testid="stSidebar"] {
        background: #111827;
    }

    [data-testid="stSidebar"] * {
        color: #f9fafb;
    }

    .brand-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0;
    }

    .brand-subtitle {
        color: #6b7280;
        font-size: 0.95rem;
        margin-top: 3px;
    }

    .hero {
        padding: 28px 10px 20px 10px;
    }

    .hero h1 {
        font-size: 3rem;
        margin-bottom: 8px;
        letter-spacing: -2px;
    }

    .hero p {
        font-size: 1.1rem;
        color: #667085;
        max-width: 760px;
    }

    .answer-box {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 24px;
        margin-top: 10px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.04);
    }

    .feature-title {
        font-weight: 700;
        font-size: 1.05rem;
    }

    .small-muted {
        color: #6b7280;
        font-size: 0.88rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(text):
    if not text:
        return ""

    text = str(text)

    # Remove accidental JSON fences
    text = text.replace("```json", "")
    text = text.replace("```", "")

    return text.strip()


def detect_service(user_text):
    """
    Detect likely service from the user's message.
    This is only used for selecting a verified source link.
    """

    text = user_text.lower()

    patterns = {
        "birth_certificate": [
            "birth certificate",
            "birth registration",
            "born certificate"
        ],

        "death_certificate": [
            "death certificate",
            "death registration"
        ],

        "income_certificate": [
            "income certificate",
            "income proof certificate"
        ],

        "caste_certificate": [
            "caste certificate",
            "community certificate"
        ],

        "residence_certificate": [
            "residence certificate",
            "domicile certificate",
            "residential certificate"
        ],

        "driving_license": [
            "driving licence",
            "driving license",
            "dl renewal",
            "driving test"
        ],

        "passport": [
            "passport",
            "passport application",
            "passport renewal"
        ],

        "aadhaar": [
            "aadhaar",
            "aadhar",
            "uidai"
        ],

        "government_schemes": [
            "government scheme",
            "govt scheme",
            "welfare scheme",
            "scheme eligibility"
        ],

        "public_grievance": [
            "complaint",
            "grievance",
            "complain about",
            "report a problem",
            "municipal complaint"
        ],

        "property_tax": [
            "property tax",
            "house tax"
        ],

        "water_connection": [
            "water connection",
            "new water connection",
            "water supply"
        ],

        "voter_service": [
            "voter id",
            "voter card",
            "voter registration",
            "election card"
        ],

        "education_scholarship": [
            "scholarship",
            "education scholarship",
            "epass",
            "e-pass"
        ],

        "employment": [
            "employment service",
            "job registration",
            "employment registration"
        ],

        "railway": [
            "railway",
            "train ticket",
            "irctc"
        ],

        "land_services": [
            "land record",
            "land records",
            "property registration",
            "land service"
        ]
    }

    for service_key, keywords in patterns.items():
        for keyword in keywords:
            if keyword in text:
                return service_key

    return None


def looks_like_service_request(user_text):
    """
    Decide whether a direct official source should be shown.
    """

    text = user_text.lower().strip()

    service_words = [
        "apply",
        "application",
        "certificate",
        "register",
        "registration",
        "renew",
        "renewal",
        "license",
        "licence",
        "scheme",
        "complaint",
        "grievance",
        "tax",
        "connection",
        "passport",
        "aadhaar",
        "voter",
        "scholarship",
        "permit",
        "document",
        "government service"
    ]

    return any(word in text for word in service_words)


def get_conversation_context():
    """
    Keep context short to reduce token usage and improve speed.
    """

    recent = st.session_state.messages[-6:]

    context = []

    for message in recent:
        role = message.get("role")

        if role not in ["user", "assistant"]:
            continue

        content = message.get("content", "")

        if not content:
            continue

        context.append(
            f"{role.upper()}: {content[:1800]}"
        )

    return "\n".join(context)


# ============================================================
# OPENROUTER REQUEST
# ============================================================

def ask_openrouter(user_text):

    if not OPENROUTER_API_KEY:
        return {
            "success": False,
            "error": "OPENROUTER_API_KEY is missing from Streamlit Secrets."
        }

    current_time = time.time()

    # Prevent accidental duplicate submissions
    if current_time - st.session_state.last_request_time < 1.2:
        return {
            "success": False,
            "error": "Please wait a moment before sending another request."
        }

    st.session_state.last_request_time = current_time

    conversation_context = get_conversation_context()

    messages = [
        {
            "role": "system",
            "content": SYSTEM_INSTRUCTION
        }
    ]

    if conversation_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Recent conversation context:\n\n"
                    + conversation_context
                )
            }
        )

    messages.append(
        {
            "role": "user",
            "content": user_text
        }
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io/",
        "X-Title": "NextStep AI"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 1200
    }

    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=45
        )

        # ----------------------------------------------------
        # RATE LIMIT
        # ----------------------------------------------------

        if response.status_code == 429:
            return {
                "success": False,
                "error": (
                    "OpenRouter free-tier limit has been reached. "
                    "The free plan currently allows 50 requests per day. "
                    "Please try again later."
                )
            }

        # ----------------------------------------------------
        # AUTH ERROR
        # ----------------------------------------------------

        if response.status_code in [401, 403]:
            return {
                "success": False,
                "error": (
                    "OpenRouter rejected the API key. "
                    "Please check OPENROUTER_API_KEY in Streamlit Secrets."
                )
            }

        # ----------------------------------------------------
        # OTHER HTTP ERROR
        # ----------------------------------------------------

        if response.status_code != 200:

            try:
                error_data = response.json()

                message = (
                    error_data
                    .get("error", {})
                    .get("message", "")
                )

            except Exception:
                message = response.text

            return {
                "success": False,
                "error": (
                    f"OpenRouter error {response.status_code}: "
                    f"{message}"
                )
            }

        # ----------------------------------------------------
        # PARSE RESPONSE
        # ----------------------------------------------------

        data = response.json()

        choices = data.get("choices", [])

        if not choices:
            return {
                "success": False,
                "error": "OpenRouter returned no AI response."
            }

        message = choices[0].get("message", {})

        answer = message.get("content", "")

        if isinstance(answer, list):

            parts = []

            for item in answer:

                if isinstance(item, dict):
                    if item.get("type") == "text":
                        parts.append(
                            item.get("text", "")
                        )

                elif isinstance(item, str):
                    parts.append(item)

            answer = "\n".join(parts)

        answer = clean_text(answer)

        if not answer:
            return {
                "success": False,
                "error": "The AI returned an empty response."
            }

        st.session_state.request_count += 1

        return {
            "success": True,
            "answer": answer
        }

    except requests.exceptions.Timeout:

        return {
            "success": False,
            "error": (
                "The AI service took too long to respond. "
                "Please try again."
            )
        }

    except requests.exceptions.ConnectionError:

        return {
            "success": False,
            "error": (
                "Could not connect to OpenRouter. "
                "Please check the Streamlit connection."
            )
        }

    except Exception as error:

        return {
            "success": False,
            "error": f"Unexpected error: {error}"
        }


# ============================================================
# DISPLAY AI RESPONSE
# ============================================================

def display_answer(answer, user_text):

    st.markdown(
        '<div class="answer-box">',
        unsafe_allow_html=True
    )

    st.markdown("### 🤖 NextStep AI")

    st.markdown(answer)

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # SOURCE LINK
    # Only show it when this looks like an actual service
    # request.
    # --------------------------------------------------------

    if looks_like_service_request(user_text):

        service_key = detect_service(user_text)

        if service_key and service_key in SERVICE_LINKS:

            service = SERVICE_LINKS[service_key]

            st.markdown("#### 🔗 Official source")

            st.link_button(
                service["label"],
                service["url"],
                use_container_width=False
            )

            st.caption(
                f"Source for: {service['name']}"
            )


# ============================================================
# PROCESS MESSAGE
# ============================================================

def process_message(user_text):

    user_text = user_text.strip()

    if not user_text:
        return

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_text
        }
    )

    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_text)

    # AI response
    with st.chat_message("assistant"):

        with st.spinner("NextStep AI is thinking..."):

            result = ask_openrouter(user_text)

        if result["success"]:

            answer = result["answer"]

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            display_answer(
                answer,
                user_text
            )

        else:

            error_message = result["error"]

            st.error(
                f"⚠️ {error_message}"
            )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:10px 0 20px 0;">
            <div style="font-size:3rem;">🤖</div>
            <h2 style="margin:0;">NextStep AI</h2>
            <p style="color:#cbd5e1;">
                Public Service Assistant
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "➕ New Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.markdown("### 🕘 Conversation")

    if st.session_state.messages:

        user_messages = [
            m["content"]
            for m in st.session_state.messages
            if m["role"] == "user"
        ]

        for index, message in enumerate(
            user_messages[-8:],
            start=1
        ):

            preview = message[:42]

            if len(message) > 42:
                preview += "..."

            st.caption(
                f"{index}. {preview}"
            )

    else:

        st.caption(
            "Your recent questions will appear here."
        )

    st.divider()

    st.markdown("### ✨ What I can help with")

    st.caption("Certificates")
    st.caption("Government schemes")
    st.caption("Public complaints")
    st.caption("Licences & permits")
    st.caption("Municipal services")
    st.caption("Education & scholarships")
    st.caption("Many other public services")

    st.divider()

    st.caption(
        "Powered by OpenRouter"
    )

    st.caption(
        f"Requests this session: "
        f"{st.session_state.request_count}"
    )


# ============================================================
# TOP BRANDING
# ============================================================

top_left, top_right = st.columns(
    [7, 3],
    vertical_alignment="center"
)

with top_left:

    st.markdown(
        """
        <div class="brand-title">
            🤖 NextStep AI
        </div>
        <div class="brand-subtitle">
            Your intelligent guide to public services
        </div>
        """,
        unsafe_allow_html=True
    )

with top_right:

    st.caption(
        "🟢 AI Assistant"
    )


st.divider()


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="hero">
            <h1>What's your next step?</h1>
            <p>
                Tell me what you need help with.
                You don't need to know the exact government
                service name. I'll help you figure it out.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 💡 Try asking")

    prompt_col1, prompt_col2 = st.columns(2)

    with prompt_col1:

        if st.button(
            "📄 I need an income certificate",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I need to apply for an income certificate."
            )

            st.rerun()

        if st.button(
            "🪪 How do I get a birth certificate?",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "How do I get a birth certificate?"
            )

            st.rerun()

        if st.button(
            "🎓 I need a scholarship",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I need help finding a government scholarship."
            )

            st.rerun()

    with prompt_col2:

        if st.button(
            "🚗 I need a driving licence",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I need help applying for a driving licence."
            )

            st.rerun()

        if st.button(
            "📢 I want to file a complaint",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to file a public service complaint."
            )

            st.rerun()

        if st.button(
            "💬 I don't know which service I need",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I have a government-related problem, "
                "but I don't know which service I need."
            )

            st.rerun()

    st.markdown("")

    feature1, feature2, feature3 = st.columns(3)

    with feature1:

        st.info(
            "**🧠 Understands your need**\n\n"
            "Describe your problem naturally. "
            "You don't need to know the service name."
        )

    with feature2:

        st.info(
            "**🪜 Gives clear next steps**\n\n"
            "Get simple, practical guidance instead "
            "of confusing government terminology."
        )

    with feature3:

        st.info(
            "**🔗 Connects you to sources**\n\n"
            "For clear service requests, the app "
            "shows a relevant official source."
        )


# ============================================================
# DISPLAY EXISTING CHAT
# ============================================================

else:

    st.markdown("### 💬 Your conversation")

    for message in st.session_state.messages:

        role = message.get("role")
        content = message.get("content", "")

        if role == "user":

            with st.chat_message("user"):
                st.markdown(content)

        elif role == "assistant":

            with st.chat_message("assistant"):

                st.markdown(
                    '<div class="answer-box">',
                    unsafe_allow_html=True
                )

                st.markdown(content)

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )


# ============================================================
# PENDING PROMPT
# ============================================================

if st.session_state.pending_prompt:

    pending = st.session_state.pending_prompt

    st.session_state.pending_prompt = None

    process_message(pending)


# ============================================================
# INPUT AREA
# ============================================================

st.markdown("")

st.markdown("### Ask NextStep AI")

input_col, voice_col = st.columns(
    [8, 1],
    vertical_alignment="bottom"
)

with input_col:

    with st.form(
        "message_form",
        clear_on_submit=True
    ):

        typed_message = st.text_input(
            "Your question",
            placeholder=(
                "Tell me what you need help with..."
            ),
            label_visibility="collapsed"
        )

        submitted = st.form_submit_button(
            "Send ➜",
            use_container_width=True
        )


with voice_col:

    audio_input = st.audio_input(
        "🎙️",
        sample_rate=16000,
        help=(
            "Record your request. "
            "Voice transcription requires a speech-to-text service."
        )
    )


# ============================================================
# TEXT SUBMISSION
# ============================================================

if submitted and typed_message:

    process_message(
        typed_message
    )


# ============================================================
# MICROPHONE NOTICE
# ============================================================

if audio_input is not None:

    st.info(
        "🎙️ Your recording was captured. "
        "The current OpenRouter free router handles text/image input, "
        "so voice transcription is not connected yet. "
        "You can type the same request in the search box."
    )
