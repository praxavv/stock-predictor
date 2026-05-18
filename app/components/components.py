import streamlit as st
import pandas as pd
from typing import Dict
from core.config import COLOR_PALETTE
import core.database as db
from datetime import datetime

@st.dialog("🔐 Account Management")
def account_management_dialog():
    mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
    username = st.text_input("Username")
    email = None
    if mode == "Sign Up":
        email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Confirm", use_container_width=True):
        if not username or not password:
            st.error("Please fill all fields")
            return
            
        if mode == "Sign Up":
            if not email:
                st.error("Email is required for signup")
                return
            if db.create_user(username, email, password):
                st.success("Account created! Please switch to Login.")
            else:
                st.error("Username already exists.")
        else:
            if db.authenticate_user(username, password):
                st.session_state.user = username
                data = db.get_user_data(username)
                st.session_state.paper_balance = data['balance']
                st.session_state.paper_holdings = data['holdings']
                st.session_state.paper_history = data['history']
                st.success("Welcome back!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

def render_account_section():
    if "user" not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user:
        st.success(f"Logged in: **{st.session_state.user}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.paper_balance = 1000000.0
            st.session_state.paper_holdings = {}
            st.session_state.paper_history = []
            st.rerun()
    else:
        if st.button("🔐 Open Account / Login", use_container_width=True, type="primary"):
            account_management_dialog()

def render_metric_cards(metrics: Dict, symbol: str = "$"):
    """Render professional KPI cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Latest Price", f"{symbol}{metrics['price']:,.2f}")
    
    with col2:
        color = "normal" if metrics['change'] >= 0 else "inverse"
        st.metric("Day Change", f"{metrics['change'] * 100:.2f}%", delta=f"{metrics['change'] * 100:.2f}%", delta_color=color)
    
    with col3:
        st.metric("RSI (14)", f"{metrics['rsi']:.1f}")
    
    with col4:
        st.metric("MA20 Status", "Above" if metrics['price'] > metrics['ma20'] else "Below")

def render_sidebar():
    """Consistent sidebar with branding and ticker selection."""

    from core.config import MARKET_SEGMENTS

    # Initialize defaults only once
    if "market" not in st.session_state:
        st.session_state.market = "USA"

    if "ticker" not in st.session_state:
        # Flatten tickers to get the first one for default
        first_market = MARKET_SEGMENTS["USA"]
        all_usa_tickers = [ticker for sector in first_market.values() for ticker in sector]
        st.session_state.ticker = all_usa_tickers[0]

    with st.sidebar:
        # 1. AUTH AT THE VERY TOP
        render_account_section()

        # 2. MARKET SELECTBOX
        market_options = list(MARKET_SEGMENTS.keys())

        selected_market = st.selectbox(
            "Market Segment",
            market_options,
            index=market_options.index(st.session_state.market)
        )

        st.session_state.market = selected_market

        # 3. TICKERS FOR MARKET (Flattened)
        market_data = MARKET_SEGMENTS[selected_market]
        tickers = [ticker for sector in market_data.values() for ticker in sector]

        if st.session_state.ticker not in tickers:
            st.session_state.ticker = tickers[0]

        selected_ticker = st.selectbox(
            "Select Ticker",
            tickers,
            index=tickers.index(st.session_state.ticker)
        )

        st.session_state.ticker = selected_ticker

        st.info(
            "Pranav's Analysis Lab uses real-time market data "
            "to generate analytical insights and trading signals."
        )

    return st.session_state.ticker, st.session_state.market

def render_backtest_report(metrics: Dict):
    """Formatted report for strategy backtesting."""
    st.subheader("Performance Analytics")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Return", f"{metrics['Total Return']*100:.2f}%")
    col2.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
    col3.metric("Win Rate", f"{metrics['Win Rate']*100:.2f}%")
    
    col4, col5, col6 = st.columns(3)
    col4.metric("Benchmark Return", f"{metrics['Benchmark Return']*100:.2f}%")
    col5.metric("Max Drawdown", f"{metrics['Max Drawdown']*100:.2f}%")
    col6.metric("Annualized Vol", f"{metrics['Volatility']*100:.2f}%")
