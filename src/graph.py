from langgraph.graph import StateGraph, END
from src.schemas import AgentState
from src.agents.orchestrator import orchestrator_classify
from src.agents.risk import risk_assess
from src.agents.rights import rights_review
from src.agents.obligations import obligations_extract
from src.agents.synthesis import synthesize_verdict
from src.agents.response_drafter import draft_response
from src.agents.lawyer_finder import find_lawyer


def should_find_lawyer(state: AgentState) -> str:
    verdict = state.get("verdict", {}).get("verdict", "consult_lawyer")
    return "find_lawyer" if verdict in ("consult_lawyer", "urgent") else END


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("orchestrator", orchestrator_classify)
    graph.add_node("risk", risk_assess)
    graph.add_node("rights", rights_review)
    graph.add_node("obligations", obligations_extract)
    graph.add_node("synthesis", synthesize_verdict)
    graph.add_node("response_drafter", draft_response)
    graph.add_node("find_lawyer", find_lawyer)

    graph.set_entry_point("orchestrator")
    graph.add_edge("orchestrator", "risk")
    graph.add_edge("risk", "rights")
    graph.add_edge("rights", "obligations")
    graph.add_edge("obligations", "synthesis")
    graph.add_edge("synthesis", "response_drafter")
    graph.add_conditional_edges("response_drafter", should_find_lawyer)
    graph.add_edge("find_lawyer", END)

    return graph.compile()


app = build_graph()


def run(letter_text: str) -> AgentState:
    initial_state: AgentState = {
        "letter_text": letter_text,
        "classification": None,
        "urgency_signal": "medium",
        "specialist_findings": [],
        "verdict": None,
        "draft_response": None,
        "lawyer_recommendation": None,
        "latencies": {},
        "errors": [],
    }
    return app.invoke(initial_state)
