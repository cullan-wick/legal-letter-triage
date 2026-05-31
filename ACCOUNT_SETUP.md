# Account And Tool Setup

Set these up before the team starts coding. One person can own the paid/API accounts, but everyone should be able to run the app locally.

## Required

### GitHub

Purpose:

- Shared repo
- Branches and PRs
- Public submission history

Setup:

1. Make sure every teammate has access to `https://github.com/cullan-wick/legal-letter-triage`.
2. Protect `main` informally during the hackathon: branch work, PR or reviewed merge, then pull latest.
3. Confirm everyone can run:

```bash
git clone https://github.com/cullan-wick/legal-letter-triage.git
```

### W&B / Weave

Purpose:

- Main prize strategy
- Trace every agent call
- Show input, output, latency, and graph behavior during demo

Setup:

1. Create or log into a W&B account.
2. Create/copy a W&B API key.
3. Set `WANDB_API_KEY` in local `.env`.
4. Use one shared project name:

```dotenv
WEAVE_PROJECT=legal-letter-triage
```

Demo note:

- One person should be logged into W&B in the browser before demo time.
- Capture a screenshot of the best trace as backup.

### Model Provider API Key

Purpose:

- LLM calls for orchestrator, specialists, synthesis, and drafting

Recommended default:

- Anthropic Claude API if available through the hackathon/API form.

Setup:

1. Create the provider account.
2. Add billing/credits if required.
3. Create one hackathon-specific API key.
4. Put it in local `.env`, never in git:

```dotenv
ANTHROPIC_API_KEY=
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-sonnet-4-6
```

Cost safety:

- Use a separate key for this project.
- Set a low spend cap if the provider supports it.
- Do not put provider keys into Claude Code/Codex global config unless you intend those agents to spend API credits.

## Strongly Recommended

### Tavily

Purpose:

- Search-backed statutes/protections agent
- Search-backed lawyer finder

Setup:

1. Create a Tavily account.
2. Copy the API key into `.env`:

```dotenv
TAVILY_API_KEY=
```

Demo note:

- Treat Tavily as stretch. The app must work without it.
- Search must fail soft so live-network issues do not break the demo.

## Not Required For Day-One Build

### LangGraph

Purpose:

- Python library for graph orchestration

Account needed?

- No account is needed for local open-source LangGraph usage.
- Install it from `requirements.txt`.

Potential later add-on:

- LangSmith/LangGraph Platform account if the team wants hosted tracing/deployment, but this is not necessary for the hackathon demo because Weave is the tracing story.

### Streamlit Community Cloud

Purpose:

- Optional hosted demo

Account needed?

- Not required. A local Streamlit demo is enough.

Use only if:

- The local demo is stable early and someone has spare time.

### MCP

Purpose:

- Optional protocol layer for tools

Account needed?

- No account by itself.

Use only if:

- The core demo is stable and there is time for a safe stretch.

## Local `.env` Template

Copy `.env.example` to `.env` locally:

```bash
cp .env.example .env
```

Then fill:

```dotenv
ANTHROPIC_API_KEY=
TAVILY_API_KEY=
WANDB_API_KEY=
WEAVE_PROJECT=legal-letter-triage
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-sonnet-4-6
```

Never commit `.env`.

## Python Version

Use Python 3.11 or newer. Do not use macOS's default Python 3.9 for this project; modern LangGraph/MCP packages may not resolve under it.

Recommended:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On the current machine, this worked:

```bash
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
