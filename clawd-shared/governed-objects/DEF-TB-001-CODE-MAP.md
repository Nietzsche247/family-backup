# DEF-TB-001 Code Map — Jurisdiction / Locality Trust Break

## Scope
Bounded code map for TB-001 only: jurisdiction/locality selections being collapsed or ignored during the intake flow.

Files analyzed:
- `src/hooks/useIntake.ts`
- `src/hooks/useIntakeReader.ts`
- `src/lib/intake/persistence.ts`
- `src/lib/intake/schema.ts`
- Supporting read surfaces needed to trace the defect:
  - `src/lib/intake/selectors.ts`
  - `src/lib/intake/adapters.ts`
  - `src/components/intake/ParsedClientInfo.tsx`
  - `src/pages/Index.tsx`
  - `src/lib/geocoding/parseGeocodeResponse.ts`

Prior art applied:
- `DEF-TB-003-CHARACTERIZATION.md`
- `PARSER-TRIGGER-CONTRACT-v2.md`

---

## Executive Summary
TB-001 is a **trust break between where jurisdiction is edited/stored and where resolved location reads it from**.

### Root cause, precisely
There are **two distinct breaks**:

1. **Manual jurisdiction is stored in `clientInfoOverrides.jurisdiction`, but the canonical resolved-location path ignores it.**  
   - Manual select writes jurisdiction into overrides: `src/components/intake/ParsedClientInfo.tsx:132-140, 444-450`
   - Intake state stores that object verbatim: `src/hooks/useIntake.ts:127-145`
   - But resolved location reads jurisdiction only from `siteIntelligenceReport.location.jurisdiction`: `src/lib/intake/selectors.ts:71-72`
   - IntakeTab props also inherit jurisdiction only from `selectResolvedLocation()`: `src/lib/intake/adapters.ts:261-285`

   **Effect:** a valid user selection exists in state, but downstream/UI summary paths treat it as blank until Site Intelligence writes a report. The selection is therefore **ignored** by the canonical read chain.

2. **Whole-object override writes still exist outside the TB-002 protected parser path, so a stale async callback can overwrite a newer manual jurisdiction selection.**  
   - `SET_CLIENT_OVERRIDES` replaces the entire override object, not a field-level patch: `src/hooks/useIntake.ts:127-145`
   - TB-002 added `clientInfoOverridesRef` protection only for `parseCRM()`: `src/hooks/useIntake.ts:343-348, 615-616`
   - `retryGeocoding()` still dispatches `SET_CLIENT_OVERRIDES` using `...intake.clientInfoOverrides` captured at async start: `src/hooks/useIntake.ts:984-1032`
   - `ParsedClientInfo.reverseGeocode()` does the same with `...overrides`: `src/components/intake/ParsedClientInfo.tsx:152-174`

   **Effect:** if the user changes jurisdiction while a geocode/reverse-geocode path is in flight, the later async write can restore an older override object and effectively **collapse** the newer jurisdiction selection.

### Bottom line
- **Ignored path:** manual jurisdiction lives in overrides, but canonical resolved location does not read it.
- **Overwrite path:** stale whole-object spreads still exist on geocoding/reverse-geocoding writes.
- **TB-002 useRef pattern does not fully cover jurisdiction fields.** It protects `parseCRM()` only; it does not cover geocoding or reverse-geocoding writes.

---

## 1) Where jurisdiction/locality fields live in the schema

## Canonical schema paths

### CRM parsed address
`src/lib/intake/schema.ts:33-44, 64-72`
- `crmData.address.street`
- `crmData.address.city`
- `crmData.address.state`
- `crmData.address.zip`
- `crmData.address.full`
- `crmData.address.lat`
- `crmData.address.lng`

**Important:** `CRMData.address` does **not** define `county` or `jurisdiction`.  
That omission is explicit in `AddressSchema`: `src/lib/intake/schema.ts:33-44`.

### Manual corrections / overrides
`src/lib/intake/schema.ts:74-95`
- `clientInfoOverrides.street`
- `clientInfoOverrides.city`
- `clientInfoOverrides.state`
- `clientInfoOverrides.zip`
- `clientInfoOverrides.latitude`
- `clientInfoOverrides.longitude`
- `clientInfoOverrides.coordSource`
- `clientInfoOverrides.parcel`
- `clientInfoOverrides.lot`
- `clientInfoOverrides.legalDescription`
- `clientInfoOverrides.hoa`
- `clientInfoOverrides.jurisdiction`
- `clientInfoOverrides.notes`

**Important asymmetry:** manual overrides include `jurisdiction`, but **not `county`**.

### Site Intelligence report
`src/lib/intake/schema.ts:221-231`
- `siteIntelligenceReport.location.lat`
- `siteIntelligenceReport.location.lng`
- `siteIntelligenceReport.location.address`
- `siteIntelligenceReport.location.county`
- `siteIntelligenceReport.location.jurisdiction`

### Site Intelligence module result artifact
`src/lib/intake/schema.ts:569-577`
- `moduleResults.siteIntelligence.data.coordinates.lat`
- `moduleResults.siteIntelligence.data.coordinates.lng`
- `moduleResults.siteIntelligence.data.formattedAddress`
- `moduleResults.siteIntelligence.data.county`
- `moduleResults.siteIntelligence.data.jurisdiction`

This exists in module-result payload shape, but TB-001’s intake flow is driven primarily by `siteIntelligenceReport`, not `moduleResults.siteIntelligence`.

### Intake root storage points
`src/lib/intake/schema.ts:745-805`
- `crmData`
- `clientInfoOverrides`
- `siteIntelligenceReport`
- geocoding state fields

### Defaults
`src/lib/intake/schema.ts:854-897`
- `crmData: null`
- `clientInfoOverrides: {}`
- `siteIntelligenceReport: null`
- `isGeocoding: false`
- `geocodingError: null`

---

## 2) How jurisdiction/locality gets populated

## A. Parser path (`parseCRM`) — city/state/zip populate; jurisdiction does not become canonical
`src/hooks/useIntake.ts:555-673`

### What `parseCRM()` writes
1. Raw parsed CRM payload is stored to `crmData`: `src/hooks/useIntake.ts:605-611`
2. If there is no existing address override, it builds `newOverrides` from parser output: `src/hooks/useIntake.ts:627-663`
   - writes `street`: `632`
   - writes `city`: `633`
   - writes `state`: `634`
   - writes `zip`: `635`
   - may write `latitude`: `639-640`
   - may write `longitude`: `642-643`
   - may write parcel/lot/legalDescription/hoa: `647-657`

### What it does **not** write
`newOverrides` does **not** include `jurisdiction`.  
See omission in `src/hooks/useIntake.ts:630-658`.

### Why that matters
- If the parser/edge response includes `address.jurisdiction`, it may exist transiently in the runtime payload stored by `SET_CRM_DATA`: `src/hooks/useIntake.ts:610`
- But `AddressSchema` has no `jurisdiction` field: `src/lib/intake/schema.ts:33-44`
- And `parseCRM()` does not map jurisdiction into the canonical manual-override path (`clientInfoOverrides.jurisdiction`): `src/hooks/useIntake.ts:630-658`

**Conclusion:** parser output can supply street/city/state/zip canonically, but jurisdiction is not promoted into the stable canonical path during CRM parse.

## B. Manual entry path — jurisdiction select writes to overrides
`src/components/intake/ParsedClientInfo.tsx:103, 132-140, 437-450`

- Displayed jurisdiction resolves as: `overrides.jurisdiction ?? data.address?.jurisdiction ?? ''`: `src/components/intake/ParsedClientInfo.tsx:103`
- Any manual field edit calls `handleChange(field, value)`: `132-140`
- Jurisdiction select specifically writes `handleChange('jurisdiction', v)`: `444-450`

This is the only direct, user-authoritative write path for jurisdiction in the intake UI.

## C. Use My Location / reverse geocode path
`src/components/intake/ParsedClientInfo.tsx:151-182`

Reverse geocode writes:
- `street = formattedAddress`: `170-171`
- `jurisdiction = result.data.jurisdiction || overrides.jurisdiction`: `172`
- `coordSource = 'use-my-location'`: `173`

This path may populate jurisdiction, but only through `clientInfoOverrides.jurisdiction`, not through `siteIntelligenceReport`.

## D. Forward geocoding path (`retryGeocoding`) — lat/lng + property data only
`src/hooks/useIntake.ts:984-1060`

`parseGeocodeResponse()` extracts jurisdiction/county from the response: `src/lib/geocoding/parseGeocodeResponse.ts:208-230`

But `retryGeocoding()` only writes:
- `crmData.address.lat/lng`: `src/hooks/useIntake.ts:1008-1020`
- `clientInfoOverrides.latitude/longitude/coordSource`: `1023-1032`
- auto property fields: `1039-1060+`

It does **not** write:
- `clientInfoOverrides.jurisdiction`
- `siteIntelligenceReport.location.county`
- `siteIntelligenceReport.location.jurisdiction`

**Conclusion:** forward geocoding knows county/jurisdiction, but does not persist them into the canonical read path used by resolved location.

## E. Site Intelligence module path
- Site Intelligence report enters intake via `handleSiteIntelligenceReportReady(report)`: `src/pages/Index.tsx:405-408`
- That calls `setSiteIntelligenceReport(...)`: `src/hooks/useIntake.ts:505-506`
- Reducer stores it at `siteIntelligenceReport`: `src/hooks/useIntake.ts:202-203`

This is the **only path** that populates the fields actually read by `selectResolvedLocation()` for county/jurisdiction.

---

## 3) Every write path to jurisdiction/locality fields

## `crmData.address.*`
### Writes
- `SET_CRM_DATA` reducer replaces `crmData`: `src/hooks/useIntake.ts:124-125`
- `parseCRM()` stores parser output into `crmData`: `src/hooks/useIntake.ts:605-611`
- `retryGeocoding()` rewrites `crmData.address.lat/lng`: `src/hooks/useIntake.ts:1008-1020`
- Full intake hydration/session load can replace `crmData` wholesale through `LOAD`: `src/hooks/useIntake.ts:106-111, 317-326, 438-441`

### Relevant locality fields at this path
- `street`, `city`, `state`, `zip`, `full`, `lat`, `lng`
- **Not jurisdiction/county** in schema: `src/lib/intake/schema.ts:33-44`

## `clientInfoOverrides.*`
### Writes
- `SET_CLIENT_OVERRIDES` reducer replaces the **entire** overrides object: `src/hooks/useIntake.ts:127-145`
- Public setter dispatches that action: `src/hooks/useIntake.ts:468-470`
- Manual text/select changes in ParsedClientInfo merge and send a new object: `src/components/intake/ParsedClientInfo.tsx:132-140`
- `parseCRM()` auto-fills address/property fields into overrides: `src/hooks/useIntake.ts:627-663`
- `retryGeocoding()` writes lat/lng/coordSource into overrides using spread of current intake snapshot: `src/hooks/useIntake.ts:1023-1032`
- `reverseGeocode()` writes street/jurisdiction/coordSource using spread of current UI `overrides`: `src/components/intake/ParsedClientInfo.tsx:167-174`
- Full hydration/session load can replace overrides wholesale through `LOAD`: `src/hooks/useIntake.ts:106-111, 317-326, 438-441`

### Relevant locality fields here
- `street`, `city`, `state`, `zip`, `latitude`, `longitude`, `jurisdiction`
- **No `county` field exists here**: `src/lib/intake/schema.ts:77-95`

## `siteIntelligenceReport.location.*`
### Writes
- Reducer stores full report: `src/hooks/useIntake.ts:202-203`
- Public setter: `src/hooks/useIntake.ts:505-506`
- Index page receives report and forwards it into intake: `src/pages/Index.tsx:405-408`
- Full hydration/session load can replace report wholesale through `LOAD`: `src/hooks/useIntake.ts:106-111, 317-326, 438-441`

### Relevant locality fields here
- `lat`, `lng`, `address`, `county`, `jurisdiction`: `src/lib/intake/schema.ts:225-230`

## Cross-page storage write path
`src/hooks/useIntake.ts:400-426`

Cross-page sync writes:
- `crmData`
- `clientInfoOverrides`
- other subsets

It does **not** write `siteIntelligenceReport`. So county/jurisdiction from Site Intelligence are absent from the cross-page fragment.

## Persistence write path
- Full intake save: `src/lib/intake/persistence.ts:56-68`
- Full intake load/validation/recovery: `src/lib/intake/persistence.ts:79-132`

---

## 4) What can overwrite jurisdiction/locality after it is set

## A. Parser re-runs
`src/hooks/useIntake.ts:555-673`

### Protected portion
TB-002 protects `parseCRM()` against stale closure on overrides by reading `clientInfoOverridesRef.current`: `src/hooks/useIntake.ts:343-348, 615-616`

### What it can still do
If no street override exists, `parseCRM()` writes a fresh override object with parser-supplied street/city/state/zip and property fields: `627-663`.

### What it does not overwrite
It does not explicitly write jurisdiction.

## B. Geocoding re-runs
`src/hooks/useIntake.ts:984-1032, 1117-1182`

This is a live overwrite risk because:
- `retryGeocoding()` dispatches `SET_CLIENT_OVERRIDES` with `{ ...intake.clientInfoOverrides, latitude, longitude, coordSource }`: `1025-1032`
- `SET_CLIENT_OVERRIDES` replaces the whole object: `127-145`

If `intake.clientInfoOverrides` is stale relative to a newer manual jurisdiction selection made during the async geocode round-trip, the later dispatch restores the older object and drops the newer field values.

## C. Reverse geocode / Use My Location
`src/components/intake/ParsedClientInfo.tsx:151-182`

Same class of risk:
- callback dispatches `onOverridesChange({ ...overrides, street, jurisdiction, coordSource })`: `167-174`
- `overrides` is render-time state from the component closure, not a ref-fresh object
- reducer later replaces whole object: `src/hooks/useIntake.ts:127-145`

## D. Site Intelligence report arrival
`src/pages/Index.tsx:405-408`, `src/hooks/useIntake.ts:202-203`

Once Site Intelligence writes a report, `selectResolvedLocation()` will prefer:
- `siteIntelligenceReport.location.county`
- `siteIntelligenceReport.location.jurisdiction`

because those are the only sources it reads for county/jurisdiction: `src/lib/intake/selectors.ts:71-72`

This does not overwrite `clientInfoOverrides.jurisdiction` in storage, but it does overwrite the **resolved read result** seen by downstream consumers.

## E. Session restore / full LOAD
- Initial load from storage: `src/hooks/useIntake.ts:317-326`
- Session event rehydrate: `src/hooks/useIntake.ts:428-441`
- `LOAD` reducer replaces the full intake object: `src/hooks/useIntake.ts:106-111`

This can replace all locality data wholesale, but TB-001 is not primarily a TB-003 reload issue.

---

## 5) Specific trust break: where valid jurisdiction gets collapsed or ignored

## Trust Break #1 — Manual jurisdiction is ignored by canonical resolved location

### Write side
- User selects jurisdiction in intake UI: `src/components/intake/ParsedClientInfo.tsx:444-450`
- That writes `clientInfoOverrides.jurisdiction` through `handleChange()`: `132-140`
- Reducer stores the whole override object: `src/hooks/useIntake.ts:127-145`

### Read side
- `selectResolvedLocation()` reads city/state/zip from overrides, **but not jurisdiction**: `src/lib/intake/selectors.ts:62-72`
- Specifically:
  - city/state/zip use overrides first: `66-68`
  - county/jurisdiction come only from `siteReport.location`: `71-72`

### Impact
A valid manual jurisdiction exists in state, but canonical downstream readers resolve jurisdiction as `null` until Site Intelligence fills `siteIntelligenceReport.location.jurisdiction`.

**This is the clearest “ignored” trust break.**

## Trust Break #2 — Parser/geocode paths know about jurisdiction but do not promote it into the canonical read chain

### Evidence
- UI expects parser-provided jurisdiction via `data.address?.jurisdiction`: `src/components/intake/ParsedClientInfo.tsx:103, 438`
- `parseGeocodeResponse()` extracts `jurisdiction`: `src/lib/geocoding/parseGeocodeResponse.ts:208-230`
- But `AddressSchema` has no `jurisdiction`: `src/lib/intake/schema.ts:33-44`
- `parseCRM()` does not map jurisdiction into overrides: `src/hooks/useIntake.ts:630-658`
- `retryGeocoding()` does not write jurisdiction anywhere canonical: `src/hooks/useIntake.ts:1007-1033`

### Impact
Jurisdiction may appear transiently in raw/edge-function data, but it is not consistently promoted into the canonical intake path that resolved readers use.

## Trust Break #3 — Stale whole-object spreads can collapse a newer manual selection

### Evidence
- Override reducer is whole-object replacement: `src/hooks/useIntake.ts:127-145`
- Geocode success path spreads captured overrides and writes a replacement object: `src/hooks/useIntake.ts:1025-1032`
- Reverse geocode path does same: `src/components/intake/ParsedClientInfo.tsx:167-174`
- TB-002 ref freshness exists only around `parseCRM()`: `src/hooks/useIntake.ts:343-348, 615-616`

### Impact
A user can make a valid jurisdiction selection, and a later async geocode/reverse-geocode completion can restore an earlier snapshot of the override object, effectively collapsing that selection.

---

## 6) Authoritative source chain — who SHOULD own jurisdiction/locality at each stage

Applying `PARSER-TRIGGER-CONTRACT-v2.md` Rule 3:
- manual correction is authoritative
- parser/geocoder outputs are candidate/enrichment data until mapped into canonical fields

## City / state / zip
### Current code reality
- Parser candidate enters `crmData.address.*`: `src/hooks/useIntake.ts:605-611`
- If no manual address override exists, parser autofill copies street/city/state/zip into overrides: `627-635`
- Resolved location reads overrides first, then CRM: `src/lib/intake/selectors.ts:62-68`

### Proper authority chain
1. Manual override in `clientInfoOverrides.*`
2. Parser-filled CRM/auto-fill when no manual override exists

This chain is mostly implemented correctly.

## County
### Current code reality
- County exists only on `siteIntelligenceReport.location.county` in the canonical read path: `src/lib/intake/selectors.ts:71`
- There is no manual county override field in schema: `src/lib/intake/schema.ts:77-95`

### Proper authority chain
1. Site Intelligence / geographic enrichment
2. No manual county authority path currently exists in intake schema

## Jurisdiction
### Current code reality
- Manual selection lives in `clientInfoOverrides.jurisdiction`: `src/lib/intake/schema.ts:94`, `src/components/intake/ParsedClientInfo.tsx:444-450`
- Site Intelligence result lives in `siteIntelligenceReport.location.jurisdiction`: `src/lib/intake/schema.ts:230`
- Resolved location ignores manual override and reads Site Intelligence only: `src/lib/intake/selectors.ts:71-72`

### Proper authority chain
Per Rule 3, it **should** be:
1. Manual `clientInfoOverrides.jurisdiction` (authoritative)
2. Site Intelligence / geocoder-enriched jurisdiction (candidate/default)
3. Parser/raw CRM mentions only as candidate input

### Current implementation mismatch
Current selector implements effectively:
1. `siteIntelligenceReport.location.jurisdiction`
2. else `null`

It does **not** honor manual override authority.

---

## 7) Does the DEF-TB-002 useRef protection pattern cover jurisdiction fields?

## Answer: only partially, and not enough for TB-001

### Covered
`parseCRM()` is protected against stale override reads by:
- `clientInfoOverridesRef`: `src/hooks/useIntake.ts:343-348`
- reading that ref inside parse flow: `src/hooks/useIntake.ts:615-616`

This means CRM parser autofill is less likely to overwrite a newer manual override due to stale closure.

### Not covered
The same protection is **not** applied to:
- `retryGeocoding()`: `src/hooks/useIntake.ts:984-1032`
- `ParsedClientInfo.reverseGeocode()`: `src/components/intake/ParsedClientInfo.tsx:151-182`
- generic manual `onOverridesChange({ ...overrides, ...patch })` component-side merges: `src/components/intake/ParsedClientInfo.tsx:132-140`

### Why this matters for jurisdiction specifically
Jurisdiction is stored in the same whole-object override bag as address fields. Since `SET_CLIENT_OVERRIDES` replaces the entire object (`src/hooks/useIntake.ts:127-145`), any stale-spread write path can remove a newer jurisdiction selection.

**Conclusion:** TB-002’s stale-closure fix does **not** fully cover jurisdiction/locality writes.

---

## 8) useIntakeReader / cross-page behavior (bounded note)

`useIntakeReader` reads from `omni-intake-cross-page` first, then falls back to full intake: `src/hooks/useIntakeReader.ts:102-117`.

Its CRM parser only reconstructs:
- `street`, `city`, `state`, `zip`: `src/hooks/useIntakeReader.ts:247-265`
- no county/jurisdiction fields are returned in `IntakeCRMData`

Cross-page sync also writes only:
- `crmData`
- `clientInfoOverrides`
- not `siteIntelligenceReport`: `src/hooks/useIntake.ts:412-420`

So even aside from the selector issue, cross-page readers do not have a first-class jurisdiction/county pipeline.

This is not a reload/persistence diagnosis; it is a field-mapping fact relevant to authority/read-path analysis.

---

## 9) Acceptance-criteria conclusions

### Root cause identified with file:line precision
Yes.

Primary read-path trust break:
- `src/lib/intake/selectors.ts:71-72`
- manual jurisdiction is stored elsewhere (`clientInfoOverrides.jurisdiction`) and ignored

Primary overwrite-risk trust break:
- whole-object replacement reducer: `src/hooks/useIntake.ts:127-145`
- stale async geocode spread: `src/hooks/useIntake.ts:1025-1032`
- stale async reverse-geocode spread: `src/components/intake/ParsedClientInfo.tsx:167-174`
- TB-002 protection exists only in parser path: `src/hooks/useIntake.ts:343-348, 615-616`

### Every write path documented
Yes — parser, manual entry, reverse geocode, forward geocode, site-intelligence report, persistence/load, session load, cross-page subset write.

### Clear distinction between parser-populated vs user-corrected values
Yes.
- Parser/geocoder outputs are candidate/enrichment data
- Manual `clientInfoOverrides.jurisdiction` should be authoritative per governing contract Rule 3

### Identifies whether DEF-TB-002 useRef pattern covers jurisdiction fields
Yes.
- It covers `parseCRM()` only
- It does not cover `retryGeocoding()` or `reverseGeocode()`

---

## Final classification
TB-001 is **not one bug but one trust-break family** centered on jurisdiction/locality ownership:

1. **Ignored authority** — manual jurisdiction is stored but not read by canonical resolved-location logic.
2. **Incomplete mapping** — parser/geocoder knowledge of jurisdiction is not consistently promoted into canonical intake fields.
3. **Unprotected overwrite path** — stale whole-object override writes still exist outside the TB-002 parser fix.

That is the bounded code map for the TB-001 fix brief.