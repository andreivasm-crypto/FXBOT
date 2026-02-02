# Risk Management Framework

## Core Principle
**You don't trade to make money. You trade to not lose money.** Perfect position sizing beats perfect entries.

---

## 1. Position Sizing Algorithms

### Method 1: Fixed Percentage Risk (Beginner-Friendly)

**Rule:** Risk the same % of account on every trade.

```
Position Size = (Account Balance × Risk %) / Stop Loss (pips)

Example:
  Account:          $10,000
  Risk % per trade: 2%
  Stop Loss:        50 pips
  
  Position Size = ($10,000 × 0.02) / (50 × $0.10/pip)
                = $200 / $5
                = 0.04 lots (4,000 units on micro-lot)
```

**Pros:** Simple, consistent, psychological comfort
**Cons:** Ignores volatility (same risk on EUR/USD and GBPJPY?)

```python
def fixed_percent_position_sizing(account_balance, risk_pct, 
                                   stop_loss_pips, pip_value):
    """
    Args:
        account_balance: Current account value
        risk_pct: % of account to risk per trade (1-2% typical)
        stop_loss_pips: Distance to stop loss
        pip_value: Value per pip ($1 for 1 lot EUR/USD, etc.)
    
    Returns:
        position_size: Lot size to trade
    """
    risk_amount = account_balance * (risk_pct / 100)
    position_size = risk_amount / (stop_loss_pips * pip_value)
    return position_size

# Example
position = fixed_percent_position_sizing(
    account_balance=10000,
    risk_pct=2,
    stop_loss_pips=50,
    pip_value=1.0
)
print(f"Position Size: {position:.3f} lots")  # 0.004 lots = 4,000 units
```

### Method 2: Kelly Criterion (Optimal Growth)

**Formula:** Adjust position based on edge strength and win rate.

```
Kelly % = (Win% × Avg_Win - Loss% × Avg_Loss) / Avg_Win

Where:
  Win% = Probability of win (0.55 = 55%)
  Avg_Win = Average winning trade size
  Loss% = Probability of loss (0.45)
  Avg_Loss = Average losing trade size

Position Size = (Kelly % / 2) × Account

Note: Use Kelly/2 (fractional Kelly) for safety in real trading
```

```python
def kelly_criterion_position_sizing(win_rate, avg_win, avg_loss, 
                                     account_balance, kelly_fraction=0.5):
    """
    Calculate optimal position size using Kelly Criterion.
    
    Args:
        win_rate: Win percentage (0.55 = 55%)
        avg_win: Average winning trade (in pips or $)
        avg_loss: Average losing trade (in pips or $)
        account_balance: Current account
        kelly_fraction: Safety factor (0.25 = quarter Kelly, 0.5 = half Kelly)
    
    Returns:
        kelly_pct: % of account to risk
        position_size: Adjusted position size
    """
    loss_rate = 1 - win_rate
    
    # Basic Kelly
    kelly_pct = (win_rate * avg_win - loss_rate * avg_loss) / avg_win
    
    # Apply safety fraction (fractional Kelly)
    kelly_pct *= kelly_fraction
    
    # Ensure not > 100%
    kelly_pct = min(kelly_pct, 0.25)  # Cap at 25% for safety
    
    return kelly_pct, kelly_pct * account_balance

# Example
win_rate = 0.58
avg_win = 120  # pips
avg_loss = 50  # pips
account = 10000

kelly_pct, position_risk = kelly_criterion_position_sizing(
    win_rate, avg_win, avg_loss, account, kelly_fraction=0.5
)

print(f"Kelly % (full): {kelly_pct / 0.5:.2%}")
print(f"Kelly % (half): {kelly_pct:.2%}")
print(f"Position Size: ${position_risk:.2f}")
```

### Method 3: Volatility-Based Position Sizing

**Idea:** Trade smaller in high volatility, larger in low volatility.

```
Position Size = Target_Risk / (Current_ATR × Adjustment_Factor)

Where:
  Current_ATR = Average True Range (volatility measure)
  Target_Risk = Fixed dollar amount willing to risk
  Adjustment_Factor = Converts ATR to position size
```

```python
def volatility_adjusted_position_sizing(target_risk_dollars, current_atr, 
                                        pip_value, atr_multiplier=2.0):
    """
    Adjust position based on current market volatility.
    
    High ATR (volatile) → smaller position
    Low ATR (quiet)     → larger position
    """
    # Set stop loss at ATR * multiplier (e.g., 2x current volatility)
    stop_loss_pips = current_atr * atr_multiplier
    
    # Calculate position
    position_size = target_risk_dollars / (stop_loss_pips * pip_value)
    
    return position_size, stop_loss_pips

# Example
atr = 45  # Current ATR in pips
target_risk = 200  # Risk $200 per trade
pip_value = 1.0  # $1 per pip for 1 lot

position, stop = volatility_adjusted_position_sizing(
    target_risk_dollars=target_risk,
    current_atr=atr,
    pip_value=pip_value,
    atr_multiplier=2.0
)

print(f"Current ATR: {atr} pips")
print(f"Stop Loss: {stop:.0f} pips")
print(f"Position Size: {position:.4f} lots")
print(f"Expected Risk: ${target_risk}")
```

### Method 4: Optimal f (Maximum Risk Per Trade)

**Used in:** Professional/algorithmic trading

```
Optimal f = (Winners - Losers × AvgLoss/AvgWin) / Largest Loss

Position Size = Account × f / Largest_Drawdown
```

```python
def optimal_f_position_sizing(trade_history, account_balance):
    """
    Calculate position size using Optimal f approach.
    
    Args:
        trade_history: List of trades (positive for wins, negative for losses)
        account_balance: Current account
    """
    # Find largest loss (drawdown)
    largest_loss = min(trade_history)
    
    # Calculate average win/loss
    wins = [t for t in trade_history if t > 0]
    losses = [t for t in trade_history if t < 0]
    
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    
    num_wins = len(wins)
    num_losses = len(losses)
    
    # Optimal f calculation
    optimal_f = (num_wins - num_losses * (avg_loss / avg_win)) / abs(largest_loss)
    optimal_f = max(0.01, min(optimal_f, 0.25))  # Constrain 1-25%
    
    position_size = account_balance * optimal_f / abs(largest_loss)
    
    return optimal_f, position_size

# Example
trade_results = [50, 120, -40, 85, 95, -50, 110, -35, 60, 100]
account = 10000

opt_f, position = optimal_f_position_sizing(trade_results, account)

print(f"Optimal f: {opt_f:.2%}")
print(f"Recommended Position Size: ${position:.2f}")
```

---

## 2. Stop-Loss Placement Techniques

### Technique 1: Support/Resistance Based

```
Long Entry:  Place stop just below nearest support level
Short Entry: Place stop just above nearest resistance level

Example (Long):
  Entry:      1.0890
  Support:    1.0855
  Stop Loss:  1.0845 (10 pips below support for margin)
  
  Risk:       45 pips
```

### Technique 2: ATR-Based Stop

```
Stop Loss = Entry Price - (ATR × Multiplier)

Multiplier:
  Conservative (more trades, more wins): 2.0
  Moderate (balanced):                   2.5
  Aggressive (fewer trades, bigger wins):3.0
  
Example:
  Entry:      1.0890
  ATR(14):    40 pips
  Multiplier: 2.5
  
  Stop Loss = 1.0890 - (40 × 2.5) = 1.0890 - 100 = 1.0790
  Risk:       100 pips
```

### Technique 3: Pivot-Based Stop

```
Use daily/weekly pivots as natural stop zones.

Daily Pivot = (High + Low + Close) / 3
R1 = 2×Pivot - Low
S1 = 2×Pivot - High

For long: Stop at S1 or S2
For short: Stop at R1 or R2
```

### Technique 4: Order Block Method (SMC)

```
Stop just below/above institutional order block accumulation zone.

Bullish: Stop below order block low (typically 20-50 pips)
Bearish: Stop above order block high (typically 20-50 pips)

Most tight stops = highest probability setups
```

```python
class StopLossManager:
    """Determine optimal stop loss placement"""
    
    @staticmethod
    def support_resistance_stop(price, support, resistance, 
                                position_type='long', buffer_pips=10):
        """Support/resistance based stops"""
        if position_type == 'long':
            stop = support - buffer_pips
        else:  # short
            stop = resistance + buffer_pips
        
        return stop
    
    @staticmethod
    def atr_based_stop(entry_price, atr_value, multiplier=2.5, 
                       position_type='long'):
        """ATR-based stops"""
        if position_type == 'long':
            stop = entry_price - (atr_value * multiplier)
        else:  # short
            stop = entry_price + (atr_value * multiplier)
        
        return stop
    
    @staticmethod
    def calculate_risk_reward(entry, stop, target, position_type='long'):
        """Calculate risk/reward ratio"""
        if position_type == 'long':
            risk = entry - stop
            reward = target - entry
        else:
            risk = stop - entry
            reward = entry - target
        
        rr_ratio = reward / risk if risk > 0 else 0
        
        return {
            'risk_pips': risk,
            'reward_pips': reward,
            'rr_ratio': rr_ratio,
            'acceptable': rr_ratio >= 1.5  # Minimum 1.5:1
        }

# Usage
manager = StopLossManager()

# ATR-based stop
entry = 1.0890
atr = 40
stop = manager.atr_based_stop(entry, atr, multiplier=2.5, position_type='long')
target = entry + (entry - stop) * 2  # 2:1 RR

rr_analysis = manager.calculate_risk_reward(entry, stop, target, position_type='long')
print(f"Stop Loss: {stop:.4f}")
print(f"Risk/Reward: {rr_analysis['rr_ratio']:.2f}:1")
```

---

## 3. Profit-Taking Levels (1:1, 1:2, 1:3+)

### Graduated Exit Strategy

```python
class ProfitTakingManager:
    """Manage profit taking with graduated exit levels"""
    
    def __init__(self, entry_price, stop_loss, position_type='long'):
        self.entry = entry_price
        self.stop = stop_loss
        self.position_type = position_type
        
        # Calculate risk
        if position_type == 'long':
            self.risk = entry_price - stop_loss
        else:
            self.risk = stop_loss - entry_price
    
    def calculate_targets(self):
        """Calculate graduated TP levels"""
        if self.position_type == 'long':
            tp1 = self.entry + self.risk * 1.0  # 1:1
            tp2 = self.entry + self.risk * 2.0  # 2:1
            tp3 = self.entry + self.risk * 3.0  # 3:1
        else:  # short
            tp1 = self.entry - self.risk * 1.0
            tp2 = self.entry - self.risk * 2.0
            tp3 = self.entry - self.risk * 3.0
        
        return {
            'tp1_1to1': tp1,
            'tp2_2to1': tp2,
            'tp3_3to1': tp3
        }
    
    def exit_plan(self, total_position=1.0):
        """Suggested exit sizes"""
        targets = self.calculate_targets()
        
        return {
            'tp1_price': targets['tp1_1to1'],
            'tp1_exit': total_position * 0.5,      # 50%
            'tp2_price': targets['tp2_2to1'],
            'tp2_exit': total_position * 0.30,     # 30%
            'tp3_price': targets['tp3_3to1'],
            'tp3_exit': 'Trailing stop or manual',  # 20% with trailing
            'description': '50% at 1:1, 30% at 2:1, 20% with trailing'
        }
    
    def print_plan(self, total_position=1.0):
        """Pretty print the plan"""
        plan = self.exit_plan(total_position)
        
        print("="*60)
        print("PROFIT TAKING PLAN")
        print("="*60)
        print(f"\nEntry:        {self.entry:.4f}")
        print(f"Stop Loss:    {self.stop:.4f}")
        print(f"Risk/Trade:   {self.risk:.4f}")
        print(f"Position:     {total_position:.4f} lots")
        print(f"\n1️⃣  TARGET 1 (1:1 Risk/Reward)")
        print(f"    Price:    {plan['tp1_price']:.4f}")
        print(f"    Exit:     {plan['tp1_exit']:.4f} lots (50%)")
        print(f"\n2️⃣  TARGET 2 (2:1 Risk/Reward)")
        print(f"    Price:    {plan['tp2_price']:.4f}")
        print(f"    Exit:     {plan['tp2_exit']:.4f} lots (30%)")
        print(f"\n3️⃣  TARGET 3 (3:1+ Risk/Reward)")
        print(f"    Price:    {plan['tp3_price']:.4f}")
        print(f"    Exit:     Trailing stop (20%)")
        print("="*60)

# Usage
manager = ProfitTakingManager(entry_price=1.0890, stop_loss=1.0845, 
                              position_type='long')
manager.print_plan(total_position=0.1)
```

### Trailing Stop for Remainder

Once at Target 2, activate trailing stop on remaining position:

```python
class TrailingStopManager:
    """Manage trailing stops for remaining position"""
    
    def __init__(self, entry_price, initial_stop, atr_value):
        self.entry = entry_price
        self.current_stop = initial_stop
        self.atr = atr_value
        self.highest_price = entry_price
    
    def update_trailing_stop(self, current_price, trail_multiplier=1.5):
        """
        Update stop loss following price action
        
        Stop = Current High - (ATR × Multiplier)
        """
        if current_price > self.highest_price:
            self.highest_price = current_price
            # New trailing stop
            self.current_stop = current_price - (self.atr * trail_multiplier)
        
        return self.current_stop

# Usage
ts = TrailingStopManager(1.0890, 1.0845, 40)

# Price moves to 1.0950
new_stop = ts.update_trailing_stop(1.0950, trail_multiplier=1.5)
print(f"New Trailing Stop: {new_stop:.4f}")
```

---

## 4. Maximum Drawdown Monitoring

### Drawdown Calculation

```python
class DrawdownMonitor:
    """Track and monitor account drawdown"""
    
    def __init__(self, starting_balance, max_dd_allowed_pct=20):
        self.starting = starting_balance
        self.current = starting_balance
        self.peak = starting_balance
        self.max_dd_allowed = max_dd_allowed_pct
        
        self.drawdown_history = []
    
    def calculate_drawdown(self, new_balance):
        """Calculate current drawdown %"""
        self.current = new_balance
        
        if new_balance > self.peak:
            self.peak = new_balance
        
        drawdown = (self.peak - new_balance) / self.peak * 100
        self.drawdown_history.append(drawdown)
        
        return drawdown
    
    def is_over_limit(self, current_balance):
        """Check if drawdown exceeded limit"""
        dd = self.calculate_drawdown(current_balance)
        return dd > self.max_dd_allowed, dd
    
    def recovery_needed(self):
        """Calculate recovery needed to reach peak"""
        dd = (self.peak - self.current) / self.current * 100
        return dd

# Usage
monitor = DrawdownMonitor(starting_balance=10000, max_dd_allowed_pct=20)

# After some losses
balance_after_trades = 8500
over_limit, drawdown = monitor.is_over_limit(balance_after_trades)

print(f"Current Drawdown: {drawdown:.2f}%")
if over_limit:
    print(f"❌ Exceeded limit of 20%! STOP TRADING")
    recovery = monitor.recovery_needed()
    print(f"Need {recovery:.2f}% gain to recover")
else:
    print(f"✅ Within limits")
```

### Drawdown Stop Rules

| Drawdown | Action |
|----------|--------|
| 0-10% | Continue trading normally |
| 10-15% | Reduce position size to 50% |
| 15-20% | Reduce position size to 25% |
| > 20% | STOP TRADING - Review strategy |

---

## 5. Risk Per Trade Calculations

### Comprehensive Risk Calculation

```python
class RiskCalculator:
    """Calculate all risk metrics for a trade"""
    
    @staticmethod
    def calculate_risk_metrics(entry, stop_loss, target, position_size,
                               pip_value=1.0, account_balance=10000):
        """
        Calculate complete risk profile for a trade.
        
        Args:
            entry: Entry price
            stop_loss: Stop loss price
            target: Target/TP price
            position_size: Number of lots
            pip_value: Value per pip
            account_balance: Current account size
        """
        # Distance calculations
        risk_pips = abs(entry - stop_loss)
        reward_pips = abs(target - entry)
        
        # Dollar risk
        risk_dollars = risk_pips * pip_value * position_size
        reward_dollars = reward_pips * pip_value * position_size
        
        # Percentages
        risk_pct_of_account = (risk_dollars / account_balance) * 100
        reward_pct_of_account = (reward_dollars / account_balance) * 100
        
        # Ratios
        rr_ratio = reward_pips / risk_pips if risk_pips > 0 else 0
        
        return {
            'risk_pips': risk_pips,
            'reward_pips': reward_pips,
            'risk_dollars': risk_dollars,
            'reward_dollars': reward_dollars,
            'risk_pct_account': risk_pct_of_account,
            'reward_pct_account': reward_pct_of_account,
            'rr_ratio': rr_ratio,
            'acceptable': {
                'risk_pct': risk_pct_of_account <= 2.5,  # Max 2.5% per trade
                'rr_ratio': rr_ratio >= 1.5               # Min 1.5:1
            }
        }
    
    @staticmethod
    def print_risk_report(metrics):
        """Pretty print risk analysis"""
        print("="*60)
        print("TRADE RISK ANALYSIS")
        print("="*60)
        print(f"\n💰 RISK METRICS")
        print(f"  Risk:              {metrics['risk_pips']:.0f} pips")
        print(f"  Reward:            {metrics['reward_pips']:.0f} pips")
        print(f"  Risk/Reward:       1:{metrics['rr_ratio']:.2f}")
        
        print(f"\n💵 DOLLAR IMPACT")
        print(f"  Risk Amount:       ${metrics['risk_dollars']:.2f}")
        print(f"  Potential Gain:    ${metrics['reward_dollars']:.2f}")
        print(f"  Risk % of Account: {metrics['risk_pct_account']:.2f}%")
        print(f"  Reward % Account:  {metrics['reward_pct_account']:.2f}%")
        
        print(f"\n✅ ACCEPTANCE")
        print(f"  Risk < 2.5%:       {'✅ PASS' if metrics['acceptable']['risk_pct'] else '❌ FAIL'}")
        print(f"  RR > 1.5:1:        {'✅ PASS' if metrics['acceptable']['rr_ratio'] else '❌ FAIL'}")
        
        if metrics['acceptable']['risk_pct'] and metrics['acceptable']['rr_ratio']:
            print(f"\n  ✅ TRADE APPROVED")
        else:
            print(f"\n  ❌ TRADE REJECTED")
        print("="*60)

# Usage
metrics = RiskCalculator.calculate_risk_metrics(
    entry=1.0890,
    stop_loss=1.0850,
    target=1.0970,
    position_size=0.1,
    pip_value=1.0,
    account_balance=10000
)

RiskCalculator.print_risk_report(metrics)
```

---

## Risk Management Checklist

```
BEFORE EVERY TRADE:

□ Position size calculated (fixed %, Kelly, or volatility-adjusted)
□ Stop loss placed (at support/ATR/OB)
□ Risk per trade ≤ 2% of account
□ Risk/Reward ratio ≥ 1.5:1
□ Account drawdown < 20%
□ Profit taking levels calculated (1:1, 2:1, 3:1)
□ Trailing stop parameters set (if applicable)
□ Trade logged with entry/SL/TP documented

CONTINUOUS:

□ Monitor current drawdown daily
□ Check each position's trailing stop
□ Review P&L weekly
□ Adjust position sizing if win rate changes
□ Rebalance when drawdown hits -15%

MONTHLY:

□ Calculate actual win rate vs expected
□ Review average win/loss ratio
□ Assess Kelly criterion adjustment needed
□ Review drawdown history
□ Make position sizing adjustments
```

---

## Summary: Risk Management Framework

**The Math That Makes Money:**
```
Long-term profit depends on three factors:

1. Win Rate (55-65%)     ← Execution, signal quality
2. Avg Win/Loss (1:2+)   ← Setup quality, exit discipline  
3. Risk Per Trade (2%)   ← Position sizing discipline

Even mediocre win rates profit with proper sizing.
Most traders fail on #3 — they risk 5-10% per trade.

Expect to win 50-60% of trades.
But with proper sizing and 1:2+ risk/reward:
→ You'll profit regardless of win rate above 40%.
```

**Position Sizing is your primary edge. Perfect entries + poor sizing = ruin. Mediocre entries + perfect sizing = wealth.**
