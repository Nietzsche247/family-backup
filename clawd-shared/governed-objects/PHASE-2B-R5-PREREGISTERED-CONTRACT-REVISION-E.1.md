# Phase 2B-R5 Preregistered Laboratory Contract â€” Revision E.1

**Experiment ID:** `P2BR5-20260904-A`  
**Rubric ID:** `P2BR3-RUBRIC-18C-v1`  
**Parent goal pointer:** `01M1DVHCYZSYREJY6AZJ0EHA0R`  
**Status:** FROZEN â€” PREREGISTERED / PRE-EXECUTION
**Freeze timestamp:** `2026-09-05T03:30:47.5238654Z`
**Supersedes Revision E:** SHA-256 `0BAD3595B6BE114DB441BD4510A40B058FFF27A4E55679B2C67892F1E10DCB4D`, 17,430 bytes
**Supersession reason:** Internal receipt-field authority arithmetic inconsistency (RECEIPT-SCHEMA-001) found by independent pre-execution Judge readback. Field 22 (`context_manifest_hash`) is pre-dispatch assigned but fell outside stated range 1–14. Field 7 (`ledger_event`) source column did not explicitly state pre-dispatch origin.  
**Phase 2C:** NOT AUTHORIZED  
**Supersedes Revision D:** SHA-256 `CBB8E0404AD8E49EB24BB2A445F6C8302A9F7CA73F0C65566727CD53480D3BA7`, 14,991 bytes (experiment `P2BR4-20260903-A`)  
**Supersession conditions:** R4 STOPPED / INVALIDATED BY RECEIPT-CONTRACT AMBIGUITY (defect RECEIPT-AUTHORITY-001). No R4 accepted TTC established. No R4 semantic verdict established. No R4 parallel arm started. No Plato semantic exposure to R4 control content.

## Prior experiment dispositions carried forward

### Revision B

- **Revision B control arm verdict:** **FAIL** â€” independent Plato semantic adjudication.
- **Controlling Judge report SHA-256:** `70E1F1BE7809D4D511D087B01E428EC2CBB4CBE740104A1BB7E8A5E73390373F`.
- **Revision B control accepted:** NO.
- **Revision B control accepted TTC:** NOT ESTABLISHED.
- **Revision B parallel arm:** NOT STARTED.
- **Revision B experiment disposition:** **PARTIAL / COMPARATIVE PERFORMANCE TEST INCOMPLETE**.
- **Phase 2B:** NOT EARNED.

### Revision C.1 / R3

- **R3 experiment:** `P2BR3-20260903-A`
- **R3 disposition:** BLOCKED / INVALIDATED BY FROZEN BASELINE CONTRADICTION
- **R3 control accepted:** NO (gate rejected 3/3 receipts)
- **R3 control accepted TTC:** NOT ESTABLISHED
- **R3 parallel arm:** NOT STARTED
- **Root defect:** BASELINE-AUTHORITY-001

### Revision D / R4

- **R4 experiment:** `P2BR4-20260903-A`
- **R4 disposition:** STOPPED / INVALIDATED BY RECEIPT-CONTRACT AMBIGUITY
- **R4 control accepted:** NO (gate passed 3/3 on orchestrator-constructed receipts; Primary rejected post-hoc receipt authority)
- **R4 control accepted TTC:** NOT ESTABLISHED
- **R4 control semantic verdict:** NOT ESTABLISHED (never submitted to Plato)
- **R4 parallel arm:** NOT STARTED
- **Root defect:** RECEIPT-AUTHORITY-001 â€” gate schema required 22 fields; contract Â§10 specified 11; producer emitted incompatible schema; orchestrator constructed replacement receipts with invented `attempt_id`; no preregistered authority for that repair

R4 produced control artifacts are historical failure evidence only. They must NOT enter R5 producer context. R4 semantic content must NOT be exposed to Plato as part of R5 preflight.

---

## 0. What changed from Revision D

**E.1. Receipt Schema Bound Into Contract (Â§10 â€” REWRITTEN)**  
The exact gate receipt schema is now defined in the contract itself, not inherited from an external gate with unstated additional requirements. All 22 required fields are enumerated. Defect addressed: RECEIPT-AUTHORITY-001.

**E.2. Producer Is Authoritative Receipt Creator (Â§10.1 â€” NEW)**  
The producer is the sole authoritative receipt creator. The orchestrator may NOT invent, semantically repair, or supplement missing producer receipt fields after output is known. Defect addressed: RECEIPT-AUTHORITY-001.

**E.3. Pre-Dispatch Receipt Identity Assignment (Â§10.2 â€” NEW)**  
`attempt_id`, `branch`, `producing_agent`, `baseline_ref`, `context_manifest_hash`, `authority_envelope`, and expected artifact paths are assigned BEFORE objective dispatch and included in the producer's work packet. The producer uses these exact values â€” it does not generate them. Defect addressed: RECEIPT-AUTHORITY-001.

**E.4. One Receipt Per Terminal Artifact (Â§10.3 â€” NEW)**  
Each terminal artifact gets exactly one receipt file. Multi-artifact receipts are invalid. Defect addressed: RECEIPT-AUTHORITY-001.

**E.5. Producer Receipt Dry-Run Fixture (Â§10.4 â€” NEW)**  
Before timer start, a dry-run fixture proves the producer prompt can emit the required receipt schema. Defect addressed: RECEIPT-AUTHORITY-001.

**E.6. Receipt Schema Consistency Check Added to Baseline Audit (Â§18 â€” EXTENDED)**  
The final baseline audit now verifies receipt schema binding consistency. Defect addressed: RECEIPT-AUTHORITY-001.

**E.7. Eight Controlled Receipt Fixtures (Â§10.5 â€” NEW)**  
Eight pre-run fixtures prove the gate correctly accepts/rejects receipt variants. Defect addressed: RECEIPT-AUTHORITY-001.

**E.8. Experiment-Identity Consistency Check Retained (Â§16.1)**  
Carried forward unchanged from Revision D.

All other rules (Â§Â§1â€“9, 11â€“15, 16, 17) are carried forward unchanged from Revision D.

---

## 1. Objective

Identical to Revision B Â§1. Unchanged.

## 2. Frozen baseline

R5 baseline binding: `P2BR5-BASELINE-BINDING-20260904-A`. It explicitly binds the current R5 identity and controlled paths to the unchanged immutable source corpus `P2BR2-BASELINE-20260902-A` (13 files, source manifest SHA-256 `0E340AFBB2995381E355B4054FE72A89669FFE3E1241A911BE45C9B5AC2E8A3A`). If the source corpus is updated, a new source baseline ID and manifest hash must be frozen and recorded here before timing.

## 3. Workload

Identical to Revision B Â§3. Same two deliverables (Recovery Playbook v2, Knowledge Brain v0 Implementation v2) and integration. Same word minimums.

**Additional control instruction (Â§7 owner directive):**

> Produce the best substantive operational result possible. Contract compliance is necessary but not sufficient. Avoid boilerplate, repeated contract restatement, receipt scaffolding, and word-count padding unless substantively required.

The same substantive quality expectation applies to the parallel system.

## 4. Model/runtime configuration

Identical to Revision B Â§4. Same models, same Ledger, same MemOS.

- Global Orchestrator: `anthropic/claude-opus-4-6`.
- Control executor: `anthropic/claude-sonnet-4-6`.
- Program Orchestrators A/B: `anthropic/claude-sonnet-4-6`.
- Specialist pool: up to 10 `anthropic/claude-sonnet-4-6` workers available.
- Independent Judge: Plato on NIETZSCHE2025.
- Canonical Ledger: `http://127.0.0.1:3003`.
- MemOS database: `C:\Users\aaron\.openclaw\memos-local\memos.db`.

## 5. Control definition

Identical to Revision B Â§5 with Â§5.1 from Revision D.

### 5.1. Control-Validity Gate

Identical to Revision D Â§5.1. Unchanged.

## 6. Parallel definition and topology

Identical to Revision B Â§6. Unchanged.

## 7. Authority envelopes

Identical to Revision B Â§7. Kant and Kant sub-agents remain OUT OF SCOPE / NON-PARTICIPATING.

**R5 authority map:** `AUTHORITY-MAP-R5.json` â€” all agent path prefixes bound to `PHASE-2B-R5/...`. Verified by experiment-identity consistency check (Â§16.1).

## 8. Semantic acceptance contract

Identical to Revision D Â§8 including Â§8.1. Unchanged.

## 9. Signal Fire firewall

Identical to Revision B Â§9. Unchanged.

## 10. Receipt finalization contract (REWRITTEN â€” fixes RECEIPT-AUTHORITY-001)

### 10.0. Canonical Gate Receipt Schema

Every receipt file validated by the integration gate MUST contain exactly these 22 fields. This is the canonical schema â€” it supersedes any prior "Receipt fields required" list.

| # | Field | Type | Source | Description |
|---|---|---|---|---|
| 1 | `packet_id` | string | Pre-dispatch assignment | Unique identifier for this receipt packet |
| 2 | `attempt_id` | string | Pre-dispatch assignment | Attempt identity; assigned before execution |
| 3 | `generation` | integer â‰¥ 1 | Pre-dispatch assignment | Generation number |
| 4 | `branch` | string | Pre-dispatch assignment | `"control"` or `"parallel-a"` or `"parallel-b"` or `"integration"` |
| 5 | `agent` | string | Pre-dispatch assignment | Agent identity matching authority map key |
| 6 | `producing_agent` | string | Pre-dispatch assignment | Must equal `agent` |
| 7 | `ledger_event` | string | Pre-dispatch assignment — timer-start Ledger event ID | The event ID recording arm dispatch |
| 8 | `authority_envelope` | string | Pre-dispatch assignment | Path prefix from authority map |
| 9 | `baseline_class` | string | Pre-dispatch assignment | `"IMMUTABLE_ARTIFACT"` for baseline-derived work |
| 10 | `baseline_ref` | object | Pre-dispatch assignment | `{ "for_immutable": { "baseline_id": "...", "manifest_sha256": "..." } }` |
| 11 | `baseline_id` | string | Pre-dispatch assignment | Baseline ID (lowercase hex for hash) |
| 12 | `baseline_manifest_sha256` | string | Pre-dispatch assignment | Lowercase hex, 64 chars |
| 13 | `scope` | string | Pre-dispatch assignment | Description of execution scope |
| 14 | `method` | string | Pre-dispatch assignment | Description of execution method |
| 15 | `claim` | string | Producer-authored | What the producer claims about this artifact |
| 16 | `artifact` | string | Producer-determined | Absolute path to the terminal artifact on disk |
| 17 | `provenance` | string | Producer-computed from file bytes | `"sha256:<64 hex chars>"` computed from `readFile(artifact)` |
| 18 | `bytes` | integer | Producer-computed from file stat | Byte count from `stat(artifact)` |
| 19 | `acceptance_evidence` | string | Producer-authored | How the producer verified the artifact |
| 20 | `timestamp` | string (ISO 8601) | Producer-generated | UTC timestamp of receipt finalization |
| 21 | `verification_status` | string | Producer-determined | Must be `"VERIFIED"` after hash readback match |
| 22 | `context_manifest_hash` | string | Pre-dispatch assignment | Lowercase hex SHA-256 of the input context manifest |

**Field authority classification:**

- **Pre-dispatch assigned (fields 1â€“14):** These values are determined by the Global Orchestrator BEFORE the producer receives its objective. They are included verbatim in the producer's work packet. The producer copies them into the receipt without modification.
- **Producer-determined (fields 15â€“21):** These values are generated by the producer from actual artifact bytes, file stats, and the producer's own verification process. The orchestrator may NOT invent, author, or substitute these fields.
- **Deterministic machine-derived:** `provenance` and `bytes` MUST be computed from the final closed artifact file â€” not from memory, not from model-generated text, not from orchestrator readback.

### 10.1. Producer Is Authoritative Receipt Creator

The producer (control executor or parallel worker) is the sole entity that creates receipts for its own terminal artifacts. The Global Orchestrator:

- **MAY** provide pre-dispatch field values for fields 1â€“14 and 22 as part of the work packet
- **MAY** validate receipts after production using the integration gate
- **MAY NOT** create, replace, supplement, or semantically repair producer receipt fields after output is known
- **MAY NOT** invent values for producer-determined fields (15â€“21)
- **MAY NOT** construct alternative receipts from orchestrator readback data

If the producer fails to emit a valid receipt, the arm's receipt-gate check FAILS. This is a legitimate experimental result, not an error to be repaired.

### 10.2. Pre-Dispatch Receipt Identity Assignment

Before the producer receives its objective, the orchestrator MUST:

1. Generate `attempt_id` (format: `P2BR5-<arm>-attempt-<ULID>`)
2. Assign `branch`, `agent`, `producing_agent`, `generation`
3. Compute `baseline_ref` from the frozen baseline manifest
4. Compute `context_manifest_hash` from the frozen input context manifest
5. Assign `authority_envelope` from the authority map
6. Assign `scope`, `method`, `baseline_class`, `baseline_id`, `baseline_manifest_sha256`
7. Assign `ledger_event` (the timer-start event ID)
8. Determine expected artifact paths under the authority envelope
9. Package all pre-dispatch fields into a `receipt_identity` block in the work packet

The producer's work packet MUST include the `receipt_identity` block with all 15 pre-dispatch fields (fields 1–14 and 22). The producer copies these into each receipt verbatim.

### 10.3. One Receipt Per Terminal Artifact

Each terminal artifact (Deliverable A, Deliverable B, Integration Report) gets exactly one receipt file. The receipt filename MUST be `<packet_id>.json`. Multi-artifact receipts are invalid and will be rejected by the gate.

### 10.4. Producer Receipt Dry-Run Fixture

Before R5 timer start, a controlled test MUST prove the producer prompt can emit the required receipt schema:

1. Create a mock `receipt_identity` block with test values
2. Create a test artifact file with known content
3. Dispatch the producer model with a minimal "write this file and create a receipt" instruction including the `receipt_identity` block
4. Verify the emitted receipt:
   - Contains all 22 fields
   - Pre-dispatch fields match the provided `receipt_identity` exactly
   - `provenance` hash matches the test artifact's actual SHA-256
   - `bytes` matches the test artifact's actual file size
   - `verification_status` is `"VERIFIED"`
   - Gate passes on the emitted receipt

If the dry-run fails, R5 does NOT start. The producer prompt or receipt instructions must be fixed first.

### 10.5. Controlled Receipt Fixtures (8 tests)

Before R5 freeze, the following fixtures MUST all produce the correct result:

| # | Fixture | Expected |
|---|---|---|
| 1 | Fully valid producer receipt | PASS |
| 2 | Missing `attempt_id` | FAIL |
| 3 | Missing `context_manifest_hash` | FAIL |
| 4 | Wrong artifact hash (`provenance` mismatch) | FAIL |
| 5 | Wrong `bytes` (size mismatch) | FAIL |
| 6 | Wrong `authority_envelope` (path mismatch) | FAIL |
| 7 | `attempt_id` not matching pre-dispatch assignment | FAIL |
| 8 | Duplicate packet_id with lower generation | Deterministic (highest generation selected) |

All 8 fixtures must produce the correct result before freeze.

### 10.6. Receipt Finalization Sequence (producer obligation)

For every terminal artifact, the producer MUST:

1. Write to a temporary path.
2. Close and flush.
3. Atomically rename to final path.
4. Hash the finalized artifact with SHA-256 (from file bytes, not memory).
5. Record byte count from file stat.
6. Create receipt file at `<receipts-dir>/<packet_id>.json` using:
   - All 15 pre-dispatch fields from the `receipt_identity` block (copied verbatim — fields 1–14 and 22)
   - `artifact`: the final artifact path
   - `provenance`: `"sha256:<computed hex>"`
   - `bytes`: the byte count from step 5
   - `claim`: producer's description of what was produced
   - `acceptance_evidence`: producer's description of verification performed
   - `timestamp`: current UTC ISO 8601
   - `verification_status`: `"VERIFIED"` (only after hash readback confirms match)
7. Read the finalized artifact back.
8. Recompute SHA-256 and byte count.
9. Require exact match with receipt values.
10. If mismatch: set `verification_status` to `"HASH_MISMATCH"` â€” do NOT silently continue.

### 10.7. Post-Production Orchestrator Obligations

After the producer completes, the orchestrator:

1. Reads each receipt file from disk
2. Runs the integration gate against the receipts
3. Reports PASS/FAIL
4. Does NOT modify, supplement, or replace any receipt
5. If a receipt is missing or malformed, the gate FAILS â€” this is a valid experimental result

## 11. Judge identity and evidence transport

Identical to Revision D Â§11 including Â§11.1 and Â§11.2. Unchanged.

## 12. Timing contract

Identical to Revision D Â§12. Unchanged.

## 13. Context-lifecycle precondition

Identical to Revision B Â§13. Unchanged.

## 14. Contamination rules

Identical to Revision D Â§14.

**Additional:** No R4 produced control outputs, receipts (original or corrected), integration reports, metrics, gate results, or semantic content may enter R5 producer context. R4 outputs are historical failure evidence only. This prohibition does **not** bar the explicitly frozen `P2BR2-BASELINE-20260902-A` source corpus in Â§2.

## 15. Stop rules

Identical to Revision D Â§15. Unchanged.

## 16. R5 pass bar

Phase 2B-R5 PASS requires all 18 (identical to Revision D Â§16):

1. semantic output equivalent or better than control (per Â§8.1 rubric);
2. accepted end-to-end parallel gain >1.0x;
3. H-003 PASS;
4. H-005 PASS;
5. R1 reuse PASS;
6. one governed reality preserved;
7. Program authority PASS;
8. cross-program dependency PASS;
9. meaningful local prioritization PASS;
10. global integration PASS;
11. genuinely independent Plato Judge PASS;
12. C PASS;
13. D PASS;
14. G PASS;
15. zero Aaron project reconstruction;
16. Signal Fire firewall PASS with explicit evidence;
17. deterministic receipt integrity PASS;
18. no self-promotion into missing authority.

No alternative success criterion after the run.

### 16.1. Experiment-Identity Consistency Check

Identical to Revision D Â§16.1. Unchanged except stale token list updated:

**Stale token rejection:** The check must FAIL if any of the following appear in a field that must represent the current R5 run: `P2BR2`, `PHASE-2B-R2`, `P2BR3`, `PHASE-2B-R3`, `P2BR4`, `PHASE-2B-R4`.

## 17. Closure rule

Identical to Revision B Â§17. Unchanged.

## 18. Baseline audit two-layer verification

Identical to Revision D Â§18.

**Additional (E.6):** The final baseline audit must also verify that the frozen receipt schema definition in Â§10.0 is consistent with the integration gate's actual validation logic. Specifically: every field the gate checks for existence must appear in Â§10.0's canonical schema table. If the gate requires a field not in Â§10.0, the audit FAILS.
