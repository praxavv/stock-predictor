import sys
import os
import yfinance as yf
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "app"))
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from core.analytics.data_service import get_stock_data
from core.analytics.technical import calculate_technical_indicators, get_latest_metrics
from core.prediction.predictor import train_alpha_model, predict_signal
from components.components import render_sidebar, render_metric_cards, account_management_dialog
from core.config import MARKET_SEGMENTS, COLOR_PALETTE
from core.ai_engine import ask_ai
import core.database as db

st.set_page_config(page_title="Pranav's Lab", layout="wide")

# --- PAPER TRADING ENGINE ---
def init_paper_trading():
    if "user" not in st.session_state:
        st.session_state.user = None

    # Initialize defaults if not logged in
    if not st.session_state.user:
        if "paper_balance" not in st.session_state:
            st.session_state.paper_balance = 1000000.0
        if "paper_holdings" not in st.session_state:
            st.session_state.paper_holdings = {}
        if "paper_history" not in st.session_state:
            st.session_state.paper_history = []

    if "portfolio_history" not in st.session_state:
        st.session_state.portfolio_history = pd.DataFrame(columns=["Timestamp", "TotalValue"])

@st.cache_data(ttl=60)

def get_live_price(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        if data.empty:
            return None
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return float(data['Close'].iloc[-1])
    except:
        return None

@st.cache_data(ttl=300)
def get_batch_prices(tickers):
    if not tickers: return {}
    try:
        data = yf.download(tickers, period="1d", interval="1m", progress=False)
        prices = {}
        if isinstance(data.columns, pd.MultiIndex):
            for t in tickers:
                try:
                    prices[t] = float(data['Close'][t].iloc[-1])
                except: continue
        else:
            if len(tickers) == 1:
                prices[tickers[0]] = float(data['Close'].iloc[-1])
        return prices
    except:
        return {}

@st.cache_data(ttl=600, show_spinner="Updating Market Heatmap...")
def get_heatmap_data(all_market_tickers):
    try:
        data = yf.download(all_market_tickers, period="1mo", interval="1d", auto_adjust=True, progress=False)
        return data
    except:
        return pd.DataFrame()

def render_trading_terminal(ticker, currency_symbol):
    st.markdown("---")
    st.subheader("🛠️ Paper Trading Terminal")
    
    # Batch fetch prices for holdings
    holdings_tickers = list(st.session_state.paper_holdings.keys())
    current_prices = get_batch_prices(holdings_tickers)
    
    total_holdings_val = 0
    for h_t, details in st.session_state.paper_holdings.items():
        price = current_prices.get(h_t, details['avg_price'])
        total_holdings_val += price * details['quantity']
    
    total_val = st.session_state.paper_balance + total_holdings_val
    total_pnl = total_val - 1000000.0
    pnl_pct = (total_pnl / 1000000.0) * 100

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Cash Balance", f"{currency_symbol}{st.session_state.paper_balance:,.2f}")
    m2.metric("Portfolio Value", f"{currency_symbol}{total_val:,.2f}")
    m3.metric("Total P&L", f"{currency_symbol}{total_pnl:,.2f}", delta=f"{pnl_pct:.2f}%")
    m4.metric("Holdings", len(st.session_state.paper_holdings))

    tab_exec, tab_port = st.tabs(["🚀 Execution", "📂 My Holdings & History"])

    with tab_exec:
        col_ex, col_context = st.columns([1, 2])
        with col_ex:
            st.write("**Order Entry**")
            price = get_live_price(ticker)
            if price is not None:
                st.markdown(f"**{ticker}** @ `{currency_symbol}{price:,.2f}`")
                side = st.radio("Side", ["BUY", "SELL"], horizontal=True, label_visibility="collapsed")
                qty = st.number_input("Quantity", min_value=1, value=10, step=1)
                cost = price * qty
                
                if side == "BUY":
                    if st.button(f"Confirm BUY ({currency_symbol}{cost:,.2f})", type="primary", use_container_width=True):
                        if not st.session_state.user:
                            account_management_dialog()
                        elif st.session_state.paper_balance >= cost:
                            st.session_state.paper_balance -= cost
                            if ticker in st.session_state.paper_holdings:
                                h = st.session_state.paper_holdings[ticker]
                                h['avg_price'] = ((h['avg_price'] * h['quantity']) + cost) / (h['quantity'] + qty)
                                h['quantity'] += qty
                            else:
                                st.session_state.paper_holdings[ticker] = {"quantity": qty, "avg_price": price}
                            st.session_state.paper_history.append({"Time": datetime.now().strftime("%H:%M:%S"), "Ticker": ticker, "Type": "BUY", "Qty": qty, "Price": price})
                            
                            # Persist to DB if logged in
                            if st.session_state.user:
                                db.save_user_data(st.session_state.user, st.session_state.paper_balance, 
                                                 st.session_state.paper_holdings, st.session_state.paper_history)
                            
                            st.success(f"Bought {qty} {ticker}")
                            st.rerun()
                        else: st.error("Low Balance")
                else:
                    if st.button(f"Confirm SELL ({currency_symbol}{cost:,.2f})", type="secondary", use_container_width=True):
                        if not st.session_state.user:
                            account_management_dialog()
                        elif ticker in st.session_state.paper_holdings and st.session_state.paper_holdings[ticker]['quantity'] >= qty:
                            st.session_state.paper_balance += cost
                            st.session_state.paper_holdings[ticker]['quantity'] -= qty
                            if st.session_state.paper_holdings[ticker]['quantity'] <= 0: del st.session_state.paper_holdings[ticker]
                            st.session_state.paper_history.append({"Time": datetime.now().strftime("%H:%M:%S"), "Ticker": ticker, "Type": "SELL", "Qty": qty, "Price": price})
                            
                            # Persist to DB if logged in
                            if st.session_state.user:
                                db.save_user_data(st.session_state.user, st.session_state.paper_balance, 
                                                 st.session_state.paper_holdings, st.session_state.paper_history)
                            
                            st.success(f"Sold {qty} {ticker}")
                            st.rerun()
                        else: st.error("No Holdings")
            else: st.warning("Live price sync failed.")
        
        with col_context:
            st.write("**Recent Price Action**")
            data = get_stock_data(ticker, period="5d", interval="15m")
            if not data.empty:
                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
                fig.update_layout(template="plotly_dark", height=250, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)

    with tab_port:
        if st.session_state.paper_holdings:
            st.write("**Active Positions**")
            df_h = []
            for t, d in st.session_state.paper_holdings.items():
                cp = current_prices.get(t, d['avg_price'])
                val = cp * d['quantity']
                pnl = (cp - d['avg_price']) * d['quantity']
                df_h.append({
                    "Ticker": t, 
                    "Quantity": d['quantity'], 
                    "Avg Cost": round(d['avg_price'], 2),
                    "Market Value": round(val, 2),
                    "P&L": round(pnl, 2),
                    "Change %": f"{((cp/d['avg_price'])-1)*100:.2f}%"
                })
            st.dataframe(pd.DataFrame(df_h), use_container_width=True, hide_index=True)
        else: st.info("No active holdings.")
        
        if st.session_state.paper_history:
            st.markdown("---")
            st.write("**Trade History**")
            st.dataframe(pd.DataFrame(st.session_state.paper_history[::-1]), use_container_width=True, hide_index=True)

def main():
    init_paper_trading()
    ticker, market = render_sidebar()
    currency_symbol = "₹" if market == "INDIA" else "$"
    
    st.title("🚀 Market Intelligence Dashboard")
    st.caption(f"Real-time Alpha Generation for {ticker} ({market})")
    
    # 1. Aggressive Data Fetch & Resiliency Logic
    data = get_stock_data(ticker)
    
    # If still empty, try an aggressive 1-year pull to ensure KPIs work
    if data.empty:
        data = get_stock_data(ticker, period="1y")

    # If data is STILL empty after aggressive pull, show a professional 'Sync' state instead of a hard error
    if data.empty:
        st.warning(f"📡 {ticker} Data Stream: Synchronizing... Please verify ticker symbol or check connection.")
        return

    # Professional Market Status Header
    last_ts = data.index[-1]
    is_recent = (pd.Timestamp.now() - last_ts).days < 3 # Rough check for weekend/closed
    
    status_color = "#00FFA3" if is_recent else "#FFB800"
    status_text = "MARKET LIVE" if is_recent else "MARKET CLOSED / ARCHIVE"
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="background-color: {status_color}; width: 10px; height: 10px; border-radius: 50%;"></div>
            <span style="color: {status_color}; font-weight: bold; letter-spacing: 1px; font-size: 0.8rem;">{status_text}</span>
            <span style="color: #888; font-size: 0.8rem;">| LAST SESSION: {last_ts.strftime('%Y-%m-%d %H:%M')}</span>
        </div>
    """, unsafe_allow_html=True)

    data = calculate_technical_indicators(data)
    latest_metrics = get_latest_metrics(data)
    
    # 2. Key Metrics Row
    render_metric_cards(latest_metrics, symbol=currency_symbol)
    
    st.markdown("---")
    
    # 3. Alpha Prediction Engine
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Alpha Prediction")
        try:
            with st.spinner("Analyzing Patterns..."):
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
            st.caption(f"Confidence score based on {model_info['accuracy']*100:.1f}% historical backtest accuracy.")
        except Exception as e:
            st.info("Generating predictive signal... (Awaiting more data)")

        
    
    # 4. Market Movers (Simplified)
    st.subheader("Institutional Market Movers")
    # Flatten tickers from all sectors
    all_tickers = [t for s in MARKET_SEGMENTS[market].values() for t in s]
    peers = all_tickers[:5]
    peer_data = []
    for p in peers:
        try:
            p_data = get_stock_data(p, period="5d")
            if len(p_data) >= 2:
                latest_price = p_data['Close'].iloc[-1]
                prev_price = p_data['Close'].iloc[-2]
                change = (latest_price / prev_price) - 1
                peer_data.append({
                    "Ticker": p, 
                    f"Price ({currency_symbol})": f"{latest_price:,.2f}", 
                    "Day Change": f"{change*100:.2f}%"
                })
        except:
            continue
    
    if peer_data:
        st.table(pd.DataFrame(peer_data))
    else:
        st.caption("Market movers temporarily unavailable.")

    # 5. Paper Trading Simulator
    render_trading_terminal(ticker, currency_symbol)

    # Compact Header & Toggle Row
    st.write("")
    col_h1, col_h2 = st.columns([2, 1])
    with col_h1:
        st.markdown("#### Market Heatmap")
    with col_h2:
        size_metric = st.radio(
            "Size Heatmap By:",
            ["Market Value", "Cash value"],
            horizontal=True,
            label_visibility="collapsed"
        )

    treemap_data = []
    
    # 1. Batch fetch all market data for the heatmap to ensure session consistency
    all_market_tickers = [t for s in MARKET_SEGMENTS[market].values() for t in s]
    batch_data = get_heatmap_data(all_market_tickers)

    # Full company names for cleaner labels
    COMPANY_NAMES = {
        "NVDA": "NVIDIA", "AAPL": "Apple", "GOOGL": "Google", "MSFT": "Microsoft",
        "AMZN": "Amazon", "WMT": "Walmart", "JPM": "JP Morgan", "V": "Visa",
        "MA": "Mastercard", "BAC": "Bank of America", "GS": "Goldman Sachs"
    }
    
    def format_value(value, symbol="$"):
        if value >= 1e12: return f"{symbol}{value/1e12:.2f}T"
        elif value >= 1e9: return f"{symbol}{value/1e9:.2f}B"
        elif value >= 1e6: return f"{symbol}{value/1e6:.2f}M"
        return f"{symbol}{value:,.0f}"
    
    if not batch_data.empty:
        for sector, companies in MARKET_SEGMENTS[market].items():
            for p in companies:
                try:
                    # Extract individual ticker data from batch
                    if p in batch_data.columns.get_level_values(1):
                        p_data = batch_data.xs(p, axis=1, level=1).dropna(subset=['Close'])
                        
                        if len(p_data) >= 2:
                            latest_price = p_data['Close'].iloc[-1]
                            prev_price = p_data['Close'].iloc[-2]
                            change = ((latest_price / prev_price) - 1) * 100

                            from core.analytics.data_service import get_company_info
                            info = get_company_info(p)
                            
                            display_value = info.get("marketCap", 0) if size_metric == "Market Value" else info.get("totalCash", 0)
                            formatted_value = format_value(display_value, symbol=currency_symbol)
                            company_name = COMPANY_NAMES.get(p, info.get("longName", p))
                
                            treemap_data.append({
                                "Country": market,
                                "Sector": sector,
                                "Company": company_name,
                                "FormattedValue": formatted_value,
                                "Value (millions)": round(display_value / 1_000_000, 2),
                                "Change": change,
                                "Metric": size_metric
                            })
                except Exception as e:
                    continue
    else:
        st.info("📊 Heatmap: Awaiting next session data sync...")
    
    treemap_df = pd.DataFrame(treemap_data)
    
    if not treemap_df.empty:
    
        fig = px.treemap(
            treemap_df,
    
            # Hierarchy
            path=["Country", "Sector", "Company"],
    
            values="Value (millions)",
    
            color="Change",
    
            color_continuous_scale=[
                [0.0, "#ff2e2e"],
                [0.5, "#1e1e1e"],
                [1.0, "#00ff88"]
            ],
    
            color_continuous_midpoint=0,
    
            hover_data={
                "Value (millions)": ':.2f',
                "Change": ':.2f'
            },

            custom_data=["FormattedValue", "Metric"],
        )
    
        fig.update_traces(
            texttemplate="%{label}<br>%{customdata[0]}",
        
            textfont_size=18,
            textfont_color="white",
            textfont_family="Arial Black",
        
            hovertemplate="""
            <b>%{label}</b><br>
            %{customdata[1]}: %{customdata[0]}<br>
            Change: %{color:.2f}%<br>
            <extra></extra>
            """
        )
    
        fig.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font_color="white",
    
            margin=dict(t=2, l=0, r=0, b=0),
    
            height=500,
    
            uniformtext=dict(
                minsize=14,
                mode='hide'
            )
        )
    
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
