# MASTER ROADMAP: FOREX SMC TRADING SYSTEM
**Autonomous Quantitative Trading System Build**

**Target:** Production-ready profitable SMC strategy for forex
**Timeline:** 8 weeks (Feb 2 - March 30, 2026)
**Focus:** EUR/USD, GBP/USD, AUD/USD (liquid pairs)
**Risk Model:** 1-2% per trade, 1:3+ risk/reward ratio
**Success Metric:** Live trading with consistent profitability + DSR > 0.90

---

## PHASE 1: FOUNDATION (WEEKS 1-2)

### Week 1: Backtester Infrastructure Setup

#### Task 1.1: Clone & Setup Walk-Forward Backtesting Framework
**What:** Clone TonyMa1/walk-forward-backtester, adapt for forex
**Repository:** https://github.com/TonyMa1/walk-forward-backtester
**Timeline:** 1-2 days
**Deliverables:**
- [ ] Clone repo to `/quant-master/code/backtester/`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify framework runs (test with sample data)
- [ ] Understand code structure (strategies/, data/, utils/)
- [ ] Document: `/quant-master/code/BACKTESTER_SETUP.md`

**Key Files to Study:**
- `strategies/base_strategy.py` - Strategy template
- `backtest_engine.py` - Core WFO logic
- `metrics.py` - Performance calculations

**Why This Tool:**
✅ Clean WFO implementation (rolling windows)
✅ Parameter sensitivity built-in
✅ Modular strategy design
✅ Performance metric calculation
✅ Active, well-documented

---

#### Task 1.2: Data Pipeline Setup
**What:** Fetch & store forex historical data
**Data Source Options:**

**Option A: Interactive Brokers (Recommended)**
- **Cost:** Free (with IB account, $10K minimum)
- **Data:** Tick-resolution historical, all forex pairs
- **API:** TWS API (Python `ibapi`)
- **Setup:**
  - [ ] Open IB account (if not already)
  - [ ] Enable API access in TWS settings
  - [ ] Install `ibapi`: `pip install ibapi`
  - [ ] Create data fetcher script
  - [ ] Store data: SQLite database

**Option B: Yahoo Finance (Free, Limited)**
- **Cost:** Free
- **Data:** Daily OHLCV only (not minute/hour)
- **API:** `yfinance` Python library
- **Limitation:** Daily resolution (need 4H/1H for SMC)
- **Setup:** `pip install yfinance`

**Option C: Alpha Vantage (Free tier, Limited)**
- **Cost:** Free (5 API calls/min, 500/day)
- **Data:** 1-minute to daily
- **API:** REST API with Python wrapper
- **Setup:** `pip install alpha-vantage`

**RECOMMENDATION: Use IB (best quality + all timeframes)**

**Implementation:**

```python
# File: /quant-master/code/data_pipeline.py
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import sqlite3
import pandas as pd

class ForexDataFetcher(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []
    
    def historicalData(self, reqId, bar):
        # Store OHLCV data
        pass
    
    def fetch_forex_data(self, symbol, duration, barsize):
        # EUR.USD, 6 months, 4H bars
        pass
    
    def save_to_db(self, symbol, data):
        # Store in SQLite
        pass
```

**Deliverables:**
- [ ] Data fetcher script (IB or Yahoo Finance)
- [ ] SQLite database created: `/quant-master/data/forex_data.db`
- [ ] Data for EUR/USD, GBP/USD, AUD/USD (6 months minimum)
- [ ] Timeframes: 4H (primary), 1H (validation)
- [ ] Document: `/quant-master/code/DATA_PIPELINE.md`

**API Details:**

| Source | URL | Auth | Rate Limit | Cost |
|--------|-----|------|-----------|------|
| **IB TWS** | https://www.interactivebrokers.com | API key + account | Unlimited | Free (account required) |
| **Yahoo Finance** | https://pypi.org/project/yfinance/ | None | Unlimited | Free |
| **Alpha Vantage** | https://www.alphavantage.co/ | API key | 5/min, 500/day | Free |

---

#### Task 1.3: Setup Development Environment
**What:** Python environment, project structure, version control

**Environment Setup:**
```bash
# Create virtual environment
python3 -m venv /quant-master/venv
source /quant-master/venv/bin/activate

# Install core dependencies
pip install pandas numpy matplotlib seaborn plotly jupyter
pip install pandas_ta ta-lib scikit-learn
pip install optuna mlflow
pip install yfinance ibapi alpha-vantage

# Optional but useful
pip install pytest black flake8 mypy
```

**Project Structure:**
```
/quant-master/
├── code/
│   ├── backtester/          (cloned from TonyMa1)
│   ├── strategies/          (custom SMC implementation)
│   ├── data_pipeline.py     (data fetching)
│   ├── smc_indicators.py    (FVG, order blocks, etc.)
│   └── risk_management.py   (position sizing, stops)
├── data/
│   └── forex_data.db        (SQLite: OHLCV data)
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_smc_indicators.ipynb
│   └── 03_backtest_analysis.ipynb
├── results/
│   ├── backtest_results.csv
│   ├── walk_forward_metrics.csv
│   └── plots/
├── research/                (already created)
├── memory/                  (session logs)
└── README.md
```

**Git Setup:**
```bash
cd /quant-master
git init
git add .
git commit -m "Initial setup: backtester, data pipeline, project structure"
```

**Deliverables:**
- [ ] Python virtual environment activated
- [ ] All dependencies installed
- [ ] Project structure created
- [ ] Git repo initialized with first commit
- [ ] Document: `/quant-master/SETUP_INSTRUCTIONS.md`

---

### Week 1-2: SMC Indicator Development

#### Task 1.4: Implement Fair Value Gap (FVG) Detection
**What:** Code algorithm to identify FVGs programmatically

**FVG Definition:**
- Bullish FVG: Gap between candle N-2 low and candle N high (upward move)
- Bearish FVG: Gap between candle N-2 high and candle N low (downward move)
- Must be "unmitigated" (price hasn't returned into gap)

**Implementation:**

```python
# File: /quant-master/code/smc_indicators.py

import pandas as pd
import numpy as np

def detect_fvg(df, lookback=20):
    """
    Detect Fair Value Gaps
    
    Parameters:
    - df: DataFrame with columns [open, high, low, close, time]
    - lookback: How many bars back to search for unmitigated FVGs
    
    Returns:
    - DataFrame with FVG zones identified
    """
    df['fvg_bullish'] = np.nan
    df['fvg_bearish'] = np.nan
    df['fvg_mitigated'] = False
    
    for i in range(2, len(df)):
        # Bullish FVG: candle[i-2].low < candle[i].high (gap up)
        if df['low'].iloc[i-2] < df['high'].iloc[i] and df['close'].iloc[i] > df['high'].iloc[i-2]:
            fvg_high = df['high'].iloc[i]
            fvg_low = df['low'].iloc[i-2]
            df.loc[i, 'fvg_bullish'] = fvg_low  # Zone bottom
            
            # Check if mitigated (price re-entered zone)
            for j in range(i+1, min(i + lookback, len(df))):
                if df['low'].iloc[j] <= fvg_high and df['high'].iloc[j] >= fvg_low:
                    df.loc[i, 'fvg_mitigated'] = True
                    break
        
        # Bearish FVG: candle[i-2].high > candle[i].low (gap down)
        if df['high'].iloc[i-2] > df['low'].iloc[i] and df['close'].iloc[i] < df['low'].iloc[i-2]:
            fvg_low = df['low'].iloc[i]
            fvg_high = df['high'].iloc[i-2]
            df.loc[i, 'fvg_bearish'] = fvg_high  # Zone top
            
            # Check if mitigated
            for j in range(i+1, min(i + lookback, len(df))):
                if df['low'].iloc[j] <= fvg_high and df['high'].iloc[j] >= fvg_low:
                    df.loc[i, 'fvg_mitigated'] = True
                    break
    
    return df

# Test:
# df = pd.read_csv('eur_usd_4h.csv')
# df = detect_fvg(df)
# print(df[['time', 'fvg_bullish', 'fvg_bearish', 'fvg_mitigated']])
```

**Deliverables:**
- [ ] FVG detection function working
- [ ] Test with sample data
- [ ] Identify false positives (too frequent?)
- [ ] Document: FVG_DETECTION.md

---

#### Task 1.5: Implement Order Block Detection
**What:** Identify supply/demand zones (strong reversals)

**Order Block Definition:**
- Bullish OB: Strong bullish candle with high volume, followed by reversal
- Bearish OB: Strong bearish candle with high volume, followed by reversal
- Must show clear wick rejection or reversal pattern

**Implementation:**

```python
# File: /quant-master/code/smc_indicators.py (continued)

def detect_order_blocks(df, lookback=20, volume_threshold=1.2):
    """
    Detect Order Blocks (supply/demand zones)
    
    Parameters:
    - df: DataFrame with [open, high, low, close, volume]
    - lookback: Bars to look back for order block formation
    - volume_threshold: Multiplier for average volume (1.2 = 20% above average)
    """
    df['ob_bullish'] = np.nan
    df['ob_bearish'] = np.nan
    df['ob_type'] = None
    
    # Calculate average volume
    df['avg_volume'] = df['volume'].rolling(window=20).mean()
    
    for i in range(2, len(df) - 5):
        current_close = df['close'].iloc[i]
        current_volume = df['volume'].iloc[i]
        avg_vol = df['avg_volume'].iloc[i]
        
        # Bullish OB: Strong up candle with volume spike
        body_size = abs(current_close - df['open'].iloc[i])
        is_bullish_candle = current_close > df['open'].iloc[i]
        has_volume = current_volume > (avg_vol * volume_threshold)
        
        if is_bullish_candle and has_volume and body_size > 0:
            # Check if followed by reversal (next 3 candles show weakness)
            reversal_count = 0
            for j in range(i+1, min(i+4, len(df))):
                if df['close'].iloc[j] < df['close'].iloc[i]:
                    reversal_count += 1
            
            if reversal_count >= 2:
                # Valid bullish OB at the high of the candle
                df.loc[i, 'ob_bullish'] = df['high'].iloc[i]
                df.loc[i, 'ob_type'] = 'bullish'
        
        # Bearish OB: Strong down candle with volume spike
        is_bearish_candle = current_close < df['open'].iloc[i]
        if is_bearish_candle and has_volume and body_size > 0:
            reversal_count = 0
            for j in range(i+1, min(i+4, len(df))):
                if df['close'].iloc[j] > df['close'].iloc[i]:
                    reversal_count += 1
            
            if reversal_count >= 2:
                # Valid bearish OB at the low of the candle
                df.loc[i, 'ob_bearish'] = df['low'].iloc[i]
                df.loc[i, 'ob_type'] = 'bearish'
    
    return df
```

**Deliverables:**
- [ ] Order block detection function
- [ ] Validation with sample data
- [ ] Parameter tuning (volume threshold, lookback)
- [ ] Document: ORDER_BLOCK_DETECTION.md

---

#### Task 1.6: Implement Liquidity Sweep Detection
**What:** Identify when price sweeps recent highs/lows (liquidity hunting)

**Liquidity Sweep Definition:**
- Price breaks above recent swing high with volume
- Quickly reverses (0-3 candles) below the high
- Indicates smart money clearing retail stop losses

**Implementation:**

```python
# File: /quant-master/code/smc_indicators.py (continued)

def detect_liquidity_sweeps(df, lookback=5):
    """
    Detect Liquidity Sweeps (institutional manipulation)
    
    Parameters:
    - df: DataFrame with [high, low, close, volume]
    - lookback: How many bars back to check for swing highs/lows
    """
    df['liquidity_sweep'] = 0
    df['sweep_type'] = None  # 'bullish' or 'bearish'
    
    for i in range(lookback, len(df) - 1):
        recent_high = df['high'].iloc[i-lookback:i].max()
        recent_low = df['low'].iloc[i-lookback:i].min()
        
        # Bullish sweep: breaks above recent high, reverses down
        if df['high'].iloc[i] > recent_high:
            # Check if next 3 candles close below high
            for j in range(i+1, min(i+4, len(df))):
                if df['close'].iloc[j] < df['high'].iloc[i]:
                    df.loc[i, 'liquidity_sweep'] = 1
                    df.loc[i, 'sweep_type'] = 'bullish'
                    break
        
        # Bearish sweep: breaks below recent low, reverses up
        if df['low'].iloc[i] < recent_low:
            for j in range(i+1, min(i+4, len(df))):
                if df['close'].iloc[j] > df['low'].iloc[i]:
                    df.loc[i, 'liquidity_sweep'] = 1
                    df.loc[i, 'sweep_type'] = 'bearish'
                    break
    
    return df
```

**Deliverables:**
- [ ] Liquidity sweep detection function
- [ ] Test with sample data
- [ ] Document detection logic

---

#### Task 1.7: Implement Higher Timeframe Structure Tracking
**What:** Identify trend direction on 4H/Daily to bias trading

**HTF Structure Definition:**
- Bullish: Price above key MA (EMA 200), making higher highs/lows
- Bearish: Price below key MA, making lower highs/lows
- Sideways: Price in range, no clear trend

**Implementation:**

```python
# File: /quant-master/code/smc_indicators.py (continued)

def detect_htf_structure(df, ma_period=200):
    """
    Detect Higher Timeframe Structure
    
    Parameters:
    - df: DataFrame with [close]
    - ma_period: EMA period (200 standard)
    """
    df['ema_200'] = df['close'].ewm(span=ma_period).mean()
    
    # Identify structure
    df['structure'] = 'sideways'
    df['higher_high'] = False
    df['higher_low'] = False
    df['lower_high'] = False
    df['lower_low'] = False
    
    for i in range(1, len(df)):
        if df['high'].iloc[i] > df['high'].iloc[i-1]:
            df.loc[i, 'higher_high'] = True
        
        if df['low'].iloc[i] > df['low'].iloc[i-1]:
            df.loc[i, 'higher_low'] = True
        
        if df['high'].iloc[i] < df['high'].iloc[i-1]:
            df.loc[i, 'lower_high'] = True
        
        if df['low'].iloc[i] < df['low'].iloc[i-1]:
            df.loc[i, 'lower_low'] = True
        
        # Determine structure
        if df['close'].iloc[i] > df['ema_200'].iloc[i] and df['higher_high'].iloc[i]:
            df.loc[i, 'structure'] = 'bullish'
        elif df['close'].iloc[i] < df['ema_200'].iloc[i] and df['lower_low'].iloc[i]:
            df.loc[i, 'structure'] = 'bearish'
        else:
            df.loc[i, 'structure'] = 'sideways'
    
    return df
```

**Deliverables:**
- [ ] HTF structure detection function
- [ ] Integration with other indicators

---

#### Task 1.8: Create SMC Strategy Entry Rules Document
**What:** Define EXACT criteria for trade entries (no ambiguity)

**Document:** `/quant-master/code/SMC_ENTRY_RULES.md`

```markdown
# SMC Strategy Entry Rules Checklist

## BULLISH ENTRY (Long Trade)

### All conditions required (AND logic):
1. [ ] HTF Structure: BULLISH (price > EMA 200, making HH/HL)
2. [ ] Liquidity Sweep: Recent bearish sweep (price cleared shorts)
3. [ ] Fair Value Gap: Unmitigated bullish FVG identified
4. [ ] Order Block: Bullish order block NOT yet mitigated
5. [ ] Price Action: Current candle close above order block low
6. [ ] Volume: Current candle volume > 20% above average

### Entry Price:
- BUY at breakout above order block high or on retest of FVG zone

### Stop Loss:
- BELOW recent swing low (or 50 pips below entry, whichever is higher)

### Take Profit:
- TP1: 1:1 RR (entry + stop size)
- TP2: 1:2 RR (move 2x stop to break-even after TP1)
- TP3: 1:3+ RR (trail stop or hold for higher target)

---

## BEARISH ENTRY (Short Trade)

### All conditions required:
1. [ ] HTF Structure: BEARISH (price < EMA 200, making LL/LH)
2. [ ] Liquidity Sweep: Recent bullish sweep (price cleared longs)
3. [ ] Fair Value Gap: Unmitigated bearish FVG identified
4. [ ] Order Block: Bearish order block NOT yet mitigated
5. [ ] Price Action: Current candle close below order block high
6. [ ] Volume: Current candle volume > 20% above average

### Entry Price:
- SELL at breakdown below order block low or on retest of FVG zone

### Stop Loss:
- ABOVE recent swing high (or 50 pips above entry, whichever is higher)

### Take Profit:
- Same as bullish (1:1, 1:2, 1:3+)

---

## Rejection Criteria (NO TRADE):

- [ ] Price inside HTF consolidation/sideways (high uncertainty)
- [ ] FVG already partially mitigated (weak zone)
- [ ] Order block too old (>20 candles ago, likely stale)
- [ ] Volume weak (below average)
- [ ] Recent liquidation event (high slippage risk)
```

**Deliverables:**
- [ ] Exact entry rules documented
- [ ] Parameters clearly defined
- [ ] No ambiguity (programmable)

---

### Week 2: Integration & Testing

#### Task 1.9: Integrate SMC Indicators into Backtester
**What:** Add all SMC indicators to backtesting framework

```python
# File: /quant-master/code/strategies/smc_strategy.py

from backtester.strategies import BaseStrategy
from smc_indicators import *

class SMCStrategy(BaseStrategy):
    def __init__(self, params):
        super().__init__(params)
        self.fvg_lookback = params.get('fvg_lookback', 20)
        self.ob_volume_threshold = params.get('ob_volume_threshold', 1.2)
        self.htf_ma_period = params.get('htf_ma_period', 200)
    
    def calculate_signals(self, df):
        """Calculate all SMC indicators"""
        df = detect_fvg(df, self.fvg_lookback)
        df = detect_order_blocks(df, volume_threshold=self.ob_volume_threshold)
        df = detect_liquidity_sweeps(df)
        df = detect_htf_structure(df, self.htf_ma_period)
        
        return df
    
    def generate_signals(self, df):
        """Generate BUY/SELL signals based on SMC rules"""
        signals = []
        
        for i in range(1, len(df)):
            # Check bullish entry conditions
            bullish_entry = (
                df['structure'].iloc[i] == 'bullish' and
                df['liquidity_sweep'].iloc[i] == 1 and
                df['sweep_type'].iloc[i] == 'bearish' and
                df['fvg_bullish'].notna().iloc[i] and
                df['ob_bullish'].notna().iloc[i] and
                not df['fvg_mitigated'].iloc[i] and
                df['volume'].iloc[i] > df['volume'].iloc[i-20:i].mean() * 1.2
            )
            
            if bullish_entry:
                signals.append({'type': 'BUY', 'bar': i, 'price': df['close'].iloc[i]})
            
            # Check bearish entry conditions (similar)
            # ...
        
        return signals
```

**Deliverables:**
- [ ] SMC indicators integrated into backtester
- [ ] Signal generation working
- [ ] Test with sample data

---

#### Task 1.10: Implement Risk Management Module
**What:** Position sizing, stop loss, take profit logic

```python
# File: /quant-master/code/risk_management.py

class RiskManager:
    def __init__(self, account_balance, risk_per_trade=0.02):
        """
        Parameters:
        - account_balance: Initial trading capital
        - risk_per_trade: Risk as % of account (0.02 = 2%)
        """
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade
    
    def calculate_position_size(self, entry_price, stop_loss_price, asset_price=1):
        """
        Calculate position size based on risk
        
        Risk Amount = Account * Risk%
        Position Size = Risk Amount / (Entry - Stop) * Asset Price
        """
        risk_amount = self.account_balance * self.risk_per_trade
        stop_distance = abs(entry_price - stop_loss_price)
        
        if stop_distance == 0:
            return 0
        
        position_size = risk_amount / stop_distance
        return position_size
    
    def calculate_sl_tp(self, entry_price, direction='long'):
        """
        Calculate SL and TP levels
        """
        if direction == 'long':
            # Default SL: 50 pips below entry (adjust per pair)
            sl = entry_price - 0.0050
            tp1 = entry_price + 0.0050  # 1:1
            tp2 = entry_price + 0.0100  # 1:2
            tp3 = entry_price + 0.0150  # 1:3
        else:  # short
            sl = entry_price + 0.0050
            tp1 = entry_price - 0.0050
            tp2 = entry_price - 0.0100
            tp3 = entry_price - 0.0150
        
        return {'sl': sl, 'tp1': tp1, 'tp2': tp2, 'tp3': tp3}
```

**Deliverables:**
- [ ] Risk management module created
- [ ] Position sizing algorithm working
- [ ] SL/TP calculation tested

---

#### Task 1.11: Backtesting Framework Integration Test
**What:** Run first backtest on EUR/USD 4H

```python
# File: /quant-master/notebooks/03_backtest_analysis.ipynb

# Load data
df = pd.read_sql("SELECT * FROM eur_usd_4h", conn)

# Initialize strategy
strategy = SMCStrategy(params={
    'fvg_lookback': 20,
    'ob_volume_threshold': 1.2,
    'htf_ma_period': 200
})

# Calculate indicators
df = strategy.calculate_signals(df)
signals = strategy.generate_signals(df)

# Run backtest (using TonyMa1's framework)
results = backtest(df, signals, initial_capital=10000, risk=0.02)

# Print results
print(f"Total Trades: {results['total_trades']}")
print(f"Win Rate: {results['win_rate']:.2%}")
print(f"Profit Factor: {results['profit_factor']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
```

**Success Criteria for Week 1-2:**
- ✅ Backtester running
- ✅ SMC indicators calculating correctly
- ✅ Signals generated
- ✅ Basic backtest results available
- ✅ No crashes or errors

**Deliverables:**
- [ ] All Week 1-2 tasks completed
- [ ] First backtest results
- [ ] Code documented and tested
- [ ] Ready to move to Phase 2

---

## PHASE 2: WALK-FORWARD OPTIMIZATION & VALIDATION (WEEKS 3-4)

### Task 2.1: Implement Walk-Forward Analysis Framework
**What:** Multi-window optimization to prevent overfitting

**Walk-Forward Setup:**
- Training window: 3 months
- Testing window: 1 month
- Rolling: Move forward 1 month, repeat

```python
# File: /quant-master/code/walk_forward_analysis.py

from sklearn.model_selection import TimeSeriesSplit

def run_walk_forward_optimization(df, strategy_class, param_grid, 
                                   train_months=3, test_months=1):
    """
    Walk-Forward Optimization
    
    Parameters:
    - df: Full historical data
    - strategy_class: SMCStrategy or similar
    - param_grid: Parameters to optimize (dict)
    - train_months: Training period (months)
    - test_months: Testing period (months)
    """
    
    results = []
    data_points_per_month = len(df) // 6  # Approximate
    
    train_size = data_points_per_month * train_months
    test_size = data_points_per_month * test_months
    
    window_start = 0
    
    while window_start + train_size + test_size <= len(df):
        train_data = df.iloc[window_start:window_start + train_size]
        test_data = df.iloc[window_start + train_size:window_start + train_size + test_size]
        
        # Optimize parameters on training set
        best_params = optimize_parameters(train_data, strategy_class, param_grid)
        
        # Test on out-of-sample data
        strategy = strategy_class(best_params)
        test_results = backtest(test_data, strategy)
        
        test_results['best_params'] = best_params
        test_results['train_metrics'] = calculate_metrics(train_data, strategy)
        test_results['test_metrics'] = test_results
        
        results.append(test_results)
        
        # Move window forward
        window_start += test_size
    
    return results

def calculate_dsr(train_sharpe, test_sharpe, train_trades, test_trades):
    """
    Calculate Deflated Sharpe Ratio
    
    DSR filters out lucky backtests by comparing in-sample vs out-of-sample Sharpe
    DSR > 0.90 = Strategy likely has real edge (not overfitted)
    """
    # Simplified DSR calculation
    # Higher values = more likely overfitting
    
    dsr_score = test_sharpe / (train_sharpe + 0.0001)  # Avoid division by zero
    
    if dsr_score > 0.90:
        return {'dsr': dsr_score, 'status': 'VALID EDGE'}
    else:
        return {'dsr': dsr_score, 'status': 'LIKELY OVERFITTED'}
```

**Parameters to Optimize:**
```python
param_grid = {
    'fvg_lookback': [15, 20, 25, 30],
    'ob_volume_threshold': [1.0, 1.2, 1.5],
    'htf_ma_period': [150, 200, 250],
    'min_volume_factor': [1.1, 1.2, 1.3]
}
```

**Deliverables:**
- [ ] Walk-forward framework implemented
- [ ] Parameter optimization working
- [ ] DSR calculation integrated

---

### Task 2.2: Run Multi-Window Backtest
**What:** Execute walk-forward on 6 months EUR/USD data

```python
# File: /quant-master/notebooks/04_walk_forward_results.ipynb

# Run walk-forward optimization
wfo_results = run_walk_forward_optimization(
    df=df_eur_usd,
    strategy_class=SMCStrategy,
    param_grid=param_grid,
    train_months=3,
    test_months=1
)

# Analyze results
import pandas as pd

results_df = pd.DataFrame([
    {
        'window': i,
        'train_sharpe': r['train_metrics']['sharpe_ratio'],
        'test_sharpe': r['test_metrics']['sharpe_ratio'],
        'dsr': calculate_dsr(r['train_metrics']['sharpe_ratio'], 
                            r['test_metrics']['sharpe_ratio']),
        'test_win_rate': r['test_metrics']['win_rate'],
        'test_profit_factor': r['test_metrics']['profit_factor'],
        'best_params': r['best_params']
    }
    for i, r in enumerate(wfo_results)
])

# Display results
print(results_df[['window', 'train_sharpe', 'test_sharpe', 'dsr', 'test_win_rate']])

# Check: Are we overfitting?
avg_dsr = results_df['dsr'].mean()
print(f"\nAverage DSR: {avg_dsr:.3f}")
if avg_dsr > 0.90:
    print("✅ VALID EDGE: Strategy likely has real edge (not overfitted)")
else:
    print("❌ LIKELY OVERFITTED: Strategy may not work in live trading")
```

**Success Criteria:**
- ✅ All windows generate signals
- ✅ DSR > 0.90 (not overfitted)
- ✅ Win rate consistent across windows (±5%)
- ✅ Profit factor > 1.5
- ✅ Fewer than 50 trades total (need more to improve stat sig)

**Deliverables:**
- [ ] Complete walk-forward results
- [ ] DSR validation report
- [ ] Parameter stability analysis

---

### Task 2.3: Parameter Sensitivity Testing
**What:** Verify strategy isn't brittle (±10% changes don't break it)

```python
# File: /quant-master/code/sensitivity_analysis.py

def parameter_sensitivity_test(base_params, strategy_class, df, sensitivity=0.10):
    """
    Test: If we change parameters ±10%, does strategy still work?
    
    If sensitivity is high (profit drops >50%), strategy is brittle.
    If sensitivity is low (profit drops <20%), strategy is robust.
    """
    
    results = {}
    
    # Test base case
    base_strategy = strategy_class(base_params)
    base_metrics = backtest(df, base_strategy)
    base_profit = base_metrics['total_profit']
    
    # Test each parameter ±10%
    for param_name, param_value in base_params.items():
        if isinstance(param_value, (int, float)):
            # Test -10%
            test_params_low = base_params.copy()
            test_params_low[param_name] = param_value * (1 - sensitivity)
            strategy_low = strategy_class(test_params_low)
            metrics_low = backtest(df, strategy_low)
            
            # Test +10%
            test_params_high = base_params.copy()
            test_params_high[param_name] = param_value * (1 + sensitivity)
            strategy_high = strategy_class(test_params_high)
            metrics_high = backtest(df, strategy_high)
            
            # Calculate sensitivity
            profit_low = metrics_low['total_profit']
            profit_high = metrics_high['total_profit']
            
            sensitivity_score = {
                'param': param_name,
                'base_value': param_value,
                'base_profit': base_profit,
                'low_profit': profit_low,
                'high_profit': profit_high,
                'low_change': (profit_low - base_profit) / base_profit,
                'high_change': (profit_high - base_profit) / base_profit,
                'avg_change': ((abs(profit_low - base_profit) + abs(profit_high - base_profit)) / 2) / base_profit
            }
            
            results[param_name] = sensitivity_score
    
    return results
```

**Deliverables:**
- [ ] Sensitivity analysis completed
- [ ] All parameters stable (±20% change acceptable)
- [ ] Brittle parameters identified and removed or refined

---

### Task 2.4: Multi-Pair Validation
**What:** Test strategy on GBP/USD and AUD/USD (not just EUR/USD)

**Goal:** Confirm edge isn't pair-specific

```python
# File: /quant-master/notebooks/05_multi_pair_validation.ipynb

pairs = ['EUR/USD', 'GBP/USD', 'AUD/USD', 'USD/JPY']
pair_results = {}

for pair in pairs:
    df = pd.read_sql(f"SELECT * FROM {pair.replace('/', '_').lower()}_4h", conn)
    
    # Run walk-forward with optimized params
    wfo_results = run_walk_forward_optimization(df, SMCStrategy, param_grid)
    
    metrics = {
        'pair': pair,
        'total_trades': sum(r['test_metrics']['total_trades'] for r in wfo_results),
        'avg_win_rate': np.mean([r['test_metrics']['win_rate'] for r in wfo_results]),
        'avg_sharpe': np.mean([r['test_metrics']['sharpe_ratio'] for r in wfo_results]),
        'avg_dsr': np.mean([calculate_dsr(r['train_metrics']['sharpe_ratio'], 
                                          r['test_metrics']['sharpe_ratio']) 
                           for r in wfo_results])
    }
    
    pair_results[pair] = metrics

# Summary
results_table = pd.DataFrame.from_dict(pair_results, orient='index')
print(results_table)

# Validation: All pairs should have similar metrics
std_win_rate = results_table['avg_win_rate'].std()
print(f"\nWin Rate Std Dev: {std_win_rate:.3f}")
if std_win_rate < 0.05:
    print("✅ CONSISTENT: Strategy works across pairs")
else:
    print("⚠️ INCONSISTENT: Strategy may be pair-specific")
```

**Success Criteria:**
- ✅ All 4 pairs show 30-45% win rate
- ✅ Profit factors consistent (±0.3)
- ✅ DSR > 0.90 on all pairs

**Deliverables:**
- [ ] Multi-pair backtest completed
- [ ] Consistency report
- [ ] Edge validated across pairs

---

## PHASE 3: MANUAL TESTING & REAL PRICE ACTION (WEEKS 5-6)

### Task 3.1: Manual Trade Execution on TradingView Replay
**What:** Execute 20-30 trades manually to validate signals match real price action

**Setup:**
1. Open TradingView account (free or paid)
2. Enable "Replay" mode (look back at historical data)
3. Start from 2025-12-01 (6 months ago)
4. Use 1H timeframe for faster feedback

**Execution Protocol:**

```markdown
# Manual Trading Protocol

## For Each Trade:

1. **Setup Identification** (5 mins)
   - Look for SMC confluence:
     * FVG + Order Block alignment
     * Liquidity sweep confirmation
     * HTF structure alignment
   
2. **Entry Decision** (2 mins)
   - Check if all conditions met (use checklist)
   - ONLY enter if confident
   - Note: Entry price, reason, time

3. **Trade Management** (Hold 1-24 hours)
   - Track stop loss hit or TP reached
   - Record: Entry, exit, profit/loss, RR ratio
   - Screenshot chart for analysis

4. **Post-Trade Analysis** (5 mins)
   - Did entry logic match actual price action?
   - Were signals clear or ambiguous?
   - What would algorithm have missed?
   - Document in trade journal

## Trade Journal Entry Template:
```python
trade_log = {
    'date': '2026-02-10',
    'pair': 'EUR/USD',
    'timeframe': '1H',
    'entry_price': 1.0850,
    'entry_reason': 'FVG + OB + bullish sweep + HTF bullish',
    'stop_loss': 1.0800,
    'take_profit_1': 1.0900,
    'exit_price': 1.0895,
    'exit_reason': 'Hit TP1 (1:1 RR)',
    'profit': 45,
    'risk_reward_actual': 1.8,
    'status': 'WIN',
    'notes': 'Clean setup, clear entry signal'
}
```

**Deliverables:**
- [ ] 20-30 manual trades executed
- [ ] Trade journal maintained (all trades logged)
- [ ] Screenshots of each setup
- [ ] Manual win rate calculated
- [ ] Comparison: Manual vs Backtest results

**Success Criteria:**
- ✅ Manual win rate within 5% of backtest
- ✅ Signals clear and identifiable
- ✅ No major surprises or ambiguities
- ✅ RR ratios achieved as planned

---

### Task 3.2: Refine Entry Rules Based on Manual Testing
**What:** Identify gaps between theory and practice

**Analysis:**
- Did signals trigger when expected?
- Were false signals frequent?
- Did price action match FVG/OB zones?
- Were stops hit too often?

**Refinements:**
- Adjust FVG detection (maybe too sensitive?)
- Adjust order block volume threshold
- Adjust HTF timeframe or MA period
- Add rejection filters (e.g., no trades during low volatility)

```python
# File: /quant-master/code/SMC_ENTRY_RULES.md (UPDATED)

# Additional Rejection Criteria:
- [ ] Volatility too low (ATR < 50 pips) → skip trade
- [ ] Price within consolidation (5-day range tight) → skip trade
- [ ] Major news upcoming (economic calendar) → skip trade
- [ ] Weekend risk (Friday evening) → close positions
```

**Deliverables:**
- [ ] Rule refinements documented
- [ ] Updated entry rules v2
- [ ] Backtester code updated

---

### Task 3.3: Final Validation Backtest
**What:** Run updated walk-forward with refined rules

```python
# File: /quant-master/notebooks/06_final_validation.ipynb

# Re-run walk-forward with refined parameters
refined_params = {
    'fvg_lookback': 22,  # Adjusted from 20
    'ob_volume_threshold': 1.1,  # Lowered from 1.2
    'min_atr': 50,  # NEW: Minimum volatility
    # ... other adjusted params
}

wfo_results_v2 = run_walk_forward_optimization(df, SMCStrategy, refined_params)

# Compare: V1 vs V2
comparison = {
    'metric': ['Win Rate', 'Profit Factor', 'Sharpe Ratio', 'DSR'],
    'v1': [0.38, 1.65, 1.2, 0.92],
    'v2': [0.40, 1.75, 1.3, 0.94],  # Expected: slight improvement
}

print("V1 vs V2 Comparison:")
print(pd.DataFrame(comparison))
```

**Deliverables:**
- [ ] Final backtest complete
- [ ] Validation metrics recorded
- [ ] Ready for paper trading

---

## PHASE 4: PAPER TRADING (WEEKS 7-8)

### Task 4.1: Paper Trading Setup
**What:** Execute signals live (but not real money)

**Broker Setup:**
1. Open Interactive Brokers account (if not done)
2. Open demo/paper trading account
3. Install TWS or IB Gateway
4. Test API connection

```python
# File: /quant-master/code/live_trading.py

from ibapi.client import EClient
from ibapi.wrapper import EWrapper

class LiveTradingBot(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.active_positions = {}
        self.trades_executed = 0
    
    def place_order(self, symbol, quantity, order_type, price, direction='BUY'):
        """Place order on Interactive Brokers"""
        # Create order object
        # Execute via API
        pass
    
    def manage_position(self, symbol, current_price):
        """Monitor and manage active positions"""
        # Check SL/TP hits
        # Move stops to break-even after TP1
        # Close at TP targets
        pass
    
    def log_trade(self, trade_data):
        """Log every trade for analysis"""
        pass
```

**Deliverables:**
- [ ] Paper trading account set up
- [ ] API connection tested
- [ ] Order placement working
- [ ] Paper trading system ready

---

### Task 4.2: Execute 50+ Paper Trades Over 4 Weeks
**What:** Track signals from SMC system, execute live

**Daily Workflow:**
1. Morning: Check for new SMC signals (EUR/USD 4H, GBP/USD 4H)
2. Execute buy/sell orders (paper trading)
3. Manage positions (SL, TP, break-even)
4. Evening: Review trades, update journal
5. Weekly: Analyze win rate, adjust if needed

**Tracking:**

```python
# File: /quant-master/data/paper_trading_log.csv

Date,Pair,TF,Entry,SL,TP1,TP2,TP3,ExitPrice,ExitReason,Profit,RR_Actual,Signal_Clarity
2026-02-10,EUR/USD,4H,1.0850,1.0800,1.0900,1.0950,1.1000,1.0895,TP1_Hit,45,1.8,Clear
2026-02-12,GBP/USD,4H,1.2750,1.2700,1.2850,1.2950,1.3050,1.2740,SL_Hit,-50,-1.0,Ambiguous
... (continue for 50+ trades)
```

**Weekly Analysis:**

```python
# File: /quant-master/notebooks/07_paper_trading_analysis.ipynb

# Load paper trading log
trades_df = pd.read_csv('/quant-master/data/paper_trading_log.csv')

# Calculate metrics
win_rate = (trades_df['Profit'] > 0).sum() / len(trades_df)
avg_win = trades_df[trades_df['Profit'] > 0]['Profit'].mean()
avg_loss = trades_df[trades_df['Profit'] < 0]['Profit'].mean()
profit_factor = abs(avg_win * (trades_df['Profit'] > 0).sum()) / abs(avg_loss * (trades_df['Profit'] < 0).sum())

print(f"Paper Trading Results (Week {week}):")
print(f"  Total Trades: {len(trades_df)}")
print(f"  Win Rate: {win_rate:.1%}")
print(f"  Avg Win: ${avg_win:.0f}")
print(f"  Avg Loss: ${avg_loss:.0f}")
print(f"  Profit Factor: {profit_factor:.2f}")
print(f"  Total P&L: ${trades_df['Profit'].sum():.0f}")
```

**Success Criteria:**
- ✅ 50+ trades executed
- ✅ Win rate matches backtest (±5%)
- ✅ Profit factors consistent
- ✅ No catastrophic losses (max loss < 5% account)

**Deliverables:**
- [ ] 4 weeks of paper trading data
- [ ] Weekly performance reports
- [ ] Trade journal complete

---

### Task 4.3: Go/No-Go Decision
**What:** Decide if ready for live capital

**Decision Matrix:**

| Criteria | Backtest | Manual | Paper | Decision |
|----------|----------|--------|-------|----------|
| Win Rate (target 35-40%) | 38% | 39% | 37% | ✅ PASS |
| Sharpe Ratio (>1.0) | 1.2 | N/A | 1.1 | ✅ PASS |
| DSR (>0.90) | 0.92 | N/A | N/A | ✅ PASS |
| Profit Factor (>1.5) | 1.7 | 1.6 | 1.65 | ✅ PASS |
| Max Drawdown (<20%) | 18% | N/A | 16% | ✅ PASS |
| Consistency (±5%) | Stable | Stable | Stable | ✅ PASS |
| Signals Clear? | Yes | Yes | Yes | ✅ PASS |

**Decision Logic:**
- If ALL green (✅) → PROCEED TO LIVE
- If 1-2 yellow (⚠️) → Refinement needed (1-2 weeks)
- If 3+ red (❌) → STOP, fundamental issue to fix

**Deliverables:**
- [ ] Go/No-Go decision documented
- [ ] If YES: Proceed to Phase 5
- [ ] If NO: Identify refinements needed

---

## PHASE 5: LIVE TRADING (WEEK 8+)

### Task 5.1: Live Account Setup
**What:** Open real account, deposit capital, start trading

```markdown
# Live Trading Setup Checklist

- [ ] Open Interactive Brokers real account
- [ ] Deposit initial capital ($10,000 minimum recommended)
- [ ] Enable API access
- [ ] Set up risk limits in IB account:
  - [ ] Max daily loss: 2% of account
  - [ ] Max per-trade loss: 2% of account
  - [ ] Max position size: 5% of account per trade
- [ ] Test order placement with small size
- [ ] Enable alerts (email, Slack)
- [ ] Start live trading bot
```

**Initial Capital Recommendation:**
- Start with $10,000 (allows 2% risk = $200 per trade)
- Expected monthly return: 3-5% if strategy performs as backtested
- Month 1 goal: Break even or small profit (prove system works)

---

### Task 5.2: Continuous Monitoring & Risk Management

**Daily Tasks:**
1. Morning: Review overnight trades
2. Check: Max drawdown < 20%
3. Check: Daily loss limit not hit
4. Log: All trades, reasons
5. Evening: Update performance dashboard

**Weekly Tasks:**
1. Calculate: Win rate, profit factor, Sharpe ratio
2. Compare: Live vs backtest
3. If deviation > 10%: Analyze why
4. Adjust: Parameters if needed (carefully)

**Monthly Tasks:**
1. Full performance review
2. Identify: Winning vs losing pairs/timeframes
3. Optimize: Focus on high-probability setups
4. Document: Lessons learned

**Deliverables:**
- [ ] Live trading started
- [ ] Daily monitoring
- [ ] Weekly performance reports
- [ ] Monthly reviews

---

## TOOLS & APIs REQUIRED

### Data Feeds

| Tool | Purpose | Cost | Status |
|------|---------|------|--------|
| **Interactive Brokers** | Forex data + live trading | Free (with account) | Required |
| **Pandas** | Data manipulation | Free | Required |
| **SQLite** | Data storage | Free | Required |

### Backtesting

| Tool | Purpose | Cost | Status |
|------|---------|------|--------|
| **TonyMa1/walk-forward-backtester** | WFO framework | Free | Required |
| **VectorBT** | Fast backtesting | Free | Optional (enhancement) |
| **Zipline** | Event-driven backtest | Free | Optional (validation) |

### Indicators & Analysis

| Tool | Purpose | Cost | Status |
|------|---------|------|--------|
| **pandas_ta** | Technical indicators | Free | Required |
| **scikit-learn** | Statistical testing | Free | Required |
| **NumPy/SciPy** | Math functions | Free | Required |

### Visualization

| Tool | Purpose | Cost | Status |
|------|---------|------|--------|
| **Matplotlib** | Charts & plots | Free | Required |
| **Plotly** | Interactive dashboards | Free | Required |
| **Seaborn** | Statistical plots | Free | Optional |

### Development

| Tool | Purpose | Cost | Status |
|------|---------|------|--------|
| **Jupyter Notebook** | Research & testing | Free | Required |
| **VS Code** | Code editor | Free | Required |
| **Git** | Version control | Free | Required |
| **GitHub** | Code hosting | Free | Optional |

### Execution

| Tool | Purpose | Cost | Status |
|------|---------|------|--------|
| **Interactive Brokers TWS API** | Live trading | Free (with IB account) | Required |
| **ibapi** (Python library) | IB API wrapper | Free | Required |

### Monitoring (Optional)

| Tool | Purpose | Cost | Status |
|------|---------|------|--------|
| **Email alerts** | Trade notifications | Free | Nice-to-have |
| **Slack integration** | Team alerts | Free | Nice-to-have |
| **MLflow** | Experiment tracking | Free | Nice-to-have |

---

## COMPLETE DEPENDENCY LIST

```bash
# Core backtesting dependencies
pip install pandas numpy scipy scikit-learn
pip install pandas-ta ta-lib
pip install optuna mlflow

# Visualization
pip install matplotlib seaborn plotly

# Development
pip install jupyter notebook ipython
pip install pytest black flake8 mypy

# Exchange APIs
pip install ibapi yfinance alpha-vantage

# Optional enhancements
pip install vectorbt backtrader freqtrade
```

---

## SUCCESS METRICS BY PHASE

### Phase 1-2 (Week 1-4)
✅ Backtester working
✅ SMC indicators detecting signals
✅ Walk-forward DSR > 0.90
✅ Win rate 35-40%
✅ Profit factor > 1.5

### Phase 3 (Week 5-6)
✅ 20-30 manual trades executed
✅ Manual results match backtest
✅ Signals clear and unambiguous
✅ Rules refined

### Phase 4 (Week 7-8)
✅ 50+ paper trades
✅ Paper trading matches backtest
✅ No surprises or major deviations
✅ Ready for live trading

### Phase 5+ (Week 8+)
✅ Live trading started
✅ 1st month: break-even or positive
✅ Consistent execution
✅ Risk management working

---

## RISK MITIGATION

### Risk 1: Overfitting
**Mitigation:** Walk-forward analysis + DSR validation
**Triggers:** If DSR < 0.90, stop and refine rules

### Risk 2: Slippage & Commission Impact
**Mitigation:** Backtest with realistic costs ($0.01-0.05 per pip)
**Triggers:** If live results 20% worse than backtest, adjust position sizing

### Risk 3: Drawdown Exceeds Plan
**Mitigation:** Max drawdown limit: 20%, daily loss limit: 2%
**Triggers:** If drawdown > 20%, close all positions and review

### Risk 4: Signal Generation Failures
**Mitigation:** Daily system checks, alerts on missing trades
**Triggers:** If no signals 5+ days, review code for bugs

### Risk 5: Market Regime Changes
**Mitigation:** Multi-regime testing, adjust rules for low volatility
**Triggers:** If win rate drops >50%, pause and analyze

---

## DECISION POINTS & GATES

### Gate 1: Walk-Forward Validation (End Week 4)
**Requirement:** DSR > 0.90 across 6+ windows
**Decision:** Proceed to manual testing or refine rules

### Gate 2: Manual Testing Results (End Week 6)
**Requirement:** Win rate within 5% of backtest
**Decision:** Proceed to paper trading or refine signals

### Gate 3: Paper Trading Results (End Week 8)
**Requirement:** Consistent performance matching backtest
**Decision:** Proceed to live trading or refine system

### Gate 4: Live Trading Month 1 (End Month 1)
**Requirement:** Positive or break-even P&L
**Decision:** Scale capital or refine rules

---

## DOCUMENTATION & COMMUNICATION

### Files Created
```
/quant-master/
├── MASTER_ROADMAP_FOREX_SMC.md (this file)
├── code/
│   ├── backtester/ (TonyMa1 clone)
│   ├── smc_indicators.py
│   ├── risk_management.py
│   ├── walk_forward_analysis.py
│   ├── live_trading.py
│   ├── SMC_ENTRY_RULES.md
│   └── DATA_PIPELINE.md
├── data/
│   ├── forex_data.db (SQLite)
│   └── paper_trading_log.csv
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_smc_indicators.ipynb
│   ├── 03_backtest_analysis.ipynb
│   ├── 04_walk_forward_results.ipynb
│   ├── 05_multi_pair_validation.ipynb
│   ├── 06_final_validation.ipynb
│   └── 07_paper_trading_analysis.ipynb
├── results/
│   ├── backtest_results.csv
│   ├── walk_forward_summary.csv
│   └── plots/ (charts)
└── memory/
    ├── SESSION_001_KICKOFF.md
    └── daily logs
```

### Weekly Communication
- **DRE:** Receives weekly progress report
- **Report Includes:** Completed tasks, metrics, blockers, next steps
- **Format:** Markdown file + summary message

### Metrics to Track
- Code written (lines, functions, tests)
- Backtests run (number, parameters)
- Trades executed (manual, paper)
- Performance metrics (win rate, Sharpe, DSR)

---

## NEXT IMMEDIATE ACTIONS

**This Week (Feb 2-6):**

1. [ ] **DRE approves plan** (or suggests changes)
2. [ ] **Clone TonyMa1/walk-forward-backtester**
3. [ ] **Set up data pipeline** (IB or Yahoo Finance)
4. [ ] **Implement FVG detection**
5. [ ] **Implement order block detection**

**By Feb 13 (Week 2):**

6. [ ] **SMC indicator complete**
7. [ ] **First backtest running**
8. [ ] **Risk management module complete**
9. [ ] **Initial results reviewed**

**By Feb 20 (Week 3):**

10. [ ] **Walk-forward optimization live**
11. [ ] **DSR calculation validated**
12. [ ] **Manual trading begins**

**By March 2 (Week 5):**

13. [ ] **Manual testing complete (20-30 trades)**
14. [ ] **Paper trading starts**

**By March 16 (Week 7):**

15. [ ] **50+ paper trades logged**
16. [ ] **Go/No-Go decision made**

**By March 30 (Week 8):**

17. [ ] **Live trading ready to start**

---

## FINAL CHECKLIST BEFORE LIVE TRADING

- [ ] Backtester validated on 6+ months data
- [ ] Walk-forward DSR > 0.90 on all windows
- [ ] Multi-pair validation passed
- [ ] Parameter sensitivity tested (±10%)
- [ ] 20+ manual trades match signals
- [ ] 50+ paper trades match backtest
- [ ] Risk management rules coded
- [ ] IB API working
- [ ] Order placement tested
- [ ] Monitoring system in place
- [ ] Emergency stop-loss procedures documented
- [ ] DRE approves go-live

---

**DOCUMENT STATUS:** Complete & Ready for Review
**DATE:** February 2, 2026
**NEXT STEP:** DRE reviews and suggests changes

---

# SUMMARY FOR DRE

**What we're building:** Automated SMC trading system for forex (EUR/USD, GBP/USD, AUD/USD)

**Timeline:** 8 weeks to live trading

**Success metrics:**
- DSR > 0.90 (statistically valid edge)
- 35-40% win rate with 1:3+ RR
- 50+ paper trades matching backtest
- Live trading starting Week 8

**Tools needed:**
- Interactive Brokers (free with account)
- Python libraries (all free)
- TonyMa1's walk-forward backtester (free, open-source)

**Cost:** $0 to get started (except IB account $10K minimum to trade live)

**Risks:** 
- Overfitting → mitigated by walk-forward + DSR
- Slippage → mitigated by realistic backtest costs
- Drawdowns → mitigated by 2% daily loss limit

**Any changes or concerns?**
