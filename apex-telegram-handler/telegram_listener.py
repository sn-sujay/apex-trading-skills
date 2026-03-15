#!/usr/bin/env python3
"""
APEX Telegram Listener - Instant Response Daemon
Runs continuously and responds immediately to Telegram commands
"""

import os
import sys
import json
import time
import requests
import yaml
import signal
from datetime import datetime
import threading

# Config
CONFIG_PATH = os.path.expanduser("~/.apex/config.yaml")
STATE_PATH = os.path.expanduser("~/.apex/state.json")
RUNNING = True

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def load_state():
    try:
        with open(STATE_PATH, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)

def send_message(text, parse_mode="Markdown"):
    config = load_config()
    bot_token = config.get('telegram', {}).get('bot_token', '')
    chat_id = config.get('telegram', {}).get('chat_id', '')
    
    if not bot_token or not chat_id:
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
    except:
        return False

def process_command(command):
    state = load_state()
    command = command.strip().upper()
    
    if command in ['STATUS', 'ST']:
        vix = state.get('india_vix', {})
        regime = state.get('market_regime', 'UNKNOWN')
        today_pnl = state.get('today_pnl', 0)
        trades = state.get('today_trades', 0)
        
        return f"""╔════════════════════════════════════════╗
║        📊 APEX STATUS                   
║       {datetime.now().strftime('%d %b %H:%M')}                
╚════════════════════════════════════════╝

🔴 VIX: {vix.get('current', 'N/A')} | Regime: *{regime}*

📈 Today: {trades} trades | P&L: *₹{today_pnl:,}*

📊 Open Positions:
📭 No open positions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 System: *ACTIVE*"""
    
    elif command in ['SUMMARY', 'SUM', 'EOD']:
        history = state.get('trade_history', [])
        wins = sum(1 for t in history if t.get('pnl', 0) > 0)
        losses = sum(1 for t in history if t.get('pnl', 0) <= 0)
        pnl = sum(t.get('pnl', 0) for t in history)
        total = len(history)
        win_rate = (wins / total * 100) if total > 0 else 0
        
        return f"""╔════════════════════════════════════════╗
║        📊 APEX EOD SUMMARY              
╚════════════════════════════════════════╝

📈 Performance:
   Trades: {total}
   Wins: {wins} | Losses: {losses}
   Win Rate: {win_rate:.1f}%

💰 P&L: *₹{pnl:,}*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 *Ready for tomorrow*"""

    elif command in ['VIX', 'REGIME']:
        vix = state.get('india_vix', {})
        regime = state.get('market_regime', 'UNKNOWN')
        return f"""╔════════════════════════════════════════╗
║        📈 MARKET STATUS                 
╚════════════════════════════════════════╝

🔴 VIX: *{vix.get('current', 'N/A')}* ({vix.get('change', 0):+.2f}%)

🎯 Regime: *{regime}*

📊 Last Updated: {vix.get('timestamp', 'N/A')}"""

    elif command in ['PNL', 'P&L']:
        pnl = state.get('today_pnl', 0)
        return f"💰 Today's P&L: *₹{pnl:,}*"

    elif command in ['STOP', 'PAUSE']:
        state.setdefault('auto_trade', {})['enabled'] = False
        save_state(state)
        return "🔴 *Trading PAUSED*\n\nAll new signal generation stopped."

    elif command in ['START', 'RESUME', 'PLAY']:
        state.setdefault('auto_trade', {})['enabled'] = True
        save_state(state)
        return "🟢 *Trading RESUMED*\n\nSystem ready to generate signals."

    elif command in ['RESET', 'CLEAR']:
        state['today_trades'] = 0
        state['today_pnl'] = 0
        state['positions'] = []
        save_state(state)
        return "🔄 *Daily counters RESET*\n\nPositions cleared."

    elif command in ['HELP', '?']:
        return """╔════════════════════════════════════════╗
║        📡 APEX COMMAND CENTER           
╚════════════════════════════════════════╝

Available Commands:

🔍 STATUS - Current positions & P&L
📊 SUMMARY - Today's trading summary  
📈 VIX - Current VIX & regime
💰 PNL - Today's P&L
❓ HELP - Show this menu

🛑 STOP - Pause trading
🟢 START - Resume trading
🔄 RESET - Reset counters"""

    else:
        return f"❓ Unknown: {command}\n\nSend *HELP* for commands."

def check_messages():
    """Check for new messages and respond instantly"""
    config = load_config()
    bot_token = config.get('telegram', {}).get('bot_token', '')
    chat_id = config.get('telegram', {}).get('chat_id', '')
    
    if not bot_token or not chat_id:
        return
    
    try:
        # Get updates (short timeout)
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates?timeout=1"
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                updates = data.get('result', [])
                
                # Process only the latest unprocessed update
                if updates:
                    last = updates[-1]
                    update_id = last.get('update_id', 0)
                    msg = last.get('message', {})
                    text = msg.get('text', '')
                    from_id = str(msg.get('from', {}).get('id', ''))
                    
                    # Only respond to our chat
                    if from_id == chat_id and text:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Command: {text}")
                        
                        # Process and respond
                        response_text = process_command(text)
                        send_message(response_text)
                        
                        # Acknowledge by advancing offset
                        requests.get(f"https://api.telegram.org/bot{bot_token}/getUpdates?offset={update_id + 1}")
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Responded!")
                        
    except Exception as e:
        pass  # Silent on errors - keep running

def signal_handler(sig, frame):
    global RUNNING
    print("\nStopping APEX Telegram Listener...")
    RUNNING = False

def run_listener():
    """Main listener loop - checks every 2 seconds for instant response"""
    global RUNNING
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"🤖 APEX Telegram Listener Started")
    print(f"   Checking every 2 seconds for instant response...")
    print(f"   Press Ctrl+C to stop")
    
    send_message("✅ *APEX Listener Started*\n\nI'll now respond to your commands instantly!\n\nTry: STATUS, HELP, VIX")
    
    while RUNNING:
        check_messages()
        time.sleep(2)  # Check every 2 seconds for near-instant response

if __name__ == "__main__":
    run_listener()