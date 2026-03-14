---
name: apex-forex-risk-veto
description: Risk veto authority for forex trades. Checks leverage, exposure limits.
tags: [apex, trading, forex, risk]
---

# APEX Forex Risk Veto Authority

## Purpose
Risk management for forex paper trading.

## Gates
1. **Leverage Gate** - Max 10:1 leverage
2. **Exposure Gate** - Max 50% in single currency
3. **Correlation Gate** - Limit correlated pair exposure
4. **News Gate** - Avoid high-impact news events

## Output
```json
{
  "forex_veto": {
    "approved": true,
    "max_leverage": 10,
    "position_limit": 50,
    "correlated_exposure": 30
  }
}
```
