---
name: apex-system-health-monitor
description: Watchdog agent monitoring all APEX agents. Fires URGENT alerts when agents are late, silent, or failed.
triggers:
  - schedule: "0 3-10 * * 1-5"  # Hourly during market
  - schedule: "*/30 3-10 * * 1-5"  # Every 30 min during market
tags: [apex, trading, health, watchdog]
---

# APEX System Health Monitor

## Purpose
Watchdog agent monitoring 13+ APEX agents across daily windows. Detects late, silent, or failed agents.

## Monitored Agents
1. india-trading-central-command
2. global-macro-intelligence-scanner
3. india-market-regime-engine
4. sentiment-intelligence-engine
5. nse-option-chain-monitor
6. options-strategy-engine
7. trading-risk-veto-authority
8. dhan-paper-trade-engine
9. live-trade-performance-monitor
10. apex-self-evolution-engine
11. apex-system-health-monitor (self)
12. apex-error-monitor

## Health Checks
- Check timestamp freshness in state.json
- Expected TTL per agent type
- Escalate after 3 consecutive failures

## Alert Levels
- URGENT: Agent late/silent
- CRITICAL: 3+ consecutive failures

## Output
```json
{
  "health_status": {
    "timestamp": "2026-03-14T10:00:00",
    "status": "OK",
    "failed_agents": [],
    "late_agents": [],
    "healthy_count": 12
  }
}
```
