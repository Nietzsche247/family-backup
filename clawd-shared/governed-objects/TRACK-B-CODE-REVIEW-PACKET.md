# Track B Code Review Packet — Intake Trigger Chain + Jurisdiction

Date: 2026-03-20  
Scope: Read-only code map for CRM paste, canonical address, manual correction, geocode, and jurisdiction/site-intelligence cascade in `C:\Users\aaron\clawd-shared\omnipools-src`

---

## Executive Summary

The active Intake flow is centered on the canonical Intake hook, not the older `useIntakeIngestion` / `useSiteIntelligence` hooks.

### Most likely origin of DEF-TB-001
**DEF-TB-001: Jurisdiction + locality trust break — jurisdiction never auto-resolves / Site Intelligence locality conflicts with canonical address**

Primary origin points:
1. **Geocode results are not promoted to authoritative jurisdiction in the canonical Intake flow**  
   - `src/hooks/useIntake.ts:968-994` updates only `lat/lng` into `crmData.address` and `clientInfoOverrides`, but does **not** persist `parsed.jurisdiction`, `parsed.county`, or `parsed.formattedAddress` from `geocode-address`.
2. **Resolved jurisdiction is sourced only from Site Intelligence report, not from CRM or geocoder**  
   - `src/lib/intake/selectors.ts:72` sets `jurisdiction: siteReport?.location?.jurisdiction ?? null`.
3. **Site Intelligence derives jurisdiction from coordinates via its own detector, not from canonical address text**  
   - `supabase/functions/site-intelligence/index.ts:186-193` computes `county` and `jurisdiction` from `lat/lng` using `detectCounty()` / `detectJurisdiction()`.
4. **Address schema does not canonically include jurisdiction/county/full geocode metadata**  
   - `src/lib/intake/schema.ts:33-40` `AddressSchema` only includes `street/city/state/zip/full/lat/lng`.

Net effect: geocoder may resolve one locality while Site Intelligence later computes another from coordinates; only the Site Intelligence value is treated as resolved jurisdiction.

### Most likely origin of DEF-TB-002
**DEF-TB-002: Manual correction silently overwritten on CRM re-parse — downstream fields revert with no warning**

Primary origin point:
1. **`parseCRM` captures stale Intake state because it is memoized with an empty dependency list**  
   - `src/hooks/useIntake.ts:518` starts `const parseCRM = useCallback(async (text: string) => { ...`  
   - `src/hooks/useIntake.ts:647` closes with `}, []);`
2. Inside that stale closure, re-parse decides whether overrides exist using captured initial state:  
   - `src/hooks/useIntake.ts:578` `const hasExistingOverride = intake.clientInfoOverrides?.street;`
3. It then rebuilds and dispatches override state from the same captured object:  
   - `src/hooks/useIntake.ts:591-623` constructs `newOverrides` from `...intake.clientInfoOverrides` and writes them with `SET_CLIENT_OVERRIDES`.
4. CRM re-parse is automatically re-triggered from Intake page changes and manually via “Re-parse”:  
   - `src/pages/Index.tsx:221-222` debounced parse on `intake.siteInfoText` changes  
   - `src/pages/Index.tsx:514-515` manual re-parse calls `parseCRM(intake.siteInfoText)`.

Net effect: manual edits can exist in current React state, but `parseCRM` may still operate against an older snapshot and re-apply parser-derived values, silently replacing manual corrections.

---

## 1) CRM Paste Path

### Entry point
- **Page:** `src/pages/Index.tsx`
- **Component:** `src/components/tabs/IntakeTab.tsx`
- **Input widget:** `SiteInfoIntake` inside Intake tab
- **Canonical state mutation:** `setSiteInfoText` from `useIntake()`

### Trigger chain
1. User pastes CRM/site info into Intake.
2. `Index.tsx` watches `intake.siteInfoText` and debounces CRM parsing.  
   - `src/pages/Index.tsx:221-222`
3. Debounced callback calls `parseCRM(text)` from the canonical hook.  
   - `src/pages/Index.tsx:196-208`
4. `useIntake.ts` invokes Supabase edge function `parse-crm-notes`.  
   - `src/hooks/useIntake.ts:518-647`
5. Parsed result is stored in Intake as `crmData`, status set to success.  
   - `SET_CRM_DATA`, `SET_CRM_STATUS`
6. If parsed address exists and no existing street override is detected, parser auto-fills `clientInfoOverrides` with address/property fields.  
   - `src/hooks/useIntake.ts:578-625`

### Parser involved
- **Edge function:** `supabase/functions/parse-crm-notes/index.ts`
- It extracts project address, jurisdiction, coordinates, parcel, lot, etc.  
  - See matches around `projectAddress`, `jurisdiction`, `latitude`, `longitude` in that function.

### Data landing zone
- `intake.siteInfoText` — raw paste
- `intake.crmData` — parsed CRM payload
- `intake.clientInfoOverrides` — auto-filled editable fields (street/city/state/zip, parcel, lot, etc.)

### Likely failure points
- **Stale closure overwrite risk** in `parseCRM` (`useCallback(..., [])`) — likely source of DEF-TB-002.
- **Auto-fill writes into override layer**, not a separate parser layer, so parser output and manual correction share the same mutable object path.
- **Schema mismatch risk:** CRM parser may emit richer address fields than canonical `AddressSchema` formally owns.

---

## 2) Canonical Project Address Path

### Canonical model as implemented
The effective address shown in Intake and used downstream is **not just `crmData.address.full`**. It is a resolved value composed from:
- CRM parsed address (`crmData.address.*`)
- manual corrections (`clientInfoOverrides.*`)
- sometimes coordinates from overrides
- jurisdiction from `siteIntelligenceReport.location`

### Resolver
- **Primary selector:** `src/lib/intake/selectors.ts:53-75` `selectResolvedLocation(intake)`

### Resolution rules
- Address text:
  - If `clientInfoOverrides.street` exists, build address string from overrides.
  - Else use `crmData.address.full`.
- Coordinates:
  - Prefer `clientInfoOverrides.latitude/longitude`, else `crmData.address.lat/lng`.
- County/jurisdiction:
  - **Only from** `siteIntelligenceReport.location.county/jurisdiction`.  
  - `src/lib/intake/selectors.ts:71-72`

### Persistence
- Canonical Intake store is persisted to localStorage key `omni-intake-v1`.  
  - `src/lib/intake/persistence.ts`
- `useIntake` auto-saves state changes via persistence module.  
  - documented in `docs/INTAKE_SOURCE_OF_TRUTH.md`

### Important trust split
There is no single address object that owns:
- text address,
- canonical formatted geocode address,
- county,
- jurisdiction,
- geocode provenance.

Instead those are split across:
- `crmData.address`
- `clientInfoOverrides`
- `siteIntelligenceReport.location`
- auto property fields (`autoSquareFootage`, `autoYearBuilt`, `autoLotSizeAcres`)

### Likely failure points
- **County/jurisdiction not tied to same source as address text.** Text address may come from overrides/CRM, while jurisdiction comes from site-intelligence only.
- **Formatted address trust break in legacy adapter:**  
  - `src/lib/intake/adapters.ts:67` uses `full: address.full || null` even when street/city/state/zip are overridden.
- **Reader path rebuilds full address from overrides while legacy adapter preserves CRM `address.full`, creating parallel representations.**

---

## 3) Manual Correction Path

### UI component
- **Component:** `src/components/intake/ParsedClientInfo.tsx`
- User edits client/address/property fields here.

### Override write path
- On any field change, component calls `onOverridesChange({ ...overrides, ...patch })`.  
  - `src/components/intake/ParsedClientInfo.tsx:132-139`
- Intake page passes that callback to `setClientInfoOverrides`.  
  - `src/pages/Index.tsx:456`
- Hook dispatches `SET_CLIENT_OVERRIDES`.  
  - `src/hooks/useIntake.ts:431-433`
- Reducer stores entire override object into `intake.clientInfoOverrides`.  
  - `src/hooks/useIntake.ts:127-146`

### What manual correction actually overrides
- Client name/phone/email
- Street/city/state/zip
- Parcel / lot / legal description / HOA
- Jurisdiction
- Lat/lng (manual or use-my-location)
- Square footage / year built / lot size

### Important implementation detail
Manual corrections and parser auto-fill both target the **same object**: `clientInfoOverrides`.

This means “manual override” is not isolated from parser refresh. It is just the latest write to the same structure.

### Likely failure points
- **Silent overwrite on re-parse:** parser also dispatches `SET_CLIENT_OVERRIDES` into the same object.  
  - `src/hooks/useIntake.ts:621-624`
- **Stale closure means parser may not see current manual edits when deciding whether to skip auto-fill.**  
  - `src/hooks/useIntake.ts:578`, `647`
- **No warning/merge UI** before re-applying parser-derived values.

### DEF-TB-002 mapping
Most likely code origin:
- `src/hooks/useIntake.ts:518-647` (`parseCRM`)  
Particularly:
- `:578` `hasExistingOverride = intake.clientInfoOverrides?.street`  
- `:591-623` rebuild + dispatch `newOverrides`  
- `:647` `useCallback(..., [])`

This is the clearest single location where manual correction can be lost on CRM re-parse.

---

## 4) Geocode Path

### Trigger source
Geocoding is triggered from canonical Intake hook, not the older ingestion hook.

### Auto-geocode chain
1. Address resolves through `selectResolvedLocation(intake)`.  
   - `src/hooks/useIntake.ts:1073`
2. Auto-geocode effect watches resolved address + coords state.  
   - `src/hooks/useIntake.ts:1078-1143`
3. When new address detected, stale auto property fields are cleared and `retryGeocoding()` is called.  
   - `src/hooks/useIntake.ts:1115-1129`
4. `retryGeocoding()` invokes `geocode-address`.  
   - `src/hooks/useIntake.ts:945-1069`
5. On success it writes:
   - `crmData.address.lat/lng`  
   - `clientInfoOverrides.latitude/longitude` + `coordSource: 'forward-geocode'`  
   - `autoSquareFootage`, `autoYearBuilt`, `autoLotSizeAcres`

### Geocoder implementation
- **Edge function:** `supabase/functions/geocode-address/index.ts`
- Geocoder can resolve:
  - `lat/lng`
  - `formattedAddress`
  - `county`
  - `jurisdiction`
  - property lookup data (sqft, year built, lot size)
- See `supabase/functions/geocode-address/index.ts:1523-1560` and parser helper `src/lib/geocoding/parseGeocodeResponse.ts:209-231`.

### What is consumed from geocode response in canonical hook
Consumed in `retryGeocoding()`:
- lat
- lng
- propertyData fields

Not promoted in canonical hook:
- jurisdiction
- county
- formattedAddress

### Likely failure points
- **Jurisdiction discarded at canonical write point.**  
  - `src/hooks/useIntake.ts:968-994`
- **Formatted geocoded address discarded; resolved address remains override/CRM text.**
- **County discarded from canonical location resolution until site-intelligence runs.**

This is a major contributor to DEF-TB-001.

---

## 5) Jurisdiction / Site-Intelligence Cascade

### Current active cascade
1. CRM paste produces address text.  
   - `useIntake.ts parseCRM`
2. Address change triggers geocoding.  
   - `useIntake.ts` auto-geocode effect
3. Intake tab renders `SiteScreeningStatus` once address/coords exist.  
   - `src/components/tabs/IntakeTab.tsx:377-385`
4. `SiteScreeningStatus` invokes `site-intelligence`.  
   - `src/components/SiteScreeningStatus.tsx:125`
5. Returned report is passed to `onFullReportReady(siteReport)` and stored in Intake via `setSiteIntelligenceReport`.  
   - `src/components/SiteScreeningStatus.tsx:139`  
   - `src/pages/Index.tsx:405-407`
6. From then on, resolved jurisdiction comes from `siteIntelligenceReport.location.jurisdiction`.  
   - `src/lib/intake/selectors.ts:72`

### Site Intelligence jurisdiction logic
- `supabase/functions/site-intelligence/index.ts:186-193`
- The function does **not** trust geocoder-provided jurisdiction as authoritative.
- It computes county and jurisdiction from coordinates using `detectCounty()` / `detectJurisdiction()`.

### Why locality can conflict with canonical address
- Address string may remain user-entered or CRM-parsed locality text.
- Geocoder may normalize that address to a different official locality.
- Site Intelligence independently assigns jurisdiction from coordinate bounding boxes.
- Selector then treats Site Intelligence jurisdiction as authoritative, even if text address still shows another locality.

### Concrete trust break
- **Text address source:** `clientInfoOverrides.street/city/state/zip` or `crmData.address.full`
- **Jurisdiction source:** `siteIntelligenceReport.location.jurisdiction`
- **No reconciliation layer** ensures those came from the same canonical geocode result.

### Likely failure points
- `src/hooks/useIntake.ts:968-994` — geocode jurisdiction not stored
- `src/lib/intake/selectors.ts:72` — jurisdiction only from site report
- `src/components/SiteScreeningStatus.tsx:125-139` — site report becomes the only populated jurisdiction source
- `supabase/functions/site-intelligence/index.ts:186-193` — coordinate-based jurisdiction detection may differ from address locality

### DEF-TB-001 mapping
Most likely origin is distributed but centered on these files:
- `src/hooks/useIntake.ts` — geocode writes only coords/property, not jurisdiction/formattedAddress
- `src/lib/intake/selectors.ts` — jurisdiction resolved only from `siteIntelligenceReport`
- `supabase/functions/site-intelligence/index.ts` — jurisdiction derived independently from coordinates

This combination explains both symptoms:
1. **jurisdiction never auto-resolves** until site-intelligence finishes, because geocode result is not made authoritative
2. **site-intelligence locality conflicts with canonical address** because the two values come from different authority chains

---

## 6) Read Path / Downstream Consumption

### Legacy tab adapter
- `src/lib/intake/adapters.ts`
- `adaptToIntakeTabProps(intake)` uses `selectResolvedLocation(intake)` for top-level `address/county/jurisdiction`.  
  - `src/lib/intake/adapters.ts:261-288`
- But `adaptCRMData(intake)` preserves `address.full` from CRM while also applying street/city/state/zip overrides separately.  
  - `src/lib/intake/adapters.ts:62-70`

### Reader hook
- `src/hooks/useIntakeReader.ts:240-270` rebuilds full address from overrides if present.

### Why this matters
There are at least **three parallel address representations** in active code:
1. `crmData.address.full`
2. rebuilt full address from `clientInfoOverrides`
3. `selectResolvedLocation().address`

And a separate jurisdiction source:
4. `siteIntelligenceReport.location.jurisdiction`

That fragmented read model increases the chance of locality/address drift.

---

## 7) Architecture Notes from Existing Docs vs Current Code

### Docs indicate intended flow
- `docs/INTAKE_SOURCE_OF_TRUTH.md` says Intake is the single source of truth.
- `docs/SYSTEM_MAP.md` describes CRM → Geocoder → Site Intelligence cascade.
- `docs/INTAKE_DATA_FLOW.md` documents manual input > intake data > defaults downstream.

### What code actually does
- Intake is the state hub, **but address truth is still split across multiple subtrees**.
- Manual corrections are intended to win, **but CRM auto-fill writes into the same override object and does so from a stale closure**.
- Geocoder can resolve jurisdiction, **but canonical selector ignores geocoder jurisdiction and waits for site-intelligence report**.

---

## 8) Specific Failure Point Table

| Path | File / Function | Likely Failure |
|---|---|---|
| CRM paste | `src/hooks/useIntake.ts` / `parseCRM` | Parser output auto-writes into override object used for manual edits |
| CRM re-parse | `src/hooks/useIntake.ts:647` / `useCallback(..., [])` | Stale `intake` snapshot causes overwrite of newer manual corrections |
| Address authority | `src/lib/intake/selectors.ts` / `selectResolvedLocation` | Address text and jurisdiction come from different authority chains |
| Geocode consume | `src/hooks/useIntake.ts` / `retryGeocoding` | Ignores `parsed.jurisdiction`, `parsed.county`, `parsed.formattedAddress` |
| Site-intel cascade | `src/components/SiteScreeningStatus.tsx` | Site-intelligence becomes sole source of jurisdiction after async run |
| Site-intel resolution | `supabase/functions/site-intelligence/index.ts` | Derives jurisdiction from coordinates, may differ from canonical text address |
| Legacy CRM adapter | `src/lib/intake/adapters.ts` | `address.full` can remain stale while override components differ |
| Reader path | `src/hooks/useIntakeReader.ts` | Rebuilds full address from overrides, creating another parallel address representation |

---

## 9) Bottom-Line Defect Attribution

### DEF-TB-001 — likely origin
**Primary code origin:**
- `src/hooks/useIntake.ts:968-994`
- `src/lib/intake/selectors.ts:72`
- `supabase/functions/site-intelligence/index.ts:186-193`

**Why:** geocoder resolves jurisdiction/locality but canonical Intake does not store/use it as authoritative; later site-intelligence computes jurisdiction from coords and selector surfaces only that result.

### DEF-TB-002 — likely origin
**Primary code origin:**
- `src/hooks/useIntake.ts:518-647`

**Most suspicious lines:**
- `:578` read override presence from captured `intake.clientInfoOverrides`
- `:591-623` reconstruct and dispatch overrides
- `:647` empty dependency array locks stale closure

**Why:** manual corrections and parser auto-fill share the same override object, and re-parse logic runs from stale Intake state, so parser-derived values can silently replace user corrections.

---

## 10) Notes on Non-Active / Secondary Paths

These exist but do not appear to be the active canonical Track B flow:
- `src/hooks/useIntakeIngestion.ts`
- `src/hooks/useSiteIntelligence.ts`

They contain more complete direct use of geocode fields (including jurisdiction), but the active Intake page is wired through `useIntake`, `Index.tsx`, `IntakeTab.tsx`, and `SiteScreeningStatus.tsx`.

That mismatch is relevant: some older paths appear conceptually closer to the intended architecture, but current Track B behavior is governed by the canonical Intake hook + selector path described above.

---

## Conclusion

The Track B failures map cleanly to two architectural seams in the active code:

1. **Address/jurisdiction authority is fragmented** — address text, coordinates, geocoder metadata, and site-intelligence jurisdiction do not share one canonical owner. That is the likely root of DEF-TB-001.
2. **Manual edits and parser auto-fill share one mutable override object, and CRM re-parse runs through a stale closure**. That is the likely root of DEF-TB-002.

No fixes proposed here; this packet is a code map only.
