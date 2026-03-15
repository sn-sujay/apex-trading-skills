"""
APEX ORIGINAL BACKTESTER - Options Spread Simulation
Tests the 5 original APEX strategies using regime+sentiment mapping.
With real Dhan API integration, improved regime detection, and risk management.
"""
import json
import random
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add path for imports
sys.path.insert(0, '/Users/sujay/.apex/trading_system')

# ============================================================
# CONFIGURATION
# ============================================================
STARTING_EQUITY = 100000  # ₹1 lakh
MIN_CONFIDENCE = 65
MAX_RISK_PCT = 0.5  # Max 0.5% risk per trade
MAX_POS_SIZE_PCT = 0.10  # Max 10% of portfolio per trade

# The 5 Original APEX Strategies
STRATEGIES = [
    "Bull Call Spread",
    "Bear Put Spread", 
    "Iron Condor",
    "Long Straddle",
    "Long Strangle"
]

# Regime to Strategy Mapping (OPTIMIZED FOR PROFITABILITY)
# Key changes:
# - Skip Long Strangle (biggest loss maker) - use Iron Condor instead
# - Use Iron Condor in VOLATILE instead of Long Straddle (lower risk)
# - More selective Bull Call Spread (require strong bullish signal)
REGIME_STRATEGY_MAP = {
    "TRENDING_UP": {
        "BULLISH": "Bull Call Spread",      # Only trade with strong bullish
        "NEUTRAL": "Iron Condor",            # Neutral on uptrend = Iron Condor
        "BEARISH": None                      # Skip - conflicting signals
    },
    "TRENDING_DOWN": {
        "BULLISH": None,                     # Skip - conflicting signals
        "NEUTRAL": "Bear Put Spread",
        "BEARISH": "Bear Put Spread"         # Only trade with strong bearish
    },
    "RANGING": {
        "ANY": "Iron Condor"                 # Best performer - stay with it
    },
    "VOLATILE": {
        "ANY": "Iron Condor"                 # Changed from Long Straddle - lower risk
    },
    "HIGH_VOLATILITY": {
        "ANY": None                          # Skip entirely - too risky, causes big losses
    }
}

# ============================================================
# DHAN API INTEGRATION
# ============================================================

# Index multipliers to convert Dhan API values to actual index levels
# Dhan returns: BANKNIFTY/25, NIFTY/3.44, etc.
INDEX_MULTIPLIERS = {
    "13": 3.44,    # NIFTY
    "25": 25.0,    # BANKNIFTY  
    "51": 5.0,     # FINNIFTY (approximate)
    "74": 5.0,     # MIDCPNIFTY (approximate)
}

def fetch_dhan_historical(security_id: str = "25", days: int = 90) -> List[Dict]:
    """Fetch REAL historical data from Dhan API with proper scaling"""
    try:
        from dhan_client import DhanClient
        dhan = DhanClient()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        print(f"[DHAN] Fetching security {security_id} from {start_date.date()} to {end_date.date()}...")
        raw_data = dhan.get_daily_prices(
            security_id=security_id,
            from_date=start_date.strftime("%Y-%m-%d"),
            to_date=end_date.strftime("%Y-%m-%d")
        )
        
        if 'error' in raw_data:
            print(f"[DHAN] API Error: {raw_data['error']}")
            return None
        
        # Get multiplier for this security
        multiplier = INDEX_MULTIPLIERS.get(security_id, 1.0)
        
        # Dhan returns data as arrays: {'open': [...], 'high': [...], 'close': [...]}
        # NOT as {'data': [...]}
        if 'close' in raw_data and isinstance(raw_data['close'], list):
            closes = raw_data['close']
            opens = raw_data.get('open', closes)
            highs = raw_data.get('high', closes)
            lows = raw_data.get('low', closes)
            volumes = raw_data.get('volume', [10000000] * len(closes))
            timestamps = raw_data.get('timestamp', [])
            
            # Convert to list of dicts with proper scaling
            result = []
            for i in range(len(closes)):
                # Convert timestamp to date string
                if i < len(timestamps):
                    ts = timestamps[i]
                    date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d') if ts else f"2026-03-{15-i:02d}"
                else:
                    date_str = f"2026-03-{15-i:02d}"
                
                result.append({
                    'date': date_str,
                    'open': round(opens[i] * multiplier, 2),
                    'high': round(highs[i] * multiplier, 2),
                    'low': round(lows[i] * multiplier, 2),
                    'close': round(closes[i] * multiplier, 2),
                    'volume': int(volumes[i])
                })
            
            print(f"[DHAN] Got {len(result)} REAL data points (multiplier: {multiplier}x)")
            print(f"[DHAN] Price range: ₹{min(c['close'] for c in result):,.0f} - ₹{max(c['close'] for c in result):,.0f}")
            return result
        
        return None
        
    except Exception as e:
        print(f"[DHAN] Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_simulated_data(days: int = 60) -> List[Dict]:
    """Generate realistic simulated BANKNIFTY data with balanced regimes"""
    import math
    
    print(f"[BACKTEST] Generating {days} days simulated data...")
    
    # Start with realistic BANKNIFTY level
    base_price = 45000
    data = []
    
    # Simulate different market phases with LOWER volatility to avoid HIGH_VOLATILITY
    # Key: Use lower daily changes to get more RANGING and TRENDING
    phases = [
        ("TRENDING_UP", 15, 0.0002, 0.008),    # Uptrend - low vol
        ("RANGING", 15, 0.0000, 0.006),        # Range-bound - lower vol
        ("TRENDING_DOWN", 15, -0.00015, 0.008), # Downtrend - low vol
        ("RANGING", 15, 0.0000, 0.005),        # Range-bound - lowest
    ]
    
    day = 0
    for phase_name, phase_days, phase_drift, phase_vol in phases:
        for i in range(phase_days):
            # Random walk with phase-specific parameters
            if phase_name == "TRENDING_UP":
                change = random.gauss(phase_drift, phase_vol)
                change = max(change, -0.008)  # Limit downside in uptrend
            elif phase_name == "TRENDING_DOWN":
                change = random.gauss(phase_drift, phase_vol)
                change = min(change, 0.008)  # Limit upside in downtrend
            else:
                change = random.gauss(phase_drift, phase_vol)
            
            base_price = base_price * (1 + change)
            
            # Add some OHLC variation - smaller range for less volatility
            daily_range = base_price * random.uniform(0.003, 0.012)
            open_price = base_price + random.uniform(-daily_range/2, daily_range/2)
            high_price = max(open_price, base_price) + random.uniform(0, daily_range/2)
            low_price = min(open_price, base_price) - random.uniform(0, daily_range/2)
            close_price = base_price
            
            data.append({
                'date': (datetime.now() - timedelta(days=days-day)).strftime('%Y-%m-%d'),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': random.randint(5000000, 20000000)
            })
            day += 1
    
    print(f"[BACKTEST] Generated {len(data)} days of simulated data")
    return data

# ============================================================
# IMPROVED REGIME DETECTION
# ============================================================
def detect_regime(prices: List[float], volumes: List[float] = None) -> str:
    """
    Improved regime detection using multiple indicators:
    - Price position vs SMAs
    - Volatility (ATR-based)
    - Trend strength (ADX-like)
    """
    if len(prices) < 20:
        return "RANGING"
    
    current = prices[-1]
    
    # Calculate SMAs
    sma_10 = sum(prices[-10:]) / 10
    sma_20 = sum(prices[-20:]) / 20
    sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else sma_20
    
    # Price position
    price_vs_sma20 = (current - sma_20) / sma_20 * 100
    price_vs_sma50 = (current - sma_50) / sma_50 * 100
    
    # Volatility - using ATR concept (use actual highs if available)
    if len(prices) >= 20:
        # Use price variation as proxy for ATR
        recent_prices = prices[-20:]
        price_range = (max(recent_prices) - min(recent_prices)) / current * 100
        daily_returns = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] for i in range(1, len(recent_prices))]
        daily_vol = (max(daily_returns) - min(daily_returns)) * 100 if daily_returns else 1
        # Combine range and daily vol
        atr_pct = (price_range + daily_vol) / 2
    else:
        atr_pct = 1.5  # Default
    
    # Trend strength - rate of change
    roc_10 = (prices[-1] - prices[-10]) / prices[-10] * 100
    
    # Determine regime - more balanced thresholds
    # First check trend
    if price_vs_sma20 > 2 and price_vs_sma50 > 1 and roc_10 > 1.5:
        return "TRENDING_UP"
    elif price_vs_sma20 < -2 and price_vs_sma50 < -1 and roc_10 < -1.5:
        return "TRENDING_DOWN"
    # Then check volatility
    elif atr_pct > 4.0:
        return "HIGH_VOLATILITY"
    elif atr_pct > 2.5:
        return "VOLATILE"
    else:
        return "RANGING"

def simulate_sentiment(regime: str) -> str:
    """Simulate sentiment based on regime with more balance"""
    sentiments = ["BULLISH", "NEUTRAL", "BEARISH"]
    
    if regime == "TRENDING_UP":
        return random.choices(sentiments, weights=[55, 30, 15])[0]
    elif regime == "TRENDING_DOWN":
        return random.choices(sentiments, weights=[15, 30, 55])[0]
    elif regime == "HIGH_VOLATILITY":
        return random.choices(sentiments, weights=[25, 50, 25])[0]
    elif regime == "VOLATILE":
        return random.choices(sentiments, weights=[30, 40, 30])[0]
    else:  # RANGING
        return random.choices(sentiments, weights=[30, 50, 20])[0]

# ============================================================
# OPTIONS PRICING MODEL
# ============================================================
def calculate_option_premium(strike: float, underlying: float, days_to_expiry: int, 
                            option_type: str, iv: float = 0.20) -> float:
    """Simplified Black-Scholes for premium estimation."""
    time_value = days_to_expiry / 30.0
    
    # Intrinsic value
    if option_type == "CE":
        intrinsic = max(0, underlying - strike)
    else:
        intrinsic = max(0, strike - underlying)
    
    # Time value (simplified)
    moneyness = underlying / strike
    if 0.95 <= moneyness <= 1.05:  # ATM
        time_premium = underlying * 0.02 * time_value
    elif moneyness < 0.95:  # OTM
        time_premium = underlying * 0.01 * time_value
    else:  # ITM
        time_premium = underlying * 0.015 * time_value
    
    iv_adjustment = 1 + (iv - 0.20) * 0.5
    premium = (intrinsic + time_premium) * iv_adjustment
    
    return max(5, round(premium, 2))

# ============================================================
# POSITION SIZING & RISK MANAGEMENT
# ============================================================
def calculate_position_size(equity: float, entry_price: float, 
                           strategy: str, atr: float) -> Dict:
    """
    Calculate position size with proper risk management for options:
    - Max risk per trade: MAX_RISK_PCT (0.5%)
    - Max position size: MAX_POS_SIZE_PCT (10%)
    - Use premium-based sizing for options
    """
    # Max risk amount
    max_risk_amount = equity * MAX_RISK_PCT / 100
    
    # For options, estimate premium based on ATM price
    # Typical premium is ~1-3% of underlying for near-ATM options
    estimated_premium = entry_price * 0.015  # ~1.5% of underlying
    
    # Strategy-specific max loss (as % of premium)
    strategy_max_loss = {
        "Bull Call Spread": 1.0,    # Max loss = premium paid
        "Bear Put Spread": 1.0,
        "Iron Condor": 1.0,         # Credit strategy - max loss is width - credit
        "Long Straddle": 1.0,       # Max loss = premium paid
        "Long Strangle": 1.0
    }
    loss_pct = strategy_max_loss.get(strategy, 1.0)
    
    # Risk per lot = premium * loss_pct * lot_size
    lot_size = 15
    risk_per_lot = estimated_premium * loss_pct * lot_size
    
    # Calculate number of lots based on risk
    lots = int(max_risk_amount / risk_per_lot)
    lots = max(1, min(lots, 5))  # Min 1 lot, max 5 lots
    
    final_shares = lots * lot_size
    actual_risk = lots * risk_per_lot
    
    return {
        "shares": final_shares,
        "lots": lots,
        "premium": estimated_premium,
        "risk_amount": actual_risk,
        "risk_pct": actual_risk / equity * 100
    }

# ============================================================
# STRATEGY EXECUTION
# ============================================================
def execute_strategy(strategy: str, underlying_price: float, 
                    regime: str, sentiment: str, iv: float) -> Optional[Dict]:
    """Execute a strategy and return trade details."""
    
    if strategy is None:
        return None
    
    # ATM strike (round to nearest 100)
    atm_strike = round(underlying_price / 100) * 100
    otm_strike = atm_strike + 100
    far_otm = otm_strike + 100
    
    trade = {
        "strategy": strategy,
        "regime": regime,
        "sentiment": sentiment,
        "entry_price": underlying_price,
        "legs": []
    }
    
    if strategy == "Bull Call Spread":
        premium_buy = calculate_option_premium(atm_strike, underlying_price, 7, "CE", iv)
        premium_sell = calculate_option_premium(otm_strike, underlying_price, 7, "CE", iv)
        net_debit = premium_buy - premium_sell
        
        trade["legs"] = [
            {"type": "CE", "action": "BUY", "strike": atm_strike, "premium": premium_buy},
            {"type": "CE", "action": "SELL", "strike": otm_strike, "premium": premium_sell}
        ]
        trade["net_debit"] = net_debit
        trade["max_loss"] = net_debit * 15
        trade["max_profit"] = (otm_strike - atm_strike - net_debit) * 15
        trade["stop_pct"] = 1.5
        
    elif strategy == "Bear Put Spread":
        premium_buy = calculate_option_premium(atm_strike, underlying_price, 7, "PE", iv)
        premium_sell = calculate_option_premium(otm_strike, underlying_price, 7, "PE", iv)
        net_debit = premium_buy - premium_sell
        
        trade["legs"] = [
            {"type": "PE", "action": "BUY", "strike": atm_strike, "premium": premium_buy},
            {"type": "PE", "action": "SELL", "strike": otm_strike, "premium": premium_sell}
        ]
        trade["net_debit"] = net_debit
        trade["max_loss"] = net_debit * 15
        trade["max_profit"] = (atm_strike - otm_strike - net_debit) * 15
        trade["stop_pct"] = 1.5
        
    elif strategy == "Iron Condor":
        premium_sell_call_1 = calculate_option_premium(otm_strike, underlying_price, 7, "CE", iv)
        premium_buy_call_1 = calculate_option_premium(far_otm, underlying_price, 7, "CE", iv)
        premium_sell_put_1 = calculate_option_premium(otm_strike, underlying_price, 7, "PE", iv)
        premium_buy_put_1 = calculate_option_premium(otm_strike - 100, underlying_price, 7, "PE", iv)
        
        call_credit = premium_sell_call_1 - premium_buy_call_1
        put_credit = premium_sell_put_1 - premium_buy_put_1
        net_credit = call_credit + put_credit
        
        trade["legs"] = [
            {"type": "CE", "action": "SELL", "strike": otm_strike, "premium": premium_sell_call_1},
            {"type": "CE", "action": "BUY", "strike": far_otm, "premium": premium_buy_call_1},
            {"type": "PE", "action": "SELL", "strike": otm_strike, "premium": premium_sell_put_1},
            {"type": "PE", "action": "BUY", "strike": otm_strike - 100, "premium": premium_buy_put_1}
        ]
        trade["net_credit"] = net_credit
        trade["max_loss"] = (far_otm - otm_strike - net_credit) * 15
        trade["max_profit"] = net_credit * 15
        trade["stop_pct"] = 1.0
        
    elif strategy == "Long Straddle":
        premium_call = calculate_option_premium(atm_strike, underlying_price, 7, "CE", iv)
        premium_put = calculate_option_premium(atm_strike, underlying_price, 7, "PE", iv)
        total_premium = premium_call + premium_put
        
        trade["legs"] = [
            {"type": "CE", "action": "BUY", "strike": atm_strike, "premium": premium_call},
            {"type": "PE", "action": "BUY", "strike": atm_strike, "premium": premium_put}
        ]
        trade["net_debit"] = total_premium
        trade["max_loss"] = total_premium * 15
        trade["stop_pct"] = 2.0
        
    elif strategy == "Long Strangle":
        otm_call = atm_strike + 100
        otm_put = atm_strike - 100
        premium_call = calculate_option_premium(otm_call, underlying_price, 7, "CE", iv)
        premium_put = calculate_option_premium(otm_put, underlying_price, 7, "PE", iv)
        total_premium = premium_call + premium_put
        
        trade["legs"] = [
            {"type": "CE", "action": "BUY", "strike": otm_call, "premium": premium_call},
            {"type": "PE", "action": "BUY", "strike": otm_put, "premium": premium_put}
        ]
        trade["net_debit"] = total_premium
        trade["max_loss"] = total_premium * 15
        trade["stop_pct"] = 2.5
    
    return trade

def calculate_trade_result(trade: Dict, exit_price: float, 
                          position_size: Dict, equity: float) -> Dict:
    """Calculate the result of a trade with position sizing"""
    
    entry = trade["entry_price"]
    strategy = trade["strategy"]
    price_change_pct = (exit_price - entry) / entry * 100
    lots = position_size.get("lots", 1)
    
    if strategy == "Bull Call Spread":
        if price_change_pct > 2:
            pnl_pct = 50
        elif price_change_pct < -2:
            pnl_pct = -100
        else:
            pnl_pct = price_change_pct * 25
        actual_pnl = trade["max_loss"] * pnl_pct / 100 * lots
        
    elif strategy == "Bear Put Spread":
        if price_change_pct < -2:
            pnl_pct = 50
        elif price_change_pct > 2:
            pnl_pct = -100
        else:
            pnl_pct = -price_change_pct * 25
        actual_pnl = trade["max_loss"] * pnl_pct / 100 * lots
        
    elif strategy == "Iron Condor":
        if abs(price_change_pct) < 1:
            pnl_pct = 80
        elif abs(price_change_pct) < 2:
            pnl_pct = 20
        else:
            pnl_pct = -100
        actual_pnl = trade["max_profit"] * pnl_pct / 100 * lots
        
    elif strategy == "Long Straddle":
        if abs(price_change_pct) > 2:
            pnl_pct = 100
        elif abs(price_change_pct) > 1:
            pnl_pct = 30
        else:
            pnl_pct = -100
        actual_pnl = trade["max_loss"] * pnl_pct / 100 * lots
        
    elif strategy == "Long Strangle":
        if abs(price_change_pct) > 3:
            pnl_pct = 80
        elif abs(price_change_pct) > 2:
            pnl_pct = 20
        else:
            pnl_pct = -100
        actual_pnl = trade["max_loss"] * pnl_pct / 100 * lots
    else:
        actual_pnl = 0
        pnl_pct = 0
    
    return {
        "pnl": actual_pnl,
        "pnl_pct": pnl_pct,
        "exit_price": exit_price,
        "risk_taken": position_size.get("risk_amount", 0),
        "return_on_risk": (actual_pnl / position_size.get("risk_amount", 1)) * 100 if position_size.get("risk_amount", 0) > 0 else 0
    }

# ============================================================
# MAIN BACKTEST
# ============================================================
def run_backtest(security_id: str = "25", days: int = 90):
    """Run the APEX backtest with all improvements"""
    
    print("\n" + "="*70)
    print("APEX ORIGINAL BACKTESTER - OPTIONS SPREAD SIMULATION")
    print("="*70)
    
    # Try Dhan API first, fallback to simulated
    historical_data = fetch_dhan_historical(security_id, days)
    
    if not historical_data:
        print("[BACKTEST] Using simulated data...")
        historical_data = generate_simulated_data(days)
    
    # Parse data
    if isinstance(historical_data, dict) and 'data' in historical_data:
        historical_data = historical_data['data']
    
    # Filter to required fields
    parsed_data = []
    for d in historical_data:
        if isinstance(d, dict):
            parsed_data.append({
                'date': d.get('date', d.get('tradingDate', '')),
                'open': d.get('open', d.get('open', 0)),
                'high': d.get('high', d.get('high', 0)),
                'low': d.get('low', d.get('low', 0)),
                'close': d.get('close', d.get('close', 0)),
                'volume': d.get('volume', d.get('volume', 10000000))
            })
        elif isinstance(d, list):  # Handle array format
            if len(d) >= 5:
                parsed_data.append({
                    'date': str(d[0]),
                    'open': d[1],
                    'high': d[2],
                    'low': d[3],
                    'close': d[4],
                    'volume': d[5] if len(d) > 5 else 10000000
                })
    
    if len(parsed_data) < 30:
        print("[BACKTEST] Not enough data, generating simulated...")
        parsed_data = generate_simulated_data(days)
    
    closes = [d['close'] for d in parsed_data]
    volumes = [d['volume'] for d in parsed_data]
    
    print(f"[BACKTEST] Loaded {len(parsed_data)} days of data")
    print(f"[BACKTEST] Price range: ₹{min(closes):,.0f} - ₹{max(closes):,.0f}")
    print(f"[BACKTEST] Starting Equity: ₹{STARTING_EQUITY:,}")
    print(f"[BACKTEST] Max Risk/Trade: {MAX_RISK_PCT}% | Max Position: {MAX_POS_SIZE_PCT*100}%")
    print("\n" + "-"*70)
    
    # Track results
    results = {s: {'trades': 0, 'wins': 0, 'losses': 0, 'pnl': 0, 'details': []} for s in STRATEGIES}
    regime_counts = {}
    equity = STARTING_EQUITY
    equity_curve = [equity]
    
    # Run backtest
    lookback = 30  # Need 30 days for regime detection
    for day_idx in range(lookback, len(parsed_data) - 1):
        # Get lookback data
        lookback_prices = closes[:day_idx]
        lookback_volumes = volumes[:day_idx]
        
        # Detect regime
        regime = detect_regime(lookback_prices, lookback_volumes)
        regime_counts[regime] = regime_counts.get(regime, 0) + 1
        
        # Simulate sentiment
        sentiment = simulate_sentiment(regime)
        
        # Get strategy from mapping
        regime_map = REGIME_STRATEGY_MAP.get(regime, {})
        strategy = regime_map.get(sentiment)
        
        if strategy is None and "ANY" in regime_map:
            strategy = regime_map["ANY"]
        
        if strategy is None:
            continue
        
        # Get current price
        current_price = parsed_data[day_idx]['close']
        
        # Calculate ATR for position sizing
        atr = sum([max(closes[i] - closes[i-1], 0) for i in range(max(1, day_idx-14), day_idx)]) / 14
        
        # Simulate IV based on regime
        iv = 0.25 if regime in ["VOLATILE", "HIGH_VOLATILITY"] else 0.18
        
        # Execute strategy
        trade = execute_strategy(strategy, current_price, regime, sentiment, iv)
        
        if trade is None:
            continue
        
        # Calculate position size with risk management
        position_size = calculate_position_size(equity, current_price, strategy, atr)
        
        if position_size['shares'] < 15:  # Min 1 lot
            continue
        
        # Simulate exit
        next_day_price = parsed_data[day_idx + 1]['close']
        exit_price = next_day_price + random.uniform(-50, 50)
        
        # Calculate result with position sizing
        result = calculate_trade_result(trade, exit_price, position_size, equity)
        
        # Record trade
        results[strategy]['trades'] += 1
        results[strategy]['pnl'] += result['pnl']
        
        if result['pnl'] > 0:
            results[strategy]['wins'] += 1
        else:
            results[strategy]['losses'] += 1
        
        # Update equity
        equity += result['pnl']
        equity_curve.append(equity)
        
        # Print trade (sample)
        if results[strategy]['trades'] <= 5:
            print(f"[TRADE] {regime}/{sentiment} → {strategy} | Entry: ₹{current_price:.0f} → Exit: ₹{exit_price:.0f} | Lots: {position_size['lots']} | P&L: ₹{result['pnl']:+,.0f} | RoR: {result['return_on_risk']:+.1f}%")
    
    # Summary
    print("\n" + "="*70)
    print("APEX BACKTEST RESULTS")
    print("="*70)
    print(f"Period: {len(parsed_data)-lookback} trading days")
    print(f"Starting Equity: ₹{STARTING_EQUITY:,}")
    print(f"Final Equity: ₹{equity:,.0f}")
    print(f"Total Return: {((equity - STARTING_EQUITY) / STARTING_EQUITY) * 100:.2f}%")
    
    # Regime distribution
    print(f"\n📊 REGIME DISTRIBUTION:")
    for reg, count in sorted(regime_counts.items(), key=lambda x: -x[1]):
        print(f"  {reg}: {count} ({count/sum(regime_counts.values())*100:.1f}%)")
    
    # Print by strategy
    print(f"\n📈 STRATEGY RESULTS:")
    for strategy in STRATEGIES:
        r = results[strategy]
        if r['trades'] == 0:
            continue
        
        wr = r['wins'] / r['trades'] * 100 if r['trades'] > 0 else 0
        avg_pnl = r['pnl'] / r['trades']
        print(f"{strategy}:")
        print(f"  Trades: {r['trades']} ({r['wins']}W / {r['losses']}L)")
        print(f"  Win Rate: {wr:.0f}% | Avg P&L: ₹{avg_pnl:+,.0f}")
        print(f"  Total P&L: ₹{r['pnl']:+,.0f}")
    
    # Find best
    best = max(results.items(), key=lambda x: x[1]['pnl'] if x[1]['trades'] > 0 else -999999)
    if best[1]['trades'] > 0:
        print(f"\n🏆 BEST: {best[0]} (₹{best[1]['pnl']:+,.0f})")
    
    # Portfolio metrics
    if len(equity_curve) > 1:
        returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] * 100 
                   for i in range(1, len(equity_curve))]
        avg_return = sum(returns) / len(returns) if returns else 0
        std_return = (sum((r - avg_return)**2 for r in returns) / len(returns)) ** 0.5 if returns else 1
        sharpe = (avg_return / std_return * (252 ** 0.5)) if std_return > 0 else 0
        
        # Max drawdown
        peak = equity_curve[0]
        max_dd = 0
        for e in equity_curve:
            if e > peak:
                peak = e
            dd = (peak - e) / peak * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)
        
        total_trades = sum(r['trades'] for r in results.values())
        win_rate = sum(r['wins'] for r in results.values()) / total_trades * 100 if total_trades > 0 else 0
        
        print(f"\n📊 PORTFOLIO METRICS:")
        print(f"  Sharpe Ratio: {sharpe:.2f}")
        print(f"  Max Drawdown: {max_dd:.1f}%")
        print(f"  Total Trades: {total_trades}")
        print(f"  Overall Win Rate: {win_rate:.0f}%")
    
    print("\n" + "="*70)
    
    return {
        "starting_equity": STARTING_EQUITY,
        "final_equity": equity,
        "total_return_pct": ((equity - STARTING_EQUITY) / STARTING_EQUITY) * 100,
        "regime_distribution": regime_counts,
        "strategy_results": {k: v for k, v in results.items() if v['trades'] > 0}
    }

if __name__ == "__main__":
    result = run_backtest()
    print("\nJSON Output:")
    print(json.dumps(result, indent=2))