---
name: apex-options-strategy-engine
description: Generates options spread signals using regime+sentiment mapping - the ORIGINAL APEX strategy logic.
tags: [apex, trading, options, signals]
---

# APEX Options Strategy Engine (ORIGINAL LOGIC)

## Purpose
Generates options spread signals based on **Market Regime + Sentiment** mapping - the original APEX strategy logic from the repo.

## The 5 ORIGINAL APEX Strategies

| # | Strategy | When to Use | Setup |
|---|----------|-------------|-------|
| 1 | **Bull Call Spread** | Trending Up (Bullish/Neutral) | Buy ATM CE + Sell OTM CE |
| 2 | **Bear Put Spread** | Trending Down (Bearish/Neutral) | Buy ATM PE + Sell OTM PE |
| 3 | **Iron Condor** | Ranging (Sideways) | Sell OTM CE + Buy further CE + Sell OTM PE + Buy further PE |
| 4 | **Long Straddle** | Volatile (big move expected) | Buy ATM CE + Buy ATM PE |
| 5 | **Long Strangle** | High Volatility | Buy OTM CE + Buy OTM PE |

## Strategy Mapping Table

| Market Regime | Sentiment | Strategy |
|--------------|-----------|----------|
| TRENDING_UP | BULLISH/NEUTRAL | Bull Call Spread |
| TRENDING_UP | BEARISH | SKIP |
| TRENDING_DOWN | BEARISH/NEUTRAL | Bear Put Spread |
| TRENDING_DOWN | BULLISH | SKIP |
| RANGING | ANY | Iron Condor |
| VOLATILE | ANY | Long Straddle |
| HIGH_VOLATILITY | ANY | Long Strangle |

## Strike Selection
- **Primary**: ATM (at-the-money)
- **Secondary**: ATM ± 1-2 strikes for spreads
- **Expiry**: Nearest weekly expiry

## Risk Parameters
| Parameter | Value |
|-----------|-------|
| Max risk per trade | 0.5% of capital |
| Min confidence | 65% |
| Position sizing | Half-Kelly |
| Stop Loss (Debit) | 40-50% of premium paid |
| Stop Loss (Credit) | 2x credit received |

## Signal Generation Logic
1. Read MARKET_REGIME from state (from apex-market-regime-engine)
2. Read SENTIMENT from state (from apex-sentiment-engine)
3. Apply mapping table above to determine strategy
4. Get option chain data (PCR, IV rank)
5. Select strikes (ATM ± 1-2)
6. Calculate entry, stop loss, target
7. Output signal with confidence score

## Output Format
```json
{
  "active_signals": [
    {
      "signal_id": "SIG001",
      "underlying": "BANKNIFTY",
      "strategy": "Bull Call Spread",
      "legs": [
        {"type": "CE", "action": "BUY", "strike": 57200, "premium": 150},
        {"type": "CE", "action": "SELL", "strike": 57500, "premium": 80}
      ],
      "net_debit": 70,
      "max_loss": 70,
      "max_profit": 230,
      "entry": 57200,
      "stop_loss": 56800,
      "target": 57800,
      "confidence": 78,
      "regime": "TRENDING_UP",
      "sentiment": "BULLISH",
      "timestamp": "2026-03-14T10:30:00+05:30"
    }
  ]
}
```

## Input Required
- `market_regime`: TRENDING_UP | TRENDING_DOWN | RANGING | VOLATILE | HIGH_VOLATILITY | EVENT_DRIVEN
- `sentiment`: BULLISH | NEUTRAL | BEARISH
- `option_chain`: PCR, IV rank, underlying price

## Implementation Note
This is the ORIGINAL APEX strategy logic. Uses real Dhan API for option chain data.
