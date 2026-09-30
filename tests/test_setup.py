"""Smoke tests: verify Phase 0 setup is correct."""

import sys


def test_python_version():
    """Verify Python 3.11+ is used."""
    assert sys.version_info >= (3, 11), (
        f"Python 3.11+ required, but you're running {sys.version}."
    )


def test_config_loads_successfully():
    """Verify that config loads and data types are valid."""
    from agent.config import (
        FORBIDDEN_MODULES,
        MAX_REPAIR_ATTEMPTS,
        PROJECT_ROOT,
        SANDBOX_MEMORY_LIMIT,
        SANDBOX_TIMEOUT_SECONDS,
    )

    assert isinstance(SANDBOX_MEMORY_LIMIT, str)
    assert isinstance(SANDBOX_TIMEOUT_SECONDS, int)
    assert isinstance(MAX_REPAIR_ATTEMPTS, int)
    assert isinstance(FORBIDDEN_MODULES, set)


def test_config_values_are_sensible():
    """Sanity checks to prevent accidental bad configurations."""
    from agent.config import (
        MAX_REPAIR_ATTEMPTS,
        SANDBOX_MEMORY_LIMIT,
        SANDBOX_PID_LIMIT,
        SANDBOX_TIMEOUT_SECONDS,
    )

    assert SANDBOX_MEMORY_LIMIT.endswith(("m", "g")), (
        "Memory limit must be like '512m' or '1g'"
    )
    assert 5 <= SANDBOX_TIMEOUT_SECONDS <= 60, "Timeout should be 5-60 seconds"
    assert 1 <= MAX_REPAIR_ATTEMPTS <= 10, "Repair attempts should be 1-10"
    assert 10 <= SANDBOX_PID_LIMIT <= 256


def test_forbidden_modules_include_critical_threats():
    """The security blocklist MUST include the most dangerous modules."""
    from agent.config import FORBIDDEN_MODULES

    critical_threats = {"os", "subprocess", "socket", "requests", "shutil"}
    missing = critical_threats - FORBIDDEN_MODULES
    assert not missing, f"CRITICAL: These dangerous modules are NOT blocked: {missing}"


def test_docker_sdk_importable():
    """Docker SDK must be installed for the sandbox to work."""
    import docker  # noqa: F401


def test_langgraph_importable():
    """LangGraph must be installed for the orchestrator to work."""
    import langgraph  # noqa: F401


def test_pydantic_importable():
    """Pydantic must be installed for output validation to work."""
    import pydantic  # noqa: F401