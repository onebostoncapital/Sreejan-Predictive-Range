import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
from datetime import datetime
import json

# MAGIC COMMAND:
# streamlit run app.py

# 1. STYLE & THEME (CLEAN & RESTORED)
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")
bias_color = {"Neutral": "#D4AF37", "Bullish": "#00FF7F", "Bearish": "#FF4B4B"}

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-gold {{ font-weight: bold; text-shadow: 0 0 15px {accent}; font-family: monospace; font-size: 32px; }}
    .ai-card {{ border: 2px solid var(--b-col); padding: 25px; border-radius: 15px; background: #050505; margin-bottom: 25px; box-shadow: 0 0 20px var(--b-col); }}
    .manual-card {{ border: 2px solid #555; padding: 25px; border-radius: 15px; background: #0a0a0a; margin-bottom: 25px; }}
    .liq-box {{ background: #440000; border: 1px solid #ff4b4b; padding: 15px; border-radius: 8px; text-align: center; color: white; }}
    .tag {{ background: #222; color: #aaa; padding: 3px 10px; border-radius: 12px; font-size: 11px; border: 1px solid #444; margin-right: 8px; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 15px; }}
    .styled-table td {{ border: 1px solid #444; padding: 12px; text-align: center; font-family: monospace; }}
</style>""", unsafe_allow_html=True)

# 2. DATA ENGINE
df, btc_p, _, status = fetch_base_data('1d')

def calculate_atr(df):
    h_l, h_c, l_c = df['high']-df['low'], np.abs(df['high']-df['close'].shift()), np.abs(df['low']-df['close'].shift())
    tr = pd.concat([h_l, h_c, l_c], axis=1).max(axis=1)
    return tr.rolling(14).mean().iloc[-1]

if status:
    price = df['close'].iloc[-1]
    current_atr = calculate_atr(df)
    
    # --- HEADER SECTION (RESTORED) ---
    st.title("🏹 Sreejan AI Forecaster Pro")
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC Price", f"${btc_p:,.2f}")
    c2.metric("S SOL Price", f"${price:,.2f}")
    c3.metric("Volatility (ATR)", f"{current_atr:.2f}")
    st.divider()

    # 3. SIDEBAR CONTROLS
    st.sidebar.header("🕹️ Strategy Parameters")
    cap = st.sidebar.number_input("Total Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage Slider", 1.0, 5.0, 1.5)
    bias = st.sidebar.selectbox("🎯 Set Market Bias", ["Neutral", "Bullish", "Bearish"])
    
    liq_p = price * (1 - (1 / lev) * 0.45)

    # 4. AI RANGE FORECAST SECTION
    v_pulse = "COILING" if current_atr < (df['high'].tail(5).mean() * 0.045) else "EXPANDING"
    ai_mult = 3.2 if v_pulse == "COILING" else 2.2
    
    # Directional Logic Shift
    bias_shift = 0
    if bias == "Bullish": bias_shift = (current_atr * 0.7)
    if bias == "Bearish": bias_shift = -(current_atr * 0.7)

    auto_l = price - (current_atr * ai_mult) + bias_shift
    auto_h = price + (current_atr * ai_mult) + bias_shift
    c_color = bias_color[bias]

    st.markdown(f"""
    <div class="ai-card" style="--b-col: {c_color};">
        <div style="display: flex; justify-content: space-between;">
            <span class="tag" style="color:{c_color}; border-color:{c_color};">BIAS: {bias.upper()}</span>
            <span class="tag">V-PULSE: {v_pulse}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
            <div>
                <h2 style="margin:0; color:{c_color};">🤖 AI Range Forecast</h2>
                <span class="glow-gold" style="color:{c_color}; text-shadow: 0 0 15px {c_color};">
                    ${auto_l:,.2f} — ${auto_h:,.2f}
                </span>
            </div>
            <div class="liq-box">
                <span style="font-size: 11px;">LIQUIDATION FLOOR</span><br>
                <span style="font-size: 20px;">${liq_p:,.2f}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. MANUAL MODE SECTION
    st.markdown('<div class="manual-card">', unsafe_allow_html=True)
    st.subheader("✍️ Manual Range Control")
    if 'v_range' not in st.session_state: st.session_state.v_range = (float(auto_l), float(auto_h))
    
    m_range = st.slider("Adjust Manual Zone", float(price*0.1), float(price*1.9), value=st.session_state.v_range, step=0.01)
    st.session_state.v_range = m_range
    m_l, m_h = m_range
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. PROFIT MATRIX
    def calculate_yield(width_val):
        daily = (cap * lev * 0.0017) * ((price * 0.35) / max(width_val, 0.01))
        return {"1 Day": daily, "1 Week": daily*7}

    st.subheader("📊 Profit Comparison")
    t1, t2 = st.columns(2)
    res_a = calculate_yield(auto_h - auto_l)
    res_m = calculate_yield(m_h - m_l)

    with t1:
        st.info(f"🤖 AI Yield: ${res_a['1 Day']:,.2f}/day")
    with t2:
        st.success(f"✍️ Manual Yield: ${res_m['1 Day']:,.2f}/day")

    # 7. LEDGER & RISK AUDIT
    ledger_entry = {"time": str(datetime.now()), "bias": bias, "range": [round(m_l, 2), round(m_h, 2)], "lev": lev}
    with open("strategy_ledger.txt", "a") as f:
        f.write(json.dumps(ledger_entry) + "\n")

    if m_l <= liq_p:
        st.error(f"🚨 RISK ALERT: Manual Low is too close to Liquidation!")
    else:
        st.sidebar.success("✅ Strategy Logged & Compliant")

    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
