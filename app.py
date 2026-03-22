import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# ── Backend imports (ensure these files exist in your directory) ─────────────
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
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "History": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>'
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

[data-testid="stSidebar"] { border-right: 1px solid #1e293b; padding-top: 1rem; }

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #2563eb, #10b981) !important;
    color: white !important;
    font-weight: 800 !important;
    padding: 0.6rem !important;
    border-radius: 8px !important;
    border: none !important;
    text-transform: uppercase;
    transition: 0.2s ease;
}

.stButton > button:hover { transform: translateY(-2px); filter: brightness(1.1); }

.portfolio-card { background: rgba(30, 41, 59, 0.3); border: 1px dashed #334155; border-radius: 10px; padding: 15px; margin-bottom: 20px; }
.mono { font-family: 'JetBrains Mono', monospace; }
.label { font-size: 0.65rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
.badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
.bullish-badge { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
.bearish-badge { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
.ledger-row { border-bottom: 1px solid #1e293b; padding: 8px 0; font-size: 0.75rem; display: flex; justify-content: space-between; align-items: center; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR 
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding-bottom:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    
    # Portfolio Summary
    current_val = sum([c * (st.session_state.last_df['Close'].iloc[-1] if 'last_df' in st.session_state else 0) for t, c in st.session_state.portfolio.items()])
    st.markdown(f"""<div class="portfolio-card">
        <div style="display:flex; align-items:center; gap:8px;">{SVG_ICONS['Wallet']} <span class="label">Total Wealth</span></div>
        <div class="mono" style="font-size:1.3rem; font-weight:800; color:#f8fafc;">${(st.session_state.cash_balance + current_val):,.2f}</div>
        <div class="label" style="margin-top:8px;">Available Cash: ${st.session_state.cash_balance:,.2f}</div>
    </div>""", unsafe_allow_html=True)
    
    ticker = st.text_input("TICKER SYMBOL", value="NVDA").upper().strip()
    risk_pct = st.slider("Risk per Trade %", 0.5, 5.0, 1.0, 0.5)
    
    # Perfectly Aligned Sidebar Buttons
    side_c1, side_c2 = st.columns(2)
    with side_c1: analyze_btn = st.button("ANALYZE")
    with side_c2: scan_btn = st.button("SCAN")

# ════════════════════════════════════════════════════════════════════════════
# 5. SCANNER / ANALYSIS LOGIC
# ════════════════════════════════════════════════════════════════════════════
if scan_btn:
    st.markdown("### 📡 Intelligence Scanner")
    for t in WATCHLIST:
        scan_df = load_stock_data(t, "1y")
        patterns = get_latest_patterns(scan_df)
        if patterns:
            sig = PATTERNS[patterns[0]]['signal']
            st.markdown(f"<div class='ledger-row'><span class='mono' style='font-weight:700; color:#3b82f6;'>{t}</span> <span class='badge {sig}-badge'>{patterns[0]}</span></div>", unsafe_allow_html=True)
    st.markdown("---")

if analyze_btn or 'last_df' in st.session_state:
    if analyze_btn:
        df = load_stock_data(ticker, "1y")
        st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, get_ticker_info(ticker), ticker

    df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
    latest_px = float(df["Close"].iloc[-1])
    patterns = get_latest_patterns(df)
    primary = patterns[0] if patterns else None
    shares_owned = st.session_state.portfolio.get(active_ticker, 0)

    # Risk Calculation
    sl_px = float(df["Low"].iloc[-1]) * 0.995
    risk_cap = st.session_state.cash_balance * (risk_pct / 100)
    qty = int(risk_cap / (latest_px - sl_px)) if (latest_px - sl_px) > 0 else 0

    st.markdown(f"## {active_ticker} <span style='color:#64748b; font-size:1rem; font-weight:400;'>{info.get('name', '')}</span>", unsafe_allow_html=True)

    # Main Action Console
    act1, act2, act3 = st.columns([1.5, 1, 1])
    with act1:
        st.markdown(f"""<div style="background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.2); border-radius:10px; padding:12px;">
            <div style="display:flex; align-items:center; gap:8px;">{SVG_ICONS['Shield']} <span class="label" style="color:#3b82f6;">Quant Suggestion</span></div>
            <div class="mono" style="font-size:1rem; margin-top:4px;"><b>Size: {qty}</b> | SL: ${sl_px:.2f}</div>
        </div>""", unsafe_allow_html=True)
    with act2:
        if st.button(f"BUY {qty} UNITS"):
            if st.session_state.cash_balance >= (latest_px * qty):
                st.session_state.cash_balance -= (latest_px * qty)
                st.session_state.portfolio[active_ticker] = shares_owned + qty
                # FIX: Explicitly set keys 'time', 't', 'type', 'px' to match the loop below
                st.session_state.trade_history.append({
                    "time": datetime.now().strftime("%H:%M:%S"), 
                    "t": active_ticker, 
                    "type": "BUY", 
                    "qty": qty, 
                    "px": latest_px
                })
                st.rerun()
    with act3:
        if st.button("CLOSE ALL"):
            if shares_owned > 0:
                st.session_state.cash_balance += (latest_px * shares_owned)
                st.session_state.portfolio[active_ticker] = 0
                st.session_state.trade_history.append({
                    "time": datetime.now().strftime("%H:%M:%S"), 
                    "t": active_ticker, 
                    "type": "SELL", 
                    "qty": shares_owned, 
                    "px": latest_px
                })
                st.rerun()

    # Chart & Intelligence
    c_left, c_right = st.columns([2, 1])
    with c_left:
        fig = go.Figure(data=[go.Candlestick(x=df.tail(60).index, open=df.tail(60)['Open'], high=df.tail(60)['High'], low=df.tail(60)['Low'], close=df.tail(60)['Close'])])
        fig.add_hline(y=sl_px, line_dash="dash", line_color="#ef4444")
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_right := c_right:
        st.markdown("<div class='label' style='display:flex; align-items:center; gap:5px;'>Active Patterns</div>", unsafe_allow_html=True)
        if patterns:
            for p in patterns:
                sig = PATTERNS[p]['signal']
                st.markdown(f'<div class="badge {sig}-badge" style="margin-bottom:8px;">{p} Signal</div>', unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top:20px;' class='label'>Operation Ledger</div>", unsafe_allow_html=True)
        # FIX: The loop keys now strictly match the dictionary created in Buy/Sell logic
        for trade in reversed(st.session_state.trade_history[-5:]):
            color = "#10b981" if trade['type'] == "BUY" else "#ef4444"
            st.markdown(f"""
            <div class='ledger-row'>
                <span class='mono' style='color:#64748b;'>{trade['time']}</span> 
                <span class='mono' style='font-weight:700;'>{trade['t']}</span> 
                <span class='mono' style='color:{color}'>{trade['type']}</span> 
                <span class='mono'>${trade['px']:.0f}</span>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:3rem; color:#1e293b; font-size:0.6rem;'>TERMINAL v8.2 • ALIGNED CORE • NO KEY ERRORS</div>", unsafe_allow_html=True)
