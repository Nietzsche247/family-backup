-- 1) Latest finalized handoff for a session
SELECT handoff_id, session_id, finalized_at_utc, finalized_pointer_hash, ledger_finalize_event_id
FROM handoffs
WHERE session_id = :session_id
  AND finalized_at_utc IS NOT NULL
ORDER BY finalized_at_utc DESC, handoff_id DESC
LIMIT 1;

-- 2) Current pointer retrieval rule
-- Preferred: handoff_current row; fallback: latest finalized handoff.
SELECT hc.session_id, hc.handoff_id, hc.pointer_json, hc.pointer_hash, hc.updated_at_utc
FROM handoff_current hc
WHERE hc.session_id = :session_id;

SELECT h.session_id, h.handoff_id, h.finalized_pointer_json AS pointer_json,
       h.finalized_pointer_hash AS pointer_hash, h.finalized_at_utc AS updated_at_utc
FROM handoffs h
WHERE h.session_id = :session_id
  AND h.finalized_at_utc IS NOT NULL
ORDER BY h.finalized_at_utc DESC, h.handoff_id DESC
LIMIT 1;

-- 3a) WAL backlog depth + oldest age
-- wal_queue(session_id,line_no,payload_json,enqueued_at_utc,acked_at_utc)
SELECT COUNT(*) AS wal_depth,
       MIN(enqueued_at_utc) AS oldest_unacked_at_utc,
       CAST((julianday('now') - julianday(MIN(enqueued_at_utc))) * 86400 AS INTEGER) AS oldest_age_seconds
FROM wal_queue
WHERE acked_at_utc IS NULL;

-- 3b) InfraNodus job backlog
SELECT queue_name,
       SUM(CASE WHEN status IN ('queued','retry') THEN 1 ELSE 0 END) AS backlog,
       SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS failed,
       MIN(CASE WHEN status IN ('queued','retry') THEN enqueued_at_utc END) AS oldest_backlog_at_utc
FROM jobs
GROUP BY queue_name
ORDER BY queue_name;
