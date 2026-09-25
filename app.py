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
# GEMINI CONFIG
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

Your purpose is to help citizens understand government services
and guide them toward the correct next step.

IMPORTANT WORKFLOW:

1. Understand what the citizen wants.

2. If important information is missing, ASK A CLARIFICATION
   QUESTION before giving the complete procedure.

3. Do not guess important information.

4. Once enough information is available, give clear,
   numbered, step-by-step instructions.

5. Mention relevant documents only when appropriate.

6. If the procedure depends on the citizen's state, city,
   country, age, or other important information, ask for it.

7. Never invent government rules, fees, deadlines,
   eligibility requirements, documents, or procedures.

8. If something needs verification, tell the citizen to
   verify it on the official government website.

9. You can help with many government services. Do not restrict
   yourself to only a fixed list.

10. Your answer should be easy for an ordinary citizen to
    understand.

WHEN CLARIFICATION IS NEEDED:

Do not give a long generic answer.

Instead, briefly explain what you understood and ask the
most useful question.

Example:

"I can help with that. Which state are you applying in?"

WHEN ENOUGH INFORMATION IS AVAILABLE:

Use this structure:

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

Keep responses friendly, professional, concise and practical.

Your goal is to guide the citizen toward their NEXT STEP.
"""


# ============================================================
# SERVICE DATABASE
# ============================================================
#
# These links are based on official Telangana government
# service directories and official government portals.
# ============================================================

SERVICES = {

    # --------------------------------------------------------
    # TELANGANA BASIC CERTIFICATES
    # --------------------------------------------------------

    "birth": {
        "name": "Birth Certificate",
        "keywords": [
            "birth certificate",
            "birth registration",
            "register birth",
            "birth record"
        ],
        "url": "https://ubdmis.telangana.gov.in/",
        "source": "Telangana Birth & Death Registration"
    },

    "death": {
        "name": "Death Certificate",
        "keywords": [
            "death certificate",
            "death registration",
            "register death",
            "death record"
        ],
        "url": "https://ubdmis.telangana.gov.in/",
        "source": "Telangana Birth & Death Registration"
    },

    "income": {
        "name": "Income Certificate",
        "keywords": [
            "income certificate",
            "income proof",
            "income certificate application"
        ],
        "url": "https://ts.meeseva.telangana.gov.in/",
        "source": "Telangana MeeSeva"
    },

    "caste": {
        "name": "Caste Certificate",
        "keywords": [
            "caste certificate",
            "community certificate",
            "sc certificate",
            "st certificate",
            "bc certificate",
            "obc certificate"
        ],
        "url": "https://ts.meeseva.telangana.gov.in/",
        "source": "Telangana MeeSeva"
    },

    "residence": {
        "name": "Residence / Domicile Certificate",
        "keywords": [
            "residence certificate",
            "domicile certificate",
            "nativity certificate"
        ],
        "url": "https://ts.meeseva.telangana.gov.in/",
        "source": "Telangana MeeSeva"
    },

    "integrated": {
        "name": "Integrated Certificate",
        "keywords": [
            "integrated certificate",
            "caste nativity dob",
            "community nativity dob"
        ],
        "url": "https://ts.meeseva.telangana.gov.in/",
        "source": "Telangana MeeSeva"
    },

    # --------------------------------------------------------
    # TELANGANA EDUCATION / SCHOLARSHIPS
    # --------------------------------------------------------

    "scholarship": {
        "name": "Telangana Scholarship",
        "keywords": [
            "scholarship",
            "student scholarship",
            "post matric scholarship",
            "pre matric scholarship",
            "epass",
            "e pass"
        ],
        "url": "https://telanganaepass.cgg.gov.in/",
        "source": "Telangana ePASS"
    },

    # --------------------------------------------------------
    # TELANGANA MUNICIPAL SERVICES
    # --------------------------------------------------------

    "property_tax": {
        "name": "Property Tax",
        "keywords": [
            "property tax",
            "house tax",
            "property payment"
        ],
        "url": "https://emunicipal.telangana.gov.in/",
        "source": "Telangana Municipal Administration"
    },

    "water": {
        "name": "Water Connection",
        "keywords": [
            "water connection",
            "new water connection",
            "water supply",
            "water connection application"
        ],
        "url": "https://emunicipal.telangana.gov.in/",
        "source": "Telangana Municipal Administration"
    },

    "building": {
        "name": "Building / Development Permission",
        "keywords": [
            "building permission",
            "building permit",
            "construction permission",
            "development permit"
        ],
        "url": "https://emunicipal.telangana.gov.in/",
        "source": "Telangana Municipal Administration"
    },

    # --------------------------------------------------------
    # TELANGANA VOTER SERVICES
    # --------------------------------------------------------

    "voter": {
        "name": "Voter Services",
        "keywords": [
            "voter",
            "voter id",
            "voter registration",
            "electoral roll",
            "electoral registration",
            "voter card"
        ],
        "url": "https://ceotelangana.nic.in/",
        "source": "Chief Electoral Officer, Telangana"
    },

    # --------------------------------------------------------
    # DRIVING LICENCE
    # --------------------------------------------------------

    "driving": {
        "name": "Driving Licence",
        "keywords": [
            "driving licence",
            "driving license",
            "learner licence",
            "learner license",
            "driving test",
            "dl application"
        ],
        "url": "https://transport.telangana.gov.in/html/driving-licence.html",
        "source": "Telangana Transport Department"
    },

    # --------------------------------------------------------
    # PASSPORT
    # --------------------------------------------------------

    "passport": {
        "name": "Passport",
        "keywords": [
            "passport",
            "new passport",
            "passport application",
            "passport renewal",
            "passport reissue",
            "passport appointment"
        ],
        "url": "https://www.passportindia.gov.in/psp",
        "source": "Passport Seva"
    },

    # --------------------------------------------------------
    # AADHAAR
    # --------------------------------------------------------

    "aadhaar": {
        "name": "Aadhaar Services",
        "keywords": [
            "aadhaar",
            "aadhar",
            "aadhaar card",
            "aadhar card",
            "aadhaar update",
            "aadhaar enrolment",
            "aadhaar enrollment"
        ],
        "url": "https://uidai.gov.in/en/",
        "source": "UIDAI"
    },

    # --------------------------------------------------------
    # PAN
    # --------------------------------------------------------

    "pan": {
        "name": "PAN Services",
        "keywords": [
            "pan card",
            "pan application",
            "pan status",
            "pan correction",
            "tan"
        ],
        "url": "https://www.incometax.gov.in/",
        "source": "Income Tax Department"
    },

    # --------------------------------------------------------
    # RAILWAYS
    # --------------------------------------------------------

    "railway": {
        "name": "Indian Railways",
        "keywords": [
            "railway",
            "train ticket",
            "train booking",
            "irctc",
            "rail ticket"
        ],
        "url": "https://www.irctc.co.in/",
        "source": "IRCTC"
    },

    # --------------------------------------------------------
    # MGNREGA
    # --------------------------------------------------------

    "mgnrega": {
        "name": "MGNREGA",
        "keywords": [
            "mgnrega",
            "nrega",
            "employment guarantee",
            "rural employment"
        ],
        "url": "https://nrega.telangana.gov.in/",
        "source": "Telangana MGNREGA"
    },

    # --------------------------------------------------------
    # POLICE
    # --------------------------------------------------------

    "police": {
        "name": "Telangana Police",
        "keywords": [
            "police",
            "police complaint",
            "fir",
            "missing person",
            "police verification"
        ],
        "url": "https://www.tspolice.gov.in/",
        "source": "Telangana Police"
    },

    # --------------------------------------------------------
    # GHMC
    # --------------------------------------------------------

    "ghmc": {
        "name": "Greater Hyderabad Municipal Corporation",
        "keywords": [
            "ghmc",
            "hyderabad municipal",
            "hyderabad property",
            "hyderabad water",
            "hyderabad birth certificate",
            "hyderabad death certificate"
        ],
        "url": "https://www.ghmc.gov.in/",
        "source": "Greater Hyderabad Municipal Corporation"
    },

    # --------------------------------------------------------
    # RATION / FOOD
    # --------------------------------------------------------

    "ration": {
        "name": "Telangana Civil Supplies",
        "keywords": [
            "ration card",
            "food security card",
            "food card",
            "civil supplies"
        ],
        "url": "https://civilsupplies.telangana.gov.in/",
        "source": "Telangana Civil Supplies"
    },

    # --------------------------------------------------------
    # LAND
    # --------------------------------------------------------

    "land": {
        "name": "Telangana Land Services",
        "keywords": [
            "land records",
            "land registration",
            "land record",
            "bhubharati",
            "bhu bharati",
            "mutation",
            "property registration"
        ],
        "url": "https://bhubharati.telangana.gov.in/",
        "source": "Telangana Bhu Bharati"
    }
}


# ============================================================
# GENERAL OFFICIAL PORTALS
# ============================================================

OFFICIAL_PORTALS = {
    "Telangana MeeSeva": "https://ts.meeseva.telangana.gov.in/",
    "Telangana State Services": "https://www.telangana.gov.in/services/state-services/",
    "Telangana Public Utility Forms": "https://www.telangana.gov.in/services/public-utility-forms/",
    "Telangana State Portal": "https://www.telangana.gov.in/",
    "Government of India Services": "https://www.india.gov.in/services",
    "National Government Services Portal": "https://services.india.gov.in/"
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
# FIND RELEVANT SERVICE
# ============================================================

def find_service(user_message):

    text = user_message.lower()

    # Check longer/more specific services first
    ordered_services = [
        "passport",
        "aadhaar",
        "pan",
        "railway",
        "mgnrega",
        "scholarship",
        "driving",
        "birth",
        "death",
        "income",
        "caste",
        "residence",
        "integrated",
        "property_tax",
        "water",
        "building",
        "voter",
        "police",
        "ghmc",
        "ration",
        "land"
    ]

    for service_key in ordered_services:

        service = SERVICES[service_key]

        for keyword in service["keywords"]:

            if keyword in text:
                return service

    return None


# ============================================================
# ASK GEMINI
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

    st.subheader("🌐 Official Portals")

    for portal_name, portal_url in OFFICIAL_PORTALS.items():

        st.link_button(
            portal_name,
            portal_url,
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
# WELCOME
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
# DISPLAY CHAT
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
    # SERVICE LINK
    # --------------------------------------------------------

    service = find_service(user_input)

    if service:

        st.divider()

        st.subheader(
            f"🔗 Official {service['name']} Service"
        )

        st.caption(
            f"Source: {service['source']}"
        )

        st.link_button(
            f"Open {service['name']} Service",
            service["url"]
        )

    else:

        st.divider()

        st.subheader(
            "🔗 Find the Official Government Service"
        )

        st.caption(
            "I couldn't confidently identify a specific "
            "service portal, so I'm showing the official "
            "government service directories instead."
        )

        col1, col2 = st.columns(2)

        with col1:

            st.link_button(
                "Telangana State Services",
                OFFICIAL_PORTALS[
                    "Telangana State Services"
                ],
                use_container_width=True
            )

        with col2:

            st.link_button(
                "Telangana MeeSeva",
                OFFICIAL_PORTALS[
                    "Telangana MeeSeva"
                ],
                use_container_width=True
            )

    # --------------------------------------------------------
    # CONVERSATION TITLE
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
