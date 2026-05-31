"""Fail-soft search wrapper.

This is stretch-only. The app must work even when Tavily is missing or offline.
"""

from __future__ import annotations

import os
from typing import Any


def search_web(query: str, max_results: int = 5) -> dict[str, Any]:
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return {"results": [], "note": "Search unavailable: TAVILY_API_KEY is not set."}

    try:
        from tavily import TavilyClient  # type: ignore

        client = TavilyClient(api_key=api_key)
        return client.search(query=query, max_results=max_results)
    except Exception as exc:
        return {"results": [], "note": f"Search unavailable: {exc}"}

