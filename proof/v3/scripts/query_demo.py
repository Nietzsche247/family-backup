import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'artifacts' / 'ledger_demo.db'

conn = sqlite3.connect(DB)
conn.execute("""CREATE TABLE IF NOT EXISTS wal_queue (
    session_id TEXT NOT NULL,
    line_no INTEGER NOT NULL,
    payload_json TEXT NOT NULL,
    enqueued_at_utc TEXT NOT NULL,
    acked_at_utc TEXT
)""")
conn.execute("DELETE FROM wal_queue")
old = (datetime.now(timezone.utc) - timedelta(seconds=95)).isoformat().replace('+00:00','Z')
conn.execute("INSERT INTO wal_queue(session_id,line_no,payload_json,enqueued_at_utc,acked_at_utc) VALUES(?,?,?,?,NULL)", ('sess-001',1,'{}',old))
conn.execute("INSERT OR REPLACE INTO jobs(job_id,queue_name,status,payload_json,enqueued_at_utc) VALUES(?,?,?,?,?)", ('job-1','infranodus','queued','{}',old))
conn.execute("INSERT OR REPLACE INTO jobs(job_id,queue_name,status,payload_json,enqueued_at_utc,last_error) VALUES(?,?,?,?,?,?)", ('job-2','infranodus','failed','{}',old,'timeout'))
conn.commit()

latest = conn.execute("""SELECT handoff_id, session_id, finalized_at_utc, finalized_pointer_hash, ledger_finalize_event_id
FROM handoffs WHERE session_id=? AND finalized_at_utc IS NOT NULL
ORDER BY finalized_at_utc DESC, handoff_id DESC LIMIT 1""", ('sess-001',)).fetchone()
current = conn.execute("SELECT session_id,handoff_id,pointer_hash,updated_at_utc FROM handoff_current WHERE session_id=?", ('sess-001',)).fetchone()
wal = conn.execute("""SELECT COUNT(*) AS wal_depth, MIN(enqueued_at_utc) AS oldest_unacked_at_utc,
CAST((julianday('now') - julianday(MIN(enqueued_at_utc))) * 86400 AS INTEGER) AS oldest_age_seconds
FROM wal_queue WHERE acked_at_utc IS NULL""").fetchone()
job = conn.execute("""SELECT queue_name,
SUM(CASE WHEN status IN ('queued','retry') THEN 1 ELSE 0 END) AS backlog,
SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS failed,
MIN(CASE WHEN status IN ('queued','retry') THEN enqueued_at_utc END) AS oldest_backlog_at_utc
FROM jobs GROUP BY queue_name ORDER BY queue_name""").fetchall()

print(json.dumps({
    'latest_finalized_handoff': latest,
    'current_pointer': current,
    'wal_backlog': wal,
    'job_backlog': job,
}, indent=2))
