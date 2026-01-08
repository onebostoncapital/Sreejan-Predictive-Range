import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data

# 1. CORE IDENTITY & STYLE
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
    .gauge-container {{ width: 100%; background-color: #333; border-radius: 10px; margin: 20px 0; height: 25px; position: relative; border: 1px solid {accent}; }}
    .gauge-fill {{ height: 100%; background: linear-gradient(90deg, #ff4b4b 0%, {accent} 50%, #ff4b4b 100%); border-radius: 10px; transition: width 0.5s; }}
    .price-marker {{ position: absolute; top: -10px; height: 45px; width: 3px; background-color: #FFFFFF; box-shadow: 0 0 10px #FFF; }}
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
    
    # 3. SIDEBAR RISK (Rule 6)
    st.sidebar.header("User Parameters")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    liq_p = price * (1 - (1 / lev) * 0.45)

    # 4. AI BIAS ENGINE (Rule 3)
    if price > df['20_ema'].iloc[-1]:
        ai_bias, ai_mult = "Bullish 🚀", 2.2
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

    # 5. THE AI FORECAST DASHBOARD
    st.markdown(f"""
    <div class="ai-card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <h2 style="margin:0; color:{accent};">📡 Strategic AI Forecast: {ai_bias}</h2>
                <div style="margin: 20px 0;">
                    <span style="font-size: 14px; opacity:0.6;">AUTONOMOUS YIELD ZONE:</span><br>
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

    # 6. MANUAL SOVEREIGNTY (The Fix)
    st.subheader("✍️ Manual Custom Range Adjustment")
    
    # Initialize session state for slider so it doesn't jump
    if 'm_range' not in st.session_state:
        st.session_state.m_range = (float(auto_l), float(auto_h))

    m_range = st.slider("Fine-Tune Your Range", 
                        float(price*0.5), float(price*1.5), 
                        value=st.session_state.m_range, 
                        step=0.01, key="manual_slider_persistent")
    
    st.session_state.m_range = m_range
    m_l, m_h = m_range
    manual_w = max(m_h - m_l, 0.01)

    # 7. VISUAL POSITION GAUGE (Rule 28)
    price_pos = ((price - m_l) / manual_w) * 100
    price_pos = max(0, min(100, price_pos)) # Constrain to 0-100%
    
    st.markdown(f"**Current Price Position in Manual Range: {price_pos:.1f}%**")
    st.markdown(f"""
    <div class="gauge-container">
        <div class="gauge-fill" style="width: 100%;"></div>
        <div class="price-marker" style="left: {price_pos}%;"></div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 30px;">
            <span>LOW: ${m_l:,.2f}</span>
            <span>MID: ${(m_l+m_h)/2:,.2f}</span>
            <span>HIGH: ${m_h:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    

    # 8. DUAL PROFIT MATRICES (Rule 17)
    def get_matrix(width):
        daily_yield = (cap * lev * 0.0017) * ((price * 0.35) / width)
        return {"1h": daily_yield/24, "1d": daily_yield, "1w": daily_yield*7, "1m": daily_yield*30}

    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"#### 🤖 AI Suggested ({ai_mult}x ATR)")
        res_a = get_matrix(auto_w)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_a.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_a}</table>', unsafe_allow_html=True)

    with t2:
        st.markdown("#### ✍️ Manual Custom Adjustment")
        res_m = get_matrix(manual_w)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_m.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_m}</table>', unsafe_allow_html=True)

    # 9. FINAL SAFETY CHECK
    if m_l <= liq_p:
        st.error(f"🚨 CRITICAL: Manual Low (${m_l:,.2f}) is below Liquidation Floor (${liq_p:,.2f})!")

    st.sidebar.divider()
    st.sidebar.metric("LIQUIDATION PRICE", f"${liq_p:,.2f}")
    if m_l > liq_p: st.sidebar.success("✅ STRATEGY COMPLIANT")
    else: st.sidebar.error("❌ NON-COMPLIANT")
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
