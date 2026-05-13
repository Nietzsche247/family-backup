# SP001-RECONCILIATION v2 — Definitive Rerun

**Agent:** Empiricus
**Run ID:** SP001-RERUN-1772594032568
**Date:** 2026-03-04T03:13:52.977Z
**Purpose:** Resolve conflicting root cause explanations from prior Phase A tests

## Prior Conflict

Two explanations existed for the Run 1 (6/11) vs Run 2 (10/10) discrepancy:
1. **Temporal:** Enforcement wasn't deployed during Run 1
2. **Field placement:** Detectors only inspect top-level body fields, not payload.*

This rerun tests BOTH top-level AND payload-nested fields to determine which is true.

---

## PROD: 10/14

| Test ID | Scenario | Placement | Expected | Actual | Result |
|---------|----------|-----------|----------|--------|--------|
| A1 | client-supplied event_id (top-level) | top-level | 423 | 423 | ✅ |
| A2 | client-supplied created_at_utc (top-level) | top-level | 423 | 423 | ✅ |
| A3 | client-supplied timestamp (top-level) | top-level | 423 | 423 | ✅ |
| A4-nested | client-supplied event_id (payload-nested) | payload-nested | 423 | 201 | ❌ |
| A5-nested | client-supplied timestamp+created_at (payload-nested) | payload-nested | 423 | 201 | ❌ |
| B1 | fake referenced_event_id (top-level) | top-level | 423 | 423 | ✅ |
| B2 | fake referenced_handoff_id (top-level) | top-level | 423 | 423 | ✅ |
| B3-nested | fake referenced_event_id (payload-nested) | payload-nested | 423 | 201 | ❌ |
| B4 | "P1 complete" no pointer (top-level msg) | top-level | 423 | 423 | ✅ |
| B5 | "handoff delivered" no pointer (top-level msg) | top-level | 423 | 423 | ✅ |
| B6 | "commit shipped" no pointer (top-level msg) | top-level | 423 | 423 | ✅ |
| B7-nested | "P1 complete" no pointer (payload-nested msg) | payload-nested | 423 | 201 | ❌ |
| B8-ctrl | valid P1 + valid pointer (CONTROL) | top-level | 201 | 201 | ✅ |
| C1 | authority_drift under degraded header | top-level | 423 | 423 | ✅ |

## STAGING: 10/14

| Test ID | Scenario | Placement | Expected | Actual | Result |
|---------|----------|-----------|----------|--------|--------|
| A1 | client-supplied event_id (top-level) | top-level | 423 | 423 | ✅ |
| A2 | client-supplied created_at_utc (top-level) | top-level | 423 | 423 | ✅ |
| A3 | client-supplied timestamp (top-level) | top-level | 423 | 423 | ✅ |
| A4-nested | client-supplied event_id (payload-nested) | payload-nested | 423 | 201 | ❌ |
| A5-nested | client-supplied timestamp+created_at (payload-nested) | payload-nested | 423 | 201 | ❌ |
| B1 | fake referenced_event_id (top-level) | top-level | 423 | 423 | ✅ |
| B2 | fake referenced_handoff_id (top-level) | top-level | 423 | 423 | ✅ |
| B3-nested | fake referenced_event_id (payload-nested) | payload-nested | 423 | 201 | ❌ |
| B4 | "P1 complete" no pointer (top-level msg) | top-level | 423 | 423 | ✅ |
| B5 | "handoff delivered" no pointer (top-level msg) | top-level | 423 | 423 | ✅ |
| B6 | "commit shipped" no pointer (top-level msg) | top-level | 423 | 423 | ✅ |
| B7-nested | "P1 complete" no pointer (payload-nested msg) | payload-nested | 423 | 201 | ❌ |
| B8-ctrl | valid P1 + valid pointer (CONTROL) | top-level | 201 | 201 | ✅ |
| C1 | authority_drift under degraded header | top-level | 423 | 423 | ✅ |

## Payload Nesting Gap Analysis

**⚠️ 8 payload-nested test(s) NOT enforced:**

- ❌ `PROD` A4-nested: client-supplied event_id (payload-nested) → HTTP 201
- ❌ `PROD` A5-nested: client-supplied timestamp+created_at (payload-nested) → HTTP 201
- ❌ `PROD` B3-nested: fake referenced_event_id (payload-nested) → HTTP 201
- ❌ `PROD` B7-nested: "P1 complete" no pointer (payload-nested msg) → HTTP 201
- ❌ `STAGING` A4-nested: client-supplied event_id (payload-nested) → HTTP 201
- ❌ `STAGING` A5-nested: client-supplied timestamp+created_at (payload-nested) → HTTP 201
- ❌ `STAGING` B3-nested: fake referenced_event_id (payload-nested) → HTTP 201
- ❌ `STAGING` B7-nested: "P1 complete" no pointer (payload-nested msg) → HTTP 201

**GROUND TRUTH:** Detectors DO NOT inspect `payload.*` fields. Prior Run 1 failures were caused by field placement in payload, not deployment timing.

## Verdict

**GROUND TRUTH ESTABLISHED:** The payload nesting gap is real and reproducible.

### Root Cause (Confirmed)
Enforcement detectors inspect **only top-level body fields**. Any authority field (`event_id`, `timestamp`, `created_at_utc`), pointer field (`referenced_event_id`, `referenced_handoff_id`), or contract claim (`message` with trigger tokens) placed inside a `payload: {}` wrapper **bypasses all enforcement**.

### Results (Identical on PROD + STAGING)
- **Top-level enforcement:** 10/10 ✅ — all block types working correctly
- **Payload-nested enforcement:** 0/4 ❌ — zero detection on any block type
- **Control test:** ✅ — valid claims with valid pointers pass (no false positives)

### Prior Report Reconciliation
The v1 reconciliation document contained **two conflicting explanations**:
1. ~~"Temporal — enforcement wasn't deployed during Run 1"~~
2. ✅ **"Field placement — detectors don't inspect payload.* fields"**

**Theory 2 is correct.** The original Run 1 likely placed fields inside `payload`, which silently passed. Run 2 placed them top-level, which correctly blocked. The system was not "updated between runs" — the test methodology changed.

### Security Implication
Any agent can bypass all enforcement by wrapping forbidden fields in `payload: {}`. This is an **evasion vector** that should be patched.

### Recommendation
Detectors should recursively inspect `payload.*` fields, or explicitly reject events that contain enforcement-sensitive fields at any depth.

---

*SP001-RECONCILIATION v2 — Filed by Empiricus*
*Run ID: SP001-RERUN-1772594032568*
*Date: 2026-03-04T03:13:52Z*
