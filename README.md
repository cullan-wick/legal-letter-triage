# LetterLens - Legal Letter Triage

LetterLens is a multi-agent legal-letter triage demo for a hackathon build. It turns intimidating legal letters into a plain-English verdict, next steps, a drafted response, and an auditable W&B Weave trace.

This is legal information and orientation, not legal advice.

## What It Does

- Classifies a pasted or canned legal letter.
- Runs specialist reviews for risk, rights, and obligations.
- Synthesizes a verdict: `handle_yourself`, `consult_lawyer`, or `urgent`.
- Drafts a calibrated response.
- Conditionally recommends what kind of lawyer to contact.
- Surfaces the full agent process in Weave.

## Architecture

```text
Streamlit UI
  -> graph runner
  -> orchestrator
  -> risk / rights / obligations
  -> synthesis
  -> response drafter
  -> lawyer finder, conditional
```

## Team Workflow

Start here:

- `ULTIMATE_HACKATHON_PLAN.md`
- `TEAM_AGENT_GUIDE.md`
- `ACCOUNT_SETUP.md`
- `CLAUDE.md`

Each teammate should work on their lane branch, not directly on `main`.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` with the keys listed in `ACCOUNT_SETUP.md`.

Use Python 3.11 or newer. On this machine, the working venv was created with:

```bash
/opt/homebrew/bin/python3.13 -m venv .venv
```

## Run Tests

The initial scaffold includes a dependency-light spine test:

```bash
.venv/bin/python -m unittest tests.test_spine
```

## Run App

After Streamlit is wired:

```bash
streamlit run app.py
```

## Sponsor / Tool Story

- W&B Weave: trace every agent input, output, and latency.
- LangGraph: orchestrate graph routing and conditional edges.
- Tavily: optional stretch for grounded statutes and lawyer search.
- Anthropic Claude or approved model provider: agent reasoning.
