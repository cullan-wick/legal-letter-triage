from pathlib import Path
import unittest

from src.graph import run_triage


class SpineTest(unittest.TestCase):
    def test_debt_collection_sample_reaches_verdict(self) -> None:
        letter = Path("samples/debt_collection.txt").read_text(encoding="utf-8")
        result = run_triage(letter)

        self.assertEqual(result["classification"]["letter_type"], "debt collection")
        self.assertIn(
            result["verdict"]["value"],
            {"handle_yourself", "consult_lawyer", "urgent"},
        )
        self.assertGreaterEqual(len(result["specialist_findings"]), 3)
        self.assertIsNotNone(result["draft_response"])
        self.assertIn("orchestrator", result["latencies"])


if __name__ == "__main__":
    unittest.main()

