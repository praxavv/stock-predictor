import sys
import os
import yfinance as yf
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "app"))
import streamlit as st
import pandas as pd
import plotly.express as px
from core.analytics.data_service import get_stock_data
from core.analytics.technical import calculate_technical_indicators, get_latest_metrics
from core.prediction.predictor import train_alpha_model, predict_signal
from components.components import render_sidebar, render_metric_cards
from core.config import MARKET_SEGMENTS, COLOR_PALETTE
from core.ai_engine import ask_ai

st.set_page_config(page_title="Pranav's Lab", layout="wide")

def main():
    ticker, market = render_sidebar()
    
    st.title("🚀 Market Intelligence Dashboard")
    st.caption(f"Real-time Alpha Generation for {ticker} ({market})")
    
    # 1. Fetch & Process Data
    data = get_stock_data(ticker)
    if data.empty:
        st.error("No data available.")
        return
        
    data = calculate_technical_indicators(data)
    latest_metrics = get_latest_metrics(data)
    
    # 2. Key Metrics Row
    render_metric_cards(latest_metrics)
    
    st.markdown("---")
    
    # 3. Alpha Prediction Engine
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Alpha Prediction")
        with st.spinner("Training Alpha Model..."):
            model, model_info = train_alpha_model(data)
            prediction = predict_signal(model, data)
  
            
        # Prediction Card
        confidence_color = "green" if prediction['confidence'] > 0.6 else "orange"
        st.markdown(f"""
            <div style="background-color: #161A23; padding: 20px; border-radius: 10px; border: 1px solid #1E2430;">
                <h4 style="margin: 0; color: #888;">Next 24h Signal</h4>
                <h2 style="margin: 10px 0; color: {COLOR_PALETTE['primary'] if prediction['signal'] == 'BULLISH' else COLOR_PALETTE['secondary']}">{prediction['signal']}</h2>
                <h4 style="margin: 0; color: {confidence_color};">Confidence: {prediction['confidence']:.1f}%</h4>
            </div>
        """, unsafe_allow_html=True)
        
        st.caption(f"Model accuracy: {model_info['accuracy']*100:.1f}% based on historical patterns.")

        
    
    # 4. Market Movers (Simplified)
    st.subheader("Institutional Market Movers")
    # Flatten tickers from all sectors
    all_tickers = [t for s in MARKET_SEGMENTS[market].values() for t in s]
    peers = all_tickers[:5]
    peer_data = []
    for p in peers:
        p_data = get_stock_data(p, period="5d")
        if not p_data.empty:
            change = (p_data['Close'].iloc[-1] / p_data['Close'].iloc[0]) - 1
            peer_data.append({"Ticker": p, "Price": p_data['Close'].iloc[-1], "5D Change": f"{change*100:.2f}%"})
    
    st.table(pd.DataFrame(peer_data))

    st.subheader("Market Heatmap")
    treemap_data = []
    
    # MARKET_SEGMENTS[market] is now a dictionary
    # Example:
    # {
    #   "Technology": ["AAPL", "MSFT"],
    #   "Finance": ["JPM", "V"]
    # }

    # Full company names for cleaner labels
    COMPANY_NAMES = {
        "NVDA": "NVIDIA",
        "AAPL": "Apple",
        "GOOGL": "Google",
        "MSFT": "Microsoft",
        "AMZN": "Amazon",
        "WMT": "Walmart",
        "JPM": "JP Morgan",
        "V": "Visa",
        "MA": "Mastercard",
        "BAC": "Bank of America",
        "GS": "Goldman Sachs"
    }
    
    def format_market_cap(value):
        if value >= 1e12:
            return f"{value/1e12:.2f}T"
        elif value >= 1e9:
            return f"{value/1e9:.2f}B"
        elif value >= 1e6:
            return f"{value/1e6:.2f}M"
        return str(value)
    
    
    for sector, companies in MARKET_SEGMENTS[market].items():
    
        for p in companies:
    
            p_data = get_stock_data(p, period="5d")
    
            if not p_data.empty:
    
                latest_price = p_data['Close'].iloc[-1]
                first_price = p_data['Close'].iloc[0]
    
                change = ((latest_price / first_price) - 1) * 100
    
                stock = yf.Ticker(p)
                market_size = stock.info.get("marketCap", 0)
    
                formatted_market_size = format_market_cap(market_size)

                company_name = COMPANY_NAMES.get(p, p)
    
                treemap_data.append({
                    "Country": market,
                    "Sector": sector,
                    "Company": company_name,
                    "FormattedMarketCap": formatted_market_size,
                    "MarketCap (millions)": round(market_size / 1_000_000, 2),
                    "Change": change
                })
    
    treemap_df = pd.DataFrame(treemap_data)
    
    if not treemap_df.empty:
    
        fig = px.treemap(
            treemap_df,
    
            # Hierarchy
            path=["Country", "Sector", "Company"],
    
            values="MarketCap (millions)",
    
            color="Change",
    
            color_continuous_scale=[
                [0.0, "#ff2e2e"],
                [0.5, "#1e1e1e"],
                [1.0, "#00ff88"]
            ],
    
            color_continuous_midpoint=0,
    
            hover_data={
                "MarketCap (millions)": ':.2f',
                "Change": ':.2f'
            },

            custom_data=["FormattedMarketCap"],
        )
    
        fig.update_traces(
            texttemplate="%{label}<br>%{customdata[0]}",
        
            textfont_size=18,
            textfont_color="white",
            textfont_family="Arial Black",
        
            hovertemplate="""
            <b>%{label}</b><br>
            Market Size: %{customdata[0]}<br>
            Change: %{color:.2f}%<br>
            <extra></extra>
            """
        )
    
        fig.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font_color="white",
    
            margin=dict(t=30, l=0, r=0, b=0),
    
            height=600,
    
            uniformtext=dict(
                minsize=14,
                mode='hide'
            )
        )
    
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
