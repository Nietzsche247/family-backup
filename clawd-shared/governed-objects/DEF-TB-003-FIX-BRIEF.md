# DEF-TB-003 Fix Brief — Cross-Page Rehydration / Reload Persistence Failure

**Date:** 2026-03-20
**Severity:** Medium-High
**Owner:** Plato (implementation) + Daedalus (review)
**Validator:** Empiricus (post-deploy)
**Scope:** NARROW — DEF-TB-003 only. This is NOT a general persistence rewrite.

---

## Defect Summary

**What happens:** After populating intake fields (CRM parse + manual corrections), reloading the page causes all intake fields to reset to blank defaults. localStorage keys exist and contain data, but the app overwrites them with factory defaults during initialization.

**Discovered by Empiricus (2026-03-20):** During DEF-TB-002 validation, Step 9 reload test failed. `omni-intake-v1` and `omni-intake-cross-page` both present after reload, but `omni-intake-cross-page` collapsed to `crmData: null`, `clientInfoOverrides: {}`, other fields empty.

---

## Root Cause (from characterization)

**Primary failure chain:**

1. `useIntake()` init calls `loadIntake()` synchronously (`useIntake.ts:315-320`)
2. `loadIntake()` returns `null` — key exists but is rejected (validation failure, schema mismatch, or partial-fragment guard)
3. Hook falls back to `createInitialIntake()` — factory defaults
4. Factory defaults have truthy `updatedAt` (`schema.ts:848-851`), making them look like "real" state
5. Cross-page sync effect (`useIntake.ts:381-397`) fires on first mount, sees truthy `updatedAt`
6. Overwrites `omni-intake-cross-page` with empty/default subset — **no guard protects this path**
7. DEF-A03 guard on `omni-intake-v1` autosave works correctly, but is not applied to cross-page writes

**Classification:** Initialization guard-gap logic error. Not a race condition. Not a browser limitation.

---

## Fix Scope

### Two changes, both in existing files:

### Fix 1 (PRIMARY): Gate cross-page sync until hydration is confirmed
**File:** `src/hooks/useIntake.ts`
**Target:** Cross-page sync effect (lines ~381-397)

**Required behavior change:**
- Do NOT write to `omni-intake-cross-page` when the current state is factory-default fallback
- Only write to `omni-intake-cross-page` when state was successfully loaded from storage OR has been mutated by user action

**Recommended approach:**
Add a `hydrationSource` ref or state flag that tracks whether the current intake came from:
- `'storage'` — successfully loaded from `omni-intake-v1`
- `'default'` — fell back to `createInitialIntake()`
- `'user'` — user has made at least one mutation (CRM paste, manual edit, etc.)

Gate the cross-page sync effect:
```typescript
// Only sync to cross-page when state is known-good (not factory defaults)
if (hydrationSourceRef.current === 'default') {
  return; // Skip cross-page write — state hasn't been confirmed yet
}
```

**Alternative (simpler):** Skip cross-page write when state matches factory-default signature AND `omni-intake-v1` exists with content. This mirrors the DEF-A03 pattern already used in autosave.

### Fix 2 (DIAGNOSTIC): Log which `loadIntake()` null-return branch is hit
**File:** `src/lib/intake/persistence.ts`
**Target:** `loadIntake()` function (lines ~79-132)

**Required behavior change:**
- Add `console.warn` at each null-return branch identifying WHY load failed:
  - Key not found
  - Partial-fragment guard triggered (lines ~86-91)
  - Migration failure
  - Validation failure
  - Recovery merge failure
- This is diagnostic only — no behavior change. Lets us (and Empiricus) see exactly which branch rejects the stored data.

---

## Files In Scope (exhaustive)

| File | Change Type | Notes |
|---|---|---|
| `src/hooks/useIntake.ts` | MODIFY | Gate cross-page sync effect (~381-397). Add hydration source tracking (~315-320). |
| `src/lib/intake/persistence.ts` | MODIFY | Add diagnostic logging to null-return branches in `loadIntake()` (~79-132). |

**Files explicitly OUT of scope:**
- `src/lib/intake/schema.ts` — do NOT change `createInitialIntake()` or `updatedAt` default
- `src/pages/Index.tsx` — do NOT change auto-restore heuristic (separate risk, not TB-003 primary)
- `src/hooks/useIntakeReader.ts` — no changes (read path, not write path)
- `src/hooks/useIntakeSessions.ts` — no changes
- `supabase/functions/*` — no changes
- Any localStorage key names — do NOT rename or restructure keys

---

## Expected Behavior Before/After

| Scenario | Before (broken) | After (fixed) |
|---|---|---|
| Reload after CRM parse + manual edits | All fields clear to blank | Fields persist from `omni-intake-v1` |
| Reload when `loadIntake()` fails validation | `omni-intake-cross-page` overwritten with empty defaults | Cross-page key preserved; diagnostic log shows WHY load failed |
| First visit (no stored data) | Factory defaults shown, cross-page written | Factory defaults shown, cross-page write SKIPPED (nothing to sync) |
| Normal usage after successful load | Cross-page syncs on every change | Cross-page syncs on every change (unchanged) |
| CRM paste on fresh session | Fields populate, cross-page syncs | Fields populate, cross-page syncs (unchanged — hydration source becomes 'user') |

---

## Regression Risks

| Risk | Mitigation |
|---|---|
| Cross-page data goes stale for downstream readers | Downstream readers (`useIntakeReader.ts:104-117`) already fall back to `omni-intake-v1` when cross-page key is missing/stale. This is safe. |
| DEF-A03 autosave guard weakened | DO NOT touch autosave effect (lines ~343-376). Fix is in cross-page effect only. |
| DEF-TB-002 fix regressed | DO NOT touch `parseCRM`, `clientInfoOverridesRef`, or `useCallback` deps. |
| localStorage key changes break existing sessions | DO NOT rename any keys. |
| Factory-default `updatedAt` behavior changed | DO NOT modify `createInitialIntake()` or schema defaults. Gate at the effect level, not the data level. |
| `omni-intake-cross-page` never written | Only blocked during factory-default state. Once user mutates state or storage loads successfully, sync resumes normally. |

---

## Pre-Commit Checklist (MANDATORY)

Before committing the fix, verify ALL of the following:

- [ ] `omni-intake-v1` localStorage key name and usage is UNCHANGED
- [ ] `omni-intake-cross-page` localStorage key name is UNCHANGED
- [ ] Autosave effect (lines ~343-376) is UNCHANGED
- [ ] DEF-A03 factory-default overwrite guard is UNCHANGED
- [ ] DEF-TB-002 fix (clientInfoOverridesRef, parseCRM) is UNCHANGED
- [ ] `createInitialIntake()` and schema defaults are UNCHANGED
- [ ] No changes to edge functions
- [ ] No changes to `selectResolvedLocation()`
- [ ] Cross-page sync still works after user makes any mutation (CRM paste, manual edit)
- [ ] Cross-page sync does NOT fire when state is factory-default fallback
- [ ] Diagnostic logging does not throw errors or affect control flow
- [ ] `Index.tsx` auto-restore logic is UNCHANGED

---

## Validation Plan (Empiricus, post-deploy)

### Primary validation (TB-003 specific):
1. Open https://omnipoolsaz.com/
2. Paste CRM note → verify fields populate
3. Make a manual correction (change address)
4. **Reload the page**
5. **CRITICAL CHECK: Verify all intake fields persist after reload**
6. Verify CRM data, manual corrections, and downstream computed values all survived

### Regression checks:
7. DEF-TB-002 check: manual correction → CRM re-parse → verify correction preserved
8. DEF-A03 check: reload again → verify data still persists (no factory-default overwrite)
9. Fresh incognito session: verify clean start works (no stale data, no errors)

### Diagnostic capture:
10. Open browser console during reload — capture any `loadIntake()` diagnostic logs
11. Report which branch was logged (if any) — this tells us if the load path has a deeper issue

Report PASS/FAIL per step to governed-objects.

---

## Sequence

1. ✅ Characterization complete (Daedalus)
2. ✅ Fix brief authored (Aristotle)
3. ⏳ Plato implements fix per this brief
4. ⏳ Daedalus reviews against pre-commit checklist
5. ⏳ Deploy to production (Lovable publish)
6. ⏳ Empiricus validates TB-003 per validation plan
7. ⏳ Governed update: DEF-TB-003 status → `fix-verified` or `fix-failed`
8. ⏳ THEN scope DEF-TB-001 separately

---

## What This Brief Is NOT

- NOT a general persistence rewrite
- NOT a redesign of localStorage key structure
- NOT a widening into DEF-TB-001 (jurisdiction)
- NOT a change to autosave or DEF-A03 protections
- NOT a change to session restoration logic

It is a **narrow guard addition** to prevent factory-default state from being treated as hydrated real data in the cross-page sync path, plus **diagnostic logging** to identify why `loadIntake()` rejects stored data.

---

*Brief authored by Aristotle | Source: Daedalus characterization report (DEF-TB-003-CHARACTERIZATION.md)*
