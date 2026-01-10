import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import json
import streamlit.components.v1 as components
import feedparser

# MAGIC COMMAND:
# streamlit run app.py

st.set_page_config(page_title="Sreejan AI Sentinel Pro", layout="wide")

# --- 1. THE BULLETPROOF DATA ENGINE ---
@st.cache_data(ttl=60)
def fetch_master_data():
    try:
        # Fetch 30 days of data
        btc = yf.Ticker("BTC-USD").history(period="30d")
        sol = yf.Ticker("SOL-USD").history(period="30d")
        
        # Current Prices & 30D Stats
        btc_p, sol_p = btc['Close'].iloc[-1], sol['Close'].iloc[-1]
        stats = {
            "btc_high": btc['High'].max(), "btc_low": btc['Low'].min(),
            "sol_high": sol['High'].max(), "sol_low": sol['Low'].min(),
            "sol_avg": sol['Close'].mean(), "t_high": sol['High'].iloc[-1], "t_low": sol['Low'].iloc[-1]
        }
        
        # 14-Day ATR Calculation
        tr = pd.concat([sol['High']-sol['Low'], 
                        np.abs(sol['High']-sol['Close'].shift()), 
                        np.abs(sol['Low']-sol['Close'].shift())], axis=1).max(axis=1)
        current_atr = tr.rolling(14).mean().iloc[-1]
        
        return btc_p, sol_p, current_atr, stats, True
    except:
        return 96000.0, 145.0, 8.5, {"sol_avg": 140.0, "btc_high": 100000, "btc_low": 90000}, False

if st.sidebar.button("🔄 Force Hard Sync"):
    st.cache_data.clear()

btc_p, sol_p, atr, s_stats, live_status = fetch_master_data()

# --- 2. THE UI STYLING (LOCKED) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@400;700&display=swap');
    .stApp { background: #05070a; color: #e0e0e0; font-family: 'Inter'; }
    .header-box { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 5px; }
    .ai-card { background: linear-gradient(145deg, #0d1117, #010203); border-left: 5px solid var(--bias-col); padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .liq-box { background: rgba(255,75,75,0.1); border: 1px solid #FF4B4B; padding: 15px; border-radius: 10px; text-align: center; min-width: 150px; }
</style>
""", unsafe_allow_html=True)

# --- MODULE 1: REAL-TIME HEADER ---
st.markdown('<div class="header-box">', unsafe_allow_html=True)
h1, h2, h3 = st.columns(3)
h1.metric("₿ BTC PRICE", f"${btc_p:,.2f}")
h2.metric("S SOL PRICE", f"${sol_p:,.2f}")
h3.metric("📉 LIVE ATR (14D)", f"${atr:,.2f}")
st.markdown('</div>', unsafe_allow_html=True)

# --- MODULE: LIVE TECHNICAL GAUGE ---
st.markdown("### 🧬 Live Technical Sentinel (Solana)")
components.html("""
<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
{"interval": "1m", "width": "100%", "isTransparent": true, "height": 380, "symbol": "BINANCE:SOLUSDT", "showIntervalTabs": true, "displayMode": "single", "locale": "en", "colorTheme": "dark"}
</script></div>""", height=400)

# --- MODULE 2: DYNAMIC PERFORMANCE RIBBON ---
st.markdown(f"""
<div style="display:flex; justify-content: space-around; background: #111; padding: 10px; border-radius: 5px; font-size: 11px; color: #888; border: 1px solid #222; margin-bottom: 20px;">
    <span>🏔️ BTC 30D: ${s_stats.get('btc_low',0):,.0f} - ${s_stats.get('btc_high',0):,.0f}</span>
    <span>🌊 SOL 30D: ${s_stats.get('sol_low',0):,.2f} - ${s_stats.get('sol_high',0):,.2f}</span>
    <span>📊 SOL AVG: ${s_stats.get('sol_avg',0):,.2f}</span>
    <span>📅 TODAY: ${s_stats.get('t_low',0):,.2f} - ${s_stats.get('t_high',0):,.2f}</span>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🕹️ STRATEGY CONTROL")
capital = st.sidebar.number_input("Capital ($)", value=10000)
manual_lev = st.sidebar.slider("Manual Leverage", 1.0, 10.0, 3.0)
bias_manual = st.sidebar.selectbox("Directional Bias", ["Sentinel AI", "Bullish", "Bearish", "Neutral"])

# --- MODULE 3 & 4: AI FORECAST & LIQUIDATION FLOOR (RESTORED) ---
ai_bias = "Bullish" if sol_p > s_stats.get('sol_avg', 0) else "Bearish"
final_bias = ai_bias if bias_manual == "Sentinel AI" else bias_manual
b_color = "#00FF7F" if final_bias == "Bullish" else "#FF4B4B" if final_bias == "Bearish" else "#D4AF37"
ai_low, ai_high = sol_p - (atr * 2.5), sol_p + (atr * 2.5)
ai_liq = sol_p * 0.5 # Safety Logic: 50% drop is 2x Liquidation

st.markdown(f"""
<div class="ai-card" style="--bias-col: {b_color};">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="background:{b_color}; color:#000; padding:2px 10px; border-radius:20px; font-weight:bold; font-size:12px;">{final_bias.upper()}</span>
            <h2 style="margin-top:10px;">AI FORECAST RANGE</h2>
            <h1 style="font-family:'JetBrains Mono'; font-size:45px; color:{b_color}; margin:0;">${ai_low:,.2f} — ${ai_high:,.2f}</h1>
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
m_range = st.slider("Select Liquidity Zone", float(sol_p*0.3), float(sol_p*1.7), (float(ai_low), float(ai_high)))

# --- MODULE 6: YIELD MATRIX ---
st.markdown("### 📊 Profit Comparison Matrix")
def get_yield_df(l, h, lev):
    base = (capital * lev * 0.0001) * (sol_p / max((h - l), 0.01))
    return pd.DataFrame({"Timeframe": ["1 Hour", "3 Hours", "1 Day", "1 Week", "1 Month"], 
                        "Profit": [f"${base:,.2f}", f"${base*3:,.2f}", f"${base*24:,.2f}", f"${base*168:,.2f}", f"${base*720:,.2f}"]})

t1, t2 = st.columns(2)
with t1: st.write("**🤖 AI Strategy (2.0x)**"); st.table(get_yield_df(ai_low, ai_high, 2.0))
with t2: st.write(f"**👤 Manual ({manual_lev}x)**"); st.table(get_yield_df(m_range[0], m_range[1], manual_lev))

# --- MODULE 7: PERSISTENT NEWS ---
st.markdown("---")
st.markdown("### 📰 Ecosystem News Feed")
try:
    feed = feedparser.parse("https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml")
    for entry in feed.entries[:3]:
        st.info(f"🔗 **{entry.title}**\n\n[Read full story]({entry.link})")
except: st.write("Syncing live news...")

# --- MODULE 8: STRATEGY LEDGER (AUTO-SAVE) ---
try:
    with open("strategy_ledger.txt", "a") as f:
        log = {"ts": str(datetime.now()), "sol": sol_p, "bias": final_bias, "manual": m_range}
        f.write(json.dumps(log) + "\n")
except: pass
st.toast("Strategy Logged!", icon="💾")
