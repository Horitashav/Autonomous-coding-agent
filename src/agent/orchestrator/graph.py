"""Agent Graph — State machine assembling nodes and conditional routing."""

from langgraph.graph import END, StateGraph

from agent.orchestrator.nodes import (
    check_code_safety_node,
    check_input_node,
    execute_code_node,
    format_failure_node,
    format_output_node,
    generate_code_node,
    human_approval_node,
    optimize_code_node,
    plan_task_node,
    repair_code_node,
)
from agent.orchestrator.state import AgentState


def route_after_input_check(state: AgentState) -> str:
    if state.get("status") == "blocked":
        return "format_failure"
    return "plan_task"


def route_after_planning(state: AgentState) -> str:
    if state.get("status") == "blocked":
        return "format_failure"
    return "generate_code"


def route_after_safety_check(state: AgentState) -> str:
    """Route to human approval gate if code is safe, else repair."""
    if state.get("code_is_safe"):
        return "human_approval"

    attempts = state.get("attempts", 0)
    max_attempts = state.get("max_attempts", 3)
    if attempts < max_attempts:
        return "repair_code"
    return "format_failure"


def route_after_approval(state: AgentState) -> str:
    """Route after human approval check.
    
    - True: proceed to execute in the Docker sandbox
    - None or awaiting_approval: suspend execution cleanly (exit graph)
    - False or rejected: route to failure diagnostic
    """
    status = state.get("status", "")
    if state.get("human_approved") is True:
        return "execute_code"
    if status == "awaiting_approval":
        return END
    return "format_failure"


def route_after_execution(state: AgentState) -> str:
    status = state.get("status", "")
    if status == "success":
        return "optimize_code"
    if status == "needs_repair":
        return "repair_code"
    return "format_failure"


def build_agent_graph() -> StateGraph:
    """Construct and compile the agent state machine with asynchronous HITL and code optimization."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("check_input", check_input_node)
    workflow.add_node("plan_task", plan_task_node)
    workflow.add_node("generate_code", generate_code_node)
    workflow.add_node("check_code_safety", check_code_safety_node)
    workflow.add_node("human_approval", human_approval_node)
    workflow.add_node("execute_code", execute_code_node)
    workflow.add_node("optimize_code", optimize_code_node)
    workflow.add_node("repair_code", repair_code_node)
    workflow.add_node("format_output", format_output_node)
    workflow.add_node("format_failure", format_failure_node)

    # Entry point
    workflow.set_entry_point("check_input")

    # Routing
    workflow.add_conditional_edges(
        "check_input",
        route_after_input_check,
        {"plan_task": "plan_task", "format_failure": "format_failure"},
    )

    workflow.add_conditional_edges(
        "plan_task",
        route_after_planning,
        {"generate_code": "generate_code", "format_failure": "format_failure"},
    )

    workflow.add_edge("generate_code", "check_code_safety")

    workflow.add_conditional_edges(
        "check_code_safety",
        route_after_safety_check,
        {
            "human_approval": "human_approval",
            "repair_code": "repair_code",
            "format_failure": "format_failure",
        },
    )

    workflow.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {
            "execute_code": "execute_code",
            "format_failure": "format_failure",
            END: END,
        },
    )

    workflow.add_conditional_edges(
        "execute_code",
        route_after_execution,
        {
            "optimize_code": "optimize_code",
            "repair_code": "repair_code",
            "format_failure": "format_failure",
        },
    )

    workflow.add_edge("optimize_code", "format_output")
    workflow.add_edge("repair_code", "check_code_safety")
    workflow.add_edge("format_output", END)
    workflow.add_edge("format_failure", END)

    return workflow.compile()


agent_graph = build_agent_graph()