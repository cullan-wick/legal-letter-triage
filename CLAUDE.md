# Legal Letter Triage - Project Context

## What This Is

Legal Letter Triage, demo name LetterLens, is a multi-agent system that reads a confusing legal letter and returns a plain-English triage report.

The output must help the user understand:

- what kind of letter this is
- what rights they may have
- what obligations and deadlines matter
- what risk they face if they ignore it
- whether to handle it themselves, consult a lawyer, or treat it as urgent
- what response they might send

This is legal information and triage, not legal advice.

## Win Conditions

Primary prize target: Best Use of Weave.

Secondary prize target: Most Sophisticated Agent Harness.

The demo should clearly show:

```text
Orchestrator -> specialist agents -> synthesis -> response drafter -> conditional lawyer finder
```

Every meaningful agent step should be visible in W&B Weave with readable op names.

## Architecture

Must-ship graph:

```text
letter_text
  -> orchestrator
  -> risk + rights + obligations
  -> synthesis
  -> response_drafter
  -> lawyer_finder only if verdict is consult_lawyer or urgent
```

Stretch graph:

```text
letter_text
  -> orchestrator
  -> risk + rights + obligations + statutes + tone_intent
  -> synthesis
  -> response_drafter
  -> lawyer_finder
```

## Core Rules

- Keep the spine green at all times.
- Prefer a working sequential graph over a broken parallel graph.
- Use structured outputs for every agent.
- Agents must fail soft and return error information instead of crashing the demo.
- Never commit `.env` or real legal letters with personal information.
- Keep outputs concise enough to render in Streamlit and inspect in Weave.
- Canned samples drive the demo; do not rely on live typing on stage.

## Verdict Values

Only use:

```text
handle_yourself
consult_lawyer
urgent
```

## Files To Read Before Work

1. `ULTIMATE_HACKATHON_PLAN.md`
2. `TEAM_AGENT_GUIDE.md`
3. `ACCOUNT_SETUP.md`
4. `CLAUDE.md`

