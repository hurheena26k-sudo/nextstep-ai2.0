import base64
import json
import re
from typing import Any, Dict, List, Optional

import requests
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NextStep AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONSTANTS
# ============================================================

OPENROUTER_CHAT_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

OPENROUTER_STT_URL = (
    "https://openrouter.ai/api/v1/audio/transcriptions"
)

CHAT_MODEL = "openrouter/free"

STT_MODEL = "openai/whisper-1"

APP_URL = "https://nextstep-ai.streamlit.app"


# ============================================================
# INDIA-WIDE OFFICIAL SERVICE LINKS
# ============================================================

SERVICE_LINKS = {

    "birth_certificate": (
        "Birth Certificate",
        "https://services.india.gov.in/"
    ),

    "death_certificate": (
        "Death Certificate",
        "https://services.india.gov.in/"
    ),

    "income_certificate": (
        "Income Certificate",
        "https://services.india.gov.in/"
    ),

    "caste_certificate": (
        "Caste Certificate",
        "https://services.india.gov.in/"
    ),

    "residence_certificate": (
        "Residence Certificate",
        "https://services.india.gov.in/"
    ),

    "driving_license": (
        "Driving Licence",
        "https://parivahan.gov.in/"
    ),

    "passport": (
        "Passport",
        "https://www.passportindia.gov.in/"
    ),

    "aadhaar": (
        "Aadhaar",
        "https://uidai.gov.in/"
    ),

    "government_schemes": (
        "Government Schemes",
        "https://www.india.gov.in/"
    ),

    "public_grievance": (
        "Public Grievance",
        "https://pgportal.gov.in/"
    ),

    "property_tax": (
        "Property Tax",
        "https://services.india.gov.in/"
    ),

    "water_connection": (
        "Water Connection",
        "https://services.india.gov.in/"
    ),

    "voter_service": (
        "Voter Services",
        "https://voters.eci.gov.in/"
    ),

    "education_scholarship": (
        "Scholarships",
        "https://scholarships.gov.in/"
    ),

    "employment": (
        "Employment Services",
        "https://www.ncs.gov.in/"
    ),

    "railway": (
        "Railway Services",
        "https://www.irctc.co.in/"
    ),

    "land_services": (
        "Land Services",
        "https://services.india.gov.in/"
    ),

    "digilocker": (
        "DigiLocker",
        "https://www.digilocker.gov.in/"
    ),

    "other_government_service": (
        "Government Services",
        "https://services.india.gov.in/"
    ),
}


# ============================================================
# SERVICE ALIASES
# ============================================================

SERVICE_ALIASES = {

    "birth certificate": "birth_certificate",

    "death certificate": "death_certificate",

    "income certificate": "income_certificate",

    "caste certificate": "caste_certificate",

    "residence certificate": "residence_certificate",

    "driving licence": "driving_license",

    "driving license": "driving_license",

    "passport": "passport",

    "aadhaar": "aadhaar",

    "aadhar": "aadhaar",

    "government scheme": "government_schemes",

    "government schemes": "government_schemes",

    "grievance": "public_grievance",

    "complaint": "public_grievance",

    "property tax": "property_tax",

    "water connection": "water_connection",

    "voter": "voter_service",

    "scholarship": "education_scholarship",

    "employment": "employment",

    "job": "employment",

    "railway": "railway",

    "train": "railway",

    "land": "land_services",

    "digilocker": "digilocker",
}


# ============================================================
# AI SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are NextStep AI, an intelligent public-service assistant
for citizens in India.

Your job is to understand what a citizen needs, identify the
relevant public-service category, and give simple practical
next steps.

The citizen may describe a problem without knowing the official
service name.

You can help with central, state, and local public services
across India, including:

- Certificates
- Aadhaar
- Passports
- Driving licences
- Voter services
- Government schemes
- Scholarships
- Employment
- Public grievances
- Municipal services
- Property tax
- Water services
- Railways
- Land services
- DigiLocker
- Permits
- Other legitimate government services

RULES:

1. Understand the citizen's actual need before choosing
   a service.

2. If the request is unclear, ask one useful clarification
   question.

3. If location matters, ask for the state or city instead
   of assuming it.

4. Give practical numbered steps when the service is clear.

5. Never invent fees, deadlines, eligibility rules,
   documents, or government procedures.

6. If a detail varies by state or local authority, clearly
   say that it varies and direct the citizen to the official
   government services portal.

7. Do not put URLs in your answer.
   The application adds official links separately.

8. Use conversation history.

9. Greetings and casual questions are general questions,
   not service requests.

10. Keep the response concise and citizen-friendly.

Return ONLY a JSON object with exactly these fields:

{
  "intent": "general" | "clarification" | "service_request",
  "service_key": "one allowed service key" | null,
  "title": "short title",
  "summary": "short explanation",
  "steps": ["step 1", "step 2"],
  "documents": ["document 1"],
  "next_action": "one clear next action",
  "transcript": "latest citizen message"
}

Allowed service_key values:

birth_certificate
death_certificate
income_certificate
caste_certificate
residence_certificate
driving_license
passport
aadhaar
government_schemes
public_grievance
property_tax
water_connection
voter_service
education_scholarship
employment
railway
land_services
digilocker
other_government_service
""".strip()


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "messages": [],
    "pending_prompt": None,
    "conversation_name": "New conversation",
    "voice_key": 0,
    "last_audio_signature": None,
    "show_settings": False,
}

for key, value in DEFAULTS.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# OPENROUTER API KEY
# ============================================================

try:

    OPENROUTER_API_KEY = st.secrets[
        "OPENROUTER_API_KEY"
    ]

except Exception:

    OPENROUTER_API_KEY = ""


# ============================================================
# INTERFACE STYLING
#
# IMPORTANT:
# This is styling only.
# The HTML/CSS itself is never displayed as page content.
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1180px;
        padding-top: 1.2rem;
        padding-bottom: 7rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(120, 140, 170, 0.20);
    }

    .hero {
        padding: 28px 30px;
        border-radius: 24px;
        background:
            linear-gradient(
                135deg,
                #101a33 0%,
                #182b55 52%,
                #123c58 100%
            );
        color: white;
        margin-bottom: 22px;
        box-shadow:
            0 12px 35px rgba(15, 31, 62, 0.20);
    }

    .hero-title {
        font-size: 38px;
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: rgba(255,255,255,0.78);
        font-size: 16px;
        margin-bottom: 0;
    }

    .section-title {
        font-size: 20px;
        font-weight: 750;
        margin: 8px 0 12px 0;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 18px;
        padding: 4px 8px;
    }

    .footer-note {
        text-align: center;
        color: #7b8798;
        font-size: 12px;
        padding-top: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# API HEADERS
# ============================================================

def headers() -> Dict[str, str]:

    return {
        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "HTTP-Referer":
            APP_URL,

        "X-Title":
            "NextStep AI",
    }


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(
    text: str
) -> Optional[Dict[str, Any]]:

    if not text:

        return None

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.I
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned
    ).strip()

    try:

        value = json.loads(cleaned)

        if isinstance(value, dict):

            return value

    except json.JSONDecodeError:

        pass

    match = re.search(
        r"\{.*\}",
        cleaned,
        flags=re.DOTALL
    )

    if match:

        try:

            value = json.loads(
                match.group(0)
            )

            if isinstance(value, dict):

                return value

        except json.JSONDecodeError:

            pass

    return None


# ============================================================
# LIST NORMALIZER
# ============================================================

def normalize_list(
    value: Any
) -> List[str]:

    if value is None:

        return []

    if isinstance(value, list):

        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, str):

        if value.strip():

            return [
                value.strip()
            ]

    return []


# ============================================================
# RESULT NORMALIZER
# ============================================================

def normalize_result(
    data: Dict[str, Any],
    fallback_transcript: str = ""
) -> Dict[str, Any]:

    intent = str(
        data.get(
            "intent",
            "general"
        )
    ).strip().lower()

    if intent not in {
        "general",
        "clarification",
        "service_request"
    }:

        intent = "general"

    service_key = data.get(
        "service_key"
    )

    if service_key is not None:

        service_key = str(
            service_key
        ).strip()

        if service_key not in SERVICE_LINKS:

            service_key = None

    if intent != "service_request":

        service_key = None

    return {

        "intent":
            intent,

        "service_key":
            service_key,

        "title":
            str(
                data.get(
                    "title",
                    "Your Next Step"
                )
            ).strip(),

        "summary":
            str(
                data.get(
                    "summary",
                    ""
                )
            ).strip(),

        "steps":
            normalize_list(
                data.get(
                    "steps"
                )
            ),

        "documents":
            normalize_list(
                data.get(
                    "documents"
                )
            ),

        "next_action":
            str(
                data.get(
                    "next_action",
                    ""
                )
            ).strip(),

        "transcript":
            str(
                data.get(
                    "transcript",
                    fallback_transcript
                )
            ).strip(),
    }


# ============================================================
# CONVERSATION HISTORY FOR AI
# ============================================================

def conversation_for_ai():

    history = []

    for message in st.session_state.messages[-12:]:

        role = message.get(
            "role"
        )

        if role == "user":

            history.append(
                {
                    "role": "user",
                    "content":
                        message.get(
                            "content",
                            ""
                        )
                }
            )

        elif role == "assistant":

            history.append(
                {
                    "role": "assistant",
                    "content":
                        message.get(
                            "summary",
                            message.get(
                                "content",
                                ""
                            )
                        )
                }
            )

    return history


# ============================================================
# SIMPLE SERVICE FALLBACK
# ============================================================

def service_key_from_text(
    text: str
) -> Optional[str]:

    lowered = text.lower()

    for alias, key in SERVICE_ALIASES.items():

        if alias in lowered:

            return key

    return None


# ============================================================
# FALLBACK AI RESULT
# ============================================================

def fallback_result(
    user_text: str
):

    key = service_key_from_text(
        user_text
    )

    if key:

        name, _ = SERVICE_LINKS[key]

        return {

            "intent":
                "service_request",

            "service_key":
                key,

            "title":
                f"Getting help with {name}",

            "summary":
                (
                    f"I can help you navigate "
                    f"{name}. The exact process "
                    f"can vary by state or authority."
                ),

            "steps": [

                "Confirm your state or the authority handling the service.",

                "Use the official service link below and check the current requirements.",

                "Complete the application or request and keep the reference number for tracking.",

            ],

            "documents": [],

            "next_action":
                (
                    "Tell me your state or city "
                    "if you want more specific guidance."
                ),

            "transcript":
                user_text,
        }

    return {

        "intent":
            "general",

        "service_key":
            None,

        "title":
            "How can I help?",

        "summary":
            (
                "Tell me what public-service "
                "problem you are trying to solve, "
                "and I will help identify the "
                "next step."
            ),

        "steps": [],

        "documents": [],

        "next_action":
            "Describe what you need in your own words.",

        "transcript":
            user_text,
    }


# ============================================================
# ERROR RESULT
# ============================================================

def api_error_result(
    title: str,
    summary: str,
    detail: str = ""
):

    return {

        "intent":
            "error",

        "service_key":
            None,

        "title":
            title,

        "summary":
            summary,

        "steps": [],

        "documents": [],

        "next_action":
            "Please try again in a moment.",

        "transcript":
            "",

        "error":
            detail,
    }


# ============================================================
# OPENROUTER CHAT
# ============================================================

def get_ai_response(
    user_text: str
):

    if not OPENROUTER_API_KEY:

        return api_error_result(

            "API key not connected",

            (
                "Add OPENROUTER_API_KEY "
                "to Streamlit Secrets before "
                "running the AI."
            )
        )

    messages = [

        {
            "role":
                "system",

            "content":
                SYSTEM_INSTRUCTION,
        }

    ]

    messages.extend(
        conversation_for_ai()
    )

    messages.append(
        {
            "role":
                "user",

            "content":
                user_text,
        }
    )

    payload = {

        "model":
            CHAT_MODEL,

        "messages":
            messages,

        "temperature":
            0.2,

        "max_tokens":
            900,
    }

    try:

        response = requests.post(

            OPENROUTER_CHAT_URL,

            headers=headers(),

            json=payload,

            timeout=60,
        )

        if response.status_code != 200:

            detail = response.text[:1000]

            if response.status_code == 429:

                return api_error_result(

                    "AI is temporarily rate-limited",

                    (
                        "OpenRouter has temporarily "
                        "limited this request. "
                        "Wait a moment and try again."
                    ),

                    detail,
                )

            return api_error_result(

                f"AI request failed "
                f"({response.status_code})",

                (
                    "The AI service returned an "
                    "error while processing your request."
                ),

                detail,
            )

        data = response.json()

        choices = data.get(
            "choices"
        ) or []

        if not choices:

            return api_error_result(

                "Empty AI response",

                (
                    "The AI did not return a usable "
                    "answer. Please try again."
                ),

                json.dumps(data)[:1000],
            )

        content = (
            choices[0]
            .get("message", {})
            .get("content", "")
        )

        parsed = extract_json(
            content
        )

        if parsed is None:

            return fallback_result(
                user_text
            )

        return normalize_result(
            parsed,
            user_text
        )

    except requests.Timeout:

        return api_error_result(

            "Request timed out",

            (
                "The AI took too long to respond. "
                "Please try the request again."
            )
        )

    except requests.RequestException as exc:

        return api_error_result(

            "Network connection problem",

            (
                "NextStep AI could not reach "
                "OpenRouter right now."
            ),

            str(exc),
        )

    except Exception as exc:

        return api_error_result(

            "Unexpected AI error",

            (
                "Something unexpected happened "
                "while processing your request."
            ),

            str(exc),
        )


# ============================================================
# AUDIO FORMAT
# ============================================================

def audio_format(
    uploaded_file: Any
) -> str:

    mime = (
        getattr(
            uploaded_file,
            "type",
            ""
        )
        or ""
    ).lower()

    mapping = {

        "audio/wav":
            "wav",

        "audio/x-wav":
            "wav",

        "audio/wave":
            "wav",

        "audio/mpeg":
            "mp3",

        "audio/mp3":
            "mp3",

        "audio/mp4":
            "m4a",

        "audio/x-m4a":
            "m4a",

        "audio/ogg":
            "ogg",

        "audio/webm":
            "webm",

        "audio/aac":
            "aac",

        "audio/flac":
            "flac",
    }

    return mapping.get(
        mime,
        "wav"
    )


# ============================================================
# OPENROUTER SPEECH-TO-TEXT
# ============================================================

def transcribe_audio(
    audio_file: Any
) -> str:

    if not OPENROUTER_API_KEY:

        raise RuntimeError(
            "OPENROUTER_API_KEY is missing "
            "from Streamlit Secrets."
        )

    raw = audio_file.getvalue()

    if not raw:

        raise RuntimeError(
            "The microphone recording was empty."
        )

    payload = {

        "model":
            STT_MODEL,

        "input_audio": {

            "data":
                base64.b64encode(
                    raw
                ).decode("utf-8"),

            "format":
                audio_format(
                    audio_file
                ),
        },

        "language":
            "en",
    }

    response = requests.post(

        OPENROUTER_STT_URL,

        headers=headers(),

        json=payload,

        timeout=60,
    )

    if response.status_code != 200:

        raise RuntimeError(

            "Speech transcription failed "
            f"({response.status_code}): "
            f"{response.text[:800]}"
        )

    result = response.json()

    transcript = str(
        result.get(
            "text",
            ""
        )
    ).strip()

    if not transcript:

        raise RuntimeError(
            "No speech was detected in the recording."
        )

    return transcript


# ============================================================
# SAVE CONVERSATION
# ============================================================

def add_exchange(
    user_text: str,
    result: Dict[str, Any]
):

    st.session_state.messages.append(

        {
            "role":
                "user",

            "content":
                user_text,
        }
    )

    st.session_state.messages.append(

        {
            "role":
                "assistant",

            "content":
                result.get(
                    "summary",
                    ""
                ),

            **result,
        }
    )


# ============================================================
# NEW CONVERSATION
# ============================================================

def start_new_conversation():

    st.session_state.messages = []

    st.session_state.pending_prompt = None

    st.session_state.conversation_name = (
        "New conversation"
    )

    st.session_state.last_audio_signature = None

    st.session_state.voice_key += 1


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "# ✦ NextStep AI"
    )

    st.caption(
        "Your intelligent guide to public services"
    )

    if st.button(
        "＋  New conversation",
        use_container_width=True,
        type="primary",
    ):

        start_new_conversation()

        st.rerun()

    st.divider()

    st.markdown(
        "### 💬 Recent conversations"
    )

    user_messages = [

        m["content"]

        for m in st.session_state.messages

        if m.get("role") == "user"

    ]

    if not user_messages:

        st.caption(
            "Your current conversation "
            "will appear here."
        )

    else:

        for index, text in enumerate(
            user_messages[-7:],
            start=1
        ):

            label = (
                text
                .replace("🎙️", "")
                .strip()
                .replace("\n", " ")
            )

            if len(label) > 38:

                label = (
                    label[:38] + "…"
                )

            st.caption(
                f"{index}. {label}"
            )

    st.divider()

    st.markdown(
        "### 🇮🇳 India-wide services"
    )

    st.caption(
        "Central, state and local government "
        "services can be routed through official "
        "government portals."
    )

    if st.button(
        "⚙️ Settings",
        use_container_width=True
    ):

        st.session_state.show_settings = (
            not st.session_state.show_settings
        )

    st.divider()

    st.caption(
        "🔐 API keys stay in Streamlit Secrets, "
        "not in this code."
    )


# ============================================================
# SETTINGS
# ============================================================

if st.session_state.show_settings:

    with st.expander(
        "⚙️ NextStep AI settings",
        expanded=True
    ):

        st.write(
            "**AI model:** OpenRouter Free Router"
        )

        st.write(
            "**Voice input:** OpenRouter Whisper"
        )

        st.write(
            "**Service coverage:** India-wide"
        )

        st.caption(
            "Voice transcription uses a separate "
            "STT request. Current OpenRouter STT "
            "pricing depends on the selected model."
        )


# ============================================================
# HERO
# ============================================================

st.markdown(

    """
    <div class="hero">

        <div class="hero-title">
            ✦ NextStep AI
        </div>

        <div class="hero-subtitle">
            Understand the problem.
            Find the service.
            Take the next step.
        </div>

    </div>
    """,

    unsafe_allow_html=True,
)


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.markdown(
        '<div class="section-title">'
        'What can I help you with today?'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "You do not need to know the exact "
        "government service name. Just describe "
        "what you need."
    )

    c1, c2, c3 = st.columns(3)

    suggestions = [

        (
            "📄",
            "Certificates",
            "I need help getting a government certificate."
        ),

        (
            "🪪",
            "Aadhaar",
            "I need help with an Aadhaar service."
        ),

        (
            "🚗",
            "Driving licence",
            "I want help with a driving licence."
        ),

        (
            "🎓",
            "Scholarship",
            "I want to find a government scholarship."
        ),

        (
            "🛂",
            "Passport",
            "I want help applying for a passport."
        ),

        (
            "🏛️",
            "Government scheme",
            "I want to know which government scheme may help me."
        ),
    ]

    for index, (
        icon,
        label,
        prompt
    ) in enumerate(suggestions):

        column = [
            c1,
            c2,
            c3
        ][index % 3]

        with column:

            if st.button(
                f"{icon}  {label}",
                key=f"suggestion_{index}",
                use_container_width=True,
            ):

                st.session_state.pending_prompt = (
                    prompt
                )

                st.rerun()

    st.divider()

    st.markdown(
        '<div class="section-title">'
        'Why NextStep AI?'
        '</div>',
        unsafe_allow_html=True,
    )

    a, b, c = st.columns(3)

    with a:

        st.info(
            "🧠 **Understand**\n\n"
            "Describe your need naturally. "
            "The AI identifies what you are "
            "actually trying to do."
        )

    with b:

        st.info(
            "🧭 **Guide**\n\n"
            "Get clear steps instead of digging "
            "through complicated government information."
        )

    with c:

        st.info(
            "🔗 **Connect**\n\n"
            "When a service is identified, the app "
            "gives you an official government source."
        )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    role = message.get(
        "role"
    )

    if role == "user":

        with st.chat_message(
            "user",
            avatar="👤"
        ):

            st.write(
                message.get(
                    "content",
                    ""
                )
            )

        continue

    with st.chat_message(
        "assistant",
        avatar="✦"
    ):

        if message.get(
            "intent"
        ) == "error":

            st.error(
                message.get(
                    "summary",
                    "Something went wrong."
                )
            )

            continue

        st.markdown(
            f"### {message.get(
                'title',
                'Your Next Step'
            )}"
        )

        if message.get(
            "summary"
        ):

            st.info(
                message["summary"]
            )

        steps = message.get(
            "steps",
            []
        )

        if steps:

            st.markdown(
                "#### 🧭 Next steps"
            )

            for index, step in enumerate(
                steps,
                start=1
            ):

                st.markdown(
                    f"**{index}.** {step}"
                )

        documents = message.get(
            "documents",
            []
        )

        if documents:

            st.markdown(
                "#### 📋 Keep these ready"
            )

            for document in documents:

                st.markdown(
                    f"• {document}"
                )

        if message.get(
            "next_action"
        ):

            st.success(
                "➡️ **Next action:** "
                + message["next_action"]
            )

        service_key = message.get(
            "service_key"
        )

        if (
            message.get("intent")
            == "service_request"
            and service_key
            in SERVICE_LINKS
        ):

            (
                service_name,
                service_url
            ) = SERVICE_LINKS[
                service_key
            ]

            st.link_button(

                f"🔗 Open official "
                f"{service_name} source",

                service_url,

                use_container_width=True,
            )

            st.caption(
                "Official government source. "
                "State/local procedures may vary."
            )


# ============================================================
# PROCESS SUGGESTED PROMPT
# ============================================================

if st.session_state.pending_prompt:

    prompt = (
        st.session_state.pending_prompt
    )

    st.session_state.pending_prompt = None

    with st.spinner(
        "✦ NextStep AI is thinking..."
    ):

        result = get_ai_response(
            prompt
        )

    add_exchange(
        prompt,
        result
    )

    st.rerun()


# ============================================================
# TEXT INPUT
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">'
    'Ask NextStep AI'
    '</div>',
    unsafe_allow_html=True,
)

text_col, send_col = st.columns(
    [8, 1],
    vertical_alignment="bottom"
)

with text_col:

    typed_message = st.text_input(

        "Your message",

        placeholder=(
            "Example: I need to apply "
            "for an income certificate..."
        ),

        label_visibility="collapsed",

        key="message_input",
    )

with send_col:

    send_clicked = st.button(

        "Send",

        use_container_width=True,

        type="primary",
    )


# ============================================================
# TEXT SUBMISSION
# ============================================================

if send_clicked:

    message = typed_message.strip()

    if not message:

        st.warning(
            "Please type a message first, "
            "or use the microphone below."
        )

    else:

        with st.spinner(
            "✦ NextStep AI is thinking..."
        ):

            result = get_ai_response(
                message
            )

        add_exchange(
            message,
            result
        )

        st.session_state.message_input = ""

        st.rerun()


# ============================================================
# VOICE INPUT
# ============================================================

voice_left, voice_right = st.columns(
    [1, 4],
    vertical_alignment="center"
)

with voice_left:

    st.markdown(
        "**🎙️ Voice assistant**"
    )

with voice_right:

    st.caption(
        "Record a short request. "
        "NextStep AI will transcribe it "
        "and then answer it."
    )


voice_input = st.audio_input(

    "Record your request",

    sample_rate=16000,

    key=(
        f"voice_input_"
        f"{st.session_state.voice_key}"
    ),

    label_visibility="collapsed",
)


# ============================================================
# VOICE SUBMISSION
# ============================================================

if voice_input is not None:

    raw_audio = (
        voice_input.getvalue()
    )

    signature = str(
        hash(raw_audio)
    )

    if (
        signature
        != st.session_state.last_audio_signature
    ):

        st.session_state.last_audio_signature = (
            signature
        )

        with st.spinner(
            "🎙️ Transcribing your request..."
        ):

            try:

                transcript = transcribe_audio(
                    voice_input
                )

                result = get_ai_response(
                    transcript
                )

                add_exchange(

                    f"🎙️ {transcript}",

                    result
                )

                st.session_state.voice_key += 1

                st.rerun()

            except Exception as exc:

                st.error(
                    "Voice input could not be processed."
                )

                st.caption(
                    str(exc)
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown(

    '<div class="footer-note">'
    'NextStep AI • Intelligent guidance for '
    'public services across India'
    '</div>',

    unsafe_allow_html=True,
)
