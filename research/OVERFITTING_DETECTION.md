# Overfitting Detection Techniques

## Core Problem: The Researcher's Dilemma

```
You have 20 years of data and 1000 parameter combinations.
One of them WILL show amazing results by pure chance.

The Question: Is your strategy's edge REAL or LUCKY?
The Answer: Overfitting detection techniques.
```

---

## 1. Parameter Space Sensitivity Analysis

### Methodology

**Concept:** A robust strategy should perform well across a WIDE parameter range, not just at one "magic" spot.

```python
class ParameterSensitivityDetector:
    """
    Detect overfitting by analyzing parameter space sensitivity.
    
    If optimal parameters show sharp peak = LIKELY OVERFIT
    If broad plateau = ROBUST
    """
    
    def __init__(self, data, backtest_func, lookback=50):
        self.data = data
        self.backtest_func = backtest_func
        self.lookback = lookback
    
    def test_parameter_stability(self, optimal_params, variation_range=0.3):
        """
        Test: Does strategy still profit if parameters vary ±30%?
        
        Args:
            optimal_params: dict of optimized parameters
            variation_range: How much to vary (0.3 = ±30%)
        
        Returns:
            robustness_score: 0-1 (1 = very robust)
        """
        results = {}
        
        for param_name in optimal_params:
            base_value = optimal_params[param_name]
            
            # Create parameter variations
            variation = int(base_value * variation_range)
            param_range = range(
                max(1, base_value - variation),
                base_value + variation + 1
            )
            
            performance_over_range = []
            
            for param_value in param_range:
                test_params = optimal_params.copy()
                test_params[param_name] = param_value
                
                perf = self.backtest_func(self.data, test_params)
                performance_over_range.append(perf['sharpe_ratio'])
            
            # Analyze distribution
            mean_performance = np.mean(performance_over_range)
            std_performance = np.std(performance_over_range)
            max_performance = np.max(performance_over_range)
            
            # Robustness = how close avg is to max
            robustness = 1 - (std_performance / max_performance) if max_performance > 0 else 0
            robustness = max(0, min(1, robustness))  # Clamp 0-1
            
            results[param_name] = {
                'base_value': base_value,
                'range': list(param_range),
                'performances': performance_over_range,
                'mean': mean_performance,
                'std': std_performance,
                'max': max_performance,
                'robustness': robustness,
                'peak_sharpness': (max_performance - mean_performance) / max_performance  # 0 = flat, 1 = sharp
            }
        
        return results
    
    @staticmethod
    def interpret_sensitivity(sensitivity_results):
        """Interpret sensitivity analysis results"""
        overall_robustness = np.mean([r['robustness'] 
                                      for r in sensitivity_results.values()])
        overall_peak_sharpness = np.mean([r['peak_sharpness'] 
                                          for r in sensitivity_results.values()])
        
        if overall_robustness > 0.7:
            assessment = "✅ ROBUST - Parameters stable across range"
        elif overall_robustness > 0.5:
            assessment = "⚠️  MODERATE - Some sensitivity detected"
        else:
            assessment = "❌ FRAGILE - Parameters very sensitive (likely overfit)"
        
        if overall_peak_sharpness > 0.3:
            peak_warning = "⚠️  Sharp peak detected (overfitting risk)"
        else:
            peak_warning = "✓ Broad plateau (good sign)"
        
        return {
            'overall_robustness': overall_robustness,
            'peak_sharpness': overall_peak_sharpness,
            'assessment': assessment,
            'peak_warning': peak_warning
        }

# Usage
detector = ParameterSensitivityDetector(data, my_backtest_function)
sensitivity = detector.test_parameter_stability(optimal_params, variation_range=0.3)
assessment = detector.interpret_sensitivity(sensitivity)

for param, result in sensitivity.items():
    print(f"\n{param}:")
    print(f"  Base value: {result['base_value']}")
    print(f"  Robustness: {result['robustness']:.2f}")
    print(f"  Peak sharpness: {result['peak_sharpness']:.2f}")

print(f"\nOverall Assessment: {assessment['assessment']}")
```

---

## 2. Multiple Regime Testing (Bull/Bear/Sideways)

### Market Regimes

```
BULL MARKET:
  Characterized by: Rising highs, rising lows, consistent uptrend
  Example period: 2017, 2020-2021 bull markets
  Strategy test: Does it still work in uptrends?

BEAR MARKET:
  Characterized by: Falling highs, falling lows, consistent downtrend
  Example period: 2022, 2008-2009
  Strategy test: Does it profit on shorts or at least minimize losses?

SIDEWAYS MARKET:
  Characterized by: No clear trend, choppy, range-bound
  Example period: 2015-2016, late 2021-early 2022
  Strategy test: Does it survive whipsaws without ruin?
```

### Regime Analysis

```python
class MarketRegimeDetector:
    """Identify market regimes and test strategy in each"""
    
    @staticmethod
    def classify_regimes(data, window=50):
        """Classify each period as Bull/Bear/Sideways"""
        data_copy = data.copy()
        
        # Calculate slope of moving average
        ma = data_copy['close'].rolling(window=window).mean()
        slope = ma.diff()
        
        # ATR for volatility
        atr = data_copy['high'] - data_copy['low']
        atr_ma = atr.rolling(window=window).mean()
        
        regimes = []
        
        for i in range(window, len(data)):
            if slope.iloc[i] > 0 and atr_ma.iloc[i] < atr_ma.mean():
                regime = 'BULL'
            elif slope.iloc[i] < 0 and atr_ma.iloc[i] < atr_ma.mean():
                regime = 'BEAR'
            else:
                regime = 'SIDEWAYS'
            
            regimes.append(regime)
        
        data_copy['regime'] = ['UNKNOWN'] * window + regimes
        return data_copy
    
    @staticmethod
    def test_by_regime(data, backtest_func, params):
        """Test strategy performance in each regime"""
        data = MarketRegimeDetector.classify_regimes(data)
        
        regime_results = {}
        
        for regime in ['BULL', 'BEAR', 'SIDEWAYS']:
            regime_data = data[data['regime'] == regime]
            
            if len(regime_data) > 10:
                perf = backtest_func(regime_data, params)
                regime_results[regime] = perf
        
        return regime_results
    
    @staticmethod
    def multi_regime_analysis(original_backtest_result, regime_results):
        """
        Analyze strategy performance across regimes.
        
        Red flag: Works great in bull but fails in bear
        """
        performances = [regime_results[r].get('sharpe_ratio', 0) 
                       for r in ['BULL', 'BEAR', 'SIDEWAYS']]
        
        consistency = 1 - (max(performances) - min(performances)) / max(1, max(performances))
        
        return {
            'bull_sharpe': regime_results.get('BULL', {}).get('sharpe_ratio', 0),
            'bear_sharpe': regime_results.get('BEAR', {}).get('sharpe_ratio', 0),
            'sideways_sharpe': regime_results.get('SIDEWAYS', {}).get('sharpe_ratio', 0),
            'consistency_score': consistency,
            'assessment': (
                "✅ Consistent across regimes" if consistency > 0.7
                else "⚠️  Performance varies by regime" if consistency > 0.4
                else "❌ Inconsistent (overfitted to one regime)"
            )
        }

# Usage
detector = MarketRegimeDetector()
regime_results = detector.test_by_regime(data, my_backtest, optimal_params)
analysis = detector.multi_regime_analysis(original_result, regime_results)

print(f"Bull Sharpe: {analysis['bull_sharpe']:.3f}")
print(f"Bear Sharpe: {analysis['bear_sharpe']:.3f}")
print(f"Sideways Sharpe: {analysis['sideways_sharpe']:.3f}")
print(f"Consistency: {analysis['consistency_score']:.2f}")
print(f"Assessment: {analysis['assessment']}")
```

---

## 3. Monte Carlo Analysis

### Concept

**Shuffle return order:** If strategy's edge is real, return order shouldn't matter. If result is lucky = shuffled returns look similar.

```python
class MonteCarloAnalyzer:
    """
    Monte Carlo: Randomize trade order to detect overfitting
    
    If shuffled returns ≈ original returns = lucky
    If shuffled returns << original returns = genuine edge
    """
    
    @staticmethod
    def monte_carlo_trades(trades, num_simulations=1000):
        """
        Shuffle trade order, recalculate P&L.
        If edge is real, shuffled order should matter.
        """
        original_pnl = [t['pnl'] for t in trades]
        original_cumulative = np.cumsum(original_pnl)
        original_final = original_cumulative[-1]
        
        simulated_finals = []
        
        for _ in range(num_simulations):
            # Shuffle trades randomly
            shuffled_pnl = np.random.permutation(original_pnl)
            shuffled_cumulative = np.cumsum(shuffled_pnl)
            simulated_finals.append(shuffled_cumulative[-1])
        
        simulated_finals = np.array(simulated_finals)
        
        # Analysis
        percentile_rank = (simulated_finals <= original_final).sum() / num_simulations
        
        return {
            'original_pnl': original_final,
            'simulated_mean': simulated_finals.mean(),
            'simulated_std': simulated_finals.std(),
            'percentile_rank': percentile_rank,
            'z_score': (original_final - simulated_finals.mean()) / (simulated_finals.std() + 0.0001),
            'is_lucky': percentile_rank < 0.6  # If most shuffles beat us, we're lucky
        }
    
    @staticmethod
    def monte_carlo_parameters(data, backtest_func, base_params, num_sims=100):
        """
        Monte Carlo parameter testing:
        Random parameter combinations to verify best params aren't luck
        """
        base_performance = backtest_func(data, base_params)
        
        random_performances = []
        
        for _ in range(num_sims):
            # Generate random parameters
            random_params = {
                'fast_ma': np.random.randint(5, 50),
                'slow_ma': np.random.randint(50, 200),
                'rsi_period': np.random.randint(10, 30)
            }
            
            perf = backtest_func(data, random_params)
            random_performances.append(perf['sharpe_ratio'])
        
        random_performances = np.array(random_performances)
        
        percentile = (random_performances <= base_performance['sharpe_ratio']).sum() / num_sims
        
        return {
            'optimized_sharpe': base_performance['sharpe_ratio'],
            'random_mean': random_performances.mean(),
            'random_std': random_performances.std(),
            'percentile': percentile,
            'better_than_random': percentile > 0.7,
            'interpretation': (
                "✅ Much better than random" if percentile > 0.8
                else "⚠️  Slightly better than random" if percentile > 0.6
                else "❌ Could be lucky (close to random)"
            )
        }
    
    @staticmethod
    def monte_carlo_drawdown_paths(trades, num_sims=1000):
        """
        Simulate different drawdown paths.
        See what max drawdown could realistically be.
        """
        pnl = [t['pnl'] for t in trades]
        
        simulated_mdd = []
        
        for _ in range(num_sims):
            shuffled = np.random.permutation(pnl)
            cumulative = np.cumsum(shuffled)
            running_max = np.maximum.accumulate(cumulative)
            drawdowns = cumulative - running_max
            mdd = np.min(drawdowns)
            simulated_mdd.append(mdd)
        
        simulated_mdd = np.array(simulated_mdd)
        
        return {
            'percentile_5': np.percentile(simulated_mdd, 5),
            'percentile_25': np.percentile(simulated_mdd, 25),
            'percentile_50': np.percentile(simulated_mdd, 50),  # Median
            'percentile_95': np.percentile(simulated_mdd, 95),
            'interpretation': (
                f"Expect MDD between {np.percentile(simulated_mdd, 25):.2f} "
                f"and {np.percentile(simulated_mdd, 95):.2f} with 90% confidence"
            )
        }

# Usage
analyzer = MonteCarloAnalyzer()

# Trade order randomization
trade_analysis = analyzer.monte_carlo_trades(trades, num_simulations=1000)
print(f"Original P&L: {trade_analysis['original_pnl']:.2f}")
print(f"Shuffled mean: {trade_analysis['simulated_mean']:.2f}")
print(f"Percentile rank: {trade_analysis['percentile_rank']:.1%}")
if trade_analysis['is_lucky']:
    print("⚠️  Likely lucky (random order does almost as well)")

# Parameter randomization
param_analysis = analyzer.monte_carlo_parameters(data, backtest_func, optimal_params)
print(f"\nOptimized Sharpe: {param_analysis['optimized_sharpe']:.3f}")
print(f"Random mean: {param_analysis['random_mean']:.3f}")
print(f"Better than random: {param_analysis['better_than_random']}")
print(f"Interpretation: {param_analysis['interpretation']}")

# Drawdown Monte Carlo
drawdown_mc = analyzer.monte_carlo_drawdown_paths(trades)
print(f"\nDrawdown Range (90% confidence):")
print(f"  {drawdown_mc['percentile_5']:.2f} to {drawdown_mc['percentile_95']:.2f}")
```

---

## 4. Real vs Synthetic Edge Validation

### The Synthetic Test

```python
class RealVsSyntheticValidator:
    """
    Generate synthetic market data (where no edge exists by definition).
    If strategy works on synthetic data = definitely overfitted.
    """
    
    @staticmethod
    def generate_random_walk(price_series, num_simulations=100):
        """
        Generate random walk data with same statistical properties
        but no real market structure = no real edge possible
        """
        log_returns = np.diff(np.log(price_series))
        
        synthetic_series = []
        
        for _ in range(num_simulations):
            # Shuffle returns (maintain distribution, destroy structure)
            shuffled_returns = np.random.permutation(log_returns)
            
            # Reconstruct price
            synthetic_prices = np.exp(np.cumsum(shuffled_returns))
            synthetic_prices = synthetic_prices * price_series.iloc[0]
            
            synthetic_series.append(synthetic_prices)
        
        return np.array(synthetic_series)
    
    @staticmethod
    def generate_geometric_brownian_motion(S0, mu, sigma, T, dt=1/252, num_sims=100):
        """Generate GBM synthetic data (random walk with drift)"""
        N = int(T / dt)
        simulated_prices = []
        
        for _ in range(num_sims):
            prices = np.zeros(N)
            prices[0] = S0
            
            for t in range(1, N):
                dW = np.random.normal(0, np.sqrt(dt))
                prices[t] = prices[t-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * dW)
            
            simulated_prices.append(prices)
        
        return np.array(simulated_prices)
    
    @staticmethod
    def test_real_vs_synthetic(real_data, backtest_func, params, num_synthetic_sims=100):
        """
        Compare strategy performance on real vs synthetic data.
        """
        # Test on real data
        real_result = backtest_func(real_data, params)
        
        # Generate synthetic data
        synthetic_prices = RealVsSyntheticValidator.generate_random_walk(
            real_data['close'], num_simulations=num_synthetic_sims
        )
        
        # Create synthetic OHLCV data
        synthetic_results = []
        
        for prices in synthetic_prices:
            # Approximate OHLCV from prices
            synthetic_data = real_data.copy()
            synthetic_data['open'] = prices
            synthetic_data['high'] = prices
            synthetic_data['low'] = prices
            synthetic_data['close'] = prices
            
            result = backtest_func(synthetic_data, params)
            synthetic_results.append(result)
        
        synthetic_sharpes = [r['sharpe_ratio'] for r in synthetic_results]
        synthetic_sharpes = np.array(synthetic_sharpes)
        
        # Analysis
        real_percentile = (synthetic_sharpes <= real_result['sharpe_ratio']).sum() / num_synthetic_sims
        
        return {
            'real_sharpe': real_result['sharpe_ratio'],
            'synthetic_mean': synthetic_sharpes.mean(),
            'synthetic_std': synthetic_sharpes.std(),
            'percentile_vs_synthetic': real_percentile,
            'is_genuine': real_percentile > 0.75,
            'interpretation': (
                "✅ Real edge likely genuine (beats random walks)" 
                if real_percentile > 0.75
                else "⚠️  Performance marginal vs random" 
                if real_percentile > 0.5
                else "❌ Underperforms random (definitely overfitted)"
            )
        }

# Usage
validator = RealVsSyntheticValidator()

result = validator.test_real_vs_synthetic(
    real_data=data,
    backtest_func=my_backtest,
    params=optimal_params,
    num_synthetic_sims=100
)

print(f"Real Data Sharpe: {result['real_sharpe']:.3f}")
print(f"Synthetic Mean: {result['synthetic_mean']:.3f}")
print(f"Percentile vs Synthetic: {result['percentile_vs_synthetic']:.1%}")
print(f"Interpretation: {result['interpretation']}")
```

---

## 5. Composite Overfitting Score

### Combine All Signals

```python
class CompositeOverfittingDetector:
    """
    Combine all overfitting detection methods into single score
    """
    
    @staticmethod
    def calculate_overfitting_index(
        param_sensitivity_score,      # 0-1 (1 = robust)
        regime_consistency_score,     # 0-1 (1 = consistent)
        monte_carlo_percentile,       # 0-1 (1 = genuine edge)
        real_vs_synthetic_percentile, # 0-1 (1 = beats random)
        oos_vs_is_degradation,        # 0-1 (0 = no degradation, 1 = 100% worse)
        sample_size_adequacy          # 0-1 (1 = large sample)
    ):
        """
        Calculate composite overfitting risk score
        
        Returns:
            0-100 (0 = robust, 100 = severely overfit)
        """
        
        # Convert to overfitting signals (higher = more overfit)
        param_sensitivity_risk = (1 - param_sensitivity_score) * 20
        regime_risk = (1 - regime_consistency_score) * 15
        monte_carlo_risk = (1 - monte_carlo_percentile) * 25
        synthetic_risk = (1 - real_vs_synthetic_percentile) * 20
        degradation_risk = oos_vs_is_degradation * 15
        sample_risk = (1 - sample_size_adequacy) * 5
        
        total_score = (
            param_sensitivity_risk +
            regime_risk +
            monte_carlo_risk +
            synthetic_risk +
            degradation_risk +
            sample_risk
        )
        
        total_score = min(100, max(0, total_score))
        
        return total_score
    
    @staticmethod
    def interpret_score(score):
        """Interpret overfitting score"""
        if score < 15:
            return "🟢 LOW RISK - Strategy likely robust"
        elif score < 30:
            return "🟡 MODERATE RISK - Some concerns, needs more validation"
        elif score < 50:
            return "🟠 HIGH RISK - Notable overfitting detected"
        else:
            return "🔴 SEVERE RISK - Likely false positive"

# Usage
detector = CompositeOverfittingDetector()

score = detector.calculate_overfitting_index(
    param_sensitivity_score=0.75,      # Robust parameters
    regime_consistency_score=0.80,     # Consistent across bull/bear
    monte_carlo_percentile=0.85,       # Better than shuffled trades
    real_vs_synthetic_percentile=0.82, # Beats random walks
    oos_vs_is_degradation=0.25,        # 25% degradation (acceptable)
    sample_size_adequacy=0.9            # Good sample size
)

print(f"Overfitting Risk Score: {score:.1f}/100")
print(f"Assessment: {detector.interpret_score(score)}")
```

---

## Overfitting Detection Checklist

```
PARAMETER SENSITIVITY:
  ☐ Test ±30% parameter variation
  ☐ Robustness score > 0.65
  ☐ Broad performance plateau, not sharp peak
  ☐ Multiple parameters show similar robustness

MULTIPLE REGIME TESTING:
  ☐ Performance in BULL market acceptable
  ☐ Performance in BEAR market acceptable
  ☐ Performance in SIDEWAYS acceptable
  ☐ Consistency score > 0.70

MONTE CARLO:
  ☐ Trades better than 80% of shuffled permutations
  ☐ Optimized params better than 75% of random params
  ☐ Expected drawdown realistic (not optimistic)

REAL VS SYNTHETIC:
  ☐ Beats random walks at 80%+ percentile
  ☐ Outperforms GBM data significantly
  ☐ Works with different synthetic parameters

SAMPLE SIZE:
  ☐ Minimum 500 trades or 3+ years of data
  ☐ Confidence intervals not too wide
  ☐ DSR > 0.90 (accounting for sample size)

OUT-OF-SAMPLE:
  ☐ Performance degradation < 50%
  ☐ Win rate similar (±5%)
  ☐ Drawdown controlled
  ☐ Profit factor stable

FINAL SCORE:
  ☐ Composite overfitting index < 30
  ☐ All component tests pass (not just majority)
  ☐ Ready for walk-forward analysis
  ☐ Ready for paper trading
```

---

## Red Flags: Warning Signs of Overfitting

```
🚩 CRITICAL RED FLAGS (Do not trade):

1. Parameter clustering
   → Best params all at edge of search space (e.g., SMA=200, RSI=1)
   
2. Performance cliff
   → Sharpe 1.5 at SMA=50 but -0.5 at SMA=51
   
3. Regime fragmentation
   → Works in bull but loses money in bear/sideways
   
4. Monte Carlo failure
   → Random trades beat your trades 60%+ of time
   
5. Synthetic dominance
   → Random walk performs nearly as well
   
6. Massive IS/OOS gap
   → In-sample Sharpe 2.0, out-of-sample Sharpe 0.2
   
7. Too many parameters
   → 10+ parameters for strategy (each adds overfitting risk)

🟡 YELLOW FLAGS (Caution, needs more validation):

1. Sample size < 1 year
2. DSR borderline (0.70-0.90)
3. Win rate highly variable month-to-month
4. Strategy needs perfect conditions (limited hours/symbols)
5. Parameters outside historical norms
```

---

## Summary: Overfitting Detection Pipeline

```
BEFORE TRADING ANY STRATEGY:

1. Parameter Sensitivity Analysis
   ✓ Robustness score > 0.65
   
2. Multiple Regime Testing
   ✓ Works in bull, bear, sideways
   ✓ Consistency score > 0.70
   
3. Monte Carlo Validation
   ✓ Beats 80%+ of shuffled trades
   ✓ Outperforms 75%+ random parameters
   
4. Real vs Synthetic
   ✓ Beats random walk data
   ✓ Outperforms GBM synthetic
   
5. Composite Score
   ✓ Overfitting index < 30
   
IF ALL PASS → PROCEED TO WALK-FORWARD TESTING
IF ANY FAIL → REJECT STRATEGY, BACK TO DRAWING BOARD
```

**Truth:** If a strategy doesn't pass these tests, it's 95%+ likely to fail in live trading. These tests are your defense against expensive mistakes.
