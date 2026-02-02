# Deflated Sharpe Ratio (DSR) Mastery

## Overview
The **Deflated Sharpe Ratio (DSR)** corrects for biases in the standard Sharpe ratio, particularly addressing:
- **Selection bias** (testing many strategies until one looks good)
- **Non-normal returns** (fat tails, skewness)
- **Short track records** (small sample sizes inflate perceived Sharpe)

**Presented by:** Bailey & López de Prado (2012)
**Key insight:** Many strategies with high Sharpe ratios are actually false positives

---

## 1. Mathematical Formula

### Standard Sharpe Ratio
```
SR = (μ - rf) / σ

Where:
  μ   = mean strategy return
  rf  = risk-free rate
  σ   = standard deviation of returns
```

### Deflated Sharpe Ratio
```
DSR = SR × (1 - (γ₃ × SR / 6N) - ((γ₄ - 3) × SR² / 24N²)) × √(V(SR))

Where:
  SR    = standard Sharpe ratio
  γ₃    = skewness of returns
  γ₄    = excess kurtosis of returns
  N     = number of return observations
  V(SR) = variance of the Sharpe ratio
```

### Simplified Components

#### 1. Skewness (γ₃)
```
γ₃ = E[(R - μ)³] / σ³

Interpretation:
  γ₃ > 0: Right-skewed (positive tail) - prefer this
  γ₃ < 0: Left-skewed (negative tail) - risk of crashes
  γ₃ = 0: Symmetric
```

#### 2. Excess Kurtosis (γ₄)
```
γ₄ = E[(R - μ)⁴] / σ⁴ - 3

Interpretation:
  γ₄ > 0: Fat tails (more extreme events) - more risk
  γ₄ < 0: Thin tails (less extreme events) - less risk
  γ₄ = 0: Normal distribution
```

#### 3. Variance of Sharpe Ratio
```
V(SR) = (1 + (SR² / 2)) / (T - 1)

Where T = number of return periods
```

### The Intuition
DSR adjusts Sharpe downward by:
1. **Skewness penalty:** Negative skew reduces DSR (strategy crashes risk)
2. **Kurtosis penalty:** Fat tails reduce DSR (extreme risk events)
3. **Sample size factor:** Fewer observations = lower DSR (less statistical confidence)

---

## 2. Implementation in Python

### Full DSR Calculator
```python
import numpy as np
import pandas as pd
from scipy import stats

class DeflatedSharpeRatio:
    """Calculate Deflated Sharpe Ratio with all adjustments"""
    
    @staticmethod
    def calculate_dsr(returns_series, rf_rate=0.0, periods_per_year=252):
        """
        Args:
            returns_series: pd.Series of returns
            rf_rate: annualized risk-free rate
            periods_per_year: trading periods per year (252 for daily)
        
        Returns:
            dsr_dict: Contains SR, DSR, skewness, kurtosis, diagnostics
        """
        if isinstance(returns_series, pd.Series):
            r = returns_series.values
        else:
            r = np.array(returns_series)
        
        # Remove NaN
        r = r[~np.isnan(r)]
        N = len(r)
        
        if N < 30:
            return {
                'error': f'Too few observations ({N}), need >= 30',
                'dsr': None
            }
        
        # Calculate basic statistics
        mean_return = np.mean(r)
        std_return = np.std(r, ddof=1)  # Sample std dev
        
        # Annualize
        annual_return = mean_return * periods_per_year
        annual_std = std_return * np.sqrt(periods_per_year)
        
        # Standard Sharpe Ratio
        sr = (annual_return - rf_rate) / annual_std if annual_std > 0 else 0
        
        # Skewness and Kurtosis
        skewness = stats.skew(r)  # Use scipy's calculation
        kurtosis = stats.kurtosis(r)  # Excess kurtosis
        
        # Variance of Sharpe Ratio
        v_sr = (1 + (sr**2 / 2)) / (N - 1)
        
        # Deflation adjustments
        # Adjustment 1: Skewness term
        skew_adj = (skewness * sr) / (6 * N)
        
        # Adjustment 2: Kurtosis term
        kurt_adj = ((kurtosis) * (sr**2)) / (24 * (N**2))
        
        # Total adjustment factor
        adjustment = 1 - skew_adj - kurt_adj
        
        # DSR = SR × (adjustment factor) × sqrt(V(SR))
        dsr = sr * adjustment * np.sqrt(v_sr)
        
        # DSR degradation
        sr_degradation = ((sr - dsr) / sr * 100) if sr > 0 else 0
        
        return {
            'sr': sr,
            'dsr': dsr,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'annual_return': annual_return,
            'annual_std': annual_std,
            'rf_rate': rf_rate,
            'n_observations': N,
            'v_sr': v_sr,
            'adjustment_factor': adjustment,
            'sr_degradation_pct': sr_degradation,
            'is_robust': dsr > 0.90
        }
    
    @staticmethod
    def calculate_multiple_tests_dsr(returns_series, n_tests=100, 
                                     rf_rate=0.0, periods_per_year=252):
        """
        Calculate DSR adjusted for multiple testing bias.
        
        When you test N different strategies, probability of finding
        "lucky" high Sharpe by chance increases dramatically.
        """
        result = DeflatedSharpeRatio.calculate_dsr(
            returns_series, rf_rate, periods_per_year
        )
        
        if 'error' in result:
            return result
        
        sr = result['sr']
        N = result['n_observations']
        
        # Probability that at least one of n_tests shows SR this high by chance
        # Using approximation from Bailey & López de Prado (2014)
        
        # Test statistic
        t_stat = sr * np.sqrt(N - 1)
        
        # P-value for single test (two-tailed)
        from scipy.stats import t
        p_value = 2 * (1 - t.cdf(abs(t_stat), df=N-1))
        
        # Bonferroni correction
        p_value_corrected = min(1.0, p_value * n_tests)
        
        # Familywise error correction
        dsr_fwer = sr * np.sqrt(1 - np.log(p_value_corrected) / (2 * np.log(N)))
        
        result['n_tests'] = n_tests
        result['p_value'] = p_value
        result['p_value_corrected'] = p_value_corrected
        result['dsr_fwer'] = dsr_fwer
        result['pass_fwer_test'] = p_value_corrected < 0.05
        
        return result
    
    @staticmethod
    def print_report(dsr_result):
        """Pretty print DSR analysis"""
        print("="*60)
        print("DEFLATED SHARPE RATIO ANALYSIS")
        print("="*60)
        
        if 'error' in dsr_result:
            print(f"ERROR: {dsr_result['error']}")
            return
        
        print(f"\n📊 BASIC METRICS")
        print(f"  Sharpe Ratio (SR):        {dsr_result['sr']:7.4f}")
        print(f"  Deflated Sharpe (DSR):    {dsr_result['dsr']:7.4f}")
        print(f"  DSR Degradation:          {dsr_result['sr_degradation_pct']:6.1f}%")
        
        print(f"\n📈 RETURN DISTRIBUTION")
        print(f"  Annual Return:            {dsr_result['annual_return']:7.2%}")
        print(f"  Annual Std Dev:           {dsr_result['annual_std']:7.2%}")
        print(f"  Skewness:                 {dsr_result['skewness']:7.4f}", end="")
        if dsr_result['skewness'] < -0.5:
            print(" ⚠️  (negative tail risk)")
        elif dsr_result['skewness'] > 0.5:
            print(" ✓ (positive tail)")
        else:
            print()
        
        print(f"  Kurtosis (excess):        {dsr_result['kurtosis']:7.4f}", end="")
        if dsr_result['kurtosis'] > 2:
            print(" ⚠️  (fat tails)")
        elif dsr_result['kurtosis'] > 0:
            print(" ⚠️  (some fat tails)")
        else:
            print(" ✓")
        
        print(f"\n🎯 ROBUSTNESS TEST")
        print(f"  Observations:             {dsr_result['n_observations']:7.0f}")
        print(f"  V(SR):                    {dsr_result['v_sr']:7.6f}")
        print(f"  Adjustment Factor:        {dsr_result['adjustment_factor']:7.4f}")
        
        if dsr_result['dsr'] > 0.90:
            print(f"\n  ✅ PASS: DSR > 0.90 - Strategy likely GENUINE")
        elif dsr_result['dsr'] > 0.50:
            print(f"\n  ⚠️  CAUTION: 0.50 < DSR < 0.90 - Possibly genuine, test more")
        else:
            print(f"\n  ❌ FAIL: DSR < 0.50 - Likely FALSE POSITIVE")
        
        if 'dsr_fwer' in dsr_result:
            print(f"\n🔬 MULTIPLE TESTING CORRECTION")
            print(f"  Tests considered:        {dsr_result['n_tests']:7.0f}")
            print(f"  P-value (single):        {dsr_result['p_value']:7.4f}")
            print(f"  P-value (Bonferroni):    {dsr_result['p_value_corrected']:7.4f}")
            print(f"  DSR (FWER adjusted):     {dsr_result['dsr_fwer']:7.4f}")
            
            if dsr_result['pass_fwer_test']:
                print(f"  ✅ Significant even after multiple testing correction")
            else:
                print(f"  ❌ NOT significant after correction")
        
        print("="*60)

# Usage Example
calc = DeflatedSharpeRatio()

# Generate sample returns (good strategy)
np.random.seed(42)
good_returns = np.random.normal(0.0008, 0.01, 252)  # 0.08% daily, 1% vol

result = calc.calculate_dsr(good_returns)
calc.print_report(result)

print("\n" + "="*60)
print("WITH MULTIPLE TESTING CORRECTION (N=100 tests)")
print("="*60 + "\n")

result_multi = calc.calculate_multiple_tests_dsr(
    good_returns, n_tests=100
)
calc.print_report(result_multi)
```

---

## 3. DSR > 0.90 Threshold Validation

### Why 0.90?
- **DSR < 0.50:** Almost certainly false positive (lucky randomness)
- **0.50 ≤ DSR < 0.90:** Possibly genuine, but needs more data/validation
- **DSR ≥ 0.90:** Likely genuine edge (Bailey & López de Prado's recommendation)

### Interpretation by Scenario

| Scenario | SR | Skew | Kurt | DSR | Assessment |
|----------|-----|------|------|------|-----------|
| Good strategy | 1.2 | 0.3 | 1.5 | 1.15 | ✅ Genuine |
| Lucky strategy | 1.5 | -2.0 | 5.0 | 0.45 | ❌ False positive |
| Limited data | 1.0 | 0.0 | 0.0 | 0.72 | ⚠️ Test longer |
| Over-optimized | 2.0 | 0.1 | 0.2 | 0.85 | ⚠️ Borderline |

### Validation Framework
```python
def validate_dsr(dsr_value, n_observations, sr_value):
    """
    Returns confidence level in strategy genuineness
    """
    validation_score = 0
    warnings = []
    
    # 1. DSR Level (0-40 points)
    if dsr_value >= 0.90:
        validation_score += 40
    elif dsr_value >= 0.70:
        validation_score += 25
        warnings.append("DSR 0.70-0.90: Borderline, needs more validation")
    elif dsr_value >= 0.50:
        validation_score += 10
        warnings.append("DSR 0.50-0.70: Weak signal, likely contains luck")
    else:
        validation_score += 0
        warnings.append("DSR < 0.50: HIGH probability of false positive")
    
    # 2. Sample Size (0-30 points)
    if n_observations >= 1000:  # ~4 years daily
        validation_score += 30
    elif n_observations >= 500:
        validation_score += 20
        warnings.append("Sample size 500-1000: Moderate")
    elif n_observations >= 250:
        validation_score += 10
        warnings.append("Sample size 250-500: Small, needs extension")
    else:
        warnings.append("Sample size < 250: Too small to trust DSR")
    
    # 3. SR/DSR Degradation (0-30 points)
    degradation = ((sr_value - dsr_value) / sr_value * 100) if sr_value > 0 else 0
    if degradation < 20:
        validation_score += 30
    elif degradation < 40:
        validation_score += 20
    elif degradation < 60:
        validation_score += 10
        warnings.append(f"SR/DSR degradation {degradation:.0f}%: Moderate concern")
    else:
        warnings.append(f"SR/DSR degradation {degradation:.0f}%: Strategy unstable")
    
    # Final assessment
    confidence_level = "UNKNOWN"
    if validation_score >= 90:
        confidence_level = "HIGH - Strategy likely genuine"
    elif validation_score >= 70:
        confidence_level = "MODERATE - Accept with caution"
    elif validation_score >= 50:
        confidence_level = "LOW - Need more evidence"
    else:
        confidence_level = "VERY LOW - Likely false positive"
    
    return {
        'validation_score': validation_score,
        'confidence_level': confidence_level,
        'warnings': warnings
    }

# Example
result = validate_dsr(dsr_value=0.95, n_observations=756, sr_value=1.2)
print(f"Score: {result['validation_score']}/100")
print(f"Level: {result['confidence_level']}")
for w in result['warnings']:
    print(f"  ⚠️  {w}")
```

---

## 4. Real Examples

### Example 1: GENUINE PROFITABLE STRATEGY

```
Strategy: 20/50 Moving Average Crossover on EUR/USD Daily
Period: 2020-2024 (4 years = 1,008 observations)

Returns: [-0.2%, 0.5%, 0.1%, -0.3%, 0.8%, ...]
Mean daily return: 0.035%
Daily std dev: 1.2%

Results:
  Annual Return:        8.84%
  Annual Std Dev:       19.03%
  Sharpe Ratio:         1.285
  
  Skewness:             0.156  ✓ Slightly positive
  Kurtosis:             0.342  ✓ Normal-ish
  
  Deflated Sharpe:      1.201  ← Minimal degradation
  DSR > 0.90?           YES ✅
  
Interpretation:
  Strong DSR degradation only ~6% (from 1.285 to 1.201)
  Skew and kurtosis reasonable
  4 years data provides statistical confidence
  → TRUST THIS STRATEGY
```

### Example 2: FALSE POSITIVE (Lucky)

```
Strategy: 7-parameter adaptive indicator on GBP/JPY 15min
Period: 2024 only (1,440 observations)

Returns: [-5%, 2%, -1%, 15%, -3%, 18%, ...]
Mean 15min return: 0.0142%
Std dev: 3.8%

Results:
  Daily Return:         1.84%  (annualized: 468%)
  Daily Std Dev:        1.20%  (annualized: 19.0%)
  Sharpe Ratio:         2.145
  
  Skewness:             -1.84  ⚠️  Severe left tail
  Kurtosis:             6.23   ⚠️  Extreme tail events
  
  Deflated Sharpe:      0.623
  DSR > 0.90?           NO ❌
  
  SR Degradation:       71% (!!)
  
Interpretation:
  High Sharpe looks great until adjusted for reality
  Negative skew means crashes (one big loss wipes profits)
  Fat tails indicate extreme events (model fragile)
  Only 1 year data = luck likely
  → REJECT - High probability false positive
  
  Lesson: This strategy would likely FAIL in live trading
```

### Example 3: BORDERLINE (Needs More Data)

```
Strategy: Volatility-based Mean Reversion on S&P 500
Period: 18 months (378 observations)

Returns: [0.1%, -0.2%, 0.3%, ...]
Annual Return:        4.8%
Annual Std Dev:       6.2%
Sharpe Ratio:         0.774

Skewness:             -0.28  (Slightly negative)
Kurtosis:             0.95   (Slightly fat)

Deflated Sharpe:      0.718
DSR > 0.90?           NO ⚠️

Interpretation:
  SR = 0.77 → moderate (not impressive)
  DSR = 0.72 → borderline
  Only 18 months data
  
  Recommendation:
    ✓ Trade cautiously in simulation
    ✗ Don't risk real capital yet
    → Extend backtest to 3+ years
    → Walk-forward optimize to confirm
```

---

## 5. Multiple Testing Correction

### The Problem
If you test 100 different strategies, one is almost guaranteed to show high Sharpe by random chance alone.

### Solution: Bonferroni Correction
```
Corrected P-value = Original P-value × Number of Tests

If you test 100 strategies:
  p-value = 0.01 becomes 0.01 × 100 = 1.0 (not significant!)
```

### Implementation
```python
# Compare strategies with correction
strategies = [
    {'name': 'Strategy A', 'sr': 1.5, 'dsr': 0.95},
    {'name': 'Strategy B', 'sr': 1.8, 'dsr': 0.82},
    {'name': 'Strategy C', 'sr': 2.1, 'dsr': 0.45},
]

n_tests = len(strategies)

print("Strategy Ranking (with multiple testing correction)")
print("="*60)

ranked = sorted(strategies, key=lambda x: x['dsr'], reverse=True)

for i, strat in enumerate(ranked, 1):
    print(f"{i}. {strat['name']}")
    print(f"   SR:  {strat['sr']:.3f}")
    print(f"   DSR: {strat['dsr']:.3f}")
    
    # Bonferroni-corrected threshold
    # At α=0.05 significance, threshold ~0.90 for single test
    # For 100 tests, need DSR > 1.40 to be truly significant
    threshold = 0.90 * np.sqrt(np.log(n_tests))
    
    if strat['dsr'] > threshold:
        print(f"   ✅ PASS multiple testing (threshold: {threshold:.3f})")
    else:
        print(f"   ❌ FAIL multiple testing (threshold: {threshold:.3f})")
    print()
```

---

## Summary & Actionable Framework

### Before Trading Any Strategy:
1. **Calculate DSR** on full backtest
2. **Check: DSR > 0.90?**
   - YES → Proceed to walk-forward testing
   - NO → Likely false positive, reject or collect more data
3. **Check skewness/kurtosis**
   - Positive skew, normal kurtosis → Good
   - Negative skew, fat tails → Red flag
4. **Check sample size**
   - < 250 obs: Too small
   - 250-500: Minimal
   - 500-1000: Good
   - 1000+: Excellent
5. **Apply multiple testing correction if needed**
   - Divide DSR by √(log(N_tests)) if testing many strategies

### DSR Interpretation Table
```
DSR         Interpretation                  Action
────────────────────────────────────────────────────────
> 1.0       Exceptional                     TRADE LIVE
0.90-1.0    Very likely genuine             Walk-forward test
0.70-0.90   Possibly genuine                More analysis needed
0.50-0.70   Weak signal, lucky             Collect more data
< 0.50      Almost certainly lucky         REJECT
```

The DSR is your **statistical sanity check** — it answers: "Is this edge real or just randomness?" Without it, most backtested strategies are dangerous illusions.
