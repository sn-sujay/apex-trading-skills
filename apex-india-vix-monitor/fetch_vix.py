#!/usr/bin/env python3
"""
India VIX Monitor with Caching
Fetches India VIX from NSE India official API
Caches locally to avoid unnecessary API calls
"""

import requests
import json
import os
from datetime import datetime, timedelta

# Cache settings
CACHE_FILE = os.path.expanduser("~/.apex/cache/vix_cache.json")
CACHE_MAX_AGE_MINUTES = 15

def get_cached_vix():
    """Get cached VIX data if fresh"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
            
            cached_time = datetime.fromisoformat(cache.get('fetched_at', '2000-01-01'))
            age = datetime.now() - cached_time
            
            age_seconds = age.total_seconds()
            age_minutes = age_seconds / 60
            
            if age_minutes < CACHE_MAX_AGE_MINUTES:
                print(f"[CACHE] Using cached VIX from {cache.get('fetched_at')}")
                return cache
            else:
                print(f"[CACHE] Cache stale (age: {age_minutes:.1f} min)")
    except Exception as e:
        print(f"[CACHE] Error reading cache: {e}")
    return None

def save_cache(vix_data):
    """Save VIX data to cache"""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump(vix_data, f, indent=2)
    except Exception as e:
        print(f"[CACHE] Error saving cache: {e}")

def fetch_india_vix():
    """
    Fetch India VIX from NSE India official API
    Uses session cookies for proper access
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        session = requests.Session()
        
        # First, visit main page to get cookies
        session.get("https://www.nseindia.com", headers=headers, timeout=15)
        
        # Fetch all indices (includes India VIX)
        url = "https://www.nseindia.com/api/allIndices"
        resp = session.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            
            for idx in data.get('data', []):
                if idx.get('index') == 'INDIA VIX':
                    return {
                        'symbol': 'INDIA VIX',
                        'security_id': '21',
                        'exchange': 'NSE',
                        'segment': 'IDX',
                        'current': float(idx.get('last', 0)),
                        'open': float(idx.get('open', 0)),
                        'high': float(idx.get('high', 0)),
                        'low': float(idx.get('low', 0)),
                        'prev_close': float(idx.get('previousClose', 0)),
                        'change': float(idx.get('variation', 0)),
                        'change_percent': float(idx.get('percentChange', 0)),
                        'year_high': float(idx.get('yearHigh', 0)),
                        'year_low': float(idx.get('yearLow', 0)),
                        'timestamp': idx.get('previousDay'),
                        'fetched_at': datetime.now().isoformat(),
                        'regime': classify_regime(float(idx.get('last', 0)))
                    }
        
        return None
    except Exception as e:
        print(f"Error fetching India VIX: {e}")
        return None

def classify_regime(vix_value):
    """Classify market regime based on India VIX level"""
    if vix_value > 20:
        return 'HIGH_VOLATILITY'
    elif vix_value > 15:
        return 'ELEVATED_VOLATILITY'
    elif vix_value < 12:
        return 'LOW_VOLATILITY'
    else:
        return 'NORMAL'

def update_state_with_vix():
    """Fetch and update state with India VIX (with caching)"""
    # Check cache first
    cached = get_cached_vix()
    if cached:
        vix_data = cached
    else:
        # Fetch from API
        print("[API] Fetching fresh India VIX from NSE...")
        vix_data = fetch_india_vix()
        
        if vix_data:
            # Save to cache
            save_cache(vix_data)
        else:
            # API failed, try to use stale cache as fallback
            print("[FALLBACK] API failed, checking for stale cache...")
            try:
                if os.path.exists(CACHE_FILE):
                    with open(CACHE_FILE, 'r') as f:
                        vix_data = json.load(f)
                    print(f"[FALLBACK] Using stale cache: {vix_data.get('current')}")
            except:
                pass
    
    if not vix_data:
        print("Failed to get India VIX (no cache, API failed)")
        return None
    
    # Load state
    state_path = os.path.expanduser("~/.apex/state.json")
    try:
        with open(state_path, 'r') as f:
            state = json.load(f)
    except:
        state = {}
    
    # Update state
    state['india_vix'] = vix_data
    state['market_regime'] = vix_data['regime']
    
    # Save state
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"India VIX: {vix_data['current']} ({vix_data['regime']}) [cached: {cached is not None}]")
    return vix_data

if __name__ == "__main__":
    vix = update_state_with_vix()
    if vix:
        print(json.dumps(vix, indent=2))