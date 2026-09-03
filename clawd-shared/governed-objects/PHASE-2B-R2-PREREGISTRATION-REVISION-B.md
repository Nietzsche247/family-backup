# Phase 2B-R2 Preregistration — Revision B (Superseding)

**Experiment ID:** `P2BR2-20260902-A`  
**Rubric ID:** `P2BR2-RUBRIC-18-v1`  
**Revision:** B (supersedes initial preregistration)  
**Parent goal pointer:** `01M1DVHCYZSYREJY6AZJ0EHA0R`  
**Status:** FROZEN — receipt hardening complete, timer NOT started  
**Revision reason:** Steel-man review discovered 7 hard blockers in the Phase 2B integration gate. Gate was forked and hardened. This revision freezes the actual system that will be timed, including the hardened gate identity.

## What changed from initial preregistration

1. **Gate forked and hardened:** `integration-gate-r2.js` replaces the Phase 2B gate for all R2 receipt validation. 14 gaps closed.
2. **Authority map created:** `AUTHORITY-MAP-R2.json` provides machine-readable domain boundaries.
3. **Open questions resolved:** 5 implementation decisions documented in `OPEN-QUESTIONS-RESOLVED.md`.
4. **Controlled fixtures proven:** 7/7 correct (`GATE-PREFLIGHT-RESULT.json`).

## What did NOT change

- Objective (unchanged)
- 18-point pass bar (unchanged)
- Semantic acceptance contract (unchanged)
- TTC definition and boundaries (unchanged)
- Independent Plato Judge requirement (unchanged)
- Signal Fire isolation rule (unchanged)
- Baseline sources (unchanged)
- Model/runtime configuration (unchanged)
- Authority envelope structure (unchanged)
- Contamination rules (unchanged)
- Stop rules (unchanged)

This is a laboratory-baseline correction, not a new success criterion.

## Frozen system identity

| Component | SHA-256 | Bytes |
|---|---|---|
| Contract | `9DC2FA4F28E98CCC5F5C7B8BAE646286A68EB0B61CED0F0F253E3B8177716796` | 10,657 |
| Hardened gate | `FF20135F07CE0731CCF834F4496F6C34587A60D629CDD581143F302FD22A436E` | 10,876 |
| Gate preflight result | `A430C64FD289C7C09B58C513C2A2520097D7A8256ACF16818C14397952F27822` | 2,590 |
| Authority map | `EA4BD0C11C5EDB1D7665F74E06D8ACF56CE83D7376729A6C8988DB51B8851D24` | 243 |
| Context manifest | `72AC0D3CDE09DDB349748078B3FD809E5352BD6E31A28B06585DEE92C0313800` | 2,440 |
| Signal Fire attestation | `EC50BC953570000F501BDE1121A1DA1BA1B7C9D8A67E6A780214219A82B300EE` | 1,884 |
| Baseline manifest | `0E340AFBB2995381E355B4054FE72A89669FFE3E1241A911BE45C9B5AC2E8A3A` | 5,243 |
| Open questions resolved | `4D0F72527BDFECF585BE338E2604BC841ED2D7D0D700BBEA61506DE506C72BDE` | 2,596 |
| Steel-man review | `99B07963918B5B1DBC5182F725822FF965028210AA9F9252093D0F4A9226EDC2` | 30,898 |
| Context lifecycle preflight | `8A403DEC6FE5E4C491078C18A6D54CF95988EF7892079E49653979C449C8D82F` | 1,550 |

## Controlled fixture proof

| Fixture | Expected | Actual | Correct |
|---|---|---|---|
| VALID | PASS | PASS | ✅ |
| MISMATCH-HASH | FAIL | FAIL | ✅ |
| MISMATCH-BYTES | FAIL | FAIL | ✅ |
| MISSING-GENERATION | FAIL | FAIL | ✅ |
| STALE-GENERATION | FAIL | FAIL | ✅ |
| PRE-TIMER | FAIL | FAIL | ✅ |
| WRONG-BASELINE | FAIL | FAIL | ✅ |

**7/7 correct.** Gate rejects every known defect class that caused the Phase 2B-R Program A receipt mismatch.

## Remaining preflight

1. Plato verifies this exact revision.
2. Plato explicitly returns **JUDGE READY** with the exact Experiment ID, Rubric ID, and Revision B contract SHA-256.
3. R2 timer starts only after Plato READY is recorded.

## Phase 2B-R2 pass bar (unchanged, 18 criteria)

1–18 per `PHASE-2B-R2-PREREGISTERED-CONTRACT.md` §16. No alternative success criterion after the run.

## Governed prior revision

Initial preregistration: `01M1J9JWT5K8VM4A85KG0F5JFD` (preserved historically, not deleted).

This revision supersedes it for the purpose of freezing the timed laboratory identity.
