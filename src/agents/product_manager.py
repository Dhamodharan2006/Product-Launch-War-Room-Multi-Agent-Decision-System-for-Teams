"""Product Manager Agent implementation using LangChain."""

import json
from typing import Dict, Any

from src.agents.base import BaseAgent


class ProductManagerAgent(BaseAgent):
    """Agent for product strategy and go/no-go decisions."""
    
    def __init__(self):
        super().__init__(
            role="Senior Product Manager",
            goal="Define success criteria, assess user impact, and frame go/no-go recommendations",
            backstory="""You are a seasoned product manager who has led 20+ product launches. 
            You balance user needs with business goals. You are decisive but data-informed. 
            You focus on user impact, market positioning, and strategic alignment. 
            You frame decisions clearly with rationale and risk assessment.""",
            config_key="pm_orchestrator",
            tools=[],
            verbose=True
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess launch viability from product perspective."""
        data_analysis = context.get("data_analysis", {})
        sentiment_summary = context.get("sentiment_summary") or {}  # FIX: Handle None
        release_notes = context.get("release_notes", "")
        
        # Extract key data
        trends = data_analysis.get("trends", {}).get("comparison", {})
        critical = data_analysis.get("critical_findings", [])
        stats = data_analysis.get("statistics", {}).get("statistics", {})
        
        activation_trend = trends.get("activation_rate", {}).get("direction", "stable")
        adoption = stats.get("feature_adoption", {}).get("current", 0) if stats else 0
        
        # Use LLM for structured assessment
        prompt = f"""
        As a Product Manager, assess this product launch:
        
        Feature Adoption: {adoption}%
        Activation Trend: {activation_trend}
        Critical Issues: {len(critical)}
        Sentiment: {sentiment_summary.get('avg_sentiment_score', 'N/A')}/1.0
        
        Release Notes Context:
        {release_notes[:500]}
        
        Provide your assessment in 2-3 sentences focusing on whether to proceed, pause, or rollback.
        """
        
        summary = self.analyze_with_llm(prompt)
        
        # Build assessment
        concerns = []
        if activation_trend == "down":
            concerns.append("Activation rate declining post-launch")
        if adoption < 20:
            concerns.append("Feature adoption below 20% threshold")
        
        return {
            "agent_role": "Product Manager",
            "summary": summary,
            "key_findings": [
                f"New feature adoption: {adoption}%",
                f"User activation trend: {activation_trend}",
                f"Critical issues: {len(critical)}"
            ],
            "concerns": concerns,
            "recommendations": [
                "Proceed with enhanced monitoring" if not critical and len(concerns) < 2 else "Consider pausing for optimization"
            ],
            "success_criteria_met": adoption > 25 and activation_trend != "down",
            "risk_score": 0.3 if len(concerns) >= 2 else 0.15
        }