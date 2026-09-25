import unittest
from agent import execute_agent_workflow, AGENT_STAGES, get_api_key
from services_data import SERVICES_DATABASE, search_service_by_query, get_verified_service_by_key


class TestNextStepAgent(unittest.TestCase):

    def test_services_database_completeness(self):
        """Verify that all 5 core supported services exist in the knowledge database."""
        core_services = ["passport", "aadhaar", "pan", "birth_certificate", "property_tax"]
        for s in core_services:
            self.assertIn(s, SERVICES_DATABASE)
            srv = SERVICES_DATABASE[s]
            self.assertIn("title", srv)
            self.assertIn("jurisdiction", srv)
            self.assertIn("official_url", srv)
            self.assertTrue(len(srv["documents"]) > 0)
            self.assertTrue(len(srv["steps"]) > 0)

    def test_search_service_by_query(self):
        """Verify fuzzy keyword searching in local knowledge base."""
        res_passport = search_service_by_query("I want to renew my passport")
        self.assertIsNotNone(res_passport)
        self.assertEqual(res_passport["id"], "passport")

        res_birth = search_service_by_query("need birth registration in GHMC Hyderabad")
        self.assertIsNotNone(res_birth)
        self.assertEqual(res_birth["id"], "birth_certificate")

    def test_agent_workflow_fallback_execution(self):
        """Verify end-to-end fallback execution when API key is None."""
        res = execute_agent_workflow("How to pay GHMC property tax online?", api_key=None)
        self.assertTrue(res["success"])
        self.assertIn("data", res)
        data = res["data"]
        self.assertEqual(data["jurisdiction"], "Telangana")
        self.assertTrue(len(data["documents"]) > 0)
        self.assertTrue(len(data["steps"]) > 0)
        self.assertTrue(data["is_verified_url"])
        self.assertIn("ghmc.gov.in", data["official_url"])

    def test_multi_turn_history_context(self):
        """Verify that follow-up queries resolve using conversation history context."""
        history = [
            {"role": "user", "content": "I need to get a birth certificate for my baby born in GHMC hospital"},
            {"role": "assistant", "content": "Birth certificate guidance"}
        ]
        res = execute_agent_workflow("Show documents", api_key=None, history=history)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["jurisdiction"], "Telangana")

    def test_agent_stages_count(self):
        """Verify 5 defined agent workflow stages."""
        self.assertEqual(len(AGENT_STAGES), 5)


if __name__ == "__main__":
    unittest.main()
