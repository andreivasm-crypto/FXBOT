# EXECUTION PLAN: FOREX SMC + CRYPTO (SEPARATE TRACKS)

**Status:** Planning phase
**Date:** February 2, 2026
**Goal:** Build TWO distinct trading systems (not one hybrid)

---

## CRITICAL DISTINCTION

### FOREX SMC (Smart Money Concepts)
- **Market:** Forex pairs (EUR/USD, GBP/USD, etc.)
- **Mechanics:** Institutional order flow, liquidity zones, sweep patterns
- **SMC Signals:** Fair Value Gaps, order blocks, breaker blocks, liquidity sweeps
- **Timeframe:** 4H/Daily bias (SMC works best on higher TF)
- **Volume:** Not applicable (forex tick-based)
- **Psychology:** Institutional smart money concepts apply directly
- **Risk/Reward:** 1:3+ achievable
- **Win Rate:** 35-40% normal (high RR = profitable)

### CRYPTO (Altcoins/Tokens)
- **Market:** 24/7 spot + perpetual futures on Binance, Bybit, Kraken
- **Mechanics:** Retail-driven, sentiment, hype cycles, flash crashes
- **Signals:** Momentum, volume cycles, support/resistance, MA crossovers
- **Timeframe:** 1H/4H (quicker moves, more noise)
- **Volume:** CRITICAL (whale accumulation/distribution visible)
- **Psychology:** Retail FOMO, pump&dumps, whale games
- **Risk/Reward:** 1:2 more realistic (more volatile)
- **Win Rate:** 45-50% achievable (lower RR, different approach)

**Decision:** Build separate strategies, don't force SMC onto crypto.

---

## TRACK 1: FOREX SMC SYSTEM (PRIMARY FOCUS)

### Phase 1: Foundation (Week 1-2)

**1.1 Backtester Setup**
- [ ] Clone TonyMa1/walk-forward-backtester (clean WFO framework)
- [ ] Set up data pipeline for forex pairs (EUR/USD, GBP/USD, AUD/USD minimum)
- [ ] Data source: IB (Interactive Brokers) historical data or Yahoo Finance (free)
- [ ] Implement DSR calculation post-optimization
- [ ] Build parameter sensitivity testing

**1.2 SMC Indicator Library**
- [ ] Implement FVG (Fair Value Gap) detection
- [ ] Implement Order Block identification
- [ ] Implement Liquidity sweep detection
- [ ] Implement Higher Timeframe structure tracking
- [ ] Create confluence scoring (multi-signal validation)

**1.3 Risk Management**
- [ ] Position sizing: 1-2% risk per trade
- [ ] Stop loss placement (below breaker block or recent swing)
- [ ] Profit taking levels (1:1, 1:2, 1:3)
- [ ] Max drawdown monitoring (20% hard limit)

### Phase 2: Strategy Development (Week 3-4)

**2.1 SMC Entry Rules**
- [ ] Identify valid FVG (size, proximity to entry)
- [ ] Order block confirmation (supply/demand confluence)
- [ ] Liquidity sweep confirmation (recent high/low break)
- [ ] Entry trigger: Price action re-entry into mitigated level
- [ ] Document exact checklist (no ambiguity)

**2.2 First Backtest**
- [ ] Run walk-forward on EUR/USD 4H (6 months historical)
- [ ] Calculate DSR (target > 0.90)
- [ ] Check parameter stability (±10% tolerance)
- [ ] Document results: win rate, avg RR, profit factor
- [ ] Identify overfitting signals

**2.3 Manual Testing (TradingView Replay)**
- [ ] Execute 20-30 manual trades on EUR/USD 1H
- [ ] Track entry/exit precise (screenshot proof)
- [ ] Calculate actual win rate vs backtest
- [ ] Refine rules based on real price action

### Phase 3: Validation (Week 5-6)

**3.1 Multi-Pair Testing**
- [ ] Run same strategy on: GBP/USD, AUD/USD, USD/JPY
- [ ] Verify edge holds across pairs (not pair-specific)
- [ ] Calculate composite DSR across all pairs
- [ ] Check for regime sensitivity (trend vs range)

**3.2 Stress Testing**
- [ ] Test through crisis periods (2020 COVID, 2008 equivalent)
- [ ] Test through range-bound markets
- [ ] Test through low-liquidity periods (weekends, holidays)
- [ ] Document failure modes

**3.3 Parameter Stability**
- [ ] Change FVG size ±10% → does strategy still work?
- [ ] Change order block lookback ±10% → still profitable?
- [ ] Change stop loss distance ±10% → still within risk limits?
- [ ] If unstable → strategy is brittle, not real edge

### Phase 4: Production Ready (Week 7-8)

**4.1 Paper Trading**
- [ ] Open demo account (Interactive Brokers or similar)
- [ ] Execute signals from backtester live (but not real money)
- [ ] Track every trade: entry reason, exit reason, actual outcome
- [ ] Duration: 4 weeks minimum
- [ ] Target: 50+ trades to validate in live conditions

**4.2 Risk System**
- [ ] Automated stop loss placement
- [ ] Position sizing calculation
- [ ] Drawdown monitoring + alerts
- [ ] Daily/weekly P&L tracking

**4.3 Go/No-Go Decision**
- [ ] If paper trading > backtest → live (small capital)
- [ ] If paper trading < backtest → refine rules (back to 2.1)
- [ ] If paper trading = backtest ± 5% → live (confidence high)

---

## TRACK 2: CRYPTO SYSTEM (SECONDARY, PARALLEL)

### Phase 1: Research & Planning (Week 3-4, parallel to forex 2.1-2.2)

**1.1 Market Research**
- [ ] Identify best altcoins for trading (liquidity > $100M)
- [ ] Study volume patterns (pump cycles, whale accumulation)
- [ ] Identify key support/resistance zones
- [ ] Map seasonal patterns (bull run vs bear)

**1.2 Strategy Design**
- [ ] NOT SMC (different market)
- [ ] Focus: Momentum + Volume + Support/Resistance
- [ ] Key signals: 
  - [ ] Volume spike + price break = momentum trade
  - [ ] Support holding at high volume = reversal
  - [ ] Moving average alignment = trend confirmation
- [ ] Timeframe: 1H/4H (faster moves than forex)

**1.3 Data Pipeline**
- [ ] Use freqtrade as base infrastructure
- [ ] Or: Build custom crypto backtester (CCXT + pandas)
- [ ] Data source: Binance API (free historical data)
- [ ] Storage: SQLite or CSV

### Phase 2: Backtesting (Week 5-6)

**2.1 Strategy Implementation**
- [ ] Code momentum entry signals
- [ ] Code volume confirmation
- [ ] Code support/resistance exits
- [ ] Walk-forward validation

**2.2 First Backtest**
- [ ] Choose 3 altcoins (BTC, ETH, SOL)
- [ ] Run 6 months historical backtest
- [ ] Target: 45-50% win rate, 1:2 risk/reward
- [ ] Calculate Sharpe ratio

**2.3 Stress Test**
- [ ] Test through bull market (2021 data)
- [ ] Test through bear market (2022 data)
- [ ] Identify regime dependency
- [ ] Adjust for volatility changes

### Phase 3: Paper Trading (Week 7, overlap with forex paper trading)

**3.1 Live Testing**
- [ ] Small position on Binance testnet OR Bybit sandbox
- [ ] Track signals, document trades
- [ ] Duration: 2-4 weeks
- [ ] Target: 20+ trades minimum

**3.2 Risk Management**
- [ ] Position size: 2% risk per trade (higher than forex due to crypto volatility)
- [ ] Stop loss: 2-3% below entry (tighter due to noise)
- [ ] Take profit: 1:2 ratio or better

### Phase 4: Go/No-Go (Week 8)

**4.1 Decision**
- [ ] If profitable in paper → live with small capital ($500-1000)
- [ ] If unprofitable → refine strategy or pause crypto
- [ ] CRYPTO IS SECONDARY → only if solid

---

## COMPARISON: FOREX SMC vs CRYPTO

| Aspect | Forex SMC | Crypto |
|--------|-----------|--------|
| **Signal Type** | Order flow, liquidity | Volume, momentum |
| **Timeframe** | 4H/Daily | 1H/4H |
| **Win Rate Target** | 35-40% | 45-50% |
| **Risk/Reward** | 1:3+ | 1:2 |
| **Volatility** | Moderate | High |
| **24/7 Trading** | No (market hours) | Yes |
| **Leverage** | 50:1 available | 125:1 available |
| **Edge Type** | Institutional | Retail/momentum |
| **Timeline to Live** | 8 weeks | 6 weeks (if first success) |

---

## OVERALL ROADMAP (8 WEEKS)

```
Week 1-2:  FOREX foundation (backtester + SMC indicators)
Week 3-4:  FOREX strategy + manual testing + CRYPTO research starts
Week 5-6:  FOREX validation + CRYPTO backtesting
Week 7-8:  FOREX paper trading + CRYPTO paper trading
Week 8+:   Go-live decision (forex first, crypto if ready)
```

---

## SUCCESS CRITERIA

### FOREX SMC (Must Achieve Before Live)
- ✅ Walk-forward DSR > 0.90 (statistically valid)
- ✅ Manual testing 20-30 trades (similar to backtest)
- ✅ 4+ week paper trading (50+ trades minimum)
- ✅ Parameter stable ±10%
- ✅ Multi-pair validation (3+ pairs)
- ✅ Win rate 35-40%
- ✅ Max drawdown < 20%
- ✅ Profit factor > 1.5

### CRYPTO (Secondary, Only if Forex Succeeds)
- ✅ Backtest shows 45%+ win rate
- ✅ Paper trading confirms results
- ✅ Different market regime test (bull/bear)
- ✅ Position sizing appropriate for volatility
- ✅ Clear edge identified (not just lucky)

---

## What We're NOT Doing

❌ Forcing SMC onto crypto (different market)
❌ Building one hybrid system (causes confusion)
❌ Moving to crypto until forex is solid (sequential, not parallel)
❌ Overfitting either strategy (DSR + walk-forward prevents this)
❌ Trading without paper validation (must prove first)

---

## What We ARE Doing

✅ **Forex SMC:** Rigorous, institutional methodology, slow to fast
✅ **Crypto:** Separate strategy, momentum-based, only if forex works
✅ **Walk-forward on both:** Prevent overfitting
✅ **Manual + paper testing:** Validate before real money
✅ **Sequential success:** Forex first, crypto second

---

## Next Immediate Action

**Choose One:**

**Option A: Start Forex SMC Now**
- Clone TonyMa1/walk-forward-backtester
- Get EUR/USD 6 months data
- Implement FVG + order block detection
- Timeline: Start this week

**Option B: Deep Research First**
- More reading on SMC mechanics
- Study existing forex bot code
- Map exact entry/exit rules
- Timeline: Another week of research

**My recommendation: Option A.** Research is solid. Time to code + test.

---

**Decision point:** Which track do you want to start with?
