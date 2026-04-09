"""LangGraph workflow builder with persistent tracing."""

import uuid
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.models.state import WarRoomState
from src.graph.nodes import (
    load_data_node, data_analyst_node, pm_analysis_node, marketing_analysis_node,
    risk_analysis_node, coordinator_node, action_plan_node, emergency_pause_node, immediate_rollback_node
)
from src.graph.edges import route_after_data_analysis, route_after_risk, route_final
from src.utils.tracer import tracer  # NEW
from src.config import settings


def build_war_room_graph():
    """Build the complete war room workflow graph with tracing."""
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
    workflow.add_conditional_edges("data_analyst", route_after_data_analysis, {
        "pm_analysis": "pm_analysis", "immediate_rollback": "immediate_rollback", "emergency_pause": "emergency_pause"
    })
    workflow.add_edge("pm_analysis", "marketing_analysis")
    workflow.add_edge("marketing_analysis", "risk_analysis")
    workflow.add_conditional_edges("risk_analysis", route_after_risk, {
        "coordinator": "coordinator", "data_analyst": "data_analyst", "marketing_analysis": "marketing_analysis"
    })
    workflow.add_conditional_edges("coordinator", route_final, {
        "action_plan": "action_plan", "emergency_pause": "emergency_pause"
    })
    workflow.add_edge("action_plan", END)
    workflow.add_edge("emergency_pause", END)
    workflow.add_edge("immediate_rollback", END)
    
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def run_war_room(metrics, feedback, release_notes, thread_id: str = None):
    """Execute the war room workflow with full traceability."""
    settings.ensure_checkpoint_dir()
    
    # Initialize tracer
    run_id = thread_id or str(uuid.uuid4())[:8]
    tracer.start_trace(run_id, {
        "metrics_count": len(metrics),
        "feedback_count": len(feedback),
        "release_notes_length": len(release_notes)
    })
    
    graph = build_war_room_graph()
    
    initial_state = {
        "metrics": metrics, "feedback": feedback, "release_notes": release_notes,
        "data_analysis": None, "pm_analysis": None, "marketing_analysis": None, "risk_analysis": None,
        "anomaly_flags": [], "sentiment_summary": None, "risk_scores": [],
        "emergency_flag": False, "rollback_triggered": False, "requires_more_data": False,
        "data_requests": [], "final_decision": None, "execution_plan": None,
        "iteration_count": 0, "conversation_history": []
    }
    
    config = {"configurable": {"thread_id": run_id}}
    
    try:
        final_state = graph.invoke(initial_state, config)
        
        # Save trace
        trace_path = tracer.end_trace(final_state)
        print(f"\n[TRACER] Execution trace saved to: {trace_path}")
        
        if final_state.get("execution_plan"):
            return final_state["execution_plan"]
        elif final_state.get("final_decision"):
            return final_state["final_decision"]
        return None
        
    except Exception as e:
        tracer.log_tool_call("system", {}, str(e), error=str(e))
        trace_path = tracer.end_trace({"error": str(e)})
        print(f"\n[TRACER] Error trace saved to: {trace_path}")
        raise