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

VERDICT_LABEL = {
    "handle_yourself": "HANDLE YOURSELF",
    "consult_lawyer": "CONSULT A LAWYER",
    "urgent": "URGENT — ACT NOW",
}


@cl.on_chat_start
async def on_start():
    await cl.Message(
        content=(
            "## Legal Letter Triage\n\n"
            "Paste a legal letter, upload a PDF, or load a sample below.\n\n"
            "**Load a sample:**\n"
            "- `sample: debt` — debt collection letter\n"
            "- `sample: eviction` — eviction notice\n"
            "- `sample: employment` — employment warning\n\n"
            "---\n"
            "*This is not legal advice. This tool helps you understand what to do next.*"
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
            await cl.Message(content="Unknown sample. Try: `sample: debt`, `sample: eviction`, or `sample: employment`").send()
            return
        text = SAMPLES[sample_key]
        await cl.Message(content=f"Loaded: **{sample_key}**\n\n```\n{text[:400]}...\n```").send()

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

    thinking = cl.Message(content="Analysing your letter — this takes about 30 seconds...")
    await thinking.send()

    result = run(text)

    verdict_data = result.get("verdict") or {}
    verdict = verdict_data.get("verdict", "consult_lawyer")
    icon = VERDICT_COLOR.get(verdict, "⚪")
    label = VERDICT_LABEL.get(verdict, verdict.upper())
    classification = result.get("classification") or {}
    findings = result.get("specialist_findings") or []
    draft = result.get("draft_response") or {}
    lawyer = result.get("lawyer_recommendation") or {}
    latencies = result.get("latencies") or {}
    errors = result.get("errors") or []

    parts = [
        f"# {icon} {label}",
        "",
        f"> {verdict_data.get('reason', '')}",
        "",
        f"**Letter type:** {classification.get('letter_type', 'unknown')}  |  "
        f"**Urgency:** {classification.get('urgency', 'unknown')}  |  "
        f"**Jurisdiction:** {classification.get('jurisdiction', 'unknown')}",
    ]

    # Urgent deadlines
    if verdict_data.get("urgent_deadlines"):
        parts += ["", "---", "## ⏰ Urgent Deadlines"]
        parts += [f"- {d}" for d in verdict_data["urgent_deadlines"]]

    # Next steps
    if verdict_data.get("next_steps"):
        parts += ["", "---", "## What to Do Next"]
        parts += [f"{i+1}. {s}" for i, s in enumerate(verdict_data["next_steps"])]

    # Specialist findings
    parts += ["", "---", "## Specialist Findings"]
    for f in findings:
        if f.get("error"):
            parts += ["", f"**{f['agent_name'].title()}:** *(analysis failed — treat with caution)*"]
            continue
        conf = f.get("confidence", "medium")
        parts += ["", f"### {f['agent_name'].title()} *(confidence: {conf})*"]
        parts += [f['summary']]
        if f.get("key_points"):
            parts += [f"- {p}" for p in f["key_points"]]
        if f.get("deadlines"):
            real = [d for d in f["deadlines"] if "no explicit" not in d.lower() and "unable" not in d.lower()]
            if real:
                parts += ["", f"**Deadlines:** {', '.join(real)}"]

    # Drafted response
    if draft:
        parts += [
            "", "---",
            "## Suggested Response Letter",
            f"**Subject:** {draft.get('subject', '')}",
            f"**Tone:** {draft.get('tone', '')}",
            "",
            draft.get("body", ""),
        ]

    # Lawyer recommendation
    if lawyer and verdict in ("consult_lawyer", "urgent"):
        parts += ["", "---", "## ⚖️ Legal Help Recommendation"]
        parts += [f"**Type of lawyer:** {lawyer.get('lawyer_type', '')}"]
        parts += [f"**Why:** {lawyer.get('reason', '')}"]

        if lawyer.get("urgency_guidance"):
            parts += [f"**Timing:** {lawyer['urgency_guidance']}"]

        if lawyer.get("questions_to_ask"):
            parts += ["", "**Questions to ask:**"]
            parts += [f"- {q}" for q in lawyer["questions_to_ask"]]

        if lawyer.get("documents_to_prepare"):
            parts += ["", "**Documents to gather:**"]
            parts += [f"- {d}" for d in lawyer["documents_to_prepare"]]

        if lawyer.get("jurisdiction_note"):
            parts += ["", f"**Local resources:** {lawyer['jurisdiction_note']}"]

        if lawyer.get("estimated_cost_range"):
            parts += ["", f"**Cost guidance:** {lawyer['estimated_cost_range']}"]

    # Footer
    latency_str = " | ".join(f"{k}: {v}s" for k, v in latencies.items())
    parts += [
        "", "---",
        f"*Agent latencies — {latency_str}*",
        f"*Weave trace: wandb.ai/nicholaslutta7-xoori-inc/legal-letter-triage/weave*",
        "",
        "*This is not legal advice. This tool helps you understand what to do next.*",
    ]

    await cl.Message(content="\n".join(parts)).send()
