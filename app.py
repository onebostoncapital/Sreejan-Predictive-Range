import streamlit as st
from data_engine import fetch_base_data

st.set_page_config(page_title="Terminal Beta: Range Model", layout="wide")

# High-Contrast "True Black" Style
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF !important; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; }
    [data-testid="stMetricLabel"] { color: #D4AF37 !important; }
    h1, h2 { color: #D4AF37 !important; }
    .risk-box { background-color: #220000; border: 2px solid #FF0000; padding: 15px; border-radius: 10px; color: #FF0000; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🔮 Predictive Model: Yield Range")

# Sidebar for Capital and Risk
st.sidebar.header("Capital Settings")
capital = st.sidebar.number_input("Portfolio Capital ($)", value=10000.0)
leverage = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
bias = st.sidebar.selectbox("Market Bias", ["Bullish 🚀", "Neutral ⚖️", "Bearish 📉"])

df, btc_p, daily_atr, status = fetch_base_data('1d')

if status:
    price = df['close'].iloc[-1]
    
    # 1. LIQUIDATION CALCULATION (Connected to Range)
    # 45% Safety rule from Master Rule Book
    liq_price = price * (1 - (1 / leverage) * 0.45)
    
    # 2. AUTOMATED RANGE LOGIC
    # Multipliers based on ATR and Bias
    mult = 3.2 if bias == "Bearish 📉" else 2.2 if bias == "Bullish 🚀" else 2.7
    auto_low, auto_high = price - (daily_atr * mult), price + (daily_atr * mult)

    # 3. INTERACTIVE UI
    col1, col2 = st.columns([2, 1])
    with col1:
        m_low, m_high = st.slider("Fine-Tune Yield Zone", float(price*0.3), float(price*1.7), (float(auto_low), float(auto_high)))
    with col2:
        # Yield Calculation formula from Rule Book
        daily_yield = (capital * leverage * 0.0017) * ((price * 0.35) / max(m_high - m_low, 0.01))
        st.metric("EST. DAILY YIELD", f"${daily_yield:,.2f}")
        st.metric("LIQUIDATION FLOOR", f"${liq_price:,.2f}")

    # 4. SAFETY CHECK (The Collision Rule)
    if m_low <= liq_price:
        st.markdown(f'<div class="risk-box">⚠️ CRITICAL: Range Low (${m_low:,.2f}) is too close to Liquidation (${liq_price:,.2f})!</div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown(f"### Target Range: **${m_low:,.2f} — ${m_high:,.2f}**")
