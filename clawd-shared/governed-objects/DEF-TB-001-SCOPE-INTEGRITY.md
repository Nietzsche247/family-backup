# DEF-TB-001 Scope & Integrity Note — Jurisdiction/Locality Trust Break

**Date:** 2026-03-23  
**Track:** B (OmniPools Calculator)  
**Item:** DEF-TB-001 — Intake state collapses or ignores jurisdiction/locality selections  
**Status of neighboring items:** TB-002 CLOSED/verified; TB-003 CLOSED/verified (per Aaron)  

---

## 0) Executive verdict (scope viability)

**VERDICT: PASS — a narrow TB-001 fix is viable** *provided the defect is in the jurisdiction/locality “trust chain” (canonical source + precedence + read/write path) and not in general reload hydration/persistence.*

**Immediate boundary trigger (forces scope re-evaluation):** If evidence shows jurisdiction/locality is only lost on reload due to schema rejection/migration failure or `loadIntake()` returning `null`, that is TB-003-class hydration/persistence behavior and cannot be handled “jurisdiction-only” without crossing guardrails.

---

## 1) Confirmation: can TB-001 be fixed narrowly without reopening TB-002/TB-003?

### Why narrow scope is plausible
- **TB-002** addressed **manual correction authority** for *clientInfoOverrides/address* using a `useRef` anti-stale-closure pattern inside `parseCRM`. TB-001 is about **jurisdiction/locality selection integrity**. These are separable as long as TB-001 does not alter:
  - the `parseCRM` override guard semantics, or
  - the “manual correction is authoritative” rule (Contract Rule 3), or
  - the callback memoization patterns that were central to TB-002.

- **TB-003** characterization (reload rehydration failure) shows risk concentrated around:
  - `loadIntake()` null-return → fallback to `createInitialIntake()` → cross-page fragment overwrite.
  - cross-page sync effect lacking a factory-default overwrite guard.

A TB-001 fix can remain narrow if it:
- **does not modify** `loadIntake()/saveIntake()`, schema validation/migrations, autosave guards, or session-restore heuristics, and
- limits changes to the **jurisdiction/locality canonical field(s)** and their **read/write precedence** (the trust chain), including any minimal cross-page “projection” *only if necessary and only for those fields*.

### Non-reopening statement
- **Do not reopen TB-002:** TB-001 must not change the TB-002-established invariant: *manual edits to canonical fields persist against parser re-runs.*
- **Do not reopen TB-003:** TB-001 must not touch reload hydration order, factory-default timestamps, or cross-page overwrite guard logic beyond the minimal jurisdiction/locality trust chain.

---

## 2) Specific risks of a narrow approach (what could go wrong?)

These are concrete failure modes that can occur even with a “jurisdiction-only” intent:

1. **False narrowness: bug is actually hydration failure**
   - Symptom pattern: jurisdiction/locality appears correct until reload, then resets.
   - Underlying cause: `loadIntake()` returns `null` (schema reject/migration/recovery fail) and state falls back to defaults (TB-003 pattern).
   - Risk: attempting to patch “jurisdiction” logic won’t stick; it will mask the real cause and create inconsistent behavior between live session vs reload.

2. **Manual correction authority regression (Contract Rule 3)**
   - If jurisdiction/locality is treated as “derived” from address/geocode and is re-derived automatically, it can silently overwrite a user-selected jurisdiction/locality.
   - This recreates the TB-002 class of user-trust violation, just on different fields.

3. **Stale-closure regression (TB-002 class) applied to jurisdiction/locality**
   - If any re-parse / recompute function that considers jurisdiction/locality is memoized with stale captured state, it can:
     - ignore a recent user selection, or
     - overwrite it with an older value.
   - This can happen without touching CRM parsing at all.

4. **Cross-page read/write mismatch (fragment vs full intake)**
   - Some pages read from `omni-intake-cross-page` first (TB-003 characterization cites this pattern).
   - If jurisdiction/locality exists only in full state (or only in the fragment) and consumers expect the other, selections may appear to “collapse” depending on navigation path.
   - Risk: Fixing only one side (writer or reader) can create path-dependent truth.

5. **coordSource protection regression**
   - If jurisdiction/locality changes trigger any coordinate recomputation, it can conflict with `coordSource` invariants (manual vs geocoded vs inferred).
   - Risk outcome: lat/lng flips unexpectedly or becomes “trusted” when it should remain manual-protected.

6. **Trigger contract violation by accidental “vibe trigger”** (Contract Rule 5)
   - If jurisdiction/locality selection is used as a proxy to trigger downstream modules (or geocoding) without required canonical inputs, that is forbidden.
   - Example class: “jurisdiction selected therefore run SI/geocode” without canonical address or lat/lng.

7. **Schema/persistence creep**
   - Adding fields or changing shapes in intake schema can force migrations and validation changes (TB-003 territory).
   - Risk: a seemingly small field addition can cause older saved payloads to fail validation → `loadIntake()` returns `null` → full state collapse.

---

## 3) Boundary conditions: where ‘jurisdiction fix’ ends and ‘persistence redesign’ begins

### In-bounds for TB-001 (jurisdiction/locality trust chain ONLY)
A TB-001 fix may include **only** actions that directly establish and preserve the canonical truth of jurisdiction/locality across the *existing* intake architecture:

- **Canonical source definition:** make it explicit which canonical field(s) represent jurisdiction/locality and what precedence applies (manual selection vs parser candidates vs inferred defaults).
- **Integrity of updates:** ensure the selected jurisdiction/locality is written to canonical state in a way that is not silently discarded by later computations.
- **Consistency across read paths:** if there are two sanctioned read surfaces (full intake vs cross-page projection), they must not disagree for jurisdiction/locality.
  - *If* cross-page projection is part of the trust chain for calculator pages, then including jurisdiction/locality in that projection can be within scope **only if limited strictly to those fields** and does not alter hydration/overwrite guards.

### Out-of-bounds (this becomes persistence redesign / Track drift)
Any of the following crosses the line:

- Changing localStorage key strategy (e.g., renaming `omni-intake-v1`, changing `omni-intake-cross-page` semantics, or introducing new storage tiers).
- Rewriting `loadIntake()`/`saveIntake()` logic, recovery merge strategy, migration pipeline, or schema-wide validation approach.
- Modifying factory-default timestamp semantics (`updatedAt` initialization) as a means to “fix” jurisdiction/locality.
- Broad refactors of `useIntake` initialization/effects ordering, session restore heuristics, or cross-page synchronization architecture.
- Any change that requires updating multiple unrelated module inputs/outputs (Track C/D drift).

### Explicit “stop work” signals (scope break)
If any of these are true during implementation planning, TB-001 narrow scope is no longer assured:
- Jurisdiction/locality cannot be represented without adding a new schema version + migration.
- The only observed failure mode is reload collapse driven by `loadIntake()` returning `null`.
- Fix requires touching autosave guard logic, session-restore logic, or debounced persistence.

---

## 4) Regression risks to manual correction authority and coordSource protections

### Manual correction authority (Contract Rule 3)
**Do not allow any automatic process (parser, inference, defaults) to silently overwrite a user’s jurisdiction/locality selection.**

Regression risks:
- A “resolveLocation()” style selector recomputes jurisdiction/locality from address each render and overwrites canonical state.
- A debounced parser run treats jurisdiction/locality as “safe to refresh” and replaces manual picks.

Required invariant for TB-001 work:
- If the designer manually sets jurisdiction/locality, that value is authoritative until the designer changes it again.

### coordSource protections
Even if jurisdiction/locality is “location-adjacent,” it is not equivalent to coordinates.

Regression risks:
- Jurisdiction/locality change triggers geocode or lat/lng writes.
- A jurisdiction/locality inference step incorrectly upgrades coordSource (“looks derived, therefore trusted”).

Required invariant for TB-001 work:
- **No new coordinate write path.** Jurisdiction/locality integrity must not alter lat/lng or coordSource behavior.

---

## 5) Contract violations the TB-001 fix must avoid (compliance constraints)

From **PARSER + TRIGGER CONTRACT v2.x**:

### Must not violate Rule 3 — Manual correction is authoritative
- A manual jurisdiction/locality selection must not be overwritten by parser re-runs or enrichments.

### Must not violate Rule 5 — No required canonical inputs → no trigger
- Jurisdiction/locality is not listed as a required canonical input for downstream modules in the governing contract excerpt. Therefore:
  - do not trigger modules merely because jurisdiction/locality is present;
  - do not treat raw text or “probably enough” location hints as canonical triggers.

### Must preserve the “candidate vs canonical” split (Rule 2)
- If parsers infer jurisdiction/locality, that output is **candidate data** until mapped into canonical fields.
- Downstream modules must not wake up on candidate fields.

### Must respect multi-entry architecture (Rule 7)
- If a module can be entered directly, it must rely on its required canonical fields, not on “came through Intake with jurisdiction/locality set.”

---

## 6) Recommended constraints for the TB-001 fix brief author (Aristotle)

These are guardrails to bake into the fix brief so implementation cannot drift:

1. **Define the trust chain explicitly**
   - State, in one place: what field(s) are canonical for jurisdiction/locality, and what precedence applies among (a) manual selection, (b) parsed/inferred candidate, (c) defaults.

2. **Enumerate allowed files / disallowed files**
   - Allowed: the narrowest possible surface where jurisdiction/locality is set/resolved/read.
   - Disallowed: `persistence.ts`, schema migrations, autosave logic, session restore logic, broad `useIntake` initialization changes.

3. **No new coordinate writes**
   - Explicitly prohibit modifying any code that writes lat/lng or alters coordSource as part of this fix.

4. **No new triggers**
   - Explicitly prohibit new module-trigger logic tied to jurisdiction/locality.

5. **Path-independence requirement**
   - Jurisdiction/locality must be consistent regardless of whether a consumer reads from full intake state or cross-page projection.
   - If both exist, they must not diverge.

6. **Regression checklist (must-pass)**
   - Manual selection persists through any parser re-run that can happen in the same session.
   - Manual selection persists through tab navigation (pages that rely on cross-page reading vs direct intake reading).
   - No change in behavior for TB-002-protected manual address overrides.
   - No change in coordSource behavior under typical flows.
   - No new module triggers without required canonical inputs.

---

## Contract compliance checklist (copy/paste for fix brief)

- [ ] **Rule 3:** Manual jurisdiction/locality selection is never overwritten by parser/inference without explicit user action.
- [ ] **Rule 2:** Parser/inferred jurisdiction/locality remains candidate until mapped to canonical; downstream does not consume candidates as authoritative.
- [ ] **Rule 5:** No module or geocode-like trigger occurs without required canonical inputs; jurisdiction/locality presence is not treated as “probably enough.”
- [ ] **coordSource:** No new lat/lng write path; coordSource protections unchanged.
- [ ] **TB-002 non-regression:** No changes that reintroduce stale-closure overwrite of manual overrides.
- [ ] **TB-003 non-regression:** No changes to `loadIntake/saveIntake`, schema-wide validation/migrations, autosave guards, session restore heuristics, or cross-page overwrite guard logic outside the minimal jurisdiction/locality trust chain.

---

## Final note
This is a **scope integrity** determination, not an implementation plan. The narrow TB-001 scope is viable as long as the work stays inside the jurisdiction/locality trust chain (canonical source + precedence + consistent read/write path) and does not drift into persistence/hydration architecture.
