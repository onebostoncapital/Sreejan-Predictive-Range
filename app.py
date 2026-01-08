import streamlit as st
import pandas as pd
import numpy as np
import requests
from data_engine import fetch_base_data

# 1. CORE IDENTITY & STYLE
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")

st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-gold {{ color: {accent}; font-weight: bold; text-shadow: 0 0 15px {accent}; font-family: monospace; font-size: 32px; }}
    .ai-intelligence-card {{ 
        border: 2px solid {accent}; padding: 25px; border-radius: 15px; 
        background: {"#050505" if theme=="Dark Mode" else "#f9f9f9"}; 
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.1); margin-bottom: 25px;
    }}
    .liquidation-box {{ background: #440000; border: 1px solid #ff4b4b; padding: 15px; border-radius: 8px; text-align: center; }}
    .tag {{ background: #222; color: {accent}; padding: 3px 10px; border-radius: 12px; font-size: 11px; border: 1px solid {accent}; margin-right: 8px; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 15px; }}
    .styled-table th, .styled-table td {{ border: 1px solid #444; padding: 12px; text-align: center; }}
</style>""", unsafe_allow_html=True)

# 2. DATA & ATR ENGINE
df, btc_p, _, status = fetch_base_data('1d')

def calculate_atr_series(df, period=14):
    h_l = df['high'] - df['low']
    h_c = np.abs(df['high'] - df['close'].shift())
    l_c = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([h_l, h_c, l_c], axis=1).max(axis=1)
    return tr.rolling(period).mean()

if status:
    df['atr_val'] = calculate_atr_series(df)
    price = df['close'].iloc[-1]
    current_atr = df['atr_val'].iloc[-1]
    
    # 3. SIDEBAR RISK CONTROLS (Rule 6 - Liquidation Soul)
    st.sidebar.header("Risk Settings")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    
    # CRITICAL: LIQUIDATION CALCULATION (Rule 6)
    liq_p = price * (1 - (1 / lev) * 0.45)
    
    # 4. AI INTELLIGENCE LAYERS (Sentiment & V-Pulse)
    avg_atr_5d = df['atr_val'].tail(5).mean()
    v_pulse = "COILING (Breakout Risk)" if current_atr < avg_atr_5d else "EXPANDING"
    btc_corr = "SUPPORTIVE" if btc_p > (btc_p * 0.98) else "DRAGGING"
    
    # Bias Engine (Rule 3.1)
    if price > df['20_ema'].iloc[-1] and btc_corr == "SUPPORTIVE":
        ai_bias, ai_mult = "Bullish 🚀", 2.2
    elif btc_corr == "DRAGGING" or v_pulse == "COILING (Breakout Risk)":
        ai_bias, ai_mult = "Bearish 📉", 3.2
    else:
        ai_bias, ai_mult = "Neutral ⚖️", 2.7

    # UNIVERSAL PRICE BANNER (Rule 13)
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC", f"${btc_p:,.2f}")
    c2.metric("S SOL", f"${price:,.2f}")
    c3.metric("ATR (14d)", f"{current_atr:.2f}")
    st.divider()

    # 5. THE AI INTELLIGENCE DASHBOARD (Glow Soul)
    auto_l = price - (current_atr * ai_mult)
    auto_h = price + (current_atr * ai_mult)
    auto_w = max(auto_h - auto_l, 0.01)

    st.markdown(f"""
    <div class="ai-intelligence-card">
        <div style="margin-bottom: 15px;">
            <span class="tag">V-PULSE: {v_pulse}</span>
            <span class="tag">LIQUIDATION SAFETY: 45%</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <h2 style="margin:0; color:{accent};">📡 Strategic AI Forecast: {ai_bias}</h2>
                <div style="margin: 20px 0;">
                    <span style="font-size: 14px; opacity:0.6; letter-spacing: 1px;">AUTONOMOUS YIELD ZONE ({ai_mult}x ATR):</span><br>
                    <span class="glow-gold">${auto_l:,.2f} — ${auto_h:,.2f}</span>
                </div>
            </div>
            <div class="liquidation-box">
                <span style="color: #ff4b4b; font-size: 12px; font-weight: bold;">LIQUIDATION PRICE</span><br>
                <span style="color: white; font-size: 24px; font-family: monospace;">${liq_p:,.2f}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 6. INTERACTIVE RANGE ADJUSTMENT (Rule 17)
    st.markdown('<div class="ai-intelligence-card" style="padding: 15px;">', unsafe_allow_html=True)
    st.subheader("✍️ Manual Custom Range Adjustment")
    m_l, m_h = st.slider("Fine-Tune Manual Zone", float(price*0.1), float(price*1.9), (float(auto_l), float(auto_h)), step=0.1)
    manual_w = max(m_h - m_l, 0.01)
    
    # RULE 7: COLLISION AUDIT
    if m_l <= liq_p:
        st.error(f"⚠️ CRITICAL ALERT: Your Manual Low (${m_l:,.2f}) has crossed the Liquidation Floor (${liq_p:,.2f})!")
    st.markdown('</div>', unsafe_allow_html=True)

    # 7. DUAL PROFITABILITY MATRICES (Rule 22)
    def get_matrix(width):
        base = (cap * lev * 0.0017) * ((price * 0.35) / width)
        return {"1 Hour": base/24, "1 Day": base, "1 Week": base*7, "1 Month": base*30}

    st.subheader("📊 Profitability Comparison Matrix")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"#### 🤖 AI Auto ({ai_mult}x)")
        res_a = get_matrix(auto_w)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_a.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_a}</table>', unsafe_allow_html=True)
    with t2:
        st.markdown("#### ✍️ Manual Custom")
        res_m = get_matrix(manual_w)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_m.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_m}</table>', unsafe_allow_html=True)

    # 8. AUDITOR & NAVIGATION
    st.sidebar.divider()
    st.sidebar.metric("LIQUIDATION FLOOR", f"${liq_p:,.2f}")
    if m_l > liq_p: st.sidebar.success("✅ STRATEGY COMPLIANT")
    else: st.sidebar.error("❌ NON-COMPLIANT")
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
