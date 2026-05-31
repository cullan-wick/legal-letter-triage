"""Spine test — run with: python tests/test_spine.py"""
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.graph import run

LETTER = pathlib.Path("samples/debt_collection.txt").read_text()

result = run(LETTER)

assert result["classification"] is not None, "Classification missing"
assert result["urgency_signal"] in ("low", "medium", "high"), "urgency_signal missing or invalid"
assert result["verdict"] is not None, "Verdict missing"
assert result["verdict"]["verdict"] in ("handle_yourself", "consult_lawyer", "urgent")
assert result["draft_response"] is not None, "Draft response missing"
assert len(result["specialist_findings"]) >= 1, "No specialist findings"

print("PASS: Spine test passed")
print(f"  Verdict: {result['verdict']['verdict']}")
print(f"  Latencies: {result['latencies']}")
print(f"  Errors: {result['errors']}")
