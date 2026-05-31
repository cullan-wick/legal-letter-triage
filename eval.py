"""
Weave Evaluation — Legal Letter Triage
Run: venv\Scripts\python.exe eval.py

Results appear at wandb.ai under the legal-letter-triage project → Weave tab.
"""

import asyncio
import pathlib
import weave
from src.config import client, MODEL
from src.graph import run

METRIC_THRESHOLD = 0.75

EXPECTED_TRAJECTORY = [
    "orchestrator",
    "risk",
    "rights",
    "obligations",
    "synthesis",
    "response_drafter",
    "lawyer_finder",
]

# ── Dataset with ground truth reference answers ───────────────────────────────

DATASET = weave.Dataset(
    name="legal-letter-triage-samples-v2",
    rows=[
        {
            "id": "debt-collection",
            "letter_text": pathlib.Path("samples/debt_collection.txt").read_text(),
            "reference": (
                "verdict: urgent or consult_lawyer. "
                "Deadline: 15 days to pay or dispute. "
                "Rights: recipient has 30 days to dispute and request debt validation in writing. "
                "Risk: civil lawsuit, wage garnishment up to 25%, credit bureau reporting. "
                "A response letter should be sent acknowledging receipt without admitting liability."
            ),
            "reference_trajectory": EXPECTED_TRAJECTORY,
            "expected_verdict_family": ["consult_lawyer", "urgent"],
            "expected_letter_type_keyword": "debt",
        },
        {
            "id": "eviction-notice",
            "letter_text": pathlib.Path("samples/eviction_notice.txt").read_text(),
            "reference": (
                "verdict: urgent. "
                "Deadline: 3 days to pay arrears of $2,400 or vacate. "
                "Rights: recipient can contest eviction in court and has right to a hearing. "
                "Risk: eviction proceedings, court costs, possible negative rental history. "
                "Tenant should gather lease, payment records, and contact tenant legal aid immediately."
            ),
            "reference_trajectory": EXPECTED_TRAJECTORY,
            "expected_verdict_family": ["consult_lawyer", "urgent"],
            "expected_letter_type_keyword": "eviction",
        },
        {
            "id": "employment-warning",
            "letter_text": pathlib.Path("samples/employment_warning.txt").read_text(),
            "reference": (
                "verdict: handle_yourself or consult_lawyer. "
                "Deadline: 5 business days to respond in writing; 90-day performance period. "
                "Rights: recipient has right to respond in writing within 5 days. "
                "Risk: termination if performance standards not met within 90 days. "
                "Recipient should document all work, respond professionally in writing, and keep records."
            ),
            "reference_trajectory": ["orchestrator", "risk", "rights", "obligations",
                                      "synthesis", "response_drafter"],
            "expected_verdict_family": ["handle_yourself", "consult_lawyer"],
            "expected_letter_type_keyword": "employment",
        },
    ],
)


# ── Model ─────────────────────────────────────────────────────────────────────

@weave.op()
def triage_model(letter_text: str) -> dict:
    """Run the full multi-agent graph."""
    result = run(letter_text)
    return {
        "verdict": result.get("verdict", {}).get("verdict", "unknown"),
        "reason": result.get("verdict", {}).get("reason", ""),
        "next_steps": result.get("verdict", {}).get("next_steps", []),
        "letter_type": result.get("classification", {}).get("letter_type", "unknown"),
        "urgency": result.get("classification", {}).get("urgency", "unknown"),
        "specialist_count": len(result.get("specialist_findings", [])),
        "specialist_summaries": [
            f['summary'] for f in result.get("specialist_findings", []) if not f.get("error")
        ],
        "has_draft_response": result.get("draft_response") is not None,
        "has_lawyer_recommendation": result.get("lawyer_recommendation") is not None,
        "errors": result.get("errors", []),
        "latencies": result.get("latencies", {}),
        "agents_run": list(result.get("latencies", {}).keys()),
    }


# ── Scorer 1: LLM-as-judge (reference-based quality) ─────────────────────────

@weave.op()
def llm_judge_quality(output: dict, reference: str, **_) -> dict:
    """LLM judge compares agent output against the reference golden answer."""
    verdict = output.get("verdict", "unknown")
    reason = output.get("reason", "")
    next_steps = " ".join(output.get("next_steps", []))
    summaries = " ".join(output.get("specialist_summaries", []))

    agent_output = f"Verdict: {verdict}. Reason: {reason}. Next steps: {next_steps}. Findings: {summaries}"

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an evaluation judge for a legal letter triage system. "
                        "Compare the agent's output to the reference answer. "
                        "Score from 0.0 to 1.0 where 1.0 = output captures all key facts from reference, "
                        "0.5 = partially correct, 0.0 = missing or wrong. "
                        "Respond ONLY with valid JSON: "
                        '{"score": float, "reasoning": str}'
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Reference answer:\n{reference}\n\n"
                        f"Agent output:\n{agent_output}\n\n"
                        "Score how well the agent output captures the key facts in the reference."
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        import json
        result = json.loads(response.choices[0].message.content)
        score = float(result.get("score", 0.0))
        reasoning = result.get("reasoning", "")
    except Exception as e:
        score = 0.0
        reasoning = f"Judge call failed: {e}"

    return {"score": min(max(score, 0.0), 1.0), "reasoning": reasoning}


# ── Scorer 2: Trajectory recall (deterministic) ───────────────────────────────

@weave.op()
def trajectory_recall(output: dict, reference_trajectory: list, **_) -> dict:
    """What fraction of expected agents actually ran?"""
    agents_run = output.get("agents_run", [])
    correct = sum(1 for a in reference_trajectory if a in agents_run)
    recall = correct / len(reference_trajectory) if reference_trajectory else 0.0
    missing = [a for a in reference_trajectory if a not in agents_run]
    return {
        "score": round(recall, 3),
        "recall": round(recall, 3),
        "agents_run": agents_run,
        "missing_agents": missing,
    }


@weave.op()
def trajectory_precision(output: dict, reference_trajectory: list, **_) -> dict:
    """Of the agents that ran, what fraction were expected?"""
    agents_run = output.get("agents_run", [])
    if not agents_run:
        return {"score": 0.0, "precision": 0.0}
    correct = sum(1 for a in agents_run if a in reference_trajectory)
    precision = correct / len(agents_run)
    unexpected = [a for a in agents_run if a not in reference_trajectory]
    return {
        "score": round(precision, 3),
        "precision": round(precision, 3),
        "unexpected_agents": unexpected,
    }


# ── Scorer 3: Structural checks (deterministic) ───────────────────────────────

@weave.op()
def verdict_is_valid(output: dict, **_) -> dict:
    verdict = output.get("verdict", "unknown")
    valid = verdict in ("handle_yourself", "consult_lawyer", "urgent")
    return {"score": 1.0 if valid else 0.0, "verdict": verdict}


@weave.op()
def verdict_in_expected_family(output: dict, expected_verdict_family: list, **_) -> dict:
    verdict = output.get("verdict", "unknown")
    match = verdict in expected_verdict_family
    return {"score": 1.0 if match else 0.0, "verdict": verdict, "expected": expected_verdict_family}


@weave.op()
def letter_classified_correctly(output: dict, expected_letter_type_keyword: str, **_) -> dict:
    letter_type = output.get("letter_type", "unknown")
    correct = expected_letter_type_keyword.lower() in letter_type.lower()
    return {"score": 1.0 if correct else 0.0, "letter_type": letter_type}


@weave.op()
def response_was_drafted(output: dict, **_) -> dict:
    drafted = output.get("has_draft_response", False)
    return {"score": 1.0 if drafted else 0.0}


@weave.op()
def no_agent_errors(output: dict, **_) -> dict:
    errors = output.get("errors", [])
    return {"score": 1.0 if not errors else 0.0, "error_count": len(errors)}


# ── Run and gate ──────────────────────────────────────────────────────────────

async def main():
    weave.init("legal-letter-triage")

    evaluation = weave.Evaluation(
        name="legal-letter-triage-eval-v2",
        dataset=DATASET,
        scorers=[
            llm_judge_quality,
            trajectory_recall,
            trajectory_precision,
            verdict_is_valid,
            verdict_in_expected_family,
            letter_classified_correctly,
            response_was_drafted,
            no_agent_errors,
        ],
    )

    print("\nRunning evaluation against 3 sample letters...")
    print("8 scorers including LLM judge + trajectory metrics (~3 minutes)\n")

    summary = await evaluation.evaluate(triage_model)

    print("\n=== EVALUATION RESULTS ===")
    failed_metrics = []
    for scorer_name, scorer_results in summary.items():
        if isinstance(scorer_results, dict) and "score" in scorer_results:
            mean_score = scorer_results["score"].get("mean", 0)
            status = "PASS" if mean_score >= METRIC_THRESHOLD else "FAIL"
            print(f"  {status} {scorer_name}: {mean_score:.2f}")
            if mean_score < METRIC_THRESHOLD:
                failed_metrics.append(scorer_name)

    print(f"\nThreshold: {METRIC_THRESHOLD}")
    print(f"Open trace: https://wandb.ai/nicholaslutta7-xoori-inc/legal-letter-triage/weave")

    if failed_metrics:
        print(f"\nFAILED metrics: {failed_metrics}")
    else:
        print("\nAll metrics passed.")

    return summary


if __name__ == "__main__":
    asyncio.run(main())
