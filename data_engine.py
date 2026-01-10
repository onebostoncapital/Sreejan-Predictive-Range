import pandas as pd
import numpy as np

# This part checks if the 'yfinance' tool is ready
try:
    import yfinance as yf
except ImportError:
    yf = None

def fetch_base_data(interval='1d'):
    if yf is None:
        # If the tool isn't ready, use our 2026 backup data
        return None, 135.84, None, False
        
    try:
        sol = yf.Ticker("SOL-USD")
        sol_df = sol.history(period="60d", interval=interval)
        btc = yf.Ticker("BTC-USD")
        btc_df = btc.history(period="60d", interval=interval)
        
        if sol_df.empty or btc_df.empty:
            return None, 135.84, None, False
            
        sol_p = sol_df['Close'].iloc[-1]
        btc_p = btc_df['Close'].iloc[-1]
        sol_df.columns = [c.lower() for c in sol_df.columns]
        btc_df.columns = [c.lower() for c in btc_df.columns]
        
        return sol_df, sol_p, btc_df, True
    except Exception:
        return None, 135.84, None, False
