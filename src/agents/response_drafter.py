import time
import weave
from src.config import client, MODEL
from src.schemas import AgentState, DraftResponse


@weave.op()
def draft_response(state: AgentState) -> AgentState:
    start = time.time()
    verdict = state.get("verdict", {})
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional letter drafter. Write a calibrated response to the legal letter. "
                        "Respond ONLY with valid JSON: "
                        '{"subject":str,"body":str,"tone":str}. '
                        "The tone should match the urgency. Do not admit liability. This is not legal advice."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Original letter:\n{state['letter_text']}\n\n"
                        f"Verdict: {verdict.get('verdict')} — {verdict.get('reason')}\n\n"
                        "Draft an appropriate response."
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        data = DraftResponse.model_validate_json(response.choices[0].message.content)
        state["draft_response"] = data.model_dump()
    except Exception as e:
        state["errors"].append(f"response_drafter: {e}")
        state["draft_response"] = {
            "subject": "Re: Your Letter",
            "body": "We acknowledge receipt of your letter and are reviewing our options.",
            "tone": "neutral",
        }
    state["latencies"]["response_drafter"] = round(time.time() - start, 2)
    return state
