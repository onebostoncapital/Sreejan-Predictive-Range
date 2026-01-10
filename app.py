import streamlit as st
import pandas as pd
import numpy as np
import requests
from data_engine import fetch_base_data
from datetime import datetime

# MAGIC COMMAND:
# streamlit run app.py

# 1. STYLE & THEME (RULE: DEFI TUNA BRANDING)
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-gold {{ color: {accent}; font-weight: bold; text-shadow: 0 0 15px {accent}; font-family: monospace; font-size: 32px; }}
    .ai-card {{ border: 2px solid {accent}; padding: 25px; border-radius: 15px; background: {"#050505" if theme=="Dark Mode" else "#f9f9f9"}; margin-bottom: 25px; }}
    .manual-card {{ border: 2px solid #555; padding: 25px; border-radius: 15px; background: {"#0a0a0a" if theme=="Dark Mode" else "#f0f0f0"}; margin-bottom: 25px; }}
    .liq-box {{ background: #440000; border: 1px solid #ff4b4b; padding: 15px; border-radius: 8px; text-align: center; color: white; }}
    .tag {{ background: #222; color: {accent}; padding: 3px 10px; border-radius: 12px; font-size: 11px; border: 1px solid {accent}; margin-right: 8px; }}
    .news-ticker {{ background: rgba(212, 175, 55, 0.1); border: 1px dashed {accent}; padding: 10px; border-radius: 8px; margin-top: 15px; font-size: 13px; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 15px; }}
    .styled-table td {{ border: 1px solid #444; padding: 12px; text-align: center; font-family: monospace; }}
</style>""", unsafe_allow_html=True)

# 2. DATA ENGINE
df, btc_p, _, status = fetch_base_data('1d')

def calculate_atr(df):
    h_l, h_c, l_c = df['high']-df['low'], np.abs(df['high']-df['close'].shift()), np.abs(df['low']-df['close'].shift())
    tr = pd.concat([h_l, h_c, l_c], axis=1).max(axis=1)
    return tr.rolling(14).mean().iloc[-1]

if status:
    price = df['close'].iloc[-1]
    current_atr = calculate_atr(df)
    
    # --- RULE: AI INTELLIGENCE ENGINE ---
    v_pulse = "COILING" if current_atr < (df['high'].tail(5).mean() * 0.045) else "EXPANDING"
    btc_corr = "SUPPORTIVE" if btc_p > (btc_p * 0.985) else "DRAGGING"
    ai_mult = 3.2 if (v_pulse == "COILING" or btc_corr == "DRAGGING") else 2.2

    # --- RULE: SIDEBAR CONTROLS (CAPITAL & LEVERAGE) ---
    st.sidebar.header("🕹️ Strategy Controls")
    cap = st.sidebar.number_input("Total Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Acceptable Leverage", 1.0, 5.0, 1.5)
    liq_p = price * (1 - (1 / lev) * 0.45) # Rule 6: Liquidation Calculation

    # 4. TOP STATS
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC Price", f"${btc_p:,.2f}")
    c2.metric("S SOL Price", f"${price:,.2f}")
    c3.metric("Market Volatility (ATR)", f"{current_atr:.2f}")
    st.divider()

    # --- RULE: AI AUTONOMOUS FORECAST MODULE ---
    auto_l, auto_h = price - (current_atr * ai_mult), price + (current_atr * ai_mult)
    st.markdown(f"""
    <div class="ai-card">
        <span class="tag">V-PULSE: {v_pulse}</span> <span class="tag">BTC: {btc_corr}</span>
        <div style="display: flex; justify-content: space-between; margin-top:15px;">
            <div>
                <h2 style="margin:0; color:{accent};">🤖 AI Range Forecast</h2>
                <p style="font-size: 14px; opacity:0.6;">SUGGESTED DEFI TUNA RANGE ({ai_mult}x ATR):</p>
                <span class="glow-gold">${auto_l:,.2f} — ${auto_h:,.2f}</span>
            </div>
            <div class="liq-box">
                <span style="font-size: 11px;">LIQUIDATION FLOOR</span><br>
                <span style="font-size: 20px;">${liq_p:,.2f}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- RULE: MANUAL MODE MODULE ---
    st.markdown('<div class="manual-card">', unsafe_allow_html=True)
    st.subheader("✍️ Manual Mode & Range Setting")
    if 'v_range' not in st.session_state: st.session_state.v_range = (float(auto_l), float(auto_h))
    
    m_range = st.slider("Set Manual Liquidity Zone", float(price*0.1), float(price*1.9), value=st.session_state.v_range, step=0.01)
    st.session_state.v_range = m_range
    m_l, m_h = m_range
    manual_w = max(m_h - m_l, 0.01)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- RULE: PROFIT COMPARISON MATRIX ---
    def calculate_yield(width_val):
        daily = (cap * lev * 0.0017) * ((price * 0.35) / width_val)
        return {"1 Day": daily, "1 Week": daily*7, "1 Month": daily*30}

    st.subheader("📊 Profitability: AI vs Manual")
    t1, t2 = st.columns(2)
    with t1:
        st.info("🤖 AI Suggested Yield")
        res_a = calculate_yield(auto_h - auto_l)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td></tr>" for k, v in res_a.items()])
        st.markdown(f'<table class="styled-table">{rows_a}</table>', unsafe_allow_html=True)
    with t2:
        st.success("✍️ Manual Mode Yield")
        res_m = calculate_yield(manual_w)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td></tr>" for k, v in res_m.items()])
        st.markdown(f'<table class="styled-table" style="border: 1px solid {accent};">{rows_m}</table>', unsafe_allow_html=True)

    # --- RULE: THE AUDITOR (RISK CHECK) ---
    st.sidebar.divider()
    if m_l <= liq_p:
        st.sidebar.error("🚨 RISK: NON-COMPLIANT")
        st.error("🚨 ALERT: Your Manual Low is too close to the Liquidation Floor!")
    else:
        st.sidebar.success("✅ STRATEGY COMPLIANT")
    
    st.sidebar.link_button("🔙 Back to Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
