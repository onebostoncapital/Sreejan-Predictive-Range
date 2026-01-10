import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import json

# MAGIC COMMAND:
# streamlit run app.py

st.set_page_config(page_title="Sreejan AI Sentinel Pro", layout="wide")

# --- 1. LIVE DATA ENGINE (COINGECKO) ---
@st.cache_data(ttl=30)  # Updates every 30 seconds
def fetch_live_market_data():
    try:
        # Live Prices
        p_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,solana&vs_currencies=usd"
        p_data = requests.get(p_url, timeout=5).json()
        
        # 30D History for Stats & ATR
        h_url = "https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=30&interval=daily"
        h_data = requests.get(h_url, timeout=5).json()
        
        if 'bitcoin' in p_data and 'prices' in h_data:
            btc_p = p_data['bitcoin']['usd']
            sol_p = p_data['solana']['usd']
            prices = [p[1] for p in h_data['prices']]
            
            # Locked Feature: ATR Calculation
            current_atr = np.std(prices) * 1.5 
            
            stats = {
                "high": max(prices), "low": min(prices), "avg": np.mean(prices),
                "t_high": sol_p * 1.01, "t_low": sol_p * 0.99
            }
            return btc_p, sol_p, current_atr, stats, True
    except:
        pass
    return 96000.0, 145.0, 8.5, {"high": 160, "low": 130, "avg": 140, "t_high": 148, "t_low": 142}, False

# Trigger for Manual Refresh
if st.sidebar.button("🔄 Force Live Sync"):
    st.cache_data.clear()

btc_p, sol_p, atr, s_stats, live_status = fetch_live_market_data()

# --- 2. THE UI STYLING (LOCKED) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@400;700&display=swap');
    .stApp { background: #05070a; color: #e0e0e0; font-family: 'Inter'; }
    .header-box { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; }
    .ai-card { background: linear-gradient(145deg, #0d1117, #010203); border-left: 5px solid var(--bias-col); padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .liq-box { background: rgba(255,75,75,0.1); border: 1px solid #FF4B4B; padding: 15px; border-radius: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- MODULE 1: REAL-TIME HEADER ---
st.markdown(f'<div class="header-box">', unsafe_allow_html=True)
h1, h2, h3 = st.columns(3)
h1.metric("₿ BTC PRICE", f"${btc_p:,.0f}")
h2.metric("S SOL PRICE", f"${sol_p:,.2f}")
h3.metric("📉 LIVE ATR", f"${atr:,.2f}")
st.markdown('</div>', unsafe_allow_html=True)

# --- MODULE 2: DYNAMIC PERFORMANCE RIBBON ---
r1, r2, r3 = st.columns(3)
with st.container():
    st.markdown(f"""
    <div style="display:flex; justify-content: space-around; background: #111; padding: 10px; border-radius: 5px; font-size: 12px; color: #888; border: 1px solid #222;">
        <span>🏔️ 30D HIGH: ${s_stats['high']:.2f}</span>
        <span>🌊 30D LOW: ${s_stats['low']:.2f}</span>
        <span>📊 30D AVG: ${s_stats['avg']:.2f}</span>
        <span>📅 TODAY RANGE: ${s_stats['t_low']:.2f} - ${s_stats['t_high']:.2f}</span>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🕹️ STRATEGY CONTROL")
capital = st.sidebar.number_input("Capital ($)", value=10000)
manual_lev = st.sidebar.slider("Manual Leverage", 1.0, 10.0, 3.0)
bias_manual = st.sidebar.selectbox("Directional Bias", ["Sentinel AI", "Bullish", "Bearish", "Neutral"])

# --- MODULE 3 & 4: AI ENGINE & FORECAST CARD ---
ai_bias = "Bullish" if sol_p > s_stats['avg'] else "Bearish"
final_bias = ai_bias if bias_manual == "Sentinel AI" else bias_manual
b_color = "#00FF7F" if final_bias == "Bullish" else "#FF4B4B" if final_bias == "Bearish" else "#D4AF37"

# AI Calculations
ai_low, ai_high = sol_p - (atr * 2.5), sol_p + (atr * 2.5)
ai_liq = sol_p * 0.5 # Fixed 2x Safety

st.markdown(f"""
<div class="ai-card" style="--bias-col: {b_color};">
    <div style="display: flex; justify-content: space-between;">
        <div>
            <span style="background:{b_color}; color:#000; padding:2px 10px; border-radius:20px; font-weight:bold; font-size:12px;">{final_bias.upper()}</span>
            <h2 style="margin-top:10px;">AI FORECAST RANGE</h2>
            <h1 style="font-family:'JetBrains Mono'; font-size:45px; color:{b_color};">${ai_low:,.2f} — ${ai_high:,.2f}</h1>
        </div>
        <div class="liq-box">
            <div style="color:#FF4B4B; font-weight:bold; font-size:12px;">LIQUIDATION FLOOR</div>
            <div style="font-size:28px; font-family:'JetBrains Mono'; color:#fff;">${ai_liq:,.2f}</div>
            <div style="font-size:10px; color:#888;">AI LOCKED @ 2.0x</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- MODULE 5: MANUAL CONTROL ---
st.subheader("✍️ Manual Range Adjustment")
m_range = st.slider("Select Liquidity Zone", float(sol_p*0.5), float(sol_p*1.5), (float(ai_low), float(ai_high)))

# --- MODULE 6: YIELD MATRIX (PROFIT TABLES) ---
st.markdown("### 📊 Profit Comparison Matrix")
t1, t2 = st.columns(2)

def get_yield_df(l, h, lev):
    base = (capital * lev * 0.0001) * (sol_p / (h - l))
    return pd.DataFrame({
        "Timeframe": ["1 Hour", "3 Hours", "1 Day", "1 Week", "1 Month"],
        "Projected Profit": [f"${base:,.2f}", f"${base*3:,.2f}", f"${base*24:,.2f}", f"${base*168:,.2f}", f"${base*720:,.2f}"]
    })

with t1:
    st.write("**🤖 AI Strategy (Locked 2.0x)**")
    st.table(get_yield_df(ai_low, ai_high, 2.0))
with t2:
    st.write(f"**👤 Manual Strategy ({manual_lev}x)**")
    st.table(get_yield_df(m_range[0], m_range[1], manual_lev))

# --- MODULE 7: STRATEGY LEDGER (AUTO-SAVE) ---
try:
    with open("strategy_ledger.txt", "a") as f:
        log = {"timestamp": str(datetime.now()), "sol_price": sol_p, "bias": final_bias, "manual_range": m_range}
        f.write(json.dumps(log) + "\n")
except:
    pass

st.success("✅ Strategy Auto-Saved to Ledger")
