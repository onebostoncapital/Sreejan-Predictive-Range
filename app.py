import streamlit as st
import pandas as pd
from data_engine import fetch_base_data

st.set_page_config(page_title="Predictive Range Model", layout="wide")

# 1. THEME & STYLING (Rule 5 & 14)
theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg = "#000000" if theme == "Dark Mode" else "#FFFFFF"
txt = "#FFFFFF" if theme == "Dark Mode" else "#000000"
accent = "#D4AF37"

st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    [data-testid="stMetricValue"] {{ color: {txt} !important; font-family: 'monospace'; }}
    [data-testid="stMetricLabel"] {{ color: {accent} !important; }}
    .predictive-box {{ border: 2px solid {accent}; padding: 20px; border-radius: 10px; background: {"#050505" if theme=="Dark Mode" else "#f9f9f9"}; margin-bottom: 20px; }}
    .forecast-display {{ background-color: {"#111" if theme=="Dark Mode" else "#eee"}; padding: 15px; border-radius: 8px; border-left: 5px solid {accent}; margin-bottom: 20px; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 10px; }}
    .styled-table th, .styled-table td {{ border: 1px solid #444; padding: 10px; text-align: center; }}
    .styled-table th {{ background-color: {"#111" if theme=="Dark Mode" else "#eee"}; color: {accent}; }}
</style>""", unsafe_allow_html=True)

# 2. DATA ENGINE (Rule 13)
df, btc_p, daily_atr, status = fetch_base_data('1d')

if status:
    price = df['close'].iloc[-1]
    
    # UNIVERSAL PRICE BANNER
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BITCOIN", f"${btc_p:,.2f}")
    c2.metric("S SOLANA", f"${price:,.2f}")
    c3.metric("ATR (14d)", f"{daily_atr:.2f}")
    st.divider()

    # 3. SIDEBAR PARAMETERS
    st.sidebar.header("DefiTuna Parameters")
    capital = st.sidebar.number_input("Capital ($)", value=10000.0)
    leverage = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    bias = st.sidebar.selectbox("Market Bias", ["Bullish 🚀", "Neutral ⚖️", "Bearish 📉"])

    # 4. RULE 3: THE SOUL - AUTO-FORECASTER CALCULATION
    mult = 2.2 if bias == "Bullish 🚀" else 3.2 if bias == "Bearish 📉" else 2.7
    auto_l = price - (daily_atr * mult)
    auto_h = price + (daily_atr * mult)
    auto_w = max(auto_h - auto_l, 0.01)

    # 5. LIQUIDATION CALC (Rule 6)
    liq_p = price * (1 - (1 / leverage) * 0.45)

    # 6. AUTO-FORECASTER DISPLAY (The Missing Section)
    st.markdown(f"""
    <div class="forecast-display">
        <h3 style="margin:0; color:{accent};">📡 DefiTuna Auto-Forecaster Range</h3>
        <p style="font-size: 20px; margin: 10px 0;">
            Based on <b>{bias}</b> bias and <b>{mult}x ATR</b>, the predicted range is: 
            <span style="color:{accent}; font-family:monospace;">${auto_l:,.2f} — ${auto_h:,.2f}</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 7. INTERACTIVE MANUAL RANGE BOX
    st.markdown('<div class="predictive-box">', unsafe_allow_html=True)
    st.subheader("✍️ Manual Custom Range Adjustment")
    
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        # MANUAL SLIDER
        m_l, m_h = st.slider("Fine-Tune Your Yield Zone", 
                             float(price*0.1), float(price*1.9), 
                             (float(auto_l), float(auto_h)), step=0.1)
        manual_w = max(m_h - m_l, 0.01)
    with col_r2:
        st.metric("LIQUIDATION FLOOR", f"${liq_p:,.2f}")

    if m_l <= liq_p:
        st.error(f"⚠️ COLLISION ALERT: Manual Low is below Liquidation Price!")
    st.markdown('</div>', unsafe_allow_html=True)

    # 8. DUAL DYNAMIC TABLES (Rule 17 & 22)
    st.subheader("📊 Dynamic Yield Comparison Matrix")
    
    def get_matrix(width_to_use):
        base_daily = (capital * leverage * 0.0017) * ((price * 0.35) / width_to_use)
        return {
            "1 Hour": base_daily / 24, "3 Hour": (base_daily / 24) * 3,
            "6 Hour": (base_daily / 24) * 6, "12 Hour": (base_daily / 24) * 12,
            "1 Day": base_daily, "1 Week": base_daily * 7, "1 Month": base_daily * 30
        }

    t_col1, t_col2 = st.columns(2)

    with t_col1:
        st.markdown(f"#### 🤖 Auto-Range Table")
        auto_res = get_matrix(auto_w)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/capital)*100:.2f}%</td></tr>" for k, v in auto_res.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Time</th><th>Profit</th><th>ROI</th></tr>{rows_a}</table>', unsafe_allow_html=True)

    with t_col2:
        st.markdown("#### ✍️ Manual Range Table")
        manual_res = get_matrix(manual_w)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/capital)*100:.2f}%</td></tr>" for k, v in manual_res.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Time</th><th>Profit</th><th>ROI</th></tr>{rows_m}</table>', unsafe_allow_html=True)

    # 9. STRATEGY AUDITOR (Rule 19)
    st.sidebar.divider()
    st.sidebar.subheader("🛡️ Strategy Auditor")
    if m_l > liq_p:
        st.sidebar.success("✅ COMPLIANT")
    else:
        st.sidebar.error("❌ NON-COMPLIANT")
    
    st.sidebar.divider()
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
