import streamlit as st
from google import genai


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# GEMINI CLIENT
# ============================================================

try:

    api_key = st.secrets["GEMINI_API_KEY"]

    client = genai.Client(
        api_key=api_key
    )

except Exception as error:

    client = None

    st.error("Gemini configuration error.")

    with st.expander("Technical details"):
        st.code(
            f"{type(error).__name__}: {error}"
        )


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are NextStep AI, an intelligent public-service assistant.

Your job is to help citizens understand government and public
services.

You can help with:

- Birth certificates
- Death certificates
- Income certificates
- Caste certificates
- Residence certificates
- Government schemes
- Licenses
- Public grievances
- Municipal services
- Education services
- Scholarships
- Passport services
- Aadhaar services
- Property tax
- Water services
- Voter services
- Employment services
- Land services
- Other legitimate public services

Behavior:

1. First understand what the citizen needs.

2. If the citizen clearly wants a service, explain the steps
   in simple numbered points.

3. If important information is missing, ask a clarification
   question.

4. Do not give an official link for every normal conversation.

5. Give an official source only when the user is actually
   requesting a specific service.

6. Never invent government rules, fees, deadlines or documents.

7. If the procedure depends on location, ask for the relevant
   state or city.

8. Keep answers short, clear and practical.

9. If the request is unrelated to public services, politely
   explain that your main purpose is public-service assistance.
"""


# ============================================================
# SERVICE LINKS
# ============================================================

SERVICE_LINKS = {

    "income certificate": (
        "Income Certificate",
        "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "Official Telangana MeeSeva"
    ),

    "birth certificate": (
        "Birth Certificate",
        "https://www.telangana.gov.in/services/state-services/",
        "Official Telangana State Services"
    ),

    "death certificate": (
        "Death Certificate",
        "https://www.telangana.gov.in/services/state-services/",
        "Official Telangana State Services"
    ),

    "caste certificate": (
        "Caste Certificate",
        "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "Official Telangana MeeSeva"
    ),

    "residence certificate": (
        "Residence Certificate",
        "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "Official Telangana MeeSeva"
    ),

    "driving licence": (
        "Driving Licence",
        "https://transport.telangana.gov.in/",
        "Official Telangana Transport Department"
    ),

    "passport": (
        "Passport",
        "https://www.passportindia.gov.in/",
        "Official Passport Seva"
    ),

    "aadhaar": (
        "Aadhaar",
        "https://www.uidai.gov.in/",
        "Official UIDAI"
    ),

    "scholarship": (
        "Education / Scholarship",
        "https://telanganaepass.cgg.gov.in/",
        "Official Telangana ePASS"
    ),

    "government scheme": (
        "Government Schemes",
        "https://www.india.gov.in/",
        "Official National Government Portal"
    ),

    "public grievance": (
        "Public Grievance",
        "https://www.india.gov.in/",
        "Official National Government Portal"
    ),

    "property tax": (
        "Property Tax",
        "https://www.telangana.gov.in/services/state-services/",
        "Official Telangana State Services"
    ),

    "water connection": (
        "Water Connection",
        "https://www.telangana.gov.in/services/state-services/",
        "Official Telangana State Services"
    ),

    "voter": (
        "Voter Services",
        "https://www.india.gov.in/",
        "Official National Government Portal"
    )
}


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


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

        st.rerun()

    st.divider()

    st.subheader("💬 Conversation")

    if not st.session_state.messages:

        st.caption(
            "Your conversation will appear here."
        )

    else:

        user_messages = [

            m["content"]

            for m in st.session_state.messages

            if m["role"] == "user"
        ]

        for i, message in enumerate(
            user_messages[-8:]
        ):

            short = message[:45]

            if len(message) > 45:

                short += "..."

            st.caption(
                f"{i + 1}. {short}"
            )

    st.divider()

    st.caption(
        "Helping citizens find their next step."
    )


# ============================================================
# HEADER
# ============================================================

st.title("✦ NextStep AI")

st.caption(
    "Tell me what you need. I'll help you find your next step."
)

st.divider()


# ============================================================
# WELCOME
# ============================================================

if not st.session_state.messages:

    st.info(
        "👋 **Welcome to NextStep AI**\n\n"
        "Describe what you need in your own words. "
        "You don't need to know the exact government service."
    )

    st.subheader("✨ Try one")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📄 Income Certificate",
            use_container_width=True
        ):

            st.session_state.quick_prompt = (
                "I want to apply for an income certificate in Telangana."
            )

            st.rerun()

        if st.button(
            "📜 Birth Certificate",
            use_container_width=True
        ):

            st.session_state.quick_prompt = (
                "I want to apply for a birth certificate in Telangana."
            )

            st.rerun()

        if st.button(
            "🚗 Driving Licence",
            use_container_width=True
        ):

            st.session_state.quick_prompt = (
                "I want to apply for a driving licence in Telangana."
            )

            st.rerun()

    with col2:

        if st.button(
            "🪪 Aadhaar",
            use_container_width=True
        ):

            st.session_state.quick_prompt = (
                "I need help with Aadhaar."
            )

            st.rerun()

        if st.button(
            "🎓 Scholarship",
            use_container_width=True
        ):

            st.session_state.quick_prompt = (
                "I want to find a government scholarship."
            )

            st.rerun()

        if st.button(
            "🛂 Passport",
            use_container_width=True
        ):

            st.session_state.quick_prompt = (
                "I want to apply for a passport."
            )

            st.rerun()


# ============================================================
# SHOW PREVIOUS MESSAGES
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message(
            "user"
        ):

            st.write(
                message["content"]
            )

    else:

        with st.chat_message(
            "assistant"
        ):

            st.write(
                message["content"]
            )

            if message.get("source"):

                name, url, label = message["source"]

                st.link_button(
                    f"🔗 Open Official {name} Source",
                    url,
                    use_container_width=True
                )

                st.caption(
                    f"Source: {label}"
                )


# ============================================================
# FIND OFFICIAL SOURCE
# ============================================================

def find_source(user_text):

    text = user_text.lower()

    for keyword, source in SERVICE_LINKS.items():

        if keyword in text:

            return source

    return None


# ============================================================
# ASK GEMINI
# ============================================================

def ask_gemini(user_text):

    if client is None:

        return None, (
            "Gemini client could not be created."
        )

    try:

        response = client.models.generate_content(

            model="gemini-3.8-flash",

            contents=[
                SYSTEM_INSTRUCTION,
                user_text
            ]
        )

        answer = response.text

        if not answer:

            return None, (
                "Gemini returned an empty response."
            )

        return answer, None

    except Exception as error:

        return None, (
            f"{type(error).__name__}: {error}"
        )


# ============================================================
# PROCESS MESSAGE
# ============================================================

def process_message(user_text):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_text
        }
    )

    with st.chat_message(
        "user"
    ):

        st.write(
            user_text
        )

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "NextStep AI is thinking..."
        ):

            answer, error = ask_gemini(
                user_text
            )

        if error:

            st.error(
                "Gemini could not process the request."
            )

            st.warning(
                "Technical error:"
            )

            st.code(
                error
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "Gemini could not process the request."
                    ),
                    "source": None
                }
            )

            return

        st.write(
            answer
        )

        source = find_source(
            user_text
        )

        if source:

            name, url, label = source

            st.link_button(
                f"🔗 Open Official {name} Source",
                url,
                use_container_width=True
            )

            st.caption(
                f"Source: {label}"
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "source": source
            }
        )


# ============================================================
# QUICK PROMPT
# ============================================================

if "quick_prompt" in st.session_state:

    quick_prompt = st.session_state.quick_prompt

    del st.session_state.quick_prompt

    process_message(
        quick_prompt
    )


# ============================================================
# CHAT INPUT
# ============================================================

user_message = st.chat_input(
    "Tell me what you need help with..."
)

if user_message:

    process_message(
        user_message
    )
