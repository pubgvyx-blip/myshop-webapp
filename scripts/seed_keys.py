import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parents[1] / "shop.db"))

ROWS = [
    ("android", "ANDROID-TEST-001"),
    ("pc", "PC-TEST-001"),
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT NOT NULL,
        key TEXT NOT NULL,
        is_used INTEGER NOT NULL DEFAULT 0
    )
    """
)
cur.executemany("INSERT INTO keys(product, key, is_used) VALUES(?, ?, 0)", ROWS)
conn.commit()
conn.close()

print(f"Seeded {len(ROWS)} keys into {DB_PATH}")
