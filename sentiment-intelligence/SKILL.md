---
name: sentiment-intelligence
description: 'Real-time Indian market sentiment pipeline from news and social media.'
---

# Sentiment Intelligence Engine

## Role
Real-time Indian market sentiment pipeline that scrapes Economic Times, MoneyControl, NSE/BSE announcements, Twitter/X, and StockTwits every 5 minutes. NLP-classifies each item as bullish/bearish/neutral with confidence score. Aggregates into a composite sentiment score and writes to Nebula memory for use by the regime engine.

## Capabilities
- Scrapes Economic Times Markets, MoneyControl News, NSE/BSE corporate announcements
- Twitter/X sentiment on $NIFTY, $BANKNIFTY, Indian market hashtags
- StockTwits stream for NSE-listed instruments
- NLP classification: bullish / bearish / neutral with confidence score
- Composite sentiment index: -100 (extreme fear) to +100 (extreme greed)
- Sector-level sentiment breakdown (IT, Banks, Auto, Pharma, Metals)
- FII/DII activity sentiment from press releases
- Breaking news detection with urgency scoring

## Memory Keys Written
| Key | Description |
|---|---|
| `SENTIMENT_COMPOSITE` | Overall market sentiment score (-100 to +100) |
| `SENTIMENT_BREAKDOWN` | Per-sector sentiment scores |
| `NEWS_ALERTS` | High-urgency breaking news items (score > 80) |
| `SOCIAL_SENTIMENT` | Twitter/X + StockTwits aggregated score |
| `FII_SENTIMENT` | FII/DII activity sentiment signal |

## Trigger
- Runs every 5 minutes during market hours
- Runs every 30 minutes pre-market (08:00–9:15 IST) and post-market (15:30–17:00 IST)

## Integration
- Feeds data to: `india-market-regime-engine`, `global-macro-intelligence-scanner`
- Part of: APEX Trading System

## Memory Protocol (MANDATORY)
NEVER call manage_memories. Use Upstash Redis REST API directly.
Write DB1: POST UPSTASH_REDIS_REST_URL/pipeline Authorization Bearer UPSTASH_REDIS_REST_TOKEN body is array with SET command array containing key value EX TTL
Writes: SENTIMENT_SNAPSHOT to DB1 TTL 360s format timestamp:ISO|score:0.35|label:NEUTRAL_BULLISH|conviction:MEDIUM|top_themes:Fed_pause,IT_earnings,FII_buying
See docs/UPSTASH_MEMORY_GUIDE.md