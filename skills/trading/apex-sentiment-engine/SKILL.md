---
name: apex-sentiment-engine
description: Scrapes news and social media for market sentiment analysis.
triggers:
  - schedule: "*/5 3-10 * * 1-5"  # Every 5 min during market hours
tags: [apex, trading, sentiment, news]
---

# APEX Sentiment Intelligence Engine

## Purpose
Aggregates market sentiment from:
- Economic Times headlines
- MoneyControl news
- Twitter/X sentiment
- StockTwits sentiment

## Scoring
- -1.0 (very bearish) to +1.0 (very bullish)
- Confidence score based on source reliability

## Output
```json
{
  "sentiment": {
    "india_sentiment": 0.25,
    "confidence": 65,
    "sources": {},
    "timestamp": "2026-03-14T10:00:00+05:30"
  }
}
```

## Implementation Note
Requires news API access. Currently in mock mode.
