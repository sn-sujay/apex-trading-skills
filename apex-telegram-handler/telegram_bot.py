#!/usr/bin/env python3
"""
APEX Telegram Bot - Polished Messages & Two-Way Communication
Handles sending formatted alerts and processing incoming commands
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Config paths
CONFIG_PATH = os.path.expanduser("~/.apex/config.yaml")
STATE_PATH = os.path.expanduser("~/.apex/state.json")

# Load config
def load_config():
    import yaml
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def load_state():
    with open(STATE_PATH, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)

def send_telegram_message(text, parse_mode="Markdown"):
    """Send message to Telegram"""
    config = load_config()
    bot_token = config.get('telegram', {}).get('bot_token', '')
    chat_id = config.get('telegram', {}).get('chat_id', '')
    
    if not bot_token or not chat_id:
        print("Telegram not configured")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

# ============================================================
# POLISHED MESSAGE FORMATTERS
# ============================================================

def format_pre_market(vix, regime, sentiment, news_summary):
    """Pre-market briefing - polished format"""
    emoji_vix = "🔴" if vix.get('current', 0) > 20 else "🟡" if vix.get('current', 0) > 15 else "🟢"
    
    text = f"""╔════════════════════════════════════════╗
║     📊 APEX PRE-MARKET BRIEFING          ║
║     {datetime.now().strftime('%d %b %Y')}                       ║
╚════════════════════════════════════════╝

{emoji_vix} INDIA VIX: {vix.get('current', 'N/A')} ({vix.get('change', 0):+.2f}%)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   
🎯 Regime: *{regime.get('current', 'UNKNOWN')}*
💭 Sentiment: *{sentiment.get('label', 'NEUTRAL')}* ({sentiment.get('confidence', 0)}%)

📰 Market Summary:
{news_summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ *Action Ready* - Monitoring Markets"""
    
    return text

def format_signal(strategy, symbol, legs, entry, sl, target, confidence, reasoning):
    """Trading signal - polished format"""
    
    legs_str = ""
    for leg in legs:
        emoji = "📈" if leg.get('type') == 'CE' else "📉"
        legs_str += f"   {emoji} {leg.get('action')} {leg.get('strike')} {leg.get('type')} @ ₹{leg.get('premium')}\n"
    
    text = f"""╔════════════════════════════════════════╗
║       🎯 APEX SIGNAL GENERATED           ║
║       {datetime.now().strftime('%H:%M')} IST                       ║
╚════════════════════════════════════════╝

🏷️ Strategy: *{strategy}*
📊 Symbol: {symbol}

📋 Position:
{legs_str}
💰 Entry: ₹{entry}
🛡️ Stop Loss: ₹{sl}
🎯 Target: ₹{target}

📈 Confidence: *{confidence}%*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Reasoning:
{reasoning[:200]}..."""

    return text

def format_trade_executed(strategy, symbol, entry_premium, legs):
    """Trade executed - polished format"""
    
    legs_str = ""
    for leg in legs:
        legs_str += f"   • {leg.get('action')} {leg.get('strike')} {leg.get('type')}\n"
    
    text = f"""╔════════════════════════════════════════╗
║     ✅ TRADE EXECUTED (PAPER)            ║
║       {datetime.now().strftime('%H:%M')} IST                       ║
╚════════════════════════════════════════╝

🏷️ *{strategy}* | {symbol}

{legs_str}
💵 Total Premium: ₹{entry_premium}

⏰ Entry Time: {datetime.now().strftime('%H:%M:%S')}
📊 Status: *MONITORING*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Paper Trade - No real money involved"""
    
    return text

def format_position_update(position, current_pnl, pnl_pct):
    """Position update - polished format"""
    
    emoji = "🟢" if current_pnl >= 0 else "🔴"
    emoji_pct = "📈" if pnl_pct >= 0 else "📉"
    
    text = f"""╔════════════════════════════════════════╗
║       📊 POSITION UPDATE                ║
║       {datetime.now().strftime('%H:%M')} IST                       ║
╚════════════════════════════════════════╝

{position.get('symbol')} | {position.get('strategy')}

{emoji} MTM P&L: *₹{current_pnl:+,}* ({pnl_pct:+.1f}%)

⏱️ Entry: {position.get('entry_time', 'N/A')}
🎯 Target: ₹{position.get('target', 'N/A')}
🛡️ Stop: ₹{position.get('stop_loss', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{emoji_pct} Status: *{'PROFITABLE' if current_pnl >= 0 else 'UNDERWATER'}*"""

    return text

def format_trade_exit(position, pnl, pnl_pct):
    """Trade exit - polished format"""
    
    emoji = "🟢" if pnl >= 0 else "🔴"
    
    text = f"""╔════════════════════════════════════════╗
║       ✅ TRADE EXITED                   ║
║       {datetime.now().strftime('%H:%M')} IST                       ║
╚════════════════════════════════════════╝

{position.get('symbol')} | {position.get('strategy')}

{emoji} P&L: *₹{pnl:+,}* ({pnl_pct:+.1f}%)

📊 Exit Reason: {position.get('exit_reason', 'Target/Stop')}
⏱️ Duration: {position.get('duration', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Session Total: Calculate from state"""

    return text

def format_eod(summary):
    """EOD Report - polished format"""
    
    text = f"""╔════════════════════════════════════════╗
║        📊 APEX EOD REPORT               ║
║       {datetime.now().strftime('%d %b %Y')}                       ║
╚════════════════════════════════════════╝

📈 Performance:
   Trades: {summary.get('total_trades', 0)}
   Wins: {summary.get('wins', 0)} | Losses: {summary.get('losses', 0)}
   Win Rate: {summary.get('win_rate', 0):.1f}%

💰 P&L: *₹{summary.get('pnl', 0):+,}*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Key Insights:
{summary.get('insights', 'System performing within parameters')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 *Ready for tomorrow's session*"""
    
    return text

def format_help():
    """Help command - polished format"""
    
    text = """╔════════════════════════════════════════╗
║        📡 APEX COMMAND CENTER           ║
╚════════════════════════════════════════╝

Available Commands:

🔍 STATUS - Current positions & P&L
📊 SUMMARY - Today's trading summary
🎯 SIGNALS - Active signals
📈 VIX - Current VIX & regime
💰 PNL - Profit/Loss breakdown

⚡ ACTION:
🔴 STOP - Pause all trading
🟢 START - Resume trading
🔄 RESET - Reset daily counters

❓ HELP - Show this menu

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Send any command to get instant response*"""
    
    return text

def format_status(state):
    """Status command - polished format"""
    
    positions = state.get('positions', [])
    today_pnl = state.get('today_pnl', 0)
    trade_count = state.get('today_trades', 0)
    vix = state.get('india_vix', {})
    regime = state.get('market_regime', 'UNKNOWN')
    
    pos_text = ""
    if positions:
        for p in positions:
            emoji = "🟢" if p.get('current_pnl', 0) >= 0 else "🔴"
            pos_text += f"\n{emoji} {p.get('symbol')} {p.get('strategy')}: ₹{p.get('current_pnl', 0):+,}"
    else:
        pos_text = "\n📭 No open positions"
    
    text = f"""╔════════════════════════════════════════╗
║        📊 APEX STATUS                   ║
║       {datetime.now().strftime('%d %b %Y %H:%M')}         ║
╚════════════════════════════════════════╝

🔴 VIX: {vix.get('current', 'N/A')} | Regime: *{regime}*

📈 Today's Stats:
   Trades: {trade_count}
   P&L: *₹{today_pnl:,}*

📊 Open Positions:{pos_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 *System: ACTIVE*"""
    
    return text

# ============================================================
# INCOMING MESSAGE HANDLER
# ============================================================

def process_command(command):
    """Process incoming Telegram command"""
    command = command.strip().upper()
    state = load_state()
    
    if command in ['STATUS', 'ST']:
        return format_status(state)
    
    elif command in ['SUMMARY', 'SUM', 'EOD']:
        summary = {
            'total_trades': len(state.get('trade_history', [])),
            'wins': sum(1 for t in state.get('trade_history', []) if t.get('pnl', 0) > 0),
            'losses': sum(1 for t in state.get('trade_history', []) if t.get('pnl', 0) <= 0),
            'pnl': sum(t.get('pnl', 0) for t in state.get('trade_history', [])),
            'win_rate': 0
        }
        if summary['total_trades'] > 0:
            summary['win_rate'] = (summary['wins'] / summary['total_trades']) * 100
        return format_eod(summary)
    
    elif command in ['SIGNALS', 'SIG']:
        return f"📡 Active signals: Check recent signals in state.json"
    
    elif command in ['VIX', 'REGIME']:
        vix = state.get('india_vix', {})
        regime = state.get('market_regime', 'UNKNOWN')
        return f"🔴 VIX: {vix.get('current', 'N/A')} ({vix.get('change', 0):+.2f}%)\n\n🎯 Regime: *{regime}*"
    
    elif command in ['PNL', 'P&L']:
        return f"💰 Today's P&L: *₹{state.get('today_pnl', 0):,}*"
    
    elif command in ['STOP', 'PAUSE']:
        state['auto_trade']['enabled'] = False
        save_state(state)
        return "🔴 *Trading PAUSED*\n\nAll new signal generation stopped."
    
    elif command in ['START', 'RESUME']:
        state['auto_trade']['enabled'] = True
        save_state(state)
        return "🟢 *Trading RESUMED*\n\nSystem ready to generate signals."
    
    elif command in ['RESET', 'CLEAR']:
        state['today_trades'] = 0
        state['today_pnl'] = 0
        state['positions'] = []
        save_state(state)
        return "🔄 *Daily counters RESET*\n\nPositions cleared, ready for new day."
    
    elif command in ['HELP', '?']:
        return format_help()
    
    else:
        return f"❓ Unknown command: {command}\n\nSend *HELP* for available commands."

def check_and_respond():
    """Check for new Telegram messages and respond"""
    config = load_config()
    bot_token = config.get('telegram', {}).get('bot_token', '')
    chat_id = config.get('telegram', {}).get('chat_id', '')
    
    if not bot_token or not chat_id:
        return False
    
    # Get updates
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                updates = data.get('result', [])
                if updates:
                    # Get last update offset
                    last_update = updates[-1]
                    offset = last_update.get('update_id', 0) + 1
                    
                    # Process message
                    message = last_update.get('message', {})
                    text = message.get('text', '')
                    from_chat = str(message.get('from', {}).get('id', ''))
                    
                    # Only respond to our chat
                    if from_chat == chat_id and text:
                        response_text = process_command(text)
                        send_telegram_message(response_text)
                        
                        # Acknowledge by marking processed
                        requests.post(f"https://api.telegram.org/bot{bot_token}/getUpdates", 
                                     json={"offset": offset})
                        return True
    except Exception as e:
        print(f"Error checking messages: {e}")
    
    return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "send":
            # Send a message
            if len(sys.argv) > 2:
                send_telegram_message(" ".join(sys.argv[2:]))
        elif sys.argv[1] == "check":
            # Check for new messages
            check_and_respond()
        elif sys.argv[1] == "test":
            # Test message formatting
            print(format_help())
    else:
        print("Usage:")
        print("  python3 telegram_bot.py send <message>")
        print("  python3 telegram_bot.py check")
        print("  python3 telegram_bot.py test")