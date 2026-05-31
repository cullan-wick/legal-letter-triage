"""Recommend what kind of legal help to seek."""

from __future__ import annotations

import json
import time

from src.schemas import AgentState, LawyerRecommendation

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


STATE_REFERRALS = {
    "CA": "California: check the State Bar of California lawyer referral services and local legal aid or tenant/consumer clinics.",
    "NY": "New York: check the New York State Bar Association referral service, LawHelpNY, and local legal aid providers.",
    "TX": "Texas: check the State Bar of Texas referral directory, TexasLawHelp, and local legal aid offices.",
    "FL": "Florida: check The Florida Bar lawyer referral service, FloridaLawHelp, and local legal aid providers.",
    "IL": "Illinois: check Illinois Legal Aid Online, local bar referral services, and legal aid organizations.",
    "MA": "Massachusetts: check MassLegalHelp, local bar referral services, and legal aid organizations.",
    "WA": "Washington: check Washington LawHelp, county bar referral services, and legal aid organizations.",
    "DC": "District of Columbia: check the D.C. Bar Pro Bono Center, LawHelpDC, and local referral services.",
}


JURISDICTION_ALIASES = {
    "california": "CA",
    "ca": "CA",
    "new_york": "NY",
    "new york": "NY",
    "ny": "NY",
    "texas": "TX",
    "tx": "TX",
    "florida": "FL",
    "fl": "FL",
    "illinois": "IL",
    "il": "IL",
    "massachusetts": "MA",
    "ma": "MA",
    "washington": "WA",
    "wa": "WA",
    "district_of_columbia": "DC",
    "district of columbia": "DC",
    "washington_dc": "DC",
    "washington dc": "DC",
    "dc": "DC",
}


HELP_BY_LETTER_TYPE = {
    "debt_collection": {
        "lawyer_type": "Consumer debt defense or consumer protection attorney",
        "legal_help_categories": [
            "consumer debt defense attorney",
            "consumer protection legal aid clinic",
            "bankruptcy attorney if the debt load is broader than this letter",
        ],
        "questions_to_ask": [
            "Can I dispute or request validation of this debt before the deadline?",
            "Is the collector allowed to contact me this way in my jurisdiction?",
            "Could this lead to a lawsuit, wage garnishment, or bank levy?",
            "Should I negotiate, dispute, or wait for more documentation?",
        ],
        "documents_to_prepare": [
            "The collection letter, envelope, and all attachments",
            "Account statements, payment records, and prior dispute letters",
            "Any court papers, if a lawsuit has already been filed",
            "A timeline of calls, emails, texts, and mailed notices from the collector",
        ],
        "reason": "Debt collection letters can involve dispute windows, validation rights, and lawsuit risk.",
        "estimated_cost_range": "Ask about free legal aid, consumer law clinics, limited-scope advice, flat-fee consults, and whether fee-shifting laws may apply.",
    },
    "eviction": {
        "lawyer_type": "Tenant rights or eviction defense attorney",
        "legal_help_categories": [
            "tenant rights attorney",
            "eviction defense legal aid clinic",
            "local housing counselor or tenants union",
        ],
        "questions_to_ask": [
            "What is the exact response or court deadline?",
            "Does the notice satisfy local eviction and rent-demand rules?",
            "Can payment, repairs, habitability issues, or rental assistance change the outcome?",
            "Should I file an answer, appear in court, or contact the landlord in writing?",
        ],
        "documents_to_prepare": [
            "Lease, renewals, house rules, and rent ledger",
            "The notice, envelope, and any court paperwork",
            "Proof of rent payments, repair requests, photos, and inspection records",
            "Messages with the landlord, property manager, or housing agency",
        ],
        "reason": "Housing notices can have short deadlines and serious court or housing consequences.",
        "estimated_cost_range": "Prioritize free eviction defense, tenant hotlines, courthouse help desks, emergency rental assistance, and legal aid before paying privately.",
    },
    "employment_warning": {
        "lawyer_type": "Employment lawyer",
        "legal_help_categories": [
            "employment attorney",
            "wage-and-hour or discrimination legal clinic",
            "worker center or government labor agency intake",
        ],
        "questions_to_ask": [
            "What claims or deadlines could I waive if I sign this?",
            "Are wages, commissions, benefits, or final pay still owed?",
            "Could retaliation, discrimination, protected leave, or whistleblowing be involved?",
            "Should I negotiate severance, references, confidentiality, or non-disparagement terms?",
        ],
        "documents_to_prepare": [
            "Offer letter, handbook, contract, severance agreement, and any releases",
            "Pay stubs, commission records, schedules, and benefits documents",
            "Performance reviews, discipline notices, emails, and messages",
            "A timeline of key events, complaints, leave requests, or termination facts",
        ],
        "reason": "Employment letters can affect wages, benefits, references, claims deadlines, or waivers.",
        "estimated_cost_range": "Ask about free worker clinics, contingency options for strong claims, agency complaint routes, and fixed-fee severance review.",
    },
}


GENERAL_HELP = {
    "lawyer_type": "General civil legal aid or consumer protection attorney",
    "legal_help_categories": [
        "general civil legal aid",
        "consumer protection attorney",
        "local bar association referral service",
    ],
    "questions_to_ask": [
        "What deadline matters most right now?",
        "What legal area does this letter fall under?",
        "Should I respond before you review the full letter?",
        "What facts or documents would change the risk level?",
    ],
    "documents_to_prepare": [
        "The letter, envelope, attachments, and delivery records",
        "Any contract, account record, notice, or prior correspondence mentioned in the letter",
        "A short timeline of what happened and who was involved",
        "Proof of payments, repairs, communications, or other supporting records",
    ],
    "reason": "The letter appears to need general civil triage before deciding whether a specialist is required.",
    "estimated_cost_range": "Ask about free legal aid, nonprofit clinics, limited-scope consults, flat-fee reviews, and local bar referral options.",
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


def _urgency_guidance(verdict_value: str, classification: dict) -> str:
    letter_type = _normalize_letter_type(classification.get("letter_type", "general"))
    urgency = classification.get("urgency", "medium")

    if verdict_value == "urgent":
        if letter_type == "eviction":
            return "Treat this as same-day urgent, especially if there is a court date, lockout threat, or short notice period."
        if letter_type == "debt_collection":
            return "Treat this as urgent if there are court papers, a judgment, garnishment threat, or a deadline under 7 days."
        if letter_type == "employment_warning":
            return "Treat this as urgent before signing anything, missing an agency deadline, or accepting severance terms."
        return "Treat this as urgent and seek advice before the next deadline or any signature/payment."

    if verdict_value == "consult_lawyer":
        if urgency == "high":
            return "Contact legal help within 24 to 48 hours and before sending a response."
        return "Schedule a consultation soon and before the earliest stated deadline."

    return "Legal help may not be necessary immediately, but use a referral if facts are disputed, deadlines are unclear, or the sender escalates."


def _jurisdiction_note(jurisdiction: str) -> str:
    normalized = jurisdiction.strip().lower().replace(".", "").replace(",", " ")
    normalized = "_".join(normalized.split())
    jurisdiction_key = JURISDICTION_ALIASES.get(normalized, jurisdiction.upper())
    return STATE_REFERRALS.get(
        jurisdiction_key,
        "Jurisdiction was not identified; use your local legal aid directory, court self-help center, or bar association referral service.",
    )


def recommend_lawyer(classification: dict, verdict: dict) -> dict:
    verdict_value = verdict.get("verdict", verdict.get("value", "handle_yourself"))
    letter_type = _normalize_letter_type(classification.get("letter_type", "general"))
    jurisdiction = classification.get("jurisdiction", "unknown")
    guidance = HELP_BY_LETTER_TYPE.get(letter_type, GENERAL_HELP)
    jurisdiction_note = _jurisdiction_note(jurisdiction)

    return {
        "lawyer_type": guidance["lawyer_type"],
        "reason": guidance["reason"],
        "questions_to_ask": list(guidance["questions_to_ask"]),
        "estimated_cost_range": f"{guidance['estimated_cost_range']} {jurisdiction_note}",
        "legal_help_categories": list(guidance["legal_help_categories"]),
        "documents_to_prepare": list(guidance["documents_to_prepare"]),
        "urgency_guidance": _urgency_guidance(verdict_value, classification),
        "jurisdiction_note": jurisdiction_note,
    }


def _validate_live_recommendation(data: dict) -> dict:
    base = LawyerRecommendation.model_validate(data).model_dump()
    return {
        **base,
        "legal_help_categories": list(data.get("legal_help_categories", [])),
        "documents_to_prepare": list(data.get("documents_to_prepare", [])),
        "urgency_guidance": str(data.get("urgency_guidance", "")),
        "jurisdiction_note": str(data.get("jurisdiction_note", "")),
    }


def _create_completion(messages: list[dict]):
    from src.config import MODEL, client

    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"},
    )


def recommend_lawyer_live(classification: dict, verdict: dict) -> dict:
    fallback = recommend_lawyer(classification, verdict)
    response = _create_completion(
        [
            {
                "role": "system",
                "content": (
                    "You are the live lawyer-finder agent in a legal-letter triage system. "
                    "Recommend what kind of legal help to seek based on the letter type, jurisdiction, and verdict. "
                    "This is legal information, not legal advice. Do not invent attorney names, claim to browse, "
                    "or imply that a specific lawyer has been found. "
                    "Respond ONLY with valid JSON with these exact keys: "
                    '{"lawyer_type":str,"reason":str,"questions_to_ask":[str],'
                    '"estimated_cost_range":str,"legal_help_categories":[str],'
                    '"documents_to_prepare":[str],"urgency_guidance":str,"jurisdiction_note":str}. '
                    "Include cost/referral notes, practical documents to prepare, and urgency guidance."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Classification:\n{classification}\n\n"
                    f"Verdict:\n{verdict}\n\n"
                    f"Deterministic baseline to improve or preserve:\n{fallback}\n\n"
                    "Produce the legal help recommendation."
                ),
            },
        ]
    )
    data = json.loads(response.choices[0].message.content)
    return _validate_live_recommendation(data)


@weave.op()
def find_lawyer(state: AgentState) -> AgentState:
    """Runs only when verdict is consult_lawyer or urgent."""
    start = time.time()
    classification = state.get("classification", {}) or {}
    verdict = state.get("verdict", {}) or {}
    try:
        state["lawyer_recommendation"] = recommend_lawyer_live(classification, verdict)
    except Exception as exc:
        state["errors"].append(f"lawyer_finder: {exc}")
        state["lawyer_recommendation"] = recommend_lawyer(classification, verdict)
    state["latencies"]["lawyer_finder"] = round(time.time() - start, 2)
    return state
