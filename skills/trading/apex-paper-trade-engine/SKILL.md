---
name: apex-paper-trade-engine
description: Paper trade execution engine. Simulates trades, tracks MTM, SL/target execution.
triggers:
  - schedule: "*/15 3-10 * * 1-5"
tags: [apex, trading, paper, execution]
---

# APEX Paper Trade Engine

## Purpose
Paper trading execution for NSE options. Simulates trades, tracks:
- Entry fills
- MTM (mark-to-market) P&L
- Stop-loss execution
- Target execution
- Position sizing

## Execution Flow
1. Receive approved signal from risk veto
2. Calculate position size (Half-Kelly)
3. Simulate entry fill
4. Track position against SL/target
5. Simulate exit on trigger
6. Update ledger

## Ledger Format
```json
{
  "trades": [
    {
      "trade_id": "T001",
      "signal_id": "SIG001",
      "underlying": "BANKNIFTY",
      "entry_time": "2026-03-14T10:30:00",
      "exit_time": "2026-03-14T11:45:00",
      "entry_price": 57200,
      "exit_price": 57500,
      "quantity": 15,
      "pnl": 4500,
      "exit_reason": "target_hit"
    }
  ]
}
```

## Implementation Note
Requires Dhan API for live prices. Currently uses mock prices.
