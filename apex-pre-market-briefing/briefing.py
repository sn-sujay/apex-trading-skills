#!/usr/bin/env python3
"""
APEX Pre-Market Briefing
Runs at 8 AM IST to scan fresh news and generate daily strategy
"""

import json
import os
import re
import requests
from datetime import datetime
import pytz

TELEGRAM_TOKEN = "8704170382:AAFvHBjC2G_LFHUrQs5WR84LQGJ2G4GKFSc"
TELEGRAM_CHAT = "419180494"
STATE_FILE = os.path.expanduser("~/.apex/state.json")
IST = pytz.timezone("Asia/Kolkata")

def send_telegram(msg):
    """Send alert to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT, "text": msg}
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def fetch_india_news():
    """Fetch latest Indian market news"""
    news = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    # Try MoneyControl
    try:
        url = "https://www.moneycontrol.com/rss/latestnews.xml"
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            # Parse XML for headlines
            import xml.etree.ElementTree as ET
            root = ET.fromstring(r.text)
            for item in root.findall('.//item')[:10]:
                title = item.find('title')
                if title is not None and title.text:
                    news.append(title.text[:150])
    except Exception as e:
        print(f"News fetch error: {e}")
    
    return news

def fetch_banking_news():
    """Fetch banking sector specific news"""
    banking_news = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    # Search for banking news
    queries = [
        "India banking sector news today",
        "RBI policy update today",
        "Indian stock market today",
        "Nifty Bank Nifty today"
    ]
    
    for query in queries[:2]:
        try:
            url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(r.text.encode('utf-8'))
                for item in root.findall('.//item')[:5]:
                    title = item.find('title')
                    if title is not None and title.text:
                        # Filter for relevant content
                        txt = title.text.lower()
                        if any(w in txt for w in ['bank', 'rbi', 'nifty', 'sensex', 'market', 'stock']):
                            banking_news.append(title.text[:150])
        except Exception as e:
            print(f"Banking news error: {e}")
    
    return banking_news[:10]

def fetch_overnight_global():
    """Get overnight global market movements"""
    import re
    
    data = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    # Use browser to get TradingView data
    try:
        from hermes_tools import browser_navigate, browser_snapshot, browser_close
        
        browser_navigate(url="https://www.tradingview.com/markets/indices/")
        snap = browser_snapshot(full=True)
        content = snap.get("snapshot", "")
        
        # Parse indices
        patterns = [
            (r'S&P 500.*?([0-9,]+\.[0-9]+).*?([+-]?\d+\.\d+)%', 'sp500'),
            (r'Nasdaq 100.*?([0-9,]+\.[0-9]+).*?([+-]?\d+\.\d+)%', 'nasdaq'),
            (r'Dow 30.*?([0-9,]+\.[0-9]+).*?([+-]?\d+\.\d+)%', 'dow'),
        ]
        
        for pattern, key in patterns:
            match = re.search(pattern, content)
            if match:
                price = float(match.group(1).replace(',', ''))
                change = float(match.group(2))
                data[key] = {"price": price, "change_pct": change}
        
        browser_close()
    except Exception as e:
        print(f"Browser error: {e}")
        # Fallback to last known
        pass
    
    return data

def analyze_strategy(weekend_outlook, fresh_news, banking_news, global_data):
    """Generate today's strategy based on all data"""
    score = 0
    factors = []
    
    # Start with weekend outlook
    if weekend_outlook == "BEARISH":
        score -= 2
    elif weekend_outlook == "BULLISH":
        score += 2
    
    # Check global overnight
    sp = global_data.get("sp500", {}).get("change_pct", 0)
    if sp > 0.5:
        score += 1
        factors.append("US markets up")
    elif sp < -0.5:
        score -= 1
        factors.append("US markets down")
    
    # Analyze news sentiment
    bearish_words = ['fall', 'drop', 'crash', 'loss', 'weak', 'decline', 'sell', 'bearish']
    bullish_words = ['rise', 'gain', 'surge', 'grow', 'bullish', 'profit', 'rally', 'high']
    
    all_news = " ".join(fresh_news + banking_news).lower()
    
    for word in bullish_words:
        if word in all_news:
            score += 0.5
    for word in bearish_words:
        if word in all_news:
            score -= 0.5
    
    # Banking sector specific
    banking_text = " ".join(banking_news).lower()
    if any(w in banking_text for w in ['rbi', 'rate', 'hike', 'policy']):
        factors.append("RBI/policy news - watch rates")
    if any(w in banking_text for w in ['bank', 'nbfc', 'credit']):
        factors.append("Banking sector active")
    
    # Determine stance
    if score >= 2:
        stance = "BULLISH"
        risk = "LOW"
        strategy = "Long setups, Bull Call Spreads, buy OTM calls"
    elif score <= -2:
        stance = "BEARISH"
        risk = "MEDIUM"
        strategy = "Short setups, Bear Put Spreads, Iron Condor"
    else:
        stance = "NEUTRAL"
        risk = "MEDIUM"
        strategy = "Wait for clarity, use Strangles/Straddles"
    
    return stance, risk, strategy, factors

def run_premarket_briefing():
    """Main pre-market briefing"""
    print("=" * 60)
    print("APEX PRE-MARKET BRIEFING")
    print("=" * 60)
    
    now = datetime.now(IST)
    print(f"Time: {now.strftime('%Y-%m-%d %H:%M IST')}")
    
    # Load state
    state = load_state()
    
    # 1. Get weekend context
    weekend_data = state.get("weekend_scan", {})
    weekend_outlook = weekend_data.get("next_week_outlook", "NEUTRAL")
    weekend_notes = weekend_data.get("actionable_notes", [])
    weekend_macro = weekend_data.get("global_macro", {})
    
    print(f"\n[1/4] Weekend context: {weekend_outlook}")
    
    # 2. Fetch fresh news
    print("[2/4] Fetching fresh news...")
    fresh_news = fetch_india_news()
    print(f"  Found {len(fresh_news)} news items")
    
    # 3. Fetch banking news
    print("[3/4] Fetching banking news...")
    banking_news = fetch_banking_news()
    print(f"  Found {len(banking_news)} banking items")
    
    # 4. Get overnight global
    print("[4/4] Fetching overnight global data...")
    global_data = fetch_overnight_global()
    print(f"  Global data: {global_data}")
    
    # Analyze and generate strategy
    stance, risk, strategy, factors = analyze_strategy(
        weekend_outlook, fresh_news, banking_news, global_data
    )
    
    # Update state
    briefing = {
        "generated_at": now.isoformat(),
        "weekend_outlook": weekend_outlook,
        "global_overnight": global_data,
        "fresh_news": fresh_news[:10],
        "banking_news": banking_news[:10],
        "today_stance": stance,
        "risk_level": risk,
        "recommended_strategy": strategy,
        "factors": factors
    }
    
    state["pre_market_briefing"] = briefing
    save_state(state)
    
    # Build report
    report = f"""PRE-MARKET BRIEFING - {now.strftime('%d %b %Y')}

=== WEEKEND CONTEXT ===
Outlook: {weekend_outlook}"""
    
    if weekend_notes:
        report += f"\nWeekend Notes:"
        for n in weekend_notes[:3]:
            report += f"\n- {n}"
    
    report += f"""

=== OVERNIGHT GLOBAL ===
"""
    if global_data.get("sp500"):
        report += f"S&P 500: {global_data['sp500']['price']:,.0f} ({global_data['sp500']['change_pct']:+.2f}%)\n"
    if global_data.get("nasdaq"):
        report += f"Nasdaq: {global_data['nasdaq']['price']:,.0f} ({global_data['nasdaq']['change_pct']:+.2f}%)\n"
    
    report += f"""

=== FRESH NEWS ({len(fresh_news)} items) ===
"""
    for n in fresh_news[:5]:
        report += "• " + n[:120] + "\n"
    
    report += """

=== BANKING SECTOR ===
"""
    if banking_news:
        for n in banking_news[:5]:
            report += "• " + n[:120] + "\n"
    else:
        report += "No major banking news found\n"
    
    report += f"""

=== TODAY'S STRATEGY ===
Stance: {stance}
Risk: {risk}
Strategy: {strategy}
"""
    
    if factors:
        report += "Factors:\n"
        for f in factors:
            report += f"- {f}\n"
    
    report += f"""
===
State updated: pre_market_briefing.today_stance = {stance}"""
    
    print("\n" + report)
    
    # Send to Telegram
    send_telegram(report)
    
    print("\n✅ Pre-market briefing complete!")
    return True

if __name__ == "__main__":
    run_premarket_briefing()