"""Risk specialist."""

from __future__ import annotations

from src.config import traced_op
from src.schemas import SpecialistFinding


@traced_op("risk_assess")
def assess_risk(letter_text: str, classification: dict) -> dict:
    letter_type = classification.get("letter_type", "general legal letter")
    urgency = classification.get("urgency", "medium")

    key_points = [
        "Do not ignore the letter until deadlines and sender authority are understood.",
        "Preserve the envelope, attachments, dates, and all communication history.",
    ]
    deadlines = []
    needs_lawyer = urgency == "high"

    if letter_type == "debt collection":
        key_points.append("Ignoring a collection demand can lead to continued collection activity or a lawsuit.")
        key_points.append("The recipient may have dispute or validation rights depending on the sender and timing.")
    elif letter_type == "housing / eviction":
        key_points.append("Housing notices can have short response windows and court consequences.")
        needs_lawyer = True
    elif letter_type == "employment":
        key_points.append("Employment letters may affect pay, benefits, references, or claims deadlines.")

    if urgency == "high":
        deadlines.append("Treat this as time-sensitive and verify any stated deadline today.")

    return SpecialistFinding(
        agent_name="risk",
        summary=f"Main risk: the {letter_type} may escalate if deadlines are missed.",
        key_points=key_points,
        deadlines=deadlines,
        confidence="medium",
        needs_lawyer=needs_lawyer,
    ).to_dict()

