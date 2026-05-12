# DEF-TB-003 Characterization — Reload Persistence / Rehydration Failure

## Scope
Bounded characterization of reload persistence / rehydration behavior in commit `8d30b34`.

Files analyzed:
- `src/hooks/useIntake.ts`
- `src/lib/intake/persistence.ts`
- `src/lib/intake/schema.ts`
- `src/hooks/useIntakeReader.ts`
- `src/hooks/useIntakeSessions.ts`
- `src/pages/Index.tsx`

---

## Executive Summary
This does **not** look like a browser persistence problem. The browser is preserving local/session storage correctly.

The likely failure mode is:
1. On page reload, `useIntake()` calls `loadIntake()` synchronously during reducer initialization.
2. If `loadIntake()` returns `null` for any reason, `useIntake()` falls back to `createInitialIntake()`.
3. That factory-default state already has a truthy `updatedAt`, so the cross-page sync effect runs immediately on first mount.
4. That effect overwrites `omni-intake-cross-page` with a partial/default object.
5. DEF-A03 protection only guards writes to `omni-intake-v1`; it does **not** guard writes to `omni-intake-cross-page`.

So the observed collapse of `omni-intake-cross-page` is real and deterministic, but it is probably a **downstream symptom** of failed full-state rehydration, not the original source of the intake-tab wipe.

### Classification
- **Primary issue type:** logic error / initialization guard gap
- **Not a classic async race** between “write defaults” and “read storage” inside `useIntake` — load is synchronous before effects
- **DEF-A03 guard involvement:** yes, but only partially. The guard protects `omni-intake-v1` autosave; it does not protect `omni-intake-cross-page` first-mount sync.

---

## Exact Initialization Sequence on Page Load

### 1) `useIntake()` initializes from `loadIntake()`
In `src/hooks/useIntake.ts:314-320`:
- `getInitialState()` calls `loadIntake()`
- if truthy, uses stored intake
- otherwise falls back to `createInitialIntake()`

Relevant lines:
- `useIntake.ts:315-317` — `const stored = loadIntake(); return stored || createInitialIntake();`
- `useIntake.ts:320` — reducer initialized with `getInitialState`

This load happens **synchronously during render initialization**, before any React effects run.

### 2) Factory default state already has `updatedAt`
In `src/lib/intake/schema.ts:848-851`, `createInitialIntake()` sets:
- `schemaVersion`
- `createdAt`
- `updatedAt`

That means a freshly-created default intake is immediately considered “updated” from the effect system’s point of view.

Relevant lines:
- `schema.ts:848-851`

### 3) Autosave effect runs after mount
In `src/hooks/useIntake.ts:343-376`, a `useEffect` runs whenever `intake` changes.

Behavior:
- if `autoSave` enabled, it evaluates a DEF-A03-style `isFactoryDefault` condition
- if current state looks factory-default **and** `omni-intake-v1` already contains meaningful content, it skips autosave
- otherwise it calls `debouncedSaveIntake(intake, saveDebounceMs)`

Relevant lines:
- `useIntake.ts:343-376`
- `useIntake.ts:349-356` — factory-default test
- `useIntake.ts:358-369` — overwrite guard against real data in `omni-intake-v1`
- `useIntake.ts:374` — `debouncedSaveIntake(...)`

### 4) Cross-page sync effect also runs after mount
In `src/hooks/useIntake.ts:381-397`, another `useEffect` runs when `intake.updatedAt` and several intake fields are present in deps.

Behavior:
- if `intake.updatedAt` is truthy, it writes a subset of intake to `omni-intake-cross-page`
- subset includes: `poolStats`, `panelAnalysis`, `equipmentAnalysis`, `crmData`, `plumbingSpecs`, `clientInfoOverrides`, `manualMainBreakerOverride`
- then emits `omni-intake-updated`

Relevant lines:
- `useIntake.ts:381-397`
- `useIntake.ts:392` — `localStorage.setItem('omni-intake-cross-page', JSON.stringify(storageData))`

This effect has **no equivalent factory-default overwrite guard**.

### 5) Session-load listener is installed, but only reacts to explicit session load events
In `src/hooks/useIntake.ts:399-420`, the hook listens for `omni-session-loaded` and then re-runs `loadIntake()`.

This is **not** part of ordinary reload hydration. It only fires when some other code explicitly dispatches `omni-session-loaded`.

Relevant lines:
- `useIntake.ts:399-420`

### 6) Index page may try one-time session auto-restore for authenticated users
In `src/pages/Index.tsx:87-143`, a mount effect may:
- skip if `sessionStorage['omni-session-restored']` already exists
- skip if `omni-intake-v1` already has “meaningful” data (`siteInfoText`, `crmData.client.name`, or `panelImages.length > 0`)
- otherwise fetch most recent cloud session
- write its `state_json` into `omni-intake-v1`
- set `omni-session-restored=true`
- reload page

Relevant lines:
- `Index.tsx:96-99` — session restore flag check
- `Index.tsx:102-109` — local-storage-content heuristic
- `Index.tsx:132` — writes session JSON to `omni-intake-v1`
- `Index.tsx:139` — sets `omni-session-restored`
- `Index.tsx:142` — reloads page

This path can overwrite local storage, but only when its heuristic decides local data is not meaningful.

---

## Persistence Module Characterization (`src/lib/intake/persistence.ts`)

## How save works
`saveIntake()`:
- serializes intake
- strips `File` objects from file arrays
- stamps a fresh `updatedAt`
- writes JSON to `omni-intake-v1`

Relevant lines:
- `persistence.ts:62-68`

Important implication:
- persisted file metadata survives
- actual `File` blobs do **not** survive reload

## How load works
`loadIntake()`:
1. reads `omni-intake-v1`
2. returns `null` if key missing
3. parses JSON
4. applies DEF-A03 partial-fragment guard: if no `schemaVersion` and `<10` keys, treat as cross-page fragment and return `null`
5. runs migration if needed
6. deserializes file-array shape (files restored as `undefined`)
7. validates with schema
8. if validation fails, attempts deep-merge recovery over `createInitialIntake()`
9. if recovery still fails, returns `null`

Relevant lines:
- `persistence.ts:79-132`
- `persistence.ts:86-91` — partial-fragment guard
- `persistence.ts:94-97` — migrations
- `persistence.ts:100-106` — primary validation
- `persistence.ts:117-126` — recovery merge success path

## What triggers save vs load
- **Load** is triggered synchronously by `useIntake()` init: `useIntake.ts:315-320`
- **Save** is triggered by the autosave effect in `useIntake.ts:343-376`
- `debouncedSaveIntake()` just schedules `saveIntake()` after the delay: `persistence.ts:243-250`
- `flushSaveIntake()` saves immediately: `persistence.ts:256-261`

---

## Autosave Path Characterization

## `debouncedSaveIntake` timing
`debouncedSaveIntake()` is a module-level debouncer:
- clears previous timeout
- schedules `saveIntake(intake)` after `delayMs`

Relevant lines:
- `persistence.ts:243-250`

In `useIntake`, it fires from the autosave effect whenever `intake` changes and the effect is not short-circuited.

## Can autosave overwrite real data with defaults?
### For `omni-intake-v1`
There is a specific guard intended to stop exactly that.

In `useIntake.ts:349-369`:
- if current state is factory-default-ish
- and existing `omni-intake-v1` has `siteInfoText`, `crmData`, or non-empty `clientInfoOverrides`
- autosave is skipped

So for the **full-state key**, DEF-A03 protection appears present and logically working.

### For `omni-intake-cross-page`
Yes — indirectly.

The cross-page sync effect has **no overwrite guard**, and it runs immediately when a default intake has truthy `updatedAt`.
That means a failed rehydrate can still collapse `omni-intake-cross-page` even when `omni-intake-v1` is preserved.

This matches Empiricus’s observation closely.

---

## `omni-intake-cross-page` Characterization

## What writes to it?
Only one production write path was found:
- `src/hooks/useIntake.ts:381-397`
- actual write at `useIntake.ts:392`

I did **not** find another production `setItem('omni-intake-cross-page', ...)` writer in `src/`.

## What reads from it?
Downstream readers use it, especially:
- `src/hooks/useIntakeReader.ts:104-117`
  - reads `omni-intake-cross-page`
  - falls back to `omni-intake-v1`
- calculator pages/hooks reference the same key via constant declarations

Crucially:
- `useIntake.ts` itself does **not** read `omni-intake-cross-page`
- main intake rehydration comes from `omni-intake-v1`, not the cross-page key

## Why would it collapse to empty defaults after reload?
Because when `useIntake` falls back to `createInitialIntake()`, the cross-page sync effect runs immediately and writes a partial/default subset.

The specific mechanism is:
1. `loadIntake()` returns `null`
2. `createInitialIntake()` creates default state with truthy `updatedAt`
3. `useEffect` at `useIntake.ts:381-397` executes
4. `omni-intake-cross-page` is overwritten with mostly empty/default values

## Is it being overwritten by a different code path during initialization?
Based on code search, **no**. The overwrite appears to come from `useIntake.ts` itself, not a downstream calculator.

---

## Session Restoration Characterization

## Role of `omni-current-session-id`
Defined in `src/hooks/useIntakeSessions.ts:106-107`.

It is used to remember which cloud session is currently associated with the local intake state. It does **not** directly hydrate the intake on normal reload.

The explicit session-load flow is:
- fetch session from Supabase
- write `state_json` into `omni-intake-v1`
- store `omni-current-session-id`
- dispatch `omni-session-loaded`

Relevant lines:
- `useIntakeSessions.ts:106-107`
- `useIntakeSessions.ts:379-405`

## Role of `omni-session-restored=true` in `sessionStorage`
In `Index.tsx:96-99` and `139`:
- it is a one-browser-session flag
- it prevents repeated auto-restoration / reload loops for authenticated users

It does **not** itself clear or load intake data.

## Is there a session-based fetch that might clear local state?
Not on ordinary reload once `omni-session-restored=true` is already present.

The authenticated auto-restore effect in `Index.tsx` can overwrite local intake **only if**:
- user is logged in
- restore has not yet been marked in sessionStorage
- local `omni-intake-v1` fails its “meaningful data” heuristic

That heuristic is narrow:
- `siteInfoText`
- `crmData?.client?.name`
- `panelImages?.length > 0`

Relevant lines:
- `Index.tsx:102-109`

So there is a **possible separate risk** here: local intake could be meaningful but still fail that heuristic. However, this does **not** explain the observed cross-page collapse pattern by itself, and it is not the primary TB-003 failure signature.

---

## Where the Rehydration Failure Likely Occurs

## Most likely failure point
### Primary gate:
- `src/hooks/useIntake.ts:315-320`
- specifically `loadIntake()` returning `null`, causing fallback to `createInitialIntake()`

### Secondary destructive symptom:
- `src/hooks/useIntake.ts:381-397`
- specifically line `392`, which overwrites `omni-intake-cross-page` from the fallback/default state

### Persistence-side root candidate:
- `src/lib/intake/persistence.ts:79-147`
- any branch returning `null` from `loadIntake()` when a stored key exists

From the current code, once `loadIntake()` returns `null`, the downstream collapse is almost guaranteed.

## What I can say confidently
- I do **not** see evidence of a true async race where defaults are written before `loadIntake()` gets a chance to read storage.
- `loadIntake()` is synchronous and happens before effects.
- I **do** see a deterministic initialization bug chain: failed full-state rehydrate -> fallback defaults -> immediate cross-page overwrite.

## What I cannot prove from static analysis alone
I cannot prove which exact `loadIntake()` null-return branch was taken in Empiricus’s failing session without the actual `omni-intake-v1` payload from that browser at failure time.

The relevant null-return branches are:
- no stored key
- partial-fragment guard (`persistence.ts:89-91`)
- unrecoverable validation/migration failure later in `loadIntake()`

Given the report that `omni-intake-v1` still existed, the most plausible explanation is:
- the key existed
- but `loadIntake()` rejected it or could not recover it
- then `useIntake()` fell back to defaults

---

## DEF-A03 Guard Assessment

## Is DEF-A03 involved?
Yes, but not as the primary failure.

### What is working
DEF-A03 protection in the autosave effect is present and appears correctly aimed at preventing default-state overwrite of `omni-intake-v1`:
- `useIntake.ts:349-369`

### What is not covered
That protection does **not** cover the cross-page sync effect:
- `useIntake.ts:381-397`

So the guard is **not misfiring** so much as **not applied to the second write path**.

### Conclusion on DEF-A03
- DEF-A03 is relevant
- it is incomplete for this scenario
- it does not appear to be the root cause of `loadIntake()` failure
- but it allows the visible collateral damage (`omni-intake-cross-page` collapse)

---

## Recommended Narrow Fix Approach
Do **not** rewrite persistence broadly.

### Recommended fix 1: Gate cross-page sync until rehydration is known-good
In `useIntake.ts`, prevent the `omni-intake-cross-page` write effect from firing on initial mount when the hook has fallen back to factory defaults before hydration certainty exists.

Examples of narrow gating strategies:
- track an `initialHydrationComplete` / `didAttemptInitialLoad` flag and skip cross-page writes until after initialization is resolved
- or skip cross-page writes when state matches the factory-default signature **and** `omni-intake-v1` already exists with meaningful content
- or make initial `updatedAt` null for untouched factory defaults and only set it on real mutation/load

### Recommended fix 2: Add diagnostics around `loadIntake()` null-return on existing key
In `persistence.ts`, add targeted logging for the exact null-return branch when `STORAGE_KEY` exists.

This is narrow and will identify whether the failing payload is:
- rejected as partial
- failing migration
- failing validation/recovery

### Recommended fix 3: Optionally harden Index auto-restore heuristic
Lower priority than the above, but worth noting:
`Index.tsx:102-109` uses a narrow “meaningful data” heuristic. If local data lives mostly outside those checked fields, cloud auto-restore may overwrite it.

This is not the main TB-003 signature, but it is a nearby initialization risk.

---

## Bottom Line
The most likely TB-003 failure chain is:
- `loadIntake()` fails to produce a valid intake on reload
- `useIntake()` falls back to `createInitialIntake()`
- immediate mount effects treat that fallback as real current state
- `omni-intake-cross-page` is overwritten with empty/default subset

So:
- **not a browser/localStorage persistence limitation**
- **not primarily a classic race condition**
- **best classified as an initialization / guard-gap logic error**
- **DEF-A03 is involved only insofar as its protection does not cover the cross-page write path**

---

## Key Line References
- `src/hooks/useIntake.ts:315-320` — initial load / fallback
- `src/hooks/useIntake.ts:343-376` — autosave + DEF-A03 overwrite guard
- `src/hooks/useIntake.ts:381-397` — cross-page sync overwrite path
- `src/hooks/useIntake.ts:399-420` — explicit session-load hydration listener
- `src/lib/intake/persistence.ts:79-132` — load pipeline / recovery / null-return risk
- `src/lib/intake/persistence.ts:243-250` — debounced autosave
- `src/lib/intake/schema.ts:848-851` — factory default timestamps
- `src/hooks/useIntakeReader.ts:104-117` — cross-page key read path
- `src/hooks/useIntakeSessions.ts:106-107` — session-id storage key
- `src/hooks/useIntakeSessions.ts:379-405` — explicit session load writes local storage + dispatches hydration event
- `src/pages/Index.tsx:96-99` — `omni-session-restored` guard
- `src/pages/Index.tsx:102-109` — local-data heuristic before auto-restore
- `src/pages/Index.tsx:132,139,142` — session restore write / session flag / reload
