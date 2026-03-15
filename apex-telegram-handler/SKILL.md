---
name: apex-telegram-handler
description: Handles polished Telegram messages and two-way communication. Processes incoming commands like STATUS, HELP, STOP, START.
triggers:
  - schedule: "*/5 * * * *"  # Every 5 minutes - check for messages
  - manual: telegram_command
tags: [apex, telegram, notifications, communication]
---

# APEX Telegram Handler

## Purpose
Send polished formatted messages and handle two-way communication via Telegram.

## Message Types

### 1. Pre-Market Briefing
- VIX with color-coded emoji
- Regime classification
- Sentiment score
- News summary

### 2. Signal Generated
- Strategy name
- Symbol (BANKNIFTY/BANKEX)
- Legs with strikes
- Entry, Stop Loss, Target
- Confidence score
- Reasoning

### 3. Trade Executed (Paper)
- Confirmation with [PAPER] tag
- Position details
- Entry time
- Status

### 4. Position Update
- Current MTM P&L with percentage
- Profit/Loss indicator
- Target/Stop status

### 5. Trade Exit
- Final P&L
- Exit reason
- Duration

### 6. EOD Report
- Total trades
- Win/Loss count
- Net P&L
- Key insights

## Commands (Two-Way Communication)

| Command | Description |
|---------|-------------|
| `STATUS` or `ST` | Current positions, P&L, VIX |
| `SUMMARY` or `EOD` | Today's trading summary |
| `SIGNALS` or `SIG` | Active signals |
| `VIX` or `REGIME` | Current VIX and regime |
| `PNL` | Profit/Loss breakdown |
| `STOP` or `PAUSE` | Pause all trading |
| `START` or `RESUME` | Resume trading |
| `RESET` or `CLEAR` | Reset daily counters |
| `HELP` or `?` | Show available commands |

## Usage

### Send a message:
```bash
python3 ~/.hermes/skills/trading/apex-telegram-handler/telegram_bot.py send "Test message"
```

### Check for incoming commands:
```bash
python3 ~/.hermes/skills/trading/apex-telegram-handler/telegram_bot.py check
```

### Test message formats:
```bash
python3 ~/.hermes/skills/trading/apex-telegram-handler/telegram_bot.py test
```

## Cron Job for Message Checking
Run every 5 minutes to check for new Telegram commands:
```
*/5 * * * *
```

## Configuration
Telegram settings in ~/.apex/config.yaml:
```yaml
telegram:
  bot_token: 'YOUR_BOT_TOKEN'
  chat_id: 'YOUR_CHAT_ID'
```

## Features
- Polished ASCII border messages
- Emoji indicators for profit/loss
- Two-way command response
- Auto-pause/resume trading
- Status on demand