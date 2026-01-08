import streamlit as st
import pandas as pd
from data_engine import fetch_base_data
import requests

# 1. SETUP & CORE IDENTITY (Rule 5 & 14)
st.set_page_config(page_title="Sreejan AI Forecaster", layout="wide")

theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")

st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-gold {{ 
        color: {accent}; font-weight: bold; 
        text-shadow: 0 0 12px rgba(212,175,55,0.9); font-family: 'Courier New', monospace; font-size: 28px;
    }}
    .predictive-box {{ border: 2px solid {accent}; padding: 20px; border-radius: 10px; background: {"#050505" if theme=="Dark Mode" else "#f9f9f9"}; }}
    .ai-card {{ background: {"#111" if theme=="Dark Mode" else "#eee"}; padding: 20px; border-radius: 10px; border-left: 6px solid {accent}; margin-bottom: 25px; }}
    .news-tag {{ background: #D4AF37; color: black; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 10px; }}
    .styled-table th, .styled-table td {{ border: 1px solid #444; padding: 12px; text-align: center; }}
    .styled-table th {{ background-color: {"#181818" if theme=="Dark Mode" else "#ddd"}; color: {accent}; }}
</style>""", unsafe_allow_html=True)

# 2. DATA & NEWS ENGINE (Rule 13 & 23)
df, btc_p, daily_atr, status = fetch_base_data('1d')

def get_market_news():
    try:
        # Fetching latest crypto sentiment headlines
        resp = requests.get("https://min-api.cryptocompare.com/data/v2/news/?categories=SOL,BTC&excludeCategories=Sponsored").json()
        return resp['Data'][:3]
    except: return []

if status:
    price = df['close'].iloc[-1]
    ema20, sma200 = df['20_ema'].iloc[-1], df['200_sma'].iloc[-1]
    news = get_market_news()

    # UNIVERSAL PRICE BANNER (Rule 13)
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BITCOIN", f"${btc_p:,.2f}")
    c2.metric("S SOLANA", f"${price:,.2f}")
    c3.metric("DAILY ATR", f"{daily_atr:.2f}")
    st.divider()

    # 3. AI AUTONOMOUS SENTIMENT (Rule 23)
    # Analysis based on Price Location + News Presence
    news_titles = " ".join([n['title'].lower() for n in news])
    bullish_news = any(word in news_titles for word in ['surge', 'buy', 'growth', 'bull', 'adoption'])
    
    if price > sma200 and (price > ema20 or bullish_news):
        ai_bias, ai_emoji, ai_mult = "Bullish", "🚀", 2.2
        ai_msg = "Momentum is Strong. AI suggests TIGHT Range for maximum Yield."
    elif price < sma200 and not bullish_news:
        ai_bias, ai_emoji, ai_mult = "Bearish", "📉", 3.2
        ai_msg = "Trend is Weak. AI suggests WIDE Range for safety."
    else:
        ai_bias, ai_emoji, ai_mult = "Neutral", "⚖️", 2.7
        ai_msg = "Consolidation detected. AI suggests BALANCED Volatility buffer."

    # 4. GLOWING AUTO-FORECASTER (Rule 3 & Visual Soul)
    auto_l = price - (daily_atr * ai_mult)
    auto_h = price + (daily_atr * ai_mult)
    auto_w = max(auto_h - auto_l, 0.01)

    st.markdown(f"""
    <div class="ai-card">
        <h2 style="margin:0; color:{accent};">📡 AI Market Intelligence: {ai_bias} {ai_emoji}</h2>
        <p style="margin: 10px 0; font-style: italic; opacity: 0.9;">{ai_msg}</p>
        <div style="margin: 15px 0;">
            <span style="font-size: 14px; letter-spacing: 1px;">AUTONOMOUS FORECASTED RANGE ({ai_mult}x ATR):</span><br>
            <span class="glow-gold">${auto_l:,.2f} — ${auto_h:,.2f}</span>
        </div>
        <div style="font-size: 12px; opacity: 0.7;">
            <b>Recent Market Drivers:</b><br>
            {"<br>".join([f"• {n['title'][:80]}..." for n in news]) if news else "Scanning for news updates..."}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. SIDEBAR PARAMETERS (Rule 6)
    st.sidebar.header("Risk Settings")
    cap = st.sidebar.number_input("Capital ($)", value=10000.0)
    lev = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    liq_p = price * (1 - (1 / lev) * 0.45)

    # 6. INTERACTIVE RANGE ADJUSTMENT (Rule 17)
    st.markdown('<div class="predictive-box">', unsafe_allow_html=True)
    st.subheader("✍️ Manual Custom Range Adjustment")
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        m_l, m_h = st.slider("Fine-Tune Manual Zone", float(price*0.1), float(price*1.9), (float(auto_l), float(auto_h)), step=0.1)
        manual_w = max(m_h - m_l, 0.01)
    with col_r2:
        st.metric("LIQUIDATION FLOOR", f"${liq_p:,.2f}")
    if m_l <= liq_p:
        st.error(f"⚠️ COLLISION ALERT: Manual Low is below Liquidation!")
    st.markdown('</div>', unsafe_allow_html=True)

    # 7. DUAL DYNAMIC MATRICES (Rule 17, 21, 22)
    def get_matrix(width_to_use):
        base_d = (cap * lev * 0.0017) * ((price * 0.35) / width_to_use)
        return {
            "1 Hour": base_d / 24, "3 Hour": (base_d / 24) * 3, "6 Hour": (base_d / 24) * 6,
            "12 Hour": (base_d / 24) * 12, "1 Day": base_d, "1 Week": base_d * 7, "1 Month": base_d * 30
        }

    st.subheader("📊 Profitability Matrix Comparison")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"#### 🤖 AI Auto-Range ({ai_mult}x)")
        res_a = get_matrix(auto_w)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_a.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_a}</table>', unsafe_allow_html=True)
    with t2:
        st.markdown("#### ✍️ Manual Custom Range")
        # THIS IS DYNAMIC: Reacts to 'manual_w' from the slider
        res_m = get_matrix(manual_w)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/cap)*100:.2f}%</td></tr>" for k, v in res_m.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Horizon</th><th>Profit</th><th>ROI</th></tr>{rows_m}</table>', unsafe_allow_html=True)

    # 8. AUDITOR & NAVIGATION
    st.sidebar.divider()
    st.sidebar.subheader("🛡️ Compliance Auditor")
    if m_l > liq_p: st.sidebar.success("✅ STRATEGY COMPLIANT")
    else: st.sidebar.error("❌ NON-COMPLIANT")
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
