import sqlite3
import json

conn = sqlite3.connect("cost.db", check_same_thread=False)

def init_db():
    conn.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_id TEXT PRIMARY KEY,
        name TEXT,
        role_arn TEXT,
        environment TEXT,
        updated_at TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS monthly_cost (
        account_id TEXT,
        total_cost REAL,
        top_services TEXT,
        environment TEXT,
        updated_at TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS daily_cost (
        account_id TEXT,
        data TEXT,
        environment TEXT,
        updated_at TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS ta_summary (
        account_id TEXT,
        data TEXT,
        environment TEXT,
        updated_at TEXT
    )
    """)
    
    # Run migrations for existing tables
    _migrate_add_environment_column("monthly_cost")
    _migrate_add_environment_column("daily_cost")
    _migrate_add_environment_column("ta_summary")


def _migrate_add_environment_column(table_name):
    """Add environment column to existing tables if it doesn't exist."""
    cur = conn.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cur.fetchall()]
    if "environment" not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN environment TEXT")
        conn.commit()

def save_account(account_id, name, role_arn, environment):
    """Save or update account metadata."""
    conn.execute(
        "INSERT OR REPLACE INTO accounts VALUES (?, ?, ?, ?, datetime('now'))",
        (account_id, name, role_arn, environment)
    )
    conn.commit()

def get_account(account_id):
    """Get account metadata by account_id."""
    cur = conn.execute(
        "SELECT account_id, name, role_arn, environment FROM accounts WHERE account_id=?",
        (account_id,)
    )
    row = cur.fetchone()
    if not row:
        return None

    return {
        "account_id": row[0],
        "name": row[1],
        "role_arn": row[2],
        "environment": row[3]
    }

def save_monthly(account_id, total_cost, top_services, environment=None):
    conn.execute(
        "DELETE FROM monthly_cost WHERE account_id=?",
        (account_id,)
    )

    conn.execute(
        "INSERT INTO monthly_cost VALUES (?, ?, ?, ?, datetime('now'))",
        (account_id, total_cost, json.dumps(top_services), environment)
    )

    conn.commit()

def save_daily(account_id, data, environment=None):
    conn.execute(
        "DELETE FROM daily_cost WHERE account_id=?",
        (account_id,)
    )

    conn.execute(
        "INSERT INTO daily_cost VALUES (?, ?, ?, datetime('now'))",
        (account_id, json.dumps(data), environment)
    )

    conn.commit()


def save_ta_summary(account_id, data, environment=None):
    """Save a Trusted Advisor summary (JSON serializable) for an account."""
    conn.execute(
        "DELETE FROM ta_summary WHERE account_id=?",
        (account_id,)
    )

    conn.execute(
        "INSERT INTO ta_summary VALUES (?, ?, ?, datetime('now'))",
        (account_id, json.dumps(data), environment)
    )

    conn.commit()

def get_monthly(account_id):
    cur = conn.execute(
        "SELECT total_cost, top_services, environment FROM monthly_cost WHERE account_id=?",
        (account_id,)
    )
    row = cur.fetchone()
    if not row:
        return None

    return {
        "total_cost": row[0],
        "top_services": json.loads(row[1]),
        "environment": row[2]
    }

def get_daily(account_id):
    cur = conn.execute(
        "SELECT data, environment FROM daily_cost WHERE account_id=?",
        (account_id,)
    )
    row = cur.fetchone()
    if not row:
        return None
    return {
        "data": json.loads(row[0]),
        "environment": row[1]
    }


def get_ta_summary(account_id):
    cur = conn.execute(
        "SELECT data, environment FROM ta_summary WHERE account_id=?",
        (account_id,)
    )
    row = cur.fetchone()
    if not row:
        return None
    return {
        "data": json.loads(row[0]),
        "environment": row[1]
    }