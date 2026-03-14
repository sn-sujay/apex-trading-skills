---
name: apex-forex-macro-engine
description: Global macro scanner for forex markets. Monitors DXY, Fed policy, major currency pairs.
triggers:
  - schedule: "0 0 * * 1-5"  # Asia open
tags: [apex, trading, forex, macro]
---

# APEX Forex Macro Regime Engine

## Purpose
Macro scanner for forex markets. Monitors:
- DXY (Dollar Index)
- Fed policy signals
- Major currency pairs (EUR/USD, GBP/USD, USD/JPY)
- Commodity currencies (AUD, CAD)

## Outputs
```json
{
  "forex_macro": {
    "dxy_trend": "BULLISH",
    "fed_stance": "HAWKISH",
    "risk_sentiment": "RISK_OFF",
    "confidence": 72
  }
}
```

## Note
Requires Alpha Vantage or similar forex data API.
