# OmniCalc GPD Physics Verification — Consolidated Audit Report

**Date:** 2026-04-18
**Auditor:** Empiricus (nietzsche-i9)
**Methodology:** GPD (Get Physics Done) verification checks 5.1-5.7
**Source:** `C:\Users\Aaron\clawd\omnipools-src\` (556 files, hub snapshot)
**Sub-agents:** 4× Sonnet 4.5 (parallel audit)

---

## 🔥 Executive Summary

| Module | Grade | Critical Bugs | Status |
|--------|-------|--------------|--------|
| **Hydraulics** | 6/10 | 3 | ⚠️ Sound at design flow, breaks at variable speed |
| **Heater Calculations** | 7/10 | 3 | ⚠️ Core thermo correct, environmental models broken |
| **Electrical Rules** | B+ screening / C permit | 6 | ❌ Known bug confirmed + 5 new NEC violations |
| **Feeder Sizing** | ❌ | 4 | ❌ NOT PRODUCTION READY — fire safety risk |

**Total bugs found: 16**
**Critical (safety/compliance): 8**
**Known bug (heater doubling) status:** CONFIRMED in electrical module (pool equipment double-counting in `computeLoads.ts`). NOT in hydraulics or heater calc modules — it's in the load calculation layer, not the physics.

---

## 🚨 Priority 1 — Fix Immediately (Safety/Compliance)

### FEEDER-1: Ampacity Table Corruption
- **All copper values ≥8 AWG are 18-25% higher than NEC Table 310.16**
- Code: #6 Cu = 65A → NEC: 55A
- **Risk:** Undersized conductors → overheating → fire

### FEEDER-2: No Temperature Derating
- Zero temperature correction for Phoenix (40-50°C ambient)
- NEC requires 0.75× at 50°C
- **Combined with FEEDER-1:** Conductors undersized by 40-60%

### FEEDER-3: No Conduit Fill Derating
- 4+ conductors require 0.80× per NEC 310.15(C)(1)
- Not applied anywhere

### ELEC-3 (KNOWN BUG CONFIRMED): Pool Equipment Double-Counting
- Existing pool breakers counted in `KNOWN_240V`
- Proposed pool equipment added separately
- No dedup check → load overestimated

### ELEC-4: Missing 125% Continuous Load Factor
- Only applied to proposed pool equipment
- NOT applied to HVAC, well pumps, existing pool pumps
- Underestimates required breaker/conductor sizing by 20%

### ELEC-5: No NEC 680.21 Validation
- Pool pump overcurrent protection must not exceed 150% of motor FLA
- No validation → non-compliant permits possible

---

## ⚠️ Priority 2 — Fix Before Production

### ELEC-2: No Heat vs. AC Exclusion (NEC 220.82(C))
- Code flags electric heat but doesn't exclude the lesser of heat/AC
- Could double-count HVAC

### ELEC-1: Fastened Appliance Demand Factor Wrong
- Applies 75% to ALL when count ≥ 4
- Should be: first TWO at 100%, remainder at 75%
- Undercalculates load by 10-15%

### ELEC-6: Permit Mode Hardcoded Values
- Uses standard loads (cooking 8000 VA, dryer 5000 VA) instead of requiring nameplate ratings
- Acceptable for screening, NOT for permits

### HYDRO-1: Tee Branch K-Value Wrong
- Code: 0.6 → Crane TP-410: 1.8 (67% too low)
- Underestimates TDH by ~2-3 ft in typical systems
- **Fix:** Change `k_value: 0.6` to `1.8` in `fittingFormula.ts:130`

### HEAT-1: Solar Gain Off by 100×
- Current: 2.5 BTU/(hr·ft²)
- Expected: 200-250 BTU/(hr·ft²) for Phoenix
- Heating costs overestimated by 10-20% for uncovered pools

### HEAT-2: Wind Effect Underestimated by 20-30×
- 10 mph wind modeled as 30% increase
- Physics: should be 500-700% increase
- Heat loss severely underestimated in windy conditions

---

## 📋 Priority 3 — Architectural Improvements

### HYDRO-2: Equipment Head Losses Are Flow-Independent
- All equipment PSI drops are hardcoded constants (don't scale with Q²)
- Acceptable if system only evaluates at 60 GPM design flow
- **Blocks variable-speed pump analysis**
- Fix: implement `ΔP(Q) = C × Q²` with manufacturer coefficients

### HYDRO-3: No Flow Rate Parameter in calculateEquipmentTDH()
- Function doesn't accept flow rate as input
- Must be refactored before variable-speed pump support

### HEAT-3: Evaporative Loss Formula Not Physics-Based
- Uses `evapLoss ∝ ΔT` (linear with temp difference)
- Should use vapor pressure difference
- Works empirically in Arizona's narrow range but breaks at edge cases

---

## ✅ What's Working Well

| Area | Finding |
|------|---------|
| **PSI↔ft conversion** | 2.31 factor correct throughout |
| **BTU thermodynamics** | 8.34 BTU/gal·°F verified |
| **TDH energy conservation** | Additive sum of all loss components correct |
| **Order of magnitude** | All modules produce realistic values for typical scenarios |
| **Equipment validation** | Database-first architecture, NO hardcoded equipment specs in heater module |
| **NEC 220.12/220.82 foundation** | Core load calculation structure is sound |
| **Dual-mode architecture** | Screening vs permit mode is excellent design |
| **Fuzzy pattern matching** | Handles real-world OCR errors well |
| **Voltage drop formula** | Correct implementation with proper 2× factor |
| **Cover effect modeling** | 70-90% reduction reasonable |

---

## 🎯 Where "Heater Doubling" Bug Lives

All four audit modules searched for this. Findings:
- **NOT in hydraulics** (componentTDH.ts accepts selections and processes correctly)
- **NOT in heater calculations** (no hardcoded equipment specs)
- **CONFIRMED in electrical** (computeLoads.ts double-counts pool equipment)
- **Likely also in UI/panel layer** that constructs `ComponentSelections`

The bug manifests as: existing pool breakers already included in `KNOWN_240V` array, then proposed pool equipment added on top without checking for overlap. The fix needs a dedup check or a clear boundary between "existing" and "proposed" equipment.

---

## Detailed Reports

- `memory/audit-hydraulics.md` — Full hydraulics verification (18KB)
- `memory/audit-heater.md` — Full heater calculations verification
- `memory/audit-electrical.md` — Full NEC compliance verification
- `memory/audit-feeder.md` — Full feeder sizing verification

---

*Audit methodology: GPD v1.1.0 verification checks (5.1 dimensional analysis, 5.2 numerical spot-check, 5.3 limiting cases, 5.4 conservation laws, 5.7 order of magnitude) plus domain-specific NEC compliance checks and Crane TP-410 cross-reference.*
