import sqlite3
import hashlib
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trading_lab.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, email TEXT, password TEXT, balance REAL)''')
    # Holdings table (stored as JSON for simplicity in this prototype)
    c.execute('''CREATE TABLE IF NOT EXISTS portfolios
                 (username TEXT PRIMARY KEY, holdings TEXT, history TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_user(username, email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, email, hash_password(password), 1000000.0))
        c.execute("INSERT INTO portfolios VALUES (?, ?, ?)", (username, '{}', '[]'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

def get_user_data(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE username=?", (username,))
    balance = c.fetchone()[0]
    c.execute("SELECT holdings, history FROM portfolios WHERE username=?", (username,))
    port = c.fetchone()
    conn.close()
    return {
        "balance": balance,
        "holdings": json.loads(port[0]),
        "history": json.loads(port[1])
    }

def save_user_data(username, balance, holdings, history):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET balance=? WHERE username=?", (balance, username))
    c.execute("UPDATE portfolios SET holdings=?, history=? WHERE username=?", 
              (json.dumps(holdings), json.dumps(history), username))
    conn.commit()
    conn.close()

init_db()
