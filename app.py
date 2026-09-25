import streamlit as st
from google import genai

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

MODEL_NAME = "gemini-3.8-flash"


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

    st.title("🧭 NextStep AI")

    st.caption("Your intelligent guide to public services")

    st.divider()

    if st.button("＋ New Conversation", use_container_width=True):

        st.session_state.messages = []
        st.session_state.current_conversation = "New Conversation"

        st.rerun()

    st.divider()

    st.subheader("💬 Previous Conversations")

    if not st.session_state.conversations:

        st.caption("No previous conversations yet.")

    else:

        for name in list(st.session_state.conversations.keys()):

            col1, col2 = st.columns([4, 1])

            with col1:

                if st.button(
                    name,
                    key=f"open_{name}",
                    use_container_width=True
                ):

                    st.session_state.messages = (
                        st.session_state.conversations[name].copy()
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

st.title("🧭 NextStep AI")

st.subheader("Your intelligent guide to public services")

st.divider()


# =========================================================
# WELCOME SCREEN
# =========================================================

if not st.session_state.messages:

    st.header("👋 Welcome to NextStep AI")

    st.write(
        "I can help you understand public services, "
        "certificates, applications, government schemes, "
        "licenses, permits, and more."
    )

    st.write(
        "You don't need to know the exact service name. "
        "Just tell me what you need."
    )

    st.info(
        "💡 What do you need help with today?"
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

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # Display user message
    with st.chat_message("user"):

        st.write(user_message)


    # Temporary response
    response = (
        "I'm understanding your request and "
        "figuring out the right next step..."
    )


    # Display AI response
    with st.chat_message("assistant"):

        st.write(response)


    # Save AI response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


    # Create conversation name
    conversation_name = user_message[:40].strip()

    if not conversation_name:

        conversation_name = "New Conversation"


    # Save conversation
    st.session_state.conversations[
        conversation_name
    ] = st.session_state.messages.copy()


    st.session_state.current_conversation = conversation_name
