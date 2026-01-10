import streamlit as st
import pandas as pd
import numpy as np
from data_engine import fetch_base_data
from datetime import datetime
import json

# MAGIC COMMAND:
# streamlit run app.py

st.set_page_config(page_title="Sreejan AI Sentinel Pro", layout="wide")

# 1. UI STYLING
theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt = ("#000000", "#FFFFFF") if theme == "Dark Mode" else ("#FFFFFF", "#000000")
bias_color = {"Neutral": "#D4AF37", "Bullish": "#00FF7F", "Bearish": "#FF4B4B"}

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .ribbon {{ background: rgba(255, 255, 255, 0.03); border-radius: 10px; padding: 15px; margin-bottom: 20px; border: 1px solid #333; }}
    .ai-card {{ border: 2px solid var(--b-col); padding: 25px; border-radius: 15px; background: #050505; position: relative; margin-bottom: 20px; box-shadow: 0 0 20px var(--b-col); }}
    .sentinel-box {{ background: rgba(123, 0, 255, 0.1); border: 1px dashed #7B00FF; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 13px; color: #E0B0FF; }}
    .liq-box {{ position: absolute; right: 25px; top: 50%; transform: translateY(-50%); border: 1px solid #FF4B4B; padding: 15px; border-radius: 8px; background: rgba(75, 0, 0, 0.3); text-align: center; }}
</style>""", unsafe_allow_html=True)

# 2. DATA ENGINE
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
    s30, b30 = sol_df.tail(30), btc_df.tail(30)
    sol_stats = {"high": s30['high'].max(), "low": s30['low'].min(), "avg": s30['close'].mean(), "t_high": sol_df['high'].iloc[-1], "t_low": sol_df['low'].iloc[-1]}
    btc_p, btc_stats = btc_df['close'].iloc[-1], {"high": b30['high'].max(), "low": b30['low'].min(), "avg": b30['close'].mean()}

def f(v, d=2): return f"${v:,.{d}f}"

# --- MODULE 1 & 2: HEADER & RIBBON ---
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

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🕹️ Parameters")
user_capital = st.sidebar.number_input("Trading Capital ($)", value=10000.0)
manual_lev = st.sidebar.slider("Manual Leverage", 1.0, 10.0, 3.0)
news_sent = st.sidebar.select_slider("News Sentiment", options=["Panic", "Bearish", "Neutral", "Bullish", "Euphoria"], value="Neutral")
bias_choice = st.sidebar.selectbox("🎯 Directional Basis", ["Sentinel Auto", "Neutral", "Bullish", "Bearish"])

# AI Intelligence Logic
neural_trend = "Bullish" if price > sol_stats['avg'] else "Bearish"
if bias_choice == "Sentinel Auto":
    if news_sent == "Panic": final_bias, sentinel_msg = "Neutral", "🚨 PANIC: Sentinel forcing safe Neutral range."
    elif news_sent == "Bullish" and neural_trend == "Bullish": final_bias, sentinel_msg = "Bullish", "⚡ CONFLUENCE: High-confidence Bullish trend."
    else: final_bias, sentinel_msg = "Neutral", "⚖️ BALANCED: AI optimizing for steady yield."
else:
    final_bias, sentinel_msg = bias_choice, "👤 MANUAL: Sentinel standing by."

# --- MODULE 4: AI FORECAST CARD (LOCKED 2X) ---
ai_lev = 2.0  # HARD LOCKED
vol_mult = 3.5 if news_sent in ["Panic", "Euphoria"] else 2.5
auto_l, auto_h = price - (current_atr * vol_mult), price + (current_atr * vol_mult)
ai_liq = price / ai_lev if final_bias == "Bullish" else price * (1 - (1/ai_lev))

st.markdown(f"""
<div class="ai-card" style="--b-col: {bias_color.get(final_bias, '#D4AF37')};">
    <div style="color: {bias_color.get(final_bias, '#D4AF37')}; font-weight: bold; border: 1px solid {bias_color.get(final_bias, '#D4AF37')}; display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{final_bias.upper()} BIAS</div>
    <h2 style="margin-top: 10px; color: {txt};">🤖 Sentinel AI Range</h2>
    <div style="font-size: 38px; font-weight: bold; font-family: monospace; color: {bias_color.get(final_bias, '#D4AF37')};">{f(auto_l)} — {f(auto_h)}</div>
    <div class="sentinel-box">{sentinel_msg}</div>
    <div class="liq-box">
        <div style="color: #FF4B4B; font-size: 10px; font-weight: bold;">AI LIQ FLOOR</div>
        <div style="font-size: 20px; font-weight: bold; color: white;">{f(ai_liq)}</div>
        <div style="color: #888; font-size: 9px;">LOCKED AT 2.0x</div>
    </div>
</div>""", unsafe_allow_html=True)

# --- MODULE 5: MANUAL CONTROL ---
st.subheader("✍️ Manual Control Module")
m_range = st.slider("Fine-tune Liquidity Zones", float(price*0.3), float(price*1.7), value=(float(auto_l), float(auto_h)))
m_l, m_h = m_range

# --- MODULE 6: YIELD MATRIX (FIXED AI vs DYNAMIC MANUAL) ---
def calc_yield(l, h, leverage):
    width = max(h - l, 0.01)
    base_fee = (user_capital * leverage * 0.0001) * ((price * 0.45) / width)
    return {"1h": f(base_fee), "3h": f(base_fee*3), "1d": f(base_fee*24), "1w": f(base_fee*168), "1m": f(base_fee*720)}

st.subheader("📊 Yield Matrix Module")
k1, k2 = st.columns(2)
with k1:
    st.markdown(f"**🤖 AI Projection (Locked 2.0x)**")
    st.table(pd.DataFrame(calc_yield(auto_l, auto_h, 2.0).items(), columns=["Time", "Profit"]))
with k2:
    st.markdown(f"**✍️ Manual Projection (Dynamic {manual_lev}x)**")
    st.table(pd.DataFrame(calc_yield(m_l, m_h, manual_lev).items(), columns=["Time", "Profit"]))

# --- MODULE 7: STRATEGY LEDGER ---
try:
    with open("strategy_ledger.txt", "a") as f_out:
        log = {"time": str(datetime.now().strftime("%H:%M:%S")), "price": price, "ai_lev": 2.0, "man_lev": manual_lev, "bias": final_bias}
        f_out.write(json.dumps(log) + "\n")
except: pass
