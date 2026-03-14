#!/usr/bin/env python3
"""
APEX Option Chain Cache
Caches option chain data to avoid repeated API calls
"""

import json
import os
import time
from datetime import datetime, timedelta

CACHE_FILE = os.path.expanduser("~/.apex/cache/option_chain_cache.json")
CACHE_MAX_AGE_MINUTES = 5  # Option chain changes faster than VIX

def get_cached_option_chain():
    """Get cached option chain if fresh"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
            
            cached_time = datetime.fromisoformat(cache.get('fetched_at', '2000-01-01'))
            age_seconds = time.time() - cached_time.timestamp()
            age_minutes = age_seconds / 60
            
            if age_minutes < CACHE_MAX_AGE_MINUTES:
                print(f"[OPTION_CHAIN_CACHE] Using cached data from {cache.get('fetched_at')}")
                return cache
            else:
                print(f"[OPTION_CHAIN_CACHE] Cache stale (age: {age_minutes:.1f} min)")
    except Exception as e:
        print(f"[OPTION_CHAIN_CACHE] Error reading cache: {e}")
    return None

def save_cache(option_data):
    """Save option chain to cache"""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump(option_data, f, indent=2)
        print(f"[OPTION_CHAIN_CACHE] Saved to cache")
    except Exception as e:
        print(f"[OPTION_CHAIN_CACHE] Error saving cache: {e}")

def get_fresh_option_chain():
    """Fetch fresh option chain from NSE"""
    import httpx
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    data = {}
    try:
        # Try NIFTY
        with httpx.Client(headers=headers, timeout=15) as client:
            client.get("https://www.nseindia.com")
            resp = client.get("https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY")
            if resp.status_code == 200:
                data['nifty'] = resp.json()
            
            # Try BANKNIFTY
            client.get("https://www.nseindia.com")  # Refresh cookies
            resp = client.get("https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY")
            if resp.status_code == 200:
                data['banknifty'] = resp.json()
    except Exception as e:
        print(f"[OPTION_CHAIN_API] Error fetching: {e}")
    
    if data:
        data['fetched_at'] = datetime.now().isoformat()
    
    return data

def get_option_chain(force_refresh=False):
    """Get option chain data with caching"""
    if force_refresh:
        print("[OPTION_CHAIN] Force refresh requested")
        data = get_fresh_option_chain()
        if data:
            save_cache(data)
        return data
    
    # Check cache first
    cached = get_cached_option_chain()
    if cached:
        return cached
    
    # Fetch fresh
    print("[OPTION_CHAIN] Fetching fresh data from NSE...")
    data = get_fresh_option_chain()
    
    if data:
        save_cache(data)
    else:
        # Try stale cache as fallback
        print("[OPTION_CHAIN] API failed, trying stale cache...")
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r') as f:
                    data = json.load(f)
                print(f"[OPTION_CHAIN] Using stale cache")
        except:
            pass
    
    return data

def parse_metrics(chain_data):
    """Parse option chain data into useful metrics"""
    metrics = {}
    
    for symbol, data in chain_data.items():
        if symbol == 'fetched_at':
            continue
            
        try:
            records = data.get('records', {})
            underlying = records.get('underlyingValue', 0)
            expiry_date = records.get('expiryDate', 'N/A')
            data_rows = records.get('data', [])
            
            total_ce_oi = 0
            total_pe_oi = 0
            
            for row in data_rows:
                ce = row.get('CE', {})
                pe = row.get('PE', {})
                total_ce_oi += ce.get('openInterest', 0)
                total_pe_oi += pe.get('openInterest', 0)
            
            pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 1.0
            
            metrics[symbol.upper()] = {
                'underlying': underlying,
                'expiry': expiry_date,
                'pcr': pcr,
                'total_ce_oi': total_ce_oi,
                'total_pe_oi': total_pe_oi,
            }
        except Exception as e:
            print(f"[PARSE] Error parsing {symbol}: {e}")
    
    return metrics

if __name__ == "__main__":
    import sys
    
    force = '--force' in sys.argv
    
    print("=" * 50)
    print("APEX Option Chain Fetcher with Caching")
    print("=" * 50)
    
    chain_data = get_option_chain(force_refresh=force)
    
    if chain_data:
        metrics = parse_metrics(chain_data)
        print("\n" + "=" * 50)
        print("PARSED METRICS:")
        print("=" * 50)
        for symbol, data in metrics.items():
            print(f"\n{symbol}:")
            print(f"  Underlying: {data['underlying']}")
            print(f"  Expiry: {data['expiry']}")
            print(f"  PCR: {data['pcr']}")
            print(f"  CE OI: {data['total_ce_oi']:,}")
            print(f"  PE OI: {data['total_pe_oi']:,}")
        
        # Save metrics to state
        state_path = os.path.expanduser("~/.apex/state.json")
        try:
            with open(state_path, 'r') as f:
                state = json.load(f)
        except:
            state = {}
        
        state['option_chain'] = metrics
        state['option_chain_fetched_at'] = datetime.now().isoformat()
        
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"\n[Saved to state]")
    else:
        print("\n[Failed to get option chain data]")