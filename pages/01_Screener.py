import streamlit as st
import plotly.graph_objects as go
from core import get_stock_data, calculate_indicators, predict_next_close, get_signal

st.set_page_config(
    page_title="Screener",
    page_icon="📈",
    layout="wide"
)

# ---------------------------------------------------
# Compact Title + Right-Aligned Tiny Dropdown
# ---------------------------------------------------
col_title, col_dropdown = st.columns([0.85, 0.15])

with col_dropdown:
    market = st.selectbox(
        "",
        ["INDIA", "USA"],
        index=0,
        label_visibility="collapsed"
    )

# Title must appear AFTER knowing the market
with col_title:
    if market == "INDIA":
        st.markdown("<h1 style='margin-top: 5px;'>🇮🇳 INDIA</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='margin-top: 5px;'>🇺🇸 USA</h1>", unsafe_allow_html=True)

# ---------------------------------------------------
# Market-Specific Inputs
# ---------------------------------------------------
if market == "INDIA":
    ticker = st.text_input("Enter Indian stock ticker:", "TCS.NS")
    period = st.selectbox("Select Period", ["1mo","3mo","6mo","1y","2y","5y"], index=2)
    interval = st.selectbox("Select Interval", ["1wk","1d","1h","30m","15m","5m","1m"], index=0)

else:
    ticker = st.text_input("Enter US stock ticker:", "AAPL")
    period = st.selectbox("Select Period",
                          ["1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"], index=1)
    interval = st.selectbox("Select Interval",
                            ["1m","2m","5m","15m","30m","60m","90m","1d","5d","1wk","1mo","3mo"], index=0)

# ---------------------------------------------------
# Data Loading + Chart
# ---------------------------------------------------
if ticker:
    data = get_stock_data(ticker, period, interval)

    if data is None or data.empty:
        st.warning("No data found. Try different inputs.")
        st.stop()

    data = calculate_indicators(data)

    if data.empty:
        st.warning("Not enough data for indicators.")
        st.stop()

    st.write(f"### Latest data for {ticker}")
    st.dataframe(data.tail())

    predicted_price = predict_next_close(data)
    signal = get_signal(data)

    st.sidebar.write("🧠 Model used: RandomForestRegressor")

    if market == "INDIA":
        st.write(f"### Predicted next close: ₹{predicted_price:.2f}")
    else:
        st.write(f"### Predicted next close: ${predicted_price:.2f}")

    st.write(f"### Signal: {signal}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Actual Close'))
    fig.add_trace(go.Scatter(x=[data.index[-1]], y=[predicted_price],
                             mode='markers+text',
                             text=['Tomorrow'],
                             textposition='bottom center',
                             marker=dict(size=10, color='orange')))
    fig.update_layout(title=f"{ticker} Price & Prediction", height=500)

    st.plotly_chart(fig, use_container_width=True)
