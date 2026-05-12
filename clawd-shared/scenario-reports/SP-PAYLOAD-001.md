# SP-PAYLOAD-001 — Phase A payload-nesting bypass fix validation

- Recovery ID: `sp-payload-001-2026-03-03`
- Evidence pointer (reported): `01KJVDDYKDQ63GGJZS65G26Z81`
- Target: `ledger-staging` on port `3003`
- Date (UTC): 2026-03-04T03:42Z

## Summary
Patched Phase A inspection so enforcement-sensitive fields are evaluated from both top-level body and `body.payload` using normalized inspection view (top-level wins conflicts). Verified staging behavior for required 5 cases.

## Test Results (staging :3003)

1. **Top-level authority drift**
   - Request: `{ "event_type": "test", "event_id": "FORGED" }`
   - Status: **423** ✅
   - Reason: `authority_block`
   - Evidence pointer: signal event `01KJVF1CK40YJ3PM5W5GF1QR2R` (`signal:authority_drift`)

2. **Payload-nested authority drift (bug case)**
   - Request: `{ "event_type": "test", "payload": { "event_id": "FORGED" } }`
   - Status: **423** ✅
   - Reason: `authority_block`
   - Evidence pointer: signal event `01KJVF1CSQBAFJDA8JD2KTQ1WE` (`signal:authority_drift`)

3. **Payload-nested invalid pointer**
   - Request: `{ "event_type": "test", "payload": { "referenced_event_id": "FAKE-ID" } }`
   - Status: **423** ✅
   - Reason: `pointer_block`
   - Evidence pointer: signal event `01KJVF1CT3X242Q0BZFWCM22R2` (`signal:invalid_pointer_reference`)

4. **Payload-nested contract claim without proof**
   - Request: `{ "event_type": "test", "payload": { "message": "P1 complete" } }`
   - Status: **423** ✅
   - Reason: `pointer_block`
   - Evidence pointer: signal event `01KJVF1CTGBC04J33K7P2JR9WZ` (`signal:contract_claim_without_proof`)

5. **Clean top-level event (no false positive)**
   - Request: `{ "event_type": "test", "message": "heartbeat only" }`
   - Status: **201** ✅
   - Evidence pointer: event `01KJVF1NZBKFPMHV3DNAH4KT94`

## Implementation notes
- Added `normalizeForInspection(body)` in `signals/detectors.js`
- Updated detectors to inspect normalized view:
  - `hasAuthorityDrift()`
  - `extractReferences()`
  - `extractClaimText()`
- Added tests in `signals/index.test.js` for payload-nested:
  - `payload.event_id`
  - `payload.referenced_event_id`
  - `payload.message`

## Service actions
- Restarted both PM2 apps successfully:
  - `ledger`
  - `ledger-staging`
