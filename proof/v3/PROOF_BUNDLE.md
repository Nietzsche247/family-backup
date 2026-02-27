# v3 Context Resilience Proof Bundle

Branch: `master`  
Commit: `8a9db59`

Run-from-root: `C:\Users\aaron\clawd-daedalus`

---

## 1) Ledger schema/migrations (exact)

**Path:** `proof/v3/migrations/001_v3_context_resilience.sql`

Includes required tables/constraints:
- `leases` with `renewal_token`
- `events` with `event_id TEXT NOT NULL UNIQUE`
- `handoffs` with staged/finalized fields including `finalized_at_utc` (server-set)
- `handoff_current` (current pointer fast path)
- `jobs` (InfraNodus queue hosting)

Snippet:
```sql
CREATE TABLE IF NOT EXISTS leases (
  lease_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  holder_agent TEXT NOT NULL,
  renewal_token TEXT NOT NULL,
  expires_at_utc TEXT NOT NULL,
  ...
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL UNIQUE,
  session_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  ...
);

CREATE TABLE IF NOT EXISTS handoffs (
  handoff_id TEXT PRIMARY KEY,
  ...
  stage_pointer_json TEXT NOT NULL,
  stage_pointer_hash TEXT NOT NULL,
  stage_manifest_hash TEXT NOT NULL,
  stage_z_path TEXT NOT NULL,
  ...
  finalized_pointer_json TEXT,
  finalized_pointer_hash TEXT,
  finalized_manifest_hash TEXT,
  finalized_at_utc TEXT,
  finalized_by_server INTEGER NOT NULL DEFAULT 0,
  finalize_marker_path TEXT,
  ledger_finalize_event_id TEXT
);
```

---

## 2) API contract examples

**Path:** `proof/v3/api/contract_examples.sh`

Contains copy/paste `curl` contracts for:
- acquire lease -> returns `renewal_token`
- renew lease -> requires `renewal_token`
- stage handoff -> accepts pointer JSON + hashes
- finalize -> server verifies by reading Z/shared path + recomputing hashes
- pointer events -> append-only query stream

Snippet:
```bash
curl -sS -X POST http://localhost:8080/v3/leases/acquire \
  -H 'content-type: application/json' \
  -d '{"session_id":"sess-001","holder_agent":"supervisor","ttl_seconds":60}'
# => {"lease_id":"lease-...","renewal_token":"rtok-...","expires_at_utc":"..."}

curl -sS -X POST http://localhost:8080/v3/leases/renew \
  -H 'content-type: application/json' \
  -d '{"lease_id":"lease-...","renewal_token":"rtok-...","ttl_seconds":60}'
```

---

## 3) Deterministic queries

**Path:** `proof/v3/queries/deterministic_queries.sql`

Includes exact SQL for:
- latest finalized handoff for session
- current pointer retrieval rule (`handoff_current` first, then finalized fallback)
- backlog depth queries:
  - WAL depth + oldest age
  - jobs backlog + failures

Verification command/output:
```powershell
python proof\v3\scripts\query_demo.py
```
Output:
```json
{
  "latest_finalized_handoff": ["hof-001","sess-001","2026-02-27T03:39:26.272473Z","dc6c1976...","evt-3694e52f-e790-4155-be2c-cb17ba8b3617"],
  "current_pointer": ["sess-001","hof-001","dc6c1976...","2026-02-27T03:39:26.272473Z"],
  "wal_backlog": [1,"2026-02-27T03:38:05.079449Z",95],
  "job_backlog": [["infranodus",1,1,"2026-02-27T03:38:05.079449Z"]]
}
```

---

## 4) Crash durability test output

**Script:** `proof/v3/scripts/crash_durability_test.py`  
**Artifact log:** `proof/v3/artifacts/crash_durability_test.log`

Command:
```powershell
python proof\v3\scripts\crash_durability_test.py
```
Output:
```text
flush_survives=True
noflush_survives=False
PASS: durability test discriminates flush vs no-flush
```

Artifact snippet:
```text
CASE flush=True rc=... survived=True bytes=20
CASE flush=False rc=... survived=False bytes=0
```

This proves “write + immediate crash survives with fsync” and “same test fails without flush.”

---

## 5) End-to-end demo run (single session)

**Script:** `proof/v3/scripts/demo_e2e.py`  
**Artifacts:**
- `proof/v3/artifacts/demo_run_output.json`
- `proof/v3/artifacts/pointer.json`
- `proof/v3/artifacts/sessions/sess-001/hof-001/Z/finalize.marker`

Command:
```powershell
python proof\v3\scripts\demo_e2e.py
```
Output:
```json
{
  "events": {
    "finalized": "evt-3694e52f-e790-4155-be2c-cb17ba8b3617",
    "staged": "evt-eb399aa6-b4ff-4030-995c-f25ba93616bc"
  },
  "handoff_id": "hof-001",
  "manifest_hash": "446697625593df99551189962e2c80ae2c08b2636b2a2250c00f5403473ef0cd",
  "pointer_hash": "dc6c19763680a2a6f2bfed2daf99aa97b5eebcf6de669c6236edb907a72e66db",
  "session_id": "sess-001"
}
```

Flow executed in script:
1. stage pointer + hashes in `handoffs`
2. replicate Z -> shared
3. verify hashes by server-side recompute from Z path
4. finalize in Ledger (`finalized_*`, `finalized_at_utc`, `finalized_by_server=1`)
5. write `finalize.marker`
6. append `pointer-finalized` event

`pointer.json` path: `proof/v3/artifacts/pointer.json`

---

## BONUS: `/healthfacts` example shape

**Path:** `proof/v3/api/healthfacts_example.json`

Contains:
- active leases + expiries
- WAL backlog + oldest age
- handoffs staged/finalized
- job backlog/failures
- degraded flags

---

## Repro commands (copy/paste)

```powershell
python proof\v3\scripts\crash_durability_test.py
python proof\v3\scripts\demo_e2e.py
python proof\v3\scripts\query_demo.py
```
