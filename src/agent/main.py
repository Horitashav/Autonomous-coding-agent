"""Main CLI entry point for the Autonomous Sandboxed Coding Agent."""

import logging
import sys
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from agent.orchestrator.graph import agent_graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

console = Console()


def run_agent(prompt: str) -> dict:
    """Execute the coding agent state machine on a natural language task."""
    console.print(Panel(prompt, title="📝 Task Description", border_style="cyan"))

    # Invoke the LangGraph state machine
    result = agent_graph.invoke({"prompt": prompt})

    status = result.get("status", "unknown")

    if status == "success":
        code = result.get("code", "")
        if code:
            console.print("\n[bold green]✅ Generated & Verified Code:[/bold green]")
            syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
            console.print(syntax)

        output = result.get("final_output", "")
        if output:
            console.print(Panel(output, title="📤 Sandbox Output", border_style="green"))

    elif status == "blocked":
        error = result.get("error_summary", "Task blocked by safety controls.")
        console.print(Panel(error, title="🚫 Security Blocked", border_style="red"))

    else:
        error = result.get("error_summary", "Task failed after retries.")
        console.print(Panel(error, title="❌ Execution Failed", border_style="red"))

    # Display execution metrics table
    table = Table(title="📊 Run Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold white")
    table.add_row("Status", status)
    table.add_row("Attempts", str(result.get("attempts", 0)))
    table.add_row("Tokens Used", str(result.get("total_tokens", 0)))
    table.add_row("Estimated Cost", f"${result.get('total_cost', 0):.5f}")
    console.print(table)

    return result


def main():
    """Command-line interface handler."""
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        console.print("[bold cyan]🤖 Autonomous Coding Agent[/bold cyan]")
        prompt = input("\nEnter task: ").strip()
        if not prompt:
            console.print("[yellow]Empty task entered. Exiting.[/yellow]")
            sys.exit(0)

    run_agent(prompt)


if __name__ == "__main__":
    main()