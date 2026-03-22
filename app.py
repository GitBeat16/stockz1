import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# ── Backend imports (unchanged) ──────────────────────────────────────────────
from data_loader      import load_stock_data, get_ticker_info
from pattern_detector import get_latest_patterns, PATTERNS
from pattern_analysis import analyse_all_patterns, build_ai_explanation

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & PERSISTENT LEDGER
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = [] # List of dicts for the Ledger

WATCHLIST = ["AAPL", "TSLA", "NVDA", "BTC-USD", "ETH-USD", "AMD", "MSFT"]

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="35" height="35" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "History": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. GLOBAL CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #020617; color: #f8fafc; }
.quant-card { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(51, 65, 85, 0.5); border-radius: 12px; padding: 1.2rem; }
.ledger-row { font-size: 0.75rem; border-bottom: 1px solid rgba(51, 65, 85, 0.3); padding: 8px 0; display: flex; justify-content: space-between; }
.mono { font-family: 'JetBrains Mono', monospace; }
.label { font-size: 0.65rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.stButton > button { width: 100%; background: linear-gradient(90deg, #2563eb, #10b981) !important; color: white !important; font-weight: 800 !important; border-radius: 8px !important; transition: 0.2s; border: none !important; }
.stButton > button:hover { transform: scale(1.02); }
.badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; }
.bullish-badge { background: rgba(16, 185, 129, 0.1); color: #10b981; }
.bearish-badge { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR & PERFORMANCE SUMMARY
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; font-size:1rem; margin-bottom:20px;'>QUANT OPS CENTER</h3>", unsafe_allow_html=True)
    
    # Live Net Worth
    total_equity = sum([count * (st.session_state.last_df['Close'].iloc[-1] if 'last_df' in st.session_state else 0) for t, count in st.session_state.portfolio.items()])
    net_worth = st.session_state.cash_balance + total_equity
    
    st.markdown(f"""<div style='background:rgba(30,41,59,0.5); border-radius:10px; padding:15px; border-left:3px solid #3b82f6;'>
        <div class='label'>Net Asset Value</div>
        <div class='mono' style='font-size:1.3rem; font-weight:800;'>${net_worth:,.2f}</div>
        <div class='label' style='margin-top:10px;'>Cash: ${st.session_state.cash_balance:,.2f}</div>
    </div>""", unsafe_allow_html=True)

    ticker = st.text_input("SYMBOL", value="NVDA").upper().strip()
    risk_pct = st.slider("Risk Tolerance %", 0.5, 5.0, 1.0)
    
    col_a, col_b = st.columns(2)
    with col_a: run_analysis = st.button("ANALYZE")
    with col_b: run_scan = st.button("SCAN")

# ════════════════════════════════════════════════════════════════════════════
# 5. CORE LOGIC & TRADING ENGINE
# ════════════════════════════════════════════════════════════════════════════
if run_scan:
    st.markdown("### 🛰️ Pattern Discovery Engine")
    for t in WATCHLIST:
        scan_df = load_stock_data(t, "1y")
        patterns = get_latest_patterns(scan_df)
        if patterns:
            sig = PATTERNS[patterns[0]]['signal']
            st.markdown(f"<div style='display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid #1e293b;'><span class='mono'>{t}</span><span class='badge {sig}-badge'>{patterns[0]}</span></div>", unsafe_allow_html=True)

if run_analysis or 'last_df' in st.session_state:
    if run_analysis:
        df = load_stock_data(ticker, "1y")
        st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, get_ticker_info(ticker), ticker

    df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
    latest_close = float(df["Close"].iloc[-1])
    patterns = get_latest_patterns(df)
    shares_owned = st.session_state.portfolio.get(active_ticker, 0)

    # Risk Calculation
    sl = float(df["Low"].iloc[-1]) * 0.99
    risk_dollars = st.session_state.cash_balance * (risk_pct / 100)
    qty = int(risk_dollars / (latest_close - sl)) if (latest_close - sl) > 0 else 0

    st.markdown(f"## {active_ticker} <span style='color:#64748b; font-size:1rem;'>{info.get('name')}</span>", unsafe_allow_html=True)

    # Execution Row
    e1, e2, e3 = st.columns([1.5, 1, 1])
    with e1:
        st.markdown(f"""<div style='background:rgba(16,185,129,0.05); border:1px solid rgba(16,185,129,0.2); border-radius:10px; padding:12px;'>
            <div class='label'>Quant Suggestion</div>
            <div class='mono'>Buy <b>{qty}</b> @ ${latest_close:.2f} | SL: ${sl:.2f}</div>
        </div>""", unsafe_allow_html=True)
    with e2:
        if st.button(f"BUY {qty} SHARES"):
            cost = latest_close * qty
            if st.session_state.cash_balance >= cost:
                st.session_state.cash_balance -= cost
                st.session_state.portfolio[active_ticker] = shares_owned + qty
                st.session_state.trade_history.append({"time": datetime.now().strftime("%H:%M"), "ticker": active_ticker, "type": "BUY", "qty": qty, "price": latest_close})
                st.rerun()
    with e3:
        if st.button("CLOSE POSITION"):
            if shares_owned > 0:
                st.session_state.cash_balance += (latest_close * shares_owned)
                st.session_state.portfolio[active_ticker] = 0
                st.session_state.trade_history.append({"time": datetime.now().strftime("%H:%M"), "ticker": active_ticker, "type": "SELL", "qty": shares_owned, "price": latest_close})
                st.rerun()

    # Main Visuals
    c_left, c_right = st.columns([2, 1])
    with c_left:
        fig = go.Figure(data=[go.Candlestick(x=df.tail(60).index, open=df.tail(60)['Open'], high=df.tail(60)['High'], low=df.tail(60)['Low'], close=df.tail(60)['Close'])])
        fig.add_hline(y=sl, line_dash="dash", line_color="#ef4444")
        fig.update_layout(template="plotly_dark", height=380, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with c_right:
        st.markdown(f"<div class='label' style='display:flex; align-items:center; gap:5px;'>{SVG_ICONS['History']} Operation Ledger</div>", unsafe_allow_html=True)
        if not st.session_state.trade_history:
            st.markdown("<div style='color:#334155; font-size:0.75rem; margin-top:10px;'>No active trades in session...</div>", unsafe_allow_html=True)
        else:
            for trade in reversed(st.session_state.trade_history[-6:]): # Show last 6
                color = "#10b981" if trade['type'] == "BUY" else "#ef4444"
                st.markdown(f"""<div class='ledger-row'><span class='mono'>{trade['time']}</span><span class='mono' style='font-weight:700;'>{trade['ticker']}</span><span class='mono' style='color:{color}'>{trade['type']}</span><span class='mono'>{trade['qty']} @ ${trade['price']:.0f}</span></div>""", unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:3rem; color:#1e293b; font-size:0.6rem; letter-spacing:0.2em;'>TERMINAL CORE v7.0 • HACKATHON FINAL</div>", unsafe_allow_html=True)
