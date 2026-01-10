import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import json

# SAFETY CHECK FOR NEWS TOOL
try:
    import feedparser
    NEWS_READY = True
except ImportError:
    NEWS_READY = False

# MAGIC COMMAND:
# streamlit run app.py

st.set_page_config(page_title="Sreejan AI Sentinel Pro", layout="wide")

# --- LIVE DATA ENGINE (IMPROVED FOR DYNAMIC PRICES) ---
@st.cache_data(ttl=30) # Refresh every 30 seconds
def fetch_live_market_data():
    try:
        # Fetching SOL and BTC simultaneously
        tickers = yf.Tickers('SOL-USD BTC-USD')
        sol_data = tickers.tickers['SOL-USD'].history(period='30d', interval='1d')
        btc_data = tickers.tickers['BTC-USD'].history(period='30d', interval='1d')
        
        if not sol_data.empty and not btc_data.empty:
            return sol_data, btc_data, True
        return None, None, False
    except Exception as e:
        return None, None, False

# UI REFRESH TRIGGER
if st.sidebar.button("🔄 Force Market Refresh"):
    st.cache_data.clear()

sol_df, btc_df, status = fetch_live_market_data()

# Logic for Stats (LOCKED BUT NOW DYNAMIC)
if status:
    # LIVE DYNAMIC PRICES
    price = sol_df['Close'].iloc[-1]
    btc_p = btc_df['Close'].iloc[-1]
    
    # ATR CALCULATION
    current_atr = (sol_df['High'] - sol_df['Low']).rolling(14).mean().iloc[-1]
    
    # STATS MAPPING
    s30 = sol_df.tail(30)
    sol_stats = {
        "high": s30['High'].max(), 
        "low": s30['Low'].min(), 
        "avg": s30['Close'].mean(), 
        "t_high": sol_df['High'].iloc[-1], 
        "t_low": sol_df['Low'].iloc[-1]
    }
    b30 = btc_df.tail(30)
    btc_stats = {"high": b30['High'].max(), "low": b30['Low'].min(), "avg": b30['Close'].mean()}
else:
    # FALLBACK (ONLY IF INTERNET FAILS)
    btc_p, price, current_atr = 90729.0, 135.84, 8.45
    sol_stats = {"high": 142.50, "low": 129.10, "avg": 134.20, "t_high": 138.95, "t_low": 134.02}
    btc_stats = {"high": 95000.0, "low": 88000.0, "avg": 91340.0}

def f(v, d=2): return f"${v:,.{d}f}"

# 1. FLASHY UI STYLING (LOCKED)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;700&display=swap');
    .stApp { background: radial-gradient(circle at top right, #0a0e17, #010203); font-family: 'Inter', sans-serif; color: #E0E0E0 !important; }
    .ribbon { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border-radius: 12px; padding: 20px; margin-bottom: 25px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .ai-card { background: linear-gradient(135deg, rgba(20, 20, 20, 0.8), rgba(0, 0, 0, 0.9)); border-left: 5px solid var(--b-col); padding: 30px; border-radius: 16px; position: relative; margin-bottom: 30px; box-shadow: inset 0 0 20px var(--b-col); }
    .metric-val { font-family: 'JetBrains Mono', monospace; font-size: 48px; font-weight: 700; letter-spacing: -2px; }
    .label-tag { background: var(--b-col); color: #000; font-size: 11px; font-weight: 900; padding: 4px 12px; border-radius: 50px; text-transform: uppercase; }
    .news-footer { background: rgba(255,255,255,0.02); padding: 25px; border-radius: 15px; border-top: 1px solid rgba(123, 0, 255, 0.2); margin-top: 40px; }
    .news-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
    .news-card { background: rgba(255,255,255,0.04); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); transition: 0.3s; height: 100%; }
    .news-card:hover { background: rgba(123, 0, 255, 0.05); border-color: #7B00FF; transform: translateY(-3px); }
    .news-link { color: #BB86FC !important; text-decoration: none; font-weight: bold; font-size: 14px; display: block; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# --- MODULE 1: HEADER ---
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
        <h1 style="color: #FFFFFF; margin:0; letter-spacing:-1px;">🏹 SENTINEL PRO <span style="font-weight:200; font-size:18px; color:#888;">v10.6</span></h1>
        <div style="text-align: right; color: {'#00FF7F' if status else '#FF4B4B'}; font-weight: bold; font-family: 'JetBrains Mono';">
            ● {'LIVE MARKET FEED' if status else 'SAFE MODE (CONNECTION ERROR)'}
        </div>
    </div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("₿ BTC/USD", f(btc_p, 0))
c2.metric("S SOL/USD", f(price, 2))
c3.metric("⚡ LIVE ATR", f(current_atr, 2))

# --- MODULE 2: PERFORMANCE RIBBON ---
st.markdown('<div class="ribbon">', unsafe_allow_html=True)
r1, r2, r3 = st.columns(3)
r1.write(f"🏔️ **30D HIGH/LOW:** {f(sol_stats['high'])} — {f(sol_stats['low'])}")
r2.write(f"📅 **TODAY'S RANGE:** {f(sol_stats['t_high'])} — {f(sol_stats['t_low'])}")
r3.write(f"📊 **30D AVG:** SOL {f(sol_stats['avg'])} | BTC {f(btc_stats['avg'], 0)}")
st.markdown('</div>', unsafe_allow_html=True)

# --- SIDEBAR & SENTINEL LOGIC ---
st.sidebar.markdown("### 🛠️ STRATEGY ENGINE")
user_capital = st.sidebar.number_input("Capital ($)", value=10000.0)
manual_lev = st.sidebar.slider("Manual Leverage", 1.0, 10.0, 3.0)
news_sent = st.sidebar.select_slider("Sentiment Override", options=["Panic", "Bearish", "Neutral", "Bullish", "Euphoria"], value="Neutral")
bias_choice = st.sidebar.selectbox("🎯 Basis", ["Sentinel Auto", "Neutral", "Bullish", "Bearish"])

bias_colors = {"Neutral": "#D4AF37", "Bullish": "#00FF7F", "Bearish": "#FF4B4B"}
neural_trend = "Bullish" if price > sol_stats['avg'] else "Bearish"

if bias_choice == "Sentinel Auto":
    if news_sent == "Panic": final_bias, sentinel_msg = "Neutral", "⚠️ SYSTEM OVERRIDE: Panic detected. Range expanded for capital safety."
    elif news_sent == "Bullish" and neural_trend == "Bullish": final_bias, sentinel_msg = "Bullish", "✅ CONFLUENCE: Trend and Sentiment aligned."
    else: final_bias, sentinel_msg = "Neutral", "⚖️ BALANCED: Sentinel optimizing for steady yield."
else:
    final_bias, sentinel_msg = bias_choice, "👤 MANUAL: Sentinel in observation mode."

# --- MAIN DASHBOARD (WIDE) ---
ai_lev = 2.0
vol_mult = 3.5 if news_sent in ["Panic", "Euphoria"] else 2.5
auto_l, auto_h = price - (current_atr * vol_mult), price + (current_atr * vol_mult)
ai_liq = price / ai_lev if final_bias == "Bullish" else price * (1 - (1/ai_lev))

st.markdown(f"""
<div class="ai-card" style="--b-col: {bias_colors.get(final_bias)};">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span class="label-tag">{final_bias} BIAS</span>
            <h3 style="margin: 15px 0 5px 0; color: #888; font-size: 14px;">SENTINEL AI RANGE FORECAST</h3>
            <div class="metric-val" style="color: {bias_colors.get(final_bias)};">{f(auto_l)} <span style="color:#333; font-size:28px;">/</span> {f(auto_h)}</div>
            <div style="background: rgba(123, 0, 255, 0.08); border-radius: 8px; padding: 12px; border: 1px solid rgba(123, 0, 255, 0.3); margin-top: 15px; color: #C197FF; font-style: italic;">{sentinel_msg}</div>
        </div>
        <div style="text-align: right; background: rgba(255,75,75,0.1); padding: 20px; border-radius: 12px; border: 1px solid #FF4B4B;">
            <div style="color: #FF4B4B; font-size: 11px; font-weight: 900; letter-spacing: 1px;">LIQUIDATION FLOOR</div>
            <div style="font-size: 32px; font-weight: 700; color: #FFF; font-family: 'JetBrains Mono';">{f(ai_liq)}</div>
            <div style="color: #888; font-size: 10px; margin-top: 5px;">AI LOCKED AT 2.0x</div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

st.subheader("✍️ Manual Sandbox Control")
m_range = st.slider("", float(price*0.3), float(price*1.7), value=(float(auto_l), float(auto_h)), label_visibility="collapsed")
m_l, m_h = m_range

# --- YIELD COMPARISON ---
st.markdown("### 📊 Performance Comparison")
k1, k2 = st.columns(2)
def calc_yield(l, h, leverage):
    width = max(h - l, 0.01)
    base_fee = (user_capital * leverage * 0.0001) * ((price * 0.45) / width)
    return {"Timeframe": ["1 Hour", "3 Hours", "1 Day", "1 Week", "1 Month"], "Profit": [f(base_fee), f(base_fee*3), f(base_fee*24), f(base_fee*168), f(base_fee*720)]}

with k1:
    st.markdown(f"**🤖 AI Strategy** (Locked 2.0x)")
    st.table(pd.DataFrame(calc_yield(auto_l, auto_h, 2.0)))
with k2:
    st.markdown(f"**👤 Manual Setup** ({manual_lev}x)")
    st.table(pd.DataFrame(calc_yield(m_l, m_h, manual_lev)))

# --- BOTTOM NEWS FEED ---
@st.cache_data(ttl=600)
def fetch_news_data():
    if not NEWS_READY: return []
    try:
        feed = feedparser.parse("https://cointelegraph.com/rss/tag/solana")
        return feed.entries[:6]
    except: return []

st.markdown('<div class="news-footer">', unsafe_allow_html=True)
st.markdown("### 📰 Live Market Sentiment Feed")
news_items = fetch_news_data()
if news_items:
    st.markdown('<div class="news-grid">', unsafe_allow_html=True)
    for entry in news_items:
        st.markdown(f"""<div class="news-card"><div style="font-size: 11px; color: #7B00FF; font-weight: bold;">SOLANA NEWS</div><div style="font-size: 10px; color: #666; margin-top: 4px;">{entry.published[:16]}</div><a href="{entry.link}" target="_blank" class="news-link">{entry.title}</a></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Scanning for latest news events...")
st.markdown('</div>', unsafe_allow_html=True)

# --- AUTO-SAVE LEDGER ---
try:
    with open("strategy_ledger.txt", "a") as f_out:
        log = {"time": str(datetime.now().strftime("%H:%M:%S")), "price": price, "bias": final_bias}
        f_out.write(json.dumps(log) + "\n")
except: pass
