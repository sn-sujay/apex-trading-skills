---
name: apex-forex-performance
description: Performance monitoring for forex trades. Tracks currency pair metrics.
tags: [apex, trading, forex, performance]
---

# APEX Forex Performance Monitor

## Purpose
Real-time performance metrics for forex paper trades.

## Tracked Metrics
- Sharpe Ratio (forex specific)
- Win rate by currency pair
- Average pips per trade
- Drawdown by pair
- Correlation between pairs

## Output
```json
{
  "forex_performance": {
    "eur_usd": {"win_rate": 0.58, "avg_pips": 12.5},
    "gbp_usd": {"win_rate": 0.52, "avg_pips": 18.2},
    "usd_jpy": {"win_rate": 0.61, "avg_pips": 9.8}
  }
}
```
