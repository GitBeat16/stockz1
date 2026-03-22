import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie

# ── 1. PAGE CONFIG & SESSION STATE ──────────────────────────────────────────
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'active_view' not in st.session_state:
    st.session_state.active_view = "DASHBOARD"

# ── 2. THE AUDIO HACK (Sound Animations) ─────────────────────────────────────
# This injects a small JS function to play a 'click' sound
st.markdown("""
    <audio id="clickSound" src="https://www.soundjay.com/buttons/sounds/button-16.mp3" preload="auto"></audio>
    <script>
    function playClick() {
        var audio = document.getElementById("clickSound");
        audio.play();
    }
    </script>
""", unsafe_allow_html=True)

# ── 3. ADVANCED UI STYLING (Hover Animations & Theme Matching) ───────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

[data-testid="stAppViewContainer"] {{
    background: radial-gradient(circle at top right, #0f172a, #020617);
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

/* Quant Card Glow */
.quant-card {{
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}}

.quant-card:hover {{
    transform: translateY(-5px);
    border-color: rgba(59, 130, 246, 0.5);
    box-shadow: 0 10px 30px -10px rgba(59, 130, 246, 0.2);
}}

/* THEME MATCHING BUTTONS */
.stButton > button {{
    width: 100%;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #3B82F6 0%, #10B981 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em;
    border: none !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    text-transform: uppercase;
}}

/* Hover Animation for Buttons */
.stButton > button:hover {{
    transform: scale(1.03) !important;
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.4) !important;
    filter: brightness(1.1);
}}

/* Active/Click Animation */
.stButton > button:active {{
    transform: scale(0.98) !important;
}}

/* Nav Button Specifics */
[data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}

.label {{ font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.8rem; font-weight: 800; color: #f8fafc; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}
</style>
""", unsafe_allow_html=True)

# ── 4. VECTOR ART REPOSITORY ────────────────────────────────────────────────
SVG_ICONS = {
    "Logo": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Info": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
}

# ── 5. NAVIGATION BAR ────────────────────────────────────────────────────────
# Using custom HTML for the Nav Bar to ensure consistent theme matching
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.8); padding: 15px 25px; border: 1px solid rgba(59, 130, 246, 0.2); margin-bottom: 25px; border-radius: 16px; backdrop-filter: blur(15px);">
    <div style="display: flex; gap: 30px; align-items: center;">
        {SVG_ICONS["Logo"]}
        <span style="color: #fff; font-weight: 800; font-family: 'JetBrains Mono'; cursor: default;">SYSTEM_V3</span>
    </div>
    <div style="display: flex; gap: 20px;">
        <span class="label" style="color: #3B82F6; border-bottom: 2px solid #3B82F6; padding-bottom: 4px;">Dashboard</span>
        <span class="label" style="opacity: 0.5;">Portfolio</span>
        <span class="label" style="opacity: 0.5;">Settings</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ... [Sidebar and Data Loading remains the same as your previous version] ...

# ── 6. EXECUTION ENGINE (With Audio Trigger) ─────────────────────────────────
st.markdown("<div class='label'>Order Execution Engine</div>", unsafe_allow_html=True)
trade_col1, trade_col2 = st.columns([2, 1])

with trade_col1:
    st.markdown('<div class="quant-card">', unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3)
    with q1: qty = st.number_input("QUANTITY", min_value=1, value=10)
    with q2: st.markdown(f'<div class="label">Total Cost</div><div class="value mono" style="font-size:1.4rem;">${qty * 180.50:,.2f}</div>', unsafe_allow_html=True) # Static for example
    with q3: st.markdown(f'<div class="label">Buying Power</div><div class="value mono" style="font-size:1.4rem;">${st.session_state.cash_balance:,.0f}</div>', unsafe_allow_html=True)
    
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        if st.button("PROCEED TO BUY"):
            # Play Sound Hack
            components.html("<script>window.parent.playClick();</script>", height=0)
            # Trade logic...
            st.toast("Order Executed", icon="⚡")
            
    with b_col2:
        if st.button("PROCEED TO SELL"):
            components.html("<script>window.parent.playClick();</script>", height=0)
            st.toast("Position Liquidated", icon="📉")
    st.markdown('</div>', unsafe_allow_html=True)

# ── 7. FINAL USER GUIDE PANEL (SVG Integration) ──────────────────────────────
st.markdown("<div style='margin-top:4rem;'></div>", unsafe_allow_html=True)
with st.expander("OPERATIONAL PROTOCOLS"):
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"#### {SVG_ICONS['Shield']} Integrity")
        st.write("Pattern recognition filters noise via a 120-day historical window.")
    with g2:
        st.markdown(f"#### {SVG_ICONS['Logo']} Deployment")
        st.write("Live data stream synced to terminal session memory.")
    with g3:
        st.markdown(f"#### {SVG_ICONS['Info']} Risk Level")
        st.write("Current Risk Profile: 1.0% based on total equity volatility.")
