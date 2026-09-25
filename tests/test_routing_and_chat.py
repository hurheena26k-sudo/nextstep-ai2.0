import unittest
import os
import sys

# Ensure root directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services_data import search_service_by_query, SERVICES_DATABASE
from agent import generate_fallback_response, execute_agent_workflow, transcribe_audio_bytes


class TestRoutingAndChat(unittest.TestCase):

    def test_natural_language_service_routing(self):
        """Test natural language requests map to correct service and NOT Aadhaar default."""
        test_cases = [
            ("I want to apply for a birth certificate", "birth_certificate"),
            ("How do I pay property tax?", "property_tax"),
            ("How can I renew my driving licence?", "driving_licence"),
            ("I need a passport", "passport"),
            ("How do I apply for PAN?", "pan"),
            ("How do I get an income certificate?", "caste_income_certificate"),
            ("I need help with MeeSeva", "caste_income_certificate"),
            ("What documents are required for a caste certificate?", "caste_income_certificate"),
            ("How do I apply for an Aadhaar update?", "aadhaar"),
        ]

        for query, expected_id in test_cases:
            res = generate_fallback_response(query)
            data = res["data"]
            self.assertEqual(
                data["service_id"],
                expected_id,
                f"Query '{query}' expected service '{expected_id}' but got '{data['service_id']}'"
            )

    def test_unrelated_query_asks_clarification(self):
        """Test that unknown/unrelated queries prompt clarification instead of guessing Aadhaar."""
        query = "What is the capital of France?"
        res = generate_fallback_response(query)
        data = res["data"]
        self.assertEqual(data["service_id"], "general_public_service")
        self.assertIsNotNone(data["clarification_needed"])
        self.assertIn("specify", data["clarification_needed"].lower())

    def test_consecutive_questions_state_lifecycle(self):
        """Test consecutive distinct questions do not bleed previous questions or stall state."""
        history = []

        # Question A
        q_a = "I need a passport"
        res_a = generate_fallback_response(q_a, history=history)
        self.assertEqual(res_a["data"]["service_id"], "passport")
        history.append({"role": "user", "content": q_a})
        history.append({"role": "assistant", "card_data": res_a["data"], "content": res_a["data"]["situation_understood"]})

        # Question B
        q_b = "How do I pay property tax?"
        res_b = generate_fallback_response(q_b, history=history)
        self.assertEqual(res_b["data"]["service_id"], "property_tax")
        history.append({"role": "user", "content": q_b})
        history.append({"role": "assistant", "card_data": res_b["data"], "content": res_b["data"]["situation_understood"]})

        # Question C
        q_c = "How can I renew my driving licence?"
        res_c = generate_fallback_response(q_c, history=history)
        self.assertEqual(res_c["data"]["service_id"], "driving_licence")

    def test_followup_question_uses_context(self):
        """Test quick actions like 'show documents' pick up previous service from conversation history."""
        history = [
            {"role": "user", "content": "I need a passport"},
            {"role": "assistant", "card_data": {"service_id": "passport", "service_name": "Passport Services"}}
        ]
        res = generate_fallback_response("show documents", history=history)
        self.assertEqual(res["data"]["service_id"], "passport")

    def test_conversational_intents(self):
        """Test conversational greetings, gratitude, and capability queries."""
        for query in ["Hello", "Thank you", "What can you do?"]:
            res = generate_fallback_response(query)
            data = res["data"]
            self.assertEqual(data["intent"], "conversational")
            self.assertIn("assistant_message", data)
            self.assertGreater(len(data.get("proactive_options", [])), 0)

    def test_ambiguous_clarification(self):
        """Test ambiguous queries ask clarification with options instead of picking Aadhaar."""
        res = generate_fallback_response("I need a certificate")
        data = res["data"]
        self.assertEqual(data["intent"], "clarification")
        self.assertIsNotNone(data.get("clarification_needed"))
        self.assertNotEqual(data.get("service_id"), "aadhaar")
        self.assertGreater(len(data.get("proactive_options", [])), 0)

    def test_process_and_fee_qa(self):
        """Test process questions like fees or timelines return direct QA answers."""
        res_fee = generate_fallback_response("What is the fee for passport?")
        data_fee = res_fee["data"]
        self.assertEqual(data_fee["intent"], "process_qa")
        self.assertIn("1,500", data_fee["assistant_message"])
        self.assertEqual(data_fee["service_id"], "passport")

        res_time = generate_fallback_response("How long does driving licence take?")
        data_time = res_time["data"]
        self.assertEqual(data_time["intent"], "process_qa")
        self.assertEqual(data_time["service_id"], "driving_licence")

    def test_service_discovery(self):
        """Test situation narratives map to service discovery with options."""
        res = generate_fallback_response("I moved to Hyderabad and need to update my address")
        data = res["data"]
        self.assertEqual(data["intent"], "service_discovery")
        self.assertIn("Aadhaar", data["assistant_message"])
        self.assertGreater(len(data.get("proactive_options", [])), 0)

    def test_audio_transcription_and_hash_deduplication(self):
        """Test audio transcription helper and empty audio validation."""
        # Empty audio
        err_res = transcribe_audio_bytes(b"")
        self.assertFalse(err_res["success"])

        # Valid audio bytes simulation
        dummy_audio = b"RIFF" + b"\x00" * 200
        ok_res = transcribe_audio_bytes(dummy_audio)
        self.assertTrue(ok_res["success"])
        self.assertIn("transcription", ok_res)
        self.assertIsNotNone(ok_res.get("hash"))


if __name__ == "__main__":
    unittest.main()
