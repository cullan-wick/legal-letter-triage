"""Synthesize specialist findings into a triage verdict."""

from __future__ import annotations

from src.config import traced_op
from src.schemas import Verdict


@traced_op("synthesize_verdict")
def synthesize(classification: dict, specialist_findings: list[dict]) -> dict:
    urgency = classification.get("urgency", "medium")
    needs_lawyer = any(finding.get("needs_lawyer") for finding in specialist_findings)
    has_deadlines = any(finding.get("deadlines") for finding in specialist_findings)

    if urgency == "high":
        value = "urgent"
        summary = "This letter appears time-sensitive and should be reviewed quickly."
    elif needs_lawyer:
        value = "consult_lawyer"
        summary = "This may be manageable, but the risk level suggests getting legal guidance."
    elif has_deadlines:
        value = "consult_lawyer"
        summary = "There are possible deadlines, so the recipient should verify before acting."
    else:
        value = "handle_yourself"
        summary = "This appears suitable for careful self-handling with documentation."

    next_steps = [
        "Save the letter, envelope, attachments, and any related messages.",
        "Calendar any stated deadlines.",
        "Respond in writing without admitting liability or waiving rights.",
    ]
    if value in {"consult_lawyer", "urgent"}:
        next_steps.append("Contact a relevant legal aid group or lawyer before the deadline.")

    return Verdict(value=value, summary=summary, next_steps=next_steps).to_dict()

