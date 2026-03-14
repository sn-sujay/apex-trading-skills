---
name: apex-validator-gate
description: Quality gate validating all inputs before execution. Checks data quality, signal integrity.
tags: [apex, trading, validation, quality]
---

# APEX Validator Gate

## Purpose
Quality gate validating all data inputs before trading decisions.

## Validations
1. **Data Freshness** - Is market data < 5 min old?
2. **Signal Integrity** - All required fields present?
3. **Range Checks** - Are values within expected bounds?
4. **Consistency** - No conflicting signals

## Gate Output
```json
{
  "validation_result": {
    "passed": true,
    "checks": {
      "data_freshness": true,
      "signal_integrity": true,
      "range_checks": true,
      "consistency": true
    },
    "errors": []
  }
}
```

## Action
If validation fails:
- Block downstream execution
- Log validation error
- Alert central command
