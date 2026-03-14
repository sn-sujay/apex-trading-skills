---
name: apex-inr-signal-engine
description: USD/INR currency pair signal generator. Tracks RBI policy, trade deficit, crude impact.
tags: [apex, trading, inr, forex, currency]
---

# APEX INR Currency Signal Engine

## Purpose
Generates signals for USD/INR currency pair based on:
- RBI policy stance
- Trade deficit data
- Crude oil prices (India is big importer)
- FII/FPI flows
- DXY correlation

## Signal Generation
```python
signals = []
if crude_up and rbi_dovish:
    signals.append({"pair": "USD/INR", "direction": "LONG", "confidence": 75})
```

## Output
```json
{
  "inr_signals": [
    {
      "pair": "USD/INR",
      "direction": "LONG",
      "entry": 83.50,
      "target": 84.20,
      "stop": 83.20,
      "confidence": 72
    }
  ]
}
```

## Note
Requires RBI data, oil prices, and currency data feeds.
