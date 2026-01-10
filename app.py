import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
from datetime import datetime
import json

# MAGIC COMMAND:
# streamlit run app.py

# 1. STYLE & THEME
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")
bias_color = {"Neutral": "#D4AF37", "Bullish": "#00FF7F", "Bearish": "#FF4B4B"}

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-text {{ font-weight: bold; font-family: monospace; font-size: 32px; }}
    .ai-card {{ border: 2px solid var(--b-col); padding: 25px; border-radius: 15px; background: #050505; margin-bottom: 25px; box-shadow: 0 0 20px var(--b-col); }}
    .tag {{ background: #222; color: #aaa; padding: 3px 10px; border-radius: 12px; font-size: 11px; border: 1px solid #444; margin-right: 8px; }}
</style>""", unsafe_allow_html=True)

# 2. DATA & AI INTELLIGENCE ENGINE
df, btc_p, _, status = fetch_base_data('1d')

def get_ai_bias(df):
    # Rule 45: Trend Score Logic
    close = df['close']
    sma20 = close.rolling(window=20).mean().iloc[-1]
    
    # Simple RSI Calculation
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs.iloc[-1]))
    
    current_p = close.iloc[-1]
    
    if current_p > sma20 and rsi > 55: return "Bullish", rsi
    elif current_p < sma20 and rsi < 45: return "Bearish", rsi
    else: return "Neutral", rsi

if status:
    price = df['close'].iloc[-1]
    # TRIGGER AI BIAS
    auto_bias, rsi_val = get_ai_bias(df)
    
    # 3. AI RANGE CALCULATION
    h_l = df['high']-df['low']
    current_atr = h_l.rolling(14).mean().iloc[-1]
    ai_mult = 2.2 if rsi_val > 60 or rsi_val < 40 else 3.2 # Tighter in trends
    
    # Apply Directional Rule 40
    bias_shift = 0
    if auto_bias == "Bullish": bias_shift = (current_atr * 0.7)
    if auto_bias == "Bearish": bias_shift = -(current_atr * 0.7)

    auto_l = price - (current_atr * ai_mult) + bias_shift
    auto_h = price + (current_atr * ai_mult) + bias_shift
    c_color = bias_color[auto_bias]

    # 4. DASHBOARD DISPLAY
    st.title("🏹 Sreejan AI: Autonomous Forecaster")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="ai-card" style="--b-col: {c_color};">
            <div style="display: flex; justify-content: space-between;">
                <span class="tag" style="color:{c_color}; border-color:{c_color};">AI DETECTED BIAS: {auto_bias.upper()}</span>
                <span class="tag">RSI: {rsi_val:.1f}</span>
            </div>
            <h2 style="margin-top:15px; color:{c_color};">🤖 Auto-Range Prediction</h2>
            <span class="glow-text" style="color:{c_color}; text-shadow: 0 0 15px {c_color};">
                ${auto_l:,.2f} — ${auto_h:,.2f}
            </span>
            <p style="font-size: 13px; opacity:0.7; margin-top:10px;">
                AI has positioned your liquidity to the <b>{auto_bias}</b> side based on current momentum.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.sidebar.header("🕹️ Strategy Parameters")
        cap = st.sidebar.number_input("Total Capital ($)", value=10000.0)
        lev = st.sidebar.slider("Leverage Slider", 1.0, 5.0, 1.5)
        liq_p = price * (1 - (1 / lev) * 0.45)
        
        st.metric("SOL Price", f"${price:,.2f}")
        st.error(f"Liquidation Floor: ${liq_p:,.2f}")

    # 5. MANUAL OVERRIDE & COMPARISON
    st.subheader("✍️ Manual Settings & Profit Matrix")
    m_range = st.slider("Manual Zone Adjust", float(price*0.1), float(price*1.9), value=(float(auto_l), float(auto_h)))
    
    def calc_yield(w):
        d = (cap * lev * 0.0017) * ((price * 0.35) / w)
        return {"Daily": d, "Weekly": d*7}

    res_a = calc_yield(auto_h - auto_l)
    res_m = calc_yield(m_range[1] - m_range[0])

    c_a, c_m = st.columns(2)
    c_a.info(f"🤖 AI Yield ({auto_bias}): ${res_a['Daily']:,.2f}/day")
    c_m.success(f"✍️ Manual Yield: ${res_m['Daily']:,.2f}/day")

    # 6. AUTO-SAVE LEDGER
    entry = {"time": str(datetime.now()), "ai_bias": auto_bias, "range": m_range, "p_day": res_m['Daily']}
    with open("strategy_ledger.txt", "a") as f:
        f.write(json.dumps(entry) + "\n")

    st.sidebar.success("✅ AI Bias & Ledger Synced")
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
