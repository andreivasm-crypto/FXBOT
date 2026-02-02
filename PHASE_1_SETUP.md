# PHASE 1: DATA COLLECTION SETUP

**Goal:** Get 1-year historical forex data from your IB account into a local SQLite database.

**Timeline:** 5 minutes
**Effort:** 2 commands (one-time setup)

---

## What You're Doing

1. **Clone the repo** (one-time)
   ```bash
   git clone https://github.com/andreivasm-crypto/forex-smc-system.git
   cd forex-smc-system
   ```

2. **Activate your venv** (every session)
   ```bash
   source venv/bin/activate
   ```

3. **Run the data collector** (one-time)
   ```bash
   python3 code/data_collectors/ib_collector.py
   ```

**That's it.**

---

## Prerequisites

✅ Python 3.11 virtual environment (you just created)
✅ Packages installed: `pandas`, `numpy`, `ibapi`, `yfinance` (you just did this)
✅ TWS running on your Mac (background, can minimize)
✅ API enabled in TWS

### Check TWS API is Enabled

1. Open TWS (if not already running)
2. **Edit → Global Configuration → API → Settings**
3. Ensure:
   - ✅ **Enable ActiveX and Socket Clients** = checked
   - ✅ **Socket port** = 7497
   - ✅ **Read-only API** = unchecked (we need read+write)

---

## What the Script Does

`ib_collector.py` will:

1. **Connect** to your TWS on `127.0.0.1:7497` (local, no internet needed)
2. **Fetch** 1 year of daily OHLCV data for:
   - EUR/USD
   - GBP/USD
   - AUD/USD
   - USD/JPY
3. **Save** to: `data/forex_1year.db` (SQLite)
4. **Verify** data was saved correctly

---

## Running It

```bash
# Activate venv
source venv/bin/activate

# Run the collector
python3 code/data_collectors/ib_collector.py
```

**Expected output:**
```
======================================================================
FOREX SMC SYSTEM - IB DATA COLLECTOR
======================================================================
Account: DUK476547
Connection: 127.0.0.1:7497
Pairs: EUR/USD, GBP/USD, AUD/USD, USD/JPY
======================================================================
[INFO] Connecting to TWS at 127.0.0.1:7497...
[✓] Connected to TWS
[→] Requesting EUR/USD historical data (1 year, daily)...
[→] Requesting GBP/USD historical data (1 year, daily)...
[→] Requesting AUD/USD historical data (1 year, daily)...
[→] Requesting USD/JPY historical data (1 year, daily)...
[INFO] Waiting for all data requests to complete...
[✓] EUR/USD: Received 252 bars (20240203 to 20250203)
[✓] GBP/USD: Received 252 bars (20240203 to 20250203)
[✓] AUD/USD: Received 252 bars (20240203 to 20250203)
[✓] USD/JPY: Received 252 bars (20240203 to 20250203)

[INFO] Saving data to: /path/to/data/forex_1year.db
[✓] Saved 1008 total rows to SQLite

[VERIFICATION] Data in database:
  AUD/USD: 252 bars
  EUR/USD: 252 bars
  GBP/USD: 252 bars
  USD/JPY: 252 bars

[✓] SUCCESS: Data collection complete!
[✓] Database: /path/to/data/forex_1year.db
```

---

## Troubleshooting

### "Could not connect to TWS"
- Make sure TWS is running (you should see it in the taskbar/dock)
- Check API is enabled (Edit → Global Configuration → API → Settings)
- Make sure port is 7497
- Try restarting TWS

### "No historical data received"
- Wait 30+ seconds (first request can be slow)
- Check your IB subscription includes forex quotes
- Verify you're in US trading hours (data request faster during market hours)

### "UNIQUE constraint failed: pair, date"
- This is normal (means data already exists)
- Script skips duplicates automatically

---

## Next Steps (After Data Collection)

Once `data/forex_1year.db` is created:

1. **Phase 2** (I handle): Build backtesting system
   - SMC indicators
   - Vision analyzer
   - Walk-forward optimization
   
2. **Week 3-4**: Review results
   - I'll show you backtest results
   - You approve which strategies to test in paper trading

3. **Week 5+**: Paper trading validation
   - Test on your IB paper account
   - Ensure real-world results match backtest

---

## Questions?

If anything breaks or is unclear, just tell me. This should be straightforward.

**Ready to run the data collector?**
