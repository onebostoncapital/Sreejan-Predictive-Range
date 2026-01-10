import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
from datetime import datetime
import json

# MAGIC COMMAND:
# streamlit run app.py

st.set_page_config(page_title="Sreejan AI Sentinel Pro", layout="wide")

# 1. UI STYLING & CORE UTILS
theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt = ("#000000", "#FFFFFF") if theme == "Dark Mode" else ("#FFFFFF", "#000000")
bias_color = {"Neutral": "#D4AF37", "Bullish": "#00FF7F", "Bearish": "#FF4B4B", "PANIC": "#7B00FF"}

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .ribbon {{ background: rgba(255, 255, 255, 0.03); border-radius: 10px; padding: 15px; margin-bottom: 20px; border: 1px solid #333; }}
    .ai-card {{ border: 2px solid var(--b-col); padding: 25px; border-radius: 15px; background: #050505; position: relative; margin-bottom: 20px; box-shadow: 0 0 20px var(--b-col); }}
    .sentinel-box {{ background: rgba(123, 0, 255, 0.1); border: 1px dashed #7B00FF; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 12px; }}
    .liq-box {{ position: absolute; right: 25px; top: 50%; transform: translateY(-50%); border: 1px solid #FF4B4B; padding: 15px; border-radius: 8px; background: rgba(75, 0, 0, 0.3); text-align: center; }}
</style>""", unsafe_allow_html=True)

# 2. HYBRID DATA ENGINE (CORE + FAILSAFE)
try:
    sol_df, sol_p, btc_df, status = fetch_base_data('1d')
except:
    sol_df, btc_df, status = None, None, False

if not status or sol_df is None:
    btc_p, price, current_atr = 90729.0, 135.84, 8.45
    sol_stats = {"high": 142.50, "low": 129.10, "avg": 134.20, "t_high": 138.95, "t_low": 134.02}
    btc_stats = {"high": 95000.0, "low": 88000.0, "avg": 91340.0}
else:
    price = sol_df['close'].iloc[-1]
    current_atr = (sol_df['high']-sol_df['low']).rolling(14).mean().iloc[-1]
    s30 = sol_df.tail(30)
    sol_stats = {"high": s30['high'].max(), "low": s30['low'].min(), "avg": s30['close'].mean(), "t_high": sol_df['high'].iloc[-1], "t_low": sol_df['low'].iloc[-1]}
    b30 = btc_df.tail(30)
    btc_p = btc_df['close'].iloc[-1]
    btc_stats = {"high": b30['high'].max(), "low": b30['low'].min(), "avg": b30['close'].mean()}

def f(v, d=2): return f"${v:,.{d}f}"

# --- MODULE 1 & 2: HEADER & RIBBON (LOCKED) ---
st.title("🏹 Sreejan AI Sentinel Pro")
c1, c2, c3 = st.columns(3)
c1.metric("₿ BTC Price", f(btc_p, 0))
c2.metric("S SOL Price", f(price, 2))
c3.metric("Volatility (ATR)", f(current_atr, 2))

st.markdown('<div class="ribbon">', unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
r1.markdown(f"**30D High/Low:** {f(sol_stats['high'])} / {f(sol_stats['low'])}")
r2.markdown(f"**Today's Range:** {f(sol_stats['t_high'])} / {f(sol_stats['t_low'])}")
r3.markdown(f"**30D Averages:** SOL {f(sol_stats['avg'])} / BTC {f(btc_stats['avg'], 0)}")
r4.markdown(f"**Safety Status:** {'✅ NOMINAL' if status else '⚠️ SAFE-MODE'}")
st.markdown('</div>', unsafe_allow_html=True)

# --- NEW MODULE 8: SENTINEL ENGINE (NEWS & NEURAL) ---
st.sidebar.header("🛡️ Sentinel Controls")
news_sentiment = st.sidebar.select_slider("News Sentiment", options=["Panic", "Bearish", "Neutral", "Bullish", "Euphoria"], value="Neutral")
neural_trend = "Bullish" if price > sol_stats['avg'] else "Bearish" # Placeholder for LSTM logic

# --- MODULE 3: AI INTELLIGENCE ENGINE (STRENGTHENED) ---
bias_choice = st.sidebar.selectbox("🎯 Directional Basis", ["Sentinel Auto-Mode", "Neutral", "Bullish", "Bearish"])

if bias_choice == "Sentinel Auto-Mode":
    # Logic: Combine Technical + Neural + News
    if news_sentiment == "Panic": 
        final_bias = "Neutral" # Force Neutral in Panic for safety
        sentinel_msg = "🚨 SENTINEL: Black Swan Alert! Forcing Neutral Range."
    elif news_sentiment == "Bullish" and neural_trend == "Bullish":
        final_bias = "Bullish"
        sentinel_msg = "⚡ SENTINEL: High Confluence Bullish Trend."
    else:
        final_bias = "Neutral"
        sentinel_msg = "⚖️ SENTINEL: Mixed signals. Playing safe."
else:
    final_bias = bias_choice
    sentinel_msg = "👤 MANUAL OVERRIDE: Sentinel Standby."

c_col = bias_color.get(final_bias, "#D4AF37")

# --- MODULE 4: AI FORECAST CARD ---
# Stretch range if News is volatile
vol_mult = 3.0 if news_sentiment in ["Panic", "Euphoria"] else 2.2
auto_l = price - (current_atr * vol_mult)
auto_h = price + (current_atr * vol_mult)
liq_p = auto_l * 0.85

st.markdown(f"""
<div class="ai-card" style="--b-col: {c_col};">
    <div style="color: {c_col}; font-weight: bold; border: 1px solid {c_col}; display: inline-block; padding: 2px 8px; border-radius: 4px;">{final_bias.upper()}</div>
    <h2 style="margin-top: 10px; color: {txt};">🤖 AI Sentinel Range</h2>
    <div style="font-size: 38px; font-weight: bold; font-family: monospace; color: {c_col};">{f(auto_l)} — {f(auto_h)}</div>
    <div class="sentinel-box">{sentinel_msg}</div>
    <div class="liq-box">
        <div style="color: #FF4B4B; font-size: 10px; font-weight: bold;">LIQUIDATION FLOOR</div>
        <div style="font-size: 20px; font-weight: bold; color: white;">{f(liq_p)}</div>
    </div>
</div>""", unsafe_allow_html=True)

# --- MODULE 5: MANUAL CONTROL ---
st.subheader("✍️ Manual Control Module")
m_l, m_h = st.slider("Fine-tune Liquidity Zones", float(price*0.5), float(price*1.5), value=(float(auto_l), float(auto_h)))

# --- MODULE 6: YIELD MATRIX ---
def get_proj(l, h):
    w = max(h - l, 0.1)
    fee = (10000 * 1.5 * 0.0001) * ((price * 0.4) / w)
    return {"1h": f(fee), "1d": f(fee*24), "1w": f(fee*168), "1m": f(fee*720)}

st.subheader("📊 Yield Matrix Module")
k1, k2 = st.columns(2)
with k1:
    st.write("🤖 AI Projection")
    st.table(pd.DataFrame(get_proj(auto_l, auto_h).items(), columns=["Time", "Profit"]))
with k2:
    st.write("✍️ Manual Projection")
    st.table(pd.DataFrame(get_proj(m_l, m_h).items(), columns=["Time", "Profit"]))

# --- MODULE 7: STRATEGY LEDGER (AUTO-SAVE) ---
try:
    with open("strategy_ledger.txt", "a") as f_out:
        log = {"t": str(datetime.now()), "p": price, "bias": final_bias, "news": news_sentiment}
        f_out.write(json.dumps(log) + "\n")
except: pass
