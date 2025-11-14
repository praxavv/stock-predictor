# stock.py
import streamlit as st
import plotly.graph_objects as go
import features
from core import get_stock_data, calculate_indicators, predict_next_close, get_signal

st.title("📈 Stock Predictor")

ticker = st.text_input("Enter stock ticker (e.g. AAPL, TCS.NS):", "AAPL")

period = st.selectbox("Select Period",
                      ["1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"],
                      index=1)
interval = st.selectbox("Select Interval",
                        ["1m","2m","5m","15m","30m","60m","90m","1d","5d","1wk","1mo","3mo"],
                        index=0)

if ticker:
    data = get_stock_data(ticker, period, interval)
    if data is None:
        st.warning("No data found. Try another combination.")
    else:
        data = calculate_indicators(data)
        st.write(f"### Latest data for {ticker} ({period}, {interval})")
        st.dataframe(data.tail())

        predicted_price = predict_next_close(data)
        signal = get_signal(data)

        st.write(f"### Predicted next close: ${predicted_price:.2f}")
        st.sidebar.write(f"🧠 Model used: RandomForestRegressor")
        st.write(f"### Signal based on MA crossover: {signal}")
