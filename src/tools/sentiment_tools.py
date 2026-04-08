"""Tools for sentiment analysis and feedback processing."""

import json
from typing import Dict, List, Any
from collections import Counter

try:
    from crewai.tools import tool
except ImportError:
    from crewai import tool


@tool("Analyze feedback sentiment with keyword extraction")
def sentiment_analysis_tool(feedback_json: str) -> str:
    """
    Analyze feedback sentiment with keyword extraction.
    Aggregates sentiment by category and identifies top issues.
    """
    try:
        feedback = json.loads(feedback_json)
        
        sentiments = {
            "positive": [],
            "negative": [],
            "neutral": [],
            "outlier": []
        }
        
        keywords = {
            "positive": [],
            "negative": [],
            "themes": Counter()
        }
        
        segment_sentiment = Counter()
        
        for item in feedback:
            category = item.get("category", "neutral")
            text = item.get("text", "").lower()
            score = item.get("sentiment_score", 0.5)
            segment = item.get("user_segment", "unknown")
            
            sentiments[category].append({
                "id": item.get("id"),
                "text": item.get("text"),
                "score": score
            })
            
            segment_sentiment[segment] += score
            
            # Extract keywords (simple approach)
            words = text.split()
            stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}
            
            for word in words:
                clean = word.strip(".,!?;:\"'()").lower()
                if len(clean) > 3 and clean not in stopwords:
                    keywords["themes"][clean] += 1
        
        # Calculate aggregations
        total = len(feedback)
        summary = {
            "total_feedback": total,
            "sentiment_distribution": {
                "positive": len(sentiments["positive"]),
                "negative": len(sentiments["negative"]),
                "neutral": len(sentiments.get("neutral", [])),
                "outlier": len(sentiments["outlier"])
            },
            "percentages": {
                "positive": round(len(sentiments["positive"]) / total * 100, 1) if total > 0 else 0,
                "negative": round(len(sentiments["negative"]) / total * 100, 1) if total > 0 else 0
            },
            "avg_sentiment_score": round(
                sum(item.get("sentiment_score", 0.5) for item in feedback) / total, 2
            ) if total > 0 else 0,
            "top_themes": dict(keywords["themes"].most_common(10)),
            "segment_breakdown": {
                seg: {
                    "count": sum(1 for f in feedback if f.get("user_segment") == seg),
                    "avg_sentiment": round(
                        sum(f.get("sentiment_score", 0.5) for f in feedback if f.get("user_segment") == seg) /
                        max(1, sum(1 for f in feedback if f.get("user_segment") == seg)), 2
                    )
                }
                for seg in set(f.get("user_segment", "unknown") for f in feedback)
            },
            "critical_issues": [
                item for item in sentiments["negative"][:5]
            ]
        }
        
        return json.dumps(summary, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("Cluster feedback by similar themes")
def feedback_clustering_tool(feedback_json: str) -> str:
    """
    Cluster feedback by similar themes to identify repeated issues.
    """
    try:
        feedback = json.loads(feedback_json)
        
        # Simple clustering by keyword matching
        clusters = {
            "crash_reports": [],
            "payment_issues": [],
            "ui_ux_complaints": [],
            "feature_requests": [],
            "positive_feedback": []
        }
        
        crash_keywords = ["crash", "freeze", "hang", "stopped", "error", "bug"]
        payment_keywords = ["payment", "checkout", "card", "billing", "charge", "failed"]
        ui_keywords = ["confusing", "ui", "interface", "button", "find", "layout", "design"]
        
        for item in feedback:
            text = item.get("text", "").lower()
            
            if any(kw in text for kw in crash_keywords):
                clusters["crash_reports"].append(item)
            elif any(kw in text for kw in payment_keywords):
                clusters["payment_issues"].append(item)
            elif any(kw in text for kw in ui_keywords):
                clusters["ui_ux_complaints"].append(item)
            elif item.get("category") == "positive":
                clusters["positive_feedback"].append(item)
            else:
                clusters["feature_requests"].append(item)
        
        cluster_summary = {
            name: {
                "count": len(items),
                "severity": "High" if len(items) > 3 and name in ["crash_reports", "payment_issues"] else "Medium" if len(items) > 0 else "Low",
                "sample_quotes": [i.get("text", "") for i in items[:3]]
            }
            for name, items in clusters.items()
        }
        
        return json.dumps({
            "clusters": cluster_summary,
            "total_clustered": sum(len(v) for v in clusters.values()),
            "primary_concern": max(clusters.items(), key=lambda x: len(x[1]))[0] if any(clusters.values()) else "none"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})