# DEF-TB-001 Phase 1 Code Review v2 — ACTUAL SOURCE

**Date:** 2026-03-23  
**Reviewer:** Daedalus  
**Scope:** Review Plato's actual current Phase 1 source files from file server mirror (`dbe9867` core wiring fix + `5b96e7f` split-brain reader fixes claim) against approved brief and prior code map.

---

## Source reviewed
Downloaded from:
- `https://hub.stigmergy.space/files/source-mirrors/tb-001-review/`
- Auth provided by requester

Files reviewed from actual source mirror:
1. `selectors.ts`
2. `useIntake.ts`
3. `ParsedClientInfo.tsx`
4. `Index.tsx`
5. `PermittingTab.tsx`
6. `FullReportsTab.tsx`
7. `HomeownerResultsTab.tsx`
8. `UnifiedPDFExport.tsx`

Additional requested verification:
- `artifacts.ts` was **not present in the uploaded mirror**. Direct actual-source verification of that file was therefore **not possible** in this review.

---

## Executive summary

## Overall recommendation: **NO-GO**

The core 3-file wiring fixes are present and correctly implemented:
- selector precedence fixed
- geocode stale-closure fix present
- reverse-geocode stale-closure fix present

However, the split-brain cleanup is **not complete** in the actual mirrored files reviewed. The downstream report/export surfaces still retain direct `siteIntelligenceReport.location.{county,jurisdiction}` fallback reads instead of using the canonical resolved values exclusively. That violates the approved brief's **"no split-brain reads"** requirement and fails contract-level canonical-source compliance.

**Result:** not ready to deploy Phase 1 as briefed.

---

## Verdict matrix

| # | Review criterion | Verdict | Notes |
|---|---|---|---|
| 1 | Trust Break #1 FIXED? `selectResolvedLocation()` reads overrides jurisdiction first | **PASS** | `selectors.ts:72` now resolves `overrides?.jurisdiction` before SI |
| 2 | Trust Break #2 FIXED? `retryGeocoding()` uses ref-fresh overrides | **PASS** | `useIntake.ts:1030` now spreads `clientInfoOverridesRef.current` |
| 3 | Trust Break #3 FIXED? `reverseGeocode()` uses ref pattern | **PASS** | `ParsedClientInfo.tsx:91-92, 175-181` adds `overridesRef` + fresh read |
| 4 | NO SPLIT-BRAIN? All 5 previously-identified direct SI readers now use canonical source | **FAIL** | Mirrored downstream files still contain direct SI fallback reads; `artifacts.ts` not provided for direct verification |
| 5 | TB-002 non-regression: `parseCRM` ref pattern untouched | **PASS** | `useIntake.ts:346-348, 616` intact |
| 6 | TB-003 non-regression: persistence/schema/autosave untouched | **PASS** | No mirrored changes to persistence/schema/autosave surfaces; `useIntake.ts` autosave/load paths appear unchanged relative to scope |
| 7 | `coordSource` non-regression: no new lat/lng writes | **PASS** | No new lat/lng write paths introduced; existing writes preserved |
| 8 | Contract compliance: Rule 3, Rule 2, Rule 5 | **FAIL** | Rule 3 fixed in selector, but Rule 2 / canonical-source requirement still violated by split-brain fallbacks |

---

## Detailed findings

## 1) Trust Break #1 — selector precedence
**Verdict: PASS**

`selectors.ts` now implements the required precedence:

```ts
county: siteReport?.location?.county ?? null,
jurisdiction: overrides?.jurisdiction || siteReport?.location?.jurisdiction ?? null,
```

**Evidence:** `selectors.ts:71-72`

This satisfies the approved Phase 1 authority chain for jurisdiction:
1. manual override (`clientInfoOverrides.jurisdiction`)
2. Site Intelligence jurisdiction
3. `null`

---

## 2) Trust Break #2 — `retryGeocoding()` stale-closure protection
**Verdict: PASS**

The geocode success path now reads fresh overrides from the ref instead of the stale closure snapshot:

```ts
payload: {
  ...clientInfoOverridesRef.current,
  latitude: String(parsed.lat),
  longitude: String(parsed.lng),
  coordSource: 'forward-geocode' as const,
},
```

**Evidence:**
- ref maintained: `useIntake.ts:346-348`
- geocode write uses ref: `useIntake.ts:1026-1033`

This directly fixes the previously identified live-session overwrite risk.

---

## 3) Trust Break #3 — `reverseGeocode()` fresh-read pattern
**Verdict: PASS**

`ParsedClientInfo.tsx` now mirrors the same freshness pattern:

```ts
const overridesRef = useRef(overrides);
overridesRef.current = overrides;
```

and later:

```ts
const freshOverrides = overridesRef.current;
onOverridesChange({
  ...freshOverrides,
  street: formattedAddress,
  jurisdiction: result.data.jurisdiction || freshOverrides.jurisdiction,
  coordSource: 'use-my-location',
});
```

**Evidence:**
- ref added: `ParsedClientInfo.tsx:91-92`
- async callback uses fresh ref value: `ParsedClientInfo.tsx:175-181`

This fixes the stale render-closure overwrite class for reverse geocoding.

---

## 4) Split-brain reader cleanup
**Verdict: FAIL**

Aaron's requirement was explicit: **no split-brain reads**. Every jurisdiction consumer must trust the same canonical source after this fix.

### What is correct
`Index.tsx` now threads canonical resolved values down to the tabs:
- `PermittingTab`: `Index.tsx:549-554`
- `FullReportsTab`: `Index.tsx:559-567`
- `HomeownerResultsTab`: `Index.tsx:572-579`

So the prop plumbing exists.

### What is still wrong
The reviewed downstream files still retain direct SI fallback reads instead of trusting canonical resolved props exclusively.

#### `PermittingTab.tsx`
Still reads:
```tsx
<InfoRow label="County" value={resolvedCounty || siteIntelligenceReport?.location?.county || 'Pima'} />
<InfoRow label="Jurisdiction" value={resolvedJurisdiction || siteIntelligenceReport?.location?.jurisdiction || 'Unincorporated'} />
```
**Evidence:** `PermittingTab.tsx:159-160`

#### `FullReportsTab.tsx`
Still reads:
```tsx
<InfoRow label="County" value={resolvedCounty || siteIntelligenceReport.location?.county || 'Unknown'} />
<InfoRow label="Jurisdiction" value={resolvedJurisdiction || siteIntelligenceReport.location?.jurisdiction || 'Unknown'} />
```
**Evidence:** `FullReportsTab.tsx:887-888`

#### `HomeownerResultsTab.tsx`
Still reads direct SI fallback into story/output data:
```ts
jurisdiction: resolvedJurisdiction || siteIntelligenceReport.location?.jurisdiction,
```
**Evidence:** `HomeownerResultsTab.tsx:397`

Still reads direct SI fallback in UI:
```tsx
<span className="text-slate-700">{resolvedJurisdiction || siteIntelligenceReport?.location?.jurisdiction || 'Unincorporated'}</span>
```
**Evidence:** `HomeownerResultsTab.tsx:705-709`

#### `UnifiedPDFExport.tsx`
Still reads direct SI fallback multiple times:
- `UnifiedPDFExport.tsx:236-237`
- `UnifiedPDFExport.tsx:274-278`
- `UnifiedPDFExport.tsx:462-463`

Examples:
```tsx
<InfoRow label="County" value={resolvedCounty || siteIntelligenceReport?.location?.county || 'Pima'} />
<InfoRow label="Jurisdiction" value={resolvedJurisdiction || siteIntelligenceReport?.location?.jurisdiction || 'Unincorporated'} />
```

### `artifacts.ts`
Plato said this file was already clean, but it was **not included in the actual source mirror**. I therefore could **not** directly verify that claim against the actual-current file.

### Conclusion on split-brain
Even with the new canonical props threaded through `Index.tsx`, these files still contain alternate raw-SI read paths. That is a split-brain pattern by definition and does **not** satisfy the brief's requirement:
- displayed state
- downstream trust
- outputs/exports

must all resolve through the same canonical source.

---

## 5) TB-002 non-regression
**Verdict: PASS**

The existing `parseCRM()` freshness protection remains intact:
- `clientInfoOverridesRef` still defined and maintained: `useIntake.ts:346-348`
- `parseCRM()` still reads `const currentOverrides = clientInfoOverridesRef.current;`: `useIntake.ts:616`

This appears additive, not regressive.

---

## 6) TB-003 non-regression
**Verdict: PASS**

No persistence/schema/autosave files were part of the uploaded actual-source mirror, and within the mirrored `useIntake.ts` there is no evidence of Phase 1 spilling into those surfaces.

Reviewed intact/non-target areas in `useIntake.ts`:
- `loadIntake()` load path still present: `useIntake.ts:318, 438`
- debounced/flush save paths still present: `useIntake.ts:381, 1401`
- the Phase 1 modifications are narrowly localized to selector/geocode freshness behavior

No schema or autosave contract drift was observed.

---

## 7) `coordSource` / lat-lng non-regression
**Verdict: PASS**

No new coordinate write classes were introduced.

Observed behavior remains scope-narrow:
- geocode path still writes `latitude`, `longitude`, `coordSource: 'forward-geocode'`: `useIntake.ts:1031-1033`
- reverse geocode path still writes `coordSource: 'use-my-location'`: `ParsedClientInfo.tsx:181`
- manual coordinate handling remains in the existing component path

The Phase 1 changes only altered freshness of the source object being merged, not the coordinate contract itself.

---

## 8) Contract compliance
**Verdict: FAIL**

### Rule 3 — manual correction authoritative
**PASS at selector level**
- `selectors.ts:72` now honors manual jurisdiction before SI.

### Rule 2 — candidate/inferred data must not bypass canonical authority
**FAIL**
- downstream report/export surfaces still directly reference `siteIntelligenceReport.location.{county,jurisdiction}` as fallback sources instead of trusting the canonical resolved props only.
- that means candidate/enrichment data can still be consumed outside the single canonical read chain.

### Rule 5 — no improper trigger-law expansion
**PASS / no new violation observed**
- no new trigger behavior introduced in reviewed files.

### Overall contract result
Because Rule 2 / canonical-source consistency is still not clean, contract compliance for Phase 1 is **not achieved**.

---

## Final recommendation

## **NO-GO**

### Why
The 3 core trust-break fixes are real and correctly implemented, but the split-brain cleanup is incomplete in the actual mirrored code reviewed.

### Required before deploy
1. Remove the remaining raw `siteIntelligenceReport.location.county/jurisdiction` fallback reads from:
   - `PermittingTab.tsx`
   - `FullReportsTab.tsx`
   - `HomeownerResultsTab.tsx`
   - `UnifiedPDFExport.tsx`
2. Provide actual-current `artifacts.ts` for direct verification, or include it in the next mirror.
3. Ensure every jurisdiction/count y consumer uses only canonical resolved values.

### Deployment status
**Not ready for Empiricus validation.**

Empiricus validation should wait until the split-brain fallbacks are removed and `artifacts.ts` is source-truth verified.

---

## Bottom line for Aaron
- Core fix set: **real**
- Brief compliance: **not yet complete**
- Recommended action: **one more pass for strict canonical-source cleanup, then re-review**
