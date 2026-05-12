# DEF-TB-002 Fix Brief — Manual Correction Overwrite on CRM Re-Parse

**Date:** 2026-03-20
**Severity:** High
**Owner:** Plato (implementation) + Daedalus (review)
**Validator:** Empiricus (post-deploy)
**Scope:** NARROW — DEF-TB-002 only. Do NOT touch DEF-TB-001 in this cycle.

---

## Defect Summary

**What happens:** Designer manually corrects Project Address → all downstream fields propagate correctly → CRM re-parse fires (debounced auto-trigger or manual "Re-parse") → manual correction is silently reverted to original CRM-parsed values. No warning, no merge, no indication that work was lost.

**Reproduced by Empiricus on production (2026-03-20):** Manual address `4828 W Condor Dr, Tucson, AZ 85742` accepted → sq ft changed to 1,403, year built to 1984 → CRM re-parse reverted address to `8880 N Camino Coronado`, sq ft to 1,052, year built to 1953.

---

## Root Cause (confirmed by code review)

**File:** `src/hooks/useIntake.ts`
**Function:** `parseCRM` (lines ~518–647)

1. `parseCRM` is memoized with `useCallback(..., [])` — **empty dependency array**
2. Inside the stale closure, it reads `intake.clientInfoOverrides?.street` to decide whether manual overrides exist (line ~578)
3. Because deps are `[]`, it captures the *initial* `intake` state — it never sees subsequent manual edits
4. On re-parse, it reconstructs `newOverrides` from the stale captured object (lines ~591–623) and dispatches `SET_CLIENT_OVERRIDES`
5. This silently replaces the current manual corrections with parser-derived values

**Auto-trigger path:** `src/pages/Index.tsx:221-222` — debounced effect watches `intake.siteInfoText` changes and calls `parseCRM(intake.siteInfoText)`

**Manual trigger path:** `src/pages/Index.tsx:514-515` — "Re-parse" button calls `parseCRM(intake.siteInfoText)`

---

## Fix Scope

### Target: `src/hooks/useIntake.ts` — `parseCRM` function

**Required behavior change:**
- When `parseCRM` runs, it MUST check the **current** `clientInfoOverrides` state (not a stale closure capture) to determine if manual edits exist
- If manual overrides are present for a field, CRM re-parse MUST NOT overwrite that field
- Manual correction authority is absolute — parser values are suggestions, manual edits are decisions

### Recommended approach (choose one):

**Option A — Fix the stale closure:**
- Add `intake.clientInfoOverrides` to the `useCallback` dependency array
- Ensure `hasExistingOverride` check reads current state
- Risk: may cause unnecessary re-renders / re-memoization. Assess impact.

**Option B — Use a ref for current overrides:**
- Create `const overridesRef = useRef(intake.clientInfoOverrides)` 
- Keep `overridesRef.current` updated via effect
- `parseCRM` reads `overridesRef.current` instead of captured `intake`
- This preserves `useCallback(..., [])` stability while getting fresh state
- Lower risk of re-render cascades

**Option C — Field-level dirty tracking:**
- Add a `manuallyEdited: Set<string>` to intake state
- `ParsedClientInfo` onChange adds field name to set
- `parseCRM` skips any field in the `manuallyEdited` set
- Most robust long-term, but larger change surface

**Recommendation:** Option B (ref pattern) for narrowest change with correct behavior. Option C is better architecture but wider scope — defer to a future hardening pass.

---

## Expected Behavior Before/After

| Scenario | Before (broken) | After (fixed) |
|---|---|---|
| CRM parse → manual address edit → CRM re-parse | Manual edit silently reverted | Manual edit preserved; parser skips overridden fields |
| CRM parse → no manual edits → CRM re-parse | Parser values applied | Parser values applied (unchanged) |
| CRM parse → manual edit to ONE field → re-parse | ALL fields reverted | Only non-manually-edited fields updated by parser |
| Manual "Re-parse" button click after edits | Edits lost | Edits preserved for manually-touched fields |

---

## Files In Scope (exhaustive)

| File | Change Type | Notes |
|---|---|---|
| `src/hooks/useIntake.ts` | MODIFY | Fix `parseCRM` stale closure — primary fix location |

**Files explicitly OUT of scope:**
- `src/lib/intake/selectors.ts` — no changes (DEF-TB-001 territory)
- `src/lib/intake/schema.ts` — no changes
- `src/lib/intake/persistence.ts` — no changes
- `supabase/functions/*` — no changes
- `src/components/intake/ParsedClientInfo.tsx` — no changes unless Option C chosen
- `src/pages/Index.tsx` — no changes (trigger paths are correct, the bug is in the callback)

---

## Regression Risks

| Risk | Mitigation |
|---|---|
| Autosave/localStorage key changes break Track A persistence fix | **DO NOT** change `omni-intake-v1` key or autosave logic. Fix is inside `parseCRM` only. |
| Address overwrite regression | Manual correction must remain authoritative. Test: edit address → re-parse → verify edit persists. |
| lat/lng write without coordSource | **DO NOT** add any lat/lng write path. If Option B ref is used, it only reads overrides — no coordinate writes. |
| Re-render cascade from dependency change (Option A) | If Option A chosen, verify no infinite re-render loop from `parseCRM` → state change → `parseCRM` re-memo → state change. |
| Cross-page sync corruption | **DO NOT** touch `omni-intake-cross-page` logic. |
| State factory-default overwrite | **DO NOT** touch init/load/autosave guard (DEF-A03 protection). |

---

## Pre-Commit Checklist (MANDATORY)

Before committing the fix, verify ALL of the following:

- [ ] `omni-intake-v1` localStorage key usage is UNCHANGED
- [ ] `omni-intake-cross-page` localStorage key usage is UNCHANGED
- [ ] Autosave/`debouncedSaveIntake` logic is UNCHANGED
- [ ] No new lat/lng write path introduced
- [ ] `coordSource` protections are UNCHANGED
- [ ] `selectResolvedLocation()` is UNCHANGED
- [ ] No changes to `persistence.ts`
- [ ] No changes to edge functions
- [ ] Manual address correction persists through: (a) page reload, (b) CRM re-parse, (c) tab switch
- [ ] CRM parse still works correctly on first paste (no manual edits yet)
- [ ] DEF-A03 state loss regression test: reload page → intake data still present
- [ ] `stripCityFromAddress()` behavior is UNCHANGED

---

## Validation Plan (Empiricus, post-deploy)

1. Paste CRM note → verify auto-parse populates all fields correctly
2. Manually change Project Address → verify downstream propagation
3. Trigger CRM re-parse → **verify manual address correction is preserved**
4. Verify non-manually-edited fields still update from parser
5. Reload page → verify all data persists (Track A regression check)
6. Report PASS/FAIL per step to governed-objects

---

## Sequence

1. Plato implements fix per this brief
2. Daedalus reviews against pre-commit checklist
3. Deploy to production (Lovable)
4. Empiricus validates DEF-TB-002 only per validation plan above
5. Governed update: DEF-TB-002 status → `fix-verified` or `fix-failed`
6. THEN scope DEF-TB-001 separately

---

*Brief authored by Aristotle | Source: Daedalus code review packet + Steel Man integrity note + Empiricus validation report*
