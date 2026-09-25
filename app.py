import streamlit as st
import json
import re
import time
from google import genai
from google.genai import types


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
# GEMINI CLIENT
# ============================================================

client = None
client_error = None

try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
except Exception as error:
    client_error = str(error)


MODEL_NAME = "gemini-3.8-flash"


# ============================================================
# NEXTSTEP AI SYSTEM INSTRUCTION
# Kept concise to reduce token usage.
# ============================================================

NEXTSTEP_SYSTEM_INSTRUCTION = """
You are NextStep AI, an intelligent public-service assistant.

Your purpose is to help citizens understand and navigate public
services and applications.

You can help with:
- Birth certificates
- Death certificates
- Income certificates
- Caste certificates
- Residence certificates
- Government schemes
- Licenses and permits
- Public grievances
- Municipal services
- Education and scholarships
- Welfare services
- Passport services
- Aadhaar services
- Property tax
- Water connections
- Voter services
- Employment services
- Railway services
- Land services
- Other legitimate public services

BEHAVIOR:
1. First understand what the citizen needs.
2. Do not assume they know the service name.
3. Ask a simple clarification question when important information is missing.
4. For a clear service request, give practical numbered steps.
5. Only provide an official source when the user is actually requesting or completing a service.
6. Do not give a source for ordinary/general questions.
7. Never invent government rules, fees, deadlines, eligibility requirements,
   documents, or websites.
8. If location matters, ask for the relevant state/city/country.
9. Use the recent conversation context when useful.
10. Greetings and casual conversation are general questions.
11. Do not include URLs. The application provides official links separately.
12. Keep answers concise and practical.
13. Your job is to make the citizen's NEXT STEP obvious.

Return ONLY valid JSON with exactly these fields:

{
  "intent": "general" | "clarification" | "service_request",
  "service_key": "service key" | null,
  "title": "short helpful title",
  "summary": "short explanation",
  "steps": ["step 1", "step 2"],
  "documents": ["document 1"],
  "next_action": "one clear next action",
  "transcript": "what the citizen said"
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
other_government_service
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

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "voice_key" not in st.session_state:
    st.session_state.voice_key = 0

if "response_cache" not in st.session_state:
    st.session_state.response_cache = {}

if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0.0


# ============================================================
# SIMPLE STYLING
# No large HTML feature blocks.
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1100px;
        padding-top: 1.2rem;
        padding-bottom: 5rem;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid #e6eaf0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🤖 NextStep AI")

    st.caption(
        "Intelligent guidance for public services"
    )

    st.divider()

    if st.button(
        "＋ New Conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.session_state.response_cache = {}
        st.rerun()

    st.divider()

    st.subheader("💬 Conversations")

    user_messages = [
        message["content"]
        for message in st.session_state.messages
        if message["role"] == "user"
    ]

    if not user_messages:

        st.caption(
            "Your conversations will appear here."
        )

    else:

        for index, message in enumerate(
            user_messages[-8:]
        ):

            short_message = message[:42]

            if len(message) > 42:
                short_message += "..."

            st.caption(
                f"{index + 1}. {short_message}"
            )

    st.divider()

    st.info(
        "💡 **Tip**\n\n"
        "Type your request or use the microphone."
    )


# ============================================================
# BRANDING
# ============================================================

st.title("✦ NextStep AI")

st.caption(
    "Your intelligent guide to public services"
)


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.info(
        "### 👋 How can I help you today?\n\n"
        "Tell me what you need in your own words. "
        "You don't need to know the exact government service name."
    )

    st.subheader("✨ Try asking")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📄 Apply for an income certificate",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to apply for an income certificate in Telangana."
            )

            st.rerun()

        if st.button(
            "📜 I need a birth certificate",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to apply for a birth certificate in Telangana."
            )

            st.rerun()

        if st.button(
            "🚗 I want a driving licence",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to apply for a driving licence in Telangana."
            )

            st.rerun()

    with col2:

        if st.button(
            "🪪 I need help with Aadhaar",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I need help with my Aadhaar service."
            )

            st.rerun()

        if st.button(
            "🎓 Find a government scholarship",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to find a government scholarship."
            )

            st.rerun()

        if st.button(
            "🛂 I want to apply for a passport",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to apply for a passport."
            )

            st.rerun()

    st.divider()

    st.subheader("Why NextStep AI?")

    info1, info2, info3 = st.columns(3)

    with info1:
        st.info(
            "🧠 **Understand**\n\n"
            "Describe your problem naturally."
        )

    with info2:
        st.info(
            "🧭 **Guide**\n\n"
            "Get clear next steps."
        )

    with info3:
        st.info(
            "🔗 **Connect**\n\n"
            "Get an official source when needed."
        )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message(
            "user",
            avatar="👤"
        ):

            st.write(
                message["content"]
            )

    else:

        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            if message.get("intent") == "error":

                st.error(
                    message.get(
                        "summary",
                        "Something went wrong."
                    )
                )

                continue

            title = message.get(
                "title",
                "Here's your Next Step"
            )

            summary = message.get(
                "summary",
                message.get("content", "")
            )

            st.markdown(
                f"### ✨ {title}"
            )

            if summary:
                st.info(summary)

            steps = message.get(
                "steps",
                []
            )

            if steps:

                st.markdown(
                    "#### 🧭 Your next steps"
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

            next_action = message.get(
                "next_action",
                ""
            )

            if next_action:

                st.success(
                    f"➡️ **Next action:** {next_action}"
                )

            service_key = message.get(
                "service_key"
            )

            intent = message.get(
                "intent"
            )

            if (
                intent == "service_request"
                and service_key in SERVICE_LINKS
            ):

                service = SERVICE_LINKS[
                    service_key
                ]

                st.link_button(
                    f"🔗 Open Official {service['name']} Source",
                    service["url"],
                    use_container_width=True
                )

                st.caption(
                    f"Official source: {service['label']}"
                )


# ============================================================
# BUILD SHORT CONVERSATION CONTEXT
# ============================================================

def build_conversation():

    recent_messages = st.session_state.messages[-6:]

    conversation = []

    for message in recent_messages:

        if message["role"] == "user":

            conversation.append(
                f"Citizen: {message['content']}"
            )

        elif message["role"] == "assistant":

            summary = message.get(
                "summary",
                message.get("content", "")
            )

            if summary:

                conversation.append(
                    f"NextStep AI: {summary}"
                )

    return "\n".join(conversation)


# ============================================================
# CLEAN JSON
# ============================================================

def clean_json(text):

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


# ============================================================
# FORMAT RESULT
# ============================================================

def format_result(data):

    intent = data.get(
        "intent",
        "general"
    )

    if intent not in [
        "general",
        "clarification",
        "service_request"
    ]:

        intent = "general"

    service_key = data.get(
        "service_key"
    )

    if service_key not in SERVICE_LINKS:
        service_key = None

    if intent != "service_request":
        service_key = None

    title = data.get(
        "title",
        "Here's your Next Step"
    )

    summary = data.get(
        "summary",
        ""
    )

    steps = data.get(
        "steps",
        []
    )

    documents = data.get(
        "documents",
        []
    )

    next_action = data.get(
        "next_action",
        ""
    )

    if not isinstance(steps, list):
        steps = [str(steps)]

    if not isinstance(documents, list):
        documents = [str(documents)]

    return {
        "intent": intent,
        "service_key": service_key,
        "title": str(title),
        "summary": str(summary),
        "steps": [
            str(x) for x in steps
        ],
        "documents": [
            str(x) for x in documents
        ],
        "next_action": str(next_action),
        "transcript": str(
            data.get("transcript", "")
        ),
        "content": str(summary)
    }


# ============================================================
# ERROR RESULT
# ============================================================

def quota_error_result(error_text):

    return {
        "intent": "error",
        "service_key": None,
        "title": "Gemini is temporarily unavailable",
        "summary": (
            "NextStep AI reached Gemini, but the current "
            "Free Tier request limit has been reached."
        ),
        "steps": [
            "Wait for the Gemini quota to become available again.",
            "Avoid repeatedly submitting the same request.",
            "Try again after the limit resets."
        ],
        "documents": [],
        "next_action": (
            "Wait and try your request again later."
        ),
        "content": "",
        "error": error_text
    }


# ============================================================
# GENERAL ERROR RESULT
# ============================================================

def general_error_result(error_text):

    return {
        "intent": "error",
        "service_key": None,
        "title": "NextStep AI could not process that",
        "summary": (
            "There was a temporary problem while "
            "processing your request."
        ),
        "steps": [
            "Check that the Gemini API key is active.",
            "Try submitting the request once more."
        ],
        "documents": [],
        "next_action": "Try again in a moment.",
        "content": "",
        "error": error_text
    }


# ============================================================
# GEMINI TEXT RESPONSE
# ONE REQUEST ONLY
# ============================================================

def get_text_response(user_message):

    if client is None:

        return {
            "intent": "error",
            "service_key": None,
            "title": "Gemini connection problem",
            "summary": (
                "The Gemini client could not be initialized."
            ),
            "steps": [
                "Check the GEMINI_API_KEY in Streamlit Secrets."
            ],
            "documents": [],
            "next_action": "Check the API configuration.",
            "content": "",
            "error": client_error
        }

    cache_key = user_message.strip().lower()

    if cache_key in st.session_state.response_cache:

        return st.session_state.response_cache[
            cache_key
        ]

    current_time = time.time()

    elapsed = (
        current_time -
        st.session_state.last_request_time
    )

    if elapsed < 1.5:

        time.sleep(
            1.5 - elapsed
        )

    conversation = build_conversation()

    prompt = f"""
{NEXTSTEP_SYSTEM_INSTRUCTION}

RECENT CONVERSATION:
{conversation}

LATEST CITIZEN MESSAGE:
{user_message}

Return ONLY valid JSON.
"""

    try:

        st.session_state.last_request_time = time.time()

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        raw_text = response.text

        if not raw_text:

            raise Exception(
                "Gemini returned an empty response."
            )

        data = json.loads(
            clean_json(raw_text)
        )

        result = format_result(data)

        # Cache successful response.
        st.session_state.response_cache[
            cache_key
        ] = result

        return result

    except Exception as error:

        error_text = str(error)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "TooManyRequests" in error_text
        ):

            return quota_error_result(
                error_text
            )

        return general_error_result(
            error_text
        )


# ============================================================
# GEMINI VOICE RESPONSE
# ONE REQUEST ONLY
# ============================================================

def get_voice_response(audio_file):

    if client is None:

        return {
            "intent": "error",
            "service_key": None,
            "title": "Gemini connection problem",
            "summary": (
                "The Gemini client could not be initialized."
            ),
            "steps": [],
            "documents": [],
            "next_action": "",
            "content": "",
            "error": client_error,
            "transcript": ""
        }

    audio_bytes = audio_file.getvalue()

    if not audio_bytes:

        return {
            "intent": "error",
            "service_key": None,
            "title": "No recording detected",
            "summary": (
                "The microphone recording was empty."
            ),
            "steps": [
                "Tap the microphone.",
                "Record a short request.",
                "Submit it again."
            ],
            "documents": [],
            "next_action": "Record your request again.",
            "content": "",
            "error": "Empty audio recording.",
            "transcript": ""
        }

    mime_type = (
        audio_file.type
        or "audio/wav"
    )

    conversation = build_conversation()

    prompt = f"""
{NEXTSTEP_SYSTEM_INSTRUCTION}

The citizen is speaking through a microphone.

Understand what the citizen said and answer the request.

RECENT CONVERSATION:
{conversation}

The transcript field must contain what you understood
from the citizen's speech.

Return ONLY valid JSON.
"""

    try:

        current_time = time.time()

        elapsed = (
            current_time -
            st.session_state.last_request_time
        )

        if elapsed < 1.5:

            time.sleep(
                1.5 - elapsed
            )

        st.session_state.last_request_time = time.time()

        audio_part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type=mime_type
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                prompt,
                audio_part
            ]
        )

        raw_text = response.text

        if not raw_text:

            raise Exception(
                "Gemini returned an empty voice response."
            )

        data = json.loads(
            clean_json(raw_text)
        )

        result = format_result(data)

        if not result["transcript"]:

            result["transcript"] = (
                "Voice request received."
            )

        return result

    except Exception as error:

        error_text = str(error)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "TooManyRequests" in error_text
        ):

            result = quota_error_result(
                error_text
            )

            result["title"] = (
                "Voice is temporarily unavailable"
            )

            result["summary"] = (
                "The microphone is working, but "
                "Gemini's current Free Tier quota "
                "is unavailable."
            )

            result["transcript"] = ""

            return result

        result = general_error_result(
            error_text
        )

        result["title"] = (
            "Voice request could not be processed"
        )

        result["summary"] = (
            "Your recording was received, but "
            "Gemini could not process it."
        )

        result["transcript"] = ""

        return result


# ============================================================
# DISPLAY RESPONSE
# ============================================================

def display_response(result):

    if result["intent"] == "error":

        st.error(
            result.get(
                "summary",
                "Something went wrong."
            )
        )

        steps = result.get(
            "steps",
            []
        )

        if steps:

            st.markdown(
                "#### 🛠️ What you can do"
            )

            for index, step in enumerate(
                steps,
                start=1
            ):

                st.markdown(
                    f"**{index}.** {step}"
                )

        next_action = result.get(
            "next_action",
            ""
        )

        if next_action:

            st.warning(
                f"➡️ **Next action:** {next_action}"
            )

        with st.expander(
            "Technical details"
        ):

            st.code(
                result.get(
                    "error",
                    "Unknown error"
                )
            )

        return

    st.markdown(
        f"### ✨ {result.get('title', 'Here’s your Next Step')}"
    )

    summary = result.get(
        "summary",
        ""
    )

    if summary:
        st.info(summary)

    steps = result.get(
        "steps",
        []
    )

    if steps:

        st.markdown(
            "#### 🧭 Your next steps"
        )

        for index, step in enumerate(
            steps,
            start=1
        ):

            st.markdown(
                f"**{index}.** {step}"
            )

    documents = result.get(
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

    next_action = result.get(
        "next_action",
        ""
    )

    if next_action:

        st.success(
            f"➡️ **Next action:** {next_action}"
        )

    service_key = result.get(
        "service_key"
    )

    intent = result.get(
        "intent"
    )

    if (
        intent == "service_request"
        and service_key in SERVICE_LINKS
    ):

        service = SERVICE_LINKS[
            service_key
        ]

        st.link_button(
            f"🔗 Open Official {service['name']} Source",
            service["url"],
            use_container_width=True
        )

        st.caption(
            f"Official source: {service['label']}"
        )


# ============================================================
# SAVE RESPONSE
# ============================================================

def save_response(result):

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result.get(
                "summary",
                ""
            ),
            "intent": result.get(
                "intent"
            ),
            "service_key": result.get(
                "service_key"
            ),
            "title": result.get(
                "title",
                ""
            ),
            "summary": result.get(
                "summary",
                ""
            ),
            "steps": result.get(
                "steps",
                []
            ),
            "documents": result.get(
                "documents",
                []
            ),
            "next_action": result.get(
                "next_action",
                ""
            )
        }
    )


# ============================================================
# PROCESS TEXT MESSAGE
# ============================================================

def process_text_message(user_message):

    user_message = user_message.strip()

    if not user_message:
        return None

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    result = get_text_response(
        user_message
    )

    save_response(
        result
    )

    return result


# ============================================================
# PROCESS VOICE MESSAGE
# ============================================================

def process_voice_message(audio_file):

    result = get_voice_response(
        audio_file
    )

    transcript = result.get(
        "transcript",
        ""
    )

    if not transcript:

        transcript = "🎙️ Voice request"

    else:

        transcript = f"🎙️ {transcript}"

    st.session_state.messages.append(
        {
            "role": "user",
            "content": transcript
        }
    )

    save_response(
        result
    )

    return result


# ============================================================
# HANDLE SUGGESTED PROMPT
# ============================================================

if st.session_state.pending_prompt:

    prompt = st.session_state.pending_prompt

    st.session_state.pending_prompt = None

    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.write(prompt)

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner(
            "✨ NextStep AI is thinking..."
        ):

            result = get_text_response(
                prompt
            )

        display_response(
            result
        )

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    save_response(
        result
    )

    st.rerun()


# ============================================================
# INPUT AREA
# Using a FORM prevents accidental requests during reruns.
# ============================================================

st.divider()

st.markdown(
    "#### 💬 Ask NextStep AI"
)

with st.form(
    "nextstep_input_form",
    clear_on_submit=True
):

    input_col, voice_col, send_col = st.columns(
        [7, 2, 1],
        vertical_alignment="bottom"
    )

    with input_col:

        typed_message = st.text_input(
            "Search",
            placeholder="Tell me what you need help with...",
            label_visibility="collapsed"
        )

    with voice_col:

        audio_input = st.audio_input(
            "🎙️",
            sample_rate=16000,
            help="Record your request",
            label_visibility="collapsed"
        )

    with send_col:

        submitted = st.form_submit_button(
            "➤",
            use_container_width=True
        )


# ============================================================
# SUBMIT TEXT / VOICE
# ============================================================

if submitted:

    if typed_message and typed_message.strip():

        message_to_send = typed_message.strip()

        with st.spinner(
            "✨ NextStep AI is thinking..."
        ):

            result = process_text_message(
                message_to_send
            )

        with st.chat_message(
            "user",
            avatar="👤"
        ):

            st.write(
                message_to_send
            )

        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            display_response(
                result
            )

        st.rerun()

    elif audio_input is not None:

        with st.spinner(
            "🎙️ Listening and understanding..."
        ):

            result = process_voice_message(
                audio_input
            )

        with st.chat_message(
            "user",
            avatar="👤"
        ):

            st.write(
                f"🎙️ {result.get('transcript', 'Voice request')}"
            )

        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            display_response(
                result
            )

        st.session_state.voice_key += 1

        st.rerun()

    else:

        st.warning(
            "Please type a request or record a voice message."
        )
