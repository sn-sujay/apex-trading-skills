---
name: apex-state-sync
description: Section-based state manager that prevents cronjobs from overwriting each other. Each agent writes to its own namespace, enabling safe parallel execution.
triggers:
  - used_by: all_agents
tags: [apex, trading, state, sync, coordination]
---

# APEX State Manager

## Problem Solved

**BEFORE (Data Loss):**
```
8:00 Pre-market writes: {"margins": 100000}
8:05 Regime OVERWRITES with: {"regime": "BULLISH"}  ← Lost margins!
```

**AFTER (Each Agent Owns Its Section):**
```
8:00 Pre-market writes to: state["agents"]["apex-india-trading-central-command"]
8:05 Regime writes to: state["agents"]["apex-market-regime-engine"]

Result: Both sections exist! No data loss!
```

## State Structure

```json
{
  "_meta": {
    "version": "2.0",
    "last_updated": "2026-03-14T09:00:00"
  },
  "config": {},
  "agents": {
    "apex-pre-market": {
      "margins": 100000,
      "_last_updated": "08:00:00"
    },
    "apex-market-regime": {
      "regime": "BULLISH",
      "_last_updated": "08:05:00"
    },
    "apex-india-vix": {
      "current": 22.65,
      "_last_updated": "09:15:00"
    }
  },
  "shared": {
    "market_status": "OPEN",
    "trading_blocked": false
  }
}
```

## Usage in Skills

### Writing (Each Agent to Own Section)
```python
from apex_state_manager import agent_write

# Pre-market agent writes its data
agent_write("apex-india-trading-central-command", {
    "margins": 100000,
    "positions": 5,
    "status": "complete"
})
```

### Reading Own Data
```python
from apex_state_manager import agent_read

my_data = agent_read("apex-market-regime-engine")
print(my_data["regime"])  # "BULLISH"
```

### Reading Other Agent's Data
```python
# Regime agent checks if pre-market is ready
pre_market = agent_read("apex-india-trading-central-command")
if pre_market.get("status") == "complete":
    # Safe to proceed
    pass
```

### Shared Data (Coordination)
```python
from apex_state_manager import shared_write, shared_read

# Block trading
shared_write("trading_blocked", true)
shared_write("block_reason", "Extreme sentiment")

# Check elsewhere
if shared_read("trading_blocked"):
    print("Trading blocked!")
```

## Cronjob Coordination

### Heartbeat Pattern
```python
from apex_state_manager import cronjob_heartbeat

def run():
    cronjob_heartbeat("pre-market")
    # Do work...
    agent_write("apex-pre-market", {"status": "complete"})
```

### Dependency Check
```python
from apex_state_manager import check_dependency

def run():
    # Wait for pre-market to complete
    if not check_dependency("pre-market"):
        print("Pre-market not ready, skipping...")
        return
    
    # Safe to proceed
    pass
```

## File Locking

Uses `fcntl` for exclusive file access:
- Prevents concurrent write corruption
- Automatic unlock after write
- Safe across multiple cronjobs

## Related
- apex-core-orchestrator (higher-level coordination)
- apex-state-sync (Upstash integration)
