---
name: apex-live-order-executor
description: Dhan Live Order Executor - Full live trading engine with bracket orders, super orders, and smart limit routing.
tags: [apex, trading, live, execution, orders]
---

# Dhan Live Order Executor

## Purpose
Full Dhan API v2 live execution engine. Places bracket orders, super orders, and multi-leg options strategies with smart limit routing within bid-ask spread.

## Activation
To activate live trading, user must set in config:
```yaml
paper_mode: false
enable_live_trading: true
```

## Capabilities
- **Bracket Orders**: Entry with SL and target in single order
- **Super Orders**: Advanced order types with trailing stop
- **Smart Limit Routing**: 
  - BUY: place at ask - 0.5 tick
  - SELL: place at bid + 0.5 tick
  - 30s unfilled → move to bid/ask
- **Multi-leg Strategies**: Iron condors, butterflies, spreads
- **Error Handling**: Retry logic, auth handling, rate limiting

## Order Types

### Bracket Order
```python
{
    'order_type': 'BRACKET',
    'transaction_type': 'BUY',
    'instrument_token': '12345',
    'quantity': 15,
    'price': 57200,
    'trigger_price': 56800,  # Stop-loss
    'target_price': 57800,
    'trailing_stop_loss': 50,
    'product_type': 'MIS'  # Intraday
}
```

### Super Order
```python
{
    'order_type': 'SUPER',
    'transaction_type': 'SELL',
    'instrument_token': '12345',
    'quantity': 15,
    'price': 0,  # Market
    'trigger_price': 56800,
    'product_type': 'MIS'
}
```

## Smart Routing Logic
```python
def place_smart_limit_order(self, side: str, quantity: int, 
                            bid: float, ask: float) -> dict:
    """
    Smart limit order routing within bid-ask spread
    """
    tick_size = 0.05  # NFO tick size
    
    if side == 'BUY':
        # Place at ask - 0.5 tick
        limit_price = ask - (0.5 * tick_size)
        order_type = 'LIMIT'
    else:  # SELL
        # Place at bid + 0.5 tick
        limit_price = bid + (0.5 * tick_size)
        order_type = 'LIMIT'
    
    # Place order
    order = self.place_order({
        'transaction_type': side,
        'quantity': quantity,
        'price': limit_price,
        'order_type': order_type,
        'product_type': 'MIS'
    })
    
    # Check fill after 30s
    time.sleep(30)
    status = self.get_order_status(order['order_id'])
    
    if status['status'] == 'PENDING':
        # Modify to market price
        if side == 'BUY':
            new_price = ask
        else:
            new_price = bid
        self.modify_order(order['order_id'], {'price': new_price})
    
    return order
```

## Error Handling
| Error | Response | Action |
|-------|----------|--------|
| HTTP 401 (auth) | Fatal | Halt trading, alert |
| HTTP 429 (rate) | Wait 5s | Retry with backoff |
| HTTP 500 | Retry once | Then halt and alert |
| Partial fill | Accept | Log partial, don't chase |

## Implementation
```python
class LiveOrderExecutor(DhanClient):
    """Live order execution with smart routing"""
    
    def execute_signal(self, signal: dict) -> dict:
        # Check if live trading enabled
        if self.config.get('paper_mode', True):
            return {'status': 'PAPER_MODE', 'message': 'Live trading disabled'}
        
        # Get live quotes
        quote = self.get_quote(signal['instrument_token'])
        bid = quote['bid']
        ask = quote['ask']
        
        # Smart limit routing
        order = self.place_smart_limit_order(
            side=signal['direction'],
            quantity=signal['quantity'],
            bid=bid,
            ask=ask
        )
        
        # Log execution
        self.log_execution(signal, order)
        
        return order
```

## Safety Checklist (Before First Live Session)
1. ✅ PAPER_MODE = false in config
2. ✅ KILL_SWITCH.active = false
3. ✅ Dhan API credentials valid
4. ✅ Capital allocation matches risk params
5. ✅ Broker margin confirmed for strategies

## Related Skills
- apex-paper-trade-engine
- apex-risk-veto-authority
