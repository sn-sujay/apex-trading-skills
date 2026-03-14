#!/usr/bin/env python3
"""
APEX Sentiment Engine - Event Publishing Version
Scrapes news and publishes sentiment events to event bus
"""

import json
import os
import sys
import random  # For demo - replace with actual scraping
from datetime import datetime

# Add orchestrator to path for event bus
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/trading/apex-core-orchestrator"))

try:
    from orchestrator import get_orchestrator
    HAS_ORCHESTRATOR = True
except:
    HAS_ORCHESTRATOR = False

def fetch_sentiment():
    """
    Fetch market sentiment from news sources
    Returns: {"score": float, "sources": dict, "headlines": list}
    """
    # TODO: Implement actual scraping:
    # - Economic Times
    # - MoneyControl
    # - Twitter/X API
    # - StockTwits
    
    # Mock implementation for now
    # In production, replace with real scraping logic
    
    headlines = [
        {"source": "Economic Times", "headline": "Market opens positive", "sentiment": 0.3},
        {"source": "MoneyControl", "headline": "FII buying continues", "sentiment": 0.4},
        {"source": "Twitter", "headline": "Nifty bullish trend", "sentiment": 0.2},
    ]
    
    # Calculate weighted sentiment
    total_sentiment = sum(h["sentiment"] for h in headlines)
    avg_sentiment = total_sentiment / len(headlines)
    
    return {
        "score": round(avg_sentiment, 2),  # -1.0 to +1.0
        "confidence": 65,
        "sources": {h["source"]: h["sentiment"] for h in headlines},
        "headlines": [h["headline"] for h in headlines],
        "fetched_at": datetime.now().isoformat()
    }

def analyze_sentiment_change(current, previous):
    """
    Determine if sentiment changed significantly
    Returns: {"significant": bool, "delta": float, "direction": str}
    """
    if previous is None:
        return {"significant": True, "delta": current, "direction": "initial"}
    
    delta = current - previous
    
    # Thresholds for significant change
    if abs(delta) > 0.3:  # 30% swing
        return {
            "significant": True,
            "delta": round(delta, 2),
            "direction": "extreme_positive" if delta > 0 else "extreme_negative"
        }
    elif abs(delta) > 0.15:  # 15% swing
        return {
            "significant": True,
            "delta": round(delta, 2),
            "direction": "positive" if delta > 0 else "negative"
        }
    
    return {"significant": False, "delta": round(delta, 2), "direction": "stable"}

def publish_sentiment_event(sentiment_data, change_analysis):
    """
    Publish sentiment event to event bus
    This alerts all subscribed agents
    """
    if not HAS_ORCHESTRATOR:
        print("[SENTIMENT] Orchestrator not available - storing in state only")
        return False
    
    try:
        orch = get_orchestrator()
        
        # Determine event type based on sentiment
        if sentiment_data["score"] < -0.5:
            event_type = "sentiment:extreme_negative"
            priority = "critical"
        elif sentiment_data["score"] < -0.3:
            event_type = "sentiment:negative"
            priority = "high"
        elif sentiment_data["score"] > 0.5:
            event_type = "sentiment:extreme_positive"
            priority = "high"
        elif sentiment_data["score"] > 0.3:
            event_type = "sentiment:positive"
            priority = "normal"
        else:
            event_type = "sentiment:neutral"
            priority = "low"
        
        # Publish event
        event = orch.event_bus.publish(
            event_type=event_type,
            payload={
                "sentiment_score": sentiment_data["score"],
                "confidence": sentiment_data["confidence"],
                "change": change_analysis,
                "sources": sentiment_data["sources"],
                "headlines": sentiment_data["headlines"]
            },
            source="apex-sentiment-engine",
            priority=priority
        )
        
        print(f"[SENTIMENT] Published event: {event_type} (score: {sentiment_data['score']})")
        return True
        
    except Exception as e:
        print(f"[SENTIMENT] Error publishing event: {e}")
        return False

def update_state(sentiment_data):
    """
    Update state.json with current sentiment
    """
    state_file = os.path.expanduser("~/.apex/state.json")
    
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
    except:
        state = {}
    
    # Store previous for comparison
    previous_sentiment = state.get("sentiment", {}).get("india_sentiment")
    
    # Update sentiment
    if "sentiment" not in state:
        state["sentiment"] = {}
    
    state["sentiment"]["india_sentiment"] = sentiment_data["score"]
    state["sentiment"]["confidence"] = sentiment_data["confidence"]
    state["sentiment"]["sources"] = sentiment_data["sources"]
    state["sentiment"]["headlines"] = sentiment_data["headlines"]
    state["sentiment"]["last_updated"] = sentiment_data["fetched_at"]
    state["sentiment"]["previous_sentiment"] = previous_sentiment
    
    # Save state
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    return previous_sentiment

def run_sentiment_engine():
    """
    Main function - fetch sentiment and publish events
    """
    print("="*70)
    print("APEX SENTIMENT ENGINE")
    print("="*70)
    
    # 1. Fetch current sentiment
    print("\n[1] Fetching sentiment from news sources...")
    sentiment = fetch_sentiment()
    print(f"    Score: {sentiment['score']} (confidence: {sentiment['confidence']}%)")
    print(f"    Headlines: {len(sentiment['headlines'])}")
    
    # 2. Update state
    print("\n[2] Updating state.json...")
    previous = update_state(sentiment)
    
    # 3. Analyze change
    print("\n[3] Analyzing sentiment change...")
    change = analyze_sentiment_change(sentiment["score"], previous)
    
    if change["significant"]:
        print(f"    ⚠️  SIGNIFICANT CHANGE DETECTED!")
        print(f"    Direction: {change['direction']}")
        print(f"    Delta: {change['delta']}")
    else:
        print(f"    Direction: {change['direction']} (delta: {change['delta']})")
    
    # 4. Publish event (NEW - this is the key addition!)
    print("\n[4] Publishing to event bus...")
    published = publish_sentiment_event(sentiment, change)
    
    if published:
        print("    ✅ Event published - other agents will respond")
    else:
        print("    ⚠️  Event not published - check orchestrator status")
    
    # 5. Generate alert if extreme
    if sentiment["score"] < -0.5:
        print("\n🚨 EXTREME NEGATIVE SENTIMENT!")
        print("   Risk veto should block new trades")
        print("   Stop losses should be tightened")
    elif sentiment["score"] > 0.5:
        print("\n✅ EXTREME POSITIVE SENTIMENT!")
        print("   Signal confidence boosted")
    
    print("\n" + "="*70)
    return sentiment


if __name__ == "__main__":
    run_sentiment_engine()
