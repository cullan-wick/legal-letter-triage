"""Obligations and deadlines specialist."""

from __future__ import annotations

import re

from src.config import traced_op
from src.schemas import SpecialistFinding


DEADLINE_PATTERNS = [
    r"\bwithin \d+ days\b",
    r"\b\d+ days\b",
    r"\bby [A-Z][a-z]+ \d{1,2},? \d{4}\b",
    r"\brespond by [^.,\n]+",
    r"\bdue by [^.,\n]+",
]


@traced_op("obligations_extract")
def extract_obligations(letter_text: str, classification: dict) -> dict:
    deadlines: list[str] = []
    for pattern in DEADLINE_PATTERNS:
        deadlines.extend(re.findall(pattern, letter_text, flags=re.IGNORECASE))

    key_points = [
        "Identify who sent the letter and whether they have authority to demand action.",
        "Calendar every stated deadline before drafting a response.",
        "Avoid admissions, payment promises, or signatures until the facts are verified.",
    ]

    if not deadlines:
        deadlines.append("No explicit deadline detected; still verify dates in the full document.")

    return SpecialistFinding(
        agent_name="obligations",
        summary="The immediate obligation is to verify deadlines, preserve records, and respond carefully.",
        key_points=key_points,
        deadlines=deadlines,
        confidence="medium",
        needs_lawyer=classification.get("urgency") == "high",
    ).to_dict()

