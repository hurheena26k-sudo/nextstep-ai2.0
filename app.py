import streamlit as st

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# SESSION STATE
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = "New Conversation"


# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.markdown("## 🧭 NextStep AI")

    st.caption("Your AI guide for public services")

    st.divider()

    if st.button(
        "＋ New Conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.session_state.current_conversation = "New Conversation"
        st.rerun()

    st.divider()

    st.markdown("### Previous Conversations")

    if not st.session_state.conversations:
        st.caption("No previous conversations yet.")

    else:
        for conversation_name in st.session_state.conversations:

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

                    st.session_state.messages = []

                    st.rerun()


# -----------------------------
# MAIN INTERFACE
# -----------------------------

st.markdown(
    """
    <div style="text-align:center; padding-top:40px;">
        <h1>🧭 NextStep AI</h1>
        <p style="font-size:20px;">
            Your intelligent guide to public services
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# -----------------------------
# AI INTRODUCTION
# -----------------------------

if not st.session_state.messages:

    st.markdown(
        """
        <div style="text-align:center; padding:30px;">
            <h2>What do you need help with?</h2>
            <p>
                Tell me what you are trying to apply for,
                understand, or solve.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# -----------------------------
# CHAT HISTORY
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# -----------------------------
# USER INPUT
# -----------------------------

user_message = st.chat_input(
    "Tell NextStep AI what you need help with..."
)

if user_message:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    with st.chat_message("user"):
        st.write(user_message)

    with st.chat_message("assistant"):
        st.write(
            "I'm understanding your request and "
            "figuring out the right next step..."
        )
