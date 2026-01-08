import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data

# 1. CORE IDENTITY & STYLE (Rules 5, 14, 27)
st.set_page_config(page_title="Sreejan AI Forecaster", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")

st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-gold {{ color: {accent}; font-weight: bold; text-shadow: 0 0 15px {accent}; font-family: monospace; font-size: 30px; }}
    .ai-box {{ border: 2px solid {accent}; padding: 20px; border-radius: 12px; background: {"#050505" if theme=="Dark Mode" else "#f9f9f9"}; margin-bottom: 20px; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 10px; }}
    .styled-table th, .styled-table td {{ border: 1px solid #444; padding: 12px; text-align: center; }}
</style>""", unsafe_allow_html=True)

# 2. DATA ENGINE & ATR CALCULATION (Prevents KeyError)
df, btc_p, daily_atr_val, status = fetch_base_data('1d')

def calculate_atr_series(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

if status:
    df['atr_val'] = calculate_atr_series(df)
    price = df['close'].iloc[-1]
    
    # 3. AI INTELLIGENCE (V-Pulse & Correlation)
    current_vol = df['atr_val'].iloc[-1]
    avg_vol_5d = df['atr_val'].tail(5).mean()
    vol_pulse = "EXPANDING" if current_vol > avg_vol_5d else "COILING (High Risk)"
    btc_sentiment = "DRAGGING" if btc_p < (btc_p * 0.99) else "SUPPORTIVE"

    # AI Bias Logic
    if btc_sentiment == "SUPPORTIVE" and price > df['20_ema'].iloc[-1]:
        ai_bias, ai_mult = "Bullish 🚀", 2.2
    elif btc_sentiment == "DRAGGING" or vol_pulse == "COILING (High Risk)":
        ai_bias, ai_mult = "Bearish 📉", 3.2
    else:
        ai_bias, ai_mult = "Neutral ⚖️", 2.7

    # 4. UNIVERSAL PRICE BANNER (With Plain English Tooltips)
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BITCOIN", f"${btc_p:,.2f}", 
              help="The current world price of Bitcoin. It often leads the direction of other coins.")
    c2.metric("S SOLANA", f"${price:,.2f}", 
              help="The current price of Solana, the asset you are planning to trade.")
    c3.metric("DAILY ATR", f"{current_vol:.2f}", 
              help="Average True Range: This measures how many dollars the price typically moves in a day. It is used to set your safety boundaries.")
    st.divider()

    # 5. THE AI INTELLIGENCE DASHBOARD (Glow Soul)
    auto_l = price - (current_vol * ai_mult)
    auto_h = price + (current_vol * ai_mult)
    auto_w = max(auto_h - auto_l, 0.01)

    st.markdown(f"""
    <div class="ai-box">
        <h2 style="margin:0; color:{accent};">📡 AI Autonomous Forecast: {ai_bias}</h2>
        <p style="opacity:0.8;">
            <b>Market State:</b> {vol_pulse} 
            <span style="cursor:help;" title="COILING means the price is squeezing and a big move is coming. EXPANDING means the price is already moving fast.">ℹ️</span>
            | <b>BTC Status:</b> {btc_sentiment}
            <span style="cursor:help;" title="SUPPORTIVE means Bitcoin is stable or rising, helping your trade. DRAGGING means Bitcoin is falling, pulling your trade down.">ℹ️</span>
        </p>
        <div style="margin: 20px 0;">
            <span style="font-size: 14px; opacity:0.6;">PREDICTED YIELD ZONE (Safe Range):</span><br>
            <span class="glow-gold">${auto_l:,.2f} — ${auto_h:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 6. SIDEBAR & MANUAL CONTROLS
    st.sidebar.header("Risk Settings")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0, help="Your total investment amount.")
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5, help="Borrowing multiplier. Higher leverage increases profit but moves your liquidation price closer.")
    liq_p = price * (1 - (1 / lev) * 0.45)
    
    m_l, m_h = st.slider("Manual Range Adjustment", float(price*0.1), float(price*1.9), 
                         (float(auto_l), float(auto_h)), step=0.1,
                         help="Slide these to manually widen or tighten your profit zone.")
    manual_w = max(m_h - m_l, 0.01)

    # 7. DUAL PROFITABILITY MATRICES
    def get_matrix(width):
        base = (cap * lev * 0.0017) * ((price * 0.35) / width)
        return {"1 Hour": base/24, "1 Day": base, "1 Week": base*7, "1 Month": base*30}

    st.subheader("📊 Strategic Profit Comparison", help="Compare the AI's safe suggestion vs your manual custom setup.")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"#### 🤖 AI Auto ({ai_mult}x)")
        res_a = get_matrix(auto_w)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_a.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_a}</table>', unsafe_allow_html=True)
    with t2:
        st.markdown("#### ✍️ Manual Adjustment")
        res_m = get_matrix(manual_w)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_m.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_m}</table>', unsafe_allow_html=True)

    # 8. AUDITOR
    st.sidebar.divider()
    st.sidebar.subheader("🛡️ Compliance Auditor", help="Checks if your manual range is dangerously close to your liquidation price.")
    if m_l > liq_p: 
        st.sidebar.success("✅ STRATEGY COMPLIANT")
    else: 
        st.sidebar.error("❌ NON-COMPLIANT")
    
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
