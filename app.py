import base64
import json
import re
import uuid
from datetime import datetime

import requests
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# API CONFIGURATION
# ============================================================

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"

# Free OpenRouter router
OPENROUTER_MODEL = "openrouter/free"

# Latest Sarvam speech models
SARVAM_STT_MODEL = "saaras:v4"
SARVAM_TTS_MODEL = "bulbul:v3"


# ============================================================
# VOICE OPTIONS
# ============================================================

VOICE_OPTIONS = {
    "Ritu · Female": "ritu",
    "Priya · Female": "priya",
    "Aditya · Male": "aditya",
    "Rahul · Male": "rahul",
}


# ============================================================
# LANGUAGE OPTIONS
# ============================================================

LANGUAGE_CODES = {
    "Auto detect": "unknown",
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Telugu": "te-IN",
    "Tamil": "ta-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Marathi": "mr-IN",
    "Bengali": "bn-IN",
    "Gujarati": "gu-IN",
    "Punjabi": "pa-IN",
    "Odia": "od-IN",
}


# ============================================================
# INDIA-WIDE PUBLIC SERVICE CATALOG
# ============================================================

SERVICE_LINKS = {

    "birth_certificate": {
        "name": "Birth Certificate",
        "url": "https://services.india.gov.in/",
        "description": (
            "Find the relevant central or state birth-certificate service."
        ),
    },

    "death_certificate": {
        "name": "Death Certificate",
        "url": "https://services.india.gov.in/",
        "description": (
            "Find the relevant central or state death-certificate service."
        ),
    },

    "income_certificate": {
        "name": "Income Certificate",
        "url": "https://services.india.gov.in/",
        "description": (
            "Find the relevant state or UT income-certificate service."
        ),
    },

    "caste_certificate": {
        "name": "Caste Certificate",
        "url": "https://services.india.gov.in/",
        "description": (
            "Find the relevant state or UT certificate service."
        ),
    },

    "residence_certificate": {
        "name": "Residence / Domicile Certificate",
        "url": "https://services.india.gov.in/",
        "description": (
            "Find the relevant state or UT residence service."
        ),
    },

    "driving_license": {
        "name": "Driving Licence",
        "url": "https://parivahan.gov.in/",
        "description": (
            "Official Parivahan portal for transport and driving-licence services."
        ),
    },

    "passport": {
        "name": "Passport",
        "url": "https://www.passportindia.gov.in/",
        "description": (
            "Official Passport Seva portal."
        ),
    },

    "aadhaar": {
        "name": "Aadhaar",
        "url": "https://uidai.gov.in/",
        "description": (
            "Official UIDAI portal."
        ),
    },

    "government_schemes": {
        "name": "Government Schemes",
        "url": "https://www.india.gov.in/my-government/schemes",
        "description": (
            "Explore national government schemes and related information."
        ),
    },

    "public_grievance": {
        "name": "Public Grievance",
        "url": "https://pgportal.gov.in/",
        "description": (
            "Official CPGRAMS public-grievance portal."
        ),
    },

    "property_tax": {
        "name": "Property Tax",
        "url": "https://services.india.gov.in/",
        "description": (
            "Locate the relevant municipal or state property-tax service."
        ),
    },

    "water_connection": {
        "name": "Water / Sewerage Service",
        "url": "https://services.india.gov.in/",
        "description": (
            "Locate the relevant local water or sewerage service."
        ),
    },

    "voter_service": {
        "name": "Voter Services",
        "url": "https://voters.eci.gov.in/",
        "description": (
            "Official Election Commission voter-services portal."
        ),
    },

    "education_scholarship": {
        "name": "Education / Scholarship",
        "url": "https://www.india.gov.in/",
        "description": (
            "Start from the national government portal and identify "
            "the applicable scheme."
        ),
    },

    "employment": {
        "name": "Employment Services",
        "url": "https://www.ncs.gov.in/",
        "description": (
            "Official National Career Service portal."
        ),
    },

    "railway": {
        "name": "Railway Services",
        "url": "https://www.irctc.co.in/",
        "description": (
            "Official IRCTC portal for ticketing and related services."
        ),
    },

    "land_services": {
        "name": "Land / Property Records",
        "url": "https://services.india.gov.in/",
        "description": (
            "Locate the relevant state or UT land-record service."
        ),
    },

    "municipal_service": {
        "name": "Municipal Service",
        "url": "https://services.india.gov.in/",
        "description": (
            "Locate the relevant city or municipal service."
        ),
    },

    "other_government_service": {
        "name": "Government Services",
        "url": "https://services.india.gov.in/",
        "description": (
            "Search India's official government-services directory."
        ),
    },
}


# ============================================================
# NEXTSTEP AI SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """

You are NextStep AI, an agentic public-service assistant for citizens in India.

Your job is not simply to chat.

Your job is to:

1. Understand the citizen's goal.
2. Identify the likely public-service category.
3. Detect missing information.
4. Ask useful clarification questions when necessary.
5. Decide the next appropriate action.
6. Guide the citizen through the process.
7. Connect them to an official service route when appropriate.

You can help with national, state, UT, municipal and other legitimate
public services across India.

Examples include:

- Birth certificates
- Death certificates
- Income certificates
- Caste certificates
- Residence certificates
- Aadhaar
- Passports
- Voter services
- Driving licences
- Government schemes
- Scholarships
- Employment services
- Public grievances
- Property tax
- Water services
- Railway services
- Land records
- Municipal complaints
- Licenses
- Permits
- Other legitimate government services

IMPORTANT AGENT BEHAVIOUR:

1. Understand the citizen's actual goal in natural language.

2. Do not require the citizen to know the official service name.

3. If the citizen describes a problem indirectly, identify the likely
   government/public-service category.

4. If location is necessary, ask for the state, city or PIN code.
   Never invent the citizen's location.

5. If important information is missing, ask ONE useful clarification question.

6. If the request is clear, provide practical numbered steps.

7. Never invent:
   - fees
   - deadlines
   - eligibility rules
   - government policies
   - documents
   - URLs

8. Use the service catalog supplied by the application.

9. General questions are not automatically service requests.

10. Greetings and casual conversation are allowed.

11. If the citizen reports a civic problem such as a broken streetlight,
    water problem, waste problem, road problem or drainage problem,
    identify the likely public-service route and ask for location when needed.

12. Keep answers concise and citizen-friendly.

13. Do not create URLs in your response.
    The application supplies official links separately.

14. If a government action has NOT actually been performed,
    never claim that it was completed.

15. You are an agentic assistant:
    understand -> decide -> ask -> route -> guide -> next action.

RETURN ONLY VALID JSON.

Use exactly these fields:

{
  "intent": "general" | "clarification" | "service_request" | "agent_action",
  "service_key": "service key" | null,
  "title": "short title",
  "summary": "short helpful explanation",
  "steps": ["step 1", "step 2"],
  "documents": ["document 1"],
  "next_action": "one clear next action",
  "clarification_question": "question if needed, otherwise empty",
  "language": "language code",
  "transcript": "what the citizen said"
}

Allowed service_key values:

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
municipal_service
other_government_service

Use null for service_key when:

- the request is general
- clarification is required
- no service has been identified

STYLE:

- Friendly
- Professional
- Clear
- Practical
- Citizen-friendly
- Concise
- Make the next action obvious
"""


# ============================================================
# API KEYS
# ============================================================

OPENROUTER_API_KEY = st.secrets.get(
    "OPENROUTER_API_KEY",
    ""
)

SARVAM_API_KEY = st.secrets.get(
    "SARVAM_API_KEY",
    ""
)


# ============================================================
# SESSION STATE
# ============================================================

def new_conversation():

    return {
        "id": str(uuid.uuid4()),
        "title": "New conversation",
        "created": datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        ),
        "messages": [],
    }


if "conversations" not in st.session_state:

    first_conversation = new_conversation()

    st.session_state.conversations = [
        first_conversation
    ]

    st.session_state.active_id = (
        first_conversation["id"]
    )


if "voice_language" not in st.session_state:

    st.session_state.voice_language = (
        "Auto detect"
    )


if "tts_voice" not in st.session_state:

    st.session_state.tts_voice = (
        "Ritu · Female"
    )


if "voice_output" not in st.session_state:

    st.session_state.voice_output = True


# ============================================================
# CONVERSATION FUNCTIONS
# ============================================================

def get_active_conversation():

    for conversation in st.session_state.conversations:

        if conversation["id"] == st.session_state.active_id:

            return conversation

    first = new_conversation()

    st.session_state.conversations.append(
        first
    )

    st.session_state.active_id = first["id"]

    return first


def create_new_conversation():

    conversation = new_conversation()

    st.session_state.conversations.insert(
        0,
        conversation
    )

    st.session_state.active_id = (
        conversation["id"]
    )


def delete_conversation(conversation_id):

    st.session_state.conversations = [
        conversation
        for conversation in st.session_state.conversations
        if conversation["id"] != conversation_id
    ]

    if not st.session_state.conversations:

        create_new_conversation()

    else:

        st.session_state.active_id = (
            st.session_state.conversations[0]["id"]
        )


# ============================================================
# INTERFACE THEME
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1180px;
        padding-top: 1.4rem;
        padding-bottom: 7rem;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(120,120,120,.15);
    }

    .hero {
        padding: 1rem 0 .8rem 0;
    }

    .hero h1 {
        font-size: 2.5rem;
        margin-bottom: .2rem;
    }

    .hero p {
        color: #667085;
        font-size: 1.05rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("# 🤖 NextStep AI")

    st.caption(
        "Agentic public-service assistant for India"
    )

    st.divider()

    if st.button(
        "＋ New conversation",
        use_container_width=True,
        type="primary",
    ):

        create_new_conversation()

        st.rerun()

    st.divider()

    st.subheader(
        "💬 Previous conversations"
    )

    for conversation in (
        st.session_state.conversations[:12]
    ):

        title = conversation["title"]

        if len(title) > 34:

            title = title[:34] + "…"

        cols = st.columns([5, 1])

        with cols[0]:

            if st.button(
                title,
                key=f"open_{conversation['id']}",
                use_container_width=True,
            ):

                st.session_state.active_id = (
                    conversation["id"]
                )

                st.rerun()

        with cols[1]:

            if st.button(
                "×",
                key=f"delete_{conversation['id']}",
            ):

                delete_conversation(
                    conversation["id"]
                )

                st.rerun()

    st.divider()

    st.subheader("🎙️ Voice settings")

    st.session_state.voice_language = (
        st.selectbox(
            "Input language",
            list(LANGUAGE_CODES.keys()),
            index=list(
                LANGUAGE_CODES.keys()
            ).index(
                st.session_state.voice_language
            ),
        )
    )

    st.session_state.tts_voice = (
        st.selectbox(
            "AI voice",
            list(VOICE_OPTIONS.keys()),
            index=list(
                VOICE_OPTIONS.keys()
            ).index(
                st.session_state.tts_voice
            ),
        )
    )

    st.session_state.voice_output = (
        st.toggle(
            "🔊 Speak AI responses",
            value=st.session_state.voice_output,
        )
    )

    st.divider()

    st.subheader(
        "🔌 Connection status"
    )

    if OPENROUTER_API_KEY:

        st.success(
            "OpenRouter connected"
        )

    else:

        st.error(
            "OpenRouter key missing"
        )

    if SARVAM_API_KEY:

        st.success(
            "Sarvam connected"
        )

    else:

        st.warning(
            "Sarvam key missing"
        )

    st.caption(
        "Sarvam voice features use your available Sarvam credits."
    )


# ============================================================
# JSON CLEANER
# ============================================================

def safe_json(text):

    text = (
        text or ""
    ).strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    try:

        return json.loads(text)

    except Exception:

        match = re.search(
            r"\{.*\}",
            text,
            flags=re.DOTALL,
        )

        if match:

            return json.loads(
                match.group(0)
            )

        raise ValueError(
            "The AI returned invalid JSON."
        )


# ============================================================
# RESULT NORMALIZER
# ============================================================

def normalize_result(
    data,
    fallback_text="",
):

    intent = data.get(
        "intent",
        "general",
    )

    allowed_intents = {
        "general",
        "clarification",
        "service_request",
        "agent_action",
    }

    if intent not in allowed_intents:

        intent = "general"

    service_key = data.get(
        "service_key"
    )

    if service_key not in SERVICE_LINKS:

        service_key = None

    if intent not in {
        "service_request",
        "agent_action",
    }:

        service_key = None

    steps = data.get(
        "steps",
        [],
    )

    documents = data.get(
        "documents",
        [],
    )

    if not isinstance(
        steps,
        list,
    ):

        steps = [steps]

    if not isinstance(
        documents,
        list,
    ):

        documents = [documents]

    return {

        "intent": intent,

        "service_key": service_key,

        "title": str(
            data.get(
                "title",
                "Your Next Step",
            )
        ),

        "summary": str(
            data.get(
                "summary",
                fallback_text,
            )
        ),

        "steps": [
            str(item)
            for item in steps
            if str(item).strip()
        ],

        "documents": [
            str(item)
            for item in documents
            if str(item).strip()
        ],

        "next_action": str(
            data.get(
                "next_action",
                "Continue with the next step above.",
            )
        ),

        "clarification_question": str(
            data.get(
                "clarification_question",
                "",
            )
        ),

        "language": str(
            data.get(
                "language",
                "en-IN",
            )
        ),

        "transcript": str(
            data.get(
                "transcript",
                fallback_text,
            )
        ),

        "content": str(
            data.get(
                "summary",
                fallback_text,
            )
        ),
    }


# ============================================================
# BUILD AI HISTORY
# ============================================================

def build_ai_messages(
    latest_user,
):

    active = get_active_conversation()

    history = []

    for message in (
        active["messages"][-12:]
    ):

        if message["role"] == "user":

            history.append(
                {
                    "role": "user",
                    "content": message["content"],
                }
            )

        elif message["role"] == "assistant":

            history.append(
                {
                    "role": "assistant",
                    "content": message.get(
                        "content",
                        "",
                    ),
                }
            )

    history.append(
        {
            "role": "user",
            "content": latest_user,
        }
    )

    service_catalog = "\n".join(
        f"{key}: {value['name']}"
        for key, value in SERVICE_LINKS.items()
    )

    complete_system_prompt = (
        SYSTEM_PROMPT
        + "\n\nSERVICE CATALOG:\n"
        + service_catalog
    )

    return [
        {
            "role": "system",
            "content": complete_system_prompt,
        }
    ] + history


# ============================================================
# OPENROUTER AI
# ============================================================

def openrouter_chat(
    user_text,
):

    if not OPENROUTER_API_KEY:

        raise RuntimeError(
            "OPENROUTER_API_KEY is missing from Streamlit Secrets."
        )

    payload = {

        "model": OPENROUTER_MODEL,

        "messages": build_ai_messages(
            user_text
        ),

        "temperature": 0.2,

        "max_tokens": 900,
    }

    headers = {

        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "HTTP-Referer":
            "https://nextstep-ai.streamlit.app",

        "X-Title":
            "NextStep AI",
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:

        raise RuntimeError(
            f"OpenRouter error "
            f"{response.status_code}: "
            f"{response.text[:800]}"
        )

    body = response.json()

    choices = body.get(
        "choices",
        [],
    )

    if not choices:

        raise RuntimeError(
            "OpenRouter returned no choices."
        )

    content = (
        choices[0]
        .get("message", {})
        .get("content", "")
    )

    if isinstance(
        content,
        list,
    ):

        content = "".join(
            item.get(
                "text",
                "",
            )
            if isinstance(
                item,
                dict,
            )
            else str(item)
            for item in content
        )

    if not content:

        raise RuntimeError(
            "OpenRouter returned an empty response."
        )

    data = safe_json(
        content
    )

    return normalize_result(
        data,
        fallback_text=user_text,
    )


# ============================================================
# SARVAM SPEECH TO TEXT
# ============================================================

def sarvam_transcribe(
    audio_bytes,
):

    if not SARVAM_API_KEY:

        raise RuntimeError(
            "SARVAM_API_KEY is missing from Streamlit Secrets."
        )

    language_code = LANGUAGE_CODES[
        st.session_state.voice_language
    ]

    files = {

        "file": (
            "nextstep_voice.wav",
            audio_bytes,
            "audio/wav",
        )

    }

    data = {

        "model":
            SARVAM_STT_MODEL,

        "mode":
            "transcribe",

        "language_code":
            language_code,

        "keyterms":
            json.dumps(
                [
                    "NextStep AI",
                    "Aadhaar",
                    "MeeSeva",
                    "CPGRAMS",
                    "Parivahan",
                    "Passport Seva",
                    "UIDAI",
                    "government scheme",
                    "public grievance",
                ]
            ),
    }

    headers = {

        "api-subscription-key":
            SARVAM_API_KEY,
    }

    response = requests.post(
        SARVAM_STT_URL,
        headers=headers,
        files=files,
        data=data,
        timeout=45,
    )

    if response.status_code != 200:

        raise RuntimeError(
            f"Sarvam STT error "
            f"{response.status_code}: "
            f"{response.text[:800]}"
        )

    body = response.json()

    transcript = str(
        body.get(
            "transcript",
            "",
        )
    ).strip()

    detected_language = (
        body.get(
            "language_code"
        )
        or language_code
    )

    if not transcript:

        raise RuntimeError(
            "Sarvam did not detect any speech. "
            "Please try speaking again."
        )

    return (
        transcript,
        detected_language,
    )


# ============================================================
# SARVAM TEXT TO SPEECH
# ============================================================

def sarvam_tts(
    text,
    language_code,
    speaker,
):

    if not SARVAM_API_KEY:

        return None

    if not text:

        return None

    supported_languages = {
        code
        for code in LANGUAGE_CODES.values()
        if code != "unknown"
    }

    if (
        language_code == "unknown"
        or language_code not in supported_languages
    ):

        language_code = "en-IN"

    payload = {

        "text":
            text[:2500],

        "language_code":
            language_code,

        "speaker":
            speaker,

        "model":
            SARVAM_TTS_MODEL,

        "pace":
            1.0,

        "speech_sample_rate":
            24000,

        "output_audio_codec":
            "wav",

        "temperature":
            0.6,
    }

    headers = {

        "api-subscription-key":
            SARVAM_API_KEY,

        "Content-Type":
            "application/json",
    }

    response = requests.post(
        SARVAM_TTS_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:

        return None

    body = response.json()

    audios = body.get(
        "audios",
        [],
    )

    if not audios:

        return None

    return base64.b64decode(
        audios[0]
    )


# ============================================================
# PROCESS USER MESSAGE
# ============================================================

def process_user_message(
    text,
    source="text",
    detected_language="en-IN",
):

    active = get_active_conversation()

    text = text.strip()

    if not text:

        return

    active["messages"].append(
        {
            "role": "user",
            "content": text,
            "source": source,
        }
    )

    if (
        active["title"]
        == "New conversation"
    ):

        active["title"] = (
            text[:45]
            + (
                "…"
                if len(text) > 45
                else ""
            )
        )

    with st.status(
        "🧠 NextStep AI is working…",
        expanded=True,
    ) as status:

        st.write(
            "Understanding your request"
        )

        st.write(
            "Identifying the likely public-service route"
        )

        st.write(
            "Checking what information is missing"
        )

        result = openrouter_chat(
            text
        )

        st.write(
            "Preparing your next action"
        )

        status.update(
            label="✅ Agent completed",
            state="complete",
            expanded=False,
        )

    result[
        "detected_language"
    ] = detected_language

    active["messages"].append(
        {
            "role": "assistant",
            "content": result[
                "summary"
            ],
            "result": result,
        }
    )

    # --------------------------------------------------------
    # OPTIONAL VOICE RESPONSE
    # --------------------------------------------------------

    if (
        st.session_state.voice_output
        and SARVAM_API_KEY
    ):

        audio = sarvam_tts(
            result["summary"],
            detected_language,
            VOICE_OPTIONS[
                st.session_state.tts_voice
            ],
        )

        if audio:

            result["audio"] = audio


# ============================================================
# HERO
# ============================================================

active = get_active_conversation()

st.markdown(
    '<div class="hero">',
    unsafe_allow_html=True,
)

st.markdown(
    "# ✦ NextStep AI"
)

st.markdown(
    "**Your intelligent guide to India's public services**"
)

st.markdown(
    "Describe what you need. NextStep AI understands your goal, "
    "asks for missing details, identifies the right service route, "
    "and guides you to the next action."
)

st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# WELCOME SCREEN
# ============================================================

if not active["messages"]:

    st.info(
        "👋 **What do you need help with today?**\n\n"
        "You can type naturally or use the microphone."
    )

    st.subheader(
        "✨ Quick actions"
    )

    quick_cols = st.columns(4)

    quick_actions = [

        (
            "📄 Certificate",
            "I need help getting a government certificate.",
        ),

        (
            "🏛️ Scheme",
            "I want to find a government scheme I may be eligible for.",
        ),

        (
            "🚨 Complaint",
            "I want to report a public-service or civic problem.",
        ),

        (
            "🪪 ID / Passport",
            "I need help with Aadhaar, voter services, or passport services.",
        ),
    ]

    for column, (
        label,
        prompt,
    ) in zip(
        quick_cols,
        quick_actions,
    ):

        with column:

            if st.button(
                label,
                use_container_width=True,
            ):

                try:

                    process_user_message(
                        prompt
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        str(error)
                    )

    st.divider()

    st.subheader(
        "Why NextStep AI?"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "🧠 **Understand**\n\n"
            "Explain your problem naturally."
        )

    with col2:

        st.info(
            "🧭 **Decide**\n\n"
            "The AI identifies the likely service route."
        )

    with col3:

        st.info(
            "⚡ **Next Step**\n\n"
            "Get a clear action instead of information overload."
        )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in active["messages"]:

    if message["role"] == "user":

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            st.write(
                message["content"]
            )

            if (
                message.get(
                    "source"
                )
                == "voice"
            ):

                st.caption(
                    "🎙️ Voice input"
                )

    else:

        result = message.get(
            "result",
            {},
        )

        with st.chat_message(
            "assistant",
            avatar="🤖",
        ):

            st.markdown(
                f"### ✨ {result.get('title', 'Your Next Step')}"
            )

            st.info(
                result.get(
                    "summary",
                    message.get(
                        "content",
                        "",
                    ),
                )
            )

            if result.get(
                "clarification_question"
            ):

                st.warning(
                    "❓ "
                    + result[
                        "clarification_question"
                    ]
                )

            if result.get(
                "steps"
            ):

                st.markdown(
                    "#### 🧭 Steps"
                )

                for number, step in enumerate(
                    result["steps"],
                    start=1,
                ):

                    st.markdown(
                        f"**{number}.** {step}"
                    )

            if result.get(
                "documents"
            ):

                st.markdown(
                    "#### 📋 Keep these ready"
                )

                for document in (
                    result["documents"]
                ):

                    st.markdown(
                        f"• {document}"
                    )

            if result.get(
                "next_action"
            ):

                st.success(
                    "➡️ **Next action:** "
                    + result[
                        "next_action"
                    ]
                )

            service_key = result.get(
                "service_key"
            )

            if service_key in SERVICE_LINKS:

                service = SERVICE_LINKS[
                    service_key
                ]

                st.markdown(
                    "#### 🔗 Official route"
                )

                st.link_button(
                    f"Open official {service['name']} service",
                    service["url"],
                    use_container_width=True,
                )

                st.caption(
                    service["description"]
                )

            if result.get(
                "transcript"
            ):

                with st.expander(
                    "🎙️ Voice transcript"
                ):

                    st.write(
                        result[
                            "transcript"
                        ]
                    )

            if result.get(
                "audio"
            ):

                st.audio(
                    result["audio"],
                    format="audio/wav",
                )


# ============================================================
# INPUT AREA
# ============================================================

st.divider()

voice_col, text_col = st.columns(
    [1, 2.8]
)


# ============================================================
# VOICE INPUT
# ============================================================

with voice_col:

    st.markdown(
        "**🎙️ Voice command**"
    )

    audio_value = st.audio_input(
        "Record",
        sample_rate=16000,
        key="nextstep_microphone",
        help=(
            "Tap the microphone, speak, then send the recording."
        ),
        label_visibility="collapsed",
    )

    if audio_value:

        st.audio(
            audio_value,
            format="audio/wav",
        )

        if st.button(
            "🎙️ Send voice",
            use_container_width=True,
            type="primary",
        ):

            try:

                with st.spinner(
                    "🎧 Understanding your voice…"
                ):

                    transcript, language = (
                        sarvam_transcribe(
                            audio_value.getvalue()
                        )
                    )

                process_user_message(
                    transcript,
                    source="voice",
                    detected_language=language,
                )

                st.rerun()

            except Exception as error:

                st.error(
                    str(error)
                )


# ============================================================
# TEXT INPUT
# ============================================================

with text_col:

    st.markdown(
        "**💬 Type your request**"
    )

    typed = st.chat_input(
        "Example: I need to report a broken streetlight in my area"
    )

    if typed:

        try:

            process_user_message(
                typed,
                source="text",
            )

            st.rerun()

        except Exception as error:

            st.error(
                str(error)
            )


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "NextStep AI • OpenRouter intelligence + Sarvam voice • "
    "Built for public-service guidance"
)
