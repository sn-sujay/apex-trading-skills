---
name: apex-global-macro-scanner
description: Global macro intelligence scanner for APEX trading system. Monitors global markets, Fed signals, and commodities.
triggers:
  - schedule: "0 20 * * 0-4"
  - schedule: "0 2 * * 1-5"
  - schedule: "0 16 * * 1-5"
tags: [apex, trading, macro, global]
---

# APEX Global Macro Scanner

## Purpose
Scans global markets before Indian market open. Monitors Fed signals, US banking sector, geopolitical events, and commodities.

## Data Sources
- Alpha Vantage (news sentiment, economic data)
- FRED (Fed rates, CPI, NFP)
- Yahoo Finance (indices, commodities, VIX)

## Scoring Model
Composite score (-1.0 to +1.0) weighted:
- Fed signal: 30%
- Banking signal: 20%
- Geopolitical: 20%
- Commodity: 15%
- Risk appetite: 15%

## Workflow
1. Check API keys in ~/.apex/config.yaml
2. Fetch market data from configured sources
3. Calculate 5 sub-signals
4. Compute weighted composite score
5. Update state.json sentiment section
6. Alert if sentiment is strongly bullish/bearish

## Output Format
```json
{
  "sentiment": {
    "global_sentiment": -0.35,
    "global_sentiment_label": "BULLISH",
    "global_sentiment_strength": "moderate",
    "timestamp": "2026-03-14T08:00:00+05:30"
  }
}
```

## Implementation
```python
from hermes_tools import read_file, send_message
import json

# Read config and state
config = read_file("~/.apex/config.yaml")
state_file = json.loads(read_file("~/.apex/state.json")["content"])

# TODO: Add Alpha Vantage and FRED API calls when keys are provided
# For now, this skill runs in "mock" mode

# Update state with placeholder
state_file["sentiment"]["global_sentiment"] = 0.0
state_file["sentiment"]["global_sentiment_label"] = "NEUTRAL"
state_file["sentiment"]["timestamp"] = "2026-03-14T08:00:00+05:30"

# Write state
with open("~/.apex/state.json", "w") as f:
    json.dump(state_file, f, indent=2)

# Notify
send_message(message="[APEX INFO] Global Macro Scanner completed (mock mode - add API keys to config.yaml)")
```

## API Key Setup
Add to ~/.apex/config.yaml:
```yaml
market_data:
  alpha_vantage: "your_key_here"
  fred_api: "your_key_here"
```

## Related Skills
- apex-india-trading-central-command
- apex-india-market-regime-engine
