import sqlite3
import os
import database  # 추가

DB_PATH = os.getenv("DB_PATH", "database.db")

database.init_db()  # 추가 — 테이블 먼저 생성

peer_data = [
    ("food",      95000),
    ("cafe",      32000),
    ("transport", 41000),
    ("shopping",  72000),
    ("medical",   15000),
    ("leisure",   43000),
    ("etc",           0),
]

conn = sqlite3.connect(DB_PATH)
conn.executemany(
    "INSERT OR REPLACE INTO peer_averages (category, avg_amount) VALUES (?, ?)",
    peer_data
)
conn.commit()
conn.close()

print("✅ 또래 비교 데이터 삽입 완료!")