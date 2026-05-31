import time
import weave
from src.config import client, MODEL
from src.schemas import AgentState, SpecialistFinding


@weave.op()
def rights_review(state: AgentState) -> AgentState:
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a consumer and tenant rights specialist. Identify rights the recipient may have. "
                        "Respond ONLY with valid JSON: "
                        '{"agent_name":"rights","summary":str,"key_points":[str],"deadlines":[str],"confidence":"low"|"medium"|"high","needs_lawyer":bool}. '
                        "This is not legal advice."
                    ),
                },
                {"role": "user", "content": f"What rights does the recipient have in this letter?\n\n{state['letter_text']}"},
            ],
            response_format={"type": "json_object"},
        )
        data = SpecialistFinding.model_validate_json(response.choices[0].message.content)
        state["specialist_findings"].append(data.model_dump())
    except Exception as e:
        state["errors"].append(f"rights: {e}")
        state["specialist_findings"].append(
            SpecialistFinding(agent_name="rights", summary="Rights review failed.", key_points=[], error=str(e)).model_dump()
        )
    state["latencies"]["rights"] = round(time.time() - start, 2)
    return state
