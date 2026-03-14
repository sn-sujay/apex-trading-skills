---
name: apex-state-sync
description: Unified state synchronization system for APEX. Syncs state across Upstash Redis, Hermes memory, and file-based storage with automatic fallback and redundancy.
triggers:
  - on_state_change: always
tags: [apex, trading, sync, state, upstash, redis]
---

# APEX State Sync Manager

## Purpose
Ensures APEX state is synchronized across multiple storage backends for redundancy and reliability.

## Storage Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│  STORAGE HIERARCHY (Priority Order)                     │
├─────────────────────────────────────────────────────────┤
│  1. Upstash Redis (Cloud)                              │
│     ├── Fastest access                                  │
│     ├── Persists across restarts                         │
│     └── Shared across multiple agents                    │
│                                                         │
│  2. Hermes Memory (Session)                            │
│     ├── In-memory caching                               │
│     ├── Fast for frequent reads                         │
│     └── Lost on restart                                 │
│                                                         │
│  3. File-Based (Local)                                 │
│     ├── Always available                                │
│     ├── Backup/fallback                                 │
│     └── Source of truth if others fail                  │
└─────────────────────────────────────────────────────────┘
```

## Configuration

### Upstash Setup (Optional but Recommended)

Create `~/.apex/upstash_config.json`:

```json
{
  "url": "https://your-redis-url.upstash.io",
  "token": "your-upstash-token",
  "enabled": true,
  "timeout_seconds": 5,
  "retry_attempts": 3
}
```

Get free Upstash account at: https://upstash.com

## Implementation

```python
"""
APEX State Sync Manager
Unified storage across Upstash, Hermes Memory, and File
"""

import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

# Try to import Upstash client
try:
    import requests
    HAS_REQUESTS = True
except:
    HAS_REQUESTS = False

# Try to import Hermes tools
try:
    from hermes_tools import memory
    HAS_HERMES_MEMORY = True
except:
    HAS_HERMES_MEMORY = False


class ApexStateSync:
    """
    Unified state manager with multi-backend sync
    """
    
    def __init__(self):
        self.state_dir = os.path.expanduser("~/.apex")
        self.state_file = os.path.join(self.state_dir, "state.json")
        self.cache_file = os.path.join(self.state_dir, "state_cache.json")
        self.sync_log = os.path.join(self.state_dir, "sync.log")
        
        # Load configuration
        self.upstash_config = self._load_upstash_config()
        
        # In-memory cache
        self._cache = {}
        self._cache_timestamp = None
        
        # Initialize
        self._ensure_directories()
        
    def _load_upstash_config(self) -> dict:
        """Load Upstash configuration"""
        config_file = os.path.join(self.state_dir, "upstash_config.json")
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            return {"enabled": False}
    
    def _ensure_directories(self):
        """Ensure state directories exist"""
        os.makedirs(self.state_dir, exist_ok=True)
    
    # ============ UPSTASH REDIS OPERATIONS ============
    
    def _upstash_get(self, key: str) -> Optional[Any]:
        """Get value from Upstash Redis"""
        if not self.upstash_config.get("enabled") or not HAS_REQUESTS:
            return None
        
        try:
            url = f"{self.upstash_config['url']}/get/{key}"
            headers = {"Authorization": f"Bearer {self.upstash_config['token']}"}
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=self.upstash_config.get("timeout_seconds", 5)
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("result"):
                    # Parse pipe-delimited string back to dict
                    return self._parse_pipe_string(result["result"])
            
            return None
            
        except Exception as e:
            self._log_sync(f"Upstash GET error: {e}", level="ERROR")
            return None
    
    def _upstash_set(self, key: str, value: Any) -> bool:
        """Set value in Upstash Redis"""
        if not self.upstash_config.get("enabled") or not HAS_REQUESTS:
            return False
        
        try:
            # Convert dict to pipe-delimited string
            pipe_string = self._dict_to_pipe_string(value)
            
            url = f"{self.upstash_config['url']}/set/{key}/{pipe_string}"
            headers = {"Authorization": f"Bearer {self.upstash_config['token']}"}
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.upstash_config.get("timeout_seconds", 5)
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self._log_sync(f"Upstash SET error: {e}", level="ERROR")
            return False
    
    def _upstash_delete(self, key: str) -> bool:
        """Delete key from Upstash Redis"""
        if not self.upstash_config.get("enabled") or not HAS_REQUESTS:
            return False
        
        try:
            url = f"{self.upstash_config['url']}/del/{key}"
            headers = {"Authorization": f"Bearer {self.upstash_config['token']}"}
            
            response = requests.get(url, headers=headers, timeout=5)
            return response.status_code == 200
            
        except:
            return False
    
    # ============ HERMES MEMORY OPERATIONS ============
    
    def _hermes_get(self, key: str) -> Optional[Any]:
        """Get value from Hermes memory"""
        if not HAS_HERMES_MEMORY:
            return None
        
        try:
            # Use Hermes memory tool
            result = memory.read(key=key)
            if result and result.get("value"):
                return json.loads(result["value"])
        except:
            pass
        
        return None
    
    def _hermes_set(self, key: str, value: Any) -> bool:
        """Set value in Hermes memory"""
        if not HAS_HERMES_MEMORY:
            return False
        
        try:
            memory.store(key=key, value=json.dumps(value))
            return True
        except:
            return False
    
    # ============ FILE OPERATIONS ============
    
    def _file_get(self, key: str = None) -> dict:
        """Get state from file"""
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            if key:
                return state.get(key)
            return state
            
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def _file_set(self, key: str, value: Any) -> bool:
        """Set value in file"""
        try:
            state = self._file_get()
            state[key] = value
            state["_last_updated"] = datetime.now().isoformat()
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            return True
            
        except Exception as e:
            self._log_sync(f"File SET error: {e}", level="ERROR")
            return False
    
    def _file_set_full(self, state: dict) -> bool:
        """Write full state to file"""
        try:
            state["_last_updated"] = datetime.now().isoformat()
            
            # Create backup
            if os.path.exists(self.state_file):
                backup_file = f"{self.state_file}.backup.{int(time.time())}"
                os.rename(self.state_file, backup_file)
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            return True
            
        except Exception as e:
            self._log_sync(f"File full write error: {e}", level="ERROR")
            return False
    
    # ============ UNIFIED OPERATIONS ============
    
    def get(self, key: str, fallback: Any = None) -> Any:
        """
        Get value with fallback chain:
        1. Try Hermes memory (fastest)
        2. Try Upstash (shared)
        3. Try file (reliable)
        """
        # 1. Check memory cache
        if key in self._cache:
            return self._cache[key]
        
        # 2. Try Hermes memory
        value = self._hermes_get(key)
        if value is not None:
            self._cache[key] = value
            return value
        
        # 3. Try Upstash
        value = self._upstash_get(key)
        if value is not None:
            # Cache it in Hermes for next time
            self._hermes_set(key, value)
            self._cache[key] = value
            return value
        
        # 4. Try file
        value = self._file_get(key)
        if value is not None:
            # Sync to other backends
            self._sync_to_backends(key, value)
            self._cache[key] = value
            return value
        
        return fallback
    
    def set(self, key: str, value: Any, sync: bool = True) -> bool:
        """
        Set value and sync to all backends
        """
        success = []
        
        # 1. Set in memory cache
        self._cache[key] = value
        
        # 2. Set in Hermes memory
        if self._hermes_set(key, value):
            success.append("hermes")
        
        # 3. Set in Upstash
        if sync and self._upstash_set(key, value):
            success.append("upstash")
        
        # 4. Set in file (always)
        if self._file_set(key, value):
            success.append("file")
        
        # Log sync
        if success:
            self._log_sync(f"SET {key} → {','.join(success)}")
        
        return len(success) > 0
    
    def get_full_state(self) -> dict:
        """Get complete state from file (source of truth)"""
        return self._file_get()
    
    def set_full_state(self, state: dict) -> bool:
        """Write complete state to all backends"""
        # 1. Write to file
        if not self._file_set_full(state):
            return False
        
        # 2. Sync to Upstash (if enabled)
        if self.upstash_config.get("enabled"):
            self._upstash_set("apex_full_state", state)
        
        # 3. Update cache
        self._cache = state.copy()
        
        self._log_sync("Full state synced to all backends")
        return True
    
    def sync_all(self) -> dict:
        """
        Full sync: Ensure all backends have same state
        Returns sync report
        """
        file_state = self._file_get()
        upstash_state = self._upstash_get("apex_full_state") if self.upstash_config.get("enabled") else None
        hermes_state = self._hermes_get("apex_full_state")
        
        # Determine newest state (by timestamp if available)
        states = [
            ("file", file_state, file_state.get("_last_updated", "1970-01-01")),
        ]
        
        if upstash_state:
            states.append(("upstash", upstash_state, upstash_state.get("_last_updated", "1970-01-01")))
        
        if hermes_state:
            states.append(("hermes", hermes_state, hermes_state.get("_last_updated", "1970-01-01")))
        
        # Sort by timestamp (newest first)
        states.sort(key=lambda x: x[2], reverse=True)
        
        newest_source, newest_state, _ = states[0]
        
        # Sync to all backends
        sync_report = {"source": newest_source, "synced_to": []}
        
        if newest_source != "file":
            self._file_set_full(newest_state)
            sync_report["synced_to"].append("file")
        
        if self.upstash_config.get("enabled") and newest_source != "upstash":
            self._upstash_set("apex_full_state", newest_state)
            sync_report["synced_to"].append("upstash")
        
        if newest_source != "hermes":
            self._hermes_set("apex_full_state", newest_state)
            sync_report["synced_to"].append("hermes")
        
        self._log_sync(f"Full sync from {newest_source} to {','.join(sync_report['synced_to'])}")
        
        return sync_report
    
    # ============ UTILITY ============
    
    def _dict_to_pipe_string(self, data: dict) -> str:
        """Convert dict to pipe-delimited string for Upstash"""
        # Simple pipe-delimited format: key1=value1|key2=value2
        pairs = []
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                v = json.dumps(v)
            pairs.append(f"{k}={v}")
        return "|".join(pairs)
    
    def _parse_pipe_string(self, pipe_string: str) -> dict:
        """Parse pipe-delimited string back to dict"""
        result = {}
        for pair in pipe_string.split("|"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                # Try to parse as JSON
                try:
                    v = json.loads(v)
                except:
                    pass
                result[k] = v
        return result
    
    def _log_sync(self, message: str, level: str = "INFO"):
        """Log sync operation"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\\n"
        
        with open(self.sync_log, 'a') as f:
            f.write(log_entry)
    
    def get_sync_status(self) -> dict:
        """Get current sync status"""
        return {
            "upstash_enabled": self.upstash_config.get("enabled", False),
            "hermes_available": HAS_HERMES_MEMORY,
            "file_state_exists": os.path.exists(self.state_file),
            "cache_keys": len(self._cache),
            "sync_log_entries": sum(1 for _ in open(self.sync_log)) if os.path.exists(self.sync_log) else 0
        }


# Global instance
_state_sync = None

def get_state_sync() -> ApexStateSync:
    """Get or create global state sync instance"""
    global _state_sync
    if _state_sync is None:
        _state_sync = ApexStateSync()
    return _state_sync


# Convenience functions
def state_get(key: str, fallback: Any = None) -> Any:
    """Get state value"""
    return get_state_sync().get(key, fallback)

def state_set(key: str, value: Any, sync: bool = True) -> bool:
    """Set state value"""
    return get_state_sync().set(key, value, sync)

def state_get_full() -> dict:
    """Get full state"""
    return get_state_sync().get_full_state()

def state_set_full(state: dict) -> bool:
    """Set full state"""
    return get_state_sync().set_full_state(state)

def state_sync_all() -> dict:
    """Force sync across all backends"""
    return get_state_sync().sync_all()


def main():
    """Test sync system"""
    print("="*70)
    print("APEX STATE SYNC MANAGER")
    print("="*70)
    
    sync = get_state_sync()
    
    # Show status
    status = sync.get_sync_status()
    print("\\nSync Status:")
    for k, v in status.items():
        print(f"  {k}: {v}")
    
    # Test operations
    print("\\nTesting sync operations...")
    
    # Test set
    result = state_set("test_key", {"value": 123, "timestamp": datetime.now().isoformat()})
    print(f"  SET test_key: {result}")
    
    # Test get
    value = state_get("test_key")
    print(f"  GET test_key: {value}")
    
    # Test full sync
    report = state_sync_all()
    print(f"  Full sync: {report}")
    
    print("\\n✅ State sync system ready")


if __name__ == "__main__":
    main()
```

## Usage

```python
# In your skills
from apex_state_sync import state_get, state_set, state_get_full

# Get value (auto-fetches from best available backend)
india_vix = state_get("india_vix", default={"current": 15.0})

# Set value (auto-syncs to all backends)
state_set("last_trade", {"symbol": "NIFTY", "pnl": 500})

# Get full state
full_state = state_get_full()

# Force sync
sync_report = state_sync_all()
```

## Auto-Sync on State Changes

The sync manager automatically:
1. Writes to file (always works)
2. Syncs to Upstash (if configured)
3. Caches in Hermes memory (if available)

## Sync Priority

**Read Order:**
1. Hermes memory (fastest)
2. Upstash Redis (shared)
3. File (reliable)

**Write Order:**
1. File (synchronous)
2. Upstash (async)
3. Hermes memory (async)

## Related Skills
- All apex-* skills (use this for state management)
- apex-core-orchestrator (coordinates state updates)
