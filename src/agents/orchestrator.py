"""Classify the incoming letter and set high-level routing context."""

from __future__ import annotations

import re

from src.config import traced_op
from src.schemas import Classification


@traced_op("orchestrator_classify")
def classify_letter(letter_text: str) -> dict:
    text = letter_text.lower()
    letter_type = "general legal letter"
    if "debt" in text or "collection" in text or "amount due" in text:
        letter_type = "debt collection"
    elif "eviction" in text or "notice to quit" in text or "rent" in text:
        letter_type = "housing / eviction"
    elif "employment" in text or "termination" in text or "severance" in text:
        letter_type = "employment"

    urgency = "medium"
    if re.search(r"\b(24 hours|48 hours|immediately|urgent|lawsuit|eviction)\b", text):
        urgency = "high"
    elif re.search(r"\b(30 days|respond by|deadline|due date)\b", text):
        urgency = "medium"

    jurisdiction = "unknown"
    state_match = re.search(r"\b(CA|NY|TX|FL|IL|MA|WA|DC)\b", letter_text)
    if state_match:
        jurisdiction = state_match.group(1)

    return Classification(
        letter_type=letter_type,
        jurisdiction=jurisdiction,
        urgency=urgency,
        summary=f"Detected a {letter_type} with {urgency} urgency.",
    ).to_dict()

