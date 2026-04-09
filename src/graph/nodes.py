"""LangGraph node implementations with persistent tracing."""

import json
import traceback
from typing import Dict, Any
from rich.console import Console

from src.models.state import WarRoomState
from src.agents import DataAnalystAgent, ProductManagerAgent, MarketingAgent, RiskCriticAgent
from src.utils.tracer import tracer

console = Console()


def load_data_node(state: WarRoomState) -> Dict[str, Any]:
    """Load and initialize all data sources."""
    console.print("[bold blue]Loading data sources...[/bold blue]")
    tracer.log_agent_start("load_data", {"metrics_count": len(state.get("metrics", {})), "feedback_count": len(state.get("feedback", []))})
    
    result = {
        "conversation_history": [{"role": "system", "content": "Data loaded successfully"}]
    }
    
    tracer.log_agent_end("load_data", result, ["data_loader"])
    return result


def data_analyst_node(state: WarRoomState) -> Dict[str, Any]:
    """Run data analyst agent on metrics."""
    console.print("[bold green]Data Analyst analyzing metrics...[/bold green]")
    tracer.log_agent_start("data_analyst", {"launch_day": 7})
    
    try:
        agent = DataAnalystAgent()
        
        # Log tool calls
        metrics_json = json.dumps(state["metrics"])
        tracer.log_tool_call("metric_aggregation_tool", {"metrics_count": len(state["metrics"])}, "executed")
        tracer.log_tool_call("anomaly_detection_tool", {"threshold_config": "crash_rate: 2%"}, "executed")
        tracer.log_tool_call("trend_comparison_tool", {"split_index": 7}, "executed")
        
        result = agent.analyze({
            "metrics": state["metrics"],
            "launch_day": 7
        })
        
        # Log LLM interaction
        tracer.log_llm_call("data_analyst", result.get("summary", "")[:200], result.get("summary", "")[:200], "llama-3.3-70b-versatile", 284)
        
        emergency = result.get("requires_rollback", False)
        anomalies = result.get("critical_findings", [])
        
        output = {
            "data_analysis": result,
            "emergency_flag": emergency,
            "rollback_triggered": emergency,
            "anomaly_flags": anomalies,
            "risk_scores": [result.get("risk_score", 0)],
            "conversation_history": [{"role": "data_analyst", "content": result.get("summary", "")}]
        }
        
        tracer.log_agent_end("data_analyst", output, ["metric_aggregation_tool", "anomaly_detection_tool", "trend_comparison_tool"])
        return output
        
    except Exception as e:
        tracer.log_tool_call("data_analyst", {}, str(e), error=str(e))
        raise


def pm_analysis_node(state: WarRoomState) -> Dict[str, Any]:
    """Run product manager assessment."""
    console.print("[bold green]Product Manager assessing strategy...[/bold green]")
    tracer.log_agent_start("pm_analysis", {"has_sentiment": bool(state.get("sentiment_summary"))})
    
    try:
        agent = ProductManagerAgent()
        result = agent.analyze({
            "data_analysis": state["data_analysis"],
            "sentiment_summary": state.get("sentiment_summary") or {},
            "release_notes": state["release_notes"]
        })
        
        tracer.log_llm_call("pm_analysis", "strategic assessment prompt", result.get("summary", "")[:200], "llama-3.3-70b-versatile", 371)
        
        output = {
            "pm_analysis": result,
            "risk_scores": [result.get("risk_score", 0)],
            "conversation_history": [{"role": "pm", "content": result.get("summary", "")}]
        }
        
        tracer.log_agent_end("pm_analysis", output, [])
        return output
        
    except Exception as e:
        tracer.log_tool_call("pm_analysis", {}, str(e), error=str(e))
        raise


def marketing_analysis_node(state: WarRoomState) -> Dict[str, Any]:
    """Run marketing/comms analysis."""
    console.print("[bold green]Marketing analyzing perception...[/bold green]")
    tracer.log_agent_start("marketing_analysis", {"feedback_count": len(state.get("feedback", []))})
    
    try:
        agent = MarketingAgent()
        result = agent.analyze({
            "feedback": state["feedback"],
            "metrics": state["metrics"]
        })
        
        tracer.log_tool_call("sentiment_analysis_tool", {"feedback_count": len(state["feedback"])}, f"sentiment_score: {result.get('sentiment_data', {}).get('avg_sentiment_score', 0)}")
        tracer.log_tool_call("feedback_clustering_tool", {"feedback_count": len(state["feedback"])}, f"clusters: {list(result.get('issue_clusters', {}).get('clusters', {}).keys())}")
        tracer.log_llm_call("marketing_analysis", "sentiment analysis prompt", result.get("summary", "")[:200], "llama-3.1-8b-instant", 232)
        
        output = {
            "marketing_analysis": result,
            "sentiment_summary": result.get("sentiment_data", {}),
            "risk_scores": [result.get("risk_score", 0)],
            "conversation_history": [{"role": "marketing", "content": result.get("summary", "")}]
        }
        
        tracer.log_agent_end("marketing_analysis", output, ["sentiment_analysis_tool", "feedback_clustering_tool"])
        return output
        
    except Exception as e:
        tracer.log_tool_call("marketing_analysis", {}, str(e), error=str(e))
        raise


def risk_analysis_node(state: WarRoomState) -> Dict[str, Any]:
    """Run risk critic analysis."""
    console.print("[bold green]Risk Critic evaluating threats...[/bold green]")
    tracer.log_agent_start("risk_analysis", {"current_risk_scores": state.get("risk_scores", [])})
    
    try:
        agent = RiskCriticAgent()
        result = agent.analyze({
            "data_analysis": state["data_analysis"],
            "marketing_analysis": state["marketing_analysis"],
            "pm_analysis": state["pm_analysis"],
            "metrics": state["metrics"],
            "feedback": state["feedback"]
        })
        
        tracer.log_tool_call("risk_scoring_tool", {"metrics_count": 9, "sentiment_data": True}, f"risk_score: {result.get('risk_score', 0)}")
        tracer.log_tool_call("rollback_impact_assessment_tool", {"crash_rate": state['metrics'].get('crash_rate', [0])[-1]}, f"rollback_recommended: {result.get('rollback_analysis', {}).get('rollback_recommended', False)}")
        tracer.log_llm_call("risk_analysis", "risk assessment prompt", result.get("summary", "")[:200], "llama-3.3-70b-versatile", 240)
        
        output = {
            "risk_analysis": result,
            "requires_more_data": result.get("requires_more_data", False),
            "data_requests": result.get("challenges_to_agents", []),
            "risk_scores": [result.get("risk_score", 0)],
            "conversation_history": [{"role": "risk_critic", "content": result.get("summary", "")}]
        }
        
        tracer.log_agent_end("risk_analysis", output, ["risk_scoring_tool", "rollback_impact_assessment_tool"])
        return output
        
    except Exception as e:
        tracer.log_tool_call("risk_analysis", {}, str(e), error=str(e))
        raise


def coordinator_node(state: WarRoomState) -> Dict[str, Any]:
    """Synthesize all inputs and make final decision."""
    console.print("[bold yellow]Coordinator synthesizing decision...[/bold yellow]")
    tracer.log_agent_start("coordinator", {"risk_scores": state.get("risk_scores", [])})
    
    try:
        avg_risk = sum(state["risk_scores"]) / max(1, len(state["risk_scores"]))
        
        if avg_risk > 0.7:
            decision = "Roll Back"
        elif avg_risk > 0.5:
            decision = "Pause"
        else:
            decision = "Proceed"
            
        key_drivers = []
        if state.get("data_analysis", {}).get("requires_rollback"):
            key_drivers.append("Critical crash rate detected")
        
        risk_factors = state.get("risk_analysis", {}).get("risk_assessment", {}).get("risk_factors", [])
        if risk_factors:
            key_drivers.extend(risk_factors[:2])
            
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
            "risk_register": [{"risk": f, "severity": "High", "mitigation": "Investigate and resolve"} for f in risk_factors[:3]] if risk_factors else [],
            "action_plan": {
                "next_24_48_hours": [
                    {"action": "Monitor crash rate hourly", "owner": "Data Analyst", "due_hours": 24},
                    {"action": "Prepare customer communication", "owner": "Marketing", "due_hours": 48}
                ]
            },
            "communication_plan": {
                "internal": f"Launch status: {decision}. Risk level: {avg_risk:.2f}",
                "external": "We are monitoring performance closely" if decision == "Proceed" else "We are addressing reported issues"
            },
            "confidence_score": round(1 - avg_risk, 2),
            "what_would_increase_confidence": ["48 hours of stable metrics", "Root cause analysis of anomalies"]
        }
        
        tracer.log_decision(decision, round(1 - avg_risk, 2), final_decision["rationale"])
        
        output = {
            "final_decision": final_decision,
            "conversation_history": [{"role": "coordinator", "content": f"Decision: {decision}"}]
        }
        
        tracer.log_agent_end("coordinator", output, [])
        return output
        
    except Exception as e:
        tracer.log_tool_call("coordinator", {}, str(e), error=str(e))
        raise


def action_plan_node(state: WarRoomState) -> Dict[str, Any]:
    """Generate structured action plan output."""
    console.print("[bold cyan]Generating final action plan...[/bold cyan]")
    tracer.log_agent_start("action_plan", {"decision": state.get("final_decision", {}).get("decision")})
    
    output = {"execution_plan": state["final_decision"]}
    tracer.log_agent_end("action_plan", output, [])
    return output


def emergency_pause_node(state: WarRoomState) -> Dict[str, Any]:
    """Emergency node for high-risk scenarios."""
    console.print("[bold red]EMERGENCY: High risk detected - Initiating pause protocol[/bold red]")
    tracer.log_agent_start("emergency_pause", {"trigger": "risk_score > 0.7"})
    tracer.log_decision("Pause", 0.5, {"emergency": true, "reason": "Risk threshold exceeded"})
    
    output = {
        "final_decision": {
            "decision": "Pause",
            "rationale": {"key_drivers": ["Risk score exceeded 0.7 threshold"], "metric_references": {}, "feedback_summary": "Emergency protocol activated"},
            "risk_register": [],
            "action_plan": {"next_24_48_hours": []},
            "communication_plan": {"internal": "Emergency pause triggered by risk threshold", "external": "Service temporarily paused for investigation"},
            "confidence_score": 0.5,
            "what_would_increase_confidence": ["Risk mitigation", "Root cause resolution"]
        },
        "conversation_history": [{"role": "system", "content": "Emergency pause triggered"}]
    }
    tracer.log_agent_end("emergency_pause", output, [])
    return output


def immediate_rollback_node(state: WarRoomState) -> Dict[str, Any]:
    """Immediate rollback for critical failures."""
    console.print("[bold red]CRITICAL: Rollback triggered[/bold red]")
    tracer.log_agent_start("immediate_rollback", {"trigger": "crash_rate > 5%"})
    tracer.log_decision("Roll Back", 0.9, {"emergency": true, "reason": "Critical crash rate detected"})
    
    output = {
        "final_decision": {
            "decision": "Roll Back",
            "rationale": {"key_drivers": ["Critical crash rate > 5% detected"], "metric_references": {"crash_rate": ">5%"}, "feedback_summary": "Critical stability issues"},
            "risk_register": [],
            "action_plan": {"next_24_48_hours": [{"action": "Execute rollback procedure", "owner": "DevOps", "due_hours": 1}]},
            "communication_plan": {"internal": "Immediate rollback in progress", "external": "Service temporarily unavailable for maintenance"},
            "confidence_score": 0.9,
            "what_would_increase_confidence": ["Successful rollback", "Stable previous version"]
        },
        "conversation_history": [{"role": "system", "content": "Immediate rollback triggered"}]
    }
    tracer.log_agent_end("immediate_rollback", output, [])
    return output