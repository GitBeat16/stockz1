import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
import pytz  
from streamlit_lottie import st_lottie
from datetime import datetime

# ── Backend imports ──────────────────────────────────────────────────────────
try:
    from data_loader      import load_stock_data, get_ticker_info
    from pattern_detector import get_latest_patterns, PATTERNS
    from pattern_analysis import analyse_all_patterns, build_ai_explanation
except ImportError:
    st.error("Backend modules missing. Please ensure data_loader, pattern_detector, and pattern_analysis are in the root.")

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "DASHBOARD"

# Helper for IST Time
def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime("%H:%M:%S")

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_scan = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_ghp9v062.json")
lottie_ai = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_ntp99aba.json")

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Info": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" cy="16" x2="12" y2="12"/><line x1="12" cy="8" x2="12.01" y2="8"/></svg>',
    "Settings": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "History": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "News": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2"><path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10l4 4v10a2 2 0 0 1-2 2z"/><path d="M7 8h5"/><path d="M7 12h10"/><path d="M7 16h10"/></svg>',
    "Brain": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.73-2.73 2.5 2.5 0 0 1-.31-4.71 2.5 2.5 0 0 1 .41-4.5 2.5 2.5 0 0 1 5.09-1.5z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.73-2.73 2.5 2.5 0 0 0 .31-4.71 2.5 2.5 0 0 0-.41-4.5 2.5 2.5 0 0 0-5.09-1.5z"/></svg>',
    "Compare": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M16 3h5v5"/><path d="M4 20L21 3"/><path d="M21 16v5h-5"/><path d="M15 15l6 6"/><path d="M4 4l5 5"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. ADVANCED ANIMATED CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

[data-testid="stAppViewContainer"] {{
    background: radial-gradient(circle at top right, #0f172a, #020617);
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

.quant-card {{
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    animation: fadeIn 0.8s ease-out;
    margin-bottom: 1rem;
}}

.ai-bubble {{
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 12px;
    padding: 12px;
    margin-top: 10px;
    font-size: 0.85rem;
    color: #e2e8f0;
    line-height: 1.4;
}}

.news-item {{
    padding: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    transition: background 0.2s;
}}

.news-item:hover {{ background: rgba(255,255,255,0.02); }}

.live-dot {{
    height: 8px; width: 8px; background-color: #10b981; border-radius: 50%;
    display: inline-block; margin-right: 8px;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 1);
    animation: pulse-green 2s infinite;
}}

@keyframes pulse-green {{
    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
    70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }}
    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
}}

@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}

.label {{ font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.75rem; font-weight: 800; margin-top: 0.25rem; color: #f8fafc; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}

.stButton > button {{
    border-radius: 12px !important;
    background: transparent !important;
    color: #64748b !important;
    font-weight: 700 !important;
    border: 1px solid transparent !important;
    transition: 0.4s !important;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
}}

.stButton > button:hover {{
    color: #3b82f6 !important;
    background: rgba(59, 130, 246, 0.1) !important;
}}

.trade-btn > div > button {{
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    font-size: 0.9rem;
}}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR & NAVIGATION
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:1.2rem; margin-bottom:20px;'>StockZ Terminal</h2>", unsafe_allow_html=True)
    
    ticker = st.text_input("INSTRUMENT", value="AAPL").upper().strip()
    period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    
    st.markdown("---")
    
    # ── AI ASSISTANT SIDEBAR COMPONENT ────────────────────────────────────────
    st.markdown(f'<div class="label">{SVG_ICONS["Brain"]} COMMAND CENTER</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="ai-bubble">', unsafe_allow_html=True)
        if 'last_ticker' in st.session_state:
            curr = st.session_state.last_ticker
            bal = st.session_state.cash_balance
            st.write(f"Analyzing **{curr}**. You have **${bal:,.0f}** liquid. I suggest looking for pattern confirmations before executing high-risk trades.")
        else:
            st.write("Awaiting engine scan to provide tactical deployment advice.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown(f'<div class="label">{SVG_ICONS["Wallet"]} PAPER BALANCE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="value mono" style="font-size:1.5rem; color:#10b981;">${st.session_state.cash_balance:,.2f}</div>', unsafe_allow_html=True)
    
    if st.session_state.portfolio:
        st.markdown('<div class="label" style="margin-top:15px; border-top: 1px solid #1e293b; padding-top:10px;">ACTIVE POSITIONS</div>', unsafe_allow_html=True)
        for sym, q in st.session_state.portfolio.items():
            if q > 0:
                st.markdown(f'<div class="mono" style="font-size:0.85rem; color:#3b82f6;">{sym}: {q} Shares</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    analyse = st.button("RUN ENGINE SCAN", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# 5. HEADER NAVIGATION BAR
# ════════════════════════════════════════════════════════════════════════════
nav_bg = "rgba(15, 23, 42, 0.8)"
st.markdown(f"""
<div style="background: {nav_bg}; padding: 10px 20px; border-bottom: 1px solid rgba(59, 130, 246, 0.2); margin-bottom: 25px; border-radius: 12px; backdrop-filter: blur(10px);">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; gap: 10px; align-items: center;">
            <span style="margin-right:15px;">{SVG_ICONS["Logo"]}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 15px;">
            <div class="live-dot"></div>
            <span class="label" style="color: #10b981;">CORE_STABLE (IST)</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([1, 1, 1, 5])
with c1:
    if st.button("DASHBOARD", use_container_width=True):
        st.session_state.current_page = "DASHBOARD"
        st.rerun()
with c2:
    if st.button("PORTFOLIO", use_container_width=True):
        st.session_state.current_page = "PORTFOLIO"
        st.rerun()
with c3:
    if st.button("SETTINGS", use_container_width=True):
        st.session_state.current_page = "SETTINGS"
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 6. ROUTER & PAGE RENDERING
# ════════════════════════════════════════════════════════════════════════════

if st.session_state.current_page == "DASHBOARD":
    if not analyse and 'last_df' not in st.session_state:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if lottie_scan: st_lottie(lottie_scan, height=300, key="initial")
            st.markdown("<p style='text-align:center; color:#64748b;' class='mono'>SYSTEM READY. AWAITING INPUT...</p>", unsafe_allow_html=True)
        st.stop()

    if analyse:
        with st.spinner("Decoding Market Fractals..."):
            time.sleep(0.8)
            df = load_stock_data(ticker, period)
            info = get_ticker_info(ticker)
            st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, info, ticker

    df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
    stats_all = analyse_all_patterns(df)
    latest_patterns = get_latest_patterns(df)
    latest_close = float(df["Close"].iloc[-1])
    primary = latest_patterns[0] if latest_patterns else None

    st.markdown(f"""
        <div style='margin-bottom:2rem;'>
            <div class='label'><span class='live-dot'></span> {info['sector']} • LIVE FEED</div>
            <div style='font-size:2.8rem; font-weight:800; letter-spacing:-0.02em;'>{info['name']} <span style='color:#3b82f6' class='mono'>{active_ticker}</span></div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="quant-card"><div class="label">Last Price</div><div class="value mono">${latest_close:,.2f}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="quant-card"><div class="label">Paper Money</div><div class="value mono" style="color:#10b981;">${st.session_state.cash_balance:,.2f}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="quant-card"><div class="label">Signal</div><div class="value" style="font-size:1.2rem; color:#3b82f6;">{primary if primary else "NEUTRAL"}</div></div>', unsafe_allow_html=True)
    with c4:
        total_val = st.session_state.cash_balance + sum([v * latest_close for v in st.session_state.portfolio.values()])
        st.markdown(f'<div class="quant-card"><div class="label">Total Equity</div><div class="value mono">${total_val:,.0f}</div></div>', unsafe_allow_html=True)

    fig = go.Figure(data=[go.Candlestick(x=df.tail(100).index, open=df.tail(100)['Open'], high=df.tail(100)['High'], low=df.tail(100)['Low'], close=df.tail(100)['Close'], 
                    increasing_line_color='#10b981', decreasing_line_color='#ef4444')])
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # ── QUANT RISK & NEWS SENTIMENT SECTION ──────────────────────────────────
    st.markdown("<div style='margin-top:2rem;' class='label'>AI Quant Suite</div>", unsafe_allow_html=True)
    r_col1, r_col2, r_col3 = st.columns([1.2, 1.4, 1.4])
    
    with r_col1:
        st.markdown('<div class="quant-card" style="height:400px; display:flex; flex-direction:column; justify-content:center;">', unsafe_allow_html=True)
        st.markdown(f'<div class="label">{SVG_ICONS["Shield"]} Exposure Gauge</div>', unsafe_allow_html=True)
        current_exposure = (sum([v * latest_close for v in st.session_state.portfolio.values()]) / total_val) * 100
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = current_exposure,
            number = {'suffix': "%", 'font': {'family': "JetBrains Mono", 'color': "#f8fafc", 'size': 20}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#3b82f6"},
                'bgcolor': "rgba(0,0,0,0)",
                'steps': [{'range': [0, 30], 'color': 'rgba(16, 185, 129, 0.2)'}, {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.2)'}]
            }
        ))
        fig_gauge.update_layout(height=180, margin=dict(l=10,r=10,t=40,b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100
        st.markdown(f'<div class="label" style="text-align:center;">Volatility: {volatility:.1f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r_col2:
        st.markdown('<div class="quant-card" style="height:400px;">', unsafe_allow_html=True)
        st.markdown(f'<div class="label">{SVG_ICONS["News"]} News Sentiment</div>', unsafe_allow_html=True)
        news_items = [
            {"title": f"{active_ticker} exceeds Q1 expectations", "sent": "BULLISH", "score": 0.8},
            {"title": "Sector regulation changes pending", "sent": "NEUTRAL", "score": 0.5},
            {"title": f"Institutional selling detected in {active_ticker}", "sent": "BEARISH", "score": 0.2}
        ]
        avg_sent = sum([i['score'] for i in news_items]) / len(news_items)
        sent_color = "#10b981" if avg_sent > 0.6 else "#ef4444" if avg_sent < 0.4 else "#f59e0b"
        st.markdown(f'<div style="font-size:1.2rem; font-weight:800; color:{sent_color}; margin:10px 0;">{ "POSITIVE" if avg_sent > 0.6 else "NEGATIVE" if avg_sent < 0.4 else "MIXED" } ({avg_sent*100:.0f}%)</div>', unsafe_allow_html=True)
        
        for item in news_items:
            s_color = "#10b981" if item['sent'] == "BULLISH" else "#ef4444" if item['sent'] == "BEARISH" else "#94a3b8"
            st.markdown(f"""
            <div class="news-item">
                <div style="font-size:0.75rem; color:#f8fafc; margin-bottom:4px;">{item['title']}</div>
                <div class="mono" style="font-size:0.6rem; color:{s_color};">{item['sent']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r_col3:
        st.markdown('<div class="quant-card" style="height:400px;">', unsafe_allow_html=True)
        st.markdown(f'<div class="label">{SVG_ICONS["Brain"]} Terminal Intelligence</div>', unsafe_allow_html=True)
        st.write("")
        # AI Logic based on volatility and balance
        risk_status = "High" if volatility > 30 else "Moderate" if volatility > 15 else "Low"
        st.markdown(f"""
        <div class="ai-bubble" style="background:transparent; border:none; padding:0;">
        <b>Risk Assessment:</b> {risk_status}<br><br>
        <b>Affordability:</b> You can purchase up to {int(st.session_state.cash_balance // latest_close)} units of {active_ticker}.<br><br>
        <b>Strategy:</b> { "Aggressive accumulation" if avg_sent > 0.6 and volatility < 25 else "Defensive positioning" if avg_sent < 0.4 else "Scaling in slowly" } is recommended for this asset profile.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── BUDGET & COMPARISON SECTION ──────────────────────────────────────────
    st.markdown("<div style='margin-top:2rem;' class='label'>Budget Suitability & Comparison</div>", unsafe_allow_html=True)
    comp_col1, comp_col2 = st.columns([1, 2])
    
    with comp_col1:
        st.markdown('<div class="quant-card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown(f'<div class="label">{SVG_ICONS["Compare"]} VS Sector Peer</div>', unsafe_allow_html=True)
        comp_ticker = st.text_input("COMPARE WITH", value="MSFT" if active_ticker != "MSFT" else "GOOGL").upper()
        if st.button("RUN COMPARATIVE ANALYSIS", use_container_width=True):
            with st.spinner("Analyzing peer..."):
                comp_df = load_stock_data(comp_ticker, period)
                comp_close = float(comp_df["Close"].iloc[-1])
                comp_stats = analyse_all_patterns(comp_df)
                max_active = int(st.session_state.cash_balance // latest_close)
                max_comp = int(st.session_state.cash_balance // comp_close)
                active_avg_win = sum([s['win_rate'] for s in stats_all.values()]) / len(stats_all) if stats_all else 0
                comp_avg_win = sum([s['win_rate'] for s in comp_stats.values()]) / len(comp_stats) if comp_stats else 0
                winner = active_ticker if active_avg_win >= comp_avg_win else comp_ticker
                st.session_state.comp_data = {"winner": winner, "max_shares": {active_ticker: max_active, comp_ticker: max_comp}, "win_rates": {active_ticker: active_avg_win, comp_ticker: comp_avg_win}}

        if 'comp_data' in st.session_state:
            res = st.session_state.comp_data
            st.markdown(f"""
                <div style="margin-top:15px; padding:10px; background:rgba(16, 185, 129, 0.1); border-radius:8px; border:1px solid #10b981;">
                    <div class="label" style="color:#10b981;">TERMINAL CHOICE</div>
                    <div class="value" style="font-size:1.2rem;">{res['winner']}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with comp_col2:
        st.markdown('<div class="quant-card" style="height:100%;">', unsafe_allow_html=True)
        if 'comp_data' in st.session_state:
            res = st.session_state.comp_data
            st.markdown('<div class="label">Affordability & Efficiency Breakdown</div>', unsafe_allow_html=True)
            k1, k2 = st.columns(2)
            with k1:
                st.markdown(f'<div class="label" style="margin-top:10px;">Max Shares ({active_ticker})</div><div class="value mono">{res["max_shares"][active_ticker]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="label" style="margin-top:10px;">Avg Win Rate</div><div class="value mono" style="color:#3b82f6;">{res["win_rates"][active_ticker]:.1f}%</div>', unsafe_allow_html=True)
            with k2:
                st.markdown(f'<div class="label" style="margin-top:10px;">Max Shares ({comp_ticker})</div><div class="value mono">{res["max_shares"][comp_ticker]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="label" style="margin-top:10px;">Avg Win Rate</div><div class="value mono" style="color:#10b981;">{res["win_rates"][comp_ticker]:.1f}%</div>', unsafe_allow_html=True)
        else:
            st.info("Compare peers to see budget efficiency.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ORDER EXECUTION ENGINE ───────────────────────────────────────────────
    st.markdown("<div style='margin-top:2rem;' class='label'>Order Execution Engine</div>", unsafe_allow_html=True)
    trade_col1, trade_col2 = st.columns([2, 1])
    with trade_col1:
        st.markdown('<div class="quant-card">', unsafe_allow_html=True)
        q_col1, q_col2, q_col3 = st.columns(3)
        with q_col1: qty = st.number_input("QUANTITY", min_value=1, value=10)
        with q_col2: st.markdown(f'<div class="label">Est. Cost</div><div class="value mono" style="font-size:1.4rem;">${qty * latest_close:,.2f}</div>', unsafe_allow_html=True)
        with q_col3: st.markdown(f'<div class="label">Buying Power</div><div class="value mono" style="font-size:1.4rem;">${st.session_state.cash_balance:,.0f}</div>', unsafe_allow_html=True)
        
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            st.markdown('<div class="trade-btn">', unsafe_allow_html=True)
            if st.button("EXECUTE BUY ORDER", use_container_width=True):
                cost = qty * latest_close
                if st.session_state.cash_balance >= cost:
                    st.session_state.cash_balance -= cost
                    st.session_state.portfolio[active_ticker] = st.session_state.portfolio.get(active_ticker, 0) + qty
                    st.session_state.trade_history.append({"time": get_ist_time(), "symbol": active_ticker, "type": "BUY", "qty": qty, "price": latest_close})
                    st.success(f"Filled: +{qty} {active_ticker}"); time.sleep(1); st.rerun()
                else: st.error("Margin Insufficient")
            st.markdown('</div>', unsafe_allow_html=True)
        with b_col2:
            st.markdown('<div class="trade-btn">', unsafe_allow_html=True)
            if st.button("EXECUTE SELL ORDER", use_container_width=True):
                if st.session_state.portfolio.get(active_ticker, 0) >= qty:
                    st.session_state.cash_balance += (qty * latest_close)
                    st.session_state.portfolio[active_ticker] -= qty
                    st.session_state.trade_history.append({"time": get_ist_time(), "symbol": active_ticker, "type": "SELL", "qty": qty, "price": latest_close})
                    st.warning(f"Filled: -{qty} {active_ticker}"); time.sleep(1); st.rerun()
                else: st.error("Position Size Mismatch")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with trade_col2:
        st.markdown('<div class="quant-card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown(f'<div class="label">{SVG_ICONS["Wallet"]} Net Position</div>', unsafe_allow_html=True)
        pos = st.session_state.portfolio.get(active_ticker, 0)
        st.markdown(f'<div class="value mono">{pos} <span style="font-size:0.8rem; color:#64748b;">Shares</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="label" style="margin-top:15px;">Market Value</div><div class="value mono" style="font-size:1.4rem; color:#10b981;">${pos * latest_close:,.2f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:3rem;' class='label'>Historical Performance Analysis</div>", unsafe_allow_html=True)
    cols = st.columns(len(stats_all))
    for i, (name, stats) in enumerate(stats_all.items()):
        with cols[i]:
            st.markdown(f'<div class="quant-card"><div class="label" style="color:#3b82f6">{name}</div><div style="font-size:1.4rem; font-weight:700; margin:0.5rem 0;">{stats["win_rate"]}% <span class="label">Win Rate</span></div><div class="label">Avg Return: {stats["avg_return"]:.2f}%</div></div>', unsafe_allow_html=True)

elif st.session_state.current_page == "PORTFOLIO":
    st.markdown("<div class='label'>Account Assets</div><h2 style='color:white;'>Active Portfolio</h2>", unsafe_allow_html=True)
    st.markdown(f'<div class="quant-card"><div class="label">Liquid Cash</div><div class="value mono" style="color:#10b981;">${st.session_state.cash_balance:,.2f}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="quant-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="label" style="margin-bottom:15px;">{SVG_ICONS["Shield"]} Open Positions</div>', unsafe_allow_html=True)
    if not st.session_state.portfolio or sum(st.session_state.portfolio.values()) == 0:
        st.info("No active positions.")
    else:
        for ticker, qty in st.session_state.portfolio.items():
            if qty > 0:
                st.markdown(f'<div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.05);"><span class="mono" style="color:#3b82f6; font-weight:700;">{ticker}</span><span class="mono" style="color:#fff;">{qty} Shares</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='label' style='margin-top:2rem;'>Activity Log</div><h2 style='color:white;'>Trade History (IST)</h2>", unsafe_allow_html=True)
    st.markdown('<div class="quant-card">', unsafe_allow_html=True)
    for trade in reversed(st.session_state.trade_history):
        color = "#10b981" if trade['type'] == "BUY" else "#ef4444"
        st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.05);"><div><span class="mono" style="color:#64748b; font-size:0.8rem; margin-right:15px;">[{trade["time"]}]</span><span class="mono" style="font-weight:700; color:{color};">{trade["type"]}</span><span class="mono" style="color:#fff; margin-left:10px;">{trade["qty"]} {trade["symbol"]}</span></div><div class="mono" style="color:#94a3b8;">@ ${trade["price"]:,.2f}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == "SETTINGS":
    st.markdown("<div class='label'>System Configuration</div><h2 style='color:white;'>Terminal Settings</h2>", unsafe_allow_html=True)
    st.markdown('<div class="quant-card">', unsafe_allow_html=True)
    st.checkbox("Enable Real-time Vector Art Rendering", value=True)
    st.checkbox("Show Advanced Quant Analytics", value=True)
    if st.button("HARD RESET TERMINAL"):
        st.session_state.cash_balance = 100000.0; st.session_state.portfolio = {}; st.session_state.trade_history = []; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with st.expander("SYSTEM PROTOCOLS", expanded=False):
    g1, g2, g3 = st.columns(3)
    with g1: st.markdown(f'{SVG_ICONS["Shield"]} **Integrity**<br><p style="font-size:0.8rem; color:#94a3b8;">Pattern window: 120D fractal match.</p>', unsafe_allow_html=True)
    with g2: st.markdown(f'{SVG_ICONS["Logo"]} **Deployment**<br><p style="font-size:0.8rem; color:#94a3b8;">Simulated session-state logic.</p>', unsafe_allow_html=True)
    with g3: st.markdown(f'{SVG_ICONS["Info"]} **Risk**<br><p style="font-size:0.8rem; color:#94a3b8;">Profile: {risk_pct}% per trade.</p>', unsafe_allow_html=True)
