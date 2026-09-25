import json
import re
from typing import Any, Dict, List, Optional

import requests
import streamlit as st


# ============================================================
# NEXTSTEP AI
# Agentic AI for Smart Cities and Public Services
# ============================================================

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIG
# ============================================================

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free model with structured JSON output support
OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_STT_MODEL = "saaras:v4"

MAX_HISTORY = 12


# ============================================================
# API KEYS
# ============================================================

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SARVAM_API_KEY = st.secrets.get("SARVAM_API_KEY", "")


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are NextStep AI, an intelligent citizen-service assistant for India.

Your purpose is to help citizens understand and navigate:

- Government services
- Municipal services
- Civic complaints
- Roads and infrastructure
- Water and electricity issues
- Waste management
- Public transport
- Documents and certificates
- Government schemes
- Education services
- Healthcare public services
- Driving licence and vehicle services
- Passport services
- Aadhaar services
- Tax services
- Scholarships
- Public grievances
- Permits and licences
- Other public services across India

You are an agentic AI assistant.

Your workflow:

1. Understand the citizen's request.
2. Identify the relevant service or problem.
3. Determine whether location is required.
4. Ask only necessary questions.
5. Identify the likely department.
6. Give clear next steps.
7. Provide an official government link when appropriate.
8. Never invent government rules, fees, deadlines, eligibility criteria,
   phone numbers or URLs.
9. If something needs verification, tell the citizen to verify it
   through the relevant official government portal.
10. Keep answers practical and easy to understand.

IMPORTANT:

Return ONLY a valid JSON object.

Do NOT use Markdown.
Do NOT use ```json.
Do NOT write anything before or after the JSON.

The JSON format must be:

{
    "summary": "Short text answer",
    "department": "Relevant department or service",
    "location_needed": false,
    "question": "",
    "steps": [],
    "documents": [],
    "official_link": "",
    "urgency": "low"
}

Rules:

- summary must always contain the main answer.
- department should identify the relevant department/service.
- location_needed must be true or false.
- question should contain only one necessary follow-up question.
- If no question is required, use an empty string.
- steps must be an array of short strings.
- documents must be an array of strings.
- official_link must be an official government URL or empty string.
- urgency must be exactly "low", "medium", or "high".

If the user greets you, respond naturally in summary and leave unnecessary
fields empty.

If the user provides enough information, do not ask unnecessary questions.
"""


# ============================================================
# OFFICIAL INDIA SERVICES
# ============================================================

INDIA_SERVICES = {
    "National Government Services Portal":
        "https://services.india.gov.in/",

    "National Portal of India":
        "https://www.india.gov.in/",

    "MyGov":
        "https://www.mygov.in/",

    "Aadhaar":
        "https://uidai.gov.in/",

    "DigiLocker":
        "https://www.digilocker.gov.in/",

    "Passport Seva":
        "https://www.passportindia.gov.in/",

    "Parivahan":
        "https://parivahan.gov.in/",

    "Income Tax":
        "https://www.incometax.gov.in/",

    "EPFO":
        "https://www.epfindia.gov.in/",

    "National Scholarship Portal":
        "https://scholarships.gov.in/",

    "PM Kisan":
        "https://pmkisan.gov.in/",

    "National Career Service":
        "https://www.ncs.gov.in/",

    "CPGRAMS":
        "https://pgportal.gov.in/",

    "Consumer Helpline":
        "https://consumerhelpline.gov.in/",
}


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversations" not in st.session_state:
    st.session_state.conversations = []

if "current_title" not in st.session_state:
    st.session_state.current_title = "New Conversation"

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "voice_language" not in st.session_state:
    st.session_state.voice_language = "Auto"


# ============================================================
# UI STYLE
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1250px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,0.15);
    }

    .title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        color: #777;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .hero {
        padding: 25px;
        border-radius: 18px;
        border: 1px solid rgba(128,128,128,0.18);
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# JSON PARSER
# ============================================================

def extract_json(text: str) -> Optional[Dict[str, Any]]:

    if not text:
        return None

    text = text.strip()

    # Direct JSON
    try:
        result = json.loads(text)

        if isinstance(result, dict):
            return result

    except Exception:
        pass

    # Remove markdown code fences
    cleaned = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"```\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    try:
        result = json.loads(cleaned.strip())

        if isinstance(result, dict):
            return result

    except Exception:
        pass

    # Find JSON object inside extra text
    start = cleaned.find("{")

    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for i in range(start, len(cleaned)):

        char = cleaned[i]

        if escaped:
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:

                candidate = cleaned[start:i + 1]

                try:

                    result = json.loads(candidate)

                    if isinstance(result, dict):
                        return result

                except Exception:
                    return None

    return None


# ============================================================
# NORMALIZE RESPONSE
# ============================================================

def normalize_response(data: Dict[str, Any]) -> Dict[str, Any]:

    steps = data.get("steps", [])
    documents = data.get("documents", [])

    if not isinstance(steps, list):
        steps = [str(steps)] if steps else []

    if not isinstance(documents, list):
        documents = [str(documents)] if documents else []

    urgency = str(
        data.get("urgency", "low")
    ).lower()

    if urgency not in ["low", "medium", "high"]:
        urgency = "low"

    return {
        "summary": str(
            data.get("summary", "")
        ).strip(),

        "department": str(
            data.get("department", "")
        ).strip(),

        "location_needed": bool(
            data.get("location_needed", False)
        ),

        "question": str(
            data.get("question", "")
        ).strip(),

        "steps": [
            str(x).strip()
            for x in steps
            if str(x).strip()
        ],

        "documents": [
            str(x).strip()
            for x in documents
            if str(x).strip()
        ],

        "official_link": str(
            data.get("official_link", "")
        ).strip(),

        "urgency": urgency,
    }


# ============================================================
# OPENROUTER AI
# ============================================================

def ask_ai(user_text: str) -> Dict[str, Any]:

    if not OPENROUTER_API_KEY:

        return {
            "summary": "OpenRouter API key is missing.",
            "department": "",
            "location_needed": False,
            "question": "",
            "steps": [],
            "documents": [],
            "official_link": "",
            "urgency": "low",
        }

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    # Add previous conversation
    for message in st.session_state.messages[-MAX_HISTORY:]:

        if message["role"] in ["user", "assistant"]:

            messages.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )

    # Current user message
    messages.append(
        {
            "role": "user",
            "content": user_text,
        }
    )

    payload = {
        "model": OPENROUTER_MODEL,

        "messages": messages,

        "temperature": 0.1,

        "max_tokens": 900,

        "response_format": {
            "type": "json_object"
        },

        "provider": {
            "require_parameters": True
        },
    }

    headers = {
        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "HTTP-Referer":
            "https://nextstep-ai.streamlit.app",

        "X-Title":
            "NextStep AI",
    }

    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=90,
        )

    except requests.RequestException as error:

        return {
            "summary":
                f"Could not connect to the AI service: {error}",

            "department": "",
            "location_needed": False,
            "question": "",
            "steps": [],
            "documents": [],
            "official_link": "",
            "urgency": "low",
        }

    if response.status_code != 200:

        try:

            error_data = response.json()

            error_message = (
                error_data
                .get("error", {})
                .get("message", response.text)
            )

        except Exception:

            error_message = response.text

        if response.status_code == 429:

            error_message = (
                "The free AI model is temporarily rate-limited. "
                "Please try again shortly."
            )

        return {
            "summary":
                f"AI service error: {error_message}",

            "department": "",
            "location_needed": False,
            "question": "",
            "steps": [],
            "documents": [],
            "official_link": "",
            "urgency": "low",
        }

    try:

        api_data = response.json()

        choices = api_data.get(
            "choices",
            []
        )

        if not choices:
            raise ValueError(
                "The AI returned no choices."
            )

        content = (
            choices[0]
            .get("message", {})
            .get("content", "")
        )

        if isinstance(content, list):

            content = "".join(
                str(item.get("text", ""))
                for item in content
                if isinstance(item, dict)
            )

        content = str(content).strip()

    except Exception as error:

        return {
            "summary":
                f"Could not read the AI response: {error}",

            "department": "",
            "location_needed": False,
            "question": "",
            "steps": [],
            "documents": [],
            "official_link": "",
            "urgency": "low",
        }

    parsed = extract_json(content)

    # If the model somehow ignores JSON formatting,
    # show its response as plain text instead of producing
    # an "invalid JSON" error.
    if parsed is None:

        return {
            "summary": content,
            "department": "",
            "location_needed": False,
            "question": "",
            "steps": [],
            "documents": [],
            "official_link": "",
            "urgency": "low",
        }

    return normalize_response(parsed)


# ============================================================
# SARVAM SPEECH TO TEXT
# ============================================================

def transcribe_audio(
    audio_bytes: bytes,
    language_code: str,
) -> str:

    if not SARVAM_API_KEY:
        return ""

    headers = {
        "api-subscription-key":
            SARVAM_API_KEY
    }

    files = {
        "file": (
            "voice.wav",
            audio_bytes,
            "audio/wav",
        )
    }

    data = {
        "model": SARVAM_STT_MODEL,
        "mode": "transcribe",
        "language_code": language_code,
    }

    try:

        response = requests.post(
            SARVAM_STT_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=90,
        )

    except requests.RequestException:
        return ""

    if response.status_code != 200:
        return ""

    try:

        result = response.json()

        transcript = (
            result.get("transcript")
            or result.get("text")
            or ""
        )

        return str(transcript).strip()

    except Exception:
        return ""


# ============================================================
# DISPLAY RESPONSE
# ============================================================

def display_response(result: Dict[str, Any]):

    summary = result.get(
        "summary",
        ""
    )

    if summary:

        st.markdown("### 🤖 NextStep AI")

        st.write(summary)

    department = result.get(
        "department",
        ""
    )

    if department:

        st.info(
            f"🏢 **Department / Service:** {department}"
        )

    urgency = result.get(
        "urgency",
        "low"
    )

    if urgency == "high":

        st.warning(
            "🚨 This request may require prompt attention."
        )

    elif urgency == "medium":

        st.info(
            "⚠️ This request may need timely action."
        )

    steps = result.get(
        "steps",
        []
    )

    if steps:

        st.markdown("### 📋 Next Steps")

        for number, step in enumerate(
            steps,
            start=1
        ):

            st.write(
                f"**{number}.** {step}"
            )

    documents = result.get(
        "documents",
        []
    )

    if documents:

        st.markdown("### 📄 Documents")

        for document in documents:

            st.write(
                f"• {document}"
            )

    official_link = result.get(
        "official_link",
        ""
    )

    if official_link.startswith(
        "http://"
    ) or official_link.startswith(
        "https://"
    ):

        st.markdown("### 🔗 Official Service")

        st.link_button(
            "Open Official Government Service",
            official_link,
        )

    question = result.get(
        "question",
        ""
    )

    if question:

        st.info(
            f"❓ **NextStep AI needs to know:** {question}"
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🧭 NextStep AI")

    st.caption(
        "Agentic AI for Smart Cities & Public Services"
    )

    st.divider()

    st.markdown("### ⚙️ System")

    if OPENROUTER_API_KEY:
        st.success("AI: Connected")
    else:
        st.error("AI: API key missing")

    if SARVAM_API_KEY:
        st.success("Voice input: Connected")
    else:
        st.warning("Voice input: Not configured")

    st.divider()

    # New conversation
    if st.button(
        "＋ New Conversation",
        use_container_width=True,
    ):

        if st.session_state.messages:

            st.session_state.conversations.append(
                {
                    "title":
                        st.session_state.current_title,

                    "messages":
                        st.session_state.messages.copy(),
                }
            )

        st.session_state.messages = []

        st.session_state.current_title = (
            "New Conversation"
        )

        st.session_state.transcript = ""

        st.rerun()

    # Previous conversations
    if st.session_state.conversations:

        st.markdown("### 🕘 Previous Conversations")

        for index, conversation in enumerate(
            st.session_state.conversations
        ):

            title = conversation.get(
                "title",
                f"Conversation {index + 1}"
            )

            if st.button(
                title,
                key=f"history_{index}",
                use_container_width=True,
            ):

                st.session_state.messages = (
                    conversation["messages"].copy()
                )

                st.session_state.current_title = title

                st.rerun()

    st.divider()

    st.markdown("### 🇮🇳 Official Services")

    for name, url in INDIA_SERVICES.items():

        st.link_button(
            name,
            url,
            use_container_width=True,
        )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="title">🧭 NextStep AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Your intelligent guide to public services across India"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# HOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="hero">
            <h2>👋 What do you need help with?</h2>
            <p>
                Tell NextStep AI what you need.
                It will understand your request, identify the relevant
                service and guide you through the next steps.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "🏙️ **Civic Services**\n\n"
            "Roads, water, waste, streetlights and complaints."
        )

    with col2:

        st.info(
            "📄 **Documents & Schemes**\n\n"
            "Aadhaar, certificates, scholarships and schemes."
        )

    with col3:

        st.info(
            "🚗 **Public Services**\n\n"
            "Transport, passport, tax and other services."
        )


# ============================================================
# DISPLAY CHAT
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user"):

            st.write(
                message["content"]
            )

    elif message["role"] == "assistant":

        with st.chat_message("assistant"):

            try:

                parsed = json.loads(
                    message["content"]
                )

                display_response(
                    normalize_response(parsed)
                )

            except Exception:

                st.write(
                    message["content"]
                )


# ============================================================
# VOICE INPUT
# ============================================================

st.markdown("### 🎙️ Voice Input")

voice_language = st.selectbox(
    "Voice language",
    [
        "Auto",
        "English",
        "Hindi",
        "Telugu",
    ],
)

language_map = {
    "Auto": "unknown",
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Telugu": "te-IN",
}


audio = st.audio_input(
    "Tap the microphone and speak",
    sample_rate=16000,
)


if audio is not None:

    audio_bytes = audio.getvalue()

    st.audio(
        audio_bytes,
        format="audio/wav",
    )

    if st.button(
        "📝 Convert Voice to Text",
        use_container_width=True,
    ):

        if not SARVAM_API_KEY:

            st.error(
                "SARVAM_API_KEY is missing from Streamlit Secrets."
            )

        else:

            with st.spinner(
                "Converting your voice to text..."
            ):

                transcript = transcribe_audio(
                    audio_bytes,
                    language_map[voice_language],
                )

            if transcript:

                st.session_state.transcript = transcript

                st.success(
                    "Voice converted successfully."
                )

            else:

                st.error(
                    "Voice transcription failed. "
                    "Please check your Sarvam API key."
                )


# ============================================================
# TRANSCRIPT
# ============================================================

if st.session_state.transcript:

    st.markdown("### 📝 Your Voice Request")

    st.text_area(
        "Transcript",
        value=st.session_state.transcript,
        height=100,
        key="voice_transcript_box",
    )

    if st.button(
        "🚀 Send Voice Request",
        use_container_width=True,
    ):

        user_text = st.session_state.transcript.strip()

        if user_text:

            if not st.session_state.messages:

                st.session_state.current_title = (
                    user_text[:40]
                )

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_text,
                }
            )

            with st.spinner(
                "NextStep AI is thinking..."
            ):

                result = ask_ai(
                    user_text
                )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": json.dumps(
                        result,
                        ensure_ascii=False,
                    ),
                }
            )

            st.session_state.transcript = ""

            st.rerun()


# ============================================================
# TEXT CHAT
# ============================================================

st.markdown("### 💬 Chat")

user_input = st.chat_input(
    "Describe what you need help with..."
)


if user_input:

    user_input = user_input.strip()

    if user_input:

        if not st.session_state.messages:

            st.session_state.current_title = (
                user_input[:40]
            )

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        with st.spinner(
            "NextStep AI is thinking..."
        ):

            result = ask_ai(
                user_input
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": json.dumps(
                    result,
                    ensure_ascii=False,
                ),
            }
        )

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🧭 NextStep AI • Agentic AI for Smart Cities & Public Services • India"
)
