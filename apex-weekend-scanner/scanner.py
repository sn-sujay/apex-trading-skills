#!/usr/bin/env python3
"""
APEX Weekend Scanner
Runs Saturday/Sunday to prepare for Monday trading
Uses browser to fetch global macro data reliably
"""

import json
import os
import sys
from datetime import datetime
import pytz

# Add project to path
sys.path.insert(0, os.path.expanduser("~/.apex"))

TELEGRAM_TOKEN = "8704170382:AAFvHBjC2G_LFHUrQs5WR84LQGJ2G4GKFSc"
TELEGRAM_CHAT = "419180494"
STATE_FILE = os.path.expanduser("~/.apex/state.json")
IST = pytz.timezone("Asia/Kolkata")

def send_telegram(msg):
    """Send alert to Telegram"""
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def load_state():
    """Load current state"""
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    """Save state"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_day_type():
    """Determine which scan this is"""
    now = datetime.now(IST)
    weekday = now.weekday()  # 5=Saturday, 6=Sunday
    
    if weekday == 5:
        return "SATURDAY_WEEKLY"
    elif now.hour >= 18:
        return "SUNDAY_PRE_MONDAY"
    else:
        return "SUNDAY_WEEKLY"

def fetch_via_browser():
    """Use browser to get TradingView data"""
    from hermes_tools import browser_navigate, browser_snapshot, browser_close, browser_scroll
    
    data = {
        "us_markets": {},
        "asia": {},
        "commodities": {}
    }
    
    try:
        # Navigate to TradingView indices page
        browser_navigate(url="https://www.tradingview.com/markets/indices/")
        
        # Get snapshot
        snap = browser_snapshot(full=True)
        content = snap.get("snapshot", "")
        
        # Parse US indices from snapshot
        if "S&P 500" in content:
            # S&P 500
            import re
            sp_match = re.search(r'S&P 500.*?([0-9,]+\.[0-9]+).*?([+-]?\d+\.\d+)%', content)
            if sp_match:
                price = float(sp_match.group(1).replace(',', ''))
                change = float(sp_match.group(2))
                data["us_markets"]["sp500"] = {"price": price, "change_pct": change}
            
            # Nasdaq 100
            nas_match = re.search(r'Nasdaq 100.*?([0-9,]+\.[0-9]+).*?([+-]?\d+\.\d+)%', content)
            if nas_match:
                price = float(nas_match.group(1).replace(',', ''))
                change = float(nas_match.group(2))
                data["us_markets"]["nasdaq"] = {"price": price, "change_pct": change}
            
            # Dow 30
            dow_match = re.search(r'Dow 30.*?([0-9,]+\.[0-9]+).*?([+-]?\d+\.\d+)%', content)
            if dow_match:
                price = float(dow_match.group(1).replace(',', ''))
                change = float(dow_match.group(2))
                data["us_markets"]["dow"] = {"price": price, "change_pct": change}
    except Exception as e:
        print(f"Browser error: {e}")
    finally:
        try:
            browser_close()
        except:
            pass
    
    return data

def fetch_fallback_data():
    """Fallback if browser fails - use last known or estimates"""
    import requests
    
    data = {
        "us_markets": {},
        "asia": {},
        "commodities": {}
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    
    # Try one more API
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d&range=2d"
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            j = r.json()
            if j.get("chart", {}).get("result"):
                result = j["chart"]["result"][0]
                price = result["meta"].get("regularMarketPrice", 0)
                data["us_markets"]["sp500_fallback"] = {"price": price, "change_pct": 0}
    except:
        pass
    
    return data

def fetch_weekend_news():
    """Get key weekend news/headlines"""
    # Simplified - could enhance with more sources
    news = []
    
    # Check India news sources
    try:
        import requests
        url = "https://news.google.com/rss/search?q=India+stock+market"
        # This requires parsing XML - simplified for now
    except:
        pass
    
    return news

def analyze_outlook(macro_data, news):
    """Determine outlook based on data"""
    score = 0
    
    # US markets positive?
    us = macro_data.get("us_markets", {})
    sp = us.get("sp500", {})
    if sp.get("change_pct", 0) > 0.5:
        score += 1
    elif sp.get("change_pct", 0) < -0.5:
        score -= 1
    
    # Check other US indices
    for idx in ["nasdaq", "dow"]:
        if idx in us:
            change = us[idx].get("change_pct", 0)
            if change > 0.3:
                score += 0.5
            elif change < -0.3:
                score -= 0.5
    
    if score >= 1:
        return "BULLISH"
    elif score <= -1:
        return "BEARISH"
    else:
        return "NEUTRAL"

def generate_actionable_notes(macro_data, news, outlook):
    """Generate specific notes for Monday"""
    notes = []
    
    us = macro_data.get("us_markets", {})
    
    # US market direction
    sp = us.get("sp500", {}).get("change_pct", 0)
    if sp > 0.5:
        notes.append("US markets strong (+0.5%+) - Risk-on Monday")
    elif sp < -0.5:
        notes.append("US markets weak (-0.5%+) - Risk-off Monday")
    
    # NASDAQ
    nas = us.get("nasdaq", {}).get("change_pct", 0)
    if nas > sp + 0.2:
        notes.append("Tech leading - growth stocks may outperform")
    elif nas < sp - 0.2:
        notes.append("Tech lagging - defensives may lead")
    
    # Outlook-based
    if outlook == "BULLISH":
        notes.append("Overall: Positive - prefer long setups, buy OTM calls")
    elif outlook == "BEARISH":
        notes.append("Overall: Negative - prefer shorts, buy OTM puts, use iron condor")
    else:
        notes.append("Overall: Mixed - wait for Monday open, use strangles")
    
    return notes

def run_weekend_scan():
    """Main scanner function"""
    print("=" * 50)
    print("APEX WEEKEND SCANNER")
    print("=" * 50)
    
    now = datetime.now(IST)
    day_type = get_day_type()
    
    print(f"Running: {day_type}")
    print(f"Time: {now.strftime('%Y-%m-%d %H:%M IST')}")
    
    # Load state
    state = load_state()
    
    # Try browser first, fallback to API
    print("\n[1/4] Fetching global macro data...")
    macro_data = fetch_via_browser()
    
    if not macro_data.get("us_markets", {}):
        print("  Browser failed, trying fallback...")
        macro_data = fetch_fallback_data()
    
    print(f"  US Markets: {macro_data.get('us_markets', {})}")
    
    print("\n[2/4] Checking for weekend news...")
    news = fetch_weekend_news()
    print(f"  Found {len(news)} news items")
    
    print("\n[3/4] Analyzing outlook...")
    outlook = analyze_outlook(macro_data, news)
    notes = generate_actionable_notes(macro_data, news, outlook)
    print(f"  Outlook: {outlook}")
    
    # Update state
    print("\n[4/4] Updating state...")
    weekend_data = {
        "last_scan": now.isoformat(),
        "scan_type": day_type,
        "global_macro": macro_data,
        "news_summary": news,
        "next_week_outlook": outlook,
        "actionable_notes": notes,
        "data_fresh": True
    }
    
    if "weekend_scan" not in state:
        state["weekend_scan"] = {}
    state["weekend_scan"].update(weekend_data)
    save_state(state)
    
    # Build report
    report = f"""╔════════════════════════════════════════╗
║     📡 WEEKEND SCANNER REPORT          
║     {now.strftime('%Y-%m-%d %H:%M')} IST
╚════════════════════════════════════════╝

📅 Scan Type: {day_type}

🌍 GLOBAL MARKETS:
"""
    
    us = macro_data.get("us_markets", {})
    if "sp500" in us:
        sp = us["sp500"]
        report += f"  📈 S&P 500: {sp.get('price', 0):,.2f} ({sp.get('change_pct', 0):+.2f}%)\n"
    if "nasdaq" in us:
        nas = us["nasdaq"]
        report += f"  📈 Nasdaq 100: {nas.get('price', 0):,.2f} ({nas.get('change_pct', 0):+.2f}%)\n"
    if "dow" in us:
        dow = us["dow"]
        report += f"  📈 Dow 30: {dow.get('price', 0):,.2f} ({dow.get('change_pct', 0):+.2f}%)\n"
    
    if not us:
        report += "  ⚠️ Data unavailable - check Monday open\n"
    
    report += f"""
🎯 OUTLOOK: {outlook}
"""
    
    report += "📝 STRATEGY NOTES FOR MONDAY:\n"
    for note in notes:
        report += f"  • {note}\n"
    
    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ State updated for Monday pre-market
   Check: state.json → weekend_scan
   Key: weekend_scan.next_week_outlook"""
    
    print("\n" + report)
    
    # Send to Telegram
    send_telegram(report)
    
    print("\n✅ Weekend scan complete!")
    return True

if __name__ == "__main__":
    run_weekend_scan()