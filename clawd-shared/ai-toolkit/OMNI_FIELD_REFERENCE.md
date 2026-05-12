# OMNI POOL BUILDERS — ProDBX FIELD REFERENCE
## Every Merge Field Available for Templates

---

## SYNTAX QUICK REFERENCE

| Context | Syntax | Example | Renders As |
|---------|--------|---------|------------|
| DigiDoc — order field | `~order-field-XXXX~` | `~order-field-2148~` | Editable dropdown/input |
| Email — order field | `*order-field-XXXX*` | `*order-field-2148*` | Read-only submitted value |
| Customer field (everywhere) | `*customer-field-XXXX*` | `*customer-field-2204*` | Read-only profile value |
| System field (everywhere) | `*field-name*` | `*customer-name*` | Read-only system value |
| Photo attachment | `*uploaded-docs-type-NN*` | `*uploaded-docs-type-31*` | Attached image |

**CRITICAL:** Never use tildes (~) in email templates. Tildes = editable. Asterisks = read-only.

---

## SECTION 1: SYSTEM / BUILT-IN MERGE FIELDS

These are ProDBX system fields — no custom field ID needed.

| Merge Tag | Description | Typical Usage |
|-----------|-------------|---------------|
| `*logo*` | Company logo image | Header |
| `*address*` | Job/order address | Header, intro |
| `*customer-name*` | Customer full name | Greeting, info bar |
| `*first-name*` | Customer first name | Personalized greetings |
| `*last-name*` | Customer last name | Formal references |
| `*customerid*` | Customer ID number | Reference numbers |
| `*order-id*` | Job/Order number | Reference numbers |
| `*todays-date*` | Current date | Visit details, timestamps |
| `*order-address*` | Order street address | Subject lines, intros |
| `*order-city*` | Order city | Subject lines, intros |
| `*order-date*` | Order creation date | Proposals, contracts |
| `*order-grand-total*` | Total amount | Proposals, invoices |
| `*balance-due*` | Balance amount | Payment reminders |
| `*order-salesrep*` | Sales rep name | Proposals, assignments |
| `*quote-expiration-date*` | Quote expiry | Proposals |
| `*order-items-table*` | Auto-generated line items | Proposals, invoices |
| `*order-drawings*` | Uploaded design drawings | Proposals |
| `*owner-photo*` | Rep headshot | Proposals |
| `*owner-cell-phone*` | Rep cell phone | Contact cards |
| `*owner-email*` | Rep email | Contact cards |
| `*pay-deposit-now-button*` | Payment button | Proposals |
| `*pay-balance-due-now-button*` | Balance payment button | Invoices |
| `*progress-payment-table*` | Payment schedule | Contracts |
| `*uploaded-docs-type-31*` | Photo attachment (type 31) | Service photos |

---

## SECTION 2: ORDER-LEVEL CUSTOM FIELDS (Maintenance Logs Tab)

These live on individual jobs/orders. Techs fill them in per service visit.

### Visit Details
| Field Name | ID | DigiDoc Syntax | Email Syntax | Type |
|---|---|---|---|---|
| Technician | 2146 | `~order-field-2146~` | `*order-field-2146*` | Dropdown |
| Weather | 2147 | `~order-field-2147~` | `*order-field-2147*` | Dropdown |

### Water Chemistry (Weekly)
| Field Name | ID | DigiDoc Syntax | Email Syntax | Type |
|---|---|---|---|---|
| Free Chlorine | 2148 | `~order-field-2148~` | `*order-field-2148*` | Number |
| pH | 2149 | `~order-field-2149~` | `*order-field-2149*` | Number |
| Total Alkalinity | 2150 | `~order-field-2150~` | `*order-field-2150*` | Number |
| Water Temperature | 2151 | `~order-field-2151~` | `*order-field-2151*` | Number |

### LSI Reading (Monthly)
| Field Name | ID | DigiDoc Syntax | Email Syntax | Type |
|---|---|---|---|---|
| Calcium Hardness | 2152 | `~order-field-2152~` | `*order-field-2152*` | Number |
| CYA (Stabilizer) | 2153 | `~order-field-2153~` | `*order-field-2153*` | Number |
| Salt / TDS | 2154 | `~order-field-2154~` | `*order-field-2154*` | Number |
| LSI Before Service | 2155 | `~order-field-2155~` | `*order-field-2155*` | Number |
| LSI After Service | 2156 | `~order-field-2156~` | `*order-field-2156*` | Number |

### Chemicals Applied
| Field Name | ID | DigiDoc Syntax | Email Syntax | Type | Unit |
|---|---|---|---|---|---|
| Chemical Method | 2160 | `~order-field-2160~` | `*order-field-2160*` | Dropdown | — |
| Liquid Chlorine | 2157 | `~order-field-2157~` | `*order-field-2157*` | Number | GAL |
| Liquid Chlorine Notes | 2192 | `~order-field-2192~` | `*order-field-2192*` | Text | — |
| 3" Tab | 2158 | `~order-field-2158~` | `*order-field-2158*` | Number | EA |
| 3" Tab Notes | 2193 | `~order-field-2193~` | `*order-field-2193*` | Text | — |
| Liquid Acid | 2159 | `~order-field-2159~` | `*order-field-2159*` | Number | GAL |
| Liquid Acid Notes | 2194 | `~order-field-2194~` | `*order-field-2194*` | Text | — |
| 1" Tab | 2161 | `~order-field-2161~` | `*order-field-2161*` | Number | EA |
| 1" Tab Notes | 2195 | `~order-field-2195~` | `*order-field-2195*` | Text | — |
| Sodium Bicarbonate | 2162 | `~order-field-2162~` | `*order-field-2162*` | Number | LBS |
| Sodium Bicarbonate Notes | 2196 | `~order-field-2196~` | `*order-field-2196*` | Text | — |
| Calcium | 2163 | `~order-field-2163~` | `*order-field-2163*` | Number | LBS |
| Calcium Notes | 2197 | `~order-field-2197~` | `*order-field-2197*` | Text | — |
| Other | 2164 | `~order-field-2164~` | `*order-field-2164*` | Number | — |
| Other Notes | 2198 | `~order-field-2198~` | `*order-field-2198*` | Text | — |
| Algaecide | 2165 | `~order-field-2165~` | `*order-field-2165*` | Number | OZ |
| Algaecide Notes | 2199 | `~order-field-2199~` | `*order-field-2199*` | Text | — |
| SC-1000 (Calcium Chelating) | 2166 | `~order-field-2166~` | `*order-field-2166*` | Number | OZ |
| SC-1000 Notes | 2200 | `~order-field-2200~` | `*order-field-2200*` | Text | — |
| PR-10000 (Phosphate Remover) | 2167 | `~order-field-2167~` | `*order-field-2167*` | Number | OZ |
| PR-10000 Notes | 2201 | `~order-field-2201~` | `*order-field-2201*` | Text | — |
| CV-600 (Enzyme Cleaner) | 2168 | `~order-field-2168~` | `*order-field-2168*` | Number | OZ |
| CV-600 Notes | 2202 | `~order-field-2202~` | `*order-field-2202*` | Text | — |
| Salt | 2169 | `~order-field-2169~` | `*order-field-2169*` | Number | BAG |
| Salt Notes | 2203 | `~order-field-2203~` | `*order-field-2203*` | Text | — |

### Service Checklist
| Field Name | ID | DigiDoc Syntax | Email Syntax | Type |
|---|---|---|---|---|
| Skim Surface | 2170 | `~order-field-2170~` | `*order-field-2170*` | Dropdown |
| Brush (walls/steps/tile) | 2171 | `~order-field-2171~` | `*order-field-2171*` | Dropdown |
| Vacuum | 2172 | `~order-field-2172~` | `*order-field-2172*` | Dropdown |
| Empty Skimmer Basket(s) | 2173 | `~order-field-2173~` | `*order-field-2173*` | Dropdown |
| Empty Pump Basket | 2174 | `~order-field-2174~` | `*order-field-2174*` | Dropdown |
| Pre-Filter Cleaned | 2176 | `~order-field-2176~` | `*order-field-2176*` | Dropdown |
| Adjust Valves / Returns | 2177 | `~order-field-2177~` | `*order-field-2177*` | Dropdown |
| Water Level | 2178 | `~order-field-2178~` | `*order-field-2178*` | Dropdown |
| Clean Salt Cell | 2179 | `~order-field-2179~` | `*order-field-2179*` | Dropdown |

### Equipment Check
| Field Name | ID | DigiDoc Syntax | Email Syntax | Type |
|---|---|---|---|---|
| Pump | 2180 | `~order-field-2180~` | `*order-field-2180*` | Dropdown |
| Filter | 2181 | `~order-field-2181~` | `*order-field-2181*` | Dropdown |
| Filter PSI | 2182 | `~order-field-2182~` | `*order-field-2182*` | Number |
| Salt System / Chlorinator | 2184 | `~order-field-2184~` | `*order-field-2184*` | Dropdown |
| Infloor / Cleaner | 2185 | `~order-field-2185~` | `*order-field-2185*` | Dropdown |
| Automation | 2186 | `~order-field-2186~` | `*order-field-2186*` | Dropdown |
| Venturi Skimmer & Main Drain | 2187 | `~order-field-2187~` | `*order-field-2187*` | Dropdown |

### Issue / Notes
| Field Name | ID | DigiDoc Syntax | Email Syntax | Type | Customer Sees? |
|---|---|---|---|---|---|
| Issue Needs Addressed? | 2189 | `~order-field-2189~` | `*order-field-2189*` | Dropdown | YES |
| Customer Notes (visible) | 2190 | `~order-field-2190~` | `*order-field-2190*` | Textarea | YES |
| Office Notes (NOT visible) | 2191 | `~order-field-2191~` | — | Textarea | NO — HIDDEN |
| Excessive Chemical Usage | 2221 | `~order-field-2221~` | — | Dropdown | NO — HIDDEN |

### AI-Driven Fields (created 2026-03-13)
| Field Name | ID | DigiDoc Syntax | Email Syntax | Type | Options | Customer Sees? |
|---|---|---|---|---|---|---|
| Pool Health Score | 2222 | `~order-field-2222~` | `*order-field-2222*` | Select: Custom | Excellent / Good / Needs Attention / Action Required | YES |
| Seasonal Tip | 2223 | `~order-field-2223~` | `*order-field-2223*` | Textarea | — | YES |
| Next Visit Preview | 2224 | `~order-field-2224~` | `*order-field-2224*` | Textarea | — | YES |
| Upsell / Repair Flag | 2229 | `~order-field-2229~` | — | Select: Custom | None / Minor Repair Needed / Equipment Upgrade Opportunity / Renovation Candidate | NO — HIDDEN |
| Time On Site (minutes) | 2230 | `~order-field-2230~` | — | Number | — | NO — HIDDEN |
| Next Visit Prep (Internal) | 2227 | `~order-field-2227~` | — | Textarea | — | NO — HIDDEN |
| How Did This Stop Go? | 2228 | `~order-field-2228~` | — | Select: Custom | 5—Great / 4—Good / 3—OK / 2—Rough / 1—Bad | NO — HIDDEN |

---

## SECTION 3: CUSTOMER-LEVEL CUSTOM FIELDS

These live on the customer record, persist across all jobs. Set once, auto-populate on every template.

### Pre-Existing Equipment Fields
| Field Name | ID | Merge Syntax | Section |
|---|---|---|---|
| Pump Model | 1494 | `*customer-field-1494*` | Installed Equipment |
| Filter Model | 1532 | `*customer-field-1532*` | Installed Equipment |
| Heater Model | 1533 | `*customer-field-1533*` | Installed Equipment |
| Salt / Chlorinator | 1539 | `*customer-field-1539*` | Installed Equipment |
| Automation System | 1544 | `*customer-field-1544*` | Pool Profile |
| Cleaner | 1549 | `*customer-field-1549*` | Installed Equipment |
| Lights | 1569 | `*customer-field-1569*` | Installed Equipment |
| Gallons | 2204 | `*customer-field-2204*` | Pool Profile + Visit Details |

### Pool Profile Fields (created 2026-03-13)
| Field Name | ID | Merge Syntax | Type | Example |
|---|---|---|---|---|
| Pool Startup Date | 2232 | `*customer-field-2232*` | Text | "March 2025" |
| Interior Finish Brand | 2233 | `*customer-field-2233*` | Text | "PebbleTec" |
| Interior Finish Color | 2234 | `*customer-field-2234*` | Text | "Midnight Blue" |
| Decking Type | 2235 | `*customer-field-2235*` | Text | "Artistic Pavers" |
| Waterline Tile | 2236 | `*customer-field-2236*` | Text | "6x6 Iridescent Blue" |
| Coping Type | 2237 | `*customer-field-2237*` | Text | "Travertine Bullnose" |

### Maintenance Schedule Fields (created 2026-03-13)
| Field Name | ID | Merge Syntax | Type | Cycle |
|---|---|---|---|---|
| Filter Clean — Last Done | 2238 | `*customer-field-2238*` | Text | 3–4 months |
| Filter Clean — Next Due | 2239 | `*customer-field-2239*` | Text | 3–4 months |
| Cartridge Replace — Last | 2240 | `*customer-field-2240*` | Text | 2–3 years |
| Cartridge Replace — Next | 2241 | `*customer-field-2241*` | Text | 2–3 years |
| Salt Cell Wash — Last | 2242 | `*customer-field-2242*` | Text | 3 months |
| Salt Cell Wash — Next | 2243 | `*customer-field-2243*` | Text | 3 months |
| Salt Cell Replace — Last | 2244 | `*customer-field-2244*` | Text | 3–5 years |
| Salt Cell Replace — Next | 2245 | `*customer-field-2245*` | Text | 3–5 years |
| Water Change — Last | 2246 | `*customer-field-2246*` | Text | 2–5 years |
| Water Change — Next | 2247 | `*customer-field-2247*` | Text | 2–5 years |
| UV Bulb — Last | 2248 | `*customer-field-2248*` | Text | 12–18 months |
| UV Bulb — Next | 2249 | `*customer-field-2249*` | Text | 12–18 months |

---

## SECTION 4: CONSTRUCTION / PROPOSAL FIELDS

These are used in estimates, proposals, and contracts — not service reports.

### Pool Measurements (Order-Level)
| Field Name | ID | Merge Syntax |
|---|---|---|
| Pool Length | 1484 | `*order-field-1484*` |
| Pool Width | 1485 | `*order-field-1485*` |
| Pool Area | 2084 | `*order-field-2084*` |
| Pool Perimeter | 1441 | `*order-field-1441*` |
| Shallow Depth | 1443 | `*order-field-1443*` |
| Deep Depth | 1445 | `*order-field-1445*` |
| Gallons | 2081 | `*order-field-2081*` |
| Jurisdiction | 1459 | `*order-field-1459*` |
| Construction Access | 2080 | `*order-field-2080*` |

---

## SECTION 5: PHOTO UPLOAD REFERENCE

Service report uses upload type 31 with 5 slots per category.

| Category | Merge Tags (5 per row) |
|---|---|
| Before Picture | `*uploaded-docs-type-31*` × 5 |
| Skimmer Basket | `*uploaded-docs-type-31*` × 5 |
| Pump Basket | `*uploaded-docs-type-31*` × 5 |
| After Picture | `*uploaded-docs-type-31*` × 5 |
| Gate Closed | `*uploaded-docs-type-31*` × 5 |

**Note:** Whether multiple identical type-31 tags render sequentially or duplicate the same photo needs to be confirmed with ProDBX support. This matches the current working production email.

---

*Field Reference v1.0 — March 2026*
*Last updated: 2026-03-18*
*Omni Pool Builders & Design LLC*
