#!/usr/bin/env python3
"""
APEX Scrip Master Cache
Downloads and caches scrip master from Dhan
Static data - only refresh if file missing or stale (>7 days)
"""

import json
import os
from datetime import datetime, timedelta

CACHE_FILE = os.path.expanduser("~/.apex/cache/scrip_master.csv")
CACHE_MAX_AGE_DAYS = 7

def get_scrip_master():
    """Get scrip master - from cache or download fresh"""
    
    # Check if cache exists and is fresh
    if os.path.exists(CACHE_FILE):
        file_age = os.path.getmtime(CACHE_FILE)
        age_days = (datetime.now().timestamp() - file_age) / (24*3600)
        
        if age_days < CACHE_MAX_AGE_DAYS:
            print(f"[SCRIP_MASTER] Using cached file (age: {age_days:.1f} days)")
            return CACHE_FILE
        else:
            print(f"[SCRIP_MASTER] Cache stale (age: {age_days:.1f} days), refreshing...")
    else:
        print("[SCRIP_MASTER] No cache, downloading...")
    
    # Download fresh
    import httpx
    url = "https://images.dhan.co/api-data/api-scrip-master.csv"
    
    try:
        resp = httpx.get(url, timeout=60)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            with open(CACHE_FILE, 'wb') as f:
                f.write(resp.content)
            print(f"[SCRIP_MASTER] Downloaded and cached ({len(resp.content):,} bytes)")
            return CACHE_FILE
        else:
            print(f"[SCRIP_MASTER] Download failed: {resp.status_code}")
    except Exception as e:
        print(f"[SCRIP_MASTER] Error: {e}")
    
    # Return existing cache if download failed
    if os.path.exists(CACHE_FILE):
        print("[SCRIP_MASTER] Using existing cache (download failed)")
        return CACHE_FILE
    
    return None

def search_scrip(query):
    """Search scrip master for a symbol"""
    import csv
    
    cache_file = get_scrip_master()
    if not cache_file:
        return None
    
    results = []
    query_lower = query.lower()
    
    try:
        with open(cache_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol = row.get('SEM_TRADING_SYMBOL', '').lower()
                name = row.get('SM_SYMBOL_NAME', '').lower()
                
                if query_lower in symbol or query_lower in name:
                    results.append({
                        'exchange': row.get('SEM_EXM_EXCH_ID', ''),
                        'segment': row.get('SEM_SEGMENT', ''),
                        'security_id': row.get('SEM_SMST_SECURITY_ID', ''),
                        'instrument': row.get('SEM_INSTRUMENT_NAME', ''),
                        'symbol': row.get('SEM_TRADING_SYMBOL', ''),
                        'name': row.get('SM_SYMBOL_NAME', ''),
                    })
                    
                    if len(results) >= 10:
                        break
    except Exception as e:
        print(f"[SCRIP_MASTER] Search error: {e}")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        print(f"Searching for: {query}")
        results = search_scrip(query)
        
        if results:
            print(f"\nFound {len(results)} results:\n")
            for r in results:
                print(f"{r['exchange']} | {r['segment']} | {r['security_id']} | {r['instrument']:10} | {r['symbol']} | {r['name']}")
        else:
            print("No results found")
    else:
        get_scrip_master()
        print("\nUsage: python fetch_scrip_master.py <search_term>")