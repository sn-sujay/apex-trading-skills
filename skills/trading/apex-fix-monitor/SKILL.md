---
name: apex-fix-monitor
description: Verifies that error fixes have resolved issues. Checks next 3 cycles after fix.
tags: [apex, trading, fix, verification]
---

# APEX Fix Verifier

## Purpose
Verifies that fixes applied by the fix agent actually work.

## Workflow
1. After fix applied, monitor for 3 cycles
2. Check if same error recurs
3. If fixed: Mark resolved, log success
4. If broken: Escalate to CRITICAL, alert user

## Output
```json
{
  "fix_verification": {
    "error_id": "ERR001",
    "fix_applied": "2026-03-14T11:00:00",
    "cycles_checked": 3,
    "status": "VERIFIED_FIXED"
  }
}
```
