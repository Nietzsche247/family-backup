# Parser + Trigger Contract v2.0 — Governing Product Rule

**Effective:** 2026-03-20
**Authority:** Aaron Baker — governing product rule, not implementation preference
**Supersedes:** Parser Contract v1.0
**Scope:** All parser surfaces, module triggers, and cascade behavior in OmniPools Calculator
**Status:** ACTIVE — binding on all agents and all parser/module work

---

## THE SHORT FORM

**Messy input is fine. Clean canonical state is required. If the next module did not actually receive the required canonical fields, it does not turn on.**

---

## PART I: PARSER RULES

### Rule 1: Messy Input Is Expected

All parsers MUST tolerate messy, real-world input and infer what they can from it. This is not an edge case — it is the default operating condition.

**Examples of expected messy input:**
| Parser | Messy Input Examples |
|---|---|
| CRM/Client (P1) | Address/name/phone/email mixed in one blob, partial data, noisy formatting |
| Pool/Spa Stats (P4) | Pool + spa stats in one pasted block, values out of order, duplicated, contradictory |
| Utility/Plumbing (P6) | `lf` / `l.f.` / `linear feet` / `feet` / `ft`, mixed pipe sizes and types |
| Equipment (P5) | Cut sheets, electrical blocks, mixed model numbers and specs |
| Panel Photos (P3) | Blurry photos, partial labels, rotated images |

### Rule 2: Parser Output Is Candidate Data

Parser output is **candidate structured data** that maps into canonical fields.

- Parsers extract and normalize candidate values
- Downstream modules only trust **canonical mapped fields**
- Raw text is not authoritative
- Parser candidates are not authoritative
- Canonical fields are the **only thing** downstream modules are allowed to wake up from

### Rule 3: Manual Correction Is Authoritative

If a designer manually corrects a canonical field:
- Parser re-runs MUST NOT silently overwrite that correction
- Downstream enrichments MUST NOT silently overwrite that correction
- The correction persists until the designer explicitly changes it again

*(Enforced by DEF-TB-002 fix — commit 8d30b34, useRef pattern in parseCRM)*

---

## PART II: TRIGGER RULES

### Rule 4: Trigger Law — Multi-Path Entry

A module may be triggered from **more than one upstream path**.

```
A ──→ C
B ──→ C
```

If C's required canonical inputs are present and valid, C may run **regardless of which upstream path produced them.**

**Concrete example:**
- Site Intelligence (M:SI) requires `lat/lng`
- Path A: CRM paste → geocode → lat/lng → SI triggers
- Path B: User enters lat/lng manually on module page → SI triggers
- Both are valid. SI doesn't care which path populated its inputs.

### Rule 5: No Required Canonical Inputs → No Trigger

If the next module did not actually receive the canonical fields it depends on, **it does not turn on.**

| Condition | Result |
|---|---|
| Required canonical inputs present and valid | Module triggers ✅ |
| Required canonical inputs missing or invalid | Module does NOT trigger ❌ |
| Raw text exists but canonical fields not populated | Module does NOT trigger ❌ |
| "Probably enough" data | Module does NOT trigger ❌ |
| Partial/vibe trigger | **FORBIDDEN** ❌ |

**No exceptions.** No "probably enough." No text-exists-therefore-trigger. No partial/vibe trigger.

### Rule 6: Cascade Law — Domino Triggers

If module C successfully resolves its required inputs and produces valid canonical outputs, it MAY wake downstream modules in a domino chain.

```
A ──→ C ──→ Z
           ──→ R
```

**But each downstream module must still obey its own required-input gate.**

- C completing does not automatically mean Z runs
- Z runs only if C's outputs satisfy Z's required canonical inputs
- Each module in the chain independently validates its own inputs

### Rule 7: Multi-Entry Architecture

A module can be reached either:
- From the primary **Intake page** (upstream data flows in)
- **Directly** from the module's own page (user enters data there)

If the user enters enough valid canonical data directly on the module page, that module MUST be able to run **without requiring the whole upstream chain.**

```
Intake → Parser → Geocode → Site Intel → Module    (full chain)
                                         Module    (direct entry with valid inputs)
```

Both are valid paths. Modules are not gatekept by "did you come through Intake."

---

## PART III: PERSISTENCE RULES

### Rule 8: Persistence Law

Partially enriched parser output MUST be storable and reloadable if meaningful canonical user-facing fields are present.

- Missing non-critical parser metadata MUST NOT cause meaningful saved work to be discarded
- Schema validation MUST distinguish between required user-facing fields and optional parser metadata
- If a stored object has valid user-facing data but is missing auxiliary parser fields, it MUST load successfully

### Rule 9: Normalization/Inference Rule

Parsers MAY normalize and infer common real-world variants when mapping into canonical fields.

| Messy Input | Canonical Target |
|---|---|
| `lf` / `l.f.` / `linear feet` / `ft` | `linearFeet` (numeric) |
| Pool/spa mixed blob | Split into `pool.*` and `spa.*` fields |
| Noisy address text | `street`, `city`, `state`, `zip` |
| Various date formats | ISO 8601 |

**Constraints:**
- **Deterministic** where possible
- **Confidence-aware** where needed
- **Safely overrideable** by a human (Rule 3)

---

## PART IV: MODULE SPECIFICATIONS

### Required Canonical Inputs Per Module

| Module | ID | Required Canonical Inputs | Trigger Sources |
|---|---|---|---|
| **Site Intelligence** | M:SI | `lat`, `lng` | P2 (geocoder), manual entry |
| **House Panel Electric** | M:H-P-E | `panelAnalysis.mainBreakerAmps` OR `manualMainBreakerOverride` | P3 (panel OCR), manual entry |
| **Pool Panel Electric** | M:P-P-E | `equipmentAnalysis.data.items[]` (with amps/voltage) | P5 (equipment OCR), manual entry |
| **Pool/Spa Controller** | M:PS-C | `poolStats.gallons`, `poolStats.hasSpa`, equipment features | P4 (pool stats), P5 (equipment), manual entry |
| **Heating Calculator** | M:HT | `poolStats.gallons`, `poolStats.hasSpa`, `crmData.address.full` | P4 (pool stats), P1 (CRM address), manual entry |
| **Hydraulics/Plumbing** | M:PL | `poolStats.gallons`, `plumbingSpecs.*` (pipe runs) | P4 (pool stats), P6 (plumbing parser), manual entry |
| **Gas Line Calculator** | M:GL | Heater BTU requirements | M:HT output, manual entry |
| **Comparison/Story** | M:COMP | Multiple module outputs | Upstream module completion |

### Cascade Map

```
P1 (CRM) ──→ P2 (Geocode) ──→ M:SI (Site Intel)
                                    ↓
P3 (Panel) ──→ M:H-P-E ──→ [Audience Reports]
                                    
P4 (Pool Stats) ──→ M:PS-C ──→ [Audience Reports]
                ──→ M:HT  ──→ M:GL
                ──→ M:PL  ──→ [Audience Reports]

P5 (Equipment) ──→ M:P-P-E ──→ [Audience Reports]
               ──→ M:PS-C

P6 (Plumbing) ──→ M:PL ──→ [Audience Reports]
              ──→ M:HT
```

**Every arrow is gated.** No module activates without its required canonical inputs.

---

## PART V: PARSER DOMAIN SPECIFICATIONS

### P1: CRM / Client Info Parser
| Spec | Definition |
|---|---|
| **Accepted input** | Freeform CRM notes: names, phones, emails, addresses, project notes in any order/format |
| **Canonical targets** | `clientInfoOverrides.*` (street/city/state/zip, clientName, phone, email), `intake.siteInfoText` |
| **Required for downstream** | `clientInfoOverrides.street` → triggers geocoding; `lat/lng` → triggers M:SI |
| **Optional metadata** | `crmData.rawText`, `crmData.parsedAt`, `crmData.confidence`, `crmData.address.lat/lng` |
| **Manual override** | Enforced via clientInfoOverridesRef (DEF-TB-002) |
| **Persistence** | Optional metadata MUST NOT block `loadIntake()` |

### P4: Pool / Spa Stats Parser
| Spec | Definition |
|---|---|
| **Accepted input** | Mixed pool + spa dimensions, depths, volumes, surface areas; abbreviations; out-of-order |
| **Canonical targets** | `intake.poolStats.*` (gallons, hasSpa, spaVolume, surfaceArea, perimeter, depths) |
| **Required for downstream** | `poolStats.gallons` → M:HT, M:PL, M:PS-C |
| **Optional metadata** | Raw paste text, parse confidence, extraction method |
| **Manual override** | Manual field edits override parsed values |
| **Persistence** | Missing metadata MUST NOT block reload |

### P6: Utility / Linear-Foot / Plumbing Parser
| Spec | Definition |
|---|---|
| **Accepted input** | `lf`, `l.f.`, `linear feet`, `feet`, `ft`, mixed pipe sizes/types/quantities |
| **Canonical targets** | `intake.plumbingSpecs.*` (pipe runs with length, diameter, type, return/jet counts) |
| **Required for downstream** | Pipe specs → M:PL TDH calculation; feature flags → M:HT |
| **Optional metadata** | Raw paste text, parse confidence |
| **Manual override** | Manual field edits override parsed values |
| **Persistence** | Missing metadata MUST NOT block reload |

### P3: Panel Photo OCR
| Spec | Definition |
|---|---|
| **Accepted input** | Photos of house electrical panels (blurry, partial, rotated accepted) |
| **Canonical targets** | `intake.panelAnalysis.*` (mainBreakerAmps, circuits[], confidence) |
| **Required for downstream** | `mainBreakerAmps` OR `manualMainBreakerOverride` → M:H-P-E |
| **Optional metadata** | OCR confidence, image processing metadata |
| **Persistence** | Missing metadata MUST NOT block reload |

### P5: Equipment Image OCR
| Spec | Definition |
|---|---|
| **Accepted input** | Equipment lists, cut sheets, electrical blocks |
| **Canonical targets** | `intake.equipmentAnalysis.data.items[]` (name, category, amps, voltage) |
| **Required for downstream** | Equipment items with amps/voltage → M:P-P-E, M:PS-C |
| **Optional metadata** | OCR confidence, source image references |
| **Persistence** | Missing metadata MUST NOT block reload |

---

## PART VI: DOCS-FIRST RULE FOR ARCHITECTURE CHANGES

When parser behavior, trigger rules, canonical mapping, or domino wiring changes, the execution order is:

| Order | Step | Description |
|---|---|---|
| **1** | **Update docs + test harness** | System Audit, Tool Flow, Test Scenarios, Baseline Test, Story Demo |
| **2** | **Implement code changes** | Only after docs reflect the target architecture |
| **3** | **Verify via admin/dev tools** | Confirm domino chain is wired correctly using System Audit |

**The docs/test surfaces that must reflect the architecture:**
- **System Audit** — live truth map of module status, data flow, canonical input gates
- **Tool Flow** — complete system reference for humans and AI, multi-entry paths, trigger rules
- **Test Scenarios** — test cases covering multi-path entry, canonical gating, cascade, manual correction, messy input
- **Baseline Test** — golden inputs aligned to trigger contract, verify modules only fire when canonical inputs present
- **Story Demo** — current outputs and branches, reflects actual system behavior

**Rationale:** The docs/test harness is the canonical expression of the architecture. Code implements the architecture. Verification confirms the wiring. Changing code without updating docs first creates drift.

---

## PART VII: ENFORCEMENT

- This contract is a **governing product rule** — it supersedes implementation convenience
- Violations are **defects**, not technical debt
- Pre-commit checklists for parser or module work MUST include contract compliance check
- Any new parser or module must define its specification per Part V format before implementation

---

## PART VII: DOCUMENTATION UPDATES REQUIRED

The following source files must reflect this contract:

| Document | Location | Update Needed |
|---|---|---|
| System Map | `docs/SYSTEM_MAP.md` | Add trigger rules, multi-entry architecture, cascade gating |
| Intake Data Flow | `docs/INTAKE_DATA_FLOW.md` | Add persistence rule, required vs optional fields per module |
| System Audit page | `src/pages/SystemAudit.tsx` | Reflect multi-entry module access, trigger validation |
| System Audit lib | `src/lib/systemAudit/runSystemAudit.ts` | Audit should check canonical input presence, not raw text |
| Audit types | `src/lib/systemAudit/auditTypes.ts` | Add canonical-input-gate audit checks |

---

## CHANGELOG

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-03-20 | Initial parser rules |
| 2.0 | 2026-03-20 | Expanded to full trigger/cascade/multi-entry architecture. Added module specs, cascade map, domino rules. Supersedes v1.0. |
| 2.1 | 2026-03-20 | Added docs-first rule (Part VI). Architecture changes require docs/test updates before code changes. |

---

*Contract authored by Aristotle from Aaron's directive | Governing product rule — effective immediately*
