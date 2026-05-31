"""Recommend what kind of legal help to seek."""

from __future__ import annotations

from src.config import traced_op
from src.schemas import LawyerRecommendation


@traced_op("find_lawyer")
def recommend_lawyer(classification: dict, verdict: dict) -> dict:
    should_show = verdict.get("value") in {"consult_lawyer", "urgent"}
    letter_type = classification.get("letter_type", "general legal letter")

    lawyer_type = "consumer protection or general civil legal aid"
    if letter_type == "housing / eviction":
        lawyer_type = "tenant rights or eviction defense"
    elif letter_type == "employment":
        lawyer_type = "employment law"
    elif letter_type == "debt collection":
        lawyer_type = "consumer debt defense"

    return LawyerRecommendation(
        should_show=should_show,
        lawyer_type=lawyer_type,
        questions_to_ask=[
            "What deadline matters most right now?",
            "Should I respond before you review the full letter?",
            "What documents should I gather?",
            "Do you offer a limited-scope consultation or legal aid referral?",
        ],
        cost_notes="Ask about free legal aid, nonprofit clinics, limited-scope consults, and flat-fee options.",
    ).to_dict()

