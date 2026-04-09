#!/usr/bin/env python3
"""Main entry point for Product Launch War Room."""

#!/usr/bin/env python3
"""Main entry point for Product Launch War Room."""

import sys
from pathlib import Path
# Add src directory to path BEFORE any local imports
sys.path.insert(0, str(Path(__file__).parent))

import json
from utils.tracer import tracer  # Now this will work!
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.config import settings
from src.data.mock_data import save_mock_data
from src.graph.workflow import run_war_room

# ... rest of your code

console = Console()


def display_results(result: dict):
    """Display formatted results."""
    if not result:
        console.print("[red]No results generated[/red]")
        return
    
    decision = result.get("decision", "Unknown")
    color = {"Proceed": "green", "Pause": "yellow", "Roll Back": "red"}.get(decision, "white")
    
    console.print(Panel.fit(f"[bold {color}]DECISION: {decision}[/bold {color}]", title="Product Launch War Room", border_style=color))
    
    rationale = result.get("rationale", {})
    console.print(f"\n[bold]Key Drivers:[/bold]")
    for driver in rationale.get("key_drivers", []):
        console.print(f"  • {driver}")
    
    table = Table(title="Risk Register")
    table.add_column("Risk", style="red")
    table.add_column("Severity", style="yellow")
    table.add_column("Mitigation", style="green")
    
    for risk in result.get("risk_register", []):
        table.add_row(risk.get("risk", "")[:50], risk.get("severity", ""), risk.get("mitigation", "")[:40])
    console.print(table)
    
    console.print(f"\n[bold]Next 24-48 Hours:[/bold]")
    for action in result.get("action_plan", {}).get("next_24_48_hours", []):
        console.print(f"  • {action.get('action')} (Owner: {action.get('owner')}, Due: {action.get('due_hours')}h)")
    
    comms = result.get("communication_plan", {})
    console.print(f"\n[bold]Communications:[/bold]")
    console.print(f"  Internal: {comms.get('internal', 'N/A')}")
    console.print(f"  External: {comms.get('external', 'N/A')}")
    
    confidence = result.get("confidence_score", 0)
    conf_color = "green" if confidence > 0.7 else "yellow" if confidence > 0.4 else "red"
    console.print(f"\n[bold {conf_color}]Confidence Score: {confidence:.0%}[/bold {conf_color}]")
    
    # Save decision
    output_path = Path("./outputs/final_decision.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    console.print(f"\n[dim]Results saved to: {output_path}[/dim]")
    
    # NEW: Show trace info
    trace_path = Path("./traces/sample_trace.json")
    if trace_path.exists():
        console.print(f"[dim]Execution trace: {trace_path}[/dim]")
        console.print(f"[dim]View detailed trace in traces/ folder[/dim]")


def main():
    """Main execution flow."""
    console.print("[bold blue]Product Launch War Room - Multi-Agent System[/bold blue]")
    
    if not settings.GROQ_API_KEY:
        console.print("[red]Error: GROQ_API_KEY not set in environment[/red]")
        sys.exit(1)
    
    console.print("\n[dim]Generating mock data...[/dim]")
    metrics, feedback, release_notes = save_mock_data()
    
    console.print("[dim]Starting multi-agent analysis...[/dim]\n")
    
    try:
        result = run_war_room(metrics=metrics, feedback=feedback, release_notes=release_notes, thread_id="launch_001")
        
        if result:
            display_results(result)
            console.print("\n[green]Execution complete. Check traces/ folder for detailed execution logs.[/green]")
        else:
            console.print("[yellow]Warning: Workflow completed but no result was generated[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error during execution: {e}[/red]")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()