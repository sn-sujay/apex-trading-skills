#!/usr/bin/env python3
"""
APEX State Sync Manager
Unified storage across Upstash, Hermes Memory, and File
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Optional, Any

# Optional imports
try:
    import requests
    HAS_REQUESTS = True
except:
    HAS_REQUESTS = False


class ApexStateSync:
    """Unified state manager with multi-backend sync"""
    
    def __init__(self):
        self.state_dir = os.path.expanduser("~/.apex")
        self.state_file = os.path.join(self.state_dir, "state.json")
        self.sync_log = os.path.join(self.state_dir, "sync.log")
        
        self.upstash_config = self._load_upstash_config()
        self._cache = {}
        
        os.makedirs(self.state_dir, exist_ok=True)
    
    def _load_upstash_config(self) -> dict:
        """Load Upstash configuration"""
        try:
            with open(os.path.join(self.state_dir, "upstash_config.json")) as f:
                return json.load(f)
        except:
            return {"enabled": False}
    
    def _upstash_get(self, key: str) -> Optional[Any]:
        """Get from Upstash Redis"""
        if not self.upstash_config.get("enabled") or not HAS_REQUESTS:
            return None
        
        try:
            url = f"{self.upstash_config['url']}/get/{key}"
            headers = {"Authorization": f"Bearer {self.upstash_config['token']}"}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("result"):
                    return json.loads(result["result"])
        except:
            pass
        
        return None
    
    def _upstash_set(self, key: str, value: Any) -> bool:
        """Set in Upstash Redis"""
        if not self.upstash_config.get("enabled") or not HAS_REQUESTS:
            return False
        
        try:
            url = f"{self.upstash_config['url']}/set/{key}/{json.dumps(value)}"
            headers = {"Authorization": f"Bearer {self.upstash_config['token']}"}
            response = requests.get(url, headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _file_get(self) -> dict:
        """Get state from file"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except:
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
            print(f"File SET error: {e}")
            return False
    
    def get(self, key: str, fallback: Any = None) -> Any:
        """Get value with fallback chain: Upstash -> File"""
        # Try Upstash first
        value = self._upstash_get(key)
        if value is not None:
            return value
        
        # Try file
        state = self._file_get()
        if key in state:
            return state[key]
        
        return fallback
    
    def set(self, key: str, value: Any) -> bool:
        """Set value and sync to all backends"""
        # Always set in file
        file_result = self._file_set(key, value)
        
        # Set in Upstash (async, don't wait)
        if self.upstash_config.get("enabled"):
            self._upstash_set(key, value)
        
        # Cache locally
        self._cache[key] = value
        
        return file_result
    
    def get_full_state(self) -> dict:
        """Get complete state"""
        return self._file_get()
    
    def set_full_state(self, state: dict) -> bool:
        """Write complete state"""
        try:
            state["_last_updated"] = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            # Sync to Upstash
            if self.upstash_config.get("enabled"):
                self._upstash_set("apex_full_state", state)
            
            return True
        except:
            return False
    
    def sync_all(self) -> dict:
        """Full sync across all backends"""
        file_state = self._file_get()
        
        # Sync to Upstash
        if self.upstash_config.get("enabled"):
            self._upstash_set("apex_full_state", file_state)
        
        return {"synced": True, "backends": ["file", "upstash" if self.upstash_config.get("enabled") else None]}


# Global instance
_sync = None

def get_sync():
    global _sync
    if _sync is None:
        _sync = ApexStateSync()
    return _sync

def state_get(key, fallback=None):
    return get_sync().get(key, fallback)

def state_set(key, value):
    return get_sync().set(key, value)

def state_get_full():
    return get_sync().get_full_state()

def state_set_full(state):
    return get_sync().set_full_state(state)

def state_sync_all():
    return get_sync().sync_all()
