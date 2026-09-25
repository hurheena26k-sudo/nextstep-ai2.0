import streamlit as st
import json
import hashlib
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

@st.cache_resource
def create_client():

    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        return None

    return genai.Client(
        api_key=api_key
    )


client = create_client()


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "gemini-3.8-flash"


# ============================================================
# NEXTSTEP AI SYSTEM INSTRUCTION
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
   track, report, or use a government/public service.

9. General questions are NOT automatically service requests.

10. Greetings and casual conversation are NOT service requests.

11. Never invent government rules, fees, deadlines, eligibility
    requirements, documents, or websites.

12. If the exact procedure depends on location, ask for the
    relevant state, city, or country when necessary.

13. Use conversation history when answering follow-up questions.

14. Do not include URLs in your response.

15. If the request is outside public services, politely explain
    that your main purpose is helping with public services.

16. Keep answers practical and easy for ordinary citizens to follow.

17. Keep answers concise and avoid unnecessary information.

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

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 NextStep AI")

    st.caption(
        "Intelligent public-service guidance"
    )

    st.divider()

    if st.button(
        "＋ New Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.session_state.last_audio_hash = None

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

            short_message = message[:45]

            if len(message) > 45:
                short_message += "..."

            st.caption(
                f"{index + 1}. {short_message}"
            )

    st.divider()

    st.subheader("✨ Features")

    st.caption("🧠 Understands natural requests")
    st.caption("🧭 Finds the relevant service")
    st.caption("📋 Gives practical steps")
    st.caption("🔗 Shows official sources")
    st.caption("🎙️ Supports voice input")

    st.divider()

    st.caption(
        "NextStep AI • Public Service Assistant"
    )


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns(
    [5, 1]
)

with header_left:

    st.title("✦ NextStep AI")

    st.caption(
        "Tell me what you need. I'll guide you to your next step."
    )

with header_right:

    st.success("AI Ready")


st.divider()


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.info(
        "### 👋 Welcome to NextStep AI\n\n"
        "Describe what you need in your own words. "
        "You don't need to know the exact government service name."
    )

    st.subheader("🚀 Try a request")

    st.caption(
        "Choose a suggestion or type your own request below."
    )

    column1, column2 = st.columns(2)

    with column1:

        if st.button(
            "📄 Income Certificate",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to apply for an income certificate in Telangana."
            )

            st.rerun()

        if st.button(
            "📜 Birth Certificate",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to apply for a birth certificate in Telangana."
            )

            st.rerun()

        if st.button(
            "🚗 Driving Licence",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to apply for a driving licence in Telangana."
            )

            st.rerun()

    with column2:

        if st.button(
            "🪪 Aadhaar Help",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I need help with my Aadhaar service."
            )

            st.rerun()

        if st.button(
            "🎓 Government Scholarship",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to find a government scholarship."
            )

            st.rerun()

        if st.button(
            "🛂 Passport",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to apply for a passport."
            )

            st.rerun()

    st.divider()

    feature1, feature2, feature3 = st.columns(3)

    with feature1:

        st.info(
            "🧠 **Understand**\n\n"
            "Explain your problem naturally."
        )

    with feature2:

        st.info(
            "🧭 **Guide**\n\n"
            "Get clear next steps."
        )

    with feature3:

        st.info(
            "🔗 **Connect**\n\n"
            "Open an official source when needed."
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
                    f"Source: {service['label']}"
                )


# ============================================================
# CONVERSATION HISTORY
# ============================================================

def get_conversation_history():

    recent_messages = (
        st.session_state.messages[-10:]
    )

    history = []

    for message in recent_messages:

        role = (
            "Citizen"
            if message["role"] == "user"
            else "NextStep AI"
        )

        history.append(
            f"{role}: {message['content']}"
        )

    return "\n".join(history)


# ============================================================
# PARSE GEMINI JSON
# ============================================================

def parse_gemini_response(raw_text):

    text = raw_text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    data = json.loads(
        text
    )

    intent = data.get(
        "intent",
        "general"
    )

    service_key = data.get(
        "service_key"
    )

    response_text = data.get(
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

    if not response_text:

        response_text = (
            "Could you provide a little more information "
            "about what you need?"
        )

    return {
        "intent": intent,
        "service_key": service_key,
        "response": response_text
    }


# ============================================================
# TEXT GEMINI REQUEST
# ============================================================

def ask_gemini(user_message):

    if client is None:

        return {
            "intent": "error",
            "service_key": None,
            "response": (
                "The Gemini API key is missing from "
                "Streamlit Secrets."
            ),
            "error": (
                "GEMINI_API_KEY was not found."
            )
        }

    history = get_conversation_history()

    prompt = f"""
CONVERSATION HISTORY:

{history}

LATEST CITIZEN MESSAGE:

{user_message}

Understand the latest citizen message.

If it is a clear public-service request:
1. Identify the relevant service.
2. Give simple numbered steps.

If important information is missing:
Ask a useful clarification question.

If it is a general question:
Answer normally without attaching an official source.

Return ONLY valid JSON.

Required format:

{{
  "intent": "general" | "clarification" | "service_request",
  "service_key": "service key" | null,
  "response": "your response to the citizen"
}}
"""

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt,

            config=types.GenerateContentConfig(

                system_instruction=(
                    NEXTSTEP_SYSTEM_INSTRUCTION
                ),

                response_mime_type="application/json"
            )
        )

        return parse_gemini_response(
            response.text
        )

    except Exception as error:

        return {
            "intent": "error",
            "service_key": None,
            "response": (
                "Gemini could not process the request."
            ),
            "error": (
                f"{type(error).__name__}: {str(error)}"
            )
        }


# ============================================================
# VOICE GEMINI REQUEST
# ============================================================

def ask_gemini_voice(audio_file):

    if client is None:

        return {
            "intent": "error",
            "service_key": None,
            "response": (
                "The Gemini API key is missing from "
                "Streamlit Secrets."
            ),
            "error": (
                "GEMINI_API_KEY was not found."
            )
        }

    audio_bytes = audio_file.getvalue()

    if not audio_bytes:

        return {
            "intent": "error",
            "service_key": None,
            "response": "The voice recording was empty.",
            "error": "No audio bytes received."
        }

    mime_type = (
        audio_file.type
        or "audio/wav"
    )

    history = get_conversation_history()

    audio_part = types.Part.from_bytes(
        data=audio_bytes,
        mime_type=mime_type
    )

    prompt = f"""
The citizen has sent a voice message.

Listen to the voice message and understand what the citizen
is asking.

Do NOT return a transcription.

Respond directly as NextStep AI.

Previous conversation:

{history}

If the citizen clearly requests a public service:
- identify the relevant service
- provide simple numbered steps

If important information is missing:
- ask a clarification question

If it is a general question:
- answer normally

Return ONLY valid JSON:

{{
  "intent": "general" | "clarification" | "service_request",
  "service_key": "service key" | null,
  "response": "your response to the citizen"
}}
"""

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=[
                audio_part,
                prompt
            ],

            config=types.GenerateContentConfig(

                system_instruction=(
                    NEXTSTEP_SYSTEM_INSTRUCTION
                ),

                response_mime_type="application/json"
            )
        )

        return parse_gemini_response(
            response.text
        )

    except Exception as error:

        return {
            "intent": "error",
            "service_key": None,
            "response": (
                "Gemini could not process the voice request."
            ),
            "error": (
                f"{type(error).__name__}: {str(error)}"
            )
        }


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(result):

    if result["intent"] == "error":

        st.error(
            result["response"]
        )

        st.warning(
            "The technical error below is important. "
            "If Gemini is still not connecting, send me this exact error."
        )

        with st.expander(
            "🔧 Show technical error"
        ):

            st.code(
                result.get(
                    "error",
                    "Unknown error"
                )
            )

        return

    st.write(
        result["response"]
    )

    service_key = result.get(
        "service_key"
    )

    if (
        result["intent"] == "service_request"
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

            result = ask_gemini(
                user_message
            )

        display_result(
            result
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["response"],
            "intent": result["intent"],
            "service_key": result["service_key"]
        }
    )


# ============================================================
# PROCESS VOICE MESSAGE
# ============================================================

def process_voice_message(audio_file):

    if audio_file is None:
        return

    audio_bytes = audio_file.getvalue()

    if not audio_bytes:
        return

    audio_hash = hashlib.sha256(
        audio_bytes
    ).hexdigest()

    if (
        st.session_state.last_audio_hash
        == audio_hash
    ):

        return

    st.session_state.last_audio_hash = audio_hash

    with st.chat_message(
        "user",
        avatar="🎙️"
    ):

        st.write(
            "🎙️ Voice request"
        )

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner(
            "Listening and understanding..."
        ):

            result = ask_gemini_voice(
                audio_file
            )

        display_result(
            result
        )

    st.session_state.messages.append(
        {
            "role": "user",
            "content": "🎙️ Voice request"
        }
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["response"],
            "intent": result["intent"],
            "service_key": result["service_key"]
        }
    )


# ============================================================
# HANDLE SUGGESTED PROMPT
# ============================================================

if st.session_state.pending_prompt:

    prompt = st.session_state.pending_prompt

    st.session_state.pending_prompt = None

    process_text_message(
        prompt
    )


# ============================================================
# INPUT AREA
# ============================================================

st.divider()

st.subheader("💬 Ask NextStep AI")

st.caption(
    "Type your request or use the microphone."
)

text_column, voice_column, send_column = st.columns(
    [7, 2, 1]
)

with text_column:

    typed_message = st.text_input(
        "Message",
        placeholder="Tell me what you need help with...",
        label_visibility="collapsed",
        key="typed_message"
    )

with voice_column:

    voice_input = st.audio_input(
        "🎙️ Voice",
        label_visibility="collapsed",
        key="voice_input"
    )

with send_column:

    send_button = st.button(
        "➤",
        use_container_width=True
    )


# ============================================================
# SEND TEXT
# ============================================================

if send_button:

    if typed_message:

        process_text_message(
            typed_message
        )

        st.rerun()

    elif voice_input:

        process_voice_message(
            voice_input
        )

        st.rerun()

    else:

        st.warning(
            "Please type a message or record a voice request."
        )


# ============================================================
# AUTO PROCESS VOICE
# ============================================================

if voice_input and not send_button:

    process_voice_message(
        voice_input
    )

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "NextStep AI • Intelligent public-service guidance • Powered by Gemini"
)
