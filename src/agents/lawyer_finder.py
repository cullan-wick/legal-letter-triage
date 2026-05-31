import time
import weave
from src.config import client, MODEL
from src.schemas import AgentState, LawyerRecommendation


@weave.op()
def find_lawyer(state: AgentState) -> AgentState:
    """Runs only when verdict is consult_lawyer or urgent."""
    start = time.time()
    classification = state.get("classification", {})
    verdict = state.get("verdict", {})
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a legal referral specialist. Recommend what type of lawyer to seek. "
                        "Respond ONLY with valid JSON: "
                        '{"lawyer_type":str,"reason":str,"questions_to_ask":[str],"estimated_cost_range":str}. '
                        "This is not legal advice."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Letter type: {classification.get('letter_type')}\n"
                        f"Jurisdiction: {classification.get('jurisdiction')}\n"
                        f"Verdict: {verdict.get('verdict')} — {verdict.get('reason')}\n\n"
                        "What kind of lawyer should the recipient consult?"
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        data = LawyerRecommendation.model_validate_json(response.choices[0].message.content)
        state["lawyer_recommendation"] = data.model_dump()
    except Exception as e:
        state["errors"].append(f"lawyer_finder: {e}")
        state["lawyer_recommendation"] = {
            "lawyer_type": "General practice attorney",
            "reason": "Could not determine specific type; consult a general attorney first.",
            "questions_to_ask": ["What are my options?", "What are the deadlines?"],
            "estimated_cost_range": "Varies by location and complexity.",
        }
    state["latencies"]["lawyer_finder"] = round(time.time() - start, 2)
    return state
