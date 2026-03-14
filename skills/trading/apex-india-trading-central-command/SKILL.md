---
name: apex-india-trading-central-command
description: Master orchestrator for APEX trading ecosystem. Routes work across all agents, runs morning market briefings, manages intraday signals, and owns KILL_SWITCH authority.
triggers:
  - schedule: "0 2 * * 1-5"  # 08:00 IST weekdays
tags: [apex, trading, india, orchestrator, nse]
---

# APEX India Trading Central Command

## Purpose
Master orchestrator for the APEX trading ecosystem. Routes work across all 12 specialist agents, runs morning market briefings at 08:00 IST, manages intraday signal routing, resolves conflicts between agents, and owns the KILL_SWITCH reset authority.

## When to Use
- Morning session start (08:00 IST weekdays)
- Intraday signal routing
- Conflict resolution between agents
- Emergency KILL_SWITCH activation/deactivation
- EOD reconciliation

## Prerequisites
- Config at ~/.apex/config.yaml
- State at ~/.apex/state.json
- Telegram configured for alerts

## Workflow

### Step 1: Session Start (08:00 IST)
```python
# Read current state
state = read_state()

# Check KILL_SWITCH
if state['kill_switch']:
    alert_telegram("[APEX ALERT] Trading suspended - KILL_SWITCH active")
    return

# Reset KILL_SWITCH if non-manual
if state['kill_switch'] and state['kill_switch_reason'] != 'manual':
    state['kill_switch'] = False
    state['kill_switch_reason'] = 'session_reset'
    write_state(state)
```

### Step 2: Initialize Daily PnL
```python
from datetime import datetime
import pytz

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)

state['daily_pnl'] = {
    'date': now.strftime('%Y-%m-%d'),
    'realized': 0.0,
    'unrealized': 0.0,
    'trades_today': 0,
    'timestamp': now.isoformat()
}
state['current_session'] = {
    'date': now.strftime('%Y-%m-%d'),
    'started_at': now.isoformat(),
    'status': 'ACTIVE'
}
write_state(state)
```

### Step 3: Delegate to Specialist Agents
1. Trigger `apex-global-macro-intelligence-scanner` for pre-market briefing
2. Trigger `apex-india-market-regime-engine` for regime classification
3. Trigger `apex-sentiment-intelligence-engine` for sentiment snapshot
4. Trigger `apex-nse-option-chain-monitor` for option chain data

### Step 4: Intraday Loop (every 15 min)
```python
# Monitor positions, P&L, KILL_SWITCH
state = read_state()

# Check circuit breaker
if state['daily_pnl']['realized'] < -CONFIG['max_daily_loss_pct']:
    state['kill_switch'] = True
    state['kill_switch_reason'] = 'circuit_breaker'
    write_state(state)
    alert_telegram("[APEX CRITICAL] Circuit breaker triggered! Daily loss limit reached.")
```

### Step 5: EOD Reconciliation (15:35 IST)
```python
# Compile session summary
summary = compile_eod_summary()
alert_telegram(f"[APEX EOD] Session complete. P&L: ₹{summary['pnl']}, Trades: {summary['trades']}")

# Reset session
state['current_session']['status'] = 'CLOSED'
write_state(state)
```

## State Access

### Keys Read
- `kill_switch`: Boolean trading halt flag
- `paper_mode`: Always true until configured otherwise
- `daily_pnl`: Daily P&L tracking
- `market_regime`: Current market regime
- `sentiment`: Sentiment snapshot
- `option_chain`: Option chain data
- `signals_blocked`: Signal gate status
- `positions`: Active positions

### Keys Written
- `kill_switch`: Reset authority
- `daily_pnl`: Initialize each session
- `current_session`: Session tracking
- `session_log`: Append-only log

## Alert Levels
- `[APEX INFO]` = General updates
- `[APEX ALERT]` = Agent issues, late/silent agents
- `[APEX CRITICAL]` = Circuit breaker, systemic failures
- `[APEX EOD]` = End-of-day reports

## Example Execution
```python
from hermes_tools import read_file, skill_view, send_message
import json
from datetime import datetime
import pytz

# Load config
config = read_file("~/.apex/config.yaml")
state_file = json.loads(read_file("~/.apex/state.json")["content"])

# Initialize session
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)

# Check KILL_SWITCH
if state_file.get("kill_switch"):
    send_message(message="[APEX ALERT] Session suspended - KILL_SWITCH active")
    exit(0)

# Reset daily P&L
state_file["daily_pnl"] = {
    "date": now.strftime("%Y-%m-%d"),
    "realized": 0.0,
    "unrealized": 0.0,
    "trades_today": 0,
    "timestamp": now.isoformat()
}
state_file["current_session"] = {
    "date": now.strftime("%Y-%m-%d"),
    "started_at": now.isoformat(),
    "status": "ACTIVE"
}

# Write updated state
with open("~/.apex/state.json", "w") as f:
    json.dump(state_file, f, indent=2)

# Send notification
send_message(message=f"[APEX INFO] Trading session started at {now.strftime('%H:%M')} IST")

# Next: Trigger specialist agents via skill_view and execute
```

## Common Errors & Fixes
| Error | Cause | Fix |
|-------|-------|-----|
| State file not found | First run | Run initialization |
| KILL_SWITCH stuck | Manual trigger | Reset manually in state.json |
| Config missing | Not configured | Add API keys to config.yaml |

## Related Skills
- `apex-global-macro-intelligence-scanner`
- `apex-india-market-regime-engine`
- `apex-sentiment-intelligence-engine`
- `apex-nse-option-chain-monitor`
- `apex-trading-risk-veto-authority`
- `apex-system-health-monitor`
