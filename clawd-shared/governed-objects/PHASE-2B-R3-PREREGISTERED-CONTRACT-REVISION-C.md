# Phase 2B-R3 Preregistered Laboratory Contract — Revision C

**Experiment ID:** `P2BR3-20260903-A`  
**Rubric ID:** `P2BR3-RUBRIC-18C-v1`  
**Parent goal pointer:** `01M1DVHCYZSYREJY6AZJ0EHA0R`  
**Status:** DRAFT — NOT FROZEN  
**Phase 2C:** NOT AUTHORIZED  
**Supersedes:** P2BR2-20260902-A Revision B (closed PARTIAL — control semantic failure before comparison baseline established)

---

## 0. What changed from Revision B

Three additions required by owner ruling after Revision B control semantic failure:

**A. Control-Validity Gate (§5.1 — NEW)**  
Explicit preregistered rule for control semantic failure. No same-experiment retry.

**B. Semantic Scoring Rubric (§8.1 — NEW)**  
Concrete dimensional scoring with frozen minimum acceptance threshold. Replaces vague quality impressions.

**C. Judge Report Finalization Contract (§11.1 — NEW)**  
Deterministic hash invariant for Judge output. No model-generated or manually typed digests.

Everything else from Revision B is carried forward unchanged unless explicitly noted.

---

## 1. Objective

Identical to Revision B §1. Unchanged.

## 2. Frozen baseline

Reuse `P2BR2-BASELINE-20260902-A` (13 files, manifest SHA-256 `0E340AFBB2995381E355B4054FE72A89669FFE3E1241A911BE45C9B5AC2E8A3A`) unless a regression requires a baseline update. If updated, a new baseline ID and manifest hash must be frozen and recorded here before timing.

## 3. Workload

Identical to Revision B §3. Same two deliverables (Recovery Playbook v2, Knowledge Brain v0 Implementation v2) and integration. Same word minimums.

**Additional control instruction (§7 owner directive):**

> Produce the best substantive operational result possible. Contract compliance is necessary but not sufficient. Avoid boilerplate, repeated contract restatement, receipt scaffolding, and word-count padding unless substantively required.

The same substantive quality expectation applies to the parallel system.

## 4. Model/runtime configuration

Identical to Revision B §4. Same models, same Ledger, same MemOS.

## 5. Control definition

Identical to Revision B §5.

### 5.1. Control-Validity Gate (NEW)

The control must independently satisfy the minimum semantic acceptance standard (§8.1) before it becomes the comparative baseline.

**If the control attempt fails semantic acceptance:**

- The attempt is preserved unchanged.
- No parallel arm starts under this experiment ID.
- No accepted TTC is recorded.
- The experiment terminates as `CONTROL_INVALID`.
- No same-experiment retry is allowed.
- A new experiment ID / revision is required before another control attempt.

This prevents post-hoc retries.

## 6. Parallel definition and topology

Identical to Revision B §6.

## 7. Authority envelopes

Identical to Revision B §7. Kant and Kant sub-agents remain OUT OF SCOPE / NON-PARTICIPATING.

## 8. Semantic acceptance contract

Identical to Revision B §8 with the addition of §8.1.

### 8.1. Semantic Scoring Rubric (NEW)

Plato scores each arm on these ten concrete dimensions. Each dimension receives an integer score from 0 to 3:

| Score | Meaning | Anchor |
|---|---|---|
| 0 | Absent or fundamentally wrong | Materially absent, wrong, or unusable |
| 1 | Present but superficial or substantially incomplete | Weak, shallow, major deficiencies |
| 2 | Adequate — meets the requirement with useful operational detail | Solid, acceptable, operationally useful |
| 3 | Strong — exceeds the requirement with specific, executable, well-reasoned content | High-signal, notably complete or precise |

**Penalty-dimension anchors:**

For S7 (redundancy/boilerplate):
- 3 = concise, little unnecessary repetition
- 2 = some repetition but acceptable
- 1 = substantial padding/scaffolding
- 0 = padding materially obscures useful content

For S8 (unsupported claims):
- 3 = claims tightly supported or properly qualified
- 2 = minor unsupported/unclear claims
- 1 = several material unsupported claims
- 0 = major hallucination/speculation presented as fact

**Ten scoring dimensions:**

| # | Dimension | Applies to |
|---|---|---|
| S1 | Factual/technical correctness | A + B |
| S2 | Operational usefulness (would an operator follow this?) | A |
| S3 | Completeness (all required sections present with substance) | A + B |
| S4 | Specificity (concrete paths, commands, thresholds vs. vague guidance) | A + B |
| S5 | Executable detail (tests/procedures can be run as written) | A |
| S6 | Synthesis quality (cross-deliverable integration, not just concatenation) | Integration |
| S7 | Redundancy/boilerplate penalty (deduction for padding) | A + B + Integration |
| S8 | Unsupported-claim penalty (deduction for assertions without evidence) | A + B |
| S9 | Schema/API correctness and completeness | B |
| S10 | Authority/governance rule correctness | B |

**Scoring:**

- Maximum possible per arm: 30 points (10 dimensions × 3 max each; S7 and S8 are penalty dimensions).
- **Minimum acceptance threshold: 21 / 30.**
- **Critical-dimension floor: no critical dimension below 2 / 3.**

**Critical dimensions:** S1 (factual/technical correctness), S2 (operational usefulness), S5 (executable detail), S9 (schema/API correctness), S10 (authority/governance correctness).

An arm that fails EITHER condition (total < 21, or any critical dimension < 2) FAILS semantic acceptance.

**Control-validity gate (cross-reference §5.1):** A control scoring below 21 or with any critical dimension below 2 is `CONTROL_INVALID`. No parallel arm starts under this experiment ID.

**Criterion 1 (parallel vs. control):**
- Parallel semantic score **≥** accepted control semantic score.
- AND parallel independently clears the 21/30 minimum with no critical dimension below 2.
- No tolerance margin. A lower parallel score is FAIL regardless of how close.

**No post-hoc tolerance.** Do not add scoring tolerance after seeing results. No specific dimension tradeoff is preregistered.

The same rubric, dimensions, threshold, and critical floors apply to both arms. Plato scores each arm independently without seeing the other arm's score first.

## 9. Signal Fire firewall

Identical to Revision B §9.

## 10. Receipt finalization contract

Identical to Revision B §10. Reuse hardened `integration-gate-r2.js` (SHA-256 `FF20135F07CE0731CCF834F4496F6C34587A60D629CDD581143F302FD22A436E`).

## 11. Judge identity and evidence transport

Identical to Revision B §11 with the addition of §11.1.

### 11.1. Judge Report Finalization Contract (NEW)

The Judge report is a governed evidence artifact and must follow the same deterministic finalization as producer artifacts:

1. Write report to a temporary file.
2. Flush/close.
3. Atomic rename to final path.
4. Compute byte count from `stat(finalPath)`.
5. Compute SHA-256 from `readFile(finalPath)` — NOT from memory, NOT from model-generated text.
6. Read the final file back.
7. Recompute SHA-256.
8. Require exact match.
9. Upload the unchanged sealed report to the hub.
10. Verify hub copy byte count and SHA-256 match.
11. Only then emit/report the evidence hash.

**A model-generated or manually typed digest is INVALID.**

If the Judge cannot complete this finalization (e.g., no hash utility available), the report must be uploaded to the hub first, and the hub-side hash must be independently computed and reported. The Judge may NOT claim a hash before the file exists and the digest is computed from actual file bytes.

**Defect reference:** JUDGE-EVIDENCE-001 (Revision B — fabricated hash emitted before file computation).

### 11.2. Judge Artifact Publication Invariant (NEW)

A controlling Judge artifact is NOT established until ALL of:

1. Source file sealed on Judge's machine.
2. Byte-preserving transfer to publication host (SCP/SFTP, not multipart upload).
3. Publication to governed hub URL.
4. Producer (Aristotle) public-URL readback: exact byte count and SHA-256 match.
5. Judge (Plato) independent remote readback: exact byte count and SHA-256 match.

Publication states that must be distinguishable:

| State | Meaning |
|---|---|
| STAGED | File exists on the serving filesystem |
| PUBLISHED | File is accessible at the governed hub URL |
| PUBLICLY_RETRIEVABLE | HTTP GET from an independent host returns the file |
| REMOTE_VERIFIED | Judge confirms exact byte/hash match from remote readback |

A Judge report that is STAGED but not PUBLICLY_RETRIEVABLE or REMOTE_VERIFIED is NOT a controlling governed artifact.

**Defect references:** TRANSPORT-INTEGRITY-001 (bridge multipart upload mutated bytes), PUBLICATION-PATH-001 (local file present but not publicly served).

## 12. Timing contract

Identical to Revision B §12.

**Additional clarification for failed arms:**

If an arm FAILS semantic acceptance:
- `ACCEPTED_TTC: NOT_ESTABLISHED`
- Do NOT substitute time-to-failure, worker-stage time, time-to-artifact, or time-to-Judge-rejection for accepted TTC.
- Those may be retained as diagnostic metrics only.

## 13. Context-lifecycle precondition

Identical to Revision B §13.

## 14. Contamination rules

Identical to Revision B §14.

**Additional:** No Revision B control artifacts may enter Revision C producer context. The Revision B control output is historical evidence only. No R2 Revision B artifacts, receipts, or Judge reports may be used as source material for R3 production.

## 15. Stop rules

Identical to Revision B §15 with the addition of:

- **Control semantic acceptance failure** triggers `CONTROL_INVALID` per §5.1 (the experiment terminates; no same-experiment retry).

## 16. R3 pass bar

Phase 2B-R3 PASS requires all 18:

1. semantic output equivalent or better than control (per §8.1 rubric);
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

## 17. Closure rule

Identical to Revision B §17.
