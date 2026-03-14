---
name: apex-risk-veto-authority
description: 6-gate risk veto system before trade execution. Checks regime, IV, daily loss, position limits.
tags: [apex, trading, risk, veto]
---

# APEX Trading Risk Veto Authority

## Purpose
6-gate risk veto system that must approve every trade before execution.

## The 6 Gates
1. **Market Regime Gate** - No trades in HIGH_VOL or EVENT_DRIVEN regimes
2. **Daily Loss Gate** - Stop if daily loss > 2%
3. **Per-Trade Risk Gate** - Max 0.5% risk per trade
4. **Position Limit Gate** - Max 3 concurrent positions
5. **IV Gate** - Extra caution if India VIX > 18
6. **Confidence Gate** - Min 65% confidence required

## Output Format
```json
{
  "veto_result": {
    "approved": true,
    "veto_reasons": [],
    "gates_passed": 6,
    "risk_assessment": "APPROVED",
    "timestamp": "2026-03-14T10:30:00+05:30"
  }
}
```

## Veto Actions
- If vetoed: Signal blocked, alert sent
- Circuit breaker: Activate KILL_SWITCH if daily loss > 2%

## Implementation
```python
# Check all 6 gates
gates = {
    'regime': regime != 'EVENT_DRIVEN' and regime != 'HIGH_VOL',
    'daily_loss': daily_pnl > -2.0,
    'per_trade_risk': trade_risk <= 0.5,
    'position_limit': len(positions) < 3,
    'iv': india_vix <= 18,
    'confidence': confidence >= 65
}

approved = all(gates.values())
veto_reasons = [k for k, v in gates.items() if not v]
```
