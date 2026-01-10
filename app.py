import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
from datetime import datetime
import json

# MAGIC COMMAND:
# streamlit run app.py

# 1. STYLE & THEME (LOCKED)
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")
bias_color = {"Neutral": "#D4AF37", "Bullish": "#00FF7F", "Bearish": "#FF4B4B"}

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .header-box {{ margin-bottom: 25px; }}
    .ai-intel-box {{ border: 1px dashed {accent}; padding: 15px; border-radius: 10px; background: rgba(212, 175, 55, 0.05); margin-bottom: 20px; }}
    .ai-card {{ border: 2px solid var(--b-col); padding: 25px; border-radius: 15px; background: #050505; margin-bottom: 20px; box-shadow: 0 0 20px var(--b-col); }}
    .manual-card {{ border: 2px solid #555; padding: 20px; border-radius: 15px; background: #0a0a0a; margin-bottom: 20px; }}
    .glow-gold {{ font-weight: bold; text-shadow: 0 0 15px {accent}; font-family: monospace; font-size: 32px; }}
    .liq-box {{ background: #440000; border: 1px solid #ff4b4b; padding: 12px; border-radius: 8px; text-align: center; color: white; }}
    .tag {{ background: #222; color: #aaa; padding: 3px 10px; border-radius: 12px; font-size: 11px; border: 1px solid #444; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
    .styled-table th {{ background: #222; padding: 10px; border: 1px solid #444; color: #aaa; }}
    .styled-table td {{ border: 1px solid #444; padding: 10px; text-align: center; font-family: monospace; }}
</style>""", unsafe_allow_html=True)

# 2. DATA & AI INTELLIGENCE (AUTOMATIC DIRECTIONAL BIAS)
df, btc_p, _, status = fetch_base_data('1d')

def get_automatic_bias(df):
    close = df['close']
    sma20 = close.rolling(20).mean().iloc[-1]
    # RSI Logic
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
    current_p = close.iloc[-1]
    
    if current_p > sma20 and rsi > 55: return "Bullish", rsi, sma20
    elif current_p < sma20 and rsi < 45: return "Bearish", rsi, sma20
    else: return "Neutral", rsi, sma20

if status:
    price = df['close'].iloc[-1]
    h_l = df['high']-df['low']
    current_atr = h_l.rolling(14).mean().iloc[-1]
    
    # --- HEADER SECTION (LOCKED) ---
    st.markdown('<div class="header-box">', unsafe_allow_html=True)
    st.title("🏹 Sreejan AI Forecaster Pro")
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC Price", f"${btc_p:,.2f}")
    c2.metric("S SOL Price", f"${price:,.2f}")
    c3.metric("Volatility (ATR)", f"{current_atr:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # 3. VISUAL AI INTELLIGENCE SECTION (FIXED: PROMINENT DISPLAY)
    auto_bias, rsi_val, sma_val = get_automatic_bias(df)
    st.markdown(f"""
    <div class="ai-intel-box">
        <h4 style="margin-top:0; color:{accent};">🧠 AI Trend Intelligence Center</h4>
        <div style="display: flex; gap: 20px;">
            <div style="flex: 1;"><b>Detected Trend:</b> <span style="color:{bias_color[auto_bias]}">{auto_bias.upper()}</span></div>
            <div style="flex: 1;"><b>RSI (14):</b> {rsi_val:.2f}</div>
            <div style="flex: 1;"><b>SMA (20):</b> ${sma_val:,.2f}</div>
            <div style="flex: 2; font-size: 12px; opacity:0.8;"><i>AI Logic: Tracking price momentum and strength to auto-align DeFi Tuna Liquidity ranges.</i></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. SIDEBAR CONTROLS (LOCKED)
    st.sidebar.header("🕹️ Strategy Parameters")
    cap = st.sidebar.number_input("Total Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage Slider", 1.0, 5.0, 1.5)
    bias_choice = st.sidebar.selectbox("🎯 Directional Basis", ["AI Automatic", "Neutral", "Bullish", "Bearish"])
    
    final_bias = auto_bias if bias_choice == "AI Automatic" else bias_choice
    liq_p = price * (1 - (1 / lev) * 0.45)

    # 5. AI RANGE FORECAST (LOCKED)
    v_pulse = "COILING" if current_atr < (df['high'].tail(5).mean() * 0.045) else "EXPANDING"
    ai_mult = 3.2 if v_pulse == "COILING" else 2.2
    
    bias_shift = 0
    if final_bias == "Bullish": bias_shift = (current_atr * 0.7)
    if final_bias == "Bearish": bias_shift = -(current_atr * 0.7)

    auto_l = price - (current_atr * ai_mult) + bias_shift
    auto_h = price + (current_atr * ai_mult) + bias_shift
    c_color = bias_color[final_bias]

    st.markdown(f"""
    <div class="ai-card" style="--b-col: {c_color};">
        <div style="display: flex; justify-content: space-between;">
            <span class="tag" style="color:{c_color}; border-color:{c_color};">BASIS: {final_bias.upper()}</span>
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

    # 6. MANUAL RANGE SECTION (LOCKED)
    st.markdown('<div class="manual-card">', unsafe_allow_html=True)
    st.subheader("✍️ Manual Range Control")
    if 'v_range' not in st.session_state: st.session_state.v_range = (float(auto_l), float(auto_h))
    
    m_range = st.slider("Adjust Manual Zone", float(price*0.1), float(price*1.9), value=st.session_state.v_range, step=0.01)
    st.session_state.v_range = m_range
    m_l, m_h = m_range
    st.markdown('</div>', unsafe_allow_html=True)

    # 7. PROFIT COMPARISON TABLES (LOCKED: 1h, 3h, 1d, 1w, 1m)
    def get_projections(l, h):
        w = max(h - l, 0.01)
        h_fee = (cap * lev * 0.00007) * ((price * 0.35) / w)
        return {"1 Hour": h_fee, "3 Hours": h_fee*3, "1 Day": h_fee*24, "1 Week": h_fee*24*7, "1 Month": h_fee*24*30}

    st.subheader("📊 Yield Comparison Matrix")
    col_ai, col_man = st.columns(2)
    ai_proj = get_projections(auto_l, auto_h)
    man_proj = get_projections(m_l, m_h)

    with col_ai:
        st.markdown(f"<h4 style='color:{c_color}'>🤖 AI Strategy Yield</h4>", unsafe_allow_html=True)
        rows = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td></tr>" for k, v in ai_proj.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Timeframe</th><th>Est. Profit</th></tr>{rows}</table>', unsafe_allow_html=True)

    with col_man:
        st.markdown("<h4 style='color:#555'>✍️ Manual Strategy Yield</h4>", unsafe_allow_html=True)
        rows = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td></tr>" for k, v in man_proj.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Timeframe</th><th>Est. Profit</th></tr>{rows}</table>', unsafe_allow_html=True)

    # 8. AUTO-SAVE LEDGER
    entry = {"time": str(datetime.now()), "bias": final_bias, "range": [round(m_l, 2), round(m_h, 2)], "daily": round(man_proj["1 Day"], 2)}
    with open("strategy_ledger.txt", "a") as f:
        f.write(json.dumps(entry) + "\n")

    if m_l <= liq_p:
        st.error(f"🚨 RISK ALERT: Manual Low (${m_l:,.2f}) is below Liquidation Floor!")
    else:
        st.sidebar.success("✅ Strategy Logged to Ledger")

    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
