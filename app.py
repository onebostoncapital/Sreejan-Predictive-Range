import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
from datetime import datetime
import json

# MAGIC COMMAND:
# streamlit run app.py

# 1. STYLE & THEME (RESTORING LOCKED UI)
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")
bias_color = {"Neutral": "#D4AF37", "Bullish": "#00FF7F", "Bearish": "#FF4B4B"}

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .ribbon {{ background: rgba(255, 255, 255, 0.03); border-radius: 10px; padding: 12px; margin-bottom: 15px; border: 1px solid #333; }}
    .ribbon-label {{ color: #888; font-size: 10px; text-transform: uppercase; margin-bottom: 2px; }}
    .ribbon-val {{ font-family: monospace; font-size: 14px; font-weight: bold; color: #EEE; }}
    .ai-card {{ border: 2px solid var(--b-col); padding: 20px; border-radius: 15px; background: #050505; position: relative; margin-bottom: 20px; box-shadow: 0 0 15px var(--b-col); }}
    .liq-box {{ position: absolute; right: 20px; top: 50%; transform: translateY(-50%); border: 1px solid #FF4B4B; padding: 10px; border-radius: 8px; background: rgba(255, 75, 75, 0.1); text-align: center; min-width: 100px; }}
    .liq-label {{ font-size: 10px; color: #FF4B4B; text-transform: uppercase; font-weight: bold; }}
    .liq-val {{ font-size: 18px; font-weight: bold; color: white; }}
    .news-module {{ border: 1px solid #333; padding: 15px; border-radius: 10px; background: #0a0a0a; margin-top: 10px; }}
</style>""", unsafe_allow_html=True)

# 2. DATA ENGINES (BULLETPROOF)
df, btc_p, btc_df, status = fetch_base_data('1d')

def get_perf(sol_df, btc_df):
    is_sol = isinstance(sol_df, pd.DataFrame) and not sol_df.empty
    is_btc = isinstance(btc_df, pd.DataFrame) and not btc_df.empty
    res = {"sol": ["Loading..."]*5, "btc": ["Loading..."]*3}
    if is_sol:
        res["sol"] = [sol_df['high'].tail(30).max(), sol_df['low'].tail(30).min(), sol_df['close'].tail(30).mean(), sol_df['high'].iloc[-1], sol_df['low'].iloc[-1]]
    if is_btc:
        res["btc"] = [btc_df['high'].tail(30).max(), btc_df['low'].tail(30).min(), btc_df['close'].tail(30).mean()]
    return res

if status:
    price = df['close'].iloc[-1]
    current_atr = (df['high']-df['low']).rolling(14).mean().iloc[-1]
    perf_data = get_perf(df, btc_df)
    def fmt(val, d=1): return f"${val:,.{d}f}" if isinstance(val, (int, float)) else val

    # --- HEADER ---
    st.title("🏹 Sreejan AI Forecaster Pro")
    h1, h2, h3 = st.columns(3)
    h1.metric("₿ BTC Price", fmt(btc_p, 2))
    h2.metric("S SOL Price", fmt(price, 2))
    h3.metric("Volatility (ATR)", fmt(current_atr, 2))

    # --- NEW PERFORMANCE RIBBON ---
    st.markdown('<div class="ribbon">', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(f'<p class="ribbon-label">30D Range (SOL)</p><p class="ribbon-val">H: {fmt(perf_data["sol"][0])} | L: {fmt(perf_data["sol"][1])}</p>', unsafe_allow_html=True)
    r2.markdown(f'<p class="ribbon-label">Today\'s SOL Range</p><p class="ribbon-val">H: {fmt(perf_data["sol"][3])} | L: {fmt(perf_data["sol"][4])}</p>', unsafe_allow_html=True)
    r3.markdown(f'<p class="ribbon-label">30D Avg Price</p><p class="ribbon-val">SOL: {fmt(perf_data["sol"][2])} | BTC: {fmt(perf_data["btc"][2], 0)}</p>', unsafe_allow_html=True)
    r4.markdown(f'<p class="ribbon-label">30D Range (BTC)</p><p class="ribbon-val">H: {fmt(perf_data["btc"][0], 0)} | L: {fmt(perf_data["btc"][1], 0)}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- PARAMETERS & BIAS ---
    st.sidebar.header("🕹️ Controls")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    
    # Technical Pulse (SMA/RSI)
    sma20 = df['close'].rolling(20).mean().iloc[-1]
    delta = df['close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l_ = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + (g / l_).iloc[-1]))
    tech_bias = "Bullish" if price > sma20 and rsi > 55 else ("Bearish" if price < sma20 and rsi < 45 else "Neutral")
    
    bias_choice = st.sidebar.selectbox("🎯 Directional Basis", ["AI Automatic", "Neutral", "Bullish", "Bearish"])
    final_bias = tech_bias if bias_choice == "AI Automatic" else bias_choice
    c_color = bias_color[final_bias]

    # --- AI FORECAST CARD (RESORED) ---
    bias_shift = (current_atr * 0.7) if final_bias == "Bullish" else (-(current_atr * 0.7) if final_bias == "Bearish" else 0)
    auto_l, auto_h = price - (current_atr * 2.5) + bias_shift, price + (current_atr * 2.5) + bias_shift
    liq_floor = auto_l * 0.8 # Calculation for the liquidation floor

    st.markdown(f"""
    <div class="ai-card" style="--b-col: {c_color};">
        <div style="font-size: 12px; color: {c_color}; font-weight: bold;">BIAS: {final_bias.upper()}</div>
        <h2 style="margin: 10px 0; color: {c_color};">🤖 AI Range Forecast</h2>
        <div style="font-size: 32px; font-weight: bold; color: {c_color}; font-family: monospace;">
            {fmt(auto_l, 2)} — {fmt(auto_h, 2)}
        </div>
        <div class="liq-box">
            <div class="liq-label">Liquidation Floor</div>
            <div class="liq-val">{fmt(liq_floor, 2)}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # --- MANUAL & NEWS ---
    st.markdown("### ✍️ Manual Range Control")
    if 'v_range' not in st.session_state: st.session_state.v_range = (float(auto_l), float(auto_h))
    m_range = st.slider("Adjust Zone", float(price*0.5), float(price*1.5), value=st.session_state.v_range)
    m_l, m_h = m_range

    st.markdown('<div class="news-module">🌍 <b>Global News Scanner</b><br><li><a href="#">Solana Mainnet Patch v3.0.14 Released (Bullish)</a></li></div>', unsafe_allow_html=True)

    # --- YIELD TABLES ---
    st.subheader("📊 Yield Comparison Matrix")
    def get_y(low, high):
        w = max(high - low, 0.01)
        h_fee = (cap * lev * 0.00007) * ((price * 0.35) / w)
        return {"1 Hour": fmt(h_fee, 2), "3 Hours": fmt(h_fee*3, 2), "1 Day": fmt(h_fee*24, 2), "1 Week": fmt(h_fee*168, 2), "1 Month": fmt(h_fee*720, 2)}
    
    c_ai, c_man = st.columns(2)
    with c_ai:
        st.write("🤖 **AI Strategy Yield**")
        st.table(pd.DataFrame(get_y(auto_l, auto_h).items(), columns=["Timeframe", "Est. Profit"]))
    with c_man:
        st.write("✍️ **Manual Strategy Yield**")
        st.table(pd.DataFrame(get_y(m_l, m_h).items(), columns=["Timeframe", "Est. Profit"]))

    # LEDGER AUTO-SAVE
    with open("strategy_ledger.txt", "a") as f: f.write(json.dumps({"time": str(datetime.now()), "m_low": m_l, "m_high": m_h}) + "\n")
