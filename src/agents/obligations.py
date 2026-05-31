import time
import weave
from src.config import client, MODEL
from src.schemas import AgentState, SpecialistFinding


@weave.op()
def obligations_extract(state: AgentState) -> AgentState:
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a legal obligations specialist. Extract all required actions and deadlines. "
                        "Respond ONLY with valid JSON: "
                        '{"agent_name":"obligations","summary":str,"key_points":[str],"deadlines":[str],"confidence":"low"|"medium"|"high","needs_lawyer":bool}. '
                        "This is not legal advice."
                    ),
                },
                {"role": "user", "content": f"What obligations and deadlines does the recipient face?\n\n{state['letter_text']}"},
            ],
            response_format={"type": "json_object"},
        )
        data = SpecialistFinding.model_validate_json(response.choices[0].message.content)
        state["specialist_findings"].append(data.model_dump())
    except Exception as e:
        state["errors"].append(f"obligations: {e}")
        state["specialist_findings"].append(
            SpecialistFinding(agent_name="obligations", summary="Obligations extraction failed.", key_points=[], error=str(e)).model_dump()
        )
    state["latencies"]["obligations"] = round(time.time() - start, 2)
    return state
