import unittest
import os
import sys

# Ensure root folder is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services_data import SERVICES_DATABASE, search_service_by_query, get_verified_service_by_key
from agent import execute_agent_workflow, generate_fallback_response, transcribe_audio_bytes, AGENT_STAGES


class TestNextStepAgent(unittest.TestCase):

    def test_transcribe_audio_bytes_empty(self):
        """Test empty audio handling in voice transcription."""
        res = transcribe_audio_bytes(b"", api_key=None)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "empty_audio")

    def test_transcribe_audio_bytes_fallback(self):
        """Test audio transcription fallback when running locally."""
        dummy_wav = b"RIFF" + b"\x00" * 200
        res = transcribe_audio_bytes(dummy_wav, api_key=None)
        self.assertTrue(res["success"])
        self.assertIn("text", res)

    def test_prompt_isolation_sequential_queries(self):
        """Test that Question A always yields Answer A and Question B yields Answer B even with conversation history."""
        # Query A: GHMC Property Tax
        history = []
        res_a = execute_agent_workflow("How do I pay GHMC property tax?", history=history)
        self.assertEqual(res_a["data"]["service_id"], "property_tax")

        # Append Query A to history
        history.append({"role": "user", "content": "How do I pay GHMC property tax?"})
        history.append({"role": "assistant", "content": "GHMC Property Tax guidance..."})

        # Query B: Passport Application with Question A in history
        res_b = execute_agent_workflow("I want to apply for a fresh passport", history=history)
        self.assertEqual(res_b["data"]["service_id"], "passport")

    def test_services_database_integrity(self):
        """Verify core services database contains expected fields and metadata."""
        self.assertGreaterEqual(len(SERVICES_DATABASE), 12)
        for s_id, s_data in SERVICES_DATABASE.items():
            self.assertIn("title", s_data)
            self.assertIn("jurisdiction", s_data)
            self.assertIn("official_url", s_data)
            self.assertTrue(s_data["official_url"].startswith("http"))
            self.assertIn("documents", s_data)
            self.assertIn("steps", s_data)
            self.assertIn("eligibility", s_data)
            self.assertIn("fees", s_data)
            self.assertIn("processing_time", s_data)
            self.assertIn("form_schema", s_data)

    def test_search_service_by_query(self):
        """Test fuzzy query matching for new and existing services."""
        voter_match = search_service_by_query("I need to apply for a voter id card")
        self.assertIsNotNone(voter_match)
        self.assertEqual(voter_match["id"], "voter_id")

        dl_match = search_service_by_query("How to renew driving licence in Telangana?")
        self.assertIsNotNone(dl_match)
        self.assertEqual(dl_match["id"], "driving_licence")

        tax_match = search_service_by_query("Pay ghmc house tax online")
        self.assertIsNotNone(tax_match)
        self.assertEqual(tax_match["id"], "property_tax")

    def test_form_filling_assistant_payload(self):
        """Test form filling assistant payload generation."""
        res = execute_agent_workflow("My name is Rajesh, DOB 15/08/1995, help me fill form for Passport")
        self.assertTrue(res["success"])
        self.assertIsNotNone(res["data"].get("form_assistant_payload"))
        fp = res["data"]["form_assistant_payload"]
        self.assertIn("form_name", fp)
        self.assertIn("mapped_fields", fp)

    def test_notice_analysis_fallback(self):
        """Test government notice decoding in fallback engine."""
        res = execute_agent_workflow("I received a tax demand notice")
        self.assertTrue(res["success"])
        self.assertIsNotNone(res["data"].get("notice_analysis"))
        self.assertIn("simple_explanation", res["data"]["notice_analysis"])

    def test_do_it_for_me_fallback(self):
        """Test 'Do it for me' mode workspace in fallback engine."""
        res = execute_agent_workflow("Can you do this for me?")
        self.assertTrue(res["success"])
        self.assertIsNotNone(res["data"].get("do_it_for_me_workspace"))
        self.assertIn("prepared_draft_fields", res["data"]["do_it_for_me_workspace"])

    def test_multi_stage_workflow_definitions(self):
        """Test 9-stage workflow definition structure."""
        self.assertEqual(len(AGENT_STAGES), 9)
        self.assertEqual(AGENT_STAGES[0]["title"], "Understand Situation")
        self.assertEqual(AGENT_STAGES[-1]["title"], "Track Progress")


if __name__ == "__main__":
    unittest.main()
