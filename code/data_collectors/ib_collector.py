#!/usr/bin/env python3
"""
IBDataCollector.py
Fetches multi-timeframe historical forex OHLCV data from Interactive Brokers TWS.

SETUP:
1. Ensure TWS is running and API is enabled (on port 7497)
2. Run: python3 ib_collector.py
3. Data saved to: ../data/forex_1year.db (SQLite)

PAIRS: EUR/USD, GBP/USD, AUD/USD, USD/JPY
TIMEFRAMES: 
  - Daily (1 day) - 1 year = 252 bars (HTF structure reference)
  - 4H (4 hours) - 1 year = ~1,008 bars (primary trading timeframe)
  - 1H (1 hour) - 6 months = ~2,000 bars (entry confirmation)
DURATION: 1 year daily, 1 year 4H, 6 months 1H
"""

import sqlite3
import time
from datetime import datetime, timedelta
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.utils import iswrapper
import pandas as pd
import sys
import os

# ============================================================================
# CONFIG (DRE's Account - Hardcoded for Security)
# ============================================================================
IB_HOST = "127.0.0.1"  # Local TWS socket
IB_PORT = 7497
IB_CLIENT_ID = 42
IB_ACCOUNT = "DUK476547"

# Pairs to fetch
FOREX_PAIRS = [
    ("EUR", "USD"),
    ("GBP", "USD"),
    ("AUD", "USD"),
    ("USD", "JPY"),
]

# Timeframes: (bar_size, duration_str, name)
# Daily: 1 year = 252 bars
# 4H: 1 year = ~1,008 bars
# 1H: 1 year = ~4,032 bars
TIMEFRAMES = [
    ("1 day", "1 Y", "DAILY"),
    ("4 hours", "1 Y", "4H"),
    ("1 hour", "6 M", "1H"),  # 6 months for 1H (saves time, still valid)
]

# ============================================================================
# DATA COLLECTOR
# ============================================================================
class ForexDataCollector(EWrapper, EClient):
    """Connects to TWS, fetches forex data, stores in SQLite."""

    def __init__(self):
        EClient.__init__(self, self)
        self.data = {}
        self.is_connected = False
        self.request_id = 10000
        self.db_path = None

    def connect_to_tws(self):
        """Connect to TWS on local socket."""
        print(f"[INFO] Connecting to TWS at {IB_HOST}:{IB_PORT}...")
        
        # Create message thread FIRST
        import threading
        api_thread = threading.Thread(target=self.run, daemon=True)
        api_thread.start()
        
        # Then connect
        self.connect(IB_HOST, IB_PORT, IB_CLIENT_ID)
        
        # Wait for connection callback
        print("[INFO] Waiting for connection callback...")
        time.sleep(4)  # Give it more time

    @iswrapper
    def connectionStatus(self, connected: bool, msg: str):
        """Called when connection status changes."""
        self.is_connected = connected
        print(f"[DEBUG] connectionStatus callback: connected={connected}, msg={msg}")
        if connected:
            print(f"[✓] Connected to TWS")
        else:
            print(f"[✗] Disconnected from TWS: {msg}")
    
    @iswrapper
    def error(self, req_id, error_code: int, error_string: str):
        """Called on error messages (most are just info from IB)."""
        # Ignore info messages (2104, 2106, 2158 are normal connection msgs)
        if error_code not in [2104, 2106, 2158]:
            print(f"[ERROR] Code {error_code}: {error_string}")
        # Set connected = True if we're receiving messages (means we're connected)
        if error_code in [2104, 2106, 2158]:
            self.is_connected = True

    def disconnect_from_tws(self):
        """Disconnect from TWS."""
        print("[INFO] Disconnecting from TWS...")
        self.disconnect()
        time.sleep(1)

    def create_forex_contract(self, pair_from, pair_to):
        """Create IB contract for forex pair."""
        contract = Contract()
        contract.symbol = pair_from
        contract.secType = "CASH"
        contract.currency = pair_to
        contract.exchange = "IDEALPRO"
        return contract

    def request_historical_data(self, contract, pair_name, timeframe_name, bar_size, duration):
        """Request historical OHLCV data for a pair + timeframe."""
        self.request_id += 1
        req_id = self.request_id

        # End date: today
        end_date = datetime.now().strftime("%Y%m%d %H:%M:%S")
        
        what_to_show = "MIDPOINT"  # Use midpoint for forex
        use_rth = 0  # Include extended trading hours

        print(f"[→] {pair_name} {timeframe_name:6s} ({duration}) ...", end="", flush=True)
        
        self.reqHistoricalData(
            req_id,
            contract,
            end_date,
            duration,
            bar_size,
            what_to_show,
            use_rth,
            1,  # formatDate: 1 = yyyyMMdd
            False,
            []
        )

        # Wait for data
        self.data[req_id] = {"pair": pair_name, "timeframe": timeframe_name, "bars": []}
        return req_id

    @iswrapper
    def historicalData(self, req_id: int, bar):
        """Called when a bar is received."""
        if req_id in self.data:
            self.data[req_id]["bars"].append({
                "date": bar.date,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            })

    @iswrapper
    def historicalDataEnd(self, req_id: int, start: str, end: str):
        """Called when historical data request is complete."""
        if req_id in self.data:
            pair = self.data[req_id]["pair"]
            timeframe = self.data[req_id]["timeframe"]
            bars = self.data[req_id]["bars"]
            print(f" ✓ {len(bars)} bars")

    def save_to_sqlite(self):
        """Save all collected data to SQLite database. Returns db_path."""
        # Get the project root (go up from code/data_collectors/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, "../../"))
        data_dir = os.path.join(project_root, "data")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        db_path = os.path.join(data_dir, "forex_1year.db")
        
        print(f"\n[INFO] Saving data to: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forex_ohlcv (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(pair, timeframe, date)
                )
            """)

            # Insert data for each pair + timeframe
            total_rows = 0
            for req_id, data in self.data.items():
                pair = data["pair"]
                timeframe = data["timeframe"]
                bars = data["bars"]
                
                for bar in bars:
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO forex_ohlcv
                            (pair, timeframe, date, open, high, low, close, volume)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            pair,
                            timeframe,
                            bar["date"],
                            bar["open"],
                            bar["high"],
                            bar["low"],
                            bar["close"],
                            bar["volume"]
                        ))
                        total_rows += 1
                    except sqlite3.IntegrityError:
                        pass  # Skip duplicates

            conn.commit()
            conn.close()
            
            print(f"[✓] Saved {total_rows} total rows to SQLite")
            
            # Verify data
            self.verify_sqlite_data(db_path)
            
            return db_path

        except Exception as e:
            print(f"[✗] Error saving to SQLite: {e}")
            raise

    def verify_sqlite_data(self, db_path):
        """Verify data was saved correctly."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT pair, timeframe, COUNT(*) as count
            FROM forex_ohlcv
            GROUP BY pair, timeframe
            ORDER BY pair, 
                     CASE timeframe 
                         WHEN 'DAILY' THEN 1 
                         WHEN '4H' THEN 2 
                         WHEN '1H' THEN 3 
                     END
        """)

        print("\n[VERIFICATION] Data in database:")
        for pair, timeframe, count in cursor.fetchall():
            print(f"  {pair:8s} {timeframe:6s}: {count:4d} bars")

        conn.close()


# ============================================================================
# MAIN
# ============================================================================
def main():
    """Fetch 1-year forex data from IB and save to SQLite."""
    
    print("=" * 70)
    print("FOREX SMC SYSTEM - IB DATA COLLECTOR (Multi-Timeframe)")
    print("=" * 70)
    print(f"Account: {IB_ACCOUNT}")
    print(f"Connection: {IB_HOST}:{IB_PORT}")
    print(f"Pairs: {', '.join([f'{p[0]}/{p[1]}' for p in FOREX_PAIRS])}")
    print(f"Timeframes: {', '.join([f'{tf[2]}' for tf in TIMEFRAMES])}")
    print(f"Total requests: {len(FOREX_PAIRS)} pairs × {len(TIMEFRAMES)} timeframes = {len(FOREX_PAIRS) * len(TIMEFRAMES)} requests")
    print("=" * 70)

    # Initialize collector
    collector = ForexDataCollector()
    
    try:
        # Connect to TWS
        collector.connect_to_tws()
        
        # Wait for connection handshake (IB sends market data messages as confirmation)
        print("[INFO] Waiting for TWS handshake...")
        time.sleep(5)
        
        print("[✓] Connected (proceeding with data requests)")

        # Request data for each pair + timeframe
        print("[INFO] Requesting data for 4 pairs × 3 timeframes = 12 requests...\n")
        req_ids = []
        
        for pair_from, pair_to in FOREX_PAIRS:
            contract = collector.create_forex_contract(pair_from, pair_to)
            pair_name = f"{pair_from}/{pair_to}"
            
            for bar_size, duration, tf_name in TIMEFRAMES:
                req_id = collector.request_historical_data(
                    contract, 
                    pair_name, 
                    tf_name,
                    bar_size,
                    duration
                )
                req_ids.append(req_id)

        # Wait for all requests to complete
        print("\n[INFO] Waiting for all data requests to complete (this can take 1-2 minutes)...")
        time.sleep(90)  # Longer timeout for 12 requests

        # Save to SQLite
        db_path = collector.save_to_sqlite()

        print("\n" + "="*70)
        print("[✓] SUCCESS: Multi-timeframe data collection complete!")
        print(f"[✓] Database: {db_path}")
        print("="*70)

    except Exception as e:
        print(f"\n[✗] ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Disconnect
        collector.disconnect_from_tws()


if __name__ == "__main__":
    main()
