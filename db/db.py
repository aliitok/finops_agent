import sqlite3
import json

conn = sqlite3.connect("cost.db", check_same_thread=False)

def init_db():
    conn.execute("""
    CREATE TABLE IF NOT EXISTS monthly_cost (
        account_id TEXT,
        total_cost REAL,
        top_services TEXT,
        updated_at TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS daily_cost (
        account_id TEXT,
        data TEXT,
        updated_at TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS ta_summary (
        account_id TEXT,
        data TEXT,
        updated_at TEXT
    )
    """)

def save_monthly(account_id, total_cost, top_services):
    conn.execute(
        "DELETE FROM monthly_cost WHERE account_id=?",
        (account_id,)
    )

    conn.execute(
        "INSERT INTO monthly_cost VALUES (?, ?, ?, datetime('now'))",
        (account_id, total_cost, json.dumps(top_services))
    )

    conn.commit()

def save_daily(account_id, data):
    conn.execute(
        "DELETE FROM daily_cost WHERE account_id=?",
        (account_id,)
    )

    conn.execute(
        "INSERT INTO daily_cost VALUES (?, ?, datetime('now'))",
        (account_id, json.dumps(data))
    )

    conn.commit()


def save_ta_summary(account_id, data):
    """Save a Trusted Advisor summary (JSON serializable) for an account."""
    conn.execute(
        "DELETE FROM ta_summary WHERE account_id=?",
        (account_id,)
    )

    conn.execute(
        "INSERT INTO ta_summary VALUES (?, ?, datetime('now'))",
        (account_id, json.dumps(data))
    )

    conn.commit()

def get_monthly(account_id):
    cur = conn.execute(
        "SELECT total_cost, top_services FROM monthly_cost WHERE account_id=?",
        (account_id,)
    )
    row = cur.fetchone()
    if not row:
        return None

    return {
        "total_cost": row[0],
        "top_services": json.loads(row[1])
    }

def get_daily(account_id):
    cur = conn.execute(
        "SELECT data FROM daily_cost WHERE account_id=?",
        (account_id,)
    )
    row = cur.fetchone()
    return json.loads(row[0]) if row else None


def get_ta_summary(account_id):
    cur = conn.execute(
        "SELECT data FROM ta_summary WHERE account_id=?",
        (account_id,)
    )
    row = cur.fetchone()
    return json.loads(row[0]) if row else None