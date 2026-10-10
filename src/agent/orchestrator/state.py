"""Agent State — The central data schema passed between LangGraph nodes."""

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """The central state dictionary passed between graph nodes."""

    # Initial user request
    prompt: str

    # Project context
    project_path: str  # Path to project root directory for multi-file ingestion

    # Planner metadata
    task_summary: str
    is_feasible: bool
    needs_approval: bool
    approval_reason: str
    estimated_complexity: str

    # Human-in-the-Loop approval (None = pending review, True = approved, False = rejected)
    human_approved: bool | None

    # Code generation and safety
    code: str
    code_is_safe: bool
    safety_violations: list[str]

    # Idiomatic Optimization & Simplification
    optimized_code: str
    optimization_metrics: dict[str, Any]

    # Execution results from Docker sandbox
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool

    # Routing and lifecycle control
    attempts: int
    max_attempts: int
    status: str  # "running", "success", "failed", "blocked", "needs_repair", "rejected", "awaiting_approval"

    # Final outputs
    final_output: str
    error_summary: str

    # Observability & circuit breaker metrics
    total_tokens: int
    total_cost: float
    step_history: list[dict[str, Any]]
