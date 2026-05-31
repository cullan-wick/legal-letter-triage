import time
import weave
from src.config import client, MODEL
from src.schemas import AgentState, SpecialistFinding


@weave.op()
def risk_assess(state: AgentState) -> AgentState:
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a risk analysis specialist. Assess the worst realistic outcome for the recipient. "
                        "Respond ONLY with valid JSON: "
                        '{"agent_name":"risk","summary":str,"key_points":[str],"deadlines":[str],"confidence":"low"|"medium"|"high","needs_lawyer":bool}. '
                        "This is not legal advice."
                    ),
                },
                {"role": "user", "content": f"Assess the risk in this legal letter:\n\n{state['letter_text']}"},
            ],
            response_format={"type": "json_object"},
        )
        data = SpecialistFinding.model_validate_json(response.choices[0].message.content)
        state["specialist_findings"].append(data.model_dump())
    except Exception as e:
        state["errors"].append(f"risk: {e}")
        state["specialist_findings"].append(
            SpecialistFinding(agent_name="risk", summary="Risk assessment failed.", key_points=[], error=str(e)).model_dump()
        )
    state["latencies"]["risk"] = round(time.time() - start, 2)
    return state
