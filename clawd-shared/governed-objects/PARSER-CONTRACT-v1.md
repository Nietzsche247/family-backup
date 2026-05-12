# Parser Contract v1.0 — Governed Execution Rule

**Effective:** 2026-03-20
**Authority:** Aaron Baker (product rule, not implementation preference)
**Scope:** All parser surfaces in OmniPools Calculator and any future calculator parsers
**Status:** ACTIVE — binding on all agents and all parser-related work

---

## THE LAW: MESSY INPUT, CLEAN CANONICAL STATE

---

### Rule 1: Real-World Messy Input Is Expected

The system MUST tolerate messy pasted or imported data. This is not an edge case — it is the default operating condition.

**Covered parser surfaces:**
- CRM / client info
- Pool / spa dimensions and stats
- Utility / linear-foot measurements
- Mixed abbreviations and variants
- Any future parser domain

**Examples of expected messy input:**
- `lf` / `l.f.` / `linear feet` / `feet` / `ft`
- Pool + spa stats mixed in one blob
- Partial or noisy text with values out of order
- Repeated or contradictory values
- Addresses with missing components
- Phone numbers in any format

---

### Rule 2: Parsers Produce Candidates, Not Sovereign Truth

Parser output is **candidate structured data** that maps into canonical fields.

- Canonical fields are the authoritative state for all downstream reactions
- Parser output populates canonical fields — it does not bypass them
- No downstream module may read directly from raw parser output; it reads canonical state

---

### Rule 3: Manual Correction Is Authoritative

If a human corrects a canonical field:
- Parser re-runs MUST NOT silently overwrite that correction
- Downstream enrichments MUST NOT silently overwrite that correction
- The correction persists until the human explicitly changes it again

**Implementation:** Manual corrections take precedence. Any re-parse or enrichment that would overwrite a manually-corrected field must either skip that field or require explicit user confirmation.

*(This rule is already enforced by DEF-TB-002 fix — commit 8d30b34.)*

---

### Rule 4: Downstream Trigger Rule

A downstream module MUST only activate when its **required canonical inputs are actually present and valid**.

| Condition | Result |
|---|---|
| Required canonical inputs present and valid | Module triggers ✅ |
| Required canonical inputs missing or invalid | Module does NOT trigger ❌ |
| Raw parser text exists but canonical fields not populated | Module does NOT trigger ❌ |
| Some canonical inputs present, some missing | Module does NOT trigger ❌ (unless explicitly designed for partial activation) |

**In plain terms:**
- No required canonical inputs → no trigger
- No partial/vibe trigger
- No pretending data exists because a parser "probably meant it"

---

### Rule 5: Normalization and Inference Rule

Parsers MAY normalize and infer common real-world variants when mapping into canonical fields.

**Permitted normalizations:**
| Messy Input | Canonical Target |
|---|---|
| `lf` / `l.f.` / `linear feet` / `ft` | `linearFeet` (numeric) |
| Pool/spa values in one blob | Split into `pool.*` and `spa.*` canonical fields |
| Noisy address/contact text | Mapped into `street`, `city`, `state`, `zip`, `clientName`, `phone`, `email` |
| Various date formats | ISO 8601 canonical |

**Inference constraints:**
- **Deterministic** where possible (unambiguous mappings)
- **Confidence-aware** where needed (ambiguous mappings carry a confidence score)
- **Safely overrideable** by a human (Rule 3 applies)

---

### Rule 6: Persistence Rule

**Partially enriched parser output MUST be storable and reloadable without being discarded.**

- Missing non-critical parser metadata MUST NOT invalidate meaningful user-facing saved data
- Schema validation MUST distinguish between required user-facing fields and optional parser metadata
- If a stored object has valid user-facing data but is missing auxiliary parser fields, it MUST load successfully

**What this means concretely:**
- `crmData.rawText`, `crmData.parsedAt`, `crmData.confidence` → optional metadata, not load-blocking
- `crmData.address.lat/lng` → may be absent at parse time (geocoding happens later), not load-blocking
- `clientInfoOverrides.street`, `clientInfoOverrides.city` → user-facing data, must persist

*(This rule directly addresses the DEF-TB-003 root cause — schema validation rejecting stored data because non-critical metadata fields were missing.)*

---

### Rule 7: Implementation Specification

For each parser/domain, define:

| Specification | Description |
|---|---|
| **Accepted messy input patterns** | What variants and noise the parser handles |
| **Canonical target fields** | Which canonical state fields the parser populates |
| **Required fields for downstream trigger** | Minimum canonical fields for dependent modules to activate |
| **Optional metadata fields** | Parser metadata that is useful but not required for persistence or downstream |
| **Confidence/uncertainty handling** | How ambiguous parses are scored and surfaced |
| **Manual override behavior** | How Rule 3 is enforced for this domain |
| **Reload/persistence behavior** | How Rule 6 is enforced — what's required vs optional for load validation |

---

## PARSER DOMAIN SPECIFICATIONS

### Domain: CRM / Client Info Parser
**Edge function:** `supabase/functions/parse-crm-notes/index.ts`
**Hook:** `src/hooks/useIntake.ts` → `parseCRM`

| Spec | Definition |
|---|---|
| **Accepted input** | Freeform CRM notes: names, phones, emails, addresses, project notes in any order/format |
| **Canonical target fields** | `clientInfoOverrides.street/city/state/zip`, `clientInfoOverrides.clientName/phone/email`, `crmData.client.*`, `crmData.address.*`, `intake.siteInfoText` |
| **Required for downstream** | `clientInfoOverrides.street` (triggers geocoding); `lat/lng` (triggers site-intelligence) |
| **Optional metadata** | `crmData.rawText`, `crmData.parsedAt`, `crmData.confidence`, `crmData.address.lat/lng` (populated later by geocoder, not parser) |
| **Confidence handling** | Edge function may return confidence per field; low-confidence fields flagged in UI |
| **Manual override** | Rule 3 enforced via `clientInfoOverridesRef` (DEF-TB-002 fix) |
| **Persistence** | Missing optional metadata MUST NOT block `loadIntake()` validation (Rule 6) |

### Domain: Pool / Spa Stats Parser
**Component:** Pool Stats paste area in Intake tab

| Spec | Definition |
|---|---|
| **Accepted input** | Mixed pool + spa dimensions, depths, volumes, surface areas; abbreviations; out-of-order values |
| **Canonical target fields** | `intake.poolStats.*` (pool length/width/depth/volume/surface, spa length/width/depth/volume) |
| **Required for downstream** | Pool dimensions required for hydraulics module activation |
| **Optional metadata** | Raw paste text, parse confidence, extraction method |
| **Confidence handling** | Ambiguous pool-vs-spa splits carry confidence flag |
| **Manual override** | Manual field edits override parsed values |
| **Persistence** | Missing metadata fields MUST NOT block reload |

### Domain: Utility / Linear-Foot Parser
**Component:** Plumbing specs / utility measurements

| Spec | Definition |
|---|---|
| **Accepted input** | `lf`, `l.f.`, `linear feet`, `feet`, `ft`, mixed with pipe sizes, types, and quantities |
| **Canonical target fields** | `intake.plumbingSpecs.*` (pipe runs with length, diameter, type) |
| **Required for downstream** | Pipe specs required for hydraulics TDH calculation |
| **Optional metadata** | Raw paste text, parse confidence |
| **Confidence handling** | Unit normalization is deterministic; quantity extraction may carry confidence |
| **Manual override** | Manual field edits override parsed values |
| **Persistence** | Missing metadata fields MUST NOT block reload |

---

## ENFORCEMENT

- This contract is a **governed execution artifact** — it supersedes implementation convenience
- Any parser change, schema change, or validation change must be reviewed against these rules
- Rule violations are defects, not technical debt
- Pre-commit checklists for parser-related work must include Parser Contract compliance check

---

## CHANGELOG

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-03-20 | Initial contract — established by Aaron as governing product rule |

---

*Contract authored by Aristotle from Aaron's directive | Effective immediately*
