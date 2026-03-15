---
name: apex-pre-market-briefing
description: Pre-market briefing at 8 AM IST - scans fresh overnight news, global markets update, and generates trading strategy for the day. Especially focuses on Indian banking sector and market-moving news.
triggers:
  - schedule: "0 8 * * 1-5"  # 08:00 IST weekdays
tags: [apex, trading, pre-market, news, banking]
---

# APEX Pre-Market Briefing

## Purpose
Comprehensive morning briefing at 8:00 AM IST before market opens. Scans fresh news, updates from weekend, and provides actionable strategy for the trading day.

## When to Use
- Weekdays at 8:00 AM IST (before market opens)
- Reads weekend_scan data for context
- Fetches fresh overnight news

## What It Does

### 1. Read Weekend Context
- Read weekend_scan.next_week_outlook
- Read weekend_scan.actionable_notes
- Get global markets data from weekend

### 2. Fetch Fresh News (Overnight + Morning)
- Indian market news (MoneyControl, BS, ET)
- Banking sector news (especially NBFC, PSU banks)
- Global markets overnight (US close, Asia open)
- Fed/RBI policy updates

### 3. Analyze Banking Sector
- Check for any RBI notifications
- Check for major bank results/announcements
- Check for NBFC news
- Check for regulatory updates

### 4. Generate Trading Strategy
- Combine weekend context + fresh news
- Determine bullish/bearish/neutral stance
- Generate specific strategy recommendations

### 5. Update State & Alert
- Update pre_market_briefing in state.json
- Send detailed Telegram alert

## Output: Telegram Alert
```
📈 PRE-MARKET BRIEFING - [DATE]

🌍 GLOBAL CONTEXT (Weekend):
- S&P 500: -0.61%
- Outlook: BEARISH

📰 FRESH NEWS:
- [News item 1]
- [News item 2]

🏦 BANKING SECTOR:
- [Banking news]

🎯 TODAY'S STRATEGY:
- Overall: [BULLISH/BEARISH/NEUTRAL]
- Recommended: [Strategy]
- Risk Level: [LOW/MEDIUM/HIGH]
```

## State Keys
```json
{
  "pre_market_briefing": {
    "generated_at": "2026-03-16T08:00:00",
    "weekend_outlook": "BEARISH",
    "fresh_news": [...],
    "banking_news": [...],
    "today_strategy": "...",
    "risk_level": "MEDIUM"
  }
}
```

## Related Skills
- apex-weekend-scanner (provides weekend context)
- apex-india-trading-central-command (executes trades)
- apex-market-regime-engine (validates regime)