import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# ── Backend imports ──────────────────────────────────────────────────────────
from data_loader      import load_stock_data, get_ticker_info
from pattern_detector import get_latest_patterns, PATTERNS
from pattern_analysis import analyse_all_patterns, build_ai_explanation

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & PERSISTENCE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []

WATCHLIST = ["AAPL", "TSLA", "NVDA", "BTC-USD", "ETH-USD", "AMD", "MSFT"]

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. UNIFIED GLOBAL CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: #020617 !important;
    color: #f8fafc;
}
[data-testid="stSidebar"] { border-right: 1px solid #1e293b; }
.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #2563eb, #10b981) !important;
    color: white !important;
    font-weight: 800 !important;
    border-radius: 8px !important;
    border: none !important;
    text-transform: uppercase;
}
.portfolio-card { background: rgba(30, 41, 59, 0.3); border: 1px dashed #334155; border-radius: 10px; padding: 15px; margin-bottom: 20px; }
.mono { font-family: 'JetBrains Mono', monospace; }
.label { font-size: 0.65rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
.bullish-badge { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
.bearish-badge { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
.ledger-row { border-bottom: 1px solid #1e293b; padding: 8px 0; font-size: 0.75rem; display: flex; justify-content: space-between; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding-bottom:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    
    # Portfolio Calc
    cur_px = st.session_state.last_df['Close'].iloc[-1] if 'last_df' in st.session_state else 0
    total_val = sum([c * cur_px for t, c in st.session_state.portfolio.items()])
    
    st.markdown(f"""<div class="portfolio-card">
        <div class="label">Total Wealth</div>
        <div class="mono" style="font-size:1.3rem; font-weight:800;">${(st.session_state.cash_balance + total_val):,.2f}</div>
        <div class="label" style="margin-top:8px;">Cash: ${st.session_state.cash_balance:,.2f}</div>
    </div>""", unsafe_allow_html=True)
    
    ticker = st.text_input("TICKER", value="NVDA").upper().strip()
    risk_pct = st.slider("Risk %", 0.5, 5.0, 1.0, 0.5)
    
    sc1, sc2 = st.columns(2)
    with sc1: analyze_btn = st.button("ANALYZE")
    with sc2: scan_btn = st.button("SCAN")

# ════════════════════════════════════════════════════════════════════════════
# 5. SCANNER / ANALYSIS LOGIC
# ════════════════════════════════════════════════════════════════════════════
if scan_btn:
    st.markdown("### 📡 Market Scan")
    for t in WATCHLIST:
        scan_df = load_stock_data(t, "1y")
        pts = get_latest_patterns(scan_df)
        if pts:
            sig = PATTERNS[pts[0]]['signal']
            st.markdown(f"<div class='ledger-row'><b>{t}</b> <span class='badge {sig}-badge'>{pts[0]}</span></div>", unsafe_allow_html=True)

if analyze_btn or 'last_df' in st.session_state:
    if analyze_btn:
        df = load_stock_data(ticker, "1y")
        st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, get_ticker_info(ticker), ticker

    df, info, active_t = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
    px = float(df["Close"].iloc[-1])
    patterns = get_latest_patterns(df)
    held = st.session_state.portfolio.get(active_t, 0)

    # Risk Engine
    sl = float(df["Low"].iloc[-1]) * 0.995
    qty = int((st.session_state.cash_balance * (risk_pct/100)) / (px - sl)) if (px - sl) > 0 else 0

    st.markdown(f"## {active_t} <span style='color:#64748b; font-size:1rem;'>{info.get('name','')}</span>", unsafe_allow_html=True)

    # Actions
    a1, a2, a3 = st.columns([1.5, 1, 1])
    with a1:
        st.markdown(f"<div style='background:rgba(59,130,246,0.1); padding:12px; border-radius:10px;'><div class='label'>Suggested Size</div><div class='mono'>{qty} Units | SL: ${sl:.2f}</div></div>", unsafe_allow_html=True)
    with a2:
        if st.button(f"BUY {qty}"):
            if st.session_state.cash_balance >= (px * qty):
                st.session_state.cash_balance -= (px * qty)
                st.session_state.portfolio[active_t] = held + qty
                st.session_state.trade_history.append({"time": datetime.now().strftime("%H:%M:%S"), "t": active_t, "type": "BUY", "px": px})
                st.rerun()
    with a3:
        if st.button("EXIT"):
            if held > 0:
                st.session_state.cash_balance += (px * held)
                st.session_state.portfolio[active_t] = 0
                st.session_state.trade_history.append({"time": datetime.now().strftime("%H:%M:%S"), "t": active_t, "type": "SELL", "px": px})
                st.rerun()

    # Chart & Ledger
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure(data=[go.Candlestick(x=df.tail(60).index, open=df.tail(60)['Open'], high=df.tail(60)['High'], low=df.tail(60)['Low'], close=df.tail(60)['Close'])])
        fig.add_hline(y=sl, line_dash="dash", line_color="#ef4444")
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2: # FIXED: Removed the walrus operator SyntaxError
        st.markdown("<div class='label'>Session Ledger</div>", unsafe_allow_html=True)
        for trade in reversed(st.session_state.trade_history[-5:]):
            clr = "#10b981" if trade['type'] == "BUY" else "#ef4444"
            st.markdown(f"<div class='ledger-row'><span class='mono' style='color:#64748b;'>{trade['time']}</span> <b>{trade['t']}</b> <span style='color:{clr}'>{trade['type']}</span> <span class='mono'>${trade['px']:.0f}</span></div>", unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:2rem; color:#1e293b; font-size:0.6rem;'>TERMINAL v8.5 • HACKATHON STABLE</div>", unsafe_allow_html=True)
