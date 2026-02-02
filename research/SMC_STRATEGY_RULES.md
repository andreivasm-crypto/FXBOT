# Smart Money Concepts (SMC) Strategy Specifics

## Foundational Theory

**Smart Money Concept (SMC)** trading is based on institutional price action patterns. It assumes large financial institutions (hedge funds, banks) manipulate liquidity pools before major moves.

**Core premise:** Price goes to where the most liquidity lies, creating predictable patterns before impulsive retail moves.

---

## 1. Liquidity Sweep Mechanics & Detection

### What is a Liquidity Sweep?

**Definition:** When price moves beyond a recent swing high/low (taking out stops) BEFORE reversing in the intended direction.

```
Example: BULLISH SWEEP (sets up for uptrend)

Price chart:
        ↗ Market reverses UP (main move)
       /
      / [Sweep zone - traders' stops taken]
     ↗
    / ← Swing High (stops placed here)
  ↗ 
 / Previous uptrend

Mechanics:
1. Price approaches recent swing high
2. Breaks above swing high (taking out bulls' stops)
3. Creates panic selling/liquidation
4. Creates liquidity for institutional entry
5. Reverses down and up goes
```

### Detection Rules

```python
class LiquiditySweepDetector:
    """Detect liquidity sweeps in price data"""
    
    def __init__(self, data, lookback=20):
        """
        Args:
            data: OHLCV DataFrame
            lookback: bars to look back for swing identification
        """
        self.data = data.copy()
        self.lookback = lookback
    
    def identify_swings(self):
        """Identify swing highs and lows"""
        high = self.data['high']
        low = self.data['low']
        
        # Swing High: point where high is greater than lookback bars before and after
        swing_highs = []
        swing_lows = []
        
        for i in range(self.lookback, len(self.data) - self.lookback):
            # Swing High
            if high.iloc[i] == high.iloc[i-self.lookback:i+self.lookback+1].max():
                swing_highs.append({
                    'bar': i,
                    'price': high.iloc[i],
                    'date': self.data.index[i]
                })
            
            # Swing Low
            if low.iloc[i] == low.iloc[i-self.lookback:i+self.lookback+1].min():
                swing_lows.append({
                    'bar': i,
                    'price': low.iloc[i],
                    'date': self.data.index[i]
                })
        
        return swing_highs, swing_lows
    
    def detect_bullish_sweep(self, recent_bars=5):
        """
        Bullish sweep: Price breaks above recent swing high
        then reverses down (creating liquidity)
        """
        swing_highs, _ = self.identify_swings()
        
        if len(swing_highs) < 2:
            return []
        
        # Get most recent swing high
        last_sh = swing_highs[-1]
        recent_high = self.data['high'].iloc[-recent_bars:].max()
        
        # Check if price broke above it
        if recent_high > last_sh['price']:
            # How much above?
            breakout_pips = recent_high - last_sh['price']
            
            # Check if it closed back below (reversal)
            current_close = self.data['close'].iloc[-1]
            
            if current_close < last_sh['price']:
                return [{
                    'type': 'bullish_sweep',
                    'swing_high': last_sh['price'],
                    'breakout_high': recent_high,
                    'breakout_pips': breakout_pips,
                    'sweep_confirmed': True
                }]
        
        return []
    
    def detect_bearish_sweep(self, recent_bars=5):
        """
        Bearish sweep: Price breaks below recent swing low
        then reverses up (creating liquidity for shorts)
        """
        _, swing_lows = self.identify_swings()
        
        if len(swing_lows) < 2:
            return []
        
        last_sl = swing_lows[-1]
        recent_low = self.data['low'].iloc[-recent_bars:].min()
        
        if recent_low < last_sl['price']:
            sweep_pips = last_sl['price'] - recent_low
            current_close = self.data['close'].iloc[-1]
            
            if current_close > last_sl['price']:
                return [{
                    'type': 'bearish_sweep',
                    'swing_low': last_sl['price'],
                    'breakout_low': recent_low,
                    'sweep_pips': sweep_pips,
                    'sweep_confirmed': True
                }]
        
        return []

# Usage
detector = LiquiditySweepDetector(daily_data)
bullish = detector.detect_bullish_sweep()
bearish = detector.detect_bearish_sweep()
```

### Liquidity Sweep Characteristics
- **Depth:** 20-100 pips below/above swing (market structure dependent)
- **Speed:** Often 1-3 candles
- **Volume:** Usually spike on breakout bar
- **Reversal:** Sharp reversal back through swing is KEY signal

---

## 2. Fair Value Gap (FVG) Identification & Sizing

### What is FVG?

**Definition:** An imbalance between supply and demand created by a gap between candles (usually on lower timeframes).

```
BULLISH FVG (gap up):

High₂ ─────┐
          │ ← FAIR VALUE GAP (imbalance)
          │   (price likely to return to fill)
Low₁   ────┘

Bar 1: Down candle (creates supply)
Bar 2: Up candle that gaps up from Bar 1
→ Gap is the FVG (unfilled supply/demand)

BEARISH FVG (gap down):

High₁ ─────┐
          │ ← FAIR VALUE GAP
          │
Low₂   ────┘

Bar 1: Up candle
Bar 2: Down candle that gaps down
```

### Detection Algorithm
```python
class FVGDetector:
    """Detect Fair Value Gaps in price data"""
    
    def __init__(self, data, min_gap_pips=5):
        """
        Args:
            data: OHLCV DataFrame
            min_gap_pips: Minimum gap size to consider (in pips)
        """
        self.data = data.copy()
        self.min_gap = min_gap_pips
    
    def detect_bullish_fvg(self):
        """
        Bullish FVG: Low of current bar > High of 2 bars ago
        """
        fvgs = []
        
        for i in range(2, len(self.data)):
            low_current = self.data['low'].iloc[i]
            high_2bars_ago = self.data['high'].iloc[i-2]
            
            gap = low_current - high_2bars_ago
            gap_pips = gap / 0.0001  # assuming forex (adjust for stock)
            
            if gap_pips >= self.min_gap:
                fvgs.append({
                    'type': 'bullish_fvg',
                    'bar': i,
                    'date': self.data.index[i],
                    'bottom': high_2bars_ago,      # Top of gap
                    'top': low_current,             # Bottom of gap
                    'gap_size': gap_pips,
                    'mid_price': (high_2bars_ago + low_current) / 2
                })
        
        return fvgs
    
    def detect_bearish_fvg(self):
        """
        Bearish FVG: High of current bar < Low of 2 bars ago
        """
        fvgs = []
        
        for i in range(2, len(self.data)):
            high_current = self.data['high'].iloc[i]
            low_2bars_ago = self.data['low'].iloc[i-2]
            
            gap = low_2bars_ago - high_current
            gap_pips = gap / 0.0001
            
            if gap_pips >= self.min_gap:
                fvgs.append({
                    'type': 'bearish_fvg',
                    'bar': i,
                    'date': self.data.index[i],
                    'top': low_2bars_ago,           # Top of gap
                    'bottom': high_current,         # Bottom of gap
                    'gap_size': gap_pips,
                    'mid_price': (low_2bars_ago + high_current) / 2
                })
        
        return fvgs
    
    def fvg_sizing(self, fvg_list):
        """
        Categorize FVGs by size (institutional vs retail)
        """
        sized_fvgs = []
        
        for fvg in fvg_list:
            size = fvg['gap_size']
            
            if size < 10:
                category = 'micro'  # Retail/noise
                bias = 0.3  # Low probability of fill
            elif 10 <= size < 30:
                category = 'minor'  # Retail
                bias = 0.5
            elif 30 <= size < 100:
                category = 'major'  # Institutional
                bias = 0.7
            else:
                category = 'massive'  # Strong institutional move
                bias = 0.85
            
            fvg['size_category'] = category
            fvg['fill_probability'] = bias
            sized_fvgs.append(fvg)
        
        return sized_fvgs

# Usage
fvg_detector = FVGDetector(daily_data, min_gap_pips=8)
bullish_fvgs = fvg_detector.detect_bullish_fvg()
bearish_fvgs = fvg_detector.detect_bearish_fvg()

all_fvgs = bullish_fvgs + bearish_fvgs
all_fvgs = fvg_detector.fvg_sizing(all_fvgs)

# Sort by probability of fill
high_prob_fvgs = [f for f in all_fvgs if f['fill_probability'] > 0.65]
```

---

## 3. Order Blocks: Placement, Validation, Use Cases

### What is an Order Block?

**Definition:** A zone where institutional orders (buyers/sellers) likely accumulated before a major price move.

```
BULLISH ORDER BLOCK (accumulation zone):

        ↗ Impulsive move UP (clear proof of buying)
       /  ^
      /   │ Price is now higher (buyers won)
     /    │
    └─────┴─ ORDER BLOCK
      (accumulation area)
    
    - Price broke out of this zone
    - This is where smart money accumulated
    - If price returns = likely buyer support
```

### Identification Rules
```python
class OrderBlockDetector:
    """Detect institutional order block zones"""
    
    @staticmethod
    def find_bullish_order_block(data, lookback=3):
        """
        OB formation:
        1. Consolidation/accumulation (multiple candles in range)
        2. Followed by CLEAR BREAKOUT UP
        3. Price doesn't return immediately = confirms buyers
        """
        order_blocks = []
        
        for i in range(lookback, len(data) - 1):
            # Look for tight range (consolidation)
            range_start = i - lookback
            range_end = i
            
            consolidation = data['high'].iloc[range_start:range_end]
            consolidation_range = consolidation.max() - consolidation.min()
            
            # Next bar should break out UP significantly
            next_bar = data.iloc[i + 1]
            breakout = next_bar['close'] > consolidation.max() * 1.002  # 20 pips
            
            if consolidation_range < (consolidation.mean() * 0.01) and breakout:
                order_blocks.append({
                    'type': 'bullish_ob',
                    'bar': i,
                    'low': consolidation.min(),
                    'high': consolidation.max(),
                    'breakout_price': next_bar['close']
                })
        
        return order_blocks
    
    @staticmethod
    def validate_order_block(ob, current_price, data_since_formation):
        """
        Validate if OB is still valid:
        - Price must not close below OB (for bulls)
        - Multiple tests of zone = stronger
        """
        if ob['type'] == 'bullish_ob':
            # Check if price still above OB low
            if current_price > ob['low']:
                # Check how many times price tested this level
                tests = (data_since_formation['low'] <= ob['high']).sum()
                
                return {
                    'valid': True,
                    'strength': min(tests / 3, 1.0),  # Stronger with more tests
                    'support_level': ob['low'],
                    'target': ob['high'] + (ob['high'] - ob['low'])  # Projection
                }
        
        return {'valid': False}
```

### Use Cases
| Scenario | Usage | Probability |
|----------|-------|-------------|
| Price approaching OB from above | Support, buy pullback | 65% |
| Multiple tests of OB | Strengthens signal | +15% for each test |
| FVG fills into OB | Continuation likely | 70% |
| OB broken decisively | Trend reversal signal | 60% |

---

## 4. HSHS Vol Div MTF (Higher Swing High/Low Divergences Multi-TimeFrame)

### What is HSHS Vol Div?

**HSHS** = Higher Swing Highs/Higher Swing Lows (uptrend structure)
**Vol Div** = Volume Divergence (declining volume on new highs = weakening)
**MTF** = Multi-TimeFrame confirmation

### Exact Criteria

```python
class HSHSVolDivDetector:
    """
    Detect weakness in uptrends when price makes higher highs
    but volume DECREASES (divergence)
    """
    
    def __init__(self, data_daily, data_hourly, min_swings=3):
        self.daily = data_daily
        self.hourly = data_hourly
        self.min_swings = min_swings
    
    def find_hshs_pattern(self, timeframe_data):
        """Find succession of higher swing highs"""
        patterns = []
        
        # Find swing highs
        highs = timeframe_data['high']
        volumes = timeframe_data['volume']
        
        swing_highs = []
        for i in range(2, len(highs) - 2):
            if highs.iloc[i] > highs.iloc[i-2] and \
               highs.iloc[i] > highs.iloc[i-1] and \
               highs.iloc[i] > highs.iloc[i+1] and \
               highs.iloc[i] > highs.iloc[i+2]:
                swing_highs.append({
                    'bar': i,
                    'price': highs.iloc[i],
                    'volume': volumes.iloc[i]
                })
        
        # Identify HSHS (3+ higher highs)
        if len(swing_highs) >= self.min_swings:
            for i in range(len(swing_highs) - 2):
                is_hshs = (swing_highs[i+1]['price'] > swing_highs[i]['price']) and \
                          (swing_highs[i+2]['price'] > swing_highs[i+1]['price'])
                
                if is_hshs:
                    patterns.append({
                        'swings': [swing_highs[i], swing_highs[i+1], swing_highs[i+2]],
                        'is_hshs': True
                    })
        
        return patterns
    
    def detect_volume_divergence(self, pattern):
        """
        Volume divergence: Price makes higher highs but volume DECREASES
        
        This signals weakening buying pressure = reversal risk
        """
        swings = pattern['swings']
        volumes = [s['volume'] for s in swings]
        prices = [s['price'] for s in swings]
        
        # Check if prices increasing but volumes decreasing
        price_trend = prices[-1] > prices[0]  # Higher high
        vol_trend = volumes[-1] < volumes[0]  # Lower volume
        
        if price_trend and vol_trend:
            div_strength = (volumes[0] - volumes[-1]) / volumes[0]  # 0-1
            return {
                'divergence_detected': True,
                'divergence_strength': div_strength,
                'interpretation': 'Weakening uptrend, reversal risk'
            }
        
        return {'divergence_detected': False}
    
    def mtf_confirmation(self):
        """
        Multi-timeframe confirmation:
        - Daily shows HSHS Vol Div (weak uptrend)
        - Hourly shows similar pattern (timing for entry)
        """
        daily_patterns = self.find_hshs_pattern(self.daily)
        hourly_patterns = self.find_hshs_pattern(self.hourly)
        
        if daily_patterns and hourly_patterns:
            daily_div = self.detect_volume_divergence(daily_patterns[-1])
            hourly_div = self.detect_volume_divergence(hourly_patterns[-1])
            
            if daily_div['divergence_detected'] and hourly_div['divergence_detected']:
                return {
                    'mtf_confirmed': True,
                    'daily_strength': daily_div['divergence_strength'],
                    'hourly_strength': hourly_div['divergence_strength'],
                    'signal': 'SHORT BIAS - Weak uptrend, likely correction'
                }
        
        return {'mtf_confirmed': False}
```

---

## 5. Entry Rules Checklist (ALL CONDITIONS REQUIRED)

### BULLISH SETUP Entry Checklist

```python
class SMCBullishEntryValidator:
    """Validate all conditions for bullish SMC entry"""
    
    def validate_all_conditions(self, data, current_bar_idx):
        """Returns True ONLY if ALL conditions are met"""
        
        conditions = {
            'liquidity_sweep': self._check_bullish_sweep(data, current_bar_idx),
            'fvg_setup': self._check_bullish_fvg(data, current_bar_idx),
            'order_block_support': self._check_order_block(data, current_bar_idx),
            'price_location': self._check_price_location(data, current_bar_idx),
            'volume_confirmation': self._check_volume(data, current_bar_idx),
            'mtf_alignment': self._check_mtf_alignment(data, current_bar_idx)
        }
        
        # ALL must be True
        all_conditions_met = all(conditions.values())
        
        return all_conditions_met, conditions
    
    def _check_bullish_sweep(self, data, idx):
        """✓ Condition 1: Bullish liquidity sweep completed"""
        recent = data.iloc[max(0, idx-5):idx]
        swing_high = recent['high'].max()
        current_low = data['low'].iloc[idx]
        
        # Price swept above swing, then came back = sweep happened
        return current_low < swing_high and data['close'].iloc[idx-1] < swing_high
    
    def _check_bullish_fvg(self, data, idx):
        """✓ Condition 2: FVG (gap) formed after sweep"""
        # Gap should be present in recent bars
        bar_2_ago = data.iloc[idx-2]
        current = data.iloc[idx]
        
        fvg_formed = current['low'] > bar_2_ago['high']
        return fvg_formed
    
    def _check_order_block(self, data, idx):
        """✓ Condition 3: Order block in accumulation zone"""
        recent_range = data.iloc[max(0, idx-10):idx]
        block_low = recent_range['low'].min()
        block_high = recent_range['high'].max()
        
        # Price should respect the block as support
        current_price = data['close'].iloc[idx]
        return current_price > block_low and current_price < block_high
    
    def _check_price_location(self, data, idx):
        """✓ Condition 4: Price is in demand zone (not overbought)"""
        # RSI < 70, or not at swing high
        swing_high = data['high'].iloc[max(0, idx-20):idx].max()
        current = data['close'].iloc[idx]
        
        # Not too extended above recent highs
        return (current < swing_high * 1.01)
    
    def _check_volume(self, data, idx):
        """✓ Condition 5: Volume confirms (high on sweep bar)"""
        sweep_bar_vol = data['volume'].iloc[idx-2]  # Bar that swept
        avg_vol = data['volume'].iloc[max(0, idx-20):idx].mean()
        
        return sweep_bar_vol > (avg_vol * 1.3)  # At least 30% above average
    
    def _check_mtf_alignment(self, data, idx):
        """✓ Condition 6: Multi-timeframe aligned (higher TF bullish)"""
        # In real impl: check daily trend is up, hourly setting up entry
        # Simplified here: trend should be UP on recent bars
        recent_5 = data['close'].iloc[max(0, idx-5):idx]
        return recent_5.iloc[-1] > recent_5.iloc[0]

# Usage
validator = SMCBullishEntryValidator()
ready, conditions = validator.validate_all_conditions(hourly_data, current_idx)

if ready:
    print("✅ ALL CONDITIONS MET - ENTER LONG")
    print(f"Details: {conditions}")
else:
    print("❌ Missing conditions:")
    for cond, met in conditions.items():
        if not met:
            print(f"   - {cond}")
```

---

## 6. Exit Rules & Profit-Taking Mechanics

### EXIT RULE 1: Stop Loss (Hard Exit)
```
Placement: Just below order block support (or FVG mid-price)

Example:
  OB Low:     1.0850
  Stop Loss:  1.0840 (10 pips below)
  
  Logic: If price closes below OB = smart money stops are taken
         = Original thesis invalidated
```

### EXIT RULE 2: Take Profit (Graduated)
```
TARGET 1 (1:1 Risk/Reward):
  Entry:      1.0875
  Stop Loss:  1.0840
  Risk:       35 pips
  Target 1:   1.0910 (1:1)
  Exit:       Close 50% of position

TARGET 2 (1:2 Risk/Reward):
  Entry:      1.0875
  Stop Loss:  1.0840
  Risk:       35 pips
  Target 2:   1.0945 (2:1)
  Exit:       Close 30% of position

TARGET 3 (1:3+ Risk/Reward):
  Entry:      1.0875
  Risk:       35 pips
  Target 3:   1.0980+ (3:1+)
  Exit:       Close remaining on reversal signal or trailing stop
```

### EXIT RULE 3: Time-Based Exit
```
If target not hit within max time:
- Intraday scalp: 4-8 hours
- Swing trade: 5-10 days
- Position trade: 2-4 weeks

Exit if time exceeded (time decay, edge lost)
```

### EXIT RULE 4: Reversal Signal (Protective)
```
Exit immediately if:
- Price creates lower low (for longs)
- Price breaks support order block
- Volume spikes on opposite direction
- RSI shows extreme reversal (70+ for shorts)
```

```python
class SMCExitManager:
    """Manage exits for SMC trades"""
    
    def __init__(self, entry_price, stop_loss, risk_amount, entry_time):
        self.entry = entry_price
        self.sl = stop_loss
        self.risk = risk_amount
        self.entry_time = entry_time
        self.targets_hit = 0
        self.position_size = 1.0
    
    def check_take_profit(self, current_price, risk_reward_ratio):
        """Check if TP levels should close positions"""
        
        profit = current_price - self.entry
        
        if risk_reward_ratio >= 1.0 and self.targets_hit == 0:
            # 50% close at 1:1
            return {'close_amount': 0.5, 'reason': 'TP1 (1:1 RR)'}
        
        elif risk_reward_ratio >= 2.0 and self.targets_hit == 1:
            # 30% close at 2:1
            return {'close_amount': 0.3, 'reason': 'TP2 (2:1 RR)'}
        
        elif risk_reward_ratio >= 3.0:
            # Trailing stop for rest
            return {'close_amount': 0, 'reason': 'Trailing stop active'}
        
        return {'close_amount': 0, 'reason': 'No TP triggered'}
    
    def check_stop_loss(self, current_price):
        """Hard stop loss"""
        if current_price <= self.sl:
            return {'exit': True, 'reason': 'Stop loss hit'}
        return {'exit': False}
    
    def check_time_exit(self, current_time, max_hours=8):
        """Exit if time exceeded"""
        hours_elapsed = (current_time - self.entry_time).total_seconds() / 3600
        
        if hours_elapsed > max_hours:
            return {'exit': True, 'reason': f'Time exit ({hours_elapsed:.1f}h)'}
        return {'exit': False}
    
    def check_reversal_exit(self, last_high, last_low, current_price):
        """Exit on reversal signal"""
        # For longs: exit if lower low forms
        if current_price < last_low:
            return {'exit': True, 'reason': 'Reversal (new low)'}
        return {'exit': False}

# Usage in live trading
def manage_smc_trade(trade, market_data, current_time):
    """Main trade management loop"""
    current_price = market_data['current_price']
    
    # Check stops first
    sl_check = trade.check_stop_loss(current_price)
    if sl_check['exit']:
        return {'action': 'CLOSE_ALL', 'reason': sl_check['reason']}
    
    # Check time exit
    time_check = trade.check_time_exit(current_time)
    if time_check['exit']:
        return {'action': 'CLOSE_ALL', 'reason': time_check['reason']}
    
    # Check TP levels
    rr = (current_price - trade.entry) / trade.risk
    tp_check = trade.check_take_profit(current_price, rr)
    if tp_check['close_amount'] > 0:
        return {
            'action': 'CLOSE_PARTIAL',
            'close_pct': tp_check['close_amount'],
            'reason': tp_check['reason']
        }
    
    return {'action': 'HOLD', 'rr': rr}
```

---

## 7. Win Rate Expectations vs Risk-Reward

### Statistical Reality

```
Win Rate:       55-65% (realistic SMC)
Avg Win/Loss:   1:2 to 1:3 (professional setup)

Expected Return:
  = (Win% × Avg_Win) - (Loss% × Avg_Loss)
  = (0.60 × 100) - (0.40 × 50)
  = 60 - 20
  = +40 (profitable!)

Even with 55% WR:
  = (0.55 × 100) - (0.45 × 50)
  = 55 - 22.5
  = +32.5 (still profitable!)
```

### Target Metrics
| Metric | Target | Reality |
|--------|--------|---------|
| Win Rate | 55-65% | 50-70% varies |
| Risk/Reward | 1:2+ | 1:2 to 1:5 |
| Profit Factor | > 1.5 | 1.8-2.5 |
| Avg Win (pips) | 80-150 | 60-200 |
| Avg Loss (pips) | 30-50 | 20-60 |

### Example Realistic Month
```
Trades Taken:        20
Winning Trades:      11 (55%)
Losing Trades:       9  (45%)

Avg Win:             120 pips
Avg Loss:            50 pips

Month P&L:
  = (11 × 120) - (9 × 50)
  = 1,320 - 450
  = +870 pips

At 0.1 lot (10,000 units):
  = 870 pips × $1 per pip
  = $870 profit (on $500 risk account = 174% ROI)

At 1 lot (100,000 units):
  = 870 pips × $10 per pip
  = $8,700 profit (on $5,000 risk account = 174% ROI)
```

---

## Summary: Full SMC Trade Setup

```
SETUP CHECKLIST:

1. ✅ Liquidity Sweep executed
   └─ Stops taken, momentum exhausted

2. ✅ FVG formed after sweep
   └─ Imbalance created, price to return

3. ✅ Order Block identified
   └─ Institutional accumulation zone

4. ✅ HSHS Vol Div (or price location)
   └─ Confirmation of institutional interest

5. ✅ Volume spike on entry bar
   └─ Institutions entering confirmed

6. ✅ Multi-timeframe alignment
   └─ Daily bullish, hourly setup ready

EXECUTION:
  Entry:  First 4H candle close above FVG midpoint
  Stop:   Just below OB support (typically 40-60 pips)
  TP1:    1:1 RR (close 50%)
  TP2:    2:1 RR (close 30%)
  TP3:    Trail remaining 20%

EXPECTATION:
  Win Rate:         58%
  Avg Win:          120 pips
  Avg Loss:         50 pips
  Risk/Reward:      1:2.4
  Profit Factor:    2.0+
```

This is **institutional-grade methodology** combining market structure analysis with smart money concepts.
