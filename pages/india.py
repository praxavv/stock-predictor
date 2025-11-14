# pages/indian_stocks.py
import streamlit as st
import plotly.graph_objects as go
import features
from core import get_stock_data, calculate_indicators, predict_next_close, get_signal

st.title("🇮🇳  Stock Predictor")

ticker = st.text_input("Enter Indian stock ticker (e.g. TCS.NS, INFY.NS, RELIANCE.BO):", "TCS.NS")

period = st.selectbox("Select Period",
                      ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                      index=2)
interval = st.selectbox("Select Interval",
                        ["1d", "1wk", "1mo"],
                        index=0)

if ticker:
    data = get_stock_data(ticker, period, interval)
    if data is None or data.empty:
        st.warning("No data found. Try another ticker like INFY.NS or RELIANCE.BO.")
    else:
        data = calculate_indicators(data)
        st.write(f"### Latest data for {ticker} ({period}, {interval})")
        st.dataframe(data.tail())

        predicted_price = predict_next_close(data)
        signal = get_signal(data)

        st.write(f"### Predicted next close: ₹{predicted_price:.2f}")
        st.sidebar.write("🧠 Model used: RandomForestRegressor")
        st.write(f"### Signal based on MA crossover: {signal}")

        # --- Chart ---
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Actual Close'))
        fig.add_trace(go.Scatter(x=[data.index[-1]], y=[predicted_price],
                                 mode='markers+text',
                                 name='Predicted Tomorrow',
                                 text=['Tomorrow'],
                                 textposition='bottom center',
                                 marker=dict(size=10, color='orange')))
        fig.update_layout(title=f"{ticker} Price & Tomorrow Prediction",
                          xaxis_title="Date",
                          yaxis_title="Price (₹)",
                          height=500)
        st.plotly_chart(fig, use_container_width=True)
