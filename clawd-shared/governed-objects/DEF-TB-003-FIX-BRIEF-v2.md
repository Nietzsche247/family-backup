# DEF-TB-003 Fix Brief v2 — Schema Validation Rejecting Stored Data

**Date:** 2026-03-20
**Severity:** Medium-High
**Owner:** Plato (implementation) + Daedalus (review)
**Validator:** Empiricus (post-deploy)
**Scope:** NARROW — DEF-TB-003 only. Schema validation fix grounded in Parser + Trigger Contract Rule 8.
**Supersedes:** DEF-TB-003-FIX-BRIEF.md (v1 addressed cross-page sync guard — that fix is already committed and correct, but insufficient alone)

---

## Defect Summary

**What happens:** After populating intake fields (CRM parse + manual corrections), reloading the page clears all fields to defaults. Data IS stored in localStorage, but `loadIntake()` rejects it during validation and falls back to factory defaults.

**Root cause (from Empiricus diagnostic logging):**
- `loadIntake()` hits the `recovery-merge-invalid` branch on reload
- Schema validation rejects stored CRM data because these fields are missing:
  - `crmData.address.lat` / `crmData.address.lng` (populated later by geocoder, not at parse time)
  - `crmData.rawText` (not returned by parse-crm-notes edge function)
  - `crmData.parsedAt` (not returned by parse-crm-notes edge function)
  - `crmData.confidence` (not returned by parse-crm-notes edge function)
- Recovery merge attempts to salvage but still fails validation
- Returns `null` → factory defaults → fields wiped

**Governing authority:** Parser + Trigger Contract v2.1, Rule 8 (Persistence Law):
> "Partially enriched parser output MUST be storable and reloadable without being discarded. Missing non-critical parser metadata MUST NOT invalidate meaningful user-facing saved data."

---

## What's Already Fixed (from v1 brief)

Commit `cb93aed` already in main:
- `hydrationSourceRef` tracking ('storage' | 'default' | 'user')
- Cross-page sync gated against factory-default state
- Diagnostic logging in all 5 `loadIntake()` null-return branches

**This was correct but insufficient.** The cross-page sync guard prevents the symptom from propagating, but the root cause is that `loadIntake()` itself rejects valid user data because of strict schema validation on non-critical fields.

---

## Fix Scope (v2)

### Fix: Relax schema validation for non-critical parser metadata

**File:** `src/lib/intake/schema.ts`

**Required change:** Make the following CRM data fields OPTIONAL in the schema validation:
- `crmData.address.lat` — geocoder populates this later, not available at parse time
- `crmData.address.lng` — same
- `crmData.rawText` — parser metadata, not user-facing
- `crmData.parsedAt` — parser metadata, not user-facing  
- `crmData.confidence` — parser metadata, not user-facing

**These are optional metadata per Parser Contract Rule 8.** They are useful when present but must not block persistence/reload.

**The distinction:**
| Field Type | Examples | Must validate? |
|---|---|---|
| **Required canonical (user-facing)** | `clientInfoOverrides.street`, `clientInfoOverrides.clientName`, `crmData.client.name` | Yes — these ARE the user's data |
| **Optional parser metadata** | `crmData.rawText`, `crmData.parsedAt`, `crmData.confidence` | No — useful but not load-blocking |
| **Optional downstream enrichment** | `crmData.address.lat/lng` | No — populated by geocoder later, not at parse time |

### Secondary fix (if needed): Harden recovery merge

**File:** `src/lib/intake/persistence.ts`

If relaxing the schema alone doesn't resolve the `recovery-merge-invalid` path, also check:
- Does the recovery merge in `loadIntake()` (lines ~117-126) correctly handle missing optional fields?
- Does the merge strategy preserve user-facing data while allowing missing metadata?

---

## Files In Scope (exhaustive)

| File | Change Type | Notes |
|---|---|---|
| `src/lib/intake/schema.ts` | MODIFY | Make non-critical CRM metadata fields optional in validation |
| `src/lib/intake/persistence.ts` | MODIFY (if needed) | Harden recovery merge to tolerate missing optional fields |

**Files explicitly OUT of scope:**
- `src/hooks/useIntake.ts` — already has v1 fixes (hydrationSourceRef, cross-page guard), do NOT touch
- `src/pages/Index.tsx` — no changes
- `supabase/functions/*` — no changes to edge functions
- `src/lib/intake/selectors.ts` — no changes
- Any localStorage key names — no changes

---

## Expected Behavior Before/After

| Scenario | Before (broken) | After (fixed) |
|---|---|---|
| CRM parse → reload | All fields wiped (schema rejects stored data) | Fields persist — missing metadata tolerated |
| CRM parse → geocode → reload | Fields wiped | Fields persist — lat/lng present from geocoder, metadata still optional |
| Manual edits → reload | Edits lost | Edits persist |
| Fresh session (no stored data) | Clean start | Clean start (unchanged) |
| Corrupted/invalid stored data | Falls back to defaults | Falls back to defaults (unchanged — truly invalid data should still be rejected) |

---

## Regression Risks

| Risk | Mitigation |
|---|---|
| Truly corrupted data no longer rejected | Only relax METADATA fields. Core schema validation for user-facing canonical fields remains strict. |
| DEF-TB-002 fix regressed | DO NOT touch useIntake.ts, parseCRM, or clientInfoOverridesRef |
| Cross-page sync guard regressed | DO NOT touch hydrationSourceRef or cross-page sync effect |
| DEF-A03 autosave guard weakened | DO NOT touch autosave effect or factory-default detection |
| localStorage key changes | DO NOT rename any keys |

---

## Pre-Commit Checklist (MANDATORY)

- [ ] Only `schema.ts` (and optionally `persistence.ts`) modified
- [ ] Non-critical metadata fields made optional, not removed from schema
- [ ] Required canonical user-facing fields remain strictly validated
- [ ] `useIntake.ts` is UNCHANGED (v1 fixes preserved)
- [ ] `omni-intake-v1` key name/usage UNCHANGED
- [ ] DEF-TB-002 fix (clientInfoOverridesRef) UNCHANGED
- [ ] DEF-A03 guard UNCHANGED
- [ ] No edge function changes
- [ ] No localStorage key renames
- [ ] TypeScript compiles clean
- [ ] Parser + Trigger Contract Rule 8 compliance: missing metadata does not invalidate stored user-facing data

---

## Validation Plan (Empiricus, post-deploy)

### Primary validation (TB-003):
1. Open https://omnipoolsaz.com/
2. Paste CRM note → verify fields populate
3. Make a manual correction (change address)
4. **RELOAD the page**
5. **CRITICAL CHECK: All intake fields persist after reload**
6. Verify CRM data, manual corrections, and downstream values survived

### Regression checks:
7. DEF-TB-002: manual correction → CRM re-parse → correction preserved
8. DEF-A03: reload again → data still persists
9. Fresh incognito session → clean start, no errors

### Diagnostic capture:
10. Open browser console during reload
11. Check for `loadIntake()` diagnostic warnings — should show NO warnings on successful load
12. If warnings present, report which branch and field names

Report PASS/FAIL per step.

---

## Sequence

1. ✅ Characterization (Daedalus)
2. ✅ Fix brief v1 — cross-page sync guard (implemented, correct but insufficient)
3. ✅ Fix brief v2 — schema validation fix (this document)
4. ⏳ Plato implements
5. ⏳ Daedalus reviews against checklist
6. ⏳ Aaron publishes via Lovable
7. ⏳ Empiricus validates
8. ⏳ Governed update: DEF-TB-003 → fix-verified or fix-failed
9. ⏳ Then scope DEF-TB-001 separately

---

*Brief authored by Aristotle | Grounded in Parser + Trigger Contract v2.1 Rule 8 (Persistence Law)*
