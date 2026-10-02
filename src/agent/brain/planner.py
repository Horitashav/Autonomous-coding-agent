"""Planner — Analyzes tasks before code generation."""

import json
import logging
from dataclasses import dataclass, field

from agent.brain.llm_client import LLMClient
from agent.brain.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_USER_TEMPLATE

logger = logging.getLogger(__name__)


@dataclass
class TaskPlan:
    """Structured assessment of task feasibility and constraints."""

    task_summary: str = ""
    approach: str = ""
    required_libraries: list[str] = field(default_factory=list)
    estimated_complexity: str = "moderate"
    potential_issues: list[str] = field(default_factory=list)
    requires_network: bool = False
    requires_file_io: bool = False
    is_destructive: bool = False
    raw_response: str = ""

    @property
    def is_feasible(self) -> bool:
        """Sandbox has no internet, so network-dependent tasks cannot run."""
        return not self.requires_network

    @property
    def needs_approval(self) -> bool:
        """Tasks flagged as destructive require a human confirmation step."""
        return self.is_destructive


class Planner:
    """Pre-execution analyzer for incoming coding tasks."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client or LLMClient()

    def analyze(self, task_description: str) -> TaskPlan:
        """Generate structured plan for the given task."""
        user_prompt = PLANNER_USER_TEMPLATE.format(task_description=task_description)

        try:
            response = self.llm_client.generate(
                system_prompt=PLANNER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                max_tokens=1024,
            )

            data = json.loads(response.content)

            return TaskPlan(
                task_summary=data.get("task_summary", ""),
                approach=data.get("approach", ""),
                required_libraries=data.get("required_libraries", []),
                estimated_complexity=data.get("estimated_complexity", "moderate"),
                potential_issues=data.get("potential_issues", []),
                requires_network=data.get("requires_network", False),
                requires_file_io=data.get("requires_file_io", False),
                is_destructive=data.get("is_destructive", False),
                raw_response=response.content,
            )
        except Exception as e:
            logger.warning(f"Planner failed to return clean JSON ({e}). Falling back to defaults.")
            return TaskPlan(
                task_summary=task_description,
                approach="Direct execution",
                estimated_complexity="moderate",
            )
