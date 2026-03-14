---
name: apex-options-strategy-engine
description: Generates options spread signals with confidence scores based on regime, sentiment, and option chain data.
tags: [apex, trading, options, signals]
---

# APEX Options Strategy Engine

## Purpose
Generates options spread signals with confidence scores based on:
- Market regime
- Global sentiment
- Option chain data (PCR, IV rank, GEX)
- Technical indicators

## Signal Types
1. **BREAKOUT** - Long call/put spreads on momentum
2. **MOMENTUM** - Directional debit spreads
3. **MEAN_REVERSION** - Credit spreads on extremes
4. **MTF_EMA** - Multi-timeframe trend following

## Risk Parameters
- Max risk per trade: 0.5% of capital
- Min confidence: 65%
- Position sizing: Half-Kelly

## Output Format
```json
{
  "active_signals": [
    {
      "signal_id": "SIG001",
      "underlying": "BANKNIFTY",
      "type": "CE",
      "direction": "LONG",
      "entry": 57200,
      "stop_loss": 56800,
      "target": 57800,
      "strategy": "BREAKOUT",
      "confidence": 78,
      "max_loss_pct": 0.5,
      "timestamp": "2026-03-14T10:30:00+05:30"
    }
  ]
}
```

## Implementation Note
Requires Dhan API for live data. Currently generates mock signals for testing.
