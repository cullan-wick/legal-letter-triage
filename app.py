import chainlit as cl
import fitz  # PyMuPDF
from src.graph import run

SAMPLES = {
    "Debt Collection": open("samples/debt_collection.txt").read(),
    "Eviction Notice": open("samples/eviction_notice.txt").read(),
    "Employment Warning": open("samples/employment_warning.txt").read(),
}

VERDICT_COLOR = {
    "handle_yourself": "🟢",
    "consult_lawyer": "🟡",
    "urgent": "🔴",
}


@cl.on_chat_start
async def on_start():
    await cl.Message(
        content=(
            "**Legal Letter Triage** — paste a letter, upload a PDF, or load a sample.\n\n"
            "Load a sample: type `sample: debt`, `sample: eviction`, or `sample: employment`\n\n"
            "*This is not legal advice.*"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    text = message.content.strip()

    # Sample shortcuts
    if text.lower().startswith("sample:"):
        key = text.split(":", 1)[1].strip().lower()
        mapping = {"debt": "Debt Collection", "eviction": "Eviction Notice", "employment": "Employment Warning"}
        sample_key = mapping.get(key)
        if not sample_key:
            await cl.Message(content="Unknown sample. Try: debt, eviction, or employment.").send()
            return
        text = SAMPLES[sample_key]
        await cl.Message(content=f"Loaded sample: **{sample_key}**\n\n```\n{text[:300]}...\n```").send()

    # PDF upload
    if message.elements:
        for el in message.elements:
            if el.path and el.path.endswith(".pdf"):
                doc = fitz.open(el.path)
                text = "\n".join(page.get_text() for page in doc)
                await cl.Message(content=f"Extracted {len(text)} characters from PDF.").send()
                break

    if not text:
        await cl.Message(content="Please paste a letter or upload a PDF.").send()
        return

    thinking = cl.Message(content="Analyzing...")
    await thinking.send()

    result = run(text)

    verdict_data = result.get("verdict") or {}
    verdict = verdict_data.get("verdict", "consult_lawyer")
    icon = VERDICT_COLOR.get(verdict, "⚪")
    classification = result.get("classification") or {}
    findings = result.get("specialist_findings") or []
    draft = result.get("draft_response") or {}
    lawyer = result.get("lawyer_recommendation")
    latencies = result.get("latencies") or {}

    parts = [
        f"## {icon} Verdict: `{verdict.upper().replace('_', ' ')}`",
        f"**{verdict_data.get('reason', '')}**",
        "",
        f"**Letter type:** {classification.get('letter_type', 'unknown')} | "
        f"**Urgency:** {classification.get('urgency', 'unknown')} | "
        f"**Jurisdiction:** {classification.get('jurisdiction', 'unknown')}",
    ]

    if verdict_data.get("urgent_deadlines"):
        parts += ["", "### ⏰ Urgent Deadlines"]
        parts += [f"- {d}" for d in verdict_data["urgent_deadlines"]]

    if verdict_data.get("next_steps"):
        parts += ["", "### Next Steps"]
        parts += [f"{i+1}. {s}" for i, s in enumerate(verdict_data["next_steps"])]

    for f in findings:
        parts += [
            "",
            f"### {f['agent_name'].title()} Analysis *(confidence: {f.get('confidence', 'medium')})*",
            f['summary'],
        ]
        if f.get("key_points"):
            parts += [f"- {p}" for p in f["key_points"]]
        if f.get("deadlines"):
            parts += ["**Deadlines:** " + ", ".join(f["deadlines"])]

    if draft:
        parts += [
            "",
            "### ✉️ Suggested Response",
            f"**Subject:** {draft.get('subject', '')}",
            f"**Tone:** {draft.get('tone', '')}",
            "",
            draft.get("body", ""),
        ]

    if lawyer:
        parts += [
            "",
            "### ⚖️ Lawyer Recommendation",
            f"**Type:** {lawyer.get('lawyer_type', '')}",
            f"**Why:** {lawyer.get('reason', '')}",
            f"**Estimated cost:** {lawyer.get('estimated_cost_range', '')}",
            "**Questions to ask:**",
        ]
        parts += [f"- {q}" for q in lawyer.get("questions_to_ask", [])]

    latency_str = " | ".join(f"{k}: {v}s" for k, v in latencies.items())
    parts += ["", f"*Latency — {latency_str}*", "", "*This is not legal advice.*"]

    await cl.Message(content="\n".join(parts)).send()
