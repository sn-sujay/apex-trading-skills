---
name: apex-fix-verifier
description: APEX Fix Verifier - Verifies Tony's code fixes resolved issues by monitoring next 3 cycles.
triggers:
  - schedule: "0 */4 * * 1-5"
tags: [apex, trading, verification, fix, tony]
---

# APEX Fix Verifier

## Purpose
Verifies that Tony's code fixes actually resolved the issues. Monitors for 3 cycles after each fix.

## Workflow
```
Tony Applies Fix → Fix Verifier checks next 3 cycles
       ↓
   Fixed? 
   /     \
  YES    NO (3+ attempts)
  ↓       ↓
Log    Escalate to manual
```

## Checks
After Tony applies a fix, verify:
1. Same error does not recur in next 3 cycles
2. Agent runs successfully without exceptions
3. State updates correctly
4. No new errors introduced

## Implementation
```python
class FixVerifier(BaseAgent):
    def run(self):
        state = self.state_mgr.read_state()
        
        # Get pending fixes
        pending_fixes = state.get('pending_fixes', [])
        
        for fix in pending_fixes:
            fix_time = datetime.fromisoformat(fix['applied_at'])
            cycles_since = self.get_cycles_since(fix_time)
            
            if cycles_since >= 3:
                # Check if error recurred
                errors_since = self.get_errors_since(fix_time)
                same_errors = [e for e in errors_since 
                              if e['agent'] == fix['agent'] 
                              and e['error_type'] == fix['error_type']]
                
                if not same_errors:
                    # Fix verified!
                    self.mark_fix_verified(fix)
                    send_alert(f"✅ Fix verified: {fix['description']}", "INFO")
                else:
                    # Fix failed - escalate
                    self.escalate_fix_failure(fix, same_errors)
                    send_alert(f"❌ Fix FAILED after 3 attempts: {fix['description']}", "CRITICAL")
```

## Output
- Fix status: VERIFIED / FAILED / PENDING
- Verification logs
- Escalation alerts for failed fixes

## Related Skills
- apex-tony-autonomous-dev
- apex-error-monitor
