#!/usr/bin/env python3
"""
APEX Rate Limiter
Centralized rate limiting for all APEX operations
"""

import time
from datetime import datetime, timedelta
from collections import deque
import json
import os

class ApexRateLimiter:
    """
    Thread-safe rate limiter for all APEX operations
    Prevents API bans and over-trading
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
        """Load rate limit state from file"""
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                # Restore timestamps if needed
        except FileNotFoundError:
            pass
    
    def save_state(self):
        """Save rate limit state"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump({"last_save": datetime.now().isoformat()}, f)
    
    # ============ DHAN API LIMITS ============
    
    def can_place_order(self):
        """Check if we can place a new order"""
        now = time.time()
        
        # Check per second limit (5 orders/second max)
        recent_sec = [t for t in self.dhan_order_times if now - t < 1]
        if len(recent_sec) >= 5:
            return False, f"Rate limit: {len(recent_sec)} orders in last second (max 5)"
        
        # Check per minute limit (100 orders/minute max)
        recent_min = [t for t in self.dhan_order_times if now - t < 60]
        if len(recent_min) >= 100:
            return False, f"Rate limit: {len(recent_min)} orders in last minute (max 100)"
        
        # Check per day limit (10000 orders/day max)
        today = datetime.now().date()
        today_count = sum(1 for t in self.dhan_order_times 
                         if datetime.fromtimestamp(t).date() == today)
        if today_count >= 10000:
            return False, f"Rate limit: {today_count} orders today (max 10000)"
        
        return True, "OK"
    
    def record_order(self):
        """Record an order placement"""
        self.dhan_order_times.append(time.time())
        self.save_state()
    
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
    
    # ============ NSE API LIMITS ============
    
    def can_fetch_india_vix(self):
        """Check if we can fetch India VIX"""
        now = time.time()
        
        # Minimum interval between requests (10 seconds)
        if self.nse_vix_times:
            last = self.nse_vix_times[-1]
            elapsed = now - last
            if elapsed < 10:
                return False, f"Rate limit: wait {10 - elapsed:.0f}s before next VIX fetch"
        
        # Per minute limit (10 fetches/minute max)
        recent = [t for t in self.nse_vix_times if now - t < 60]
        if len(recent) >= 10:
            return False, "Rate limit: max 10 VIX fetches/minute"
        
        return True, "OK"
    
    def record_vix_fetch(self):
        """Record a VIX fetch"""
        self.nse_vix_times.append(time.time())
        self.save_state()
    
    def can_fetch_option_chain(self):
        """Check if we can fetch option chain"""
        now = time.time()
        
        # Minimum interval (15 seconds)
        if self.nse_option_times:
            last = self.nse_option_times[-1]
            elapsed = now - last
            if elapsed < 15:
                return False, f"Rate limit: wait {15 - elapsed:.0f}s before next option chain fetch"
        
        # Per minute limit (5 fetches/minute max)
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
        
        # Check cooldown after loss (5 minutes)
        if self.last_loss_time:
            elapsed = now - self.last_loss_time
            if elapsed < 300:
                return False, f"Cooldown after loss: wait {300 - elapsed:.0f}s"
        
        # Check min time between trades (60 seconds)
        if self.trade_times:
            last = self.trade_times[-1]
            elapsed = now - last
            if elapsed < 60:
                return False, f"Rate limit: wait {60 - elapsed:.0f}s between trades"
        
        # Check per hour limit (10 trades/hour max)
        recent_hour = [t for t in self.trade_times if now - t < 3600]
        if len(recent_hour) >= 10:
            return False, f"Rate limit: {len(recent_hour)} trades in last hour (max 10)"
        
        # Check per day limit (30 trades/day max)
        today = datetime.now().date()
        today_trades = sum(1 for t in self.trade_times 
                          if datetime.fromtimestamp(t).date() == today)
        if today_trades >= 30:
            return False, f"Rate limit: {today_trades} trades today (max 30)"
        
        return True, "OK"
    
    def record_trade(self, pnl=None):
        """Record a trade execution"""
        self.trade_times.append(time.time())
        if pnl is not None and pnl < 0:
            self.last_loss_time = time.time()
        self.save_state()
    
    # ============ SIGNAL LIMITS ============
    
    def can_generate_signal(self, strategy_name=None):
        """Check if we can generate a signal"""
        now = time.time()
        
        # Check min time between signals (5 minutes)
        if self.signal_times:
            last = self.signal_times[-1]
            elapsed = now - last
            if elapsed < 300:
                return False, f"Rate limit: wait {300 - elapsed:.0f}s between signals"
        
        # Check per hour limit (5 signals/hour max)
        recent_hour = [t for t in self.signal_times if now - t < 3600]
        if len(recent_hour) >= 5:
            return False, f"Rate limit: {len(recent_hour)} signals in last hour (max 5)"
        
        # Check per day limit (15 signals/day max across all strategies)
        today_signals = sum(1 for t in self.signal_times 
                           if datetime.fromtimestamp(t).date() == datetime.now().date())
        if today_signals >= 15:
            return False, f"Rate limit: {today_signals} signals today (max 15)"
        
        return True, "OK"
    
    def record_signal(self):
        """Record a signal generation"""
        self.signal_times.append(time.time())
    
    # ============ STATUS ============
    
    def get_status(self):
        """Get current rate limit status"""
        now = time.time()
        today = datetime.now().date()
        
        return {
            "dhan_orders": {
                "last_second": len([t for t in self.dhan_order_times if now - t < 1]),
                "last_minute": len([t for t in self.dhan_order_times if now - t < 60]),
                "today": len([t for t in self.dhan_order_times 
                            if datetime.fromtimestamp(t).date() == today])
            },
            "nse_vix_fetches": {
                "last_minute": len([t for t in self.nse_vix_times if now - t < 60]),
                "today": len([t for t in self.nse_vix_times 
                            if datetime.fromtimestamp(t).date() == today])
            },
            "trades": {
                "last_hour": len([t for t in self.trade_times if now - t < 3600]),
                "today": len([t for t in self.trade_times 
                            if datetime.fromtimestamp(t).date() == today])
            },
            "signals": {
                "last_hour": len([t for t in self.signal_times if now - t < 3600]),
                "today": len([t for t in self.signal_times 
                            if datetime.fromtimestamp(t).date() == today])
            },
            "in_cooldown": self.last_loss_time is not None and (time.time() - self.last_loss_time) < 300
        }


# Global instance
_rate_limiter = None

def get_rate_limiter():
    """Get or create global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = ApexRateLimiter()
    return _rate_limiter

# Convenience functions
def check_order_rate_limit():
    return get_rate_limiter().can_place_order()

def check_trade_rate_limit():
    return get_rate_limiter().can_trade()

def check_signal_rate_limit(strategy=None):
    return get_rate_limiter().can_generate_signal(strategy)

def check_vix_rate_limit():
    return get_rate_limiter().can_fetch_india_vix()

def record_order():
    get_rate_limiter().record_order()

def record_trade(pnl=None):
    get_rate_limiter().record_trade(pnl)

def record_signal():
    get_rate_limiter().record_signal()

def record_vix_fetch():
    get_rate_limiter().record_vix_fetch()

def get_rate_limit_status():
    return get_rate_limiter().get_status()


if __name__ == "__main__":
    # Test rate limiter
    print("APEX Rate Limiter Test")
    print("="*50)
    
    limiter = get_rate_limiter()
    
    # Test order limits
    can, msg = check_order_rate_limit()
    print(f"Can place order: {can} - {msg}")
    
    # Test trade limits
    can, msg = check_trade_rate_limit()
    print(f"Can trade: {can} - {msg}")
    
    # Test VIX limits
    can, msg = check_vix_rate_limit()
    print(f"Can fetch VIX: {can} - {msg}")
    
    # Show status
    print("
Rate Limit Status:")
    print(json.dumps(get_rate_limit_status(), indent=2))
