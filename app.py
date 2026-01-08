import streamlit as st
import pandas as pd
import numpy as np
import requests
from data_engine import fetch_base_data

# 1. CORE IDENTITY & STYLE
st.set_page_config(page_title="Sreejan AI Forecaster Pro", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")

st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-gold {{ color: {accent}; font-weight: bold; text-shadow: 0 0 15px {accent}; font-family: monospace; font-size: 32px; }}
    .ai-card {{ border: 2px solid {accent}; padding: 20px; border-radius: 15px; background: {"#050505" if theme=="Dark Mode" else "#f9f9f9"}; margin-bottom: 20px; }}
    .manual-card {{ border: 2px solid #555; padding: 20px; border-radius: 15px; background: {"#0a0a0a" if theme=="Dark Mode" else "#f0f0f0"}; margin-bottom: 20px; }}
    .liq-box {{ background: #440000; border: 1px solid #ff4b4b; padding: 12px; border-radius: 8px; text-align: center; color: white; }}
    .tag {{ background: #222; color: {accent}; padding: 3px 10px; border-radius: 12px; font-size: 11px; border: 1px solid {accent}; margin-right: 8px; }}
    .news-ticker {{ background: rgba(212, 175, 55, 0.1); border: 1px dashed {accent}; padding: 10px; border-radius: 8px; margin-top: 10px; font-size: 13px; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 10px; }}
    .styled-table td {{ border: 1px solid #444; padding: 10px; text-align: center; font-family: monospace; }}
    .gauge-container {{ width: 100%; background-color: #333; border-radius: 10px; margin: 15px 0; height: 12px; position: relative; border: 1px solid #555; }}
    .price-marker {{ position: absolute; top: -10px; height: 32px; width: 4px; background-color: #FFF; box-shadow: 0 0 10px #FFF; z-index: 10; }}
</style>""", unsafe_allow_html=True)

# 2. DATA & ATR ENGINE
df, btc_p, _, status = fetch_base_data('1d')

def calculate_atr(df):
    h_l, h_c, l_c = df['high']-df['low'], np.abs(df['high']-df['close'].shift()), np.abs(df['low']-df['close'].shift())
    tr = pd.concat([h_l, h_c, l_c], axis=1).max(axis=1)
    return tr.rolling(14).mean().iloc[-1]

def get_live_news():
    try:
        url = "https://min-api.cryptocompare.com/data/v2/news/?categories=SOL&excludeCategories=Sponsored"
        return requests.get(url).json()['Data'][:3]
    except: return []

if status:
    price = df['close'].iloc[-1]
    current_atr = calculate_atr(df)
    news_items = get_live_news()
    
    # AI INTELLIGENCE: V-Pulse & BTC Correlation
    v_pulse = "COILING" if current_atr < (df['high'].tail(5).mean() * 0.045) else "EXPANDING"
    btc_corr = "SUPPORTIVE" if btc_p > (btc_p * 0.98) else "DRAGGING"
    ai_mult = 3.2 if (v_pulse == "COILING" or btc_corr == "DRAGGING") else 2.2
    
    # 3. GLOBAL RISK CONTROL
    st.sidebar.header("Command Center")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    liq_p = price * (1 - (1 / lev) * 0.45) # Rule 6

    # UNIVERSAL PRICE BANNER
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC", f"${btc_p:,.2f}")
    c2.metric("S SOL", f"${price:,.2f}")
    c3.metric("ATR (14d)", f"{current_atr:.2f}")
    st.divider()

    # 4. SECTION A: AI COMMAND CENTER (Suggested Only)
    auto_l, auto_h = price - (current_atr * ai_mult), price + (current_atr * ai_mult)
    
    st.markdown(f"""
    <div class="ai-card">
        <div style="margin-bottom: 10px;">
            <span class="tag">AI SENTIMENT</span> <span class="tag">V-PULSE: {v_pulse}</span> <span class="tag">BTC: {btc_corr}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <div>
                <h2 style="margin:0; color:{accent};">🤖 AI Autonomous Suggestion</h2>
                <div style="margin: 15px 0;">
                    <span style="font-size: 14px; opacity:0.6;">SUGGESTED RANGE ({ai_mult}x ATR):</span><br>
                    <span class="glow-gold">${auto_l:,.2f} — ${auto_h:,.2f}</span>
                </div>
            </div>
            <div class="liq-box">
                <span style="font-size: 11px; font-weight: bold;">LIQUIDATION SOUL</span><br>
                <span style="font-size: 20px; font-family: monospace;">${liq_p:,.2f}</span>
            </div>
        </div>
        <div class="news-ticker">
            <b style="color:{accent};">⚡ LIVE NEWS:</b><br>
            {"".join([f'<div style="margin-top:5px;">• {n["title"]} <a style="color:{accent};" href="{n["url"]}" target="_blank">[Read]</a></div>' for n in news_items]) if news_items else "Scanning..."}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. SECTION B: HARD-LOCKED MANUAL ENGINE (The Fix)
    st.markdown('<div class="manual-card">', unsafe_allow_html=True)
    st.subheader("✍️ Manual Control & Profitability Engine")

    # THE SENTINEL LOCK: This prevents the reset loop
    if 'user_m_range' not in st.session_state:
        # First time run: Initialize with AI suggested values
        st.session_state.user_m_range = (float(auto_l), float(auto_h))

    # Single-piece dual-handle slider
    # Note: We do NOT use 'value=auto_l' here, we strictly use session_state
    m_range = st.slider("Set Your Custom Profit Zone", 
                        float(price*0.1), float(price*1.9), 
                        value=st.session_state.user_m_range, 
                        step=0.01, key="manual_slider_soul")
    
    # Update state only when user moves the slider
    st.session_state.user_m_range = m_range
    m_l, m_h = m_range
    manual_w = max(m_h - m_l, 0.01)

    # VISUAL GAUGE (Rule 28)
    price_pct = ((price - m_l) / manual_w) * 100
    price_pct = max(0, min(100, price_pct))
    
    st.markdown(f"**Positioning:** {price_pct:.1f}% inside your custom zone")
    st.markdown(f"""
    <div class="gauge-container">
        <div class="price-marker" style="left: {price_pct}%;"></div>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 11px; opacity: 0.7;">
        <span>LOW: ${m_l:,.2f}</span>
        <span>HIGH: ${m_h:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. DUAL PROFIT CALCULATOR (Rule 17)
    def calculate_yield(width):
        daily = (cap * lev * 0.0017) * ((price * 0.35) / width)
        return {"1 Hour": daily/24, "1 Day": daily, "1 Week": daily*7, "1 Month": daily*30}

    st.subheader("📊 Profitability Matrix")
    t1, t2 = st.columns(2)
    
    with t1:
        st.markdown(f"#### 🤖 AI Suggested")
        res_a = calculate_yield(auto_h - auto_l)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_a.items()])
        st.markdown(f'<table class="styled-table">{rows_a}</table>', unsafe_allow_html=True)

    with t2:
        st.markdown("#### ✍️ Manual Custom")
        # THIS IS THE REACTIVE FIX: It calculates strictly on m_range output
        res_m = calculate_yield(manual_w)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_m.items()])
        st.markdown(f'<table class="styled-table" style="border: 1px solid {accent};">{rows_m}</table>', unsafe_allow_html=True)

    # 7. SAFETY AUDITOR
    st.sidebar.divider()
    if m_l <= liq_p:
        st.sidebar.error("🚨 RISK: NON-COMPLIANT")
        st.error(f"🚨 ALERT: Your Manual Low (${m_l:,.2f}) has crossed the Liquidation Soul (${liq_p:,.2f})!")
    else:
        st.sidebar.success("✅ STRATEGY COMPLIANT")
    
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
