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
.styled-table {{ width:100%; border-collapse: collapse; }}
.styled-table th, .styled-table td {{ border: 1px solid #333; padding: 10px; text-align: center; }}
</style>""", unsafe_allow_html=True)

df, btc_p, daily_atr, status = fetch_base_data('1d')

if status:
    # Rule 13: Universal Banner
    price = df['close'].iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BITCOIN", f"${btc_p:,.2f}")
    c2.metric("S SOLANA", f"${price:,.2f}")
    c3.metric("DAILY ATR (14d)", f"{daily_atr:.2f}")
    st.divider()

    # SIDEBAR SETTINGS
    st.sidebar.header("DefiTuna Parameters")
    capital = st.sidebar.number_input("Capital ($)", value=10000.0)
    leverage = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    bias = st.sidebar.selectbox("Market Bias", ["Bullish 🚀", "Neutral ⚖️", "Bearish 📉"])

    # RULE 3: DEFITUNA AUTO-FORECASTER MATH
    # Bullish: 2.2 | Neutral: 2.7 | Bearish: 3.2
    mult = 2.2 if bias == "Bullish 🚀" else 3.2 if bias == "Bearish 📉" else 2.7
    auto_low = price - (daily_atr * mult)
    auto_high = price + (daily_atr * mult)

    # RULE 6: LIQUIDATION FLOOR
    liq_price = price * (1 - (1 / leverage) * 0.45)

    # MAIN UI
    st.markdown('<div class="predictive-box">', unsafe_allow_html=True)
    st.subheader(f"🔮 DefiTuna Auto-Forecaster ({bias})")
    
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        m_low, m_high = st.slider("Adjust Yield Range", float(price*0.2), float(price*1.8), (float(auto_low), float(auto_high)))
    with col_r2:
        st.metric("LIQUIDATION PRICE", f"${liq_price:,.2f}")

    # RULE 7: COLLISION ALERT
    if m_low <= liq_price:
        st.error(f"⚠️ RISK ALERT: Range Low (${m_low:,.2f}) is below Liquidation (${liq_price:,.2f})!")

    st.markdown(f"### Target Zone: **${m_low:,.2f} — ${m_high:,.2f}**")
    st.markdown('</div>', unsafe_allow_html=True)

    # RULE 17: PROFITABILITY CALCULATOR (1h, 3h, 6h, 12h, 1d, 1w, 1m)
    st.divider()
    st.subheader("📊 Profitability Matrix")
    
    range_width = max(m_high - m_low, 0.01)
    # Yield Logic based on Capital, Leverage, and Range Tightness
    base_daily = (capital * leverage * 0.0017) * ((price * 0.35) / range_width)
    
    intervals = {
        "1 Hour": base_daily / 24,
        "3 Hour": (base_daily / 24) * 3,
        "6 Hour": (base_daily / 24) * 6,
        "12 Hour": (base_daily / 24) * 12,
        "1 Day": base_daily,
        "1 Week": base_daily * 7,
        "1 Month": base_daily * 30
    }

    rows = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/capital)*100:.2f}%</td></tr>" for k, v in intervals.items()])
    st.markdown(f"""
        <table class="styled-table">
            <tr><th>Timeframe</th><th>Estimated Profit</th><th>ROI (%)</th></tr>
            {rows}
        </table>
    """, unsafe_allow_html=True)

    # BACK TO HUB
    st.sidebar.divider()
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
