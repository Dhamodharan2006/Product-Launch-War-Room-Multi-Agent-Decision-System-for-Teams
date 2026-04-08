"""Generate realistic mock data for the war room simulation."""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json


def generate_metrics(days: int = 14) -> Dict[str, List[Any]]:
    """Generate realistic post-launch metrics with dip and recovery pattern."""
    base_date = datetime.now() - timedelta(days=days)
    
    metrics = {
        "dates": [],
        "activation_rate": [],      # % signup to activation
        "dau_wau_ratio": [],        # Daily/Weekly active ratio
        "d1_retention": [],         # Day 1 retention %
        "d7_retention": [],         # Day 7 retention %
        "crash_rate": [],           # % sessions crashed
        "api_latency_p95": [],      # milliseconds
        "payment_success_rate": [], # %
        "support_ticket_volume": [], # count
        "feature_adoption": [],     # % completing new feature
        "churn_rate": []            # % churned
    }
    
    # Launch was on day 7 (index 7)
    launch_idx = 7
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        metrics["dates"].append(date.isoformat())
        
        # Launch day dip pattern
        launch_factor = 1.0
        if i == launch_idx:
            launch_factor = 0.85  # 15% dip on launch day
        elif i == launch_idx + 1:
            launch_factor = 0.90
        elif i > launch_idx + 1:
            launch_factor = 0.95 + (0.05 * (i - launch_idx) / 7)  # Gradual recovery
        
        # Generate metrics with realistic noise
        metrics["activation_rate"].append(round(random.uniform(45, 55) * launch_factor, 2))
        metrics["dau_wau_ratio"].append(round(random.uniform(0.4, 0.6) * launch_factor, 3))
        metrics["d1_retention"].append(round(random.uniform(35, 45) * launch_factor, 2))
        metrics["d7_retention"].append(round(random.uniform(20, 30) * launch_factor, 2))
        
        # Crash rate spike on day 8 (bug discovered)
        if i == launch_idx + 1:
            crash = random.uniform(4.5, 5.5)  # Critical threshold crossed
        else:
            crash = random.uniform(0.5, 2.0)
        metrics["crash_rate"].append(round(crash, 2))
        
        metrics["api_latency_p95"].append(int(random.uniform(120, 250)))
        metrics["payment_success_rate"].append(round(random.uniform(96, 99.5), 2))
        metrics["support_ticket_volume"].append(int(random.uniform(50, 150) * (2.0 if i >= launch_idx else 1.0)))
        metrics["feature_adoption"].append(round(random.uniform(15, 35) * launch_factor, 2))
        metrics["churn_rate"].append(round(random.uniform(2, 5) * (1.2 if i >= launch_idx else 1.0), 2))
    
    return metrics


def generate_feedback(count: int = 35) -> List[Dict[str, Any]]:
    """Generate mixed user feedback with repeated issues."""
    base_date = datetime.now() - timedelta(days=7)
    
    positive_templates = [
        "Love the new {feature}! Makes my workflow so much faster.",
        "Great update, the {feature} is exactly what we needed.",
        "Finally! Been waiting for {feature} for months.",
        "UI is much cleaner now. Good job team.",
        "Performance feels snappier after the update.",
        "The new {feature} integration works perfectly with our stack.",
    ]
    
    negative_templates = [
        "Crashes every time I try to use {feature} on mobile.",
        "Can't complete checkout, payment keeps failing.",
        "UI is confusing, can't find the {feature} settings.",
        "Extremely slow loading times today.",
        "Getting constant 500 errors when accessing {feature}.",
        "The new layout is counterintuitive.",
    ]
    
    outlier_templates = [
        "Can you add blockchain support to {feature}?",
        "Would be great if it integrated with my smart fridge.",
        "Need ASCII art export functionality urgently.",
    ]
    
    feedback = []
    categories = ["positive"] * 21 + ["negative"] * 11 + ["outlier"] * 3
    
    # Ensure 3 repeated issues (crash, payment, confusion)
    repeated_issues = [
        {"text": "App crashes immediately when opening dashboard after update", "category": "negative", "issue_type": "crash"},
        {"text": "Payment failed three times, lost my cart", "category": "negative", "issue_type": "payment"},
        {"text": "Where did the export button go? Can't find it anywhere", "category": "negative", "issue_type": "ux_confusion"},
    ]
    
    # Add repeated issues multiple times
    for issue in repeated_issues:
        for _ in range(2):  # Each appears twice
            feedback.append({
                "id": f"fb_{len(feedback)}",
                "timestamp": (base_date + timedelta(hours=random.randint(0, 168))).isoformat(),
                "user_segment": random.choice(["enterprise", "pro", "free"]),
                "text": issue["text"],
                "category": issue["category"],
                "sentiment_score": random.uniform(0.1, 0.3) if issue["category"] == "negative" else random.uniform(0.7, 0.9),
                "source": random.choice(["app_store", "support_ticket", "in_app"])
            })
    
    # Fill remaining slots
    remaining = count - len(feedback)
    for i in range(remaining):
        cat = random.choice(categories)
        feature = "dashboard"
        
        if cat == "positive":
            text = random.choice(positive_templates).format(feature=feature)
            sentiment = random.uniform(0.7, 0.95)
        elif cat == "negative":
            text = random.choice(negative_templates).format(feature=feature)
            sentiment = random.uniform(0.1, 0.4)
        else:
            text = random.choice(outlier_templates).format(feature=feature)
            sentiment = random.uniform(0.4, 0.6)
        
        feedback.append({
            "id": f"fb_{len(feedback)}",
            "timestamp": (base_date + timedelta(hours=random.randint(0, 168))).isoformat(),
            "user_segment": random.choice(["enterprise", "pro", "free"]),
            "text": text,
            "category": cat,
            "sentiment_score": round(sentiment, 2),
            "source": random.choice(["app_store", "support_ticket", "in_app"])
        })
    
    return sorted(feedback, key=lambda x: x["timestamp"])


def generate_release_notes() -> str:
    """Generate realistic release notes."""
    return """
# Release v2.4.0 - Advanced Analytics Dashboard

## New Features
- **Real-time Analytics Dashboard**: Live metrics visualization with customizable widgets
- **Export API v2**: New REST endpoints for bulk data export with CSV/JSON support
- **Enhanced Mobile Experience**: Responsive redesign of core workflows

## Technical Changes
- Database migration to PostgreSQL 15
- Updated authentication middleware
- New caching layer implementation (Redis)

## Known Risks (Pre-Launch)
- ⚠️ Database migration may cause temporary latency spikes
- ⚠️ Mobile responsive changes untested on Android 12
- ⚠️ Export API rate limits not yet stress-tested

## Rollback Procedure
1. Revert DNS to v2.3.9 cluster
2. Execute rollback script: `./scripts/rollback-v2.4.sh`
3. Notify users via status page
4. Estimated downtime: 15 minutes
"""


def save_mock_data(output_dir: str = "./outputs"):
    """Generate and save all mock data."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    metrics = generate_metrics()
    feedback = generate_feedback()
    release_notes = generate_release_notes()
    
    # FIX: Added encoding='utf-8' to handle Unicode characters (emojis)
    with open(f"{output_dir}/metrics.json", "w", encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    
    with open(f"{output_dir}/feedback.json", "w", encoding='utf-8') as f:
        json.dump(feedback, f, indent=2)
    
    with open(f"{output_dir}/release_notes.txt", "w", encoding='utf-8') as f:
        f.write(release_notes)
    
    return metrics, feedback, release_notes