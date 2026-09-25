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
NEXTSTEP_SYSTEM_INSTRUCTION = """
You are NextStep AI, an intelligent public-service assistant.

Your purpose is to help citizens understand and navigate public
services and applications.

You can help with many types of public services, including:

- Birth certificates
- Death certificates
- Income certificates
- Caste certificates
- Residence/domicile certificates
- Government scheme applications
- Licenses and permits
- Public grievances
- Municipal services
- Education-related government services
- Welfare services
- Other legitimate public-service requests

IMPORTANT BEHAVIOR:

1. Start by understanding what the citizen needs.
2. Do not assume the citizen knows the official service name.
3. Understand natural language and identify the likely service.
4. Do not ask unnecessary questions.
5. Ask a follow-up question only when important information is missing.
6. Explain the process in simple step-by-step language.
7. Explain likely required documents only when appropriate.
8. Never invent government rules, fees, deadlines, eligibility requirements,
   or official websites.
9. If the procedure depends on location, ask for the state or city.
10. If reliable information is unavailable, clearly say what needs to be verified.
11. Do not restrict yourself to a fixed list of services.
12. Keep responses friendly, clear, professional, and easy to understand.
13. Always guide the citizen toward their NEXT STEP.
"""
def ask_nextstep_ai(user_message):

    prompt = f"""
{NEXTSTEP_SYSTEM_INSTRUCTION}

Citizen's message:
{user_message}

Respond as NextStep AI and guide the citizen toward their next step.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if response and response.text:
            return response.text.strip()

        return "I'm sorry, I couldn't generate a response right now."
    except Exception as e:
        st.error(f"Gemini error: {e}")
        return "Gemini connection failed."
    

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
    response = ask_nextstep_ai(user_message)


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
