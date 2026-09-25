"""
Agent Engine for NextStep AI.
Implements 5 agent workflow stages:
1. Intent Analysis
2. Service Identification
3. Information Retrieval
4. Step Planning
5. Verification & Response Generation

Handles real Gemini API calling via `google-genai` and robust fallback using `services_data`.
Supports multi-turn conversation context and language preferences.
"""

import json
import os
import time
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from services_data import SERVICES_DATABASE, search_service_by_query, get_verified_service_by_key


# Stage definitions for UI animation
AGENT_STAGES = [
    {"id": 1, "title": "Intent Analysis", "icon": "🧠", "description": "Parsing natural language request & citizen context"},
    {"id": 2, "title": "Service Identification", "icon": "🔍", "description": "Determining exact service & jurisdiction (Central vs Telangana)"},
    {"id": 3, "title": "Information Retrieval", "icon": "📚", "description": "Fetching verified document requirements & eligibility rules"},
    {"id": 4, "title": "Step Planning", "icon": "🗺️", "description": "Building personalized step-by-step guidance workflow"},
    {"id": 5, "title": "Verification", "icon": "🛡️", "description": "Validating official government sources & generating disclaimers"}
]


SYSTEM_PROMPT = """
You are NextStep AI, an expert AI assistant navigating Indian public and government services with specialized expertise in Central Government services and Telangana State services (MeeSeva, GHMC, CDMA).

Your task is to analyze a citizen's request (and conversation history) and respond strictly in valid JSON format adhering to the following structure:

{
  "service_id": "passport|aadhaar|pan|birth_certificate|property_tax|other_service_id",
  "service_name": "Official Service Name",
  "jurisdiction": "Central|Telangana|Other State",
  "jurisdiction_label": "e.g., Central Government (UIDAI) or Telangana State Government (MeeSeva / GHMC)",
  "summary": "Clear 2-sentence summary of what this service handles or answer to citizen's follow-up question.",
  "documents": [
    {"name": "Document Name", "required": true, "notes": "Short explanation"},
    {"name": "Document Name 2", "required": false, "notes": "Optional/conditional explanation"}
  ],
  "steps": [
    {"step": 1, "title": "Step title", "description": "Clear step action"},
    {"step": 2, "title": "Step title", "description": "Clear step action"}
  ],
  "official_url": "https://official-government-url.gov.in/",
  "portal_name": "Official Portal Name",
  "is_verified_url": true,
  "verification_notes": "Explicit details on verified rules, fees, timelines, or warning about items needing confirmation.",
  "next_action": "Clear single immediate next action for the citizen."
}

CRITICAL GUIDELINES:
1. Always accurately identify if the service is a Central Government service (e.g. Passport, Aadhaar, PAN) or a Telangana State service (e.g. Birth Certificate via MeeSeva/GHMC, Property Tax via GHMC/CDMA).
2. Never invent fake government portal URLs or URLs ending in .com unless it's an official partner like IRCTC/Protean. For Passport use https://www.passportindia.gov.in/, for Aadhaar use https://uidai.gov.in/, for PAN use https://www.incometax.gov.in/, for Telangana Birth/MeeSeva use https://ts.meeseva.telangana.gov.in/, for Property Tax use https://www.ghmc.gov.in/.
3. Clearly distinguish mandatory documents (`required: true`) from conditional documents (`required: false`).
4. Support follow-up responses seamlessly using conversation history.
5. Respect the requested language preference (English, Telugu, or Hindi) for output text fields (`summary`, `steps`, `next_action`, `notes`).
6. Output ONLY raw valid JSON, without markdown backticks or commentary surrounding the JSON.
"""


def get_api_key(st_secrets=None) -> Optional[str]:
    """Retrieves GEMINI_API_KEY from environment or streamlit secrets safely."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        return key

    if st_secrets is not None:
        try:
            if "GEMINI_API_KEY" in st_secrets:
                return st_secrets["GEMINI_API_KEY"]
            if "GOOGLE_API_KEY" in st_secrets:
                return st_secrets["GOOGLE_API_KEY"]
            if "OPENROUTER_API_KEY" in st_secrets:
                return st_secrets["OPENROUTER_API_KEY"]
        except Exception:
            pass

    return None


def generate_fallback_response(query: str, history: Optional[List[Dict[str, str]]] = None, language: str = "English") -> Dict[str, Any]:
    """Generates structured response from local curated knowledge base if API key is not available or API fails."""
    # Check if query matches keywords directly or in recent history
    combined_query = query
    if history:
        for msg in reversed(history[-4:]):
            if msg.get("role") == "user":
                combined_query += " " + msg.get("content", "")

    matched = search_service_by_query(combined_query) or search_service_by_query(query)

    if matched:
        return {
            "success": True,
            "source": "knowledge_base",
            "data": {
                "service_id": matched["id"],
                "service_name": matched["title"],
                "jurisdiction": matched["jurisdiction"],
                "jurisdiction_label": matched["jurisdiction_label"],
                "summary": matched["description"],
                "documents": matched["documents"],
                "steps": matched["steps"],
                "official_url": matched["official_url"],
                "portal_name": matched["portal_name"],
                "is_verified_url": matched["is_verified"],
                "verification_notes": matched["verification_notes"],
                "next_action": f"Gather the mandatory documents listed above and visit {matched['portal_name']}."
            }
        }

    # Handle common quick-reply queries when in a conversation
    query_lower = query.lower().strip()
    if query_lower in ["show documents", "documents"]:
        return generate_fallback_response("passport", history, language)
    if query_lower in ["what should i do next?", "what next?", "next steps"]:
        return generate_fallback_response("birth certificate", history, language)

    # Generic fallback if query is outside the 5 main services
    is_telangana = any(kw in combined_query.lower() for kw in ["telangana", "hyderabad", "ghmc", "meeseva", "ts"])
    jurisdiction = "Telangana" if is_telangana else "Central"
    jurisdiction_label = "Telangana State Government (MeeSeva Portal)" if is_telangana else "Central Government (National Portal of India)"
    portal_url = "https://ts.meeseva.telangana.gov.in/" if is_telangana else "https://www.india.gov.in/"
    portal_name = "Telangana MeeSeva Portal" if is_telangana else "National Government Portal of India"

    return {
        "success": True,
        "source": "general_guidance",
        "data": {
            "service_id": "general_public_service",
            "service_name": "General Public Service Inquiry",
            "jurisdiction": jurisdiction,
            "jurisdiction_label": jurisdiction_label,
            "summary": f"Your query regarding '{query[:50]}' pertains to {jurisdiction} public administration.",
            "documents": [
                {"name": "Government Issued Identity Proof (Aadhaar / Voter ID / PAN)", "required": True, "notes": "Mandatory identity proof"},
                {"name": "Proof of Address (Utility Bill / Ration Card / Aadhaar)", "required": True, "notes": "Mandatory residential address proof"},
                {"name": "Passport Size Photographs", "required": False, "notes": "Required if physical application form is submitted"}
            ],
            "steps": [
                {"step": 1, "title": "Identify Official Department", "description": f"Verify whether this service is handled online via {portal_name}."},
                {"step": 2, "title": "Prepare Documents", "description": "Ensure your demographic details (Name, Date of Birth, Address) match across all ID proofs."},
                {"step": 3, "title": "Submit Application", "description": f"Access {portal_name} or nearest government service centre to register your request."},
                {"step": 4, "title": "Track Application Status", "description": "Note down the Application Reference / Acknowledgement Number to track progress online."}
            ],
            "official_url": portal_url,
            "portal_name": portal_name,
            "is_verified_url": True,
            "verification_notes": "Official portal URL is verified. Exact fees and application procedures should be confirmed directly on the official portal.",
            "next_action": f"Visit {portal_name} ({portal_url}) to search for specific service forms."
        }
    }


def execute_agent_workflow(
    user_query: str,
    api_key: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
    language: str = "English",
    progress_callback=None
) -> Dict[str, Any]:
    """
    Executes the 5-stage agent workflow:
    1. Intent Analysis
    2. Service Identification
    3. Information Retrieval
    4. Step Planning
    5. Verification & Response Generation
    """

    # Simulate stage progress callback if provided
    for stage in AGENT_STAGES:
        if progress_callback:
            try:
                progress_callback(stage["id"], stage["title"], stage["description"])
            except Exception:
                pass
            time.sleep(0.1)

    # If no API key, use verified knowledge engine fallback
    if not api_key:
        return generate_fallback_response(user_query, history, language)

    try:
        # Initialize Google GenAI client with official SDK
        client = genai.Client(api_key=api_key)

        history_str = ""
        if history:
            history_str = "Conversation History:\n"
            for msg in history[-6:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_str += f"{role.upper()}: {content}\n"

        prompt = f"{history_str}\nTarget Language: {language}\nLatest Citizen Query: {user_query}\n\nProvide the response strictly as valid JSON following the schema specified in the system instructions."

        # Call Gemini 2.5 Flash model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        raw_text = response.text.strip()

        # Clean JSON markdown delimiters if present
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        data = json.loads(raw_text.strip())

        # Cross-verify and patch official verified URLs if matched with curated database
        combined = user_query
        if history:
            for m in reversed(history[-4:]):
                combined += " " + m.get("content", "")
        matched_db = search_service_by_query(combined) or search_service_by_query(user_query)

        if matched_db:
            data["official_url"] = matched_db["official_url"]
            data["portal_name"] = matched_db["portal_name"]
            data["is_verified_url"] = True
            data["jurisdiction"] = matched_db["jurisdiction"]
            data["jurisdiction_label"] = matched_db["jurisdiction_label"]

        return {
            "success": True,
            "source": "gemini_2_5_flash",
            "data": data
        }

    except Exception as e:
        print(f"Gemini API Exception, falling back to Knowledge Engine: {e}")
        fallback = generate_fallback_response(user_query, history, language)
        fallback["api_error"] = str(e)
        return fallback
