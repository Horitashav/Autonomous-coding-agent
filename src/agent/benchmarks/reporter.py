"""
Benchmark Reporter — Generates formatted reports from benchmark results.
"""

from tabulate import tabulate

from agent.benchmarks.runner import BenchmarkResult


class BenchmarkReporter:
    """Generates markdown and terminal reports from benchmark results."""

    @staticmethod
    def to_markdown(result: BenchmarkResult) -> str:
        """Generate a markdown report suitable for CI/CD artifacts or documentation."""
        lines = [
            "# 📊 Benchmark Results\n",
            f"**Total Problems:** {result.total_problems}",
            f"**Total Time:** {result.total_time_seconds:.1f}s\n",
            "## Summary Metrics\n",
            "| Metric | Value | Target | Status |",
            "|---|---|---|---|",
            f"| **pass@1** | {result.pass_at_1}% | ≥ 60% | {'✅' if result.pass_at_1 >= 60 else '❌'} |",
            f"| **pass@3** | {result.pass_at_3}% | ≥ 80% | {'✅' if result.pass_at_3 >= 80 else '❌'} |",
            f"| **Recovery Rate** | {result.recovery_rate}% | ≥ 70% | {'✅' if result.recovery_rate >= 70 else '❌'} |",
            f"| **Avg Latency** | {result.avg_latency_ms:.0f}ms | ≤ 15000ms | {'✅' if result.avg_latency_ms <= 15000 else '❌'} |",
            "",
        ]

        breakdown = result.by_difficulty
        if breakdown:
            lines.append("## By Difficulty\n")
            lines.append("| Difficulty | Total | Passed | Rate |")
            lines.append("|---|---|---|---|")
            for diff, data in breakdown.items():
                lines.append(f"| {diff.capitalize()} | {data['total']} | {data['passed']} | {data['rate']}% |")
            lines.append("")

        lines.append("## Detailed Results\n")
        lines.append("| Task ID | Difficulty | Status | Time (ms) |")
        lines.append("|---|---|---|---|")
        for r in result.results:
            status = "✅ PASS" if r.passed else "❌ FAIL"
            lines.append(f"| {r.task_id} | {r.difficulty} | {status} | {r.execution_time_ms:.0f} |")

        return "\n".join(lines)

    @staticmethod
    def to_terminal(result: BenchmarkResult) -> str:
        """Generate a tabular terminal report."""
        headers = ["Metric", "Value", "Target", "Status"]
        data = [
            ["pass@1", f"{result.pass_at_1}%", "≥ 60%", "PASS" if result.pass_at_1 >= 60 else "FAIL"],
            ["pass@3", f"{result.pass_at_3}%", "≥ 80%", "PASS" if result.pass_at_3 >= 80 else "FAIL"],
            ["Recovery Rate", f"{result.recovery_rate}%", "≥ 70%", "PASS" if result.recovery_rate >= 70 else "FAIL"],
            ["Avg Latency", f"{result.avg_latency_ms:.0f}ms", "≤ 15000ms", "PASS" if result.avg_latency_ms <= 15000 else "FAIL"],
        ]
        return tabulate(data, headers=headers, tablefmt="grid")