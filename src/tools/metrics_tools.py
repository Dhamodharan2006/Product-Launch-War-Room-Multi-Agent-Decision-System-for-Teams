"""Tools for metric analysis and anomaly detection."""

import json
import numpy as np
from typing import Dict, List, Any

# Use CrewAI's tool decorator instead of LangChain's
try:
    from crewai.tools import tool
except ImportError:
    from crewai import tool


@tool("Calculate metric statistics and detect anomalies")
def metric_aggregation_tool(metrics_json: str) -> str:
    """
    Calculate statistical aggregations (mean, median, std) for metrics.
    Detects anomalies using z-score method.
    """
    try:
        metrics = json.loads(metrics_json)
        results = {}
        anomalies = []
        
        metric_keys = [k for k in metrics.keys() if k not in ["dates"]]
        
        for key in metric_keys:
            values = metrics[key]
            if not values or not isinstance(values, list):
                continue
                
            arr = np.array(values, dtype=float)
            mean = float(np.mean(arr))
            median = float(np.median(arr))
            std = float(np.std(arr))
            
            # Z-score anomaly detection (|z| > 2)
            z_scores = np.abs((arr - mean) / std) if std > 0 else np.zeros_like(arr)
            anomaly_indices = np.where(z_scores > 2)[0]
            
            if len(anomaly_indices) > 0:
                for idx in anomaly_indices:
                    anomalies.append({
                        "metric": key,
                        "date": metrics["dates"][idx] if "dates" in metrics and idx < len(metrics["dates"]) else f"index_{idx}",
                        "value": float(arr[idx]),
                        "z_score": float(z_scores[idx]),
                        "severity": "High" if z_scores[idx] > 3 else "Medium"
                    })
            
            # Trend calculation (last 3 days vs first 3 days)
            if len(arr) >= 6:
                recent = np.mean(arr[-3:])
                early = np.mean(arr[:3])
                trend = ((recent - early) / early) * 100 if early != 0 else 0
            else:
                trend = 0
            
            results[key] = {
                "mean": round(mean, 2),
                "median": round(median, 2),
                "std_dev": round(std, 2),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "trend_percent": round(trend, 2),
                "current": float(arr[-1]) if len(arr) > 0 else 0
            }
        
        output = {
            "statistics": results,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies)
        }
        
        return json.dumps(output, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("Detect threshold violations in metrics")
def anomaly_detection_tool(metrics_json: str, threshold_config: str = "{}") -> str:
    """
    Identify metric deviations from business thresholds.
    threshold_config: JSON string mapping metric names to {'min': x, 'max': y}
    """
    try:
        metrics = json.loads(metrics_json)
        thresholds = json.loads(threshold_config) if threshold_config else {}
        
        default_thresholds = {
            "crash_rate": {"max": 2.0},
            "api_latency_p95": {"max": 300},
            "payment_success_rate": {"min": 97.0},
            "activation_rate": {"min": 40.0},
            "churn_rate": {"max": 6.0}
        }
        default_thresholds.update(thresholds)
        
        violations = []
        critical_metrics = []
        
        for metric, bounds in default_thresholds.items():
            if metric not in metrics or not isinstance(metrics[metric], list):
                continue
            
            values = metrics[metric]
            current = values[-1] if values else 0
            
            if "min" in bounds and current < bounds["min"]:
                violations.append({
                    "metric": metric,
                    "type": "below_minimum",
                    "current": current,
                    "threshold": bounds["min"],
                    "severity": "Critical" if metric in ["crash_rate", "payment_success_rate"] else "Warning"
                })
                if metric == "crash_rate" and current > 5.0:
                    critical_metrics.append(f"Critical crash rate: {current}%")
            
            if "max" in bounds and current > bounds["max"]:
                violations.append({
                    "metric": metric,
                    "type": "above_maximum",
                    "current": current,
                    "threshold": bounds["max"],
                    "severity": "Critical" if metric in ["crash_rate"] else "Warning"
                })
                if metric == "crash_rate":
                    critical_metrics.append(f"Critical crash rate: {current}%")
        
        return json.dumps({
            "violations": violations,
            "violation_count": len(violations),
            "critical_flags": critical_metrics,
            "requires_immediate_action": len(critical_metrics) > 0
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})