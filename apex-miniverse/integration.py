#!/usr/bin/env python3
"""
APEX Miniverse Integration
Sends heartbeat to Miniverse to show APEX agents in pixel world
"""

import os
import json
import time
import requests
from datetime import datetime
import threading

# Configuration
MINIVERSE_URL = "https://miniverse-public-production.up.railway.app"
STATE_FILE = os.path.expanduser("~/.apex/state.json")

# APEX Agents to visualize
AGENTS = {
    "vix-monitor": {"task": "Watching India VIX", "icon": "📊"},
    "regime-engine": {"task": "Analyzing market regime", "icon": "🎯"},
    "strategy-engine": {"task": "Generating options signals", "icon": "📈"},
    "risk-veto": {"task": "Validating trades", "icon": "🛡️"},
    "order-executor": {"task": "Executing trades", "icon": "💰"},
    "premarket-scanner": {"task": "Scanning news", "icon": "📰"},
    "weekend-scanner": {"task": "Weekend analysis", "icon": " weekend"},
    "health-monitor": {"task": "System health", "icon": "❤️"},
}

def get_agent_state(agent_name):
    """Determine agent state from state.json"""
    state = {}
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except:
        pass
    
    now = datetime.now()
    hour = now.hour
    
    # Determine state based on time and activity
    # Market hours: 9 AM - 4 PM IST Mon-Fri
    is_market_hours = 9 <= hour <= 15 and now.weekday() < 5
    
    if agent_name == "vix-monitor":
        if is_market_hours:
            return "working", "Watching VIX for regime signals"
        return "idle", "VIX monitoring paused"
    
    elif agent_name == "regime-engine":
        if is_market_hours:
            return "working", "Classifying market regime"
        return "idle", "Regime check complete"
    
    elif agent_name == "strategy-engine":
        if is_market_hours:
            return "working", "Generating options strategies"
        return "idle", "Strategy generation paused"
    
    elif agent_name == "risk-veto":
        if is_market_hours:
            return "working", "Validating trade risk"
        return "idle", "Risk monitoring paused"
    
    elif agent_name == "order-executor":
        # Check if there's activity
        positions = state.get("positions", [])
        if positions:
            return "working", f"Managing {len(positions)} positions"
        return "idle", "No open positions"
    
    elif agent_name == "premarket-scanner":
        if 7 <= hour <= 8 and now.weekday() < 5:
            return "working", "Scanning morning news"
        return "idle", "Waiting for pre-market"
    
    elif agent_name == "weekend-scanner":
        if now.weekday() >= 5:
            return "working", "Scanning weekend markets"
        return "sleeping", "Weekend scanner waiting"
    
    elif agent_name == "health-monitor":
        return "working", "Monitoring agent health"
    
    return "idle", "Ready"

def send_heartbeat(agent_name, info):
    """Send heartbeat to Miniverse"""
    state, task = get_agent_state(agent_name)
    
    payload = {
        "agent": f"apex-{agent_name}",
        "state": state,
        "task": f"{info['icon']} {task}"
    }
    
    try:
        url = f"{MINIVERSE_URL}/api/heartbeat"
        r = requests.post(url, json=payload, timeout=5)
        if r.status_code == 200:
            print(f"✅ {agent_name}: {state}")
        else:
            print(f"❌ {agent_name}: {r.status_code}")
    except Exception as e:
        print(f"❌ {agent_name}: {e}")

def run_heartbeat_loop():
    """Main loop to update all agents"""
    print("🚀 Starting APEX Miniverse Integration")
    print(f"📍 Server: {MINIVERSE_URL}")
    print("-" * 40)
    
    while True:
        for agent_name, info in AGENTS.items():
            send_heartbeat(agent_name, info)
        
        print("-" * 40)
        time.sleep(60)  # Update every minute

if __name__ == "__main__":
    # Run once for testing
    print("Testing APEX Miniverse Integration...")
    for agent_name, info in AGENTS.items():
        send_heartbeat(agent_name, info)
    
    print("\n✅ Setup complete!")
    print("\nTo run continuously:")
    print("  python3 integration.py")
    print("\nAgents will appear in Miniverse at:")
    print("  https://miniverse-public-production.up.railway.app")