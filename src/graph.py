"""Dependency-light graph runner for the initial team scaffold.

Lane 1 can replace this with LangGraph while preserving `run_triage`.
"""

from __future__ import annotations

from time import perf_counter
from typing import Callable

from src.agents.lawyer_finder import recommend_lawyer
from src.agents.obligations import extract_obligations
from src.agents.orchestrator import classify_letter
from src.agents.response_drafter import draft_response
from src.agents.rights import review_rights
from src.agents.risk import assess_risk
from src.agents.synthesis import synthesize
from src.config import init_weave
from src.schemas import TriageState, empty_state


def _timed(name: str, state: TriageState, call: Callable[[], dict]) -> dict:
    start = perf_counter()
    try:
        result = call()
    except Exception as exc:
        state["errors"].append({"step": name, "error": str(exc)})
        result = {"agent_name": name, "summary": "Step failed softly.", "error": str(exc)}
    state["latencies"][name] = round((perf_counter() - start) * 1000, 2)
    return result


def run_triage(letter_text: str) -> TriageState:
    init_weave()
    state = empty_state(letter_text)

    classification = _timed("orchestrator", state, lambda: classify_letter(letter_text))
    state["classification"] = classification

    for name, agent in [
        ("risk", assess_risk),
        ("rights", review_rights),
        ("obligations", extract_obligations),
    ]:
        finding = _timed(name, state, lambda agent=agent: agent(letter_text, classification))
        state["specialist_findings"].append(finding)

    verdict = _timed(
        "synthesis",
        state,
        lambda: synthesize(classification, state["specialist_findings"]),
    )
    state["verdict"] = verdict

    state["draft_response"] = _timed(
        "response_drafter",
        state,
        lambda: draft_response(classification, verdict),
    )

    if verdict.get("value") in {"consult_lawyer", "urgent"}:
        state["lawyer_recommendation"] = _timed(
            "lawyer_finder",
            state,
            lambda: recommend_lawyer(classification, verdict),
        )

    return state

