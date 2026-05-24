import sys
import os
import yfinance as yf
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if os.path.join(root_dir, "app") not in sys.path:
    sys.path.insert(0, os.path.join(root_dir, "app"))
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from core.analytics.data_service import get_stock_data, get_company_info
from core.analytics.technical import calculate_technical_indicators, get_latest_metrics
from core.prediction.predictor import train_alpha_model, predict_signal
from components.components import render_sidebar, render_metric_cards, account_management_dialog
from core.config import MARKET_SEGMENTS, COLOR_PALETTE, SECTOR_ORDER
from core.ai_engine import ask_ai
import core.database as db

st.set_page_config(page_title="Pranav's Lab", layout="wide")

# --- PAPER TRADING ENGINE ---
def init_paper_trading():
    if "user" not in st.session_state:
        st.session_state.user = None

def initialize_user_session():
    # Create session defaults only once
    if "user" not in st.session_state:
        st.session_state.user = None

    if "paper_balance" not in st.session_state:
        st.session_state.paper_balance = 1000000.0

    if "paper_holdings" not in st.session_state:
        st.session_state.paper_holdings = {}

    if "paper_history" not in st.session_state:
        st.session_state.paper_history = []       

    # If logged in, ALWAYS reload latest data from DB
    if st.session_state.user:
        data = db.get_user_data(st.session_state.user)

        if data:
            st.session_state.paper_balance = data["balance"]
            st.session_state.paper_holdings = data["holdings"]
            st.session_state.paper_history = data["history"]

initialize_user_session()             


def login_user(username, password):
    if db.authenticate_user(username, password):

        # Save logged-in user
        st.session_state.user = username

        # Load account data
        data = db.get_user_data(username)

        if data:
            st.session_state.paper_balance = data["balance"]
            st.session_state.paper_holdings = data["holdings"]
            st.session_state.paper_history = data["history"]

        return True

    return False


def logout_user():
    st.session_state.user = None
    st.session_state.paper_balance = 1000000.0
    st.session_state.paper_holdings = {}
    st.session_state.paper_history = {}

    # Migration/Normalization of history data
    if "paper_history" in st.session_state and st.session_state.paper_history:
        cleaned_history = []
        for entry in st.session_state.paper_history:
            new_entry = entry.copy()
            # Rename "Time" to "Date/Time" if it exists
            if "Time" in new_entry and "Date/Time" not in new_entry:
                new_entry["Date/Time"] = new_entry.pop("Time")
            
            # Remove seconds if present in "Date/Time"
            if "Date/Time" in new_entry:
                dt_str = str(new_entry["Date/Time"])
                if ":" in dt_str and len(dt_str.split(":")) > 2: # Has HH:MM:SS
                    parts = dt_str.split(":")
                    new_entry["Date/Time"] = f"{parts[0]}:{parts[1]}"
                    # If it was just time, append a placeholder date since we don't know it
                    if "," not in dt_str:
                        new_entry["Date/Time"] += ", (Prev Trade)"
            
            cleaned_history.append(new_entry)
        st.session_state.paper_history = cleaned_history

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
    st.subheader(" Trading Terminal")
    
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
                                h['date'] = datetime.now().strftime("%d %b %Y")
                            else:
                                st.session_state.paper_holdings[ticker] = {"quantity": qty, "avg_price": price, "date": datetime.now().strftime("%d %b %Y")}
                            st.session_state.paper_history.append({"Date/Time": datetime.now().strftime("%H:%M, %d %b %Y"), "Ticker": ticker, "Type": "BUY", "Qty": qty, "Price": price})
                            
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
                            st.session_state.paper_history.append({"Date/Time": datetime.now().strftime("%H:%M, %d %b %Y"), "Ticker": ticker, "Type": "SELL", "Qty": qty, "Price": price})
                            
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
    currency_symbol = "₹" if market == "INDIA" or ticker.endswith((".NS", ".BO")) else "$"
    
    st.title("🚀 Market Intelligence Dashboard")
    st.caption(f"Real-time Alpha Generation for {ticker} ({market})")
    
    data = get_stock_data(ticker)
    if data.empty:
        data = get_stock_data(ticker, period="1y")
    if data.empty:
        st.warning(f"📡 {ticker} Data Stream: Synchronizing...")
        return

    last_ts = data.index[-1]
    now = pd.Timestamp.now(tz=last_ts.tzinfo) if last_ts.tzinfo else pd.Timestamp.now()
    is_recent = (now - last_ts).days < 3
    
    status_color = "#00FFA3" if is_recent else "#FFB800"
    status_text = "MARKET LIVE" if is_recent else "MARKET CLOSED / ARCHIVE"
    
    if is_recent:
        st.status("MARKET LIVE", state="complete")
    else:
        st.warning(f"MARKET CLOSED | LAST SESSION: {last_ts.strftime('%Y-%m-%d %H:%M')}")

    data = calculate_technical_indicators(data)
    latest_metrics = get_latest_metrics(data)
    render_metric_cards(latest_metrics, symbol=currency_symbol)
    
    st.markdown("---")
    
    st.subheader("Alpha Prediction")
    
    try:
        with st.spinner("Analyzing Patterns..."):
            model, model_info = train_alpha_model(data)
            prediction = predict_signal(model, data)
    
        color = "green" if prediction['signal'] == 'BULLISH' else "red"
    
        st.markdown(
            f"""
            ### :{color}[{prediction['signal']}]
            **Confidence:** {prediction['confidence']:.1%}
    
            Confidence score based on {model_info['accuracy']*100:.1f}% historical backtest accuracy.
            """
        )
    
    except:
        st.info("Generating predictive signal... (Awaiting more data)")

    st.subheader("Institutional Market Movers")
    
    movers_tickers = []
    for sector_list in MARKET_SEGMENTS[market].values():
        if sector_list: movers_tickers.append(sector_list[0])
    
    peer_data = []
    if movers_tickers:
        movers_data = get_heatmap_data(movers_tickers)
        for p in movers_tickers:
            try:
                if p in movers_data.columns.get_level_values(1):
                    p_ts = movers_data.xs(p, axis=1, level=1).dropna()
                    if len(p_ts) >= 2:
                        lp = p_ts['Close'].iloc[-1]
                        pp = p_ts['Close'].iloc[-2]
                        chg = (lp / pp) - 1
                        info = get_company_info(p)
                        peer_data.append({
                            "Ticker": p, 
                            "Company": info.get("longName", p),
                            f"Price ({currency_symbol})": f"{lp:,.2f}", 
                            "Day Change": f"{chg*100:.2f}%"
                        })
            except: continue
    
    if peer_data:
        st.table(pd.DataFrame(peer_data))
    else:
        st.caption("Market movers temporarily unavailable.")

    render_trading_terminal(ticker, currency_symbol)

    # --- HEATMAP SECTION ---
    st.write("")
    col_title, col_toggle = st.columns([3, 1])
    with col_title:
        st.markdown("#### 📊 11 sectors Heatmap")
    with col_toggle:
        size_metric = st.selectbox("Size By:", ["Market Cap", "Cash Value"], label_visibility="collapsed")
    
    all_market_tickers = [t for s in MARKET_SEGMENTS[market].values() for t in s]
    batch_data = get_heatmap_data(all_market_tickers)

    if not batch_data.empty:
        treemap_records = []
        sorted_sectors = sorted(MARKET_SEGMENTS[market].keys(), 
                               key=lambda x: SECTOR_ORDER.index(x) if x in SECTOR_ORDER else 99)
        
        for sector in sorted_sectors:
            companies = MARKET_SEGMENTS[market][sector]
            for t in companies:
                try:
                    if t in batch_data.columns.get_level_values(1):
                        p_data = batch_data.xs(t, axis=1, level=1).dropna()
                        if len(p_data) < 2: continue
                        
                        change = ((p_data['Close'].iloc[-1] / p_data['Close'].iloc[-2]) - 1) * 100
                        info = get_company_info(t)
                        
                        val_key = "marketCap" if size_metric == "Market Cap" else "totalCash"
                        raw_val = info.get(val_key, 0)
                        if raw_val <= 0: continue
                        
                        label_val = f"{currency_symbol}{raw_val/1e9:.1f}B" if raw_val >= 1e9 else f"{currency_symbol}{raw_val/1e6:.1f}M"
                        display_name = info.get("shortName", t.split('.')[0])

                        treemap_records.append({
                            "Sector": sector,
                            "Company": display_name,
                            "Value": raw_val,
                            "Label": label_val,
                            "Change": change
                        })
                except: continue
        
        df_map = pd.DataFrame(treemap_records)
        if not df_map.empty:
            fig = px.treemap(
                df_map,
                path=["Sector", "Company"],
                values="Value",
                color="Change",
                color_continuous_scale="RdYlGn",
                color_continuous_midpoint=0,
                custom_data=["Label", "Change"],
                height=550
            )
            fig.update_traces(
                texttemplate="<b>%{label}</b>", 
                hovertemplate="<b>%{label}</b><br>Value: %{customdata[0]}<br>Change: %{customdata[1]:.2f}%",
                marker=dict(line=dict(width=1, color='#1E2430')),
                tiling=dict(pad=3)
            )
            
            fig.update_layout(
                margin=dict(t=10, l=10, r=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                uniformtext=dict(minsize=10, mode='hide')
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Heatmap: Awaiting next session data sync...")

if __name__ == "__main__":
    main()
