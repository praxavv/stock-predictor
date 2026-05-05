import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from core.config import CHART_THEME, COLOR_PALETTE

def plot_main_price_chart(data: pd.DataFrame, ticker: str) -> go.Figure:
    """Create a professional candlestick chart with indicators."""
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price"
    ))

    # Moving Averages
    if 'MA20' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], line=dict(color=COLOR_PALETTE['primary'], width=1.5), name='MA20'))
    if 'MA50' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], line=dict(color=COLOR_PALETTE['secondary'], width=1.5), name='MA50'))
    if 'MA200' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['MA200'], line=dict(color='#888', width=1, dash='dot'), name='MA200'))

    # Bollinger Bands
    if 'BB_upper' in data.columns:
         fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], line=dict(color='#333', width=0.5), name='BB Upper', showlegend=False))
         fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], line=dict(color='#333', width=0.5), fill='tonexty', name='BB Lower', showlegend=False))

    fig.update_layout(
        title=f"{ticker} | Price Analysis",
        template=CHART_THEME,
        height=600,
        xaxis_rangeslider_visible=False,
        yaxis_title="Price",
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig

def plot_rsi(data: pd.DataFrame) -> go.Figure:
    """Professional RSI subplot."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='#D4AF37', width=1.5), name='RSI'))
    
    # Levels
    fig.add_hline(y=70, line_dash="dot", line_color="red", line_width=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", line_width=1)
    
    fig.update_layout(
        height=200,
        template=CHART_THEME,
        yaxis_title="RSI",
        yaxis=dict(range=[0, 100]),
        margin=dict(l=0, r=0, b=0, t=10)
    )
    return fig

def plot_backtest_performance(results: pd.DataFrame) -> go.Figure:
    """Cumulative performance plot for backtest results."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=results.index, y=results['Cum_Benchmark'], name='Benchmark', line=dict(color='#888', width=1)))
    fig.add_trace(go.Scatter(x=results.index, y=results['Cum_Strategy'], name='Strategy', line=dict(color=COLOR_PALETTE['primary'], width=2)))
    
    fig.update_layout(
        title="Cumulative Performance vs Benchmark",
        template=CHART_THEME,
        height=400,
        yaxis_title="Growth (1.0 = Initial)",
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig
