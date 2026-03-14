---
name: apex-core-orchestrator
description: Core orchestrator that coordinates all APEX agents/skills, manages inter-agent communication, and ensures autonomous operation. Acts as the central nervous system.
triggers:
  - schedule: "*/5 * * * 1-5"  # Every 5 minutes during market hours
  - startup: always
tags: [apex, trading, orchestrator, coordination, core]
---

# APEX Core Orchestrator

## Purpose
The brain of APEX. Coordinates communication between all agents, manages workflows, and ensures the system operates autonomously without manual intervention.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              APEX CORE ORCHESTRATOR                          │
├─────────────────────────────────────────────────────────────┤
│  EVENT BUS ←→ MESSAGE QUEUE ←→ AGENT REGISTRY               │
├─────────────────────────────────────────────────────────────┤
│  WORKFLOW ENGINE                                             │
│  ├── Market Open Workflow (9:15 AM)                        │
│  ├── Intraday Monitoring Workflow (every 5 min)            │
│  ├── Signal Generation Workflow                           │
│  ├── Trade Execution Workflow                              │
│  └── Market Close Workflow (3:30 PM)                       │
├─────────────────────────────────────────────────────────────┤
│  AGENT COORDINATION                                          │
│  ├── India VIX Agent → Regime Engine                       │
│  ├── Option Chain Agent → Signal Engine                    │
│  ├── Signal Engine → Risk Veto → Order Executor            │
│  ├── Order Executor → Monitor → Performance                │
│  └── Performance → Evolution Engine                        │
└─────────────────────────────────────────────────────────────┘
```

## Inter-Agent Communication Protocol

### Event Types
```python
class ApexEvent:
    MARKET_OPEN = "market:open"
    MARKET_CLOSE = "market:close"
    VIX_UPDATE = "data:vix_updated"
    REGIME_CHANGE = "market:regime_changed"
    SIGNAL_GENERATED = "signal:generated"
    SIGNAL_VALIDATED = "signal:validated"
    TRADE_EXECUTED = "trade:executed"
    TRADE_CLOSED = "trade:closed"
    RISK_VIOLATION = "risk:violation"
    PERFORMANCE_UPDATE = "perf:updated"
    EVOLUTION_TRIGGER = "evolution:trigger"
```

### Message Format
```json
{
  "event_id": "uuid",
  "event_type": "signal:generated",
  "timestamp": "2026-03-14T09:30:00+05:30",
  "source_agent": "apex-option-chain-monitor",
  "target_agents": ["apex-risk-veto-authority", "apex-validator-gate"],
  "payload": {
    "signal": "BUY",
    "symbol": "NIFTY",
    "strike": 22500,
    "strategy": "Bull Call Spread"
  },
  "priority": "high",
  "requires_response": true
}
```

## Agent Registry

Each agent registers its capabilities:

```python
AGENT_REGISTRY = {
    "apex-india-vix-monitor": {
        "capabilities": ["fetch_vix", "regime_detection"],
        "triggers": ["schedule:9:15", "schedule:12:00", "schedule:15:00"],
        "outputs": ["vix_data", "market_regime"],
        "subscribes_to": [],
        "publishes_to": ["data:vix_updated", "market:regime_changed"]
    },
    "apex-option-chain-monitor": {
        "capabilities": ["fetch_option_chain", "pcr_analysis", "oi_analysis"],
        "triggers": ["schedule:*/15", "event:market_open"],
        "outputs": ["option_data", "pcr", "max_pain"],
        "subscribes_to": ["data:vix_updated"],
        "publishes_to": ["data:option_chain_updated"]
    },
    "apex-market-regime-engine": {
        "capabilities": ["classify_regime", "trend_detection"],
        "triggers": ["event:vix_updated", "event:price_updated"],
        "outputs": ["regime", "trend", "sentiment"],
        "subscribes_to": ["data:vix_updated", "data:price_updated"],
        "publishes_to": ["market:regime_changed"]
    },
    "apex-risk-veto-authority": {
        "capabilities": ["validate_trade", "check_limits"],
        "triggers": ["event:signal_generated"],
        "outputs": ["approval_status", "risk_metrics"],
        "subscribes_to": ["signal:generated"],
        "publishes_to": ["signal:validated", "risk:violation"]
    },
    "apex-live-order-executor": {
        "capabilities": ["place_order", "modify_order", "cancel_order"],
        "triggers": ["event:signal_validated"],
        "outputs": ["order_confirmation", "order_rejection"],
        "subscribes_to": ["signal:validated"],
        "publishes_to": ["trade:executed"]
    },
    "apex-self-evolution-engine": {
        "capabilities": ["analyze_performance", "adjust_weights", "detect_weaknesses"],
        "triggers": ["schedule:15:30", "event:market_close"],
        "outputs": ["weight_updates", "improvements"],
        "subscribes_to": ["perf:updated", "trade:closed"],
        "publishes_to": ["evolution:trigger"]
    }
}
```

## Workflow Definitions

### 1. Market Open Workflow (9:15 AM IST)
```python
def market_open_workflow():
    """
    Executed once at market open
    """
    # 1. Fetch India VIX
    vix_data = execute_agent("apex-india-vix-monitor", action="fetch_vix")
    
    # 2. Detect market regime
    regime = execute_agent("apex-market-regime-engine", 
                          input=vix_data, 
                          action="classify")
    
    # 3. Check portfolio/positions
    portfolio = execute_agent("apex-live-order-monitor", 
                             action="get_positions")
    
    # 4. Update state
    update_state({
        "market_status": "OPEN",
        "regime": regime,
        "vix": vix_data,
        "positions": portfolio
    })
    
    # 5. Notify all agents that market is open
    broadcast_event("market:open", payload={"regime": regime})
```

### 2. Signal Generation Workflow
```python
def signal_generation_workflow():
    """
    Continuous signal generation and validation
    Triggered every 5 minutes or on data updates
    """
    # 1. Fetch option chain data
    option_data = execute_agent("apex-option-chain-monitor", 
                               action="fetch")
    
    # 2. Analyze for signals
    signals = execute_agent("apex-inr-signal-engine", 
                           input=option_data,
                           action="generate_signals")
    
    # 3. For each signal, validate through risk veto
    for signal in signals:
        # Publish signal event
        publish_event("signal:generated", 
                     source="apex-inr-signal-engine",
                     payload=signal)
        
        # Risk veto authority validates automatically
        validation = execute_agent("apex-risk-veto-authority",
                                  input=signal,
                                  action="validate")
        
        if validation["approved"]:
            publish_event("signal:validated",
                         payload={**signal, **validation})
            
            # Auto-execute if enabled
            if get_config("auto_execute"):
                execute_trade_workflow(signal)
```

### 3. Trade Execution Workflow
```python
def trade_execution_workflow(signal):
    """
    Execute a validated trade
    Triggered when signal:validated event is received
    """
    # 1. Check rate limits
    rate_check = execute_agent("apex-rate-limiter",
                              action="check_trade_limit")
    if not rate_check["allowed"]:
        log_warning(f"Rate limit prevented trade: {rate_check['reason']}")
        return
    
    # 2. Calculate position size
    position = execute_agent("apex-risk-veto-authority",
                            input=signal,
                            action="calculate_position")
    
    # 3. Place order
    order = execute_agent("apex-live-order-executor",
                         input={**signal, **position},
                         action="place_order")
    
    # 4. Record trade
    execute_agent("apex-performance-monitor",
                 input=order,
                 action="record_trade")
    
    # 5. Publish execution event
    publish_event("trade:executed", payload=order)
    
    # 6. Start monitoring
    execute_agent("apex-live-order-monitor",
                 input=order,
                 action="start_monitoring")
```

### 4. Market Close Workflow (3:30 PM IST)
```python
def market_close_workflow():
    """
    End of day processing
    Triggered at market close
    """
    # 1. Close all open intraday positions
    positions = execute_agent("apex-live-order-monitor",
                             action="get_open_positions")
    
    for position in positions:
        if position["type"] == "INTRADAY":
            execute_agent("apex-live-order-executor",
                         input=position,
                         action="close_position")
    
    # 2. Calculate daily performance
    performance = execute_agent("apex-performance-monitor",
                               action="calculate_daily_pnl")
    
    # 3. Update state
    update_state({
        "market_status": "CLOSED",
        "daily_pnl": performance
    })
    
    # 4. Trigger evolution
    publish_event("market:close", payload=performance)
    
    # 5. Run evolution engine
    execute_agent("apex-self-evolution-engine",
                 input=performance,
                 action="evolve")
```

## Implementation

```python
#!/usr/bin/env python3
"""
APEX Core Orchestrator
Coordinates all agents and manages inter-agent communication
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
import os
import sys

# Add skills to path
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/trading"))

class ApexEventBus:
    """
    Central event bus for inter-agent communication
    """
    def __init__(self, state_file=None):
        self.state_file = state_file or os.path.expanduser("~/.apex/event_bus.json")
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue = []
        self.processed_events = set()
        
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        
    def publish(self, event_type: str, payload: dict, 
               source: str = None, priority: str = "normal"):
        """Publish an event to the bus"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "source_agent": source,
            "payload": payload,
            "priority": priority
        }
        
        self.message_queue.append(event)
        self._persist_event(event)
        
        # Notify subscribers
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"[ORCHESTRATOR] Error notifying subscriber: {e}")
    
    def process_queue(self):
        """Process pending messages"""
        # Sort by priority and timestamp
        priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
        self.message_queue.sort(
            key=lambda x: (priority_order.get(x["priority"], 2), x["timestamp"])
        )
        
        processed = []
        for event in self.message_queue:
            if event["event_id"] not in self.processed_events:
                self._route_event(event)
                self.processed_events.add(event["event_id"])
                processed.append(event)
        
        # Clear processed messages
        self.message_queue = [e for e in self.message_queue 
                              if e["event_id"] not in self.processed_events]
        
        return len(processed)
    
    def _route_event(self, event: dict):
        """Route event to appropriate handler"""
        event_type = event["event_type"]
        
        # Built-in event handlers
        handlers = {
            "market:open": self._handle_market_open,
            "market:close": self._handle_market_close,
            "signal:generated": self._handle_signal_generated,
            "signal:validated": self._handle_signal_validated,
            "trade:executed": self._handle_trade_executed,
        }
        
        if event_type in handlers:
            handlers[event_type](event)
    
    def _handle_market_open(self, event):
        """Handle market open event"""
        print("[ORCHESTRATOR] Market opened, triggering workflows...")
        orchestrator.trigger_workflow("market_open")
    
    def _handle_market_close(self, event):
        """Handle market close event"""
        print("[ORCHESTRATOR] Market closed, running EOD workflows...")
        orchestrator.trigger_workflow("market_close")
    
    def _handle_signal_generated(self, event):
        """Handle new signal"""
        print(f"[ORCHESTRATOR] Signal generated: {event['payload']}")
        # Auto-route to risk veto
        orchestrator.execute_agent("apex-risk-veto-authority",
                                   event["payload"],
                                   "validate_signal")
    
    def _handle_signal_validated(self, event):
        """Handle validated signal"""
        if event["payload"].get("approved"):
            print("[ORCHESTRATOR] Signal approved, executing trade...")
            orchestrator.trigger_workflow("trade_execution", 
                                         event["payload"])
    
    def _handle_trade_executed(self, event):
        """Handle executed trade"""
        print(f"[ORCHESTRATOR] Trade executed: {event['payload']}")
        # Notify performance monitor
        orchestrator.execute_agent("apex-performance-monitor",
                                   event["payload"],
                                   "record_trade")
    
    def _persist_event(self, event: dict):
        """Persist event to state file"""
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
        except:
            data = {"events": []}
        
        data["events"].append(event)
        # Keep only last 1000 events
        data["events"] = data["events"][-1000:]
        
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(data, f)


class ApexAgentRegistry:
    """
    Registry of all available agents and their capabilities
    """
    def __init__(self):
        self.agents = {}
        self._discover_agents()
    
    def _discover_agents(self):
        """Auto-discover available agents"""
        skills_path = os.path.expanduser("~/.hermes/skills/trading")
        
        for skill_name in os.listdir(skills_path):
            if skill_name.startswith("apex-"):
                skill_path = os.path.join(skills_path, skill_name)
                skill_file = os.path.join(skill_path, "SKILL.md")
                
                if os.path.exists(skill_file):
                    with open(skill_file, 'r') as f:
                        content = f.read()
                    
                    # Parse skill metadata from frontmatter
                    self.agents[skill_name] = {
                        "path": skill_path,
                        "available": True
                    }
    
    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self.agents.keys())
    
    def is_available(self, agent_name: str) -> bool:
        """Check if agent is available"""
        return agent_name in self.agents


class ApexOrchestrator:
    """
    Main orchestrator class
    """
    def __init__(self):
        self.event_bus = ApexEventBus()
        self.registry = ApexAgentRegistry()
        self.workflows = {}
        self.state_file = os.path.expanduser("~/.apex/orchestrator_state.json")
        self.load_state()
        
        # Register built-in workflows
        self._register_workflows()
    
    def _register_workflows(self):
        """Register available workflows"""
        self.workflows = {
            "market_open": self._market_open_workflow,
            "market_close": self._market_close_workflow,
            "signal_generation": self._signal_generation_workflow,
            "trade_execution": self._trade_execution_workflow,
            "intraday_monitoring": self._intraday_monitoring_workflow,
        }
    
    def load_state(self):
        """Load orchestrator state"""
        try:
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        except:
            self.state = {
                "active_workflows": [],
                "last_market_status": None,
                "agent_status": {}
            }
    
    def save_state(self):
        """Save orchestrator state"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def trigger_workflow(self, workflow_name: str, payload: dict = None):
        """Trigger a workflow"""
        if workflow_name in self.workflows:
            print(f"[ORCHESTRATOR] Triggering workflow: {workflow_name}")
            try:
                self.workflows[workflow_name](payload)
            except Exception as e:
                print(f"[ORCHESTRATOR] Workflow error: {e}")
        else:
            print(f"[ORCHESTRATOR] Unknown workflow: {workflow_name}")
    
    def execute_agent(self, agent_name: str, payload: dict, action: str):
        """Execute an agent with given payload"""
        if not self.registry.is_available(agent_name):
            print(f"[ORCHESTRATOR] Agent not available: {agent_name}")
            return None
        
        print(f"[ORCHESTRATOR] Executing {agent_name}.{action}")
        
        # Load and execute agent logic
        # This would dynamically load the agent's Python module
        try:
            agent_module = self._load_agent_module(agent_name)
            if agent_module and hasattr(agent_module, action):
                return getattr(agent_module, action)(payload)
        except Exception as e:
            print(f"[ORCHESTRATOR] Agent execution error: {e}")
        
        return None
    
    def _load_agent_module(self, agent_name: str):
        """Dynamically load agent module"""
        # Find Python file in agent directory
        agent_path = os.path.expanduser(f"~/.hermes/skills/trading/{agent_name}")
        
        for file in os.listdir(agent_path):
            if file.endswith('.py'):
                module_name = file[:-3]
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        module_name, os.path.join(agent_path, file)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
                except Exception as e:
                    print(f"[ORCHESTRATOR] Error loading {file}: {e}")
        
        return None
    
    def _market_open_workflow(self, payload):
        """Market open workflow"""
        print("[WORKFLOW] Executing market open workflow...")
        
        # 1. Fetch India VIX
        vix = self.execute_agent("apex-india-vix-monitor", {}, "fetch_india_vix")
        
        # 2. Classify regime
        if vix:
            regime = self.execute_agent("apex-market-regime-engine", vix, "classify_regime")
        
        # 3. Fetch positions
        positions = self.execute_agent("apex-live-order-monitor", {}, "get_positions")
        
        print("[WORKFLOW] Market open complete")
    
    def _market_close_workflow(self, payload):
        """Market close workflow"""
        print("[WORKFLOW] Executing market close workflow...")
        
        # 1. Run evolution
        self.execute_agent("apex-self-evolution-engine", {}, "self_evolution_cycle")
        
        print("[WORKFLOW] Market close complete")
    
    def _signal_generation_workflow(self, payload):
        """Signal generation workflow"""
        pass
    
    def _trade_execution_workflow(self, payload):
        """Trade execution workflow"""
        pass
    
    def _intraday_monitoring_workflow(self, payload):
        """Intraday monitoring workflow"""
        pass
    
    def run(self):
        """Main orchestrator loop"""
        print("="*70)
        print("APEX CORE ORCHESTRATOR")
        print("="*70)
        print(f"Registered agents: {len(self.registry.list_agents())}")
        print(f"Registered workflows: {list(self.workflows.keys())}")
        print("="*70)
        
        # Process events
        processed = self.event_bus.process_queue()
        print(f"\nProcessed {processed} events")
        
        # Check for scheduled workflows
        now = datetime.now()
        
        # Market open at 9:15 AM
        if now.hour == 9 and now.minute == 15:
            if self.state.get("last_market_status") != "open":
                self.event_bus.publish("market:open", {}, source="orchestrator")
                self.state["last_market_status"] = "open"
        
        # Market close at 3:30 PM
        elif now.hour == 15 and now.minute == 30:
            if self.state.get("last_market_status") != "close":
                self.event_bus.publish("market:close", {}, source="orchestrator")
                self.state["last_market_status"] = "close"
        
        self.save_state()


# Global orchestrator instance
orchestrator = None

def get_orchestrator():
    """Get or create global orchestrator"""
    global orchestrator
    if orchestrator is None:
        orchestrator = ApexOrchestrator()
    return orchestrator


def main():
    """Main entry point"""
    orch = get_orchestrator()
    orch.run()


if __name__ == "__main__":
    main()
```

## Auto-Discovery & Setup

When this skill is loaded, it automatically:

1. **Discovers** all available apex-* skills
2. **Registers** them in the agent registry
3. **Sets up** event routing between agents
4. **Schedules** workflows based on market hours
5. **Coordinates** inter-agent communication

## Usage

```python
# In your AI agent
load_skill("apex-core-orchestrator")

# The orchestrator automatically:
# - Registers all agents
# - Sets up event bus
# - Starts monitoring market hours
# - Triggers workflows at appropriate times

# To manually trigger a workflow:
orchestrator.trigger_workflow("market_open")

# To publish an event:
event_bus.publish("signal:generated", 
                  payload={"symbol": "NIFTY"},
                  source="my_strategy")

# Other agents automatically receive and handle the event
```

## Portability

When you import this to another platform:

1. **Auto-Discovery**: Finds all apex-* skills automatically
2. **Auto-Configuration**: Reads configuration from ~/.apex/state.json
3. **Auto-Scheduling**: Sets up cronjobs automatically
4. **Auto-Coordination**: Agents start talking to each other immediately

No manual configuration needed - it just works!

## Related Skills
- All apex-* skills (coordinated by this orchestrator)
- apex-controller (high-level control)
- apex-system-health-monitor (monitors orchestrator health)
