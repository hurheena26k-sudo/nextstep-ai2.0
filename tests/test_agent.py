import unittest
import os
import sys

# Ensure root folder is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services_data import SERVICES_DATABASE, search_service_by_query, get_verified_service_by_key
from agent import execute_agent_workflow, generate_fallback_response, AGENT_STAGES


class TestNextStepAgent(unittest.TestCase):

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
            for doc in s_data["documents"]:
                self.assertIn("name", doc)
                self.assertIn("status", doc)
                self.assertIn("why_needed", doc)

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
