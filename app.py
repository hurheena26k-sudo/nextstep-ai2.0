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

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

OPENROUTER_TRANSCRIPTION_URL = (
    "https://openrouter.ai/api/v1/audio/transcriptions"
)

MODEL_NAME = "openrouter/free"

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

3. If a necessary detail is missing, ask one clear clarification
question.

4. Give practical steps when the request is clear.

5. Do not invent government rules, fees, eligibility criteria,
deadlines, documents, or URLs.

6. Procedures can vary by state, UT, city, or department.
Ask for location when it materially matters.

7. This assistant covers services across India, not only one state.

8. Greetings and general questions are not service requests.

9. Do not include URLs in your answer.
The application adds official links separately.

10. Keep the response concise and citizen-friendly.

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

def openrouter_headers(api_key: str):

    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nextstep-ai.streamlit.app",
        "X-Title": "NextStep AI",
    }


# ============================================================
# JSON CLEANER
# ============================================================

def clean_json(text: str):

    text = (text or "").strip()

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
):

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

        "content": str(
            data.get("summary")
            or ""
        ),
    }


# ============================================================
# CONVERSATION FOR AI
# ============================================================

def conversation_for_ai():

    history = []

    for message in st.session_state.messages:

        role = message.get("role")

        if role == "user":

            history.append({
                "role": "user",
                "content": message.get(
                    "content",
                    "",
                ),
            })

        elif role == "assistant":

            history.append({
                "role": "assistant",
                "content": message.get(
                    "content",
                    "",
                ),
            })

    return history


# ============================================================
# OPENROUTER CHAT
# ============================================================

def call_openrouter(user_message: str):

    api_key = get_api_key()

    if not api_key:

        return {

            "intent": "error",

            "service_key": None,

            "title": "OpenRouter key not found",

            "summary": (
                "Add OPENROUTER_API_KEY to "
                "Streamlit Secrets before using "
                "NextStep AI."
            ),

            "steps": [
                "Open your Streamlit app settings.",
                "Add OPENROUTER_API_KEY in Secrets.",
                "Save and restart the app.",
            ],

            "documents": [],

            "next_action": (
                "Add the OpenRouter API key "
                "to Streamlit Secrets."
            ),

            "content": "",

            "transcript": "",
        }


    messages = [

        {
            "role": "system",
            "content": SYSTEM_INSTRUCTION,
        }

    ]

    messages.extend(
        conversation_for_ai()
    )

    messages.append({
        "role": "user",
        "content": user_message,
    })


    payload = {

        "model": MODEL_NAME,

        "messages": messages,

        "temperature": 0.2,
    }


    try:

        response = requests.post(

            OPENROUTER_URL,

            headers=openrouter_headers(
                api_key
            ),

            json=payload,

            timeout=60,
        )


        if response.status_code == 429:

            return {

                "intent": "error",

                "service_key": None,

                "title": "AI rate limit reached",

                "summary": (
                    "OpenRouter temporarily "
                    "limited this request."
                ),

                "steps": [
                    "Wait a short moment.",
                    "Try the same request again.",
                ],

                "documents": [],

                "next_action": (
                    "Try again in a moment."
                ),

                "content": "",

                "transcript": "",
            }


        if response.status_code >= 400:

            try:

                error_data = response.json()

                message = (
                    error_data
                    .get("error", {})
                    .get(
                        "message",
                        response.text,
                    )
                )

            except Exception:

                message = response.text


            return {

                "intent": "error",

                "service_key": None,

                "title": "AI request failed",

                "summary": (
                    "OpenRouter returned an error: "
                    f"{message}"
                ),

                "steps": [
                    "Check your OpenRouter key.",
                    "Check model availability.",
                    "Try again.",
                ],

                "documents": [],

                "next_action": (
                    "Check the OpenRouter connection."
                ),

                "content": "",

                "transcript": "",
            }


        data = response.json()

        choices = data.get(
            "choices"
        ) or []


        if not choices:

            raise ValueError(
                "OpenRouter returned no choices."
            )


        raw_content = (

            choices[0]
            .get("message", {})
            .get("content", "")
        )


        if isinstance(
            raw_content,
            list,
        ):

            raw_content = "".join(

                item.get("text", "")
                if isinstance(item, dict)
                else str(item)

                for item in raw_content
            )


        parsed = json.loads(
            clean_json(
                str(raw_content)
            )
        )


        return normalize_result(
            parsed
        )


    except requests.RequestException:

        return {

            "intent": "error",

            "service_key": None,

            "title": "Connection problem",

            "summary": (
                "NextStep AI could not "
                "reach OpenRouter right now."
            ),

            "steps": [
                "Check your internet connection.",
                "Try again in a moment.",
            ],

            "documents": [],

            "next_action": (
                "Try the request again."
            ),

            "content": "",

            "transcript": "",
        }


    except (
        ValueError,
        json.JSONDecodeError,
    ):

        return {

            "intent": "error",

            "service_key": None,

            "title": "Unexpected AI response",

            "summary": (
                "The AI returned a response "
                "that NextStep AI could not "
                "safely format."
            ),

            "steps": [
                "Try the request again."
            ],

            "documents": [],

            "next_action": (
                "Try again with the same request."
            ),

            "content": "",

            "transcript": "",
        }


    except Exception:

        return {

            "intent": "error",

            "service_key": None,

            "title": "Something went wrong",

            "summary": (
                "NextStep AI encountered "
                "an unexpected problem."
            ),

            "steps": [
                "Try the request again."
            ],

            "documents": [],

            "next_action": (
                "Try again in a moment."
            ),

            "content": "",

            "transcript": "",
        }


# ============================================================
# SPEECH TO TEXT
# ============================================================

def transcribe_audio(audio_file):

    api_key = get_api_key()

    if not api_key:

        raise RuntimeError(
            "OPENROUTER_API_KEY is missing "
            "from Streamlit Secrets."
        )


    audio_bytes = audio_file.getvalue()

    if not audio_bytes:

        raise ValueError(
            "The recorded audio is empty."
        )


    audio_b64 = base64.b64encode(
        audio_bytes
    ).decode("utf-8")


    payload = {

        "model": TRANSCRIPTION_MODEL,

        "input_audio": {

            "data": audio_b64,

            "format": "wav",
        },
    }


    if (
        st.session_state.voice_language
        != "Auto"
    ):

        payload["language"] = (
            st.session_state.voice_language
        )


    response = requests.post(

        OPENROUTER_TRANSCRIPTION_URL,

        headers=openrouter_headers(
            api_key
        ),

        json=payload,

        timeout=60,
    )


    if response.status_code >= 400:

        try:

            error_data = response.json()

            message = (
                error_data
                .get("error", {})
                .get(
                    "message",
                    response.text,
                )
            )

        except Exception:

            message = response.text


        raise RuntimeError(
            f"Speech transcription failed: "
            f"{message}"
        )


    data = response.json()

    transcript = str(
        data.get("text") or ""
    ).strip()


    if not transcript:

        raise ValueError(
            "No speech was detected."
        )


    return transcript


# ============================================================
# RENDER ASSISTANT RESPONSE
# ============================================================

def render_assistant_result(result):

    title = result.get(
        "title"
    ) or "Your Next Step"

    summary = result.get(
        "summary"
    ) or ""

    intent = result.get(
        "intent"
    )


    st.subheader(
        f"✨ {title}"
    )


    if summary:

        st.info(
            summary
        )


    transcript = result.get(
        "transcript"
    )

    if transcript:

        with st.expander(
            "🎙️ Voice transcript"
        ):

            st.write(
                transcript
            )


    steps = result.get(
        "steps"
    ) or []


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


    documents = result.get(
        "documents"
    ) or []


    if documents:

        st.markdown(
            "#### 📋 Documents to check"
        )


        for document in documents:

            st.write(
                f"• {document}"
            )


    next_action = result.get(
        "next_action"
    ) or ""


    if next_action:

        st.success(
            f"➡️ **Next action:** "
            f"{next_action}"
        )


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
# PROCESS MESSAGE
# ============================================================

def process_user_message(text):

    text = text.strip()

    if not text:
        return


    if not st.session_state.messages:

        st.session_state.conversation_title = (
            text[:45]
        )


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

    st.title(
        "🤖 NextStep AI"
    )

    st.caption(
        "India-wide public-service guidance"
    )


    st.divider()


    if st.button(
        "＋ New conversation",
        use_container_width=True,
    ):

        new_conversation()

        st.rerun()


    st.divider()


    st.subheader(
        "💬 Current conversation"
    )


    st.caption(
        st.session_state.conversation_title
    )


    user_messages = [

        message["content"]

        for message in st.session_state.messages

        if message.get("role") == "user"
    ]


    if user_messages:

        for index, message in enumerate(

            user_messages[-8:],
            start=1,
        ):

            preview = (
                message
                .replace("\n", " ")
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


    st.subheader(
        "🎙️ Voice"
    )


    st.session_state.voice_language = (
        st.selectbox(

            "Speech language",

            [
                "Auto",
                "en",
                "hi",
                "te",
            ],

            format_func=lambda x: {

                "Auto": "Auto detect",

                "en": "English",

                "hi": "Hindi",

                "te": "Telugu",

            }[x],
        )
    )


    st.divider()


    st.info(

        "💡 You can describe the problem "
        "in normal language. You do not "
        "need to know the exact department."
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
        "help identify the likely service "
        "and next steps."
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
    "Record your request. "
    "NextStep AI will convert the speech "
    "to text and process it."
)


voice = st.audio_input(

    "Record a voice request",

    sample_rate=16000,

    key="voice_input",
)


if voice is not None:

    st.audio(
        voice
    )


    if st.button(

        "📝 Transcribe and send",

        use_container_width=True,

        key="transcribe_send",
    ):

        try:

            with st.spinner(
                "Transcribing your voice..."
            ):

                transcript = (
                    transcribe_audio(
                        voice
                    )
                )


            st.session_state.last_transcript = (
                transcript
            )


            process_user_message(
                transcript
            )


            st.rerun()


        except Exception as error:

            st.error(
                str(error)
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
