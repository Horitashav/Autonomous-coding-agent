"""Agent Graph — State machine assembling nodes and conditional routing."""

from langgraph.graph import END, StateGraph

from agent.orchestrator.nodes import (
    check_code_safety_node,
    check_input_node,
    execute_code_node,
    format_failure_node,
    format_output_node,
    generate_code_node,
    plan_task_node,
    repair_code_node,
)
from agent.orchestrator.state import AgentState


def route_after_input_check(state: AgentState) -> str:
    """Branch after input check."""
    if state.get("status") == "blocked":
        return "format_failure"
    return "plan_task"


def route_after_planning(state: AgentState) -> str:
    """Branch after task planning."""
    if state.get("status") == "blocked":
        return "format_failure"
    return "generate_code"


def route_after_safety_check(state: AgentState) -> str:
    """Branch after AST security analysis."""
    if state.get("code_is_safe"):
        return "execute_code"

    attempts = state.get("attempts", 0)
    max_attempts = state.get("max_attempts", 3)
    if attempts < max_attempts:
        return "repair_code"
    return "format_failure"


def route_after_execution(state: AgentState) -> str:
    """Branch after sandbox execution (Self-Healing decision)."""
    status = state.get("status", "")
    if status == "success":
        return "format_output"
    if status == "needs_repair":
        return "repair_code"
    return "format_failure"


def build_agent_graph() -> StateGraph:
    """Construct and compile the agent state machine."""
    workflow = StateGraph(AgentState)

    # Add all node steps
    workflow.add_node("check_input", check_input_node)
    workflow.add_node("plan_task", plan_task_node)
    workflow.add_node("generate_code", generate_code_node)
    workflow.add_node("check_code_safety", check_code_safety_node)
    workflow.add_node("execute_code", execute_code_node)
    workflow.add_node("repair_code", repair_code_node)
    workflow.add_node("format_output", format_output_node)
    workflow.add_node("format_failure", format_failure_node)

    # Set start node
    workflow.set_entry_point("check_input")

    # Connect conditional routing edges
    workflow.add_conditional_edges(
        "check_input",
        route_after_input_check,
        {
            "plan_task": "plan_task",
            "format_failure": "format_failure",
        },
    )

    workflow.add_conditional_edges(
        "plan_task",
        route_after_planning,
        {
            "generate_code": "generate_code",
            "format_failure": "format_failure",
        },
    )

    workflow.add_edge("generate_code", "check_code_safety")

    workflow.add_conditional_edges(
        "check_code_safety",
        route_after_safety_check,
        {
            "execute_code": "execute_code",
            "repair_code": "repair_code",
            "format_failure": "format_failure",
        },
    )

    workflow.add_conditional_edges(
        "execute_code",
        route_after_execution,
        {
            "format_output": "format_output",
            "repair_code": "repair_code",
            "format_failure": "format_failure",
        },
    )

    # The repair loop routes back to security validation
    workflow.add_edge("repair_code", "check_code_safety")

    # Final nodes terminate the graph
    workflow.add_edge("format_output", END)
    workflow.add_edge("format_failure", END)

    return workflow.compile()


agent_graph = build_agent_graph()