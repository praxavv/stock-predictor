import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "app"))
import streamlit as st
from core.analytics.data_service import get_stock_data
from core.analytics.technical import calculate_technical_indicators
from components.components import render_sidebar
from components.charts import plot_main_price_chart, plot_rsi

st.set_page_config(page_title="AlphaStream | Analysis", layout="wide")

def main():
    ticker, market = render_sidebar()
    
    st.title("🔍 Interactive Technical Analysis")
    st.caption(f"Deep-dive charting for {ticker} ({market})")
    
    # 1. Timeline Selection
    col1, col2 = st.columns([1, 4])
    with col1:
        period = st.selectbox("Historical Window", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
        interval = st.selectbox("Resolution", ["1d", "1wk"], index=0)
        
    # 2. Fetch Data
    with st.spinner("Analyzing market patterns..."):
        data = get_stock_data(ticker, period=period, interval=interval)
        if data.empty:
            st.error("No data found.")
            return
        
        data = calculate_technical_indicators(data)
        
    # 3. Main Chart
    fig_price = plot_main_price_chart(data, ticker)
    st.plotly_chart(fig_price, use_container_width=True)
    
    # 4. RSI Subplot
    fig_rsi = plot_rsi(data)
    st.plotly_chart(fig_rsi, use_container_width=True)
    
    # 5. Data View (Institutional Grid)
    with st.expander("View Institutional Price Feed"):
        st.dataframe(data.tail(50).style.highlight_max(axis=0))

if __name__ == "__main__":
    main()
