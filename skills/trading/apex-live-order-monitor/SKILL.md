---
name: apex-live-order-monitor
description: Live order monitoring and execution tracking for Dhan API.
tags: [apex, trading, execution, orders]
---

# APEX Live Order Monitor

## Purpose
Tracks live orders through Dhan API:
- New order placement
- Order status updates
- Fill notifications
- Slippage tracking

## Order States
- PENDING
- OPEN
- PARTIAL_FILL
- COMPLETE_FILL
- CANCELLED
- REJECTED

## Output
```json
{
  "orders": [
    {
      "order_id": "O001",
      "status": "COMPLETE_FILL",
      "filled_qty": 15,
      "avg_price": 57250,
      "slippage": 2.5
    }
  ]
}
```

## Note
Requires Dhan API credentials.
