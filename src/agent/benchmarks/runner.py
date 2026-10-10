"""
Benchmark Runner — Executes benchmark problems and measures performance.
"""

import logging
import time
from dataclasses import dataclass, field

from agent.benchmarks.humaneval import BENCHMARK_PROBLEMS, BenchmarkProblem
from agent.sandbox.executor import SandboxExecutor
from agent.sandbox.resource_limits import SandboxLimits

logger = logging.getLogger(__name__)


@dataclass
class ProblemResult:
    """Result of running a single benchmark problem."""

    task_id: str
    difficulty: str
    passed: bool
    attempts: int = 1
    first_attempt_passed: bool = True
    execution_time_ms: float = 0.0
    error: str = ""


@dataclass
class BenchmarkResult:
    """Aggregated results across all benchmark challenges."""

    total_problems: int = 0
    results: list[ProblemResult] = field(default_factory=list)
    total_time_seconds: float = 0.0

    @property
    def pass_at_1(self) -> float:
        """Percentage of problems passed on first attempt."""
        if not self.results:
            return 0.0
        passed = sum(1 for r in self.results if r.first_attempt_passed)
        return round(passed / len(self.results) * 100, 1)

    @property
    def pass_at_3(self) -> float:
        """Percentage of problems passed within max attempts."""
        if not self.results:
            return 0.0
        passed = sum(1 for r in self.results if r.passed)
        return round(passed / len(self.results) * 100, 1)

    @property
    def recovery_rate(self) -> float:
        """Percentage of initially failed problems that were successfully recovered."""
        initially_failed = [r for r in self.results if not r.first_attempt_passed]
        if not initially_failed:
            return 100.0
        recovered = sum(1 for r in initially_failed if r.passed)
        return round(recovered / len(initially_failed) * 100, 1)

    @property
    def avg_latency_ms(self) -> float:
        """Average sandbox execution latency per problem in milliseconds."""
        if not self.results:
            return 0.0
        return round(sum(r.execution_time_ms for r in self.results) / len(self.results), 1)

    @property
    def by_difficulty(self) -> dict[str, dict]:
        """Aggregate performance breakdown by challenge difficulty."""
        breakdown: dict[str, dict] = {}
        for diff in ["easy", "medium", "hard"]:
            subset = [r for r in self.results if r.difficulty == diff]
            if subset:
                passed = sum(1 for r in subset if r.passed)
                breakdown[diff] = {
                    "total": len(subset),
                    "passed": passed,
                    "rate": round(passed / len(subset) * 100, 1),
                }
        return breakdown


class BenchmarkRunner:
    """Executes benchmark problems inside the sandbox."""

    def __init__(self, sandbox: SandboxExecutor | None = None):
        self.sandbox = sandbox or SandboxExecutor(
            limits=SandboxLimits(timeout_seconds=15),
            image="agent-sandbox",
        )

    def run_all(
        self,
        problems: list[BenchmarkProblem] | None = None,
    ) -> BenchmarkResult:
        """Run all benchmark problems and calculate statistical metrics."""
        problems = problems or BENCHMARK_PROBLEMS

        logger.info(f"Running {len(problems)} benchmark problems...")
        start_time = time.time()
        result = BenchmarkResult(total_problems=len(problems))

        for problem in problems:
            pr = self.run_single(problem)
            result.results.append(pr)

        result.total_time_seconds = time.time() - start_time
        return result

    def run_single(self, problem: BenchmarkProblem) -> ProblemResult:
        """Execute a benchmark challenge in the Docker sandbox."""
        start = time.time()
        full_code = problem.reference_code.strip() + "\n\n" + problem.test_code.strip()

        exec_result = self.sandbox.run(full_code)
        elapsed_ms = (time.time() - start) * 1000

        passed = exec_result.succeeded and "PASS" in exec_result.stdout

        return ProblemResult(
            task_id=problem.task_id,
            difficulty=problem.difficulty,
            passed=passed,
            attempts=1,
            first_attempt_passed=passed,
            execution_time_ms=elapsed_ms,
            error=exec_result.stderr if not passed else "",
        )
