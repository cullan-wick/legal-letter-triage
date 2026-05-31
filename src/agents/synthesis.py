"""Synthesize specialist findings into a triage verdict."""

from __future__ import annotations

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


def _real_deadlines(specialist_findings: list[dict]) -> list[str]:
    deadlines: list[str] = []
    seen: set[str] = set()
    for finding in specialist_findings:
        if finding.get("error"):
            continue
        for deadline in finding.get("deadlines", []):
            if not isinstance(deadline, str) or not _is_real_deadline(deadline):
                continue
            normalized = deadline.strip()
            key = normalized.lower()
            if key not in seen:
                deadlines.append(normalized)
                seen.add(key)
    return deadlines


def _has_signal(specialist_findings: list[dict], terms: tuple[str, ...]) -> bool:
    combined = " ".join(
        " ".join([finding.get("summary", ""), *finding.get("key_points", [])]).lower()
        for finding in specialist_findings
        if not finding.get("error")
    )
    return any(term in combined for term in terms)


def _letter_context(letter_type: str) -> dict[str, str]:
    return LETTER_TYPE_CONTEXT.get(_normalize_letter_type(letter_type), LETTER_TYPE_CONTEXT["general"])


def _reason(verdict: str, letter_type: str, deadlines: list[str], needs_lawyer: bool) -> str:
    context = _letter_context(letter_type)
    subject = context["summary_subject"]

    if verdict == "urgent":
        if deadlines:
            return f"This {subject} appears time-sensitive because it includes a deadline: {deadlines[0]}."
        return f"This {subject} appears time-sensitive and should be reviewed quickly."
    if verdict == "consult_lawyer":
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
    needs_lawyer = any(
        finding.get("needs_lawyer") for finding in specialist_findings if not finding.get("error")
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
    elif needs_lawyer or has_urgent_signal:
        verdict = "consult_lawyer"
    elif deadlines:
        verdict = "consult_lawyer"
    else:
        verdict = "handle_yourself"

    output = SynthesisOutput(
        verdict=verdict,
        reason=_reason(verdict, letter_type, deadlines, needs_lawyer),
        next_steps=_next_steps(verdict, letter_type, deadlines),
        urgent_deadlines=deadlines if verdict == "urgent" else [],
    )
    return output.model_dump()


@weave.op()
def synthesize_verdict(state: AgentState) -> AgentState:
    start = time.time()
    state["verdict"] = synthesize(
        state.get("classification", {}) or {},
        state.get("specialist_findings", []),
        state.get("urgency_signal", "medium"),
    )
    state["latencies"]["synthesis"] = round(time.time() - start, 2)
    return state
