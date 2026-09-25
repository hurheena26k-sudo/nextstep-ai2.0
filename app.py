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

try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
except Exception as error:
    client = None
    client_error = str(error)


MODEL_NAME = "gemini-3.8-flash"


# ============================================================
# NEXTSTEP AI INSTRUCTION
# ============================================================

NEXTSTEP_SYSTEM_INSTRUCTION = """
You are NextStep AI, an intelligent public-service assistant.

Your purpose is to help citizens understand and navigate public
services and applications.

You can help with many types of public services, including:

- Birth certificates
- Death certificates
- Income certificates
- Caste certificates
- Residence certificates
- Government schemes
- Licenses and permits
- Public grievances
- Municipal services
- Education-related government services
- Welfare services
- Passport services
- Aadhaar-related services
- Property tax
- Water connections
- Voter services
- Employment services
- Railway services
- Land services
- Other legitimate public-service requests

IMPORTANT BEHAVIOR:

1. First understand what the citizen needs.

2. Do not assume that the citizen already knows the exact
   government service.

3. If the citizen describes a problem indirectly, identify
   the possible service they may need.

4. If important information is missing, ask a simple clarification
   question.

5. When the request is clear enough to identify a service,
   provide practical numbered steps.

6. Give the steps before discussing the official source.

7. Do not provide an official source for every normal question.

8. Only classify something as a service_request when the citizen
   is actually trying to apply for, obtain, renew, download,
   track, use, or complete a government service.

9. General questions should remain general questions.

10. Never invent government rules, fees, deadlines, eligibility
    requirements, documents, or websites.

11. If the exact procedure depends on location, ask for the
    relevant state, city, or country when necessary.

12. Use conversation history.

13. Greetings and casual conversation are NOT service requests.

14. If the citizen asks something such as:
    "What is an income certificate?"
    explain it normally.

15. If the citizen's request is outside public services,
    politely explain that your main purpose is helping with
    public services.

16. Do not include URLs in your response.
    The application will provide official sources separately.

17. Keep answers useful and concise.

ANSWER FORMAT:

Return ONLY valid JSON.

Use exactly these fields:

{
  "intent": "general" | "clarification" | "service_request",
  "service_key": "service key" | null,
  "title": "short helpful title",
  "summary": "short explanation",
  "steps": ["step 1", "step 2", "step 3"],
  "documents": ["document 1", "document 2"],
  "next_action": "one clear next action",
  "transcript": "what the citizen said"
}

For general questions:
- steps may be an empty list
- documents may be an empty list
- next_action may be a short suggestion

For clarification:
- ask the most useful missing question
- do not invent steps

For service requests:
- provide practical numbered steps
- include documents only when reasonably appropriate
- identify the correct service_key

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

Use null when the request is general or clarification is required.

STYLE:

- Friendly
- Professional
- Clear
- Simple
- Practical
- Citizen-friendly
- Avoid unnecessary long paragraphs
- Make the next step obvious
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


# ============================================================
# SIMPLE NATIVE STYLING
# No HTML blocks are used.
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

    .answer-title {
        font-size: 24px;
        font-weight: 700;
    }

    .small-muted {
        color: #6b7280;
        font-size: 14px;
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
        "You can type your request or use the microphone."
    )


# ============================================================
# TOP BRANDING
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
            "Get clear next steps instead of confusing information."
        )

    with info3:
        st.info(
            "🔗 **Connect**\n\n"
            "Get an official source when a specific service is identified."
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
# BUILD CONVERSATION HISTORY
# ============================================================

def build_conversation():

    conversation = []

    for message in st.session_state.messages:

        if message["role"] == "user":

            conversation.append(
                f"Citizen: {message['content']}"
            )

        elif message["role"] == "assistant":

            conversation.append(
                f"NextStep AI: {message.get('content', '')}"
            )

    return "\n".join(conversation)


# ============================================================
# CLEAN JSON RESPONSE
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
# FORMAT GEMINI RESULT
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
        data.get("response", "")
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
        "steps": [str(x) for x in steps],
        "documents": [str(x) for x in documents],
        "next_action": str(next_action),
        "transcript": str(
            data.get("transcript", "")
        ),
        "content": str(summary)
    }


# ============================================================
# GEMINI TEXT RESPONSE
# ============================================================

def get_text_response(user_message):

    if client is None:

        return {
            "intent": "error",
            "service_key": None,
            "title": "Connection problem",
            "summary": (
                "The Gemini client could not be initialized."
            ),
            "steps": [],
            "documents": [],
            "next_action": "",
            "content": "",
            "error": client_error
        }

    conversation = build_conversation()

    prompt = f"""
{NEXTSTEP_SYSTEM_INSTRUCTION}

CONVERSATION HISTORY:

{conversation}

LATEST CITIZEN MESSAGE:

{user_message}

Return ONLY valid JSON.
"""

    try:

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

        return format_result(data)

    except Exception as error:

        error_text = str(error)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

            return {
                "intent": "error",
                "service_key": None,
                "title": "Gemini quota is temporarily unavailable",
                "summary": (
                    "NextStep AI is connected to Gemini, "
                    "but the project's current Gemini quota has been exhausted."
                ),
                "steps": [
                    "Check the Gemini project quota in Google AI Studio.",
                    "Wait for the quota to reset or use a project with available quota.",
                    "Then try your request again."
                ],
                "documents": [],
                "next_action": (
                    "Check your Gemini API project's usage and rate limits."
                ),
                "content": "",
                "error": error_text
            }

        return {
            "intent": "error",
            "service_key": None,
            "title": "Gemini could not process the request",
            "summary": (
                "There was a temporary problem while processing "
                "your request."
            ),
            "steps": [
                "Check that your Gemini API key is active.",
                "Try the request again."
            ],
            "documents": [],
            "next_action": "Try again in a moment.",
            "content": "",
            "error": error_text
        }


# ============================================================
# GEMINI VOICE RESPONSE
# ============================================================

def get_voice_response(audio_file):

    if client is None:

        return {
            "intent": "error",
            "service_key": None,
            "title": "Connection problem",
            "summary": (
                "The Gemini client could not be initialized."
            ),
            "steps": [],
            "documents": [],
            "next_action": "",
            "content": "",
            "error": client_error
        }

    conversation = build_conversation()

    audio_bytes = audio_file.getvalue()

    mime_type = (
        audio_file.type
        or "audio/wav"
    )

    prompt = f"""
{NEXTSTEP_SYSTEM_INSTRUCTION}

The citizen is speaking through a microphone.

First understand and transcribe what the citizen said.
Then answer their request.

CONVERSATION HISTORY:

{conversation}

IMPORTANT:

Return ONLY valid JSON.

The "transcript" field must contain the text you understood
from the citizen's audio.

The "summary", "steps", "documents", and "next_action" fields
should answer the citizen's actual request.

Do not include markdown code fences.
"""

    try:

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

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

            return {
                "intent": "error",
                "service_key": None,
                "title": "Voice is temporarily unavailable",
                "summary": (
                    "The microphone is working, but Gemini's "
                    "current project quota is exhausted."
                ),
                "steps": [
                    "Check your Gemini project quota in Google AI Studio.",
                    "Wait for the quota to reset or use a project with available quota.",
                    "Then try the microphone again."
                ],
                "documents": [],
                "next_action": (
                    "Check the Gemini API project's usage and rate limits."
                ),
                "content": "",
                "error": error_text
            }

        return {
            "intent": "error",
            "service_key": None,
            "title": "Voice request could not be processed",
            "summary": (
                "Your microphone recording was received, "
                "but Gemini could not process it."
            ),
            "steps": [
                "Try speaking clearly for a short sentence.",
                "Try the microphone again."
            ],
            "documents": [],
            "next_action": "Record your request again.",
            "content": "",
            "error": error_text
        }


# ============================================================
# DISPLAY ASSISTANT RESPONSE
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

    title = result.get(
        "title",
        "Here's your Next Step"
    )

    summary = result.get(
        "summary",
        ""
    )

    st.markdown(
        f"### ✨ {title}"
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
# PROCESS TEXT MESSAGE
# ============================================================

def process_text_message(user_message):

    user_message = user_message.strip()

    if not user_message:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    result = get_text_response(
        user_message
    )

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
# PROCESS VOICE MESSAGE
# ============================================================

def process_voice_message(audio_file):

    result = get_voice_response(
        audio_file
    )

    transcript = result.get(
        "transcript",
        "Voice request"
    )

    if not transcript:
        transcript = "Voice request"

    st.session_state.messages.append(
        {
            "role": "user",
            "content": f"🎙️ {transcript}"
        }
    )

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

        display_response(result)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

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

    st.rerun()


# ============================================================
# INPUT AREA
# ============================================================

st.divider()

st.markdown(
    "#### 💬 Ask NextStep AI"
)

input_col, voice_col = st.columns(
    [8, 2],
    vertical_alignment="bottom"
)

with input_col:

    typed_message = st.text_input(
        "Search",
        placeholder="Tell me what you need help with...",
        label_visibility="collapsed",
        key="text_message"
    )

with voice_col:

    audio_input = st.audio_input(
        "🎙️",
        sample_rate=16000,
        key=f"voice_input_{st.session_state.voice_key}",
        help="Tap to record your request",
        label_visibility="collapsed"
    )


# ============================================================
# TEXT SUBMISSION
# ============================================================

if typed_message:

    message_to_send = typed_message.strip()

    if message_to_send:

        st.session_state.text_message = ""

        with st.spinner(
            "✨ NextStep AI is thinking..."
        ):

            process_text_message(
                message_to_send
            )

        st.rerun()


# ============================================================
# VOICE SUBMISSION
# ============================================================

if audio_input is not None:

    with st.spinner(
        "🎙️ Listening and understanding..."
    ):

        process_voice_message(
            audio_input
        )

    # Change widget key so the same recording
    # is not processed repeatedly.
    st.session_state.voice_key += 1

    st.rerun()
