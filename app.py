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

You can help with many types of public services, including but not
limited to:

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

9. If the exact procedure depends on the citizen's location,
   ask for the relevant state, city, or country.

10. If you do not have enough reliable information, clearly say
    what needs to be verified.

11. Do not restrict yourself to a fixed list of services.

12. If the citizen's request is outside public services,
    politely explain that your main purpose is helping with
    public services.

CONVERSATION STYLE:

- Friendly
- Clear
- Professional
- Easy for ordinary citizens to understand
- Helpful without overwhelming the citizen

Most importantly, behave like an intelligent assistant that
guides the citizen toward their NEXT STEP.
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
    """
    Select an appropriate official government portal based
    on the citizen's request.
    """

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
    """
    Send the user's message and conversation history to Gemini.
    """

    contents = []

    for message in conversation_history:
        contents.append(
            types.Content(
                role=message["role"],
                parts=[
                    types.Part(text=message["content"])
                ]
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part(text=user_message)
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
        "I'm sorry, I'm temporarily unable to connect to the AI service. "
        "Please try again in a moment.\n\n"
        f"Technical information: {last_error}"
    )


def save_current_conversation():
    """
    Save the current conversation into session history.
    """

    if not st.session_state.messages:
        return

    name = st.session_state.current_conversation

    st.session_state.conversations[name] = list(
        st.session_state.messages
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */

    .main {
        padding-top: 1rem;
    }

    /* Header */

    .nextstep-header {
        text-align: center;
        padding: 30px 20px 25px 20px;
        border-radius: 16px;
        margin-bottom: 25px;
        background: #f8fafc;
    }

    .nextstep-logo {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 5px;
    }

    .nextstep-tagline {
        font-size: 18px;
        color: #475569;
        margin-top: 5px;
    }

    /* Welcome card */

    .welcome-card {
        background: #f8fafc;
        padding: 30px;
        border-radius: 14px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .welcome-card h2 {
        font-size: 24px;
        margin-bottom: 12px;
    }

    .welcome-card p {
        font-size: 18px;
        line-height: 1.6;
    }

    .welcome-small {
        font-size: 16px !important;
        color: #475569;
    }

    /* Source card */

    .source-card {
        padding: 18px;
        border-radius: 12px;
        background: #f8fafc;
        margin-top: 20px;
    }

    .source-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .source-description {
        color: #475569;
        margin-bottom: 12px;
    }

    /* Sidebar */

    .sidebar-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="nextstep-header">

        <div class="nextstep-logo">
            🤖 NextStep AI
        </div>

        <div class="nextstep-tagline">
            Your intelligent guide to public services
        </div>

    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-title">
            💬 Conversations
        </div>
        """,
        unsafe_allow_html=True
    )

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

    st.markdown(
        """
        <div class="source-card">

            <div class="source-title">
                🌐 Official Sources
            </div>

            <div class="source-description">
                Access government portals directly.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    for source_name, source_data in OFFICIAL_SOURCES.items():

        st.link_button(
            source_name,
            source_data["url"],
            use_container_width=True
        )

# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="welcome-card">

            <h2>
                👋 What do you need help with?
            </h2>

            <p>
                Tell me what you need in your own words.
            </p>

            <p class="welcome-small">
                You don't need to know the official service name.
                I'll help you find the right next step.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Tell NextStep AI what you need help with..."
)

if user_input:

    # Display user message

    with st.chat_message("user"):
        st.markdown(user_input)

    # Add user message to history

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Get AI response

    with st.chat_message("assistant"):

        with st.spinner("NextStep AI is thinking..."):

            ai_response = ask_nextstep_ai(
                user_input,
                st.session_state.messages[:-1]
            )

        st.markdown(ai_response)

    # Add AI response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_response
        }
    )

    # Show relevant official source

    source = get_source_for_message(user_input)

    st.markdown(
        f"""
        <div class="source-card">

            <div class="source-title">
                🌐 Official source
            </div>

            <div class="source-description">
                {source["description"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.link_button(
        f"Open {list(
            OFFICIAL_SOURCES.keys()
        )[list(
            OFFICIAL_SOURCES.values()
        ).index(source)]}",
        source["url"]
    )

    # Save conversation

    if st.session_state.current_conversation == "New Conversation":

        title = user_input[:35]

        if len(user_input) > 35:
            title += "..."

        st.session_state.current_conversation = title

    save_current_conversation()
