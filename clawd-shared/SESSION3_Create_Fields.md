# SESSION 3: Create Remaining Fields
## Omni Pool Service Report — Pick Up Where Session 2 Left Off

**Date:** March 11, 2026  
**Platform:** ProDBX at `login.prodbx.com`  
**Status:** Audit complete, creation needed

---

## WHAT'S ALREADY DONE

- All existing order fields (2146-2203) confirmed working
- All existing customer fields (1494, 1532, 1533, 1539, 1544, 1549, 1569, 2204) confirmed working
- **Field 2222 = Pool Health Score** — already created in session 1. Use this ID.

## WHAT TO CREATE NOW

### ORDER-LEVEL FIELDS (6 remaining — create on DigiForm → Edit → Form Fields → Digiform tab)

Use "Select: Custom" for dropdowns. Tab Location: "Maintenance Logs" (ID 2145).

| # | Label | Type | Dropdown Options (one per line) |
|---|-------|------|---------------------------------|
| 1 | Seasonal Tip | Text Area | (none) |
| 2 | Next Visit Preview | Text Area | (none) |
| 3 | Upsell / Repair Flag | Select: Custom | None / Minor Repair Needed / Equipment Upgrade Opportunity / Renovation Candidate |
| 4 | Time On Site (minutes) | Number | (none) |
| 5 | Next Visit Prep (Internal) | Text Area | (none) |
| 6 | How Did This Stop Go? | Select: Custom | 5 — Great / 4 — Good / 3 — OK / 2 — Rough / 1 — Bad |

**After creating fields 3-6:** Go to Settings → Hidden Fields and add them there so they don't show on the customer report.

### CUSTOMER-LEVEL FIELDS (18 — create on customer record → Equipment List/Pool Info area)

Navigate to Customers → open any customer → find where fields like 1494 (Pump Model & Type) live → look for Add Field / Edit Fields / gear icon. All 18 are **Text** type.

**Profile (6):**
1. Pool Startup Date
2. Interior Finish Brand
3. Interior Finish Color
4. Decking Type
5. Waterline Tile
6. Coping Type

**Maintenance Schedule (12):**
7. Filter Clean — Last Done
8. Filter Clean — Next Due
9. Cartridge/Sand Replace — Last Done
10. Cartridge/Sand Replace — Next Due
11. Salt Cell Clean — Last Done
12. Salt Cell Clean — Next Due
13. Salt Cell Replace — Last Done
14. Salt Cell Replace — Next Due
15. Water Change — Last Done
16. Water Change — Next Due
17. UV Bulb Replace — Last Done
18. UV Bulb Replace — Next Due

If you can't find where to create customer fields, stop and ask Aaron.

## WHEN DONE: SAVE THE ID MAP

Save to `C:\Users\aaron\clawd-shared\SERVICE_REPORT_FIELD_ID_MAP.md`:

```
# SERVICE REPORT FIELD ID MAP — March 11, 2026

## ORDER-LEVEL FIELDS
~order-field-NEW-SCORE~        → ~order-field-2222~
~order-field-NEW-SEASON-TIP~   → ~order-field-____~
~order-field-NEW-NEXT-VISIT~   → ~order-field-____~
~order-field-NEW-UPSELL~       → ~order-field-____~
~order-field-NEW-TIME~         → ~order-field-____~
~order-field-NEW-PREP~         → ~order-field-____~
~order-field-NEW-RATING~       → ~order-field-____~

## CUSTOMER-LEVEL FIELDS
*customer-field-NEW-STARTUP*        → *customer-field-____*
*customer-field-NEW-FINISH*         → *customer-field-____*
*customer-field-NEW-FINISH-COLOR*   → *customer-field-____*
*customer-field-NEW-DECK*           → *customer-field-____*
*customer-field-NEW-TILE*           → *customer-field-____*
*customer-field-NEW-COPING*         → *customer-field-____*
*customer-field-NEW-FCLEAN-LAST*    → *customer-field-____*
*customer-field-NEW-FCLEAN-NEXT*    → *customer-field-____*
*customer-field-NEW-FREPLACE-LAST*  → *customer-field-____*
*customer-field-NEW-FREPLACE-NEXT*  → *customer-field-____*
*customer-field-NEW-SCLEAN-LAST*    → *customer-field-____*
*customer-field-NEW-SCLEAN-NEXT*    → *customer-field-____*
*customer-field-NEW-SCELL-LAST*     → *customer-field-____*
*customer-field-NEW-SCELL-NEXT*     → *customer-field-____*
*customer-field-NEW-DRAIN-LAST*     → *customer-field-____*
*customer-field-NEW-DRAIN-NEXT*     → *customer-field-____*
*customer-field-NEW-UV-LAST*        → *customer-field-____*
*customer-field-NEW-UV-NEXT*        → *customer-field-____*
```

Fill in each ____ with the real ID as you create each field. The SCORE line is already filled (2222).
