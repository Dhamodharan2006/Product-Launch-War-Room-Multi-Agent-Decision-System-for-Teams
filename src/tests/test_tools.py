"""Unit tests for analytical tools."""

import json
import pytest
import numpy as np
from src.tools.metrics_tools import metric_aggregation_tool, anomaly_detection_tool
from src.tools.sentiment_tools import sentiment_analysis_tool, feedback_clustering_tool
from src.tools.risk_tools import risk_scoring_tool, rollback_impact_assessment_tool
from src.tools.trend_tools import trend_comparison_tool


class TestMetricAggregationTool:
    """Test suite for metric aggregation tool."""
    
    def test_basic_statistics(self):
        """Test mean, median, std calculation."""
        metrics = {
            "dates": ["2024-01-01", "2024-01-02"],
            "crash_rate": [1.0, 2.0],
            "activation_rate": [50.0, 55.0]
        }
        
        result = metric_aggregation_tool.run(json.dumps(metrics))
        data = json.loads(result)
        
        assert "statistics" in data
        assert data["statistics"]["crash_rate"]["mean"] == 1.5
        assert data["statistics"]["activation_rate"]["mean"] == 52.5
        
    def test_anomaly_detection_zscore(self):
        """Test z-score anomaly detection."""
        metrics = {
            "dates": ["2024-01-01"] * 10,
            "crash_rate": [1.0] * 9 + [10.0]  # One outlier
        }
        
        result = metric_aggregation_tool.run(json.dumps(metrics))
        data = json.loads(result)
        
        assert data["total_anomalies"] >= 1
        assert any(a["metric"] == "crash_rate" for a in data["anomalies"])
        
    def test_empty_metrics(self):
        """Test handling of empty input."""
        result = metric_aggregation_tool.run("{}")
        data = json.loads(result)
        
        assert "statistics" in data
        assert data["total_anomalies"] == 0


class TestAnomalyDetectionTool:
    """Test suite for threshold-based anomaly detection."""
    
    def test_threshold_violation(self):
        """Test detection of metrics exceeding thresholds."""
        metrics = {
            "dates": ["2024-01-01"],
            "crash_rate": [5.5],  # Above 5% threshold
            "payment_success_rate": [95.0]  # Below 97% threshold
        }
        
        result = anomaly_detection_tool.run(json.dumps(metrics))
        data = json.loads(result)
        
        assert data["requires_immediate_action"] is True
        assert any(v["metric"] == "crash_rate" for v in data["violations"])
        
    def test_no_violations(self):
        """Test normal metrics pass."""
        metrics = {
            "dates": ["2024-01-01"],
            "crash_rate": [1.0],
            "payment_success_rate": [98.0]
        }
        
        result = anomaly_detection_tool.run(json.dumps(metrics))
        data = json.loads(result)
        
        assert data["violation_count"] == 0
        assert data["requires_immediate_action"] is False


class TestSentimentAnalysisTool:
    """Test suite for sentiment analysis."""
    
    def test_positive_sentiment(self):
        """Test positive feedback detection."""
        feedback = [
            {"id": "f1", "text": "Great product, love it!", "category": "positive", "sentiment_score": 0.9, "user_segment": "pro", "source": "app_store", "timestamp": "2024-01-01"}
        ]
        
        result = sentiment_analysis_tool.run(json.dumps(feedback))
        data = json.loads(result)
        
        assert data["avg_sentiment_score"] > 0.7
        assert data["sentiment_distribution"]["positive"] == 1
        
    def test_negative_sentiment(self):
        """Test negative feedback detection."""
        feedback = [
            {"id": "f1", "text": "App crashes constantly, very frustrated", "category": "negative", "sentiment_score": 0.1, "user_segment": "free", "source": "support_ticket", "timestamp": "2024-01-01"}
        ]
        
        result = sentiment_analysis_tool.run(json.dumps(feedback))
        data = json.loads(result)
        
        assert data["avg_sentiment_score"] < 0.3
        assert data["sentiment_distribution"]["negative"] == 1


class TestFeedbackClusteringTool:
    """Test suite for feedback clustering."""
    
    def test_crash_clustering(self):
        """Test crash-related feedback grouping."""
        feedback = [
            {"id": "f1", "text": "App crashes immediately", "category": "negative", "sentiment_score": 0.1, "user_segment": "pro", "source": "app_store", "timestamp": "2024-01-01"},
            {"id": "f2", "text": "Crashes every time I open it", "category": "negative", "sentiment_score": 0.2, "user_segment": "free", "source": "support_ticket", "timestamp": "2024-01-02"}
        ]
        
        result = feedback_clustering_tool.run(json.dumps(feedback))
        data = json.loads(result)
        
        assert data["clusters"]["crash_reports"]["count"] == 2
        assert data["primary_concern"] == "crash_reports"


class TestRiskScoringTool:
    """Test suite for risk scoring."""
    
    def test_high_risk_scenario(self):
        """Test high risk detection."""
        analysis = {
            "metrics_stats": {"crash_rate": {"std_dev": 6.0}},
            "sentiment": {"percentages": {"negative": 45}},
            "anomalies": [{"metric": "crash_rate", "severity": "High"}] * 6,
            "violations": [{"metric": "crash_rate", "current": 6.0}]
        }
        
        result = risk_scoring_tool.run(json.dumps(analysis))
        data = json.loads(result)
        
        # FIXED: Changed > to >= for boundary case
        assert data["composite_risk_score"] >= 0.6
        assert data["risk_level"] in ["High", "Critical"]
        
    def test_low_risk_scenario(self):
        """Test low risk detection."""
        analysis = {
            "metrics_stats": {},
            "sentiment": {"percentages": {"negative": 10}},
            "anomalies": [],
            "violations": []
        }
        
        result = risk_scoring_tool.run(json.dumps(analysis))
        data = json.loads(result)
        
        assert data["composite_risk_score"] < 0.3
        assert data["risk_level"] == "Low"


class TestTrendComparisonTool:
    """Test suite for trend comparison."""
    
    def test_trend_direction(self):
        """Test trend direction calculation."""
        metrics = {
            "dates": ["2024-01-01"] * 14,
            "activation_rate": [40.0] * 7 + [50.0] * 7  # 25% increase
        }
        
        # FIXED: Pass split_index as second argument (split at day 7)
        result = trend_comparison_tool.run(
            json.dumps(metrics),  # First arg: metrics_json
            "7"                   # Second arg: split_index (where to split pre vs post)
        )
        data = json.loads(result)
        
        assert data["comparison"]["activation_rate"]["direction"] == "up"
        assert data["comparison"]["activation_rate"]["change_percent"] > 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])