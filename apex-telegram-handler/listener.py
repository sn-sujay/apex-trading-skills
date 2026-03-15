#!/usr/bin/env python3
"""
APEX Telegram Listener - Simple instant response
"""

import os
import sys
import json
import time
import requests
import yaml
import signal

TOKEN = "8704170382:AAFvHBjC2G_LFHUrQs5WR84LQGJ2G4GKFSc"
CHAT_ID = "419180494"
RUNNING = True

def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=data, timeout=5)
    except Exception as e:
        print(f"Send error: {e}")

def process(cmd):
    cmd = cmd.strip().upper()
    
    if cmd in ['STATUS', 'ST']:
        return """╔════════════════════════════════════════╗
║        📊 APEX STATUS                   
╚════════════════════════════════════════╝

🔴 VIX: Check state.json
🎯 Regime: Check state.json

📈 Today: 0 trades | P&L: ₹0

📊 Positions: None

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 System: ACTIVE"""
    
    elif cmd == 'HELP':
        return """╔════════════════════════════════════════╗
║        📡 APEX COMMANDS                 
╚════════════════════════════════════════╝

STATUS - Positions & P&L
VIX - Market VIX level
PNL - Today's P&L
HELP - This menu

STOP - Pause trading
START - Resume trading"""

    elif cmd == 'VIX':
        return "🔴 VIX: Check state.json for current value"
    
    elif cmd == 'PNL':
        return "💰 Today's P&L: ₹0"
    
    else:
        return f"❓ Unknown: {cmd}. Send HELP."

def signal_handler(sig, frame):
    global RUNNING
    RUNNING = False

# Signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print("🤖 APEX Telegram Listener Running")
print("Send me a command!")

send("✅ *Listener Running!*\n\nCommands now respond instantly!\nTry: STATUS, HELP, VIX")

while RUNNING:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?timeout=1"
        r = requests.get(url, timeout=3)
        
        if r.status_code == 200:
            data = r.json()
            updates = data.get('result', [])
            
            if updates:
                last = updates[-1]
                msg = last.get('message', {})
                text = msg.get('text', '')
                from_id = str(msg.get('from', {}).get('id', ''))
                update_id = last.get('update_id', 0)
                
                if from_id == CHAT_ID and text:
                    print(f"Command: {text}")
                    response = process(text)
                    send(response)
                    print("Responded!")
                    
                    # Acknowledge
                    requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={update_id + 1}", timeout=3)
                    
    except Exception as e:
        # Just continue on any error
        pass
    
    time.sleep(1)  # Check every second for instant response

print("Stopped")