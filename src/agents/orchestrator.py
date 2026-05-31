import time
import weave
from src.config import client, MODEL
from src.schemas import AgentState, Classification


@weave.op()
def orchestrator_classify(state: AgentState) -> AgentState:
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a legal document classifier. "
                        "Respond ONLY with valid JSON matching this schema: "
                        '{"letter_type": str, "jurisdiction": str, "urgency": "low"|"medium"|"high", "summary": str}. '
                        "Do not include legal advice."
                    ),
                },
                {"role": "user", "content": f"Classify this legal letter:\n\n{state['letter_text']}"},
            ],
            response_format={"type": "json_object"},
        )
        data = Classification.model_validate_json(response.choices[0].message.content)
        state["classification"] = data.model_dump()
    except Exception as e:
        state["errors"].append(f"orchestrator: {e}")
        state["classification"] = {
            "letter_type": "unknown",
            "jurisdiction": "unknown",
            "urgency": "medium",
            "summary": "Classification failed.",
        }
    state["latencies"]["orchestrator"] = round(time.time() - start, 2)
    return state
