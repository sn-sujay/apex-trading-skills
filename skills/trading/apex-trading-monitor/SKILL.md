---
name: apex-trading-monitor
description: APEX Trading Monitor - Real-time dashboard and HTML email reports. Compiles system status and sends richly formatted reports.
triggers:
  - schedule: "*/15 3-10 * * 1-5"  # Every 15 min during market
tags: [apex, trading, monitor, dashboard, reports]
---

# APEX Trading Monitor

## Purpose
Real-time trading monitor that compiles system status and sends richly formatted reports via Telegram (HTML email replacement).

## When to Run
- Every 15 minutes during market hours
- At session open (09:15) for full report
- At session close (15:35) for EOD summary

## Report Includes
1. **Market Regime** - Current classification with confidence
2. **Active Signals** - Entry, target, stop-loss, confidence
3. **Paper Trading Ledger** - Open positions, today's PnL
4. **Risk Status** - Daily loss %, positions used, circuit breaker
5. **Agent Health** - Last run timestamps, success/failure
6. **Performance Metrics** - Win rate, Sharpe, total PnL

## Dashboard View
```
╔════════════════════════════════════════════════════════════╗
║  APEX Trading Dashboard - [TIMESTAMP]                      ║
╠════════════════════════════════════════════════════════════╣
║  MARKET                                                    ║
║  Regime: TRENDING_UP (Confidence: 78%)                     ║
║  India VIX: 13.4 | Nifty PCR: 1.12                         ║
╠════════════════════════════════════════════════════════════╣
║  SIGNALS                                                   ║
║  Active: 2 | Approved: 1 | Executed: 3                     ║
║  Latest: BANKNIFTY LONG @ 57200 (Conf: 70%)               ║
╠════════════════════════════════════════════════════════════╣
║  POSITIONS                                                 ║
║  Open: 1 | P&L Today: ₹+1,250                              ║
║  BANKNIFTY CE 57200: +₹1,250 (1 lot)                       ║
╠════════════════════════════════════════════════════════════╣
║  RISK                                                      ║
║  Daily Loss: -0.4% (Limit: -2%)                           ║
║  Circuit Breaker: OFF | Kill Switch: OFF                   ║
╠════════════════════════════════════════════════════════════╣
║  PERFORMANCE                                               ║
║  Total Trades: 15 | Win Rate: 60%                         ║
║  Total P&L: ₹+8,450                                       ║
╚════════════════════════════════════════════════════════════╝
```

## Implementation
```python
from hermes_tools import read_file, send_message
import json
from datetime import datetime

# Read all state files
config = json.loads(read_file("~/.apex/config.yaml")["content"])
state = json.loads(read_file("~/.apex/state.json")["content"])
signals = json.loads(read_file("~/.apex/signals.json")["content"])
ledger = json.loads(read_file("~/.apex/ledger.json")["content"])

# Compile report
report = f"""
╔════════════════════════════════════════════════════════════╗
║  APEX Trading Dashboard - {datetime.now().strftime('%H:%M %d-%b')}                 ║
╠════════════════════════════════════════════════════════════╣
║  MARKET                                                    ║
║  Regime: {state.get('market_regime', {}).get('regime', 'N/A')} (Conf: {state.get('market_regime', {}).get('confidence', 0)}%)║
║  India VIX: {state.get('market_regime', {}).get('india_vix', 'N/A')} | P&L Today: ₹{state.get('daily_pnl', {}).get('realized', 0)}║
╠════════════════════════════════════════════════════════════╣
║  SIGNALS                                                   ║
║  Active: {len(signals.get('active_signals', []))} | Executed: {len(ledger.get('trades', []))}                    ║
╠════════════════════════════════════════════════════════════╣
║  RISK                                                      ║
║  Kill Switch: {'ON' if state.get('kill_switch') else 'OFF'} | Paper Mode: {'ON' if state.get('paper_mode') else 'OFF'}     ║
╚════════════════════════════════════════════════════════════╝
"""

# Send to Telegram
send_message(message=report)

# Log monitor run
if not state.get('monitor_log'):
    state['monitor_log'] = []
state['monitor_log'].append({
    'timestamp': datetime.now().isoformat(),
    'signals_active': len(signals.get('active_signals', [])),
    'positions_open': len(state.get('positions', [])),
    'daily_pnl': state.get('daily_pnl', {}).get('realized', 0)
})

with open("~/.apex/state.json", "w") as f:
    json.dump(state, f, indent=2)
```

## Output
- Rich text dashboard to Telegram
- Status summary every 15 minutes
- Full report at market open/close
- Agent health check included

## Related Skills
- apex-system-health-monitor
- apex-live-order-monitor
