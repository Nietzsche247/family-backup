# DEF-TB-001 Engine Audit — Jurisdiction Engine v5 Cross-Reference

## Scope
Reference reviewed first:
- `C:\Users\aaron\clawd-shared\governed-objects\JURISDICTION-ENGINE-V5.js`
- `C:\Users\aaron\clawd-shared\governed-objects\JURISDICTION-DETECTION-V5.md`
- Prior art: `C:\Users\aaron\clawd-shared\governed-objects\DEF-TB-001-CODE-MAP.md`

Codebase searched:
- `C:\Users\aaron\clawd-shared\omnipools-repo\src\`

Constraint followed:
- Read-only on source; no source edits made.

---

## Executive Classification
# PARTIALLY WIRED

### Why this is **PARTIALLY WIRED**, not FULLY WIRED
The current codebase has **jurisdiction field plumbing** and **UI surfaces that display a county/jurisdiction string**, but I found **no active JurisdictionEngine v5 (or equivalent)** in `src`, and I found **no active jurisdiction rules database / subdivision setback database / alert engine / Pima dual-API detection logic**.

So:
- **Present:** jurisdiction value ingestion, storage, selector/adaptor flow, and simple UI display.
- **Missing:** the v5 detection engine itself and the v5 rules payload/UI.
- **Result:** current app can carry and show a jurisdiction string, but it is **not running the v5 auto-detection + rules system** described in the reference files.

---

## 1) Is `JurisdictionEngine` (or equivalent) present in the current codebase?

## Finding
**No active `JurisdictionEngine` or equivalent v5 engine exists in `src`.**

### Search terms attempted against `src`
- `JurisdictionEngine`
- `jurisdiction detection`
- `bounding box`
- `Pima GIS`
- `gisdata.pima.gov`
- `JURIS_CODE_MAP`
- `detectPimaJurisdiction`
- `detectCounty(`
- `detectCochiseCity(`
- `detectSantaCruzCity(`
- `lookupJurisdiction(`
- `OV_SUBDIVISION_SETBACKS`
- `subdivision`

### Result
No active hits for the v5 engine identifiers or its core mechanisms:
- **No `JurisdictionEngine` symbol** in active code
- **No `gisdata.pima.gov` calls** in active `src`
- **No `JURIS_CODE_MAP`**
- **No bounding-box jurisdiction detection helpers**
- **No `lookupJurisdiction()` implementation**
- **No Oro Valley subdivision setback DB**

### What *is* present instead
The active code relies on external function outputs that already contain `county` / `jurisdiction`, then passes those values through intake/site-intelligence UI.

Evidence:
- `src/lib/geocoding/parseGeocodeResponse.ts:208-230` extracts `county` and `jurisdiction` from geocode response payloads.
- `src/hooks/useIntakeIngestion.ts:193-200` maps parsed geocode results into intake address data.
- `src/hooks/useSiteIntelligence.ts:120`, `src/hooks/useSiteIntelligence.ts:186` map `parsed.jurisdiction` into site-intelligence ingestion data.
- `src/components/siteIntelligence/cards/LocationCard.tsx:159-166` displays jurisdiction.
- `src/components/SiteIntelligenceReport.tsx:279-280` displays jurisdiction.

### Dead-code note
There is one **inactive** simplistic mapping in dead code, not an engine:
- `src/_dead_code_2026-03-09/IngestionRouter.tsx:176-184`
  - maps county names to coarse jurisdiction slugs (`Pima -> pima-county`, etc.)
  - this is not the v5 engine, not subdivision-aware, not Pima GIS-backed, and not active.

### Conclusion
**The v5 engine is not present in active `src`.**
The active code only consumes a plain `jurisdiction` value from upstream geocode/site-intelligence responses.

---

## 2) Is the jurisdiction RULES data present?

## Finding
**No active v5 jurisdiction rules dataset is present in `src`.**

### Search terms attempted against `src`
- `setback`
- `barrier`
- `door alarms`
- `auto-closer`
- `auto closer`
- `auto-slider`
- `auto slider`
- `window film`
- `window latch`
- `discharge permit`
- `2018 ISPSC`
- `2015 ISPSC`
- `2014 NEC`
- `ARS 36-1681`
- jurisdiction names from v5 reference: `Tucson`, `Oro Valley`, `Marana`, `Sahuarita`, `Pima County`, `Cochise County`, `Sierra Vista`, `Benson`, `Green Valley`, `Nogales`, `Santa Cruz County`, `Bisbee`, `Douglas`

### Result
I found **no active object/table/module** in `src` containing the v5 rules content:
- no per-jurisdiction setback matrix
- no barrier-height rule table
- no auto-closer / auto-slider rule table
- no alarm / door-type requirements table
- no subdivision-specific setback DB
- no 12-jurisdiction requirements object equivalent to `JURISDICTIONS` in the reference file

### What jurisdiction-name hits do exist
They are mostly **labels/options/tests/display strings**, not rules:
- `src/components/intake/ParsedClientInfo.tsx:58-66`
  - manual dropdown options include `Tucson`, `Oro Valley`, `Marana`, `Sahuarita`, `Pima County`, etc.
- `src/pages/Index.tsx:239-258`
  - mock/demo site-intelligence data includes `jurisdiction: 'Marana'` and `source: 'Pima County GIS'`
- `src/lib/heaterCalculations/climate.ts:115-224`
  - locality names used for climate resolution (`Marana`, `Oro Valley`, `Green Valley`, `Sahuarita`) but this is unrelated to code rules

### Important negative evidence
A targeted source search for the actual rule phrases from v5 returned only the dropdown declaration in `ParsedClientInfo.tsx`:
- `auto-closer`, `auto-slider`, `window film`, `window latch`, `door alarms`, `2018 ISPSC`, `2015 ISPSC`, `2014 NEC`, `ARS 36-1681`, `Pool water discharge permit` → **no active rules hits in `src`**

### Conclusion
**The jurisdiction RULES data from v5 is missing from active code.**
The codebase has jurisdiction strings, not jurisdiction requirements.

---

## 3) Is there a UI surface that displays jurisdiction rules?

## Finding
**No active UI surface was found that displays jurisdiction-specific rules.**

### Active UI surfaces that display only location/jurisdiction identity
- `src/components/siteIntelligence/cards/LocationCard.tsx:159-166`
  - shows a `Jurisdiction` badge only
- `src/components/SiteIntelligenceReport.tsx:275-280`
  - shows county + jurisdiction in the Location panel
- `src/components/tabs/IntakeTab.tsx:347-356`
  - shows county/jurisdiction text in the Site Intelligence header area
- `src/components/tabs/HomeownerResultsTab.tsx:188-191`
  - shows county/jurisdiction in homeowner output
- `src/components/tabs/FullReportsTab.tsx:881-883`
  - shows county/jurisdiction in Site Intelligence data section
- `src/components/reports/UnifiedPDFExport.tsx:231`, `:272`, `:457`
  - exports jurisdiction string
- `src/components/tabs/PermittingTab.tsx:154`
  - shows jurisdiction field

### What I did **not** find
No active UI component for:
- jurisdiction rules card/panel/section
- setback rules display
- barrier requirements display
- alarm requirements display
- door requirements display
- Oro Valley subdivision setback display
- jurisdiction alerts panel equivalent to `JurisdictionEngine.updateUI()` output

### Site Intelligence-specific conclusion
The Site Intelligence module currently surfaces **location identity** (`county`, `jurisdiction`) plus soil/flood/geology data, but **not jurisdiction code rules**.

---

## 4) Wiring status and evidence

## Classification: PARTIALLY WIRED

### Evidence for the “wired” part
There is a real path for jurisdiction strings to move through the app:
- Geocode parser extracts jurisdiction: `src/lib/geocoding/parseGeocodeResponse.ts:208-230`
- Intake ingestion can carry jurisdiction into parsed address data: `src/hooks/useIntakeIngestion.ts:335-343`
- Site Intelligence report schema includes jurisdiction: `src/lib/intake/schema.ts:221-231`
- Canonical resolved location reads jurisdiction from `siteIntelligenceReport.location.jurisdiction`: `src/lib/intake/selectors.ts:71-72`
- Intake adapter passes jurisdiction into the tab props: `src/lib/intake/adapters.ts:281-285`
- UI displays jurisdiction:
  - `src/components/siteIntelligence/cards/LocationCard.tsx:159-166`
  - `src/components/SiteIntelligenceReport.tsx:279-280`
  - `src/components/tabs/FullReportsTab.tsx:881-883`
  - `src/components/reports/UnifiedPDFExport.tsx:231`, `:272`, `:457`

### Evidence for the “not fully wired” part
The v5-specific engine/rules wiring is absent:
- No active `JurisdictionEngine`
- No active Pima dual-API calls (`gisdata.pima.gov` absent in `src`)
- No bounding-box fallback detection helpers
- No `JURIS_CODE_MAP`
- No jurisdiction requirements DB equivalent to the v5 `JURISDICTIONS` object
- No OV subdivision setback DB
- No rules UI / alerts UI

### Bottom line
The codebase is **not** “engine exists, called on geocode, results displayed.”
Instead it is:
- **jurisdiction string exists**
- **string is displayed**
- **v5 engine/rules are absent**

That is why the correct classification is **PARTIALLY WIRED**, not FULLY WIRED and not completely MISSING.

---

## 5) Gap map — what specific pieces are missing or disconnected relative to v5

This is an audit-only gap map, not a fix plan.

### A. Missing detection engine layer
Defined in v5, not found in active `src`:
- `JurisdictionEngine.detect(lat, lng)` entry point
- county bbox detection (`detectCounty`)
- Cochise city bbox detection (`detectCochiseCity`)
- Santa Cruz city bbox detection (`detectSantaCruzCity`)
- Pima fallback city bbox detection
- merged priority chain:
  - Pima Subdivisions API
  - Pima Boundaries2 API
  - bbox fallback

### B. Missing Pima GIS integration layer
Defined in v5, not found in active `src`:
- `https://gisdata.pima.gov/.../LandRecords/MapServer/15/query`
- `https://gisdata.pima.gov/.../Boundaries2/MapServer/4/query`
- `JURIS_CODE_MAP`
- `JURIS_TEXT_MAP`
- subdivision extraction (`SUB_NAME`)
- zoning extraction (`ZONING`)

### C. Missing jurisdiction rules database
Defined in v5, not found in active `src`:
- 12-jurisdiction requirements object
- fields such as:
  - setback
  - enclosure/barrier height
  - barriers
  - equipment constraints
  - gateLatch
  - autoCloser
  - autoSlider
  - windowFilm
  - windowLatch
  - doorAlarms
  - barrierAsElectricCover
  - code cycle
  - phone / verify notes

### D. Missing subdivision-specific logic
Defined in v5, not found in active `src`:
- `OV_SUBDIVISION_SETBACKS`
- fuzzy subdivision matching
- Oro Valley-specific setback resolution from subdivision name

### E. Missing rules/alerts presentation layer
Defined in v5, not found in active `src`:
- `lookupJurisdiction()` consumption for requirements
- jurisdiction alerts list / severity rendering
- jurisdiction rule card/panel
- rules export surface in reports/PDF

### F. Current active implementation is narrower than v5
Current app supports only:
- user-entered jurisdiction selection: `src/components/intake/ParsedClientInfo.tsx:437-450`
- geocode/site-intelligence supplied jurisdiction strings
- display/export of county/jurisdiction label only

It does **not** currently support:
- v5-quality jurisdiction resolution logic
- rules lookup
- rule-specific UI output

---

## Active evidence summary

### Active files proving jurisdiction value plumbing exists
- `src/lib/geocoding/parseGeocodeResponse.ts:208-230`
- `src/hooks/useIntakeIngestion.ts:193-200`
- `src/hooks/useIntakeIngestion.ts:335-343`
- `src/lib/intake/schema.ts:221-231`
- `src/lib/intake/selectors.ts:71-72`
- `src/lib/intake/adapters.ts:281-285`
- `src/components/siteIntelligence/cards/LocationCard.tsx:159-166`
- `src/components/SiteIntelligenceReport.tsx:279-280`
- `src/components/tabs/IntakeTab.tsx:347-356`
- `src/components/tabs/FullReportsTab.tsx:881-883`
- `src/components/reports/UnifiedPDFExport.tsx:231`, `:272`, `:457`

### Active evidence that rules engine is missing
No active hits in `src` for:
- `JurisdictionEngine`
- `gisdata.pima.gov`
- `JURIS_CODE_MAP`
- `lookupJurisdiction(`
- `OV_SUBDIVISION_SETBACKS`
- v5 rule phrases (`auto-closer`, `auto-slider`, `window film`, `window latch`, `door alarms`, `2018 ISPSC`, `2015 ISPSC`, `2014 NEC`, `ARS 36-1681`, `Pool water discharge permit`)

### Dead-code-only note
- `src/_dead_code_2026-03-09/IngestionRouter.tsx:176-184`
  - contains only a coarse county→jurisdiction slug map
  - not active, not v5, not rules-aware

---

## Final answer
The current OmniPools `src` tree is **PARTIALLY WIRED** for jurisdiction as a **data label**, but the **Jurisdiction Engine v5 itself is missing from active code**, and the **jurisdiction rules dataset/UI are also missing**.

So TB-001 is **not** just a selector-only issue if the goal is to restore full v5 behavior. The codebase currently has the **plumbing to carry/show jurisdiction**, but not the **v5 detection + requirements system** that Aaron provided in the reference JS/MD.
