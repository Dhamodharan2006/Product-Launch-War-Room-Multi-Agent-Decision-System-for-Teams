"""Tools for risk assessment and scoring."""

import json
from typing import Dict, Any

try:
    from crewai.tools import tool
except ImportError:
    from crewai import tool


@tool("Calculate composite risk score")
def risk_scoring_tool(analysis_json: str) -> str:
    """
    Calculate composite risk score based on metrics, sentiment, and anomalies.
    Input: JSON string with keys: metrics_stats, sentiment, anomalies, violations
    """
    try:
        data = json.loads(analysis_json)
        
        score = 0.0
        risk_factors = []
        
        # Metric stability (30% weight)
        metrics = data.get("metrics_stats", {})
        if metrics:
            high_std = sum(1 for m in metrics.values() if m.get("std_dev", 0) > 5)
            if high_std > 2:
                score += 0.3
                risk_factors.append("High volatility in multiple metrics")
        
        # Crash rate (25% weight)
        violations = data.get("violations", [])
        critical_crash = any(v.get("metric") == "crash_rate" and v.get("current", 0) > 5 for v in violations)
        if critical_crash:
            score += 0.25
            risk_factors.append("Critical crash rate above 5%")
        elif any(v.get("metric") == "crash_rate" for v in violations):
            score += 0.15
            risk_factors.append("Elevated crash rate")
        
        # Sentiment (20% weight)
        sentiment = data.get("sentiment", {})
        neg_pct = sentiment.get("percentages", {}).get("negative", 0)
        if neg_pct > 40:
            score += 0.2
            risk_factors.append(f"High negative sentiment ({neg_pct}%)")
        elif neg_pct > 25:
            score += 0.1
            risk_factors.append(f"Moderate negative sentiment ({neg_pct}%)")
        
        # Anomaly count (15% weight)
        anomalies = data.get("anomalies", [])
        if len(anomalies) > 5:
            score += 0.15
            risk_factors.append(f"Multiple metric anomalies detected ({len(anomalies)})")
        elif len(anomalies) > 2:
            score += 0.08
            risk_factors.append("Some metric anomalies present")
        
        # Payment issues (10% weight)
        payment_fail = any(v.get("metric") == "payment_success_rate" for v in violations)
        if payment_fail:
            score += 0.1
            risk_factors.append("Payment processing issues")
        
        # Clamp to 0-1
        score = min(1.0, max(0.0, score))
        
        return json.dumps({
            "composite_risk_score": round(score, 2),
            "risk_level": "Critical" if score > 0.7 else "High" if score > 0.5 else "Medium" if score > 0.3 else "Low",
            "risk_factors": risk_factors,
            "recommendation": "Immediate rollback" if score > 0.7 else "Pause and investigate" if score > 0.5 else "Monitor closely" if score > 0.3 else "Proceed with monitoring"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("Assess rollback impact")
def rollback_impact_assessment_tool(metrics_json: str, feedback_json: str) -> str:
    """
    Assess the impact and feasibility of a rollback scenario.
    """
    try:
        metrics = json.loads(metrics_json)
        feedback = json.loads(feedback_json)
        
        # Analyze current state
        current_crash = metrics.get("crash_rate", [0])[-1]
        current_payment = metrics.get("payment_success_rate", [100])[-1]
        
        # Estimate user impact
        total_feedback = len(feedback)
        negative_count = sum(1 for f in feedback if f.get("category") == "negative")
        
        impact_score = 0
        
        # Data loss risk
        if current_payment < 98:
            impact_score += 20
        
        # User frustration
        if negative_count / max(1, total_feedback) > 0.3:
            impact_score += 30
        
        # Stability issues
        if current_crash > 3:
            impact_score += 40
        
        return json.dumps({
            "rollback_recommended": impact_score > 50 or current_crash > 5,
            "impact_score": impact_score,
            "estimated_downtime_minutes": 15,
            "data_loss_risk": "Low" if current_payment > 98 else "Medium",
            "user_impact": f"{negative_count} users reported issues",
            "alternative_actions": [
                "Feature flag disable" if current_crash > 3 else "Hotfix deployment",
                "Status page update",
                "Proactive customer communication"
            ]
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})