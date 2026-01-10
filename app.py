import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
from datetime import datetime
import json
import feedparser  # New requirement: pip install feedparser

# MAGIC COMMAND:
# pip install feedparser
# streamlit run app.py

st.set_page_config(page_title="Sreejan AI Sentinel Pro", layout="wide")

# 1. FLASHY UI STYLING (LOCKED & ENHANCED)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;700&display=swap');
    .stApp { background: radial-gradient(circle at top right, #0a0e17, #010203); font-family: 'Inter', sans-serif; color: #E0E0E0 !important; }
    .ribbon { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border-radius: 12px; padding: 20px; margin-bottom: 25px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .ai-card { background: linear-gradient(135deg, rgba(20, 20, 20, 0.8), rgba(0, 0, 0, 0.9)); border-left: 5px solid var(--b-col); padding: 30px; border-radius: 16px; position: relative; margin-bottom: 30px; box-shadow: inset 0 0 15px var(--b-col); }
    .metric-val { font-family: 'JetBrains Mono', monospace; font-size: 42px; font-weight: 700; }
    .label-tag { background: var(--b-col); color: #000; font-size: 11px; font-weight: 900; padding: 4px 10px; border-radius: 50px; text-transform: uppercase; }
    .news-card { background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1); transition: 0.3s; }
    .news-card:hover { background: rgba(255,255,255,0.1); border-color: #7B00FF; }
    .news-link { color: #BB86FC !important; text-decoration: none; font-weight: bold; font-size: 14px; }
    .sentinel-box { background: rgba(123, 0, 255, 0.08); border-radius: 8px; padding: 12px; border: 1px solid rgba(123, 0, 255, 0.3); margin-top: 15px; color: #C197FF; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# 2. DATA ENGINES
@st.cache_data(ttl=600)
def fetch_news():
    try:
        # Pulling from a reliable Crypto RSS Feed
        feed = feedparser.parse("https://cointelegraph.com/rss/tag/solana")
        return feed.entries[:5] # Get top 5 stories
    except: return []

try:
    sol_df, sol_p, btc_df, status = fetch_base_data('1d')
except:
    sol_df, btc_df, status = None, None, False

# Logic for Stats (LOCKED)
if not status or sol_df is None:
    btc_p, price, current_atr = 90729.0, 135.84, 8.45
    sol_stats = {"high": 142.50, "low": 129.10, "avg": 134.20, "t_high": 138.95, "t_low": 134.02}
    btc_stats = {"high": 95000.0, "low": 88000.0, "avg": 91340.0}
else:
    price = sol_df['close'].iloc[-1]
    current_atr = (sol_df['high']-sol_df['low']).rolling(14).mean().iloc[-1]
    s30, b30 = sol_df.tail(30), btc_df.tail(30)
    sol_stats = {"high": s30['high'].max(), "low": s30['low'].min(), "avg": s30['close'].mean(), "t_high": sol_df['high'].iloc[-1], "t_low": sol_df['low'].iloc[-1]}
    btc_p, btc_stats = btc_df['close'].iloc[-1], {"high": b30['high'].max(), "low": b30['low'].min(), "avg": b30['close'].mean()}

def f(v, d=2): return f"${v:,.{d}f}"

# --- MODULE 1: HEADER ---
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h1 style="color: #FFFFFF; margin:0;">🏹 SENTINEL PRO <span style="font-weight:200; font-size:18px; color:#888;">v10.4</span></h1>
        <div style="text-align: right; color: {'#00FF7F' if status else '#FF4B4B'}; font-weight: bold;">● {'SYSTEM NOMINAL' if status else 'SAFE MODE'}</div>
    </div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("₿ BITCOIN", f(btc_p, 0))
c2.metric("S SOLANA", f(price, 2))
c3.metric("⚡ VOLATILITY (ATR)", f(current_atr, 2))

# --- MODULE 2: PERFORMANCE RIBBON (LOCKED) ---
st.markdown('<div class="ribbon">', unsafe_allow_html=True)
r1, r2, r3 = st.columns(3)
r1.write(f"🏔️ **30D HIGH/LOW:** {f(sol_stats['high'])} — {f(sol_stats['low'])}")
r2.write(f"📅 **TODAY'S RANGE:** {f(sol_stats['t_high'])} — {f(sol_stats['t_low'])}")
r3.write(f"📊 **30D AVG:** SOL {f(sol_stats['avg'])} | BTC {f(btc_stats['avg'], 0)}")
st.markdown('</div>', unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.markdown("### 🛠️ STRATEGY ENGINE")
user_capital = st.sidebar.number_input("Capital ($)", value=10000.0)
manual_lev = st.sidebar.slider("Manual Leverage", 1.0, 10.0, 3.0)
news_sent = st.sidebar.select_slider("Sentiment Override", options=["Panic", "Bearish", "Neutral", "Bullish", "Euphoria"], value="Neutral")
bias_choice = st.sidebar.selectbox("🎯 Basis", ["Sentinel Auto", "Neutral", "Bullish", "Bearish"])

bias_colors = {"Neutral": "#D4AF37", "Bullish": "#00FF7F", "Bearish": "#FF4B4B"}
neural_trend = "Bullish" if price > sol_stats['avg'] else "Bearish"

if bias_choice == "Sentinel Auto":
    if news_sent == "Panic": final_bias, sentinel_msg = "Neutral", "⚠️ SYSTEM OVERRIDE: Panic detected in News Feed. Safety ranges active."
    elif news_sent == "Bullish" and neural_trend == "Bullish": final_bias, sentinel_msg = "Bullish", "✅ CONFLUENCE: Trend and Sentiment aligned."
    else: final_bias, sentinel_msg = "Neutral", "⚖️ BALANCED: Sentinel optimizing for steady yield."
else:
    final_bias, sentinel_msg = bias_choice, "👤 MANUAL: Sentinel in observation mode."

# --- MAIN DASHBOARD LAYOUT ---
col_main, col_news = st.columns([2, 1])

with col_main:
    # --- MODULE 4: AI FORECAST CARD (LOCKED) ---
    ai_lev = 2.0
    vol_mult = 3.5 if news_sent in ["Panic", "Euphoria"] else 2.5
    auto_l, auto_h = price - (current_atr * vol_mult), price + (current_atr * vol_mult)
    ai_liq = price / ai_lev if final_bias == "Bullish" else price * (1 - (1/ai_lev))

    st.markdown(f"""
    <div class="ai-card" style="--b-col: {bias_colors.get(final_bias)};">
        <span class="label-tag">{final_bias} BIAS</span>
        <h3 style="margin: 10px 0 5px 0; color: #888; font-size: 14px;">SENTINEL AI RANGE FORECAST</h3>
        <div class="metric-val" style="color: {bias_colors.get(final_bias)};">{f(auto_l)} <span style="color:#444; font-size:24px;">/</span> {f(auto_h)}</div>
        <div class="sentinel-box">{sentinel_msg}</div>
    </div>""", unsafe_allow_html=True)

    # --- MODULE 5 & 6: MANUAL & YIELD MATRIX (LOCKED) ---
    st.subheader("✍️ Manual Sandbox")
    m_range = st.slider("", float(price*0.3), float(price*1.7), value=(float(auto_l), float(auto_h)), label_visibility="collapsed")
    m_l, m_h = m_range

    st.markdown("### 📊 Performance Comparison")
    k1, k2 = st.columns(2)
    def calc_yield(l, h, leverage):
        width = max(h - l, 0.01)
        base_fee = (user_capital * leverage * 0.0001) * ((price * 0.45) / width)
        return {"Time": ["1h", "1d", "1w", "1m"], "Profit": [f(base_fee), f(base_fee*24), f(base_fee*168), f(base_fee*720)]}

    with k1:
        st.write("**🤖 AI (Locked 2x)**")
        st.table(pd.DataFrame(calc_yield(auto_l, auto_h, 2.0)))
    with k2:
        st.write(f"**👤 Manual ({manual_lev}x)**")
        st.table(pd.DataFrame(calc_yield(m_l, m_h, manual_lev)))

with col_news:
    st.markdown("### 📰 Live Solana Feed")
    news_items = fetch_news()
    if news_items:
        for entry in news_items:
            st.markdown(f"""
            <div class="news-card">
                <div style="font-size: 10px; color: #888;">{entry.published[:16]}</div>
                <a href="{entry.link}" target="_blank" class="news-link">{entry.title[:70]}...</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Searching for latest Solana news...")

# --- MODULE 7: AUTO-SAVE LEDGER (LOCKED) ---
try:
    with open("strategy_ledger.txt", "a") as f_out:
        log = {"time": str(datetime.now().strftime("%H:%M:%S")), "price": price, "bias": final_bias}
        f_out.write(json.dumps(log) + "\n")
except: pass
