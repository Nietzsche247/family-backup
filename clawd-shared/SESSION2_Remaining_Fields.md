# SESSION 2: Remaining Field Programming
## Service Report v4.3 — Only What's Left

**Date:** March 11, 2026  
**Platform:** ProDBX at `login.prodbx.com`

---

## WHAT'S DONE

Previous session created some order-level fields on the DigiForm. The existing customer equipment fields (1494, 1528, 1532, 1533, 1539, 1544, 1549, 1565, 1569, 2204) have been mapped to the template — no need to create those.

## WHAT'S LEFT

### TASK 1: Verify Order-Level Fields (DigiForm → Form Fields → Digiform tab)

Check if these 7 fields were created in the previous session. If they exist, record their field IDs. If any are missing, create them.

| Field | Type | Dropdown Options |
|-------|------|-----------------|
| Pool Health Score | Select: Custom | Excellent / Good / Needs Attention / Action Required |
| Seasonal Tip | Text Area | (no dropdown) |
| Next Visit Preview | Text Area | (no dropdown) |
| Upsell / Repair Flag | Select: Custom | None / Minor Repair Needed / Equipment Upgrade Opportunity / Renovation Candidate |
| Time On Site (minutes) | Number | (no dropdown) |
| Next Visit Prep (Internal) | Text Area | (no dropdown) |
| How Did This Stop Go? | Select: Custom | 5 — Great / 4 — Good / 3 — OK / 2 — Rough / 1 — Bad |

The last 4 (Upsell through Self-Rating) need to be added to Settings → Hidden Fields tab after creation.

### TASK 2: Create Customer-Level Fields

Navigate to a customer record → find the Equipment List/Pool Info section where fields like 1494 (Pump Model & Type) already exist. Look for a way to ADD new custom fields there. If you can't find it on the customer record, check Settings or Admin for "Custom Fields" management.

Create these 18 customer-level fields:

**Profile fields (6) — all Text type:**

| Label |
|-------|
| Pool Startup Date |
| Interior Finish Brand |
| Interior Finish Color |
| Decking Type |
| Waterline Tile |
| Coping Type |

**Maintenance schedule fields (12) — all Text type:**

| Label |
|-------|
| Filter Clean — Last Done |
| Filter Clean — Next Due |
| Cartridge/Sand Replace — Last Done |
| Cartridge/Sand Replace — Next Due |
| Salt Cell Clean — Last Done |
| Salt Cell Clean — Next Due |
| Salt Cell Replace — Last Done |
| Salt Cell Replace — Next Due |
| Water Change — Last Done |
| Water Change — Next Due |
| UV Bulb Replace — Last Done |
| UV Bulb Replace — Next Due |

If ProDBX has a tab/group selector, put Profile fields under "Equipment List/Pool Info" and Maintenance fields under "Maintenance Logs" (or create a new group if possible).

### TASK 3: Save the Complete Field ID Map

Save to `C:\Users\aaron\clawd-shared\SERVICE_REPORT_FIELD_ID_MAP.md` in this format:

```
# SERVICE REPORT FIELD ID MAP
## Created March 11, 2026

### ORDER-LEVEL FIELDS (on DigiForm)
~order-field-NEW-SCORE~        → ~order-field-____~
~order-field-NEW-SEASON-TIP~   → ~order-field-____~
~order-field-NEW-NEXT-VISIT~   → ~order-field-____~
~order-field-NEW-UPSELL~       → ~order-field-____~
~order-field-NEW-TIME~         → ~order-field-____~
~order-field-NEW-PREP~         → ~order-field-____~
~order-field-NEW-RATING~       → ~order-field-____~

### CUSTOMER-LEVEL FIELDS
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

Fill in each ____ with the real numeric ID as you create or find each field.

---

## NOTES
- Order field syntax: `~order-field-XXXX~` (tildes)
- Customer field syntax: `*customer-field-XXXX*` (asterisks)
- If you can't create customer fields from the UI, stop and tell Aaron — may need ProDBX support
- Priority: Task 1 first (verify order fields), then Task 2 (customer fields), then Task 3 (save map)
