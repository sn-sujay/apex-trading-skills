#!/usr/bin/env python3
"""
APEX Agent Dashboard
Simple terminal dashboard showing all APEX agent status
"""

import os
import json
import time
from datetime import datetime
import pytz

STATE_FILE = os.path.expanduser("~/.apex/state.json")
IST = pytz.timezone("Asia/Kolkata")

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}

def get_agent_status(state):
    """Get status of all APEX agents"""
    now = datetime.now(IST)
    hour = now.hour
    weekday = now.weekday()
    is_weekend = weekday >= 5
    is_market_hours = 9 <= hour <= 15 and not is_weekend
    
    agents = []
    
    # Weekend Scanner
    if is_weekend:
        ws = state.get("weekend_scan", {})
        if ws.get("data_fresh"):
            agents.append({
                "name": "📡 Weekend Scanner",
                "status": "working",
                "task": f"Outlook: {ws.get('next_week_outlook', 'NEUTRAL')}",
                "last": ws.get("last_scan", "Never")[:19] if isinstance(ws.get("last_scan"), str) else "Never"
            })
        else:
            agents.append({
                "name": "📡 Weekend Scanner",
                "status": "idle",
                "task": "Waiting for weekend",
                "last": "N/A"
            })
    else:
        ws = state.get("weekend_scan", {})
        if ws.get("last_scan"):
            agents.append({
                "name": "📡 Weekend Scanner",
                "status": "idle",
                "task": f"Last: {ws.get('next_week_outlook', 'N/A')}",
                "last": ws.get("last_scan", "Never")[:19] if isinstance(ws.get("last_scan"), str) else "N/A"
            })
    
    # Pre-Market Briefing
    pm = state.get("pre_market_briefing", {})
    if pm.get("generated_at"):
        agents.append({
            "name": "📰 Pre-Market",
            "status": "working",
            "task": f"Strategy: {pm.get('today_stance', 'NEUTRAL')} | Risk: {pm.get('risk_level', 'N/A')}",
            "last": pm.get("generated_at", "Never")[:19] if isinstance(pm.get("generated_at"), str) else "N/A"
        })
    else:
        agents.append({
            "name": "📰 Pre-Market",
            "status": "waiting" if 7 <= hour <= 8 and not is_weekend else "idle",
            "task": "Waiting for 8 AM" if 7 <= hour <= 8 and not is_weekend else "Waiting for next day",
            "last": "N/A"
        })
    
    # VIX Monitor
    vix = state.get("india_vix", {})
    if isinstance(vix, dict) and vix.get("current"):
        agents.append({
            "name": "📊 VIX Monitor",
            "status": "working" if is_market_hours else "idle",
            "task": f"VIX: {vix.get('current', 'N/A')} ({vix.get('change', 0):+.2f}%)",
            "last": vix.get("timestamp", "Never")[:19] if isinstance(vix.get("timestamp"), str) else "N/A"
        })
    else:
        agents.append({
            "name": "📊 VIX Monitor",
            "status": "idle",
            "task": "Waiting for data",
            "last": "Never"
        })
    
    # Market Regime
    regime = state.get("market_regime", "")
    if regime:
        agents.append({
            "name": "🎯 Regime Engine",
            "status": "working" if is_market_hours else "idle",
            "task": f"Regime: {regime}",
            "last": state.get("last_regime_update", "Never")[:19] if state.get("last_regime_update") else "N/A"
        })
    else:
        agents.append({
            "name": "🎯 Regime Engine",
            "status": "idle",
            "task": "Waiting for classification",
            "last": "Never"
        })
    
    # Sentiment
    sentiment = state.get("sentiment", {})
    if isinstance(sentiment, dict) and sentiment.get("label"):
        agents.append({
            "name": "😊 Sentiment Engine",
            "status": "working" if is_market_hours else "idle",
            "task": f"Sentiment: {sentiment.get('label', 'NEUTRAL')} ({sentiment.get('confidence', 0)}%)",
            "last": sentiment.get("last_updated", "Never")[:19] if isinstance(sentiment.get("last_updated"), str) else "N/A"
        })
    
    # Positions
    positions = state.get("positions", [])
    agents.append({
        "name": "💰 Order Executor",
        "status": "working" if positions else "idle",
        "task": f"{len(positions)} open positions",
        "last": "N/A"
    })
    
    # P&L
    pnl = state.get("daily_pnl", {})
    pnl_val = pnl.get("realized", 0)
    agents.append({
        "name": "📈 Performance",
        "status": "working",
        "task": f"P&L: ₹{pnl_val:,.0f} | Trades: {pnl.get('trades_today', 0)}",
        "last": pnl.get("date", "N/A")
    })
    
    # Kill Switch
    ks = state.get("kill_switch", False)
    agents.append({
        "name": "🛡️ Risk Veto",
        "status": "idle" if not ks else "error",
        "task": f"Kill Switch: {'ACTIVE' if ks else 'OFF'}",
        "last": "N/A"
    })
    
    return agents

def print_dashboard():
    """Print the dashboard"""
    state = load_state()
    now = datetime.now(IST)
    
    print("\n" + "=" * 60)
    print(f"  APEX TRADING AGENTS - {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 60)
    
    agents = get_agent_status(state)
    
    status_icons = {
        "working": "🟢",
        "idle": "⚪",
        "waiting": "🟡",
        "error": "🔴",
        "sleeping": "💤"
    }
    
    for agent in agents:
        icon = status_icons.get(agent["status"], "⚪")
        print(f"\n{icon} {agent['name']}")
        print(f"   Task: {agent['task']}")
        print(f"   Last: {agent['last']}")
    
    print("\n" + "-" * 60)
    print(f"Weekend Scan: {state.get('weekend_scan', {}).get('next_week_outlook', 'N/A')}")
    print(f"Today's Strategy: {state.get('pre_market_briefing', {}).get('today_stance', 'N/A')}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        # Watch mode - refresh every 5 seconds
        while True:
            print("\033[2J\033[H")  # Clear screen
            print_dashboard()
            time.sleep(5)
    else:
        # Single run
        print_dashboard()