# DEFECT: RECEIPT-AUTHORITY-001

**Filed:** 2026-09-04
**Experiment:** P2BR4-20260903-A (Phase 2B-R4, Revision D)
**Classification:** PRE-SEAL PROCEDURAL AUTHORITY FAILURE
**Disposition:** R4 STOPPED / INVALIDATED

## Definition

Frozen experiment required hardened receipt-gate compliance, but the producer emitted a receipt incompatible with the gate schema. The Global Orchestrator constructed replacement receipts post-production, including at least one invented experiment-bound field (`attempt_id`) and orchestrator-authored `acceptance_evidence`. Frozen Revision D did not explicitly authorize or prohibit that repair path. Post-hoc authorization was therefore rejected by Primary.

## Root cause

1. **Schema mismatch:** The hardened integration gate (`integration-gate-r2.js`) requires 22 fields per receipt. Revision D §10 (inherited from Revision B §10) specifies 11 "Receipt fields required." The gate's additional 11 fields (`baseline_class`, `baseline_ref`, `scope`, `method`, `claim`, `context_manifest_hash`, `producing_agent`, `branch`, `acceptance_evidence`, `ledger_event`, `bytes` as top-level) were not listed in the frozen contract's receipt field specification.

2. **Producer receipt format:** The control executor produced a single multi-artifact receipt (`CONTROL-RECEIPT.json`) with an `artifacts[]` array. The gate expects one receipt file per artifact with a single `artifact` path and `provenance` hash.

3. **Missing experiment-bound identity:** The producer receipt omitted `attempt_id`. The orchestrator invented `P2BR4-control-attempt-001` to satisfy the gate. No pre-dispatch assignment of `attempt_id` existed.

4. **Authority gap:** No clause in Revision D explicitly authorizes or prohibits the orchestrator constructing, reformatting, or supplementing producer receipts after production.

## Evidence preserved

| Artifact | Path | SHA-256 |
|---|---|---|
| Original producer receipt | `receipts/control-arm/CONTROL-RECEIPT.json` | `F74043BC3FC5A0FFC46E444D86B880FEDE321CD6721C5813B9D27059EDBE6528` |
| Corrected receipt (001) | `receipts/control-arm/P2BR4-20260903-A-control-001.json` | `91581C412A4DE1A3EAF209B13E04834A9F10B5159C4460482E76FD7FE4258B22` |
| Corrected receipt (002) | `receipts/control-arm/P2BR4-20260903-A-control-002.json` | `C2B1B3E8BA73CC887575AD32D4DB0ADE53F57BEAD6BE865D97F288D5BF152D84` |
| Corrected receipt (003) | `receipts/control-arm/P2BR4-20260903-A-control-003.json` | `3BDFDBFEE7A4D0BB54EB5B4808AE19F9D4EC66D91C4CA6EF70ADAD04BA2E52F3` |
| Gate result | `receipts/control-arm/GATE-RESULT.json` | `DDF653A4FEFC155A4A453F7D4867C0CB1C5309B8A8862E76B5E73D15569D4BF1` |
| Control Deliverable A | `control-arm/RECOVERY-PLAYBOOK-V2.md` | `876114106002216607E91A1C5C64620EB74F617C04D422EA3ED9A347375C71A5` |
| Control Deliverable B | `control-arm/KNOWLEDGE-BRAIN-V0-IMPLEMENTATION-V2.md` | `C0CF05AE4AA966F8907666A694A26EBF01F019B91AFBF99F79769C07B35C05AF` |
| Control Integration | `control-arm/INTEGRATION-REPORT.md` | `CACD13AB2FEE73B73DF0045C0191440257DBFA9BCEDBFBC5B6B8951F06B1C7A7` |
| Timebase reconciliation | This document + Ledger event `01M1QFJQFXD0K118PR0CESRZRA` |
| Prior incorrect heartbeat statement | Corrected: no 20:00 transition occurred during control window |

## Corrective requirements for R5

See Primary's 12-point list in the R5 preregistration contract.

## Semantic boundary lesson

**GATE SCHEMA ≠ CONTRACT RECEIPT SPEC.** A frozen contract that says "use this gate" and separately lists "receipt fields required" creates an authority gap when the gate requires more fields than the contract specifies. The fix is to bind the exact gate receipt schema into the frozen contract itself, and prove producer receipt compliance in a dry fixture before timer start.
