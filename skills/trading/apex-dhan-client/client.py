"""
Dhan API Client for APEX Trading System
"""
import requests
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import base64

class DhanClient:
    """Dhan API client for NSE trading"""
    
    BASE_URL = "https://api.dhan.co/v2"
    TOKEN_URL = "https://api.dhan.co/v2 accesstoken"
    
    def __init__(self, client_id: str = None, access_token: str = None, 
                 api_key: str = None, api_secret: str = None):
        """Initialize with credentials from config or parameters"""
        config_path = Path.home() / ".apex" / "config.yaml"
        
        # Also check state.json
        state_path = Path.home() / ".apex" / "state.json"
        state_config = {}
        if state_path.exists():
            with open(state_path) as f:
                state_config = json.load(f)
        
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                self.client_id = client_id or config.get('dhan', {}).get('client_id')
                self.access_token = access_token or config.get('dhan', {}).get('access_token')
                self.api_key = api_key or state_config.get('dhan_config', {}).get('api_key') or config.get('dhan', {}).get('api_key')
                self.api_secret = api_secret or state_config.get('dhan_config', {}).get('api_secret') or config.get('dhan', {}).get('api_secret')
        else:
            self.client_id = client_id
            self.access_token = access_token
            self.api_key = api_key
            self.api_secret = api_secret
        
        self.headers = {
            "access-token": self.access_token,
            "Content-Type": "application/json"
        }
        
        self._token_expiry = None
    
    def refresh_token(self) -> bool:
        """Refresh access token using API key and secret"""
        if not self.api_key or not self.api_secret:
            print("[DHAN] No API key/secret to refresh token")
            return False
        
        try:
            # Create basic auth header
            auth = base64.b64encode(f"{self.api_key}:{self.api_secret}".encode()).decode()
            
            url = f"{self.BASE_URL}/token"
            headers = {
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json"
            }
            payload = {"grant_type": "refresh_token"}
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.headers["access-token"] = self.access_token
                print("[DHAN] Token refreshed successfully")
                return True
            else:
                print(f"[DHAN] Token refresh failed: {response.text}")
                return False
        except Exception as e:
            print(f"[DHAN] Token refresh error: {e}")
            return False
    
    def get_holdings(self) -> Dict:
        """Get current holdings"""
        url = f"{self.BASE_URL}/holdings"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def get_positions(self) -> Dict:
        """Get current positions"""
        url = f"{self.BASE_URL}/positions"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            # Handle both list and dict responses
            if isinstance(data, list):
                return {"data": data}
            return data
        return {"error": response.text}
    
    def get_funds(self) -> Dict:
        """Get fund limits"""
        url = f"{self.BASE_URL}/fundlimit"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def get_daily_prices(self, security_id: str, exchange: str = "NSE", 
                         from_date: str = None, to_date: str = None) -> Dict:
        """Get daily OHLC prices"""
        if not from_date:
            from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        
        # Determine instrument type - indices use INDEX, not OPTIDX
        # NIFTY=13, BANKNIFTY=25, FINNIFTY=51, MIDCPNIFTY=74 are indices
        index_ids = ["13", "25", "51", "74"]
        
        if security_id in index_ids:
            instrument = "INDEX"
            exchange_segment = "NSE_EQ"
        else:
            instrument = "EQUITY"
            exchange_segment = "NSE_EQ"
        
        url = f"{self.BASE_URL}/charts/historical"
        payload = {
            "securityId": security_id,
            "exchangeSegment": exchange_segment,
            "instrument": instrument,
            "fromDate": from_date,
            "toDate": to_date
        }
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def get_option_chain(self, underlying: str, expiry: str = None) -> Dict:
        """Get option chain for underlying (NIFTY, BANKNIFTY, etc.)"""
        # Map indices to Dhan security IDs
        index_map = {
            "NIFTY": "13",
            "BANKNIFTY": "25",
            "FINNIFTY": "51",
            "MIDCPNIFTY": "74"
        }
        
        security_id = index_map.get(underlying.upper())
        if not security_id:
            return {"error": f"Unknown underlying: {underlying}"}
        
        # Get option chain from Dhan
        url = f"{self.BASE_URL}/option-chain"
        params = {
            "securityId": security_id,
            "exchangeSegment": "NSE_FNO"
        }
        if expiry:
            params["expiry"] = expiry
        
        response = requests.get(url, headers=self.headers, params=params)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def place_order(self, order_params: Dict) -> Dict:
        """Place an order"""
        url = f"{self.BASE_URL}/orders"
        response = requests.post(url, headers=self.headers, json=order_params)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        url = f"{self.BASE_URL}/orders/{order_id}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def get_order_list(self) -> Dict:
        """Get all orders"""
        url = f"{self.BASE_URL}/orders"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            # Handle both list and dict responses
            if isinstance(data, list):
                return {"data": data}
            return data
        return {"error": response.text}
    
    def get_trade_history(self, from_date: str = None, to_date: str = None) -> Dict:
        """Get trade history"""
        url = f"{self.BASE_URL}/trades"
        params = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        
        response = requests.get(url, headers=self.headers, params=params)
        return response.json() if response.status_code == 200 else {"error": response.text}




    # ============================================================
    # ENHANCED ORDER TYPES (Bracket, Super, Smart Routing)
    # ============================================================
    
    def place_bracket_order(self, params: dict) -> dict:
        """
        Place a Bracket Order with entry, SL, and target.
        
        Params:
        - transaction_type: BUY/SELL
        - instrument_token: Security ID
        - quantity: Number of units
        - price: Entry price (0 for market)
        - trigger_price: Stop-loss trigger
        - target_price: Profit target
        - trailing_stop_loss: Trailing SL value
        - product_type: MIS (intraday)
        """
        url = f"{self.BASE_URL}/orders/bracket"
        
        order_payload = {
            "transactionType": params.get('transaction_type'),
            "instrumentToken": params.get('instrument_token'),
            "quantity": params.get('quantity'),
            "price": params.get('price', 0),
            "triggerPrice": params.get('trigger_price'),
            "targetPrice": params.get('target_price'),
            "trailingStopLoss": params.get('trailing_stop_loss', 0),
            "productType": params.get('product_type', 'MIS'),
            "orderType": params.get('order_type', 'LIMIT'),
            "exchangeSegment": params.get('exchange_segment', 'NSE_FNO')
        }
        
        response = requests.post(url, headers=self.headers, json=order_payload)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def place_super_order(self, params: dict) -> dict:
        """
        Place a Super Order with advanced features.
        
        Similar to bracket order but with more options.
        """
        url = f"{self.BASE_URL}/orders/super"
        
        order_payload = {
            "transactionType": params.get('transaction_type'),
            "instrumentToken": params.get('instrument_token'),
            "quantity": params.get('quantity'),
            "price": params.get('price', 0),
            "triggerPrice": params.get('trigger_price'),
            "targetPrice": params.get('target_price'),
            "stopLossPrice": params.get('stop_loss_price'),
            "productType": params.get('product_type', 'MIS'),
            "orderType": params.get('order_type', 'MARKET'),
            "exchangeSegment": params.get('exchange_segment', 'NSE_FNO')
        }
        
        response = requests.post(url, headers=self.headers, json=order_payload)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def get_quote(self, instrument_token: str, exchange: str = "NSE") -> dict:
        """Get live bid-ask quote for smart routing"""
        url = f"{self.BASE_URL}/quotes"
        params = {
            "instrumentToken": instrument_token,
            "exchangeSegment": "NSE_FNO" if exchange == "NSE_FNO" else "NSE_EQ"
        }
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        return {"error": response.text, "bid": 0, "ask": 0}
    
    def place_smart_limit_order(self, side: str, instrument_token: str, 
                                quantity: int, max_wait: int = 30) -> dict:
        """
        Smart limit order routing within bid-ask spread.
        
        Strategy:
        1. Place at bid+0.5tick (sell) or ask-0.5tick (buy)
        2. Wait max_wait seconds
        3. If unfilled, move to bid/ask
        4. If still unfilled, convert to market
        """
        import time
        
        # Get current quote
        quote = self.get_quote(instrument_token)
        if "error" in quote:
            return quote
        
        bid = float(quote.get('bid', 0))
        ask = float(quote.get('ask', 0))
        tick_size = 0.05  # NFO tick size
        
        # Calculate smart limit price
        if side.upper() == 'BUY':
            limit_price = ask - (0.5 * tick_size)
            fallback_price = ask
        else:  # SELL
            limit_price = bid + (0.5 * tick_size)
            fallback_price = bid
        
        # Place limit order
        order_params = {
            'transaction_type': side.upper(),
            'instrument_token': instrument_token,
            'quantity': quantity,
            'price': round(limit_price, 2),
            'order_type': 'LIMIT',
            'product_type': 'MIS'
        }
        
        order = self.place_order(order_params)
        order_id = order.get('orderId') or order.get('order_id')
        
        if not order_id:
            return order
        
        # Wait and check fill
        time.sleep(max_wait)
        status = self.get_order_status(order_id)
        
        if status.get('status') == 'PENDING':
            # Modify to fallback price
            self.modify_order(order_id, {'price': round(fallback_price, 2)})
            
            # Wait another 30s
            time.sleep(30)
            status = self.get_order_status(order_id)
            
            if status.get('status') == 'PENDING':
                # Convert to market
                self.modify_order(order_id, {
                    'price': 0,
                    'order_type': 'MARKET'
                })
        
        return order
    
    def modify_order(self, order_id: str, modifications: dict) -> dict:
        """Modify an existing order"""
        url = f"{self.BASE_URL}/orders/{order_id}"
        response = requests.put(url, headers=self.headers, json=modifications)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    def cancel_order(self, order_id: str) -> dict:
        """Cancel an order"""
        url = f"{self.BASE_URL}/orders/{order_id}"
        response = requests.delete(url, headers=self.headers)
        return response.json() if response.status_code == 200 else {"error": response.text}
    
    # ============================================================
    # SEBI CHARGES CALCULATION
    # ============================================================
    
    def calculate_sebi_charges(self, turnover: float, side: str = 'BOTH') -> dict:
        """
        Calculate SEBI-compliant charges for a trade.
        
        Args:
            turnover: Trade turnover in INR
            side: 'BUY', 'SELL', or 'BOTH'
        
        Returns:
            dict with all charge components
        """
        # Brokerage (0.03% per side, max ₹20 per order)
        brokerage_per_side = min(turnover * 0.0003, 20)
        brokerage = brokerage_per_side * (2 if side == 'BOTH' else 1)
        
        # Exchange Transaction Charge (0.0009%)
        exchange_txn = turnover * 0.000009
        
        # SEBI Charges (₹10 per crore)
        sebi_charges = turnover * (10 / 10000000)
        
        # Stamp Duty (0.0001% on buy only)
        stamp_duty = turnover * 0.000001 if side in ['BUY', 'BOTH'] else 0
        
        # STT (0.0001% on sell only)
        stt = turnover * 0.000001 if side in ['SELL', 'BOTH'] else 0
        
        # GST (18% on brokerage + exchange charges)
        gst_base = brokerage + exchange_txn
        gst = gst_base * 0.18
        
        total = brokerage + exchange_txn + sebi_charges + stamp_duty + stt + gst
        
        return {
            'turnover': turnover,
            'brokerage': round(brokerage, 2),
            'exchange_transaction': round(exchange_txn, 2),
            'sebi_charges': round(sebi_charges, 2),
            'stamp_duty': round(stamp_duty, 2),
            'stt': round(stt, 2),
            'gst': round(gst, 2),
            'total_charges': round(total, 2),
            'net_pnl_impact': round(-total, 2)
        }
    
    # ============================================================
    # FOREX / CDS TRADING
    # ============================================================
    
    def place_forex_order(self, pair: str, side: str, lots: int, 
                          order_type: str = 'MARKET', price: float = 0) -> dict:
        """
        Place order for NSE CDS currency futures.
        
        Pairs: USDINR, EURINR, GBPINR, JPYINR
        Lot size: 1000 units
        """
        forex_tokens = {
            'USDINR': '1',
            'EURINR': '2', 
            'GBPINR': '3',
            'JPYINR': '4'
        }
        
        token = forex_tokens.get(pair.upper())
        if not token:
            return {"error": f"Unknown forex pair: {pair}"}
        
        url = f"{self.BASE_URL}/orders"
        payload = {
            "transactionType": side.upper(),
            "instrumentToken": token,
            "quantity": lots * 1000,  # 1000 units per lot
            "price": price,
            "orderType": order_type,
            "productType": "MIS",
            "exchangeSegment": "NSE_CDS"
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json() if response.status_code == 200 else {"error": response.text}

if __name__ == "__main__":
    # Test the client
    client = DhanClient()
    print("Testing Dhan Client...")
    
    # Test funds
    funds = client.get_funds()
    print(f"Funds: {funds}")
    
    # Test positions
    positions = client.get_positions()
    print(f"Positions: {positions}")
