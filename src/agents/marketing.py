"""Marketing/Comms Agent implementation using LangChain."""

import json
from typing import Dict, Any, List

from src.agents.base import BaseAgent
from src.tools.sentiment_tools import sentiment_analysis_tool, feedback_clustering_tool


class MarketingAgent(BaseAgent):
    """Agent for customer perception and communication strategy."""
    
    def __init__(self):
        super().__init__(
            role="Marketing & Communications Lead",
            goal="Assess customer perception, brand impact, and develop communication strategies",
            backstory="""You are a marketing leader with expertise in crisis communications 
            and brand management. You understand how technical issues translate to customer 
            perception. You craft messaging that is transparent yet reassuring.""",
            config_key="marketing",
            tools=[sentiment_analysis_tool, feedback_clustering_tool],
            verbose=True
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer perception and sentiment."""
        feedback = context.get("feedback", [])
        
        feedback_json = json.dumps(feedback)
        
        # Run tools directly
        try:
            sentiment_result = sentiment_analysis_tool.invoke({"feedback_json": feedback_json})
            sentiment = json.loads(sentiment_result)
        except Exception as e:
            sentiment = {"error": str(e), "avg_sentiment_score": 0.5, "percentages": {"negative": 0}}
        
        try:
            clustering_result = feedback_clustering_tool.invoke({"feedback_json": feedback_json})
            clusters = json.loads(clustering_result)
        except Exception as e:
            clusters = {"error": str(e), "primary_concern": "none"}
        
        neg_pct = sentiment.get("percentages", {}).get("negative", 0)
        primary_concern = clusters.get("primary_concern", "none")
        
        # Generate summary using LLM
        prompt = f"""
        As Marketing Lead, assess customer perception:
        
        Sentiment Score: {sentiment.get('avg_sentiment_score', 0)}/1.0
        Negative Feedback: {neg_pct}%
        Primary Concern: {primary_concern}
        Total Feedback: {sentiment.get('total_feedback', 0)}
        
        Provide a 2-sentence assessment with recommended communication strategy.
        """
        
        summary = self.analyze_with_llm(prompt)
        
        return {
            "agent_role": "Marketing/Comms",
            "sentiment_data": sentiment,
            "issue_clusters": clusters,
            "summary": summary,
            "key_findings": [
                f"Sentiment: {sentiment.get('avg_sentiment_score', 0)}/1.0",
                f"Negative: {neg_pct}%",
                f"Primary concern: {primary_concern}"
            ],
            "concerns": [f"High negative sentiment ({neg_pct}%)"] if neg_pct > 30 else [],
            "recommendations": ["Proactive communication" if neg_pct > 20 else "Standard monitoring"],
            "communication_urgency": "High" if neg_pct > 30 else "Normal",
            "risk_score": 0.4 if neg_pct > 30 else 0.2 if neg_pct > 20 else 0.1
        }