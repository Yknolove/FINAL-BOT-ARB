import sqlite3
from datetime import datetime

DB_PATH = 'arbitpro.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        referrer INTEGER,
        trial_start TEXT
    );
    CREATE TABLE IF NOT EXISTS settings (
        user_id INTEGER PRIMARY KEY,
        buy_rate REAL,
        sell_rate REAL
    );
    CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        buy_price REAL,
        sell_price REAL,
        profit REAL,
        timestamp TEXT
    );
    """)
    conn.commit()
    conn.close()

def ensure_user(user_id, referrer=None):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users(user_id,referrer,trial_start) VALUES(?,?,?)",
                    (user_id, referrer, datetime.utcnow().isoformat()))
        conn.commit()
    conn.close()

def set_rates(user_id, buy, sell):
    conn= get_conn(); cur= conn.cursor()
    cur.execute("REPLACE INTO settings(user_id,buy_rate,sell_rate) VALUES(?,?,?)",
                (user_id,buy,sell))
    conn.commit(); conn.close()

def get_rates(user_id):
    conn= get_conn(); cur= conn.cursor()
    cur.execute("SELECT buy_rate,sell_rate FROM settings WHERE user_id=?", (user_id,))
    row= cur.fetchone(); conn.close()
    return (row['buy_rate'],row['sell_rate']) if row else (None,None)

def add_deal(user_id, amt, buy, sell, profit):
    conn=get_conn(); cur= conn.cursor()
    cur.execute(
        "INSERT INTO deals(user_id,amount,buy_price,sell_price,profit,timestamp) VALUES(?,?,?,?,?,?)",
        (user_id,amt,buy,sell,profit,datetime.utcnow().isoformat())
    )
    conn.commit(); conn.close()

def get_history(user_id):
    conn=get_conn(); cur= conn.cursor()
    cur.execute("SELECT * FROM deals WHERE user_id=? ORDER BY timestamp DESC LIMIT 20", (user_id,))
    rows= cur.fetchall(); conn.close()
    return rows

def get_top_deals():
    conn=get_conn(); cur= conn.cursor()
    today = datetime.utcnow().date().isoformat() + '%'
    cur.execute(
        "SELECT * FROM deals WHERE timestamp LIKE ? ORDER BY profit DESC LIMIT 10", (today,)
    )
    rows= cur.fetchall(); conn.close()
    return rows
