"""Stretch: Tavily search tool. Fail-soft — never crashes the graph."""

import os

from dotenv import load_dotenv

# Load .env here too so the tool works regardless of import order (e.g. when imported
# without src.config having run first).
load_dotenv()


def search(query: str, max_results: int = 3) -> dict:
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        results = client.search(query, max_results=max_results)
        return {"results": results.get("results", []), "error": None}
    except Exception as e:
        return {"results": [], "error": str(e), "note": "Search unavailable; proceeding with general triage."}
