import streamlit as st
import pandas as pd
from data_engine import fetch_base_data

st.set_page_config(page_title="Predictive Range Model", layout="wide")

# THEME TOGGLE (Rule 14)
theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg = "#000000" if theme == "Dark Mode" else "#FFFFFF"
txt = "#FFFFFF" if theme == "Dark Mode" else "#000000"
accent = "#D4AF37"

st.markdown(f"""<style>.stApp {{ background-color: {bg}; color: {txt} !important; }} 
[data-testid="stMetricValue"] {{ color: {txt} !important; }}
[data-testid="stMetricLabel"] {{ color: {accent} !important; }}
.predictive-box {{ border: 2px solid {accent}; padding: 20px; border-radius: 10px; background: {"#050505" if theme=="Dark Mode" else "#f0f0f0"}; }}
.styled-table {{ width:100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9em; }}
.styled-table th, .styled-table td {{ border: 1px solid #333; padding: 8px; text-align: center; }}
.styled-table th {{ background-color: {"#111" if theme=="Dark Mode" else "#eee"}; color: {accent}; }}
</style>""", unsafe_allow_html=True)

df, btc_p, daily_atr, status = fetch_base_data('1d')

if status:
    price = df['close'].iloc[-1]
    
    # 1. UNIVERSAL BANNER (Rule 13)
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC", f"${btc_p:,.2f}")
    c2.metric("S SOL", f"${price:,.2f}")
    c3.metric("ATR (14d)", f"{daily_atr:.2f}")
    st.divider()

    # 2. SIDEBAR SETTINGS
    st.sidebar.header("DefiTuna Parameters")
    capital = st.sidebar.number_input("Capital ($)", value=10000.0)
    leverage = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    bias = st.sidebar.selectbox("Market Bias", ["Bullish 🚀", "Neutral ⚖️", "Bearish 📉"])

    # 3. RULE 3: AUTO-FORECASTER MATH (Rule 3)
    mult = 2.2 if bias == "Bullish 🚀" else 3.2 if bias == "Bearish 📉" else 2.7
    auto_low = price - (daily_atr * mult)
    auto_high = price + (daily_atr * mult)
    auto_width = max(auto_high - auto_low, 0.01)

    # 4. RULE 6: LIQUIDATION FLOOR
    liq_price = price * (1 - (1 / leverage) * 0.45)

    # 5. MAIN UI: RANGE MODEL
    st.markdown('<div class="predictive-box">', unsafe_allow_html=True)
    st.subheader(f"🔮 Range Comparison Terminal: {bias}")
    
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        m_low, m_high = st.slider("Manual Range Adjustment", float(price*0.1), float(price*1.9), (float(auto_low), float(auto_high)))
        manual_width = max(m_high - m_low, 0.01)
    with col_r2:
        st.metric("LIQUIDATION PRICE", f"${liq_price:,.2f}")

    if m_low <= liq_price:
        st.error(f"⚠️ CRITICAL: Manual Range Low is below Liquidation!")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. RULE 22: DUAL PROFITABILITY TABLES
    st.divider()
    t_col1, t_col2 = st.columns(2)

    def calculate_intervals(width):
        # Master Yield Formula
        base_daily = (capital * leverage * 0.0017) * ((price * 0.35) / width)
        return {
            "1 Hour": base_daily / 24, "3 Hour": (base_daily / 24) * 3,
            "6 Hour": (base_daily / 24) * 6, "12 Hour": (base_daily / 24) * 12,
            "1 Day": base_daily, "1 Week": base_daily * 7, "1 Month": base_daily * 30
        }

    # Table A: Auto Forecaster
    with t_col1:
        st.markdown(f"#### 🤖 Auto-Forecaster ({mult}x ATR)")
        st.caption(f"Range: ${auto_low:,.2f} - ${auto_high:,.2f}")
        auto_data = calculate_intervals(auto_width)
        rows_auto = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/capital)*100:.2f}%</td></tr>" for k, v in auto_data.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_auto}</table>', unsafe_allow_html=True)

    # Table B: Manual Adjustment
    with t_col2:
        st.markdown("#### ✍️ Manual Custom Range")
        st.caption(f"Range: ${m_low:,.2f} - ${m_high:,.2f}")
        manual_data = calculate_intervals(manual_width)
        rows_manual = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/capital)*100:.2f}%</td></tr>" for k, v in manual_data.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_manual}</table>', unsafe_allow_html=True)

    # 7. RULE 19 & 20: STRATEGY AUDITOR
    st.sidebar.divider()
    st.sidebar.subheader("🛡️ Strategy Auditor")
    if m_low > liq_price:
        st.sidebar.success("✅ Compliance: STRATEGY OK")
    else:
        st.sidebar.error("❌ Compliance: NON-COMPLIANT")
    
    # LINK BACK TO HUB
    st.sidebar.divider()
    st.sidebar.link_button("🔙 Main Hub", "https://sreejan-main-hub-link.streamlit.app/")
