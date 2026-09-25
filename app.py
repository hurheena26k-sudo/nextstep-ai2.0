import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)


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

    st.markdown("## 🧭 NextStep AI")
    st.caption("Your intelligent guide to public services")

    st.divider()

    if st.button(
        "＋ New Conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.session_state.current_conversation = "New Conversation"
        st.rerun()

    st.divider()

    st.markdown("### 💬 Previous Conversations")

    if not st.session_state.conversations:
        st.caption("No previous conversations yet.")

    else:

        for conversation_name in list(
            st.session_state.conversations.keys()
        ):

            col1, col2 = st.columns([4, 1])

            with col1:

                if st.button(
                    conversation_name,
                    key=f"open_{conversation_name}",
                    use_container_width=True
                ):

                    st.session_state.messages = (
                        st.session_state.conversations[
                            conversation_name
                        ].copy()
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
    <div style="
        text-align: center;
        padding-top: 25px;
        padding-bottom: 10px;
    ">

        <div style="font-size: 65px;">
            🧭
        </div>

        <h1 style="
            font-size: 42px;
            margin-bottom: 5px;
        ">
            NextStep AI
        </h1>

        <p style="
            font-size: 19px;
            color: #666666;
        ">
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
            text-align: center;
            padding: 35px 20px 20px 20px;
        ">

            <h2>
                👋 Welcome to NextStep AI
            </h2>

            <p style="font-size: 18px;">
                I can help you understand public services,
                certificates, applications, government schemes,
                licenses, permits, and more.
            </p>

            <p style="
                font-size: 16px;
                color: #666666;
            ">
                You don't need to know the exact service name.
                Just tell me what you need.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "💡 Tell me what you are trying to apply for, "
        "understand, or solve."
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
# PROCESS USER MESSAGE
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

    # Temporary AI response
    with st.chat_message("assistant"):

        response = (
            "I'm understanding your request and "
            "figuring out the right next step..."
        )

        st.write(response)

    # Save AI response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    # Conversation name
    conversation_name = user_message[:40].strip()

    if not conversation_name:
        conversation_name = "New Conversation"

    # Save conversation
    st.session_state.conversations[
        conversation_name
    ] = st.session_state.messages.copy()

    st.session_state.current_conversation = conversation_name
