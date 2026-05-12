# DEF-TB-001 Fix Brief — Phase 1: Jurisdiction/Locality Trust Chain Wiring

**Date:** 2026-03-23
**Track:** B (OmniPools Calculator)
**Author:** Aristotle
**Version:** 2.0 (supersedes v1.0 — corrected framing per Aaron)
**Status:** APPROVED BY AARON (2026-03-23 10:18 MST)
**Inputs:** DEF-TB-001-CODE-MAP.md (Daedalus), DEF-TB-001-SCOPE-INTEGRITY.md (Steel Man), DEF-TB-001-ENGINE-AUDIT.md (Daedalus), JURISDICTION-DETECTION-V5.md (Aaron), Aaron's scoping decision (layered delivery — Phase 1 of 3)
**Governing law:** Parser + Trigger Contract v2.1

---

## Phased Delivery Context

Aaron chose **layered delivery** — three phases, three separate governed briefs:

| Phase | Scope | Status |
|-------|-------|--------|
| **1 (this brief)** | Wiring fix — trust chain, canonical source, read/write precedence | ACTIVE |
| 2 | V5 engine integration — `JurisdictionEngine.detect(lat, lng)` auto-detection | QUEUED |
| 3 | Rules display UI — setbacks, barriers, alarms, doors per jurisdiction | QUEUED |

**Phase 1 explicitly excludes:** engine integration, rules data, rules UI. Those are Phase 2 and 3.

---

## Root Cause — Plain English

Jurisdiction is supposed to auto-populate from the geocode/Site Intelligence pipeline — the designer almost never selects it manually. But the wiring is broken in two ways:

1. **The canonical location resolver ignores available jurisdiction data.** `selectResolvedLocation()` reads city/state/zip from manual overrides (correct), but reads jurisdiction and county **only** from the Site Intelligence report. Even when the geocoder, reverse-geocoder, or a manual correction has jurisdiction available in `clientInfoOverrides.jurisdiction`, the resolver doesn't look there. So downstream consumers see jurisdiction as `null` unless Site Intelligence has run.

2. **Stale async callbacks can erase jurisdiction mid-session.** The geocode and reverse-geocode paths dispatch whole-object replacements of `clientInfoOverrides`. If any jurisdiction value gets set (manually or via reverse-geocode) while a geocode operation is in-flight, the stale callback overwrites the entire overrides object with an older snapshot, collapsing the jurisdiction value. TB-002 fixed this class of bug for the CRM parser path only — geocode/reverse-geocode paths remain unprotected.

---

## Authoritative Source Decision

Per Parser + Trigger Contract v2.1 Rule 3 (manual correction is authoritative):

**Jurisdiction resolution precedence:**
1. `clientInfoOverrides.jurisdiction` — **authoritative** (manual correction by designer, if present)
2. `siteIntelligenceReport.location.jurisdiction` — **enrichment/auto-populated** (primary path in normal flow)
3. `null` — no jurisdiction resolved yet

**Why manual override is listed first even though auto-population is the normal path:**
In typical use, the designer never touches jurisdiction — it auto-populates from geocode → SI. But if SI gets it wrong (e.g., address near a city boundary), the designer must be able to correct it, and that correction must stick. Rule 3 is non-negotiable. The precedence chain ensures auto-populated values flow through while manual corrections take priority when present.

**County resolution precedence:**
1. `siteIntelligenceReport.location.county` — enrichment only (no manual county field exists in schema; adding one is out of Phase 1 scope)
2. `null` — no county resolved

**Note:** Once Phase 2 integrates the v5 engine, the auto-population path will be much richer (12 jurisdictions, bounding box + Pima dual-API). Phase 1 just ensures whatever jurisdiction value exists gets read correctly.

---

## Exact File/Function Scope

### Files IN SCOPE for changes:

**Core wiring (original 3 — committed dbe9867):**

| File | What Changes | Why |
|------|-------------|-----|
| `src/lib/intake/selectors.ts` | `selectResolvedLocation()` lines 62-72 | Must include `clientInfoOverrides.jurisdiction` in resolution chain — overrides first, SI report second |
| `src/hooks/useIntake.ts` | `retryGeocoding()` lines 1023-1032 | Must read fresh overrides from `clientInfoOverridesRef.current` instead of stale `intake.clientInfoOverrides` capture |
| `src/components/intake/ParsedClientInfo.tsx` | `reverseGeocode()` lines 167-174 | Must read fresh overrides (via ref or callback pattern) instead of stale component-closure `overrides` |

**Split-brain reader fixes (added per Daedalus review + Aaron directive):**

| File | Lines | Issue | Fix |
|------|-------|-------|-----|
| `src/components/reports/UnifiedPDFExport.tsx` | 231, 272, 457 | Reads `siteIntelligenceReport.location.jurisdiction` directly | Must use `selectResolvedLocation()` output |
| `src/components/tabs/FullReportsTab.tsx` | 882 | Reads SI jurisdiction directly | Must use canonical selector |
| `src/components/tabs/PermittingTab.tsx` | 154 | Reads SI jurisdiction directly | Must use canonical selector |
| `src/components/tabs/HomeownerResultsTab.tsx` | 391, 700-701 | Reads SI jurisdiction directly | Must use canonical selector |
| `src/lib/intake/artifacts.ts` | (story/export builder) | Builds exports from SI jurisdiction directly | Must use canonical selector |

### Files EXPLICITLY OUT OF SCOPE:

| File | Why excluded |
|------|-------------|
| `persistence.ts` | No persistence changes (Phase 1) |
| `schema.ts` | No schema changes — `jurisdiction` field already exists in `ClientInfoOverridesSchema` |
| `useIntakeReader.ts` | Cross-page reader (TB-003 territory) |
| Autosave/session-restore logic | TB-003 territory |
| Any migration or schema version bump | Not needed |
| Jurisdiction engine / detection logic | Phase 2 |
| Rules data / display UI | Phase 3 |

---

## Recommended Narrow Fix (3 changes)

### Fix 1: Selector reads overrides jurisdiction in resolution chain
**File:** `src/lib/intake/selectors.ts`
**Lines:** 71-72
**Change:** Jurisdiction resolution should read `clientInfoOverrides.jurisdiction` first, fall back to `siteIntelligenceReport.location.jurisdiction`.

Current (broken):
```typescript
county: siteReport?.location?.county ?? null,
jurisdiction: siteReport?.location?.jurisdiction ?? null,
```

Target:
```typescript
county: siteReport?.location?.county ?? null,
jurisdiction: overrides?.jurisdiction || siteReport?.location?.jurisdiction ?? null,
```

Where `overrides` is `intake.clientInfoOverrides` (already available in the selector's scope or trivially passable).

**Why this works:** In normal flow, `clientInfoOverrides.jurisdiction` will be empty and SI report provides the value. When a manual correction exists, it takes precedence. Both paths use the same canonical read function.

### Fix 2: Stale-closure protection on geocode path
**File:** `src/hooks/useIntake.ts`
**Lines:** 1023-1032 (`retryGeocoding`)
**Change:** Replace `...intake.clientInfoOverrides` with `...clientInfoOverridesRef.current` to read fresh overrides at dispatch time.

The ref already exists (TB-002 created it at lines 343-348). This is extending its usage to a second write path — same proven pattern.

### Fix 3: Stale-closure protection on reverse geocode path
**File:** `src/components/intake/ParsedClientInfo.tsx`
**Lines:** 167-174 (`reverseGeocode`)
**Change:** The component currently spreads `...overrides` from its render closure. Two acceptable approaches:
- **(A) Callback pattern:** pass a fresh-overrides getter from the parent hook
- **(B) Ref pattern:** mirror the useRef approach from useIntake.ts within the component

Plato decides implementation — both are acceptable as long as the dispatched object includes the latest override values at write time.

---

## AARON'S IMPLEMENTATION EMPHASIS (non-negotiable)

This is not just a dropdown/display fix. It must establish a **single canonical jurisdiction/locality source** with clear precedence:
- Auto-populated by geocode/SI by default
- Manual override authoritative when present

The same canonical source must be used consistently for:
- **Displayed field state** (what the designer sees)
- **Downstream module trust** (what modules consume)
- **Outputs/exports/permit-facing summaries** (what leaves the system)

**No split-brain reads.** No one page trusting one source while another page trusts a different one. Every consumer of jurisdiction MUST resolve through `selectResolvedLocation()` after this fix.

---

## Regression Risks

| Risk | Mitigation |
|------|-----------|
| Fix 1 changes resolved location for all downstream consumers | Only jurisdiction field changes; city/state/zip/county untouched. Normal flow (SI auto-populates, no manual override) produces identical results. |
| Fix 2/3 changes geocode callback behavior | Only changes *which snapshot* of overrides is used — fresh instead of stale. No new fields, no removed fields. |
| Manual jurisdiction could conflict with SI jurisdiction | Precedence is explicit: manual wins. This is the same pattern city/state/zip already use. In normal flow, manual override is empty and SI value passes through. |
| TB-002 regression (parseCRM stale closure) | parseCRM path is untouched. Ref usage is additive (extending to more write paths). |
| TB-003 regression (reload/persistence) | No persistence, schema, or autosave changes. |
| coordSource regression | No lat/lng or coordSource writes in any of the 3 fixes. |

---

## Contract Compliance Checklist

- [ ] **Rule 3:** Manual `clientInfoOverrides.jurisdiction` is authoritative — never overwritten by parser/inference without explicit user action
- [ ] **Rule 2:** Parser/inferred jurisdiction remains candidate until mapped to canonical field; downstream does not consume candidates as authoritative
- [ ] **Rule 5:** No module triggers based on jurisdiction presence alone; jurisdiction is not a required canonical input for any downstream module in Phase 1
- [ ] **coordSource:** No new lat/lng write path; coordSource protections unchanged
- [ ] **TB-002 non-regression:** parseCRM useRef pattern untouched; stale-closure fix extended (not replaced)
- [ ] **TB-003 non-regression:** No changes to loadIntake/saveIntake, schema validation/migrations, autosave guards, session restore heuristics, or cross-page overwrite guard logic

---

## Phase 1 Acceptance Criteria (for Empiricus validation)

### Live-session behavior:
1. Jurisdiction auto-populated by SI → value appears in resolved location correctly
2. Manual jurisdiction correction → value persists in resolved location, takes precedence over SI
3. Geocode completes after jurisdiction is set → jurisdiction is NOT overwritten
4. Reverse geocode completes after jurisdiction is set → jurisdiction is NOT overwritten
5. CRM parser re-run does not affect jurisdiction (TB-002 non-regression)

### Canonical source consistency:
6. Displayed jurisdiction in UI matches `selectResolvedLocation().jurisdiction`
7. Any downstream module/export that uses jurisdiction reads from the same canonical source
8. City/state/zip manual override behavior is unchanged
9. coordSource behavior is unchanged

### Distinguishing from TB-003 (reload/rehydration):
10. If jurisdiction collapses ONLY on reload, that is TB-003 class — note it but do NOT fail TB-001 for it
11. If jurisdiction collapses during live session (no reload), that IS a TB-001 failure

---

## Execution Sequence

1. ✅ Code map (Daedalus) — DONE
2. ✅ Engine audit (Daedalus) — DONE → PARTIALLY WIRED (engine not in codebase)
3. ✅ Scope check (Steel Man) — DONE / PASS
4. ✅ Fix brief Phase 1 v2.0 (this document) — PENDING AARON REVIEW
5. ⬜ Source-truth preflight (Plato) — IN PROGRESS
6. ⬜ Validation plan (Empiricus) — IN PROGRESS
7. ⬜ Aaron approves brief → Plato implements
8. ⬜ Daedalus code review
9. ⬜ Aaron deploys
10. ⬜ Empiricus validates Phase 1 acceptance criteria
11. ⬜ Governed close → Ledger event

---

## Phase 2 Preview (NOT in scope for this brief)
- Port `JurisdictionEngine.detect(lat, lng)` into OmniPools codebase
- Wire to geocode pipeline: lat/lng resolved → auto-detect jurisdiction → populate canonical field
- 12 jurisdictions, hybrid bounding box + Pima dual-API
- Reference: `JURISDICTION-ENGINE-V5.js`, `JURISDICTION-DETECTION-V5.md`

## Phase 3 Preview (NOT in scope for this brief)
- Rules display UI — once jurisdiction is resolved, surface: setback rules, barrier height, allowed/disallowed barrier types, alarm types, door types
- Per-jurisdiction rules dataset from v5 reference doc
- This is the user-facing payoff of the jurisdiction feature

---

*Aristotle — DEF-TB-001 Fix Brief Phase 1 v2.0 — 2026-03-23*
