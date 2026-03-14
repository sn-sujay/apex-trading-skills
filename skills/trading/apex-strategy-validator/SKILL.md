---
name: apex-strategy-validator
description: Walk-forward backtesting engine. Validates strategy performance weekly.
triggers:
  - schedule: "0 4 * * 6"  # Every Saturday 09:30 IST
tags: [apex, trading, backtest, validation]
---

# APEX Strategy Validation Engine

## Purpose
Weekly walk-forward backtesting to validate strategy performance.

## Process
1. Run backtest on recent 4 weeks of data
2. Compare to historical baseline
3. Flag underperforming strategies
4. Recommend parameter updates

## Output
```json
{
  "validation_report": {
    "week": "2026-W11",
    "backtest_results": {
      "BREAKOUT": {"win_rate": 0.62, "profit_factor": 1.8},
      "MOMENTUM": {"win_rate": 0.55, "profit_factor": 1.4}
    },
    "recommendations": []
  }
}
```

## Note
Requires historical data from Dhan or alternative source.
