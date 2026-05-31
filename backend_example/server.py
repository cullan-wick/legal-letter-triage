"""Minimal FastAPI wrapper around run_triage() for the LetterLens web UI.

Run with:
    uvicorn backend_example.server:app --reload

Then set apiUrl in triage-api.jsx:
    window.LetterLensConfig = { apiUrl: "http://localhost:8000/api/triage" };
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.graph import run_triage

app = FastAPI(title="LetterLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TriageRequest(BaseModel):
    letter_text: str


@app.post("/api/triage")
def triage(req: TriageRequest):
    return run_triage(req.letter_text)
