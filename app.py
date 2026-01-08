import streamlit as st
import pandas as pd
from data_engine import fetch_base_data

st.set_page_config(page_title="AI Predictive Range Model", layout="wide")

# 1. STYLE & THEME (Rule 5 & 14)
theme = st.sidebar.radio("Theme Mode", ["Dark Mode", "Light Mode"])
bg, txt, accent = ("#000000", "#FFFFFF", "#D4AF37") if theme == "Dark Mode" else ("#FFFFFF", "#000000", "#D4AF37")

st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; color: {txt} !important; }} 
    .glow-gold {{ 
        color: {accent}; font-weight: bold; 
        text-shadow: 0 0 10px rgba(212,175,55,0.8); font-family: monospace; font-size: 26px;
    }}
    .predictive-box {{ border: 2px solid {accent}; padding: 20px; border-radius: 10px; background: {"#050505" if theme=="Dark Mode" else "#f9f9f9"}; }}
    .sentiment-card {{ background: {"#111" if theme=="Dark Mode" else "#eee"}; padding: 15px; border-radius: 8px; border-left: 5px solid {accent}; margin-bottom: 20px; }}
    .styled-table {{ width:100%; border-collapse: collapse; margin-top: 10px; }}
    .styled-table th, .styled-table td {{ border: 1px solid #444; padding: 10px; text-align: center; }}
</style>""", unsafe_allow_html=True)

# 2. DATA ENGINE (Rule 13)
df, btc_p, daily_atr, status = fetch_base_data('1d')

if status:
    price = df['close'].iloc[-1]
    ema20 = df['20_ema'].iloc[-1]
    sma200 = df['200_sma'].iloc[-1]
    
    # 3. AI SENTIMENT ANALYZER (Rule 23)
    # Logic: Analyzes Market Situation (Price vs Trend + Volatility)
    if price > sma200 and price > ema20:
        ai_bias, ai_emoji, ai_mult = "Bullish", "🚀", 2.2
        ai_desc = "Market shows strong upward momentum. Tightening range for maximum yield."
    elif price < sma200 and price < ema20:
        ai_bias, ai_emoji, ai_mult = "Bearish", "📉", 3.2
        ai_desc = "Trend is breaking down. Expanding range for downside protection."
    else:
        ai_bias, ai_emoji, ai_mult = "Neutral", "⚖️", 2.7
        ai_desc = "Market is consolidating. Using standard volatility buffer."

    # UNIVERSAL PRICE BANNER
    c1, c2, c3 = st.columns(3)
    c1.metric("₿ BITCOIN", f"${btc_p:,.2f}")
    c2.metric("S SOLANA", f"${price:,.2f}")
    c3.metric("ATR (14d)", f"{daily_atr:.2f}")
    st.divider()

    # 4. AUTO-FORECASTER DISPLAY (The Soul with Gold Glow)
    auto_l = price - (daily_atr * ai_mult)
    auto_h = price + (daily_atr * ai_mult)
    auto_w = max(auto_h - auto_l, 0.01)

    st.markdown(f"""
    <div class="sentiment-card">
        <h3 style="margin:0; color:{accent};">📡 AI Sentiment Engine: {ai_bias} {ai_emoji}</h3>
        <p style="margin: 5px 0;">{ai_desc}</p>
        <div style="margin-top: 10px;">
            <span style="font-size: 14px; opacity: 0.8;">FORECASTED RANGE ({ai_mult}x ATR):</span><br>
            <span class="glow-gold">${auto_l:,.2f} — ${auto_h:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. SIDEBAR SETTINGS (Rule 6)
    st.sidebar.header("Capital & Leverage")
    capital = st.sidebar.number_input("Capital ($)", value=10000.0)
    leverage = st.sidebar.slider("Leverage", 1.0, 5.0, 1.5)
    liq_p = price * (1 - (1 / leverage) * 0.45)

    # 6. INTERACTIVE MANUAL BOX (Rule 17)
    st.markdown('<div class="predictive-box">', unsafe_allow_html=True)
    st.subheader("✍️ Manual Custom Range Adjustment")
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        m_l, m_h = st.slider("Fine-Tune Manual Zone", 
                             float(price*0.1), float(price*1.9), 
                             (float(auto_l), float(auto_h)), step=0.1)
        manual_w = max(m_h - m_l, 0.01)
    with col_r2:
        st.metric("LIQUIDATION FLOOR", f"${liq_p:,.2f}")
    
    if m_l <= liq_p:
        st.error(f"⚠️ COLLISION: Manual Low is below Liquidation Price!")
    st.markdown('</div>', unsafe_allow_html=True)

    # 7. DUAL DYNAMIC TABLES (Rule 17 & 22)
    def get_matrix(width_to_use):
        base_daily = (capital * leverage * 0.0017) * ((price * 0.35) / width_to_use)
        return {
            "1 Hour": base_daily / 24, "1 Day": base_daily, 
            "1 Week": base_daily * 7, "1 Month": base_daily * 30
        }

    st.subheader("📊 Profitability Matrix")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown(f"#### 🤖 AI Auto-Range ({ai_mult}x)")
        auto_res = get_matrix(auto_w)
        rows_a = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/capital)*100:.2f}%</td></tr>" for k, v in auto_res.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Time</th><th>Profit</th><th>ROI</th></tr>{rows_a}</table>', unsafe_allow_html=True)

    with t_col2:
        st.markdown("#### ✍️ Manual Custom Range")
        manual_res = get_matrix(manual_w)
        rows_m = "".join([f"<tr><td>{k}</td><td>${v:,.2f}</td><td>{(v/capital)*100:.2f}%</td></tr>" for k, v in manual_res.items()])
        st.markdown(f'<table class="styled-table"><tr><th>Time</th><th>Profit</th><th>ROI</th></tr>{rows_m}</table>', unsafe_allow_html=True)

    # 8. STRATEGY AUDITOR
    st.sidebar.divider()
    st.sidebar.subheader("🛡️ Auditor")
    if m_l > liq_p: st.sidebar.success("✅ COMPLIANT")
    else: st.sidebar.error("❌ NON-COMPLIANT")
    st.sidebar.link_button("🔙 Main Hub", "https://defi-tuna-apper-bohsifbb9dawewnwd56uo5.streamlit.app/")
