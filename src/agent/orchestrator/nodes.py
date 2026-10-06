"""Graph Nodes — The individual processing steps in the agent pipeline."""

import logging

from agent.brain.code_generator import CodeGenerator
from agent.brain.planner import Planner
from agent.config import MAX_REPAIR_ATTEMPTS
from agent.guardrails.ast_checker import check_code_safety
from agent.guardrails.input_guard import check_input_safety
from agent.orchestrator.state import AgentState
from agent.sandbox.executor import SandboxExecutor

logger = logging.getLogger(__name__)

# Lazy singletons (created on first call to optimize startup time)
_code_generator: CodeGenerator | None = None
_planner: Planner | None = None
_sandbox: SandboxExecutor | None = None


def _get_code_generator() -> CodeGenerator:
    global _code_generator
    if _code_generator is None:
        _code_generator = CodeGenerator()
    return _code_generator


def _get_planner() -> Planner:
    global _planner
    if _planner is None:
        _planner = Planner()
    return _planner


def _get_sandbox() -> SandboxExecutor:
    global _sandbox
    if _sandbox is None:
        _sandbox = SandboxExecutor()
    return _sandbox


def check_input_node(state: AgentState) -> dict:
    """Verify input prompt is safe from injection attacks."""
    prompt = state.get("prompt", "")
    guard_result = check_input_safety(prompt)

    if not guard_result.is_safe:
        return {
            "status": "blocked",
            "error_summary": (
                f"Input rejected by security guardrail. "
                f"Rules triggered: {', '.join(guard_result.triggered_rules)}."
            ),
        }

    return {
        "status": "running",
        "attempts": 0,
        "max_attempts": MAX_REPAIR_ATTEMPTS,
        "total_tokens": 0,
        "total_cost": 0.0,
    }


def plan_task_node(state: AgentState) -> dict:
    """Analyze feasibility and requirements before generating code."""
    prompt = state.get("prompt", "")
    planner = _get_planner()
    plan = planner.analyze(prompt)

    update = {
        "task_summary": plan.task_summary,
        "is_feasible": plan.is_feasible,
        "needs_approval": plan.needs_approval,
        "estimated_complexity": plan.estimated_complexity,
    }

    if not plan.is_feasible:
        update["status"] = "blocked"
        update["error_summary"] = (
            "Task is not feasible in the sandbox (requires external network access)."
        )

    return update


def generate_code_node(state: AgentState) -> dict:
    """Generate Python script using the LLM."""
    prompt = state.get("prompt", "")
    generator = _get_code_generator()
    result = generator.generate(prompt)

    prev_tokens = state.get("total_tokens", 0)
    prev_cost = state.get("total_cost", 0.0)

    return {
        "code": result.code,
        "total_tokens": prev_tokens + result.llm_response.total_tokens,
        "total_cost": prev_cost + result.llm_response.estimated_cost_usd,
    }


def check_code_safety_node(state: AgentState) -> dict:
    """Scan generated Python code for security violations via AST."""
    code = state.get("code", "")
    result = check_code_safety(code)

    return {
        "code_is_safe": result.is_safe,
        "safety_violations": result.violations,
    }


def execute_code_node(state: AgentState) -> dict:
    """Execute code inside the isolated Docker sandbox."""
    code = state.get("code", "")
    sandbox = _get_sandbox()
    result = sandbox.run(code)

    update = {
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "timed_out": result.timed_out,
    }

    if result.succeeded:
        update["status"] = "success"
    else:
        attempts = state.get("attempts", 0) + 1
        max_attempts = state.get("max_attempts", MAX_REPAIR_ATTEMPTS)
        update["attempts"] = attempts

        if attempts >= max_attempts:
            update["status"] = "failed"
        else:
            update["status"] = "needs_repair"

    return update


def repair_code_node(state: AgentState) -> dict:
    """Self-healing: repair code using error traceback and re-attempt."""
    prompt = state.get("prompt", "")
    code = state.get("code", "")
    stderr = state.get("stderr", "")
    attempts = state.get("attempts", 1)
    max_attempts = state.get("max_attempts", MAX_REPAIR_ATTEMPTS)

    error_output = stderr
    if state.get("timed_out"):
        error_output = "TIMEOUT: Code exceeded time limit (infinite loop).\n" + error_output

    violations = state.get("safety_violations", [])
    if violations:
        error_output = (
            "SECURITY VIOLATIONS (must remove forbidden imports/calls):\n"
            + "\n".join(f"- {v}" for v in violations)
            + "\n\n"
            + error_output
        )

    generator = _get_code_generator()
    result = generator.repair(
        task_description=prompt,
        failed_code=code,
        error_output=error_output,
        attempt_number=attempts,
        max_attempts=max_attempts,
    )

    prev_tokens = state.get("total_tokens", 0)
    prev_cost = state.get("total_cost", 0.0)

    return {
        "code": result.code,
        "status": "running",
        "total_tokens": prev_tokens + result.llm_response.total_tokens,
        "total_cost": prev_cost + result.llm_response.estimated_cost_usd,
    }


def format_output_node(state: AgentState) -> dict:
    """Format standard output for successful task completion."""
    stdout = state.get("stdout", "")
    return {
        "final_output": stdout.strip(),
        "status": "success",
    }


def format_failure_node(state: AgentState) -> dict:
    """Create human-readable diagnostic summary when retries fail."""
    attempts = state.get("attempts", 0)
    stderr = state.get("stderr", "")
    error_summary = state.get("error_summary", "")

    if not error_summary:
        error_summary = f"Task failed after {attempts} attempt(s).\n\nLast error:\n{stderr[-500:]}"

    return {
        "error_summary": error_summary,
        "final_output": error_summary,
        "status": state.get("status", "failed"),
    }