---
name: apex-weekend-scanner
description: Weekend market scanner - runs Saturday/Sunday to prepare for Monday. Scans global macro, news, weekend events, and updates state with pre-week briefing.
triggers:
  - schedule: "0 10 * * 6"   # Saturday 10 AM IST
  - schedule: "0 10 * * 0"   # Sunday 10 AM IST
  - schedule: "0 18 * * 0"   # Sunday 6 PM IST (pre-Monday)
tags: [apex, trading, weekend, macro, scanner]
---

# APEX Weekend Scanner

## Purpose
Scans global markets and news over the weekend to prepare APEX for Monday trading. Ensures the system has context about weekend events before Monday's pre-market run.

## When to Use
- Saturday 10:00 AM IST - Weekly scan
- Sunday 10:00 AM IST - Follow-up scan
- Sunday 6:00 PM IST - Pre-Monday briefing

## What It Does

### 1. Global Macro Scan
- US Markets (S&P 500, NASDAQ Friday close)
- DXY (Dollar Index)
- Fed futures / interest rate expectations
- Asia markets (Nikkei, Hang Seng openers)
- Crude Oil / Commodities
- Global bond yields

### 2. News Monitoring
- Major economic news from Friday-Sunday
- Geopolitical events
- Corporate earnings surprises
- RBI / SEBI policy updates

### 3. VIX Context
- Check if VIX moved over weekend (from Friday close)
- Estimate Monday gap expectations

### 4. State Update
- Write weekend_summary to state.json
- Update next_week_outlook (BULLISH/BEARISH/NEUTRAL)
- Set weekend_data_fresh: true
- Include actionable notes for Monday

## Output
Telegram alert with:
- Weekend macro summary
- Key events to watch Monday
- Recommended strategy bias
- State updated for Monday pre-market

## State Keys Written
```json
{
  "weekend_scan": {
    "last_scan": "2026-03-15T10:00:00",
    "scan_type": "SATURDAY_WEEKLY",
    "next_scan": "2026-03-15T18:00:00",
    "global_macro": {...},
    "news_summary": [...],
    "vix_context": {...},
    "next_week_outlook": "BULLISH",
    "actionable_notes": [...]
  }
}
```

## Related Skills
- apex-global-macro-intelligence-scanner (uses same data sources)
- apex-sentiment-intelligence-engine (news parsing)
- apex-india-trading-central-command (reads weekend_scan on Monday)