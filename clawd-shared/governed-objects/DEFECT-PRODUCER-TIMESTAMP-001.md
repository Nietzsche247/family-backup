# DEFECT: PRODUCER-TIMESTAMP-001

**Filed:** 2026-09-05
**Experiment:** P2BR5-20260904-A (Phase 2B-R5, Revision E.2)
**Classification:** PRODUCER RECEIPT MECHANICAL FAILURE
**Disposition:** R5 parallel arm STOPPED

## Definition

Producer model used local Arizona wall-clock time (America/Phoenix, UTC-7) and serialized it with a UTC `Z` suffix in the receipt `timestamp` field. The hardened integration gate correctly rejected the receipt because the timestamp appeared to precede the experiment dispatch time.

## Exact failure

```
PRODUCER WROTE:    "timestamp": "2026-09-05T10:48:33Z"
ACTUAL UTC:        2026-09-05T17:48:33Z (confirmed by file mtime 17:48:59Z)
EXPERIMENT START:  2026-09-05T17:41:18Z
GATE RULE:         timestamp must be >= experiment start
GATE RESULT:       FAIL (10:48:33Z < 17:41:18Z)
```

The producer manually constructed the timestamp string from local time without UTC conversion.

## Why the dry-run did not catch this

The pre-freeze dry-run ran in a session context where the model happened to emit a timestamp compatible with the test experiment-start boundary. The dry-run did not exercise timezone conversion because the test did not simulate a non-UTC host timezone.

## Corrective requirements for R6

1. Producer receipt timestamps must come from deterministic runtime code, not model-constructed strings
2. The work packet must include a concrete UTC timestamp generation instruction using runtime APIs
3. New timestamp fixture tests must cover:
   - America/Phoenix → correct UTC
   - Second non-UTC timezone → correct UTC
   - Local-time-with-Z → REJECTED
   - Timestamp >= experiment dispatch
   - Ambiguous/local timestamp without offset → REJECTED
   - Canonical UTC serialization byte-stable
4. The exact R5 failure class must be reproduced as a fixture

## Evidence preserved

| Artifact | Path |
|---|---|
| Failed receipt | `receipts/parallel-arm/P2BR5-20260904-A-parallel-b-001.json` |
| Gate result | `receipts/parallel-arm/GATE-RESULT.json` |
| All parallel artifacts | `parallel-arm/PROGRAM-A/`, `parallel-arm/PROGRAM-B/`, `parallel-arm/global-integration/` |
| All receipts | `receipts/parallel-arm/` |
