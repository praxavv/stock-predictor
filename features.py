import plotly.graph_objects as go
import numpy as np

def add_indicator_toggles(st):
    show_ma20 = st.checkbox("Show MA20", value=True)
    show_ma50 = st.checkbox("Show MA50", value=True)
    show_bb = st.checkbox("Show Bollinger Bands", value=True)
    show_rsi = st.checkbox("Show RSI subplot", value=True)
    return show_ma20, show_ma50, show_bb, show_rsi

def plot_main_chart(data, show_ma20, show_ma50, show_bb):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price"
    ))
    if show_ma20:
        fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], 
                                 line=dict(color='blue', width=2), name='MA20'))
    if show_ma50:
        fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], 
                                 line=dict(color='orange', width=2), name='MA50'))
    if show_bb:
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], 
                                 line=dict(color='green', width=1, dash='dot'), name='BB Upper'))
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], 
                                 line=dict(color='red', width=1, dash='dot'), name='BB Lower'))
    fig.update_layout(height=600, xaxis_rangeslider_visible=False)
    return fig

def plot_rsi(data):
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], 
                                 line=dict(color='purple', width=2), name='RSI'))
    fig_rsi.add_hrect(y0=30, y1=30, line_width=1, line_dash="dot", fillcolor="green", opacity=0.2)
    fig_rsi.add_hrect(y0=70, y1=70, line_width=1, line_dash="dot", fillcolor="red", opacity=0.2)
    fig_rsi.update_layout(height=250, yaxis=dict(title="RSI"))
    return fig_rsi

def backtest_strategy(data):
    """Simple MA20/MA50 crossover vs buy-and-hold backtest."""
    data = data.copy()
    data['Signal'] = 0
    data.loc[data['MA20'] > data['MA50'], 'Signal'] = 1
    data.loc[data['MA20'] < data['MA50'], 'Signal'] = -1

    # Strategy returns
    data['Return'] = data['Close'].pct_change()
    data['Strategy'] = data['Signal'].shift(1) * data['Return']
    cum_strategy = (1 + data['Strategy']).cumprod() - 1
    cum_buyhold = (1 + data['Return']).cumprod() - 1

    return cum_strategy, cum_buyhold
