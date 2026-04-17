import streamlit as st
from src.data.data_service import get_stock_data
from src.indicators.technical import calculate_technical_indicators
from src.backtest.engine import backtest_strategy
from src.ui.components import render_sidebar, render_backtest_report
from src.ui.charts import plot_backtest_performance

st.set_page_config(page_title="AlphaStream | Backtester", layout="wide")

def main():
    ticker, market = render_sidebar()
    
    st.title("🧪 Institutional Backtesting Engine")
    st.caption(f"Strategy validation and risk auditing for {ticker} ({market})")
    
    # 1. Backtest Settings
    col1, col2 = st.columns([1, 4])
    with col1:
        st.subheader("Config")
        strategy = st.selectbox("Strategy Logic", ["MA_CROSS", "BUY_AND_HOLD"], index=0)
        period = st.selectbox("Historical Lookback", ["1y", "2y", "5y", "10y"], index=2)
        
    # 2. Run Backtest
    with st.spinner("Simulating strategy..."):
        data = get_stock_data(ticker, period=period)
        if data.empty:
            st.error("No data found.")
            return
            
        data = calculate_technical_indicators(data)
        results, metrics = backtest_strategy(data, strategy_type=strategy)
        
    # 3. Report & Visuals
    render_backtest_report(metrics)
    
    st.markdown("---")
    
    fig_perf = plot_backtest_performance(results)
    st.plotly_chart(fig_perf, use_container_width=True)
    
    # 4. Strategy Log
    with st.expander("Strategy Execution Log"):
        st.write("Displaying last 20 signals and performance delta:")
        st.dataframe(results[['Close', 'Signal', 'Strategy_Return', 'Cum_Strategy']].tail(20))

if __name__ == "__main__":
    main()
