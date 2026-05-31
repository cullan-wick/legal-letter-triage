import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.agents.lawyer_finder import find_lawyer, recommend_lawyer


def llm_response(content: str) -> SimpleNamespace:
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


class LawyerFinderTest(unittest.TestCase):
    def test_debt_collection_recommendation_is_specific_to_type_and_state(self) -> None:
        recommendation = recommend_lawyer(
            {"letter_type": "debt_collection", "jurisdiction": "California", "urgency": "medium"},
            {"verdict": "consult_lawyer"},
        )

        self.assertIn("Consumer debt defense", recommendation["lawyer_type"])
        self.assertIn("consumer debt defense attorney", recommendation["legal_help_categories"])
        self.assertIn("debt", " ".join(recommendation["questions_to_ask"]).lower())
        self.assertIn("collection letter", " ".join(recommendation["documents_to_prepare"]).lower())
        self.assertIn("California", recommendation["estimated_cost_range"])
        self.assertIn("before the earliest stated deadline", recommendation["urgency_guidance"])

    def test_eviction_urgent_recommendation_prioritizes_same_day_help(self) -> None:
        recommendation = recommend_lawyer(
            {"letter_type": "eviction", "jurisdiction": "unknown", "urgency": "high"},
            {"verdict": "urgent"},
        )

        self.assertIn("Tenant rights", recommendation["lawyer_type"])
        self.assertIn("eviction defense legal aid clinic", recommendation["legal_help_categories"])
        self.assertIn("Lease", recommendation["documents_to_prepare"][0])
        self.assertIn("same-day urgent", recommendation["urgency_guidance"])
        self.assertIn("Jurisdiction was not identified", recommendation["jurisdiction_note"])

    def test_handle_yourself_still_returns_optional_self_help_guidance(self) -> None:
        recommendation = recommend_lawyer(
            {"letter_type": "employment_warning", "jurisdiction": "NY", "urgency": "medium"},
            {"verdict": "handle_yourself"},
        )

        self.assertEqual(recommendation["lawyer_type"], "Employment lawyer")
        self.assertIn("employment attorney", recommendation["legal_help_categories"])
        self.assertIn("severance", " ".join(recommendation["questions_to_ask"]).lower())
        self.assertIn("New York", recommendation["estimated_cost_range"])
        self.assertIn("may not be necessary immediately", recommendation["urgency_guidance"])

    def test_find_lawyer_uses_live_model(self) -> None:
        state = {
            "letter_text": "Sample debt collection letter.",
            "classification": {"letter_type": "debt_collection", "jurisdiction": "CA", "urgency": "medium"},
            "urgency_signal": "medium",
            "specialist_findings": [],
            "verdict": {"verdict": "consult_lawyer", "reason": "Debt collection deadline."},
            "draft_response": None,
            "lawyer_recommendation": None,
            "latencies": {},
            "errors": [],
        }

        with patch(
            "src.agents.lawyer_finder._create_completion",
            return_value=llm_response(
                '{"lawyer_type":"Consumer protection attorney","reason":"Live recommendation tailored to debt collection.",'
                '"questions_to_ask":["Can I request debt validation?","Is there a response deadline?"],'
                '"estimated_cost_range":"Ask about legal aid and limited-scope consults.",'
                '"legal_help_categories":["consumer protection attorney","debt defense legal aid"],'
                '"documents_to_prepare":["Collection letter","Payment records"],'
                '"urgency_guidance":"Schedule a consultation before the earliest deadline.",'
                '"jurisdiction_note":"California referral services may help locate consumer law assistance."}'
            ),
        ) as create:
            result = find_lawyer(state)

        recommendation = result["lawyer_recommendation"]

        create.assert_called_once()
        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation["lawyer_type"], "Consumer protection attorney")
        self.assertIn("legal_help_categories", recommendation)
        self.assertIn("documents_to_prepare", recommendation)
        self.assertIn("urgency_guidance", recommendation)
        self.assertIn("lawyer_finder", result["latencies"])
        self.assertEqual(result["errors"], [])

    def test_find_lawyer_falls_back_when_live_model_fails(self) -> None:
        state = {
            "letter_text": "Sample debt collection letter.",
            "classification": {"letter_type": "debt_collection", "jurisdiction": "CA", "urgency": "medium"},
            "urgency_signal": "medium",
            "specialist_findings": [],
            "verdict": {"verdict": "consult_lawyer", "reason": "Debt collection deadline."},
            "draft_response": None,
            "lawyer_recommendation": None,
            "latencies": {},
            "errors": [],
        }

        with patch("src.agents.lawyer_finder._create_completion", side_effect=RuntimeError("model down")):
            result = find_lawyer(state)

        recommendation = result["lawyer_recommendation"]

        self.assertIsNotNone(recommendation)
        self.assertIn("Consumer debt defense", recommendation["lawyer_type"])
        self.assertEqual(recommendation["live_referrals"], [])
        self.assertEqual(recommendation["error"], "model down")
        self.assertIn("lawyer_finder", result["latencies"])
        self.assertEqual(result["errors"], [])


if __name__ == "__main__":
    unittest.main()
