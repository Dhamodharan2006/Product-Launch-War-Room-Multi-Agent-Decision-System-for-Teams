"""Data Analyst Agent implementation using LangChain."""

import json
from typing import Dict, Any

from src.agents.base import BaseAgent
from src.tools.metrics_tools import metric_aggregation_tool, anomaly_detection_tool
from src.tools.trend_tools import trend_comparison_tool


class DataAnalystAgent(BaseAgent):
    """Agent specialized in quantitative metrics analysis."""
    
    def __init__(self):
        super().__init__(
            role="Senior Data Analyst",
            goal="Analyze product metrics, detect anomalies, and provide data-driven insights for launch decisions",
            backstory="""You are a senior data analyst with 10 years of experience in SaaS metrics. 
            You specialize in statistical analysis, anomaly detection, and trend identification. 
            You are meticulous about data quality and always verify your calculations. 
            You communicate findings clearly with specific numbers and confidence intervals.""",
            config_key="data_analyst",
            tools=[metric_aggregation_tool, anomaly_detection_tool, trend_comparison_tool],
            verbose=True
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run full metrics analysis pipeline."""
        metrics = context.get("metrics", {})
        launch_day = context.get("launch_day", 7)
        
        metrics_json = json.dumps(metrics)
        
        # Run tools directly
        try:
            stats_result = metric_aggregation_tool.invoke({"metrics_json": metrics_json})
            stats = json.loads(stats_result)
        except Exception as e:
            stats = {"error": str(e), "statistics": {}, "anomalies": []}
        
        try:
            anomaly_result = anomaly_detection_tool.invoke({
                "metrics_json": metrics_json,
                "threshold_config": json.dumps({
                    "crash_rate": {"max": 2.0},
                    "api_latency_p95": {"max": 300},
                    "payment_success_rate": {"min": 97.0}
                })
            })
            anomalies = json.loads(anomaly_result)
        except Exception as e:
            anomalies = {"error": str(e), "violations": [], "critical_flags": []}
        
        try:
            trend_result = trend_comparison_tool.invoke({
                "metrics_json": metrics_json,
                "split_index": str(launch_day)
            })
            trends = json.loads(trend_result)
        except Exception as e:
            trends = {"error": str(e), "comparison": {}}
        
        # Check for critical conditions
        critical_crash = any(
            v.get("metric") == "crash_rate" and v.get("current", 0) > 5 
            for v in anomalies.get("violations", [])
        )
        
        # Generate summary using LLM
        analysis_prompt = f"""
        As a Data Analyst, provide a brief assessment of these metrics:
        
        Key Stats: Crash rate {stats.get('statistics', {}).get('crash_rate', {}).get('current', 'N/A')}%, 
        Activation {stats.get('statistics', {}).get('activation_rate', {}).get('current', 'N/A')}%
        
        Anomalies: {len(anomalies.get('anomalies', []))} detected
        Violations: {len(anomalies.get('violations', []))} threshold breaches
        
        Trends: {trends.get('summary', {})}
        
        Critical crash detected: {critical_crash}
        
        Provide a 2-sentence summary focusing on the most important findings.
        """
        
        summary = self.analyze_with_llm(analysis_prompt)
        
        return {
            "agent_role": "Data Analyst",
            "statistics": stats,
            "anomalies": anomalies,
            "trends": trends,
            "critical_findings": anomalies.get("critical_flags", []),
            "requires_rollback": critical_crash,
            "summary": summary,
            "key_findings": [
                f"Crash rate: {stats.get('statistics', {}).get('crash_rate', {}).get('current', 'N/A')}%",
                f"Anomalies: {len(anomalies.get('anomalies', []))}",
                f"Violations: {len(anomalies.get('violations', []))}"
            ],
            "recommendations": ["Investigate critical issues" if critical_crash else "Continue monitoring"],
            "risk_score": 0.8 if critical_crash else 0.3 if anomalies.get("total_anomalies", 0) > 2 else 0.1
        }