---
name: apex-dashboard
description: Real-time terminal dashboard showing all APEX agent status. View VIX, regime, sentiment, positions, and P&L at a glance.
triggers:
  - command: "apex-dashboard" or "apex status"
tags: [apex, trading, dashboard, monitoring]
---

# APEX Dashboard

## Purpose
Real-time terminal dashboard showing status of all APEX trading agents. Gives instant visibility into what's happening across the system.

## Usage

```bash
# Single view
python3 apex-dashboard/dashboard.py

# Watch mode (auto-refresh every 5s)
python3 apex-dashboard/dashboard.py --watch
```

## What It Shows

| Agent | Shows |
|-------|-------|
| 📡 Weekend Scanner | Last weekend outlook |
| 📰 Pre-Market | Today's strategy & risk level |
| 📊 VIX Monitor | Current VIX & change |
| 🎯 Regime Engine | Current market regime |
| 😊 Sentiment Engine | Sentiment & confidence |
| 💰 Order Executor | Open positions count |
| 📈 Performance | P&L & trade count |
| 🛡️ Risk Veto | Kill switch status |

## State Dependencies
Reads from `~/.apex/state.json`:
- `weekend_scan.next_week_outlook`
- `pre_market_briefing.today_stance`
- `india_vix.current`
- `market_regime`
- `sentiment.label`
- `positions`
- `daily_pnl`
- `kill_switch`

## Status Indicators
- 🟢 Working: Agent active
- ⚪ Idle: Paused/waiting
- 🟡 Waiting: Waiting for trigger
- 🔴 Error: Issue detected
- 💤 Sleeping: Weekend/off-hours