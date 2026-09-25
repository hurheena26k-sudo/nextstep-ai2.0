import json
import re
import time

import streamlit as st
from google import genai
from google.genai import types


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="NextStep AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GEMINI
# ============================================================

MODEL_NAME = "gemini-3.8-flash"

try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    client_error = None
except Exception as exc:
    client = None
    client_error = str(exc)


# ============================================================
# AI INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are NextStep AI, an intelligent public-service assistant.

Your purpose is to help citizens understand and navigate legitimate
government and public services.

You can help with:
birth certificates, death certificates, income certificates,
caste certificates, residence certificates, government schemes,
licenses and permits, public grievances, municipal services,
education and scholarships, welfare services, passport services,
Aadhaar services, property tax, water connections, voter services,
employment services, railway services, land services, and other
legitimate public-service requests.

BEHAVIOR:
1. Understand what the citizen actually needs.
2. Do not assume they know the service name.
3. If the request is unclear, ask one useful clarification question.
4. For a clear service request, give practical numbered next steps.
5. Mention documents only when reasonably appropriate.
6. Do not provide an official source for every normal question.
7. Only use service_request when the citizen is actually trying to
   apply for, obtain, renew, download, track, use, or complete a
   government/public service.
8. General questions should stay general.
9. If location matters, ask for the relevant state/city/country.
10. Never invent rules, fees, deadlines, eligibility requirements,
    documents, or websites.
11. Do not include URLs in your answer. The app supplies official
    sources separately.
12. Use the conversation history when it is relevant.
13. Greetings and casual conversation are not service requests.
14. Keep answers concise, useful, professional, and citizen-friendly.

Return ONLY valid JSON with exactly these fields:
{
  "intent": "general" | "clarification" | "service_request",
  "service_key": "service key" | null,
  "title": "short helpful title",
  "summary": "short explanation",
  "steps": ["step 1", "step 2", "step 3"],
  "documents": ["document 1", "document 2"],
  "next_action": "one clear next action",
  "transcript": "what the citizen said"
}

For general questions, steps/documents may be empty.
For clarification, ask the most useful missing question and do not
invent steps.
For service requests, provide useful steps and the correct service_key.

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
other_government_service
"""


# ============================================================
# VERIFIED SOURCE DIRECTORY USED BY THE APP
# ============================================================

SERVICE_LINKS = {
    "birth_certificate": {
        "name": "Birth Certificate",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana State Services",
    },
    "death_certificate": {
        "name": "Death Certificate",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana State Services",
    },
    "income_certificate": {
        "name": "Income Certificate",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva",
    },
    "caste_certificate": {
        "name": "Caste Certificate",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva",
    },
    "residence_certificate": {
        "name": "Residence Certificate",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva",
    },
    "driving_license": {
        "name": "Driving Licence",
        "url": "https://transport.telangana.gov.in/",
        "label": "Official Telangana Transport Department",
    },
    "passport": {
        "name": "Passport",
        "url": "https://www.passportindia.gov.in/",
        "label": "Official Passport Seva",
    },
    "aadhaar": {
        "name": "Aadhaar",
        "url": "https://www.uidai.gov.in/",
        "label": "Official UIDAI",
    },
    "government_schemes": {
        "name": "Government Schemes",
        "url": "https://www.india.gov.in/",
        "label": "Official National Government Portal",
    },
    "public_grievance": {
        "name": "Public Grievance",
        "url": "https://www.india.gov.in/",
        "label": "Official National Government Portal",
    },
    "property_tax": {
        "name": "Property Tax",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana State Services",
    },
    "water_connection": {
        "name": "Water Connection",
        "url": "https://www.telangana.gov.in/services/state-services/",
        "label": "Official Telangana State Services",
    },
    "voter_service": {
        "name": "Voter Services",
        "url": "https://www.india.gov.in/",
        "label": "Official National Government Portal",
    },
    "education_scholarship": {
        "name": "Education / Scholarship",
        "url": "https://telanganaepass.cgg.gov.in/",
        "label": "Official Telangana ePASS",
    },
    "employment": {
        "name": "Employment Services",
        "url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "label": "Official Telangana MeeSeva",
    },
    "railway": {
        "name": "Railway Services",
        "url": "https://www.irctc.co.in/",
        "label": "Official IRCTC",
    },
    "land_services": {
        "name": "Land Services",
        "url": "https://www.telangana.gov.in/",
        "label": "Official Telangana State Portal",
    },
    "other_government_service": {
        "name": "Government Services",
        "url": "https://www.india.gov.in/",
        "label": "Official National Government Portal",
    },
}


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "voice_key" not in st.session_state:
    st.session_state.voice_key = 0

if "last_request_id" not in st.session_state:
    st.session_state.last_request_id = None


# ============================================================
# LIGHT UI STYLING
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1120px;
        padding-top: 1.2rem;
        padding-bottom: 5rem;
    }
    section[data-testid="stSidebar"] {
        border-right: 1px solid #e6eaf0;
    }
    div[data-testid="stChatMessage"] {
        padding-top: 0.35rem;
        padding-bottom: 0.35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def empty_result(title="Something went wrong.", summary=""):
    return {
        "intent": "error",
        "service_key": None,
        "title": title,
        "summary": summary,
        "steps": [],
        "documents": [],
        "next_action": "",
        "transcript": "",
        "content": summary,
        "error": "",
    }


def clean_json(text):
    text = (text or "").strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def normalize_result(data):
    if not isinstance(data, dict):
        return empty_result(
            "Invalid AI response",
            "NextStep AI received an unexpected response format.",
        )

    intent = data.get("intent", "general")
    if intent not in {"general", "clarification", "service_request"}:
        intent = "general"

    service_key = data.get("service_key")
    if intent != "service_request" or service_key not in SERVICE_LINKS:
        service_key = None

    steps = data.get("steps", [])
    documents = data.get("documents", [])

    if not isinstance(steps, list):
        steps = [steps]
    if not isinstance(documents, list):
        documents = [documents]

    summary = str(data.get("summary", data.get("response", "")))
    return {
        "intent": intent,
        "service_key": service_key,
        "title": str(data.get("title", "Here's your Next Step")),
        "summary": summary,
        "steps": [str(x) for x in steps if str(x).strip()],
        "documents": [str(x) for x in documents if str(x).strip()],
        "next_action": str(data.get("next_action", "")),
        "transcript": str(data.get("transcript", "")),
        "content": summary,
        "error": "",
    }


def conversation_context():
    # Keep the prompt compact for speed and lower token usage.
    recent = st.session_state.messages[-8:]
    lines = []

    for message in recent:
        role = message.get("role")
        if role == "user":
            lines.append(f"Citizen: {message.get('content', '')}")
        elif role == "assistant":
            lines.append(
                f"NextStep AI: {message.get('summary', message.get('content', ''))}"
            )

    return "\n".join(lines)


def quota_result(error_text, voice=False):
    title = "Gemini is temporarily busy" if not voice else "Voice is temporarily unavailable"
    summary = (
        "NextStep AI reached Gemini, but the Gemini project is currently "
        "rate-limited or out of available quota. Your app connection is working."
    )

    return {
        "intent": "error",
        "service_key": None,
        "title": title,
        "summary": summary,
        "steps": [
            "Wait a little and try again.",
            "If the problem continues, check the Gemini project's usage and rate limits.",
        ],
        "documents": [],
        "next_action": "Try again after the quota/rate limit becomes available.",
        "transcript": "",
        "content": "",
        "error": error_text,
    }


# ============================================================
# GEMINI TEXT REQUEST
# ============================================================

def get_text_response(user_message):
    if client is None:
        return empty_result(
            "Gemini connection problem",
            "The Gemini client could not be initialized. Check Streamlit Secrets.",
        ) | {"error": client_error or "Unknown client error"}

    history = conversation_context()

    prompt = f"""
{SYSTEM_INSTRUCTION}

RECENT CONVERSATION:
{history if history else "(No previous conversation.)"}

LATEST CITIZEN MESSAGE:
{user_message}

Return ONLY valid JSON.
"""

    # One Gemini request only. No fallback loop, because fallback calls
    # can consume more quota and make a rate-limit problem worse.
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        raw = response.text
        if not raw:
            raise RuntimeError("Gemini returned an empty response.")

        data = json.loads(clean_json(raw))
        return normalize_result(data)

    except Exception as exc:
        error_text = str(exc)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            return quota_result(error_text)

        return {
            **empty_result(
                "Gemini could not process the request",
                "There was a temporary problem while processing your request.",
            ),
            "steps": [
                "Check that the Gemini API key in Streamlit Secrets is active.",
                "Try the request again.",
            ],
            "next_action": "Try again in a moment.",
            "error": error_text,
        }


# ============================================================
# GEMINI VOICE REQUEST
# ============================================================

def get_voice_response(audio_file):
    if client is None:
        return empty_result(
            "Gemini connection problem",
            "The Gemini client could not be initialized. Check Streamlit Secrets.",
        ) | {"error": client_error or "Unknown client error"}

    audio_bytes = audio_file.getvalue()
    mime_type = audio_file.type or "audio/wav"
    history = conversation_context()

    prompt = f"""
{SYSTEM_INSTRUCTION}

The citizen is speaking through a microphone.

First understand what the citizen said, then answer the request.

RECENT CONVERSATION:
{history if history else "(No previous conversation.)"}

The JSON field "transcript" must contain the text understood from
the citizen's audio.

Return ONLY valid JSON.
"""

    try:
        audio_part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type=mime_type,
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, audio_part],
        )

        raw = response.text
        if not raw:
            raise RuntimeError("Gemini returned an empty voice response.")

        data = json.loads(clean_json(raw))
        result = normalize_result(data)

        if not result["transcript"]:
            result["transcript"] = "Voice request received."

        return result

    except Exception as exc:
        error_text = str(exc)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            return quota_result(error_text, voice=True)

        return {
            **empty_result(
                "Voice request could not be processed",
                "Your recording was received, but Gemini could not process it.",
            ),
            "steps": [
                "Try a shorter recording.",
                "Speak clearly and try the microphone again.",
            ],
            "next_action": "Record your request again.",
            "error": error_text,
        }


# ============================================================
# DISPLAY
# ============================================================

def display_response(result):
    if result.get("intent") == "error":
        st.error(f"**{result.get('title', 'Something went wrong.')}**")
        if result.get("summary"):
            st.write(result["summary"])

        if result.get("steps"):
            st.markdown("#### 🛠️ What you can do")
            for i, step in enumerate(result["steps"], 1):
                st.markdown(f"**{i}.** {step}")

        if result.get("next_action"):
            st.info(f"➡️ **Next action:** {result['next_action']}")

        # Keep technical details available without cluttering the UI.
        with st.expander("Technical details"):
            st.code(result.get("error", "No technical details available."))

        return

    st.markdown(f"### ✨ {result.get('title', 'Here is your next step')}")

    if result.get("summary"):
        st.info(result["summary"])

    if result.get("steps"):
        st.markdown("#### 🧭 Your next steps")
        for i, step in enumerate(result["steps"], 1):
            st.markdown(f"**{i}.** {step}")

    if result.get("documents"):
        st.markdown("#### 📋 Keep these ready")
        for document in result["documents"]:
            st.markdown(f"• {document}")

    if result.get("next_action"):
        st.success(f"➡️ **Next action:** {result['next_action']}")

    service_key = result.get("service_key")
    if result.get("intent") == "service_request" and service_key in SERVICE_LINKS:
        service = SERVICE_LINKS[service_key]
        st.link_button(
            f"🔗 Open Official {service['name']} Source",
            service["url"],
            use_container_width=True,
        )
        st.caption(f"Official source: {service['label']}")


def save_result(result):
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result.get("summary", ""),
            "intent": result.get("intent"),
            "service_key": result.get("service_key"),
            "title": result.get("title", ""),
            "summary": result.get("summary", ""),
            "steps": result.get("steps", []),
            "documents": result.get("documents", []),
            "next_action": result.get("next_action", ""),
        }
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🤖 NextStep AI")
    st.caption("Intelligent guidance for public services")

    st.divider()

    if st.button("＋ New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.session_state.voice_key += 1
        st.session_state.last_request_id = None
        st.rerun()

    st.divider()
    st.subheader("💬 Conversations")

    user_messages = [
        m["content"]
        for m in st.session_state.messages
        if m.get("role") == "user"
    ]

    if not user_messages:
        st.caption("Your conversations will appear here.")
    else:
        for i, message in enumerate(user_messages[-8:], 1):
            text = message[:48]
            if len(message) > 48:
                text += "..."
            st.caption(f"{i}. {text}")

    st.divider()
    st.info(
        "💡 **Tip**\n\n"
        "Type your request or use the microphone. "
        "You don't need to know the exact service name."
    )


# ============================================================
# HEADER
# ============================================================

st.title("✦ NextStep AI")
st.caption("Your intelligent guide to public services")


# ============================================================
# WELCOME
# ============================================================

if not st.session_state.messages:
    st.info(
        "### 👋 How can I help you today?\n\n"
        "Tell me what you need in your own words. "
        "NextStep AI will understand your request and guide you."
    )

    st.subheader("✨ Try asking")

    c1, c2 = st.columns(2)

    prompts = [
        ("📄 Apply for an income certificate", "I want to apply for an income certificate in Telangana."),
        ("📜 I need a birth certificate", "I want to apply for a birth certificate in Telangana."),
        ("🚗 I want a driving licence", "I want to apply for a driving licence in Telangana."),
        ("🪪 I need help with Aadhaar", "I need help with my Aadhaar service."),
        ("🎓 Find a government scholarship", "I want to find a government scholarship."),
        ("🛂 I want to apply for a passport", "I want to apply for a passport."),
    ]

    for index, (label, prompt) in enumerate(prompts):
        target = c1 if index % 2 == 0 else c2
        with target:
            if st.button(label, use_container_width=True, key=f"prompt_{index}"):
                st.session_state.pending_prompt = prompt
                st.rerun()

    st.divider()
    st.subheader("Why NextStep AI?")

    a, b, c = st.columns(3)
    with a:
        st.info("🧠 **Understand**\n\nDescribe your problem naturally.")
    with b:
        st.info("🧭 **Guide**\n\nGet clear, practical next steps.")
    with c:
        st.info("🔗 **Connect**\n\nGet an official source for clear service requests.")


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:
    if message.get("role") == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(message.get("content", ""))
    elif message.get("role") == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            display_response(message)


# ============================================================
# SUGGESTED PROMPT PROCESSING
# ============================================================

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    with st.chat_message("user", avatar="👤"):
        st.write(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("✨ NextStep AI is thinking..."):
            result = get_text_response(prompt)
        display_response(result)

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    save_result(result)
    st.rerun()


# ============================================================
# INPUT AREA
# ============================================================

st.divider()
st.markdown("#### 💬 Ask NextStep AI")

text_col, send_col, voice_col = st.columns(
    [7.0, 1.3, 1.7],
    vertical_alignment="bottom",
)

with text_col:
    typed_message = st.text_input(
        "Message",
        placeholder="Tell me what you need help with...",
        label_visibility="collapsed",
        key="message_box",
    )

with send_col:
    send_clicked = st.button(
        "➤ Send",
        use_container_width=True,
    )

with voice_col:
    audio_input = st.audio_input(
        "🎙️",
        sample_rate=16000,
        key=f"voice_input_{st.session_state.voice_key}",
        help="Record your request",
        label_visibility="collapsed",
    )


# ============================================================
# TEXT SEND
# ============================================================

if send_clicked:
    message_to_send = typed_message.strip()

    if not message_to_send:
        st.warning("Please type a request first.")
    else:
        with st.spinner("✨ NextStep AI is thinking..."):
            result = get_text_response(message_to_send)

        st.session_state.messages.append(
            {"role": "user", "content": message_to_send}
        )
        save_result(result)

        # Clear the widget on the next run.
        st.session_state.message_box = ""
        st.rerun()


# ============================================================
# VOICE SEND
# ============================================================

if audio_input is not None:
    with st.spinner("🎙️ Listening and understanding..."):
        result = get_voice_response(audio_input)

    transcript = result.get("transcript") or "Voice request received."

    st.session_state.messages.append(
        {
            "role": "user",
            "content": f"🎙️ {transcript}",
        }
    )
    save_result(result)

    # Move to a new widget key so the same recording is not
    # processed again after rerun.
    st.session_state.voice_key += 1
    st.rerun()
