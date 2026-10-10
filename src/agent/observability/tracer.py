"""Tracer — Persists run history, token costs, and node execution traces."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent.orchestrator.state import AgentState

RUN_HISTORY_DIR = Path(".run_history")


class RunTracer:
    """Records audit logs and telemetry for agent executions."""

    def __init__(self, run_dir: Path = RUN_HISTORY_DIR):
        self.run_dir = run_dir
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def log_run(self, state: AgentState) -> Path:
        """Write the completed state metadata to a timestamped JSON file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        status = state.get("status", "unknown")
        filename = self.run_dir / f"run_{timestamp}_{status}.json"

        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt": state.get("prompt", ""),
            "status": status,
            "task_summary": state.get("task_summary", ""),
            "needs_approval": state.get("needs_approval", False),
            "approval_reason": state.get("approval_reason", ""),
            "human_approved": state.get("human_approved", True),
            "attempts": state.get("attempts", 0),
            "total_tokens": state.get("total_tokens", 0),
            "total_cost": state.get("total_cost", 0.0),
            "final_output": state.get("final_output", ""),
            "error_summary": state.get("error_summary", ""),
            "code": state.get("code", ""),
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)

        return filename
