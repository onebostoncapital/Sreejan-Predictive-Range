import streamlit as st
from data_engine import fetch_base_data

st.set_page_config(page_title="Range Model", layout="wide")

# Rule 14: Theme Toggle
theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg = "#000000" if theme == "Dark Mode" else "#FFFFFF"
txt = "#FFFFFF" if theme == "Dark Mode" else "#000000"
st.markdown(f"<style>.stApp {{ background-color: {bg}; color: {txt} !important; }} [data-testid='stMetricLabel'] {{ color: #D4AF37 !important; }}</style>", unsafe_allow_html=True)

df, btc_p, daily_atr, status = fetch_base_data('1d')

if status:
    # Rule 13: Price Banner
    c1, c2 = st.columns(2)
    c1.metric("₿ BTC", f"${btc_p:,.2f}")
    c2.metric("S SOL", f"${df['close'].iloc[-1]:,.2f}")
    st.divider()

    price = df['close'].iloc[-1]
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    
    # Rule 6: Liquidation in Range Model
    liq_price = price * (1 - (1 / lev) * 0.45)
    auto_low = price - (daily_atr * 2.5)
    auto_high = price + (daily_atr * 2.5)
    
    m_low, m_high = st.slider("Yield Zone", float(price*0.3), float(price*1.7), (float(auto_low), float(auto_high)))

    col1, col2 = st.columns(2)
    col1.metric("LIQUIDATION FLOOR", f"${liq_price:,.2f}")
    col2.metric("TARGET RANGE LOW", f"${m_low:,.2f}")

    # Rule 7: Collision Alert
    if m_low <= liq_price:
        st.error("⚠️ CRITICAL RISK: Range Low is below Liquidation Floor!")
