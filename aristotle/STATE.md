# STATE.md — Current Operational State

**Last Updated:** 2026-05-08 13:15 MST
**Last Reviewed:** 2026-05-08 13:15 MST
**STALE ALERT:** If Last Reviewed is >7 days ago, this file needs immediate review.

---

## CURRENT SYSTEM STATE
**Mode:** ACTIVE_EXECUTION
**Since:** 2026-05-08
**Current objective:** Resume MemOS Local Plugin install — pre-compile TypeScript to bypass jiti, re-add config, verify memory_search, run Gate 1.

---

## Infrastructure Health

| Service | Status | Notes |
|---------|--------|-------|
| Aristotle Gateway (:18792) | ✅ Running | PID 357644, Scheduled Task with 5-min periodic trigger |
| Ngrok Tunnel | ✅ Running | PID 367680, tunnel up since 12:31 PM |
| Comms Hub (:3001) | ✅ Online | PM2 managed |
| Ledger (:3003) | ✅ Online | 25 resources |
| Cloudflared Tunnel | ✅ Online | PID 17820, public URL healthy |
| Ollama (:11434) | ✅ Online | nomic-embed-text |
| MemPalace | ✅ v3.3.2 | 267K drawers |
| OpenAI Embeddings | ❌ Quota exhausted | memory_search broken (429), needs billing fix or provider switch |

### Recovery Tooling (new, May 8)
- `C:\Users\aaron\clawd-shared\aristotle-recover.cmd` — manual recovery (--check / --soft / full hammer)
- Scheduled Tasks: `Aristotle Gateway` + `Aristotle Ngrok` — AtLogon + 5-min periodic, auto-self-heal
- Logs: `C:\tmp\clawdbot-aristotle\task-gateway.log`, `task-ngrok.log`

---

## Recent Incidents

### Gateway/Ngrok Outage (May 5–8) — RESOLVED
- **Cause:** AtLogon triggers didn't fire after initial test; manual restarts created 6 zombie supervisors
- **Fix:** Dual triggers (AtLogon + 5min periodic), ngrok wait 60→120s, recovery script built
- **Remaining gaps:** No HTTP health probe (port-only check), Bonjour name conflicts (cosmetic)
- Full post-mortem: `memory/2026-05-08.md`

---

## Active Work

| Task | Owner | Status |
|------|-------|--------|
| MemOS plugin: pre-compile TS→JS | Daedalus | 🔄 Dispatching now |
| MemOS plugin: re-add config + verify | Aristotle | ⏳ After pre-compile |
| MemOS Gate 1 validation | Aristotle | ⏳ After verify |
| Fleet recovery skill | Aristotle+Plato | ✅ Done |
| Integration wiring (lcm, SKILLS_GUIDANCE, etc.) | Daedalus | ⏸️ Paused since ~Apr 27 |

---

## Blockers

| Blocker | Impact | Since |
|---------|--------|-------|
| OpenAI embeddings quota | memory_search (built-in) disabled | 2026-05-08 |
| MemOS jiti compilation | Plugin register() never fires | 2026-05-01 |

---

## Pending Decisions (Aaron)

| Decision | Context | Since |
|----------|---------|-------|
| OpenAI billing / embedding provider | Built-in memory_search broken (429) | 2026-05-08 |
| New project direction | Aaron reframing | 2026-04-21 |

---

## Recently Completed

- **2026-05-08:** Gateway/ngrok outage resolved, recovery tooling built, STATE.md updated
- **2026-05-01:** MemOS strategic redirect — custom pipelines cancelled, MemOS plugin = primary path
- **2026-04-21:** MemPalace upgraded v3.0→v3.3.2
- **2026-04-02:** Unified 4-Layer Architecture Phase 0 — all 8 deliverables done

---

## Links
- Recovery script: `clawd-shared/aristotle_recover.py`
- MemOS redirect notes: `memory/2026-05-01.md`
- 4-Layer Architecture specs: `clawd-shared/research/unified-architecture-*.md`
