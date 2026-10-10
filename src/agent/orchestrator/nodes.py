"""Graph Nodes — The individual processing steps in the agent pipeline."""

import ast
import logging
from agent.brain.code_generator import (
    CodeGenerationResult,
    CodeGenerator,
    extract_code,
)
from agent.brain.planner import Planner
from agent.brain.prompts import (
    CODE_GENERATOR_SYSTEM_PROMPT,
    CONTEXT_AWARE_USER_TEMPLATE,
)
from agent.config import MAX_REPAIR_ATTEMPTS
from agent.context.context_builder import ContextBuilder
from agent.guardrails.ast_checker import check_code_safety
from agent.guardrails.input_guard import check_input_safety
from agent.guardrails.output_guard import redact_pii
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

    reasons = []
    if plan.is_destructive:
        reasons.append("Task involves data deletion or overwriting")
    if plan.requires_file_io:
        reasons.append("Task involves reading or writing disk files")
    if plan.estimated_complexity == "complex":
        reasons.append("Task has high computational complexity")

    approval_reason = "; ".join(reasons) if reasons else "Routine execution"

    update = {
        "task_summary": plan.task_summary,
        "is_feasible": plan.is_feasible,
        "needs_approval": plan.needs_approval or len(reasons) > 0,
        "approval_reason": approval_reason,
        "estimated_complexity": plan.estimated_complexity,
    }

    if not plan.is_feasible:
        update["status"] = "blocked"
        update["error_summary"] = (
            "Task is not feasible in the sandbox (requires external network access)."
        )

    return update


def generate_code_node(state: AgentState) -> dict:
    """Generate code, optionally with project file context."""
    prompt = state.get("prompt", "")
    project_path = state.get("project_path", "")
    generator = _get_code_generator()

    context_text = ""
    if project_path:
        try:
            builder = ContextBuilder(project_path)
            ctx_result = builder.build(user_prompt=prompt, token_budget=20_000)
            context_text = ctx_result.context_text
            logger.info(f"Injected context: {len(ctx_result.included_files)} files")
        except Exception as e:
            logger.warning(f"Context building failed: {e}")

    if context_text:
        user_prompt = CONTEXT_AWARE_USER_TEMPLATE.format(
            task_description=prompt,
            project_context=context_text,
        )
        response = generator.llm_client.generate(
            system_prompt=CODE_GENERATOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        code = extract_code(response.content)
        gen_result = CodeGenerationResult(code=code, llm_response=response)
    else:
        gen_result = generator.generate(prompt)

    prev_tokens = state.get("total_tokens", 0)
    prev_cost = state.get("total_cost", 0.0)

    return {
        "code": gen_result.code,
        "total_tokens": prev_tokens + gen_result.llm_response.total_tokens,
        "total_cost": prev_cost + gen_result.llm_response.estimated_cost_usd,
    }


def check_code_safety_node(state: AgentState) -> dict:
    """Scan generated Python code for security violations via AST."""
    code = state.get("code", "")
    result = check_code_safety(code)

    return {
        "code_is_safe": result.is_safe,
        "safety_violations": result.violations,
    }


def human_approval_node(state: AgentState) -> dict:
    """Check human authorization gate without blocking ASGI server execution."""
    needs_approval = state.get("needs_approval", False)
    human_approved = state.get("human_approved", None)

    # 1. If no approval is needed, auto-approve and proceed
    if not needs_approval:
        return {"human_approved": True}

    # 2. If already authorized via API / approval route, proceed
    if human_approved is True:
        return {"human_approved": True, "status": "running"}

    # 3. If explicit rejection received
    if human_approved is False:
        return {
            "human_approved": False,
            "status": "rejected",
            "error_summary": "Task was rejected by human operator during security review.",
        }

    # 4. First pass: Suspend execution cleanly for async/UI approval
    reason = state.get("approval_reason", "High-risk operation requested")
    logger.info(f"Awaiting human approval for task: {reason}")
    return {
        "status": "awaiting_approval",
        "human_approved": False,
        "error_summary": f"Execution paused: Human approval required ({reason}).",
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
    """Format standard output for successful completion and sanitize PII."""
    stdout = state.get("stdout", "").strip()

    # Redact sensitive PII before persistence and client delivery
    try:
        redaction = redact_pii(stdout)
        final_output = redaction.redacted_text
        if redaction.had_pii:
            logger.warning(
                f"Redacted {redaction.redaction_count} PII occurrences ({redaction.redacted_types})"
            )
    except Exception as e:
        logger.warning(f"PII redaction skipped due to error: {e}")
        final_output = stdout

    return {
        "final_output": final_output,
        "status": "success",
    }


def format_failure_node(state: AgentState) -> dict:
    """Create human-readable diagnostic summary when retries fail."""
    attempts = state.get("attempts", 0)
    stderr = state.get("stderr", "")
    error_summary = state.get("error_summary", "")

    if not error_summary:
        if state.get("timed_out"):
            error_summary = (
                f"Task timed out after {attempts} attempt(s). Last error:\n{stderr[-500:]}"
            )
        else:
            error_summary = f"Task failed after {attempts} attempt(s). Last error:\n{stderr[-500:]}"

    return {
        "error_summary": error_summary,
        "final_output": error_summary,
        "status": state.get("status", "failed"),
    }


OPTIMIZER_SYSTEM_PROMPT = """You are a Principal Python Architect specializing in idiomatic refactoring and cyclomatic simplification.
Your goal is to take verified, working Python code and refactor it into clean, idiomatic Python using Python's standard library.

STRICT REQUIREMENTS:
1. Leverage standard library utilities:
   - `collections` (Counter, defaultdict, deque)
   - `itertools` (chain, combinations, pairwise, groupby, islice)
   - `functools` (reduce, lru_cache)
   - `heapq`, `math`, `re`, `pathlib`
   - Built-in comprehensions
2. Replace manual 10-25 line imperative loops and accumulators with concise 2-5 line standard library calls.
3. Preserve the exact signature, behavior, and output semantics.
4. DO NOT add verbose test data, sample runner boilerplate, or if __name__ == '__main__' blocks unless they were in the original code. Focus purely on condensing the logic.
5. Output ONLY executable Python code within ```python ``` markdown fences.
"""


def _count_ast_nodes(code_str: str) -> int:
    try:
        tree = ast.parse(code_str)
        return sum(1 for _ in ast.walk(tree))
    except Exception:
        return 0


def optimize_code_node(state: AgentState) -> dict:
    """Refactor verified code using standard library idioms and measure AST reduction."""
    code = state.get("code", "")
    if not code:
        return {}

    generator = _get_code_generator()

    user_prompt = (
        f"Task Description: {state.get('prompt', '')}\n\n"
        f"Working Baseline Code:\n```python\n{code}\n```\n\n"
        "Refactor this into concise, idiomatic Python using standard library modules."
    )

    try:
        response = generator.llm_client.generate(
            system_prompt=OPTIMIZER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        opt_code = extract_code(response.content)
    except Exception as e:
        logger.warning(f"Optimization node fallback: {e}")
        opt_code = code
        response = None

    # Calculate LOC reduction
    orig_lines = [
        line.strip()
        for line in code.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    opt_lines = [
        line.strip()
        for line in opt_code.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    orig_loc = len(orig_lines)
    opt_loc = len(opt_lines)

    # Calculate AST reduction
    orig_ast_count = _count_ast_nodes(code)
    opt_ast_count = _count_ast_nodes(opt_code)

    loc_reduction = (
        round(((orig_loc - opt_loc) / max(orig_loc, 1)) * 100, 1) if orig_loc > opt_loc else 0.0
    )
    ast_reduction = (
        round(((orig_ast_count - opt_ast_count) / max(orig_ast_count, 1)) * 100, 1)
        if orig_ast_count > opt_ast_count
        else 0.0
    )

    metrics = {
        "original_loc": orig_loc,
        "optimized_loc": opt_loc,
        "loc_reduction_pct": max(loc_reduction, 0.0),
        "original_ast_nodes": orig_ast_count,
        "optimized_ast_nodes": opt_ast_count,
        "ast_reduction_pct": max(ast_reduction, 0.0),
    }

    prev_tokens = state.get("total_tokens", 0)
    prev_cost = state.get("total_cost", 0.0)
    added_tokens = response.total_tokens if response else 0
    added_cost = response.estimated_cost_usd if response else 0.0

    return {
        "optimized_code": opt_code,
        "optimization_metrics": metrics,
        "total_tokens": prev_tokens + added_tokens,
        "total_cost": prev_cost + added_cost,
    }
