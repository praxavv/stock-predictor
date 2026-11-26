-- supabase_schema.sql
-- ─────────────────────────────────────────────────────────────────────────────
-- Run this once in the Supabase SQL Editor (project → SQL Editor → New query)
-- before the first deploy.
-- ─────────────────────────────────────────────────────────────────────────────

-- Users table
-- password column stores bcrypt hashes ($2b$ prefix).
-- Legacy SHA-256 hashes (64-char hex) may appear during migration;
-- they are silently upgraded to bcrypt on first login.
create table if not exists users (
    username  text             primary key,
    email     text             not null,
    password  text             not null,
    balance   double precision not null default 1000000.0
);

-- Portfolios table
-- holdings is a JSON object  { "AAPL": {"quantity": 10, "avg_price": 150.0, "date": "26 Nov 2025"}, ... }
-- history  is a JSON array   [{"Date/Time": "10:30, 26 Nov 2025", "Ticker": "AAPL", "Type": "BUY", ...}, ...]
create table if not exists portfolios (
    username  text  primary key references users (username) on delete cascade,
    holdings  jsonb not null    default '{}',
    history   jsonb not null    default '[]'
);

-- (Optional) Row Level Security
-- If you are using the anon key, enable RLS so each user can only read/write their own row.
-- With the service-role key, RLS is bypassed automatically.
--
-- alter table users     enable row level security;
-- alter table portfolios enable row level security;
--
-- create policy "Users can read their own record"
--     on users for select using (auth.uid()::text = username);
--
-- create policy "Users can update their own record"
--     on users for update using (auth.uid()::text = username);
--
-- (Repeat similar policies for portfolios.)
