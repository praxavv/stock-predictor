"""
app/components/components.py
─────────────────────────────────────────────────────────────────────────────
Shared UI components: sidebar, account management, metric cards, etc.

Authentication design
─────────────────────
• Login dialog writes a signed HMAC token to `st.query_params["session"]`
  instead of the raw username. The token encodes the username + an expiry
  timestamp and is signed with a secret key from Streamlit secrets:

      [session]
      secret_key = "<random 32+ char string>"

• On every page load, `render_account_section` validates the token before
  trusting it. A missing, expired, or tampered token is silently cleared.
  This eliminates the previous ?user=<username> account-takeover vector.
─────────────────────────────────────────────────────────────────────────────
"""

import hashlib
import hmac
import time

import streamlit as st
import pandas as pd
from typing import Dict

from core.config import COLOR_PALETTE
import core.database as db
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# Session-token helpers
# ─────────────────────────────────────────────────────────────────────────────

_SESSION_PARAM    = "session"
_SESSION_TTL_SECS = 7 * 24 * 3600  # 7-day rolling session


def _session_secret() -> str:
    """Return the HMAC signing key from Streamlit secrets."""
    try:
        return st.secrets["session"]["secret_key"]
    except Exception:
        # Only reached in a local dev environment that hasn't set secrets yet.
        # Production deploys on Streamlit Cloud MUST have this secret configured.
        return "dev-only-insecure-fallback-change-before-deploy"


def _make_session_token(username: str) -> str:
    """
    Build a signed, time-limited session token.

    Format:  ``<username>|<expiry_epoch>|<hmac_sha256>``

    The ``|`` separator is safe because Streamlit usernames cannot contain it.
    """
    expiry  = int(time.time()) + _SESSION_TTL_SECS
    payload = f"{username}|{expiry}"
    sig     = hmac.new(
        _session_secret().encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload}|{sig}"


def _verify_session_token(token: str) -> str | None:
    """
    Validate a session token.

    Returns the authenticated username on success, None on any failure
    (expired, tampered, malformed).
    """
    try:
        parts = token.split("|")
        if len(parts) != 3:
            return None
        username, expiry_str, sig = parts

        # 1. Check expiry
        if int(time.time()) > int(expiry_str):
            return None  # Token expired

        # 2. Verify HMAC signature (constant-time comparison prevents timing attacks)
        payload  = f"{username}|{expiry_str}"
        expected = hmac.new(
            _session_secret().encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None  # Signature mismatch — token tampered

        return username

    except Exception:
        return None


def _clear_session_token() -> None:
    """Remove the session token from query params without raising."""
    try:
        del st.query_params[_SESSION_PARAM]
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Account management dialog
# ─────────────────────────────────────────────────────────────────────────────

@st.dialog("🔐 Account Management")
def account_management_dialog():
    mode     = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
    username = st.text_input("Username")
    email    = None
    if mode == "Sign Up":
        email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Confirm", use_container_width=True):
        if not username or not password:
            st.error("Please fill all fields")
            return

        if mode == "Sign Up":
            if not email:
                st.error("Email is required for signup")
                return
            if db.create_user(username, email, password):
                st.success("Account created! Please switch to Login.")
            else:
                st.error("Username already exists.")
        else:
            if db.authenticate_user(username, password):
                data = db.get_user_data(username)
                # Populate session state
                st.session_state.user           = username
                st.session_state.paper_balance  = data["balance"]
                st.session_state.paper_holdings = data["holdings"]
                st.session_state.paper_history  = data["history"]
                # Write a signed token to query params for cross-tab / cross-page persistence.
                # The token cannot be forged without the secret key.
                st.query_params[_SESSION_PARAM] = _make_session_token(username)
                st.success("Welcome back!")
                st.rerun()
            else:
                st.error("Invalid credentials.")


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar account section
# ─────────────────────────────────────────────────────────────────────────────

def render_account_section():
    if "user" not in st.session_state:
        st.session_state.user = None

    # ── Auto-login from signed session token ──────────────────────────────────
    # Only trust a token; never trust a raw username in the URL.
    if not st.session_state.user and _SESSION_PARAM in st.query_params:
        token            = st.query_params[_SESSION_PARAM]
        verified_username = _verify_session_token(token)

        if verified_username:
            data = db.get_user_data(verified_username)
            if data:
                st.session_state.user           = verified_username
                st.session_state.paper_balance  = data["balance"]
                st.session_state.paper_holdings = data["holdings"]
                st.session_state.paper_history  = data["history"]
                st.rerun()
            else:
                # Token valid but user not found — stale token; clear it
                _clear_session_token()
        else:
            # Token expired or tampered — clear silently
            _clear_session_token()

    # ── Render logged-in / logged-out UI ─────────────────────────────────────
    if st.session_state.user:
        st.success(f"Logged in: **{st.session_state.user}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.user           = None
            st.session_state.paper_balance  = 1_000_000.0
            st.session_state.paper_holdings = {}
            st.session_state.paper_history  = []
            st.query_params.clear()
            st.rerun()
    else:
        if st.button("🔐 Open Account / Login", use_container_width=True, type="primary"):
            account_management_dialog()


# ─────────────────────────────────────────────────────────────────────────────
# Metric cards
# ─────────────────────────────────────────────────────────────────────────────

def render_metric_cards(metrics: Dict, symbol: str = "$"):
    """Render professional KPI cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Latest Price", f"{symbol}{metrics['price']:,.2f}")

    with col2:
        color = "normal" if metrics["change"] >= 0 else "inverse"
        st.metric(
            "Day Change",
            f"{metrics['change'] * 100:.2f}%",
            delta=f"{metrics['change'] * 100:.2f}%",
            delta_color=color,
        )

    with col3:
        st.metric("RSI (14)", f"{metrics['rsi']:.1f}")

    with col4:
        st.metric(
            "MA20 Status",
            "Above" if metrics["price"] > metrics["ma20"] else "Below",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar():
    """Consistent sidebar with branding and ticker selection."""

    from core.config import MARKET_SEGMENTS

    # Initialize defaults only once
    if "market" not in st.session_state:
        st.session_state.market = "USA"

    if "ticker" not in st.session_state:
        first_market   = MARKET_SEGMENTS["USA"]
        all_usa_tickers = [t for sector in first_market.values() for t in sector]
        st.session_state.ticker = all_usa_tickers[0]

    with st.sidebar:
        # 1. AUTH AT THE VERY TOP
        render_account_section()

        # 2. MARKET SELECTBOX
        market_options  = list(MARKET_SEGMENTS.keys())
        selected_market = st.selectbox(
            "Market Segment",
            market_options,
            index=market_options.index(st.session_state.market),
        )
        st.session_state.market = selected_market

        # 3. TICKERS FOR MARKET (flattened)
        market_data = MARKET_SEGMENTS[selected_market]
        tickers     = [t for sector in market_data.values() for t in sector]

        if st.session_state.ticker not in tickers:
            st.session_state.ticker = tickers[0]

        selected_ticker = st.selectbox(
            "Select Ticker",
            tickers,
            index=tickers.index(st.session_state.ticker),
        )
        st.session_state.ticker = selected_ticker

        st.info(
            "Pranav's Analysis Lab uses real-time market data "
            "to generate analytical insights and trading signals."
        )

    return st.session_state.ticker, st.session_state.market


# ─────────────────────────────────────────────────────────────────────────────
# Backtest report
# ─────────────────────────────────────────────────────────────────────────────

def render_backtest_report(metrics: Dict):
    """Formatted report for strategy backtesting."""
    st.subheader("Performance Analytics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Return",      f"{metrics['Total Return'] * 100:.2f}%")
    col2.metric("Sharpe Ratio",      f"{metrics['Sharpe Ratio']:.2f}")
    col3.metric("Win Rate",          f"{metrics['Win Rate'] * 100:.2f}%")

    col4, col5, col6 = st.columns(3)
    col4.metric("Benchmark Return",  f"{metrics['Benchmark Return'] * 100:.2f}%")
    col5.metric("Max Drawdown",      f"{metrics['Max Drawdown'] * 100:.2f}%")
    col6.metric("Annualized Vol",    f"{metrics['Volatility'] * 100:.2f}%")
