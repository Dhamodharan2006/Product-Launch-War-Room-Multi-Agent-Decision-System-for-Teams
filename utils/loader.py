import json
from pathlib import Path
import pandas as pd

def load_from_tracer(path="outputs/tracer.json"):
    """Load and parse tracer.json into UI-friendly format."""
    try:
        if not Path(path).exists():
            return None
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        trace = data.get("execution_trace", [])
        if not trace:
            return None
            
        # Find trace_end event
        end_event = next((e for e in trace if e.get("event") == "trace_end"), None)
        if not end_event:
            return None
            
        final_state = end_event.get("final_state", {})
        start_event = next((e for e in trace if e.get("event") == "trace_start"), {})
        
        return {
            "metrics": final_state.get("metrics", {}),
            "feedback": final_state.get("feedback", []),
            "data_analysis": final_state.get("data_analysis", {}),
            "pm_analysis": final_state.get("pm_analysis", {}),
            "marketing_analysis": final_state.get("marketing_analysis", {}),
            "risk_analysis": final_state.get("risk_analysis", {}),
            "final_decision": final_state.get("final_decision", {}),
            "risk_scores": final_state.get("risk_scores", []),
            "run_id": start_event.get("run_id", "unknown"),
            "timestamp": end_event.get("timestamp", ""),
            "duration_ms": end_event.get("total_duration_ms", 0)
        }
    except Exception as e:
        print(f"Load error: {e}")
        return None

def extract_metrics_df(results):
    """Convert metrics dict to DataFrame."""
    metrics = results.get("metrics", {})
    if not metrics or "dates" not in metrics:
        return pd.DataFrame()
    
    df = pd.DataFrame(metrics)
    df['dates'] = pd.to_datetime(df['dates'])
    return df.set_index('dates')

def extract_feedback_df(results):
    """Convert feedback list to DataFrame."""
    feedback = results.get("feedback", [])
    if not feedback:
        return pd.DataFrame()
    return pd.DataFrame(feedback)