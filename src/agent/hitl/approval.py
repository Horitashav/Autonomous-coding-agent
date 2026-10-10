"""Human-in-the-Loop (HITL) — Approval gate for dangerous operations."""

import logging
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class ApprovalResult:
    approved: bool
    reason: str = ""
    reviewer: str = "cli_operator"


def request_approval(
    task_description: str, planned_code: str, risk_factors: list[str]
) -> ApprovalResult:
    console.print()
    console.print(
        Panel(
            "[bold red]⚠️  HUMAN APPROVAL REQUIRED[/bold red]\n\n"
            "The agent has planned an action requiring explicit confirmation.",
            border_style="red",
        )
    )
    console.print(f"\n[bold]Task:[/bold] {task_description}")
    console.print("\n[bold red]Risk Factors:[/bold red]")
    for factor in risk_factors:
        console.print(f"  🔴 {factor}")

    if planned_code:
        console.print("\n[bold]Proposed Code:[/bold]")
        console.print(Syntax(planned_code, "python", theme="monokai", line_numbers=True))

    approved = Confirm.ask(
        "\n[bold yellow]Authorize execution in sandbox?[/bold yellow]", default=False
    )
    reason = "Manually approved via CLI" if approved else "Manually rejected via CLI"
    return ApprovalResult(approved=approved, reason=reason)


def check_if_approval_needed(
    task_description: str, planned_code: str, is_destructive: bool
) -> bool:
    if not is_destructive:
        return True

    risk_factors = []
    lower_code = planned_code.lower()
    if any(k in lower_code for k in ["delete", "remove", "drop", "unlink"]):
        risk_factors.append("Code contains deletion/destructive operations")
    if not risk_factors:
        risk_factors.append("Task was flagged as high-risk or destructive by planner")

    result = request_approval(task_description, planned_code, risk_factors)
    return result.approved
