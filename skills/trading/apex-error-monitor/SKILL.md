---
name: apex-error-monitor
description: Watches for trigger execution failures. Classifies errors and delegates to fix agent.
triggers:
  - schedule: "0 * * * 1-5"  # Every hour weekdays
tags: [apex, trading, error, monitoring]
---

# APEX Error Monitor

## Purpose
Watches for trigger execution failures. Reads ERROR_LOG and HEALTH_STATUS every hour.

## Error Classification
- MEMORY_WRITE_FAILURE
- EMAIL_DELIVERY_FAILURE
- API_ERROR
- AGENT_TIMEOUT

## Workflow
1. Read error_log from state
2. Classify new errors
3. Track recurrence counts
4. Delegate to fix agent if needed
5. Escalate to CRITICAL if error recurs 3+ times

## Self-Healing Loop
```
[Error Detected] -> Error Monitor -> Fix Agent -> Verification
                                     (Tony)         (3 cycles)
```

## CRITICAL Escalation
Same error 3+ times without resolution:
- Send Telegram alert
- Log for manual review

## Output
```json
{
  "error_log": [
    {
      "timestamp": "2026-03-14T10:00:00",
      "agent": "option-chain-monitor",
      "error_type": "API_ERROR",
      "message": "Dhan API timeout",
      "recurrences": 1,
      "status": "open"
    }
  ]
}
```
