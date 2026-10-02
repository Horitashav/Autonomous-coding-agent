"""Tests for the Docker sandbox executor."""

import pytest

from agent.sandbox.executor import SandboxExecutor
from agent.sandbox.resource_limits import SandboxLimits


@pytest.fixture(scope="module")
def executor():
    """Shared SandboxExecutor instance for tests in this module."""
    try:
        return SandboxExecutor(
            limits=SandboxLimits(timeout_seconds=10),
            image="agent-sandbox",
        )
    except RuntimeError:
        pytest.skip("Docker is not available — skipping sandbox tests")


@pytest.fixture
def fast_executor():
    """Executor with a short 3-second timeout for testing timeout behavior."""
    try:
        return SandboxExecutor(
            limits=SandboxLimits(timeout_seconds=3),
            image="agent-sandbox",
        )
    except RuntimeError:
        pytest.skip("Docker is not available")


class TestHappyPath:
    """Verify normal code execution succeeds."""

    def test_simple_print(self, executor):
        result = executor.run('print("Hello, Sandbox!")')
        assert result.succeeded
        assert "Hello, Sandbox!" in result.stdout

    def test_arithmetic(self, executor):
        result = executor.run("print(sum(range(1, 101)))")
        assert result.succeeded
        assert "5050" in result.stdout

    def test_numpy_available(self, executor):
        code = "import numpy as np; arr = np.array([1, 2, 3]); print(arr.mean())"
        result = executor.run(code)
        assert result.succeeded
        assert "2.0" in result.stdout

    def test_pandas_available(self, executor):
        code = "import pandas as pd; df = pd.DataFrame({'a': [1, 2]}); print(df.shape)"
        result = executor.run(code)
        assert result.succeeded
        assert "(2, 1)" in result.stdout


class TestErrorHandling:
    """Verify that execution errors are captured cleanly."""

    def test_syntax_error(self, executor):
        result = executor.run('print("missing closing quote)')
        assert not result.succeeded
        assert "SyntaxError" in result.stderr

    def test_runtime_error(self, executor):
        result = executor.run("x = 1 / 0")
        assert not result.succeeded
        assert "ZeroDivisionError" in result.stderr


class TestSecurity:
    """Verify resource limits and containment."""

    def test_timeout_kills_infinite_loop(self, fast_executor):
        result = fast_executor.run("while True: pass")
        assert not result.succeeded
        assert result.timed_out

    def test_network_blocked(self, executor):
        code = """
import urllib.request
try:
    urllib.request.urlopen("https://google.com", timeout=3)
    print("NETWORK_ACCESSIBLE")
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}")
"""
        result = executor.run(code)
        assert "NETWORK_ACCESSIBLE" not in result.stdout

    def test_cannot_write_to_root(self, executor):
        code = """
try:
    with open("/etc/test_write", "w") as f:
        f.write("test")
    print("WRITE_SUCCEEDED")
except Exception:
    print("BLOCKED")
"""
        result = executor.run(code)
        assert "WRITE_SUCCEEDED" not in result.stdout

    def test_can_write_to_tmp(self, executor):
        code = """
with open("/tmp/test.txt", "w") as f:
    f.write("hello tmpfs")
with open("/tmp/test.txt", "r") as f:
    print(f.read())
"""
        result = executor.run(code)
        assert result.succeeded
        assert "hello tmpfs" in result.stdout


class TestEdgeCases:
    """Verify edge inputs."""

    def test_empty_code(self, executor):
        result = executor.run("")
        assert result.exit_code == 0

    def test_unicode_output(self, executor):
        result = executor.run('print("Hello 🌍 — नमस्कार")')
        assert result.succeeded
        assert "🌍" in result.stdout
