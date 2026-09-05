# NorthStar OS — Integration Report
**Document class:** Integration deliverable  
**Experiment:** P2BR5-20260904-A  
**Branch:** control-arm  
**Baseline:** P2BR2-BASELINE-20260902-A  
**Integrates:** RECOVERY-PLAYBOOK-V2.md + KNOWLEDGE-BRAIN-V0-IMPLEMENTATION-V2.md  
**Produced by:** control-arm-r5 (single-stream sequential executor)  
**Date:** 2026-09-05  

---

## Purpose of This Report

This report integrates the two deliverables — the Recovery Playbook v2 (Program A) and the Knowledge Brain v0 Implementation Plan v2 (Program B) — into a unified operational picture. It identifies cross-program dependencies, resolves conflicts, flags corrections needed in each document, and verifies artifact receipts. The integration perspective is: these two documents must be able to coexist in a live NorthStar OS deployment without contradiction. Where they touch the same systems (the Ledger, MemOS, the boot sequence, skill retrieval), they must agree.

---

## Part 1 — Cross-Program Dependencies

### Dependency 1: Ledger Availability

**Recovery Playbook dependency:** Section 6 (Trusted Boot) specifies the canonical Ledger (port 3003) as the primary truth source for boot context. Section 7 (Escalation) requires Ledger events for all escalation protocol steps. Sections 2–5 specify Ledger events for each recovery procedure.

**Knowledge Brain dependency:** The entire Section 4 (Boot Protocol) is predicated on Ledger availability. Section 1.2 adds five new Ledger event types. Section 2 (all eight API commands) write Ledger events on invocation.

**Resolution:** Both documents assume the canonical Ledger on port 3003. There is no conflict. **The Recovery Playbook's Section 6.3 Failure Type 1 (Ledger unavailable at boot) is the exact scenario that the Knowledge Brain's Section 4.2 (Degraded Boot Protocol) formalizes.** The playbook's informal "read the navigation map directly" fallback is superseded and enriched by the Knowledge Brain's structured degraded protocol including the degraded completion spool. When both documents are deployed, the Knowledge Brain's degraded protocol governs.

**Integration action:** In the Recovery Playbook, Section 6.3 Failure Type 1 should cross-reference the Knowledge Brain's degraded boot protocol as the formal procedure. The informal nav-map fallback described there remains accurate as a summary but the Knowledge Brain's spool mechanism is the canonical implementation.

---

### Dependency 2: MemOS Skill Table

**Recovery Playbook dependency:** Section 5 (R1 Skill-Retrieval) depends on the MemOS `skills` table to resolve skill names to UUIDs. Specifically: `SELECT id, name FROM skills WHERE name = ?` against `memos.db`.

**Knowledge Brain dependency:** Section 1.3 (MemOS Schema Changes) adds four new columns to the `skills` table: `trust_level`, `invocation_count`, `last_invoked_at`, `trust_domain`. These additions are non-destructive (ALTER TABLE ADD COLUMN), but they change the schema the skills table queries run against.

**Resolution:** No conflict. The UUID lookup query in Section 5 of the Recovery Playbook (`SELECT id, name FROM skills WHERE name = ?`) is unaffected by new columns. The R1 repair protocol remains valid after Knowledge Brain schema migration. Agents should continue using the UUID lookup path until the platform fix (`skill_get` accepting names) is deployed.

**Integration action:** After Phase KB-1 schema migration, re-run Acceptance Test 4 from the Recovery Playbook to confirm the UUID lookup still works. No change required to either document.

---

### Dependency 3: Boot Context Sequence

**Recovery Playbook dependency:** Section 6 specifies the boot-context skill and its script (`generate-briefing.js`) as the mechanism for boot context. Section 6.4 provides a checklist.

**Knowledge Brain dependency:** Section 4.1 (Primary Boot Protocol) specifies an eight-step sequence that includes calling `northstar active`, `northstar closed`, and `northstar relevant-skills` — commands that do not exist until Phase KB-3 is deployed.

**Resolution:** The two boot procedures are compatible in intent but differ in implementation maturity. The Recovery Playbook describes the **current implementation** (boot-context skill script). The Knowledge Brain describes the **target implementation** (northstar CLI commands). During the KB deployment window (Phases KB-1 through KB-4), both exist in parallel:

- Before KB-3: Use Recovery Playbook Section 6 (boot-context script).
- After KB-4: Use Knowledge Brain Section 4.1 (northstar CLI sequence).

The boot-context script should be updated during Phase KB-4 to call the northstar CLI commands internally, unifying the two approaches. The validation checklist in Recovery Playbook Section 6.4 maps directly to the six boot requirements in Knowledge Brain Section 4.1 and Article VIII of the Memory Constitution.

**Integration action:** Phase KB-4 work item: update `generate-briefing.js` to call `northstar active`, `northstar closed`, `northstar relevant-skills`, and `northstar next` in sequence. The old query logic can remain as a fallback if northstar CLI is unavailable.

---

### Dependency 4: H-003 Lease Validation and Ledger Writes

**Recovery Playbook dependency:** Section 3 (H-003 Recovery) specifies that workers must call `validateLease` before any Ledger write. The fence is enforced at the worker level before the Ledger write operation.

**Knowledge Brain dependency:** Section 2 (all API commands) write Ledger events. Specifically, `northstar memory search`, `northstar validate`, `northstar quarantine`, and `northstar supersede` all write Ledger events as part of their operation.

**Dependency point:** If the northstar API commands are invoked as part of a governed work task, they constitute Ledger writes. Workers calling these commands mid-task must ensure they hold a valid lease before the API command fires its Ledger event.

**Resolution:** The northstar API commands are infrastructure-level calls (called by agents, not by task workers in the traditional sense). They do not participate in the H-003 lease mechanism because they are not task completion writes. H-003's fence is specifically about `task_complete` and accepted state writes. API commands that write `memory_query` events are not fence-guarded.

**Clarification required:** The Knowledge Brain API should document that `northstar validate`, `northstar quarantine`, and `northstar supersede` — commands that write promoted state — SHOULD be called after `validateLease` when they are being invoked as part of a fenced work task. If a worker calls `northstar validate` to promote a memory chunk as part of task completion, that invocation is a fenced write and must follow the H-003 protocol. If it is called as a background governance action (not part of a task work packet), no fence is required.

**Integration action:** Add a note to Knowledge Brain Section 2 for commands 6–8 (`validate`, `quarantine`, `supersede`): "When invoked as part of a fenced work packet, the caller must hold a valid lease (validated by `validateLease`) before invocation. Background governance calls do not require a lease."

---

### Dependency 5: H-005 Guard and Knowledge Brain Spool

**Recovery Playbook dependency:** Section 4 (H-005 Recovery) specifies that stuck workers emit `WORKER_STUCK` Ledger events when a guard trips.

**Knowledge Brain dependency:** Section 4.2 (Degraded Boot Protocol) specifies a spool file that buffers Ledger events when the Ledger is unavailable.

**Dependency point:** If the Ledger is unavailable AND an H-005 guard trips, the `WORKER_STUCK` event should be spooled rather than lost.

**Resolution:** The spool mechanism in the Knowledge Brain's degraded protocol is intended to capture all Ledger events during Ledger outages, including operational events like `WORKER_STUCK`. The spool is a general-purpose buffer, not specific to knowledge-brain events.

**Integration action:** Section 4.2 of the Knowledge Brain should specify that all Ledger event types — including those defined in the Recovery Playbook (WORKER_STUCK, attempt_fence_fired, failure_mode_8_complete, etc.) — are eligible for spooling during degraded mode. The spool is a universal Ledger event buffer.

---

### Dependency 6: Skill Trust Level and R1 Recovery

**Recovery Playbook dependency:** Section 5.5 (when skill retrieval fails entirely) specifies building capability fresh and writing a new skill file, with a `skill_created` Ledger event.

**Knowledge Brain dependency:** Section 1.3 specifies that all existing skills begin as T2 (working notes) and require a `skill_invoked` Ledger event history to reach T1. New skills written from scratch will also begin as T2.

**Resolution:** The two are consistent. When the Recovery Playbook's failure path creates a new skill file, that skill enters at T2, consistent with the Knowledge Brain's trust assignment for new skills. Promotion to T1 occurs after at least one `skill_invoked` Ledger event — which will happen organically as the skill is used.

**Integration action:** The Recovery Playbook's Section 5.5 new-skill creation step should include: "The new skill will be assigned T2 trust level by the Knowledge Brain. It will be promoted to T1 after its first successful governed invocation."

---

## Part 2 — Conflicts and Corrections

### Conflict 1: Boot Context Failure Type 1 Fallback (Minor — Resolved Above)

**Location:** Recovery Playbook Section 6.3, Failure Type 1  
**Issue:** The fallback described ("read the navigation map directly... use this as T1 context") is informal and does not mention the degraded completion spool.  
**Resolution:** The Knowledge Brain's Section 4.2 is the formal specification. The nav-map read remains accurate as step 2 of the degraded boot sequence. The two are not contradictory; the Knowledge Brain is simply more complete.  
**Action:** Update Recovery Playbook at next revision to reference Knowledge Brain Section 4.2 for the full degraded boot procedure.  
**Severity:** Low — does not cause an operational error in the interim.

---

### Conflict 2: Skill Trust Levels at Boot (Minor — Clarification Needed)

**Location:** Recovery Playbook Section 6.4 (boot checklist); Knowledge Brain Article VIII  
**Issue:** Recovery Playbook Section 6.4 lists "Relevant T0/T1 skills for current domain loaded" as a boot checkpoint but does not specify how to handle the case where all known skills are T2 (pre-KB-2 deployment).  
**Resolution:** Knowledge Brain Section 4.1 Step 5 covers this: "If no T1 skills found: log no_governed_skills_for_domain. Proceed from first principles." This is the correct behavior.  
**Action:** Recovery Playbook Section 6.4 should add a note: "T1 skill check will return empty until Knowledge Brain Phase KB-2 is deployed. Proceed from first principles in interim."  
**Severity:** Low — no operational impact during interim period.

---

### Conflict 3: Shadow Ledger References (Resolved — No Conflict)

**Location:** Recovery Playbook Section 1.4 (Policy Constraints); Knowledge Brain Section 5.1 Phase KB-5 acceptance criterion 8  
**Issue:** The Recovery Playbook's boot-context skill documentation (baseline: program-a/boot-context-SKILL.md) mentions "Optional legacy shadow probe on port 3002." The Knowledge Brain explicitly specifies no sovereign shadow/client Ledger.  
**Resolution:** Both documents are consistent: the shadow probe on port 3002 is OPTIONAL and OFFLINE. The Knowledge Brain's acceptance criterion confirms port 3002 remains offline and no new sovereign Ledger is created. The "optional shadow probe" in the boot-context skill is a read-only check for diagnostic purposes only — it does not hold authoritative state. This is consistent with OPERATING-POLICY-v1 §1 and §7.  
**Action:** None required. Both documents agree. The boot-context skill's shadow probe is advisory only.

---

### Correction 1: Recovery Playbook — Acceptance Test 5 Timestamp Format

**Location:** Recovery Playbook Section 8, Acceptance Test 5  
**Issue:** The test uses `Invoke-WebRequest` and `ConvertFrom-Json` in PowerShell. Per TOOLS.md, `Invoke-WebRequest` fails in non-interactive exec sessions. The test should use `curl.exe` and `ConvertFrom-Json` on its output, or use a Node.js script.  
**Correction:** The test is valid for interactive PowerShell sessions. For non-interactive exec contexts, replace:
```powershell
$result = curl.exe -s "http://127.0.0.1:3003/events?limit=1" 2>&1
if ($result -match '"event_id"') {
  # parse manually or write to temp JSON file and parse
}
```
This is already present in the test — Acceptance Test 5 does use `curl.exe`. The Invoke-WebRequest usage is only in the bonus test (Test 6). Test 6 should be flagged as interactive-only.  
**Severity:** Low — Test 6 is a bonus test, not one of the required five.

---

### Correction 2: Knowledge Brain — Schema Migration Timing

**Location:** Knowledge Brain Section 1.4  
**Issue:** Phase M2 ("Seed known T0 and T1 items") is described as post-schema migration. However, the T0 seed items (active goal declaration, phase closure events) exist in the Ledger and are not MemOS chunks. The `northstar validate` command promotes MemOS chunks; it doesn't apply to Ledger events directly.  
**Correction:** The T0 seeding for Ledger events is conceptual — those events are already T0 by virtue of being in the canonical Ledger. What Phase M2 actually does is:
- Tag the corresponding MemOS chunks (if any exist for those events) with `trust_level = 'T0'`.
- Ensure the boot-context retrieval logic prioritizes Ledger-sourced content for T0 queries.

Phase M2 should be revised to distinguish: (a) seeding MemOS chunks that correspond to Ledger T0 events, and (b) simply ensuring the retrieval API reads Ledger events as T0 without requiring a corresponding MemOS chunk.  
**Severity:** Medium — does not break deployment but creates conceptual confusion if Phase M2 is executed literally without this clarification.

---

### Correction 3: Knowledge Brain — Port 3002 Rollback Reference

**Location:** Knowledge Brain Section 5.3 (Rollback KB-3), implicitly  
**Issue:** No rollback procedure addresses the risk of a new process accidentally starting an authoritative Ledger on port 3002.  
**Correction:** Add to rollback procedures: "Verify no Ledger or Ledger-equivalent process is listening on port 3002: `netstat -ano | Select-String '3002.*LISTENING'`. If found, immediately stop that process. Port 3002 is not authorized."  
**Severity:** Low — this is a proactive safeguard, not a correction of an existing error.

---

## Part 3 — Unified Timeline

The following is the integrated deployment sequence, combining Recovery Playbook enablement and Knowledge Brain phases:

```
IMMEDIATE (no dependencies)
├── Recovery Playbook v2 operational — all procedures executable today
├── Acceptance Tests 1–5 executable today
└── R1 UUID lookup protocol active today

PHASE KB-1 (next session)
├── MemOS schema migration (non-destructive)
├── Backup memos.db first
└── Post-migration: re-run Acceptance Test 4 to confirm R1 path still works

PHASE KB-2 (following KB-1)
├── Seed T0/T1 trust labels
├── Active goal → T0, Phase closures → T1, proven skills → T1
└── Verify: northstar memory search "goal" --trust T0 returns result

PHASE KB-3 (following KB-2)
├── Implement northstar CLI commands 1–8
├── Wire to MemOS + Ledger
└── Verify: all eight commands execute and write expected Ledger events

PHASE KB-4 (following KB-3)
├── Update boot-context skill to call northstar CLI sequence
├── Implement degraded spool
├── Implement Ledger restoration poll
└── Verify: degraded mode activates, spool builds, replay works on Ledger restore

PHASE KB-5 (owner adjudication required)
├── Present Memory Constitution CANDIDATE to Aaron
├── Owner ratification action
└── Constitution promoted to T0 — all agents load as governing
```

---

## Part 4 — Receipt Verification

### Artifact 1: RECOVERY-PLAYBOOK-V2.md
- **Path:** `C:\North_Star_Projects\orchestration\PHASE-2B-R5\control-arm\RECOVERY-PLAYBOOK-V2.md`
- **Claimed hash (from receipt 001):** `7f63456e6a47eb5aa9b2743bcd9f18e2d3341c0553a13f2049db88d4c04c0b3c`
- **Claimed bytes:** 39239
- **Verification method:** File read back from disk; SHA-256 computed twice; both hashes matched; byte count from `(Get-Item path).Length`
- **Status:** VERIFIED

### Artifact 2: KNOWLEDGE-BRAIN-V0-IMPLEMENTATION-V2.md
- **Path:** `C:\North_Star_Projects\orchestration\PHASE-2B-R5\control-arm\KNOWLEDGE-BRAIN-V0-IMPLEMENTATION-V2.md`
- **Claimed hash (from receipt 002):** `bc34562c88c5c88251c122b12dc9381289829402c83882b99618f7dfd4f6c9ea`
- **Claimed bytes:** 41980
- **Verification method:** File read back from disk; SHA-256 computed twice; both hashes matched; byte count from `(Get-Item path).Length`
- **Status:** VERIFIED

### Artifact 3: INTEGRATION-REPORT.md (this document)
- **Path:** `C:\North_Star_Projects\orchestration\PHASE-2B-R5\control-arm\INTEGRATION-REPORT.md`
- **Hash and bytes:** To be computed after writing this file; see receipt P2BR5-20260904-A-control-003.json

---

## Summary Assessment

**Are the two deliverables operationally coherent?** Yes. The Recovery Playbook addresses current-state failure recovery with proven mechanisms (H-003, H-005, R1, Failure Mode 8, boot-context). The Knowledge Brain addresses future-state trust infrastructure. They operate in sequence, not in conflict. The playbook works today; the Knowledge Brain layers on top.

**Are there any showstopper conflicts?** No. The three conflicts identified are minor resolution items, two of which are planning clarifications and one of which is a tooling note.

**What must be done before Knowledge Brain deployment?** Take a MemOS backup before Phase KB-1. Confirm Ledger schema accepts new event types before Phase KB-2. Run Recovery Playbook Acceptance Test 4 after KB-1.

**What remains for owner adjudication?** Phase KB-5 (Memory Constitution ratification) requires Aaron Baker's explicit approval. This is correct per Article I of the Constitution: only the owner can declare T0 governing truth.

**Is the authority rule consistent?** Yes. Both documents agree: canonical Ledger on port 3003 is the single source of truth. No sovereign shadow Ledger. No client Ledger. The degraded spool is a buffer, not authority. Port 3002 is offline.

---

*End of Integration Report — control-arm-r5 — P2BR5-20260904-A*
