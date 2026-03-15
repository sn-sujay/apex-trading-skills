# APEX Autonomous Trading System - Complete Technical Documentation

**Version:** 2.0 (LLM-Driven)  
**Last Updated:** March 15, 2026  
**Author:** APEX Architecture Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Agent Ecosystem](#agent-ecosystem)
4. [Inter-Agent Communication](#inter-agent-communication)
5. [Live Market Flow - Step by Step](#live-market-flow---step-by-step)
6. [Decision Making Process](#decision-making-process)
7. [Cron Jobs & Scheduling](#cron-jobs--scheduling)
8. [State Management](#state-management)
9. [Example: A Complete Trade Day](#example-a-complete-trade-day)
10. [Troubleshooting](#troubleshooting)

---

## Executive Summary

APEX is an **autonomous AI-driven trading system** for Indian equity and derivatives (NSE F&O). The system uses **LLM-powered agents** that:

- Analyze market conditions in real-time
- Generate trading signals with reasoning
- Execute trades automatically (paper or live)
- Learn from performance and evolve strategies
- Coordinate via an event-driven architecture

**Key Stats:**
- 32 trading skills
- 10+ specialized agents
- Event-driven pub/sub architecture
- Full state synchronization (local + cloud)
- Self-healing & autonomous evolution

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           APEX TRADING SYSTEM                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                     HERMES AGENT (LLM Brain)                             │   │
│   │              All Analysis, Reasoning, Decision Making                    │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                             │
│                                    ▼                                             │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                    APEX CORE ORCHESTRATOR                                │   │
│   │              Event Bus + Agent Registry + Workflow Engine                │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                             │
│         ┌──────────────────────────┼──────────────────────────┐               │
│         ▼                          ▼                          ▼               │
│   ┌─────────────┐          ┌─────────────┐            ┌─────────────┐         │
│   │   MARKET    │          │   SIGNAL    │            │  TRADING    │         │
│   │   ANALYSIS  │          │  GENERATION │            │  EXECUTION  │         │
│   │             │          │             │            │             │         │
│   │ • VIX       │─────────▶│ • Options   │───────────▶│ • Executor  │         │
│   │ • Regime    │          │ • Strategy  │            │ • Monitor   │         │
│   │ • Options   │          │ • Forex     │            │ • Risk Veto │         │
│   │ • Sentiment │          │             │            │             │         │
│   └─────────────┘          └─────────────┘            └─────────────┘         │
│                                    │                          │                 │
│                                    ▼                          ▼                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                    LEARNING & OPTIMIZATION                              │   │
│   │              Self-Evolution + Performance Monitoring                    │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Ecosystem

### 1. Market Analysis Agents

| Agent | Purpose | Key Functions |
|-------|---------|---------------|
| **apex-india-vix-monitor** | Monitor India VIX | Fetch VIX from NSE, detect volatility regime |
| **apex-option-chain-monitor** | Option chain analysis | PCR, IV rank, GEX, OI analysis, max pain |
| **apex-sentiment-engine** | News & social sentiment | Scrape news, social media, generate sentiment score |
| **apex-global-macro-scanner** | Global macro intelligence | DXY, Fed rates, US market futures |

### 2. Signal Generation Agents

| Agent | Purpose | Key Functions |
|-------|---------|---------------|
| **apex-market-regime-engine** | Classify market regime | TRENDING_UP, TRENDING_DOWN, RANGING, VOLATILE |
| **apex-options-strategy-engine** | Generate trade signals | Bull Call Spread, Bear Put Spread, Iron Condor, etc. |
| **apex-inr-signal-engine** | USD/INR signals | RBI policy tracking, range analysis |

### 3. Trading Execution Agents

| Agent | Purpose | Key Functions |
|-------|---------|---------------|
| **apex-live-order-executor** | Place live orders | Dhan API integration, order placement |
| **apex-live-order-monitor** | Monitor positions | Track SL, Target, MTM P&L, auto-exit |
| **apex-paper-trade-engine** | Paper trading | Simulate trades, track performance |
| **apex-risk-veto-authority** | Risk validation | 6-gate risk check before execution |
| **apex-validator-gate** | Input validation | Validate all inputs before execution |

### 4. Learning & Evolution Agents

| Agent | Purpose | Key Functions |
|-------|---------|---------------|
| **apex-self-evolution-engine** | Auto-learning | Adjust strategy weights, log trade lessons |
| **apex-performance-monitor** | Track metrics | Sharpe, Calmar, Sortino ratios |
| **apex-strategy-validator** | Backtesting | Walk-forward validation |
| **apex-system-health-monitor** | Watchdog | Monitor all agents, fire URGENT alerts |

### 5. Orchestration Agents

| Agent | Purpose | Key Functions |
|-------|---------|---------------|
| **apex-core-orchestrator** | Central coordination | Event bus, workflow engine, agent registry |
| **apex-india-trading-central-command** | Master router | Route workflows, EOD reconciliation |
| **apex-state-sync** | State synchronization | Sync between file, Upstash, Hermes memory |

---

## Inter-Agent Communication

### Event Bus Architecture

The orchestrator maintains an **event bus** where agents publish and subscribe to events:

```
┌─────────────────────────────────────────────────────────────┐
│                    APEX EVENT BUS                           │
├─────────────────────────────────────────────────────────────┤
│  AGENT A ──publishes──┐                                    │
│  AGENT B ──publishes──┼───→ EVENT QUEUE                    │
│  AGENT C ──publishes──┘         │                           │
│                                ▼                           │
│              ┌─────────────────────────┐                   │
│              │    SUBSCRIBER CHAIN     │                   │
│              └─────────────────────────┘                   │
│                        │                                   │
│         ┌──────────────┼──────────────┐                   │
│         ▼              ▼              ▼                   │
│    AGENT D         AGENT E        AGENT F                  │
│   (process)      (process)       (process)                 │
└─────────────────────────────────────────────────────────────┘
```

### Event Types

| Event | Published By | Consumed By | Description |
|-------|--------------|-------------|-------------|
| `market:open` | Orchestrator | All agents | Market opened at 9:15 AM |
| `market:close` | Orchestrator | All agents | Market closed at 3:30 PM |
| `data:vix_updated` | VIX Monitor | Regime Engine | New VIX data available |
| `market:regime_changed` | Regime Engine | Risk Manager | Regime classification changed |
| `signal:generated` | Strategy Engine | Risk Veto | New trading signal ready |
| `signal:validated` | Risk Veto | Order Executor | Signal approved for execution |
| `trade:executed` | Order Executor | Monitor, Performance | Trade placed successfully |
| `trade:closed` | Order Monitor | Evolution Engine | Trade exited, analyze performance |
| `evolution:trigger` | Daily @ 3:30 PM | Self-Evolution | Time to learn and adjust |
| `sentiment:changed` | Sentiment Engine | Risk Veto | Market sentiment shifted |
| `error:trigger_failed` | Error Monitor | Fix Monitor | Auto-healing needed |

### Message Format

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "signal:generated",
  "timestamp": "2026-03-15T09:30:00+05:30",
  "source_agent": "apex-options-strategy-engine",
  "target_agents": ["apex-risk-veto-authority", "apex-validator-gate"],
  "payload": {
    "signal": "BUY",
    "symbol": "NIFTY",
    "action": "Bull Call Spread",
    "strike": 22500,
    "expiry": "2026-03-20",
    "entry_price": 150,
    "stop_loss": 75,
    "target": 225,
    "confidence": 72,
    "reasoning": "PCR at 1.45 suggests bullish sentiment..."
  },
  "priority": "high",
  "requires_response": true
}
```

---

## Live Market Flow - Step by Step

### Phase 1: Pre-Market (8:00 AM - 9:00 AM)

```
┌────────────────────────────────────────────────────────────────────┐
│                     8:00 AM - PRE-MARKET                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  1. Cronjob triggers apex-india-trading-central-command           │
│                                                                    │
│  2. Central Command runs LLM with full context:                   │
│     ┌─────────────────────────────────────────────────────────┐   │
│     │ TASK: Generate Pre-Market Briefing                      │
│     │                                                         │   │
│     │ STEPS:                                                  │   │
│     │ 1. Fetch India VIX from NSE                            │   │
│     │ 2. Fetch Nifty/Finnifty levels                         │   │
│     │ 3. Search latest market news                           │   │
│     │ 4. Analyze global markets (US, Asia)                   │   │
│     │ 5. Classify market regime (LLM reasoning)              │   │
│     │ 6. Generate sentiment score                            │   │
│     │ 7. Output: Pre-market briefing with regime/sentiment   │   │
│     └─────────────────────────────────────────────────────────┘   │
│                                                                    │
│  3. LLM Output sent to Telegram                                   │
│                                                                    │
│  Example Output:                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 📊 APEX Pre-Market Briefing - March 15, 2026               │  │
│  │                                                            │  │
│  │ 🇮🇳 VIX: 22.65 (+5.23%) - HIGH VOLATILITY                  │  │
│  │ 📈 Nifty: 22,450 (ATM)                                     │  │
│  │                                                            │  │
│  │ 🌍 Global: US markets mixed, Asia flat                     │  │
│  │ 📰 News: RBI holds rates, IT stocks mixed                  │  │
│  │                                                            │  │
│  │ 🎯 Regime: HIGH_VOLATILITY                                 │  │
│  │ 💭 Sentiment: BULLISH (Confidence: 65%)                    │  │
│  │                                                            │  │
│  │ ⚠️ Recommendation: Use Long Strangle/Straddle due to      │  │
│  │    high IV. Reduced position size recommended.            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Phase 2: Market Open (9:15 AM)

```
┌────────────────────────────────────────────────────────────────────┐
│                    9:15 AM - MARKET OPEN                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  1. Cronjob triggers apex-market-regime-engine                    │
│                                                                    │
│  2. Market Regime Engine (LLM):                                   │
│     ┌─────────────────────────────────────────────────────────┐   │
│     │ TASK: Classify Market Regime                            │
│     │                                                         │   │
│     │ INPUTS:                                                 │   │
│     │ • Current VIX: 22.65                                   │   │
│     │ • Yesterday's trend: +0.8%                             │   │
│     │ • Global cues: Mixed                                   │   │
│     │ • Pre-market sentiment: BULLISH                        │   │
│     │                                                         │   │
│     │ OUTPUT:                                                 │   │
│     │ {                                                       │   │
│     │   "regime": "HIGH_VOLATILITY",                         │   │
│     │   "confidence": 78,                                    │   │
│     │   "reasoning": "VIX above 20 indicates elevated       │   │
│     │   volatility. Combined with range-bound nifty..."     │   │
│     │ }                                                       │   │
│     └─────────────────────────────────────────────────────────┘   │
│                                                                    │
│  3. Publishes event: market:regime_changed                        │
│                                                                    │
│  4. Risk Veto adjusts parameters:                                 │
│     • Max position size: 0.5 (reduced from 1.0)                  │
│     • Stop loss tighter: 40% (vs 50%)                            │   │
│     • Cooldown between trades: 300s (vs 60s)                     │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Phase 3: Signal Generation (Every Hour 9:00 AM - 2:00 PM)

```
┌────────────────────────────────────────────────────────────────────┐
│                    HOURLY - SIGNAL GENERATION                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Cronjob: apex-options-strategy-engine                            │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    OPTIONS STRATEGY ENGINE                   │  │
│  │                   (LLM-Powered Signal Generator)             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 1: Fetch Data                                          │  │
│  │   • VIX: 22.65 (cached)                                     │  │
│  │   • Option Chain: PCR=1.45, IV Rank=65%                     │  │
│  │   • Regime: HIGH_VOLATILITY                                 │  │
│  │   • Sentiment: BULLISH                                      │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 2: LLM Reasoning (Full Prompt)                         │  │
│  │ ┌─────────────────────────────────────────────────────────┐ │  │
│  │ │ TASK: Generate Trading Signal                           │ │  │
│  │ │                                                         │ │  │
│  │ │ MARKET CONDITIONS:                                      │ │  │
│  │ │ • VIX: 22.65 (HIGH)                                     │ │  │
│  │ │ • PCR: 1.45 (Bullish - more puts bought)                │ │  │
│  │ │ • IV Rank: 65%                                          │ │  │
│  │ │ • Regime: HIGH_VOLATILITY                                │ │  │
│  │ │ • Sentiment: BULLISH (65%)                               │ │  │
│  │ │                                                         │ │  │
│  │ │ STRATEGY MAPPING:                                        │ │  │
│  │ │ • TRENDING_UP + BULLISH → Bull Call Spread              │ │  │
│  │ │ • HIGH_VOLATILITY → Long Strangle                       │ │  │
│  │ │ • RANGING → Iron Condor                                  │ │  │
│  │ │                                                         │ │  │
│  │ │ YOUR JOB:                                               │ │  │
│  │ │ 1. Analyze the above conditions                         │ │  │
│  │ │ 2. Select appropriate strategy                          │ │  │
│  │ │ 3. Calculate strikes (ATM +/- 1-2)                      │ │  │
│  │ │ 4. Determine entry/exit/stop loss                       │ │  │
│  │ │ 5. Assign confidence score                              │ │  │
│  │ │ 6. Explain your reasoning                               │ │  │
│  │ └─────────────────────────────────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 3: LLM Output - Trade Signal                           │  │
│  │ {                                                           │  │
│  │   "signal": "BUY",                                          │  │
│  │   "strategy": "Long Strangle",                              │  │
│  │   "symbol": "NIFTY",                                        │  │
│  │   "expiry": "2026-03-20",                                   │  │
│  │   "legs": [                                                 │  │
│  │     {"action": "BUY", "type": "CE", "strike": 22500,       │  │
│  │      "premium": 180},                                       │  │
│  │     {"action": "BUY", "type": "PE", "strike": 22300,       │  │
│  │      "premium": 165}                                        │  │
│  │   ],                                                        │  │
│  │   "entry_range": {"min": 340, "max": 360},                 │  │
│  │   "stop_loss": 170,  // 50% of total premium               │  │
│  │   "target": 510,   // 1.5x premium                         │  │
│  │   "confidence": 72,                                         │  │
│  │   "reasoning": "VIX at 22.65 indicates high volatility.   │  │
│  │   PCR at 1.45 suggests bullish bias but high IV favors    │  │
│  │   buying volatility. Long Strangle benefits from large    │  │
│  │   moves in either direction while limiting loss to       │  │
│  │   premium paid..."                                         │  │
│  │ }                                                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 4: Publish to Event Bus                                │  │
│  │   event: signal:generated                                  │  │
│  │   target: apex-risk-veto-authority                         │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Phase 4: Risk Validation

```
┌────────────────────────────────────────────────────────────────────┐
│                    RISK VETO AUTHORITY                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  When signal:generated event is received:                         │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ GATE 1: Regime Check                                        │  │
│  │   • Is signal appropriate for current regime?              │  │
│  │   • HIGH_VOLATILITY → OK for Strangle                      │  │
│  │   Result: ✅ PASS                                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ GATE 2: Confidence Threshold                                │  │
│  │   • Signal confidence: 72                                   │  │
│  │   • Minimum required: 65                                    │  │
│  │   Result: ✅ PASS                                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ GATE 3: Position Size                                       │  │
│  │   • Proposed risk: ₹10,000                                  │  │
│  │   • Max allowed: ₹25,000 (based on regime)                 │  │
│  │   Result: ✅ PASS                                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ GATE 4: Daily Trade Limit                                   │  │
│  │   • Trades today: 1                                         │  │
│  │   • Max daily: 5                                            │  │
│  │   Result: ✅ PASS                                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ GATE 5: Cooldown                                            │  │
│  │   • Last trade: 45 minutes ago                              │  │
│  │   • Required cooldown: 60 minutes (HIGH_VOLATILITY)        │  │
│  │   Result: ❌ FAIL - Wait 15 more minutes                   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ GATE 6: Margin Availability                                 │  │
│  │   • Required margin: ₹50,000                                │  │
│  │   • Available: ₹1,20,000                                    │  │
│  │   Result: ✅ PASS                                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ FINAL DECISION: ✅ SIGNAL VALIDATED                         │  │
│  │   Publish: signal:validated                                 │  │
│  │   Next: apex-live-order-executor                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Phase 5: Order Execution

```
┌────────────────────────────────────────────────────────────────────┐
│                    LIVE ORDER EXECUTOR                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  When signal:validated event is received:                         │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 1: Check Auto-Execute Setting                          │  │
│  │   • auto_execute: true/false (from config)                 │  │
│  │   • If false → Send to Telegram for manual approval        │  │
│  │   • If true → Proceed to execution                         │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 2: Place Orders via Dhan API                           │  │
│  │                                                         │   │
│  │ Leg 1: BUY NIFTY 22500 CE @ ₹180                          │   │
│  │   POST https://api.dhan.co/orders/regular                 │   │
│  │   {                                                        │   │
│  │     "exchange": "NSE_FO",                                  │   │
│  │     "transaction_type": "BUY",                             │   │
│  │     "security_id": "13044",  // NIFTY 22500 CE           │   │
│  │     "quantity": 75,                                        │   │
│  │     "order_type": "LIMIT",                                 │   │
│  │     "price": 180                                           │   │
│  │   }                                                        │   │
│  │                                                         │   │
│  │ Leg 2: BUY NIFTY 22300 PE @ ₹165                          │   │
│  │   (same structure)                                         │   │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 3: Monitor Order Status                                │  │
│  │   • Order 1: FILLED @ ₹180                                 │   │
│  │   • Order 2: FILLED @ ₹165                                 │   │
│  │   Total Premium: ₹34,500                                   │   │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 4: Update State                                        │  │
│  │   {                                                         │  │
│  │     "positions": [                                         │  │
│  │       {                                                     │  │
│  │         "symbol": "NIFTY",                                 │  │
│  │         "strategy": "Long Strangle",                       │  │
│  │         "legs": [...],                                     │  │
│  │         "entry_premium": 345,                              │  │
│  │         "stop_loss": 172,                                  │  │
│  │         "target": 517,                                     │  │
│  │         "entry_time": "2026-03-15T09:35:00",               │  │
│  │         "status": "OPEN"                                   │  │
│  │       }                                                     │  │
│  │   ]                                                         │  │
│  │ }                                                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 5: Publish Event                                       │  │
│  │   event: trade:executed                                    │  │
│  │   Target: apex-live-order-monitor                         │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Phase 6: Intraday Monitoring (Every 5 Minutes)

```
┌────────────────────────────────────────────────────────────────────┐
│                 ORCHESTRATOR - INTRADAY MONITORING                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Cronjob runs every 5 minutes (9:15 AM - 3:00 PM):                │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ FOR EACH OPEN POSITION:                                     │  │
│  │                                                             │  │
│  │ 1. Fetch current market price                              │  │
│  │ 2. Calculate MTM P&L                                       │  │
│  │ 3. Check stop loss                                         │  │
│  │    • Current loss > stop loss? → EXIT                      │  │
│  │ 4. Check target                                            │  │
│  │    • Current profit > target? → EXIT                       │  │
│  │ 5. Check time exit                                         │  │
│  │    • Near market close? → EXIT                             │  │
│  │ 6. Check for reversal signals                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│           ┌──────────────────┼──────────────────┐                 │
│           ▼                  ▼                  ▼                 │
│    ┌────────────┐     ┌────────────┐     ┌────────────┐          │
│    │  STOP LOSS │     │   TARGET   │     │  TIME EXIT │          │
│    │   HIT ❌   │     │   HIT ✅   │     │    -       │          │
│    └────────────┘     └────────────┘     └────────────┘          │
│           │                  │                                    │
│           ▼                  ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ EXIT TRADE                                                  │  │
│  │ • Sell both legs via Dhan API                              │  │
│  │ • Calculate realized P&L                                   │  │
│  │ • Update state.json                                        │  │
│  │ • Publish: trade:closed                                    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Phase 7: Market Close & Evolution (3:30 PM)

```
┌────────────────────────────────────────────────────────────────────┐
│                    3:30 PM - MARKET CLOSE                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ SELF-EVOLUTION ENGINE                                        │  │
│  │ (LLM-Powered Learning)                                       │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 1: Analyze Today's Trades                              │  │
│  │   • Total trades: 2                                         │  │
│  │   • Winners: 1 (Long Strangle +₹4,200)                     │  │
│  │   • Losers: 1 (Bull Call Spread -₹1,800)                   │  │
│  │   • Net P&L: +₹2,400                                        │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 2: LLM Analysis                                         │  │
│  │ ┌─────────────────────────────────────────────────────────┐ │  │
│  │ │ TASK: Analyze trading performance                       │ │  │
│  │ │                                                         │ │  │
│  │ │ TODAY'S RESULTS:                                        │ │  │
│  │ │ • Trade 1: Long Strangle - WIN (+₹4,200)               │ │  │
│  │ │   Reasoning: Correct call on volatility, VIX moved     │ │  │
│  │ │   from 22 to 26, benefited from IV crush reversal      │ │  │
│  │ │                                                         │ │  │
│  │ │ • Trade 2: Bull Call Spread - LOSS (-₹1,800)           │ │  │
│  │ │   Reasoning: Wrong direction, nifty reversed after     │ │  │
│  │ │   initial move. Stop loss worked correctly.            │ │  │
│  │ │                                                         │ │  │
│  │ │ METRICS:                                                │ │  │
│  │ │ • Sharpe: 1.2 (improved from 1.1)                      │ │  │
│  │ │ • Win rate: 50% (same)                                 │ │  │
│  │ │ • Avg win/loss: 2.3 (improved from 2.1)                │ │  │
│  │ │                                                         │ │  │
│  │ │ YOUR JOB:                                               │ │  │
│  │ │ 1. What worked well today?                             │ │  │
│  │ │ 2. What needs improvement?                             │ │  │
│  │ │ 3. Adjust strategy weights for next week               │ │  │
│  │ │ 4. Log trade lessons for future reference              │ │  │
│  │ └─────────────────────────────────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 3: Adjust Strategy Weights                             │  │
│  │   {                                                         │  │
│  │     "strategy_weights": {                                   │  │
│  │       "Bull Call Spread": 0.20,  // Reduced               │  │
│  │       "Bear Put Spread": 0.15,                             │  │
│  │       "Iron Condor": 0.25,                                 │  │
│  │       "Long Straddle": 0.25,  // Increased                │  │
│  │       "Long Strangle": 0.15                                │  │
│  │     },                                                      │  │
│  │     "confidence_thresholds": {                             │  │
│  │       "Bull Call Spread": 70,  // Increased from 65       │  │
│  │       "Long Straddle": 60                                  │  │
│  │     },                                                      │  │
│  │     "trade_lessons": [                                     │  │
│  │       "Long Strangle works better when VIX > 20",         │  │
│  │       "Reduce Bull Call Spread in uncertain markets"      │  │
│  │     ]                                                       │  │
│  │   }                                                         │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ STEP 4: Send EOD Report to Telegram                         │  │
│  │   ┌────────────────────────────────────────────────────┐   │  │
│  │   │ 📊 APEX EOD Report - March 15, 2026                 │   │  │
│  │   │                                                     │   │  │
│  │   │ Trades: 2 | Wins: 1 | Loss: 1                       │   │  │
│  │   │ P&L: +₹2,400                                        │   │  │
│  │   │                                                     │   │  │
│  │   │ Key Insight: Long Strangle performed well in       │   │  │
│  │   │ high volatility. Will increase weight next week.   │   │  │
│  │   └────────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Decision Making Process

### How the LLM Makes Decisions

```
┌────────────────────────────────────────────────────────────────────┐
│                    LLM DECISION FRAMEWORK                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Every LLM call includes:                                         │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ CONTEXT (What the LLM knows)                                │  │
│  │ • Current VIX and trend                                     │  │
│  │ • Option chain metrics (PCR, IV, OI)                       │  │
│  │ • Market regime classification                              │  │
│  │ • Sentiment score                                           │  │
│  │ • Historical performance (win rate, Sharpe)                │  │
│  │ • Current open positions                                    │  │
│  │ • Strategy weights                                          │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ CONSTRAINTS (Rules it must follow)                          │  │
│  │ • Max position size based on regime                         │  │
│  │ • Minimum confidence threshold (65%)                        │  │
│  │ • Max daily trades (5)                                      │  │
│  │ • Cooldown between trades                                   │  │
│  │ • Stop loss rules (40-50% of premium)                       │  │
│  │ • Capital preservation first                                │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ DECISION TREE                                               │  │
│  │                                                             │  │
│  │ INPUTS:                                                     │  │
│  │   VIX = 22.65 (HIGH)                                        │  │
│  │   PCR = 1.45 (Bullish)                                      │  │
│  │   Regime = HIGH_VOLATILITY                                  │  │
│  │   Sentiment = BULLISH                                       │  │
│  │                                                             │  │
│  │ LOGIC:                                                      │  │
│  │   IF VIX > 20 THEN                                          │  │
│  │     → Strategy = Long Strangle OR Long Straddle            │  │
│  │   ELSE IF Regime = TRENDING_UP AND Sentiment = BULLISH     │  │
│  │     → Strategy = Bull Call Spread                          │  │
│  │   ELSE IF Regime = TRENDING_DOWN                           │  │
│  │     → Strategy = Bear Put Spread                           │  │
│  │   ELSE IF Regime = RANGING                                  │  │
│  │     → Strategy = Iron Condor                               │  │
│  │                                                             │  │
│  │ OUTPUT:                                                     │  │
│  │   Selected: Long Strangle                                   │  │
│  │   Confidence: 72%                                           │  │
│  │   Reasoning: Explained in detail                            │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ VALIDATION                                                  │  │
│  │ • Does confidence >= 65%? → YES                            │  │
│  │ • Is strategy valid for regime? → YES                      │  │
│  │ • Within position limits? → YES                            │  │
│  │ • Passes all risk gates? → YES/NO                          │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ EXECUTE OR REJECT                                           │  │
│  │                                                             │  │
│  │ ✅ All checks pass → Execute trade                          │  │
│  │ ❌ Any check fails → Log reason, skip trade                │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Cron Jobs & Scheduling

### Current Schedule (All times IST)

| Time | Job | Action | Agent |
|------|-----|--------|-------|
| 8:00 AM | Pre-Market | LLM generates briefing, analyzes VIX/news/regime | Central Command |
| 9:15 AM | Market Regime | LLM classifies market regime | Market Regime Engine |
| Every 5 min | Orchestrator | Monitor positions, process events | Core Orchestrator |
| Hourly 9-2 PM | Signal Gen | LLM generates trading signals | Options Strategy Engine |
| 3:30 PM | Evolution | LLM analyzes performance, adjusts weights | Self-Evolution Engine |
| 3:40 PM | EOD | Close positions, compile report | Central Command |
| Sunday 8 PM | Health | System check, API validation | System Health Monitor |

### Cron Expression Format

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
* * * * *

Examples:
"0 8 * * 1-5"     → 8:00 AM, Mon-Fri
"15 9 * * 1-5"    → 9:15 AM, Mon-Fri
"*/5 9-15 * * 1-5"→ Every 5 min, 9:15 AM-3:00 PM, Mon-Fri
"0 9-14 * * 1-5"  → Every hour 9 AM-2 PM, Mon-Fri
"30 15 * * 1-5"   → 3:30 PM, Mon-Fri
"0 20 * * 0"      → 8:00 PM, Sunday
```

---

## State Management

### State Files

| File | Location | Purpose |
|------|----------|---------|
| `state.json` | `~/.apex/state.json` | Main config, positions, trades, VIX, regime |
| `orchestrator_state.json` | `~/.apex/orchestrator_state.json` | Workflow state, pending events |
| `event_bus.json` | `~/.apex/event_bus.json` | Event log, message queue |
| `rate_limits.json` | `~/.apex/rate_limits.json` | API rate limit tracking |

### State Hierarchy

```
1. HERMES MEMORY (fastest, session cache)
         ↓
2. UPSTASH REDIS (cloud, shared across agents)
         ↓
3. FILE SYSTEM (source of truth, ~/.apex/)

WRITE: File → Redis → Hermes Memory (async)
READ:  Hermes Cache → Redis → File (fallback)
```

### State.json Structure

```json
{
  "dhan_config": {...},
  "market_data": {
    "india_vix": {...},
    "option_chain": {...}
  },
  "strategy_mapping": {...},
  "trade_history": [...],
  "positions": [...],
  "evolution_log": [...]
}
```

---

## Example: A Complete Trade Day

### Morning (8:00 AM)

```
📱 Telegram Message Received:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 APEX Pre-Market Briefing - March 15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🇮🇳 VIX: 22.65 (+5.23%) - ELEVATED
📈 Nifty: 22,450 | BankNifty: 48,200

🌍 Global: US markets mixed, Asia flat
📰 News: RBI keeps rates steady

🎯 Regime: HIGH_VOLATILITY (conf: 78%)
💭 Sentiment: BULLISH (conf: 65%)

⚠️ Recommendation: Long Strangle
   • Reduced position size (0.5x)
   • Wide stop loss (60%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Mid-Morning (9:30 AM)

```
📱 Telegram Message Received:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 APEX Signal Generated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Strategy: Long Strangle
Symbol: NIFTY
Expiry: Mar 20, 2026

Legs:
  • BUY 22500 CE @ ₹180
  • BUY 22300 PE @ ₹165
  • Total Premium: ₹345

Entry: ₹340-350
Stop Loss: ₹172 (50%)
Target: ₹517 (1.5x)
Confidence: 72%

Reasoning: "VIX at 22.65 indicates high 
volatility. PCR at 1.45 suggests bullish 
sentiment. Long Strangle benefits from 
large moves in either direction..."

⚠️ Awaiting Risk Validation...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### After Validation

```
📱 Telegram Message Received:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TRADE EXECUTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Strategy: Long Strangle
Entry: ₹345 (both legs filled)
Stop Loss: ₹172
Target: ₹517

⏰ Entry Time: 09:35:22
📈 Status: MONITORING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Mid-Day Updates

```
📱 Telegram Message Received:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Position Update
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NIFTY Long Strangle
├── Current MTM: +₹2,100 (61%)
├── Time Elapsed: 2h 15m
├── Status: ACTIVE
└── Target: ₹517 (remaining: +₹172)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### End of Day

```
📱 Telegram Message Received:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TRADE EXITED - TARGET HIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Strategy: Long Strangle
Entry: ₹345
Exit: ₹510
P&L: +₹4,200 (+122%)

Duration: 5h 30m
Trade Lesson: Long Strangle works well 
when VIX > 20 and market is uncertain.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Telegram Message Received:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 APEX EOD Report - March 15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Performance:
  • Trades: 1 | Wins: 1 | Loss: 0
  • P&L: +₹4,200
  • Win Rate: 100%

📊 Metrics:
  • Sharpe: 1.3 (+0.2)
  • Avg Win/Loss: 2.5

🔄 Adjustments:
  • Long Strangle weight: 15% → 25%
  • Min confidence: 65% → 60%

📝 Trade Lessons:
  • Works great in high volatility
  • Good risk/reward ratio
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Troubleshooting

### Check System Status

```bash
# List all cronjobs
list_cronjobs()

# Check state
cat ~/.apex/state.json

# Check event bus
cat ~/.apex/event_bus.json

# Check logs
tail -100 ~/.hermes/logs/apex*.log
```

### Common Issues

| Issue | Solution |
|-------|----------|
| No signals generated | Check VIX and Option Chain caches |
| Trade rejected by Risk Veto | Check confidence score, position limits |
| State sync issues | Run apex-state-sync manually |
| Rate limit errors | Check apex-rate-limiter status |
| Missing positions | Check apex-live-order-monitor |

### Manual Intervention

```python
# Run specific agent manually
load_skill("apex-india-vix-monitor")
load_skill("apex-options-strategy-engine")
load_skill("apex-risk-veto-authority")

# Check positions
load_skill("apex-live-order-monitor")

# Force state sync
load_skill("apex-state-sync")
```

---

## Summary

APEX is a fully autonomous trading system where:

1. **LLM is the brain** - Every decision, analysis, and signal generation uses LLM with full context
2. **Agents are specialized** - Each agent has a specific role (VIX, Options, Risk, Execution)
3. **Events drive everything** - Agents communicate via event bus (pub/sub)
4. **Self-learning** - System evolves by analyzing trade performance
5. **Risk-first** - Every trade passes through 6-gate risk validation
6. **Fully automated** - From pre-market to EOD, everything runs autonomously

The system learns from every trade, adjusts strategy weights, and improves over time while maintaining strict risk controls.