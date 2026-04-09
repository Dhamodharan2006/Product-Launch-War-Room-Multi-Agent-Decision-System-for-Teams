"""Tools for sentiment analysis and feedback processing."""

import json
from typing import Dict, List, Any
from collections import Counter

try:
    from crewai.tools import tool
except ImportError:
    from langchain.tools import tool

from src.config import settings


@tool("Analyze feedback sentiment with keyword extraction")
def sentiment_analysis_tool(feedback_json: str) -> str:
    """
    Analyze feedback sentiment with keyword extraction.
    Aggregates sentiment by category and identifies top issues.
    """
    try:
        feedback = json.loads(feedback_json)
        
        sentiments = {"positive": [], "negative": [], "neutral": [], "outlier": []}
        keywords = {"positive": [], "negative": [], "themes": Counter()}
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
            
            words = text.split()
            stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}
            
            for word in words:
                clean = word.strip(".,!?;:\"'()").lower()
                if len(clean) > 3 and clean not in stopwords:
                    keywords["themes"][clean] += 1
        
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
            "critical_issues": [item for item in sentiments["negative"][:5]]
        }
        
        return json.dumps(summary, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("Cluster feedback using LLM-based semantic analysis")
def feedback_clustering_tool(feedback_json: str, use_llm: str = "true") -> str:
    """
    Cluster feedback by similar themes using LLM-based classification.
    Falls back to keyword matching if LLM is unavailable.
    """
    try:
        feedback = json.loads(feedback_json)
        
        # LLM-based clustering (NEW - replaces simple keyword matching)
        if use_llm.lower() == "true" and len(feedback) > 0:
            try:
                llm = settings.get_llm("marketing")
                
                # Prepare feedback for LLM analysis
                feedback_samples = [
                    {"id": f.get("id"), "text": f.get("text"), "category": f.get("category")}
                    for f in feedback[:20]  # Limit to avoid token limits
                ]
                
                prompt = f"""
                Analyze these user feedback entries and cluster them by semantic theme.
                Identify the primary issue categories and their severity.
                
                Feedback entries: {json.dumps(feedback_samples, indent=2)}
                
                Return JSON with this structure:
                {{
                    "clusters": {{
                        "crash_reports": {{"count": N, "severity": "High|Medium|Low", "sample_ids": ["id1", "id2"]}},
                        "payment_issues": {{"count": N, "severity": "...", "sample_ids": [...]}},
                        "ui_ux_issues": {{"count": N, "severity": "...", "sample_ids": [...]}},
                        "performance_issues": {{"count": N, "severity": "...", "sample_ids": [...]}},
                        "feature_requests": {{"count": N, "severity": "Low", "sample_ids": [...]}},
                        "positive_feedback": {{"count": N, "severity": "Low", "sample_ids": [...]}}
                    }},
                    "primary_concern": "name_of_most_severe_cluster",
                    "analysis_summary": "Brief 2-sentence summary of findings"
                }}
                
                Only return the JSON, no other text.
                """
                
                response = llm.invoke([
                    {"role": "system", "content": "You are a feedback analysis expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ])
                
                content = response.content if hasattr(response, 'content') else str(response)
                
                # Extract JSON from response
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                llm_result = json.loads(content.strip())
                
                # Validate and supplement with full counts
                clusters = llm_result.get("clusters", {})
                primary_concern = llm_result.get("primary_concern", "none")
                analysis_summary = llm_result.get("analysis_summary", "")
                
                # Ensure all clusters exist with counts
                for cluster_name in ["crash_reports", "payment_issues", "ui_ux_issues", "performance_issues", "feature_requests", "positive_feedback"]:
                    if cluster_name not in clusters:
                        clusters[cluster_name] = {"count": 0, "severity": "Low", "sample_ids": []}
                
                return json.dumps({
                    "clusters": clusters,
                    "primary_concern": primary_concern,
                    "analysis_summary": analysis_summary,
                    "clustering_method": "llm_semantic",
                    "total_analyzed": len(feedback)
                }, indent=2)
                
            except Exception as llm_error:
                # Fall back to keyword matching if LLM fails
                pass
        
        # FALLBACK: Keyword-based clustering (original method)
        clusters = {
            "crash_reports": [],
            "payment_issues": [],
            "ui_ux_issues": [],
            "performance_issues": [],
            "feature_requests": [],
            "positive_feedback": []
        }
        
        crash_keywords = ["crash", "freeze", "hang", "stopped", "error", "bug", "crashes", "crashing"]
        payment_keywords = ["payment", "checkout", "card", "billing", "charge", "failed", "transaction"]
        ui_keywords = ["confusing", "ui", "interface", "button", "find", "layout", "design", "settings", "navigation"]
        performance_keywords = ["slow", "loading", "lag", "speed", "performance", "latency", "stuck"]
        
        for item in feedback:
            text = item.get("text", "").lower()
            item_id = item.get("id")
            
            if any(kw in text for kw in crash_keywords):
                clusters["crash_reports"].append(item_id)
            elif any(kw in text for kw in payment_keywords):
                clusters["payment_issues"].append(item_id)
            elif any(kw in text for kw in ui_keywords):
                clusters["ui_ux_issues"].append(item_id)
            elif any(kw in text for kw in performance_keywords):
                clusters["performance_issues"].append(item_id)
            elif item.get("category") == "positive":
                clusters["positive_feedback"].append(item_id)
            else:
                clusters["feature_requests"].append(item_id)
        
        cluster_summary = {
            name: {
                "count": len(ids),
                "severity": "High" if len(ids) > 3 and name in ["crash_reports", "payment_issues"] else "Medium" if len(ids) > 0 else "Low",
                "sample_ids": ids[:3]
            }
            for name, ids in clusters.items()
        }
        
        # Determine primary concern
        primary = max(cluster_summary.items(), key=lambda x: x[1]["count"] if x[1]["severity"] in ["High", "Medium"] else 0)
        primary_concern = primary[0] if primary[1]["count"] > 0 else "none"
        
        return json.dumps({
            "clusters": cluster_summary,
            "primary_concern": primary_concern,
            "analysis_summary": f"Found {len(feedback)} feedback entries across {sum(1 for c in cluster_summary.values() if c['count'] > 0)} categories.",
            "clustering_method": "keyword_fallback",
            "total_analyzed": len(feedback),
            "llm_fallback_reason": "LLM unavailable or disabled" if use_llm.lower() == "true" else "LLM clustering disabled"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "clustering_method": "failed"})