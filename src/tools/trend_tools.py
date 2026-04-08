"""Tools for trend analysis and comparison."""

import json
import numpy as np
from typing import Dict, Any

try:
    from crewai.tools import tool
except ImportError:
    from crewai import tool


@tool("Compare pre vs post launch metrics")
def trend_comparison_tool(metrics_json: str, split_index: str) -> str:
    """
    Compare pre vs post launch metrics.
    split_index: Index where launch occurred (string number)
    """
    try:
        metrics = json.loads(metrics_json)
        split = int(split_index)
        
        comparison = {}
        
        for key, values in metrics.items():
            if key == "dates" or not isinstance(values, list):
                continue
            
            pre = values[:split]
            post = values[split:]
            
            if not pre or not post:
                continue
            
            pre_mean = np.mean(pre)
            post_mean = np.mean(post)
            change = ((post_mean - pre_mean) / pre_mean * 100) if pre_mean != 0 else 0
            
            comparison[key] = {
                "pre_launch_avg": round(float(pre_mean), 2),
                "post_launch_avg": round(float(post_mean), 2),
                "change_percent": round(float(change), 2),
                "direction": "up" if change > 5 else "down" if change < -5 else "stable"
            }
        
        return json.dumps({
            "comparison": comparison,
            "summary": {
                "improved": sum(1 for v in comparison.values() if v["direction"] == "up"),
                "degraded": sum(1 for v in comparison.values() if v["direction"] == "down"),
                "stable": sum(1 for v in comparison.values() if v["direction"] == "stable")
            }
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("Analyze metric volatility")
def volatility_analysis_tool(metrics_json: str, window: str = "3") -> str:
    """
    Analyze metric volatility using rolling standard deviation.
    window: Rolling window size (default 3 days)
    """
    try:
        metrics = json.loads(metrics_json)
        win = int(window)
        
        volatility_report = {}
        
        for key, values in metrics.items():
            if key == "dates" or not isinstance(values, list) or len(values) < win:
                continue
            
            arr = np.array(values, dtype=float)
            
            # Calculate rolling std
            rolling_std = []
            for i in range(len(arr) - win + 1):
                window_data = arr[i:i+win]
                rolling_std.append(float(np.std(window_data)))
            
            volatility_report[key] = {
                "avg_volatility": round(float(np.mean(rolling_std)), 3),
                "max_volatility": round(float(np.max(rolling_std)), 3),
                "volatility_trend": "increasing" if rolling_std[-1] > rolling_std[0] else "decreasing",
                "stability_score": round(1.0 / (1.0 + float(np.mean(rolling_std))), 2)
            }
        
        return json.dumps({
            "volatility_by_metric": volatility_report,
            "most_volatile": max(volatility_report.items(), key=lambda x: x[1]["avg_volatility"])[0] if volatility_report else "none",
            "assessment": "High volatility detected" if any(v["avg_volatility"] > 5 for v in volatility_report.values()) else "Metrics stable"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})