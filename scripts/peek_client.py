# scripts/peek_client.py
import sqlite3
from app.db import DATABASE_URL

path = DATABASE_URL.replace("sqlite:///", "")
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("PRAGMA table_info(clients)")
print(cur.fetchall())
conn.close()
