# Multi-Agent Systems Primer
### For engineers who haven't built one before

Read the section for your lane. Read the shared concepts first — everyone needs those.

---

## What Is a Multi-Agent System?

A single AI call is a function: you send text in, you get text out. That works for simple tasks.

A multi-agent system is a **pipeline of AI calls** where each one does one focused job, and the output of one feeds into the next. Think of it like an assembly line where each worker is a specialist. No single worker sees the whole picture — but the line produces something none of them could alone.

In our app:

```
Letter text
    │
    ▼
Orchestrator (classify the letter)
    │
    ▼
Risk Agent ──► Rights Agent ──► Obligations Agent
    │               │                  │
    └───────────────┴──────────────────┘
                    │
                    ▼
             Synthesis Agent (verdict)
                    │
                    ▼
           Response Drafter (always runs)
                    │
              ┌─────┴─────┐
              ▼           ▼
         handle_yourself  consult_lawyer / urgent
                               │
                               ▼
                        Lawyer Finder
```

Each box is a **node**. The arrows are **edges**. The whole thing is a **graph**. LangGraph is the library that manages this graph.

---

## The Three Things Every Multi-Agent System Needs

### 1. Shared State

Agents can't talk to each other directly. Instead, they all read from and write to a shared state object — a dictionary that gets passed through every node. Think of it as the whiteboard everyone writes on.

In our project, this is `AgentState` in `src/schemas.py`:

```python
class AgentState(TypedDict):
    letter_text: str           # the original letter — never changes
    classification: dict       # orchestrator writes this
    specialist_findings: list  # risk/rights/obligations each append to this
    verdict: dict              # synthesis writes this
    draft_response: dict       # response_drafter writes this
    lawyer_recommendation: dict # lawyer_finder writes this (conditional)
    latencies: dict            # each agent records how long it took
    errors: list               # agents write errors here instead of crashing
```

**Rule:** An agent receives the full state, does its work, writes its result into the relevant field, and returns the updated state. It must never crash — if something goes wrong, it writes to `errors` and returns a safe default.

### 2. Nodes (the agents)

A node is just a Python function that takes `AgentState` and returns `AgentState`. That's it.

```python
def risk_assess(state: AgentState) -> AgentState:
    # 1. Read what you need from state
    letter = state["letter_text"]

    # 2. Call the LLM
    response = client.chat.completions.create(...)

    # 3. Write your result back into state
    state["specialist_findings"].append(result)

    # 4. Return the updated state
    return state
```

Every agent in `src/agents/` follows this exact pattern.

### 3. The Graph (the wiring)

The graph defines the order agents run in and when branching happens. This lives in `src/graph.py`.

```python
graph = StateGraph(AgentState)

# Register nodes
graph.add_node("risk", risk_assess)
graph.add_node("rights", rights_review)

# Wire edges (defines execution order)
graph.add_edge("risk", "rights")  # risk runs, then rights runs

# Conditional edge (branching logic)
graph.add_conditional_edges("response_drafter", should_find_lawyer)

# Compile and run
app = graph.compile()
result = app.invoke(initial_state)
```

---

## Observability: Why Every Function Has `@weave.op()`

W&B Weave records every function call — what went in, what came out, how long it took. You attach it with one decorator:

```python
import weave

@weave.op()
def risk_assess(state: AgentState) -> AgentState:
    ...
```

That's the entire integration. Weave handles the rest automatically. When you open the W&B dashboard, you'll see every agent call as a node in a trace tree. This is one of the two prizes we're targeting — make sure every agent function has this decorator.

**Op naming tip:** The function name IS the op name in Weave. Name your functions clearly: `risk_assess`, `rights_review`, `obligations_extract`, `synthesize_verdict`, `draft_response`, `find_lawyer`. Judges will read these names.

---

## Structured Output: Why We Use Pydantic

LLMs return free text. Free text breaks code. Pydantic forces the output into a strict schema so every agent always returns the same shape.

```python
from pydantic import BaseModel
from typing import Literal

class SpecialistFinding(BaseModel):
    agent_name: str
    summary: str
    key_points: list[str]
    deadlines: list[str]
    confidence: Literal["low", "medium", "high"]
    needs_lawyer: bool
```

Tell the LLM to respond in JSON, then validate it:

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=[...],
    response_format={"type": "json_object"},  # forces JSON output
)
data = SpecialistFinding.model_validate_json(response.choices[0].message.content)
state["specialist_findings"].append(data.model_dump())
```

If validation fails, catch the exception and write a safe default to state. Never let a bad LLM response crash the graph.

---

## The Fail-Soft Rule

Every agent must handle errors gracefully. The spine must never break because one specialist returned garbage.

```python
try:
    # normal path
    data = SpecialistFinding.model_validate_json(response.choices[0].message.content)
    state["specialist_findings"].append(data.model_dump())
except Exception as e:
    # safe fallback — log the error, write a default, keep going
    state["errors"].append(f"risk: {e}")
    state["specialist_findings"].append(
        SpecialistFinding(
            agent_name="risk",
            summary="Risk assessment failed.",
            key_points=[],
            error=str(e)
        ).model_dump()
    )
```

Synthesis has an additional rule: even if all specialists fail, it must still produce a verdict. Default to `consult_lawyer` with a note that checks were incomplete.

---

## How the Model Is Called

We use the OpenAI SDK pointed at W&B's inference API. This means:
- You write normal OpenAI-style code
- The model runs on W&B's servers (free credits from the hackathon)
- Every call is automatically traced in Weave

```python
from src.config import client, MODEL

response = client.chat.completions.create(
    model=MODEL,                          # "qwen3-coder-480b" by default
    messages=[
        {"role": "system", "content": "Your focused system prompt here."},
        {"role": "user", "content": f"The letter:\n\n{state['letter_text']}"},
    ],
    response_format={"type": "json_object"},
)
```

Never hardcode the model name. Always import `MODEL` from `src/config.py` so the whole team can swap models from one place.

---

## Lane-Specific Guides

---

### Lane 1 — Graph + Weave (`feature/langgraph-core`)

**You are the critical path.** Every other lane depends on what you define.

**Your job in order:**
1. Define `AgentState` in `src/schemas.py` — agree with the team on field names before anyone writes code
2. Define all Pydantic output models in `src/schemas.py`
3. Write `src/config.py` — loads env vars, calls `weave.init()`, creates the OpenAI client
4. Write stub versions of each agent (just return the state with a hardcoded default) so the graph can run before real agents exist
5. Wire the graph in `src/graph.py`
6. Write the spine test in `tests/test_spine.py`

**The LangGraph pattern you need to know:**

```python
from langgraph.graph import StateGraph, END

graph = StateGraph(AgentState)

# Add every node
graph.add_node("orchestrator", orchestrator_classify)
graph.add_node("risk", risk_assess)
graph.add_node("synthesis", synthesize_verdict)
graph.add_node("response_drafter", draft_response)
graph.add_node("find_lawyer", find_lawyer)

# Set where the graph starts
graph.set_entry_point("orchestrator")

# Linear edges
graph.add_edge("orchestrator", "risk")
graph.add_edge("risk", "synthesis")
graph.add_edge("synthesis", "response_drafter")

# Conditional edge — function decides what node runs next
def should_find_lawyer(state: AgentState) -> str:
    verdict = state.get("verdict", {}).get("verdict", "consult_lawyer")
    return "find_lawyer" if verdict in ("consult_lawyer", "urgent") else END

graph.add_conditional_edges("response_drafter", should_find_lawyer)
graph.add_edge("find_lawyer", END)

app = graph.compile()
```

**Running the graph:**

```python
result = app.invoke({
    "letter_text": "...",
    "classification": None,
    "specialist_findings": [],
    "verdict": None,
    "draft_response": None,
    "lawyer_recommendation": None,
    "latencies": {},
    "errors": [],
})
```

**Stub agent pattern** — write this first so the graph runs before Lane 2 finishes:

```python
def risk_assess(state: AgentState) -> AgentState:
    # STUB — replace with real implementation
    state["specialist_findings"].append({
        "agent_name": "risk",
        "summary": "Stub: risk assessment not yet implemented.",
        "key_points": [],
        "deadlines": [],
        "confidence": "low",
        "needs_lawyer": False,
    })
    return state
```

**Your definition of done:** `python tests/test_spine.py` passes and a Weave trace appears at wandb.ai.

---

### Lane 2 — Specialist Agents (`feature/specialist-prompts`)

**Your job:** Implement `risk.py`, `rights.py`, `obligations.py` — each a focused LLM call that appends a `SpecialistFinding` to `state["specialist_findings"]`.

**The pattern — copy this for each agent, change the system prompt:**

```python
import time
import weave
from src.config import client, MODEL
from src.schemas import AgentState, SpecialistFinding

@weave.op()
def rights_review(state: AgentState) -> AgentState:
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a consumer rights specialist. "
                        "Identify rights the recipient has. "
                        "Respond ONLY with valid JSON matching: "
                        '{"agent_name":"rights","summary":str,"key_points":[str],'
                        '"deadlines":[str],"confidence":"low"|"medium"|"high","needs_lawyer":bool}. '
                        "This is not legal advice."
                    ),
                },
                {
                    "role": "user",
                    "content": f"What rights does the recipient have?\n\n{state['letter_text']}",
                },
            ],
            response_format={"type": "json_object"},
        )
        data = SpecialistFinding.model_validate_json(response.choices[0].message.content)
        state["specialist_findings"].append(data.model_dump())
    except Exception as e:
        state["errors"].append(f"rights: {e}")
        state["specialist_findings"].append(
            SpecialistFinding(agent_name="rights", summary="Rights review failed.",
                              key_points=[], error=str(e)).model_dump()
        )
    state["latencies"]["rights"] = round(time.time() - start, 2)
    return state
```

**System prompt guidance per agent:**

| Agent | Focus | Key instruction |
|---|---|---|
| `risk_assess` | Worst realistic outcome | "What is the worst realistic consequence if the recipient ignores this?" |
| `rights_review` | Recipient's protections | "What rights does the recipient have that the sender did not mention?" |
| `obligations_extract` | Required actions + deadlines | "Extract every deadline, required action, and consequence of inaction." |

**Rules:**
- Never say "legal advice" — always add "This is not legal advice." to system prompts
- Keep `key_points` to 3–5 bullets — judges see this in the UI
- Always populate `deadlines` even if empty list — synthesis depends on it
- Do not change `AgentState` field names — only Lane 1 owns those

---

### Lane 3 — Ingestion + UI + Demo (`feature/ui-and-parser`)

**Your job:** Build `app.py` (Chainlit) and the three sample letters. You own what judges see.

**Chainlit basics:**

```python
import chainlit as cl

@cl.on_chat_start
async def on_start():
    # Runs once when a user opens the app
    await cl.Message(content="Welcome message here.").send()

@cl.on_message
async def on_message(message: cl.Message):
    # Runs every time the user sends something
    text = message.content

    # Access uploaded files
    for el in message.elements:
        if el.path.endswith(".pdf"):
            # process the PDF
            pass

    # Send a response
    await cl.Message(content="Response here.").send()
```

**PDF parsing with PyMuPDF:**

```python
import fitz  # PyMuPDF

def extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)
```

**Calling the graph from the UI:**

```python
from src.graph import run

result = run(letter_text)  # returns the full AgentState dict
verdict = result["verdict"]["verdict"]  # "handle_yourself" | "consult_lawyer" | "urgent"
```

**Verdict color mapping:**
```python
COLORS = {
    "handle_yourself": "🟢",
    "consult_lawyer":  "🟡",
    "urgent":          "🔴",
}
```

**Rules:**
- Do not call the LLM directly — always go through `src/graph.run()`
- Do not change schemas — only Lane 1 owns those
- The three sample letters live in `samples/` — use them as canned demos

---

### Lane 4 — Synthesis + Weave + Submission (`feature/synthesis-and-weave`)

**Your job:** Build the synthesis agent (merges all specialist findings into a verdict), response drafter, and lawyer finder. Own the Weave trace quality and the README.

**Synthesis pattern** — reads everything, produces a verdict:

```python
@weave.op()
def synthesize_verdict(state: AgentState) -> AgentState:
    # Build a summary of all specialist findings to give to the LLM
    findings_text = "\n\n".join(
        f"[{f['agent_name'].upper()}] {f['summary']}"
        for f in state["specialist_findings"]
    )

    # Ask the LLM to make a judgment call
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Produce a verdict: handle_yourself, consult_lawyer, or urgent."},
            {"role": "user", "content": f"Findings:\n{findings_text}"},
        ],
        response_format={"type": "json_object"},
    )

    # Always have a safe default
    try:
        data = SynthesisOutput.model_validate_json(response.choices[0].message.content)
        state["verdict"] = data.model_dump()
    except Exception as e:
        state["errors"].append(f"synthesis: {e}")
        state["verdict"] = {
            "verdict": "consult_lawyer",
            "reason": "One or more checks were incomplete — review before acting.",
            "next_steps": ["Consult a lawyer before responding."],
            "urgent_deadlines": [],
        }
    return state
```

**Weave op naming checklist** — make sure every function name is exactly this:

| Agent | Function name (= Weave op name) |
|---|---|
| Orchestrator | `orchestrator_classify` |
| Risk | `risk_assess` |
| Rights | `rights_review` |
| Obligations | `obligations_extract` |
| Synthesis | `synthesize_verdict` |
| Response drafter | `draft_response` |
| Lawyer finder | `find_lawyer` |

**Checking your Weave trace:**
1. Run the app
2. Go to wandb.ai → your project → Weave tab
3. You should see a trace tree with all 7 op names visible
4. Each op should show: inputs, output, and duration
5. Screenshot this for the demo — it is a key judging moment

---

## Quick Reference Card

| Concept | How it works in this project |
|---|---|
| State | `AgentState` TypedDict in `src/schemas.py` — shared by all agents |
| Node | A Python function `(AgentState) -> AgentState` in `src/agents/` |
| Edge | `graph.add_edge("a", "b")` — b runs after a |
| Conditional edge | `graph.add_conditional_edges("node", fn)` — fn returns next node name |
| Observability | `@weave.op()` on every agent function |
| Structured output | Pydantic model + `response_format={"type": "json_object"}` |
| Model call | `client.chat.completions.create(model=MODEL, messages=[...])` |
| Fail soft | `try/except` in every agent — write to `state["errors"]`, return default |
| Run the graph | `from src.graph import run; result = run(letter_text)` |
| Run the app | `chainlit run app.py` |
| Run spine test | `python tests/test_spine.py` |

## The One Rule

Keep the spine green at all times:

```
letter_text → graph.invoke → orchestrator → risk → synthesis → verdict → Weave trace visible
```

If your change breaks this path, fix it before adding anything else.
