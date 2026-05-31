"""Obligations and deadlines specialist.

Extracts the concrete actions the recipient is being asked to take and every deadline or
response window in the letter. Runs as a LangGraph node and fails soft so the spine stays
green.
"""

import time

import weave

from src.config import MODEL, client
from src.schemas import AgentState, SpecialistFinding

SYSTEM_PROMPT = (
    "You are an obligations-and-deadlines specialist in a legal-letter triage system. You "
    "provide legal information, not legal advice. Read the letter and extract exactly what "
    "the recipient is being asked or required to do, who is demanding it, and every deadline "
    "or response window. Put each concrete date or time window (e.g. 'within 30 days', "
    "'by March 14, 2026') as its own entry in deadlines. If no explicit deadline is stated, "
    "say so in deadlines and advise verifying dates in the full document. Warn against "
    "admissions, payments, or signatures before the facts are verified.\n\n"
    "Respond with ONLY a JSON object with these exact keys:\n"
    '{"agent_name": "obligations", "summary": string, "key_points": [string], '
    '"deadlines": [string], "confidence": "low"|"medium"|"high", "needs_lawyer": boolean}\n'
    "Set needs_lawyer to true when a deadline is short or the required action carries legal weight."
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
def obligations_extract(state: AgentState) -> dict:
    """Parallel-safe: writes only its own staging key (`obligations_finding`) so concurrent
    specialists never write the same channel. `collect` folds it into specialist_findings."""
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
        finding.agent_name = "obligations"
        if not finding.deadlines:
            finding.deadlines = ["No explicit deadline detected; verify dates in the full document."]
        result = finding.model_dump()
    except Exception as exc:
        result = SpecialistFinding(
            agent_name="obligations",
            summary="Obligations could not be extracted; verify all deadlines in the full document.",
            key_points=[],
            deadlines=["Unable to extract deadlines automatically; review the letter for dates."],
            needs_lawyer=True,
            error=str(exc),
        ).model_dump()
    result["latency_ms"] = round(time.time() - start, 2)
    return {"obligations_finding": result}
