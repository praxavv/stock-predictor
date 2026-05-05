import streamlit as st
import pandas as pd
from typing import Dict
from core.config import COLOR_PALETTE

def render_metric_cards(metrics: Dict):
    """Render professional KPI cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Latest Price", f"${metrics['price']:,.2f}")
    
    with col2:
        color = "normal" if metrics['change'] >= 0 else "inverse"
        st.metric("Day Change", f"{metrics['change'] * 100:.2f}%", delta=f"{metrics['change'] * 100:.2f}%", delta_color=color)
    
    with col3:
        st.metric("RSI (14)", f"{metrics['rsi']:.1f}")
    
    with col4:
        st.metric("MA20 Status", "Above" if metrics['price'] > metrics['ma20'] else "Below")

def render_sidebar():
    """Consistent sidebar with branding and ticker selection."""

    import streamlit as st
    from core.config import MARKET_SEGMENTS

    # Initialize defaults only once
    if "market" not in st.session_state:
        st.session_state.market = "USA"

    if "ticker" not in st.session_state:
        st.session_state.ticker = MARKET_SEGMENTS["USA"][0]

    with st.sidebar:

        # MARKET SELECTBOX
        market_options = ["USA", "INDIA"]

        selected_market = st.selectbox(
            "Market Segment",
            market_options,
            index=market_options.index(st.session_state.market)
        )

        st.session_state.market = selected_market

        # TICKERS FOR MARKET
        tickers = MARKET_SEGMENTS[selected_market]

        # Prevent invalid ticker after market switch
        if st.session_state.ticker not in tickers:
            st.session_state.ticker = tickers[0]

        # TICKER SELECTBOX
        selected_ticker = st.selectbox(
            "Select Ticker",
            tickers,
            index=tickers.index(st.session_state.ticker)
        )

        st.session_state.ticker = selected_ticker

        st.markdown("---")

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
