---
name: apex-market-regime-engine
description: Classifies market regime as TRENDING_UP, TRENDING_DOWN, RANGE_BOUND, EVENT_DRIVEN, or HIGH_VOLATILITY.
triggers:
  - schedule: "5 2 * * 1-5"  # 5 min after market open
tags: [apex, trading, regime, classifier]
---

# APEX Market Regime Engine

## Purpose
Classifies current market regime as:
- TRENDING_UP - Strong directional move up
- TRENDING_DOWN - Strong directional move down
- RANGE_BOUND - Sideways chop
- EVENT_DRIVEN - High impact news event
- HIGH_VOLATILITY - India VIX > 18 or abnormal moves

## Regime Detection Logic

### Trend Detection
```
Using EMA alignment:
- Price > EMA9 > EMA21 > EMA50 = TRENDING_UP
- Price < EMA9 < EMA21 < EMA50 = TRENDING_DOWN
- Mixed signals = RANGE_BOUND
```

### Volatility Check
```
IF India VIX > 18: HIGH_VOLATILITY
IF 3-sigma move in Nifty: EVENT_DRIVEN
```

### Inputs (from state)
- Nifty spot price history
- BANKNIFTY price history
- India VIX level
- Option chain IV rank

## Output Format
```json
{
  "market_regime": {
    "regime": "TRENDING_UP",
    "confidence": 78,
    "india_vix": 13.4,
    "sentiment": "BULLISH",
    "signal_source": "regime-engine",
    "timestamp": "2026-03-14T09:30:00+05:30"
  }
}
```

## Risk Gate
If regime is EVENT_DRIVEN or HIGH_VOLATILITY:
- Set signals_blocked = True
- Alert: "Market regime HIGH_VOL - no new positions"

## Implementation
```python
from hermes_tools import read_file, send_message
import json
from datetime import datetime

# Load state
state_file = json.loads(read_file("~/.apex/state.json")["content"])

# TODO: Implement regime detection when Dhan API available
# For now, placeholder regime

state_file["market_regime"] = {
    "regime": "RANGE_BOUND",
    "confidence": 50,
    "india_vix": 15.0,
    "sentiment": "NEUTRAL",
    "signal_source": "regime-engine",
    "timestamp": datetime.now().isoformat()
}

# Write state
with open("~/.apex/state.json", "w") as f:
    json.dump(state_file, f, indent=2)

send_message(message="[APEX INFO] Market Regime: RANGE_BOUND (mock mode)")
```

## Related Skills
- apex-nse-option-chain-monitor (provides IV data)
- apex-trading-risk-veto-authority (reads regime for veto)
