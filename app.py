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
def get_gemini_client():
    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )


client = get_gemini_client()


# ============================================================
# FAST MODEL FALLBACK
# ============================================================

PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.7-flash"


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

13. Use the conversation history to understand follow-up questions.

14. Do not include URLs in your response.
    The application provides official sources separately.

15. If the request is outside public services, politely explain
    that your main purpose is helping with public services.

16. Keep answers practical and easy for ordinary citizens to follow.

17. Do not overwhelm the citizen with unnecessary information.

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
- Concise
- Helpful
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

if "processed_audio_hash" not in st.session_state:
    st.session_state.processed_audio_hash = None


# ============================================================
# NATIVE STREAMLIT VISUAL DESIGN
# NO HTML
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f9fc;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e7ebf2;
        padding: 12px;
        border-radius: 12px;
    }

    .stButton > button {
        border-radius: 12px;
        min-height: 42px;
        font-weight: 600;
    }

    .stLinkButton > a {
        border-radius: 12px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 NextStep AI")

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
        st.session_state.processed_audio_hash = None

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
            "No conversations yet."
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

    st.subheader("✨ What I can do")

    st.caption("🧠 Understand natural language")
    st.caption("🧭 Identify the right service")
    st.caption("📋 Explain the next steps")
    st.caption("🔗 Provide official sources")
    st.caption("🎙️ Accept voice requests")

    st.divider()

    st.caption(
        "NextStep AI • Public Service Assistant"
    )


# ============================================================
# HEADER
# ============================================================

top_left, top_right = st.columns(
    [5, 1]
)

with top_left:

    st.title("✦ NextStep AI")

    st.caption(
        "Tell me what you need. I'll help you find your next step."
    )

with top_right:

    st.metric(
        "AI Assistant",
        "Online"
    )


st.divider()


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.info(
        "### 👋 Welcome to NextStep AI\n\n"
        "Describe what you need in your own words. "
        "You don't need to know the exact government service name. "
        "I can understand your request, ask for missing information, "
        "and guide you through the next step."
    )

    st.subheader("🚀 Try asking")

    st.caption(
        "Select a suggestion or type your own request below."
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
            "📜 Get a birth certificate",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to apply for a birth certificate in Telangana."
            )

            st.rerun()

        if st.button(
            "🚗 Apply for a driving licence",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to apply for a driving licence in Telangana."
            )

            st.rerun()

    with col2:

        if st.button(
            "🪪 Help with Aadhaar",
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
            "🛂 Apply for a passport",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "I want to apply for a passport."
            )

            st.rerun()

    st.divider()

    st.subheader("Why NextStep AI?")

    feature1, feature2, feature3 = st.columns(3)

    with feature1:

        st.info(
            "🧠 **Understand**\n\n"
            "Describe your problem naturally."
        )

    with feature2:

        st.info(
            "🧭 **Guide**\n\n"
            "Get clear steps toward your next action."
        )

    with feature3:

        st.info(
            "🔗 **Connect**\n\n"
            "Access official sources for clear service requests."
        )


# ============================================================
# CHAT HISTORY
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
                message.get("intent") == "service_request"
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
# BUILD CONVERSATION CONTEXT
# ============================================================

def build_conversation_context():

    recent_messages = st.session_state.messages[-12:]

    conversation = []

    for message in recent_messages:

        role = (
            "Citizen"
            if message["role"] == "user"
            else "NextStep AI"
        )

        conversation.append(
            f"{role}: {message['content']}"
        )

    return "\n".join(conversation)


# ============================================================
# CLEAN GEMINI JSON
# ============================================================

def clean_json_response(raw_text):

    text = raw_text.strip()

    if text.startswith("```json"):

        text = text[7:]

    elif text.startswith("```"):

        text = text[3:]

    if text.endswith("```"):

        text = text[:-3]

    text = text.strip()

    return json.loads(text)


# ============================================================
# NORMALIZE AI RESULT
# ============================================================

def normalize_result(data):

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

    if not answer:

        answer = (
            "I need a little more information to help you "
            "with that request."
        )

    return {
        "intent": intent,
        "service_key": service_key,
        "response": answer
    }


# ============================================================
# GEMINI TEXT REQUEST
# ============================================================

def get_text_response(user_message):

    conversation = build_conversation_context()

    prompt = f"""
CONVERSATION HISTORY:

{conversation}

LATEST CITIZEN MESSAGE:

{user_message}

Understand the citizen's latest message using the conversation
history.

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add explanation outside the JSON.

Remember:
- Give practical steps when the service is clear.
- Ask a clarification question when important information is missing.
- Do not provide a source for general questions.
- Only use service_request when the citizen is actually requesting
  a public service.
"""

    return call_gemini(
        contents=prompt
    )


# ============================================================
# GEMINI VOICE REQUEST
# ONE CALL FOR AUDIO + UNDERSTANDING
# ============================================================

def get_voice_response(audio_file):

    audio_bytes = audio_file.getvalue()

    mime_type = (
        audio_file.type
        if audio_file.type
        else "audio/wav"
    )

    conversation = build_conversation_context()

    audio_part = types.Part.from_bytes(
        data=audio_bytes,
        mime_type=mime_type
    )

    prompt = f"""
The citizen has sent a voice message.

Listen carefully to the audio and understand what the citizen
is asking.

Do NOT return a transcription.

Instead, directly understand the citizen's request and respond
as NextStep AI.

Use the previous conversation when relevant.

CONVERSATION HISTORY:

{conversation}

After understanding the audio:

- Identify the citizen's need.
- Ask a clarification question if important information is missing.
- If it is a clear public-service request, provide practical
  numbered steps.
- Only classify it as service_request when the citizen is actually
  requesting a service.
- Do not provide URLs.
- Return ONLY valid JSON.

Required JSON:

{{
  "intent": "general" | "clarification" | "service_request",
  "service_key": "service key" | null,
  "response": "your response to the citizen"
}}
"""

    return call_gemini(
        contents=[
            audio_part,
            prompt
        ]
    )


# ============================================================
# SINGLE GEMINI CALL
# ============================================================

def call_gemini(contents):

    last_error = None

    for model_name in [
        PRIMARY_MODEL,
        FALLBACK_MODEL
    ]:

        try:

            response = client.models.generate_content(

                model=model_name,

                contents=contents,

                config=types.GenerateContentConfig(

                    system_instruction=(
                        NEXTSTEP_SYSTEM_INSTRUCTION
                    ),

                    response_mime_type="application/json",

                    temperature=0.2

                )
            )

            data = clean_json_response(
                response.text
            )

            return normalize_result(
                data
            )

        except Exception as error:

            last_error = error

    return {
        "intent": "error",
        "service_key": None,
        "response": (
            "I'm having trouble connecting to the AI service "
            "right now. Please try again in a moment."
        ),
        "error": str(last_error)
    }


# ============================================================
# DISPLAY AI RESPONSE
# ============================================================

def display_ai_result(result):

    answer = result["response"]

    intent = result["intent"]

    service_key = result["service_key"]

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

            result = get_text_response(
                user_message
            )

        if result["intent"] == "error":

            st.error(
                result["response"]
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

        else:

            display_ai_result(
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
# PROCESS VOICE
# ============================================================

def process_voice(audio_file):

    if audio_file is None:
        return

    audio_bytes = audio_file.getvalue()

    if not audio_bytes:
        return

    audio_hash = hashlib.sha256(
        audio_bytes
    ).hexdigest()

    if (
        st.session_state.processed_audio_hash
        == audio_hash
    ):

        return

    st.session_state.processed_audio_hash = audio_hash

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

            result = get_voice_response(
                audio_file
            )

        if result["intent"] == "error":

            st.error(
                result["response"]
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

        else:

            display_ai_result(
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

    process_message(
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

input_col, voice_col, send_col = st.columns(
    [7, 2, 1]
)

with input_col:

    typed_message = st.text_input(
        "Message",
        placeholder=(
            "Example: I need an income certificate..."
        ),
        label_visibility="collapsed",
        key="message_input"
    )

with voice_col:

    voice_input = st.audio_input(
        "🎙️ Voice",
        label_visibility="collapsed",
        key="voice_input"
    )

with send_col:

    send_clicked = st.button(
        "➤",
        use_container_width=True
    )


# ============================================================
# SEND TEXT
# ============================================================

if send_clicked:

    if typed_message:

        process_message(
            typed_message
        )

        st.rerun()

    elif voice_input:

        process_voice(
            voice_input
        )

        st.rerun()

    else:

        st.warning(
            "Please type a message or record a voice request."
        )


# ============================================================
# ENTER-KEY SUPPORT
# ============================================================

if typed_message and not send_clicked:

    st.caption(
        "Press the ➤ button to send your message."
    )


# ============================================================
# VOICE AUTO PROCESS
# ============================================================

if voice_input and not send_clicked:

    process_voice(
        voice_input
    )

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

footer_left, footer_right = st.columns(
    [3, 1]
)

with footer_left:

    st.caption(
        "NextStep AI • Intelligent public-service guidance"
    )

with footer_right:

    st.caption(
        "Powered by Gemini"
    )
