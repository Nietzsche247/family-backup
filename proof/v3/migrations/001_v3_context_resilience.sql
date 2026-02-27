-- v3 Context Resilience Ledger schema
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS leases (
  lease_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  holder_agent TEXT NOT NULL,
  renewal_token TEXT NOT NULL,
  expires_at_utc TEXT NOT NULL,
  renewed_at_utc TEXT,
  created_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_leases_session ON leases(session_id);
CREATE INDEX IF NOT EXISTS idx_leases_expiry ON leases(expires_at_utc);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL UNIQUE,
  session_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_events_session_created ON events(session_id, created_at_utc DESC);

CREATE TABLE IF NOT EXISTS handoffs (
  handoff_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  from_agent TEXT NOT NULL,
  to_agent TEXT NOT NULL,
  stage_pointer_json TEXT NOT NULL,
  stage_pointer_hash TEXT NOT NULL,
  stage_manifest_hash TEXT NOT NULL,
  stage_z_path TEXT NOT NULL,
  stage_shared_path TEXT,
  staged_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

  finalized_pointer_json TEXT,
  finalized_pointer_hash TEXT,
  finalized_manifest_hash TEXT,
  finalized_at_utc TEXT,
  finalized_by_server INTEGER NOT NULL DEFAULT 0,
  finalize_marker_path TEXT,
  ledger_finalize_event_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_handoffs_session_staged ON handoffs(session_id, staged_at_utc DESC);
CREATE INDEX IF NOT EXISTS idx_handoffs_session_finalized ON handoffs(session_id, finalized_at_utc DESC);

CREATE TABLE IF NOT EXISTS handoff_current (
  session_id TEXT PRIMARY KEY,
  handoff_id TEXT NOT NULL,
  pointer_json TEXT NOT NULL,
  pointer_hash TEXT NOT NULL,
  updated_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  FOREIGN KEY(handoff_id) REFERENCES handoffs(handoff_id)
);

CREATE TABLE IF NOT EXISTS jobs (
  job_id TEXT PRIMARY KEY,
  queue_name TEXT NOT NULL,
  status TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  attempt_count INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  enqueued_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  started_at_utc TEXT,
  finished_at_utc TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_queue_status ON jobs(queue_name, status, enqueued_at_utc);
