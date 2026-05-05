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
    
    with st.sidebar:
        market = st.selectbox(
            "Market Segment",
            ["USA", "INDIA"]
        )
        from core.config import MARKET_SEGMENTS
        tickers = MARKET_SEGMENTS[market]
        ticker = st.selectbox(
            "Select Ticker",
            tickers
        )
        st.markdown("---")
        st.info(
            "AlphaStream uses real-time market data "
            "to generate high-conviction signals."
        )
        return ticker, market

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
