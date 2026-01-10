import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
from datetime import datetime
import json

# MAGIC COMMAND:
# streamlit run app.py

# 1. STYLE ENGINE (LOCKED UI)
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")
bias_color = {"Neutral": "#D4AF37", "Bullish": "#00FF7F", "Bearish": "#FF4B4B"}

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .ribbon {{ background: rgba(255, 255, 255, 0.03); border-radius: 10px; padding: 15px; margin-bottom: 20px; border: 1px solid #333; }}
    .ribbon-label {{ color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }}
    .ribbon-val {{ font-family: monospace; font-size: 15px; font-weight: bold; color: white; }}
    .ai-card {{ border: 2px solid var(--b-col); padding: 25px; border-radius: 15px; background: #050505; position: relative; margin-bottom: 20px; box-shadow: 0 0 20px var(--b-col); min-height: 180px; }}
    .liq-box {{ position: absolute; right: 25px; top: 50%; transform: translateY(-50%); border: 1px solid #FF4B4B; padding: 15px; border-radius: 8px; background: rgba(255, 75, 75, 0.1); text-align: center; min-width: 140px; }}
    .liq-label {{ font-size: 10px; color: #FF4B4B; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }}
    .liq-val {{ font-size: 22px; font-weight: bold; color: white; }}
    .glow-gold {{ font-weight: bold; text-shadow: 0 0 15px var(--b-col); font-family: monospace; font-size: 34px; margin-top: 10px; }}
</style>""", unsafe_allow_html=True)

# 2. CRASH-PROOF DATA ENGINE
sol_df, _, _, sol_status = fetch_base_data('1d')
btc_raw, btc_p, btc_df, btc_status = fetch_base_data('1d')

def get_stats(s_df, b_df):
    stats = {"sol": ["---"]*5, "btc": ["---"]*3}
    # Safety Check: Must be a DataFrame and not empty
    if isinstance(s_df, pd.DataFrame) and not s_df.empty:
        s30 = s_df.tail(30)
        stats["sol"] = [s30['high'].max(), s30['low'].min(), s30['close'].mean(), s_df['high'].iloc[-1], s_df['low'].iloc[-1]]
    
    if isinstance(b_df, pd.DataFrame) and not b_df.empty:
        b30 = b_df.tail(30)
        stats["btc"] = [b30['high'].max(), b30['low'].min(), b30['close'].mean()]
    return stats

if sol_status:
    price = sol_df['close'].iloc[-1]
    current_atr = (sol_df['high']-sol_df['low']).rolling(14).mean().iloc[-1]
    perf = get_stats(sol_df, btc_df)
    def f(v, d=1): return f"${v:,.{d}f}" if isinstance(v, (int, float)) else v

    # --- HEADER & RIBBON ---
    st.title("🏹 Sreejan AI Forecaster Pro")
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC Price", f(btc_p, 2))
    c2.metric("S SOL Price", f(price, 2))
    c3.metric("Volatility (ATR)", f(current_atr, 2))

    st.markdown('<div class="ribbon">', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(f'<p class="ribbon-label">30D Range (SOL)</p><p class="ribbon-val">H: {f(perf["sol"][0])} | L: {f(perf["sol"][1])}</p>', unsafe_allow_html=True)
    r2.markdown(f'<p class="ribbon-label">Today\'s Range (SOL)</p><p class="ribbon-val">H: {f(perf["sol"][3])} | L: {f(perf["sol"][4])}</p>', unsafe_allow_html=True)
    r3.markdown(f'<p class="ribbon-label">30D Avg Price</p><p class="ribbon-val">SOL: {f(perf["sol"][2])} | BTC: {f(perf["btc"][2], 0)}</p>', unsafe_allow_html=True)
    r4.markdown(f'<p class="ribbon-label">30D Range (BTC)</p><p class="ribbon-val">H: {f(perf["btc"][0], 0)} | L: {f(perf["btc"][1], 0)}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- AI FORECAST & SIDEBAR ---
    st.sidebar.header("🕹️ Controls")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    
    # Auto-Bias Logic
    sma20 = sol_df['close'].rolling(20).mean().iloc[-1]
    rsi = 50 # Default
    delta = sol_df['close'].diff()
    if len(delta) > 14:
        g = (delta.where(delta > 0, 0)).rolling(14).mean(); l_ = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g / l_).iloc[-1]))
    
    tech_bias = "Bullish" if price > sma20 and rsi > 55 else ("Bearish" if price < sma20 and rsi < 45 else "Neutral")
    bias_choice = st.sidebar.selectbox("🎯 Directional Basis", ["AI Automatic", "Neutral", "Bullish", "Bearish"])
    final_bias = tech_bias if bias_choice == "AI Automatic" else bias_choice
    c_col = bias_color[final_bias]

    # AI Forecast Range
    bias_shift = (current_atr * 0.7) if final_bias == "Bullish" else (-(current_atr * 0.7) if final_bias == "Bearish" else 0)
    auto_l, auto_h = price - (current_atr * 2.5) + bias_shift, price + (current_atr * 2.5) + bias_shift
    liq_p = price * (1 - (1/lev)*0.45) 

    # --- AI CARD RESTORED ---
    st.markdown(f"""
    <div class="ai-card" style="--b-col: {c_col};">
        <div style="background: rgba(0,0,0,0.5); padding: 3px 12px; border-radius: 5px; display: inline-block; font-size: 11px; color: {c_col}; border: 1px solid {c_col};">BIAS: {final_bias.upper()}</div>
        <h2 style="margin: 15px 0 5px 0; color: {c_col};">🤖 AI Range Forecast</h2>
        <div class="glow-gold" style="--b-col: {c_col}; color: {c_col};">{f(auto_l, 2)} — {f(auto_h, 2)}</div>
        <div class="liq-box">
            <div class="liq-label">Liquidation Floor</div>
            <div class="liq-val">{f(liq_p, 2)}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # --- MANUAL & TABLES ---
    st.subheader("✍️ Manual Range Control")
    if 'v_range' not in st.session_state: st.session_state.v_range = (float(auto_l), float(auto_h))
    m_range = st.slider("Adjust Manual Zone", float(price*0.3), float(price*1.7), value=st.session_state.v_range)
    m_l, m_h = m_range

    def get_proj(low, high):
        w = max(high - low, 0.01)
        h_fee = (cap * lev * 0.00007) * ((price * 0.35) / w)
        return {"1 Hour": f(h_fee, 2), "3 Hours": f(h_fee*3, 2), "1 Day": f(h_fee*24, 2), "1 Week": f(h_fee*168, 2), "1 Month": f(h_fee*720, 2)}
    
    st.subheader("📊 Yield Comparison Matrix")
    ca, cm = st.columns(2)
    with ca:
        st.markdown(f"<p style='color:{c_col}; font-weight:bold;'>🤖 AI Strategy Yield</p>", unsafe_allow_html=True)
        st.table(pd.DataFrame(get_proj(auto_l, auto_h).items(), columns=["Timeframe", "Est. Profit"]))
    with cm:
        st.markdown("<p style='color:#888; font-weight:bold;'>✍️ Manual Strategy Yield</p>", unsafe_allow_html=True)
        st.table(pd.DataFrame(get_proj(m_l, m_h).items(), columns=["Timeframe", "Est. Profit"]))

    # AUTO-SAVE TO LEDGER
    with open("strategy_ledger.txt", "a") as f_out:
        f_out.write(json.dumps({"time": str(datetime.now()), "manual_low": m_l, "manual_high": m_h, "bias": final_bias}) + "\n")
    st.sidebar.success("✅ Strategy Logged")
