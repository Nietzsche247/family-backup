# OmniCalc Consolidated Audit Report
**Date:** 2026-04-18
**Auditor:** Empiricus (4-agent parallel audit)
**Spec Reference:** `hub.stigmergy.space/files/specs/OMNICALC_CANONICAL_TRUTH.md`
**DB Reference:** `hub.stigmergy.space/files/specs/OMNIPOOLS_DB_SCHEMAS.md`

---

## Executive Summary

4 parallel sub-agents audited the OmniCalc codebase against the Canonical Truth spec and DB schemas. **The core engineering is sound** — formulas are correct, module interfaces are clean, and the architecture follows the spec's intent. But there are **critical bugs in the electrical layer** and a **systemic hardcoding problem** across multiple modules.

| Module | Grade | Critical | Major | Minor |
|--------|-------|----------|-------|-------|
| Pool Panel Electrical | 🚨 **F** | 3 | 0 | 0 |
| Heater/Thermal Physics | ✅ **A** (95/100) | 0 | 0 | 1 |
| Cascade & Equipment | ⚠️ **C+** | 1 | 1 | 2 |
| Hydraulics & Data Flow | 🟢 **B+** | 0 | 2 | 1 |

**Total: 4 Critical, 3 Major, 4 Minor**

---

## 🚨 CRITICAL BUGS (Fix Before Production)

### C1: Heater Doubling Bug — Double-Counted Electrical Load
**Severity:** CRITICAL | **Modules:** Pool Panel + Cascade
**Files:** `equipmentClassifier/contextRules.ts:260-275` + `poolSubpanel/calculatePoolSubpanel.ts:240-256`

**Root Cause:** Heater added via TWO independent code paths:
- **Path 1:** Equipment classifier fires `therapy_requires_heater` rule when `hasSpa: true` → adds MasterTemp 400K BTU (460736)
- **Path 2:** `gatherEquipmentLoads()` processes `selectedEquipment.heater` field → adds same heater AGAIN

**Note:** The spa forcing dedup logic in `reconcile.ts` works correctly — this bug is in the load *calculation* layer, not the equipment *selection* layer.

**Impact:** Heater electrical load counted twice → ~3-6A overcounted per system.

**Fix:** Check `selectedEquipment.heater` in the `therapy_requires_heater` condition, OR deduplicate in `gatherEquipmentLoads()`.

---

### C2: Pump Mis-Allocation — Wrong Models for Roles
**Severity:** CRITICAL | **Module:** Pool Panel
**File:** `equipmentClassifier/contextRules.ts:200-210`

**Root Cause:** Same 3HP pump model (`011028` IntelliFlo VSF) hardcoded for ALL pump roles:
```
pump_main_vs: '011028'     ← correct
pump_spa: '011028'         ← WRONG (should be 1-2HP spa pump)
pump_secondary: '011028'   ← WRONG (should be 1HP water feature pump)
```

**Impact:** Spa/water feature pumps oversized by 8-15A each → electrical demand inflated → false "insufficient capacity" results.

**Fix:** Use distinct model numbers per role from `electrical_equipment_defaults` table.

---

### C3: Manual Overrides Not Protected
**Severity:** CRITICAL | **Module:** Cascade
**File:** `contextRules.ts:385+`

**Root Cause:** No `overrideSource` tracking. When a designer manually removes equipment (e.g., removes blower), the assumption rule re-adds it on next cascade recalculation because it only checks `!hasCategory(equipment, 'blower')`.

**Impact:** Designer intent silently overwritten → frustration, loss of trust in the tool.

**Fix:** Add `overrideSource: 'manual' | 'parser' | 'assumption'` field to equipment entries. Assumption rules must check source before overwriting.

---

### C4: Hardcoded Electrical Constants (Drift Risk)
**Severity:** CRITICAL (cumulative) | **Modules:** Pool Panel + Cascade + Feeder
**Files:** Multiple (see inventory below)

**Root Cause:** Values that exist in `calculation_assumptions` table are hardcoded in code:

| Value | Hardcoded In | DB Key | Match? |
|-------|-------------|--------|--------|
| 1.25 (continuous load) | `calculatePoolSubpanel.ts:38`, `constants.ts:135`, `useElectricalDefaults.ts:135` | `continuous_load_factor` | ✅ Today |
| 125A (panel max) | `calculatePoolSubpanel.ts:38`, `:46-56` (6 places) | `intellicenter_system_max` | ✅ Today |
| 100A (lite max) | `calculatePoolSubpanel.ts:46` | `intellicenter_lite_max` | ✅ Today |
| 3.0% (voltage drop) | `constants.ts:136`, `useElectricalDefaults.ts:136` | `max_voltage_drop_percent` | ✅ Today |
| 20+ model numbers | `contextRules.ts:28-66`, `outputRules.ts:72-88` | `electrical_equipment_defaults` | Unchecked |

**Impact:** Values match TODAY but will drift when admin updates DB without corresponding code changes. Creates invisible inconsistencies.

**Fix:** Replace all hardcoded values with `getAssumptionsSync()` or DB lookups (the heater module already does this correctly — use it as the pattern).

---

## ⚠️ MAJOR ISSUES

### M1: Hardcoded Hydraulic Constants
**Severity:** MAJOR | **Module:** Hydraulics
**Files:** `componentTDH.ts`, `fittingFormula.ts`

All equipment head losses (skimmers, drains, returns, filters, heaters, chlorinators) and fitting K-values are hardcoded arrays instead of reading from `omni_whitegoods_master` table.

The DB has `k_value`, `equiv_length_ft`, and `loss_method` columns specifically for this data — they're just not being used.

**Note:** K-value for tee branch is 0.6 in code vs ~1.0-1.8 in Crane TP-410. This may underestimate TDH by ~2 ft in a typical system.

---

### M2: Embedded NEC Ampacity Tables
**Severity:** MAJOR | **Module:** Feeder Sizing
**File:** `calculateFeederSizing.ts:40-56`

Full NEC 310.16 copper/aluminum ampacity table hardcoded. No temperature derating, no conduit fill derating. Standard breaker sizes also embedded.

---

### M3: Equipment Class Defaults Hardcoded
**Severity:** MAJOR | **Module:** Cascade
**File:** `outputRules.ts:72-88`

12+ equipment categories have hardcoded `{amps, voltage}` fallback defaults that bypass the `equipment` table entirely. These are used when equipment lookup fails, but they create a shadow data source.

---

## ✅ WHAT'S WORKING WELL

| Area | Assessment |
|------|-----------|
| **Heater/thermal physics** | All constants DB-driven via `getAssumptionsSync()`. Cover factors, heat loss, BTU calcs all correct. Exemplary pattern. |
| **TDH formula** | Correct Hazen-Williams implementation. Mode-aware (Omni HDS vs standard). Proper additive head loss. |
| **Cross-module interfaces** | Clean TypeScript interfaces, no state coupling, proper separation of concerns. |
| **Session state** | Single store (`omni-intake-v1`), schema versioning, no dual-store issues. `omni-intake-cross-page` not found in current codebase. |
| **Spa forcing dedup** | `reconcile.ts:270-318` properly handles parsed vs assumed conflicts. Priority ordering correct. |
| **Legacy code paths** | None found. Single calculation engine per module. Clean architecture. |

---

## Systemic Pattern: The DB-Driven Spectrum

The codebase shows a clear spectrum of DB compliance:

```
EXCELLENT ─────────────── GOOD ─────────────── POOR
   │                        │                    │
   Heater module         Pipe ID fallbacks    Equipment defaults
   (all via DB)          (DB primary,         Fitting K-values
                          fallback exists)     Component TDH
                                              NEC tables
                                              Model numbers
```

**The heater module is the gold standard.** Every other module should follow its pattern: `getAssumptionsSync()` with graceful fallbacks, NOT hardcoded primary values.

---

## Recommended Fix Priority

### Phase 1: Stop the Bleeding (Week 1)
1. **Fix heater doubling** — deduplicate in `gatherEquipmentLoads()` (C1)
2. **Fix pump roles** — distinct model numbers per pump type (C2)
3. **Add override source tracking** — `overrideSource` field on equipment entries (C3)

### Phase 2: DB Migration (Week 2-3)
4. **Electrical constants → DB** — replace all hardcoded values with `getAssumptionsSync()` (C4)
5. **Hydraulic constants → DB** — wire `componentTDH.ts` to `omni_whitegoods_master` (M1)
6. **Equipment defaults → DB** — wire `outputRules.ts` to `electrical_equipment_defaults` (M3)

### Phase 3: Completeness (Week 3-4)
7. **NEC tables → DB** — create `nec_ampacity` table for feeder sizing (M2)
8. **Verify tee K-value** — confirm 0.6 vs Crane TP-410 standard (M1)
9. **Add assumption audit trail** — log which rules fired and why

---

## Individual Audit Reports

| Report | Location |
|--------|----------|
| Pool Panel Electrical | `memory/omnicalc-audit/AUDIT-1-POOL-PANEL.md` |
| Heater/Thermal Physics | `memory/omnicalc-audit/AUDIT-2-HEATER-PHYSICS.md` |
| Cascade & Equipment | `memory/omnicalc-audit/AUDIT-3-CASCADE-EQUIPMENT.md` |
| Hydraulics & Data Flow | `memory/omnicalc-audit/AUDIT-4-HYDRAULICS-DATAFLOW.md` |

---

*Compiled by Empiricus from 4 parallel Sonnet 4 sub-agent audits. Total audit runtime: ~8 minutes. Total tokens: ~247k across agents.*
