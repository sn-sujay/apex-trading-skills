---
name: apex-controller
description: Master controller and documentation hub for APEX trading system.
tags: [apex, trading, controller, docs]
---

# APEX Controller

## System Overview
APEX is an autonomous AI trading system with 20 specialized agents for NSE India options and forex trading.

## State Files Location
- ~/.apex/config.yaml - Configuration
- ~/.apex/state.json - System state
- ~/.apex/signals.json - Trading signals
- ~/.apex/ledger.json - Trade history

## 20 Agent Skills

### India NSE (16 agents)
1. apex-india-trading-central-command
2. apex-global-macro-scanner
3. apex-market-regime-engine
4. apex-sentiment-engine
5. apex-option-chain-monitor
6. apex-options-strategy-engine
7. apex-validator-gate
8. apex-risk-veto-authority
9. apex-paper-trade-engine
10. apex-live-order-monitor
11. apex-performance-monitor
12. apex-self-evolution-engine
13. apex-system-health-monitor
14. apex-error-monitor
15. apex-fix-monitor
16. apex-strategy-validator

### Forex (5 agents)
17. apex-forex-macro-engine
18. apex-inr-signal-engine
19. apex-forex-paper-engine
20. apex-forex-performance
21. apex-forex-risk-veto

## Setup Instructions
1. Add API keys to ~/.apex/config.yaml
2. Configure Telegram in config.yaml
3. Review state files
4. Set paper_mode: true

## Note
All API credentials should be added to ~/.apex/config.yaml file only.
