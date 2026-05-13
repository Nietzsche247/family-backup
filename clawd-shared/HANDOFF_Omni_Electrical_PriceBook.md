# OMNI ELECTRICAL PRICEBOOK — MASTER BUILD SUMMARY
## Handoff Document for Session Continuity
**Date:** April 9, 2026
**Author:** Aaron Baker + Claude
**File:** `Omni_Electrical_PriceBook_v1.xlsx`
**Location:** `C:\Users\aaron\Downloads\Omni_Electrical_PriceBook_v1.xlsx`

---

## ⚠ CRITICAL INSTRUCTION FOR NEXT SESSION

**Before responding to ANY request, the next Claude session MUST:**

1. **Search past chats** for conversations about "electrical pricebook," "gas calculator," "ProDBX upload," and "simple sets" to load full context
2. **Read the two gas-related Excel files** from Aaron's Downloads folder:
   - `C:\Users\aaron\Downloads\Gas_Line_Calculator.xlsx` — Gas line sizing calculator (trunk → branch → pipe size logic based on BTU)
   - `C:\Users\aaron\Downloads\GAS LINE MATERIAL PRICE LIST.xlsx` — Spool pricing comparison (500' vs 250' vs 100' cost per foot analysis)
3. **Read the completed electrical pricebook** for structural reference:
   - `C:\Users\aaron\Downloads\Omni_Electrical_PriceBook_v1.xlsx`
4. **Read the original electrical service price sheet** for the ProDBX upload template formats:
   - `C:\Users\aaron\Downloads\Electrical_Service_Price_Sheet.xlsx` — Contains the master ProDBX 82-column upload template (tab: "Master Stock Upload(DO NOT ALTE)") and the Simple Set upload template (tab: "SIMPLE SET BASE")
5. **Review the project knowledge** files: `Omni_Claude_Team_Architecture_Blueprint.md`, `HANDOFF_ProDBX_Contract_DigiDoc.md`, and `service-automation-playbook.md` for the full ProDBX context

The gas pricebook build MUST follow the identical architecture, upload format, naming conventions, and automation philosophy established in the electrical build documented below.

---

## 1. WHAT WE BUILT (Electrical)

### Deliverable: `Omni_Electrical_PriceBook_v1.xlsx`

**6 tabs:**

| Tab | Purpose | Upload to ProDBX? |
|-----|---------|-------------------|
| ⚠ READ BEFORE UPLOAD | Step-by-step checklist for Adam (ProDBX implementer) | NO — instructions only |
| Working Reference | Internal design layer with item codes, categories, material pairs, phase assignments | NO — reference only |
| Electrical - Labor_For_Upload | 162 labor stock items in ProDBX 82-column format | YES — Upload #1 as CSV |
| Elec - Material_For_Upload | 89 material stock items in ProDBX 82-column format | YES — Upload #2 as CSV |
| Simple Sets — For Upload | 25 Simple Sets in ProDBX template format (Man. Number / DBX ID / Name / Description / Pricebook / Complex Set Group) | YES — Upload #3 (after #1 and #2, once DBX IDs are captured) |
| Parametric Set Design | If/Then logic blueprint for the Underground Feed Per LF parametric set | NO — programming reference |

### Item Counts:
- **162 labor atoms** across 12 categories
- **89 material atoms** across 7 ProDBX categories
- **25 Simple Sets** with 329 total stock item references
- **123 numbered If/Then rules** for ProDBX programming

---

## 2. WHY LABOR AND MATERIALS ARE SEPARATE

Omni moved electrical work in-house (no more sub-contractors). The old sub model (Craig's, Miranda's, the 2015 sub sheet) bundled labor + materials into single flat-rate prices. That's dead because it provides zero visibility.

**Separating labor and materials enables:**

1. **Accurate estimating** — Designer picks a Simple Set, ProDBX calculates labor hours + material cost independently
2. **Purchasing/PO generation** — Material stock items are flagged `inventoried=1` and `fulfillment=vendor`, so ProDBX generates POs to suppliers (Superior Pool Products, Heritage Pool Supply via DistributorConnect API)
3. **Inventory tracking** — Know what's on the truck, what's been used, what needs reordering
4. **P&L accuracy at job close** — Compare estimated labor hours vs actual, estimated material qty vs actual invoiced. See exactly where you made or lost money
5. **API-ready material pricing** — Materials flagged "API-SYNC" will auto-update cost from distributor feeds. Materials flagged "MANUAL" (pool-specific items like listed jboxes) are maintained by hand
6. **Waste tracking** — All materials carry `quantity_over=15` (15% overage). ProDBX auto-orders 15% more than estimated. At job close, compare ordered vs used to validate the 15% factor
7. **Rate change isolation** — If labor rate changes, update ONE number. If copper prices spike, material costs update via API or one edit. Neither affects the other

---

## 3. THE LABOR RATE MODEL

**$150/hr is the EFFECTIVE COST per productive hour — NOT a raw wage or a billable rate.**

It accounts for the real operational reality:
- 2-man crew on every job
- 45-minute drive each way
- Supply runs mid-job (30+ min)
- Full day pay for ~2-4 hours of productive work
- Wages + burden (workers comp, FICA, benefits, tools, truck)

This goes in the ProDBX `cost` column. The `price` column (what the customer pays) is calculated by ProDBX using margin settings:
- **42% default margin**
- **27% for construction (commercial and residential)**
- **42% for renovation/service/warranty**

These division margins are pre-populated in every row of both upload tabs.

---

## 4. HOW THE SIMPLE SETS WORK

### Architecture: Atoms → Simple Sets → Complex Sets

- **Stock Items (Atoms)** = Individual labor tasks or material products. Smallest unit. Example: "Bond Pump" (0.343 hrs × $150 = $51.45)
- **Simple Sets (Molecules)** = Pre-built packages that group atoms. Example: "Electrical — Standard Pool" bundles 40 atoms into one sellable package
- **Complex Sets (Organisms)** = Full project packages combining Simple Sets across ALL trades. Example: "New Construction — Standard" = Excavation Set + Steel Set + Shotcrete Set + Plumbing Set + **Electrical Set** + Tile Set + Coping Set + Decking Set + Equipment Set + Interior Set + Startup Set

### The 25 Electrical Simple Sets:

**New Construction:**
1. Standard Pool | 2. Pool + Spa | 3. Full Build (Pool+Spa+WF+Automation)
22. Bonding Only (Rough Phase) | 23. Finish Electrical (Phase 2)

**Add-On/Upgrade:**
4. Outdoor Kitchen | 5. Fire Features | 6. Landscape/Patio
10. Heater Add | 11. Heat Pump Add | 12. Salt System Add
13. Automation Upgrade | 14. Pool Light Upgrade | 15. Pool Light Add
17. Water Feature Add | 18. Misting System | 19. Automatic Pool Cover
20. Solar Heating | 21. Pergola/Outdoor Structure | 25. EV Charger Prep

**Utility (sub-components):**
9. Underground Feed Per LF (parametric) | 7. Panel Upgrade | 16. Standalone Spa | 24. Commercial Pool Base

**Service:**
8. Service/Repair

### Upload Sequence for Simple Sets:

ProDBX has a Simple Set upload template (from "SIMPLE SET BASE" tab in the original file). Format:
- Row 1: Set header (Name, Description, Brochure/URL, Pricebook, Complex Set Group)
- Rows 2+: Stock items referenced by **DBX ID** (column B)

**The DBX IDs don't exist until stock items are imported.** So the upload sequence is:
1. Upload Labor CSV → ProDBX assigns stock IDs
2. Upload Material CSV → ProDBX assigns stock IDs
3. Export stock item list from ProDBX → grab assigned IDs
4. Fill column B (currently red "⚠ FILL") in Simple Sets tab with actual DBX IDs
5. Upload Simple Sets

Every DBX ID cell is flagged RED in the file so Adam can't miss them.

---

## 5. THE PARAMETRIC SET CONCEPT (Underground Feed Per LF)

**Problem:** You don't want 6 separate Simple Sets for 30A, 50A, 60A, 100A, 125A, 150A underground feeds when the only things that change are conduit size, wire gauge, and breaker.

**Solution:** One parametric Simple Set where If/Then rules swap atoms based on an amperage input:

| Amperage | Conduit | Wire | Breaker |
|----------|---------|------|---------|
| ≤30A | 3/4" PVC | #10 AWG | SP-30A |
| 40-50A | 1" PVC | #8 AWG | DP-50A |
| 60A | 1.25" PVC | #6 AWG | DP-60A |
| 80-100A | 1.25" PVC | #4 AWG | DP-100A |
| 125A | 1.5" PVC | #2 AWG | DP-125A |
| 150-200A | 2" PVC | #1/0 AWG | DP-200A |

**Trench and backfill labor are the same regardless of amperage** — the ditch is the same width.

**Pending confirmation with Adam:** Does ProDBX If/Then logic support item substitution within a Simple Set? If yes → Option A (one parametric set). If no → Option B (6 hardcoded sets as fallback). Both options are documented in the Parametric Set Design tab.

---

## 6. NAMING CONVENTION

All items follow: **[Category] — [Action/Type] — [Specifics] — [Qualifier]**

Item codes follow: **[CAT]-[TYPE]-[DETAIL]**

Examples:
- `BOND-PUMP` → Bonding — Bond — Pump
- `CONN-HV-HEATER` → Connection — HV — Gas Heater
- `COND-PVC40-1` → Conduit Install — PVC Sch40 — 1"
- `BRK-GFCI-240` → Breaker Install — GFCI — 240V

This allows calculators to query by prefix (all `BOND-*` items) and APIs to match equipment to connection types programmatically.

---

## 7. THE 12 LABOR CATEGORIES

| Category | Count | Description |
|----------|-------|-------------|
| BONDING | 15 | Equipotential bonding per NEC 680.26 |
| CONNECTION-HV | 27 | High-voltage equipment connections (120-240V) |
| CONNECTION-LV | 22 | Low-voltage control connections |
| CONDUIT | 24 | Conduit installation by type/size/method |
| TRENCHING | 6 | Dig/backfill by method (hand, jackhammer, machine, boulder) |
| WIRE | 5 | Wire pulling and ground conductor runs |
| PANEL | 9 | Sub-panel and disconnect installations |
| BREAKER | 13 | Breaker installations by type/amperage |
| LIGHT | 17 | Niche install, cord pull, jbox, gangbox, receptacle, landscape |
| AUTOMATION | 9 | Panel mount, programming, actuators, sensors, ESO, cover switch |
| SPECIALTY | 10 | Outdoor kitchen, pergola, camera, EV prep, decommission, reno |
| SERVICE | 5 | Diagnostic, troubleshoot, equipment swap, trip charge |

---

## 8. MATERIAL WASTE FACTOR

All material stock items carry `quantity_over=15` in ProDBX (column T in upload template). When a designer enters 80 LF, ProDBX auto-orders 92 LF. This covers:
- Conduit cut waste from 10' sticks
- Wire termination slack at both ends
- Coupling losses at every joint
- Field damage (Tucson caliche/rock = higher conduit breakage)
- Supply-run-avoidance buffer

Industry standard is 10-15% for electrical. We use 15% because of Tucson conditions.

---

## 9. DISTRIBUTOR API SYNC FLAGS

Each material item has a sync flag in its notes:
- **API-SYNC** — Cost should auto-update from Superior Pool Products or Heritage Pool Supply via DistributorConnect. Most conduit, wire, breakers, panels, standard electrical components.
- **MANUAL** — Pool-specific items (NEC 680.24 listed pool jboxes, forming shells, specialty bonding clamps) that distributors may not carry. Maintain costs manually.

When API sync goes live, verify synced items don't overwrite the `quantity_over=15` setting.

---

## 10. COLOR-CODING SYSTEM (Upload Tabs)

| Color | Meaning | Action |
|-------|---------|--------|
| 🔴 RED | STOP — Must fill with data from ProDBX | Cannot upload until filled |
| 🟡 YELLOW | VERIFY — Pre-filled but must match ProDBX exactly | One typo = duplicate category |
| 🟢 GREEN | READY — Correct, don't touch | Leave as-is |
| ⬜ BLANK | Not used for this import | Leave empty |

**Red cells that block upload:**
- Column A (stockid) — if ProDBX doesn't auto-generate
- Column I (phaseid) — needs numeric phase ID from ProDBX
- Column AM (cost) on material tab — estimates need real supplier pricing
- Columns AO/AS/AW (vendorid) on material tab — needs ProDBX vendor ID numbers
- Column B on Simple Set tab — needs DBX IDs after stock item import

---

## 11. REFERENCE FILES USED IN THIS BUILD

| File | What It Is | Location |
|------|-----------|----------|
| `Electrical_Service_Price_Sheet.xlsx` | Original working file with ProDBX templates, test labor list, sub sheets | Aaron's uploads |
| `PRICE_LIST_ELECTRICAL_2023.pdf` | Craig's Electrical Solutions price sheet (2021) — 30+ bundled items for market reference | Aaron's uploads |
| `Price_list.pdf` | Miranda's Pool Plumbing electrical price sheet (July 2022) — 16 bundled items | Aaron's uploads |
| `Electrical_Sub` tab (in original xlsx) | 2015 sub-contractor sheet — 21 items, all flat-rate bundled | Tab in original file |
| Peacock Construction Plan | Real pool plans for validation (34'×9.5', 87' perimeter, 675 SF int surface) | Project knowledge |
| Lee Marvin Construction Plan | Real pool plans for validation (60'×20', 160' perimeter, size-escalated heavy steel) | Project knowledge |

---

## 12. NEXT BUILD: GAS LINE PRICEBOOK

### Same Architecture, Different Trade

The gas line pricebook must follow the identical structure:
1. **Labor atoms** — individual gas tasks (trench per LF, pipe install per LF, pressure test, connection per EA, etc.)
2. **Material atoms** — gas pipe by size/type, fittings, risers, tape, connectors — each with API-SYNC or MANUAL flag
3. **Simple Sets** — packages for typical gas scenarios (standard pool heater run, spa heater, outdoor kitchen gas, fire feature gas, BBQ gas line, etc.)
4. **If/Then rules** — pipe size driven by BTU load and run length (this is where the Gas Line Calculator becomes critical)
5. **ProDBX 82-column upload format** — identical column structure, same margin settings, same color-coding, same failsafe instructions for Adam

### Key Files to Review for Gas Build:

1. **`C:\Users\aaron\Downloads\Gas_Line_Calculator.xlsx`** — This is Aaron's gas line sizing calculator. It starts with the trunk/first leg, then determines subsequent branch line sizes based on BTU load. The logic: total BTU demand + longest run length → trunk size, then each branch sized by its individual BTU load + branch length. This is the gas equivalent of the Underground Feed Per LF parametric set — it should become If/Then logic in ProDBX or feed a calculator that pushes quantities.

2. **`C:\Users\aaron\Downloads\GAS LINE MATERIAL PRICE LIST.xlsx`** — Aaron's spool pricing comparison. Compares cost per foot between 500', 250', and 100' spool purchases to find where bulk buying makes sense. This data feeds directly into the material atom costs in the gas pricebook.

3. **`C:\Users\aaron\Downloads\Electrical_Service_Price_Sheet.xlsx`** — The ProDBX upload template format (tabs: "Master Stock Upload(DO NOT ALTE)" for the 82-column stock item format, "SIMPLE SET BASE" for the Simple Set upload format). Gas pricebook uses the SAME templates.

### Gas-Specific Considerations:

- **Pipe sizing is BTU-driven** — unlike electrical where amperage drives wire gauge, gas pipe sizing is determined by total BTU demand and run length. The Gas Line Calculator encodes this logic. It needs to translate into If/Then rules or a parametric Simple Set.
- **Trunk vs. branch architecture** — the first/trunk line is sized for total BTU, branches are sized for their individual loads. This is a tree structure, not a single run like electrical.
- **Common pipe sizes for Tucson pools:** 3/4" PE (poly), 1" PE, 1-1/4" PE, and potentially larger for commercial or long runs. Corrugated stainless steel tubing (CSST) may also be used.
- **Materials include:** PE gas pipe by size/roll, PE fittings (tees, elbows, couplings, transitions), risers (PE to steel at equipment), gas shutoff valves, Teflon tape/pipe dope, gas pressure test equipment, tracer wire
- **Labor tasks include:** Trench per LF (same as electrical), pipe install per LF (by size), pressure test (per system), connection per equipment (heater, BBQ, fire feature), riser install, leak test, meter/manifold work
- **Inspection coordination** — gas requires pressure test + hold before backfill, then inspection
- **The spool pricing comparison matters** — buying 500' spools vs 100' coils can save 15-30% on material cost. The pricebook should use the optimal spool cost, not retail per-foot pricing

### Automation Intent for Gas Pricebook:

- **Designer workflow:** Select equipment (heater type + BTU, BBQ, fire features), enter approximate run distances. ProDBX calculates pipe sizes per the BTU/length rules, quantities all materials with 15% waste, prices labor per LF, generates PO for pipe and fittings.
- **Zero manual pipe sizing** — the If/Then rules or calculator do it automatically
- **Integrated with electrical** — a pool+spa+heater Complex Set pulls BOTH the electrical Simple Set (heater HV+LV connections) AND the gas Simple Set (gas line run + connection). No double entry.
- **P&L tracking** — same as electrical: estimated gas pipe vs actual used, estimated labor hours vs actual, compare at job close
- **Purchasing integration** — gas materials generate POs to suppliers, track inventory (how many 500' spools on hand?)
- **Mistake catching** — If designer selects a 400K BTU heater but only specs 3/4" pipe on a 60' run, the If/Then rules should flag it or auto-correct the pipe size

---

## 13. PRODBX UPLOAD FORMAT REFERENCE

### Stock Item Upload (82 columns) — Key fields:

| Column | Field | Labor Value | Material Value |
|--------|-------|-------------|----------------|
| A | stockid | Auto or pre-assign | Auto or pre-assign |
| B | active | 1 | 1 |
| D | name | Standardized name | Product name |
| E | price | Labor cost (hrs × $150) | 0 (calculated by margin) |
| G | unit_description | EA, LF, HR | EA, LF |
| H | category | "Electrical - Labor" (or "Gas - Labor") | Per CatDesign taxonomy |
| I | phaseid | Numeric from ProDBX | Numeric from ProDBX |
| J | notes | Description + item code + material pair ref | Description + SYNC flag |
| T | quantity_over | 0 (labor) | 15 (15% waste) |
| Z | fulfillment_method | "none" | "vendor" |
| AB | inventoried_item | 0 | 1 |
| AD | margin | 42 | 42 |
| AE-AL | division margins | 27/27/42/42 by job type | 27/27/42/42 by job type |
| AM | cost | Labor cost (hrs × $150) | Actual supplier cost |
| AO | vendorid | blank | ProDBX vendor ID |
| BB | auto_create_po | 0 | 0 |

### Simple Set Upload — Format:

Row 1 (per set): Headers — Man. Number | DBX ID | Name | Description | Brochure/URL | Pricebook | Complex Set Group
Row 2 (set info): blank | blank | Set Name | Set Description | URL | Pricebook name | Group name
Rows 3+: blank | **DBX ID** (filled after stock import) | Stock Item Name | Qty + Unit + Notes | blank | blank | blank

---

*Summary created April 9, 2026. Save to `C:\Users\aaron\clawd-shared\HANDOFF_Omni_Electrical_PriceBook.md`*
