"""Rights specialist."""

from __future__ import annotations

from src.config import traced_op
from src.schemas import SpecialistFinding


@traced_op("rights_review")
def review_rights(letter_text: str, classification: dict) -> dict:
    letter_type = classification.get("letter_type", "general legal letter")

    key_points = [
        "The recipient can ask for clarification in writing before admitting facts or liability.",
        "The recipient should keep copies of all letters and responses.",
    ]

    if letter_type == "debt collection":
        key_points.extend(
            [
                "The recipient may be able to dispute the debt or request validation.",
                "Collectors may be limited in how and when they can contact the recipient.",
            ]
        )
    elif letter_type == "housing / eviction":
        key_points.extend(
            [
                "The recipient may have notice, habitability, payment, or court-process rights.",
                "Local tenant protections can matter a lot and should be checked quickly.",
            ]
        )
    elif letter_type == "employment":
        key_points.extend(
            [
                "The recipient may have rights related to wages, discrimination, retaliation, or final pay.",
                "Signing a release can affect future claims.",
            ]
        )

    return SpecialistFinding(
        agent_name="rights",
        summary="The recipient likely has process and documentation rights worth preserving.",
        key_points=key_points,
        confidence="medium",
    ).to_dict()

