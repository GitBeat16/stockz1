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
    from pattern_detector import get_latest_patterns
    from pattern_analysis import analyse_all_patterns
except ImportError:
    st.error("Backend modules missing. Please ensure data_loader, pattern_detector, and pattern_analysis are in the root.")

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

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
    "Shield": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "News": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2"><path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10l4 4v10a2 2 0 0 1-2 2z"/><path d="M7 8h5"/><path d="M7 12h10"/><path d="M7 16h10"/></svg>',
    "Brain": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.73-2.73 2.5 2.5 0 0 1-.31-4.71 2.5 2.5 0 0 1 .41-4.5 2.5 2.5 0 0 1 5.09-1.5z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.73-2.73 2.5 2.5 0 0 0 .31-4.71 2.5 2.5 0 0 0-.41-4.5 2.5 2.5 0 0 0-5.09-1.5z"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. ADVANCED UI CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
[data-testid="stAppViewContainer"] {{ background: radial-gradient(circle at top right, #0f172a, #020617); font-family: 'Plus Jakarta Sans', sans-serif; }}
.quant-card {{ background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 1.5rem; transition: all 0.3s ease; animation: fadeIn 0.8s ease-out; margin-bottom: 1rem; }}
.ai-bubble {{ background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 15px; margin-top: 10px; font-size: 0.85rem; color: #e2e8f0; }}
.news-item {{ padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); transition: background 0.2s; }}
.news-item:hover {{ background: rgba(59, 130, 246, 0.05); }}
.live-dot {{ height: 8px; width: 8px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 0 0 rgba(16, 185, 129, 1); animation: pulse-green 2s infinite; }}
@keyframes pulse-green {{ 0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }} 70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }} 100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }} }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.label {{ font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.75rem; font-weight: 800; margin-top: 0.25rem; color: #f8fafc; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}
.stButton > button {{ border-radius: 12px !important; background: transparent !important; color: #3b82f6 !important; font-weight: 700 !important; border: 1px solid #3b82f6 !important; transition: 0.4s !important; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.1em; }}
.stButton > button:hover {{ color: white !important; background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%) !important; border: 1px solid transparent !important; }}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR & NAVIGATION
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:1.2rem; margin-bottom:20px;'>StockZ Terminal</h2>", unsafe_allow_html=True)
    ticker = st.text_input("INSTRUMENT", value="AAPL").upper().strip()
    period = st.selectbox("LOOKBACK", options=["6mo", "1y", "2y", "5y"], index=1)
    st.markdown("---")
    st.markdown(f'<div class="label">{SVG_ICONS["Brain"]} SYSTEM STATUS</div>', unsafe_allow_html=True)
    st.markdown('<div class="ai-bubble">Terminal calibrated. Monitoring live liquidity and news flow.</div>', unsafe_allow_html=True)
    st.markdown("---")
    analyse = st.button("EXECUTE ANALYSIS", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# 5. LIVE SENTIMENT CORE
# ════════════════════════════════════════════════════════════════════════════
def get_live_sentiment(ticker_symbol):
    try:
        search = yf.Search(ticker_symbol, news_count=5)
        news = search.news
        if not news: return [], 50 # Default Neutral
        
        # Simple keywords for scoring (since we avoid heavy NLP libs for speed)
        bullish_terms = ["surge", "buy", "growth", "high", "positive", "profit", "gain", "upgrade", "outperform"]
        bearish_terms = ["drop", "sell", "fall", "low", "negative", "loss", "risk", "downgrade", "underperform"]
        
        score = 50
        processed_news = []
        for n in news:
            title = n.get('title', '').lower()
            sent = "NEUTRAL"
            if any(word in title for word in bullish_terms):
                score += 8
                sent = "BULLISH"
            elif any(word in title for word in bearish_terms):
                score -= 8
                sent = "BEARISH"
            processed_news.append({"h": n.get('title')[:60] + "...", "s": sent})
            
        return processed_news, min(max(score, 10), 90)
    except:
        return [{"h": "News feed currently restricted", "s": "N/A"}], 50

# ════════════════════════════════════════════════════════════════════════════
# 6. ROUTER & VALIDATION
# ════════════════════════════════════════════════════════════════════════════
if not analyse and st.session_state.last_df is None:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if lottie_scan: st_lottie(lottie_scan, height=300, key="initial")
        st.markdown("<p style='text-align:center; color:#64748b;' class='mono'>AWAITING INSTRUMENT SELECTION...</p>", unsafe_allow_html=True)
    st.stop()

if analyse:
    with st.spinner("Decoding Market Fractals..."):
        df = load_stock_data(ticker, period)
        if df is None or df.empty or "Open" not in df.columns:
            st.error(f"DATA_FAILURE: Symbol '{ticker}' returned no data. Check ticker and retry.")
            st.stop()
        
        info = get_ticker_info(ticker)
        news_data, sent_score = get_live_sentiment(ticker)
        st.session_state.last_df = df
        st.session_state.last_info = info
        st.session_state.last_ticker = ticker
        st.session_state.last_news = news_data
        st.session_state.last_sent_score = sent_score

# Load cached state
df = st.session_state.last_df
info = st.session_state.last_info
active_ticker = st.session_state.last_ticker
news_items = st.session_state.last_news
sentiment_score = st.session_state.last_sent_score

stats_all = analyse_all_patterns(df)
latest_patterns = get_latest_patterns(df)
latest_close = float(df["Close"].iloc[-1])
primary_pattern = latest_patterns[0] if latest_patterns else "STABLE CONSOLIDATION"

# ── DASHBOARD UI ─────────────────────────────────────────────────────────────
st.markdown(f"""
    <div style='margin-bottom:2rem;'>
        <div class='label'><span class='live-dot'></span> {info['sector']} • LIVE FEED (IST: {get_ist_time()})</div>
        <div style='font-size:2.8rem; font-weight:800; letter-spacing:-0.02em;'>{info['name']} <span style='color:#3b82f6' class='mono'>{active_ticker}</span></div>
    </div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="quant-card"><div class="label">Last Price</div><div class="value mono">${latest_close:,.2f}</div></div>', unsafe_allow_html=True)
with c2: 
    change = df['Close'].pct_change().iloc[-1] * 100
    color = "#10b981" if change >= 0 else "#ef4444"
    st.markdown(f'<div class="quant-card"><div class="label">24H Change</div><div class="value mono" style="color:{color};">{change:+.2f}%</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="quant-card"><div class="label">Dominant Signal</div><div class="value" style="font-size:1.2rem; color:#3b82f6;">{primary_pattern}</div></div>', unsafe_allow_html=True)
with c4:
    vol = df['Close'].pct_change().std() * np.sqrt(252) * 100
    st.markdown(f'<div class="quant-card"><div class="label">Volatility (Annu)</div><div class="value mono">{vol:.1f}%</div></div>', unsafe_allow_html=True)

fig = go.Figure(data=[go.Candlestick(x=df.tail(120).index, open=df.tail(120)['Open'], high=df.tail(120)['High'], low=df.tail(120)['Low'], close=df.tail(120)['Close'], increasing_line_color='#10b981', decreasing_line_color='#ef4444')])
fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

r_col1, r_col2, r_col3 = st.columns([1.2, 1.4, 1.4])

with r_col1:
    st.markdown('<div class="quant-card" style="height:450px;">', unsafe_allow_html=True)
    st.markdown(f'<div class="label">{SVG_ICONS["Shield"]} Pattern Reliability</div>', unsafe_allow_html=True)
    avg_win = sum([s['win_rate'] for s in stats_all.values()]) / len(stats_all) if stats_all else 50
    fig_gauge = go.Figure(go.Indicator(mode = "gauge+number", value = avg_win, number = {'suffix': "%", 'font': {'family': "JetBrains Mono", 'color': "#f8fafc", 'size': 24}},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#3b82f6"}, 'bgcolor': "rgba(0,0,0,0)"}))
    fig_gauge.update_layout(height=220, margin=dict(l=10,r=10,t=40,b=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown(f'<div class="ai-bubble" style="text-align:center;">Backtest Accuracy: <b>{avg_win:.1f}%</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r_col2:
    st.markdown('<div class="quant-card" style="height:450px;">', unsafe_allow_html=True)
    st.markdown(f'<div class="label">{SVG_ICONS["News"]} Live {active_ticker} Sentiment</div>', unsafe_allow_html=True)
    s_label = "BULLISH FLOW" if sentiment_score > 55 else "BEARISH FLOW" if sentiment_score < 45 else "NEUTRAL BIAS"
    s_color = "#10b981" if sentiment_score > 55 else "#ef4444" if sentiment_score < 45 else "#64748b"
    st.markdown(f'<div style="font-size:1.4rem; font-weight:800; color:{s_color}; margin:15px 0;">{s_label}</div>', unsafe_allow_html=True)
    for item in news_items:
        st.markdown(f'<div class="news-item"><div style="font-size:0.75rem; color:#f8fafc;">{item["h"]}</div><div class="mono" style="font-size:0.6rem; color:#3b82f6;">{item["s"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r_col3:
    st.markdown('<div class="quant-card" style="height:450px;">', unsafe_allow_html=True)
    st.markdown(f'<div class="label">{SVG_ICONS["Brain"]} AI Context</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="ai-bubble">
    <b>Market Mood:</b> The {s_label.lower()} reflects active news headlines.<br><br>
    <b>Fractal State:</b> {primary_pattern} confirmed on the {period} timeframe.<br><br>
    <b>Volatility:</b> {vol:.1f}% indicates {"high risk" if vol > 30 else "moderate risk" if vol > 15 else "low risk"} profile.
    </div>""", unsafe_allow_html=True)
    st.markdown(f'<div class="label" style="margin-top:20px;">Trend Strength</div>', unsafe_allow_html=True)
    st.progress(min(max(sentiment_score/100, 0.0), 1.0))
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem;' class='label'>Historical Performance Matrix</div>", unsafe_allow_html=True)
cols = st.columns(len(stats_all))
for i, (name, stats) in enumerate(stats_all.items()):
    with cols[i]:
        st.markdown(f'<div class="quant-card"><div class="label" style="color:#10b981">{name}</div><div style="font-size:1.4rem; font-weight:700; margin:0.5rem 0;">{stats["win_rate"]}%</div><div class="label">Avg: {stats["avg_return"]:.2f}%</div></div>', unsafe_allow_html=True)
