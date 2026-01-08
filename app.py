import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data

# 1. CORE IDENTITY & STYLE (Rule 5)
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")

st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-gold {{ color: {accent}; font-weight: bold; text-shadow: 0 0 15px {accent}; font-family: monospace; font-size: 32px; }}
    .ai-card {{ border: 2px solid {accent}; padding: 25px; border-radius: 15px; background: {"#050505" if theme=="Dark Mode" else "#f9f9f9"}; margin-bottom: 25px; }}
    .liq-box {{ background: #440000; border: 1px solid #ff4b4b; padding: 15px; border-radius: 8px; text-align: center; color: white; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 15px; }}
    .styled-table th, .styled-table td {{ border: 1px solid #444; padding: 12px; text-align: center; }}
</style>""", unsafe_allow_html=True)

# 2. DATA ENGINE
df, btc_p, _, status = fetch_base_data('1d')

def calculate_atr(df):
    h_l = df['high'] - df['low']
    h_c = np.abs(df['high'] - df['close'].shift())
    l_c = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([h_l, h_c, l_c], axis=1).max(axis=1)
    return tr.rolling(14).mean().iloc[-1]

if status:
    price = df['close'].iloc[-1]
    current_atr = calculate_atr(df)
    
    # 3. SIDEBAR RISK (Rule 6 - Liquidation Soul)
    st.sidebar.header("User Parameters")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    
    # CALCULATE LIQUIDATION (Rule 6)
    liq_p = price * (1 - (1 / lev) * 0.45)

    # 4. AI AUTONOMOUS LOGIC (Rule 3)
    # Volatility Check
    v_pulse = "COILING" if current_atr < df['high'].tail(5).mean() * 0.05 else "EXPANDING"
    # Bias Engine
    if price > df['20_ema'].iloc[-1]:
        ai_bias, ai_mult = "Bullish 🚀", 2.2
    elif v_pulse == "COILING":
        ai_bias, ai_mult = "Bearish 📉", 3.2
    else:
        ai_bias, ai_mult = "Neutral ⚖️", 2.7

    auto_l = price - (current_atr * ai_mult)
    auto_h = price + (current_atr * ai_mult)
    auto_w = max(auto_h - auto_l, 0.01)

    # UNIVERSAL PRICE BANNER
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC", f"${btc_p:,.2f}")
    c2.metric("S SOL", f"${price:,.2f}")
    c3.metric("ATR (14d)", f"{current_atr:.2f}")
    st.divider()

    # 5. THE AI FORECAST DASHBOARD (With Liquidation Box)
    st.markdown(f"""
    <div class="ai-card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <h2 style="margin:0; color:{accent};">📡 Strategic AI Forecast: {ai_bias}</h2>
                <div style="margin: 20px 0;">
                    <span style="font-size: 14px; opacity:0.6;">PREDICTED YIELD ZONE:</span><br>
                    <span class="glow-gold">${auto_l:,.2f} — ${auto_h:,.2f}</span>
                </div>
            </div>
            <div class="liq-box">
                <span style="font-size: 12px; font-weight: bold;">LIQUIDATION PRICE</span><br>
                <span style="font-size: 24px; font-family: monospace;">${liq_p:,.2f}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 6. REACTIVE MANUAL ADJUSTMENT (Rule 17)
    # We use a key to ensure Streamlit tracks the manual state correctly
    st.subheader("✍️ Manual Custom Range Adjustment")
    m_range = st.slider("Select your Custom Range", 
                        float(price*0.5), float(price*1.5), 
                        (float(auto_l), float(auto_h)), step=0.01, key="manual_slider")
    
    m_l, m_h = m_range
    manual_w = max(m_h - m_l, 0.01)

    # RULE 7: COLLISION WARNING
    if m_l <= liq_p:
        st.error(f"🚨 ALERT: Manual Low (${m_l:,.2f}) is below Liquidation Floor (${liq_p:,.2f})!")

    # 7. DUAL PROFIT MATRICES (Recalculating live on every slider move)
    def get_matrix(width):
        # The DefiTuna Master Profit Formula
        daily_yield = (cap * lev * 0.0017) * ((price * 0.35) / width)
        return {
            "1 Hour": daily_yield / 24,
            "1 Day": daily_yield,
            "1 Week": daily_yield * 7,
            "1 Month": daily_yield * 30
        }

    st.subheader("📊 Dynamic Profit Comparison")
    t1, t2 = st.columns(2)
    
    with t1:
        st.markdown(f"#### 🤖 AI Suggested ({ai_mult}x ATR)")
        res_a = get_matrix(auto_w)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_a.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Time</th><th>Profit</th><th>ROI</th></tr>{rows_a}</table>', unsafe_allow_html=True)

    with t2:
        st.markdown("#### ✍️ Manual Custom Adjustment")
        # Critical Fix: This table now ONLY uses the manual_w from the slider
        res_m = get_matrix(manual_w)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_m.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Time</th><th>Profit</th><th>ROI</th></tr>{rows_m}</table>', unsafe_allow_html=True)

    # 8. AUDITOR & NAVIGATION
    st.sidebar.divider()
    st.sidebar.metric("LIQUIDATION FLOOR", f"${liq_p:,.2f}")
    if m_l > liq_p: st.sidebar.success("✅ STRATEGY COMPLIANT")
    else: st.sidebar.error("❌ NON-COMPLIANT")
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
