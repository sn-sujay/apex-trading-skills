---
name: apex-performance-monitor
description: Monitors live trade performance - Sharpe, Calmar, Sortino ratios, decay detection.
triggers:
  - schedule: "0 3-10 * * 1-5"  # Hourly during market
tags: [apex, trading, performance, metrics]
---

# APEX Performance Monitor

## Purpose
Real-time performance monitoring with metrics:
- Sharpe Ratio
- Calmar Ratio
- Sortino Ratio
- Win rate
- Profit factor
- Strategy decay detection

## Decay Detection
Flags strategies underperforming vs 30-day baseline:
```python
if current_win_rate < baseline_win_rate * 0.8:
    decay_alerts.append(f"{strategy}: Significant decay detected")
```

## Output
```json
{
  "performance_metrics": {
    "sharpe_ratio": 1.45,
    "calmar_ratio": 2.1,
    "sortino_ratio": 1.8,
    "win_rate": 0.58,
    "profit_factor": 1.72,
    "max_drawdown": -3.2,
    "decay_alerts": []
  }
}
```

## Alerts
- Decay alerts via Telegram
- Performance summary at EOD
