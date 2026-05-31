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
    verdict = (state.get("verdict") or {}).get("verdict", "consult_lawyer")
    return "find_lawyer" if verdict in ("consult_lawyer", "urgent") else END


def collect_findings(state: AgentState) -> dict:
    """Fan-in node: fold the three parallel specialists' staging slots
    (risk_finding / rights_finding / obligations_finding) into the shared
    specialist_findings list plus per-agent latencies.

    This node is the SOLE writer of specialist_findings, so there is no concurrent-write
    conflict and no LangGraph reducer is required. Downstream nodes (synthesis, drafter,
    lawyer_finder) see specialist_findings/latencies exactly as before — unchanged.
    """
    findings: list[dict] = []
    latencies = dict(state.get("latencies") or {})
    errors = list(state.get("errors") or [])
    for name in ("risk", "rights", "obligations"):
        finding = state.get(f"{name}_finding")
        if not finding:
            continue
        finding = dict(finding)
        latency = finding.pop("latency_ms", None)
        if latency is not None:
            latencies[name] = latency
        if finding.get("error"):
            errors.append(f"{name}: {finding['error']}")
        findings.append(finding)
    return {"specialist_findings": findings, "latencies": latencies, "errors": errors}


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("orchestrator", orchestrator_classify)
    graph.add_node("risk", risk_assess)
    graph.add_node("rights", rights_review)
    graph.add_node("obligations", obligations_extract)
    graph.add_node("collect", collect_findings)
    graph.add_node("synthesis", synthesize_verdict)
    graph.add_node("response_drafter", draft_response)
    graph.add_node("find_lawyer", find_lawyer)

    graph.set_entry_point("orchestrator")

    # fan-out: orchestrator -> the three independent specialists (run concurrently)
    graph.add_edge("orchestrator", "risk")
    graph.add_edge("orchestrator", "rights")
    graph.add_edge("orchestrator", "obligations")

    # fan-in: all three specialists must finish before collect runs
    graph.add_edge("risk", "collect")
    graph.add_edge("rights", "collect")
    graph.add_edge("obligations", "collect")
    graph.add_edge("collect", "synthesis")

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
        "risk_finding": None,
        "rights_finding": None,
        "obligations_finding": None,
        "specialist_findings": [],
        "verdict": None,
        "draft_response": None,
        "lawyer_recommendation": None,
        "latencies": {},
        "errors": [],
    }
    return app.invoke(initial_state)
