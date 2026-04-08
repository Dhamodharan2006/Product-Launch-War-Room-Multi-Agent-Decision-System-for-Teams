"""Conditional routing logic for LangGraph."""

from typing import Literal
from src.models.state import WarRoomState


def route_after_data_analysis(state: WarRoomState) -> Literal["pm_analysis", "immediate_rollback", "emergency_pause"]:
    """Route based on data analysis results."""
    # Critical crash rate > 5% triggers immediate rollback
    if state.get("rollback_triggered", False):
        return "immediate_rollback"
    
    # Check risk score from data analysis
    if state.get("risk_scores") and len(state["risk_scores"]) > 0:
        if state["risk_scores"][-1] > 0.7:
            return "emergency_pause"
    
    return "pm_analysis"


def route_after_risk(state: WarRoomState) -> Literal["coordinator", "data_analyst", "marketing_analysis"]:
    """Route based on risk critic output."""
    # If risk critic demands more data, loop back
    if state.get("requires_more_data", False):
        requests = state.get("data_requests", [])
        
        # Route to specific agent based on request
        for req in requests:
            if "Data Analyst" in req:
                return "data_analyst"
            elif "Marketing" in req:
                return "marketing_analysis"
        
        return "data_analyst"
    
    return "coordinator"


def route_final(state: WarRoomState) -> Literal["action_plan", "emergency_pause"]:
    """Final safety check before action plan."""
    avg_risk = sum(state.get("risk_scores", [0])) / max(1, len(state.get("risk_scores", [1])))
    
    if avg_risk > 0.7:
        return "emergency_pause"
    
    return "action_plan"