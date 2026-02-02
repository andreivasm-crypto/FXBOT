# Python Backtesting Architecture

## VectorBT vs Backtrader Comparison

### VectorBT

**Philosophy:** Vectorized, fast, NumPy/Pandas based

| Aspect | VectorBT |
|--------|----------|
| **Speed** | ⚡⚡⚡ Very fast (vectorized) |
| **Setup Time** | Medium (learning curve) |
| **Memory Usage** | Low (vectorized operations) |
| **Parallelization** | Excellent (multi-core ready) |
| **Code Clarity** | Medium (pandas-heavy) |
| **Real Exchange Features** | Limited |
| **Best For** | Fast research, parameter optimization, large datasets |
| **Worst For** | Complex logic, real broker integration, paper trading |

**Strengths:**
- Blazing fast backtests
- Built for optimization research
- Great for walk-forward analysis
- Low memory footprint
- Excellent for Monte Carlo analysis

**Weaknesses:**
- Steep learning curve
- Less intuitive entry/exit syntax
- Limited order types
- No live trading hooks

### Backtrader

**Philosophy:** Event-driven, realistic, broker-like

| Aspect | Backtrader |
|--------|-----------|
| **Speed** | 🐌 Slower (event-driven) |
| **Setup Time** | Fast (intuitive) |
| **Memory Usage** | Higher (event-by-event) |
| **Parallelization** | Limited (not designed for it) |
| **Code Clarity** | High (very readable) |
| **Real Exchange Features** | Excellent |
| **Best For** | Complex strategies, live trading, paper trading |
| **Worst For** | Large-scale optimization, Monte Carlo |

**Strengths:**
- Intuitive, easy to learn
- Event-driven = realistic simulation
- Excellent broker integration
- Paper trading built-in
- Good documentation

**Weaknesses:**
- Slow for large datasets
- Not suitable for massive optimization
- Memory intensive
- Limited to single-core

### Decision Matrix

```
Use VECTORBT if:
  ✓ Testing many parameters
  ✓ Large historical dataset
  ✓ Need walk-forward analysis
  ✓ Need Monte Carlo simulations
  ✓ Speed is critical

Use BACKTRADER if:
  ✓ Complex logic with conditions
  ✓ Need realistic broker simulation
  ✓ Planning live trading later
  ✓ Need paper trading
  ✓ Clarity > speed
```

---

## Walk-Forward Framework Structure

### Overall Architecture

```
BACKTESTING SYSTEM

├── DATA LAYER
│   ├── Load historical OHLCV
│   ├── Resample (daily → 4H → 1H if needed)
│   └── Validate data quality
│
├── WALK-FORWARD ENGINE
│   ├── Split data: [2018-2019] [2020] [2021-2022]
│   └── For each walk:
│       ├── OPTIMIZATION: Backtest on IS data
│       ├── PARAMETER SEARCH: Find best params
│       └── VALIDATION: Test on OOS data
│
├── STRATEGY LAYER
│   ├── Entry signals
│   ├── Exit rules
│   ├── Position sizing
│   └── Risk management
│
├── EXECUTION LAYER
│   ├── Order placement
│   ├── Slippage modeling
│   ├── Commission calculation
│   └── Trade tracking
│
└── REPORTING LAYER
    ├── Aggregate statistics
    ├── Drawdown analysis
    ├── Sharpe ratio calculation
    └── Generate reports
```

### Minimal Backtrader Framework

```python
import backtrader as bt
import pandas as pd
import numpy as np

class SMCStrategy(bt.Strategy):
    """Base SMC trading strategy"""
    
    params = (
        ('fast_ma', 20),
        ('slow_ma', 50),
        ('rsi_period', 14),
        ('printlog', False),
    )
    
    def log(self, txt, dt=None):
        """Logging function"""
        dt = dt or self.datas[0].datetime.date(0)
        if self.params.printlog:
            print(f'{dt.isoformat()} {txt}')
    
    def __init__(self):
        # Add indicators
        self.ma_fast = bt.indicators.SMA(self.data.close, 
                                          period=self.params.fast_ma)
        self.ma_slow = bt.indicators.SMA(self.data.close, 
                                          period=self.params.slow_ma)
        self.rsi = bt.indicators.RSI(self.data.close, 
                                      period=self.params.rsi_period)
        
        self.order = None
        self.buyprice = None
        self.buycomm = None
    
    def notify_order(self, order):
        """Handle order execution"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.log(f'BUY EXECUTED: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED: {order.executed.price:.2f}')
            
            self.order = None
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            self.order = None
    
    def next(self):
        """Called on each bar"""
        # Entry logic
        if not self.position:
            if self.ma_fast[0] > self.ma_slow[0] and self.rsi[0] < 70:
                self.order = self.buy()
        
        # Exit logic
        else:
            if self.ma_fast[0] < self.ma_slow[0]:
                self.order = self.sell()

class WalkForwardOptimizer:
    """Walk-forward optimization framework"""
    
    def __init__(self, data_file, in_sample_days=252, 
                 out_sample_days=63, initial_cash=10000):
        """
        Args:
            data_file: CSV with OHLCV data
            in_sample_days: Training window (days)
            out_sample_days: Testing window (days)
            initial_cash: Starting capital
        """
        self.data_df = pd.read_csv(data_file, 
                                   index_col='date', 
                                   parse_dates=True)
        self.in_days = in_sample_days
        self.out_days = out_sample_days
        self.cash = initial_cash
        self.results = []
    
    def run_walk(self, in_data, out_data, params, verbose=False):
        """Run single walk-forward cycle"""
        
        # OPTIMIZATION PHASE
        best_params = self._optimize(in_data, params)
        
        # VALIDATION PHASE
        out_results = self._backtest(out_data, best_params)
        
        return {
            'best_params': best_params,
            'out_of_sample': out_results
        }
    
    def _optimize(self, data, param_ranges):
        """Grid search optimization"""
        best_params = None
        best_sharpe = float('-inf')
        
        # Generate param combinations
        param_combos = self._param_grid(param_ranges)
        
        for params in param_combos:
            result = self._backtest(data, params)
            sharpe = result['sharpe_ratio']
            
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = params.copy()
        
        return best_params
    
    def _backtest(self, data, params):
        """Run backtest with given parameters"""
        cerebro = bt.Cerebro()
        
        # Add data
        datafeed = self._create_datafeed(data)
        cerebro.adddata(datafeed)
        
        # Add strategy with params
        cerebro.addstrategy(SMCStrategy, **params)
        
        # Broker settings
        cerebro.broker.setcash(self.cash)
        cerebro.broker.setcommission(commission=0.001)
        
        # Run backtest
        results = cerebro.run()
        
        # Extract metrics
        strat = results[0]
        
        # Calculate statistics
        stats = {
            'total_return': (cerebro.broker.getvalue() / self.cash) - 1,
            'sharpe_ratio': self._calculate_sharpe(strat),
            'max_drawdown': self._calculate_mdd(strat),
            'trades': len(strat.trades)
        }
        
        return stats
    
    def _create_datafeed(self, data_df):
        """Convert DataFrame to Backtrader datafeed"""
        class PandasData(bt.feeds.PandasData):
            params = (
                ('datetime', None),
                ('open', 'open'),
                ('high', 'high'),
                ('low', 'low'),
                ('close', 'close'),
                ('volume', 'volume'),
                ('openinterest', None),
            )
        
        feed = PandasData(dataname=data_df)
        return feed
    
    def _param_grid(self, param_ranges):
        """Generate all parameter combinations"""
        import itertools
        param_names = list(param_ranges.keys())
        param_lists = []
        
        for name in param_names:
            min_v, max_v, step = param_ranges[name]
            param_lists.append(range(min_v, max_v + step, step))
        
        combos = []
        for combo in itertools.product(*param_lists):
            params = {param_names[i]: combo[i] 
                     for i in range(len(param_names))}
            combos.append(params)
        
        return combos
    
    def _calculate_sharpe(self, strategy):
        """Calculate Sharpe ratio"""
        # Implementation depends on strategy attributes
        return 1.0  # Placeholder
    
    def _calculate_mdd(self, strategy):
        """Calculate maximum drawdown"""
        return -0.10  # Placeholder
    
    def run_walk_forward(self, param_ranges):
        """Execute full walk-forward analysis"""
        walk_num = 0
        
        in_start = 0
        while in_start + self.in_days + self.out_days <= len(self.data_df):
            in_end = in_start + self.in_days
            out_start = in_end
            out_end = out_start + self.out_days
            
            # Get data
            in_data = self.data_df.iloc[in_start:in_end]
            out_data = self.data_df.iloc[out_start:out_end]
            
            # Run walk
            result = self.run_walk(in_data, out_data, param_ranges)
            result['walk'] = walk_num
            self.results.append(result)
            
            print(f"Walk {walk_num}: "
                  f"Params={result['best_params']}, "
                  f"OOS Return={result['out_of_sample']['total_return']:.2%}")
            
            # Roll forward
            in_start += self.out_days
            walk_num += 1
        
        return self.results

# Usage
optimizer = WalkForwardOptimizer(
    'data/EURUSD_daily.csv',
    in_sample_days=252,
    out_sample_days=63
)

param_ranges = {
    'fast_ma': [5, 50, 5],
    'slow_ma': [20, 200, 20],
    'rsi_period': [10, 30, 5]
}

results = optimizer.run_walk_forward(param_ranges)
```

---

## Performance Metric Calculations

```python
class BacktestMetrics:
    """Calculate comprehensive backtesting metrics"""
    
    @staticmethod
    def calculate_sharpe_ratio(returns_series, risk_free_rate=0.02, 
                               periods_per_year=252):
        """
        Sharpe Ratio = (Mean Return - RF Rate) / Std Dev
        """
        mean_return = returns_series.mean() * periods_per_year
        std_dev = returns_series.std() * np.sqrt(periods_per_year)
        
        sharpe = (mean_return - risk_free_rate) / std_dev
        return sharpe
    
    @staticmethod
    def calculate_max_drawdown(returns_series):
        """Calculate maximum drawdown"""
        cumulative = (1 + returns_series).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = drawdown.min()
        return max_dd
    
    @staticmethod
    def calculate_win_rate(trades):
        """Win rate from trade list"""
        if not trades:
            return 0
        
        winning = sum(1 for t in trades if t['pnl'] > 0)
        return winning / len(trades)
    
    @staticmethod
    def calculate_profit_factor(trades):
        """Profit Factor = Gross Profit / Gross Loss"""
        gross_profit = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
        
        if gross_loss == 0:
            return float('inf')
        
        return gross_profit / gross_loss
    
    @staticmethod
    def calculate_calmar_ratio(returns_series, periods_per_year=252):
        """Calmar = Annual Return / Max Drawdown"""
        annual_return = returns_series.mean() * periods_per_year
        max_dd = abs(BacktestMetrics.calculate_max_drawdown(returns_series))
        
        if max_dd == 0:
            return 0
        
        return annual_return / max_dd
    
    @staticmethod
    def generate_report(returns_series, trades, initial_capital=10000):
        """Generate complete backtest report"""
        
        final_value = initial_capital * (1 + returns_series.iloc[-1])
        
        report = {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': returns_series.iloc[-1],
            'annual_return': returns_series.mean() * 252,
            'sharpe_ratio': BacktestMetrics.calculate_sharpe_ratio(returns_series),
            'max_drawdown': BacktestMetrics.calculate_max_drawdown(returns_series),
            'calmar_ratio': BacktestMetrics.calculate_calmar_ratio(returns_series),
            'win_rate': BacktestMetrics.calculate_win_rate(trades),
            'profit_factor': BacktestMetrics.calculate_profit_factor(trades),
            'num_trades': len(trades)
        }
        
        return report

# Usage
metrics = BacktestMetrics()
report = metrics.generate_report(returns_series, trades_list)

print(f"Total Return: {report['total_return']:.2%}")
print(f"Sharpe Ratio: {report['sharpe_ratio']:.3f}")
print(f"Max Drawdown: {report['max_drawdown']:.2%}")
```

---

## Statistical Testing Implementation

```python
class StatisticalTests:
    """Statistical tests for strategy validity"""
    
    @staticmethod
    def t_test_returns(returns_series, expected_mean=0):
        """
        T-test: Are returns significantly different from expected?
        """
        from scipy import stats
        
        t_stat, p_value = stats.ttest_1samp(returns_series, expected_mean)
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    
    @staticmethod
    def autocorrelation_test(returns_series):
        """
        Detect autocorrelation (serial correlation)
        If present = may indicate market anomaly
        """
        from scipy.stats import pearsonr
        
        returns_1lag = returns_series[:-1].values
        returns_current = returns_series[1:].values
        
        correlation, p_value = pearsonr(returns_1lag, returns_current)
        
        return {
            'autocorrelation': correlation,
            'p_value': p_value,
            'detected': abs(correlation) > 0.1 and p_value < 0.05
        }
    
    @staticmethod
    def normality_test(returns_series):
        """
        Shapiro-Wilk test for normal distribution
        Non-normal returns = higher risk than Sharpe suggests
        """
        from scipy import stats
        
        statistic, p_value = stats.shapiro(returns_series[:min(5000, len(returns_series))])
        
        return {
            'is_normal': p_value > 0.05,
            'p_value': p_value,
            'interpretation': 'Normal' if p_value > 0.05 else 'Non-normal (fat tails likely)'
        }
    
    @staticmethod
    def white_reality_check(strategy_pnl, benchmark_pnl, num_tests=100):
        """
        White's Reality Check (Hansen's SPA)
        Is this strategy better than random alternatives?
        """
        # Simplified version
        strategy_return = strategy_pnl.sum()
        benchmark_return = benchmark_pnl.sum()
        
        # Generate random permutations
        best_random = float('-inf')
        
        for _ in range(num_tests):
            perm = np.random.permutation(strategy_pnl.values)
            best_random = max(best_random, perm.sum())
        
        # If strategy > typical random performance
        return {
            'strategy_return': strategy_return,
            'best_random_return': best_random,
            'passes_reality_check': strategy_return > best_random * 1.1
        }

# Usage
tests = StatisticalTests()

# T-test
t_result = tests.t_test_returns(returns_series, expected_mean=0)
print(f"T-test p-value: {t_result['p_value']:.4f}")
print(f"Significant returns: {t_result['significant']}")

# Normality
normal_result = tests.normality_test(returns_series)
print(f"Is normal: {normal_result['is_normal']}")

# Reality check
reality_result = tests.white_reality_check(strategy_pnl, benchmark_pnl)
print(f"Passes reality check: {reality_result['passes_reality_check']}")
```

---

## Summary: Framework Choice Guide

```
RESEARCH PHASE:
  Use VECTORBT
  → Need fast parameter optimization
  → Testing 50+ parameter sets
  → Walk-forward analysis

VALIDATION PHASE:
  Use BACKTRADER
  → Complex entry/exit logic
  → Multiple timeframes
  → Risk management details
  → Validate with realistic broker simulation

PRODUCTION PHASE:
  Use BACKTRADER
  → Paper trading testing
  → Live execution (broker API)
  → Real-time monitoring
  → Event-driven processing
```

**The Professional Pipeline:**
1. VectorBT → Identify promising parameters (1-2 hours)
2. Backtrader → Validate with realistic logic (1 day)
3. Walk-forward → Confirm robustness (2-3 days)
4. Paper trading → Test live (2 weeks minimum)
5. Live trading → Small position, scale up (gradual)
