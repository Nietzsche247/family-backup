# Phase 2B-R2 Preregistered Laboratory Contract

**Experiment ID:** `P2BR2-20260902-A`  
**Rubric ID:** `P2BR2-RUBRIC-18-v1`  
**Parent goal pointer:** `01M1DVHCYZSYREJY6AZJ0EHA0R`  
**Status:** FROZEN BEFORE TIMING  
**Phase 2C:** NOT AUTHORIZED

## 1. Objective

Determine whether the partitioned Phase 2B hierarchy can produce semantic output equivalent to or better than a single-stream control with **accepted end-to-end parallel gain greater than 1.0x**, without context-lifecycle interruption, receipt-integrity failure, missing Signal Fire-firewall evidence, unavailable Judge transport, or self-promotion into missing authority.

The Phase 2 semantic objective is unchanged. The swarm is not enlarged.

## 2. Frozen baseline

- Baseline ID: `P2BR2-BASELINE-20260902-A`
- Manifest: `baseline/BASELINE-MANIFEST.json`
- Manifest SHA-256: `0E340AFBB2995381E355B4054FE72A89669FFE3E1241A911BE45C9B5AC2E8A3A`
- Frozen files: 13

No arm may read prior Phase 2B-R outputs, receipts, Judge reports, Signal Fire content, or the other R2 arm.

## 3. Workload

Both arms receive the same objective and frozen source baseline.

### Deliverable A — Recovery Playbook v2

Produce a governed operational recovery playbook covering:

1. Five-skill UUID inventory and retrieval evidence.
2. Aristotle gateway recovery.
3. Fleet health diagnosis.
4. H-003 attempt-fencing recovery.
5. H-005 loop/budget recovery.
6. R1 skill-retrieval recovery.
7. Trusted boot/context recovery.
8. Escalation and authority boundaries.
9. At least five executable acceptance tests.

Minimum: 2,500 substantive words.

### Deliverable B — Knowledge Brain v0 Implementation v2

Produce a CANDIDATE implementation plan covering:

1. Ledger and MemOS schema changes.
2. At least five retrieval/API commands.
3. Eight-article Memory Constitution, explicitly CANDIDATE.
4. Primary and degraded boot-retrieval protocol.
5. Integration/deployment phases, risks, rollback, and acceptance criteria.
6. Correct authority rule: canonical Ledger on port 3003; degraded-completion spool when unavailable; no sovereign shadow/client Ledger.

Minimum: 3,000 substantive words.

### Integration deliverable

Integrate A and B, resolve cross-program dependencies, list conflicts/corrections, verify receipts, and publish an arm evidence package for Plato.

## 4. Model/runtime configuration

Frozen before timing:

- Global Orchestrator: `anthropic/claude-opus-4-6`.
- Control executor: `anthropic/claude-sonnet-4-6`.
- Program Orchestrators A/B: `anthropic/claude-sonnet-4-6`.
- Specialist pool: up to 10 `anthropic/claude-sonnet-4-6` workers available; no scale increase beyond 10.
- Independent Judge: Plato on NIETZSCHE2025, intended live Judge model recorded by Plato at execution time.
- Canonical Ledger: `http://127.0.0.1:3003`.
- MemOS database: `C:\Users\aaron\.openclaw\memos-local\memos.db`.

Control and parallel production use the same worker model class, tools, baseline, objective, evidence obligations, and acceptance standard.

## 5. Control definition

One Sonnet 4.6 executor performs A, then B, then local integration **sequentially**. No concurrent specialists. It must finalize receipts, package evidence, deliver to Plato, receive exact-hash acknowledgment, receive Plato's independent arm acceptance result, and make the result available for governed readback before its clock stops.

Prior Phase 2B-R control is historical comparison only and is not reused as the R2 control.

## 6. Parallel definition and topology

- One Global Orchestrator.
- Two semantically partitioned Program Orchestrators running concurrently.
- Up to ten specialist slots available (five per program maximum).
- Plato is the independent Judge.

Program A owns Recovery Playbook v2 and local specialist decisions. Program B owns Knowledge Brain implementation v2 and local specialist decisions. Global handles only cross-program dependencies, final integration, evidence transport, and governed readback.

Because nested spawning is unavailable, Global may instantiate specialists only on a Program Orchestrator's explicit request. The requesting Program Orchestrator retains task definition, prioritization, acceptance, and local integration authority.

## 7. Authority envelopes

- Control writes only under `PHASE-2B-R2/control-arm/` and `receipts/control-arm/`.
- Program A writes only under `parallel-arm/PROGRAM-A/` and its receipt paths.
- Program B writes only under `parallel-arm/PROGRAM-B/` and its receipt paths.
- Global writes only under `parallel-arm/global-integration/`, arm packaging, and governed state.
- Plato writes only its independent reports at the Hub/Plato workspace.
- No producer may act as Judge.
- No worker may promote the phase or modify another domain's artifact.

## 8. Semantic acceptance contract

Plato compares control and parallel outputs for required coverage, correctness, internal consistency, source fidelity, unresolved contradictions, and substantive depth. Word or artifact count alone cannot establish equivalence. Parallel must be equivalent or better overall and may not regress C, D, or G.

## 9. Signal Fire firewall

Signal Fire remains outside project execution and is not introduced merely to prove absence.

Each role receives a frozen input/context manifest. Signal Fire diary, reflection, or social content is prohibited for truth, routing, dispatch, priority, budgets, leases, capability assignment, retry/repair, promotion, or acceptance.

Required evidence:

- `SIGNAL-FIRE-FIREWALL-ATTESTATION-R2.md`
- Per-role context manifests.
- Source allowlists and prohibited-source checks.
- Integration-gate result.
- Plato verification.

## 10. Receipt finalization contract

For every terminal artifact:

1. Write to a temporary path.
2. Close and flush.
3. Atomically rename to final path.
4. Hash the finalized artifact with SHA-256.
5. Record byte count.
6. Create receipt from that exact final hash and byte count.
7. Read the finalized artifact back.
8. Recompute SHA-256 and byte count.
9. Require exact match.
10. Record verification status and detect later mutation.

Receipt fields required:

- artifact path/identity
- packet ID
- attempt ID
- generation
- baseline ID and baseline-manifest SHA-256
- byte count
- SHA-256
- creation/finalization timestamp
- producing agent
- authority envelope
- verification status

The deterministic integration gate rejects or quarantines missing artifact, size mismatch, hash mismatch, stale generation, superseded attempt, missing authority, or missing provenance.

Before timing, prove one valid receipt passes and one plausible mismatched receipt fails.

## 11. Judge identity and evidence transport

Plato is the independent Judge unless genuinely unavailable.

Before timing:

1. Publish this contract/rubric and hash.
2. Obtain Plato acknowledgment of exact experiment ID, rubric ID, and contract SHA-256.
3. Confirm Plato can reach the Hub location.
4. Record Judge READY.
5. Use delivery states precisely: PERSISTED, DELIVERED, ACKNOWLEDGED, PROCESSED.

At each arm completion:

1. Publish a sealed evidence bundle.
2. Send only locator and hashes through the preflighted path.
3. Obtain exact-hash acknowledgment.
4. Plato independently judges the arm.
5. Plato publishes a hashed report.
6. Aristotle records it only after independent readback.

If Plato is unavailable: `BLOCKED / JUDGE UNAVAILABLE`. No substitute Judge and no self-promotion.

## 12. Timing contract

For both arms record:

- time to first plausible result
- worker-stage time
- local Program integration time
- Global integration time
- evidence packaging time
- delivery/acknowledgment time
- independent Judge time
- time to accepted completion

**Governing metric:** end-to-end time to independently accepted completion.

Clock starts when an arm receives the objective. Clock stops only when Plato has accepted/adjudicated that arm and the acceptance evidence is available for governed readback.

Integration, packaging, transport, acknowledgment, and Judge time remain inside TTC. Worker-stage ratios are diagnostics only. Literal interruption time remains visible. No post-hoc metric substitution.

## 13. Context-lifecycle precondition

Before either timer starts, verify and record:

- active Aristotle execution session genuinely fresh and healthy
- effective model equals intended model
- no dead `modelOverride`
- transcript/context below safe threshold
- Ledger and MemOS operational
- correct goal pointer
- session identity recorded

If context becomes invalid during timing: preserve completed work, checkpoint frontier, rotate through supported `sessions.reset`, reconstruct, continue, and keep clock running. `/new` or `/reset` alone is not rotation proof. Historical transcript poison is not self-repaired.

## 14. Contamination rules

- No prior R2 arm output crosses into the other arm.
- No prior Phase 2B-R output enters producer context.
- No Signal Fire execution content.
- No worker conversation transcript supplied to another worker.
- Global receives only governed outputs, receipts, contract, and context manifests.
- Plato receives only sealed evidence.

## 15. Stop rules

Stop and record BLOCKED/PARTIAL when:

- receipt gate rejects and cannot be corrected before receipt issuance
- stale/superseded attempt writes
- authority boundary breach
- baseline drift
- Signal Fire contamination
- Judge unavailable
- required artifact absent
- Ledger unavailable beyond governed degraded path
- context invalid without successful governed frontier recovery

Do not rewrite the contract after timer start.

## 16. R2 pass bar

Phase 2B-R2 PASS requires all 18:

1. semantic output equivalent or better than control;
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

No alternative success criterion after the run. Worker-stage ratio, more words/artifacts, structural correctness, or preliminary self-assessment cannot independently promote the phase.

## 17. Closure rule

Final Phase 2B-R2 disposition must be based on Plato's controlling report and written through a supported governed event contract with the parent goal pointer. Phase 2C remains unauthorized regardless of R2 result until a separate owner decision.
