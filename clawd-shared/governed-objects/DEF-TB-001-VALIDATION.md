# DEF-TB-001 Validation Report

**Validator:** Empiricus  
**Date:** 2026-03-23 MST  
**Environment:** Production — `https://omnipoolsaz.com/`  
**Observed bundle:** `assets/index-CTtJqlS-.js`  
**Scope:** TB-001 Phase 1 only, with TB-002 / TB-003 / coordSource noted separately where relevant.

---

## Verdict

**TB-001 = FAIL**

This is a **live-session collapse**, not only a reload-class issue.

### Why it fails
On the live production bundle, after CRM parse + geocode/site-intel completion:
- **Jurisdiction field does not auto-populate** — Intake still shows `Select jurisdiction`
- **Site Intelligence locality/jurisdiction display disagrees with the canonical address**
- The mismatch occurs **before reload**, so this is a TB-001 trust-break failure by definition.

---

## Test Input

CRM note used:

```text
Lead: Maria Gonzalez
Phone: 520-555-1234
Email: maria.gonzalez@email.com
Project Address: 8880 N Camino Coronado, Tucson, AZ 85704
Notes: existing pool needs resurfacing
```

---

## Phase 1 checks

### 1. Jurisdiction auto-populates from geocode / Site Intelligence
**Expected:** Jurisdiction field auto-fills without manual selection.  
**Observed:** Intake `Jurisdiction` remained `Select jurisdiction` after parsing/geocoding completed.  
**Observed related state:**
- Project Address input: `8880 N Camino Coronado`
- Site Intelligence header address: `8880 N Camino Coronado, Tucson, AZ 85704`
- Site Intelligence location text: `Pima, Oro Valley`

**Result:** **FAIL**

### 2. Manual override sticks if applied
**Status:** Not required to determine TB-001 verdict because Phase 1 already fails in live session.

**Note:** Manual-override persistence was not needed to classify this run. The live-session failure already blocks closure.

### 3. UI / reports / permitting / homeowner / PDF all show same jurisdiction value
**Expected:** One canonical jurisdiction source across all surfaces.  
**Observed from live UI + code-path inspection:**
- Intake editable jurisdiction field: blank / `Select jurisdiction`
- Site Intelligence display: `Oro Valley`
- Report/export surfaces in code are wired to `siteIntelligenceReport.location.jurisdiction`
  - `src/components/reports/UnifiedPDFExport.tsx`
  - `src/components/tabs/PermittingTab.tsx`
  - `src/components/tabs/HomeownerResultsTab.tsx`
  - `src/lib/artifacts/generatePermitPacket.ts`

**Interpretation:** current architecture still allows report/export surfaces to trust Site Intelligence jurisdiction while Intake canonical field is blank or divergent.

**Result:** **FAIL**

### 4. No TB-002 regression (CRM parser corrections still stick)
**Status:** Not executed in this run.  
**Reason:** TB-001 already failed on live session canonical mismatch. Separate regression run still advisable.

### 5. No TB-003 regression (note reload behavior separately)
**Status:** Not executed in this run.  
**Reason:** TB-001 fail occurred pre-reload, so reload behavior is not needed for classification.

### 6. No coordSource regression
**Observed:** Latitude/Longitude fields remained tagged `CRM`; no new obvious coordSource trust-break was surfaced during this run.  
**Result:** **PASS / no obvious regression observed in this limited pass**

---

## Exact live evidence

### Intake surface
- `Project Address` = `8880 N Camino Coronado`
- `Jurisdiction` = `Select jurisdiction`
- `Latitude` = `32.368751`
- `Longitude` = `-110.984189`
- Property data fetched successfully (`RentCast property records`, sqft/year/lot size populated)

### Site Intelligence surface
- Status = `Analysis complete`
- Displayed address = `8880 N Camino Coronado, Tucson, AZ 85704`
- Displayed locality/jurisdiction line = `Pima, Oro Valley`

### Failure condition hit
The system presents two different truths simultaneously:
1. editable Intake jurisdiction is blank
2. Site Intelligence display asserts `Oro Valley`
3. address says `Tucson, AZ 85704`

That is exactly a **live-session canonical trust break**.

---

## TB-001 / TB-003 classification note

- **TB-001** = live-session collapse → **YES, reproduced**
- **TB-003** = reload/rehydration-only collapse → **not required for this verdict**

Because the mismatch appears **before reload**, this run is a **TB-001 FAIL** regardless of reload behavior.

---

## Technical note

Observed bundle is new (`index-CTtJqlS-.js`), so this was not just stale old bundle evidence.

Code-path inspection also still shows permit/report surfaces sourcing jurisdiction from site-intelligence location data rather than a clearly unified Intake canonical field.

Relevant files observed:
- `src/components/tabs/IntakeTab.tsx`
- `src/components/reports/UnifiedPDFExport.tsx`
- `src/components/tabs/PermittingTab.tsx`
- `src/components/tabs/HomeownerResultsTab.tsx`
- `src/lib/artifacts/generatePermitPacket.ts`

---

## Bottom line

**Do not close DEF-TB-001.**

Current production still fails Phase 1 because jurisdiction does **not** auto-populate into the Intake canonical field, and Site Intelligence still displays a conflicting jurisdiction/locality in the same live session.
