from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ── Verdict ──────────────────────────────────────────────────────────────────

Verdict = Literal["handle_yourself", "consult_lawyer", "urgent"]


# ── Agent output models ───────────────────────────────────────────────────────

class Classification(BaseModel):
    letter_type: str = Field(description="e.g. debt_collection, eviction, employment_warning")
    jurisdiction: str = Field(description="Inferred jurisdiction if determinable, else 'unknown'")
    urgency: Literal["low", "medium", "high"]
    summary: str


class SpecialistFinding(BaseModel):
    agent_name: str
    summary: str
    key_points: list[str]
    deadlines: list[str] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"] = "medium"
    needs_lawyer: bool = False
    error: Optional[str] = None


class SynthesisOutput(BaseModel):
    verdict: Verdict
    reason: str
    next_steps: list[str]
    urgent_deadlines: list[str] = Field(default_factory=list)


class DraftResponse(BaseModel):
    subject: str
    body: str
    tone: str


class LawyerRecommendation(BaseModel):
    lawyer_type: str
    reason: str
    questions_to_ask: list[str]
    estimated_cost_range: str


# ── LangGraph state ───────────────────────────────────────────────────────────

class AgentState(TypedDict):
    letter_text: str
    classification: Optional[dict]
    urgency_signal: str              # "low"|"medium"|"high" — set by orchestrator, read by synthesis
    # Per-specialist staging slots: each parallel specialist writes its OWN key so there is
    # never a concurrent write to a shared channel. The `collect` node folds these into
    # specialist_findings, which keeps synthesis/drafter/lawyer_finder unchanged.
    risk_finding: Optional[dict]
    rights_finding: Optional[dict]
    obligations_finding: Optional[dict]
    specialist_findings: list[dict]
    verdict: Optional[dict]
    draft_response: Optional[dict]
    lawyer_recommendation: Optional[dict]
    latencies: dict
    errors: list[str]
