import sqlite3
db = sqlite3.connect(r"C:\Users\aaron\.openclaw\memos-local\memos.db")
cur = db.cursor()
print("== SKILLS ==")
for r in cur.execute("SELECT id, name FROM skills"):
    print("  ", r[0], "|", r[1])

print("\n== chunks with skill_id set (top names) ==")
for r in cur.execute("SELECT skill_id, COUNT(*) FROM chunks WHERE skill_id IS NOT NULL AND skill_id != '' GROUP BY skill_id"):
    print("  ", r)

print("\n== chunks mentioning 'ledger' (count) ==")
n = cur.execute("SELECT COUNT(*) FROM chunks WHERE content LIKE '%ledger%' OR content LIKE '%Ledger%'").fetchone()[0]
print("  ", n)

print("\n== sample ledger chunks ==")
for r in cur.execute("SELECT id, session_key, role, task_id, skill_id, substr(content,1,160) FROM chunks WHERE content LIKE '%ledger%' OR content LIKE '%/events%' LIMIT 8"):
    print("  --", r[0], "| role=", r[2], "| task=", r[3], "| skill=", r[4])
    print("     ", r[5].replace("\n"," "))

print("\n== tasks mentioning ledger ==")
for r in cur.execute("SELECT id, title, substr(summary,1,120) FROM tasks WHERE title LIKE '%ledger%' OR summary LIKE '%ledger%' LIMIT 8"):
    print("  ", r)
