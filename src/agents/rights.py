"""Rights specialist.

Identifies rights and protections the recipient may have (dispute/validation rights,
tenant protections, employment protections, and process/documentation rights). Runs as a
LangGraph node and fails soft so the spine stays green.
"""

import time

import weave

from src.config import MODEL, client
from src.schemas import AgentState, SpecialistFinding

SYSTEM_PROMPT = (
    "You are a consumer, tenant, and employee rights specialist in a legal-letter triage "
    "system. You provide legal information, not legal advice. Read the letter and identify "
    "the rights and protections the recipient may have — for example the right to dispute or "
    "request validation of a debt, limits on how a collector may contact them, tenant notice "
    "and habitability protections, or employment protections around wages, discrimination, "
    "and final pay. Always include the general right to ask for clarification in writing and "
    "to keep records before admitting anything.\n\n"
    "Respond with ONLY a JSON object with these exact keys:\n"
    '{"agent_name": "rights", "summary": string, "key_points": [string], '
    '"deadlines": [string], "confidence": "low"|"medium"|"high", "needs_lawyer": boolean}\n'
    "Set needs_lawyer to true when asserting these rights realistically requires a lawyer."
)


def _context(state: AgentState) -> str:
    classification = state.get("classification") or {}
    letter_type = classification.get("letter_type", "unknown")
    jurisdiction = classification.get("jurisdiction", "unknown")
    return (
        f"Letter type: {letter_type}\nJurisdiction: {jurisdiction}\n\n"
        f"Letter:\n{state['letter_text']}"
    )


@weave.op()
def rights_review(state: AgentState) -> dict:
    """Parallel-safe: writes only its own staging key (`rights_finding`) so concurrent
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
        finding.agent_name = "rights"
        result = finding.model_dump()
    except Exception as exc:
        result = SpecialistFinding(
            agent_name="rights",
            summary="Rights review could not be completed; preserve all records and verify rights before acting.",
            key_points=[],
            needs_lawyer=True,
            error=str(exc),
        ).model_dump()
    result["latency_ms"] = round(time.time() - start, 2)
    return {"rights_finding": result}
