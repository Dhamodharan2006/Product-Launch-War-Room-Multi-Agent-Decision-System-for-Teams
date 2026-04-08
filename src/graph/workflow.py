"""LangGraph workflow builder and compiler."""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.models.state import WarRoomState
from src.graph.nodes import (
    load_data_node,
    data_analyst_node,
    pm_analysis_node,
    marketing_analysis_node,
    risk_analysis_node,
    coordinator_node,
    action_plan_node,
    emergency_pause_node,
    immediate_rollback_node
)
from src.graph.edges import (
    route_after_data_analysis,
    route_after_risk,
    route_final
)


def build_war_room_graph():
    """Build the complete war room workflow graph."""
    
    # Initialize graph
    workflow = StateGraph(WarRoomState)
    
    # Add nodes
    workflow.add_node("load_data", load_data_node)
    workflow.add_node("data_analyst", data_analyst_node)
    workflow.add_node("pm_analysis", pm_analysis_node)
    workflow.add_node("marketing_analysis", marketing_analysis_node)
    workflow.add_node("risk_analysis", risk_analysis_node)
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("action_plan", action_plan_node)
    workflow.add_node("emergency_pause", emergency_pause_node)
    workflow.add_node("immediate_rollback", immediate_rollback_node)
    
    # Define edges
    workflow.set_entry_point("load_data")
    workflow.add_edge("load_data", "data_analyst")
    
    # Conditional routing from data analysis
    workflow.add_conditional_edges(
        "data_analyst",
        route_after_data_analysis,
        {
            "pm_analysis": "pm_analysis",
            "immediate_rollback": "immediate_rollback",
            "emergency_pause": "emergency_pause"
        }
    )
    
    # Standard flow
    workflow.add_edge("pm_analysis", "marketing_analysis")
    workflow.add_edge("marketing_analysis", "risk_analysis")
    
    # Risk critic can loop back or proceed
    workflow.add_conditional_edges(
        "risk_analysis",
        route_after_risk,
        {
            "coordinator": "coordinator",
            "data_analyst": "data_analyst",
            "marketing_analysis": "marketing_analysis"
        }
    )
    
    # Final safety check
    workflow.add_conditional_edges(
        "coordinator",
        route_final,
        {
            "action_plan": "action_plan",
            "emergency_pause": "emergency_pause"
        }
    )
    
    # Terminal nodes
    workflow.add_edge("action_plan", END)
    workflow.add_edge("emergency_pause", END)
    workflow.add_edge("immediate_rollback", END)
    
    # Add memory for checkpointing
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)


def run_war_room(metrics, feedback, release_notes, thread_id: str = "default"):
    """Execute the war room workflow."""
    from src.config import settings
    settings.ensure_checkpoint_dir()
    
    graph = build_war_room_graph()
    
    initial_state = {
        "metrics": metrics,
        "feedback": feedback,
        "release_notes": release_notes,
        "data_analysis": None,
        "pm_analysis": None,
        "marketing_analysis": None,
        "risk_analysis": None,
        "anomaly_flags": [],
        "sentiment_summary": None,
        "risk_scores": [],
        "emergency_flag": False,
        "rollback_triggered": False,
        "requires_more_data": False,
        "data_requests": [],
        "final_decision": None,
        "execution_plan": None,
        "iteration_count": 0,
        "conversation_history": []
    }
    
    # Run graph with proper configuration
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Use invoke instead of stream for simpler execution
        final_state = graph.invoke(initial_state, config)
        
        # Return the execution plan if available, otherwise final decision
        if final_state.get("execution_plan"):
            return final_state["execution_plan"]
        elif final_state.get("final_decision"):
            return final_state["final_decision"]
        else:
            return None
            
    except Exception as e:
        print(f"Error during graph execution: {e}")
        raise