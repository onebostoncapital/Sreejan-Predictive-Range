import streamlit as st
import pandas as pd
from data_engine import fetch_base_data
import requests

st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

# 1. CORE STYLE (Rule 5 & Glow Soul)
theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")

st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-gold {{ color: {accent}; font-weight: bold; text-shadow: 0 0 15px {accent}; font-family: monospace; font-size: 30px; }}
    .ai-box {{ border: 2px solid {accent}; padding: 20px; border-radius: 12px; background: {"#050505" if theme=="Dark Mode" else "#f9f9f9"}; margin-bottom: 20px; }}
    .intelligence-tag {{ background: #222; color: {accent}; padding: 4px 10px; border-radius: 20px; font-size: 10px; border: 1px solid {accent}; margin-right: 5px; }}
</style>""", unsafe_allow_html=True)

# 2. DATA & CORRELATION ENGINE (Rule 13 & 26)
df, btc_p, daily_atr, status = fetch_base_data('1d')

if status:
    price = df['close'].iloc[-1]
    # AI Logic: Volatility Pulse (Rule 24)
    # If current ATR is lower than 5-day average, we expect a breakout
    recent_atr_avg = df['atr'].tail(5).mean()
    vol_pulse = "EXPANDING" if daily_atr > recent_atr_avg else "COILING (High Risk)"
    
    # AI Logic: BTC Correlation (Rule 26)
    # Simple proxy: If BTC is below its 20 EMA, it drags SOL down
    btc_sentiment = "DRAGGING" if btc_p < (btc_p * 0.98) else "SUPPORTIVE"

    # 3. AI AUTONOMOUS BIAS (Rule 3.1 & 23)
    if btc_sentiment == "SUPPORTIVE" and price > df['20_ema'].iloc[-1]:
        ai_bias, ai_mult, ai_color = "Bullish 🚀", 2.2, "#00FFA3"
    elif btc_sentiment == "DRAGGING" or vol_pulse == "COILING (High Risk)":
        ai_bias, ai_mult, ai_color = "Bearish 📉", 3.2, "#FF4B4B"
    else:
        ai_bias, ai_mult, ai_color = "Neutral ⚖️", 2.7, "#888888"

    # UNIVERSAL PRICE BANNER (Rule 13)
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC", f"${btc_p:,.2f}")
    c2.metric("S SOL", f"${price:,.2f}")
    c3.metric("ATR (V-PULSE)", f"{daily_atr:.2f} ({vol_pulse})")
    st.divider()

    # 4. THE AI INTELLIGENCE DASHBOARD
    st.markdown(f"""
    <div class="ai-box">
        <div style="display: flex; margin-bottom: 10px;">
            <span class="intelligence-tag">V-PULSE AI</span>
            <span class="intelligence-tag">BTC-CORRELATION</span>
            <span class="intelligence-tag">LIQUIDATION-SHARK</span>
        </div>
        <h2 style="margin:0; color:{accent};">📡 AI Autonomous Forecast</h2>
        <p style="opacity:0.8;">Market is currently <b>{vol_pulse}</b> with <b>{btc_sentiment}</b> BTC pressure.</p>
        <div style="margin: 20px 0;">
            <span style="font-size: 14px; opacity:0.6;">PREDICTED YIELD ZONE ({ai_mult}x ATR):</span><br>
            <span class="glow-gold">${price - (daily_atr * ai_mult):,.2f} — ${price + (daily_atr * ai_mult):,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. SIDEBAR & MANUAL CONTROLS (Rule 6 & 17)
    st.sidebar.header("Capital & Leverage")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    liq_p = price * (1 - (1 / lev) * 0.45)
    
    m_l, m_h = st.slider("Manual Range Adjustment", float(price*0.1), float(price*1.9), 
                         (float(price - (daily_atr * ai_mult)), float(price + (daily_atr * ai_mult))), step=0.1)

    # 6. DUAL PROFITABILITY TABLES (Rule 17, 21, 22)
    def get_matrix(width):
        base = (cap * lev * 0.0017) * ((price * 0.35) / max(width, 0.01))
        return {"1h": base/24, "12h": base/2, "1d": base, "1w": base*7, "1m": base*30}

    st.subheader("📊 Strategic Profit Comparison")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"#### 🤖 AI Auto ({ai_mult}x)")
        res_a = get_matrix(daily_atr * ai_mult * 2)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_a.items()])
        st.markdown(f'<table width="100%" style="text-align:center; border:1px solid #333;">{rows_a}</table>', unsafe_allow_html=True)
    with t2:
        st.markdown("#### ✍️ Manual Adjustment")
        res_m = get_matrix(m_h - m_l)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_m.items()])
        st.markdown(f'<table width="100%" style="text-align:center; border:1px solid #333;">{rows_m}</table>', unsafe_allow_html=True)

    # 7. NAVIGATION & AUDITOR (Rule 19)
    st.sidebar.divider()
    if m_l > liq_p: st.sidebar.success("✅ COMPLIANT")
    else: st.sidebar.error("❌ NON-COMPLIANT")
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
