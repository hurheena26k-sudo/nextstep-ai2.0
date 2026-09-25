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
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIG
# ============================================================

OPENROUTER_CHAT_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

OPENROUTER_TRANSCRIPTION_URL = (
    "https://openrouter.ai/api/v1/audio/transcriptions"
)

# Free router for normal text chat
CHAT_MODEL = "openrouter/free"

# OpenRouter's documented transcription model
TRANSCRIPTION_MODEL = "openai/whisper-1"


# ============================================================
# NEXTSTEP AI SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are NextStep AI, an intelligent public-service assistant
for citizens in India.

Your job is to understand what a citizen needs, identify the
likely public service, and provide simple practical next steps.

IMPORTANT RULES:

1. Understand the citizen's actual need before choosing a service.

2. Citizens do not need to know the official service name.

3. If a necessary detail is missing, ask ONE clear clarification
question instead of guessing.

4. Give practical steps when the request is clear.

5. Do not invent government rules, fees, eligibility criteria,
deadlines, documents, or URLs.

6. Procedures can vary by state, UT, city, or department.
Ask for location when it materially matters.

7. This assistant covers services across INDIA.

8. Do not assume the citizen is from Telangana, Andhra Pradesh,
Delhi, Maharashtra, or any other particular state.

9. Greetings and general questions are not service requests.

10. Do not include URLs in your answer.
The application adds official links separately.

11. Keep the response concise and citizen-friendly.

12. If the user gives an unclear request, ask one useful
clarification question.

13. If the user describes a public problem without knowing
the department, identify the likely category yourself.

14. Never pretend that a government service is available in a
specific state unless the information is known from the request.

15. For state-specific services, ask for the state/city when
needed.

Return ONLY valid JSON with exactly these fields:

{
  "intent": "general" | "clarification" | "service_request",
  "service_key": "service key" | null,
  "title": "short title",
  "summary": "short explanation",
  "steps": ["step 1", "step 2"],
  "documents": ["document 1"],
  "next_action": "one clear next action",
  "transcript": "what the citizen said"
}

Allowed service_key values:

india_services
birth_certificate
death_certificate
income_certificate
caste_certificate
residence_certificate
aadhaar
driving_license
passport
voter_service
government_schemes
public_grievance
property_tax
water_connection
education_scholarship
employment
railway
land_services
vehicle_services
digilocker
other_government_service

Use null for general or clarification responses.
"""


# ============================================================
# INDIA-WIDE OFFICIAL SOURCES
# ============================================================

SERVICE_LINKS = {
    "india_services": {
        "name": "National Government Services Portal",
        "url": "https://services.india.gov.in/",
        "label": "Government of India",
    },

    "birth_certificate": {
        "name": "Birth Certificate",
        "url": "https://services.india.gov.in/",
        "label": "National Government Services Portal",
    },

    "death_certificate": {
        "name": "Death Certificate",
        "url": "https://services.india.gov.in/",
        "label": "National Government Services Portal",
    },

    "income_certificate": {
        "name": "Income Certificate",
        "url": "https://services.india.gov.in/",
        "label": "National Government Services Portal",
    },

    "caste_certificate": {
        "name": "Caste Certificate",
        "url": "https://services.india.gov.in/",
        "label": "National Government Services Portal",
    },

    "residence_certificate": {
        "name": "Residence Certificate",
        "url": "https://services.india.gov.in/",
        "label": "National Government Services Portal",
    },

    "aadhaar": {
        "name": "Aadhaar",
        "url": "https://uidai.gov.in/",
        "label": "UIDAI",
    },

    "driving_license": {
        "name": "Driving Licence",
        "url": "https://parivahan.gov.in/",
        "label": "Parivahan Sewa",
    },

    "passport": {
        "name": "Passport",
        "url": "https://www.passportindia.gov.in/",
        "label": "Passport Seva",
    },

    "voter_service": {
        "name": "Voter Services",
        "url": "https://voters.eci.gov.in/",
        "label": "Election Commission of India",
    },

    "government_schemes": {
        "name": "Government Schemes",
        "url": "https://www.myscheme.gov.in/",
        "label": "myScheme",
    },

    "public_grievance": {
        "name": "Public Grievance",
        "url": "https://pgportal.gov.in/",
        "label": "CPGRAMS",
    },

    "property_tax": {
        "name": "Property Tax",
        "url": "https://services.india.gov.in/",
        "label": "National Government Services Portal",
    },

    "water_connection": {
        "name": "Water Services",
        "url": "https://services.india.gov.in/",
        "label": "National Government Services Portal",
    },

    "education_scholarship": {
        "name": "Education / Scholarships",
        "url": "https://scholarships.gov.in/",
        "label": "National Scholarship Portal",
    },

    "employment": {
        "name": "Employment Services",
        "url": "https://www.ncs.gov.in/",
        "label": "National Career Service",
    },

    "railway": {
        "name": "Railway Services",
        "url": "https://www.irctc.co.in/",
        "label": "IRCTC",
    },

    "land_services": {
        "name": "Land Services",
        "url": "https://services.india.gov.in/",
        "label": "National Government Services Portal",
    },

    "vehicle_services": {
        "name": "Vehicle Services",
        "url": "https://parivahan.gov.in/",
        "label": "Parivahan Sewa",
    },

    "digilocker": {
        "name": "DigiLocker",
        "url": "https://www.digilocker.gov.in/",
        "label": "DigiLocker",
    },

    "other_government_service": {
        "name": "Government Services",
        "url": "https://services.india.gov.in/",
        "label": "National Government Services Portal",
    },
}


# ============================================================
# SESSION STATE
# ============================================================

def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation_title" not in st.session_state:
        st.session_state.conversation_title = "New conversation"

    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None

    if "voice_language" not in st.session_state:
        st.session_state.voice_language = "Auto"

    if "last_transcript" not in st.session_state:
        st.session_state.last_transcript = ""


init_state()


# ============================================================
# API KEY
# ============================================================

def get_api_key() -> Optional[str]:
    try:
        key = st.secrets.get("OPENROUTER_API_KEY")
    except Exception:
        return None

    if not key:
        return None

    return str(key).strip()


# ============================================================
# OPENROUTER HEADERS
# ============================================================

def openrouter_headers(api_key: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nextstep-ai.streamlit.app",
        "X-Title": "NextStep AI",
    }


# ============================================================
# JSON CLEANING
# ============================================================

def clean_json(text: str) -> str:
    text = (text or "").strip()

    # Remove markdown code fences
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
    )

    return text.strip()


def extract_json_object(text: str) -> Dict[str, Any]:
    """
    Attempts to safely extract a JSON object even if the model
    accidentally adds a little extra text around it.
    """

    cleaned = clean_json(text)

    try:
        parsed = json.loads(cleaned)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # Try to locate the first JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start:end + 1]

        try:
            parsed = json.loads(candidate)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

    raise ValueError("Could not parse the AI response as JSON.")


# ============================================================
# SAFE LIST
# ============================================================

def safe_list(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    value = str(value).strip()

    if value:
        return [value]

    return []


# ============================================================
# NORMALIZE AI RESULT
# ============================================================

def normalize_result(
    data: Dict[str, Any],
    fallback_transcript: str = "",
) -> Dict[str, Any]:

    intent = str(
        data.get("intent", "general")
    ).strip().lower()

    if intent not in {
        "general",
        "clarification",
        "service_request",
    }:
        intent = "general"

    service_key = data.get("service_key")

    if service_key not in SERVICE_LINKS:
        service_key = None

    if intent != "service_request":
        service_key = None

    return {
        "intent": intent,
        "service_key": service_key,
        "title": str(
            data.get("title")
            or "Your Next Step"
        ),
        "summary": str(
            data.get("summary")
            or ""
        ),
        "steps": safe_list(
            data.get("steps")
        ),
        "documents": safe_list(
            data.get("documents")
        ),
        "next_action": str(
            data.get("next_action")
            or ""
        ),
        "transcript": str(
            data.get("transcript")
            or fallback_transcript
        ),
    }


# ============================================================
# ERROR RESULT
# ============================================================

def error_result(
    title: str,
    summary: str,
    steps: Optional[List[str]] = None,
    next_action: str = "",
) -> Dict[str, Any]:

    return {
        "intent": "error",
        "service_key": None,
        "title": title,
        "summary": summary,
        "steps": steps or [],
        "documents": [],
        "next_action": next_action,
        "transcript": "",
    }


# ============================================================
# CONVERSATION HISTORY
# ============================================================

def conversation_for_ai() -> List[Dict[str, str]]:
    """
    Converts the existing conversation into OpenRouter format.

    IMPORTANT:
    The current user message is NOT included here because
    call_openrouter() adds it separately.

    This prevents the newest user message from being sent twice.
    """

    history = []

    for message in st.session_state.messages:

        role = message.get("role")

        if role == "user":

            content = str(
                message.get("content", "")
            ).strip()

            if content:
                history.append({
                    "role": "user",
                    "content": content,
                })

        elif role == "assistant":

            content = str(
                message.get("content", "")
            ).strip()

            if content:
                history.append({
                    "role": "assistant",
                    "content": content,
                })

    return history


# ============================================================
# OPENROUTER CHAT
# ============================================================

def call_openrouter(
    user_message: str,
) -> Dict[str, Any]:

    api_key = get_api_key()

    if not api_key:

        return error_result(
            "OpenRouter key not found",
            (
                "NextStep AI needs your OpenRouter "
                "API key before it can process requests."
            ),
            [
                "Open your Streamlit app settings.",
                "Open the Secrets section.",
                "Add OPENROUTER_API_KEY.",
                "Save the secret and restart the app.",
            ],
            "Add the OpenRouter API key to Streamlit Secrets.",
        )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_INSTRUCTION,
        }
    ]

    # Add previous conversation
    messages.extend(
        conversation_for_ai()
    )

    # Add ONLY the current message
    messages.append({
        "role": "user",
        "content": user_message,
    })

    payload = {
        "model": CHAT_MODEL,
        "messages": messages,
        "temperature": 0.2,
    }

    try:

        response = requests.post(
            OPENROUTER_CHAT_URL,
            headers=openrouter_headers(api_key),
            json=payload,
            timeout=90,
        )

        # ----------------------------------------------------
        # RATE LIMIT
        # ----------------------------------------------------

        if response.status_code == 429:

            return error_result(
                "AI rate limit reached",
                (
                    "OpenRouter temporarily limited "
                    "this request."
                ),
                [
                    "Wait a short moment.",
                    "Try the same request again.",
                ],
                "Try again in a moment.",
            )

        # ----------------------------------------------------
        # OTHER API ERRORS
        # ----------------------------------------------------

        if response.status_code >= 400:

            try:

                error_data = response.json()

                error_object = error_data.get(
                    "error",
                    {},
                )

                message = error_object.get(
                    "message",
                    response.text,
                )

            except Exception:

                message = response.text

            return error_result(
                "AI request failed",
                (
                    "OpenRouter returned an error:\n\n"
                    f"{message}"
                ),
                [
                    "Check your OpenRouter API key.",
                    "Check whether the selected model is available.",
                    "Try the request again.",
                ],
                "Check the OpenRouter connection.",
            )

        # ----------------------------------------------------
        # PARSE RESPONSE
        # ----------------------------------------------------

        data = response.json()

        choices = data.get("choices") or []

        if not choices:

            return error_result(
                "No AI response",
                "OpenRouter did not return a usable AI response.",
                [
                    "Wait a moment.",
                    "Try the request again.",
                ],
                "Try again.",
            )

        message_data = (
            choices[0]
            .get("message", {})
        )

        raw_content = message_data.get(
            "content",
            "",
        )

        # Some providers can return structured content.
        if isinstance(raw_content, list):

            parts = []

            for item in raw_content:

                if isinstance(item, dict):

                    text_part = item.get(
                        "text",
                        "",
                    )

                    if text_part:
                        parts.append(
                            str(text_part)
                        )

                else:
                    parts.append(str(item))

            raw_content = "".join(parts)

        if not str(raw_content).strip():

            return error_result(
                "Empty AI response",
                "The AI returned an empty response.",
                [
                    "Try asking the question again.",
                ],
                "Try again.",
            )

        # ----------------------------------------------------
        # JSON PARSING
        # ----------------------------------------------------

        parsed = extract_json_object(
            str(raw_content)
        )

        return normalize_result(
            parsed,
            fallback_transcript=user_message,
        )

    # --------------------------------------------------------
    # NETWORK ERROR
    # --------------------------------------------------------

    except requests.Timeout:

        return error_result(
            "Request timed out",
            (
                "The AI service took too long "
                "to respond."
            ),
            [
                "Check your internet connection.",
                "Try the request again.",
            ],
            "Try again.",
        )

    except requests.RequestException as error:

        return error_result(
            "Connection problem",
            (
                "NextStep AI could not reach "
                "OpenRouter right now."
            ),
            [
                "Check your internet connection.",
                "Check your OpenRouter key.",
                "Try again in a moment.",
            ],
            "Try the request again.",
        )

    # --------------------------------------------------------
    # JSON / RESPONSE ERROR
    # --------------------------------------------------------

    except ValueError:

        return error_result(
            "Unexpected AI response",
            (
                "The AI returned a response "
                "that NextStep AI could not "
                "safely format."
            ),
            [
                "Try asking the same question again.",
                "Keep the request short and clear.",
            ],
            "Try again.",
        )

    except Exception:

        return error_result(
            "Something went wrong",
            (
                "NextStep AI encountered "
                "an unexpected problem."
            ),
            [
                "Try the request again.",
            ],
            "Try again in a moment.",
        )


# ============================================================
# OPENROUTER SPEECH TO TEXT
# ============================================================

def transcribe_audio(
    audio_file,
) -> str:

    api_key = get_api_key()

    if not api_key:

        raise RuntimeError(
            "OpenRouter API key not found."
        )

    if audio_file is None:

        raise ValueError(
            "No voice recording was received."
        )

    try:

        audio_bytes = audio_file.getvalue()

    except Exception as error:

        raise RuntimeError(
            f"Could not read the voice recording: {error}"
        )

    if not audio_bytes:

        raise ValueError(
            "The voice recording is empty."
        )

    # Streamlit st.audio_input currently returns WAV audio.
    # OpenRouter expects base64 audio + a format.
    audio_base64 = base64.b64encode(
        audio_bytes
    ).decode("utf-8")

    selected_language = (
        st.session_state.get(
            "voice_language",
            "Auto",
        )
    )

    payload = {
        "model": TRANSCRIPTION_MODEL,
        "input_audio": {
            "data": audio_base64,
            "format": "wav",
        },
    }

    # Do NOT send a language when Auto is selected.
    # This lets the transcription model determine it.
    language_map = {
        "English": "en",
        "Hindi": "hi",
        "Telugu": "te",
    }

    if selected_language in language_map:

        payload["language"] = language_map[
            selected_language
        ]

    try:

        response = requests.post(
            OPENROUTER_TRANSCRIPTION_URL,
            headers=openrouter_headers(api_key),
            json=payload,
            timeout=90,
        )

    except requests.Timeout:

        raise RuntimeError(
            "Voice transcription timed out. "
            "Please try again."
        )

    except requests.RequestException:

        raise RuntimeError(
            "Could not connect to OpenRouter "
            "for voice transcription."
        )

    # --------------------------------------------------------
    # HANDLE ERRORS
    # --------------------------------------------------------

    if response.status_code == 429:

        raise RuntimeError(
            "Voice transcription was rate-limited. "
            "Please wait a moment and try again."
        )

    if response.status_code >= 400:

        try:

            error_data = response.json()

            error_object = error_data.get(
                "error",
                {},
            )

            message = error_object.get(
                "message",
                response.text,
            )

        except Exception:

            message = response.text

        raise RuntimeError(
            "Voice transcription failed: "
            f"{message}"
        )

    # --------------------------------------------------------
    # PARSE TRANSCRIPTION
    # --------------------------------------------------------

    try:

        result = response.json()

    except ValueError:

        raise RuntimeError(
            "OpenRouter returned an invalid "
            "transcription response."
        )

    transcript = str(
        result.get("text", "")
    ).strip()

    if not transcript:

        raise ValueError(
            "No speech was detected. "
            "Please speak clearly and try again."
        )

    return transcript


# ============================================================
# RENDER ASSISTANT RESPONSE
# ============================================================

def render_assistant_result(
    result: Dict[str, Any],
):

    title = result.get(
        "title",
        "Your Next Step",
    )

    summary = result.get(
        "summary",
        "",
    )

    intent = result.get(
        "intent",
        "general",
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    st.subheader(
        f"✨ {title}"
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    if summary:

        st.info(summary)

    # --------------------------------------------------------
    # TRANSCRIPT
    # --------------------------------------------------------

    transcript = result.get(
        "transcript",
        "",
    )

    if transcript:

        with st.expander(
            "🎙️ Voice transcript"
        ):

            st.write(transcript)

    # --------------------------------------------------------
    # CLARIFICATION
    # --------------------------------------------------------

    if intent == "clarification":

        st.warning(
            "❓ I need one more detail "
            "to guide you correctly."
        )

    # --------------------------------------------------------
    # STEPS
    # --------------------------------------------------------

    steps = result.get(
        "steps",
        [],
    )

    if steps:

        st.markdown(
            "#### 🧭 Next steps"
        )

        for index, step in enumerate(
            steps,
            start=1,
        ):

            st.write(
                f"**{index}.** {step}"
            )

    # --------------------------------------------------------
    # DOCUMENTS
    # --------------------------------------------------------

    documents = result.get(
        "documents",
        [],
    )

    if documents:

        st.markdown(
            "#### 📋 Documents to check"
        )

        for document in documents:

            st.write(
                f"• {document}"
            )

    # --------------------------------------------------------
    # NEXT ACTION
    # --------------------------------------------------------

    next_action = result.get(
        "next_action",
        "",
    )

    if next_action:

        st.success(
            f"➡️ **Next action:** {next_action}"
        )

    # --------------------------------------------------------
    # OFFICIAL SOURCE
    # --------------------------------------------------------

    service_key = result.get(
        "service_key"
    )

    if (
        intent == "service_request"
        and service_key in SERVICE_LINKS
    ):

        service = SERVICE_LINKS[
            service_key
        ]

        st.markdown(
            "#### 🔗 Official source"
        )

        st.link_button(
            f"Open {service['name']}",
            service["url"],
            use_container_width=True,
        )

        st.caption(
            f"Source: {service['label']}"
        )


# ============================================================
# PROCESS USER MESSAGE
# ============================================================

def process_user_message(
    text: str,
):

    text = str(text).strip()

    if not text:
        return

    # First user message becomes conversation title.
    if not st.session_state.messages:

        title = re.sub(
            r"\s+",
            " ",
            text,
        )

        if len(title) > 45:
            title = title[:45] + "..."

        st.session_state.conversation_title = title

    # Add user message to history BEFORE calling AI.
    # conversation_for_ai() uses previous history only
    # because the current message is passed separately.
    st.session_state.messages.append({
        "role": "user",
        "content": text,
    })

    with st.chat_message(
        "assistant",
        avatar="🤖",
    ):

        with st.spinner(
            "Thinking through the next step..."
        ):

            result = call_openrouter(
                text
            )

        render_assistant_result(
            result
        )

    # Save complete result for history.
    st.session_state.messages.append({
        "role": "assistant",
        "content": result.get(
            "summary",
            "",
        ),
        **result,
    })


# ============================================================
# NEW CONVERSATION
# ============================================================

def new_conversation():

    st.session_state.messages = []

    st.session_state.conversation_title = (
        "New conversation"
    )

    st.session_state.pending_prompt = None

    st.session_state.last_transcript = ""


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 NextStep AI")

    st.caption(
        "India-wide public-service guidance"
    )

    st.divider()

    # --------------------------------------------------------
    # NEW CONVERSATION
    # --------------------------------------------------------

    if st.button(
        "＋ New conversation",
        use_container_width=True,
    ):

        new_conversation()

        st.rerun()

    st.divider()

    # --------------------------------------------------------
    # CURRENT CONVERSATION
    # --------------------------------------------------------

    st.subheader(
        "💬 Current conversation"
    )

    st.caption(
        st.session_state.conversation_title
    )

    user_messages = [
        message.get(
            "content",
            "",
        )
        for message in st.session_state.messages
        if message.get("role") == "user"
    ]

    if user_messages:

        for index, message in enumerate(
            user_messages[-8:],
            start=1,
        ):

            preview = message.replace(
                "\n",
                " ",
            )

            if len(preview) > 42:

                preview = (
                    preview[:42]
                    + "..."
                )

            st.caption(
                f"{index}. {preview}"
            )

    else:

        st.caption(
            "Your messages will appear here."
        )

    st.divider()

    # --------------------------------------------------------
    # VOICE SETTINGS
    # --------------------------------------------------------

    st.subheader("🎙️ Voice")

    st.session_state.voice_language = (
        st.selectbox(
            "Speech language",
            [
                "Auto",
                "English",
                "Hindi",
                "Telugu",
            ],
            index=[
                "Auto",
                "English",
                "Hindi",
                "Telugu",
            ].index(
                st.session_state.voice_language
            )
            if st.session_state.voice_language
            in [
                "Auto",
                "English",
                "Hindi",
                "Telugu",
            ]
            else 0,
        )
    )

    st.caption(
        "Auto lets the transcription model "
        "detect the language."
    )

    st.divider()

    # --------------------------------------------------------
    # APP INFO
    # --------------------------------------------------------

    st.info(
        "💡 Describe your problem in normal "
        "language. You do not need to know "
        "the exact government department."
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title(
    "✦ NextStep AI"
)

st.caption(
    "Understand the problem. "
    "Find the service. "
    "Take the next step."
)


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.info(
        "👋 **What do you need help with?**\n\n"
        "Describe your public-service need "
        "in your own words. NextStep AI will "
        "understand the request, identify the "
        "likely service, and guide you."
    )

    st.subheader(
        "✨ Try an example"
    )

    col1, col2 = st.columns(2)

    examples = [
        (
            "📄 Income certificate",
            "I want to apply for an income certificate.",
        ),
        (
            "📜 Birth certificate",
            "I need help getting a birth certificate.",
        ),
        (
            "🪪 Aadhaar",
            "I need help with an Aadhaar service.",
        ),
        (
            "🚗 Driving licence",
            "I want to apply for a driving licence.",
        ),
        (
            "🎓 Scholarship",
            "I want to find a government scholarship.",
        ),
        (
            "🛂 Passport",
            "I want to apply for a passport.",
        ),
    ]

    for index, (
        label,
        example_prompt,
    ) in enumerate(examples):

        target = (
            col1
            if index % 2 == 0
            else col2
        )

        with target:

            if st.button(
                label,
                use_container_width=True,
                key=f"example_{index}",
            ):

                st.session_state.pending_prompt = (
                    example_prompt
                )

                st.rerun()

    st.divider()

    st.subheader(
        "Why NextStep AI?"
    )

    a, b, c = st.columns(3)

    with a:

        st.info(
            "🧠 **Understand**\n\n"
            "Describe your need naturally."
        )

    with b:

        st.info(
            "🧭 **Guide**\n\n"
            "Get practical next steps."
        )

    with c:

        st.info(
            "🔗 **Connect**\n\n"
            "Open the relevant official source."
        )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    if message.get("role") == "user":

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            st.write(
                message.get(
                    "content",
                    "",
                )
            )

    elif message.get("role") == "assistant":

        with st.chat_message(
            "assistant",
            avatar="🤖",
        ):

            render_assistant_result(
                message
            )


# ============================================================
# VOICE INPUT
# ============================================================

st.markdown(
    "### 🎙️ Voice input"
)

st.caption(
    "Record your request, then send it to "
    "NextStep AI. Your voice is converted "
    "to text before the AI processes it."
)

voice = st.audio_input(
    "🎙️ Record a voice request",
    sample_rate=16000,
    key="voice_input",
)

if voice is not None:

    # --------------------------------------------------------
    # PLAYBACK
    # --------------------------------------------------------

    st.audio(
        voice,
        format="audio/wav",
    )

    st.success(
        "✅ Voice recording received."
    )

    # --------------------------------------------------------
    # SEND BUTTON
    # --------------------------------------------------------

    if st.button(
        "📝 Transcribe and send",
        use_container_width=True,
        key="transcribe_send",
    ):

        try:

            # ------------------------------------------------
            # TRANSCRIPTION
            # ------------------------------------------------

            with st.spinner(
                "🎙️ Converting your voice to text..."
            ):

                transcript = transcribe_audio(
                    voice
                )

            st.session_state.last_transcript = (
                transcript
            )

            st.success(
                "📝 Speech detected:"
            )

            st.write(
                f"**“{transcript}”**"
            )

            # ------------------------------------------------
            # AI PROCESSING
            # ------------------------------------------------

            process_user_message(
                transcript
            )

            # Clear the old recording widget
            # on the next render.
            st.session_state.voice_input = None

        except Exception as error:

            st.error(
                f"❌ {error}"
            )


# ============================================================
# TEXT CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Tell NextStep AI what you need..."
)

if prompt:

    process_user_message(
        prompt
    )

    st.rerun()


# ============================================================
# EXAMPLE BUTTON PROCESSING
# ============================================================

if st.session_state.pending_prompt:

    pending = (
        st.session_state.pending_prompt
    )

    st.session_state.pending_prompt = None

    process_user_message(
        pending
    )

    st.rerun()
