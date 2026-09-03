# Signal Fire Firewall Attestation — Phase 2B-R2

**Experiment:** `P2BR2-20260902-A`  
**Rubric:** `P2BR2-RUBRIC-18-v1`  
**Status:** FROZEN PRE-RUN EVIDENCE REQUIREMENT

Signal Fire remains outside project execution. Signal Fire content is not introduced to prove its absence.

## Prohibited uses

No Signal Fire diary, reflection, social, or experiential content may govern or influence:

- truth
- routing
- dispatch
- priority
- budgets
- leases
- capability assignment
- retry or repair
- promotion
- acceptance

## Evidence mechanism

1. Every role receives the source allowlist in `R2-INPUT-CONTEXT-MANIFEST.json`.
2. Every work packet records the supplied source list and affirms that no unlisted source was used.
3. Every receipt includes the context-manifest SHA-256 and a negative Signal Fire attestation.
4. Global integration scans worker receipts and source lists for `signal-fire`, `Signal Fire`, diary, reflection, or social-content paths.
5. The integration gate fails or quarantines any undeclared source or any Signal Fire execution source.
6. The sealed arm bundle contains this attestation, all role manifests, receipts, scan output, and gate result.
7. Plato independently verifies the negative evidence.

## Per-role attestation fields

Each role must provide:

- role and attempt ID
- exact allowed-source list/hash
- exact sources actually read
- prohibited-source scan result
- statement: `signal_fire_execution_use: false`
- producing agent and timestamp
- signature hash as part of its deterministic receipt

## Arm result

This document does not predeclare PASS. Each arm receives:

- `control_result: PENDING`
- `program_a_result: PENDING`
- `program_b_result: PENDING`
- `global_integration_result: PENDING`
- `judge_result: PENDING`

Criterion 16 passes only when Plato verifies the complete negative-evidence chain. Absence of evidence is not PASS.
