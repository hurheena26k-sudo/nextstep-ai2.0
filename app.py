import streamlit as st
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
# GEMINI CONFIGURATION
# ============================================================

MODEL_NAME = "gemini-3.8-flash"

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

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
- Residence and domicile certificates
- Government scheme applications
- Licenses and permits
- Public grievances
- Municipal services
- Education-related government services
- Welfare services
- Aadhaar-related guidance
- Passport-related guidance
- Voter-related services
- Driving licence-related services
- Property and municipal services
- Water and sanitation services
- Other legitimate public-service requests

IMPORTANT BEHAVIOR:

1. Start by understanding what the citizen needs.

2. Do not assume that the citizen already knows the official
   name of the service.

3. If the citizen describes a problem indirectly, identify
   the possible service they may need.

4. Ask simple follow-up questions when important information
   is missing.

5. Determine what information is relevant before giving guidance.

6. Explain the process in simple step-by-step language.

7. Explain likely required documents only when appropriate.

8. Never invent government rules, fees, websites, deadlines,
   eligibility requirements, or documents.

9. If the exact procedure depends on location, ask for the
   relevant state, city, or country.

10. If you do not have enough reliable information, clearly
    say what needs to be verified.

11. Do not restrict yourself to a fixed list of services.

12. If the citizen's request is outside public services,
    politely explain that your main purpose is helping with
    public services.

STYLE:

- Friendly
- Clear
- Professional
- Easy for ordinary citizens to understand
- Helpful without overwhelming the citizen

Most importantly, guide the citizen toward their NEXT STEP.
"""

# ============================================================
# OFFICIAL GOVERNMENT SOURCES
# ============================================================

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

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = "New Conversation"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_source_for_message(message):

    text = message.lower()

    telangana_keywords = [
        "telangana",
        "hyderabad",
        "meeseva",
        "ghmc",
        "income certificate",
        "caste certificate",
        "residence certificate",
        "domicile",
        "birth certificate",
        "death certificate",
        "property tax",
        "water connection",
        "municipal",
        "scholarship",
        "ration card"
    ]

    central_keywords = [
        "aadhaar",
        "passport",
        "pan card",
        "income tax",
        "railway",
        "india post",
        "mgnrega",
        "central government"
    ]

    if any(word in text for word in telangana_keywords):
        return OFFICIAL_SOURCES["Telangana MeeSeva"]

    if any(word in text for word in central_keywords):
        return OFFICIAL_SOURCES["India Government Services"]

    return OFFICIAL_SOURCES["National Government Services Portal"]


def ask_nextstep_ai(user_message, conversation_history):

    contents = []

    for message in conversation_history:

        contents.append(
            types.Content(
                role=message["role"],
                parts=[
                    types.Part(
                        text=message["content"]
                    )
                ]
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part(
                    text=user_message
                )
            ]
        )
    )

    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash"
    ]

    last_error = None

    for model in models_to_try:

        try:

            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=NEXTSTEP_SYSTEM_INSTRUCTION,
                    temperature=0.4
                )
            )

            if response.text:
                return response.text

        except Exception as error:

            last_error = error

    return (
        "I'm temporarily unable to connect to the AI service. "
        "Please try again in a moment.\n\n"
        f"Technical information: {last_error}"
    )


def save_current_conversation():

    if not st.session_state.messages:
        return

    name = st.session_state.current_conversation

    st.session_state.conversations[name] = list(
        st.session_state.messages
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("💬 Conversations")

    if st.button(
        "➕ New Conversation",
        use_container_width=True
    ):

        save_current_conversation()

        st.session_state.messages = []
        st.session_state.current_conversation = "New Conversation"

        st.rerun()

    st.divider()

    conversation_names = list(
        st.session_state.conversations.keys()
    )

    if conversation_names:

        for conversation_name in conversation_names:

            col1, col2 = st.columns([4, 1])

            with col1:

                if st.button(
                    conversation_name,
                    key=f"open_{conversation_name}",
                    use_container_width=True
                ):

                    st.session_state.messages = list(
                        st.session_state.conversations[
                            conversation_name
                        ]
                    )

                    st.session_state.current_conversation = (
                        conversation_name
                    )

                    st.rerun()

            with col2:

                if st.button(
                    "🗑️",
                    key=f"delete_{conversation_name}"
                ):

                    del st.session_state.conversations[
                        conversation_name
                    ]

                    if (
                        st.session_state.current_conversation
                        == conversation_name
                    ):
                        st.session_state.messages = []
                        st.session_state.current_conversation = (
                            "New Conversation"
                        )

                    st.rerun()

    else:

        st.caption(
            "Your previous conversations will appear here."
        )

    st.divider()

    st.subheader("🌐 Official Sources")

    st.caption(
        "Access government portals directly."
    )

    for source_name, source_data in OFFICIAL_SOURCES.items():

        st.link_button(
            source_name,
            source_data["url"],
            use_container_width=True
        )

# ============================================================
# MAIN HEADER
# ============================================================

st.title("🤖 NextStep AI")

st.write(
    "Your intelligent guide to public services."
)

st.divider()

# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.subheader("👋 What do you need help with?")

    st.write(
        "Tell me what you need in your own words."
    )

    st.caption(
        "You don't need to know the official service name. "
        "I'll help you find the right next step."
    )

    st.divider()

# ============================================================
# DISPLAY CONVERSATION
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Tell NextStep AI what you need help with..."
)

if user_input:

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.write(user_input)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "NextStep AI is thinking..."
        ):

            ai_response = ask_nextstep_ai(
                user_input,
                st.session_state.messages[:-1]
            )

        st.write(ai_response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_response
        }
    )

    # --------------------------------------------------------
    # OFFICIAL SOURCE
    # --------------------------------------------------------

    source = get_source_for_message(user_input)

    st.info(
        f"🌐 Official source: {source['description']}"
    )

    st.link_button(
        "Open Official Government Portal",
        source["url"]
    )

    # --------------------------------------------------------
    # SAVE CONVERSATION
    # --------------------------------------------------------

    if (
        st.session_state.current_conversation
        == "New Conversation"
    ):

        title = user_input[:35]

        if len(user_input) > 35:
            title += "..."

        st.session_state.current_conversation = title

    save_current_conversation()
