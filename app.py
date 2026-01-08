import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
import requests

# 1. CORE IDENTITY & STYLE (Rule 5 & 14)
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")

st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-gold {{ color: {accent}; font-weight: bold; text-shadow: 0 0 15px {accent}; font-family: monospace; font-size: 30px; }}
    .ai-box {{ border: 2px solid {accent}; padding: 20px; border-radius: 12px; background: {"#050505" if theme=="Dark Mode" else "#f9f9f9"}; margin-bottom: 20px; }}
    .intelligence-tag {{ background: #222; color: {accent}; padding: 4px 10px; border-radius: 20px; font-size: 10px; border: 1px solid {accent}; margin-right: 5px; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 10px; }}
    .styled-table th, .styled-table td {{ border: 1px solid #444; padding: 12px; text-align: center; }}
</style>""", unsafe_allow_html=True)

# 2. DATA ENGINE & ATR CALCULATION (Fixing KeyError)
df, btc_p, daily_atr, status = fetch_base_data('1d')

def calculate_atr_series(df, period=14):
    """Calculates the ATR column manually to prevent KeyErrors."""
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

if status:
    # Inject ATR column into dataframe
    df['atr_val'] = calculate_atr_series(df)
    price = df['close'].iloc[-1]
    
    # AI Logic: Volatility Pulse (Rule 24)
    # Compare current ATR to the 5-day average of ATR
    current_vol = df['atr_val'].iloc[-1]
    avg_vol_5d = df['atr_val'].tail(5).mean()
    vol_pulse = "EXPANDING" if current_vol > avg_vol_5d else "COILING (High Risk)"
    
    # AI Logic: BTC Correlation (Rule 26)
    btc_sentiment = "DRAGGING" if btc_p < (btc_p * 0.99) else "SUPPORTIVE"

    # 3. AI AUTONOMOUS BIAS (Rule 3.1 & 23)
    if btc_sentiment == "SUPPORTIVE" and price > df['20_ema'].iloc[-1]:
        ai_bias, ai_mult = "Bullish 🚀", 2.2
    elif btc_sentiment == "DRAGGING" or vol_pulse == "COILING (High Risk)":
        ai_bias, ai_mult = "Bearish 📉", 3.2
    else:
        ai_bias, ai_mult = "Neutral ⚖️", 2.7

    # UNIVERSAL PRICE BANNER (Rule 13)
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC", f"${btc_p:,.2f}")
    c2.metric("S SOL", f"${price:,.2f}")
    c3.metric("ATR (V-PULSE)", f"{current_vol:.2f}")
    st.divider()

    # 4. THE AI INTELLIGENCE DASHBOARD (Rule 3 Soul)
    auto_l = price - (current_vol * ai_mult)
    auto_h = price + (current_vol * ai_mult)
    auto_w = max(auto_h - auto_l, 0.01)

    st.markdown(f"""
    <div class="ai-box">
        <div style="display: flex; margin-bottom: 10px;">
            <span class="intelligence-tag">V-PULSE: {vol_pulse}</span>
            <span class="intelligence-tag">BTC: {btc_sentiment}</span>
            <span class="intelligence-tag">STRATEGY: DEFITUNA {ai_mult}x</span>
        </div>
        <h2 style="margin:0; color:{accent};">📡 AI Autonomous Forecast: {ai_bias}</h2>
        <div style="margin: 20px 0;">
            <span style="font-size: 14px; opacity:0.6;">PREDICTED YIELD ZONE:</span><br>
            <span class="glow-gold">${auto_l:,.2f} — ${auto_h:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. SIDEBAR & MANUAL CONTROLS (Rule 6 & 17)
    st.sidebar.header("Capital & Leverage")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    liq_p = price * (1 - (1 / lev) * 0.45)
    
    # Interactive Slider
    m_l, m_h = st.slider("Manual Range Adjustment", float(price*0.1), float(price*1.9), 
                         (float(auto_l), float(auto_h)), step=0.1)
    manual_w = max(m_h - m_l, 0.01)

    # 6. DUAL PROFITABILITY MATRICES (Rule 17, 21, 22)
    def get_matrix(width):
        # Master Yield Formula: Profitability for 1h, 3h, 6h, 12h, 1d, 1w, 1m
        base = (cap * lev * 0.0017) * ((price * 0.35) / width)
        return {
            "1 Hour": base/24, "12 Hour": base/2, 
            "1 Day": base, "1 Week": base*7, "1 Month": base*30
        }

    st.subheader("📊 Strategic Profit Comparison")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"#### 🤖 AI Auto ({ai_mult}x ATR)")
        res_a = get_matrix(auto_w)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_a.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_a}</table>', unsafe_allow_html=True)
    with t2:
        st.markdown("#### ✍️ Manual Adjustment")
        res_m = get_matrix(manual_w)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_m.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_m}</table>', unsafe_allow_html=True)

    # 7. NAVIGATION & AUDITOR
    st.sidebar.divider()
    if m_l > liq_p: st.sidebar.success("✅ STRATEGY COMPLIANT")
    else: st.sidebar.error("❌ NON-COMPLIANT")
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
