import unittest
from types import SimpleNamespace
from typing import Optional
from unittest.mock import patch

from src.agents.synthesis import synthesize, synthesize_verdict


def finding(
    agent_name: str,
    *,
    summary: str = "Finding summary.",
    key_points: Optional[list[str]] = None,
    deadlines: Optional[list[str]] = None,
    needs_lawyer: bool = False,
    error: Optional[str] = None,
) -> dict:
    return {
        "agent_name": agent_name,
        "summary": summary,
        "key_points": key_points or [],
        "deadlines": deadlines or [],
        "confidence": "medium",
        "needs_lawyer": needs_lawyer,
        "error": error,
    }


def llm_response(content: str) -> SimpleNamespace:
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


class SynthesisTest(unittest.TestCase):
    def test_urgent_housing_deadline_routes_to_urgent(self) -> None:
        verdict = synthesize(
            {"letter_type": "eviction", "jurisdiction": "CA", "urgency": "medium"},
            [
                finding(
                    "risk",
                    summary="Housing notices can have short response windows.",
                    key_points=["Eviction proceedings may follow."],
                    needs_lawyer=True,
                ),
                finding("rights", key_points=["Local tenant protections can matter."]),
                finding("obligations", deadlines=["within 3 days"]),
            ],
        )

        self.assertEqual(verdict["verdict"], "urgent")
        self.assertIn("within 3 days", verdict["reason"])
        self.assertEqual(verdict["urgent_deadlines"], ["within 3 days"])
        self.assertIn("tenant legal aid", " ".join(verdict["next_steps"]).lower())

    def test_debt_collection_real_deadline_routes_to_consult_lawyer(self) -> None:
        verdict = synthesize(
            {"letter_type": "debt_collection", "jurisdiction": "NY", "urgency": "medium"},
            [
                finding("risk", key_points=["Collection activity may continue."]),
                finding("rights", key_points=["The recipient may request validation."]),
                finding("obligations", deadlines=["within 30 days"]),
            ],
        )

        self.assertEqual(verdict["verdict"], "consult_lawyer")
        self.assertIn("within 30 days", " ".join(verdict["next_steps"]))
        self.assertIn("debt-defense", " ".join(verdict["next_steps"]))

    def test_fallback_deadline_does_not_force_consult_lawyer(self) -> None:
        verdict = synthesize(
            {"letter_type": "general", "jurisdiction": "unknown", "urgency": "medium"},
            [
                finding("risk"),
                finding("rights"),
                finding(
                    "obligations",
                    deadlines=["No explicit deadline detected; still verify dates in the full document."],
                ),
            ],
        )

        self.assertEqual(verdict["verdict"], "handle_yourself")
        self.assertIn("No explicit deadline was confirmed", " ".join(verdict["next_steps"]))

    def test_specialist_lawyer_flag_routes_to_consult_lawyer(self) -> None:
        verdict = synthesize(
            {"letter_type": "employment_warning", "jurisdiction": "WA", "urgency": "medium"},
            [
                finding("risk"),
                finding(
                    "rights",
                    key_points=["Signing a release can affect future claims."],
                    needs_lawyer=True,
                ),
                finding("obligations"),
            ],
        )

        self.assertEqual(verdict["verdict"], "consult_lawyer")
        self.assertIn("legal guidance is needed", verdict["reason"])
        self.assertIn("employment lawyer", " ".join(verdict["next_steps"]).lower())

    def test_failed_specialist_is_ignored_when_other_signals_are_low(self) -> None:
        verdict = synthesize(
            {"letter_type": "general", "jurisdiction": "unknown", "urgency": "medium"},
            [
                finding("risk"),
                finding("rights", error="rights failed", needs_lawyer=True, deadlines=["within 1 day"]),
                finding("obligations"),
            ],
        )

        self.assertEqual(verdict["verdict"], "handle_yourself")

    def test_all_failed_specialists_route_to_consult_lawyer(self) -> None:
        verdict = synthesize(
            {"letter_type": "general", "jurisdiction": "unknown", "urgency": "medium"},
            [
                finding("risk", summary="Risk assessment could not be completed.", error="risk failed"),
                finding("rights", summary="Rights review could not be completed.", error="rights failed"),
                finding(
                    "obligations",
                    summary="Obligations could not be extracted.",
                    deadlines=["Unable to extract deadlines automatically; review the letter for dates."],
                    error="obligations failed",
                ),
            ],
        )

        self.assertEqual(verdict["verdict"], "consult_lawyer")
        self.assertIn("Specialist checks", verdict["reason"])
        self.assertEqual(verdict["urgent_deadlines"], [])

    def test_synthesize_verdict_uses_live_model(self) -> None:
        state = {
            "letter_text": "Sample employment warning.",
            "classification": {"letter_type": "employment_warning", "jurisdiction": "WA", "urgency": "medium"},
            "urgency_signal": "medium",
            "specialist_findings": [
                finding("rights", key_points=["Signing a release can affect future claims."], needs_lawyer=True)
            ],
            "verdict": None,
            "draft_response": None,
            "lawyer_recommendation": None,
            "latencies": {},
            "errors": [],
        }

        with patch(
            "src.agents.synthesis._create_completion",
            return_value=llm_response(
                '{"verdict":"consult_lawyer","reason":"Live synthesis found signing risk.",'
                '"next_steps":["Do not sign yet.","Ask an employment lawyer to review the release."],'
                '"urgent_deadlines":[]}'
            ),
        ) as create:
            result = synthesize_verdict(state)

        create.assert_called_once()
        self.assertEqual(result["verdict"]["verdict"], "consult_lawyer")
        self.assertIn("Live synthesis", result["verdict"]["reason"])
        self.assertIn("synthesis", result["latencies"])
        self.assertEqual(result["errors"], [])

    def test_synthesize_verdict_falls_back_when_live_model_fails(self) -> None:
        state = {
            "letter_text": "Sample employment warning.",
            "classification": {"letter_type": "employment_warning", "jurisdiction": "WA", "urgency": "medium"},
            "urgency_signal": "medium",
            "specialist_findings": [
                finding("rights", key_points=["Signing a release can affect future claims."], needs_lawyer=True)
            ],
            "verdict": None,
            "draft_response": None,
            "lawyer_recommendation": None,
            "latencies": {},
            "errors": [],
        }

        with patch("src.agents.synthesis._create_completion", side_effect=RuntimeError("model down")):
            result = synthesize_verdict(state)

        self.assertEqual(result["verdict"]["verdict"], "consult_lawyer")
        self.assertIn("synthesis: model down", result["errors"])


if __name__ == "__main__":
    unittest.main()
