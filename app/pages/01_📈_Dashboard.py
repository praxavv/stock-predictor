import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "app"))
import streamlit as st
import pandas as pd
from core.analytics.data_service import get_stock_data
from core.analytics.technical import calculate_technical_indicators, get_latest_metrics
from core.prediction.predictor import train_alpha_model, predict_signal
from components.components import render_sidebar, render_metric_cards
from core.config import MARKET_SEGMENTS, COLOR_PALETTE

st.set_page_config(page_title="AlphaStream | Dashboard", layout="wide")

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
        
    with col2:
        st.subheader("Market Sentiment & Signals")
        
        # Technical Signal Logic
        signals = []
        if latest_metrics['rsi'] > 70: signals.append(("RSI Overbought", "BEARISH"))
        elif latest_metrics['rsi'] < 30: signals.append(("RSI Oversold", "BULLISH"))
        
        if latest_metrics['price'] > latest_metrics['ma50'] > latest_metrics['ma200'] if 'ma200' in latest_metrics else True:
            signals.append(("Golden Cross / Up-trend", "BULLISH"))
            
        # Display signals in a professional table
        if signals:
            for sig, sentiment in signals:
                st.write(f"{'✅' if sentiment == 'BULLISH' else '⚠️'} **{sig}**")
        else:
            st.write("Neutral market signals.")

    st.markdown("---")
    
    # 4. Market Movers (Simplified)
    st.subheader("Institutional Market Movers")
    peers = MARKET_SEGMENTS[market][:5]
    peer_data = []
    for p in peers:
        p_data = get_stock_data(p, period="5d")
        if not p_data.empty:
            change = (p_data['Close'].iloc[-1] / p_data['Close'].iloc[0]) - 1
            peer_data.append({"Ticker": p, "Price": p_data['Close'].iloc[-1], "5D Change": f"{change*100:.2f}%"})
    
    st.table(pd.DataFrame(peer_data))

if __name__ == "__main__":
    main()
