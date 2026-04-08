"""Pydantic models for structured outputs."""

from typing import List, Dict, Optional, Literal, Any  # Added Any here
from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    """Individual risk register entry."""
    risk: str = Field(..., description="Description of the risk")
    severity: Literal["High", "Medium", "Low"] = Field(..., description="Risk severity level")
    mitigation: str = Field(..., description="Action to mitigate this risk")


class ActionItem(BaseModel):
    """Action item for next 24-48 hours."""
    action: str = Field(..., description="Specific action to take")
    owner: str = Field(..., description="Role responsible (PM, Data Analyst, etc.)")
    due_hours: int = Field(..., description="Due time in hours from now")


class MetricReference(BaseModel):
    """Metric with context."""
    value: str = Field(..., description="Current value")
    trend: str = Field(..., description="Trend direction")
    threshold_status: str = Field(..., description="Above/below threshold")


class LaunchDecision(BaseModel):
    """Final structured output schema."""
    decision: Literal["Proceed", "Pause", "Roll Back"] = Field(
        ..., description="Final go/no-go decision"
    )
    rationale: Dict[str, Any] = Field(  # ✅ Fixed: Changed 'any' to 'Any'
        ..., description="Structured rationale"
    )
    risk_register: List[RiskItem] = Field(
        default_factory=list, description="Identified risks"
    )
    action_plan: Dict[str, List[ActionItem]] = Field(
        ..., description="Actions for next 24-48 hours"
    )
    communication_plan: Dict[str, str] = Field(
        ..., description="Internal and external messaging"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in decision (0-1)"
    )
    what_would_increase_confidence: List[str] = Field(
        default_factory=list, description="Missing data that would improve confidence"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision": "Proceed",
                "confidence_score": 0.85
            }
        }


class AgentAnalysis(BaseModel):
    """Individual agent analysis output."""
    agent_role: str = Field(..., description="Role of the analyzing agent")
    summary: str = Field(..., description="Brief summary of findings")
    key_findings: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    risk_score: float = Field(0.0, ge=0.0, le=1.0)
    
    class Config:
        extra = "allow"