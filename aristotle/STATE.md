# STATE.md — Current Operational State

**Last Updated:** 2026-03-26 12:15 MST
**Updated By:** Aristotle

---

## OPERATIONAL MODE: OMNI GOVERNED EXECUTION

**NorthStar OS: FROZEN** — bugfixes and maintenance only, no new build tracks.
**OmniPools Calculator: ACTIVE** — governed execution per packet v2.0.

---

## Current Task
**Unified 4-Layer Architecture — Phase 0 Execution**

### Design Status: APPROVED
- Steel Man final review: BUILDABLE verdict (2026-04-02)
- Aristotle audit: CONCUR — all 6 spec amendments valid
- Universal capabilities amendment: DRAFTED + reviewed
- Two Phase 0→1 gate decisions documented: (1) hooks vs proxies, (2) TS-first token counter

### Phase 0 Build Status
| Deliverable | Owner | Status |
|---|---|---|
| OpenClaw fork (clone) | Daedalus | ✅ Done (11K files) |
| Baseline tag + branch | Daedalus | ✅ Done (`baseline-v0` tag, `integrate/unified-4layer` branch) |
| Codebase map | Daedalus | ✅ Done (`clawd-shared/research/openclaw-codebase-map.md`) |
| Transcript fixtures | Daedalus | ✅ Done (3 real + 3 synthetic in `openclaw-fork/test/fixtures/`) |
| Replay harness | Daedalus | ✅ Done (verified e2e, caveat: heavyweight modules hang on cold import) |
| Invariants checker | Thales | ✅ Done (tested on 34 live sessions, found ~3,200 token-bound violations) |
| Backup/restore scripts | Thales | ✅ Done (backup discovers all 7 roots + 8 workspaces, restore has WhatIf/preview) |
| Dry-run compaction CLI | Thales | ✅ Done (389K→79K on test session, 79.7% reduction, 0 new violations) |

### Phase 0 Status: ✅ COMPLETE (2026-04-02)
All deliverables delivered. Sub-agents completed successfully (were slow, not dead).

### Critical Production Finding
Invariants checker found ~3,200 token-bound violations. Sessions running to 400-490K tokens. Compaction was NOT firing. Primary Phase 1 target.

### Next: Phase 1 Gate Decisions Required
1. Hooks vs proxies for tool/model wrapping → Aristotle recommends: HOOKS
2. Single token counter strategy → Aristotle recommends: TS-first library
Aaron approval needed before Phase 1 begins.

### Key Documents (all in clawd-shared/research/)
1. unified-architecture-spec.md (v0.9)
2. unified-implementation-plan.md
3. unified-architecture-final-review.md
4. spec-amendment-universal-capabilities.md
5. spec-amendment-steelman-review.md

---

## Previous Task (Completed)
**OmniPools Track B — Intake Trigger Chain + Jurisdiction**

### DEF-TB-002: CLOSED / FIX-VERIFIED (2026-03-20)
- Stale closure in `parseCRM` (useIntake.ts) — manual corrections silently overwritten by CRM re-parse
- Fix: useRef pattern (commit 8d30b34), +11/-2 lines
- Full verification chain: Empiricus validation → Daedalus code map → Steel Man guardrails → Aristotle fix brief → Plato implementation → Daedalus review PASS → Aaron deploy → Empiricus post-deploy PASS

### DEF-TB-003: CLOSED / FIX-VERIFIED (2026-03-20)
- Cross-page rehydration failure — schema validation rejecting non-critical CRM metadata
- Fix: relaxed schema for non-critical fields (commit a059078), all 12 test steps PASS
- Parser + Trigger Contract v2.1 established as governing law

### DEF-TB-001: DAEDALUS REVIEW PASS — AWAITING DEPLOY + EMPIRICUS VALIDATION (2026-03-23)
- Jurisdiction/locality trust break — FIXED across 8 files, 4 commits
- Commits: dbe9867 (core 3-file wiring) + 5b96e7f (split-brain readers) + 38a82f8 (SI fallback removal) + 44fb951 (generateGeologyStory fix)
- Daedalus code review: ALL PASS — GO for deployment
- All jurisdiction/county consumers now use canonical `selectResolvedLocation()` output only
- No split-brain reads remain
- TB-002/TB-003/coordSource non-regression: all PASS
- Next: Aaron deploys via Lovable → Empiricus validates → governed close

Canonical brief: `C:\Users\aaron\clawd-shared\NorthStar-OmniPools-Project-Packet.md`

### Known Track A Defects (from prior observations — pending current verification)
| ID | Title | Status | Owner |
|----|-------|--------|-------|
| DEF-A01 | Auth reset loop / listSessions fetch failures | **Previously observed** — pending re-characterization in current live state | Plato |
| DEF-A02 | NULL user_id (12/18 sessions) | **Previously observed** — pending current verification | Plato |
| DEF-A03 | Session state loss on reload (schema mismatch) | **FIXED** (commit f87b41b, validated by Empiricus March 10) — pending confirmation fix is still deployed | Plato |
| DEF-A04 | Admin visibility gaps | PASS (documented March 10) — pending current verification | — |

### Launch Criteria (Track A)
| ID | Criterion | Status (last known) |
|----|-----------|---------------------|
| LC-A01 | No auth reset loops | BLOCKED (not tested) |
| LC-A02 | Session survives reload | PASS (after DEF-A03 fix) |
| LC-A03 | Intake data persists | PASS (after DEF-A03 fix) |
| LC-A04 | User identity visible | PASS |
| LC-A05 | Admin access documented | PASS |

### Track A Closure (2026-03-19)
| Item | Result |
|------|--------|
| DEF-A05 (Notes persistence) | NOT REPRODUCIBLE on prod — no fix needed |
| DEF-A01 (Auth reset loop) | RESOLVED — zero errors, root cause was DEF-A03 |
| RLS anonymous-session policy | COMMITTED (6363e3d) — awaiting Lovable deploy |
| All launch criteria | PASS (LC-A01 through LC-A05) |
| Deferred: DEF-A02, admin tooling | Later hardening |

**Status: CLOSED** — RLS deployed via Lovable 2026-03-19 19:34 EDT. Canonical event: 01KM477HBQJ6FRXH76XPWHCKTF.

## Next Task
Track C (Semantic/Field-Meaning Cleanup) — only after Track B is CLOSED.

## Infrastructure
### Admin Elevation — SOLVED (2026-03-26)
- Canonical wrapper: `C:\ProgramData\clawdbot\bin\sudo.ps1`
- All agents on AlienWare can now run pm2, net, reg commands without Aaron
- Steel Man review: `clawd-steelman/reviews/elevation-access-final-review-2026-03-26.md`
- Comms hub restarted — BLM proxy route + God-Eye config now active

## Blockers
- DEF-TB-001: Awaiting Aaron's Lovable deploy → Empiricus validation

## Governance Rules
- No canonical publication proof, no PASS
- Shared docs = truth, chat = not authoritative
- One bounded track at a time
- Governed objects (CalculatorDefect, CalculatorAssumption, LaunchCriterion) = live project state

## NorthStar OS Status (FROZEN + QUEUED)
| Track | Status | Note |
|-------|--------|------|
| A | ✅ CLOSED | Ledger persistence |
| B | ✅ CLOSED | Environment authority, shadow monitoring until April 2 |
| C | ✅ CLOSED | Tunnel supervision |
| New tracks | ❄️ FROZEN | Bugfixes/maintenance only |

### Queued: Semantic Knowledge Layer
- **Trigger:** After next major OmniPools benchmark passes
- **Scope:** pgvector + embeddings over Ledger events, memory files, governed objects, shared artifacts
- **Estimated effort:** 4 days across Daedalus + Thales
- **Project doc:** `clawd-shared/PROJECT-SEMANTIC-KNOWLEDGE-LAYER.md`
- **Database decision pending:** Separate Supabase (recommended) vs local PostgreSQL vs Lovable-owned (not recommended)
