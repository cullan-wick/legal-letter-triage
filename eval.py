"""
Weave Evaluation — Legal Letter Triage
Run: venv\Scripts\python.exe eval.py
Opens results at wandb.ai under the legal-letter-triage project.
"""

import asyncio
import pathlib
import weave
from src.graph import run

# ── Dataset ───────────────────────────────────────────────────────────────────

DATASET = weave.Dataset(
    name="legal-letter-triage-samples",
    rows=[
        {
            "id": "debt-collection",
            "letter_text": pathlib.Path("samples/debt_collection.txt").read_text(),
            "expected_verdict_family": ["consult_lawyer", "urgent"],
            "expected_letter_type_keyword": "debt",
            "description": "Debt collection letter with 15-day deadline and lawsuit threat",
        },
        {
            "id": "eviction-notice",
            "letter_text": pathlib.Path("samples/eviction_notice.txt").read_text(),
            "expected_verdict_family": ["consult_lawyer", "urgent"],
            "expected_letter_type_keyword": "eviction",
            "description": "3-day eviction notice with unpaid rent and lease violation",
        },
        {
            "id": "employment-warning",
            "letter_text": pathlib.Path("samples/employment_warning.txt").read_text(),
            "expected_verdict_family": ["handle_yourself", "consult_lawyer"],
            "expected_letter_type_keyword": "employment",
            "description": "Formal employment warning with 90-day performance period",
        },
    ],
)


# ── Model (wraps the full agent graph) ───────────────────────────────────────

@weave.op()
def triage_model(letter_text: str) -> dict:
    """Run the full multi-agent graph and return structured output."""
    result = run(letter_text)
    return {
        "verdict": result.get("verdict", {}).get("verdict", "unknown"),
        "reason": result.get("verdict", {}).get("reason", ""),
        "letter_type": result.get("classification", {}).get("letter_type", "unknown"),
        "urgency": result.get("classification", {}).get("urgency", "unknown"),
        "specialist_count": len(result.get("specialist_findings", [])),
        "has_draft_response": result.get("draft_response") is not None,
        "has_lawyer_recommendation": result.get("lawyer_recommendation") is not None,
        "errors": result.get("errors", []),
        "latencies": result.get("latencies", {}),
    }


# ── Scorers ───────────────────────────────────────────────────────────────────

@weave.op()
def verdict_is_valid(output: dict, **_) -> dict:
    """Verdict must be one of the three allowed values."""
    verdict = output.get("verdict", "unknown")
    valid = verdict in ("handle_yourself", "consult_lawyer", "urgent")
    return {"valid_verdict": valid, "score": 1.0 if valid else 0.0}


@weave.op()
def verdict_in_expected_family(output: dict, expected_verdict_family: list, **_) -> dict:
    """Verdict should match the expected risk level for this letter type."""
    verdict = output.get("verdict", "unknown")
    match = verdict in expected_verdict_family
    return {"verdict_match": match, "verdict": verdict, "score": 1.0 if match else 0.0}


@weave.op()
def letter_classified_correctly(output: dict, expected_letter_type_keyword: str, **_) -> dict:
    """Orchestrator should identify the correct letter category."""
    letter_type = output.get("letter_type", "unknown")
    correct = expected_letter_type_keyword.lower() in letter_type.lower()
    return {"correct_classification": correct, "letter_type": letter_type, "score": 1.0 if correct else 0.0}


@weave.op()
def all_specialists_ran(output: dict, **_) -> dict:
    """All 3 specialist agents (risk, rights, obligations) must run."""
    count = output.get("specialist_count", 0)
    complete = count >= 3
    return {"all_specialists_ran": complete, "count": count, "score": 1.0 if complete else count / 3}


@weave.op()
def response_was_drafted(output: dict, **_) -> dict:
    """A response letter must always be drafted."""
    drafted = output.get("has_draft_response", False)
    return {"drafted": drafted, "score": 1.0 if drafted else 0.0}


@weave.op()
def no_agent_errors(output: dict, **_) -> dict:
    """Agents should complete without errors."""
    errors = output.get("errors", [])
    clean = len(errors) == 0
    return {"clean_run": clean, "error_count": len(errors), "score": 1.0 if clean else 0.0}


# ── Run evaluation ────────────────────────────────────────────────────────────

async def main():
    weave.init("legal-letter-triage")

    evaluation = weave.Evaluation(
        name="legal-letter-triage-eval",
        dataset=DATASET,
        scorers=[
            verdict_is_valid,
            verdict_in_expected_family,
            letter_classified_correctly,
            all_specialists_ran,
            response_was_drafted,
            no_agent_errors,
        ],
    )

    print("\nRunning evaluation against 3 sample letters...")
    print("This will call Qwen for each agent on each letter (~90 seconds)\n")

    results = await evaluation.evaluate(triage_model)

    print("\n=== EVALUATION COMPLETE ===")
    print(f"Open results at: https://wandb.ai/nicholaslutta7-xoori-inc/legal-letter-triage/weave")
    return results


if __name__ == "__main__":
    asyncio.run(main())
