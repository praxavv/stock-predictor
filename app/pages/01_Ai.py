import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "app"))

import streamlit as st

from core.analytics.data_service import get_stock_data
from core.analytics.technical import (
    calculate_technical_indicators,
    get_latest_metrics
)
from core.prediction.predictor import (
    train_alpha_model,
    predict_signal
)
from components.components import render_sidebar
from core.ai_engine import ask_ai
from core.ai.rag_service import refresh_news, get_ai_summary


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Neurex AI",
    layout="wide"
)


# ==========================================
# SIDEBAR
# ==========================================

ticker, market = render_sidebar()


# ==========================================
# HEADER
# ==========================================

st.title("AI Report by Neurex")
st.caption(f"Synthesized analysis for {ticker}")


# ==========================================
# LOAD MARKET DATA
# ==========================================

data = get_stock_data(ticker)

if data.empty:
    st.error(
        f"Could not load market data for {ticker}. "
        "AI analysis requires historical price feeds."
    )
    st.stop()


# ==========================================
# MAIN AI PIPELINE
# ==========================================

with st.spinner("Analyzing markets..."):

    # Technical analysis
    data = calculate_technical_indicators(data)
    latest_metrics = get_latest_metrics(data)

    # Prediction model
    model, model_info = train_alpha_model(data)
    prediction = predict_signal(model, data)

    # Market news summary
    market_summary = get_ai_summary()

    # AI Context
    ai_context = {
        "ticker": ticker,
        "market": market,
        "latest_price": round(latest_metrics["price"], 2),
        "rsi": round(latest_metrics["rsi"], 2),
        "ma50": round(latest_metrics["ma50"], 2),
        "signal": prediction["signal"],
        "confidence": round(prediction["confidence"], 2),
        "news_summary": market_summary
    }

    # Generate AI Report
    ai_report = ask_ai(ai_context)


# ==========================================
# OUTPUT DISPLAY
# ==========================================

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🌐 Market Summary")
    st.info(market_summary)
    if st.button("🔄 Refresh Market News"):
        with st.spinner("Updating news..."):
            refresh_news()
            st.rerun()

with col2:
    st.subheader(f"🎯 {ticker} Insights")
    if "Error" in ai_report:
        st.error(ai_report)
    else:
        st.success(ai_report)
    
    # Simple data table for the "info about specific stock" part
    st.write(f"**Current Price:** ${latest_metrics['price']:.2f}")
    st.write(f"**Signal:** {prediction['signal'].upper()} ({prediction['confidence']:.1%})")
    st.write(f"**Technical RSI:** {latest_metrics['rsi']:.2f}")
    st.write(f"**Moving Average (50d):** ${latest_metrics['ma50']:.2f}")

st.divider()
st.caption(f"Powered by Neurex AI | Model: gemma3:270m | Accuracy: {model_info['accuracy']:.1%}")
