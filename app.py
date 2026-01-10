import streamlit as st
import pandas as pd
import numpy as np
import requests
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

# --- NEW DATA ENGINE: COINGECKO (RELIABLE LIVE PRICES) ---
@st.cache_data(ttl=15)  # Fresh data every 15 seconds
def fetch_live_market_data():
    try:
        # Fetching Live Prices for BTC and SOL
        price_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,solana&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true"
        price_data = requests.get(price_url, timeout=5).json()
        
        # Fetching 30-day Historical Data for ATR & Stats
        sol_history_url = "https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=30&interval=daily"
        sol_history = requests.get(sol_history_url, timeout=5).json()
        
        if 'bitcoin' in price_data and 'solana' in price_data and 'prices' in sol_history:
            # Current Prices
            btc_p = price_data['bitcoin']['usd']
            sol_p = price_data['solana']['usd']
            
            # Process History for ATR and Stats
            prices_list = [p[1] for p in sol_history['prices']]
            vol_list = [v[1] for v in sol_history['total_volumes']]
            
            # Simple ATR Calculation from price swings
            avg_swing = np.std(prices_list) * 1.5 
            
            sol_stats = {
                "high": max(prices_list),
                "low": min(prices_list),
                "avg": np.mean(prices_list),
                "t_high": sol_p * 1.02, # Estimated today's high
                "t_low": sol_p * 0.98   # Estimated today's low
            }
            return btc_p, sol_p, avg_swing, sol_stats, True
        return 0, 0, 0, {}, False
    except Exception as e:
        return 0, 0, 0, {}, False

# UI REFRESH TRIGGER
if st.sidebar.button("🔄 Force CoinGecko Sync"):
    st.cache_data.clear()

btc_p, price, current_atr, sol_stats, status = fetch_live_market_data()

# FALLBACK (ONLY IF INTERNET FAILS)
if not status:
    btc_p, price, current_atr = 95200.0, 145.20, 9.15
    sol_stats = {"high": 160.50, "low": 120.10, "avg": 138.20, "t_high": 148.95, "t_low": 142.02}

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
    .news-link { color: #BB86FC !important; text-decoration: none; font-weight: bold; font-size: 14px; display: block; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# --- MODULE 1: HEADER ---
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
        <h1 style="color: #FFFFFF; margin:0; letter-spacing:-1px;">🏹 SENTINEL PRO <span style="font-weight:200; font-size:18px; color:#888;">v10.7</span></h1>
        <div style="text-align: right; color: {'#00FF7F' if status else '#FF4B4B'}; font-weight: bold; font-family: 'JetBrains Mono';">
            ● {'COINGECKO FEED ACTIVE' if status else 'SAFE MODE (API DELAY)'}
        </div>
    </div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("₿ BITCOIN", f(btc_p, 0))
c2.metric("S SOLANA", f(price, 2))
c3.metric("⚡ DYNAMIC ATR", f(current_atr, 2))

# --- MODULE 2: PERFORMANCE RIBBON ---
st.markdown('<div class="ribbon">', unsafe_allow_html=True)
r1, r2, r3 = st.columns(3)
r1.write(f"🏔️ **30D HIGH/LOW:** {f(sol_stats['high'])} — {f(sol_stats['low'])}")
r2.write(f"📅 **TODAY'S RANGE:** {f(sol_stats['t_high'])} — {f(sol_stats['t_low'])}")
r3.write(f"📊 **30D AVG:** SOL {f(sol_stats['avg'])}")
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
        st.markdown(f"""<div class="news-card"><div style="font-size: 11px; color: #7B00FF; font-weight: bold;">SOLANA NEWS</div><div style="font-size: 10px; color: #666; margin-top: 4px;">{entry.published[:16]}</div><a href="{entry.link}" target="_blank" class="news-link">{entry.title}</a></div>""")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Scanning for latest news events...")
st.markdown('</div>', unsafe_allow_html=True)

# --- AUTO-SAVE LEDGER ---
try:
    with open("strategy_ledger.txt", "a") as f_out:
        log = {"time": str(datetime.now().strftime("%H:%M:%S")), "price": price, "bias": final_bias, "l": m_l, "h": m_h}
        f_out.write(json.dumps(log) + "\n")
except: pass
