# APEX Setup Guide

Complete installation and setup guide for APEX Trading System.

---

## Prerequisites

```bash
# Required
- Python 3.10+
- git
- Hermes Agent (or any AI agent with skill loading)
- Dhan API account (for live trading)
```

---

## Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/sn-sujay/apex-trading-skills.git
cd apex-trading-skills

# Run setup script
python3 setup.py
```

The setup script will:
1. Copy all 32 skills to `~/.hermes/skills/trading/`
2. Create `~/.apex/` directory structure
3. Create `~/.apex/state.json` from template
4. Create cache directories
5. Set up event bus files
6. Display setup summary

---

## Option 2: Manual Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/sn-sujay/apex-trading-skills.git ~/apex-trading-skills
```

### Step 2: Copy Skills

```bash
# Copy all skills to Hermes skills directory
cp -r ~/apex-trading-skills/skills/trading/* ~/.hermes/skills/trading/

# Verify
ls ~/.hermes/skills/trading/ | grep ^apex- | wc -l
# Should output: 32
```

### Step 3: Create Directory Structure

```bash
mkdir -p ~/.apex/cache
mkdir -p ~/.apex/logs
chmod 755 ~/.apex
```

### Step 4: Copy State Template

```bash
cp ~/apex-trading-skills/config/state.template.json ~/.apex/state.json
```

### Step 5: Set Up Environment

```bash
# Copy example env file
cp ~/apex-trading-skills/.env.example ~/.apex/.env

# Edit with your credentials
nano ~/.apex/.env
```

---

## Configuration

### Environment Variables

Create `~/.apex/.env` or `~/.hermes/.env`:

```bash
# ===========================================
# REQUIRED (for live trading)
# ===========================================

# Dhan API Credentials
DHAN_CLIENT_ID=your_client_id_here
DHAN_ACCESS_TOKEN=your_access_token_here

# ===========================================
# OPTIONAL (for alerts)
# ===========================================

# Telegram Alerts
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# ===========================================
# OPTIONAL (for cloud sync)
# ===========================================

# Upstash Redis (state sync)
UPSTASH_REDIS_REST_URL=https://your-db.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token

# ===========================================
# OPTIONAL (for debugging)
# ===========================================

# Logging
APEX_LOG_LEVEL=INFO
APEX_DEBUG=false
```

### State File Configuration

Edit `~/.apex/state.json`:

```json
{
  "version": "2.0",
  "dhan_config": {
    "client_id": "YOUR_CLIENT_ID",
    "access_token": "YOUR_ACCESS_TOKEN"
  },
  "trading_config": {
    "auto_execute": false,
    "max_position_size": 50000,
    "max_loss_per_day": 10000,
    "max_trades_per_day": 10
  },
  "strategy_weights": {
    "BREAKOUT": 0.30,
    "MOMENTUM": 0.25,
    "MEAN_REVERSION": 0.20,
    "MTF_EMA": 0.15,
    "OPTION_SPREAD": 0.10
  },
  "notifications": {
    "telegram_enabled": true,
    "email_enabled": false
  }
}
```

---

## Quick Test (Before Trading)

### Test 1: Verify Skills Installed

```bash
ls ~/.hermes/skills/trading/ | grep ^apex-
# Should list 32 skills
```

### Test 2: Test API Connection

```bash
# Test Dhan API
python3 -c "
import requests
import os
import json

client_id = os.getenv('DHAN_CLIENT_ID', 'YOUR_CLIENT_ID')
token = os.getenv('DHAN_ACCESS_TOKEN', 'YOUR_TOKEN')

headers = {
    'Authorization': token,
    'Content-Type': 'application/json'
}

# Test fetching positions
resp = requests.get(
    'https://api.dhan.co/v2/positions',
    headers=headers
)
print('Status:', resp.status_code)
print('Response:', resp.text[:200])
"
```

### Test 3: Fetch India VIX

```bash
python3 ~/.hermes/skills/trading/apex-india-vix-monitor/fetch_vix.py

# Expected output:
# INDIA VIX: 15.23 (up 0.82)
# Classification: NORMAL
```

### Test 4: Fetch Option Chain

```bash
python3 ~/.hermes/skills/trading/apex-option-chain-monitor/fetch_option_chain.py

# Expected output:
# NIFTY Option Chain:
# PCR: 1.15
# Max Pain: 22500
# IV Rank: 45%
```

### Test 5: Check State

```bash
cat ~/.apex/state.json | python3 -m json.tool | head -30
```

---

## Setting Up Cronjobs

### Hermes Agent

```python
# In Hermes or any compatible agent
from hermes_tools import schedule_cronjob

# 1. Pre-market (8:00 AM)
schedule_cronjob(
    schedule="0 8 * * 1-5",
    name="apex-pre-market",
    prompt="""APEX Pre-Market Session Start (08:00 IST Mon-Fri).

Execute Central Command pre-market tasks:
1. Fetch India VIX (Security ID: 21)
2. Fetch global macro data (DXY, Fed rates)
3. Update option chain cache
4. Compile pre-market summary
5. Update state.json

Send summary via telegram.""",
    deliver="telegram"
)

# 2. Market regime (9:15 AM)
schedule_cronjob(
    schedule="15 9 * * 1-5",
    name="apex-market-regime",
    prompt="""APEX Market Regime Classification (09:15 IST).

Run apex-market-regime-engine to classify market as:
- TRENDING_UP
- TRENDING_DOWN  
- RANGING
- HIGH_VOLATILITY

Update risk parameters based on regime.
Publish regime event to event bus.""",
    deliver="telegram"
)

# 3. Orchestrator (every 5 min)
schedule_cronjob(
    schedule="*/5 9-15 * * 1-5",
    name="apex-orchestrator",
    prompt="""APEX Core Orchestrator - Event Coordination & Monitoring

Run apex-core-orchestrator every 5 minutes:
1. Check open positions (MTM, SL, Target triggers)
2. Process event queue from event bus
3. Every hour: Generate signals via apex-options-strategy-engine
4. Route signals through apex-risk-veto-authority
5. Execute approved trades via apex-live-order-executor
6. Monitor for errors, alert if any issues

Market hours only: 9:00 AM - 3:00 PM IST.""",
    deliver="telegram"
)

# 4. Strategy generation (hourly)
schedule_cronjob(
    schedule="0 9-14 * * 1-5",
    name="apex-strategy-gen",
    prompt="""APEX Strategy Generation (Hourly 09:00-14:00 IST).

Run apex-options-strategy-engine:
1. Fetch fresh option chain data
2. Analyze PCR, Max Pain, IV Rank, OI changes
3. Generate signals: BREAKOUT, MOMENTUM, MEAN_REVERSION
4. Assign confidence scores (0-100)
5. Publish to event bus for risk validation

Apply current strategy weights from state.json""",
    deliver="tagram"
)

# 5. Evolution (3:30 PM)
schedule_cronjob(
    schedule="30 15 * * 1-5",
    name="apex-evolution-engine",
    prompt="""APEX Self-Evolution Engine (15:30 IST Mon-Fri).

Run apex-self-evolution-engine:
1. Analyze today's trades (P&L by strategy)
2. Calculate Sharpe, Calmar, Sortino ratios
3. Compare to benchmarks, adjust strategy weights
4. Log [TRADE_LESSON] for each trade
5. Update confidence scores based on performance

Capital preservation priority.""",
    deliver="telegram"
)

# 6. EOD (3:40 PM)
schedule_cronjob(
    schedule="40 15 * * 1-5",
    name="apex-eod",
    prompt="""APEX EOD Reconciliation (15:40 IST Mon-Fri).

Execute Central Command EOD tasks:
1. Close all intraday positions
2. Calculate daily P&L
3. Compile session summary
4. Update state.json for next day
5. Send EOD report via telegram

Mark closed trades with [TRADE_LESSON].""",
    deliver="telegram"
)

# 7. Sunday health (Sunday 8 PM)
schedule_cronjob(
    schedule="0 20 * * 0",
    name="apex-sunday-health",
    prompt="""APEX Sunday Health Check (Sunday 20:00 IST).

Pre-week system verification:
1. Test Dhan API connection
2. Verify state.json integrity
3. Check all 32 skills present
4. Verify cache directories exist
5. Test event bus functionality

Send health report via telegram.""",
    deliver="telegram"
)
```

### Verify Cronjobs

```python
# List all scheduled jobs
list_cronjobs()
```

---

## Running Standalone (No Cronjobs)

### Run Individual Skills Directly

```bash
# Fetch India VIX
python3 ~/.hermes/skills/trading/apex-india-vix-monitor/fetch_vix.py

# Fetch Option Chain (NIFTY)
python3 ~/.hermes/skills/trading/apex-option-chain-monitor/fetch_option_chain.py

# Fetch Option Chain (BANKNIFTY)
python3 ~/.hermes/skills/trading/apex-option-chain-monitor/fetch_option_chain.py 25

# Search Scrip
python3 ~/.hermes/skills/trading/apex-controller/fetch_scrip_master.py RELIANCE

# Global Macro
python3 ~/.hermes/skills/trading/apex-global-macro-scanner/fetch_macro.py

# INR Signals
python3 ~/.hermes/skills/trading/apex-inr-signal-engine/fetch_inr.py
```

### Run Full Orchestrator

```bash
# Run orchestrator once
python3 ~/.hermes/skills/trading/apex-core-orchestrator/orchestrator.py
```

---

## Integration with Other Platforms

### For Other AI Agents

1. **Clone to agent's skills directory**
   ```bash
   cp -r apex-trading-skills/skills/trading/* <AGENT_SKILLS_PATH>/trading/
   ```

2. **Set environment variables**
   ```bash
   export DHAN_CLIENT_ID=your_client_id
   export DHAN_ACCESS_TOKEN=your_token
   ```

3. **Load skills as needed**
   - Each skill can be loaded independently
   - Skills communicate via event bus
   - State stored in `~/.apex/state.json`

### For Custom Trading Platforms

1. **Use as library**
   ```python
   import sys
   sys.path.insert(0, "~/.hermes/skills/trading")
   
   from apex_india_vix_monitor import fetch_vix
   from apex_option_chain_monitor import fetch_option_chain
   ```

2. **Read state**
   ```python
   import json
   with open("~/.apex/state.json") as f:
       state = json.load(f)
   ```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `python3 setup.py` or copy skills manually |
| `No such file: state.json` | Run `setup.py` or copy from `config/state.template.json` |
| API errors | Check credentials in `.env` file |
| Rate limiting | Wait 1 minute, check `~/.apex/rate_limits.json` |
| Cronjob not running | Check with `list_cronjobs()` |

### Debug Mode

```bash
# Enable debug logging
export APEX_DEBUG=true
export APEX_LOG_LEVEL=DEBUG

# Run with debug
python3 -u ~/.hermes/skills/trading/apex-core-orchestrator/orchestrator.py
```

### Check Logs

```bash
# View recent logs
tail -100 ~/.hermes/logs/apex*.log

# Search for errors
grep -i error ~/.hermes/logs/apex*.log | tail -20
```

---

## Directory Structure After Setup

```
~/.apex/
├── state.json              # Main config & state
├── event_bus.json          # Event log
├── orchestrator_state.json # Workflow state
├── rate_limits.json        # API rate limit tracking
├── cache/
│   ├── vix_cache.json      # India VIX cache
│   ├── option_chain_cache.json
│   └── scrip_master.csv    # NSE scrip master
└── logs/
    ├── apex-*.log          # Skill execution logs

~/.hermes/skills/trading/
├── apex-controller/
├── apex-core-orchestrator/
├── apex-error-monitor/
... (32 skills total)
```

---

## Next Steps

1. **Test with paper trading** - Set `auto_execute: false` in state.json
2. **Enable live trading** - Set `auto_execute: true` after testing
3. **Set up Telegram** - Get bot token from @BotFather
4. **Start with small positions** - Max ₹50,000 initially

---

## Safety Features

- **6-gate risk veto** before every trade
- **Max loss per day** limit
- **Position size limits**
- **Rate limiting** for API calls
- **Auto-execute toggle** in config
- **Event-driven architecture** for instant response