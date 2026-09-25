import streamlit as st
import json
import re
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

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

MODEL_NAME = "gemini-3.8-flash"


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
- Residence/domicile certificates
- Government scheme applications
- Licenses and permits
- Public grievances
- Municipal services
- Education-related government services
- Welfare services
- Passport services
- Aadhaar-related services
- Other legitimate public-service requests

IMPORTANT BEHAVIOR:

1. First understand what the citizen needs.

2. Do not assume that the citizen already knows the exact name
   of the government service.

3. If the citizen describes a problem indirectly, identify the
   possible service they may need.

4. If important information is missing, ask a simple clarification
   question instead of immediately giving a source.

5. When the request is clear enough to identify a service,
   provide practical numbered steps.

6. Give steps BEFORE discussing the official source.

7. Do not provide an official source for every normal question.

8. A source should only be used when the user's request clearly
   corresponds to a specific government service.

9. Never invent government rules, fees, deadlines, eligibility
   requirements, documents, or websites.

10. If the exact procedure depends on location, ask for the relevant
    state/city/country when necessary.

11. If you do not have enough reliable information, clearly say what
    needs to be verified.

12. Do not restrict yourself to a fixed list of services.

13. If the citizen asks a general question such as:
    "What is an income certificate?"
    explain it normally and do not classify it as a service request
    unless they are actually asking to apply, download, renew,
    obtain, track, or use the service.

14. Greetings and casual conversation are NOT service requests.

15. If the citizen's request is outside public services, politely
    explain that your main purpose is helping with public services.

16. Use the conversation history. If the citizen gives information
    across multiple messages, combine the context.

17. For a clear service request, return useful steps that a normal
    citizen can understand.

18. Do not include URLs in your answer. The application will provide
    the official source button separately.

Your response must be returned as valid JSON with exactly these fields:

{
  "intent": "general" | "clarification" | "service_request",
  "service_key": "service key" | null,
  "response": "your response to the citizen"
}

Allowed service_key values include:

birth_certificate
death_certificate
income_certificate
caste_certificate
residence_certificate
driving_license
passport
aadhaar
government_schemes
public_grievance
property_tax
water_connection
voter_service
education_scholarship
employment
railway
land_services
other_government_service
null

Rules for service_key:

- Use a specific key whenever the service is clearly identifiable.
- Use null for general questions.
- Use null when clarification is required.
- If the service is clear but not one of the listed services,
  use "other_government_service".

Response style:

- Friendly
- Clear
- Professional
- Simple enough for ordinary citizens
- Avoid unnecessary technical language
- Do not overwhelm the citizen
"""


# ============================================================
# OFFICIAL SERVICE SOURCES
# ============================================================

SERVICE_LINKS = {

    "birth_certificate": {
        "name": "Birth Certificate",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana Birth Certificate Services"
    },

    "death_certificate": {
        "name": "Death Certificate",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana Death Certificate Services"
    },

    "income_certificate": {
        "name": "Income Certificate",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva"
    },

    "caste_certificate": {
        "name": "Caste Certificate",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva"
    },

    "residence_certificate": {
        "name": "Residence Certificate",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva"
    },

    "driving_license": {
        "name": "Driving Licence",
        "url": "https://transport.telangana.gov.in/",
        "label": "Official Telangana Transport Department"
    },

    "passport": {
        "name": "Passport",
        "url": "https://www.passportindia.gov.in/",
        "label": "Official Passport Seva"
    },

    "aadhaar": {
        "name": "Aadhaar",
        "url": "https://www.uidai.gov.in/",
        "label": "Official UIDAI"
    },

    "government_schemes": {
        "name": "Government Schemes",
        "url": "https://www.india.gov.in/",
        "label": "Official National Government Portal"
    },

    "public_grievance": {
        "name": "Public Grievance",
        "url": "https://www.india.gov.in/",
        "label": "Official Government Services Portal"
    },

    "property_tax": {
        "name": "Property Tax",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana State Services"
    },

    "water_connection": {
        "name": "Water Connection",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana State Services"
    },

    "voter_service": {
        "name": "Voter Services",
        "url": "https://www.india.gov.in/",
        "label": "Official National Government Portal"
    },

    "education_scholarship": {
        "name": "Education / Scholarship",
        "url": "https://telanganaepass.cgg.gov.in/",
        "label": "Official Telangana ePASS"
    },

    "employment": {
        "name": "Employment Services",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva"
    },

    "railway": {
        "name": "Railway Services",
        "url": "https://www.irctc.co.in/",
        "label": "Official IRCTC"
    },

    "land_services": {
        "name": "Land Services",
        "url": "https://www.telangana.gov.in/",
        "label": "Official Telangana State Portal"
    },

    "other_government_service": {
        "name": "Government Services",
        "url": "https://www.india.gov.in/",
        "label": "Official National Government Portal"
    }
}


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 NextStep AI")

    st.caption("Your intelligent public-service assistant")

    st.divider()

    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_started = False
        st.rerun()

    st.divider()

    st.subheader("Previous Conversations")

    if len(st.session_state.messages) == 0:
        st.caption("No previous messages yet.")
    else:
        user_messages = [
            message["content"]
            for message in st.session_state.messages
            if message["role"] == "user"
        ]

        if user_messages:

            for index, message in enumerate(user_messages[-8:]):

                short_message = message[:45]

                if len(message) > 45:
                    short_message += "..."

                st.caption(f"{index + 1}. {short_message}")


# ============================================================
# MAIN HEADER
# ============================================================

st.title("🤖 NextStep AI")

st.write(
    "Tell me what you need help with. "
    "I'll understand your request and guide you to the next step."
)

st.divider()


# ============================================================
# DISPLAY PREVIOUS CHAT
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user"):
            st.write(message["content"])

    elif message["role"] == "assistant":

        with st.chat_message("assistant"):

            st.write(message["content"])

            service_key = message.get("service_key")

            if (
                message.get("intent") == "service_request"
                and service_key in SERVICE_LINKS
            ):

                service = SERVICE_LINKS[service_key]

                st.link_button(
                    f"🔗 Open Official {service['name']} Source",
                    service["url"],
                    use_container_width=True
                )

                st.caption(
                    f"Official source: {service['label']}"
                )


# ============================================================
# GEMINI RESPONSE FUNCTION
# ============================================================

def get_nextstep_response(user_message):

    conversation_text = ""

    for message in st.session_state.messages:

        role = message["role"]

        if role == "user":
            conversation_text += f"Citizen: {message['content']}\n"

        elif role == "assistant":
            conversation_text += f"NextStep AI: {message['content']}\n"

    conversation_text += f"Citizen: {user_message}\n"

    prompt = f"""
{NEXTSTEP_SYSTEM_INSTRUCTION}

Here is the conversation so far:

{conversation_text}

Now respond to the latest citizen message.

Return ONLY valid JSON.

Do not use markdown fences.
Do not add any text before or after the JSON.
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        raw_text = response.text.strip()

        # Remove accidental markdown JSON fences
        raw_text = re.sub(
            r"^```json\s*",
            "",
            raw_text,
            flags=re.IGNORECASE
        )

        raw_text = re.sub(
            r"\s*```$",
            "",
            raw_text
        )

        data = json.loads(raw_text)

        intent = data.get("intent", "general")
        service_key = data.get("service_key")
        answer = data.get("response", "")

        if intent not in [
            "general",
            "clarification",
            "service_request"
        ]:
            intent = "general"

        if service_key not in SERVICE_LINKS:
            service_key = None

        # A source is ONLY allowed for a clear service request.
        if intent != "service_request":
            service_key = None

        return {
            "intent": intent,
            "service_key": service_key,
            "response": answer
        }

    except json.JSONDecodeError:

        return {
            "intent": "general",
            "service_key": None,
            "response": (
                "I understood your request, but I couldn't properly "
                "process the response. Please try asking again."
            )
        }

    except Exception as e:

        return {
            "intent": "general",
            "service_key": None,
            "response": (
                "I'm having trouble connecting to the AI service "
                "right now. Please try again in a moment."
            )
        }


# ============================================================
# CHAT INPUT
# ============================================================

user_message = st.chat_input(
    "What public service do you need help with?"
)


# ============================================================
# PROCESS USER MESSAGE
# ============================================================

if user_message:

    st.session_state.conversation_started = True

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

    # Get AI response
    with st.chat_message("assistant"):

        with st.spinner("NextStep AI is thinking..."):

            result = get_nextstep_response(user_message)

        answer = result["response"]
        intent = result["intent"]
        service_key = result["service_key"]

        # Display AI response
        st.write(answer)

        # ====================================================
        # SHOW SOURCE ONLY FOR CLEAR SERVICE REQUESTS
        # ====================================================

        if (
            intent == "service_request"
            and service_key in SERVICE_LINKS
        ):

            service = SERVICE_LINKS[service_key]

            st.link_button(
                f"🔗 Open Official {service['name']} Source",
                service["url"],
                use_container_width=True
            )

            st.caption(
                f"Official source: {service['label']}"
            )

    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "intent": intent,
            "service_key": service_key
        }
    )
