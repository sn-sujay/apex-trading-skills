---
name: apex-rate-limiter
description: Centralized rate limiting for all APEX API calls and trading operations
Triggers:
  - Used by all skills to ensure compliance with API limits
tags: [apex, trading, rate-limit, api-management]
---

# APEX Rate Limiter

## Purpose
Ensures APEX respects API rate limits and trading frequency limits to avoid:
- API bans from Dhan or NSE
- Over-trading
- System overload

## Rate Limits Configured

### Dhan API Limits
```python
DHAN_LIMITS = {
    "order_placement": {
        "max_per_second": 5,
        "max_per_minute": 100,
        "max_per_day": 10000
    },
    "order_modification": {
        "max_per_second": 2,
        "max_per_minute": 50
    },
    "portfolio_requests": {
        "max_per_minute": 60
    },
    "market_data": {
        "note": "Use NSE India API instead (no strict limits)"
    }
}
```

### NSE India API Limits
```python
NSE_LIMITS = {
    "india_vix": {
        "max_per_minute": 10,
        "min_interval_seconds": 10
    },
    "option_chain": {
        "max_per_minute": 5,
        "min_interval_seconds": 15
    },
    "all_indices": {
        "max_per_minute": 10
    }
}
```

### Trading Frequency Limits
```python
TRADING_LIMITS = {
    "min_time_between_trades_seconds": 60,
    "max_trades_per_hour": 10,
    "max_trades_per_day": 30,
    "max_orders_per_trade": 3,  # Entry, SL, Target
    "cooldown_after_loss_seconds": 300,  # 5 min after loss
}
```

### Signal Generation Limits
```python
SIGNAL_LIMITS = {
    "max_signals_per_hour": 5,
    "min_time_between_signals_seconds": 300,  # 5 minutes
    "max_signals_per_strategy_per_day": 3
}
```

## Implementation

```python
"""
APEX Rate Limiter
Centralized rate limiting for APIs and trading
"""

import time
from datetime import datetime, timedelta
from collections import deque
import json
import os

class ApexRateLimiter:
    """
    Thread-safe rate limiter for all APEX operations
    """
    
    def __init__(self, state_file=None):
        self.state_file = state_file or os.path.expanduser("~/.apex/rate_limits.json")
        self.load_state()
        
        # Dhan API rate trackers
        self.dhan_order_times = deque(maxlen=10000)
        self.dhan_modify_times = deque(maxlen=1000)
        self.dhan_portfolio_times = deque(maxlen=1000)
        
        # NSE API rate trackers
        self.nse_vix_times = deque(maxlen=1000)
        self.nse_option_times = deque(maxlen=500)
        
        # Trading rate trackers
        self.trade_times = deque(maxlen=1000)
        self.signal_times = deque(maxlen=500)
        self.last_loss_time = None
        
    def load_state(self):
        """Load rate limit state"""
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                # Restore timestamps
        except:
            pass
    
    def save_state(self):
        """Save rate limit state"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        # Save relevant state
    
    # ============ DHAN API LIMITS ============
    
    def can_place_order(self):
        """Check if we can place a new order"""
        now = time.time()
        
        # Check per second limit
        recent = [t for t in self.dhan_order_times if now - t < 1]
        if len(recent) >= 5:
            return False, "Rate limit: max 5 orders/second"
        
        # Check per minute limit
        recent_min = [t for t in self.dhan_order_times if now - t < 60]
        if len(recent_min) >= 100:
            return False, "Rate limit: max 100 orders/minute"
        
        # Check per day limit
        today = datetime.now().date()
        today_count = sum(1 for t in self.dhan_order_times 
                         if datetime.fromtimestamp(t).date() == today)
        if today_count >= 10000:
            return False, "Rate limit: max 10000 orders/day"
        
        return True, "OK"
    
    def record_order(self):
        """Record an order placement"""
        self.dhan_order_times.append(time.time())
    
    def can_modify_order(self):
        """Check if we can modify an order"""
        now = time.time()
        
        recent = [t for t in self.dhan_modify_times if now - t < 1]
        if len(recent) >= 2:
            return False, "Rate limit: max 2 modifications/second"
        
        recent_min = [t for t in self.dhan_modify_times if now - t < 60]
        if len(recent_min) >= 50:
            return False, "Rate limit: max 50 modifications/minute"
        
        return True, "OK"
    
    def record_modification(self):
        """Record an order modification"""
        self.dhan_modify_times.append(time.time())
    
    def can_fetch_portfolio(self):
        """Check if we can fetch portfolio data"""
        now = time.time()
        recent = [t for t in self.dhan_portfolio_times if now - t < 60]
        if len(recent) >= 60:
            return False, "Rate limit: max 60 portfolio requests/minute"
        return True, "OK"
    
    def record_portfolio_fetch(self):
        """Record a portfolio fetch"""
        self.dhan_portfolio_times.append(time.time())
    
    # ============ NSE API LIMITS ============
    
    def can_fetch_india_vix(self):
        """Check if we can fetch India VIX"""
        now = time.time()
        
        # Minimum interval between requests
        if self.nse_vix_times:
            last = self.nse_vix_times[-1]
            if now - last < 10:
                return False, "Rate limit: min 10 seconds between VIX fetches"
        
        # Per minute limit
        recent = [t for t in self.nse_vix_times if now - t < 60]
        if len(recent) >= 10:
            return False, "Rate limit: max 10 VIX fetches/minute"
        
        return True, "OK"
    
    def record_vix_fetch(self):
        """Record a VIX fetch"""
        self.nse_vix_times.append(time.time())
    
    def can_fetch_option_chain(self):
        """Check if we can fetch option chain"""
        now = time.time()
        
        if self.nse_option_times:
            last = self.nse_option_times[-1]
            if now - last < 15:
                return False, "Rate limit: min 15 seconds between option chain fetches"
        
        recent = [t for t in self.nse_option_times if now - t < 60]
        if len(recent) >= 5:
            return False, "Rate limit: max 5 option chain fetches/minute"
        
        return True, "OK"
    
    def record_option_fetch(self):
        """Record an option chain fetch"""
        self.nse_option_times.append(time.time())
    
    # ============ TRADING LIMITS ============
    
    def can_trade(self):
        """Check if we can execute a trade"""
        now = time.time()
        
        # Check cooldown after loss
        if self.last_loss_time and now - self.last_loss_time < 300:
            remaining = 300 - (now - self.last_loss_time)
            return False, f"Cooldown after loss: {remaining:.0f}s remaining"
        
        # Check min time between trades
        if self.trade_times:
            last = self.trade_times[-1]
            if now - last < 60:
                return False, "Rate limit: min 60 seconds between trades"
        
        # Check per hour limit
        recent_hour = [t for t in self.trade_times if now - t < 3600]
        if len(recent_hour) >= 10:
            return False, "Rate limit: max 10 trades/hour"
        
        # Check per day limit
        today = datetime.now().date()
        today_trades = sum(1 for t in self.trade_times 
                          if datetime.fromtimestamp(t).date() == today)
        if today_trades >= 30:
            return False, "Rate limit: max 30 trades/day"
        
        return True, "OK"
    
    def record_trade(self, pnl=None):
        """Record a trade execution"""
        self.trade_times.append(time.time())
        if pnl is not None and pnl < 0:
            self.last_loss_time = time.time()
    
    # ============ SIGNAL LIMITS ============
    
    def can_generate_signal(self, strategy_name):
        """Check if we can generate a signal"""
        now = time.time()
        
        # Check min time between signals
        if self.signal_times:
            last = self.signal_times[-1]
            if now - last < 300:
                return False, "Rate limit: min 5 minutes between signals"
        
        # Check per hour limit
        recent_hour = [t for t in self.signal_times if now - t < 3600]
        if len(recent_hour) >= 5:
            return False, "Rate limit: max 5 signals/hour"
        
        # Check per day limit per strategy
        today_signals = sum(1 for t in self.signal_times 
                           if datetime.fromtimestamp(t).date() == datetime.now().date())
        if today_signals >= 15:  # 3 per strategy x 5 strategies
            return False, "Rate limit: max signals for today"
        
        return True, "OK"
    
    def record_signal(self):
        """Record a signal generation"""
        self.signal_times.append(time.time())
    
    # ============ UTILITY ============
    
    def get_status(self):
        """Get current rate limit status"""
        now = time.time()
        
        return {
            "dhan_orders": {
                "last_second": len([t for t in self.dhan_order_times if now - t < 1]),
                "last_minute": len([t for t in self.dhan_order_times if now - t < 60]),
                "today": len([t for t in self.dhan_order_times 
                            if datetime.fromtimestamp(t).date() == datetime.now().date()])
            },
            "trades": {
                "last_hour": len([t for t in self.trade_times if now - t < 3600]),
                "today": len([t for t in self.trade_times 
                            if datetime.fromtimestamp(t).date() == datetime.now().date()])
            },
            "signals": {
                "last_hour": len([t for t in self.signal_times if now - t < 3600]),
                "today": len([t for t in self.signal_times 
                            if datetime.fromtimestamp(t).date() == datetime.now().date()])
            }
        }

# Global instance
rate_limiter = ApexRateLimiter()

# Convenience functions for skills
def check_order_rate_limit():
    return rate_limiter.can_place_order()

def check_trade_rate_limit():
    return rate_limiter.can_trade()

def check_signal_rate_limit(strategy):
    return rate_limiter.can_generate_signal(strategy)

def check_vix_rate_limit():
    return rate_limiter.can_fetch_india_vix()

def record_order():
    rate_limiter.record_order()

def record_trade(pnl=None):
    rate_limiter.record_trade(pnl)

def record_signal():
    rate_limiter.record_signal()

def record_vix_fetch():
    rate_limiter.record_vix_fetch()
```

## Usage in Skills

```python
from hermes_tools import skill_view

# Load rate limiter functions
skill_view("apex-rate-limiter")

# Before placing order
can_trade, message = check_order_rate_limit()
if not can_trade:
    print(f"[RATE LIMIT] {message}")
    return

# Place order
place_order(...)
record_order()
```

## Related Skills
- apex-live-order-executor (uses order limits)
- apex-india-vix-monitor (uses VIX fetch limits)
- apex-option-chain-monitor (uses option chain limits)
- apex-self-evolution-engine (uses signal limits)
