"""
APEX Weekend Backtesting Engine - Improved Version
Walk-forward validation for strategy testing with better signal generation
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import requests
import yaml
from pathlib import Path
import random

class WeekendBacktester:
    """
    Weekend backtesting using historical data.
    Provides simulated trades for faster Kelly learning.
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.load_historical_data()
    
    def _load_config(self):
        config_path = Path.home() / ".apex" / "config.yaml"
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    def load_historical_data(self):
        """Load historical BANKNIFTY data from Dhan API"""
        from trading_system.dhan_client import DhanClient
        
        self.dhan = DhanClient()
        
        # Fetch from Dhan API
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)  # Get 60 days for more signals
        
        try:
            # Get historical prices for BANKNIFTY (security ID: 25)
            data = self.dhan.get_daily_prices(
                security_id="25",
                from_date=start_date.strftime("%Y-%m-%d"),
                to_date=end_date.strftime("%Y-%m-%d")
            )
            
            if 'close' in data:
                # Convert to list of dicts
                self.historical_data = []
                for i in range(len(data['close'])):
                    self.historical_data.append({
                        'date': data.get('timestamp', ['']*len(data['close']))[i] if i < len(data.get('timestamp', [])) else str(i),
                        'open': data['open'][i],
                        'high': data['high'][i],
                        'low': data['low'][i],
                        'close': data['close'][i],
                        'volume': data['volume'][i]
                    })
                print(f"[BACKTEST] Loaded {len(self.historical_data)} days of historical data")
            else:
                print(f"[BACKTEST] Error loading data: {data}")
                self.historical_data = []
            
        except Exception as e:
            print(f"[BACKTEST] Error loading data: {e}")
            self.historical_data = []
    
    def calculate_indicators(self, prices: List[float], highs: List[float], lows: List[float]) -> Dict:
        """Calculate technical indicators"""
        indicators = {}
        
        # Simple Moving Averages
        for period in [5, 10, 20, 50]:
            if len(prices) >= period:
                indicators[f'sma_{period}'] = sum(prices[-period:]) / period
            else:
                indicators[f'sma_{period}'] = prices[-1] if prices else 0
        
        # EMA (exponential)
        for period in [9, 21]:
            if len(prices) >= period:
                multiplier = 2 / (period + 1)
                ema = prices[-period]
                for p in prices[-period:]:
                    ema = (p - ema) * multiplier + ema
                indicators[f'ema_{period}'] = ema
            else:
                indicators[f'ema_{period}'] = prices[-1] if prices else 0
        
        # RSI
        if len(prices) >= 15:
            gains = []
            losses = []
            for i in range(len(prices) - 14, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / 14
            avg_loss = sum(losses) / 14
            
            if avg_loss == 0:
                indicators['rsi'] = 100.0
            else:
                rs = avg_gain / avg_loss
                indicators['rsi'] = 100 - (100 / (1 + rs))
        else:
            indicators['rsi'] = 50.0
        
        # Bollinger Bands
        if len(prices) >= 20:
            sma20 = sum(prices[-20:]) / 20
            variance = sum((p - sma20) ** 2 for p in prices[-20:]) / 20
            std_dev = variance ** 0.5
            indicators['bb_upper'] = sma20 + (2 * std_dev)
            indicators['bb_lower'] = sma20 - (2 * std_dev)
            indicators['bb_middle'] = sma20
        else:
            indicators['bb_upper'] = prices[-1] if prices else 0
            indicators['bb_lower'] = prices[-1] if prices else 0
            indicators['bb_middle'] = prices[-1] if prices else 0
        
        # ATR (Average True Range)
        if len(highs) >= 14 and len(lows) >= 14 and len(prices) >= 15:
            true_ranges = []
            for i in range(len(prices) - 14, len(prices)):
                tr = max(
                    highs[i] - lows[i],
                    abs(highs[i] - prices[i-1]),
                    abs(lows[i] - prices[i-1])
                )
                true_ranges.append(tr)
            indicators['atr'] = sum(true_ranges) / 14
        else:
            indicators['atr'] = (highs[-1] - lows[-1]) if highs and lows else 0
        
        # MACD
        if len(prices) >= 26:
            # EMA12
            ema12_mult = 2 / 13
            ema12 = sum(prices[-12:]) / 12
            for p in prices[-12:]:
                ema12 = (p - ema12) * ema12_mult + ema12
            
            # EMA26
            ema26_mult = 2 / 27
            ema26 = sum(prices[-26:]) / 26
            for p in prices[-26:]:
                ema26 = (p - ema26) * ema26_mult + ema26
            
            indicators['macd'] = ema12 - ema26
            indicators['macd_signal'] = ema12 - ema26  # Simplified
        else:
            indicators['macd'] = 0
            indicators['macd_signal'] = 0
        
        # Price momentum
        if len(prices) >= 5:
            indicators['momentum'] = (prices[-1] - prices[-5]) / prices[-5] * 100
        else:
            indicators['momentum'] = 0
        
        # Volume SMA
        if len(self.historical_data) >= 20:
            volumes = [d['volume'] for d in self.historical_data[-20:]]
            indicators['volume_sma20'] = sum(volumes) / 20
        else:
            indicators['volume_sma20'] = 1
        
        return indicators
    
    def generate_signal(self, day: Dict, prices: List[float], highs: List[float], 
                       lows: List[float], strategy: str, confidence_boost: float = 0) -> Dict:
        """Generate trading signal based on strategy with improved logic"""
        
        indicators = self.calculate_indicators(prices, highs, lows)
        current_price = day['close']
        current_volume = day.get('volume', 0)
        
        signal = None
        base_confidence = 50
        
        if strategy == 'BREAKOUT':
            # Breakout strategy - price breaks resistance/support
            # Long: Price breaks above 20 SMA with volume
            if (current_price > indicators['sma_20'] * 1.02 and 
                indicators['rsi'] > 50 and 
                current_volume > indicators['volume_sma20'] * 1.2):
                signal = 'LONG'
                base_confidence = 70
            
            # Short: Price breaks below 20 SMA
            elif (current_price < indicators['sma_20'] * 0.98 and 
                  indicators['rsi'] < 50 and 
                  current_volume > indicators['volume_sma20'] * 1.2):
                signal = 'SHORT'
                base_confidence = 70
        
        elif strategy == 'MOMENTUM':
            # Momentum strategy - trend following
            # Long: Price above 50 SMA, RSI in sweet spot, positive momentum
            if (current_price > indicators['sma_50'] and 
                45 < indicators['rsi'] < 75 and 
                indicators['momentum'] > 0):
                signal = 'LONG'
                base_confidence = 75
            
            # Short: Price below 50 SMA, negative momentum
            elif (current_price < indicators['sma_50'] and 
                  25 < indicators['rsi'] < 55 and 
                  indicators['momentum'] < 0):
                signal = 'SHORT'
                base_confidence = 75
        
        elif strategy == 'MEAN_REVERSION':
            # Mean reversion - buy oversold, sell overbought
            # Long: Price at lower Bollinger Band, RSI oversold
            if (current_price <= indicators['bb_lower'] and 
                indicators['rsi'] < 35):
                signal = 'LONG'
                base_confidence = 65
            
            # Short: Price at upper Bollinger Band, RSI overbought
            elif (current_price >= indicators['bb_upper'] and 
                  indicators['rsi'] > 65):
                signal = 'SHORT'
                base_confidence = 65
        
        elif strategy == 'MACD_CROSS':
            # MACD crossover strategy
            if (indicators['macd'] > indicators['macd_signal'] and 
                indicators['rsi'] > 50):
                signal = 'LONG'
                base_confidence = 70
            elif (indicators['macd'] < indicators['macd_signal'] and 
                  indicators['rsi'] < 50):
                signal = 'SHORT'
                base_confidence = 70
        
        elif strategy == 'VOLUME_SPIKE':
            # Volume spike strategy
            if current_volume > indicators['volume_sma20'] * 2:
                if indicators['momentum'] > 1:
                    signal = 'LONG'
                    base_confidence = 65
                elif indicators['momentum'] < -1:
                    signal = 'SHORT'
                    base_confidence = 65
        
        if signal and confidence_boost > 0:
            base_confidence = min(95, base_confidence + confidence_boost)
        
        if signal:
            # Calculate stop loss and target
            atr = indicators.get('atr', current_price * 0.02)
            
            if signal == 'LONG':
                stop_loss = current_price - (2 * atr)
                target = current_price + (3 * atr)
            else:
                stop_loss = current_price + (2 * atr)
                target = current_price - (3 * atr)
            
            return {
                'direction': signal,
                'price': current_price,
                'confidence': base_confidence,
                'stop_loss': stop_loss,
                'target': target,
                'indicators': {k: round(v, 2) for k, v in indicators.items()}
            }
        
        return None
    
    def simulate_trade(self, day: Dict, signal: Dict, equity: float) -> Dict:
        """Simulate a single trade with realistic mechanics"""
        entry_price = signal['price']
        exit_price = day['close']  # Exit at end of day (intraday)
        
        # Calculate P&L percentage
        if signal['direction'] == 'LONG':
            pnl_pct = (exit_price - entry_price) / entry_price * 100
        else:
            pnl_pct = (entry_price - exit_price) / entry_price * 100
        
        # Add some randomness (market slippage simulation)
        pnl_pct += random.uniform(-0.3, 0.3)
        
        # Position size (use 10% of equity)
        position_size = equity * 0.10
        quantity = int(position_size / entry_price)
        
        pnl = pnl_pct * position_size / 100
        
        return {
            'entry_price': entry_price,
            'exit_price': exit_price,
            'quantity': quantity,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'direction': signal['direction'],
            'confidence': signal['confidence']
        }
    
    def run_walk_forward_test(self, strategy: str = 'BREAKOUT') -> Dict:
        """Run walk-forward backtest on historical data"""
        
        if not self.historical_data or len(self.historical_data) < 30:
            return {'status': 'no_data', 'message': 'Insufficient historical data'}
        
        trades = []
        equity_curve = [100000]  # Start with ₹1L
        
        # Start from day 30 to have enough data for indicators
        for i in range(30, len(self.historical_data)):
            day = self.historical_data[i]
            
            # Prepare price data
            prices = [d['close'] for d in self.historical_data[:i]]
            highs = [d['high'] for d in self.historical_data[:i]]
            lows = [d['low'] for d in self.historical_data[:i]]
            
            # Generate signal
            signal = self.generate_signal(day, prices, highs, lows, strategy)
            
            if signal:
                # Simulate trade
                trade = self.simulate_trade(day, signal, equity_curve[-1])
                trades.append(trade)
                
                # Update equity
                new_equity = equity_curve[-1] + trade['pnl']
                equity_curve.append(max(0, new_equity))  # Prevent negative
        
        # Calculate metrics
        if not trades:
            return {
                'strategy': strategy,
                'status': 'no_signals',
                'trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'Kelly_fraction': 0
            }
        
        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] <= 0]
        
        win_rate = len(wins) / len(trades) if trades else 0
        total_pnl = sum(t['pnl'] for t in trades)
        
        # Kelly calculation
        avg_win = sum(t['pnl'] for t in wins) / len(wins) if wins else 0
        avg_loss = abs(sum(t['pnl'] for t in losses) / len(losses)) if losses else 1
        
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio if win_loss_ratio > 0 else 0
        kelly = max(0, min(kelly, 0.25))  # Cap at 25%
        
        # Max drawdown
        peak = equity_curve[0]
        max_dd = 0
        for e in equity_curve:
            if e > peak:
                peak = e
            dd = (peak - e) / peak * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)
        
        return {
            'strategy': strategy,
            'status': 'success',
            'trades': len(trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'win_loss_ratio': win_loss_ratio,
            'Kelly_fraction': kelly,
            'max_drawdown': max_dd,
            'final_equity': equity_curve[-1],
            'start_equity': 100000
        }
    
    def run_all_strategies(self) -> List[Dict]:
        """Run backtest on all strategies"""
        
        strategies = ['BREAKOUT', 'MOMENTUM', 'MEAN_REVERSION', 'MACD_CROSS', 'VOLUME_SPIKE']
        results = []
        
        for strategy in strategies:
            print(f"[BACKTEST] Running {strategy}...")
            result = self.run_walk_forward_test(strategy)
            results.append(result)
        
        return results
    
    def print_results(self, results: List[Dict]):
        """Print formatted backtest results"""
        
        print("\n" + "=" * 70)
        print("APEX BACKTEST RESULTS - BANKNIFTY")
        print("=" * 70)
        
        # Find best strategy
        best_strategy = None
        best_score = -float('inf')
        
        for r in results:
            if r.get('status') != 'success':
                continue
            
            # Score = total_pnl with penalty for high drawdown
            score = r['total_pnl'] - (r['max_drawdown'] * 100)
            
            if score > best_score:
                best_score = score
                best_strategy = r['strategy']
            
            print(f"\n{r['strategy']}:")
            print(f"  Trades: {r['trades']} ({r['wins']}W / {r['losses']}L)")
            print(f"  Win Rate: {r['win_rate']:.0%}")
            print(f"  P&L: ₹{r['total_pnl']:+.0f}")
            print(f"  Avg Win: ₹{r['avg_win']:+.0f} | Avg Loss: ₹{r['avg_loss']:.0f}")
            print(f"  Kelly: {r['Kelly_fraction']:.0%} | Max DD: {r['max_drawdown']:.1f}%")
            print(f"  Final Equity: ₹{r['final_equity']:,.0f}")
        
        if best_strategy:
            print(f"\n{'=' * 70}")
            print(f"🏆 BEST STRATEGY: {best_strategy}")
            print(f"{'=' * 70}")
        
        return best_strategy


# Run if executed directly
if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    sys.path.insert(0, "./trading_system")
    
    bt = WeekendBacktester()
    results = bt.run_all_strategies()
    best = bt.print_results(results)
    
    # Print detailed results as JSON for analysis
    print("\n\nJSON Output:")
    print(json.dumps(results, indent=2))