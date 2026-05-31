# Team Agent Guide - Legal Letter Triage

This file is the shared operating manual for the four humans and their Claude Code/Codex agents. Read this before writing code.

The goal is simple: four people can work in parallel without stepping on each other, while the project keeps a green demo spine at all times.

## Source Of Truth

Read these in order:

1. `ULTIMATE_HACKATHON_PLAN.md` - product strategy, scope, timeline, and demo priorities.
2. `TEAM_AGENT_GUIDE.md` - team workflow, file ownership, branch rules, and handoff protocol.
3. `README.md` - public-facing project description once it exists.

When there is a conflict, follow the latest committed version of `ULTIMATE_HACKATHON_PLAN.md`, then this file.

## Team Shape

We are a team of 4. Each person should run their own Claude Code/Codex session on their own branch.

Do not all push directly to `main`.

Recommended lanes:

| Lane | Human + Agent Role | Primary Files | Must Deliver |
|---|---|---|---|
| Lane 1 | Graph + Weave owner | `src/graph.py`, `src/schemas.py`, `src/config.py`, `tests/test_spine.py` | Green spine and traceable graph |
| Lane 2 | Specialist agents owner | `src/agents/risk.py`, `src/agents/rights.py`, `src/agents/obligations.py`, optional `statutes.py`, `tone_intent.py` | Useful structured specialist outputs |
| Lane 3 | UI + demo owner | `app.py`, `samples/`, screenshots/video assets, README screenshots | Streamlit demo surface and canned samples |
| Lane 4 | Actions + submission owner | `src/agents/response_drafter.py`, `src/agents/lawyer_finder.py`, `src/tools/search.py`, `README.md`, `.env.example` | Conditional routing actions, submission polish |

Lane 1 is the critical path. Everyone else should make their work fit the interfaces Lane 1 defines.

## Branch Workflow

Each lane works on a branch:

```bash
git checkout main
git pull
git checkout -b lane-1-graph-weave
```

Use these branch names:

- `lane-1-graph-weave`
- `lane-2-specialists`
- `lane-3-ui-demo`
- `lane-4-actions-submission`

Commit early and often:

```bash
git add .
git commit -m "Add risk specialist output model"
git push -u origin lane-2-specialists
```

Open PRs into `main` when a slice is working. During the hackathon, PR review can be fast, but one person should still inspect the diff before merge.

## Integration Rule

One person is the integrator at any given time.

Integrator responsibilities:

- Own merges into `main`.
- Keep `main` runnable.
- Pull each lane's branch and resolve conflicts.
- Reject changes that break the spine close to demo time.
- Decide when a stretch feature is too risky.

Suggested integration order:

1. Lane 1 scaffold and spine.
2. Lane 2 core specialists.
3. Lane 4 drafter + lawyer finder.
4. Lane 3 UI.
5. Lane 4 README/submission updates.
6. Stretch work only after the demo path is stable.

## Golden Rule

Keep the spine green:

```text
sample letter -> graph.invoke -> orchestrator -> specialists -> synthesis -> response -> UI -> Weave trace
```

If a change breaks this path, fix it immediately or revert that change. Do not stack more work on a broken spine.

## Shared Interfaces

Lane 1 defines the final schemas. Until those exist, use this provisional contract.

### Verdict Values

Only use these values:

```text
handle_yourself
consult_lawyer
urgent
```

### Agent Output Shape

Each specialist should return structured data like:

```python
{
    "agent_name": "risk",
    "summary": "Plain-English finding.",
    "key_points": ["Point 1", "Point 2"],
    "deadlines": [],
    "confidence": "medium",
    "needs_lawyer": true
}
```

### State Shape

The graph state should contain at least:

```python
{
    "letter_text": str,
    "classification": dict,
    "specialist_findings": list,
    "verdict": dict,
    "draft_response": dict | None,
    "lawyer_recommendation": dict | None,
    "latencies": dict,
    "errors": list
}
```

Agents must fail soft. If an agent errors, return an error entry and let synthesis continue.

## File Ownership

Avoid editing another lane's files unless you coordinate first.

Safe ownership:

### Lane 1 - Graph + Weave

Owns:

- `src/config.py`
- `src/schemas.py`
- `src/graph.py`
- `tests/test_spine.py`
- core package structure

Should avoid:

- UI styling
- detailed specialist prompt tuning
- README polish unless needed for setup

### Lane 2 - Specialist Agents

Owns:

- `src/agents/risk.py`
- `src/agents/rights.py`
- `src/agents/obligations.py`
- optional `src/agents/statutes.py`
- optional `src/agents/tone_intent.py`

Should avoid:

- changing graph edges directly without syncing with Lane 1
- adding live network calls before the core app is stable

### Lane 3 - UI + Demo

Owns:

- `app.py`
- `samples/debt_collection.txt`
- `samples/eviction_notice.txt`
- `samples/employment_warning.txt`
- demo screenshots or video assets

Should avoid:

- changing schemas
- changing agent internals
- making the UI depend on live network calls

### Lane 4 - Actions + Submission

Owns:

- `src/agents/response_drafter.py`
- `src/agents/lawyer_finder.py`
- `src/tools/search.py`
- `.env.example`
- `README.md`

Should avoid:

- MCP refactor before the demo path works
- search behavior that can crash the app

## Agent Startup Prompt

Each Claude Code/Codex session should start with this:

```text
Read ULTIMATE_HACKATHON_PLAN.md and TEAM_AGENT_GUIDE.md.

I am working on Lane [1/2/3/4]: [lane name].

Stay inside my lane's file ownership unless a change is required for integration. Keep the demo spine green. Use structured Pydantic outputs where relevant. Decorate agent functions with @weave.op() when implementing agents. Do not commit secrets. Before editing, summarize the files you will touch.
```

Then give the lane-specific task.

## Lane-Specific Prompts

### Lane 1 Prompt - Graph + Weave

```text
Implement the project scaffold and the green spine. Create config, schemas, graph, basic orchestrator/risk/synthesis stubs if needed, and tests/test_spine.py. The graph must run from a sample letter to a verdict and produce Weave-traceable ops. Keep interfaces stable for the other lanes.
```

### Lane 2 Prompt - Specialist Agents

```text
Implement risk, rights, and obligations agents with focused prompts and structured Pydantic outputs. Do not change graph wiring unless asked by Lane 1. Include deadline extraction in obligations. Keep outputs concise enough to render in the UI and inspect in Weave.
```

### Lane 3 Prompt - UI + Demo

```text
Build the Streamlit app and sample letters. The UI should load canned samples, run analysis only on an Analyze button click, show a classification summary, color-coded verdict banner, expandable specialist findings, deadlines, drafted response, lawyer recommendations when present, latency, Weave trace instructions, and a legal-information disclaimer.
```

### Lane 4 Prompt - Actions + Submission

```text
Implement response_drafter and lawyer_finder with structured outputs. Lawyer finder must run only for consult_lawyer or urgent verdicts once wired by Lane 1. Keep search optional and fail-soft. Maintain README.md as the public hackathon submission page.
```

## Handoff Protocol

Every handoff message should include:

```text
Lane:
Branch:
Files changed:
What works:
How to test:
Known risks:
Needs from other lanes:
```

Example:

```text
Lane: 2 specialists
Branch: lane-2-specialists
Files changed: src/agents/risk.py, src/agents/rights.py, src/agents/obligations.py
What works: each agent returns structured output using the provisional schema
How to test: pytest tests/test_spine.py after Lane 1 wires them
Known risks: obligations deadline extraction is simple regex + model summary
Needs from other lanes: Lane 1 should confirm final Pydantic model names
```

## Merge Checklist

Before merging any PR:

- `git status` is clean.
- No `.env`, API keys, account numbers, names, addresses, or private legal letters are committed.
- The app still runs the main sample.
- The spine test passes, or the PR clearly explains why tests cannot run yet.
- The UI path still works from a canned sample.
- Weave ops are still named clearly.
- README remains accurate.

## Demo Freeze

At 7:00, stop building features.

Allowed after freeze:

- Fix demo-breaking bugs.
- Improve README wording.
- Fix sample text.
- Fix obvious UI rendering issues.
- Rehearse and record.

Not allowed after freeze:

- New agents.
- MCP refactor.
- Major schema changes.
- Live search dependency changes.
- Full UI redesign.
- Anything that requires relearning how the app works.

## Conflict Resolution

If two lanes need the same file, the file's owner decides.

If the file has no clear owner, the integrator decides.

If a stretch feature threatens the demo, cut the stretch.

The project wins by being clear, traceable, and reliable. Fancy work that does not show up in the demo is lower priority than a clean Weave trace and a useful verdict.

