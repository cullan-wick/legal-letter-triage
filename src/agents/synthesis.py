"""Synthesize specialist findings into a triage verdict."""

from __future__ import annotations

import re
import time

from src.schemas import AgentState, SynthesisOutput

try:
    import weave  # type: ignore
except Exception:
    class _WeaveFallback:
        @staticmethod
        def op():
            def decorate(func):
                return func

            return decorate

    weave = _WeaveFallback()


NON_DEADLINE_MARKERS = (
    "no explicit deadline detected",
    "no deadline detected",
    "verify dates",
)


LETTER_TYPE_CONTEXT = {
    "debt_collection": {
        "summary_subject": "debt collection letter",
        "protective_step": "Preserve account records and consider a written dispute or validation request before admitting liability.",
        "lawyer_step": "Contact consumer legal aid or a debt-defense lawyer if the sender threatens a lawsuit, judgment, garnishment, or a short deadline.",
    },
    "eviction": {
        "summary_subject": "housing or eviction notice",
        "protective_step": "Gather the lease, rent ledger, payment proof, repair records, photos, and all landlord messages.",
        "lawyer_step": "Contact tenant legal aid, an eviction defense clinic, or a court self-help desk before any response or court date.",
    },
    "employment_warning": {
        "summary_subject": "employment letter",
        "protective_step": "Preserve the offer letter, handbook, pay records, reviews, warnings, severance terms, and related messages.",
        "lawyer_step": "Consult an employment lawyer or worker clinic before signing a release, severance agreement, or anything that waives claims.",
    },
    "general": {
        "summary_subject": "legal letter",
        "protective_step": "Preserve the letter, envelope, attachments, contracts, payment records, and related messages.",
        "lawyer_step": "Contact local legal aid or a bar referral service if the sender escalates, threatens court, or demands a signature/payment.",
    },
}


def _normalize_letter_type(letter_type: str) -> str:
    normalized = letter_type.lower().replace(" ", "_").replace("/", "_")
    if "debt" in normalized or "collection" in normalized:
        return "debt_collection"
    if "eviction" in normalized or "housing" in normalized or "tenant" in normalized or "rent" in normalized:
        return "eviction"
    if "employment" in normalized or "termination" in normalized or "severance" in normalized:
        return "employment_warning"
    return "general"


def _is_real_deadline(deadline: str) -> bool:
    normalized = deadline.strip().lower()
    return bool(normalized) and not any(marker in normalized for marker in NON_DEADLINE_MARKERS)


_MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"
_DATE_RE = re.compile(
    rf"\b(?:{_MONTHS})\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}\b"  # May 30, 2026
    r"|\b\d{1,2}/\d{1,2}/\d{2,4}\b"                                # 05/30/2026
    r"|\b\d{4}-\d{2}-\d{2}\b",                                     # 2026-05-30
    re.IGNORECASE,
)


def _deadline_key(deadline: str) -> str:
    """Collapse different phrasings of the same deadline onto one key.

    Specialists often restate the same date in different words ("May 30, 2026" vs
    "Payment deadline: May 30, 2026 (15 days...)"). Key on the calendar date when one is
    present so those merge; otherwise fall back to a normalized form of the whole phrase.
    """
    match = _DATE_RE.search(deadline)
    if match:
        return re.sub(r"[\s,]+", " ", match.group(0).lower()).strip()
    return re.sub(r"[^a-z0-9]+", " ", deadline.lower()).strip()


def _real_deadlines(specialist_findings: list[dict]) -> list[str]:
    best: dict[str, str] = {}
    order: list[str] = []
    for finding in _successful_findings(specialist_findings):
        for deadline in finding.get("deadlines", []):
            if not isinstance(deadline, str) or not _is_real_deadline(deadline):
                continue
            normalized = deadline.strip()
            key = _deadline_key(normalized)
            if key not in best:
                best[key] = normalized
                order.append(key)
            elif len(normalized) > len(best[key]):
                # keep the most informative phrasing for this date
                best[key] = normalized
    return [best[key] for key in order]


def _successful_findings(specialist_findings: list[dict]) -> list[dict]:
    return [finding for finding in specialist_findings if not finding.get("error")]


def _has_signal(specialist_findings: list[dict], terms: tuple[str, ...]) -> bool:
    combined = " ".join(
        " ".join([finding.get("summary", ""), *finding.get("key_points", [])]).lower()
        for finding in _successful_findings(specialist_findings)
    )
    return any(term in combined for term in terms)


def _letter_context(letter_type: str) -> dict[str, str]:
    return LETTER_TYPE_CONTEXT.get(_normalize_letter_type(letter_type), LETTER_TYPE_CONTEXT["general"])


def _reason(
    verdict: str,
    letter_type: str,
    deadlines: list[str],
    needs_lawyer: bool,
    specialist_review_incomplete: bool,
) -> str:
    context = _letter_context(letter_type)
    subject = context["summary_subject"]

    if verdict == "urgent":
        if deadlines:
            return f"This {subject} appears time-sensitive because it includes a deadline: {deadlines[0]}."
        return f"This {subject} appears time-sensitive and should be reviewed quickly."
    if verdict == "consult_lawyer":
        if specialist_review_incomplete:
            return f"Specialist checks for this {subject} were incomplete, so the recipient should get legal guidance before acting."
        if needs_lawyer:
            return f"This {subject} may be manageable, but at least one specialist flagged that legal guidance is needed."
        if deadlines:
            return f"This {subject} includes a real timing issue, so the recipient should verify rights and obligations before acting."
        return f"This {subject} has enough legal complexity that a short consultation would reduce risk."
    return f"This {subject} has no high-urgency signal or real deadline detected, so it appears suitable for careful self-handling."


def _next_steps(verdict: str, letter_type: str, deadlines: list[str]) -> list[str]:
    context = _letter_context(letter_type)
    steps = [
        "Save the letter, envelope, attachments, and any related messages.",
        context["protective_step"],
        "Respond in writing without admitting liability, waiving rights, or making promises before the facts are verified.",
    ]

    if deadlines:
        steps.insert(1, f"Calendar and verify the stated deadline: {deadlines[0]}.")
    else:
        steps.insert(1, "No explicit deadline was confirmed; still check the full document for dates, court information, or response windows.")

    if verdict == "urgent":
        steps.insert(0, "Treat this as urgent and seek legal information or legal help today.")
        steps.append(context["lawyer_step"])
    elif verdict == "consult_lawyer":
        steps.append(context["lawyer_step"])
    else:
        steps.append("Escalate to legal help if the sender threatens court, eviction, termination, garnishment, or demands a signature/payment.")

    return steps


def synthesize(
    classification: dict,
    specialist_findings: list[dict],
    urgency_signal: str = "medium",
) -> dict:
    letter_type = classification.get("letter_type", "general")
    normalized_letter_type = _normalize_letter_type(letter_type)
    urgency = classification.get("urgency", urgency_signal)
    successful_findings = _successful_findings(specialist_findings)
    specialist_review_incomplete = not successful_findings
    needs_lawyer = any(
        finding.get("needs_lawyer") for finding in successful_findings
    )
    deadlines = _real_deadlines(specialist_findings)
    has_urgent_signal = _has_signal(
        specialist_findings,
        (
            "eviction",
            "court",
            "lawsuit",
            "lockout",
            "garnishment",
            "signing a release",
            "waive",
            "today",
        ),
    )

    if urgency == "high" or urgency_signal == "high" or (
        normalized_letter_type == "eviction" and (deadlines or needs_lawyer)
    ):
        verdict = "urgent"
    elif specialist_review_incomplete:
        verdict = "consult_lawyer"
    elif needs_lawyer or has_urgent_signal:
        verdict = "consult_lawyer"
    elif deadlines:
        verdict = "consult_lawyer"
    else:
        verdict = "handle_yourself"

    output = SynthesisOutput(
        verdict=verdict,
        reason=_reason(verdict, letter_type, deadlines, needs_lawyer, specialist_review_incomplete),
        next_steps=_next_steps(verdict, letter_type, deadlines),
        urgent_deadlines=deadlines if verdict == "urgent" else [],
    )
    return output.model_dump()


def _findings_text(specialist_findings: list[dict]) -> str:
    return "\n\n".join(
        (
            f"[{finding.get('agent_name', 'unknown').upper()}]\n"
            f"Summary: {finding.get('summary', '')}\n"
            f"Key points: {finding.get('key_points', [])}\n"
            f"Deadlines: {finding.get('deadlines', [])}\n"
            f"Confidence: {finding.get('confidence', 'medium')}\n"
            f"Needs lawyer: {finding.get('needs_lawyer', False)}\n"
            f"Error: {finding.get('error')}"
        )
        for finding in specialist_findings
    )


def _create_completion(messages: list[dict]):
    from src.config import MODEL, client

    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"},
    )


def synthesize_live(
    letter_text: str,
    classification: dict,
    specialist_findings: list[dict],
    urgency_signal: str = "medium",
) -> dict:
    fallback = synthesize(classification, specialist_findings, urgency_signal)
    response = _create_completion(
        [
            {
                "role": "system",
                "content": (
                    "You are the live synthesis agent in a legal-letter triage system. "
                    "Use the classifier and specialist findings to produce the final triage verdict. "
                    "This is legal information, not legal advice. "
                    "Respond ONLY with valid JSON matching this schema: "
                    '{"verdict":"handle_yourself"|"consult_lawyer"|"urgent",'
                    '"reason":str,"next_steps":[str],"urgent_deadlines":[str]}. '
                    "Do not weaken urgency below the deterministic baseline unless the specialist findings clearly justify it. "
                    "When specialist checks failed or are incomplete, default to consult_lawyer."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Original letter:\n{letter_text}\n\n"
                    f"Classification:\n{classification}\n\n"
                    f"Urgency signal: {urgency_signal}\n\n"
                    f"Specialist findings:\n{_findings_text(specialist_findings)}\n\n"
                    f"Deterministic baseline to respect or strengthen:\n{fallback}\n\n"
                    "Produce the final synthesis verdict."
                ),
            },
        ]
    )
    data = SynthesisOutput.model_validate_json(response.choices[0].message.content)
    return data.model_dump()


@weave.op()
def synthesize_verdict(state: AgentState) -> AgentState:
    start = time.time()
    classification = state.get("classification", {}) or {}
    specialist_findings = state.get("specialist_findings", [])
    urgency_signal = state.get("urgency_signal", "medium")
    state["verdict"] = synthesize_live(
        state.get("letter_text", ""),
        classification,
        specialist_findings,
        urgency_signal,
    )
    state["latencies"]["synthesis"] = round(time.time() - start, 2)
    return state
