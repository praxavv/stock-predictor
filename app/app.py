import streamlit as st
import sys
import os

# Add the project root and app directory to the python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'app'))

from core.config import APP_TITLE, APP_ICON
from components.components import render_sidebar

# Page Configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for VC-polish
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    .stMetric {
        background-color: #161A23;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #1E2430;
    }
    [data-testid="stSidebar"] {
        background-color: #11141C;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #00FFA3;
        color: black;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Render Sidebar
    render_sidebar()

    # Home Page Content
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.subheader("Next-Generation Alpha Generation & Risk Management")
    
    st.markdown("""
    Welcome to **AlphaStream**, the premier destination for institutional-grade stock market analysis. 
    Our platform leverages advanced machine learning, robust technical indicators, and comprehensive 
    backtesting engines to provide you with a competitive edge in the markets.
    
    ---
    
    ### 🚀 Getting Started
    
    Select a module from the sidebar to begin your analysis:
    
    1.  **📈 Dashboard**: Real-time signals and market sentiment overview.
    2.  **🔍 Deep Analysis**: Interactive charting with technical overlays.
    3.  **🧪 Backtester**: Strategy validation and risk metric auditing.
    
    ---
    
    ### 💎 Key Features
    - **Alpha Prediction Engine**: Powered by Random Forest classification to detect high-conviction entry points.
    - **Institutional Risk Metrics**: Evaluate strategies using Sharpe, Sortino, and Max Drawdown.
    - **Multi-Market Support**: Seamlessly transition between Indian (NSE) and US (NASDAQ/NYSE) markets.
    """)

    # High-level Market Recap (Optional - Placeholder for now)
    st.info("💡 **Pro Tip**: Check the 'Deep Analysis' page for real-time Bollinger Band breakouts.")

if __name__ == "__main__":
    main()
