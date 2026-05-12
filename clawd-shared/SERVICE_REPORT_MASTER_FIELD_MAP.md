# OMNI SERVICE REPORT — MASTER FIELD MAP
# Every field used in the Service Report DigiDoc + Email
# Generated: 2026-03-13

------------------------------------------------------------------------------------------------------------------------

NOT YET CREATED — Need to Build in Settings → Customers → Custom Fields  — Placeholder in HTML, needs to be built in ProDBX
#### Pool Profile Fields (set once at project close, rarely changes)

| Field Name | Placeholder | Type | Example |
|---|---|---|---|
| Pool Startup Date | *customer-field-NEW-STARTUP* | Date or Text | "March 2025" |
| Interior Finish Brand | *customer-field-NEW-FINISH* | Dropdown or Text | PebbleTec / PebbleSheen |
| Interior Finish Color | *customer-field-NEW-FINISH-COLOR* | Text | "Midnight Blue" |
| Decking Type | *customer-field-NEW-DECK* | Text | "Artistic Pavers - Ledgestone" |
| Waterline Tile | *customer-field-NEW-TILE* | Text | "6x6 Iridescent Blue" |
| Coping Type | *customer-field-NEW-COPING* | Text | "Travertine Bullnose" |
#### Maintenance Schedule Fields (office updates after each service event)


| Field Name | Placeholder | Type | Notes |
|---|---|---|---|
| Filter Clean — Last Done | *customer-field-NEW-FCLEAN-LAST* | Date or Text | Office updates after service |
| Filter Clean — Next Due | *customer-field-NEW-FCLEAN-NEXT* | Date or Text | Office updates after service |
| Cartridge/Sand Replace — Last | *customer-field-NEW-FREPLACE-LAST* | Date or Text | 2-3 year cycle |
| Cartridge/Sand Replace — Next | *customer-field-NEW-FREPLACE-NEXT* | Date or Text | 2-3 year cycle |
| Salt Cell Wash — Last Done | *customer-field-NEW-SCLEAN-LAST* | Date or Text | 3 month cycle |
| Salt Cell Wash — Next Due | *customer-field-NEW-SCLEAN-NEXT* | Date or Text | 3 month cycle |
| Salt Cell Replace — Last | *customer-field-NEW-SCELL-LAST* | Date or Text | 3-5 year cycle |
| Salt Cell Replace — Next | *customer-field-NEW-SCELL-NEXT* | Date or Text | 3-5 year cycle |
| Water Change — Last Done | *customer-field-NEW-DRAIN-LAST* | Date or Text | 2-5 year cycle |
| Water Change — Next Due | *customer-field-NEW-DRAIN-NEXT* | Date or Text | 2-5 year cycle |
| UV Bulb — Last Done | *customer-field-NEW-UV-LAST* | Date or Text | 12-18 month cycle |
| UV Bulb — Next Due | *customer-field-NEW-UV-NEXT* | Date or Text | 12-18 month cycle |

**Total: 18 customer-level fields still need to be created.**
Once created, replace each `NEW-XXXX` placeholder with the real `*customer-field-NNNN*` ID.
---------------------------------------------------------------------------------------------------------------------


## SECTION: ORDER-LEVEL FIELDS (Maintenance Logs Tab)
### Pre-Existing 

| Field Name | Field ID | Merge Syntax | Type | Report Section |
|---|---|---|---|---|
| Technician | 2146 | ~order-field-2146~ | Dropdown | Visit Details |
| Weather | 2147 | ~order-field-2147~ | Dropdown | Visit Details |
| Free Chlorine | 2148 | ~order-field-2148~ | Number | Water Chemistry |
| pH | 2149 | ~order-field-2149~ | Number | Water Chemistry |
| Total Alkalinity | 2150 | ~order-field-2150~ | Number | Water Chemistry |
| Water Temperature | 2151 | ~order-field-2151~ | Number | Water Chemistry |
| LSI - Calcium Hardness | 2152 | ~order-field-2152~ | Number | LSI Reading |
| LSI - CYA | 2153 | ~order-field-2153~ | Number | LSI Reading |
| LSI - Salt/TDS | 2154 | ~order-field-2154~ | Number | LSI Reading |
| LSI Before | 2155 | ~order-field-2155~ | Number | LSI Reading |
| LSI After | 2156 | ~order-field-2156~ | Number | LSI Reading |
| Chemical Method | 2160 | ~order-field-2160~ | Dropdown | Chemicals Applied |
| Liquid Chlorine | 2157 | ~order-field-2157~ | Number | Chemicals Applied |
| Liquid Chlorine Notes | 2192 | ~order-field-2192~ | Text | Chemicals Applied |
| 3" Tab | 2158 | ~order-field-2158~ | Number | Chemicals Applied |
| 3" Tab Notes | 2193 | ~order-field-2193~ | Text | Chemicals Applied |
| Liquid Acid | 2159 | ~order-field-2159~ | Number | Chemicals Applied |
| Liquid Acid Notes | 2194 | ~order-field-2194~ | Text | Chemicals Applied |
| 1" Tab | 2161 | ~order-field-2161~ | Number | Chemicals Applied |
| 1" Tab Notes | 2195 | ~order-field-2195~ | Text | Chemicals Applied |
| Sodium Bicarbonate | 2162 | ~order-field-2162~ | Number | Chemicals Applied |
| Sodium Bicarbonate Notes | 2196 | ~order-field-2196~ | Text | Chemicals Applied |
| Calcium | 2163 | ~order-field-2163~ | Number | Chemicals Applied |
| Calcium Notes | 2197 | ~order-field-2197~ | Text | Chemicals Applied |
| Other | 2164 | ~order-field-2164~ | Number | Chemicals Applied |
| Other Notes | 2198 | ~order-field-2198~ | Text | Chemicals Applied |
| Algaecide | 2165 | ~order-field-2165~ | Number | Chemicals Applied |
| Algaecide Notes | 2199 | ~order-field-2199~ | Text | Chemicals Applied |
| SC 1000 | 2166 | ~order-field-2166~ | Number | Chemicals Applied |
| SC 1000 Notes | 2200 | ~order-field-2200~ | Text | Chemicals Applied |
| PR 10000 | 2167 | ~order-field-2167~ | Number | Chemicals Applied |
| PR 10000 Notes | 2201 | ~order-field-2201~ | Text | Chemicals Applied |
| CV 600 | 2168 | ~order-field-2168~ | Number | Chemicals Applied |
| CV 600 Notes | 2202 | ~order-field-2202~ | Text | Chemicals Applied |
| Salt | 2169 | ~order-field-2169~ | Number | Chemicals Applied |
| Salt Notes | 2203 | ~order-field-2203~ | Text | Chemicals Applied |
| Skim Surface | 2170 | ~order-field-2170~ | Dropdown | Service Checklist |
| Brush | 2171 | ~order-field-2171~ | Dropdown | Service Checklist |
| Vacuum | 2172 | ~order-field-2172~ | Dropdown | Service Checklist |
| Empty Skimmer Basket(s) | 2173 | ~order-field-2173~ | Dropdown | Service Checklist |
| Empty Pump Basket | 2174 | ~order-field-2174~ | Dropdown | Service Checklist |
| Pre-Filter Cleaned | 2176 | ~order-field-2176~ | Dropdown | Service Checklist |
| Adjust Valves / Returns | 2177 | ~order-field-2177~ | Dropdown | Service Checklist |
| Water Level | 2178 | ~order-field-2178~ | Dropdown | Service Checklist |
| Clean Salt Cell | 2179 | ~order-field-2179~ | Dropdown | Service Checklist |
| Pump | 2180 | ~order-field-2180~ | Dropdown | Equipment Check |
| Filter | 2181 | ~order-field-2181~ | Dropdown | Equipment Check |
| Filter PSI | 2182 | ~order-field-2182~ | Number | Equipment Check |
| Salt System / Chlorinator | 2184 | ~order-field-2184~ | Dropdown | Equipment Check |
| Infloor / Cleaner | 2185 | ~order-field-2185~ | Dropdown | Equipment Check |
| Automation | 2186 | ~order-field-2186~ | Dropdown | Equipment Check |
| Venturi Skimmer & Main Drain | 2187 | ~order-field-2187~ | Dropdown | Equipment Check |
| Issue Needs Addressed? | 2189 | ~order-field-2189~ | Dropdown | Issue Flag |
| Customer Notes (visible) | 2190 | ~order-field-2190~ | Textarea | Customer Notes |
| Office Notes (NOT visible) | 2191 | ~order-field-2191~ | Textarea | HIDDEN |
| Excessive Chemical Usage Noted | 2221 | ~order-field-2221~ | Dropdown | (internal) |

###  Created 2026-03-13
| Field Name | Field ID | Merge Syntax | Type | Options | Visible to Customer? |
|---|---|---|---|---|---|
| Pool Health Score | 2222 | ~order-field-2222~ | Select: Custom | Excellent / Good / Needs Attention / Action Required | YES |
| Seasonal Tip | 2223 | ~order-field-2223~ | Textarea | — | YES |
| Next Visit Preview | 2224 | ~order-field-2224~ | Textarea | — | YES |
| Upsell / Repair Flag | 2229 | ~order-field-2229~ | Select: Custom | None / Minor Repair Needed / Equipment Upgrade Opportunity / Renovation Candidate | NO (hidden) |
| Time On Site (minutes) | 2230 | ~order-field-2230~ | Number | — | NO (hidden) |
| Next Visit Prep (Internal) | 2227 | ~order-field-2227~ | Textarea | — | NO (hidden) |
| How Did This Stop Go? | 2228 | ~order-field-2228~ | Select: Custom | 5—Great / 4—Good / 3—OK / 2—Rough / 1—Bad | NO (hidden) |

---

## SECTION: CUSTOMER-LEVEL FIELDS (Customer Custom Fields)
### Pre-Existing

| Field Name | Field ID | Merge Syntax | Report Section |
|---|---|---|---|
| Pump Model | 1494 | *customer-field-1494* | Installed Equipment |
| Filter Model | 1532 | *customer-field-1532* | Installed Equipment |
| Heater Model | 1533 | *customer-field-1533* | Installed Equipment |
| Salt / Chlorinator | 1539 | *customer-field-1539* | Installed Equipment |
| Automation System | 1544 | *customer-field-1544* | Pool Profile |
| Cleaner | 1549 | *customer-field-1549* | Installed Equipment |
| Lights | 1569 | *customer-field-1569* | Installed Equipment |
| Gallons | 2204 | *customer-field-2204* | Pool Profile + Visit Details |


---

## SECTION: SYSTEM / TEMPLATE MERGE FIELDS
These are built-in ProDBX merge tags (not custom fields):
| Merge Tag | Description | Used In |
|---|---|---|
| *logo* | Company logo image | Header |
| *address* | Job address | Header + Intro |
| *customer-name* | Customer full name | Service Info Bar |
| *customerid* | Customer ID number | Service Info Bar |
| *order-id* | Job/Order number | Service Info Bar |
| *todays-date* | Current date | Visit Details |
| *order-address* | Order address line | Intro paragraph |
| *order-city* | Order city | Intro paragraph |
| *uploaded-docs-type-31* | Photo attachment | Service Photos (5 per category) |

---
## SECTION: PHOTO CATEGORIES
| Category | Slots | Merge Tag |
|---|---|---|
| Before Picture | 5 | *uploaded-docs-type-31* |
| Skimmer Basket | 5 | *uploaded-docs-type-31* |
| Pump Basket | 5 | *uploaded-docs-type-31* |
| After Picture | 5 | *uploaded-docs-type-31* |
| Gate Closed | 5 | *uploaded-docs-type-31* |

---

## SECTION: FILES

| File | Location | Purpose |
|---|---|---|
| service-report-digidoc-v4.4.html | clawd-shared | DigiDoc source (paste into ProDBX) |
| service-report-email-v4.4-full.html | clawd-shared | Client email (all sections, no internal fields) |
| SERVICE_REPORT_FIELD_ID_MAP.md | clawd-shared | Quick-reference ID map (this file replaces it) |
| service-report-field-programming-guide.md | clawd-shared | Original field programming guide |
| service-automation-playbook.md | clawd-shared | Automation triggers and workflows |

---

