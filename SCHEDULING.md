# APEX Scheduling & Operations Guide

Complete schedule for APEX autonomous trading system. All times are **IST (India Standard Time)**.

---

## Cronjobs Overview

### 7 Cronjobs (Current Configuration)

| Time IST | Schedule | Skill | Action | Status |
|----------|----------|-------|--------|--------|
| 8:00 AM | `0 8 * * 1-5` | apex-india-trading-central-command | Pre-market setup | ✅ Active |
| 9:15 AM | `15 9 * * 1-5` | apex-market-regime-engine | Classify regime at open | ✅ Active |
| Every 5 min | `*/5 9-15 * * 1-5` | apex-core-orchestrator | Event coordination | ✅ Active |
| Hourly 9AM-2PM | `0 9-14 * * 1-5` | apex-options-strategy-engine | Generate signals | ✅ Active |
| 3:30 PM | `30 15 * * 1-5` | apex-self-evolution-engine | Post-market learning | ✅ Active |
| 3:40 PM | `40 15 * * 1-5` | apex-india-trading-central-command | EOD reconciliation | ✅ Active |
| Sunday 8PM | `0 20 * * 0` | apex-system-health-monitor | Weekend system check | ✅ Active |

---

## Market Hours (IST)

| Session | Time | Notes |
|---------|------|-------|
| **Pre-market** | 9:00 AM - 9:15 AM | Orders can be placed |
| **Market Open** | 9:15 AM | Trading starts |
| **Intraday** | 9:15 AM - 3:00 PM | Active trading |
| **Market Close** | 3:30 PM | Last trading time |
| **Post-market** | 3:40 PM - 4:00 PM | Square off & reporting |

All cron jobs are aligned to run during or around these hours.

---

## Cronjob Details

### 1. apex-pre-market (8:00 AM)

**Schedule:** `0 8 * * 1-5` (Mon-Fri 8:00 AM IST)

**What it does:**
- Fetches India VIX data
- Fetches global macro data (DXY, Fed rates)
- Updates option chain cache
- Compiles pre-market summary
- Updates state.json with morning data

**Skill:** `apex-india-trading-central-command`

**Output:** Telegram alert with VIX, global markets status

---

### 2. apex-market-regime (9:15 AM)

**Schedule:** `15 9 * * 1-5` (Mon-Fri 9:15 AM IST)

**What it does:**
- Classifies market regime (TRENDING_UP, TRENDING_DOWN, RANGING, HIGH_VOL)
- Updates risk parameters based on regime
- Publishes regime change event

**Skill:** `apex-market-regime-engine`

**Output:** Market regime classification + risk adjustments

---

### 3. apex-orchestrator (Every 5 Minutes)

**Schedule:** `*/5 9-15 * * 1-5` (Every 5 min during market hours)

**What it does:**
- **Intraday Monitoring:** Check positions, SL/Target, MTM P&L
- **Signal Generation:** Fetch option chain → analyze → generate signals
- **Risk Validation:** Validate each signal through 6 gates
- **Trade Execution:** Execute validated trades, start monitoring
- **Error Detection:** Quick detection of issues
- **Event Processing:** Process any pending events from event bus

**Skill:** `apex-core-orchestrator`

**Key Workflows:**
```
Every 5 Minutes:
  1. Check open positions
     └─→ MTM P&L calculation
     └─→ SL/Target trigger check
  
  2. Process event queue
     └─→ Route pending events
     └─→ Execute callbacks
  
  3. Generate signals (every hour)
     └─→ Fetch option chain
     └─→ Analyze PCR, IV, OI
     └─→ Publish signal:generated
  
  4. Validate signals
     └─→ Route to risk veto
     └─→ Execute approved trades
  
  5. Health check
     └─→ Check API connectivity
     └─→ Detect errors
```

---

### 4. apex-strategy-gen (Hourly)

**Schedule:** `0 9-14 * * 1-5` (Mon-Fri 9 AM, 10 AM, 11 AM, 12 PM, 1 PM, 2 PM IST)

**What it does:**
- Fetches fresh option chain data
- Analyzes PCR, max pain, IV rank
- Generates trading signals with confidence scores
- Publishes signals to event bus

**Skill:** `apex-options-strategy-engine`

**Signal Types:**
- BREAKOUT (30% weight)
- MOMENTUM (25% weight)
- MEAN_REVERSION (20% weight)
- MTF_EMA (15% weight)
- OPTION_SPREAD (10% weight)

---

### 5. apex-evolution-engine (3:30 PM)

**Schedule:** `30 15 * * 1-5` (Mon-Fri 3:30 PM IST)

**What it does:**
- Analyzes daily performance
- Calculates Sharpe, Calmar, Sortino ratios
- Adjusts strategy weights based on performance
- Logs trade lessons
- Updates confidence scores

**Skill:** `apex-self-evolution-engine`

**Learning Cycle:**
```
1. Analyze today's trades
   └─→ P&L by strategy
   └─→ Win rate
   └─→ Average gain/loss

2. Compare to benchmarks
   └─→ Sharpe ratio
   └─→ Max drawdown
   └─→ Win rate

3. Adjust weights
   └─→ Increase weight on winning strategies
   └─→ Decrease weight on losing strategies

4. Log lessons
   └─→ Save [TRADE_LESSON] to memory
   └─→ Record what worked/didn't
```

---

### 6. apex-eod (3:40 PM)

**Schedule:** `40 15 * * 1-5` (Mon-Fri 3:40 PM IST)

**What it does:**
- Close all intraday positions
- Compile session summary
- Update state.json for next day
- Send EOD report

**Skill:** `apex-india-trading-central-command`

---

### 7. apex-sunday-health (Sunday 8PM)

**Schedule:** `0 20 * * 0` (Sunday 8:00 PM IST)

**What it does:**
- Test all API connections
- Verify Dhan API connectivity
- Check state file integrity
- Verify all skills are present
- Send weekend health report

**Skill:** `apex-system-health-monitor`

---

## Running Fetch Scripts (Standalone)

These can be run independently at any time:

```bash
# Fetch India VIX (with 15-min caching)
python3 ~/.hermes/skills/trading/apex-india-vix-monitor/fetch_vix.py

# Fetch Option Chain (with 5-min caching)
python3 ~/.hermes/skills/trading/apex-option-chain-monitor/fetch_option_chain.py

# Search Scrip Master (with 7-day caching)
python3 ~/.hermes/skills/trading/apex-controller/fetch_scrip_master.py NIFTY

# Check global macros
python3 ~/.hermes/skills/trading/apex-global-macro-scanner/fetch_macro.py

# Check INR signals
python3 ~/.hermes/skills/trading/apex-inr-signal-engine/fetch_inr.py
```

---

## Caching System (Performance Optimization)

APEX uses caching to reduce API calls:

| Data | Cache File | Cache Duration | Location |
|------|------------|----------------|----------|
| India VIX | `vix_cache.json` | 15 min | `~/.apex/cache/` |
| Option Chain | `option_chain_cache.json` | 5 min | `~/.apex/cache/` |
| Scrip Master | `scrip_master.csv` | 7 days | `~/.apex/cache/` |

### Caching Logic
1. Check cache - if fresh, use cached data (instant)
2. If stale, fetch from API and update cache
3. If API fails, fallback to stale cache

---

## Response Time

| Scenario | Without Orchestrator | With Orchestrator |
|----------|---------------------|-------------------|
| Crisis News | Stored in state.json | Instant event published |
| Trading Blocked | Manual review needed | Auto-block in <5 sec |
| Stop Losses Adjusted | Manual adjustment | Auto-tightened |
| User Alerted | Next cron (up to 30 min) | Instant telegram |

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| List cronjobs | `list_cronjobs()` |
| Get India VIX | `python3 fetch_vix.py` |
| Get Option Chain | `python3 fetch_option_chain.py` |
| Search Symbol | `python3 fetch_scrip_master.py <query>` |
| Check State | `cat ~/.apex/state.json` |
| Check Cache | `ls -la ~/.apex/cache/` |
| View Logs | `tail -f ~/.hermes/logs/apex*.log` |

---

## Schedule Summary (Cron Format)

```bash
# Pre-market (8:00 AM)
0 8 * * 1-5

# Market open (9:15 AM) 
15 9 * * 1-5

# Orchestrator every 5 min (9:00 AM - 3:00 PM)
*/5 9-15 * * 1-5

# Strategy generation hourly (9 AM - 2 PM)
0 9-14 * * 1-5

# Evolution (3:30 PM)
30 15 * * 1-5

# EOD (3:40 PM)
40 15 * * 1-5

# Sunday health (8 PM Sunday)
0 20 * * 0
```

---

## Setup Cronjobs (Hermes)

```python
# Pre-market
schedule_cronjob(
    schedule="0 8 * * 1-5",
    name="apex-pre-market",
    prompt="Run apex-india-trading-central-command for pre-market setup. Check VIX, global macros, update state.",
    deliver="telegram"
)

# Market regime
schedule_cronjob(
    schedule="15 9 * * 1-5", 
    name="apex-market-regime",
    prompt="Run apex-market-regime-engine to classify market as TRENDING_UP, TRENDING_DOWN, RANGING, or HIGH_VOL.",
    deliver="telegram"
)

# Orchestrator (every 5 min)
schedule_cronjob(
    schedule="*/5 9-15 * * 1-5",
    name="apex-orchestrator",
    prompt="Run apex-core-orchestrator: (1) Process event queue, (2) Check positions/MTM, (3) Generate signals hourly, (4) Validate through risk veto, (5) Execute approved trades.",
    deliver="telegram"
)

# Strategy generation
schedule_cronjob(
    schedule="0 9-14 * * 1-5",
    name="apex-strategy-gen",
    prompt="Run apex-options-strategy-engine: Fetch option chain, analyze PCR/IV/OI, generate signals with confidence scores, publish to event bus.",
    deliver="telegram"
)

# Evolution
schedule_cronjob(
    schedule="30 15 * * 1-5",
    name="apex-evolution-engine",
    prompt="Run apex-self-evolution-engine: Analyze daily performance, calculate Sharpe/Calmar/Sortino, adjust strategy weights, log trade lessons.",
    deliver="telegram"
)

# EOD
schedule_cronjob(
    schedule="40 15 * * 1-5",
    name="apex-eod",
    prompt="Run apex-india-trading-central-command EOD: Close intraday positions, compile session summary, update state.json, send EOD report.",
    deliver="telegram"
)

# Sunday health
schedule_cronjob(
    schedule="0 20 * * 0",
    name="apex-sunday-health",
    prompt="Run apex-system-health-monitor: Test API connections, verify state files, check all skills present, send health report.",
    deliver="telegram"
)
```