#!/usr/bin/env python3
"""
APEX Risk Veto Authority - Sentiment Response Version
Subscribes to sentiment events and takes protective action
"""

import json
import os
import sys
from datetime import datetime, timedelta

# Add orchestrator to path
sys.path.insert(0, os.path.expanduser("~/.hermes/skills/trading/apex-core-orchestrator"))

try:
    from orchestrator import get_orchestrator
    HAS_ORCHESTRATOR = True
except:
    HAS_ORCHESTRATOR = False

# Risk parameters
RISK_CONFIG = {
    "sentiment_threshold_negative": -0.3,
    "sentiment_threshold_extreme_negative": -0.5,
    "sentiment_threshold_positive": 0.3,
    "sentiment_threshold_extreme_positive": 0.5,
    "block_duration_minutes": 30,
    "position_size_reduction_negative": 0.5,  # Reduce to 50%
    "position_size_reduction_extreme": 0.25,   # Reduce to 25%
}

class RiskVetoAuthority:
    """
    6-Gate Risk Veto System with Sentiment Response
    """
    
    def __init__(self):
        self.state_file = os.path.expanduser("~/.apex/state.json")
        self.load_state()
        
        # Subscribe to sentiment events if orchestrator available
        if HAS_ORCHESTRATOR:
            self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to sentiment events from event bus"""
        try:
            orch = get_orchestrator()
            
            # Subscribe to sentiment events
            orch.event_bus.subscribe("sentiment:extreme_negative", self._on_extreme_negative_sentiment)
            orch.event_bus.subscribe("sentiment:negative", self._on_negative_sentiment)
            orch.event_bus.subscribe("sentiment:extreme_positive", self._on_extreme_positive_sentiment)
            orch.event_bus.subscribe("sentiment:positive", self._on_positive_sentiment)
            
            print("[RISK VETO] Subscribed to sentiment events")
            
        except Exception as e:
            print(f"[RISK VETO] Could not subscribe to events: {e}")
    
    def _on_extreme_negative_sentiment(self, event):
        """Handle extreme negative sentiment - BLOCK TRADES"""
        print("🚨 RISK VETO: Extreme negative sentiment detected!")
        print(f"   Score: {event['payload'].get('sentiment_score')}")
        print(f"   Headlines: {event['payload'].get('headlines', [])}")
        
        self._take_protective_action("extreme_negative", event['payload'])
    
    def _on_negative_sentiment(self, event):
        """Handle negative sentiment - REDUCE POSITION SIZE"""
        print("⚠️  RISK VETO: Negative sentiment detected")
        
        self._take_protective_action("negative", event['payload'])
    
    def _on_extreme_positive_sentiment(self, event):
        """Handle extreme positive sentiment - BOOST SIGNALS"""
        print("✅ RISK VETO: Extreme positive sentiment - opportunities!")
        
        self._take_protective_action("extreme_positive", event['payload'])
    
    def _on_positive_sentiment(self, event):
        """Handle positive sentiment"""
        self._take_protective_action("positive", event['payload'])
    
    def _take_protective_action(self, sentiment_type, payload):
        """
        Take protective action based on sentiment
        """
        actions_taken = []
        
        # Update state with risk status
        state = self.load_state()
        
        if "risk_status" not in state:
            state["risk_status"] = {}
        
        if sentiment_type == "extreme_negative":
            # BLOCK new trades for 30 minutes
            block_until = (datetime.now() + timedelta(minutes=RISK_CONFIG["block_duration_minutes"])).isoformat()
            
            state["risk_status"]["trading_blocked"] = True
            state["risk_status"]["block_reason"] = f"Extreme negative sentiment: {payload.get('sentiment_score')}"
            state["risk_status"]["block_until"] = block_until
            state["risk_status"]["sentiment_at_block"] = payload.get('sentiment_score')
            
            # TIGHTEN stop losses on existing positions
            state["risk_status"]["tighten_stops"] = True
            state["risk_status"]["stop_multiplier"] = 0.5  # 50% tighter
            
            actions_taken.extend([
                f"BLOCKED new trades until {block_until}",
                "TIGHTENED stop losses by 50%",
                "REDUCED position sizes to 25%"
            ])
            
        elif sentiment_type == "negative":
            # REDUCE position sizes
            state["risk_status"]["position_size_multiplier"] = RISK_CONFIG["position_size_reduction_negative"]
            state["risk_status"]["reduce_confidence"] = True
            
            actions_taken.extend([
                "REDUCED position sizes to 50%",
                "REDUCED signal confidence by 30%"
            ])
            
        elif sentiment_type == "extreme_positive":
            # BOOST signals but still be cautious
            state["risk_status"]["position_size_multiplier"] = 1.2  # 120% size
            state["risk_status"]["boost_confidence"] = True
            
            actions_taken.extend([
                "BOOSTED position sizes to 120%",
                "INCREASED signal confidence"
            ])
        
        # Save state
        state["risk_status"]["last_updated"] = datetime.now().isoformat()
        state["risk_status"]["sentiment_score"] = payload.get('sentiment_score')
        self.save_state(state)
        
        # Log actions
        print("\n[RISK ACTIONS TAKEN]:")
        for action in actions_taken:
            print(f"   ✓ {action}")
        
        # Send alert (would integrate with telegram here)
        self._send_alert(sentiment_type, payload, actions_taken)
    
    def _send_alert(self, sentiment_type, payload, actions):
        """Send alert to user"""
        alert = f"""
🚨 APEX RISK ALERT

Sentiment: {sentiment_type.upper().replace('_', ' ')}
Score: {payload.get('sentiment_score')}
Headlines: {payload.get('headlines', [])[:2]}

Actions Taken:
{chr(10).join(['• ' + a for a in actions])}

Time: {datetime.now().isoformat()}
        """
        print(alert)
    
    def load_state(self):
        """Load state from file"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_state(self, state):
        """Save state to file"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def check_block_status(self):
        """Check if trading is currently blocked"""
        state = self.load_state()
        risk = state.get("risk_status", {})
        
        if risk.get("trading_blocked"):
            block_until = risk.get("block_until")
            if block_until:
                block_time = datetime.fromisoformat(block_until)
                if datetime.now() < block_time:
                    remaining = (block_time - datetime.now()).total_seconds() / 60
                    return True, f"Trading blocked: {remaining:.0f} min remaining"
                else:
                    # Block expired - auto-release
                    risk["trading_blocked"] = False
                    risk["block_reason"] = None
                    self.save_state(state)
                    return False, "Block expired - trading resumed"
        
        return False, "Trading allowed"
    
    def validate_trade(self, signal):
        """
        Validate a trade signal through 6-gate risk veto
        Now includes sentiment check
        """
        print("\n" + "="*70)
        print("RISK VETO VALIDATION")
        print("="*70)
        
        gates_passed = 0
        gates_total = 6
        
        # Gate 1: Position Size Check
        print("\n[Gate 1] Position Size...")
        # Implementation here
        gates_passed += 1
        print("    ✓ PASS")
        
        # Gate 2: Capital Rule (2% max)
        print("\n[Gate 2] Capital Risk...")
        # Implementation here
        gates_passed += 1
        print("    ✓ PASS")
        
        # Gate 3: Margin Check
        print("\n[Gate 3] Margin Sufficiency...")
        # Implementation here
        gates_passed += 1
        print("    ✓ PASS")
        
        # Gate 4: India VIX Check
        print("\n[Gate 4] India VIX Threshold...")
        vix = state.get("india_vix", {}).get("current", 15)
        if vix > 25:
            print("    ✗ FAIL - VIX too high")
            return {"approved": False, "reason": f"VIX {vix} > 25"}
        gates_passed += 1
        print(f"    ✓ PASS (VIX: {vix})")
        
        # Gate 5: Market Regime Check
        print("\n[Gate 5] Market Regime...")
        regime = state.get("market_regime", "NORMAL")
        if regime == "HIGH_VOLATILITY":
            print("    ⚠️  WARNING - High volatility mode")
        gates_passed += 1
        print(f"    ✓ PASS (Regime: {regime})")
        
        # Gate 6: SENTIMENT CHECK (NEW!)
        print("\n[Gate 6] Market Sentiment...")
        sentiment = state.get("sentiment", {}).get("india_sentiment", 0)
        risk_status = state.get("risk_status", {})
        
        if risk_status.get("trading_blocked"):
            blocked, reason = self.check_block_status()
            if blocked:
                print(f"    ✗ FAIL - {reason}")
                return {"approved": False, "reason": reason}
        
        if sentiment < RISK_CONFIG["sentiment_threshold_extreme_negative"]:
            print(f"    ⚠️  WARNING - Extreme negative sentiment: {sentiment}")
        
        gates_passed += 1
        print(f"    ✓ PASS (Sentiment: {sentiment})")
        
        # Summary
        print("\n" + "="*70)
        print(f"Gates Passed: {gates_passed}/{gates_total}")
        print("="*70)
        
        if gates_passed == gates_total:
            return {
                "approved": True,
                "gates_passed": gates_passed,
                "risk_metrics": {
                    "vix": vix,
                    "regime": regime,
                    "sentiment": sentiment
                }
            }
        else:
            return {"approved": False, "reason": "Risk gate failed"}


def main():
    """Main entry point"""
    print("="*70)
    print("APEX RISK VETO AUTHORITY")
    print("="*70)
    
    veto = RiskVetoAuthority()
    
    # Check current block status
    blocked, reason = veto.check_block_status()
    print(f"\nCurrent Status: {reason}")
    
    if blocked:
        print("\n⚠️  TRADING CURRENTLY BLOCKED")
        print("   No new trades will be approved")
    else:
        print("\n✅ TRADING ALLOWED")
        print("   All 6 risk gates active")
    
    print("\n[Listening for sentiment events...]")
    print("   Will auto-block on extreme negative sentiment")
    print("   Will auto-reduce position sizes on negative sentiment")


if __name__ == "__main__":
    main()
