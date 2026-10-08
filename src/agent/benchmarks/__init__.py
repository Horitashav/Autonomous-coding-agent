"""
Benchmarks module — Automated evaluation of agent performance.
"""

from agent.benchmarks.reporter import BenchmarkReporter
from agent.benchmarks.runner import BenchmarkResult, BenchmarkRunner

__all__ = ["BenchmarkRunner", "BenchmarkResult", "BenchmarkReporter"]