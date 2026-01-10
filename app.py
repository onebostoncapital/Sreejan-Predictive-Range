import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
from datetime import datetime
import json

# MAGIC COMMAND:
# streamlit run app.py

# 1. STYLE & THEME (CLEAN DASHBOARD)
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")
bias_color = {"Neutral": "#D4AF37", "Bullish": "#00FF7F", "Bearish": "#FF4B4B"}

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-gold {{ font-weight: bold; text-shadow: 0 0 15px {accent}; font-family: monospace; font-size: 32px; }}
    .bias-card {{ border: 3px solid #333; padding: 20px; border-radius: 15px; background: #111; text-align: center; margin-bottom: 10px; }}
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
    
    st.title("🏹 Sreejan AI Forecaster Pro")
    
    # 3. DIRECTIONAL BIAS (MANUAL CONTROL)
    col_a, col_b, col_c = st.columns([1, 2, 1])
    
    with col_a:
        st.markdown('<div class="bias-card">', unsafe_allow_html=True)
        bias = st.radio("🎯 SELECT MARKET BIAS", ["Neutral", "Bullish", "Bearish"], horizontal=False)
        st.markdown('</div>', unsafe_allow_html=True)

    # Logic: AI Range + User Bias Shift
    v_pulse = "COILING" if current_atr < (df['high'].tail(5).mean() * 0.045) else "EXPANDING"
    ai_mult = 3.2 if v_pulse == "COILING" else 2.2
    
    bias_shift = 0
    if bias == "Bullish": bias_shift = (current_atr * 0.7)
    if bias == "Bearish": bias_shift = -(current_atr * 0.7)

    auto_l = price - (current_atr * ai_mult) + bias_shift
    auto_h = price + (current_atr * ai_mult) + bias_shift
    c_color = bias_color[bias]

    with col_b:
        st.markdown(f"""
        <div class="ai-card" style="--b-col: {c_color};">
            <div style="display: flex; justify-content: space-between;">
                <span class="tag" style="color:{c_color}; border-color:{c_color};">MODE: {bias.upper()}</span>
                <span class="tag">VOLATILITY: {v_pulse}</span>
            </div>
            <h2 style="margin-top:15px; color:{c_color};">🤖 AI Range Forecast</h2>
            <span class="glow-gold" style="text-shadow: 0 0 15px {c_color}; color:{c_color};">
                ${auto_l:,.2f} — ${auto_h:,.2f}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col_c:
        st.sidebar.header("🕹️ Strategy Parameters")
        cap = st.sidebar.number_input("Total Capital ($)", value=10000.0)
        lev = st.sidebar.slider("Leverage Slider", 1.0, 5.0, 1.5)
        liq_p = price * (1 - (1 /
