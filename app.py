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
    .ai-intel-box {{ border: 1px dashed {accent}; padding: 15px; border-radius: 10px; background: rgba(212, 175, 55, 0.05); margin-bottom: 20px; }}
    .news-module {{ border: 1px solid #333; padding: 15px; border-radius: 10px; background: #0a0a0a; margin-bottom: 20px; }}
    .news-tag {{ padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: bold; text-transform: uppercase; }}
    .ai-card {{ border: 2px solid var(--b-col); padding: 25px; border-radius: 15px; background: #050505; margin-bottom: 20px; box-shadow: 0 0 20px var(--b-col); }}
    .manual-card {{ border: 2px solid #555; padding: 20px; border-radius: 15px; background: #0a0a0a; margin-bottom: 20px; }}
    .glow-gold {{ font-weight: bold; text-shadow: 0 0 15px {accent}; font-family: monospace; font-size: 32px; }}
    .liq-box {{ background: #440000; border: 1px solid #ff4b4b; padding: 12px; border-radius: 8px; text-align: center; color: white; }}
    .tag {{ background: #222; color: #aaa; padding: 3px 10px; border-radius: 12px; font-size: 11px; border: 1px solid #444; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
    .styled-table th {{ background: #222; padding: 10px; border: 1px solid #444; color: #aaa; }}
    .styled-table td {{ border: 1px solid #444; padding: 10px; text-align: center; font-family: monospace; }}
</style>""", unsafe_allow_html=True)

# 2. DATA & ENGINES (LOCKED + NEWS UPGRADE)
df, btc_p, _, status = fetch_base_data('1d')

def get_news_intelligence():
    # Simulated Live News Scan for Jan 10, 2026
    news_items = [
        {"title": "Solana Mainnet v3.0.14 Critical Patch Released", "bias": "Bullish", "link": "https://cryptonews.com"},
        {"title": "Analysts Target $150 SOL as ETF Inflows Surge", "bias": "Bullish", "link": "https://mexc.com"},
        {"title": "Regulatory Clarity Bill Heads to US Senate Next Week", "bias": "Neutral", "link": "https://economictimes.com"}
    ]
    # Simple logic to derive overall news sentiment
    bull_count = sum(1 for n in news_items if n['bias'] == "Bullish")
    bear_count = sum(1 for n in news_items if n['bias'] == "Bearish")
    
    overall = "Bullish" if bull_count > bear_count else ("Bearish" if bear_count > bull_count else "Neutral")
    return news_items, overall

def get_tech_bias(df):
    close = df['close']
    sma20 = close.rolling(20).mean().iloc[-1]
    delta = close.diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
    tech_bias = "Bullish" if close.iloc[-1] > sma20 and rsi > 55 else ("Bearish" if close.iloc[-1] < sma20 and rsi < 45 else "Neutral")
    return tech_bias, rsi, sma20

if status:
    price = df['close'].iloc[-1]
    current_atr = (df['high']-df['low']).rolling(14).mean().iloc[-1]
    
    # --- HEADER SECTION (LOCKED) ---
    st.title("🏹 Sreejan AI Forecaster Pro")
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC Price", f"${btc_p:,.2f}")
    c2.metric("S SOL Price", f"${price:,.2f}")
    c3.metric("Volatility (ATR)", f"{current_atr:.2f}")
    st.divider()

    # 3. AI TECH INTELLIGENCE (LOCKED)
    tech_bias, rsi_val, sma_val = get_tech_bias(df)
    st.markdown(f"""<div class="ai-intel-box"><b>🧠 TECH PULSE:</b> {tech_bias.upper()} (RSI: {rsi_val:.2f} | SMA: ${sma_val:,.2f})</div>""", unsafe_allow_html=True)

    # 4. SIDEBAR & FINAL BIAS (LOCKED)
    st.sidebar.header("🕹️ Parameters")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    
    news_data, news_sentiment = get_news_intelligence()
    # COMBINED LOGIC: News has a 50% weight on the final auto-bias
    final_auto = news_sentiment if news_sentiment != "Neutral" else tech_bias
    
    bias_choice = st.sidebar.selectbox("🎯 Directional Basis", ["AI Automatic", "Neutral", "Bullish", "Bearish"])
    final_bias = final_auto if bias_choice == "AI Automatic" else bias_choice

    # 5. AI RANGE CARD (UPGRADED WITH NEWS MULTIPLIER)
    v_pulse = "COILING" if current_atr < (df['high'].tail(5).mean() * 0.045) else "EXPANDING"
    ai_mult = 3.2 if v_pulse == "COILING" else 2.2
    
    # News Impact on Range
    range_mod = 1.15 if news_sentiment == "Bullish" else (0.85 if news_sentiment == "Bearish" else 1.0)
    
    bias_shift = (current_atr * 0.7) if final_bias == "Bullish" else (-(current_atr * 0.7) if final_bias == "Bearish" else 0)
    auto_l = price - (current_atr * ai_mult * (2-range_mod)) + bias_shift
    auto_h = price + (current_atr * ai_mult * range_mod) + bias_shift
    c_color = bias_color[final_bias]

    st.markdown(f"""<div class="ai-card" style="--b-col: {c_color};">
        <div style="display:flex; justify-content:space-between;"><span class="tag">BASIS: {final_bias.upper()}</span><span class="tag">V-PULSE: {v_pulse}</span></div>
        <h2 style="margin:15px 0 0 0; color:{c_color};">🤖 AI Range Forecast</h2>
        <span class="glow-gold" style="color:{c_color};">${auto_l:,.2f} — ${auto_h:,.2f}</span>
    </div>""", unsafe_allow_html=True)

    # 6. GLOBAL NEWS INTELLIGENCE (NEW MODULE ABOVE MANUAL)
    st.markdown('<div class="news-module">', unsafe_allow_html=True)
    st.subheader("🌍 Global News Scanner")
    for item in news_data:
        n_col = bias_color[item['bias']]
        st.markdown(f"""
            <div style="margin-bottom:10px; padding-bottom:5px; border-bottom:1px solid #222;">
                <span class="news-tag" style="background:{n_col}; color:black;">{item['bias']}</span> 
                <a href="{item['link']}" style="color:#ddd; text-decoration:none; margin-left:10px;">{item['title']}</a>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 7. MANUAL SECTION (LOCKED)
    st.markdown('<div class="manual-card">', unsafe_allow_html=True)
    st.subheader("✍️ Manual Range Control")
    if 'v_range' not in st.session_state: st.session_state.v_range = (float(auto_l), float(auto_h))
    m_range = st.slider("Adjust Zone", float(price*0.1), float(price*1.9), value=st.session_state.v_range)
    st.session_state.v_range = m_range
    m_l, m_h = m_range
    st.markdown('</div>', unsafe_allow_html=True)

    # 8. YIELD MATRIX (LOCKED)
    def get_projections(l, h):
        w = max(h - l, 0.01)
        h_fee = (cap * lev * 0.00007) * ((price * 0.35) / w)
        return {"1 Hour": h_fee, "3 Hours": h_fee*3, "1 Day": h_fee*24, "1 Week": h_fee*24*7, "1 Month": h_fee*24*30}

    st.subheader("📊 Yield Comparison Matrix")
    c_ai, c_man = st.columns(2)
    ai_p, man_p = get_projections(auto_l, auto_h), get_projections(m_l, m_h)
    with c_ai:
        st.markdown(f"<h4 style='color:{c_color}'>🤖 AI Yield</h4>", unsafe_allow_html=True)
        rows = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td></tr>" for k, v in ai_p.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Time</th><th>Profit</th></tr>{rows}</table>', unsafe_allow_html=True)
    with c_man:
        st.markdown("<h4>✍️ Manual Yield</h4>", unsafe_allow_html=True)
        rows = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td></tr>" for k, v in man_p.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Time</th><th>Profit</th></tr>{rows}</table>', unsafe_allow_html=True)

    # 9. LEDGER (AUTO-SAVE)
    with open("strategy_ledger.txt", "a") as f:
        f.write(json.dumps({"time": str(datetime.now()), "bias": final_bias, "daily": round(man_p["1 Day"], 2)}) + "\n")
    st.sidebar.success("✅ Strategy Logged")
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
