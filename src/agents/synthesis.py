import time
import weave
from src.config import client, MODEL
from src.schemas import AgentState, SynthesisOutput


@weave.op()
def synthesize_verdict(state: AgentState) -> AgentState:
    start = time.time()
    findings_text = "\n\n".join(
        f"[{f['agent_name'].upper()}] {f['summary']}\nKey points: {f['key_points']}\nDeadlines: {f['deadlines']}"
        for f in state["specialist_findings"]
    )
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a legal triage synthesizer. Based on specialist findings, produce a verdict. "
                        "Respond ONLY with valid JSON: "
                        '{"verdict":"handle_yourself"|"consult_lawyer"|"urgent","reason":str,"next_steps":[str],"urgent_deadlines":[str]}. '
                        "This is not legal advice. Default to consult_lawyer if uncertain."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Original letter:\n{state['letter_text']}\n\n"
                        f"Urgency signal from classifier: {state.get('urgency_signal', 'medium')} "
                        f"(use as a tiebreaker — 'high' leans urgent, 'low' leans handle_yourself)\n\n"
                        f"Specialist findings:\n{findings_text}\n\n"
                        "Produce a triage verdict."
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        data = SynthesisOutput.model_validate_json(response.choices[0].message.content)
        state["verdict"] = data.model_dump()
    except Exception as e:
        state["errors"].append(f"synthesis: {e}")
        state["verdict"] = {
            "verdict": "consult_lawyer",
            "reason": "One or more checks were incomplete, so this should be reviewed before acting.",
            "next_steps": ["Consult a lawyer before responding."],
            "urgent_deadlines": [],
        }
    state["latencies"]["synthesis"] = round(time.time() - start, 2)
    return state
