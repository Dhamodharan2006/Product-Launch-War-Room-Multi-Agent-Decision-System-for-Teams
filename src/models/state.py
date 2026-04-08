"""LangGraph state definitions."""

from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
import operator


class WarRoomState(TypedDict):
    """State schema for the Product Launch War Room."""
    
    # Input Data
    metrics: Dict[str, Any]  # Time series metrics
    feedback: List[Dict[str, Any]]  # User feedback entries
    release_notes: str  # Release documentation
    
    # Analysis Results
    data_analysis: Optional[Dict[str, Any]]
    pm_analysis: Optional[Dict[str, Any]]
    marketing_analysis: Optional[Dict[str, Any]]
    risk_analysis: Optional[Dict[str, Any]]
    
    # Aggregated insights
    anomaly_flags: Annotated[List[str], operator.add]
    sentiment_summary: Optional[Dict[str, Any]]
    risk_scores: Annotated[List[float], operator.add]
    
    # Decision flow control
    emergency_flag: bool
    rollback_triggered: bool
    requires_more_data: bool
    data_requests: Annotated[List[str], operator.add]
    
    # Final output
    final_decision: Optional[Dict[str, Any]]
    execution_plan: Optional[Dict[str, Any]]
    
    # Metadata
    iteration_count: int
    conversation_history: Annotated[List[Dict[str, str]], operator.add]