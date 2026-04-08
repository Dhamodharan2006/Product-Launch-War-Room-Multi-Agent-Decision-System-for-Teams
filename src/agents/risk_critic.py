"""Risk/Critic Agent implementation using LangChain."""

import json
from typing import Dict, Any, List

from src.agents.base import BaseAgent
from src.tools.risk_tools import risk_scoring_tool, rollback_impact_assessment_tool


class RiskCriticAgent(BaseAgent):
    """Agent for challenging assumptions and highlighting risks."""
    
    def __init__(self):
        super().__init__(
            role="Risk & Quality Assurance Lead",
            goal="Challenge assumptions, identify hidden risks, and demand evidence for all claims",
            backstory="""You are a risk management specialist with a background in quality assurance 
            and site reliability. You are naturally skeptical and ask hard questions.""",
            config_key="risk_critic",
            tools=[risk_scoring_tool, rollback_impact_assessment_tool],
            verbose=True
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Critique all analyses and calculate comprehensive risk score."""
        data_analysis = context.get("data_analysis", {})
        marketing_analysis = context.get("marketing_analysis", {})
        metrics = context.get("metrics", {})
        feedback = context.get("feedback", [])
        
        # Prepare inputs
        risk_input = {
            "metrics_stats": data_analysis.get("statistics", {}).get("statistics", {}),
            "sentiment": marketing_analysis.get("sentiment_data", {}),
            "anomalies": data_analysis.get("statistics", {}).get("anomalies", []),
            "violations": data_analysis.get("anomalies", {}).get("violations", [])
        }
        
        # Run tools
        try:
            risk_result = risk_scoring_tool.invoke({"analysis_json": json.dumps(risk_input)})
            risk_data = json.loads(risk_result)
        except Exception as e:
            risk_data = {"error": str(e), "composite_risk_score": 0.5, "risk_factors": []}
        
        try:
            rollback_result = rollback_impact_assessment_tool.invoke({
                "metrics_json": json.dumps(metrics),
                "feedback_json": json.dumps(feedback)
            })
            rollback_data = json.loads(rollback_result)
        except Exception as e:
            rollback_data = {"error": str(e), "rollback_recommended": False}
        
        # Identify challenges
        challenges = []
        if data_analysis.get("statistics", {}).get("total_anomalies", 0) > 3:
            challenges.append("Explain root cause of multiple anomalies")
        
        neg_pct = marketing_analysis.get("sentiment_data", {}).get("percentages", {}).get("negative", 0)
        if neg_pct > 25:
            challenges.append("Address high negative sentiment")
        
        # Generate summary using LLM
        prompt = f"""
        As Risk Lead, provide final assessment:
        
        Risk Score: {risk_data.get('composite_risk_score', 0)}
        Risk Level: {risk_data.get('risk_level', 'Unknown')}
        Rollback Recommended: {rollback_data.get('rollback_recommended', False)}
        
        Provide a 2-sentence risk assessment with final recommendation.
        """
        
        summary = self.analyze_with_llm(prompt)
        
        return {
            "agent_role": "Risk/Critic",
            "risk_assessment": risk_data,
            "rollback_analysis": rollback_data,
            "challenges_to_agents": challenges,
            "summary": summary,
            "key_findings": [f"Risk score: {risk_data.get('composite_risk_score', 0)}"],
            "concerns": risk_data.get("risk_factors", []) + challenges,
            "recommendations": [risk_data.get("recommendation", "Monitor")],
            "risk_score": risk_data.get("composite_risk_score", 0),
            "requires_more_data": len(challenges) > 0
        }