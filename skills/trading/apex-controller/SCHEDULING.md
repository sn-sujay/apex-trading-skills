# APEX Scheduling & Operations Guide

Complete schedule for APEX autonomous trading system. All times are **IST (India Standard Time)**.

## Cronjobs Overview

### 7 Cronjobs (Current Configuration)

| Time IST | Schedule | Skill | Action |
|----------|----------|-------|--------|
| 8:00 AM | `0 8 * * 1-5` | apex-pre-market | Pre-market setup |
| 9:15 AM | `15 9 * * 1-5` | apex-market-regime | Classify regime at market open |
| Every 5 min | `*/5 9-15 * * 1-5` | apex-orchestrator | Event coordination & monitoring |
| Hourly 9AM-3PM | `0 9-14 * * 1-5` | apex-strategy-gen | Generate trading signals |
| 3:30 PM | `30 15 * * 1-5` | apex-evolution-engine | Post-market learning |
| 3:40 PM | `40 15 * * 1-5` | apex-eod | EOD reconciliation |
| Sunday 8PM | `0 20 * * 0` | apex-sunday-health | Weekend system check |

## Market Hours (IST)
- **Pre-market:** 9:00 AM - 9:15 AM
- **Market Open:** 9:15 AM
- **Market Close:** 3:30 PM
- **Post-market:** 3:40 PM - 4:00 PM

All cron jobs are aligned to run during or around these hours.

## Orchestrator (Every 5 Minutes)

The `apex-orchestrator` runs every 5 minutes during market hours and handles:

- **Intraday Monitoring:** Check positions, SL/Target, MTM P&L
- **Signal Generation:** Fetch option chain → analyze → generate signals
- **Risk Validation:** Validate each signal through 6 gates
- **Trade Execution:** Execute validated trades, start monitoring
- **Error Detection:** Quick detection of issues

## Caching System (Performance Optimization)

APEX uses caching to reduce API calls and improve response times:

| Data | Cache File | Cache Duration | Location |
|------|------------|----------------|----------|
| India VIX | `vix_cache.json` | 15 min | `~/.apex/cache/` |
| Option Chain | `option_chain_cache.json` | 5 min | `~/.apex/cache/` |
| Scrip Master | `scrip_master.csv` | 7 days | `~/.apex/cache/` |

### Caching Behavior
1. First check cache - if fresh, use cached data (instant)
2. If stale, fetch from API and update cache
3. If API fails, fallback to stale cache

### Running Fetch Scripts
```bash
# Fetch India VIX (with caching)
python3 ~/.hermes/skills/trading/apex-india-vix-monitor/fetch_vix.py

# Fetch Option Chain (with caching)
python3 ~/.hermes/skills/trading/apex-option-chain-monitor/fetch_option_chain.py

# Search Scrip Master (with caching)
python3 ~/.hermes/skills/trading/apex-controller/fetch_scrip_master.py <search_term>
```

## Security IDs (For Dhan API)

| Instrument | Security ID | Exchange | Segment |
|------------|-------------|----------|---------|
| INDIA VIX | 21 | NSE | INDEX |
| NIFTY | 13 | NSE | INDEX |
| BANKNIFTY | 25 | NSE | INDEX |
| FINNIFTY | 38 | NSE | INDEX |

## Rate Limits (Dhan API)

```python
DHAN_LIMITS = {
    "order_placement": {"max_per_second": 5, "max_per_minute": 100},
    "order_modification": {"max_per_second": 2, "max_per_minute": 50},
    "portfolio_requests": {"max_per_minute": 60},
}

NSE_LIMITS = {
    "india_vix": {"max_per_minute": 10, "min_interval_seconds": 10},
    "option_chain": {"max_per_minute": 5, "min_interval_seconds": 15},
}

TRADING_LIMITS = {
    "min_time_between_trades_seconds": 60,
    "max_trades_per_hour": 10,
    "max_trades_per_day": 30,
    "cooldown_after_loss_seconds": 300,
}
```

## Toolset Configuration

For optimal performance, only load required toolsets:

```yaml
# ~/.hermes/config.yaml
toolsets:
  - trading    # Required for APEX
  - research   # For macro/forex analysis
```

Loading `all` (all 20+ categories) significantly slows down agent startup.

## Quick Reference

| Task | Skill/Command |
|------|---------------|
| Get India VIX | `python3 fetch_vix.py` in `apex-india-vix-monitor/` |
| Get Option Chain | `python3 fetch_option_chain.py` in `apex-option-chain-monitor/` |
| Search Symbol | `python3 fetch_scrip_master.py <query>` in `apex-controller/` |
| Check State | `cat ~/.apex/state.json` |
| Check Cache | `ls -la ~/.apex/cache/` |
| View Logs | `tail -f ~/.hermes/logs/apex*.log` |