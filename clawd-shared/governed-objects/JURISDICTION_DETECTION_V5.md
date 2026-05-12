# JURISDICTION DETECTION v5 — COMPLETE REFERENCE
## Omni Pool Builders & Design LLC
## Updated: 2026-02-25
## 12 Jurisdictions | Benson Added | Cochise Setback Flagged | Sierra Vista Discharge Fixed

---

## CHANGES FROM v4

| Change | Detail |
|---|---|
| Benson added | 12th jurisdiction. 2015 ISPSC, 48" setback confirmed from Omni field build |
| Cochise County setback | Changed from "7'" to "UNVERIFIED — varies by zoning district (34 districts)" |
| Sierra Vista drain permit | Reworded to "Pool water discharge permit (Public Works)" — applies when draining pool for maintenance/repairs/replaster. Cartridge filters do not backwash, but full pool drains still require this permit |
| Benson bbox added | detectCochiseCity() now includes Benson coordinates |

---

## WHY THIS EXISTS

**8880 N Camino Coronado** has Postal City = TUCSON but Jurisdiction = ORO VALLEY. A bounding box gets this wrong. Wrong jurisdiction = wrong setbacks, wrong barrier requirements, wrong auto-closer rules, permit rejection.

**The fix:** Query Pima County GIS APIs for the REAL jurisdiction, then match to requirements database. For other counties with no API, use bounding boxes + manual verification flags.

---

## ARCHITECTURE: DETECTION PRIORITY CHAIN

```
ADDRESS (from CRM Parser)
  |
  +-> Census Geocoder -> lat/lng
  +-> detectCounty(lat, lng) -> bounding box (fine for counties)
  +-> IF PIMA COUNTY (90% of jobs):
        +-> Query BOTH endpoints in PARALLEL (Promise.allSettled):
        |     (1) Subdivisions (Layer 15) -> JURIS + SUB_NAME
        |     (2) Boundaries2 (Layer 4)   -> JURISDICTION + ZONING
        +-> MERGE with priority chain:
        |     JURISDICTION: Subdivisions.JURIS -> Boundaries2.JURISDICTION -> bbox
        |     SUBDIVISION:  Subdivisions.SUB_NAME (only source)
        |     ZONING:       Boundaries2.ZONING (only source)
        +-> lookupJurisdiction() -> full requirements object
              +-> IF Oro Valley: getOroValleySubdivisionSetback(SUB_NAME)
      IF PINAL: Default "Pinal County", flag near Casa Grande/Coolidge
      IF COCHISE: bbox -> Sierra Vista / Benson / Bisbee / Douglas / unincorp
      IF SANTA CRUZ: bbox -> Nogales / Patagonia / unincorp
```

---

## API GAP ANALYSIS (VERIFIED 2026-02-25)

Both Pima endpoints have coverage gaps. They COMPLEMENT each other:

| Test Point | Boundaries2 (Layer 4) | Subdivisions (Layer 15) |
|---|---|---|
| 8880 N Camino Coronado (Campo Bello) | EMPTY | OV / CAMPO BELLO |
| OV nearby point | TOWN OF ORO VALLEY | OV / CAMPO BELLO |
| OV R1-36 area (unplatted) | TOWN OF ORO VALLEY | EMPTY |
| Tucson central | CITY OF TUCSON | TUC / PUEBLO CENTER |
| Marana Dove Mountain | TOWN OF MARANA | EMPTY |
| Sahuarita | TOWN OF SAHUARITA | SAH / RANCHO SAHUARITA |
| Green Valley (unincorp) | PIMA COUNTY | PC / TUCSON GREEN VALLEY |
| Unplatted desert | PIMA COUNTY | EMPTY |

Running BOTH in parallel and merging gives ~99% coverage. Subdivisions is the MUST-HAVE for residential pools (returns subdivision name for OV setback lookup, catches boundary-edge parcels).

---

## VERIFIED PIMA COUNTY ENDPOINTS

### Endpoint 1: Subdivisions (Layer 15) — PRIMARY

```
URL: https://gisdata.pima.gov/arcgis1/rest/services/GISOpenData/LandRecords/MapServer/15/query
Params: geometry={lng},{lat}&geometryType=esriGeometryPoint&inSR=4326
        &spatialRel=esriSpatialRelIntersects&outFields=JURIS,SUB_NAME,SEQ_NUM,LOT_COUNT
        &returnGeometry=false&f=json
Returns: { "JURIS": "OV", "SUB_NAME": "CAMPO BELLO" }
```

| Code | Jurisdiction | Key |
|---|---|---|
| OV | Town of Oro Valley | Oro Valley |
| TU/TUC | City of Tucson | Tucson |
| MA/MAR | Town of Marana | Marana |
| SA/SAH | Town of Sahuarita | Sahuarita |
| PC | Pima County (unincorp) | Pima County |
| ST/STUC | City of South Tucson | Pima County |
| GV | Green Valley (CDP) | Pima County |
| AJ | Ajo (CDP) | Pima County |

### Endpoint 2: Boundaries2 Zoning (Layer 4) — SECONDARY

```
URL: https://gisdata.pima.gov/arcgis1/rest/services/GISOpenData/Boundaries2/MapServer/4/query
Params: geometry={lng},{lat}&geometryType=esriGeometryPoint&inSR=4326
        &spatialRel=esriSpatialRelIntersects&outFields=JURISDICTION,ZONING,ZONE
        &returnGeometry=false&f=json
Returns: { "JURISDICTION": "TOWN OF ORO VALLEY", "ZONING": "R1-36 OV" }
```

| API Value | Key |
|---|---|
| CITY OF TUCSON | Tucson |
| TOWN OF ORO VALLEY | Oro Valley |
| TOWN OF MARANA | Marana |
| TOWN OF SAHUARITA | Sahuarita |
| PIMA COUNTY | Pima County |
| CITY OF SOUTH TUCSON | Pima County |

---

## ALL 12 JURISDICTIONS — REQUIREMENTS DATABASE

### 1. Pima County (Unincorporated)

| Field | Value |
|---|---|
| Setback | 4' PL to Water |
| Enclosure | 4' (48") |
| Barriers | 4' W/I, SCSL, Door Alarms |
| Equipment | None |
| Gate latch | 54" |
| Auto-closer | No |
| Window film | No |
| Code | 2018 ISPSC (Chapter 3) |

### 2. City of Tucson

| Field | Value |
|---|---|
| Setback | 20" min from WATERLINE (not PL) |
| Enclosure | 5' |
| Barriers | 5' W/I, SCSL, Door Alarms |
| Equipment | None |
| Gate latch | 54" |
| Auto-closer | No |
| Window film | Required (spec sheet) |
| Code | ARS 36-1681 + local amendments |

### 3. Town of Marana

| Field | Value |
|---|---|
| Setback | Per subdivision (Continental Ranch: 5') |
| Enclosure | 5' |
| Barriers | 5' W/I, SCSL, Door Alarms |
| Equipment | 4' from common wall |
| Gate latch | 54" |
| Auto-closer | No |
| Window film | No |
| Code | ARS 36-1681 + local |
| Notes | 4' non-climbable zone, 5' total height |

### 4. Town of Oro Valley — MOST COMPLEX

| Field | Value |
|---|---|
| Setback | VARIES BY SUBDIVISION (5' to 20' side, 5' rear) |
| Enclosure | 5' |
| Barriers | 5' W/I, SCSL (NO door alarms) |
| Equipment | 4' from enclosure/barrier OR 4'H screen |
| Gate latch | 54" |
| Auto-closer | YES — ALL exterior doors (UNIQUE TO OV) |
| Auto-slider | YES — ALL sliding glass doors (UNIQUE TO OV) |
| Window film | Required (spec sheet) |
| Window latch | 42" above floor |
| Portable spa | Max 8' any direction |
| Code | ARS 36-1681 + OV local |
| Phone | (520) 229-4800 |

**OV Subdivision Setbacks (matched from API SUB_NAME):**

| Subdivision | Side | Rear |
|---|---|---|
| Sun City OV, La Canada Hills, Steam Pump Village | 5' | 5' |
| Catalina Shadows | 8' | 5' |
| Rancho Vistoso, Countryside, La Cholla Hills, OV Country Club, Pusch Ridge Vistas, Canada del Oro, Westward Look, Mountain Vistas, Village at OV, Campo Bello, Shadow Mountain Estates | 10' | 5' |
| La Reserve, Arroyo Grande | 15' | 5' |
| Stone Canyon | 20' | 5' |
| Default (unmatched) | VERIFY — Call (520) 229-4800 | 5' |

### 5. Town of Sahuarita

| Field | Value |
|---|---|
| Setback | 5' |
| Enclosure | 5' |
| Barriers | 5' W/I, SCSL, Door Alarms |
| Equipment | Heater 4' from PL; Pump/Filter 4' from common wall |
| Gate latch | 54" |
| Auto-closer | No |
| Window film | No |
| Window latch | 54" above finished floor (highest in service area) |
| Barrier as electric cover | NOT allowed (unique restriction) |
| Code | ARS 36-1681 + local |

### 6. Pinal County (Unincorporated)

| Field | Value |
|---|---|
| Setback | 4' PL to Water, 30" around pool (not on PL) |
| Enclosure | 3' to house, 5' perimeter |
| Barriers | 5' W/I, SCSL, OR Door Alarms (alternative, not both) |
| Equipment | None |
| Gate latch | 54" |
| Auto-closer | No |
| Window film | Case by case |
| Code | 2006 Fire Code |

### 7. Santa Cruz County (Unincorporated)

| Field | Value |
|---|---|
| Setback | R1-R5: 7.5' Side & Rear, 15' Front (variance only) |
| Enclosure | 5' |
| Barriers | 5' W/I, SCSL, Solar Blanket |
| Equipment | None |
| Auto-closer | No |
| Window film | No |
| Code | ARS 36-1681 |
| Notes | Front setback requires variance (rarely granted) |

### 8. City of Nogales

| Field | Value |
|---|---|
| Setback | 3' (tied with Sierra Vista for least restrictive) |
| Enclosure | 4' |
| Barriers | 4' W/I, SCSL, Solar Blanket |
| Equipment | None |
| Auto-closer | No |
| Window film | No |
| Code | ARS 36-1681 |

### 9. Cochise County (Unincorporated) — SETBACK UNVERIFIED

| Field | Value |
|---|---|
| Setback | **UNVERIFIED — varies by zoning district (34 districts). Call (520) 432-9240** |
| Enclosure | 5' (60" per local amendment to ISPSC 305.2.1) |
| Barriers | 5' W/I, SCSL, Doors, Chain Link, Solar Blanket |
| Equipment | Exhaust 4' from PL |
| Gate latch | 54" |
| Auto-closer | No |
| Window film | No |
| Code | 2015 IRC/IBC + local amendments |
| Phone | (520) 432-9240 |

Previous v4 listed 7' — this is UNCONFIRMED. Cochise has 34 zoning districts each with their own setback standards. Confirm per parcel with Planning & Zoning.

### 10. City of Sierra Vista

| Field | Value |
|---|---|
| Setback | 3' (0' if abuts alley/wash) |
| Enclosure | 48" ISPSC / USE 5' per ARS 36-1681 |
| Barriers | 48" min, no 4" sphere passage, SCSL gate |
| Door alarms | Yes (UL 2017, per ISPSC 305.4) |
| Equipment | Standard code + NEC clearances |
| Gate latch | 54" |
| Auto-closer | No |
| Window alarm | Yes (if sill < 48") |
| Window film | No |
| **Discharge permit** | **Pool water discharge permit through Public Works (not Building Dept). Applies when draining pool for maintenance, repairs, or replaster. Cartridge filter systems do not backwash, but full pool drains still require this permit.** |
| Spa fee | $50 flat fee |
| Code | 2018 ISPSC (Resolution 2023-043) |
| Phone | (520) 458-3315 |
| Permits | CitizenServe online |

**Boundary danger — Sierra Vista vs Cochise County:**

| | Sierra Vista | Cochise Unincorporated |
|---|---|---|
| Setback | 3' | UNVERIFIED (varies by zone) |
| Code basis | 2018 ISPSC | 2015 IRC + amendments |
| Detection | Bounding box only (no GIS API) |

### 11. City of Benson — NEW in v5

| Field | Value |
|---|---|
| Setback | **48" (4') from rear and side property lines** |
| Enclosure | 5' per ARS 36-1681 |
| Barriers | Per 2015 ISPSC + ARS 36-1681 |
| Equipment | Standard code + NEC clearances |
| Gate latch | 54" |
| Auto-closer | No |
| Window film | No |
| Code | **2015 ISPSC + 2014 NEC** |
| Phone | (520) 720-6328 |
| Verified | **YES — from Omni field build** |

Note: Benson is on a different code cycle than Sierra Vista (2015 vs 2018) and unincorporated Cochise (2015 IRC vs 2015 ISPSC). Three Cochise County jurisdictions, three different code bases.

### 12. [Placeholder] City of Douglas / City of Bisbee

Not yet researched to full depth. Default to Cochise County requirements + manual verification until field data obtained.

---

## WORKAROUNDS AND EDGE CASES

### Boundaries2 returns empty for boundary-edge parcels
Run Subdivisions layer FIRST in priority chain. If both empty, fall back to bbox + flag.

### Subdivisions returns empty for unplatted land
Boundaries2 covers these. Dual-API approach catches both cases.

### No Cochise County GIS API
Bounding box with WARNING flag. Benson bbox added in v5. Conservative sizing to avoid false positives.

### No Pinal County jurisdiction field
Default "Pinal County" (unincorporated). Flag near Casa Grande/Coolidge.

### Postal city vs actual jurisdiction
NEVER use postal city for jurisdiction. Always use GIS API (Pima) or bbox (others).

### OV subdivision name fuzzy matching
API returns "CAMPO BELLO CNTRL PTN TRACT 14" — fuzzy match extracts "CAMPO BELLO".

### ARS 36-1681 vs local codes
Always build to MORE RESTRICTIVE of state or local. In practice: 5' everywhere except confirmed no children under 6 AND local allows 4'.

### Cochise County setback ambiguity
v4 listed 7' — this is unconfirmed. Cochise has 34 zoning districts. The setback is a ZONING requirement, not a building code requirement, so it varies by parcel zoning classification. Always call (520) 432-9240 for Cochise County builds.

### Sierra Vista discharge permit
This is a pool water discharge permit through Public Works — NOT a pool drain (suction line) permit. It applies when draining pool water for maintenance, repairs, or replaster. Cartridge filter systems (which Omni typically installs) do not produce backwash water, but a full pool drain for replaster or major repair still triggers this permit requirement. Sand filter systems DO backwash and would also trigger discharge rules, but Omni does not typically install sand filters.

---

## PLUG-IN JAVASCRIPT

Complete module: **jurisdiction-engine-v5.js** (443 lines)

Integration:
```javascript
const result = await JurisdictionEngine.detect(lat, lng);
JurisdictionEngine.updateUI(result);
JurisdictionEngine.store(result);
const reqs = JurisdictionEngine.lookupJurisdiction(result.jurisdiction);
```

---

## DATA FRESHNESS

| Source | Verified | Method |
|---|---|---|
| Pima Subdivisions API (Layer 15) | 2026-02-25 | Live test |
| Pima Boundaries2 API (Layer 4) | 2026-02-25 | Live test |
| Pima jurisdiction values (all 6) | 2026-02-25 | Live test |
| OV subdivision setbacks (20 entries) | 2025-12 | OV Building Safety |
| Benson setback (48") | 2026 | Omni field build |
| Sierra Vista codes | 2026-02-25 | Resolution 2023-043 |
| Cochise County setback | UNVERIFIED | Previously listed 7', needs confirmation |
| All other jurisdictions | 2025-12 | Code research |

---

## PENDING

- [ ] Confirm Cochise County pool setback per zoning district — call (520) 432-9240
- [ ] Confirm Sierra Vista discharge permit applicability — call (520) 458-3315
- [ ] Test Pinal County parcel endpoints for jurisdiction field
- [ ] Integrate jurisdiction-engine-v5.js into site-intelligence-v6.html
- [ ] Add more OV subdivisions as discovered
- [ ] Research Bisbee and Douglas to full jurisdiction depth
- [ ] Add Marana subdivision setback database (Continental Ranch etc.)
