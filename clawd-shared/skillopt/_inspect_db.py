import sqlite3, json
db = sqlite3.connect(r"C:\Users\aaron\.openclaw\memos-local\memos.db")
cur = db.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("TABLES:", tables)
for t in tables:
    try:
        cur.execute(f"PRAGMA table_info({t})")
        cols = [(r[1], r[2]) for r in cur.fetchall()]
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        n = cur.fetchone()[0]
        print(f"\n== {t} (rows={n}) ==")
        for c in cols:
            print("   ", c[0], c[1])
    except Exception as e:
        print(f"\n== {t} ERROR: {e}")
