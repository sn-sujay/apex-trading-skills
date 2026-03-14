---
name: apex-option-chain-monitor
description: Polls NSE option chain for PCR, IV rank, GEX, OI signals.
triggers:
  - schedule: "*/5 3-10 * * 1-5"  # Every 5 min during market hours
tags: [apex, trading, options, nse]
---

# APEX NSE Option Chain Monitor

## Purpose
Polls NSE option chain via Dhan API during market hours (09:15-15:30 IST) for NIFTY, BANKNIFTY, FINNIFTY, and MIDCPNIFTY.

## Computed Metrics
- PCR (Put-Call Ratio) per expiry
- IV Rank and IV Percentile
- Gamma Exposure (GEX) aggregation
- Max pain strike
- OI buildup/unwinding detection

## Output
```json
{
  "option_chain": {
    "nifty_pcr": 1.12,
    "banknifty_pcr": 0.98,
    "max_pain_nifty": 24200,
    "max_pain_banknifty": 57000,
    "iv_rank": 42,
    "gamma_exp": "HIGH",
    "oi_buildup": "BANKNIFTY_57500CE:STRONG_CALL_WRITING",
    "timestamp": "2026-03-14T10:00:00+05:30"
  }
}
```

## Implementation Note
Requires Dhan API credentials. Currently in mock mode.
