#!/usr/bin/env python3
"""
APEX Core Orchestrator
Coordinates all agents and manages inter-agent communication
"""

import json
import time
import uuid
from datetime import datetime
from collections import deque
import os
import sys

class ApexEventBus:
    """Central event bus for inter-agent communication"""
    
    def __init__(self, state_dir=None):
        self.state_dir = state_dir or os.path.expanduser("~/.apex")
        self.state_file = os.path.join(self.state_dir, "event_bus.json")
        self.subscribers = {}
        self.message_queue = deque(maxlen=1000)
        self.processed_events = set()
        os.makedirs(self.state_dir, exist_ok=True)
        
    def subscribe(self, event_type, callback):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        
    def publish(self, event_type, payload, source=None, priority="normal"):
        """Publish an event"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "source_agent": source,
            "payload": payload,
            "priority": priority
        }
        
        self.message_queue.append(event)
        
        # Notify subscribers
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"[ORCHESTRATOR] Subscriber error: {e}")
        
        return event
    
    def process_queue(self):
        """Process pending messages"""
        processed = 0
        while self.message_queue:
            event = self.message_queue.popleft()
            if event["event_id"] not in self.processed_events:
                self.processed_events.add(event["event_id"])
                processed += 1
        return processed


class ApexAgentRegistry:
    """Registry of available agents"""
    
    def __init__(self, skills_path=None):
        self.skills_path = skills_path or os.path.expanduser("~/.hermes/skills/trading")
        self.agents = {}
        self._discover_agents()
    
    def _discover_agents(self):
        """Auto-discover all apex agents"""
        if not os.path.exists(self.skills_path):
            return
            
        for skill_name in os.listdir(self.skills_path):
            if skill_name.startswith("apex-"):
                skill_path = os.path.join(self.skills_path, skill_name)
                if os.path.isdir(skill_path):
                    self.agents[skill_name] = {
                        "path": skill_path,
                        "available": True
                    }
    
    def list_agents(self):
        return list(self.agents.keys())
    
    def is_available(self, agent_name):
        return agent_name in self.agents


class ApexOrchestrator:
    """Main orchestrator"""
    
    def __init__(self):
        self.event_bus = ApexEventBus()
        self.registry = ApexAgentRegistry()
        self.state_file = os.path.expanduser("~/.apex/orchestrator_state.json")
        self.state = self._load_state()
        
        # Register built-in event handlers
        self._register_handlers()
    
    def _load_state(self):
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "active_agents": [],
                "last_market_status": None,
                "workflow_history": []
            }
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _register_handlers(self):
        """Register event handlers"""
        self.event_bus.subscribe("market:open", self._on_market_open)
        self.event_bus.subscribe("market:close", self._on_market_close)
        self.event_bus.subscribe("signal:generated", self._on_signal_generated)
    
    def _on_market_open(self, event):
        print("[ORCHESTRATOR] Market opened!")
        self._run_market_open_workflow()
    
    def _on_market_close(self, event):
        print("[ORCHESTRATOR] Market closed!")
        self._run_market_close_workflow()
    
    def _on_signal_generated(self, event):
        print(f"[ORCHESTRATOR] Signal: {event['payload']}")
        # Auto-route to risk veto
        # This is where the magic happens - agents talk to each other!
    
    def _run_market_open_workflow(self):
        """Morning workflow"""
        print("[WORKFLOW] Running market open sequence...")
        # 1. Fetch VIX
        # 2. Classify regime  
        # 3. Fetch positions
        print("[WORKFLOW] Market open complete")
    
    def _run_market_close_workflow(self):
        """Evening workflow"""
        print("[WORKFLOW] Running market close sequence...")
        # 1. Close positions
        # 2. Calculate P&L
        # 3. Run evolution
        print("[WORKFLOW] Market close complete")
    
    def execute_agent(self, agent_name, action, payload=None):
        """Execute an agent action"""
        if not self.registry.is_available(agent_name):
            print(f"[ORCHESTRATOR] Agent {agent_name} not available")
            return None
        
        print(f"[ORCHESTRATOR] Executing {agent_name}.{action}")
        
        # Try to load and execute agent module
        agent_path = self.registry.agents[agent_name]["path"]
        for file in os.listdir(agent_path):
            if file.endswith('.py') and file != '__init__.py':
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        file[:-3], os.path.join(agent_path, file)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, action):
                        return getattr(module, action)(payload or {})
                except Exception as e:
                    print(f"[ORCHESTRATOR] Error: {e}")
        
        return None
    
    def run(self):
        """Main loop"""
        print("="*70)
        print("APEX CORE ORCHESTRATOR")
        print("="*70)
        print(f"Agents registered: {len(self.registry.list_agents())}")
        
        for agent in sorted(self.registry.list_agents()):
            print(f"  ✓ {agent}")
        
        print("="*70)
        
        # Check market hours and trigger events
        now = datetime.now()
        
        # Market open (9:15 AM)
        if now.hour == 9 and now.minute >= 15 and now.minute < 16:
            if self.state.get("last_market_status") != "open":
                self.event_bus.publish("market:open", {}, source="orchestrator")
                self.state["last_market_status"] = "open"
                self._save_state()
        
        # Market close (3:30 PM)  
        elif now.hour == 15 and now.minute >= 30 and now.minute < 31:
            if self.state.get("last_market_status") != "close":
                self.event_bus.publish("market:close", {}, source="orchestrator")
                self.state["last_market_status"] = "close"
                self._save_state()
        
        # Process any pending events
        processed = self.event_bus.process_queue()
        if processed > 0:
            print(f"[ORCHESTRATOR] Processed {processed} events")


# Global instance
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ApexOrchestrator()
    return _orchestrator


def main():
    orch = get_orchestrator()
    orch.run()


if __name__ == "__main__":
    main()
