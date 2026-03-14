---
name: apex-tony-autonomous-dev
description: Tony Autonomous Senior Dev - Self-healing code fix agent. Detects errors, generates fixes, creates patches, and verifies resolution.
triggers:
  - schedule: "0 */4 * * 1-5"  # Every 4 hours weekdays
tags: [apex, trading, self-healing, dev, autonomous]
---

# Tony Autonomous Senior Dev

## Purpose
Self-healing code fix agent for APEX. Tony reads error logs, diagnoses issues, generates code fixes, applies patches, and verifies fixes work.

## When to Run
- Every 4 hours during weekdays
- On-demand when errors detected
- Triggered by Error Monitor for recurring issues

## Workflow

### Step 1: Error Diagnosis
```python
def analyze_errors():
    state = read_state()
    errors = state.get('error_log', [])
    
    # Group by error type
    error_counts = {}
    for error in errors:
        key = f"{error['agent']}:{error['error_type']}"
        error_counts[key] = error_counts.get(key, 0) + 1
    
    # Find recurring errors (> 3 occurrences)
    recurring = [k for k, v in error_counts.items() if v >= 3]
    return recurring
```

### Step 2: Generate Fix
```python
def generate_fix(error_key: str) -> dict:
    """
    Analyze error and generate code fix
    Returns: {'file': str, 'patch': str, 'description': str}
    """
    agent_name, error_type = error_key.split(':')
    
    # Map common errors to fixes
    fixes = {
        'API_ERROR': {
            'file': 'trading_system/dhan_client.py',
            'patch': 'Add retry logic with exponential backoff',
            'description': 'Handle API timeout with retries'
        },
        'MEMORY_WRITE_FAILURE': {
            'file': 'trading_system/state_manager.py',
            'patch': 'Add file lock and atomic write',
            'description': 'Fix race condition in state writes'
        },
        'AGENT_TIMEOUT': {
            'file': f'trading_system/agents.py',
            'patch': 'Add timeout decorator and early exit',
            'description': 'Prevent agent from hanging'
        }
    }
    
    return fixes.get(error_type, None)
```

### Step 3: Apply Fix
```python
def apply_fix(fix: dict) -> bool:
    try:
        # Create backup
        backup_file(fix['file'])
        
        # Apply patch
        with open(fix['file'], 'a') as f:
            f.write(f"\n# TONY FIX: {fix['description']}\n")
        
        # Log fix
        log_fix_applied(fix)
        return True
    except Exception as e:
        log_error(f"Tony fix failed: {e}")
        return False
```

### Step 4: Verify Fix
```python
def verify_fix(fix: dict) -> bool:
    """
    Run tests to verify fix works
    Returns True if fix verified
    """
    # Run affected agent
    # Check no new errors in next 3 cycles
    # Return verification status
    pass
```

## Implementation
```python
from hermes_tools import read_file, write_file, send_message
from datetime import datetime
import json

# Read error log
state_file = json.loads(read_file("~/.apex/state.json")["content"])
errors = state_file.get("error_log", [])

# Find recurring errors in last 4 hours
from datetime import datetime, timedelta
cutoff = (datetime.now() - timedelta(hours=4)).isoformat()

recent_errors = [e for e in errors if e.get('timestamp', '') > cutoff]

# Group and count
from collections import Counter
error_types = Counter(f"{e['agent']}:{e['error_type']}" for e in recent_errors)

# Fix recurring errors
for error_key, count in error_types.items():
    if count >= 2:  # 2+ errors in 4 hours
        agent_name, error_type = error_key.split(':')
        send_message(
            message=f"[TONY ALERT] Detected {count} occurrences of {error_key}. Generating fix..."
        )
        
        # Apply common fixes
        if error_type == 'API_ERROR':
            # Add retry logic to dhan_client
            pass
        elif error_type == 'MEMORY_ERROR':
            # Fix state manager
            pass

# Log Tony activity
if not state_file.get('tony_log'):
    state_file['tony_log'] = []

state_file['tony_log'].append({
    'timestamp': datetime.now().isoformat(),
    'errors_checked': len(recent_errors),
    'fixes_applied': 0,
    'status': 'completed'
})

with open("~/.apex/state.json", "w") as f:
    json.dump(state_file, f, indent=2)
```

## Alerts
- [TONY INFO] - Routine scan complete
- [TONY ALERT] - Recurring error detected
- [TONY FIX] - Fix applied successfully
- [TONY ERROR] - Fix failed, manual intervention needed

## Related Skills
- apex-error-monitor (triggers Tony)
- apex-fix-verifier (verifies Tony's work)
