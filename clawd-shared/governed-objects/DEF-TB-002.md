# DEF-TB-002 — Manual Project Address Correction Silently Overwritten by CRM Re-Parse

| Field | Value |
|---|---|
| **defect_id** | DEF-TB-002 |
| **track** | B |
| **title** | Manual Project Address correction silently overwritten by CRM re-parse |
| **reported_by** | Empiricus |
| **owner** | Plato |
| **status** | **CLOSED / FIX-VERIFIED** |
| **severity** | High |
| **closed_date** | 2026-03-20 |

## Description
CRM re-parse silently reverted manual address corrections. Designer changes address from CRM-parsed value to a different address → downstream fields propagate correctly → CRM re-parse fires (debounced auto-trigger or manual) → manual correction silently reverted to original CRM values with no warning.

## Root Cause
`src/hooks/useIntake.ts` — `parseCRM` used `useCallback(..., [])` (empty dependency array), creating a stale closure. The `hasExistingOverride` guard and `newOverrides` spread both read from the initial captured `intake.clientInfoOverrides` state, never seeing subsequent manual edits.

## Fix
**Commit:** 8d30b34 (branch: main, repo: Nietzsche247/nebula-organizer)
**Approach:** Option B — useRef pattern
- Added `clientInfoOverridesRef = useRef(intake.clientInfoOverrides)` synced on every render
- `parseCRM` reads `clientInfoOverridesRef.current` for both guard check and override spread
- `useCallback` dependency array unchanged (stable identity preserved)
- **+11/-2 lines, `src/hooks/useIntake.ts` only**

## Verification Chain
| Step | Agent | Result | Date |
|---|---|---|---|
| Validation report (pre-fix) | Empiricus | 31 PASS / 7 FAIL, defect confirmed | 2026-03-20 |
| Code review packet | Daedalus | Root cause identified | 2026-03-20 |
| Scope integrity note | Steel Man | Guardrails documented | 2026-03-20 |
| Fix brief authored | Aristotle | DEF-TB-002-FIX-BRIEF.md | 2026-03-20 |
| Implementation | Plato | Commit 8d30b34 | 2026-03-20 |
| Code review (12-point checklist) | Daedalus | PASS — all items clear | 2026-03-20 |
| Production deploy | Aaron (Lovable publish) | Deployed | 2026-03-20 |
| Post-deploy validation | Empiricus | Core fix PASS — manual correction preserved through re-parse | 2026-03-20 |

## Notes
- Bundle hash (`index-z3_wuSFN.js`) did not change post-deploy. Noted as non-blocking — runtime behavior confirms fix is active.
- Reload persistence failure observed during validation (Step 9) — determined to be a **separate pre-existing issue**, not caused by this fix. Opened as DEF-TB-003.

## Related Artifacts
- `governed-objects/DEF-TB-002-FIX-BRIEF.md`
- `governed-objects/TRACK-B-CODE-REVIEW-PACKET.md`
- `governed-objects/TRACK-B-SCOPE-INTEGRITY-NOTE.md`
- `governed-objects/TRACK-B-INTAKE-VALIDATION-2026-03-20.md`
- `governed-objects/DEF-TB-002-CODE-REVIEW.md`
