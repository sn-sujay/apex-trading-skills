#!/usr/bin/env python3
"""
APEX Self-Evolution Engine
Autonomous learning system for APEX trading
Run daily at 15:30 IST post-market
"""

import json
from datetime import datetime, timedelta
import statistics
import requests

# Config
STATE_FILE = "~/.apex/state.json"
LOG_FILE = "~/.apex/evolution_log.json"

def self_evolution_cycle():
    """Main autonomous learning loop"""
    print("="*70)
    print("APEX SELF-EVOLUTION ENGINE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*70)
    
    state = load_state()
    trades = state.get('trade_history', [])
    
    if len(trades) < 10:
        print("[LEARN] Not enough trades (<10) for meaningful analysis")
        return state
    
    print(f"[LEARN] Analyzing {len(trades)} trades...")
    
    # Analyze performance
    metrics = analyze_performance(trades)
    print(f"[METRICS] Win Rate: {metrics.get('win_rate', 0):.1f}%, "
          f"Expectancy: {metrics.get('expectancy', 0):.2f}%, "
          f"PF: {metrics.get('profit_factor', 0):.2f}")
    
    # Adjust strategy weights
    new_weights, weight_changes = optimize_strategy_weights(metrics, state, trades)
    state['strategy_weights'] = new_weights
    
    if weight_changes:
        print(f"[WEIGHTS] Updated: {weight_changes}")
    
    # Detect weaknesses
    weaknesses = identify_weaknesses(metrics, trades, state)
    print(f"[WEAKNESS] Found {len(weaknesses)} areas to improve")
    
    # Auto-implement fixes
    implementations = 0
    for weakness in weaknesses[:2]:  # Max 2 per cycle
        feature = select_feature_to_implement(weakness)
        if feature and should_implement_now(state):
            print(f"[AUTO-IMPL] Queuing: {feature} ({weakness['reason']})")
            state = queue_implementation(state, feature, weakness)
            implementations += 1
    
    # Save evolution
    state['last_evolution'] = {
        'timestamp': datetime.now().isoformat(),
        'metrics': metrics,
        'new_weights': new_weights,
        'weaknesses_found': len(weaknesses),
        'implementations_queued': implementations
    }
    
    save_state(state)
    log_evolution(state['last_evolution'])
    
    print("="*70)
    return state

def load_state():
    """Load state file"""
    path = os.path.expanduser(STATE_FILE)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return initialize_state()

def save_state(state):
    """Save state file"""
    path = os.path.expanduser(STATE_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(state, f, indent=2)

def initialize_state():
    """Initialize fresh state"""
    return {
        # ORIGINAL 5 APEX STRATEGIES - track performance by regime+sentiment combo
        'strategy_performance': {
            'Bull Call Spread': {'trades': 0, 'wins': 0, 'pnl': 0},
            'Bear Put Spread': {'trades': 0, 'wins': 0, 'pnl': 0},
            'Iron Condor': {'trades': 0, 'wins': 0, 'pnl': 0},
            'Long Straddle': {'trades': 0, 'wins': 0, 'pnl': 0},
            'Long Strangle': {'trades': 0, 'wins': 0, 'pnl': 0}
        },
        # Track regime detection accuracy
        'regime_accuracy': {},
        'auto_implemented_features': [],
        'strategy_pause_list': [],
        'trade_history': []
    }

def analyze_performance(trades):
    """Calculate performance metrics"""
    if not trades:
        return {}
    
    pnls = [t.get('pnl', 0) for t in trades]
    winning = [p for p in pnls if p > 0]
    losing = [p for p in pnls if p <= 0]
    
    total_profit = sum(winning) if winning else 0
    total_loss = abs(sum(losing)) if losing else 0.001
    
    return {
        'total_trades': len(trades),
        'winning_trades': len(winning),
        'losing_trades': len(losing),
        'total_pnl': sum(pnls),
        'win_rate': (len(winning) / len(trades) * 100) if trades else 0,
        'profit_factor': total_profit / total_loss if total_loss else 0,
        'expectancy': calculate_expectancy(trades),
        'max_drawdown': calculate_max_drawdown(trades),
    }

def calculate_expectancy(trades):
    """Calculate expectancy"""
    if not trades:
        return 0
    pnls = [t.get('pnl', 0) for t in trades]
    winning = [p for p in pnls if p > 0]
    losing = [abs(p) for p in pnls if p <= 0]
    
    win_rate = len(winning) / len(trades)
    avg_win = statistics.mean(winning) if winning else 0
    avg_loss = statistics.mean(losing) if losing else 0
    
    return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

def calculate_max_drawdown(trades):
    """Calculate max drawdown"""
    if not trades:
        return 0
    peak = 0
    equity = 0
    max_dd = 0
    for t in trades:
        equity += t.get('pnl', 0)
        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak if peak > 0 else 0
        max_dd = max(max_dd, dd)
    return max_dd * 100

def optimize_strategy_weights(metrics, state, trades):
    """
    ORIGINAL APEX: Track performance by the 5 strategies.
    Returns strategy performance dict and list of underperforming ones.
    """
    strategies = ['Bull Call Spread', 'Bear Put Spread', 'Iron Condor', 'Long Straddle', 'Long Strangle']
    perf = state.get('strategy_performance', {s: {'trades': 0, 'wins': 0, 'pnl': 0} for s in strategies})
    
    changes = []
    
    # Analyze each strategy
    for strategy in strategies:
        st_trades = [t for t in trades if t.get('strategy') == strategy]
        if st_trades:
            wins = len([t for t in st_trades if t.get('pnl', 0) > 0])
            perf[strategy] = {
                'trades': len(st_trades),
                'wins': wins,
                'win_rate': wins / len(st_trades) * 100 if st_trades else 0,
                'pnl': sum(t.get('pnl', 0) for t in st_trades)
            }
            # Flag underperforming strategies
            if len(st_trades) >= 3:
                wr = wins / len(st_trades)
                if wr < 0.40:
                    changes.append(f"{strategy}: {wr:.0%} win rate - consider pausing")
                elif perf[strategy]['pnl'] < -1000:
                    changes.append(f"{strategy}: ₹{perf[strategy]['pnl']} loss - review regime mapping")
    
    return perf, changes

def identify_weaknesses(metrics, trades, state):
    """Find what needs fixing"""
    weaknesses = []
    
    # Large losses
    big_losses = [t for t in trades if t.get('pnl', 0) < -0.5]
    if len(big_losses) >= 3:
        weaknesses.append({
            'type': 'large_losses',
            'reason': f'{len(big_losses)} trades lost >0.5%',
            'fix': 'stop_loss_trailing'
        })
    
    # Breakeven waste
    breakeven = [t for t in trades if -0.1 < t.get('pnl', 0) < 0.1]
    if len(breakeven) >= 5:
        weaknesses.append({
            'type': 'breakeven_waste',
            'reason': f'{len(breakeven)} trades at breakeven',
            'fix': 'breakeven_stop'
        })
    
    # Low expectancy
    if metrics.get('expectancy', 0) < 0.2:
        weaknesses.append({
            'type': 'low_expectancy',
            'reason': f"Expectancy {metrics['expectancy']:.2f}% too low",
            'fix': 'expectancy_filter'
        })
    
    return weaknesses

def select_feature_to_implement(weakness):
    """Map weakness to feature"""
    mapping = {
        'large_losses': 'stop_loss_trailing',
        'breakeven_waste': 'breakeven_stop',
        'low_expectancy': 'expectancy_filter',
    }
    return mapping.get(weakness['type'])

def should_implement_now(state):
    """Rate limiting"""
    impls = state.get('auto_implemented_features', [])
    if not impls:
        return True
    last = impls[-1]
    days = (datetime.now() - datetime.fromisoformat(last['date'])).days
    return days >= 2

def queue_implementation(state, feature, weakness):
    """Queue feature for implementation"""
    if 'auto_implemented_features' not in state:
        state['auto_implemented_features'] = []
    
    state['auto_implemented_features'].append({
        'feature': feature,
        'date': datetime.now().isoformat(),
        'reason': weakness['reason'],
        'status': 'queued'
    })
    return state

def log_evolution(entry):
    """Log to evolution log"""
    path = os.path.expanduser(LOG_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a') as f:
        f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    import os
    self_evolution_cycle()
