# DEF-TB-003 — Intake State Collapses to Defaults on Page Reload

| Field | Value |
|---|---|
| **defect_id** | DEF-TB-003 |
| **track** | B |
| **title** | Intake state collapses to defaults on page reload despite localStorage persistence |
| **reported_by** | Empiricus |
| **owner** | Plato |
| **status** | **CLOSED / FIX-VERIFIED** |
| **severity** | Medium-High |
| **closed_date** | 2026-03-20 |

## Description
After populating intake fields (CRM parse + manual corrections), reloading the page caused all intake fields to reset to blank defaults. localStorage keys existed but `loadIntake()` rejected stored data during schema validation because non-critical parser metadata fields were missing.

## Root Cause
`src/lib/intake/schema.ts` — Zod schema required fields that the CRM parser edge function doesn't always populate:
- `crmData.address.lat/lng` (populated later by geocoder, not at parse time)
- `crmData.rawText`, `crmData.parsedAt`, `crmData.confidence` (parser metadata not returned by edge function)

Schema validation rejected the stored data → `loadIntake()` returned null → factory defaults loaded → cross-page sync overwrote real data.

## Fix (Two Commits)

### v1: Cross-page sync guard (commit cb93aed)
- Added `hydrationSourceRef` tracking ('storage' | 'default' | 'user')
- Gated cross-page sync against factory-default state
- Added diagnostic logging to all 5 `loadIntake()` null-return branches
- **Correct but insufficient alone** — prevented symptom propagation but didn't fix root cause

### v2: Schema validation fix (commit a059078)
- Made 5 non-critical CRM metadata fields `.optional()` in Zod schema
- `AddressSchema`: `lat`, `lng` → optional
- `CRMDataSchema`: `rawText`, `parsedAt`, `confidence` → optional
- **+11/-5 lines in schema.ts only**
- Grounded in Parser + Trigger Contract v2.1 Rule 8 (Persistence Law)

## Verification Chain
| Step | Agent | Result | Date |
|---|---|---|---|
| Characterization | Daedalus | Root cause: initialization guard-gap + schema mismatch | 2026-03-20 |
| Fix brief v1 (cross-page guard) | Aristotle | Implemented by Plato (cb93aed) | 2026-03-20 |
| v1 validation | Empiricus | Core fix insufficient — reload still failed, but diagnostics revealed schema mismatch | 2026-03-20 |
| Parser + Trigger Contract v2.1 | Aaron/Aristotle | Rule 8 established: missing metadata must not invalidate stored data | 2026-03-20 |
| Fix brief v2 (schema fix) | Aristotle | Targeted schema.ts | 2026-03-20 |
| Implementation | Plato | Commit a059078 | 2026-03-20 |
| Code review | Daedalus | APPROVED — all checklist items pass | 2026-03-20 |
| Production deploy | Aaron (Lovable publish) | Deployed (bundle index-ClHu5VKP.js) | 2026-03-20 |
| Post-deploy validation | Empiricus | ALL 12 STEPS PASS | 2026-03-20 |

## Notes
- Minor display oddity noted: Site Intelligence address renders as composite string with duplicate city/state. This is cosmetic and likely related to address assembly in `selectResolvedLocation` — DEF-TB-001 territory, not TB-003.
- New bundle hash confirmed: `index-ClHu5VKP.js`

## Related Artifacts
- `governed-objects/DEF-TB-003-CHARACTERIZATION.md`
- `governed-objects/DEF-TB-003-FIX-BRIEF.md` (v1)
- `governed-objects/DEF-TB-003-FIX-BRIEF-v2.md`
- `governed-objects/DEF-TB-003-v2-CODE-REVIEW.md`
- `governed-objects/PARSER-TRIGGER-CONTRACT-v2.md` (Rule 8)
