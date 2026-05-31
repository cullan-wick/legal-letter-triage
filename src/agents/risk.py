"""Risk specialist.

Explains the worst realistic outcome the recipient faces if they mishandle or ignore
the letter. Runs as a LangGraph node and fails soft so the spine stays green.
"""

import time

import weave

from src.config import MODEL, client
from src.schemas import AgentState, SpecialistFinding

SYSTEM_PROMPT = (
    "You are a risk-analysis specialist in a legal-letter triage system. You provide "
    "legal information, not legal advice. Read the letter and assess the worst realistic "
    "outcome if the recipient ignores or mishandles it, plus how quickly it could escalate. "
    "Be concrete and calm; do not exaggerate.\n\n"
    "Respond with ONLY a JSON object with these exact keys:\n"
    '{"agent_name": "risk", "summary": string, "key_points": [string], '
    '"deadlines": [string], "confidence": "low"|"medium"|"high", "needs_lawyer": boolean}\n'
    "Set needs_lawyer to true when the realistic downside (lawsuit, eviction, wage loss, "
    "lost legal rights) is serious enough that professional guidance is warranted."
)


def _context(state: AgentState) -> str:
    classification = state.get("classification") or {}
    letter_type = classification.get("letter_type", "unknown")
    urgency = classification.get("urgency", "unknown")
    return (
        f"Letter type: {letter_type}\nUrgency: {urgency}\n\n"
        f"Letter:\n{state['letter_text']}"
    )


@weave.op()
def risk_assess(state: AgentState) -> AgentState:
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _context(state)},
            ],
            response_format={"type": "json_object"},
        )
        finding = SpecialistFinding.model_validate_json(response.choices[0].message.content)
        finding.agent_name = "risk"
        state["specialist_findings"].append(finding.model_dump())
    except Exception as exc:
        state["errors"].append(f"risk: {exc}")
        state["specialist_findings"].append(
            SpecialistFinding(
                agent_name="risk",
                summary="Risk assessment could not be completed; treat this as needing review.",
                key_points=[],
                needs_lawyer=True,
                error=str(exc),
            ).model_dump()
        )
    state["latencies"]["risk"] = round(time.time() - start, 2)
    return state
