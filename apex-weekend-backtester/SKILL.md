---
name: apex-weekend-backtester
description: Weekend backtesting engine for APEX options strategies using real Dhan API data. Tests Bull Call Spread, Bear Put Spread, Iron Condor, Long Straddle, and Long Strangle against historical BANKNIFTY data.
triggers:
  - schedule: "0 9 * * 6"  # Saturday 9 AM
  - manual: apex-backtest
tags: [apex, trading, backtest, options, strategy]
---

# APEX Weekend Backtester

## Purpose
Run comprehensive backtests on the 5 original APEX options strategies using real historical data from Dhan API.

## Strategies Tested
1. **Bull Call Spread** - TRENDING_UP markets
2. **Bear Put Spread** - TRENDING_DOWN markets  
3. **Iron Condor** - RANGING markets
4. **Long Straddle** - VOLATILE markets
5. **Long Strangle** - HIGH_VOLATILITY markets

## Data Source
- Real BANKNIFTY historical data from Dhan API
- 25x multiplier applied to convert API values to actual index levels
- Falls back to simulated data if API fails

## Configuration
- Starting equity: ₹100,000
- Max risk per trade: 0.5%
- Max position size: 10%
- Min confidence: 65%

## Run Commands

### Run full backtest
```bash
python3 ~/.apex/trading_system/apex_backtester.py
```

### Run with custom parameters
```python
from apex_backtester import run_backtest
result = run_backtest(security_id="25", days=90)
```

## Output
- Regime distribution analysis
- Strategy-wise P&L breakdown
- Sharpe ratio, max drawdown, win rate
- JSON output for logging

## Notes
- Token refresh issue fixed - loads token_expiry from state.json
- No unnecessary token refresh attempts
- Real data with proper scaling