import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "database.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            amount     INTEGER NOT NULL,
            store      TEXT    NOT NULL,
            category   TEXT    NOT NULL,
            date       TEXT    NOT NULL,
            time       TEXT    NOT NULL,
            card       TEXT,
            created_at TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS peer_averages (
            category   TEXT    PRIMARY KEY,
            avg_amount INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def insert_transaction(amount, store, category, date, time, card=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (amount, store, category, date, time, card)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (amount, store, category, date, time, card))
    conn.commit()
    transaction_id = cursor.lastrowid
    conn.close()
    return transaction_id


def get_transactions(month=None):
    conn = get_connection()
    cursor = conn.cursor()

    if month:
        cursor.execute("""
            SELECT id, amount, store, category, date, time, card
            FROM transactions
            WHERE strftime('%Y-%m', date) = ?
            ORDER BY date DESC, time DESC
        """, (month,))
    else:
        cursor.execute("""
            SELECT id, amount, store, category, date, time, card
            FROM transactions
            ORDER BY date DESC, time DESC
        """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats(month):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE strftime('%Y-%m', date) = ?
        GROUP BY category
    """, (month,))

    CATEGORIES = ["food", "cafe", "transport", "shopping", "medical", "leisure", "etc"]
    by_category = {cat: 0 for cat in CATEGORIES}
    for row in cursor.fetchall():
        by_category[row["category"]] = row["total"]

    cursor.execute("""
        SELECT date, SUM(amount) as total
        FROM transactions
        WHERE strftime('%Y-%m', date) = ?
        GROUP BY date
        ORDER BY date
    """, (month,))

    by_date = [{"date": row["date"], "amount": row["total"]} for row in cursor.fetchall()]

    conn.close()
    return {
        "total_amount": sum(by_category.values()),
        "by_category": by_category,
        "by_date": by_date
    }


def get_peer_averages():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, avg_amount FROM peer_averages")
    rows = cursor.fetchall()
    conn.close()
    return {row["category"]: row["avg_amount"] for row in rows}