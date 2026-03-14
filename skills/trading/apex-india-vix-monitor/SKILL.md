---
name: apex-india-vix-monitor
description: Monitors India VIX from NSE India official API and classifies market regime
triggers:
  - schedule: "15 9 * * 1-5"  # 9:15 AM IST - market open
tags: [apex, trading, vix, volatility, india]
---

# APEX India VIX Monitor

## Purpose
Fetches India VIX (Volatility Index) from NSE India official API.
Updates state with current VIX level and market regime classification.

## India VIX Details
- **Trading Symbol**: INDIA VIX
- **Security ID**: 21
- **Exchange**: NSE
- **Segment**: IDX (Index)

## API Source
```
Source: NSE India Official API
URL: https://www.nseindia.com/api/allIndices
Method: Session-based with cookies
Reliability: High (official source)
```

## Regime Classification
| VIX Level | Regime | Trading Implication |
|-----------|--------|---------------------|
| > 20 | HIGH_VOLATILITY | Reduce position size, wider stops |
| 15-20 | ELEVATED_VOLATILITY | Caution, watch for expansion |
| 12-15 | NORMAL | Standard trading |
| < 12 | LOW_VOLATILITY | Tighter stops, expect mean reversion |

## Output
```json
{
  "india_vix": {
    "symbol": "INDIA VIX",
    "security_id": "21",
    "current": 22.65,
    "open": 21.52,
    "high": 22.88,
    "low": 21.25,
    "prev_close": 21.52,
    "change": 1.13,
    "change_percent": 5.23,
    "regime": "HIGH_VOLATILITY",
    "fetched_at": "2026-03-14T09:15:00+05:30"
  },
  "market_regime": "HIGH_VOLATILITY"
}
```

## Usage
```python
python fetch_vix.py
```

## Related
- apex-market-regime-engine (uses VIX for regime classification)
- apex-risk-veto-authority (checks VIX before trades)
