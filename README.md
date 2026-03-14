# APEX Trading Skills

**32 Autonomous Trading Skills for Indian Equity and Derivatives Markets with Inter-Agent Communication**

## Overview

APEX is a complete autonomous trading system where agents **talk to each other** and **coordinate automatically**. When you import these skills, they form a self-organizing ecosystem that:

- **Auto-discovers** available agents
- **Auto-coordinates** workflows
- **Auto-communicates** via event bus
- **Auto-executes** trading strategies
- **Auto-learns** from performance
- **Auto-heals** by fixing errors autonomously

---

## What's Included (32 Skills)

### Core Orchestration
- **apex-core-orchestrator** - Central nervous system that coordinates all agents
- **apex-india-trading-central-command** - Master orchestrator for routing workflows
- **apex-state-sync** - State synchronization between agents and upstash

### Trading Execution
- **apex-live-order-executor** - Dhan Live Order Executor for actual trade placement
- **apex-live-order-monitor** - Monitors open positions, SL/Target, MTM P&L
- **apex-paper-trade-engine** - Paper trading simulation engine
- **apex-risk-veto-authority** - 6-gate risk validation before trade execution
- **apex-validator-gate** - Quality gate validating all inputs before execution

### Market Analysis
- **apex-india-vix-monitor** - Monitors India VIX from NSE (Security ID: 21)
- **apex-option-chain-monitor** - Polls NSE option chain for PCR, IV rank, GEX, OI
- **apex-market-regime-engine** - Classifies market as TRENDING_UP, TRENDING_DOWN, etc.
- **apex-sentiment-engine** - Scrapes news/social media for sentiment analysis
- **apex-global-macro-scanner** - Global macro intelligence (DXY, Fed rates, etc.)

### Learning & Evolution
- **apex-self-evolution-engine** - Auto-learning engine that evolves strategies
- **apex-performance-monitor** - Monitors Sharpe, Calmar, Sortino ratios
- **apex-strategy-validator** - Walk-forward backtesting validation
- **apex-system-health-monitor** - Watchdog agent monitoring all agents

### Risk Management
- **apex-rate-limiter** - Centralized rate limiting for all API calls

### Monitoring & Error Handling
- **apex-controller** - Master controller and documentation hub
- **apex-state-manager** - Section-based state manager preventing cronjob overruns
- **apex-error-monitor** - Watches for trigger execution failures
- **apex-fix-monitor** - Verifies error fixes have resolved issues
- **apex-fix-verifier** - Verifies code fixes resolved issues
- **apex-trading-monitor** - Real-time dashboard and HTML email reports
- **apex-tony-autonomous-dev** - Self-healing code fix agent

### GitHub Integration
- **apex-github-sync** - Syncs skills between local and GitHub

### Forex (Beta)
- **apex-forex-macro-engine** - Global macro scanner for forex
- **apex-forex-paper-engine** - Paper trading for currency pairs
- **apex-forex-performance** - Performance tracking for forex
- **apex-forex-risk-veto** - Risk veto for forex trades
- **apex-inr-signal-engine** - USD/INR signal generator

### Options
- **apex-options-strategy-engine** - Generates options spread signals

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APEX TRADING SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EVENT BUS (apex-core-orchestrator)               │   │
│  │              Publish/Subscribe - Inter-Agent Communication          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐           │
│         ▼                          ▼                          ▼           │
│  ┌─────────────┐          ┌─────────────┐            ┌─────────────┐      │
│  │   MARKET    │          │   SIGNAL    │            │  TRADING    │      │
│  │   ANALYSIS  │          │  GENERATION │            │  EXECUTION  │      │
│  │             │          │             │            │             │      │
│  │ • VIX       │─────────▶│ • Options   │───────────▶│ • Executor  │      │
│  │ • Regime    │          │ • Strategy  │            │ • Monitor   │      │
│  │ • Options   │          │ • Forex     │            │ • Risk Veto │      │
│  │ • Sentiment │          │             │            │             │      │
│  └─────────────┘          └─────────────┘            └─────────────┘      │
│                                    │                          │            │
│                                    ▼                          ▼            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LEARNING & OPTIMIZATION                          │   │
│  │              Self-Evolution + Performance Monitoring                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## How Agents Talk to Each Other

### Event Bus Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    APEX EVENT BUS                           │
├─────────────────────────────────────────────────────────────┤
│  AGENT 1 ──subscribes──┐                                    │
│  AGENT 2 ──subscribes──┼───→ EVENT: signal:generated       │
│  AGENT 3 ──subscribes──┘         ↓                         │
│  AGENT 4 ──subscribes───────────→ AUTO-EXECUTES           │
└─────────────────────────────────────────────────────────────┘
```

### Complete Communication Flow

```
1. India VIX Agent detects HIGH VOLATILITY
   └─→ Publishes: event("market:regime_changed", {"regime": "HIGH_VOL"})

2. Market Regime Agent receives event
   └─→ Updates risk parameters
   └─→ Publishes: event("risk:adjusted", {"max_position": 0.5})

3. Option Chain Agent generates signal
   └─→ Publishes: event("signal:generated", {"symbol": "NIFTY", "action": "BUY"})

4. Risk Veto Agent validates signal
   └─→ Checks against HIGH_VOL regime
   └─→ Publishes: event("signal:validated", {"approved": True})

5. Order Executor receives validated signal
   └─→ Places order automatically
   └─→ Publishes: event("trade:executed", {...})

6. Performance Monitor logs trade
   └─→ Updates P&L
   └─→ Triggers evolution if needed
```

### All Event Types

| Event | Triggered By | Consumed By | Action |
|-------|--------------|-------------|--------|
| `market:open` | Orchestrator @ 9:15 AM | All agents | Start daily workflows |
| `market:close` | Orchestrator @ 3:30 PM | All agents | End of day processing |
| `data:vix_updated` | India VIX Monitor | Regime Engine | Classify volatility |
| `market:regime_changed` | Regime Engine | Risk Manager | Adjust risk params |
| `signal:generated` | Signal Engine | Risk Veto | Validate trade |
| `signal:validated` | Risk Veto | Order Executor | Execute trade |
| `trade:executed` | Order Executor | Performance Monitor | Log trade |
| `trade:closed` | Order Monitor | Evolution Engine | Analyze & learn |
| `evolution:trigger` | Daily @ 3:30 PM | Self-Evolution | Adjust strategy weights |
| `sentiment:changed` | Sentiment Engine | Risk Veto | Crisis response |
| `error:trigger_failed` | Error Monitor | Fix Monitor | Auto-heal |

---

## Cronjobs (Automated Scheduling)

**7 Cronjobs** run during market hours (all times IST):

| Time | Schedule | Skill | Action |
|------|----------|-------|--------|
| 8:00 AM | `0 8 * * 1-5` | apex-india-trading-central-command | Pre-market setup |
| 9:15 AM | `15 9 * * 1-5` | apex-market-regime-engine | Classify regime at open |
| Every 5 min | `*/5 9-15 * * 1-5` | apex-core-orchestrator | Event coordination & monitoring |
| Hourly 9AM-2PM | `0 9-14 * * 1-5` | apex-options-strategy-engine | Generate trading signals |
| 3:30 PM | `30 15 * * 1-5` | apex-self-evolution-engine | Post-market learning |
| 3:40 PM | `40 15 * * 1-5` | apex-india-trading-central-command | EOD reconciliation |
| Sunday 8PM | `0 20 * * 0` | apex-system-health-monitor | Weekend system check |

### Market Hours (IST)
- **Pre-market:** 9:00 AM - 9:15 AM
- **Market Open:** 9:15 AM
- **Market Close:** 3:30 PM
- **Post-market:** 3:40 PM - 4:00 PM

---

## Quick Start

### Prerequisites

```bash
# Required
- Python 3.10+
- git
- Hermes Agent (or any AI agent that supports skills)

# Optional (for live trading)
- Dhan API account
- Telegram bot (for alerts)
```

### 1. Clone & Setup

```bash
git clone https://github.com/sn-sujay/apex-trading-skills.git
cd apex-trading-skills
python3 setup.py
```

The setup script automatically:
- Installs all 32 skills to `~/.hermes/skills/trading/`
- Creates `~/.apex/state.json` with template config
- Creates cache directories
- Sets up event bus files

### 2. Configure

```bash
# Copy and edit the environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

Required variables:
- `DHAN_CLIENT_ID` - Your Dhan API client ID
- `DHAN_ACCESS_TOKEN` - Your Dhan API access token
- `TELEGRAM_BOT_TOKEN` - Optional, for alerts
- `TELEGRAM_CHAT_ID` - Optional, for alerts
- `UPSTASH_REDIS_REST_URL` - Optional, for cloud state sync
- `UPSTASH_REDIS_REST_TOKEN` - Optional, for cloud state sync

### 3. Run Locally (Standalone)

```bash
# Run a specific skill directly
python3 ~/.hermes/skills/trading/apex-india-vix-monitor/fetch_vix.py
python3 ~/.hermes/skills/trading/apex-option-chain-monitor/fetch_option_chain.py

# Run orchestrator
python3 ~/.hermes/skills/trading/apex-core-orchestrator/orchestrator.py

# Run any skill
python3 ~/.hermes/skills/trading/<skill-name>/<script>.py
```

### 4. Setup Cronjobs

```bash
# In Hermes Agent or similar
schedule_cronjob(
    schedule="0 8 * * 1-5",
    prompt="APEX Pre-Market - Run apex-india-trading-central-command for pre-market setup",
    name="apex-pre-market",
    deliver="telegram"
)

schedule_cronjob(
    schedule="15 9 * * 1-5", 
    prompt="APEX Market Regime - Run apex-market-regime-engine to classify market",
    name="apex-market-regime",
    deliver="telegram"
)

schedule_cronjob(
    schedule="*/5 9-15 * * 1-5",
    prompt="APEX Core Orchestrator - Event coordination, intraday monitoring, signal generation",
    name="apex-orchestrator",
    deliver="telegram"
)

schedule_cronjob(
    schedule="0 9-14 * * 1-5",
    prompt="APEX Strategy Generation - Run apex-options-strategy-engine for signals",
    name="apex-strategy-gen",
    deliver="telegram"
)

schedule_cronjob(
    schedule="30 15 * * 1-5",
    prompt="APEX Self-Evolution - Run apex-self-evolution-engine for learning",
    name="apex-evolution-engine",
    deliver="telegram"
)

schedule_cronjob(
    schedule="40 15 * * 1-5",
    prompt="APEX EOD - Run apex-india-trading-central-command for reconciliation",
    name="apex-eod",
    deliver="telegram"
)

schedule_cronjob(
    schedule="0 20 * * 0",
    prompt="APEX Sunday Health - Run apex-system-health-monitor for system check",
    name="apex-sunday-health",
    deliver="telegram"
)
```

---

## State & Configuration

### State Files

| File | Location | Purpose |
|------|----------|---------|
| `state.json` | `~/.apex/state.json` | Main config, positions, trades |
| `orchestrator_state.json` | `~/.apex/orchestrator_state.json` | Workflow state |
| `event_bus.json` | `~/.apex/event_bus.json` | Event log |
| `rate_limits.json` | `~/.apex/rate_limits.json` | API rate limit tracking |

### Cache Files

| File | Location | Duration |
|------|----------|----------|
| `vix_cache.json` | `~/.apex/cache/` | 15 min |
| `option_chain_cache.json` | `~/.apex/cache/` | 5 min |
| `scrip_master.csv` | `~/.apex/cache/` | 7 days |

---

## Dhan API Security IDs

| Instrument | Security ID | Exchange | Segment |
|------------|-------------|----------|---------|
| INDIA VIX | 21 | NSE | INDEX |
| NIFTY | 13 | NSE | INDEX |
| BANKNIFTY | 25 | NSE | INDEX |
| FINNIFTY | 38 | NSE | INDEX |

---

## Rate Limits

### Dhan API
```python
DHAN_LIMITS = {
    "order_placement": {"max_per_second": 5, "max_per_minute": 100},
    "order_modification": {"max_per_second": 2, "max_per_minute": 50},
    "portfolio_requests": {"max_per_minute": 60},
}
```

### NSE
```python
NSE_LIMITS = {
    "india_vix": {"max_per_minute": 10, "min_interval_seconds": 10},
    "option_chain": {"max_per_minute": 5, "min_interval_seconds": 15},
}
```

### Trading
```python
TRADING_LIMITS = {
    "min_time_between_trades_seconds": 60,
    "max_trades_per_hour": 10,
    "max_trades_per_day": 30,
    "cooldown_after_loss_seconds": 300,
}
```

---

## Skill Usage Examples

### Run Individual Skills

```python
# In Hermes or any AI agent with skill loading

# Market Analysis
load_skill("apex-india-vix-monitor")
load_skill("apex-option-chain-monitor")
load_skill("apex-market-regime-engine")
load_skill("apex-sentiment-engine")

# Trading
load_skill("apex-live-order-executor")
load_skill("apex-live-order-monitor")
load_skill("apex-paper-trade-engine")
load_skill("apex-risk-veto-authority")

# Learning
load_skill("apex-self-evolution-engine")
load_skill("apex-performance-monitor")
load_skill("apex-strategy-validator")

# Orchestration
load_skill("apex-core-orchestrator")
load_skill("apex-india-trading-central-command")
```

### Direct Python Execution

```bash
# Fetch India VIX
python3 ~/.hermes/skills/trading/apex-india-vix-monitor/fetch_vix.py

# Fetch Option Chain  
python3 ~/.hermes/skills/trading/apex-option-chain-monitor/fetch_option_chain.py

# Search Scrip Master
python3 ~/.hermes/skills/trading/apex-controller/fetch_scrip_master.py RELIANCE

# Check State
cat ~/.apex/state.json

# View Logs
tail -f ~/.hermes/logs/apex*.log
```

---

## Autonomous Operation

### What Happens Automatically

**At 8:00 AM IST (Pre-Market):**
```
Central Command → Fetches VIX, Option Chain, Global Macros
                 → Updates state.json
                 → Sends pre-market summary
```

**At 9:15 AM IST (Market Open):**
```
Market Regime Engine → Classifies market as TRENDING/RANGING
                     → Publishes regime event
Risk Veto → Adjusts max position sizes based on regime
Orchestrator → Broadcasts market:open
```

**Every 5 Minutes (9:15 AM - 3:00 PM):**
```
Orchestrator → Checks all positions (MTM, SL, Target)
            → Monitors for exit signals
            → Processes any pending events
            → Coordinates inter-agent communication
```

**Hourly (9:00 AM - 2:00 PM):**
```
Options Strategy Engine → Generates new signals
                       → Publishes to event bus
Risk Veto → Validates each signal
Order Executor → Executes approved trades (if auto-execute enabled)
```

**At 3:30 PM IST (Market Close):**
```
Self-Evolution Engine → Analyzes day's performance
                      → Adjusts strategy weights
                      → Logs trade lessons
                      → Updates confidence scores
```

**At 3:40 PM IST (EOD):**
```
Central Command → Closes intraday positions
                → Compiles daily report
                → Updates state.json
                → Sends EOD summary
```

---

## Troubleshooting

### Check System Health

```bash
# List all cronjobs
list_cronjobs()

# Check state
cat ~/.apex/state.json

# Check event bus
cat ~/.apex/event_bus.json

# Check cache
ls -la ~/.apex/cache/

# View logs
tail -100 ~/.hermes/logs/apex*.log
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Rate limit errors | Check apex-rate-limiter status |
| State sync issues | Run apex-state-sync manually |
| Missing positions | Check apex-live-order-monitor |
| Strategy not generating | Check VIX and Option Chain caches |

---

## Directory Structure

```
apex-trading-skills/
├── README.md                 # This file
├── SETUP.md                  # Detailed setup guide
├── SCHEDULING.md             # Cronjob documentation
├── MEMORY_SHARING.md         # Inter-agent memory
├── .env.example              # Environment template
├── setup.py                  # Installation script
├── config/
│   └── state.template.json   # State file template
└── skills/
    └── trading/
        ├── apex-controller/
        ├── apex-core-orchestrator/
        ├── apex-error-monitor/
        ├── apex-fix-monitor/
        ├── apex-fix-verifier/
        ├── apex-forex-macro-engine/
        ├── apex-forex-paper-engine/
        ├── apex-forex-performance/
        ├── apex-forex-risk-veto/
        ├── apex-github-sync/
        ├── apex-global-macro-scanner/
        ├── apex-india-trading-central-command/
        ├── apex-india-vix-monitor/
        ├── apex-inr-signal-engine/
        ├── apex-live-order-executor/
        ├── apex-live-order-monitor/
        ├── apex-market-regime-engine/
        ├── apex-option-chain-monitor/
        ├── apex-options-strategy-engine/
        ├── apex-paper-trade-engine/
        ├── apex-performance-monitor/
        ├── apex-rate-limiter/
        ├── apex-risk-veto-authority/
        ├── apex-self-evolution-engine/
        ├── apex-sentiment-engine/
        ├── apex-state-manager/
        ├── apex-state-sync/
        ├── apex-strategy-validator/
        ├── apex-system-health-monitor/
        ├── apex-tony-autonomous-dev/
        ├── apex-trading-monitor/
        └── apex-validator-gate/
```

---

## License

MIT License - Use at your own risk. Trading involves substantial risk.

---

## Support

- For issues, check `~/.hermes/logs/apex*.log`
- State file: `~/.apex/state.json`
- Event bus: `~/.apex/event_bus.json`