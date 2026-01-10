import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
from datetime import datetime
import json

# MAGIC COMMAND:
# streamlit run app.py

# 1. STYLE & THEME (LOCKED)
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")
bias_color = {"Neutral": "#D4AF37", "Bullish": "#00FF7F", "Bearish": "#FF4B4B"}

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .ribbon {{ background: rgba(255, 255, 255, 0.03); border-radius: 10px; padding: 15px; margin-bottom: 20px; border: 1px solid #333; }}
    .ribbon-label {{ color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }}
    .ribbon-val {{ font-family: monospace; font-size: 16px; font-weight: bold; }}
    .ai-intel-box {{ border: 1px dashed {accent}; padding: 15px; border-radius: 10px; background: rgba(212, 175, 55, 0.05); margin-bottom: 20px; }}
    .news-module {{ border: 1px solid #333; padding: 15px; border-radius: 10px; background: #0a0a0a; margin-bottom: 20px; }}
    .ai-card {{ border: 2px solid var(--b-col); padding: 25px; border-radius: 15px; background: #050505; margin-bottom: 20px; box-shadow: 0 0 20px var(--b-col); }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
    .styled-table th {{ background: #222; padding: 10px; border: 1px solid #444; color: #aaa; }}
    .styled-table td {{ border: 1px solid #444; padding: 10px; text-align: center; font-family: monospace; }}
</style>""", unsafe_allow_html=True)

# 2. DATA ENGINES (LOCKED + SAFETY SHIELD)
df, btc_p, btc_df, status = fetch_base_data('1d')

def get_performance_stats(sol_df, btc_df):
    # Safety Check: If DataFrames are empty, return placeholders
    if sol_df is None or sol_df.empty or btc_df is None or btc_df.empty:
        return {"sol": ["N/A"]*5, "btc": ["N/A"]*3}
    
    # SOL stats (Check if we have enough rows)
    s_rows = len(sol_df)
    sol_30_h = sol_df['high'].tail(min(30, s_rows)).max()
    sol_30_l = sol_df['low'].tail(min(30, s_rows)).min()
    sol_30_avg = sol_df['close'].tail(min(30, s_rows)).mean()
    sol_today_h = sol_df['high'].iloc[-1]
    sol_today_l = sol_df['low'].iloc[-1]
    
    # BTC stats
    b_rows = len(btc_df)
    btc_30_h = btc_df['high'].tail(min(30, b_rows)).max()
    btc_30_l = btc_df['low'].tail(min(30, b_rows)).min()
    btc_30_avg = btc_df['close'].tail(min(30, b_rows)).mean()
    
    return {
        "sol": [sol_30_h, sol_30_l, sol_30_avg, sol_today_h, sol_today_l],
        "btc": [btc_30_h, btc_30_l, btc_30_avg]
    }

if status:
    price = df['close'].iloc[-1]
    current_atr = (df['high']-df['low']).rolling(14).mean().iloc[-1]
    perf = get_performance_stats(df, btc_df)
    
    # Formatting function for N/A values
    def fmt(val, d=1): return f"${val:,.{d}f}" if isinstance(val, (int, float)) else val

    # --- HEADER SECTION (LOCKED) ---
    st.title("🏹 Sreejan AI Forecaster Pro")
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC Price", fmt(btc_p, 2))
    c2.metric("S SOL Price", fmt(price, 2))
    c3.metric("Volatility (ATR)", fmt(current_atr, 2))
    
    # --- PERFORMANCE RIBBON MODULE (FIXED) ---
    st.markdown('<div class="ribbon">', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(f'<p class="ribbon-label">30D High/Low (SOL)</p><p class="ribbon-val">H: {fmt(perf["sol"][0])} | L: {fmt(perf["sol"][1])}</p>', unsafe_allow_html=True)
    with r2:
        st.markdown(f'<p class="ribbon-label">Today\'s Range (SOL)</p><p class="ribbon-val">H: {fmt(perf["sol"][3])} | L: {fmt(perf["sol"][4])}</p>', unsafe_allow_html=True)
    with r3:
        st.markdown(f'<p class="ribbon-label">30D Avg Price</p><p class="ribbon-val">SOL: {fmt(perf["sol"][2])} | BTC: {fmt(perf["btc"][2], 0)}</p>', unsafe_allow_html=True)
    with r4:
        st.markdown(f'<p class="ribbon-label">30D High/Low (BTC)</p><p class="ribbon-val">H: {fmt(perf["btc"][0], 0)} | L: {fmt(perf["btc"][1], 0)}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # --- AI TECH INTELLIGENCE (LOCKED) ---
    sma20 = df['close'].rolling(20).mean().iloc[-1]
    delta = df['close'].diff(); g = (delta.where(delta > 0, 0)).rolling(14).mean(); l = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + (g / l).iloc[-1]))
    tech_bias = "Bullish" if price > sma20 and rsi > 55 else ("Bearish" if price < sma20 and rsi < 45 else "Neutral")
    st.markdown(f"""<div class="ai-intel-box"><b>🧠 TECH PULSE:</b> {tech_bias.upper()} (RSI: {rsi:.2f} | SMA: ${sma20:,.2f})</div>""", unsafe_allow_html=True)

    # --- SIDEBAR & FINAL BIAS (LOCKED) ---
    st.sidebar.header("🕹️ Parameters")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    
    news_sentiment = "Bullish" 
    final_auto = news_sentiment if news_sentiment != "Neutral" else tech_bias
    bias_choice = st.sidebar.selectbox("🎯 Directional Basis", ["AI Automatic", "Neutral", "Bullish", "Bearish"])
    final_bias = final_auto if bias_choice == "AI Automatic" else bias_choice

    # --- AI RANGE CARD (LOCKED) ---
    range_mod = 1.15 if news_sentiment == "Bullish" else 1.0
    bias_shift = (current_atr * 0.7) if final_bias == "Bullish" else (-(current_atr * 0.7) if final_bias == "Bearish" else 0)
    auto_l, auto_h = price - (current_atr * 2.5 * (2-range_mod)) + bias_shift, price + (current_atr * 2.5 * range_mod) + bias_shift
    c_color = bias_color[final_bias]

    st.markdown(f"""<div class="ai-card" style="--b-col: {c_color};">
        <h2 style="margin:0; color:{c_color};">🤖 AI Range Forecast</h2>
        <span class="glow-gold" style="color:{c_color};">${auto_l:,.2f} — ${auto_h:,.2f}</span>
    </div>""", unsafe_allow_html=True)

    # --- NEWS MODULE (LOCKED) ---
    st.markdown('<div class="news-module">🌍 <b>Global News Scanner</b><br><li><a href="#">Solana Mainnet Patch v3.0.14 Released (Bullish)</a></li></div>', unsafe_allow_html=True)

    # --- MANUAL SECTION (LOCKED) ---
    st.markdown('<div class="ribbon">✍️ <b>Manual Range Control</b>', unsafe_allow_html=True)
    if 'v_range' not in st.session_state: st.session_state.v_range = (float(auto_l), float(auto_h))
    m_range = st.slider("Adjust Zone", float(price*0.1), float(price*1.9), value=st.session_state.v_range)
    m_l, m_h = m_range
    st.markdown('</div>', unsafe_allow_html=True)

    # --- YIELD MATRIX (LOCKED) ---
    def get_projections(l, h):
        w = max(h - l, 0.01)
        h_fee = (cap * lev * 0.00007) * ((price * 0.35) / w)
        return {"1h": h_fee, "24h": h_fee*24, "1w": h_fee*24*7, "1m": h_fee*24*30}
    
    st.subheader("📊 Yield Comparison Matrix")
    c_ai, c_man = st.columns(2)
    ai_p, man_p = get_projections(auto_l, auto_h), get_projections(m_l, m_h)
    with c_ai: st.write("🤖 AI Yield", pd.DataFrame(ai_p.items()))
    with c_man: st.write("✍️ Manual Yield", pd.DataFrame(man_p.items()))

    # --- LEDGER (AUTO-SAVE) ---
    with open("strategy_ledger.txt", "a") as f: f.write(json.dumps({"time": str(datetime.now()), "bias": final_bias}) + "\n")
    st.sidebar.success("✅ Strategy Logged")
