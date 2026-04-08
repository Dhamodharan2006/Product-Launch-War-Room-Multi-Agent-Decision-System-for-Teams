"""LangGraph node implementations."""

import json
import traceback
from typing import Dict, Any
from rich.console import Console

from src.models.state import WarRoomState
from src.agents import DataAnalystAgent, ProductManagerAgent, MarketingAgent, RiskCriticAgent

console = Console()


def load_data_node(state: WarRoomState) -> Dict[str, Any]:
    """Load and initialize all data sources."""
    console.print("[bold blue]📊 Loading data sources...[/bold blue]")
    
    return {
        "conversation_history": [{"role": "system", "content": "Data loaded successfully"}]
    }


def data_analyst_node(state: WarRoomState) -> Dict[str, Any]:
    """Run data analyst agent on metrics."""
    console.print("[bold green]🔍 Data Analyst analyzing metrics...[/bold green]")
    
    try:
        agent = DataAnalystAgent()
        result = agent.analyze({
            "metrics": state["metrics"],
            "launch_day": 7
        })
        
        # Check for critical conditions
        emergency = result.get("requires_rollback", False)
        anomalies = result.get("critical_findings", [])
        
        return {
            "data_analysis": result,
            "emergency_flag": emergency,
            "rollback_triggered": emergency,
            "anomaly_flags": anomalies,
            "risk_scores": [result.get("risk_score", 0)],
            "conversation_history": [{"role": "data_analyst", "content": result.get("summary", "")}]
        }
    except Exception as e:
        console.print(f"[red]Error in data_analyst_node: {e}[/red]")
        traceback.print_exc()
        raise


def pm_analysis_node(state: WarRoomState) -> Dict[str, Any]:
    """Run product manager assessment."""
    console.print("[bold green]📋 Product Manager assessing strategy...[/bold green]")
    
    try:
        agent = ProductManagerAgent()
        result = agent.analyze({
            "data_analysis": state["data_analysis"],
            "sentiment_summary": state.get("sentiment_summary") or {},
            "release_notes": state["release_notes"]
        })
        
        return {
            "pm_analysis": result,
            "risk_scores": [result.get("risk_score", 0)],
            "conversation_history": [{"role": "pm", "content": result.get("summary", "")}]
        }
    except Exception as e:
        console.print(f"[red]Error in pm_analysis_node: {e}[/red]")
        traceback.print_exc()
        raise


def marketing_analysis_node(state: WarRoomState) -> Dict[str, Any]:
    """Run marketing/comms analysis."""
    console.print("[bold green]📢 Marketing analyzing perception...[/bold green]")
    
    try:
        agent = MarketingAgent()
        result = agent.analyze({
            "feedback": state["feedback"],
            "metrics": state["metrics"]
        })
        
        return {
            "marketing_analysis": result,
            "sentiment_summary": result.get("sentiment_data", {}),
            "risk_scores": [result.get("risk_score", 0)],
            "conversation_history": [{"role": "marketing", "content": result.get("summary", "")}]
        }
    except Exception as e:
        console.print(f"[red]Error in marketing_analysis_node: {e}[/red]")
        traceback.print_exc()
        raise


def risk_analysis_node(state: WarRoomState) -> Dict[str, Any]:
    """Run risk critic analysis."""
    console.print("[bold green]⚠️ Risk Critic evaluating threats...[/bold green]")
    
    try:
        agent = RiskCriticAgent()
        result = agent.analyze({
            "data_analysis": state["data_analysis"],
            "marketing_analysis": state["marketing_analysis"],
            "pm_analysis": state["pm_analysis"],
            "metrics": state["metrics"],
            "feedback": state["feedback"]
        })
        
        return {
            "risk_analysis": result,
            "requires_more_data": result.get("requires_more_data", False),
            "data_requests": result.get("challenges_to_agents", []),
            "risk_scores": [result.get("risk_score", 0)],
            "conversation_history": [{"role": "risk_critic", "content": result.get("summary", "")}]
        }
    except Exception as e:
        console.print(f"[red]Error in risk_analysis_node: {e}[/red]")
        traceback.print_exc()
        raise


def coordinator_node(state: WarRoomState) -> Dict[str, Any]:
    """Synthesize all inputs and make final decision."""
    console.print("[bold yellow]🎯 Coordinator synthesizing decision...[/bold yellow]")
    
    try:
        # Aggregate risk scores
        avg_risk = sum(state["risk_scores"]) / max(1, len(state["risk_scores"]))
        
        # Determine decision
        if avg_risk > 0.7:
            decision = "Roll Back"
        elif avg_risk > 0.5:
            decision = "Pause"
        else:
            decision = "Proceed"
        
        # Build rationale
        key_drivers = []
        if state.get("data_analysis", {}).get("requires_rollback"):
            key_drivers.append("Critical crash rate detected")
        
        risk_factors = state.get("risk_analysis", {}).get("risk_assessment", {}).get("risk_factors", [])
        if risk_factors:
            key_drivers.extend(risk_factors[:2])
        
        # Build final output structure
        final_decision = {
            "decision": decision,
            "rationale": {
                "key_drivers": key_drivers if key_drivers else ["Standard monitoring"],
                "metric_references": {
                    "crash_rate": f"{state['metrics'].get('crash_rate', [0])[-1]}% (current)",
                    "avg_sentiment": f"{state.get('sentiment_summary', {}).get('avg_sentiment_score', 0)}/1.0"
                },
                "feedback_summary": state.get("marketing_analysis", {}).get("summary", "No summary available")
            },
            "risk_register": [
                {
                    "risk": f,
                    "severity": "High",
                    "mitigation": "Investigate and resolve"
                }
                for f in risk_factors[:3]
            ] if risk_factors else [],
            "action_plan": {
                "next_24_48_hours": [
                    {
                        "action": "Monitor crash rate hourly",
                        "owner": "Data Analyst",
                        "due_hours": 24
                    },
                    {
                        "action": "Prepare customer communication",
                        "owner": "Marketing",
                        "due_hours": 48
                    }
                ]
            },
            "communication_plan": {
                "internal": f"Launch status: {decision}. Risk level: {avg_risk:.2f}",
                "external": "We are monitoring performance closely" if decision == "Proceed" else "We are addressing reported issues"
            },
            "confidence_score": round(1 - avg_risk, 2),
            "what_would_increase_confidence": [
                "48 hours of stable metrics",
                "Root cause analysis of anomalies"
            ]
        }
        
        console.print(f"[green]Decision synthesized: {decision}[/green]")
        
        return {
            "final_decision": final_decision,
            "conversation_history": [{"role": "coordinator", "content": f"Decision: {decision}"}]
        }
        
    except Exception as e:
        console.print(f"[red]Error in coordinator: {e}[/red]")
        traceback.print_exc()
        return {
            "final_decision": {
                "decision": "Pause",
                "rationale": {"key_drivers": ["Error in decision synthesis"], "metric_references": {}, "feedback_summary": ""},
                "risk_register": [],
                "action_plan": {"next_24_48_hours": []},
                "communication_plan": {"internal": "Error occurred", "external": "Investigating"},
                "confidence_score": 0.0,
                "what_would_increase_confidence": []
            },
            "conversation_history": [{"role": "coordinator", "content": f"Error: {str(e)}"}]
        }


def action_plan_node(state: WarRoomState) -> Dict[str, Any]:
    """Generate structured action plan output."""
    console.print("[bold cyan]✅ Generating final action plan...[/bold cyan]")
    
    return {
        "execution_plan": state["final_decision"]
    }


def emergency_pause_node(state: WarRoomState) -> Dict[str, Any]:
    """Emergency node for high-risk scenarios."""
    console.print("[bold red]🚨 EMERGENCY: High risk detected - Initiating pause protocol[/bold red]")
    
    return {
        "final_decision": {
            "decision": "Pause",
            "rationale": {
                "key_drivers": ["Risk score exceeded 0.7 threshold"],
                "metric_references": {},
                "feedback_summary": "Emergency protocol activated"
            },
            "risk_register": [],
            "action_plan": {"next_24_48_hours": []},
            "communication_plan": {
                "internal": "Emergency pause triggered by risk threshold",
                "external": "Service temporarily paused for investigation"
            },
            "confidence_score": 0.5,
            "what_would_increase_confidence": ["Risk mitigation", "Root cause resolution"]
        },
        "conversation_history": [{"role": "system", "content": "Emergency pause triggered"}]
    }


def immediate_rollback_node(state: WarRoomState) -> Dict[str, Any]:
    """Immediate rollback for critical failures."""
    console.print("[bold red]🚨 CRITICAL: Rollback triggered[/bold red]")
    
    return {
        "final_decision": {
            "decision": "Roll Back",
            "rationale": {
                "key_drivers": ["Critical crash rate > 5% detected"],
                "metric_references": {"crash_rate": ">5%"},
                "feedback_summary": "Critical stability issues"
            },
            "risk_register": [],
            "action_plan": {
                "next_24_48_hours": [
                    {"action": "Execute rollback procedure", "owner": "DevOps", "due_hours": 1}
                ]
            },
            "communication_plan": {
                "internal": "Immediate rollback in progress",
                "external": "Service temporarily unavailable for maintenance"
            },
            "confidence_score": 0.9,
            "what_would_increase_confidence": ["Successful rollback", "Stable previous version"]
        },
        "conversation_history": [{"role": "system", "content": "Immediate rollback triggered"}]
    }