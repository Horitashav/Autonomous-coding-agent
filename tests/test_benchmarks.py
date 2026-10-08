"""
Tests for the benchmark runner and reporter.
"""

import ast
import pytest

from agent.benchmarks.humaneval import BENCHMARK_PROBLEMS, BenchmarkProblem
from agent.benchmarks.reporter import BenchmarkReporter
from agent.benchmarks.runner import BenchmarkResult, ProblemResult


class TestBenchmarkProblems:
    def test_problems_have_required_fields(self):
        for p in BENCHMARK_PROBLEMS:
            assert p.task_id, "Problem missing task_id"
            assert p.prompt, f"{p.task_id} missing prompt"
            assert p.reference_code, f"{p.task_id} missing reference_code"
            assert p.test_code, f"{p.task_id} missing test_code"
            assert p.difficulty in ("easy", "medium", "hard")

    def test_have_20_problems(self):
        assert len(BENCHMARK_PROBLEMS) == 20

    def test_reference_code_is_valid_python(self):
        """All reference solutions must parse without syntax errors."""
        for p in BENCHMARK_PROBLEMS:
            full = p.reference_code + "\n" + p.test_code
            try:
                ast.parse(full)
            except SyntaxError as e:
                pytest.fail(f"{p.task_id} has syntax error: {e}")


class TestBenchmarkResult:
    def test_pass_at_1_calculation(self):
        result = BenchmarkResult(
            total_problems=4,
            results=[
                ProblemResult(task_id="1", difficulty="easy", passed=True, first_attempt_passed=True),
                ProblemResult(task_id="2", difficulty="easy", passed=True, first_attempt_passed=True),
                ProblemResult(task_id="3", difficulty="easy", passed=True, first_attempt_passed=False),
                ProblemResult(task_id="4", difficulty="easy", passed=False, first_attempt_passed=False),
            ],
        )
        assert result.pass_at_1 == 50.0
        assert result.pass_at_3 == 75.0

    def test_recovery_rate(self):
        result = BenchmarkResult(
            total_problems=3,
            results=[
                ProblemResult(task_id="1", difficulty="easy", passed=True, first_attempt_passed=True),
                ProblemResult(task_id="2", difficulty="easy", passed=True, first_attempt_passed=False),
                ProblemResult(task_id="3", difficulty="easy", passed=False, first_attempt_passed=False),
            ],
        )
        assert result.recovery_rate == 50.0


class TestBenchmarkReporter:
    def test_markdown_report(self):
        result = BenchmarkResult(
            total_problems=2,
            results=[
                ProblemResult(
                    task_id="BENCH/001",
                    difficulty="easy",
                    passed=True,
                    first_attempt_passed=True,
                    execution_time_ms=100,
                ),
                ProblemResult(
                    task_id="BENCH/002",
                    difficulty="medium",
                    passed=False,
                    first_attempt_passed=False,
                    execution_time_ms=200,
                ),
            ],
            total_time_seconds=0.3,
        )

        report = BenchmarkReporter.to_markdown(result)
        assert "pass@1" in report
        assert "BENCH/001" in report
        assert "✅" in report