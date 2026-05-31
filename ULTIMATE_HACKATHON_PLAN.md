# Ultimate Hackathon Plan - Legal Letter Triage

## North Star

Build a public, demo-ready multi-agent system that turns a confusing legal letter into a plain-English triage report:

- What is this letter?
- What rights does the recipient have?
- What obligations and deadlines matter?
- What happens if they ignore it?
- Should they handle it themselves, consult a lawyer, or treat it as urgent?
- What reply should they send?
- If needed, what kind of lawyer should they look for?

The winning demo is not "we made a legal chatbot." The winning demo is:

> A visible orchestration harness where an orchestrator routes a legal letter through specialist agents, synthesizes a verdict, conditionally drafts next actions, and shows every step in a clean W&B Weave trace.

The product frame is triage and orientation, not legal advice.

## Prize Strategy

Primary target: **Best Use of Weave**

Secondary target: **Most Sophisticated Agent Harness**

Why this can win:

- The Weave trace is not just instrumentation; it is the product's trust layer.
- Judges can see the graph: orchestrator, specialists, synthesis, drafter, conditional lawyer finder.
- The output is useful, visceral, and easy to understand from one canned sample letter.
- The demo has a strong safety frame: "This is not legal advice. This helps people understand what to do next."

## Must-Ship Scope

Protect this scope. Everything else is stretch.

| Priority | Slice | Definition of Done | Target |
|---|---|---|---|
| 1 | Repo + safety scaffold | Public repo, `.gitignore`, `.env.example`, README stub, sample letters | 12:00 |
| 2 | Green spine | Paste/load letter -> orchestrator -> risk agent -> synthesis -> verdict -> Weave trace | 12:30 |
| 3 | Three-agent triage | Add rights + obligations/deadlines specialists | 2:30 |
| 4 | Conditional routing | Response drafter always runs; lawyer finder runs only for `consult_lawyer` or `urgent` | 3:30 |
| 5 | Demo UI | One Chainlit screen, canned samples, color verdict banner, expandable findings, drafted reply | 4:30 |
| 6 | Weave polish | Named ops, readable trace tree, per-agent latency, trace screenshot/link ready | 6:00 |
| 7 | Submission polish | README matches checklist, demo video under 2 minutes, final repo clean | 7:00 |

If the spine is not green by 12:30, cut specialists, not the spine.

## Stretch Scope, In Order

Only attempt these after must-ship scope is green and committed.

1. True parallel fan-out/fan-in in LangGraph.
2. Statutes agent with Tavily search and fail-soft citations.
3. Tone/intent agent to assess whether the letter is a real threat or scare tactic.
4. Weave Dataset + Evaluation from the sample letters.
5. MCP wrapper for the search tool via `langchain-mcp-adapters`.
6. A2A or networked agent services: do not attempt unless everything else is finished.

## Architecture

Minimum demo architecture:

```text
Chainlit UI
  |
  v
LangGraph
  |
  v
Orchestrator
  |
  +--> Risk Specialist
  +--> Rights Specialist
  +--> Obligations Specialist
  |
  v
Synthesis
  |
  +--> Response Drafter
  |
  +--> Lawyer Finder
       conditional: only if verdict is consult_lawyer or urgent
```

Full stretch architecture:

```text
Orchestrator
  |
  +--> Rights
  +--> Obligations
  +--> Risk
  +--> Statutes + Search
  +--> Tone & Intent
  |
  v
Synthesis
  |
  +--> Response Drafter
  |
  +--> Lawyer Finder + Search
```

Every node should be decorated with `@weave.op()` and named clearly enough that a judge can understand the trace without explanation.

## Stack

| Tool | Role | Why |
|---|---|---|
| Python 3.11+ | Core language | Fastest path to LangGraph, Chainlit, Pydantic, Weave |
| LangGraph | Agent orchestration | Clear graph, conditional routing, fan-out/fan-in story |
| Pydantic | Structured I/O | Stable synthesis and readable traces |
| W&B Weave | Observability | Main prize strategy and trust layer |
| Chainlit | UI | Chat-native demo surface with file upload |
| Tavily | Search | Stretch grounding for statutes and lawyer finder |
| MCP | Tool protocol | Stretch protocol story, not a critical path dependency |
| W&B Inference | Model provider | OpenAI-compatible API; default model `qwen3-coder-480b`; every call auto-traced in Weave |

## Repo Scaffold

```text
legal-letter-triage/
|-- CLAUDE.md
|-- README.md
|-- ULTIMATE_HACKATHON_PLAN.md
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- app.py
|-- src/
|   |-- __init__.py
|   |-- config.py
|   |-- schemas.py
|   |-- graph.py
|   |-- agents/
|   |   |-- orchestrator.py
|   |   |-- risk.py
|   |   |-- rights.py
|   |   |-- obligations.py
|   |   |-- synthesis.py
|   |   |-- response_drafter.py
|   |   |-- lawyer_finder.py
|   |   |-- statutes.py
|   |   `-- tone_intent.py
|   `-- tools/
|       `-- search.py
|-- samples/
|   |-- debt_collection.txt
|   |-- eviction_notice.txt
|   `-- employment_warning.txt
`-- tests/
    `-- test_spine.py
```

## Required Env Files

`.gitignore` must include:

```gitignore
.env
__pycache__/
.venv/
*.pyc
.streamlit/secrets.toml
```

`.env.example` should include:

```dotenv
OPENAI_API_KEY=                                   # W&B Inference key
OPENAI_BASE_URL=https://api.inference.wandb.ai/v1
WANDB_API_KEY=                                    # W&B dashboard key
WEAVE_PROJECT=legal-letter-triage
MODEL=qwen3-coder-480b
TAVILY_API_KEY=                                   # stretch only
```

Never commit `.env`.

## Implementation Plan

### Slice 0 - Project Context

Create `CLAUDE.md` before serious coding. It should tell the coding agent:

- This is a legal-letter triage app.
- The win conditions are orchestration and Weave.
- The core graph is orchestrator -> specialists -> synthesis -> drafter/lawyer finder.
- All agent I/O should be structured with Pydantic.
- All agent functions should be `@weave.op()`.
- The output must say it is not legal advice.
- The spine must stay green at all times.

### Slice 1 - Spine

Build the thinnest possible end-to-end path:

- `src/config.py`: load env, create model client, call `weave.init`.
- `src/schemas.py`: define state and Pydantic outputs.
- `src/agents/orchestrator.py`: classify letter type, jurisdiction, urgency.
- `src/agents/risk.py`: explain worst realistic outcome.
- `src/agents/synthesis.py`: produce verdict and next steps.
- `src/graph.py`: wire orchestrator -> risk -> synthesis.
- `tests/test_spine.py`: run on `samples/debt_collection.txt`.

Done means the test passes and a Weave trace appears.

### Slice 2 - Core Specialists

Add only the two specialists that most improve usefulness:

- `rights.py`: rights the recipient may have.
- `obligations.py`: required actions and deadlines.

Keep each output compact and structured. Do not add statutes or tone yet unless ahead of schedule.

### Slice 3 - Routing + Actions

Add the demo's strongest sophistication signal:

- `response_drafter.py`: always drafts a calibrated response.
- `lawyer_finder.py`: only runs when verdict is `consult_lawyer` or `urgent`.
- Conditional edge in `graph.py`.

For the first version, lawyer finder can recommend lawyer type, questions to ask, and estimated cost categories without live search.

### Slice 4 - Chainlit UI

One screen. No landing page. Run with `chainlit run app.py`.

Required UI:

- Text input for pasted letter; PDF/image file upload via PyMuPDF.
- Sample shortcuts: type `sample: debt`, `sample: eviction`, `sample: employment`.
- Classification summary at top.
- Large color-coded verdict banner (🟢 handle_yourself / 🟡 consult_lawyer / 🔴 urgent).
- Expandable specialist findings (Risk, Rights, Obligations).
- Deadline callouts.
- Drafted response.
- Lawyer finder section only when present.
- Per-agent latency.
- Weave trace link or clear instruction to open Weave project.
- One-line disclaimer: "This is not legal advice."

Avoid live typing during the demo. Use a canned sample.

### Slice 5 - Weave Polish

Make the Weave trace legible:

- Clear op names: `orchestrator_classify`, `risk_assess`, `rights_review`, `obligations_extract`, `synthesize_verdict`, `draft_response`, `find_lawyer`.
- Inputs and outputs are structured and short enough to inspect.
- Latency is visible in the UI.
- Capture a screenshot of the trace for backup.
- Rehearse opening the exact trace during the demo.

### Slice 6 - Stretch Grounding

Add search only after the core app is stable:

- `src/tools/search.py` wraps Tavily.
- `statutes.py` searches for likely rights/protections.
- `lawyer_finder.py` searches for directories and cost expectations.
- All search must fail soft.

Search failure behavior:

```python
{
    "citations": [],
    "note": "Search unavailable; proceeding with general triage."
}
```

Never let a network timeout break the demo.

## Engineering Guardrails

### State Merge

If true parallel fan-out is implemented, specialist outputs must write to reducer-friendly fields. If LangGraph raises `InvalidUpdateError`, the likely issue is concurrent branches writing the same state key.

De-risking rule:

- Try reducer fields for 45 minutes.
- If it fights back, run specialists sequentially and move on.

The judges care more about the visible trace and working verdict than perfect internal concurrency.

### Synthesis Nil Guard

Synthesis must produce a verdict even if one specialist fails or returns empty output.

Safe default:

- Verdict: `consult_lawyer`
- Reason: "One or more checks were incomplete, so this should be reviewed before acting."

This is safer for users and keeps the conditional lawyer-finder demo path alive.

### Chainlit Rerun Guard

Use `cl.user_session` or guard logic in `@cl.on_message` so re-sends do not re-run the graph accidentally. Run analysis only when the user explicitly sends a message or clicks Analyze.

### Secrets

Before pushing:

```bash
git status
git diff --cached
```

Confirm `.env` is not tracked.

## Demo-Killer Registry

| Failure Mode | Likelihood | Blast Radius | Mitigation |
|---|---:|---|---|
| No green spine | Medium | No demo | Build spine first; cut features if needed |
| Parallel state clobber | High if attempted early | 60-90 min lost | Sequential fallback after 45 min |
| Live search timeout | Medium | Demo crash | Fail-soft wrapper; pre-cache sample path |
| Empty specialist output breaks synthesis | Medium | Blank verdict | Nil guard and safe default |
| `.env` committed | Low/Medium | Public secret leak | `.gitignore` before first commit |
| Chainlit reruns graph on re-send | Medium | Slow/duplicated demo | Guard in on_message handler |
| MCP refactor breaks working app | High if attempted late | Unfinished at submission | Stretch only, dead last |
| README unfinished | Medium | Weak submission | Update throughout, finalize by 7:00 |

## Hour-by-Hour Plan

| Time | Owner Focus | Outcome |
|---|---|---|
| 11:30-12:00 | Repo lead | Public repo, scaffold, env safety, README stub |
| 12:00-12:30 | Graph lead | Spine green: orchestrator -> risk -> synthesis -> Weave |
| 12:30-2:30 | Agent lead + graph lead | Rights + obligations added; three-agent verdict working |
| 2:30-3:30 | Routing lead | Response drafter + conditional lawyer finder |
| 3:30-4:30 | UI lead | Chainlit demo screen with canned samples and PDF upload |
| 4:30-6:00 | Weave/demo lead | Trace polish, latency display, screenshot, rehearsal |
| 6:00-7:00 | Whole team | Pick one stretch only; record video; update README |
| 7:00-8:00 | Submission lead | Freeze code, final README, submit |

## Team Split

For a team of five:

- Graph + Weave owner: critical path, owns `src/graph.py`, state, traces.
- Specialist owner: owns `risk`, `rights`, `obligations`, and optional `statutes`/`tone_intent`.
- UI + demo owner: owns `app.py`, sample letters, demo video.
- Actions/tooling owner: owns `response_drafter`, `lawyer_finder`, optional Tavily/MCP.
- Floater/submission owner: tests real letters, hunts demo-killers, writes README/submission.

The graph owner should never be blocked waiting on final specialist implementations. Use stubs, then swap in real agents.

## Prompt Sequence

Use these prompts in order with the coding agent.

### Prompt 0 - Plan Only

```text
Read CLAUDE.md and ULTIMATE_HACKATHON_PLAN.md. Propose the LangGraph State schema and the Pydantic models for each must-ship agent output. List the files you'll create. Don't write code yet; show the plan.
```

### Prompt 1 - Spine

```text
Build the thinnest end-to-end path: src/config.py, src/schemas.py, orchestrator, risk, synthesis, and src/graph.py wiring orchestrator -> risk -> synthesis. Decorate every agent with @weave.op(). Add tests/test_spine.py that runs the graph on samples/debt_collection.txt. Get it running.
```

### Prompt 2 - Core Specialists

```text
Implement rights and obligations specialists, each in its own file, each with a focused prompt and Pydantic output, each decorated with @weave.op(). Update synthesis to combine risk, rights, and obligations into a verdict.
```

### Prompt 3 - Conditional Actions

```text
Add response_drafter, which always runs after synthesis. Add lawyer_finder and a conditional edge so it runs only when the verdict is consult_lawyer or urgent. Keep lawyer_finder non-networked for now. Update tests.
```

### Prompt 4 - UI

```text
Build app.py in Chainlit: PDF upload via PyMuPDF, sample shortcuts (sample: debt/eviction/employment), classification summary, color-coded verdict banner, expandable agent findings, deadlines, drafted reply, lawyer recommendations when present, per-agent latency, Weave trace link/instructions, and a disclaimer. Run with: chainlit run app.py
```

### Prompt 5 - Weave Polish

```text
Make every graph node and Weave op name clear and demo-friendly. Surface total and per-agent latency in the UI. Update README.md to match the hackathon submission checklist.
```

### Prompt 6 - One Stretch Only

```text
Choose the safest single stretch based on current status: true parallel fan-out, statutes+Tavily, tone_intent, Weave Dataset/Evaluation, or MCP wrapper. Implement only that stretch and keep the existing demo path green.
```

## README Submission Checklist

The README should be submission-ready:

- Project name and short tagline.
- 2-3 sentence summary.
- Problem it solves.
- How the user uses it.
- Architecture diagram or text graph.
- Sponsor/tools used and exactly how.
- Weave trace story.
- Safety disclaimer.
- How to run locally.
- Screenshots or demo GIF if time permits.
- Team members.
- What was built during the event.

## Demo Script

Target: under 2 minutes.

1. "Legal letters are designed to be intimidating. This app turns one into a structured triage report, not legal advice."
2. Load the canned debt collection or eviction sample.
3. Click Analyze.
4. Show verdict banner and deadlines.
5. Open specialist findings: risk, rights, obligations.
6. Show drafted response.
7. If verdict triggers it, show lawyer finder.
8. Open Weave trace.
9. "This trace is the trust layer: every agent, input, output, and latency is inspectable."
10. Close with: "The user gets an immediate next step, and the system leaves an auditable trail."

## Canned Demo Sample Strategy

Use one main sample and two backups.

Best main sample:

- Debt collection letter with a deadline, amount demanded, threat language, and enough ambiguity to need triage.

Backups:

- Eviction notice with date and jurisdiction.
- Employment warning or severance-related letter.

Redact all names, addresses, account numbers, and phone numbers.

## Final Freeze Rules

After 7:00:

- No new architecture.
- No MCP refactor.
- No live-network dependency unless already proven stable.
- No visual redesign.
- Only fix demo-breaking bugs, README issues, and submission details.

At freeze, the app should be able to run the main sample three times in a row without manual intervention.

## The One-Sentence Pitch

LetterLens is a multi-agent legal-letter triage system that gives people a plain-English verdict, next steps, and a drafted reply while exposing the entire agent decision process through W&B Weave.

