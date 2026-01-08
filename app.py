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
    .ai-card {{ border: 2px solid {accent}; padding: 25px; border-radius: 15px; background: {"#050505" if theme=="Dark Mode" else "#f9f9f9"}; margin-bottom: 25px; }}
    .manual-card {{ border: 2px solid #555; padding: 25px; border-radius: 15px; background: {"#0a0a0a" if theme=="Dark Mode" else "#f0f0f0"}; margin-bottom: 25px; }}
    .liq-box {{ background: #440000; border: 1px solid #ff4b4b; padding: 15px; border-radius: 8px; text-align: center; color: white; }}
    .tag {{ background: #222; color: {accent}; padding: 3px 10px; border-radius: 12px; font-size: 11px; border: 1px solid {accent}; margin-right: 8px; }}
    .news-ticker {{ background: rgba(212, 175, 55, 0.1); border: 1px dashed {accent}; padding: 10px; border-radius: 8px; margin-top: 15px; font-size: 13px; }}
    .news-link {{ color: {accent} !important; text-decoration: none; font-weight: bold; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 15px; }}
    .styled-table td {{ border: 1px solid #444; padding: 12px; text-align: center; }}
    .gauge-container {{ width: 100%; background-color: #333; border-radius: 10px; margin: 20px 0; height: 15px; position: relative; border: 1px solid #555; }}
    .price-marker {{ position: absolute; top: -8px; height: 30px; width: 4px; background-color: #FFF; box-shadow: 0 0 10px #FFF; z-index: 10; }}
</style>""", unsafe_allow_html=True)

# 2. DATA & INTELLIGENCE ENGINES
df, btc_p, _, status = fetch_base_data('1d')

def calculate_atr(df):
    h_l = df['high'] - df['low']
    h_c = np.abs(df['high'] - df['close'].shift())
    l_c = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([h_l, h_c, l_c], axis=1).max(axis=1)
    return tr.rolling(14).mean().iloc[-1]

def get_live_intelligence():
    try:
        url = "https://min-api.cryptocompare.com/data/v2/news/?categories=SOL&excludeCategories=Sponsored"
        data = requests.get(url).json()['Data'][:3]
        titles = " ".join([n['title'].lower() for n in data])
        sentiment = "Bullish" if any(x in titles for x in ['surge', 'buy', 'pump', 'growth', 'up']) else "Neutral"
        return sentiment, data
    except: return "Neutral", []

if status:
    price = df['close'].iloc[-1]
    current_atr = calculate_atr(df)
    news_bias, news_list = get_live_intelligence()
    
    # V-Pulse & BTC Correlation (Rule 23)
    v_pulse = "COILING" if current_atr < (df['high'].tail(5).mean() * 0.04) else "EXPANDING"
    btc_corr = "SUPPORTIVE" if btc_p > (btc_p * 0.985) else "DRAGGING"

    # 3. SIDEBAR RISK (Rule 6 - Liquidation Soul)
    st.sidebar.header("Command Controls")
    cap = st.sidebar.number_input("Total Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    liq_p = price * (1 - (1 / lev) * 0.45)

    # 4. UNIVERSAL PRICE BANNER
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BTC", f"${btc_p:,.2f}")
    c2.metric("S SOL", f"${price:,.2f}")
    c3.metric("DAILY ATR", f"{current_atr:.2f}")
    st.divider()

    # 5. SECTION A: AI COMMAND CENTER + NEWS TICKER
    if price > df['20_ema'].iloc[-1] and news_bias == "Bullish":
        ai_bias, ai_mult = "Strong Bullish 🚀", 2.2
    elif v_pulse == "COILING" or btc_corr == "DRAGGING":
        ai_bias, ai_mult = "Precautionary Bearish 📉", 3.2
    else:
        ai_bias, ai_mult = "Neutral ⚖️", 2.7

    auto_l = price - (current_atr * ai_mult)
    auto_h = price + (current_atr * ai_mult)
    
    st.markdown(f"""
    <div class="ai-card">
        <div style="margin-bottom: 15px;">
            <span class="tag">NEWS: {news_bias.upper()}</span>
            <span class="tag">V-PULSE: {v_pulse}</span>
            <span class="tag">BTC: {btc_corr}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <div>
                <h2 style="margin:0; color:{accent};">🤖 AI Autonomous Forecast: {ai_bias}</h2>
                <div style="margin: 15px 0;">
                    <span style="font-size: 14px; opacity:0.6;">SUGGESTED RANGE ({ai_mult}x ATR):</span><br>
                    <span class="glow-gold">${auto_l:,.2f} — ${auto_h:,.2f}</span>
                </div>
            </div>
            <div class="liq-box">
                <span style="font-size: 11px;">LIQUIDATION SOUL</span><br>
                <span style="font-size: 20px; font-family: monospace;">${liq_p:,.2f}</span>
            </div>
        </div>
        <div class="news-ticker">
            <b style="color:{accent};">⚡ LIVE SOLANA NEWS:</b><br>
            {"".join([f'<div style="margin-top:5px;">• {n["title"]} <a class="news-link" href="{n["url"]}" target="_blank">[Read More]</a></div>' for n in news_list]) if news_list else "Scanning headlines..."}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 6. SECTION B: ISOLATED MANUAL ENGINE (Sovereign Controls)
    st.markdown('<div class="manual-card">', unsafe_allow_html=True)
    st.subheader("✍️ Manual Range Control & Profitability Engine")
    
    if 'man_low' not in st.session_state: st.session_state.man_low = float(auto_l)
    if 'man_high' not in st.session_state: st.session_state.man_high = float(auto_h)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        m_l = st.slider("Set Manual Low Boundary", float(price*0.4), float(price), st.session_state.man_low, step=0.01)
        st.session_state.man_low = m_l
    with col_m2:
        m_h = st.slider("Set Manual High Boundary", float(price), float(price*1.6), st.session_state.man_high, step=0.01)
        st.session_state.man_high = m_h

    manual_w = max(m_h - m_l, 0.01)

    # VISUAL GAUGE (Rule 28)
    price_pct = ((price - m_l) / manual_w) * 100
    price_pct = max(0, min(100, price_pct))
    
    st.markdown(f"**Current Position:** {price_pct:.1f}% within manual range")
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

    # 7. THE DUAL-MATRIX PROFIT CALCULATOR (Rule 17)
    def get_matrix(width):
        daily = (cap * lev * 0.0017) * ((price * 0.35) / width)
        return {"1 Hour": daily/24, "1 Day": daily, "1 Week": daily*7, "1 Month": daily*30}

    st.subheader("📊 Profitability Comparison")
    t1, t2 = st.columns(2)
    
    with t1:
        st.markdown(f"#### 🤖 AI Suggested ({ai_mult}x)")
        res_a = get_matrix(auto_h - auto_l)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_a.items()])
        st.markdown(f'<table class="styled-table">{rows_a}</table>', unsafe_allow_html=True)

    with t2:
        st.markdown("#### ✍️ Manual Custom Range")
        res_m = get_matrix(manual_w)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_m.items()])
        st.markdown(f'<table class="styled-table" style="border: 1px solid {accent};">{rows_m}</table>', unsafe_allow_html=True)

    # 8. AUDITOR & NAVIGATION
    st.sidebar.divider()
    if m_l <= liq_p:
        st.sidebar.error("🚨 RISK: NON-COMPLIANT")
        st.error(f"🚨 ALERT: Manual Low (${m_l:,.2f}) is below Liquidation Floor (${liq_p:,.2f})!")
    else:
        st.sidebar.success("✅ STRATEGY COMPLIANT")
    
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
