import unittest

from src.agents.lawyer_finder import find_lawyer, recommend_lawyer


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

    def test_find_lawyer_updates_state_without_live_search(self) -> None:
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

        result = find_lawyer(state)
        recommendation = result["lawyer_recommendation"]

        self.assertIsNotNone(recommendation)
        self.assertIn("legal_help_categories", recommendation)
        self.assertIn("documents_to_prepare", recommendation)
        self.assertIn("urgency_guidance", recommendation)
        self.assertIn("lawyer_finder", result["latencies"])


if __name__ == "__main__":
    unittest.main()
