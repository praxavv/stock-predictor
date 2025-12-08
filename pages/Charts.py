import streamlit as st
import plotly.graph_objects as go
import features
from core import get_stock_data, calculate_indicators

st.title("📉 Charts & Indicators")

ticker = st.text_input("Enter stock ticker again (e.g. AAPL, TCS.NS):", "AAPL")

period = st.selectbox("Select Period",
                      ["1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"],
                      index=1)
interval = st.selectbox("Select Interval",
                        ["1m","2m","5m","15m","30m","60m","90m","1d","5d","1wk","1mo","3mo"],
                        index=0)

if ticker:
    data = get_stock_data(ticker, period, interval)
    if data is not None:
        data = calculate_indicators(data)

        # Toggles
        show_ma20, show_ma50, show_bb, show_rsi = features.add_indicator_toggles(st)

        # Main chart
        fig = features.plot_main_chart(data, show_ma20, show_ma50, show_bb)
        st.plotly_chart(fig, use_container_width=True)

        # RSI chart
        if show_rsi:
            st.write("### RSI Indicator")
            st.plotly_chart(features.plot_rsi(data), use_container_width=True)

        # Backtest
        st.write("### Backtest: MA20/MA50 vs Buy & Hold")
        cum_strategy, cum_buyhold = features.backtest_strategy(data)
        st.line_chart({"Strategy": cum_strategy, "Buy & Hold": cum_buyhold})
    else:
        st.warning("No data found for this combination.")

st.set_page_config(page_title="Charts", layout="wide")

st.title("📊 Detailed Charts")

if 'data' not in st.session_state:
    st.warning("No data found. Go back and fetch a ticker first.")
    st.stop()

data = st.session_state['data']
ticker = st.session_state['ticker']

st.write(f"### Charts for {ticker}")

# Add toggles
show_ma20, show_ma50, show_bb, show_rsi = features.add_indicator_toggles(st)

fig = features.plot_main_chart(data, show_ma20, show_ma50, show_bb)
st.plotly_chart(fig, use_container_width=True)

if show_rsi:
    st.write("### RSI Indicator")
    fig_rsi = features.plot_rsi(data)
    st.plotly_chart(fig_rsi, use_container_width=True)

st.write("### Backtest Performance")
cum_strategy, cum_buyhold = features.backtest_strategy(data)
st.line_chart({"Strategy": cum_strategy, "Buy & Hold": cum_buyhold})
