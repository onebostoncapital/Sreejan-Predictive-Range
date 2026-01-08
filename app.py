import streamlit as st
import pandas as pd
from data_engine import fetch_base_data
import streamlit.components.v1 as components

# 1. CORE CONFIGURATION
st.set_page_config(page_title="Sreejan Predictive Range", layout="wide")

# Rule 14: Theme Toggle
theme = st.sidebar.radio("Display Theme", ["Dark Mode", "Light Mode"])
bg_color = "#000000" if theme == "Dark Mode" else "#FFFFFF"
text_color = "#FFFFFF" if theme == "Dark Mode" else "#000000"
accent_gold = "#D4AF37"

# Rule 5: Master CSS Styling
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color} !important; }}
    [data-testid="stMetricValue"] {{ color: {text_color} !important; font-family: 'Roboto Mono'; }}
    [data-testid="stMetricLabel"] {{ color: {accent_gold} !important; }}
    .predictive-box {{ 
        border: 2px solid {accent_gold}; padding: 25px; border-radius: 12px; 
        background: {"#050505" if theme == "Dark Mode" else "#F9F9F9"}; margin-top: 20px; 
    }}
    .styled-table {{ width:100%; color: {text_color}; border-collapse: collapse; margin: 15px 0; }}
    .styled-table th {{ background-color: #1A1C23; color: {accent_gold}; padding: 10px; border: 1px solid #333; }}
    .styled-table td {{ padding: 10px; border: 1px solid #222; text-align: center; }}
    .forecast-box {{ border-left: 5px solid {accent_gold}; padding-left: 15px; margin: 20px 0; }}
    </style>
""", unsafe_allow_html=True)

# 2. DATA PROCESSING
df, btc_p, daily_atr, status = fetch_base_data('1d')

if status:
    price = df['close'].iloc[-1]
    ema20, sma200 = df['20_ema'].iloc[-1], df['200_sma'].iloc[-1]

    # Rule 13: Universal Price Banner
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BITCOIN", f"${btc_p:,.2f}")
    c2.metric("S SOLANA", f"${price:,.2f}")
    c3.metric("DAILY ATR", f"{daily_atr:.2f}")
    st.divider()

    # 3. SIDEBAR RISK SETTINGS
    st.sidebar.header("🎛️ Yield Controls")
    capital = st.sidebar.number_input("Portfolio Capital ($)", value=10000.0)
    leverage = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    bias = st.sidebar.selectbox("Range Bias", ["Bullish 🚀", "Neutral ⚖️", "Bearish 📉"])

    # 4. AUTO FORECASTER LOGIC (Rule 18)
    st.markdown('<div class="forecast-box">', unsafe_allow_html=True)
    st.subheader("📡 Auto Forecaster")
    if price > sma200 and price > ema20:
        forecast, f_color = "BULLISH ACCELERATION", "#00FFA3"
    elif price < sma200 and price < ema20:
        forecast, f_color = "BEARISH DECAY", "#FF4B4B"
    else:
        forecast, f_color = "CONSOLIDATION / NEUTRAL", "#888"
    
    st.markdown(f"Current Sentiment: <span style='color:{f_color}; font-weight:bold;'>{forecast}</span>", unsafe_allow_html=True)
    st.caption("Forecast derived from $20\text{ EMA}$ and $200\text{ SMA}$ positioning.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 5. PREDICTIVE RANGE BOX (Rule 6 & 7)
    liq_price = price * (1 - (1 / leverage) * 0.45)
    mult = 3.2 if bias == "Bearish 📉" else 2.2 if bias == "Bullish 🚀" else 2.7
    auto_low, auto_high = price - (daily_atr * mult), price + (daily_atr * mult)

    st.markdown('<div class="predictive-box">', unsafe_allow_html=True)
    st.header("🔮 Yield Range Model")
    
    r1, r2 = st.columns([2, 1])
    with r1:
        m_low, m_high = st.slider("Manual Zone Tuning", float(price*0.3), float(price*1.7), (float(auto_low), float(auto_high)))
    with r2:
        st.metric("LIQUIDATION FLOOR", f"${liq_price:,.2f}")

    if m_low <= liq_price:
        st.error(f"⚠️ CRITICAL RISK: Range Low (${m_low:,.2f}) is BELOW Liquidation (${liq_price:,.2f})!")

    # 6. MULTI-TIMEFRAME PROFITABILITY CALCULATOR (Rule 17)
    st.divider()
    st.subheader("💹 Profitability Projection Matrix")
    
    # Yield Logic: Efficiency based on Range Width
    range_width = max(m_high - m_low, 0.01)
    base_daily_yield = (capital * leverage * 0.0017) * ((price * 0.35) / range_width)
    
    timeframes = {
        "1 Hour": base_daily_yield / 24,
        "3 Hour": (base_daily_yield / 24) * 3,
        "6 Hour": (base_daily_yield / 24) * 6,
        "12 Hour": (base_daily_yield / 24) * 12,
        "1 Day": base_daily_yield,
        "1 Week": base_daily_yield * 7,
        "1 Month": base_daily_yield * 30
    }

    # Display as a Styled Table
    rows = "".join([f"<tr><td>{tf}</td><td>${val:,.2f}</td><td>{(val/capital)*100:.2f}%</td></tr>" for tf, val in timeframes.items()])
    st.markdown(f"""
        <table class="styled-table">
            <tr><th>Time Horizon</th><th>Est. Profit ($)</th><th>ROI (%)</th></tr>
            {rows}
        </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Rule 4: Back to Hub Link
    st.sidebar.divider()
    st.sidebar.link_button("🔙 Back to Main Hub", "https://sreejan-main-hub-link.streamlit.app/")
