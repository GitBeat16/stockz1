import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
import pytz  
import yfinance as yf
from streamlit_lottie import st_lottie
from datetime import datetime

# ── Backend imports ──────────────────────────────────────────────────────────
try:
    from data_loader    import load_stock_data, get_ticker_info
    from pattern_detector import get_latest_patterns, detect_all_patterns
    from pattern_analysis import analyse_all_patterns
except ImportError:
    st.error("SYSTEM_ERROR: Critical backend modules missing. Check root directory.")

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | Multi-Asset Quant", layout="wide", initial_sidebar_state="expanded")

if 'last_df' not in st.session_state:
    st.session_state.last_df = None

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

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "News": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2"><path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10l4 4v10a2 2 0 0 1-2 2z"/><path d="M7 8h5"/><path d="M7 12h10"/><path d="M7 16h10"/></svg>',
    "Brain": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.73-2.73 2.5 2.5 0 0 1-.31-4.71 2.5 2.5 0 0 1 .41-4.5 2.5 2.5 0 0 1 5.09-1.5z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.73-2.73 2.5 2.5 0 0 0 .31-4.71 2.5 2.5 0 0 0-.41-4.5 2.5 2.5 0 0 0-5.09-1.5z"/></svg>',
    "Compare": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2"><path d="M16 3l4 4-4 4M8 21l-4-4 4-4M20 7H9M4 17h11"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. ADVANCED UI CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
[data-testid="stAppViewContainer"] {{ background: #020617; font-family: 'Plus Jakarta Sans', sans-serif; }}
[data-testid="stSidebar"] {{ background: rgba(15, 23, 42, 0.95) !important; border-right: 1px solid rgba(255,255,255,0.05); }}
.quant-card {{ background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.4) 100%); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 1.5rem; margin-bottom: 1rem; }}
.ai-bubble {{ background: rgba(59, 130, 246, 0.05); border-left: 3px solid #3b82f6; border-radius: 4px 12px 12px 4px; padding: 15px; font-size: 0.85rem; color: #94a3b8; line-height: 1.6; }}
.label {{ font-size: 0.65rem; color: #64748b; font-weight: 800; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 4px; }}
.value {{ font-size: 1.5rem; font-weight: 800; color: #f8fafc; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}
.stButton > button {{ border-radius: 8px !important; background: transparent !important; color: #f8fafc !important; font-weight: 600 !important; border: 1px solid rgba(255,255,255,0.1) !important; }}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR & COMPARISON INPUTS
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="margin-top:20px; margin-bottom:30px;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    ticker = st.text_input("PRIMARY_TICKER", value="AAPL").upper().strip()
    
    st.markdown(f'<div class="label" style="margin-top:20px;">{SVG_ICONS["Compare"]} COMPARISON_NODES</div>', unsafe_allow_html=True)
    comp_ticker_1 = st.text_input("NODE_01", value="MSFT").upper().strip()
    comp_ticker_2 = st.text_input("NODE_02", value="GOOGL").upper().strip()
    comp_ticker_3 = st.text_input("NODE_03", value="NVDA").upper().strip()
    
    period = st.selectbox("TIMEFRAME", options=["6mo", "1y", "2y"], index=1)
    st.markdown("---")
    analyse = st.button("SYNC TERMINAL", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# 5. CORE COMPARISON LOGIC
# ════════════════════════════════════════════════════════════════════════════
def get_comparison_data(tickers, period):
    comp_results = []
    for t in tickers:
        if not t: continue
        try:
            data = yf.download(t, period=period, progress=False)
            if not data.empty:
                returns = data['Close'].pct_change().dropna()
                comp_results.append({
                    "ticker": t,
                    "price": float(data['Close'].iloc[-1]),
                    "change": float(data['Close'].pct_change().iloc[-1] * 100),
                    "volatility": float(returns.std() * np.sqrt(252) * 100),
                    "perf_6m": float(((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100)
                })
        except: continue
    return comp_results

# ════════════════════════════════════════════════════════════════════════════
# 6. ROUTER & EXECUTION
# ════════════════════════════════════════════════════════════════════════════
if not analyse and st.session_state.last_df is None:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if lottie_scan: st_lottie(lottie_scan, height=300, key="init")
        st.markdown("<p style='text-align:center; color:#475569;' class='mono'>TERMINAL_IDLE: SYNC_REQUIRED</p>", unsafe_allow_html=True)
    st.stop()

if analyse:
    with st.spinner("Calibrating Multi-Asset Grid..."):
        df = load_stock_data(ticker, period)
        if df is None or df.empty:
            st.error("PRIMARY_TICKER_FAILURE")
            st.stop()
        
        info = get_ticker_info(ticker)
        comparisons = get_comparison_data([comp_ticker_1, comp_ticker_2, comp_ticker_3], period)
        
        st.session_state.last_df = df
        st.session_state.last_info = info
        st.session_state.last_ticker = ticker
        st.session_state.last_comps = comparisons

# Load State
df = st.session_state.last_df
info = st.session_state.last_info
active_ticker = st.session_state.last_ticker
comps = st.session_state.last_comps

# ── HEADER & MAIN METRICS ───────────────────────────────────────────────────
st.markdown(f"<div class='label'>PRIMARY_NODE</div><div style='font-size:2.8rem; font-weight:800; margin-bottom:2rem;'>{info['name']} <span style='color:#3b82f6;'>/ {active_ticker}</span></div>", unsafe_allow_html=True)

# ── COMPARISON SUMMARY GRID ─────────────────────────────────────────────────
st.markdown(f"<div class='label' style='margin-bottom:15px;'>{SVG_ICONS['Compare']} ASSET_COMPARISON_MATRIX</div>", unsafe_allow_html=True)
c_cols = st.columns(len(comps) + 1)

# Primary Asset Card
with c_cols[0]:
    p_change = df['Close'].pct_change().iloc[-1] * 100
    st.markdown(f"""<div class='quant-card' style='border-left: 3px solid #3b82f6;'>
        <div class='label' style='color:#3b82f6;'>{active_ticker} (PRIMARY)</div>
        <div class='value mono'>${float(df['Close'].iloc[-1]):,.2f}</div>
        <div class='label' style='color:{"#10b981" if p_change >=0 else "#ef4444"}; margin-top:8px;'>{p_change:+.2f}% 24H</div>
    </div>""", unsafe_allow_html=True)

# Comparison Asset Cards
for i, asset in enumerate(comps):
    with c_cols[i+1]:
        st.markdown(f"""<div class='quant-card'>
            <div class='label'>{asset['ticker']}</div>
            <div class='value mono'>${asset['price']:,.2f}</div>
            <div class='label' style='color:{"#10b981" if asset['change'] >=0 else "#ef4444"}; margin-top:8px;'>{asset['change']:+.2f}% 24H</div>
        </div>""", unsafe_allow_html=True)

# ── COMPARATIVE PERFORMANCE CHART ────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
fig_comp = go.Figure()

# Add Primary
p_norm = (df['Close'] / df['Close'].iloc[0]) * 100
fig_comp.add_trace(go.Scatter(x=df.index, y=p_norm, name=active_ticker, line=dict(color='#3b82f6', width=3)))

# Add Comparisons
colors = ['#60a5fa', '#34d399', '#f59e0b']
for i, asset in enumerate(comps):
    c_df = yf.download(asset['ticker'], period=period, progress=False)
    c_norm = (c_df['Close'] / c_df['Close'].iloc[0]) * 100
    fig_comp.add_trace(go.Scatter(x=c_df.index, y=c_norm, name=asset['ticker'], line=dict(color=colors[i], width=1.5, dash='dot')))

fig_comp.update_layout(title="RELATIVE_GROWTH_INDEX (BASE 100)", template="plotly_dark", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig_comp, use_container_width=True)

# ── AI COMPARATIVE SUMMARY ──────────────────────────────────────────────────
st.markdown(f"<div class='label'>{SVG_ICONS['Brain']} FRACTAL_COMPARISON_SUMMARY</div>", unsafe_allow_html=True)
best_perf = max(comps, key=lambda x: x['perf_6m']) if comps else {"ticker": active_ticker, "perf_6m": 0}

st.markdown(f"""
<div class='ai-bubble'>
    <b>CORE_INSIGHT:</b> Analysis shows <b>{best_perf['ticker']}</b> is currently outperforming the cluster with a {best_perf['perf_6m']:.1f}% period return. <br><br>
    <b>VOLATILITY_SYNC:</b> {active_ticker} maintains a volatility profile of {df['Close'].pct_change().std() * np.sqrt(252) * 100:.1f}%, which is 
    {"higher" if (df['Close'].pct_change().std()*np.sqrt(252)*100) > (sum(c['volatility'] for c in comps)/len(comps) if comps else 0) else "lower"} 
    than the peer average. <br><br>
    <b>STRATEGY_NOTE:</b> Divergence in price action between {active_ticker} and {comp_ticker_1} may indicate an alpha opportunity if correlation begins to snap back.
</div>
""", unsafe_allow_html=True)
