"""
core/database.py
─────────────────────────────────────────────────────────────────────────────
Persistence layer backed by Supabase PostgreSQL.

Required Streamlit secrets (`.streamlit/secrets.toml`):

    [supabase]
    url = "https://<project>.supabase.co"
    key = "<service-role-or-anon-key>"

Required Supabase tables — run `scripts/supabase_schema.sql` once in the
Supabase SQL editor before first use.
─────────────────────────────────────────────────────────────────────────────
"""

import hashlib
import bcrypt
import streamlit as st
from supabase import create_client, Client


# ─────────────────────────────────────────────────────────────────────────────
# Client — cached for the lifetime of the server process
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _get_client() -> Client:
    """Return a cached Supabase client. Reads credentials from st.secrets."""
    url: str = st.secrets["supabase"]["url"]
    key: str = st.secrets["supabase"]["key"]
    return create_client(url, key)


# ─────────────────────────────────────────────────────────────────────────────
# Public API shim — init_db() is a no-op; tables live in Supabase.
# ─────────────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """No-op. Tables are managed in Supabase (see scripts/supabase_schema.sql)."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Password helpers
# ─────────────────────────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt. Returns a str-encoded hash."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against a stored hash.

    Supports:
      • bcrypt  ($2b$, $2a$, $2y$ prefixes)  — the current standard
      • SHA-256 (64-char hex)                 — legacy, migrated on first login
    """
    if stored_hash.startswith(("$2b$", "$2a$", "$2y$")):
        try:
            return bcrypt.checkpw(password.encode(), stored_hash.encode())
        except Exception:
            return False
    # Legacy SHA-256 fallback (used only during migration window)
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash


def _upgrade_to_bcrypt(username: str, password: str, stored_hash: str) -> None:
    """
    Silently re-hash a legacy SHA-256 password to bcrypt on successful login.
    Non-critical — a failure here is logged but does not break auth.
    """
    if stored_hash.startswith(("$2b$", "$2a$", "$2y$")):
        return  # Already bcrypt; nothing to do

    new_hash = _hash_password(password)
    try:
        _get_client().table("users") \
            .update({"password": new_hash}) \
            .eq("username", username) \
            .execute()
    except Exception as exc:
        # Non-fatal — user is logged in; hash upgrade retried on next login
        st.warning(f"Password upgrade deferred: {exc}", icon="⚠️")


# ─────────────────────────────────────────────────────────────────────────────
# Public database functions (same signatures as the old SQLite version)
# ─────────────────────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password: str) -> bool:
    """
    Register a new user.

    Returns True on success, False if the username already exists or on error.
    """
    client = _get_client()
    try:
        # Guard against duplicate usernames (Supabase PK would also catch this,
        # but checking first gives us a cleaner error path).
        existing = (
            client.table("users")
            .select("username")
            .eq("username", username)
            .execute()
        )
        if existing.data:
            return False

        client.table("users").insert({
            "username": username,
            "email":    email,
            "password": _hash_password(password),
            "balance":  1_000_000.0,
        }).execute()

        client.table("portfolios").insert({
            "username": username,
            "holdings": {},
            "history":  [],
        }).execute()

        return True

    except Exception:
        return False


def authenticate_user(username: str, password: str) -> bool:
    """
    Verify credentials. Silently upgrades legacy SHA-256 hashes to bcrypt
    on the first successful login.

    Returns True on success, False otherwise.
    """
    client = _get_client()
    try:
        result = (
            client.table("users")
            .select("password")
            .eq("username", username)
            .execute()
        )
        if not result.data:
            return False

        stored_hash: str = result.data[0]["password"]

        if _verify_password(password, stored_hash):
            _upgrade_to_bcrypt(username, password, stored_hash)
            return True

        return False

    except Exception:
        return False


def get_user_data(username: str) -> dict | None:
    """
    Fetch balance, holdings, and trade history for a user.

    Returns a dict  ``{"balance": float, "holdings": dict, "history": list}``
    or None if the user does not exist.
    """
    client = _get_client()
    try:
        user_res = (
            client.table("users")
            .select("balance")
            .eq("username", username)
            .execute()
        )
        if not user_res.data:
            return None

        balance = float(user_res.data[0]["balance"])

        port_res = (
            client.table("portfolios")
            .select("holdings, history")
            .eq("username", username)
            .execute()
        )
        if not port_res.data:
            return {"balance": balance, "holdings": {}, "history": []}

        port     = port_res.data[0]
        holdings = port["holdings"] if isinstance(port["holdings"], dict) else {}
        history  = port["history"]  if isinstance(port["history"],  list) else []

        return {"balance": balance, "holdings": holdings, "history": history}

    except Exception:
        return None


def save_user_data(
    username: str,
    balance:  float,
    holdings: dict,
    history:  list,
) -> None:
    """
    Persist balance, holdings, and trade history for a user.

    Supabase's JSONB columns accept Python dicts/lists directly —
    no manual json.dumps required.
    """
    client = _get_client()
    try:
        client.table("users") \
            .update({"balance": balance}) \
            .eq("username", username) \
            .execute()

        client.table("portfolios") \
            .update({"holdings": holdings, "history": history}) \
            .eq("username", username) \
            .execute()

    except Exception:
        pass  # Non-fatal; will retry on the next trade action


# Legacy call at module level kept for backward compatibility —
# now a no-op but won't break any import that relied on it.
init_db()
