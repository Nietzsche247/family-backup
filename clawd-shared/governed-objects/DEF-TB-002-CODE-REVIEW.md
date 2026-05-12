# DEF-TB-002 Code Review — commit `8d30b34`

**Date:** 2026-03-20
**Reviewer:** Daedalus
**Repo:** `C:\Users\aaron\clawd-shared\omnipools-repo`
**Commit reviewed:** `8d30b3457d89fc6d04d414d777766bea8e2474ae`
**Result:** **PASS**

## Summary

Reviewed commit `8d30b34` against the DEF-TB-002 fix brief.

The implementation is **narrow, correct, and safe** for the stated defect:
- It introduces a `useRef` mirror of `intake.clientInfoOverrides`
- It keeps that ref synchronized on every render
- `parseCRM` now reads the ref instead of the stale closure-captured `intake.clientInfoOverrides`
- `parseCRM` remains memoized with `useCallback(..., [])`, preserving stable identity
- No other files were modified

This correctly fixes both stale-closure failure points in `parseCRM`:
1. `hasExistingOverride` now reads current state
2. `newOverrides` now spreads current state

## Checklist Review

- **PASS** — `omni-intake-v1` localStorage key usage is **UNCHANGED**
  - `useIntake.ts` still reads `localStorage.getItem('omni-intake-v1')` in the existing autosave guard path.
  - No change to key name or ownership.

- **PASS** — `omni-intake-cross-page` localStorage key usage is **UNCHANGED**
  - Existing cross-page sync effect still writes to `localStorage.setItem('omni-intake-cross-page', JSON.stringify(storageData))`.
  - No change to key name or sync behavior.

- **PASS** — Autosave / `debouncedSaveIntake` logic is **UNCHANGED**
  - Existing autosave effect and `debouncedSaveIntake(intake, saveDebounceMs)` call remain unchanged.
  - No changes to guard conditions, debounce behavior, or save flow.

- **PASS** — No new lat/lng write path introduced
  - The CRM parse path already wrote `latitude` / `longitude` into `newOverrides` when present.
  - The fix only changed the source object spread from stale `intake.clientInfoOverrides` to current `clientInfoOverridesRef.current`.
  - No additional coordinate-writing path was added.

- **PASS** — `coordSource` protections are **UNCHANGED**
  - Existing `coordSource: 'forward-geocode'` write in `retryGeocoding` is unchanged.
  - `parseCRM` still does not add or alter `coordSource` behavior.

- **PASS** — `selectResolvedLocation()` is **UNCHANGED**
  - No changes to selector implementation or its call sites related to this fix.

- **PASS** — No changes to `persistence.ts`
  - Commit diff shows no modification to `src/lib/intake/persistence.ts`.

- **PASS** — No changes to edge functions
  - Commit diff shows no modification under `supabase/functions/*`.

- **PASS** — Only `useIntake.ts` was modified
  - `git diff --name-only 8d30b34^ 8d30b34` returns only `src/hooks/useIntake.ts`.

- **PASS** — The ref pattern correctly solves the stale closure (parseCRM will now read current overrides)
  - `clientInfoOverridesRef` is initialized from `intake.clientInfoOverrides`.
  - `clientInfoOverridesRef.current = intake.clientInfoOverrides` keeps the ref current every render.
  - Inside `parseCRM`, both the override-presence check and spread now use `currentOverrides = clientInfoOverridesRef.current`.
  - This removes reliance on the initial `intake` captured by `useCallback(..., [])`.

- **PASS** — No infinite re-render risk from the ref sync pattern
  - Assigning to `clientInfoOverridesRef.current` does **not** trigger a render.
  - It is a mutable ref write, not React state.
  - Therefore this pattern does not create a render loop.

- **PASS** — `useCallback` dependency array is still `[]` (stable identity preserved)
  - `parseCRM` remains declared as `const parseCRM = useCallback(async (text: string) => { ... }, []);`

## Additional Verification

### Ref sync pattern is standard and safe
**PASS**

This is a standard React escape-hatch pattern for reading the latest mutable value from a stable callback. Using:

```ts
const clientInfoOverridesRef = useRef(intake.clientInfoOverrides);
clientInfoOverridesRef.current = intake.clientInfoOverrides;
```

is safe because:
- `useRef` preserves object identity across renders
- updating `.current` does not schedule state updates
- the stable callback can read the latest value at execution time

Using direct assignment during render is acceptable here because the ref is only being synchronized to current state and is not used to drive rendering.

### No missed `intake.clientInfoOverrides` references inside `parseCRM`
**PASS**

Reviewed `parseCRM` specifically. After the fix:
- `hasExistingOverride` uses `currentOverrides?.street`
- `newOverrides` uses `...currentOverrides`

No remaining direct references to `intake.clientInfoOverrides` were found inside `parseCRM`.

### Both symptoms are addressed
**PASS**

The fix addresses both required symptoms:
- **(a)** `hasExistingOverride` now sees current state via `clientInfoOverridesRef.current`
- **(b)** `newOverrides` now spreads current state via `...currentOverrides`

This means a manual correction made after initial render will no longer be lost because of the stale closure.

## Concerns / Notes

### No blocking concerns
The implementation is appropriately narrow and matches the fix brief's recommended Option B.

### Minor note on behavior scope
The existing overwrite guard is still keyed off `street` (`const hasExistingOverride = currentOverrides?.street`). That behavior was already present before this fix and was **not** changed by this commit. This review treats that as intentional and in-scope preservation, not a defect introduced by the fix.

## Final Verdict

**PASS** — Commit `8d30b34` correctly and safely implements the DEF-TB-002 stale-closure fix with a narrow `useRef` pattern in `src/hooks/useIntake.ts` only, while preserving stable callback identity and leaving the broader persistence/autosave/geocoding protections unchanged.
