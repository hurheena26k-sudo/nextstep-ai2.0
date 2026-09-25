import streamlit as st
from google import genai
import time


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# GEMINI
# =========================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

MODEL_NAME = "gemini-3.8-flash"


# =========================================================
# OFFICIAL SERVICE SOURCES
# =========================================================

OFFICIAL_SOURCES = {
    "Telangana MeeSeva": {
        "url": "https://ts.meeseva.telangana.gov.in/",
        "description": "Telangana government citizen services and applications."
    },

    "Telangana State Services": {
        "url": "https://www.telangana.gov.in/services/state-services/",
        "description": "Official Telangana state government services."
    },

    "Telangana Public Utility Forms": {
        "url": "https://www.telangana.gov.in/services/public-utility-forms/",
        "description": "Official Telangana government application forms."
    },

    "India Government Services": {
        "url": "https://www.india.gov.in/services",
        "description": "National Portal of India government services."
    },

    "National Government Services Portal": {
        "url": "https://services.india.gov.in/",
        "description": "Government of India services directory."
    },

    "Telangana State Portal": {
        "url": "https://www.telangana.gov.in/",
        "description": "Official Telangana government portal."
    }
}


# =========================================================
# NEXTSTEP AI INSTRUCTIONS
# =========================================================

NEXTSTEP_SYSTEM_INSTRUCTION = """
You are NextStep AI, an intelligent public-service navigation assistant.

Your main purpose is to understand what a citizen needs and guide them
toward the correct official government service.

You can help with a very broad range of public services, including:

CERTIFICATES:
- Birth certificate
- Death certificate
- Income certificate
- Caste/community certificate
- Residence certificate
- Domicile/nativity certificate
- EWS certificate
- Family member certificate
- Non-creamy layer certificate
- Other legitimate certificates

IDENTITY AND CIVIC SERVICES:
- Aadhaar-related services
- Voter services
- PAN-related services
- Passport services
- Government registrations

MUNICIPAL SERVICES:
- Property tax
- Water connection
- Birth/death registration
- Building permissions
- Trade licences
- Municipal complaints
- Other local-body services

TRANSPORT:
- Driving licence
- Learner licence
- Vehicle-related services
- Transport applications

WELFARE AND SCHEMES:
- Scholarships
- Government welfare schemes
- Employment-related government services
- Social welfare services
- Farmer-related services
- Other legitimate government schemes

PUBLIC GRIEVANCES:
- Municipal complaints
- Public-service complaints
- Department grievances
- Civic problems

OTHER SERVICES:
- Licences
- Permits
- Government applications
- Education services
- Health-related government services
- Housing services
- Utility services
- Any other legitimate public-service request

IMPORTANT:

1. Understand natural language.

2. The citizen does NOT need to know the official service name.

3. Identify the likely service when the request is clear.

4. Do not ask unnecessary questions.

5. Ask only important follow-up questions.

6. If location matters, ask for the state/city.

7. Never invent government rules, fees, deadlines, eligibility criteria,
   documents, or official URLs.

8. Do not pretend that NextStep AI itself submits an application unless
   the application is actually supported by the system.

9. When an official government source is available, direct the citizen
   toward that official source.

10. Clearly distinguish between:
    - what NextStep AI knows,
    - what the citizen needs to verify,
    - and where the citizen can continue the official process.

11. Do not restrict yourself to a fixed list of services.

12. Be concise, friendly, professional and easy to understand.

13. Always help the citizen reach a clear NEXT STEP.

14. If the request is unrelated to public services, politely explain
    that your main purpose is public-service assistance.
"""


# =========================================================
# GEMINI FUNCTION
# =========================================================

def ask_nextstep_ai(user_message, conversation_history):

    history_text = ""

    for message in conversation_history:

        history_text += (
            f'{message["role"].upper()}: '
            f'{message["content"]}\n'
        )

    prompt = f"""
{NEXTSTEP_SYSTEM_INSTRUCTION}

Previous conversation:
{history_text}

Current citizen message:
{user_message}

Official source options available inside this application:

1. Telangana MeeSeva
   {OFFICIAL_SOURCES["Telangana MeeSeva"]["url"]}

2. Telangana State Services
   {OFFICIAL_SOURCES["Telangana State Services"]["url"]}

3. Telangana Public Utility Forms
   {OFFICIAL_SOURCES["Telangana Public Utility Forms"]["url"]}

4. India Government Services
   {OFFICIAL_SOURCES["India Government Services"]["url"]}

5. National Government Services Portal
   {OFFICIAL_SOURCES["National Government Services Portal"]["url"]}

Use these official sources when relevant.

Do not invent another government URL.

Respond naturally as NextStep AI.

If the request is clear:
- identify the service,
- briefly explain what the citizen should do next,
- mention the appropriate official portal.

If location is unknown and the service depends on location:
ask for the state/city before giving a location-specific recommendation.

If the citizen already gave their location earlier,
do not ask for it again.

Current citizen message:
{user_message}
"""

    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash"
    ]

    for model_name in models_to_try:

        for attempt in range(2):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response and response.text:

                    return response.text.strip()

            except Exception as e:

                error_text = str(e)

                temporary_error = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                )

                if temporary_error:

                    if attempt == 0:
                        time.sleep(2)
                        continue

                    break

                return (
                    "I'm temporarily unable to process that request. "
                    "Please try again."
                )

    return (
        "The AI service is temporarily busy. "
        "Please try again in a moment."
    )


# =========================================================
# FIND RELEVANT OFFICIAL SOURCE
# =========================================================

def get_source_for_message(message):

    text = message.lower()

    if any(
        word in text
        for word in [
            "telangana",
            "hyderabad",
            "meeseva",
            "income certificate",
            "caste certificate",
            "community certificate",
            "residence certificate",
            "domicile",
            "birth certificate",
            "death certificate",
            "property tax",
            "water connection",
            "trade licence",
            "scholarship"
        ]
    ):

        return "Telangana MeeSeva"

    if any(
        word in text
        for word in [
            "aadhaar",
            "passport",
            "pan",
            "voter",
            "central government",
            "india government"
        ]
    ):

        return "India Government Services"

    return "National Government Services Portal"


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = "New Conversation"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center;">
            <div style="font-size:48px;">🧭</div>
            <h2>NextStep AI</h2>
            <p>Your public-service guide</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    if st.button(
        "＋ New Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.current_conversation = (
            "New Conversation"
        )

        st.rerun()

    st.divider()

    st.subheader("💬 Previous Conversations")

    if not st.session_state.conversations:

        st.caption("No previous conversations yet.")

    else:

        for name in list(
            st.session_state.conversations.keys()
        ):

            col1, col2 = st.columns([4, 1])

            with col1:

                if st.button(
                    name,
                    key=f"open_{name}",
                    use_container_width=True
                ):

                    st.session_state.messages = (
                        st.session_state
                        .conversations[name]
                        .copy()
                    )

                    st.session_state.current_conversation = name

                    st.rerun()

            with col2:

                if st.button(
                    "🗑️",
                    key=f"delete_{name}"
                ):

                    del st.session_state.conversations[name]

                    st.session_state.messages = []

                    st.session_state.current_conversation = (
                        "New Conversation"
                    )

                    st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    """
    <div style="text-align:center; padding:25px 10px 10px 10px;">

        <div style="font-size:65px;">
            🧭
        </div>

        <h1 style="font-size:44px; margin-bottom:5px;">
            NextStep AI
        </h1>

        <p style="font-size:21px;">
            Your intelligent guide to public services
        </p>

    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# WELCOME SCREEN
# =========================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:20px 20px 15px 20px;
        ">

            <h2>
                👋 What do you need help with?
            </h2>

            <p style="font-size:18px;">
                Tell me what you need in your own words.
            </p>

            <p style="font-size:16px;">
                You don't need to know the official service name.
                I'll help you find the right next step.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# =========================================================
# USER INPUT
# =========================================================

user_message = st.chat_input(
    "Tell NextStep AI what you need help with..."
)


# =========================================================
# PROCESS MESSAGE
# =========================================================

if user_message:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    with st.chat_message("user"):

        st.write(user_message)

    previous_messages = (
        st.session_state.messages[:-1]
    )

    with st.chat_message("assistant"):

        with st.spinner(
            "🧭 NextStep AI is finding your next step..."
        ):

            response = ask_nextstep_ai(
                user_message,
                previous_messages
            )

        st.write(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


    # =====================================================
    # OFFICIAL SERVICE BUTTON
    # =====================================================

    source_name = get_source_for_message(
        user_message
    )

    source = OFFICIAL_SOURCES[source_name]

    st.markdown(
        "### 🔗 Official Service"
    )

    st.caption(
        f"Based on your request, you can continue through: "
        f"**{source_name}**"
    )

    st.link_button(
        f"Open {source_name} ↗",
        source["url"],
        use_container_width=True
    )


    # =====================================================
    # SAVE CONVERSATION
    # =====================================================

    conversation_name = (
        user_message[:40].strip()
    )

    if not conversation_name:

        conversation_name = "New Conversation"

    st.session_state.conversations[
        conversation_name
    ] = st.session_state.messages.copy()

    st.session_state.current_conversation = (
        conversation_name
    )
