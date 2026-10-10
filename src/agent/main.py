"""Main entry point for running the autonomous coding agent via CLI."""

import sys

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from agent.observability.tracer import RunTracer
from agent.orchestrator.graph import agent_graph

console = Console()


def run_agent(prompt: str) -> None:
    """Execute the agent workflow on a user prompt and display formatted outputs."""
    console.print()
    console.print(
        Panel(
            prompt,
            title="[bold blue]📝 Task Description[/bold blue]",
            border_style="blue",
        )
    )

    # Execute through the compiled LangGraph state machine
    result = agent_graph.invoke({"prompt": prompt})

    status = result.get("status", "unknown")
    code = result.get("code", "")
    final_output = result.get("final_output", "")
    error_summary = result.get("error_summary", "")

    # Display code if generated
    if code:
        console.print()
        console.print("[bold green]✅ Generated & Verified Code:[/bold green]")
        console.print(Syntax(code, "python", theme="monokai", line_numbers=True))

    # Display execution outcome
    if status == "success":
        console.print()
        console.print(
            Panel(
                final_output,
                title="[bold green]📤 Sandbox Output[/bold green]",
                border_style="green",
            )
        )
    elif status == "blocked":
        console.print()
        console.print(
            Panel(
                error_summary or "Task blocked by guardrails.",
                title="[bold red]🚫 Security Blocked[/bold red]",
                border_style="red",
            )
        )
    elif status == "rejected":
        console.print()
        console.print(
            Panel(
                error_summary or "Execution rejected by user.",
                title="[bold yellow]🛑 Execution Canceled[/bold yellow]",
                border_style="yellow",
            )
        )
    else:
        console.print()
        console.print(
            Panel(
                error_summary or "Task failed to execute successfully.",
                title="[bold red]❌ Execution Failure[/bold red]",
                border_style="red",
            )
        )

    # Save run execution trace to .run_history/
    tracer = RunTracer()
    trace_file = tracer.log_run(result)
    console.print()
    console.print(f"[dim]Run trace logged to: {trace_file}[/dim]")

    # Display summary metrics
    table = Table(title="📊 Run Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Status", status)
    table.add_row("Attempts", str(result.get("attempts", 0)))
    table.add_row("Tokens Used", str(result.get("total_tokens", 0)))
    table.add_row("Estimated Cost", f"${result.get('total_cost', 0.0):.5f}")

    console.print(table)


def main() -> None:
    """Read CLI arguments or trigger interactive input."""
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        console.print("[bold cyan]Enter a coding task for the agent:[/bold cyan]")
        prompt = input("> ").strip()

    if not prompt:
        console.print("[yellow]No task provided. Exiting.[/yellow]")
        return

    run_agent(prompt)


if __name__ == "__main__":
    main()
