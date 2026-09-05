# NorthStar OS — Knowledge Brain v0 Implementation Plan v2
**Document class:** CANDIDATE implementation plan  
**Experiment:** P2BR5-20260904-A  
**Branch:** control-arm  
**Baseline:** P2BR2-BASELINE-20260902-A  
**Produced by:** control-arm-r5 (single-stream sequential executor)  
**Date:** 2026-09-05  

---

## Executive Summary

NorthStar OS has demonstrated infrastructure viability: the Ledger enforces schema and stores events, MemOS captures memories, the Comms Hub bridges agents, recovery scripts survive real incidents, and skills are beginning to compound. The missing capability is **trustworthy retrieval** — the ability to distinguish what to act on from what to merely consider, and to enforce that distinction consistently at every agent boot, every skill invocation, and every memory query.

Knowledge Brain v0 is the trust classification, storage, retrieval, and boot-protocol layer that makes retrieval trustworthy. It does not replace the Ledger or MemOS — it classifies and annotates the content they already hold. This implementation plan covers the schema changes required to store trust labels, the retrieval API that enforces trust filters, the Memory Constitution that governs agent behavior, the boot protocol that ensures every session starts from verified reality, and the deployment phases that get from current state to a working v0 without breaking existing infrastructure.

**Authority rule (OPERATING-POLICY-v1 §7, §1):** The canonical Ledger on port 3003 is the single source of truth. There is no sovereign shadow Ledger and no client Ledger that holds authoritative state. The port 3002 legacy Ledger is offline and is not part of this architecture. Any degraded-completion spool (described in Section 4) is a temporary buffer that replays to the canonical Ledger when connectivity is restored — it never becomes authoritative.

---

## Section 1 — Ledger and MemOS Schema Changes

### 1.1 Guiding Principle

The schema changes are minimal and additive. No existing Ledger event types are modified. No existing MemOS columns are dropped. All changes are backward-compatible: old events and chunks remain valid; they simply lack trust labels and are treated as T3 (recall candidates) by the retrieval layer until explicitly promoted.

### 1.2 Ledger Schema Changes

The canonical Ledger (port 3003) receives two new event types and three additions to the existing event schema.

**New event types:**

```
memory_validated
  Required fields: chunk_id, previous_trust_level, new_trust_level, evidence_cited, agent, timestamp
  Purpose: Records formal promotion of a memory chunk from one trust level to another.

memory_quarantined
  Required fields: chunk_id, previous_trust_level, suspected_reason, detecting_agent, timestamp
  Purpose: Records quarantine of a memory chunk (classification to T4).

truth_superseded
  Required fields: old_event_id, new_event_id, reason, scope, agent, timestamp
  Purpose: Formally supersedes one T0 item with another. Reclassifies old to T1.

boot_context_loaded
  Required fields: agent, session_id, validation_status (PASS/FAIL), t0_goal_pointer, 
                   active_defect_id, closed_items_count, skills_loaded_count, timestamp
  Purpose: Records that a session boot completed and what was loaded.

skill_invoked
  Required fields: skill_id, trust_level, invocation_source, preconditions_checked, 
                   goal_pointer, agent, result_summary, timestamp
  Purpose: Records successful skill invocation (required for T1 qualification).
```

**Schema additions to existing event types:**

The following optional fields are added to the base event schema. Existing events without these fields are valid; the retrieval layer treats them as unlabeled (T3 by default).

```json
{
  "trust_level": "T0 | T1 | T2 | T3 | T4",
  "trust_domain": "string — domain tag (e.g., 'skill-invocation', 'defect-lifecycle', 'boot-context')",
  "expires_at": "ISO 8601 timestamp — when this event's trust claim expires and requires re-validation",
  "provenance_chain": ["event_id_1", "event_id_2", "..."]
}
```

**Enforcement:** The Ledger's schema v1.1 enforcement (decision_rationale, context_capsule, goal_pointer required fields) remains unchanged. The new optional fields do not override existing required fields.

### 1.3 MemOS Schema Changes

MemOS local DB (`C:\Users\aaron\.openclaw\memos-local\memos.db`) receives five new columns on the `chunks` table and one new table.

**New columns on `chunks` table:**

```sql
ALTER TABLE chunks ADD COLUMN trust_level TEXT DEFAULT 'T3';
ALTER TABLE chunks ADD COLUMN trust_domain TEXT DEFAULT NULL;
ALTER TABLE chunks ADD COLUMN expires_at TEXT DEFAULT NULL;
ALTER TABLE chunks ADD COLUMN promoted_by TEXT DEFAULT NULL;
ALTER TABLE chunks ADD COLUMN provenance_chain TEXT DEFAULT NULL;
-- provenance_chain stored as JSON array of Ledger event_ids
```

Migration strategy: `ALTER TABLE ... ADD COLUMN` is safe and non-destructive in SQLite. All existing chunks gain `trust_level = 'T3'` by default, marking them as recall candidates pending explicit promotion. This is correct: no existing chunk has been formally validated for Knowledge Brain v0.

**New table: `trust_audit_log`**

```sql
CREATE TABLE IF NOT EXISTS trust_audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chunk_id TEXT NOT NULL,
  action TEXT NOT NULL,  -- 'promoted', 'demoted', 'quarantined', 'expired'
  from_level TEXT,
  to_level TEXT,
  agent TEXT,
  reason TEXT,
  ledger_event_id TEXT,  -- corresponds to memory_validated or memory_quarantined Ledger event
  timestamp TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_trust_audit_chunk ON trust_audit_log(chunk_id);
CREATE INDEX IF NOT EXISTS idx_trust_audit_ts ON trust_audit_log(timestamp);
```

This table provides a full audit trail for every trust state change. It is the MemOS equivalent of the Ledger's event stream for trust operations.

**New columns on `skills` table:**

```sql
ALTER TABLE skills ADD COLUMN trust_level TEXT DEFAULT 'T2';
ALTER TABLE skills ADD COLUMN invocation_count INTEGER DEFAULT 0;
ALTER TABLE skills ADD COLUMN last_invoked_at TEXT DEFAULT NULL;
ALTER TABLE skills ADD COLUMN trust_domain TEXT DEFAULT NULL;
```

All existing skills begin as T2 (working notes). Promotion to T1 requires at least one `skill_invoked` Ledger event. This enforces the principle that a skill file is not a proven skill until it has been invoked and confirmed.

### 1.4 Migration Execution Plan

The migration is a two-phase operation:

**Phase M1 — Schema migration (non-destructive, run first):**
```sql
-- Run against memos.db
ALTER TABLE chunks ADD COLUMN trust_level TEXT DEFAULT 'T3';
ALTER TABLE chunks ADD COLUMN trust_domain TEXT DEFAULT NULL;
ALTER TABLE chunks ADD COLUMN expires_at TEXT DEFAULT NULL;
ALTER TABLE chunks ADD COLUMN promoted_by TEXT DEFAULT NULL;
ALTER TABLE chunks ADD COLUMN provenance_chain TEXT DEFAULT NULL;

ALTER TABLE skills ADD COLUMN trust_level TEXT DEFAULT 'T2';
ALTER TABLE skills ADD COLUMN invocation_count INTEGER DEFAULT 0;
ALTER TABLE skills ADD COLUMN last_invoked_at TEXT DEFAULT NULL;
ALTER TABLE skills ADD COLUMN trust_domain TEXT DEFAULT NULL;

CREATE TABLE IF NOT EXISTS trust_audit_log ( ... );
```

**Phase M2 — Seed known T0 and T1 items (post-schema):**

After schema migration, the following items are explicitly promoted via the API:

- Active `goal_declaration` Ledger event → T0 (via `northstar validate` command)
- Phase closure events (2A through 2A-LW) → T1 (validated artifacts)
- Proven skills with `skill_invoked` history → T1 (per invocation count)
- Memory Constitution (once ratified) → T0

Phase M2 is executed through the API layer, not direct SQL, to ensure Ledger events are written for every promotion.

---

## Section 2 — Retrieval API Commands

The retrieval API provides the trust-aware query interface. All commands write Ledger events when invoked in governed mode, ensuring retrieval itself is auditable. The commands are designed to be called from agent scripts, boot routines, and skill invocations.

### Command 1: `northstar memory search "<query>" --trust T0,T1`

**Purpose:** Search the Knowledge Brain for memories matching the query, filtered to specified trust levels.

**Full syntax:**
```
northstar memory search "<query>" [--trust <levels>] [--domain <domain>] [--limit <n>] [--include-recall]
```

**Parameters:**
- `<query>` — Natural language or keyword query, forwarded to MemOS vector search
- `--trust` — Comma-separated filter: T0, T1, T2, T3 (T4 is never returned regardless of flags). Default: T0,T1
- `--domain` — Optional domain scoping to narrow results (e.g., "skill-invocation", "recovery", "defect-lifecycle")
- `--limit` — Max results returned (default: 10, max: 50)
- `--include-recall` — Append T3 recall candidate results, clearly labeled and flagged as requiring validation

**Implementation:** Translates query into MemOS FTS/vector search with a WHERE clause on `chunks.trust_level IN (...)`. Returns results sorted by trust level descending, then by recency.

**Ledger event emitted:** `memory_query` with fields: query_text, trust_filter, domain, result_count, agent, timestamp.

**Output format:**
```
[memory_search result]
Query: "<q>"
Trust filter: T0, T1
Results: N

1. [T0] Governed Truth
   Summary: "..."
   Source: Ledger / goal_declaration
   Event-ID: 01M1DVHCYZSYREJY6AZJ0EHA0R
   Created: 2026-09-01T22:36:19Z  |  Age: 3d

2. [T1] Validated Artifact
   Summary: "..."
   Source: MemOS chunk abc-def
   Created: 2026-08-15T10:00:00Z  |  Age: 21d  |  Expires: 2026-11-15

[With --include-recall:]
3. [T3 RECALL CANDIDATE — NOT VALIDATED — do not act without validation step]
   Summary: "..."
   Source: MemOS chunk xyz-123
   Created: 2026-07-01T00:00:00Z  |  Age: 66d
```

**Error behavior:** If no T0 results found for a query tagged as governed-domain, returns empty result with warning:
```
⚠ WARNING: No governed truth (T0) found for this query.
  Boot context may be incomplete. Run `northstar active` before proceeding.
```

---

### Command 2: `northstar active [--full] [--agent <id>]`

**Purpose:** Return the current active governed state — the primary boot command for establishing what the agent is working on.

**Implementation:** Queries canonical Ledger for the most recent `northstar.state.v1` or `goal_declaration` event. If unavailable (Ledger offline), falls back to navigation map + degraded-mode flag.

**Output:**
```
[northstar active]
Generated: 2026-09-05T16:00:00Z
Source: Ledger / T0 governed state

ACTIVE PROJECT
  Name: NorthStar OS
  Phase: Phase 2B — Governed Small-Swarm Experiment
  Goal pointer: 01M1DVHCYZSYREJY6AZJ0EHA0R
  Trust: T0  |  Authority: Ledger event 01M1DVHCYZSYREJY6AZJ0EHA0R

ACTIVE TRACK
  ID: [track_id or NONE]

ACTIVE DEFECT
  ID: [defect_id or NONE]
  Assigned: [agent or UNASSIGNED]

AUTHORITY SOURCE
  Ledger event: [event_id]

CONSTITUTION: LOADED / NOT LOADED
BOOT VALIDATION: PASS / FAIL [reason]
```

**Ledger event emitted:** `memory_query` with subtype `active_state_check`.

---

### Command 3: `northstar closed [--domain <domain>] [--since <date>] [--limit <n>]`

**Purpose:** Return the list of closed items that must not be reopened without new evidence and owner authorization.

**Implementation:** Queries Ledger for events with `event_subtype IN ('phase_closed', 'defect_closed', 'track_closed')` and MemOS for chunks tagged `trust_domain='closed_items'`. Returns as a structured "do not reopen" list.

**Output:**
```
[northstar closed]
Generated: 2026-09-05T16:00:00Z
Trust: T1 (validated closure records)

CLOSED PHASES
  Phase 2A:    CLOSED — event 01M1ES419QDE34NSSXNDY385S6
  Phase 2A-R:  CLOSED — event 01M1EWBR9E6B3B16F02QCJRDHM
  Phase 2A-R2: CLOSED — event 01M1EWBR9E6B3B16F02QCJRDHM
  Phase 2A-R3: CLOSED — event 01M1EY54RKSH7JY5Z8DB1X8809
  Phase 2A-LW: CLOSED — event 01M1FF5ET0R53C0VEBGD89Z1SB

CLOSED DEFECTS
  [from Ledger query]

⛔ DO NOT REOPEN any item above without:
   1. New evidence not present at time of closure
   2. Owner (Aaron Baker) authorization
   3. Ledger change_order event
```

**Ledger event emitted:** `memory_query` with subtype `closed_state_check`.

---

### Command 4: `northstar next [--agent <id>] [--format brief|full]`

**Purpose:** Return the next allowed governed action for the agent — bounded to current authority scope. Prevents agents from hallucinating "next steps" disconnected from governed reality.

**Implementation:** Combines `northstar active` + `northstar closed` + authority scope lookup. Produces a recommendation that is explicitly bounded by the authority envelope and constraints.

**Output:**
```
[northstar next]
Agent: <agent_id>
Generated: 2026-09-05T16:00:00Z

CURRENT STATE
  Phase: 2B — in progress
  Active goal: 01M1DVHCYZSYREJY6AZJ0EHA0R
  Active defect: NONE

NEXT ALLOWED ACTION
  Action: <specific next action from active state>
  Scope: <authority domain>
  Constraint: <what is out of scope>
  Authority: <Ledger event_id or work packet>

BLOCKED BY
  <Cross-program dependencies or pending adjudications>

NEXT MILESTONE
  <What completes the current task>
```

**Ledger event emitted:** `memory_query` with subtype `next_action_check`.

---

### Command 5: `northstar relevant-skills "<domain>" [--trust T0,T1] [--invoked-only] [--limit <n>]`

**Purpose:** Return skills relevant to the specified domain, filtered to proven trust levels only. Skills with no `skill_invoked` Ledger event history are not included in default results (they are T2 working skills, not T1 validated artifacts).

**Implementation:** Queries MemOS `skills` table with `trust_level IN ('T0', 'T1')` and optional `invocation_count > 0` filter. Also performs FTS match on skill description and domain fields.

**Output:**
```
[northstar relevant-skills "gateway recovery"]
Domain: gateway recovery
Trust filter: T0, T1
Invoked-only: true

SKILLS FOUND: 1

1. [T1] recover-aristotle-gateway
   Skill ID: 37a87886-dc4f-4e45-953a-c963282f5671
   Description: 7-step recovery for Aristotle wedged gateway (Failure Mode 8)
   Invoked: 3 times  |  Last: 2026-08-15T10:00:00Z
   Path: C:\Users\aaron\.openclaw\skills\recover-aristotle-gateway\
   Preconditions: Gateway process unresponsive, port 18792
   Trust domain: recovery / gateway
```

**Ledger event emitted:** `memory_query` with subtype `skill_search_governed`.

---

### Command 6: `northstar validate <chunk_id> --promote-to T1 --evidence "<evidence>"`

**Purpose:** Promote a T2 or T3 memory chunk to a higher trust level with an evidence citation.

**Implementation:** Updates `chunks.trust_level` and `chunks.promoted_by` in MemOS. Inserts row into `trust_audit_log`. Writes `memory_validated` Ledger event.

**Ledger event emitted:** `memory_validated` with all required fields.

---

### Command 7: `northstar quarantine <chunk_id> --reason "<reason>"`

**Purpose:** Quarantine a memory chunk by reclassifying to T4.

**Implementation:** Updates `chunks.trust_level = 'T4'`. Inserts `trust_audit_log` entry. Writes `memory_quarantined` Ledger event. Triggers contamination check (queries all chunks whose `provenance_chain` contains the quarantined chunk_id).

**Ledger event emitted:** `memory_quarantined` with all required fields.

---

### Command 8: `northstar supersede <old_event_id> --with <new_event_id> --reason "<reason>" [--scope "<scope>"]`

**Purpose:** Formally supersede an old T0 item with a new T0 declaration.

**Implementation:** Queries old event to confirm it is T0. Writes `truth_superseded` Ledger event. Updates any MemOS chunks whose `provenance_chain` includes `old_event_id` to note the supersession. The old item's trust_level is reclassified to T1 in MemOS; the event itself remains in the Ledger (immutable).

**Ledger event emitted:** `truth_superseded` with: old_event_id, new_event_id, reason, scope, agent, timestamp.

---

## Section 3 — Memory Constitution (CANDIDATE)

**Status: CANDIDATE — not yet ratified. Requires owner (Aaron Baker) adjudication before becoming T0.**

This Memory Constitution defines the operating rules for how NorthStar agents interact with stored knowledge. It is the law of the Knowledge Brain. All agents must comply once ratified.

---

### Article I — What May Govern

Only T0-classified content may govern agent behavior. Governance means: may issue instructions, may set acceptance criteria, may close or open work, may define what constitutes success or failure.

A T0 item earns its status through one of three paths:
1. **Owner declaration:** Aaron Baker explicitly designates it as governing truth.
2. **Ledger proof chain:** A sequence of Ledger events forms an unbroken evidence chain with no contradicting T0 event. The canonical Ledger on port 3003 is the only valid source for T0 proof chains.
3. **Ratified constitution or charter:** A document committed as canonical governance and acknowledged in the Ledger.

No agent may self-promote its own working notes to T0 status. No agent may declare a memory T0 without the proof chain above. If an agent receives a conflicting T0 signal, it must log the contradiction to the Ledger immediately and halt governed action until the conflict is resolved by owner adjudication.

The canonical Ledger on port 3003 is the only sovereign truth store (OPERATING-POLICY-v1 §1, §7). Port 3002 is offline. No new sovereign Ledger instances may be created at any port.

---

### Article II — What May Advise

T1-classified content may advise agent behavior. Advisory means: may inform decisions, may be cited as evidence, may strengthen or weaken a hypothesis, but may not govern or instruct alone.

T2 content (working notes) may advise only within the current session and only when the agent explicitly acknowledges it is working from unvalidated material. Any output produced primarily from T2 advice must be tagged: *"advisory — requires validation before governing use."*

When T1 advice conflicts with another T1 item, the agent surfaces both, defers to the more evidence-rich or more recent item, and logs the reasoning. When T1 advice conflicts with any T0 item, T0 wins without exception.

---

### Article III — What Must Be Validated

The following categories must be validated before use in any governed decision, regardless of apparent trust level:

1. **Any content older than its stated expiry.** Age alone is grounds for mandatory re-validation.
2. **Any content from an external source.** External input enters as T4 and must be promoted through the full chain (T4→T3→T2→T1→T0).
3. **Any content whose provenance chain is incomplete.** If the origin event cannot be traced to the Ledger or a governed object, validation is required.
4. **All T3 and T4 content before any use in decisions.** No exceptions.
5. **Any content conflicting with current T0 state.** Even T1 items require adjudication before they may advise when in direct conflict with a T0 item.
6. **Skill files before invocation in novel domains.** Skills proven in domain A must be validated for applicability in domain B before governed invocation.

Validation produces a `memory_validated` Ledger event with: agent, timestamp, evidence cited, and resulting trust level.

---

### Article IV — What May Be Invoked

Only T0 and T1-classified skills may be invoked in governed workflows. A skill qualifies as T1 when:
1. It carries T1 trust classification in the MemOS `skills` table.
2. It has at least one `skill_invoked` Ledger event proving prior successful execution.
3. Its preconditions match current system state.
4. Its domain applicability has been validated for the current task.

T2 skills (working/experimental) may be invoked in sandboxed advisory mode with explicit acknowledgment that results are unvalidated. T2 invocations must be logged with `event_subtype = "sandboxed_invocation"`.

T3 skills may NOT be invoked. They must be promoted to T2 via validation before any invocation.

T4 skills may NEVER be invoked. Any attempt to invoke a T4 skill must be logged as a governed violation and escalated.

Every invocation writes a `skill_invoked` Ledger event before the skill output may be used in any governed decision.

---

### Article V — What May Be Forgotten

Forgetting is a governed act. The following may be forgotten (deleted or downgraded to T4 for deletion review):

1. **T4 items not promoted within 90 days** with no open validation ticket.
2. **T2 items not promoted within 24 hours** of creation.
3. **T3 items that have exceeded their stated expiry** and are not referenced by any active T0 or T1 item. (30-day expiry in active domains; 180-day expiry in archival domains.)
4. **Superseded duplicate T1 items** where a newer, evidence-equivalent version exists and the older item has been explicitly superseded.
5. **Boilerplate noise** — heartbeats, routine status confirmations, session administrative entries — not referenced by any active Ledger event.

Every forgetting action requires a `memory_expiry` or `memory_deletion` Ledger event with reason, agent, and timestamp. Mass deletion without Ledger recording is a governed violation. T1 or higher deletion requires owner approval.

What may NEVER be forgotten: T0 items (superseded only, never deleted), closed defect records, phase completion receipts, evidence chain events, and any item referenced by an open governed object.

---

### Article VI — How Old Truth Is Superseded

Truth does not become false by age alone. It must be explicitly superseded by a newer T0 declaration via this protocol:

1. **New T0 declaration event** is written to the Ledger with: old_event_id (superseded), new_event_id, agent, reason, timestamp, and change_order_ref.
2. **The old T0 item is reclassified to T1** — auditable historical artifact. It is NOT deleted.
3. **All agents that cached the old T0 context** must receive a supersession signal and reload their boot context before continuing governed work.
4. **Two T0 items without a supersession event** is a critical governed error. Both are quarantined pending adjudication. No governed work proceeds in the affected domain until the owner resolves the conflict.

No agent may informally treat an old T0 item as superseded based on reasoning alone. Only the formal protocol above constitutes truth transition.

Partial supersession is permitted: a new T0 item may supersede one section of an old T0 item while leaving other sections intact. The supersession event must specify the exact scope of supersession.

---

### Article VII — How Poisoned Memory Is Handled

A poisoned memory contains false, fabricated, externally manipulated, or corrupted content that has infiltrated the trust chain.

**Step 1 — Quarantine.** Suspected item is immediately reclassified to T4. No agent may continue to act on it. Write `memory_quarantined` Ledger event with: item_id, suspected_reason, detecting_agent, timestamp.

**Step 2 — Trace.** Identify the provenance chain. Which events referenced the poisoned item? Which decisions were influenced by it? Log as `poison_trace` Ledger events.

**Step 3 — Contamination check.** Any T0 or T1 item directly informed by the poisoned item is flagged for re-validation. If a T0 item was poisoned, all work governed by it is suspended pending adjudication.

**Step 4 — Remediation.** Valid items that were contaminated are re-validated through clean evidence chains and re-promoted. Work products derived from poisoned memory are marked `requires_rederivation`.

**Step 5 — Adjudication.** If poison reached T0 level, owner action is required to restore governed state. No agent may self-adjudicate T0 poisoning.

**Step 6 — Post-mortem.** Write `poison_postmortem` Ledger event documenting: entry vector, propagation path, items affected, remediation taken, and prevention recommendations.

The immune system principle: detecting and containing a poisoned memory quickly is a success, not a failure. Flag early. False positives are acceptable. False negatives are not.

---

### Article VIII — Boot Context Rules

Every fresh agent session must load governed reality before doing any work.

**Required loads (all sessions):**
1. Active T0 goal declaration — current project and phase.
2. Active track and defect — current assignments.
3. Closed items list — what must not be reopened.
4. Relevant T0/T1 skills for current domain — available tools.
5. Authority source — Ledger event establishing scope.
6. Memory Constitution (this document) — operating rules.

**Prohibited boot loads:**
- T2 items (per-session notes from prior sessions)
- T3 items (recall candidates, unless explicitly requested with `--include-recall`)
- T4 items (quarantined content — loading T4 on boot is a critical violation under any condition)
- Superseded T0 items (old truth reclassified as T1 — informative but not governing)

**Boot validation gate:** After loading boot context, the agent must confirm:
- At least one T0 goal declaration loaded
- No conflicting T0 items present
- Memory Constitution loaded
- Active goal pointer matches Ledger current state

If boot validation fails, the agent reports the failure state and requests human or governance review before proceeding with governed work. An unvalidated boot is an ungoverned session.

**Boot context package format:**
```
Agent: [agent_id]
Session: [session_key]
Boot trust floor: T0+T1
Active goal: [goal_pointer] — [summary]
Active track: [track_id or NONE]
Active defect: [defect_id or NONE]
Closed items: [list with event_ids]
Do not reopen: [list with reasons]
Relevant skills (T0/T1): [skill_ids and UUIDs]
Authority source: [Ledger event_id or governed object ref]
Constitution: LOADED (T0 once ratified; T1 CANDIDATE until ratified)
Boot validation: PASS / FAIL [reason if fail]
```

---

## Section 4 — Primary and Degraded Boot-Retrieval Protocol

### 4.1 Primary Boot Protocol

The primary boot protocol runs when the canonical Ledger (port 3003) is available and MemOS is healthy.

**Sequence:**

```
Step 1: LEDGER PING
  GET http://127.0.0.1:3003/events?limit=1
  → If HTTP 200: Ledger available. Proceed with primary protocol.
  → If connection refused or timeout: Enter degraded protocol (Section 4.2).

Step 2: ACTIVE STATE LOAD (T0)
  northstar active
  → Loads most recent northstar.state.v1 or goal_declaration from Ledger.
  → Records goal_pointer and phase.
  → If no T0 goal event found: report UNGOVERNED BOOT, halt governed work.

Step 3: CLOSED ITEMS LOAD (T1)
  northstar closed
  → Loads all phase_closed, defect_closed, track_closed events from Ledger.
  → Verifies Phase 2A–2A-LW closure events are present.
  → If query fails: log boot_closed_items_query_failed, treat all prior phases as closed.

Step 4: ACTIVE DEFECT/TRACK LOAD (T0/T1)
  Ledger query: GET /events?event_subtype=defect_opened&status=open
  → Loads any open defects assigned to this agent.
  → Cross-check: confirm no closed defect appears in open state.

Step 5: RELEVANT SKILLS LOAD (T1)
  northstar relevant-skills "<current domain>"
  → Loads T1 skills with invocation history relevant to current task domain.
  → If no T1 skills found: log no_governed_skills_for_domain. Proceed from first principles.

Step 6: AUTHORITY SOURCE LOAD
  Ledger query for this agent's work packet event.
  → Confirms scope: permitted writes, prohibited writes, authority envelope.
  → If no authority source: log authority_source_missing, halt governed writes.

Step 7: MEMORY CONSTITUTION LOAD
  skill_get with UUID for boot-context skill (18a6297b-1223-4f0a-80c4-6c782249173f).
  → Load Memory Constitution articles if available as T0/T1 content.
  → If unavailable: treat all memory operations as unvalidated.

Step 8: BOOT VALIDATION
  Confirm all six requirements satisfied.
  → PASS: emit boot_context_loaded Ledger event with validation_status=PASS.
  → FAIL: emit boot_context_loaded with validation_status=FAIL and failure_reason.
           Report to operator. Do not proceed with governed work.
```

### 4.2 Degraded Boot Protocol

The degraded boot protocol runs when the canonical Ledger is unavailable. It provides a safe fallback that preserves agent orientation without permitting ungoverned action.

**Authority rule:** When the Ledger is unavailable, NO new T0 truth may be established. NO governed state may be promoted. The agent operates in advisory-only mode until the Ledger is restored.

**Degraded Completion Spool:** Events that would have been written to the Ledger during degraded mode are buffered to a local spool file:
```
C:\North_Star_Projects\orchestration\spool\pending-ledger-events.jsonl
```
This spool is NOT authoritative. It is a staging area for replay. When the Ledger is restored, spool events are submitted in order. If a spool event conflicts with current Ledger state (because another agent wrote the same thing while the spool was building), the Ledger state wins and the spool event is logged as superseded.

**Degraded boot sequence:**

```
Step 1: LEDGER UNAVAILABLE — Confirmed
  Log: "Ledger unreachable at http://127.0.0.1:3003. Entering degraded boot."
  Initialize spool file at: C:\North_Star_Projects\orchestration\spool\pending-ledger-events.jsonl

Step 2: NAVIGATION MAP LOAD (T1 — advisory only)
  Read: C:\Users\aaron\clawd-shared\NORTHSTAR-NAVIGATION-MAP.md
  → Extract most recent phase, active goal, and next action.
  → Label context as T1 ADVISORY — not T0 governed. Nav map is stale without Ledger confirmation.

Step 3: MEMOS RECALL (T3 — conditional)
  northstar memory search "<active domain>" --trust T1 --include-recall
  → Surface T1 MemOS chunks for relevant context.
  → T3 recall items labeled as UNVALIDATED RECALL.

Step 4: CLOSED ITEMS ASSUMPTION
  Treat all prior phases as closed until Ledger confirmation.
  No reopening of any item during degraded mode.

Step 5: SKILLS FROM FILESYSTEM (T2 fallback)
  Read skills directly from filesystem: C:\Users\aaron\.openclaw\skills\
  → Skills retrieved without Ledger invocation confirmation are T2 (working notes).
  → Do not treat filesystem skills as T1 without confirmed invocation history.

Step 6: DEGRADED SESSION DECLARATION
  Agent logs: "DEGRADED BOOT — Ledger unavailable. Operating in advisory-only mode.
               No governed writes. No T0 promotions. Spool active for replay on Ledger restore."
  Write to spool: { "event_type": "boot_context_loaded", "validation_status": "DEGRADED", ... }

Step 7: OPERATOR NOTIFICATION
  Notify Aaron via configured channel: "Ledger unavailable at boot. Degraded mode active."

Step 8: LEDGER RESTORATION POLL
  Every 5 minutes: attempt GET http://127.0.0.1:3003/events?limit=1
  → When Ledger returns HTTP 200: exit degraded mode, replay spool, re-run primary boot.
```

### 4.3 Protocol Comparison

| Requirement | Primary Protocol | Degraded Protocol |
|---|---|---|
| T0 goal declaration | ✅ From Ledger | ❌ Not available — use nav map T1 |
| Closed items | ✅ From Ledger events | ⚠ Assumed from prior knowledge |
| Active defect | ✅ From Ledger | ⚠ From MemOS recall only |
| Relevant skills | ✅ T1 with invocation proof | ⚠ T2 filesystem fallback |
| Authority source | ✅ From Ledger event | ❌ No governed authority |
| Memory Constitution | ✅ T0/T1 | ⚠ T2 if available locally |
| Governed writes | ✅ Permitted | ❌ Blocked — spool only |
| T0 promotions | ✅ Permitted | ❌ Blocked |

---

## Section 5 — Integration and Deployment Phases, Risks, Rollback, and Acceptance Criteria

### 5.1 Phase Definitions

**Phase KB-1: Schema Migration (Non-Destructive)**
- Duration: 1 session
- Prerequisites: MemOS DB backup taken, canonical Ledger healthy
- Work: Apply `ALTER TABLE` statements to add trust_level, trust_domain, expires_at, promoted_by, provenance_chain to chunks; trust_level, invocation_count, last_invoked_at to skills; create trust_audit_log table
- Ledger events added: memory_validated, memory_quarantined, truth_superseded, boot_context_loaded, skill_invoked schema registered
- Acceptance criteria: All new columns present in schema. All existing rows retain original data. No existing queries broken.

**Phase KB-2: Seed Trust Labels**
- Duration: 1–2 sessions
- Prerequisites: KB-1 complete
- Work: Promote active goal declaration to T0 via `northstar validate`. Promote phase closure events to T1. Promote known-good skills with invocation history to T1. Write Memory Constitution as T1 candidate artifact.
- Acceptance criteria: At least 1 T0 chunk present in MemOS. At least 5 T1 chunks present. `northstar memory search "goal" --trust T0` returns the active goal declaration. `northstar relevant-skills "recovery"` returns `recover-aristotle-gateway` at T1.

**Phase KB-3: Retrieval API Deployment**
- Duration: 2–3 sessions
- Prerequisites: KB-2 complete
- Work: Implement northstar CLI commands 1–8 as described in Section 2. Wire to MemOS SQLite queries with trust_level filter. Wire `northstar active` and `northstar closed` to Ledger query endpoints. Implement `northstar next` combining active + closed + authority scope.
- Acceptance criteria: All eight commands execute without error. Each command writes expected Ledger event. `northstar memory search "recovery" --trust T0,T1` returns non-empty results. `northstar closed` lists all five Phase 2A closure events.

**Phase KB-4: Boot Context Integration**
- Duration: 1–2 sessions
- Prerequisites: KB-3 complete
- Work: Update boot-context skill script to call northstar API commands in sequence. Implement boot validation gate (6-requirement check). Implement degraded spool file. Implement Ledger restoration poll.
- Acceptance criteria: Cold agent boot produces a validated boot context package. `boot_context_loaded` Ledger event written with validation_status=PASS. Degraded mode activates when Ledger is taken offline and spools events correctly. Spool replays on Ledger restoration.

**Phase KB-5: Constitution Ratification**
- Duration: 1 session (owner adjudication)
- Prerequisites: KB-4 complete and proven
- Work: Present Memory Constitution CANDIDATE to Aaron. Upon approval: write constitution as T0 governed artifact to Ledger. Reclassify from CANDIDATE to ratified. Emit `constitution_ratified` Ledger event.
- Acceptance criteria: `northstar memory search "constitution" --trust T0` returns the ratified document. Boot context loads constitution as T0. All agents acknowledge constitution load in their boot_context_loaded event.

### 5.2 Risks and Mitigations

**Risk 1 — SQLite migration fails or corrupts MemOS DB**
- Probability: Low (ALTER TABLE ADD COLUMN is non-destructive in SQLite)
- Impact: High (MemOS unavailable)
- Mitigation: Take a full file backup of `memos.db` before Phase KB-1. If migration fails, restore backup and investigate before retrying.
- Detection: Post-migration: `SELECT trust_level FROM chunks LIMIT 1` should not error.

**Risk 2 — Existing queries break due to new columns**
- Probability: Low (SQLite ADD COLUMN with DEFAULT is backward-compatible)
- Impact: Medium (search results or skill retrieval disrupted)
- Mitigation: Test all primary query paths (skill_search, memory_search, boot-context script) after KB-1 before proceeding to KB-2.
- Detection: Run acceptance tests 4 and 5 from Recovery Playbook v2 after KB-1.

**Risk 3 — Ledger API changes required for new event types**
- Probability: Medium (new event types require schema v1.1 to accept them)
- Impact: High (new events rejected by Ledger validation)
- Mitigation: Confirm Ledger schema allows new event_type values via POST /events before writing new types. If Ledger schema is strict, coordinate schema update with gateway team.
- Detection: Test POST of a `memory_validated` event to Ledger sandbox before Phase KB-2.

**Risk 4 — Degraded spool grows unbounded**
- Probability: Low in normal operation; higher if Ledger outage is prolonged
- Impact: Medium (disk usage; spool replay takes longer)
- Mitigation: Cap spool at 1,000 events per session. If cap reached: log warning, halt non-critical spool writes, and escalate Ledger restoration. Critical events (boot_context_loaded, worker_stuck) always write to spool regardless of cap.
- Detection: Monitor `(Get-Item pending-ledger-events.jsonl).Length` — alert if > 10MB.

**Risk 5 — Trust label drift (items labeled incorrectly)**
- Probability: Medium (human error in promotion decisions)
- Impact: High (wrong trust levels lead to agents acting on T3 as if T0)
- Mitigation: Require evidence citation for every `northstar validate` invocation. Audit `trust_audit_log` weekly. T0 promotions require explicit Ledger event and cannot be done via direct SQL.
- Detection: `trust_audit_log` entries with no corresponding `memory_validated` Ledger event_id indicate bypassed promotion path — run weekly audit query.

**Risk 6 — Memory Constitution ratification delay**
- Probability: High (requires owner adjudication, scheduling dependent)
- Impact: Medium (agents operate with CANDIDATE constitution, not T0)
- Mitigation: Deploy KB-1 through KB-4 with CANDIDATE constitution at T1. System operates correctly — agents follow the constitution's rules even at T1 trust. Ratification upgrades it from advisory to governing.
- Detection: `northstar memory search "constitution" --trust T0` returns empty until ratification.

### 5.3 Rollback Procedures

**Rollback KB-1 (Schema Migration):**
1. Stop all MemOS write activity.
2. Replace `memos.db` with pre-migration backup.
3. Verify backup integrity: `SELECT count(*) FROM chunks` should match pre-migration count.
4. Resume operations with original schema.

**Rollback KB-2 (Seed Trust Labels):**
1. Execute: `UPDATE chunks SET trust_level = 'T3' WHERE trust_level IN ('T0', 'T1', 'T2')` — resets all labels to recall-candidate default.
2. Write Ledger event: `{ "event_type": "status_update", "event_subtype": "kb_seed_rollback", "reason": "<reason>" }`
3. Note: Ledger events written during KB-2 cannot be rolled back (Ledger is append-only). They remain as historical record but no longer correspond to active trust labels.

**Rollback KB-3 (Retrieval API):**
1. Remove or disable northstar CLI command implementations.
2. Agents revert to direct MemOS search and Ledger query without trust filters.
3. No data loss — trust labels remain in MemOS but are simply not enforced.

**Rollback KB-4 (Boot Context Integration):**
1. Revert boot-context skill script to pre-KB-4 version.
2. Remove spool file.
3. Agents revert to legacy boot context (nav map + Ledger query without structured validation).

**Rollback KB-5 (Constitution Ratification):**
Not applicable — ratification is a declaration event, not a code change. If the constitution needs revision, the owner issues a supersession event per Article VI and publishes a revised CANDIDATE.

### 5.4 Acceptance Criteria (Knowledge Brain v0 Complete)

The Knowledge Brain v0 is complete when all of the following hold simultaneously:

1. **Trust labels deployed:** `SELECT DISTINCT trust_level FROM chunks` returns T0, T1, T2, T3 (and optionally T4). At least one T0 chunk exists (active goal declaration).

2. **Retrieval filters working:** `northstar memory search "current goal" --trust T0` returns the active goal with trust level T0. `northstar memory search "current goal" --trust T1` excludes T4 and T0 items (T0 is included as T0 supersedes T1 in trust floor queries) or surfaces them clearly labeled.

3. **Boot context structured:** A fresh cold agent boot produces a boot context package matching the format in Article VIII. `boot_context_loaded` event appears in Ledger within 5 minutes of boot.

4. **Skill invocation proven:** At least one `skill_invoked` Ledger event exists for a T1 skill. `northstar relevant-skills "recovery"` returns `recover-aristotle-gateway` at T1.

5. **Constitution loaded:** `northstar memory search "constitution" --trust T0,T1` returns the Memory Constitution document. (T0 if ratified; T1 if CANDIDATE.)

6. **Closed items verified:** `northstar closed` lists all five Phase 2A closure events. Any attempt to reopen a listed item produces a Ledger `blocked_reopen_attempt` event.

7. **Degraded mode proven:** When Ledger is taken offline, degraded boot protocol activates without crashing. Spool file is created. When Ledger is restored, spool replays and boot_context_loaded with validation_status=PASS appears in Ledger.

8. **No sovereign shadow Ledger:** Confirmed that no process is running an authoritative Ledger on any port other than 3003. Port 3002 remains offline. No agent holds local canonical state.

---

## Appendix — Trust Level Quick Reference

| Level | Name | Governs? | Advises? | Boot Load | Expiry | Invocable? |
|---|---|---|---|---|---|---|
| T0 | Governed Truth | YES | YES | Required | Never (superseded only) | YES |
| T1 | Validated Artifact | NO | YES | Yes (domain-relevant) | 90d review cycle | YES (with invocation proof) |
| T2 | Working Note | NO | Session only | NO | 24h auto-expire | YES (sandboxed only) |
| T3 | Recall Candidate | NO | Suggestion only | Conditional (--include-recall) | 30-180d | NO |
| T4 | Untrusted Input | NO | NO | NEVER | 90d → deletion review | NEVER |

---

## Appendix — Authority Boundary Summary

- **Who may declare T0:** Aaron Baker (owner) or Ledger proof chain from canonical port 3003
- **Who may promote T1→T0:** Aaron Baker only
- **Who may promote T2→T1:** Any agent with evidence citation + Ledger event
- **Who may quarantine to T4:** Any agent (immediate, no owner required)
- **Who may delete T1+:** Owner approval required
- **Sovereign Ledger:** Port 3003 only — no additional Ledger instances ever
- **Spool rule:** Degraded spool is a staging buffer, never authoritative, always replays to canonical Ledger on restore

---

*End of Knowledge Brain v0 Implementation Plan v2 — CANDIDATE — control-arm-r5 — P2BR5-20260904-A*
