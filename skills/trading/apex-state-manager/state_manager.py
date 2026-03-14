#!/usr/bin/env python3
"""
APEX Section-Based State Manager
Prevents cronjobs from overwriting each other's data
Each agent writes to its own section
"""

import json
import os
import fcntl
import time
from datetime import datetime

class ApexStateManager:
    """
    Thread-safe, section-based state management
    Each agent writes to its own section without conflicts
    """
    
    def __init__(self):
        self.state_dir = os.path.expanduser("~/.apex")
        self.state_file = os.path.join(self.state_dir, "state.json")
        self.agents_dir = os.path.join(self.state_dir, "agents")
        
        # Create agents directory for per-agent state
        os.makedirs(self.agents_dir, exist_ok=True)
        
        # Initialize main state file if doesn't exist
        self._init_state_file()
    
    def _init_state_file(self):
        """Initialize state file with proper structure"""
        if not os.path.exists(self.state_file):
            initial_state = {
                "_meta": {
                    "version": "2.0",
                    "initialized": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                },
                "config": {},
                "agents": {},
                "shared": {
                    "market_regime": None,
                    "india_vix": None,
                    "trading_blocked": False,
                    "global_sentiment": None,
                    "last_update": None
                },
                "cronjobs": {},
                "trade_history": [],
                "evolution_log": []
            }
            self._write_state(initial_state)
    
    def _read_state(self):
        """Read entire state file"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _write_state(self, state):
        """Write entire state file"""
        state["_meta"]["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    # ============ AGENT-SPECIFIC STORAGE ============
    
    def agent_write(self, agent_name: str, data: dict):
        """
        Each agent writes ONLY to its own section
        No conflicts between agents!
        """
        # Lock file for exclusive access
        with open(self.state_file, 'r+') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            
            try:
                state = json.load(f)
                
                # Initialize agent section if doesn't exist
                if "agents" not in state:
                    state["agents"] = {}
                
                # Write to agent's own section
                state["agents"][agent_name] = {
                    **data,
                    "_last_updated": datetime.now().isoformat()
                }
                
                # Update shared data if provided
                if "shared_update" in data:
                    state["shared"].update(data["shared_update"])
                
                # Write back
                f.seek(0)
                f.truncate()
                json.dump(state, f, indent=2)
                
            finally:
                fcntl.flock(f.filENO(), fcntl.LOCK_UN)
        
        print(f"[STATE] {agent_name} wrote to its section")
    
    def agent_read(self, agent_name: str) -> dict:
        """
        Agent reads its OWN data
        """
        state = self._read_state()
        return state.get("agents", {}).get(agent_name, {})
    
    def agent_read_other(self, target_agent: str) -> dict:
        """
        Agent reads ANOTHER agent's data (for coordination)
        """
        state = self._read_state()
        return state.get("agents", {}).get(target_agent, {})
    
    # ============ SHARED STORAGE ============
    
    def shared_write(self, key: str, value):
        """
        Write to shared section (use sparingly - lock contention)
        """
        with open(self.state_file, 'r+') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            
            try:
                state = json.load(f)
                
                if "shared" not in state:
                    state["shared"] = {}
                
                state["shared"][key] = value
                state["shared"]["_last_updated"] = datetime.now().isoformat()
                
                f.seek(0)
                f.truncate()
                json.dump(state, f, indent=2)
                
            finally:
                fcntl.flock(f.filENO(), fcntl.LOCK_UN)
    
    def shared_read(self, key: str, default=None):
        """
        Read from shared section
        """
        state = self._read_state()
        return state.get("shared", {}).get(key, default)
    
    def shared_read_all(self) -> dict:
        """
        Read entire shared section
        """
        state = self._read_state()
        return state.get("shared", {})
    
    # ============ CRONJOB COORDINATION ============
    
    def cronjob_heartbeat(self, cronjob_name: str):
        """
        Each cronjob writes heartbeat when it runs
        Other jobs can check this
        """
        self.agent_write(f"cronjob_{cronjob_name}", {
            "last_run": datetime.now().isoformat(),
            "status": "running"
        })
    
    def cronjob_check_dependency(self, dependency_name: str) -> bool:
        """
        Check if a dependency cronjob has run recently
        """
        dep_state = self.agent_read(f"cronjob_{dependency_name}")
        if not dep_state:
            return False
        
        last_run = dep_state.get("last_run")
        if not last_run:
            return False
        
        # Check if run in last 10 minutes
        last_run_time = datetime.fromisoformat(last_run)
        elapsed = (datetime.now() - last_run_time).total_seconds()
        
        return elapsed < 600  # 10 minutes
    
    # ============ AGENT COORDINATION ============
    
    def wait_for_agent(self, agent_name: str, timeout_seconds: int = 60):
        """
        Wait for another agent to complete
        """
        start = time.time()
        while time.time() - start < timeout_seconds:
            agent_state = self.agent_read(agent_name)
            if agent_state.get("status") == "complete":
                return True
            time.sleep(1)
        return False
    
    def publish_signal(self, signal_type: str, data: dict):
        """
        Publish signal for other agents
        """
        signal = {
            "type": signal_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "source": "unknown"  # Set by calling agent
        }
        
        # Write to agent's signals section
        agent_name = data.get("source_agent", "unknown")
        current = self.agent_read(agent_name)
        
        if "signals" not in current:
            current["signals"] = []
        
        current["signals"].append(signal)
        current["signals"] = current["signals"][-100:]  # Keep last 100
        
        self.agent_write(agent_name, current)


# Global instance
_manager = None

def get_state_manager():
    global _manager
    if _manager is None:
        _manager = ApexStateManager()
    return _manager


# Convenience functions for agents
def agent_write(agent_name: str, data: dict):
    get_state_manager().agent_write(agent_name, data)

def agent_read(agent_name: str) -> dict:
    return get_state_manager().agent_read(agent_name)

def shared_write(key: str, value):
    get_state_manager().shared_write(key, value)

def shared_read(key: str, default=None):
    return get_state_manager().shared_read(key, default)

def cronjob_heartbeat(cronjob_name: str):
    get_state_manager().cronjob_heartbeat(cronjob_name)

def check_dependency(cronjob_name: str) -> bool:
    return get_state_manager().cronjob_check_dependency(cronjob_name)


if __name__ == "__main__":
    # Test
    print("APEX State Manager Test")
    print("="*50)
    
    manager = get_state_manager()
    
    # Simulate pre-market agent
    agent_write("apex-india-trading-central-command", {
        "margins": 100000,
        "positions": 5,
        "status": "complete",
        "pre_market_check": "passed"
    })
    
    # Simulate regime agent reading pre-market data
    pre_market = agent_read("apex-india-trading-central-command")
    print(f"Pre-market data: {pre_market}")
    
    # Simulate regime agent writing its data
    agent_write("apex-market-regime-engine", {
        "regime": "BULLISH",
        "confidence": 85,
        "status": "complete"
    })
    
    # Now both agents have their own sections!
    regime_data = agent_read("apex-market-regime-engine")
    print(f"Regime data: {regime_data}")
    
    # Shared data works too
    shared_write("market_status", "OPEN")
    print(f"Shared status: {shared_read('market_status')}")
    
    print("\n✅ Section-based storage working!")
