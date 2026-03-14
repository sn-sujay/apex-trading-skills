---
name: apex-self-evolution-engine
description: Autonomous self-learning engine that evolves APEX trading strategies from real data and auto-implements institutional research features.
triggers:
  - schedule: "30 15 * * 1-5"  # 15:30 IST (post-market)
tags: [apex, trading, ml, autonomous, learning, evolution]
---

# APEX Self-Evolution Engine v2.0

## Purpose
Autonomous learning brain of APEX trading system. Continuously evolves by:
1. Performance Attribution - Analyzes every trade by strategy
2. Auto-Weight Adjustment - Updates strategy weights based on performance  
3. Weakness Detection - Identifies what's losing money
4. Auto-Implementation - Automatically implements fixes from institutional research
5. Strategy Decay Detection - Pauses underperforming strategies

## Learning Loop (Runs Daily at 3:30 PM IST)

```
LEARNING_CYCLE():
    1. INGEST today's trades
    2. CALCULATE performance metrics (Sharpe, Win Rate, Expectancy)
    3. DETECT weaknesses (large losses, breakeven waste, poor timing)
    4. ADJUST strategy weights
    5. SELECT features to auto-implement
    6. DELEGATE implementation to dev agent
    7. LOG all changes
```

## Auto-Implementation Priority Queue

| Priority | Feature | Trigger Condition |
|----------|---------|------------------|
| 1 | Trailing Stop Loss | >3 trades lost >0.5% |
| 2 | Breakeven Stop | >5 trades closed at breakeven |
| 3 | Session Win Filter | Morning win rate <30% |
| 4 | Expectancy Filter | Overall expectancy < 0.5 |
| 5 | Weekly Loss Limiter | Weekly P&L < -5% |
| 6 | Kelly Sizing | Win rate > 55% and stable |

## Implementation

See Python code in skill for full implementation.

## Auto-Implementation Schedule

- Daily at 15:30 IST: Performance analysis, weight adjustments
- Every 2 days: Auto-implement ONE feature (if conditions met)
- Weekly Friday: Deep strategy review

## Safety Limits

```python
AUTO_IMPLEMENTATION_RULES = {
    "max_per_week": 2,
    "require_paper_test": True,
    "paper_test_days": 3,
    "abort_if_drawdown": 0.05,
    "abort_if_consecutive_losses": 5
}
```
