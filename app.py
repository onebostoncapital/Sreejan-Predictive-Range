import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import json
import streamlit.components.v1 as components
import feedparser

# MAGIC COMMAND:
# streamlit run app.py

st.set_page_config(page_title="Sreejan AI Sentinel Pro", layout="wide")

# --- 1. BULLETPROOF DATA ENGINE (LOCKED) ---
@st.cache_data(ttl=60)
def fetch_master_data():
    try:
        # Fetching 30 days of data for BTC and SOL
        btc = yf.Ticker("BTC-USD").history(period="30d")
        sol = yf.Ticker("SOL-USD").history(period="30d")
        
        # Current Prices
        btc_p = btc['Close'].iloc[-1]
        sol_p = sol['Close'].iloc[-1]
        
        # 30-Day Stats (Master Rules)
        stats = {
            "btc_30d_high": btc['High'].max(),
            "btc_30d_low": btc['Low'].min(),
            "sol_30d_high": sol['High'].max(),
            "sol_30d_low": sol['Low'].min(),
            "sol_30d_avg": sol['Close'].mean(),
            "today_high": sol['High'].iloc[-1],
            "today_low": sol['Low'].iloc[-1]
        }
        
        # Accurate ATR Calculation (Standard 14-period)
        high_low = sol['High'] - sol['Low']
        high_close = np.abs(sol['High'] - sol['Close'].shift())
        low_close = np.abs(sol['Low'] - sol['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        current_atr = tr.rolling(14).mean().iloc[-1]
        
        return btc_p, sol_p, current_atr, stats, True
    except Exception as e:
        st.error(f"Data Sync Error: {e}")
        return 96000.0, 145.0, 8.5, {"sol_30d_avg": 140.0}, False

# Force Refresh Button
if st.sidebar.button("🔄 Hard Sync Market Data"):
    st.cache_data.clear()

btc_p, sol_p, atr, s_stats, live_status = fetch_master_data()

# --- 2. THE UI STYLING (LOCKED) ---
st.markdown("""
<style>
    .stApp { background: #05070a; color: #e0e0e0; font-family: 'Inter'; }
    .header-box { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 5px; }
    .ai-card { background: linear-gradient(145deg, #0d1117, #010203); border-left: 5px solid var(--bias-col); padding: 25px; border-radius: 15px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- MODULE 1: REAL-TIME HEADER (BTC, SOL, ATR) ---
st.markdown('<div class="header-box">', unsafe_allow_html=True)
h1, h2, h3 = st.columns(3)
h1.metric("₿ BTC PRICE", f"${btc_p:,.2f}")
h2.metric("S SOL PRICE", f"${sol_p:,.2f}")
h3.metric("📉 LIVE ATR (14D)", f"${atr:,.2f}")
st.markdown('</div>', unsafe_allow_html=True)

# --- MODULE: LIVE TECHNICAL GAUGE (SEPARATE) ---
components.html("""
<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
{"interval": "1m", "width": "100%", "isTransparent": true, "height": 380, "symbol": "BINANCE:SOLUSDT", "showIntervalTabs": true, "displayMode": "single", "locale": "en", "colorTheme": "dark"}
</script></div>""", height=400)

# --- MODULE 2: DYNAMIC PERFORMANCE RIBBON (LOCKED) ---
st.markdown(f"""
<div style="display:flex; justify-content: space-around; background: #111; padding: 10px; border-radius: 5px; font-size: 11px; color: #888; border: 1px solid #222; margin-bottom: 20px;">
    <span>₿ BTC 30D: ${s_stats.get('btc_30d_low',0):,.0f} - ${s_stats.get('btc_30d_high',0):,.0f}</span>
    <span>S SOL 30D: ${s_stats.get('sol_30d_low',0):,.2f} - ${s_stats.get('sol_30d_high',0):,.2f}</span>
    <span>📊 SOL AVG: ${s_stats.get('sol_30d_avg',0):,.2f}</span>
    <span>📅 TODAY: ${s_stats.get('today_low',0):,.2f} - ${s_stats.get('today_high',0):,.2f}</span>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR & LOGIC ---
st.sidebar.header("🕹️ STRATEGY CONTROL")
capital = st.sidebar.number_input("Capital ($)", value=10000)
manual_lev = st.sidebar.slider("Manual Leverage", 1.0, 10.0, 3.0)
bias_manual = st.sidebar.selectbox("Directional Bias", ["Sentinel AI", "Bullish", "Bearish", "Neutral"])

# --- MODULE 3 & 4: AI ENGINE & FORECAST ---
ai_bias = "Bullish" if sol_p > s_stats.get('sol_30d_avg', 0) else "Bearish"
final_bias = ai_bias if bias_manual == "Sentinel AI" else bias_manual
b_color = "#00FF7F" if final_bias == "Bullish" else "#FF4B4B" if final_bias == "Bearish" else "#D4AF37"
ai_low, ai_high = sol_p - (atr * 2.5), sol_p + (atr * 2.5)

st.markdown(f"""<div class="ai-card" style="--bias-col: {b_color};">
    <span style="background:{b_color}; color:#000; padding:2px 10px; border-radius:20px; font-weight:bold; font-size:12px;">{final_bias.upper()}</span>
    <h2 style="margin-top:10px;">AI FORECAST RANGE</h2>
    <h1 style="font-size:45px; color:{b_color};">${ai_low:,.2f} — ${ai_high:,.2f}</h1>
</div>""", unsafe_allow_html=True)

# --- MODULE 5 & 6: MANUAL & YIELD MATRIX ---
st.subheader("✍️ Manual adjustment & Profit Matrix")
m_range = st.slider("Liquidity Zone", float(sol_p*0.3), float(sol_p*1.7), (float(ai_low), float(ai_high)))

def get_yield_df(l, h, lev):
    base = (capital * lev * 0.0001) * (sol_p / max((h - l), 0.01))
    return pd.DataFrame({"Timeframe": ["1 Hour", "1 Day", "1 Week", "1 Month"], "Profit": [f"${base:,.2f}", f"${base*24:,.2f}", f"${base*168:,.2f}", f"${base*720:,.2f}"]})

c1, c2 = st.columns(2)
with c1: st.write("🤖 **AI Strategy (2.0x)**"); st.table(get_yield_df(ai_low, ai_high, 2.0))
with c2: st.write(f"👤 **Manual ({manual_lev}x)**"); st.table(get_yield_df(m_range[0], m_range[1], manual_lev))

# --- MODULE 7: NEWS & MODULE 8: LEDGER ---
st.markdown("---")
st.markdown("### 📰 Ecosystem News")
try:
    feed = feedparser.parse("https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml")
    for entry in feed.entries[:3]:
        st.write(f"🔹 **{entry.title}** - [Link]({entry.link})")
except: st.write("Syncing news...")

try:
    with open("strategy_ledger.txt", "a") as f:
        f.write(json.dumps({"ts": str(datetime.now()), "price": sol_p, "bias": final_bias}) + "\n")
except: pass
