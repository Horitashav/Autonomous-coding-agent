"""Agent State — The central data schema passed between LangGraph nodes."""

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """The central state dictionary passed between graph nodes."""

    # Initial user request
    prompt: str

    # Planner metadata
    task_summary: str
    is_feasible: bool
    needs_approval: bool
    approval_reason: str
    estimated_complexity: str

    # Human-in-the-Loop approval
    human_approved: bool

    # Code generation and safety
    code: str
    code_is_safe: bool
    safety_violations: list[str]

    # Execution results from Docker sandbox
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool

    # Routing and lifecycle control
    attempts: int
    max_attempts: int
    status: str  # "running", "success", "failed", "blocked", "needs_repair", "rejected"

    # Final outputs
    final_output: str
    error_summary: str

    # Observability & cost metrics
    total_tokens: int
    total_cost: float
    step_history: list[dict[str, Any]]