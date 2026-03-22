import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ── Backend imports ──────────────────────────────────────────────────────────
# Mock functions for demonstration if modules aren't present
try:
    from data_loader      import load_stock_data, get_ticker_info
    from pattern_detector import get_latest_patterns, PATTERNS
    from pattern_analysis import analyse_all_patterns, build_ai_explanation
except ImportError:
    # Fallback for local testing
    def load_stock_data(t, p): 
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
        return pd.DataFrame(np.random.randn(100, 4), index=dates, columns=['Open', 'High', 'Low', 'Close'])
    def get_ticker_info(t): return {"sector": "TECHNOLOGY", "name": "Apple Inc."}
    def analyse_all_patterns(df): return {"Bullish": {"win_rate": 65, "avg_return": 1.2}}
    def get_latest_patterns(df): return ["BULLISH_ENGULFING"]

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_scan = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_ghp9v062.json")

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY (Replacing Emojis)
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Info": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    "Loading": '<svg width="50" height="50" viewBox="0 0 50 50"><circle cx="25" cy="25" r="20" fill="none" stroke="#3b82f6" stroke-width="5" stroke-dasharray="31.4 31.4" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 25 25" to="360 25 25" dur="1s" repeatCount="indefinite"/></circle></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. CSS STYLING
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
[data-testid="stAppViewContainer"] {{ background: radial-gradient(circle at top right, #0f172a, #020617); font-family: 'Plus Jakarta Sans', sans-serif; }}
.quant-card {{ background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 1.5rem; transition: all 0.3s ease; margin-bottom: 1rem; }}
.quant-card:hover {{ transform: translateY(-5px); border-color: rgba(59, 130, 246, 0.5); }}
.live-dot {{ height: 8px; width: 8px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 0 0 rgba(16, 185, 129, 1); animation: pulse-green 2s infinite; }}
@keyframes pulse-green {{ 0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }} 70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }} 100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }} }}
.label {{ font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.75rem; font-weight: 800; margin-top: 0.25rem; color: #f8fafc; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR & DATA LOADING
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    ticker = st.text_input("INSTRUMENT", value="AAPL").upper().strip()
    period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    st.markdown("---")
    analyse_btn = st.button("RUN ENGINE SCAN")

if not analyse_btn and 'last_df' not in st.session_state:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st_lottie(lottie_scan, height=300, key="initial")
        st.markdown("<p style='text-align:center; color:#64748b;' class='mono'>SYSTEM READY. AWAITING INPUT...</p>", unsafe_allow_html=True)
    st.stop()

if analyse_btn:
    with st.status("Decoding Market Fractals...", expanded=True) as status:
        st.write("Fetching historical data...")
        df = load_stock_data(ticker, period)
        st.write("Analyzing patterns...")
        info = get_ticker_info(ticker)
        time.sleep(0.5)
        st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, info, ticker
        status.update(label="Scan Complete", state="complete", expanded=False)

# Data References
df = st.session_state.last_df
info = st.session_state.last_info
active_ticker = st.session_state.last_ticker
latest_close = float(df["Close"].iloc[-1])

# ════════════════════════════════════════════════════════════════════════════
# 5. HEADER & KPI CALCULATION
# ════════════════════════════════════════════════════════════════════════════
stats_all = analyse_all_patterns(df)
latest_patterns = get_latest_patterns(df)
daily_chg = (latest_close - float(df["Close"].iloc[-2])) / float(df["Close"].iloc[-2]) * 100
primary = latest_patterns[0] if latest_patterns else "NEUTRAL"

# Calculate Total Equity (Cash + All Positions)
current_market_value = sum([count * latest_close for t, count in st.session_state.portfolio.items() if t == active_ticker])
# Note: In a real app, you'd fetch prices for all tickers in portfolio.
total_equity = st.session_state.cash_balance + current_market_value

st.markdown(f"<div><div class='label'><span class='live-dot'></span> {info['sector']} • LIVE FEED</div>"
            f"<div style='font-size:2.8rem; font-weight:800;'>{info['name']} <span style='color:#3b82f6' class='mono'>{active_ticker}</span></div></div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="quant-card"><div class="label">Last Traded</div><div class="value mono">${latest_close:,.2f}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="quant-card"><div class="label">Session Change</div><div class="value mono" style="color:{"#10b981" if daily_chg >=0 else "#ef4444"}">{daily_chg:+.2f}%</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="quant-card"><div class="label">Pattern Signal</div><div class="value" style="font-size:1.2rem; color:#3b82f6;">{primary}</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="quant-card"><div class="label">Total Equity</div><div class="value mono">${total_equity:,.2f}</div></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 6. CHART & TRADE MODULE
# ════════════════════════════════════════════════════════════════════════════
fig = go.Figure(data=[go.Candlestick(x=df.tail(100).index, open=df.tail(100)['Open'], high=df.tail(100)['High'], low=df.tail(100)['Low'], close=df.tail(100)['Close'], increasing_line_color='#10b981', decreasing_line_color='#ef4444')])
fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

st.markdown("<div class='label'>Order Execution Engine</div>", unsafe_allow_html=True)
t_col1, t_col2 = st.columns([2, 1])

with t_col1:
    st.markdown('<div class="quant-card">', unsafe_allow_html=True)
    q_col1, q_col2, q_col3 = st.columns(3)
    qty = q_col1.number_input("QUANTITY", min_value=1, value=10)
    q_col2.markdown(f'<div class="label">Est. Cost</div><div class="value mono" style="font-size:1.4rem;">${qty * latest_close:,.2f}</div>', unsafe_allow_html=True)
    q_col3.markdown(f'<div class="label">Buying Power</div><div class="value mono" style="font-size:1.4rem;">${st.session_state.cash_balance:,.2f}</div>', unsafe_allow_html=True)
    
    b1, b2 = st.columns(2)
    if b1.button("EXECUTE BUY ORDER", use_container_width=True):
        cost = qty * latest_close
        if st.session_state.cash_balance >= cost:
            st.session_state.cash_balance -= cost
            st.session_state.portfolio[active_ticker] = st.session_state.portfolio.get(active_ticker, 0) + qty
            st.rerun()
        else:
            st.error("Insufficient Funds")
            
    if b2.button("EXECUTE SELL ORDER", use_container_width=True):
        if st.session_state.portfolio.get(active_ticker, 0) >= qty:
            st.session_state.cash_balance += (qty * latest_close)
            st.session_state.portfolio[active_ticker] -= qty
            st.rerun()
        else:
            st.error("Insufficient Position")
    st.markdown('</div>', unsafe_allow_html=True)

with t_col2:
    st.markdown('<div class="quant-card" style="height:100%;">', unsafe_allow_html=True)
    st.markdown(f'<div class="label">{SVG_ICONS["Wallet"]} Net Position</div>', unsafe_allow_html=True)
    shares = st.session_state.portfolio.get(active_ticker, 0)
    st.markdown(f'<div class="value mono">{shares} <span style="font-size:0.8rem; color:#64748b;">Shares</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="label" style="margin-top:15px;">Position Value</div><div class="value mono" style="font-size:1.4rem; color:#10b981;">${shares * latest_close:,.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 7. FOOTER METRICS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='margin-top:2rem;' class='label'>Historical Performance</div>", unsafe_allow_html=True)
perf_cols = st.columns(len(stats_all))
for i, (name, stats) in enumerate(stats_all.items()):
    perf_cols[i].markdown(f"""
        <div class="quant-card">
            <div class="label" style="color:#3b82f6">{name}</div>
            <div style="font-size:1.4rem; font-weight:700;">{stats['win_rate']}% <span class="label">Wins</span></div>
        </div>
    """, unsafe_allow_html=True)
