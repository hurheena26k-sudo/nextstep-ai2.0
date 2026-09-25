import streamlit as st
import json
import re
from google import genai


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

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ============================================================
# MODEL FALLBACK
# ============================================================

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash"
]


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

6. Give steps before discussing the official source.

7. Do not provide an official source for every normal question.

8. Only use a source when the user's request clearly corresponds
   to a specific government service.

9. Never invent government rules, fees, deadlines, eligibility
   requirements, documents, or websites.

10. If the exact procedure depends on location, ask for the
    relevant state, city, or country when necessary.

11. Use conversation history.

12. Greetings and casual conversation are NOT service requests.

13. If the citizen asks a general question such as:
    "What is an income certificate?"
    explain it normally and do not classify it as a service request
    unless they are actually asking to apply, obtain, download,
    renew, track, or use the service.

14. If the citizen's request is outside public services,
    politely explain that your main purpose is helping with
    public services.

15. Do not include URLs in your response.
    The application will provide the official source separately.

Your response MUST be valid JSON with exactly these fields:

{
  "intent": "general" | "clarification" | "service_request",
  "service_key": "service key" | null,
  "response": "your response to the citizen"
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

Use null when the request is general or clarification is required.

Response style:

- Friendly
- Clear
- Professional
- Simple
- Practical
- Do not overwhelm the citizen
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

if "processed_audio_id" not in st.session_state:
    st.session_state.processed_audio_id = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 NextStep AI")

    st.caption(
        "Your intelligent public-service assistant"
    )

    st.divider()

    if st.button(
        "＋ New Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.session_state.processed_audio_id = None

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

            short_message = message[:40]

            if len(message) > 40:
                short_message += "..."

            st.caption(
                f"{index + 1}. {short_message}"
            )

    st.divider()

    st.caption(
        "Guiding citizens toward their next step."
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title("✦ NextStep AI")

st.caption(
    "Intelligent guidance for public services"
)


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.info(
        "### How can I help you today?\n\n"
        "Tell me what you need in your own words. "
        "You don't need to know the exact government "
        "service name. I'll understand your request "
        "and guide you toward the next step."
    )

    st.subheader("✨ Suggested prompts")

    st.caption(
        "Click one to start a conversation."
    )

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
                "I want to find a government scholarship I may be eligible for."
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
            "🧠 **Understands your need**\n\n"
            "Describe your problem naturally. "
            "You don't need to know the exact service."
        )

    with info2:

        st.info(
            "🧭 **Guides your next step**\n\n"
            "Get simple, practical steps based on "
            "what you are trying to do."
        )

    with info3:

        st.info(
            "🔗 **Official sources**\n\n"
            "Clear service requests can receive "
            "a direct official source."
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

            st.write(
                message["content"]
            )

            service_key = message.get(
                "service_key"
            )

            if (
                message.get("intent")
                == "service_request"
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
# GEMINI RESPONSE FUNCTION
# ============================================================

def get_nextstep_response(user_message):

    conversation_text = ""

    for message in st.session_state.messages:

        if message["role"] == "user":

            conversation_text += (
                f"Citizen: {message['content']}\n"
            )

        elif message["role"] == "assistant":

            conversation_text += (
                f"NextStep AI: {message['content']}\n"
            )

    conversation_text += (
        f"Citizen: {user_message}\n"
    )

    prompt = f"""
{NEXTSTEP_SYSTEM_INSTRUCTION}

CONVERSATION HISTORY:

{conversation_text}

LATEST CITIZEN MESSAGE:

{user_message}

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add any explanation outside the JSON.
"""

    last_error = None

    for model_name in MODELS:

        try:

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            raw_text = response.text.strip()

            raw_text = re.sub(
                r"^```json\s*",
                "",
                raw_text,
                flags=re.IGNORECASE
            )

            raw_text = re.sub(
                r"\s*```$",
                "",
                raw_text
            )

            data = json.loads(
                raw_text
            )

            intent = data.get(
                "intent",
                "general"
            )

            service_key = data.get(
                "service_key"
            )

            answer = data.get(
                "response",
                ""
            )

            if intent not in [
                "general",
                "clarification",
                "service_request"
            ]:

                intent = "general"

            if service_key not in SERVICE_LINKS:

                service_key = None

            if intent != "service_request":

                service_key = None

            return {
                "intent": intent,
                "service_key": service_key,
                "response": answer
            }

        except Exception as error:

            last_error = error
            continue

    return {
        "intent": "error",
        "service_key": None,
        "response": (
            "I couldn't connect to the AI service right now. "
            "Please try again in a moment."
        ),
        "error": str(last_error)
    }


# ============================================================
# VOICE TRANSCRIPTION
# ============================================================

def transcribe_voice(audio_file):

    if audio_file is None:
        return None, None

    audio_bytes = audio_file.getvalue()

    if not audio_bytes:
        return None, "No audio was recorded."

    last_error = None

    for model_name in MODELS:

        try:

            response = client.models.generate_content(
                model=model_name,
                contents=[
                    {
                        "inline_data": {
                            "mime_type": "audio/wav",
                            "data": audio_bytes
                        }
                    },
                    """
                    Listen to this audio carefully.

                    Transcribe exactly what the citizen said.

                    Return ONLY the spoken text.

                    Do not answer the citizen.
                    Do not summarize.
                    Do not add explanations.

                    If the audio cannot be understood,
                    return AUDIO_UNCLEAR.
                    """
                ]
            )

            transcript = response.text.strip()

            if not transcript:
                return None, "I couldn't hear anything clearly."

            if transcript == "AUDIO_UNCLEAR":
                return None, (
                    "I couldn't understand the recording clearly. "
                    "Please try speaking again."
                )

            return transcript, None

        except Exception as error:

            last_error = error
            continue

    return None, (
        "I couldn't process the voice recording right now. "
        "Please try again."
    )


# ============================================================
# PROCESS MESSAGE
# ============================================================

def process_message(user_message):

    if not user_message:
        return

    user_message = user_message.strip()

    if not user_message:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.write(
            user_message
        )

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner(
            "NextStep AI is thinking..."
        ):

            result = get_nextstep_response(
                user_message
            )

        answer = result["response"]

        intent = result["intent"]

        service_key = result["service_key"]

        if intent == "error":

            st.error(
                answer
            )

            if "error" in result:

                with st.expander(
                    "Technical details"
                ):

                    st.code(
                        result["error"]
                    )

        else:

            st.write(
                answer
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

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "intent": intent,
            "service_key": service_key
        }
    )


# ============================================================
# HANDLE SUGGESTED PROMPT
# ============================================================

if st.session_state.pending_prompt:

    prompt = st.session_state.pending_prompt

    st.session_state.pending_prompt = None

    process_message(
        prompt
    )

    st.rerun()


# ============================================================
# INPUT AREA
# ============================================================

st.divider()

text_col, voice_col = st.columns(
    [8, 1],
    vertical_alignment="bottom"
)


# ============================================================
# TEXT INPUT
# ============================================================

with text_col:

    text_message = st.text_input(
        "Message",
        placeholder="Tell me what you need help with...",
        label_visibility="collapsed",
        key="text_message"
    )


# ============================================================
# VOICE INPUT
# ============================================================

with voice_col:

    audio_file = st.audio_input(
        "🎙️",
        key="voice_input",
        help="Record your request"
    )


# ============================================================
# TEXT MESSAGE
# ============================================================

if text_message:

    process_message(
        text_message
    )

    st.rerun()


# ============================================================
# VOICE MESSAGE
# ============================================================

if audio_file is not None:

    current_audio_id = hash(
        audio_file.getvalue()
    )

    if (
        st.session_state.processed_audio_id
        != current_audio_id
    ):

        st.session_state.processed_audio_id = (
            current_audio_id
        )

        with st.spinner(
            "🎙️ Understanding your voice..."
        ):

            transcript, voice_error = transcribe_voice(
                audio_file
            )

        if voice_error:

            st.warning(
                voice_error
            )

        elif transcript:

            process_message(
                transcript
            )

            st.rerun()
