#!/usr/bin/env python3
"""
Interactive Brokers Data Collector
Fetches historical forex data from your running TWS instance
Account: DUK476547
Connection: 127.0.0.1:7497
Client ID: 42
"""

import sqlite3
import pandas as pd
import time
import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import TickAttrib
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IBDataCollector(EWrapper, EClient):
    """Collect forex data from Interactive Brokers TWS"""
    
    def __init__(self, db_path='data/forex_1year.db'):
        EClient.__init__(self, self)
        self.data = {}
        self.db_path = db_path
        self.next_req_id = 1
        self.connected = False
        
        # Initialize database
        self._init_db()
        logger.info(f"Database initialized: {db_path}")
    
    def _init_db(self):
        """Create SQLite database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create OHLCV table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forex_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                UNIQUE(symbol, date)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def error(self, reqId, errorCode, errorString):
        """Handle errors from TWS"""
        logger.error(f"Error ID {reqId}: Code {errorCode} - {errorString}")
    
    def connectionClosed(self):
        """Called when TWS connection closes"""
        logger.warning("TWS connection closed")
        self.connected = False
    
    def nextValidId(self, orderId):
        """Called when connection establishes"""
        super().nextValidId(orderId)
        self.next_req_id = orderId
        self.connected = True
        logger.info(f"✅ Connected to TWS (Next Valid ID: {orderId})")
    
    def historicalData(self, reqId, bar):
        """Called for each historical bar from TWS"""
        if reqId not in self.data:
            self.data[reqId] = []
        
        self.data[reqId].append({
            'date': bar.date,
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume
        })
        
        logger.info(f"Received bar: {bar.date} - {bar.close:.4f}")
    
    def historicalDataEnd(self, reqId, start, end):
        """Called when all historical data is received"""
        logger.info(f"✅ Data request {reqId} complete: {len(self.data[reqId])} bars")
    
    def connect_to_tws(self):
        """Connect to TWS on localhost"""
        logger.info("Connecting to TWS at 127.0.0.1:7497...")
        
        try:
            self.connect("127.0.0.1", 7497, clientId=42)
            
            # Start reader thread
            thread = threading.Thread(target=self.run, daemon=True)
            thread.start()
            
            # Wait for connection
            timeout = 10
            start = time.time()
            while not self.connected and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                logger.info("✅ Connected to TWS successfully")
                return True
            else:
                logger.error("❌ Failed to connect to TWS (timeout)")
                return False
        
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def fetch_forex_data(self, symbol, duration='1 Y', barsize='4 hours'):
        """
        Fetch historical forex data
        
        Args:
            symbol: e.g., 'EUR.USD'
            duration: e.g., '1 Y' (1 year)
            barsize: e.g., '4 hours', '1 hour', '1 day'
        """
        logger.info(f"Fetching {symbol} ({duration}, {barsize})...")
        
        contract = Contract()
        contract.symbol = symbol.split('.')[0]
        contract.secType = 'CASH'
        contract.exchange = 'IDEALPRO'
        contract.currency = symbol.split('.')[1]
        
        req_id = self.next_req_id
        self.next_req_id += 1
        
        self.data[req_id] = []
        
        # Request historical data
        self.reqHistoricalData(
            reqId=req_id,
            contract=contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=barsize,
            whatToShow='MIDPOINT',
            useRTH=1,
            formatDate=1,
            keepUpToDate=False
        )
        
        # Wait for data
        timeout = 60
        start = time.time()
        while req_id not in self.data or len(self.data[req_id]) == 0:
            if (time.time() - start) > timeout:
                logger.error(f"❌ Timeout fetching {symbol}")
                return None
            time.sleep(0.1)
        
        return req_id
    
    def save_to_db(self, symbol, req_id):
        """Save fetched data to SQLite"""
        if req_id not in self.data or len(self.data[req_id]) == 0:
            logger.warning(f"No data to save for {symbol}")
            return False
        
        try:
            df = pd.DataFrame(self.data[req_id])
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prepare data
            df['symbol'] = symbol
            df = df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']]
            
            # Insert data
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT OR REPLACE INTO forex_data 
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', tuple(row))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Saved {len(df)} rows for {symbol} to database")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error saving data: {e}")
            return False
    
    def disconnect_from_tws(self):
        """Disconnect from TWS"""
        logger.info("Disconnecting from TWS...")
        self.disconnect()
        logger.info("✅ Disconnected")
    
    def validate_data(self, symbol):
        """Validate saved data quality"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql(
                f"SELECT * FROM forex_data WHERE symbol = '{symbol}' ORDER BY date",
                conn
            )
            conn.close()
            
            if len(df) == 0:
                logger.warning(f"No data found for {symbol}")
                return False
            
            # Check for issues
            nan_count = df.isnull().sum().sum()
            invalid_candles = ((df['low'] > df['high']).sum() + 
                              (df['close'] > df['high']).sum() + 
                              (df['close'] < df['low']).sum())
            
            logger.info(f"\n=== Data Validation: {symbol} ===")
            logger.info(f"Total candles: {len(df)}")
            logger.info(f"NaN values: {nan_count}")
            logger.info(f"Invalid candles: {invalid_candles}")
            logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
            
            if nan_count > 0 or invalid_candles > 0:
                logger.warning("⚠️  Data quality issues detected")
                return False
            
            logger.info("✅ Data validation passed")
            return True
        
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            return False


def main():
    """Main execution"""
    logger.info("\n" + "="*50)
    logger.info("FOREX DATA COLLECTOR - INTERACTIVE BROKERS")
    logger.info("="*50 + "\n")
    
    # Initialize collector
    collector = IBDataCollector(db_path='data/forex_1year.db')
    
    # Connect to TWS
    if not collector.connect_to_tws():
        logger.error("Failed to connect to TWS. Exiting.")
        return
    
    # Wait for connection to stabilize
    time.sleep(2)
    
    # Fetch data for each pair
    pairs = ['EUR.USD', 'GBP.USD', 'AUD.USD', 'USD.JPY']
    
    for pair in pairs:
        logger.info(f"\n--- Fetching {pair} ---")
        
        # Request data
        req_id = collector.fetch_forex_data(pair, duration='1 Y', barsize='4 hours')
        
        if req_id is not None:
            # Save to database
            collector.save_to_db(pair, req_id)
            
            # Validate
            collector.validate_data(pair)
        
        # Wait between requests
        time.sleep(2)
    
    # Disconnect
    collector.disconnect_from_tws()
    
    logger.info("\n" + "="*50)
    logger.info("✅ DATA COLLECTION COMPLETE")
    logger.info("="*50 + "\n")


if __name__ == '__main__':
    main()
