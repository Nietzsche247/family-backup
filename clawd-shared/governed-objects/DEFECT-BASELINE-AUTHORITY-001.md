# DEFECT: BASELINE-AUTHORITY-001

**Classification:** PRE-RUN BASELINE VALIDATION FAILURE  
**Discovered in:** P2BR3-20260903-A  
**Discovered by:** Aristotle (hardened integration gate)  
**Stop event:** `01M1M2R8Z1VTPSDYETBJPBGPPZ`  
**Date:** 2026-09-03T16:48:38.369Z  

## Finding

The frozen R3 authority map (`AUTHORITY-MAP-R3.json`) retained experiment-bound path prefixes from Revision B / PHASE-2B-R2 while the R3 execution correctly produced paths under PHASE-2B-R3.

- **Frozen authority prefix:** `PHASE-2B-R2/control-arm/`
- **Actual R3 path:** `PHASE-2B-R3/control-arm/`

The hardened integration gate correctly rejected all three receipts (0/3 passed).

## This is NOT

- ❌ Receipt-gate failure (gate worked correctly)
- ❌ Worker semantic failure (worker produced correct paths)
- ❌ Parallelism failure (parallel arm never started)
- ❌ Phase 2B architecture failure

## Why the 30/30 preflight missed it

The prior baseline audit verified the authority map as a governed artifact (file hash matched frozen baseline) but did not prove that every experiment-bound literal inside that artifact matched the current experiment identity.

**Critical distinction:**

> ARTIFACT IDENTITY VALID does not imply ARTIFACT INTERNAL REFERENCES CURRENT

A file can have the correct SHA-256 and still contain stale experiment-bound values if the file was frozen with those stale values.

## Corrective action

1. R4 authority map must be created from the current experiment identity (`P2BR4-20260903-A`)
2. A new deterministic EXPERIMENT-IDENTITY CONSISTENCY CHECK must be added to preflight
3. The final baseline audit must verify BOTH artifact identity/hash AND internal experiment-bound values
4. Controlled test fixtures must prove the checker catches stale R2 and R3 prefixes

## Disposition

R3 experiment `P2BR3-20260903-A` is BLOCKED / INVALIDATED. All evidence preserved. No in-place repair. Fresh experiment R4 authorized.
