import base64
import json
import re
from datetime import datetime
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
# CONFIGURATION
# ============================================================

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free OpenRouter model with JSON response support
OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"

SARVAM_STT_MODEL = "saaras:v4"
SARVAM_TTS_MODEL = "bulbul:v3"

MAX_HISTORY_MESSAGES = 20


# ============================================================
# SECRETS
# ============================================================

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SARVAM_API_KEY = st.secrets.get("SARVAM_API_KEY", "")


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are NextStep AI, an intelligent citizen-service assistant for India.

Your purpose is to help citizens understand and navigate public services,
government processes, civic complaints, schemes, documents, permits,
transport, utilities, education, healthcare access, municipal services,
and other public-service needs across India.

You are an agentic AI assistant.

Your workflow:

1. Understand what the citizen wants.
2. Identify the service or problem.
3. Determine whether location is necessary.
4. Ask only the necessary follow-up questions.
5. Identify the likely department/service.
6. Explain the next steps clearly.
7. Provide an official government service link when appropriate.
8. Never invent government rules, fees, deadlines, eligibility requirements,
   phone numbers, or URLs.
9. If information is uncertain, clearly say that it should be verified
   through the relevant official government portal.
10. Prefer official Indian government sources such as:
    india.gov.in
    services.india.gov.in
    mygov.in
    uidai.gov.in
    incometax.gov.in
    parivahan.gov.in
    passportindia.gov.in
    epfindia.gov.in
    digilocker.gov.in
    scholarships.gov.in
    pmkisan.gov.in

IMPORTANT:
Return ONLY valid JSON.
Do not use Markdown.
Do not put JSON inside code fences.

The JSON must contain exactly these fields:

{
  "summary": "Short helpful answer",
  "department": "Relevant department or service",
  "location_needed": true or false,
  "question": "One necessary follow-up question, or empty string",
  "steps": ["Step 1", "Step 2"],
  "documents": ["Document 1", "Document 2"],
  "official_link": "Official URL or empty string",
  "urgency": "low, medium, or high"
}

If the citizen has provided enough information, do not ask unnecessary questions.

If the user simply greets you, respond naturally in the summary and leave
department, question, documents and official_link empty.

If the citizen reports an emergency, advise them to contact the appropriate
emergency service immediately, while keeping the response concise.

You are not a substitute for an official government authority.
"""


# ============================================================
# SERVICE DIRECTORY
# ============================================================

INDIA_SERVICES = {
    "National Government Services Portal":
        "https://services.india.gov.in/",

    "National Portal of India":
        "https://www.india.gov.in/",

    "MyGov India":
        "https://www.mygov.in/",

    "UIDAI Aadhaar":
        "https://uidai.gov.in/",

    "DigiLocker":
        "https://www.digilocker.gov.in/",

    "Income Tax":
        "https://www.incometax.gov.in/",

    "Passport Seva":
        "https://www.passportindia.gov.in/",

    "Parivahan":
        "https://parivahan.gov.in/",

    "EPFO":
        "https://www.epfindia.gov.in/",

    "National Scholarship Portal":
        "https://scholarships.gov.in/",

    "PM Kisan":
        "https://pmkisan.gov.in/",

    "National Career Service":
        "https://www.ncs.gov.in/",

    "RTI Online":
        "https://rtionline.gov.in/",

    "Consumer Helpline":
        "https://consumerhelpline.gov.in/",

    "CPGRAMS":
        "https://pgportal.gov.in/",
}


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = "New Conversation"

if "last_transcript" not in st.session_state:
    st.session_state.last_transcript = ""

if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

if "tts_audio" not in st.session_state:
    st.session_state.tts_audio = None

if "selected_voice" not in st.session_state:
    st.session_state.selected_voice = "priya"

if "agent_status" not in st.session_state:
    st.session_state.agent_status = "Ready"


# ============================================================
# UI STYLE
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1250px;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128,128,128,0.15);
        }

        .nextstep-title {
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0;
        }

        .nextstep-subtitle {
            color: #777;
            font-size: 1rem;
            margin-top: 0.2rem;
        }

        .status-card {
            padding: 12px 16px;
            border-radius: 12px;
            border: 1px solid rgba(128,128,128,0.18);
            margin-bottom: 12px;
        }

        .service-card {
            padding: 15px;
            border-radius: 14px;
            border: 1px solid rgba(128,128,128,0.18);
            margin-bottom: 10px;
        }

        .small-muted {
            color: #777;
            font-size: 0.85rem;
        }

        .hero-box {
            padding: 22px;
            border-radius: 18px;
            border: 1px solid rgba(128,128,128,0.18);
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def safe_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, str) and value.strip():
        return [value.strip()]

    return []


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Robust JSON parser.

    Handles:
    - normal JSON
    - JSON inside markdown fences
    - extra text before/after JSON
    """

    if not text:
        return None

    text = text.strip()

    # Remove markdown fences.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    try:
        result = json.loads(text)

        if isinstance(result, dict):
            return result
    except Exception:
        pass

    # Find the first JSON object.
    start = text.find("{")

    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(text)):
        char = text[index]

        if escape:
            escape = False
            continue

        if char == "\\":
            escape = True
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
                candidate = text[start:index + 1]

                try:
                    result = json.loads(candidate)

                    if isinstance(result, dict):
                        return result

                except Exception:
                    return None

    return None


def normalize_ai_response(data: Dict[str, Any]) -> Dict[str, Any]:

    return {
        "summary": clean_text(data.get("summary")),
        "department": clean_text(data.get("department")),
        "location_needed": bool(data.get("location_needed", False)),
        "question": clean_text(data.get("question")),
        "steps": safe_list(data.get("steps")),
        "documents": safe_list(data.get("documents")),
        "official_link": clean_text(data.get("official_link")),
        "urgency": clean_text(data.get("urgency")).lower() or "low",
    }


def get_chat_history() -> List[Dict[str, str]]:

    history = []

    for item in st.session_state.messages[-MAX_HISTORY_MESSAGES:]:
        role = item.get("role")

        if role not in ("user", "assistant"):
            continue

        content = item.get("content", "")

        if not content:
            continue

        history.append(
            {
                "role": role,
                "content": content,
            }
        )

    return history


# ============================================================
# OPENROUTER CHAT
# ============================================================

def call_openrouter(user_message: str) -> Dict[str, Any]:

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
            "content": SYSTEM_INSTRUCTION,
        }
    ]

    # Existing conversation history
    for message in get_chat_history():

        messages.append(
            {
                "role": message["role"],
                "content": message["content"],
            }
        )

    # Add current message exactly once.
    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 1000,
        "response_format": {
            "type": "json_object"
        },
        "provider": {
            "require_parameters": True
        },
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nextstep-ai.streamlit.app",
        "X-Title": "NextStep AI",
    }

    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )

    except requests.RequestException as error:

        return {
            "summary": f"Connection error while contacting the AI service: {error}",
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
                "Please wait a little and try again."
            )

        return {
            "summary": f"AI service error: {error_message}",
            "department": "",
            "location_needed": False,
            "question": "",
            "steps": [],
            "documents": [],
            "official_link": "",
            "urgency": "low",
        }

    try:

        result = response.json()

        choices = result.get("choices", [])

        if not choices:
            raise ValueError("No response choices returned.")

        content = (
            choices[0]
            .get("message", {})
            .get("content", "")
        )

        if isinstance(content, list):

            parts = []

            for part in content:

                if isinstance(part, dict):
                    parts.append(
                        clean_text(part.get("text"))
                    )

            content = "".join(parts)

        content = clean_text(content)

    except Exception as error:

        return {
            "summary": f"Could not read the AI response: {error}",
            "department": "",
            "location_needed": False,
            "question": "",
            "steps": [],
            "documents": [],
            "official_link": "",
            "urgency": "low",
        }

    parsed = extract_json(content)

    if parsed is None:

        # Final graceful fallback.
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

    return normalize_ai_response(parsed)


# ============================================================
# SARVAM SPEECH TO TEXT
# ============================================================

def transcribe_with_sarvam(
    audio_bytes: bytes,
    language_code: str = "unknown",
) -> str:

    if not SARVAM_API_KEY:
        return ""

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
    }

    files = {
        "file": (
            "nextstep_voice.wav",
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

        return clean_text(transcript)

    except Exception:
        return ""


# ============================================================
# OPENROUTER WHISPER FALLBACK
# ============================================================

def transcribe_with_openrouter(
    audio_bytes: bytes,
) -> str:

    if not OPENROUTER_API_KEY:
        return ""

    encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")

    payload = {
        "model": "openai/whisper-1",
        "input_audio": {
            "data": encoded_audio,
            "format": "wav",
        },
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/audio/transcriptions",
            headers=headers,
            json=payload,
            timeout=90,
        )

    except requests.RequestException:
        return ""

    if response.status_code != 200:
        return ""

    try:

        result = response.json()

        transcript = (
            result.get("text")
            or result.get("transcript")
            or ""
        )

        return clean_text(transcript)

    except Exception:
        return ""


def transcribe_audio(
    audio_bytes: bytes,
    language_code: str,
) -> str:

    # Prefer Sarvam for Indian-language recognition.
    if SARVAM_API_KEY:

        transcript = transcribe_with_sarvam(
            audio_bytes,
            language_code,
        )

        if transcript:
            return transcript

    # Fallback to OpenRouter Whisper.
    return transcribe_with_openrouter(audio_bytes)


# ============================================================
# SARVAM TEXT TO SPEECH
# ============================================================

def generate_speech(
    text: str,
    language_code: str = "en-IN",
    voice: str = "priya",
) -> Optional[bytes]:

    if not SARVAM_API_KEY:
        return None

    text = clean_text(text)

    if not text:
        return None

    # Keep the spoken answer reasonably short.
    text = text[:2500]

    payload = {
        "text": text,
        "target_language_code": language_code,
        "speaker": voice,
        "model": SARVAM_TTS_MODEL,
    }

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json",
    }

    try:

        response = requests.post(
            SARVAM_TTS_URL,
            headers=headers,
            json=payload,
            timeout=90,
        )

    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:

        result = response.json()

        audios = result.get("audios", [])

        if not audios:
            return None

        return base64.b64decode(audios[0])

    except Exception:
        return None


# ============================================================
# SAVE CONVERSATION
# ============================================================

def save_message(
    role: str,
    content: str,
):

    st.session_state.messages.append(
        {
            "role": role,
            "content": content,
            "time": datetime.now().strftime("%H:%M"),
        }
    )


def create_conversation_title(text: str) -> str:

    text = clean_text(text)

    if len(text) <= 32:
        return text

    return text[:32] + "..."


# ============================================================
# DISPLAY AI RESPONSE
# ============================================================

def display_ai_response(result: Dict[str, Any]):

    summary = result.get("summary", "")

    if summary:
        st.markdown("### 🤖 NextStep AI")
        st.write(summary)

    department = result.get("department", "")

    if department:
        st.info(f"🏢 **Department / Service:** {department}")

    urgency = result.get("urgency", "low")

    if urgency == "high":
        st.warning("🚨 **Priority:** This request may require prompt attention.")

    elif urgency == "medium":
        st.warning("⚠️ **Priority:** This request may need timely action.")

    steps = result.get("steps", [])

    if steps:

        st.markdown("### 📋 Next Steps")

        for index, step in enumerate(steps, 1):
            st.write(f"**{index}.** {step}")

    documents = result.get("documents", [])

    if documents:

        st.markdown("### 📄 Possible Documents")

        for document in documents:
            st.write(f"• {document}")

    official_link = result.get("official_link", "")

    if official_link:

        if official_link.startswith("http://") or official_link.startswith(
            "https://"
        ):

            st.markdown("### 🔗 Official Service")

            st.link_button(
                "Open Official Government Service",
                official_link,
            )

    question = result.get("question", "")

    if question:

        st.info(f"❓ **Next question:** {question}")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🧭 NextStep AI")

    st.caption("AI-powered citizen services for India")

    st.divider()

    st.markdown("### 🤖 Agent Status")

    if OPENROUTER_API_KEY:
        st.success("AI connected")
    else:
        st.error("OpenRouter key missing")

    if SARVAM_API_KEY:
        st.success("Voice services connected")
    else:
        st.warning("Sarvam voice key not configured")

    st.divider()

    st.markdown("### 💬 Conversation")

    if st.button(
        "＋ New Conversation",
        use_container_width=True,
    ):

        if st.session_state.messages:

            st.session_state.conversation_history.append(
                {
                    "title": st.session_state.current_conversation,
                    "messages": st.session_state.messages.copy(),
                }
            )

        st.session_state.messages = []
        st.session_state.current_conversation = "New Conversation"
        st.session_state.last_transcript = ""
        st.session_state.tts_audio = None

        st.rerun()

    if st.session_state.conversation_history:

        st.markdown("#### Previous Conversations")

        for index, conversation in enumerate(
            st.session_state.conversation_history
        ):

            title = conversation.get(
                "title",
                f"Conversation {index + 1}",
            )

            if st.button(
                title,
                key=f"conversation_{index}",
                use_container_width=True,
            ):

                st.session_state.messages = (
                    conversation.get("messages", []).copy()
                )

                st.session_state.current_conversation = title

                st.rerun()

    st.divider()

    st.markdown("### 🎙️ Voice")

    selected_voice = st.selectbox(
        "Assistant voice",
        options=[
            "priya",
            "ritu",
            "aditya",
            "rahul",
        ],
        index=[
            "priya",
            "ritu",
            "aditya",
            "rahul",
        ].index(st.session_state.selected_voice),
    )

    st.session_state.selected_voice = selected_voice

    st.divider()

    st.markdown("### 🇮🇳 Government Services")

    for name, url in list(INDIA_SERVICES.items())[:8]:

        st.link_button(
            name,
            url,
            use_container_width=True,
        )

    st.divider()

    st.caption(
        "NextStep AI helps citizens discover the right next step. "
        "Always verify important information with the official authority."
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="nextstep-title">🧭 NextStep AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="nextstep-subtitle">'
    "Your intelligent guide to public services across India"
    "</div>",
    unsafe_allow_html=True,
)

st.write("")


# ============================================================
# HERO
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="hero-box">
            <h2>👋 What do you need help with?</h2>
            <p>
                Tell me what you need. I can help you navigate
                government services, civic complaints, documents,
                schemes, transport, utilities and more.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("🏙️ **Civic Services**\n\nComplaints, roads, waste, water and infrastructure.")

    with col2:
        st.info("📄 **Documents & Schemes**\n\nAadhaar, certificates, schemes and applications.")

    with col3:
        st.info("🚗 **Transport & Public Services**\n\nDriving licence, vehicles, passports and more.")


# ============================================================
# CHAT HISTORY DISPLAY
# ============================================================

for message in st.session_state.messages:

    role = message.get("role", "assistant")

    if role == "user":

        with st.chat_message("user"):
            st.write(message.get("content", ""))

    elif role == "assistant":

        with st.chat_message("assistant"):

            raw_content = message.get("content", "")

            parsed = extract_json(raw_content)

            if parsed:

                display_ai_response(
                    normalize_ai_response(parsed)
                )

            else:
                st.write(raw_content)


# ============================================================
# VOICE INPUT
# ============================================================

st.markdown("### 🎙️ Voice Input")

voice_language = st.selectbox(
    "Voice language",
    options=[
        "Auto",
        "English",
        "Hindi",
        "Telugu",
    ],
    index=0,
)

language_map = {
    "Auto": "unknown",
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Telugu": "te-IN",
}

audio_value = st.audio_input(
    "Tap the microphone and speak",
    sample_rate=16000,
)

if audio_value is not None:

    audio_bytes = audio_value.getvalue()

    st.audio(
        audio_bytes,
        format="audio/wav",
    )

    st.success("🎙️ Voice recording captured.")

    if st.button(
        "📝 Transcribe Voice",
        use_container_width=True,
    ):

        with st.spinner("Understanding your voice..."):

            transcript = transcribe_audio(
                audio_bytes,
                language_map[voice_language],
            )

        if transcript:

            st.session_state.last_transcript = transcript

            st.success("Voice converted to text.")

        else:

            st.error(
                "I could not convert the recording to text. "
                "Check your Sarvam/OpenRouter API configuration."
            )


if st.session_state.last_transcript:

    st.markdown("#### 📝 Transcribed Request")

    st.info(st.session_state.last_transcript)

    if st.button(
        "🚀 Send Voice Request",
        use_container_width=True,
    ):

        user_message = st.session_state.last_transcript

        if not st.session_state.messages:
            st.session_state.current_conversation = (
                create_conversation_title(user_message)
            )

        save_message(
            "user",
            user_message,
        )

        st.session_state.agent_status = "Thinking"

        with st.spinner("NextStep AI is analyzing your request..."):

            result = call_openrouter(
                user_message
            )

        st.session_state.agent_status = "Ready"

        result_text = json.dumps(
            result,
            ensure_ascii=False,
        )

        save_message(
            "assistant",
            result_text,
        )

        st.session_state.last_transcript = ""

        # Generate speech when Sarvam is available.
        spoken_text = result.get("summary", "")

        if spoken_text and SARVAM_API_KEY:

            tts_language = "en-IN"

            if voice_language == "Hindi":
                tts_language = "hi-IN"

            elif voice_language == "Telugu":
                tts_language = "te-IN"

            audio_output = generate_speech(
                spoken_text,
                tts_language,
                st.session_state.selected_voice,
            )

            if audio_output:
                st.session_state.tts_audio = audio_output

        st.rerun()


# ============================================================
# TEXT CHAT
# ============================================================

st.markdown("### 💬 Ask NextStep AI")

user_input = st.chat_input(
    "Describe what you need help with..."
)

if user_input:

    user_input = clean_text(user_input)

    if user_input:

        if not st.session_state.messages:

            st.session_state.current_conversation = (
                create_conversation_title(user_input)
            )

        save_message(
            "user",
            user_input,
        )

        st.session_state.agent_status = "Thinking"

        with st.spinner("NextStep AI is analyzing your request..."):

            result = call_openrouter(
                user_input
            )

        st.session_state.agent_status = "Ready"

        result_text = json.dumps(
            result,
            ensure_ascii=False,
        )

        save_message(
            "assistant",
            result_text,
        )

        # Text-to-speech
        if SARVAM_API_KEY:

            spoken_text = result.get(
                "summary",
                "",
            )

            if spoken_text:

                audio_output = generate_speech(
                    spoken_text,
                    "en-IN",
                    st.session_state.selected_voice,
                )

                if audio_output:
                    st.session_state.tts_audio = audio_output

        st.rerun()


# ============================================================
# PLAY LAST AI VOICE RESPONSE
# ============================================================

if st.session_state.tts_audio:

    st.divider()

    st.markdown("### 🔊 Voice Response")

    st.audio(
        st.session_state.tts_audio,
        format="audio/wav",
    )

    if st.button(
        "✕ Clear Voice Response",
    ):

        st.session_state.tts_audio = None

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

footer_col1, footer_col2 = st.columns(2)

with footer_col1:

    st.caption(
        "🧭 NextStep AI • Agentic AI for Smart Cities & Public Services"
    )

with footer_col2:

    st.caption(
        "🇮🇳 Designed for citizen-service navigation across India"
    )
