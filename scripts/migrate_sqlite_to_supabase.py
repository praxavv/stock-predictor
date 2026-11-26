#!/usr/bin/env python3
"""
scripts/migrate_sqlite_to_supabase.py
─────────────────────────────────────────────────────────────────────────────
One-shot data migration: copies all users and portfolios from the local
SQLite database into Supabase PostgreSQL.

Run this LOCALLY (not on Streamlit Cloud) ONCE before the first deploy:

    # Option A — interactive (prompts for credentials)
    python scripts/migrate_sqlite_to_supabase.py

    # Option B — via environment variables
    SUPABASE_URL=https://xxx.supabase.co \\
    SUPABASE_KEY=your-service-role-key   \\
    python scripts/migrate_sqlite_to_supabase.py

Pre-requisites
──────────────
1. Run `scripts/supabase_schema.sql` in the Supabase SQL Editor first.
2. Install dependencies:  pip install supabase bcrypt
3. The SQLite DB file must exist at  core/trading_lab.db

Notes
─────
• Existing usernames in Supabase are SKIPPED (safe to re-run).
• SHA-256 password hashes are migrated as-is; they will be silently upgraded
  to bcrypt the first time each user logs in (handled by core/database.py).
• Balance, holdings, and history are migrated verbatim.
─────────────────────────────────────────────────────────────────────────────
"""

import json
import os
import sqlite3
import sys

# ── Path setup ──────────────────────────────────────────────────────────────
ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_PATH = os.path.join(ROOT_DIR, "core", "trading_lab.db")

sys.path.insert(0, ROOT_DIR)


# ── Credentials ─────────────────────────────────────────────────────────────
def _get_credentials() -> tuple[str, str]:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()

    if not url:
        url = input("Supabase project URL (e.g. https://abc.supabase.co): ").strip()
    if not key:
        key = input("Supabase service-role key: ").strip()

    if not url or not key:
        print("ERROR: Both URL and key are required.")
        sys.exit(1)

    return url, key


# ── Migration ────────────────────────────────────────────────────────────────
def migrate() -> None:
    from supabase import create_client

    if not os.path.exists(SQLITE_PATH):
        print(f"SQLite DB not found at {SQLITE_PATH!r}.")
        print("Nothing to migrate — the cloud database is already the source of truth.")
        return

    supabase_url, supabase_key = _get_credentials()
    client = create_client(supabase_url, supabase_key)

    conn    = sqlite3.connect(SQLITE_PATH)
    users   = conn.execute(
        "SELECT username, email, password, balance FROM users"
    ).fetchall()

    print(f"\nFound {len(users)} user(s) in SQLite.")
    print("─" * 60)

    migrated = 0
    skipped  = 0
    errors   = 0

    for username, email, password_hash, balance in users:
        # ── Check if already in Supabase ──────────────────────────────────
        try:
            existing = (
                client.table("users")
                .select("username")
                .eq("username", username)
                .execute()
            )
        except Exception as exc:
            print(f"  ✗  {username!r}: could not check existence — {exc}")
            errors += 1
            continue

        if existing.data:
            print(f"  ↷  {username!r}: already in Supabase, skipping")
            skipped += 1
            continue

        # ── Migrate user row ──────────────────────────────────────────────
        try:
            client.table("users").insert({
                "username": username,
                "email":    email,
                "password": password_hash,  # SHA-256 → bcrypt upgrade on first login
                "balance":  float(balance),
            }).execute()
        except Exception as exc:
            print(f"  ✗  {username!r}: failed to insert user — {exc}")
            errors += 1
            continue

        # ── Migrate portfolio row ─────────────────────────────────────────
        try:
            port = conn.execute(
                "SELECT holdings, history FROM portfolios WHERE username=?",
                (username,),
            ).fetchone()

            holdings = json.loads(port[0]) if port and port[0] else {}
            history  = json.loads(port[1]) if port and port[1] else []

            client.table("portfolios").insert({
                "username": username,
                "holdings": holdings,
                "history":  history,
            }).execute()

            print(f"  ✓  {username!r}: migrated (balance={balance:.2f}, "
                  f"holdings={len(holdings)}, trades={len(history)})")
            migrated += 1

        except Exception as exc:
            print(f"  ✗  {username!r}: user inserted but portfolio failed — {exc}")
            errors += 1

    conn.close()

    print("─" * 60)
    print(f"Done.  ✓ {migrated} migrated  |  ↷ {skipped} skipped  |  ✗ {errors} errors")

    if errors:
        print("\nSome rows had errors. Fix them manually in the Supabase table editor.")

    print(
        "\nReminder: SHA-256 password hashes will be upgraded to bcrypt "
        "automatically the first time each user logs in."
    )


if __name__ == "__main__":
    migrate()
