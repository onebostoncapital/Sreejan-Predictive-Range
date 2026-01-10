import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
from datetime import datetime
import json

# MAGIC COMMAND:
# streamlit run app.py

# 1. UI ENGINE (LOCKED & RESTORED)
st.set_page_config(page_title="Sreejan AI Multi-Logic Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt = ("#000000", "#FFFFFF") if theme == "Dark Mode" else ("#FFFFFF", "#000000")
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

# 2. HYBRID DATA ENGINE (CORE + 3-PILLAR)
try:
    sol_df, sol_p, _, sol_status = fetch_base_data('1d')
    _, btc_p, btc_df, btc_status = fetch_base_data('1d')
except:
    sol_df, btc_df = None, None
    sol_status, btc_status = False, False

# --- DATA FAIL-SAFE (JAN 10, 2026) ---
if btc_df is None or btc_df.empty:
    btc_p = 90729.0
    btc_stats = {"high": 95000.0, "low": 88000.0, "avg": 91340.0}
else:
    b30 = btc_df.tail(30)
    btc_stats = {"high": b30['high'].max(), "low": b30['low'].min(), "avg": b30['close'].mean()}

if sol_df is None or sol_df.empty:
    price = 135.84
    current_atr = 8.45
    sol_stats = {"high": 142.50, "low": 129.10, "avg": 134.20, "t_high": 138.95, "t_low": 134.02}
else:
    price = sol_df['close'].iloc[-1]
    current_atr = (sol_df['high']-sol_df['low']).rolling(14).mean().iloc[-1]
    s30 = sol_df.tail(30)
    sol_stats = {"high": s30['high'].max(), "low": s30['low'].min(), "avg": s30['close'].mean(), "t_high": sol_df['high'].iloc[-1], "t_low": sol_df['low'].iloc[-1]}

def f(v, d=2): return f"${v:,.{d}f}"

# --- MODULE 1 & 2: HEADER & RIBBON ---
st.title("🏹 Sreejan AI Predictive Engine")
c1, c2, c3 = st.columns(3)
c1.metric("₿ BTC Price", f(btc_p, 0))
c2.metric("S SOL Price", f(price, 2))
c3.metric("Volatility (ATR)", f(current_atr, 2))

st.markdown('<div class="ribbon">', unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
r1.markdown(f'<p class="ribbon-label">30D High/Low (SOL)</p><p class="ribbon-val">H: {f(sol_stats["high"])} | L: {f(sol_stats["low"])}</p>', unsafe_allow_html=True)
r2.markdown(f'<p class="ribbon-label">Today\'s Range (SOL)</p><p class="ribbon-val">H: {f(sol_stats["t_high"])} | L: {f(sol_stats["t_low"])}</p>', unsafe_allow_html=True)
r3.markdown(f'<p class="ribbon-label">30D Avg Price</p><p class="ribbon-val">SOL: {f(sol_stats["avg"])} | BTC: {f(btc_stats["avg"], 0)}</p>', unsafe_allow_html=True)
r4.markdown(f'<p class="ribbon-label">BTC 30D Range</p><p class="ribbon-val">H: {f(btc_stats["high"], 0)} | L: {f(btc_stats["low"], 0)}</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- MODULE 3: STRENGTHENED AI ENGINE ---
st.sidebar.header("🕹️ Parameters")
cap = st.sidebar.number_input("Capital ($)", value=10000.0)
lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
bias_choice = st.sidebar.selectbox("🎯 Directional Basis", ["Integrated AI Auto", "Neutral", "Bullish", "Bearish"])

if bias_choice == "Integrated AI Auto":
    # OLD LOGIC: Price vs 30D Avg
    base_is_bullish = price > sol_stats["avg"]
    # NEW LOGIC (Strengthening): Is it near extreme walls or exhausted?
    is_exhausted_up = price > (sol_stats["high"] - (current_atr * 0.5))
    is_exhausted_down = price < (sol_stats["low"] + (current_atr * 0.5))
    
    if base_is_bullish and not is_exhausted_up: final_bias = "Bullish"
    elif not base_is_bullish and not is_exhausted_down: final_bias = "Bearish"
    else: final_bias = "Neutral" # Combined result
else:
    final_bias = bias_choice

c_col = bias_color[final_bias]

# --- MODULE 4: AI FORECAST CARD (Pillar 3 Expected Move) ---
move_mult = 2.2 
shift = (current_atr * 0.7) if final_bias == "Bullish" else (-(current_atr * 0.7) if final_bias == "Bearish" else 0)
auto_l, auto_h = price - (current_atr * move_mult) + shift, price + (current_atr * move_mult) + shift
liq_p = auto_l * 0.84

st.markdown(f"""
<div class="ai-card" style="--b-col: {c_col};">
    <div style="background: rgba(0,0,0,0.5); padding: 3px 12px; border-radius: 5px; display: inline-block; font-size: 11px; color: {c_col}; border: 1px solid {c_col};">INTEGRATED LOGIC: {final_bias.upper()}</div>
    <h2 style="margin: 15px 0 5px 0; color: {c_col};">🤖 AI Statistical Forecast</h2>
    <div class="glow-gold" style="--b-col: {c_col}; color: {c_col};">{f(auto_l, 2)} — {f(auto_h, 2)}</div>
    <div class="liq-box">
        <div class="liq-label">Liquidation Floor</div>
        <div class="liq-val">{f(liq_p, 2)}</div>
    </div>
</div>""", unsafe_allow_html=True)

# --- MODULE 5: MANUAL CONTROL ---
st.subheader("✍️ Manual Adjust (Confluence)")
m_l, m_h = st.slider("Manual Setting", float(price*0.5), float(price*1.5), value=(float(auto_l), float(auto_h)))

# --- MODULE 6: YIELD MATRIX ---
def get_proj(low, high):
    w = max(high - low, 0.01)
    h_fee = (cap * lev * 0.0001) * ((price * 0.38) / w) 
    return {"1 Hour": f(h_fee, 2), "1 Day": f(h_fee*24, 2), "1 Week": f(h_fee*168, 2), "1 Month": f(h_fee*720, 2)}

st.subheader("📊 Yield Comparison Matrix")
ca, cm = st.columns(2)
with ca:
    st.markdown(f"<p style='color:{c_col}; font-weight:bold;'>🤖 Integrated AI Yield</p>", unsafe_allow_html=True)
    st.table(pd.DataFrame(get_proj(auto_l, auto_h).items(), columns=["Timeframe", "Est. Profit"]))
with cm:
    st.markdown("<p style='color:#888; font-weight:bold;'>✍️ Manual Logic Yield</p>", unsafe_allow_html=True)
    st.table(pd.DataFrame(get_proj(m_l, m_h).items(), columns=["Timeframe", "Est. Profit"]))

# --- MODULE 7: STRATEGY LEDGER (AUTO-SAVE) ---
try:
    with open("strategy_ledger.txt", "a") as f_out:
        f_out.write(json.dumps({"time": str(datetime.now()), "m_l": m_l, "m_h": m_h, "bias": final_bias}) + "\n")
except: pass
