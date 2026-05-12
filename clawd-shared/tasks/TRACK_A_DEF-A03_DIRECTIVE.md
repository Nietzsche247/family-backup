# Track A Governed Directive — DEF-A03 CLOSED

**Issued:** 2026-03-11 15:37 MST
**Updated:** 2026-03-11 18:50 MST (narrowed by Aaron)
**Closed:** 2026-03-11 19:28 MST (Empiricus validation PASS)
**Priority:** Resolved

---

## Governed Truth (Updated 2026-03-11 19:28 MST)

| LC | Status | Notes |
|----|--------|-------|
| LC-A01 | **BLOCKED** | Pending safe sign-in test |
| LC-A02 | **PASS** | Session and data survive reload (validated by Empiricus on production) |
| LC-A03 | **PASS** | All intake data persists: Client Name, phone, email, address, coordSource (validated by Empiricus on production) |
| LC-A04 | PASS | Admin link visible, documented |
| LC-A05 | PASS | Documented |

## DEF-A03: FIX-VERIFIED / CLOSED

**Fix:** Commit f87b41b (Plato) — cross-page key separation, schema relaxation, recovery merge, auto-save guard + Client Name persistence fix
**Validation:** Empiricus bounded production re-validation — PASS
- Client Name restores after reload ✅
- Phone/email/address restore after reload ✅
- coordSource survives reload ✅
- No false save confidence remaining ✅

---

## Remaining Track A Defects

| Defect | Status | Summary |
|--------|--------|---------|
| DEF-A03 | **CLOSED** | Save/load truth — fix-verified |
| DEF-A01 | OPEN | Fetch errors / reset-loop behavior |
| DEF-A02 | OPEN | 12/18 sessions have null user_id |
| DEF-A04 | OPEN | Admin cannot view state_json, edit/delete sessions |

## Decision Needed (Aaron)

Track A has 4/5 launch criteria passing. LC-A01 remains BLOCKED.
Options:
1. **Keep Track A open** — work DEF-A01 (fetch errors) then DEF-A02 (null user_id)
2. **Pivot to safe sign-in testing** — unblock LC-A01, determine if auth reset loop is real
3. **Close Track A with known limits** — document DEF-A01/A02/A04 as known seams, move to Track B/C/D
