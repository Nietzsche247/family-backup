# DEF-TB-003 Code Review — commit `cb93aed`

**Date:** 2026-03-20  
**Reviewer:** Daedalus  
**Source repo:** `C:\Users\aaron\clawd-shared\omnipools-repo`  
**Compared commits:** `8d30b34` → `cb93aed`  
**Review type:** Re-review of amended fix after prior blocking feedback

## Summary

**Overall result: FAIL**

The amended change **does resolve the original blocking issue** from the prior review:
- the `'default'` → `'user'` promotion logic now covers the previously missed meaningful mutation paths
- the promotion check now includes:
  - `siteInfoText`
  - `crmData`
  - `clientInfoOverrides`
  - `poolStats`
  - `panelAnalysis`
  - `equipmentAnalysis`
  - `plumbingSpecs`
  - `manualMainBreakerOverride`
- the cross-page sync guard against factory-default fallback remains correct
- no new broad-scope regressions were introduced in the touched files

However, the amended implementation still does **not** fully satisfy the re-review requirements because:
- the **promotion effect dependency array does not match the cross-page sync effect dependency array exactly**
- specifically, the promotion effect depends on `intake.siteInfoText`, while the cross-page sync effect does **not**

That means the prior blocking defect is fixed, but the explicit dependency-array parity requirement is still unmet.

---

## Exact diff scope verified

`git diff --name-only 8d30b34 cb93aed` shows exactly:
- `src/hooks/useIntake.ts`
- `src/lib/intake/persistence.ts`

No other files changed.

---

## Re-review against requested focus

### 1) Blocking issue resolved — promotion now covers all cross-page fields

**Result: PASS**

In `src/hooks/useIntake.ts`, the promotion effect now checks:

```ts
const hasContent = intake.siteInfoText || intake.crmData ||
  (intake.clientInfoOverrides && Object.keys(intake.clientInfoOverrides).length > 0) ||
  intake.poolStats || intake.panelAnalysis || intake.equipmentAnalysis ||
  intake.plumbingSpecs || intake.manualMainBreakerOverride != null;
```

This closes the prior gap where promotion failed to occur when the first meaningful mutation landed in:
- `poolStats`
- `panelAnalysis`
- `equipmentAnalysis`
- `plumbingSpecs`
- `manualMainBreakerOverride`

So the original blocker from the previous review is resolved.

### 2) Promotion effect dependency array matches cross-page sync effect

**Result: FAIL**

Promotion effect dependencies are:

```ts
[intake.siteInfoText, intake.crmData, intake.clientInfoOverrides, intake.poolStats, intake.panelAnalysis, intake.equipmentAnalysis, intake.plumbingSpecs, intake.manualMainBreakerOverride]
```

Cross-page sync effect dependencies are:

```ts
[intake.updatedAt, intake.poolStats, intake.panelAnalysis, intake.equipmentAnalysis, intake.crmData, intake.plumbingSpecs, intake.clientInfoOverrides, intake.manualMainBreakerOverride]
```

These arrays do **not** match exactly:
- promotion effect includes `intake.siteInfoText`
- cross-page sync effect includes `intake.updatedAt`
- cross-page sync effect does **not** include `intake.siteInfoText`

So the parity claim is not accurate.

### 3) Same checklist from prior review re-run

**Result: MIXED — all prior checklist items pass except the newly requested dependency-parity requirement**

Detailed checklist below.

### 4) No new issues introduced by amendment

**Result: PASS with note**

I do not see any new broad regressions introduced by the amendment beyond the dependency-array mismatch noted above. The scope remains tight and the original fix direction remains sound.

---

## Checklist Review

- **PASS** — `omni-intake-v1` localStorage key name and usage is UNCHANGED  
  Verified in `src/lib/intake/persistence.ts`: `const STORAGE_KEY = 'omni-intake-v1';` remains unchanged. `useIntake.ts` cross-page logic still does not write to this key directly.

- **PASS** — `omni-intake-cross-page` localStorage key name is UNCHANGED  
  Verified in `useIntake.ts`: cross-page sync still writes `localStorage.setItem('omni-intake-cross-page', ...)`.

- **PASS** — Autosave effect is UNCHANGED in behavior  
  The autosave effect and DEF-A03 overwrite guard remain unchanged apart from line displacement.

- **PASS** — DEF-A03 factory-default overwrite guard is UNCHANGED  
  The `isFactoryDefault` guard and the `omni-intake-v1` overwrite prevention logic are unchanged.

- **PASS** — DEF-TB-002 fix (`clientInfoOverridesRef`, `parseCRM`) is UNCHANGED  
  `clientInfoOverridesRef` remains present and synchronized as before. No TB-002 regression found.

- **PASS** — `createInitialIntake()` and schema defaults are UNCHANGED  
  No schema files changed. Diff scope remains limited to the two intended files.

- **PASS** — No changes to edge functions  
  No files under `supabase/functions/*` changed.

- **PASS** — No changes to `selectResolvedLocation()`  
  No selector files changed.

- **PASS** — Cross-page sync still works after user makes any relevant mutation  
  This was the prior blocking failure, and it is now fixed. The promotion effect now recognizes all previously missed fields relevant to the reported issue.

- **PASS** — Cross-page sync does NOT fire when state is factory-default fallback  
  The early return on `hydrationSourceRef.current === 'default'` still correctly prevents default-state cross-page overwrite.

- **PASS** — Diagnostic logging does not throw errors or affect control flow  
  The warn-path additions remain side-effect-free from a control-flow perspective.

- **PASS** — `Index.tsx` auto-restore logic is UNCHANGED  
  No `Index.tsx` diff; file is outside the changed scope.

- **FAIL** — Promotion effect dependency array mirrors cross-page sync effect exactly  
  It does not. `siteInfoText` appears only in the promotion effect dependency list, while `updatedAt` appears only in the cross-page sync effect dependency list.

---

## Additional Verification

### 1) `hydrationSourceRef` pattern correctness

**Result: PASS**

What is correct:
- initial state sets source to `'storage'` when `loadIntake()` succeeds
- initial fallback sets source to `'default'`
- session-load hydration sets source to `'storage'`
- cross-page sync is gated on `'default'`
- promotion now covers the previously missed meaningful mutation paths

### 2) Promotion logic soundness

**Result: PASS**

The amended `hasContent` check now includes the fields that were previously omitted and resolves the substantive under-promotion issue identified in the prior review.

### 3) No case from prior review where cross-page sync remains blocked after the first meaningful mutation

**Result: PASS**

The previously documented scenarios involving first mutation in:
- `panelAnalysis`
- `poolStats`
- `equipmentAnalysis`
- `plumbingSpecs`
- `manualMainBreakerOverride`

are now covered by the promotion effect.

### 4) The 5 diagnostic warn paths in `persistence.ts` correctly identify each null-return branch

**Result: PASS**

Warnings remain present for the same five null-return paths:
1. `key-not-found`
2. `partial-fragment-guard`
3. `recovery-merge-invalid`
4. `recovery-merge-threw`
5. `top-level-catch`

### 5) No interaction between this fix and DEF-TB-002's `clientInfoOverridesRef`

**Result: PASS**

No adverse interaction found.

---

## Remaining concern

### Concern 1 — Dependency-array parity requirement is still unmet

If the requirement is that the promotion effect dependency array should mirror the cross-page sync effect dependency array exactly, the current implementation does not meet that requirement.

Current mismatch:
- promotion effect includes `siteInfoText`
- cross-page sync effect includes `updatedAt`
- arrays therefore diverge in both membership and semantics

This is the only remaining review failure I found in the amended commit.

---

## Recommended disposition

**Do not approve as-is if exact dependency-array parity is a release requirement.**

If the intended acceptance criteria are:
1. fix the original blocker, and
2. make the promotion dependency list exactly mirror the cross-page sync dependency list,

then commit `cb93aed` is still **not fully complete**.

If the team decides exact dependency parity is non-essential and only the substantive promotion-coverage bug matters, then the code is functionally much improved and the original blocker is resolved. But against the re-review brief as written, this remains a **FAIL**.

## Suggested fix direction

Make a deliberate choice and align the two effects accordingly:
- either remove `siteInfoText` from the promotion effect dependency list, or
- add corresponding dependency intent to the cross-page sync effect and document why,
- and ensure the final dependency sets are intentionally identical if that parity is required.