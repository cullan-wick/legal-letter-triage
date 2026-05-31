"""Minimal FastAPI wrapper around the LetterLens web pipeline.

Run with:
    uvicorn backend_example.server:app --reload

Then set apiUrl in triage-api.jsx:
    window.LetterLensConfig = { apiUrl: "http://localhost:8000/api/triage" };
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.agents.response_drafter import draft_response
from src.graph import initial_state, run_fast

app = FastAPI(title="LetterLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TriageRequest(BaseModel):
    letter_text: str


class DraftRequest(BaseModel):
    letter_text: str
    verdict: dict


@app.post("/api/triage")
def triage(req: TriageRequest):
    return run_fast(req.letter_text)


@app.post("/api/draft")
def draft(req: DraftRequest):
    state = initial_state(req.letter_text)
    state["verdict"] = req.verdict
    return draft_response(state)
