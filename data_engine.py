import pandas as pd
import numpy as np
import yfinance as yf

def fetch_base_data(interval='1d'):
    """
    Fetches BTC and SOL data with built-in crash protection.
    """
    try:
        # Fetching Solana (SOL-USD)
        sol = yf.Ticker("SOL-USD")
        sol_df = sol.history(period="60d", interval=interval)
        
        # Fetching Bitcoin (BTC-USD)
        btc = yf.Ticker("BTC-USD")
        btc_df = btc.history(period="60d", interval=interval)
        
        # Validation Check
        if sol_df.empty or btc_df.empty:
            return None, 0, None, False
            
        sol_p = sol_df['Close'].iloc[-1]
        btc_p = btc_df['Close'].iloc[-1]
        
        # Clean data for the app
        sol_df.columns = [c.lower() for c in sol_df.columns]
        btc_df.columns = [c.lower() for c in btc_df.columns]
        
        return sol_df, sol_p, btc_df, True
    except Exception as e:
        # If internet fails, return 'None' so app.py uses its 2026 backup data
        return None, 135.84, None, False
