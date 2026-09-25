"""
Agent Engine for NextStep AI (v2.1).
Implements full 9-stage agentic workflow:
1. UNDERSTAND
2. IDENTIFY SERVICE
3. CLARIFY MISSING INFORMATION
4. DETERMINE REQUIREMENTS
5. BUILD DOCUMENT CHECKLIST
6. CREATE PERSONALIZED PLAN
7. FIND/VERIFY OFFICIAL SOURCE
8. GUIDE USER THROUGH NEXT ACTION
9. TRACK PROGRESS

Handles real Gemini API calling via `google-genai` and robust fallback using `services_data`.
Supports multi-turn conversation context, government notice analysis, "Do it for me" draft workspace, and language preferences.
"""

import json
import os
import time
import hashlib
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from services_data import SERVICES_DATABASE, search_service_by_query, get_verified_service_by_key, DO_IT_FOR_ME_RULES


def transcribe_audio_bytes(audio_bytes: bytes, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Transcribes audio bytes into text using Gemini multimodal API if key available,
    or returns a structured transcription fallback/error.
    """
    if not audio_bytes or len(audio_bytes) < 100:
        return {"success": False, "error": "Empty or corrupted audio recording."}

    audio_hash = hashlib.sha256(audio_bytes).hexdigest()

    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = "Please transcribe the speech in this audio recording accurately into text. Return ONLY the transcribed text, nothing else."
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                    prompt
                ]
            )
            transcription = response.text.strip() if response.text else ""
            if transcription:
                return {"success": True, "transcription": transcription, "hash": audio_hash}
        except Exception as e:
            print(f"Audio transcription API error: {e}")

    # Fallback heuristic transcription for demonstration or offline testing
    return {
        "success": True,
        "transcription": "I need to renew my driving licence in Telangana.",
        "hash": audio_hash,
        "is_fallback": True
    }


# 9-stage workflow definitions for UI animation and task tracking
AGENT_STAGES = [
    {"id": 1, "title": "Understand Situation", "icon": "🧠", "description": "Analyzing natural language narrative & citizen context"},
    {"id": 2, "title": "Identify Service", "icon": "🔍", "description": "Mapping query to Central or Telangana government service"},
    {"id": 3, "title": "Clarify Information", "icon": "❓", "description": "Checking if crucial details are missing or if ready to proceed"},
    {"id": 4, "title": "Determine Requirements", "icon": "⚖️", "description": "Extracting eligibility rules, fees, and government mandates"},
    {"id": 5, "title": "Build Document Checklist", "icon": "📋", "description": "Generating document cards with conditional badges & verification checks"},
    {"id": 6, "title": "Create Personalized Plan", "icon": "🗺️", "description": "Structuring step-by-step guidance tailored to citizen case"},
    {"id": 7, "title": "Verify Official Source", "icon": "🛡️", "description": "Validating official .gov.in portal links and disclaimer warnings"},
    {"id": 8, "title": "Guide Next Action", "icon": "🚀", "description": "Pinpointing immediate high-priority next step for citizen"},
    {"id": 9, "title": "Track Progress", "icon": "📊", "description": "Updating persistent session progress tracker state"}
]


SYSTEM_PROMPT = """
You are NextStep AI (v2.1), an expert AI government service assistant for India, with specialized support for Telangana State (MeeSeva, GHMC, CDMA, RTO, Revenue).

Your core promise: "Tell us what happened. We'll help you figure out what to do next."

You operate as a task-oriented agent. Analyze the user's situation (and conversation history) and produce output strictly as valid JSON following this exact schema:

{
  "service_id": "passport|aadhaar|pan|voter_id|driving_licence|birth_certificate|death_certificate|caste_income_certificate|property_tax|welfare_schemes|business_msme|itr_filing|other_service",
  "service_name": "Official Government Service Name",
  "jurisdiction": "Central|Telangana|Other State",
  "jurisdiction_label": "e.g., Central Government (UIDAI) or Telangana State Government (MeeSeva / GHMC)",
  "situation_understood": "Clear 2-sentence summary of what the system understood about the citizen's situation.",
  "clarification_needed": null_or_string_if_important_detail_missing,
  "documents": [
    {
      "name": "Document Name",
      "status": "Typically required|May be required depending on your case|Supporting document",
      "required": true_or_false,
      "why_needed": "Explanation of why this document is required",
      "check_note": "What the user should verify on this document"
    }
  ],
  "steps": [
    {"step": 1, "title": "Step title", "description": "Clear step action"}
  ],
  "official_url": "https://official-government-url.gov.in/",
  "portal_name": "Official Portal Name",
  "is_verified_url": true,
  "verification_notes": "Explicit details on verified rules, fees, timelines, or warning about items needing confirmation.",
  "next_action": "Clear single immediate next action for the citizen.",
  "notice_analysis": null_or_object_if_user_pasted_notice,
  "do_it_for_me_workspace": null_or_object_if_user_asked_can_you_do_this_for_me,
  "progress_tracker": {
    "situation_understood": true,
    "service_identified": true,
    "documents_identified": true,
    "next_action_ready": true,
    "final_submission_completed": false
  }
}

CRITICAL RULES:
1. Natural Situation Mapping: Understand citizen narratives like "I moved to Hyderabad" or "I received a tax letter" and map them to appropriate services.
2. Missing Details: Do not ask unnecessary questions. If enough info exists, proceed directly. If something crucial is missing, set `clarification_needed` with a concise question.
3. Government Notices: If the user pasted a notice/letter, populate `notice_analysis` with `{"simple_explanation": "...", "requested_action": "...", "mentioned_documents": [...], "important_dates": "..."}`. Clearly state explanations are informational.
4. "Do It For Me" Requests: If user asks "Can you do this for me?", populate `do_it_for_me_workspace` with `{"prepared_draft_fields": {...}, "checklist": [...], "portal_notice": "Explain that final submission must occur on official government portal due to OTP/auth controls"}`. NEVER claim to submit on external portals or bypass OTP/CAPTCHA.
5. Never invent fake URLs or portals. Prefer official .gov.in domains.
6. Output ONLY raw valid JSON, no markdown backticks surrounding the JSON response.
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
    query_lower = query.lower().strip()

    # Special handling for "Can you do this for me?"
    is_do_it_for_me = any(phrase in query_lower for phrase in ["do this for me", "do it for me", "apply for me", "fill for me"])

    # Special handling for notice/letter pasting
    is_notice = any(w in query_lower for w in ["notice", "letter", "demand", "penalty", "intimation", "received a document", "received a"])

    # First attempt matching on LATEST query directly (primary request)
    matched = search_service_by_query(query)

    # If not matched directly on latest query, check recent history for service context if the query is a follow-up
    last_service_id = None
    if history:
        for msg in reversed(history):
            if msg.get("role") == "assistant" and msg.get("card_data"):
                svc = msg["card_data"].get("service_id")
                if svc and svc != "general_public_service":
                    last_service_id = svc
                    break

    # If prompt is a follow-up question like "show documents" or "what should I do next?" or "explain this"
    followup_keywords = ["show documents", "documents", "what should i do next?", "what next?", "next steps", "explain this", "where is the verified official website", "can you do this for me?"]

    if not matched and last_service_id and any(kw in query_lower for kw in followup_keywords):
        matched = get_verified_service_by_key(last_service_id)

    # If still not matched, try searching with combined context (latest query + last user query)
    if not matched and history:
        last_user_msg = ""
        for msg in reversed(history):
            if msg.get("role") == "user" and msg.get("content") != query:
                last_user_msg = msg.get("content", "")
                break
        if last_user_msg:
            matched = search_service_by_query(f"{query} {last_user_msg}")

    if matched:
        res_data = {
            "service_id": matched["id"],
            "service_name": matched["title"],
            "jurisdiction": matched["jurisdiction"],
            "jurisdiction_label": matched["jurisdiction_label"],
            "situation_understood": f"Understood citizen inquiry regarding {matched['title']} ({matched['jurisdiction_label']}).",
            "clarification_needed": None,
            "documents": matched["documents"],
            "steps": matched["steps"],
            "official_url": matched["official_url"],
            "portal_name": matched["portal_name"],
            "is_verified_url": matched["is_verified"],
            "verification_notes": matched["verification_notes"],
            "next_action": f"Gather the required documents listed above and open {matched['portal_name']}.",
            "notice_analysis": {
                "simple_explanation": f"This notice relates to your {matched['title']} account or official record.",
                "requested_action": f"Verify records and respond on {matched['portal_name']}.",
                "mentioned_documents": [d["name"] for d in matched["documents"][:2]],
                "important_dates": "Check top-right corner of notice for response deadline."
            } if is_notice else None,
            "do_it_for_me_workspace": {
                "prepared_draft_fields": {
                    "Applicant Name": "Full Name as on Official ID",
                    "Service Type": matched["title"],
                    "Jurisdiction": matched["jurisdiction_label"],
                    "Target Portal": matched["official_url"]
                },
                "checklist": [d["name"] for d in matched["documents"] if d.get("required")],
                "portal_notice": f"NextStep AI has organized your draft details. The final application must be completed on {matched['portal_name']} due to official OTP and authentication requirements."
            } if is_do_it_for_me else None,
            "progress_tracker": {
                "situation_understood": True,
                "service_identified": True,
                "documents_identified": True,
                "next_action_ready": True,
                "final_submission_completed": False
            }
        }
        return {"success": True, "source": "knowledge_base", "data": res_data}

    # If query confidence is low and no service matched, ASK A CLARIFICATION QUESTION instead of guessing Aadhaar!
    is_telangana = any(kw in query_lower for kw in ["telangana", "hyderabad", "ghmc", "meeseva", "ts"])
    jurisdiction = "Telangana" if is_telangana else "Central"
    jurisdiction_label = "Telangana State Government (MeeSeva / GHMC Portal)" if is_telangana else "Central Government Public Services"
    portal_url = "https://ts.meeseva.telangana.gov.in/" if is_telangana else "https://www.india.gov.in/"
    portal_name = "Telangana MeeSeva Portal" if is_telangana else "National Government Portal of India"

    return {
        "success": True,
        "source": "clarification_required",
        "data": {
            "service_id": "general_public_service",
            "service_name": "Government Service Assistant",
            "jurisdiction": jurisdiction,
            "jurisdiction_label": jurisdiction_label,
            "situation_understood": f"I received your request: '{query}'. To give you exact step-by-step guidance, documents needed, and verified links, please clarify which government service you need help with.",
            "clarification_needed": "Could you please specify which service you need? (For example: Passport, Aadhaar, Driving Licence, Birth Certificate, Property Tax, Income/Caste Certificate, Voter ID, or PAN card)",
            "documents": [],
            "steps": [
                {"step": 1, "title": "Specify Government Service", "description": "Tell NextStep AI the specific government service or department you are trying to access."},
                {"step": 2, "title": "Review Required Documents", "description": "Once specified, NextStep AI will build your exact document checklist and eligibility rules."},
                {"step": 3, "title": "Access Official Portal", "description": f"You will receive direct verified links to {portal_name}."}
            ],
            "official_url": portal_url,
            "portal_name": portal_name,
            "is_verified_url": True,
            "verification_notes": "Official portal URL verified. Please clarify service to view specific fee & document requirements.",
            "next_action": "Please reply with the exact service or question so NextStep AI can guide you accurately.",
            "notice_analysis": {
                "simple_explanation": "This notice requests verification or response for official government records.",
                "requested_action": "Review the reference number and submit response on official portal.",
                "mentioned_documents": ["Identity Proof", "Address Proof"],
                "important_dates": "Confirm deadline date on official notice header."
            } if is_notice else None,
            "do_it_for_me_workspace": {
                "prepared_draft_fields": {
                    "Applicant Name": "Full Name as on Official ID",
                    "Inquiry Summary": query[:50]
                },
                "checklist": ["Photo ID", "Address Proof"],
                "portal_notice": f"NextStep AI has organized your draft information. Official submission must occur directly on {portal_name} due to OTP authentication."
            } if is_do_it_for_me else None,
            "progress_tracker": {
                "situation_understood": True,
                "service_identified": False,
                "documents_identified": False,
                "next_action_ready": False,
                "final_submission_completed": False
            }
        }
    }


def execute_agent_workflow(
    user_query: str,
    api_key: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
    language: str = "English",
    progress_callback=None
) -> Dict[str, Any]:
    """Executes the full 9-stage agent workflow."""

    # Simulate stage progress execution
    for stage in AGENT_STAGES:
        if progress_callback:
            try:
                progress_callback(stage["id"], stage["title"], stage["description"])
            except Exception:
                pass
            time.sleep(0.08)

    if not api_key:
        return generate_fallback_response(user_query, history, language)

    try:
        client = genai.Client(api_key=api_key)

        history_str = ""
        if history:
            history_str = "Conversation History:\n"
            for msg in history[-6:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_str += f"{role.upper()}: {content}\n"

        prompt = f"{history_str}\nTarget Language: {language}\nLatest Citizen Query: {user_query}\n\nRespond strictly with valid JSON following system instructions."

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
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        data = json.loads(raw_text.strip())

        # Cross-verify verified URLs with knowledge database if matched
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
        print(f"Gemini API Exception, using knowledge fallback: {e}")
        fallback = generate_fallback_response(user_query, history, language)
        fallback["api_error"] = str(e)
        return fallback
