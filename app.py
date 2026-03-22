import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random

# ── Backend imports (Assuming these exist in your project) ──────────────────
from data_loader      import load_stock_data, get_ticker_info
from pattern_detector import get_latest_patterns, PATTERNS
from pattern_analysis import analyse_all_patterns, build_ai_explanation

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="TERMINAL | v5.2", layout="wide", initial_sidebar_state="expanded")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY (Icons & Logos)
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Hammer": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M8 2h8v4H8z"/></svg>',
    "Doji": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M4 12h16"/></svg>',
    "Bullish Engulfing": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="10" width="6" height="10" fill="currentColor"/><rect x="14" y="4" width="6" height="18" fill="none" stroke="currentColor"/></svg>',
    "Bearish Engulfing": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="6" height="18" fill="none" stroke="currentColor"/><rect x="14" y="10" width="6" height="10" fill="currentColor"/></svg>',
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Terminal": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>',
    "Pulse": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. ADVANCED QUANT CSS (Glassmorphism & Terminal Stylings)
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [data-testid="stAppViewContainer"] {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #020617; color: #f8fafc; }}
.quant-card {{ 
    background: rgba(30, 41, 59, 0.3); 
    backdrop-filter: blur(8px); 
    border: 1px solid rgba(51, 65, 85, 0.4); 
    border-radius: 12px; 
    padding: 1.5rem; 
    transition: all 0.3s ease;
}}
.quant-card:hover {{ border: 1px solid #3b82f6; transform: translateY(-2px); }}
.terminal-box {{ 
    background: #000; 
    border-radius: 8px; 
    padding: 12px; 
    font-family: 'JetBrains Mono', monospace; 
    font-size: 11px; 
    border: 1px solid #1e293b;
    height: 120px;
    overflow-y: auto;
}}
.log-entry {{ color: #10b981; margin-bottom: 4px; opacity: 0.9; }}
.risk-panel {{ background: rgba(16, 185, 129, 0.03); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 1.2rem; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}
.label {{ font-size: 0.65rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; }}
.value {{ font-size: 1.6rem; font-weight: 800; margin-top: 0.2rem; }}
.stButton > button {{ width: 100%; background: #1e293b !important; border: 1px solid #334155 !important; color: white !important; font-weight: 700 !important; border-radius: 8px !important; }}
.stButton > button:hover {{ border-color: #3b82f6 !important; color: #3b82f6 !important; }}
.badge {{ display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }}
.bullish-badge {{ background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }}
.bearish-badge {{ background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR & TERMINAL LOGS
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:1rem; letter-spacing:2px;'>QUANT ENGINE v5.2</h2>", unsafe_allow_html=True)
    
    ticker = st.text_input("INSTRUMENT", value="AAPL").upper().strip()
    period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
    risk_pct = st.slider("Trade Risk (%)", 0.5, 5.0, 1.0, 0.5)
    
    # Terminal Log Component
    st.markdown(f"<div class='label' style='margin-top:20px; display:flex; align-items:center; gap:5px;'>{SVG_ICONS['Terminal']} Live Sequence</div>", unsafe_allow_html=True)
    log_entries = [
        f"› Initializing {ticker} handshake...",
        "› Fetching WebSocket feeds...",
        "› Running Pattern Recognition...",
        "› Status: Ready for execution"
    ]
    log_html = "".join([f"<div class='log-entry'>{entry}</div>" for entry in log_entries])
    st.markdown(f"<div class='terminal-box'>{log_html}</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    analyse = st.button("RUN QUANT ANALYSIS")

# ════════════════════════════════════════════════════════════════════════════
# 5. CORE LOGIC & COMPUTATION
# ════════════════════════════════════════════════════════════════════════════
if not analyse and 'last_df' not in st.session_state:
    st.markdown(f'<div style="height:75vh; display:flex; flex-direction:column; align-items:center; justify-content:center; opacity:0.3">{SVG_ICONS["Logo"]}<p class="label" style="margin-top:1rem">Awaiting Signal Input</p></div>', unsafe_allow_html=True)
    st.stop()

if analyse or 'last_df' not in st.session_state:
    df = load_stock_data(ticker, period)
    info = get_ticker_info(ticker)
    st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, info, ticker

df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
stats_all = analyse_all_patterns(df)
latest_patterns = get_latest_patterns(df)
latest_close = float(df["Close"].iloc[-1])
daily_chg = (latest_close - float(df["Close"].iloc[-2])) / float(df["Close"].iloc[-2]) * 100
primary = latest_patterns[0] if latest_patterns else None

# Risk Calculations
current_low = float(df["Low"].iloc[-1])
stop_loss = current_low * 0.995 
risk_per_share = latest_close - stop_loss
dollar_risk = st.session_state.cash_balance * (risk_pct / 100)
suggested_shares = int(dollar_risk / risk_per_share) if risk_per_share > 0 else 0

# ════════════════════════════════════════════════════════════════════════════
# 6. MAIN DASHBOARD UI
# ════════════════════════════════════════════════════════════════════════════
# Header
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(f"<div><div class='label' style='color:#3b82f6'>{info['sector']} • {info['industry']}</div><div style='font-size:2.8rem; font-weight:800;'>{info['name']} <span style='color:#1e293b' class='mono'>{active_ticker}</span></div></div>", unsafe_allow_html=True)

# Top Bar: Gauge and Risk
r1, r2 = st.columns([1.5, 2.5])
with r1:
    # Signal Strength Gauge
    win_rate = stats_all[primary]['win_rate'] if primary else 50
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = win_rate,
        number = {'suffix': "%", 'font': {'family': "JetBrains Mono", 'color': "#f8fafc"}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#334155"},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [{'range': [0, 100], 'color': "rgba(51, 65, 85, 0.3)"}]
        }
    ))
    fig_gauge.update_layout(height=180, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

with r2:
    st.markdown(f"""
    <div class="risk-panel">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:15px;">{SVG_ICONS['Shield']} <span class="label" style="color:#10b981;">Risk Execution Module</span></div>
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:15px;">
            <div><div class="label">Position Size</div><div class="mono" style="font-size:1.3rem;">{suggested_shares} <span style='font-size:0.7rem; color:#64748b;'>SHARES</span></div></div>
            <div><div class="label">Hard Stop</div><div class="mono" style="font-size:1.3rem; color:#ef4444;">${stop_loss:.2f}</div></div>
            <div><div class="label">Risk Cap</div><div class="mono" style="font-size:1.3rem;">${dollar_risk:,.0f}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# KPI Metrics Grid
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
m1.markdown(f'<div class="quant-card"><div class="label">Price</div><div class="value mono">{latest_close:,.2f}</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="quant-card"><div class="label">Session Delta</div><div class="value mono" style="color:{"#10b981" if daily_chg >=0 else "#ef4444"}">{daily_chg:+.2f}%</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="quant-card"><div class="label">Active Signal</div><div class="value" style="font-size:1.1rem; color:#3b82f6; text-transform:uppercase;">{primary if primary else "Neural Drift"}</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="quant-card"><div class="label">Buying Power</div><div class="value mono">${st.session_state.cash_balance:,.0f}</div></div>', unsafe_allow_html=True)

# Main Charting Area
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
c_left, c_right = st.columns([2.2, 1])

with c_left:
    chart_df = df.tail(100)
    fig = go.Figure(data=[go.Candlestick(
        x=chart_df.index, open=chart_df['Open'], high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'],
        increasing_line_color='#10b981', decreasing_line_color='#ef4444',
        increasing_fillcolor='rgba(16, 185, 129, 0.2)', decreasing_fillcolor='rgba(239, 68, 68, 0.2)'
    )])
    fig.update_layout(
        template="plotly_dark", height=450, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False, yaxis=dict(side="right", gridcolor="#1e293b", font=dict(family="JetBrains Mono"))
    )
    st.plotly_chart(fig, use_container_width=True)

with c_right:
    st.markdown(f"<div class='label' style='margin-bottom:10px; display:flex; align-items:center; gap:8px;'>{SVG_ICONS['Pulse']} Signal intelligence</div>", unsafe_allow_html=True)
    if latest_patterns:
        for p in latest_patterns:
            sig_class = "bullish-badge" if "Bullish" in p or p in ["Hammer", "Morning Star"] else "bearish-badge"
            st.markdown(f'<div class="badge {sig_class}" style="margin-bottom:10px;">{SVG_ICONS.get(p, "")} {p.upper()}</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background:rgba(30,41,59,0.2); padding:1.2rem; border-radius:12px; border:1px solid #1e293b;'>
            <div class='label' style='color:#3b82f6; margin-bottom:8px;'>Probability Note</div>
            <div style='font-size:0.85rem; line-height:1.6; color:#94a3b8; font-style:italic;'>
                {build_ai_explanation(primary, stats_all[primary])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; padding:3rem; color:#334155; border:1px dashed #1e293b; border-radius:12px;'>NO HIGH-PROBABILITY SIGNALS DETECTED</div>", unsafe_allow_html=True)

st.markdown("<div style='height:50px'></div><div style='text-align:center; border-top:1px solid #1e293b; padding:2rem; color:#334155; font-size:0.6rem; letter-spacing:3px;'>TERMINAL v5.2 • NO EMOJI DEPLOYMENT • ENCRYPTED SESSION</div>", unsafe_allow_html=True)
