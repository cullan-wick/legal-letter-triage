"""Draft a cautious response."""

from __future__ import annotations

from src.config import traced_op
from src.schemas import DraftResponse


@traced_op("draft_response")
def draft_response(classification: dict, verdict: dict) -> dict:
    letter_type = classification.get("letter_type", "legal matter")
    subject = f"Response regarding {letter_type}"
    body = (
        "To whom it may concern,\n\n"
        "I received your letter and am reviewing it. Please provide any supporting "
        "documents, account records, dates, and the legal basis for the requested "
        "action. I do not admit liability or waive any rights by asking for this "
        "information.\n\n"
        "Please communicate with me in writing so I can keep accurate records.\n\n"
        "Sincerely,\n"
        "[Your name]"
    )
    if verdict.get("value") == "urgent":
        body += "\n\nNote: Because your letter appears time-sensitive, I am also seeking appropriate guidance."

    return DraftResponse(subject=subject, body=body).to_dict()

