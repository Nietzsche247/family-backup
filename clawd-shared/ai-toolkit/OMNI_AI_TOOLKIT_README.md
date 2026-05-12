# OMNI POOL BUILDERS — AI TEMPLATE TOOLKIT
## How to Use These Files

**Company:** Omni Pool Builders & Design LLC, Tucson AZ
**Platform:** ProDBX (CRM/project management)
**Purpose:** Generate branded HTML email templates, DigiDocs, and DiForms

---

## FILES IN THIS TOOLKIT

| File | Purpose | When to Reference |
|------|---------|-------------------|
| `OMNI_DESIGN_SYSTEM.md` | Visual design rules, HTML patterns, CSS | Every template you build |
| `OMNI_FIELD_REFERENCE.md` | All ProDBX merge fields, syntax, field IDs | Every template you build |
| `OMNI_AI_TOOLKIT_README.md` | This file — instructions for AI systems | Read first |

---

## INSTRUCTIONS FOR AI SYSTEMS

You are building HTML templates for ProDBX, a CRM platform used by a premium pool construction and service company in Tucson, Arizona. Templates are pasted into ProDBX's TinyMCE editor via Tools → Source Code.

### THREE TEMPLATE TYPES

**1. DigiDoc (Source Code)**
- The form/document a tech or employee fills out
- Uses `~order-field-XXXX~` (TILDE) syntax for ORDER-LEVEL fields — renders as editable inputs/dropdowns
- Uses `*customer-field-XXXX*` (ASTERISK) syntax for CUSTOMER-LEVEL fields — read-only, auto-populated
- Paste into: Documents → DigiDocs → [doc] → Tools → Source Code

**2. Email Template (what customer receives)**
- What the customer receives after form submission or from an automation
- Uses `*order-field-XXXX*` (ASTERISK) syntax for ALL order fields — renders as READ-ONLY submitted values
- Uses `*customer-field-XXXX*` (ASTERISK) syntax for customer fields — read-only
- ⚠ NEVER use tildes (~) in emails — tildes create editable dropdowns that customers can change!
- Paste into: Settings → Templates → Email Templates → Source Code

**3. DigiForm (tech mobile form)**
- The mobile-friendly form techs fill out in the field
- Field configuration is done in ProDBX UI, not raw HTML
- Understanding field IDs helps configure the form correctly

### CRITICAL SYNTAX RULES — MEMORIZE THIS

```
CONTEXT                        SYNTAX                    EXAMPLE
─────────────────────────────────────────────────────────────────
DigiDoc order fields:          ~order-field-XXXX~        ~order-field-2148~
Email order fields:            *order-field-XXXX*        *order-field-2148*
Customer fields (everywhere):  *customer-field-XXXX*     *customer-field-2204*
System/built-in fields:        *field-name*              *customer-name*
Photo attachments:             *uploaded-docs-type-NN*   *uploaded-docs-type-31*
```

**The # symbol rule:** `~tildes~` = editable (DigiDoc only). `*asterisks*` = read-only (Email + customer fields everywhere).

### WHEN ASKED TO BUILD A TEMPLATE

Follow this sequence:
1. Ask what TYPE (DigiDoc, Email, or both paired)
2. Ask what TRIGGERS it (manual send, automation, form submission, timer)
3. Ask what DATA it needs (reference OMNI_FIELD_REFERENCE.md for available fields)
4. Ask what ACTIONS the recipient should take (call, pay, approve, nothing)
5. Build using the design system patterns from OMNI_DESIGN_SYSTEM.md
6. Use CORRECT merge syntax based on template type (tildes vs asterisks)
7. Include all 5 ROC license numbers in footer for customer-facing templates
8. Include the Consumer Awareness Note if customer-facing
9. Always include the CTA block with office phone 520-222-8503

### AUTOMATION CONTEXT

ProDBX supports these automation triggers — ask about them when designing templates:

| Trigger Type | Example | Template Implications |
|---|---|---|
| Form submitted | Tech completes service log | Auto-send service report email to customer |
| Field value changed | Issue flag set to "Yes" | Escalation email to office + task created |
| Timer/schedule | Every Monday at 8am | Weekly prep email to techs |
| Status changed | Job moves to "Shotcrete" | Milestone notification to customer |
| Date approaching | Filter clean due in 7 days | Maintenance reminder to customer |
| Date passed | Overdue maintenance item | Alert to office + task created |

When building automation-triggered templates, always ask:
- What triggers this email/doc?
- What conditions should filter it? (e.g., only active service customers)
- Who receives it? (Customer, tech, office, sales team?)
- What follow-up actions should happen?
- Should the office get a CC?

### EXAMPLE USE CASES (non-exhaustive)

- Post-service visit email to customer (already built — see service-report-email-v4.4-full.html)
- Construction milestone notification ("Shotcrete is scheduled for Tuesday!")
- Equipment repair estimate / approval request
- Monthly service summary digest
- Welcome letter for new service customer
- Seasonal maintenance reminder
- Filter clean / salt cell service due reminder
- Warranty claim acknowledgment
- Invoice / payment reminder
- Referral request after positive service rating
- New construction progress update (phase by phase)
- Pre-visit prep summary for tech (internal)
- Issue escalation alert (internal)
- Chemical usage report (internal, weekly)

---

## COMPANY INFORMATION (for headers, footers, compliance blocks)

**Legal Name:** Omni Pool Builders & Design LLC
**Address:** 6640 N. Oracle Rd. Suite 130, Tucson, AZ 85704
**Phone:** (520) 222-8503
**Website:** tucsonpoolbuilders.com

**Licenses (ALL must appear in customer-facing footers):**
- ROC #282151: KA-5 Commercial/Residential Pool Contractor
- ROC #326882: CR-21 Hardscaping/Masonry
- ROC #350879: CR-37 Ramada, Pergola & Canopies
- ROC #353526: CR-14 Fencing
- ROC #339947: CR-37 Gas Lines/Plumbing

**Consumer Awareness Note (required on customer-facing templates):**
"Unlicensed work may lack insurance, risking your protection. We're authorized by the Arizona Registrar of Contractors for all listed work, ensuring compliance and full coverage."

**Tagline:** "We built your pool. We maintain your pool. That's the Omni difference."
