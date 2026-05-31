"""Shared state and output contracts for all lanes.

These lightweight dataclasses keep the scaffold dependency-light. Lane 1 can
upgrade them to Pydantic models while preserving the field names.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


VerdictValue = Literal["handle_yourself", "consult_lawyer", "urgent"]
Confidence = Literal["low", "medium", "high"]


@dataclass
class Classification:
    letter_type: str
    jurisdiction: str
    urgency: str
    summary: str
    latency_ms: float = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SpecialistFinding:
    agent_name: str
    summary: str
    key_points: list[str] = field(default_factory=list)
    deadlines: list[str] = field(default_factory=list)
    confidence: Confidence = "medium"
    needs_lawyer: bool = False
    error: str | None = None
    latency_ms: float = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Verdict:
    value: VerdictValue
    summary: str
    next_steps: list[str]
    disclaimer: str = "This is legal information, not legal advice."
    latency_ms: float = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DraftResponse:
    subject: str
    body: str
    tone: str = "calm and documented"
    latency_ms: float = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LawyerRecommendation:
    should_show: bool
    lawyer_type: str
    questions_to_ask: list[str]
    cost_notes: str
    latency_ms: float = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


TriageState = dict[str, Any]


def empty_state(letter_text: str) -> TriageState:
    return {
        "letter_text": letter_text,
        "classification": None,
        "specialist_findings": [],
        "verdict": None,
        "draft_response": None,
        "lawyer_recommendation": None,
        "latencies": {},
        "errors": [],
    }

