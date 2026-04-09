"""Integration tests for agent workflows."""

import pytest
from src.agents.data_analyst import DataAnalystAgent
from src.agents.product_manager import ProductManagerAgent
from src.agents.marketing import MarketingAgent
from src.agents.risk_critic import RiskCriticAgent


class TestDataAnalystAgent:
    """Test Data Analyst Agent integration."""
    
    def test_analyze_metrics(self):
        """Test full metric analysis pipeline."""
        agent = DataAnalystAgent()
        
        metrics = {
            "dates": ["2024-01-0{}".format(i) for i in range(1, 8)],
            "crash_rate": [1.0, 1.2, 1.1, 1.3, 1.0, 1.2, 1.1],
            "activation_rate": [45.0, 46.0, 44.0, 47.0, 45.0, 46.0, 48.0]
        }
        
        result = agent.analyze({"metrics": metrics, "launch_day": 3})
        
        assert "statistics" in result
        assert "anomalies" in result
        assert "summary" in result
        assert isinstance(result.get("risk_score"), (int, float))
        
    def test_critical_crash_detection(self):
        """Test detection of critical crash rates."""
        agent = DataAnalystAgent()
        
        metrics = {
            "dates": ["2024-01-0{}".format(i) for i in range(1, 8)],
            "crash_rate": [1.0, 1.2, 6.0, 1.1, 1.0, 1.2, 1.1],  # Day 3 has critical crash
            "activation_rate": [45.0] * 7
        }
        
        result = agent.analyze({"metrics": metrics, "launch_day": 3})
        
        assert result.get("requires_rollback") is True
        assert len(result.get("critical_findings", [])) > 0


class TestMarketingAgent:
    """Test Marketing Agent integration."""
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis pipeline."""
        agent = MarketingAgent()
        
        feedback = [
            {"id": "f{}".format(i), "text": "Great product!", "category": "positive", "sentiment_score": 0.8 + (i * 0.01), "user_segment": "pro", "source": "app_store", "timestamp": "2024-01-0{}".format(i+1)}
            for i in range(10)
        ] + [
            {"id": "f{}".format(i+10), "text": "App crashes", "category": "negative", "sentiment_score": 0.2, "user_segment": "free", "source": "support_ticket", "timestamp": "2024-01-{}".format(i+11)}
            for i in range(5)
        ]
        
        result = agent.analyze({"feedback": feedback, "metrics": {}})
        
        assert "sentiment_data" in result
        assert "issue_clusters" in result
        assert result.get("agent_role") == "Marketing/Comms"


class TestRiskCriticAgent:
    """Test Risk Critic Agent integration."""
    
    def test_risk_calculation(self):
        """Test comprehensive risk scoring."""
        agent = RiskCriticAgent()
        
        context = {
            "data_analysis": {
                "statistics": {"statistics": {"crash_rate": {"current": 2.5}}, "anomalies": []},
                "anomalies": {"violations": [{"metric": "crash_rate", "current": 2.5}]}
            },
            "marketing_analysis": {
                "sentiment_data": {"percentages": {"negative": 35}, "avg_sentiment_score": 0.4}
            },
            "pm_analysis": {"recommendations": ["Proceed with monitoring"]},
            "metrics": {"crash_rate": [2.5], "payment_success_rate": [96.0]},
            "feedback": [{"category": "negative", "text": "Issues"}] * 10
        }
        
        result = agent.analyze(context)
        
        assert "risk_assessment" in result
        assert "risk_score" in result
        assert isinstance(result.get("risk_score"), (int, float))
        assert result.get("risk_score") > 0.3  # Should detect elevated risk


if __name__ == "__main__":
    pytest.main([__file__, "-v"])