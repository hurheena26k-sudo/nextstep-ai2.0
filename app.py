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
# GEMINI
# ============================================================

MODEL_NAME = "gemini-3.8-flash"

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ============================================================
# NEXTSTEP AI INSTRUCTIONS
# ============================================================

NEXTSTEP_SYSTEM_INSTRUCTION = """
You are NextStep AI, an intelligent public-service assistant.

Your job is to help citizens understand what government service
they may need and guide them toward the correct next step.

You must NOT behave like a simple question-answer chatbot.

Your workflow is:

1. Understand what the citizen is trying to accomplish.

2. If the citizen has not provided enough information, ASK A
   CLEAR CLARIFICATION QUESTION before giving a final process.

3. Do not guess important information.

4. Once enough information is available, explain the process
   using simple numbered steps.

5. Explain only the documents that are relevant to the service
   when you have reliable information.

6. If location matters, ask for the state/city/country.

7. Never invent:
   - government rules
   - fees
   - deadlines
   - eligibility requirements
   - documents
   - official websites
   - processing times

8. If you are uncertain about something, clearly say that it
   needs to be verified from the official government source.

9. Do not restrict yourself to only a few services.

10. You can help with many public services including:
    - Birth certificates
    - Death certificates
    - Income certificates
    - Caste certificates
    - Residence/domicile certificates
    - Government schemes
    - Scholarships
    - Licences
    - Permits
    - Public grievances
    - Municipal services
    - Property services
    - Water services
    - Education services
    - Welfare services
    - Aadhaar-related guidance
    - Passport-related guidance
    - Voter-related guidance
    - Driving licence-related guidance
    - Other legitimate government services

RESPONSE BEHAVIOR:

If information is missing:

Say what you understand and ask the most useful clarification
question.

Example:

"I can help you with that. Which state are you applying in?"

Do NOT provide a long generic procedure before the clarification.

If enough information is available:

Give the answer in this structure:

What I understood:
[short explanation]

Next steps:
1. ...
2. ...
3. ...
4. ...

Documents:
- ...
- ...

Important:
[only if necessary]

Keep answers:
- Clear
- Friendly
- Professional
- Beginner-friendly
- Short enough to understand easily

Your purpose is to help the citizen reach the correct NEXT STEP.
"""


# ============================================================
# OFFICIAL SERVICE LINKS
# ============================================================
#
# These are official government sources.
# If a specific direct service link is not verified,
# use the official government service directory instead.
# ============================================================

SERVICE_LINKS = {

    "birth_certificate": {
        "name": "Birth Certificate",
        "keywords": [
            "birth certificate",
            "birth registration",
            "register birth"
        ],
        "url": (
            "https://ts.meeseva.telangana.gov.in/"
            "meeseva/downloadzip.htm?"
            "filename=CDMAAPPLICATIONFORBIRTHCERTIFICATE.pdf"
        ),
        "description": "Official Telangana birth certificate application form."
    },

    "death_certificate": {
        "name": "Death Certificate",
        "keywords": [
            "death certificate",
            "death registration",
            "register death"
        ],
        "url": (
            "https://ts.meeseva.telangana.gov.in/"
            "meeseva/downloadzip.htm?"
            "filename=CDMAAPPLICATIONFORDEATHCERTIFICATE.pdf"
        ),
        "description": "Official Telangana death registration application form."
    },

    "income_certificate": {
        "name": "Income Certificate",
        "keywords": [
            "income certificate",
            "income proof",
            "income certificate application"
        ],
        "url": (
            "https://ts.meeseva.telangana.gov.in/"
            "meeseva/downloadzip.htm?"
            "filename=IncomeGeneralApplicationForm.pdf"
        ),
        "description": "Official Telangana income certificate application form."
    },

    "driving_license": {
        "name": "Driving Licence",
        "keywords": [
            "driving licence",
            "driving license",
            "learner licence",
            "learner license",
            "dl application"
        ],
        "url": (
            "https://transport.telangana.gov.in/"
            "html/driving-licence.html"
        ),
        "description": "Official Telangana Transport Department driving licence service."
    },

    "passport": {
        "name": "Passport",
        "keywords": [
            "passport",
            "new passport",
            "passport application",
            "passport renewal",
            "passport reissue"
        ],
        "url": "https://passportindia.gov.in/",
        "description": "Official Passport Seva portal."
    },

    "voter_registration": {
        "name": "Voter Registration",
        "keywords": [
            "voter",
            "voter registration",
            "voter id",
            "electoral roll",
            "electoral registration"
        ],
        "url": (
            "https://www.india.gov.in/services/"
        ),
        "description": "Official Government of India services portal."
    },

    "scholarship": {
        "name": "Telangana Scholarship",
        "keywords": [
            "scholarship",
            "student scholarship",
            "pre matric scholarship",
            "post matric scholarship"
        ],
        "url": "https://telanganaepass.cgg.gov.in/",
        "description": "Official Telangana ePASS scholarship portal."
    },

    "caste_certificate": {
        "name": "Caste Certificate",
        "keywords": [
            "caste certificate",
            "community certificate",
            "sc certificate",
            "st certificate",
            "bc certificate"
        ],
        "url": (
            "https://www.telangana.gov.in/"
            "services/state-services/"
        ),
        "description": "Official Telangana State Services portal."
    },

    "residence_certificate": {
        "name": "Residence / Domicile Certificate",
        "keywords": [
            "residence certificate",
            "domicile certificate",
            "nativity certificate"
        ],
        "url": (
            "https://www.telangana.gov.in/"
            "services/state-services/"
        ),
        "description": "Official Telangana State Services portal."
    },

    "property_tax": {
        "name": "Property Tax",
        "keywords": [
            "property tax",
            "house tax",
            "property payment"
        ],
        "url": (
            "https://www.telangana.gov.in/"
            "services/state-services/"
        ),
        "description": "Official Telangana State Services portal."
    },

    "water_connection": {
        "name": "Water Connection",
        "keywords": [
            "water connection",
            "new water connection",
            "water supply"
        ],
        "url": (
            "https://www.telangana.gov.in/"
            "services/state-services/"
        ),
        "description": "Official Telangana State Services portal."
    },

    "general": {
        "name": "Government Services Directory",
        "keywords": [],
        "url": "https://www.india.gov.in/services",
        "description": "Official Government of India services directory."
    }
}


# ============================================================
# OFFICIAL GENERAL PORTALS
# ============================================================

OFFICIAL_PORTALS = {
    "Telangana MeeSeva": (
        "https://ts.meeseva.telangana.gov.in/"
    ),
    "Telangana State Services": (
        "https://www.telangana.gov.in/services/state-services/"
    ),
    "Telangana Public Utility Forms": (
        "https://www.telangana.gov.in/services/public-utility-forms/"
    ),
    "India Government Services": (
        "https://www.india.gov.in/services"
    ),
    "National Government Services Portal": (
        "https://services.india.gov.in/"
    )
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
# FIND SERVICE LINK
# ============================================================

def find_service_link(user_message):

    text = user_message.lower()

    for service_key, service in SERVICE_LINKS.items():

        for keyword in service["keywords"]:

            if keyword in text:

                return service

    return SERVICE_LINKS["general"]


# ============================================================
# GEMINI FUNCTION
# ============================================================

def ask_nextstep_ai(user_message, conversation_history):

    contents = []

    for message in conversation_history:

        role = message["role"]

        if role == "assistant":
            role = "model"

        contents.append(
            types.Content(
                role=role,
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
                    temperature=0.3
                )
            )

            if response.text:

                return response.text

        except Exception as error:

            last_error = error

    return (
        "I'm temporarily unable to connect to the AI service. "
        "Please try again in a moment."
    )


# ============================================================
# SAVE CONVERSATION
# ============================================================

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

        st.session_state.current_conversation = (
            "New Conversation"
        )

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

    st.subheader("🌐 Official Government Portals")

    for name, url in OFFICIAL_PORTALS.items():

        st.link_button(
            name,
            url,
            use_container_width=True
        )


# ============================================================
# MAIN APP
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

    st.subheader(
        "👋 What do you need help with?"
    )

    st.write(
        "Tell me what you need in your own words."
    )

    st.caption(
        "You don't need to know the official service name. "
        "I'll help you find the right next step."
    )

    st.divider()


# ============================================================
# DISPLAY CHAT HISTORY
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
    # SHOW USER MESSAGE
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
    # OFFICIAL SERVICE LINK
    # --------------------------------------------------------

    service = find_service_link(user_input)

    st.divider()

    st.subheader(
        f"🔗 Official {service['name']} Source"
    )

    st.caption(
        service["description"]
    )

    st.link_button(
        f"Open {service['name']} Service",
        service["url"]
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
