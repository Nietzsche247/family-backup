# DEF-TB-001 Phase 1 Code Review — Commit dbe9867

**Date:** 2026-03-23  
**Reviewer:** Daedalus  
**Scope:** Verify Phase 1 TB-001 wiring fix against approved brief and code map  
**Requested target:** commit `dbe9867`

---

## Source-truth status

**FAIL — target commit was not accessible from available sources during review.**

I checked:
- `C:\Users\aaron\clawd-shared\omnipools-repo\` → stale snapshot, current HEAD `a059078`, not `dbe9867`
- `C:\Users\aaron\clawd-shared\source-mirrors\omnipools-src.zip` / file server mirror paths → also stale (March 20-era contents)
- file server paths for the three changed files under `https://hub.stigmergy.space/files/omnipools-repo/...` → still showed pre-fix code

So I could **not directly verify commit `dbe9867`**. Per instruction, this review therefore flags what I actually reviewed: the latest accessible snapshot, which still contains the original TB-001 defects.

---

## Verdict summary

| Check | Verdict | Reason |
|---|---|---|
| Trust Break #1 — selector precedence | **FAIL / UNVERIFIED ON TARGET** | Latest accessible snapshot still resolves `jurisdiction` from `siteIntelligenceReport.location.jurisdiction` only; manual override is ignored. |
| Trust Break #2 — `retryGeocoding()` stale capture | **FAIL / UNVERIFIED ON TARGET** | Latest accessible snapshot still spreads `...intake.clientInfoOverrides`, not a ref-fresh object. |
| Trust Break #3 — `reverseGeocode()` ref pattern | **FAIL / UNVERIFIED ON TARGET** | Latest accessible snapshot still spreads closure `...overrides`; no `overridesRef` present. |
| No split-brain jurisdiction reads | **FAIL** | Multiple report/export surfaces still read `siteIntelligenceReport.location.jurisdiction` directly instead of canonical selector output. |
| TB-002 non-regression | **PASS on accessible snapshot** | `parseCRM()` ref pattern remains present and untouched. |
| TB-003 non-regression | **PASS on accessible snapshot** | Persistence/schema/autosave/session-restore paths reviewed; no jurisdiction-specific changes visible there. |
| coordSource non-regression | **PASS on accessible snapshot** | No new lat/lng or `coordSource` write paths observed beyond existing ones. |
| Contract compliance | **FAIL on accessible snapshot** | Rule 3 violated by selector split; Rule 2 weakened by direct SI reads on outputs; Rule 5 not newly violated, but canonical-source law is still not cleanly enforced. |

---

## Detailed review

## 1) Trust Break #1 — `selectResolvedLocation()` precedence

**Target requirement:** manual `clientInfoOverrides.jurisdiction` > SI `siteIntelligenceReport.location.jurisdiction` > `null`

**What I found in accessible source:**
- `src/lib/intake/selectors.ts:72`
- current code:

```ts
jurisdiction: siteReport?.location?.jurisdiction ?? null,
```

**Assessment:**
- Manual jurisdiction is **still not read** by the canonical resolver.
- Precedence is still effectively `SI > null`.
- This means Rule 3 (manual authoritative) is still broken in the reviewed snapshot.

**Verdict:** **FAIL / UNVERIFIED ON TARGET**

---

## 2) Trust Break #2 — `retryGeocoding()` stale whole-object spread

**Target requirement:** use `clientInfoOverridesRef.current`, not closure-captured `intake.clientInfoOverrides`

**What I found in accessible source:**
- `src/hooks/useIntake.ts` geocode success path still dispatches:

```ts
payload: {
  ...intake.clientInfoOverrides,
  latitude: String(parsed.lat),
  longitude: String(parsed.lng),
  coordSource: 'forward-geocode' as const,
},
```

- reducer still performs whole-object replacement for `SET_CLIENT_OVERRIDES`

**Assessment:**
- A manual jurisdiction change made while geocoding is in flight can still be overwritten by the older object snapshot.
- TB-002 ref protection is present for `parseCRM()` only, not this path.

**Verdict:** **FAIL / UNVERIFIED ON TARGET**

---

## 3) Trust Break #3 — `reverseGeocode()` fresh-read pattern

**Target requirement:** use ref/callback freshness pattern rather than closure `overrides`

**What I found in accessible source:**
- `src/components/intake/ParsedClientInfo.tsx` still has:

```ts
onOverridesChange({
  ...overrides,
  street: formattedAddress,
  jurisdiction: result.data.jurisdiction || overrides.jurisdiction,
  coordSource: 'use-my-location',
});
```

- no `overridesRef` is present in the component

**Assessment:**
- This remains the exact stale-closure overwrite class identified in the code map.
- If user changes jurisdiction before reverse-geocode settles, the later write can restore stale fields.

**Verdict:** **FAIL / UNVERIFIED ON TARGET**

---

## 4) Split-brain jurisdiction read check

Aaron’s emphasis was correct: the problem is not only the 3 touched files.

### Canonical-good consumers (through selector)
These are wired correctly in the accessible snapshot **if** `selectResolvedLocation()` were fixed:
- `src/lib/intake/adapters.ts` via `const location = selectResolvedLocation(intake)`
- `src/lib/artifacts/generatePermitPacket.ts`
- `src/lib/intake/unifiedExport.ts`
- downstream selector-based surfaces in `src/lib/intake/selectors.ts`

### Remaining direct SI jurisdiction readers (split-brain)
These still bypass the canonical selector and read raw SI directly in the accessible snapshot:
- `src/components/reports/UnifiedPDFExport.tsx:231, 272, 457`
- `src/components/tabs/FullReportsTab.tsx:882`
- `src/components/tabs/PermittingTab.tsx:154`
- `src/components/tabs/HomeownerResultsTab.tsx:391, 700-701`
- `src/lib/intake/artifacts.ts` builds story/export data from `siteIntelligenceReport.location?.jurisdiction`

### Interpretation
Even if Plato implemented the three requested Phase 1 edits exactly as described, **these direct SI read surfaces would still remain split-brain unless they were also updated**. That matters because the fix brief explicitly says:
- no split-brain reads
- displayed state, downstream trust, and outputs/exports must use the same canonical source

**Verdict:** **FAIL**

---

## 5) TB-002 non-regression check

**Reviewed area:** `src/hooks/useIntake.ts`

What remains intact in accessible snapshot:
- `clientInfoOverridesRef` is still initialized
- `clientInfoOverridesRef.current = intake.clientInfoOverrides` still keeps it in sync
- `parseCRM()` still reads from the ref before auto-fill merge

**Verdict:** **PASS on accessible snapshot**

---

## 6) TB-003 non-regression check

**Reviewed areas:**
- `src/lib/intake/persistence.ts`
- `src/lib/intake/schema.ts`
- autosave/cross-page/session restore sections in `src/hooks/useIntake.ts`
- `src/hooks/useIntakeReader.ts`

**Findings:**
- No Phase 1-style jurisdiction changes are visible in persistence/schema paths in accessible source.
- Existing TB-003 protections remain present.
- `useIntakeReader.ts` still does **not** add a first-class jurisdiction pipeline, but that was explicitly out of Phase 1 scope in the brief.

**Verdict:** **PASS on accessible snapshot**

---

## 7) coordSource / lat-lng non-regression

**Findings:**
- Existing write paths remain:
  - forward geocode → `coordSource: 'forward-geocode'`
  - manual lat/lng entry → `coordSource: 'manual'`
  - reverse geocode / use-my-location → `coordSource: 'use-my-location'`
- I did not observe any additional lat/lng or `coordSource` write paths in the accessible snapshot.

**Verdict:** **PASS on accessible snapshot**

---

## 8) Contract compliance

### Rule 3 — manual authoritative
**Fails in accessible snapshot** because canonical resolver still ignores `clientInfoOverrides.jurisdiction`.

### Rule 2 — candidate vs canonical
**Still weak / partially violated** because multiple export/report surfaces bypass canonical resolved location and read SI raw fields directly.

### Rule 5 — no vibe triggers
I did **not** identify a new trigger-law regression in the reviewed snapshot. The core issue remains source-of-truth inconsistency, not a new trigger path.

**Verdict:** **FAIL on accessible snapshot**

---

## Overall recommendation

## **FAIL / NO-GO FOR DEPLOYMENT UNTIL SOURCE TRUTH IS VERIFIED**

Reasoning:
1. I could not access commit `dbe9867`, so I cannot honestly certify the three stated fixes as implemented.
2. The latest accessible source still contains all three original TB-001 defects.
3. Independent of the three-file patch, the accessible codebase still has **remaining split-brain jurisdiction read paths** in report/export surfaces, which violates the approved brief’s canonical-source requirement.

---

## What Plato / Aaron should know immediately

If commit `dbe9867` truly contains only the three announced edits, then **Phase 1 is still not fully compliant with the brief** unless the direct SI readers were also corrected or intentionally deferred by Aaron.

### Minimum blockers before I can issue PASS
- Access to the actual target commit `dbe9867` or exact file contents for:
  - `src/lib/intake/selectors.ts`
  - `src/hooks/useIntake.ts`
  - `src/components/intake/ParsedClientInfo.tsx`
- Clarification or follow-up fix for remaining split-brain readers:
  - `src/components/reports/UnifiedPDFExport.tsx`
  - `src/components/tabs/FullReportsTab.tsx`
  - `src/components/tabs/PermittingTab.tsx`
  - `src/components/tabs/HomeownerResultsTab.tsx`
  - `src/lib/intake/artifacts.ts`

If Plato provides the exact `dbe9867` file contents, I can reissue a fast definitive PASS/FAIL against the real patch.
