"""Stretch: Tavily search tool. Fail-soft — never crashes the graph."""


def search(query: str) -> dict:
    try:
        from tavily import TavilyClient
        import os
        client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        results = client.search(query, max_results=3)
        return {"results": results.get("results", []), "error": None}
    except Exception as e:
        return {"results": [], "error": str(e), "note": "Search unavailable; proceeding with general triage."}
