# Legal Letter Triage — Agent Context

## What This Is
A multi-agent legal letter triage system. Input: a legal letter (text or PDF). Output: a plain-English triage report with verdict, specialist findings, drafted response, and optional lawyer recommendation.

## Win Conditions
1. Primary: Best Use of Weave — every agent function decorated with `@weave.op()`, named clearly.
2. Secondary: Most Sophisticated Agent Harness — visible orchestration graph with conditional routing.

## Stack
- **LangGraph** — graph orchestration (`src/graph.py`)
- **W&B Weave** — observability, wrap all agent functions with `@weave.op()`
- **Chainlit** — UI (`app.py`)
- **OpenAI SDK** — model calls via W&B Inference API (`https://api.inference.wandb.ai/v1`)
- **PyMuPDF** — PDF/image ingestion
- **Pydantic** — structured agent I/O

## Model
Default model: `qwen3-coder-480b` via W&B Inference (OpenAI-compatible).
Keep model configurable via `src/config.py`.

## Core Graph
```
letter_text → orchestrator → [risk, rights, obligations] → synthesis → response_drafter → (conditional) lawyer_finder
```

## Rules
- All agent functions MUST be decorated with `@weave.op()` and named clearly (e.g. `risk_assess`, `rights_review`).
- All agent I/O MUST use Pydantic models defined in `src/schemas.py`.
- Agents must fail soft — return an error entry, never crash the graph.
- Synthesis must always produce a verdict even if a specialist fails.
- Safe verdict default: `consult_lawyer` with reason "One or more checks were incomplete."
- `lawyer_finder` runs ONLY when verdict is `consult_lawyer` or `urgent`.
- Never commit `.env`. Check `git status` before every push.
- Output must include: "This is not legal advice."

## Verdict Values
Only these three:
- `handle_yourself`
- `consult_lawyer`
- `urgent`

## File Ownership (4-lane team)
- Lane 1: `src/config.py`, `src/schemas.py`, `src/graph.py`, `tests/test_spine.py`
- Lane 2: `src/agents/risk.py`, `src/agents/rights.py`, `src/agents/obligations.py`
- Lane 3: `app.py`, `samples/`
- Lane 4: `src/agents/response_drafter.py`, `src/agents/lawyer_finder.py`, `src/tools/search.py`, `README.md`

## Spine (keep green at all times)
```
sample letter → graph.invoke() → orchestrator → risk → synthesis → Weave trace appears
```
If the spine breaks, fix it before adding anything new.
