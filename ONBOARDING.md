# Legal Triage System: Team Onboarding & Setup

Welcome to the team! We are building a Multi-Agent Legal Notice Triage System using LangGraph, W&B (Weave + Inference API), and Chainlit. This document will get your local environment spun up and explain our development strategy.

---

## 🛠️ Step 1: Global Installation & Setup

Run these commands in your terminal to initialize your environment and install the entire core tech stack.

```bash
# 1. Clone repo and create virtual environment
git clone <your-github-repo-url>
cd legal-triage-agent
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 2. Upgrade pip and install the stack
pip install --upgrade pip
pip install langgraph weave chainlit openai pymupdf python-dotenv
```

### Create a `.env` File

Create a `.env` file in the root directory and add the credentials provided by the hackathon organizers:

```env
OPENAI_API_KEY="your-wandb-inference-api-key-here"
OPENAI_BASE_URL="https://api.inference.wandb.ai/v1"
WANDB_API_KEY="your-wandb-dashboard-api-key"
```

---

## 🏃‍♂️ Step 2: Verification Smoke Test

To verify everything is wired correctly, create a file named `app.py` and run `chainlit run app.py`. If a chat window opens in your browser, your stack is functional.

```python
import chainlit as cl
import weave
from openai import OpenAI

# Initialize Weave telemetry
weave.init("legal-triage-test")
client = OpenAI()  # Picks up base_url and key from .env automatically

@weave.op()
async def call_llm(user_message: str):
    response = client.chat.completions.create(
        model="qwen3-coder-480b",  # Or alternative W&B hosted model
        messages=[{"role": "user", "content": user_message}]
    )
    return response.choices[0].message.content

@cl.on_message
async def main(message: cl.Message):
    # This automatically shows up in Chainlit as a step
    response_text = await call_llm(message.content)
    await cl.Message(content=response_text).send()
```

---

## 📊 Agile GitHub & Team Breakdown (4 Developers)

To win a short hackathon, you must avoid developer gridlock. We will use a modular, protocol-driven architecture. Each developer will own an isolated slice of the stack that communicates via predefined data structures, preventing Git merge conflicts.

```
       [ Dev 1: Document Processing / PDF Ingestion ]
                             │
                             ▼ (Raw Text Payload)
              [ Dev 2: LangGraph Core Orchestrator ]
               /             │             \
              ▼              ▼              ▼
         [ Dev 3: Specialist Prompt Engineering & Agents ]
         (Rights)   (Obligations)   (Risk)   (Statutes)
              \              │              /
               ▼             ▼             ▼
              [ Dev 4: Synthesis, Weave & Presentation ]
```

---

## 👤 Developer 1: Ingestion & Frontend UI (The UX Engineer)

**Git Branch:** `feature/ui-and-parser`

**Responsibilities:**
- Build the Chainlit UI layout, message handlers, and sidebar components.
- Implement file upload support for PDFs and images.
- Build the document parsing script using PyMuPDF or a fallback OCR library to clean and extract raw string payloads from messy legal notifications.

**Target Milestone:** Deliver a clean string of text to Dev 2's LangGraph entry point by hour 6.

---

## 👤 Developer 2: LangGraph Core Architect (The System Plumber)

**Git Branch:** `feature/langgraph-core`

**Responsibilities:**
- Define the global `AgentState` TypedDict dictionary that stores variables as they pass through the application.
- Map out the parallel graph layout, node linkages, and asynchronous conditional routers.
- Write stub/mock functions for the specialist agents so the system can run locally even before the prompts are fully written.

**Target Milestone:** Have a working, cyclical graph architecture routing dummy text data end-to-end by hour 8.

---

## 👤 Developer 3: Prompt & AI Agent Engineer (The LLM Whisperer)

**Git Branch:** `feature/specialist-prompts`

**Responsibilities:**
- Design specialized, highly restrictive system instructions for the parallel agents: Rights, Obligations, Risk Analysis, and Statutes.
- Fine-tune the JSON schemas to ensure each agent outputs clean, structurally sound markdown blocks.
- Benchmark model performance between `qwen3-coder-480b` and `llama-4` variants on the W&B inference platform to optimize formatting and latency.

**Target Milestone:** Deliver four production-ready, isolated functions to be dropped into Dev 2's LangGraph nodes by hour 12.

---

## 👤 Developer 4: Synthesis, Telemetry & Pitch Prep (The Closer)

**Git Branch:** `feature/synthesis-and-weave`

**Responsibilities:**
- Build the Synthesis Agent that merges the markdown blocks from the 4 specialists into a cohesive triage report.
- Implement the Adversarial Response Simulator to challenge the output tones.
- Monitor the W&B Weave dashboard, ensure every function is wrapped with `@weave.op`, and build out a clean tracking layout to show the judges.
- Own the pitch slide deck construction and time the live demo.

---

## 🛠️ GitHub Branch & Merge Protocol (The Git Law)

1. **Protect Main** — Nobody pushes directly to `main`. All code goes to your assigned `feature/` branch.

2. **Contract-First Coding** — Before writing a single line of code, Dev 2 and Dev 3 must sit down and agree exactly on what keys the `AgentState` object will contain.

3. **Micro PRs** — Merge into `main` frequently. Do not wait until 4:00 AM to merge a giant 1,000-line change. Run your tests, open a Pull Request, have one team member review it immediately, and merge.
