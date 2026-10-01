"""Sandbox Executor — Runs code inside isolated Docker containers."""

import logging
from dataclasses import dataclass
from typing import Optional
import docker

from agent.config import SANDBOX_DOCKER_IMAGE, SANDBOX_TIMEOUT_SECONDS
from agent.sandbox.resource_limits import DEFAULT_LIMITS, SandboxLimits

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """The structured outcome of running code inside the sandbox."""

    exit_code: int          # 0 = success, non-zero = failure, -1 = timeout/crash
    stdout: str             # Captured standard output
    stderr: str             # Captured error output/tracebacks
    timed_out: bool         # Flag indicating if execution was halted by timeout
    error_message: str = "" # High-level failure description

    @property
    def succeeded(self) -> bool:
        """Helper to determine if execution succeeded cleanly."""
        return self.exit_code == 0 and not self.timed_out


class SandboxExecutor:
    """Manages creation, execution, and cleanup of Docker sandbox containers."""

    def __init__(
        self,
        limits: Optional[SandboxLimits] = None,
        image: str = SANDBOX_DOCKER_IMAGE,
    ):
        self.limits = limits or DEFAULT_LIMITS
        self.image = image

        try:
            # Initialize client from local environment (named pipe on Windows)
            self.client = docker.from_env()
            self.client.ping()
        except docker.errors.DockerException as e:
            raise RuntimeError(
                "Cannot connect to Docker daemon. Is Docker Desktop running?\n"
                f"Error: {e}"
            ) from e

    def run(self, code: str) -> ExecutionResult:
        """Run Python code string inside an isolated ephemeral container."""
        container = None

        try:
            docker_kwargs = self.limits.to_docker_kwargs()

            logger.info("Starting sandbox container...")
            # Detach=True allows non-blocking start so we can enforce our own timeout
            container = self.client.containers.run(
                image=self.image,
                command=["python", "-c", code],
                detach=True,
                **docker_kwargs,
            )

            logger.info(f"Running code with timeout={self.limits.timeout_seconds}s...")
            result = container.wait(timeout=self.limits.timeout_seconds)

            # Retrieve separate stream logs and decode bytes to utf-8 strings
            stdout = container.logs(stdout=True, stderr=False).decode(
                "utf-8", errors="replace"
            )
            stderr = container.logs(stdout=False, stderr=True).decode(
                "utf-8", errors="replace"
            )
            exit_code = result.get("StatusCode", 1)

            return ExecutionResult(
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                timed_out=False,
            )

        except Exception as e:
            error_msg = str(e)
            is_timeout = "Read timed out" in error_msg or "timed out" in error_msg.lower()

            logger.warning(
                f"Execution {'timed out' if is_timeout else 'failed'}: {error_msg}"
            )

            # Force-kill container immediately if still running
            if container:
                try:
                    container.kill()
                except Exception:
                    pass

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=error_msg if not is_timeout else "",
                timed_out=is_timeout,
                error_message=(
                    f"Code execution timed out after {self.limits.timeout_seconds} seconds."
                    if is_timeout
                    else f"Sandbox execution failed: {error_msg}"
                ),
            )

        finally:
            # Always ensure container cleanup occurs
            if container:
                try:
                    container.remove(force=True)
                    logger.info("Sandbox container removed successfully.")
                except Exception:
                    logger.warning("Failed to remove container (may already be destroyed).")