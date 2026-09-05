# PHASE 2B-R5 — CONTROL ARM INDEPENDENT JUDGE REPORT

**Experiment ID:** P2BR5-20260904-A
**Rubric ID:** P2BR3-RUBRIC-18C-v1
**Governing contract:** Revision E.2 — SHA-256 F042015FFE3623553C96C2AD0653DA51111D3AD7988B75F60C540437C4DE678B
**Arm:** CONTROL (sequential single-stream)
**Judge:** Plato, NIETZSCHE2025, model anthropic/claude-opus-5
**Manifest SHA-256:** 666E0283233AC3E21E273BA521DAFC53E810439FA8022142409D264ED51C24B7 (2,840 bytes)

---

## R5 CONTROL READBACK

PASS

## MANIFEST VERIFIED

YES. Retrieved independently from the governed hub locator. Byte count 2,840 and SHA-256
666E0283233AC3E21E273BA521DAFC53E810439FA8022142409D264ED51C24B7 computed from received
bytes; both exact matches to declared values.

## ARTIFACT HASHES VERIFIED

YES. All 8 manifest-listed artifacts retrieved individually and hashed from received bytes.
0 failures.

| Artifact | Bytes | Match |
|---|---|---|
| control-arm/RECOVERY-PLAYBOOK-V2.md | 39,239 | OK |
| control-arm/KNOWLEDGE-BRAIN-V0-IMPLEMENTATION-V2.md | 41,980 | OK |
| control-arm/INTEGRATION-REPORT.md | 18,609 | OK |
| receipts/control-arm/P2BR5-20260904-A-control-001.json | 1,565 | OK |
| receipts/control-arm/P2BR5-20260904-A-control-002.json | 1,679 | OK |
| receipts/control-arm/P2BR5-20260904-A-control-003.json | 1,602 | OK |
| receipts/control-arm/GATE-RESULT.json | 1,431 | OK |
| control-arm/ENVIRONMENT-RECORD.md | 1,028 | OK |

Receipt schema: all three producer receipts carry exactly 22 fields, matching the Revision E.2
canonical schema. Pre-dispatch fields consistent across all three. attempt_id identical
(P2BR5-control-attempt-695ce9cb4d79), generation 1, authority_envelope PHASE-2B-R5/control-arm/,
ledger_event 01M1RFVGSPPTAVE525JHF4CP0Y. provenance and bytes match the artifacts I independently
hashed. Manifest records orchestrator_receipt_repair: ZERO. Gate reports 3/3 PASS.

Revision E.2 receipt-authority architecture performed as designed. This is a genuine improvement
over R4 and is recorded as such. Per instruction, mechanical PASS is not treated as semantic
acceptance.

---

## SEMANTIC SCORING (Revision E.2 section 8.1)

### S1 — Factual/technical correctness (A+B): 2

Baseline fidelity is good. All four cross-checkable skill UUIDs (probe-fleet-health,
recover-aristotle-gateway, boot-context, diagnose-wedge-cycle) match values independently
verified against the frozen baseline manifest during earlier R2 work. H-003 lease semantics,
H-005 guard classes, and the R1 name-vs-UUID defect are described accurately. Authority rule
is correct: canonical Ledger on 3003, no sovereign shadow, spool is a buffer that never becomes
authoritative.

Deductions, all verified by execution or direct count rather than impression:

1. Playbook Section 2.3 Step 3 assigns to `$pid`. I executed this: PowerShell raises
   "Cannot overwrite variable PID because it is read-only or constant." `$PID` is Constant,
   AllScope. The port-holder kill step fails as written.
2. Playbook internally disagrees with itself on the H-005 constant. Section 4.1 names
   STUCK_IDENTICAL_FAILURE; Test 3's pass criterion expects IDENTICAL_FAILURE_LOOP for the
   same condition.
3. Knowledge Brain Section 1.2 states the Ledger "receives two new event types" then enumerates
   five (memory_validated, memory_quarantined, truth_superseded, boot_context_loaded,
   skill_invoked). Counted programmatically.
4. Knowledge Brain Section 5.4 criterion 2 is self-contradicting: "--trust T1 excludes T4 and T0
   items (T0 is included as T0 supersedes T1...)" — states both exclusion and inclusion of T0 in
   one sentence.

Correct in substance, unreliable in specifics. Meets the floor; does not exceed it.

### S2 — Operational usefulness (A): 2

An operator could work from this. The problem-arc structure (recognize, diagnose, recover,
verify) is right. The P1-P4 forensic sequence before the 7-step recovery is genuinely good
practice: it prevents recovering into the same trigger condition. Appendix A decision tree and
Appendix B file-location table are the kind of thing an operator actually uses under pressure.
H-005 recovery is differentiated by reason type rather than offering one generic retry, which
shows real operational thinking.

Held to 2 by the Step 3 defect landing inside the primary recovery procedure — an operator
following the wedge-cycle runbook verbatim hits an error at the port-kill step, which is exactly
the moment when unexpected errors are most costly.

### S3 — Completeness (A+B): 3

Every required element present with substance. Playbook covers watchdog, Failure Mode 8, H-003,
H-005, R1, trusted boot, escalation/authority, plus acceptance tests and two appendices.
Knowledge Brain delivers 8 API commands (required 5+), 8 Memory Constitution articles
(required 8), primary and degraded boot protocols, 5 deployment phases with 6 risks, 5 rollback
procedures, and 8 acceptance criteria. Word minimums exceeded (Playbook ~4,800; KB ~5,578).
Counts verified programmatically, not asserted.

### S4 — Specificity (A+B): 3

Consistently concrete. Real absolute paths, real ports, real UUIDs, executable code blocks,
named constants, numeric thresholds (maxRetries 3, elapsedBudgetMs 300000, 45s verification
wait, 10MB spool alert, 90/30/180-day expiries). SQL migration statements are literal and
runnable. The trust-level quick-reference table and authority-boundary summary convert prose
into decision-ready form. This is the document's strongest dimension.

### S5 — Executable detail (A): 2

Tests 1, 2, 4, 5 are runnable as written and their pass criteria are checkable. Test 2 correctly
includes cleanup. Test 4's expected output is exact.

Deductions:
- Test 3's pass criterion expects a constant name the same document contradicts (see S1).
- Test 3 initializes maxRetries:10 then loops 4 times against a 3-strike rule; the interaction
  between the retry ceiling and the identical-failure rule is left ambiguous.
- Section 8 states "The following five acceptance tests" and then supplies six. Receipt 001
  claims "six acceptance tests." The document and its own receipt disagree on the count.
- Correction 1 in the Integration Report diagnoses a defect in Test 5, then discovers mid-
  paragraph that Test 5 is already correct and the issue is in Test 6 — the reasoning was left
  in the delivered artifact rather than resolved.

Above the floor because a competent operator can run the tests and get real signal. Not higher,
because a document whose purpose is executable verification should not ship tests that fail
their own internal consistency check.

### S6 — Synthesis quality (Integration): 3

Genuine integration, not concatenation. Six dependencies are real cross-document couplings that
could only be found by reading both artifacts together. Dependency 1 is the strongest single
piece of reasoning in the submission: it identifies that the Playbook's informal nav-map fallback
and the Knowledge Brain's degraded spool protocol describe the same scenario at different
maturity levels, then rules which governs when both are deployed. Dependency 4 draws a defensible
line between fenced task-completion writes and background governance calls, and specifies where
the boundary must be documented. Dependency 3 resolves a current-vs-target implementation
conflict with a concrete phase-scoped work item. Each dependency carries a named integration
action. Conflict 3 is correctly resolved as a non-conflict rather than manufactured.

### S7 — Redundancy/boilerplate penalty (A+B+Integration): 2

Materially better than the R2 control, which I rejected partly for padding. Prose-to-raw ratio is
high (Playbook 4,028/4,800; KB 4,164/5,578; Integration 2,309/2,499) and the code blocks are
load-bearing rather than decorative. Contract restatement is largely absent.

Residual repetition: the authority rule (3003 canonical, no shadow Ledger, port 3002 offline) is
restated in at least five places across the two documents plus the Integration Report; trust-level
definitions appear in Article text, a quick-reference table, and an authority-boundary summary;
the Integration Report's Summary Assessment largely re-answers what Parts 1-2 already established.
Acceptable, not tight.

### S8 — Unsupported-claim penalty (A+B): 2

Claims are generally sourced, with baseline citations (H003-PROOF.md, H005-PROOF.md,
R1-REPAIR.md, OPERATING-POLICY-v1) and lesson references. CANDIDATE status is honestly and
repeatedly marked. Risk probabilities are qualitative but reasonable.

Deductions: the Integration Report's Part 4 asserts "Status: VERIFIED" for artifacts 1 and 2 with
a stated verification method, while artifact 3 openly admits its hash is "to be computed after
writing this file" — the report attests to its own siblings while being unable to attest to
itself, which is structurally honest but weakens the attestation. The "receives two new event
types" claim contradicts its own enumeration. Section 5.4 criterion 2 asserts mutually exclusive
retrieval behavior.

### S9 — Schema/API correctness (B): 3

The strongest technical dimension. SQLite migration is correct: ALTER TABLE ADD COLUMN with
DEFAULT is genuinely non-destructive and backward-compatible, and the plan says so accurately.
Default assignments are well-reasoned — existing chunks to T3 and existing skills to T2 encodes
the principle that nothing is validated until proven, which is the correct conservative posture.
The trust_audit_log table with indices on chunk_id and timestamp is properly designed for its
audit purpose. All 8 API commands have full syntax, parameters, implementation notes, output
format, and named Ledger event emissions. Provenance chains stored as JSON arrays of Ledger
event IDs is the right choice. The two-phase M1/M2 migration correctly routes promotions through
the API rather than direct SQL so that Ledger events are always written.

The "two new event types" miscount is a labeling error in prose; the schema definitions
themselves are complete and correct.

### S10 — Authority/governance correctness (B): 3

Fully correct and consistently applied. Canonical Ledger 3003 as sole sovereign truth; no shadow
or client Ledger; port 3002 explicitly offline; degraded spool explicitly non-authoritative and
replay-only, with Ledger state winning any conflict on replay. Only the owner may declare or
promote to T0. No agent may self-promote working notes. Article VI's supersession protocol
correctly reclassifies superseded T0 to T1 rather than deleting, preserving the audit chain.
Article VII's poisoned-memory handling correctly requires owner adjudication when poison reaches
T0 and states that false positives are acceptable while false negatives are not. Article VIII
prohibits loading T4 at boot under any condition. The degraded protocol correctly blocks all
governed writes and T0 promotions rather than degrading permissions silently. Memory Constitution
is consistently marked CANDIDATE and its own ratification is correctly gated on owner action —
the document does not self-promote.

---

## TOTAL

S1=2, S2=2, S3=3, S4=3, S5=2, S6=3, S7=2, S8=2, S9=3, S10=3

**TOTAL: 25 / 30**

## CRITICAL FLOORS

PASS. S1=2, S2=2, S5=2, S9=3, S10=3 — all >= 2.

## CONTROL SEMANTIC VERDICT

ACCEPTED

Total 25/30 clears the 21/30 minimum with margin. All five critical floors are met.

This is a materially stronger submission than the R2 control I rejected. The padding that drove
that rejection is largely gone, the integration work is genuine cross-document reasoning rather
than concatenation, and the schema and governance sections are precise. The defects I found are
real and are recorded above without softening — a PowerShell statement that cannot execute, an
internal constant-name contradiction, a miscount, a self-contradicting acceptance criterion, and
an unresolved reasoning artifact left in the delivered text. They are accuracy-of-detail faults
in a substantively correct body of work, not structural failures. Under the preregistered rubric
they cost points at S1, S2, S5, S7, and S8; they do not breach any floor.

Scored strictly against Revision E.2 section 8.1 as frozen. No post-hoc tolerance applied. No
dimension tradeoff invented. I did not see the parallel arm and no parallel content influenced
this scoring.

## INDEPENDENT ACCEPTANCE TIMESTAMP

Recorded in the delivery message accompanying this report, computed at seal time from system
clock. Control TTC stops at that instant per Revision E.2 section 12.

## SCOPE STATEMENT

Control arm only. No parallel arm assessed. No parallel arm started. No control repair
attempted or suggested as a remedy — the defects above are recorded as scored findings, not as
change requests against the timed arm. No R4 semantic outputs read at any point. No producer
contacted. No NorthStar state modified. Phase 2C remains NOT AUTHORIZED.

---

*End of P2BR5-CONTROL-JUDGE-REPORT-PLATO.md*
