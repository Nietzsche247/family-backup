# NORTHSTAR NAVIGATION MAP

> **If you are reading this 3 weeks from now and lost:** start at Section 1.
> Read Section 5 (Current Phase) to know what you're working on.
> Run Section 9 (Verification) to confirm what's still alive.
> If anything in Section 9 fails, jump to Section 10 (Recovery).

**Canonical as of 2026-05-15. Supersedes prior versions.**
**Last updated:** 2026-05-15
**Updated by:** Aaron + Aristotle
**Authoritative location:** `C:\Users\aaron\clawd-shared\NORTHSTAR-NAVIGATION-MAP.md`
**Synced to:** github.com/Nietzsche247/family-backup via clawd-shared-sync

---

## 1. ONE-LINER

NorthStar OS is a multi-agent AI fleet built to solve persistent context loss.
You are currently building **Phase 2b: Skill Invocation** (making yesterday's
5 skill files actually findable + invocable by future sessions).

The end goal is: a fresh agent can boot, find its current work, invoke prior
skills, write proof to the Ledger, and produce results — **without Aaron
pasting context.** That moment is the "see it work" demo for NorthStar.

OmniPoolsAZ is a proving ground, not the product. NorthStar OS is the product.

---

## 2. WHAT'S PROVEN (touch only with care)

These survived real incidents and should not be modified casually:

| Component | Evidence of working | Location |
|---|---|---|
| **Ledger** (port 3003) | 769+ events, schema-enforced (rejected `fleet_status`, accepted `status_update`) | C:\North_Star_Projects\ledger\ledger-staging.db |

> **Ledger note:** File is named `-staging` but is the de facto production instance. 769 events. The original `ledger.db` (161 events) is a stillborn shadow - `ledger` pm2 process stopped 2026-05-15. Rename deferred - not worth the migration risk.
| **Phase 3 Bridge** (memory_chunk_id) | turnId fix landed 2026-05-13 21:00 PDT, chunks linked since | extensions/memos-local/index.ts |
| **Supervisor patch (L41)** | Survived May 14 wedge, 72-min auto-recovery | C:\Users\aaron\.clawdbot-aristotle\gateway-resilient.cmd |
| **Watchdog** | Caught 2 wedges in 2 days, escalated correctly | C:\Users\aaron\clawd-shared\aristotle-watchdog.ps1 |
| **MemOS filter v4** | 94.6% → ~3% noise, 1 leak per 30min (parked) | extensions/memos-local/index.ts isBoilerplate() |
| **Recovery scripts** | Used in production wedge recovery | clawd-shared/aristotle_recover_v2.py, clawd\scripts\plato_recover.py |
| **GitHub sync** | 3-machine fleet sync, conflict-handling, hash-detection | C:\Users\aaron\clawd-aristotle\scripts\clawd-shared-sync.ps1 (and 2 sister copies) |
| **Comms Hub** (port 3001) | Cross-agent bridge, bravo-team integration | C:\North_Star_Projects\comms-hub\ |

---

## 3. COMPONENT STATE MATRIX

Four states: **Ported** (code in place) → **Wired** (tools registered but no traffic) → **Integrated** (data flows) → **Complete** (production-grade, monitored).

### Phase 1: Infrastructure (mostly Complete)
| Component | State |
|---|---|
| Clawdbot fork | ✅ Operational |
| Ledger | ✅ Operational |
| Comms Hub | ✅ Operational |
| Recovery infrastructure (supervisor + watchdog + scripts) | ✅ Operational |
| GitHub sync (3-machine) | ✅ Operational |
| ngrok tunneling (Aristotle reserved, Plato dynamic) | ✅ Operational |

> **Operational** = stable internal use, proven through real incidents. **Complete** is reserved for product-ready external deliverables (none today).

### Phase 2: Hermes Skills (Wired, becoming Integrated in Phase 2b)
| Component | State |
|---|---|
| skill_manage (creation) | 🟡 Integrated (5 skills exist, files on disk) |
| skill_get / skill_search | 🟠 Wired (registered, cannot find files) ← **Phase 2b target** |
| skill_invocation events | ❌ Not started ← Phase 2b target |

### Phase 3: Memory Bridge (Integrated)
| Component | State |
|---|---|
| MemOS Local capture | ✅ Integrated (9,427 chunks) |
| memory_capture bridge to Ledger | ✅ Integrated |
| memory_chunk_id linkage | ✅ Integrated (turnId fix live) |
| Boilerplate filter | ✅ Integrated (~3% leak rate) |
| Sub-agent capture | 🟡 Indirect-only (parent session captures) |

### Phase 4: Rail Kit v1 (Not started)
See `NORTHSTAR_OS_RAIL_KIT_BUILD_INSTRUCTIONS.md`. Major components:
| Component | State |
|---|---|
| Repomix source-pack | ❌ Tool not installed |
| ast-grep structural patterns | ❌ Tool not installed |
| dependency-cruiser architecture map | ❌ Tool not installed |
| Semgrep guardrails | ❌ Tool not installed (requires WSL2) |
| Graphify audit | ❌ Stale since Apr 13 |
| Source-truth preflight skill | ❌ Not written |
| Deploy-truth verification skill | ❌ Not written |
| Validation packet runner skill | ❌ Not written |

> **CLARIFICATION:**
> - **Graphify** = code visualization tool (currently stale, last run Apr 13). Audit-or-retire decision pending.
> - **Graphiti / Knowledge Graph** = separate future memory layer (Phase 5+, NOT today). Easy to confuse the names; they are unrelated.

### Phase 5: Knowledge Brain (Pieces exist, not assembled)
| Component | State |
|---|---|
| Storage backend | ✅ MemOS Local (already vector + FTS) |
| Trust labels (T0-T4) | ❌ Schema designed, not applied |
| Retrieval into agent boot | ❌ Not built |
| Memory Constitution doc | ❌ Not written |

### Phase 6: Deferred (DO NOT START)
- InfraNodus integration (key exists, API never wired)
- Graphify revival (stale, audit first)
- MemPalace → Ledger bridge (palace has 267K drawers, no events flow)
- March 26 emitter family (canonical, signal.context_recall, goal.*) - paused
- Direct sub-agent agent_end hook (requires Clawdbot core change)
- Full Graphiti / Temporal / OPA / packaging

---

## 4. PAST PHASES (breadcrumb trail)

| Date | Phase | Result | Key Ledger event ID |
|---|---|---|---|
| 2026-05-08 | MemOS plugin rebuild + 5-day silent wedge | Cycling started, undiscovered | (none - silent) |
| 2026-05-13 | Phase 3 bridge schema + turnId fix | Bridge fully operational | First chunk-linked event: id=716 |
| 2026-05-13 PM | Supervisor patch (L41) + watchdog deployed | Defense-in-depth installed | (script deploy, no event) |
| 2026-05-14 AM | 72-min wedge auto-recovered | Watchdog + supervisor patches validated | (recovery, no event) |
| 2026-05-14 | Phase 2b prep: T1/T2/T3 daily tracks | 5 skills created, filter deployed, sub-agent capture confirmed indirect | `01KRMN3TG5BF9FM9GM3S8V64GX` |
| 2026-05-15 AM | Plato diagnostic + watchdog deploy + zombie reap | Chat Triage + Clawdbot Gateway tasks disabled, Plato Gateway Watchdog (SYSTEM) deployed | (no event) |
| 2026-05-15 AM | Ledger path discovery | ledger-staging.db is de facto production (769 events). ledger pm2 process stopped. | (no event) |
| 2026-05-15 T2b-1 | Hermes retrieval cracked | filesystem + MemOS store mismatch. SQL workaround applied. AT-1, AT-2 passed. | (no event) |
| 2026-05-15 T2b-2 | Skill invocation event | probe-fleet-health invoked, skill_invoked event landed | `01KRPRTFZF9GG5YXB5FB7QW7NP` |
| 2026-05-15 T2b-3 | Phase 2b COMPLETE — all 5 ATs passed | skill_invoked + fresh agent discovery confirmed | `01KRPRTFZF9GG5YXB5FB7QW7NP` |
| 2026-05-15 PM | Rail Kit tools + 2 new skills + RAIL-PATTERN-v1 | repomix+depcruise installed, source-truth-preflight + validation-packet-runner drafted | `01KRPX8TH1ZT9QEX8M8J5JYNGJ` |

---

## 5. CURRENT PHASE: Phase 2b - Skill Invocation

⚠️ **CRITICAL: NO RAIL KIT WORK UNTIL PHASE 2b PROVES SKILL INVOCATION.** Rail Kit depends on invocable skills; jumping ahead creates another pile of unmanaged tools. Phase 2b acceptance test (AT-1 through AT-5) must pass before any Rail Kit work begins, unless Aaron explicitly overrides.

**Goal:** Make yesterday's 5 skills findable and invocable. Emit `skill_invoked` events. Begin the compounding mechanism.

**The 5 skills (from T1):**

| File | Path | Search keyword |
|------|------|----------------|
| recover-aristotle-gateway | C:\Users\aaron\.openclaw\skills\ | recover |
| probe-fleet-health | C:\Users\aaron\.openclaw\skills\ | probe |
| dispatch-to-sub-agent | C:\Users\aaron\.openclaw\skills\ | dispatch |
| ledger-emit | C:\Users\aaron\.openclaw\skills\ | ledger |
| comms-hub-bridge-send | C:\Users\aaron\.openclaw\skills\ | bridge |

**Phase 2b ACCEPTANCE TEST (all 5 must pass):**
- **AT-1:** skill_search "recover" returns recover-aristotle-gateway ✅
- **AT-2:** skill_get on returned skill returns the file contents ✅
- **AT-3:** invocation of the skill runs successfully ✅
- **AT-4:** skill_invoked event lands in Ledger (payload includes skill_name + duration_ms + success) ✅
- **AT-5:** fresh agent session discovers the skill without Aaron pasting context ✅

**Out of scope today:**
- Rail Kit tool installs (overflow only, after AT-1–5 pass)
- Trust label schema deployment (design only, deploy in Phase 5)
- New skills (the existing 5 are the demo)

---

## 6. NEXT 3 PHASES

### Phase 2c: Boot Context (probable next)
**Goal:** Agent reads current state on boot without Aaron's paste.
**Components:** NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md becomes the boot packet. Per-task variant emerges. Retrieval from Ledger by recency + relevance.
**Done when:** A fresh agent session can answer "what am I working on right now" without Aaron typing.

### Phase 4: Rail Kit v1 (foundation layer)
**Goal:** Source truth + code intelligence + guardrails for code projects.
**First deliverable:** `source-truth-preflight` skill that wraps Repomix source-pack generation.
**See:** `NORTHSTAR_OS_RAIL_KIT_BUILD_INSTRUCTIONS.md` (existing doc, treat as canonical roadmap)
**Done when:** Aristotle can run `northstar source-pack OmniPoolsAZ` and get a hashed, AI-readable source bundle with a Ledger event.

### Phase 5: Knowledge Brain v0 (memory promotion)
**Goal:** Trust labels applied to MemOS chunks + Ledger events. Retrieval respects them.
**See:** `NORTHSTAR-TRUST-LABEL-SCHEMA-v1.md` (Section 8 below)
**Done when:** A query for "T1 only chunks mentioning X" returns ranked results, and `--include-recall` opens it to T3.

---

## 7. PARKING LOT (residual issues, fix when convenient)

| Item | Severity | Notes |
|---|---|---|
| Hermes skill retrieval indexing | 🔴 Active Phase 2b | Today's primary target |
| MemOS filter leaks 1/30min | 🟡 Low | Heartbeat patrol slips occasionally, isBoilerplate true offline but passed at runtime |
| `[tools] cron failed: jobId required` errors | 🟡 Low | Unmigrated caller using old `id` param |
| Skill_get/search index gap (workaround possible) | 🔴 Active | Same as top item |
| PAT rotation (leaked github_pat in 3 scripts) | 🟠 Medium | 10-min job, do before next public exposure |
| Plato watchdog | ✅ Resolved 2026-05-15 | Deployed as SYSTEM PT5M, replaces both popup tasks |
| Chat Triage Refresh Poll on Plato | ✅ Resolved 2026-05-15 | Disabled, XML saved |
| Clawdbot Gateway task on Plato | ✅ Resolved 2026-05-15 | Disabled (PT5M InteractiveToken popup), XML saved |
| 14 zombie node processes on Plato | ✅ Resolved 2026-05-15 | Killed, gateway PID 4336 still healthy |
| Aristotle Watchdog popup | ✅ Resolved 2026-05-15 | Converted from Interactive to SYSTEM (no popup) |
| Ledger filename mismatch | 🟡 Low | ledger-staging.db is de facto production. Rename when refactor is convenient. |
| R1 skill_get name lookup fails | 🟡 Low | Only UUID works. UX gap. Patch later. |
| R2 skill_manage doesn't write to MemOS store | 🟡 Medium | Workaround SQL in clawd-shared/sql/register-skill.sql. Long-term: patch hermes-lossless-claw. L44 documented. |
| Cross-agent skill discovery | 🟡 Medium | MemOS stores are per-gateway. Daedalus at :18800 has empty skills table. AT-5 passed within Aristotle's gateway only. Defer to Phase 5+. |
| Secret storage for fleet credentials | 🟡 Medium | Currently plaintext .secrets files with ACLs. Long-term: Windows Credential Manager or DPAPI-encrypted store. |
| PAT rotation | 🟠 Medium | Deferred 2026-05-15 PM. Leaked token [REDACTED_GH_FINEGRAINED]... in repo history + 3 scripts. Aaron will regenerate in GitHub UI when convenient. |

---

## 8. TRUST LABEL SCHEMA (designed, not deployed)

Full spec: `clawd-shared/governed-objects/NORTHSTAR-TRUST-LABEL-SCHEMA-v1.md`

**Five classes:**
- **T0** - Governed truth (Ledger + signed-off governed object)
- **T1** - Validated artifact (used N≥1 times or passed validation)
- **T2** - Working note (real work, not yet validated)
- **T3** - Recall candidate (semantic match, unconfirmed)
- **T4** - Untrusted input (raw external content)

**Governance rule:** T4 may never instruct without validation. Agent boot context is T0+T1 only.

**Where applied (when deployed):**
- MemOS chunks: `trust_class` column (default T3)
- Ledger events: `trust_class` column (default T1)
- Hermes skills: `trust_class` frontmatter field (default T2 on creation)

**Persistence checks (build into watchdog):**
- Daily `trust_distribution` event: T0/T1/T2/T3/T4 counts
- If >95% of yesterday's chunks are T3 default → red flag, capture pipeline isn't classifying

---

## 8.5 AUTHORITY STACK (when sources conflict, this is the order)

1. Ledger events + governed objects (T0)
2. Canonical docs (this map, NORTHSTAR-FLEET-KNOWLEDGE, recovery references)
3. Validated artifacts (T1)
4. MemOS recall (T2, T3 — semantic match candidates)
5. Agent working notes (T2)
6. Raw external input (T4 — never instructs without validation)

**Rule:** when two sources disagree, the higher item wins. If the Ledger says a skill was invoked at 14:00 but an agent note says 13:00, the Ledger wins.

---

## 9. VERIFICATION COMMANDS (run these to know what's alive)

### Aristotle health
```powershell
python C:\Users\aaron\clawd-shared\aristotle_recover_v2.py --check --json
```
Expected: `"status": "healthy"`

### Plato health
```bash
ssh -i C:\Users\Aaron\.ssh\plato_recovery_key Aaron@10.0.0.50 ^
  "python C:\Users\Aaron\clawd\scripts\plato_recover.py --check --json"
```
Expected: `"status": "healthy"`, PID 4336 uptime > 4 days as of 2026-05-15

### Ledger pulse
```python
import sqlite3
con = sqlite3.connect("file:C:/North_Star_Projects/ledger/ledger-staging.db?mode=ro", uri=True)
# Events in last 24h
con.execute("SELECT event_type, COUNT(*) FROM events WHERE created_at_utc >= datetime('now','-1 day') GROUP BY event_type").fetchall()
```
Expected at least: `memory_capture` events arriving regularly

### MemOS pulse
```python
import sqlite3
con = sqlite3.connect("file:C:/Users/aaron/.openclaw/memos-local/memos.db?mode=ro", uri=True)
# Chunks in last 24h
con.execute("SELECT COUNT(*) FROM chunks WHERE created_at >= ?", ((int(time.time())-86400)*1000,)).fetchone()
# Noise ratio (boilerplate count)
con.execute("SELECT COUNT(*) FROM chunks WHERE session_key LIKE '%heartbeat%' AND created_at >= ?", ((int(time.time())-86400)*1000,)).fetchone()
```
Expected: noise ratio < 30%

### Phase 3 bridge health
```python
# Are new memory_capture events getting memory_chunk_id populated?
con.execute("""
  SELECT COUNT(*) total, SUM(CASE WHEN memory_chunk_id IS NOT NULL THEN 1 ELSE 0 END) with_chunk
  FROM events
  WHERE event_type='memory_capture' AND created_at_utc >= datetime('now','-1 day')
""").fetchone()
```
Expected: with_chunk > 0 and ideally with_chunk / total ratio > 50%

### GitHub sync health
```powershell
Get-ScheduledTask -TaskName "Clawd-Shared Sync" | Get-ScheduledTaskInfo
```
Expected: `LastRunTime` within last 90 min, `LastTaskResult` = 0

---

## 10. RECOVERY (if you've lost the plot completely)

**Scenario: "I haven't touched this in 3 weeks and nothing seems to work."**

1. **First, don't panic.** Self-healing infrastructure runs without you. Most likely answer: everything's fine, you just need to re-read.

2. **Run all of Section 9 (Verification Commands).** Each one returns green/red. This is your dashboard.

3. **If Aristotle is wedged:**
   - `python C:\Users\aaron\clawd-shared\aristotle_recover_v2.py` (full hammer)
   - If that fails, see `C:\Users\aaron\clawd-shared\ARISTOTLE-RECOVERY-REFERENCE.md` Failure Mode 8 (the L30+L31 manual procedure)

4. **If Plato is wedged:**
   - SSH in: `ssh -i C:\Users\Aaron\.ssh\plato_recovery_key Aaron@10.0.0.50`
   - `python C:\Users\Aaron\clawd\scripts\plato_recover.py`
   - See `C:\Users\aaron\clawd-shared\PLATO-ARCHITECTURE-INFO.md`

5. **If the Ledger is empty or rejected your events:**
   - The schema is enforced. New event types must be added to schema FIRST.
   - Check `C:\North_Star_Projects\ledger\` for schema files
   - Use existing accepted types: `status_update`, `memory_capture`, `goal_declaration`, etc.

6. **If MemOS has no recent chunks:**
   - Capture is filtered, so heartbeat-only sessions produce zero. That's correct.
   - Send a real message to Aristotle via Google Chat. Wait 1 min. Re-check chunks count.

7. **If you need to re-orient on what to build next:**
   - Re-read Section 5 (Current Phase) of this doc
   - Check the last Ledger `status_update` event with subtype `daily_checkpoint`
   - That contains the latest "what's done, what's deferred"

8. **If this doc itself feels outdated:**
   - Check `git log` on family-backup repo for recent commits
   - Check `C:\tmp\clawdbot-aristotle\watchdog.log` for recent activity
   - Aristotle's recovery reference is mirrored at `C:\Users\aaron\clawd-shared\ARISTOTLE-RECOVERY-REFERENCE.md` - that doc is updated by the agents themselves and is more current than this map

---

## 11. KEY FILE INDEX

### Read these first (in order)
1. **NORTHSTAR-NAVIGATION-MAP.md** - this file
2. **NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md** - agent-facing onboarding
3. **ARISTOTLE-RECOVERY-REFERENCE.md** - Aristotle-specific
4. **PLATO-ARCHITECTURE-INFO.md** - Plato-specific
5. **NORTHSTAR_OS_RAIL_KIT_BUILD_INSTRUCTIONS.md** - long-term roadmap

### Governed objects (truth artifacts)
- `clawd-shared/governed-objects/NORTHSTAR-TRUST-LABEL-SCHEMA-v1.md`
- `clawd-shared/governed-objects/NORTHSTAR-MEMORY-CONSTITUTION.md` (not yet written)
- `clawd-shared/governed-objects/RAIL-PATTERN-v1.md` (not yet written)

### Recovery infrastructure
- `clawd-shared/aristotle_recover_v2.py`
- `clawd-shared/aristotle-watchdog.ps1`
- `clawd-shared/sync-scripts/` (per-machine sync variants)
- `clawd\scripts\plato_recover.py` (on Plato only)

### Code (what you've written)
- `extensions/memos-local/index.ts` - MemOS plugin with filter v4 + turnId emitter
- `.clawdbot-aristotle/gateway-resilient.cmd` - supervisor with L41 patch
- `clawd-aristotle/scripts/clawd-shared-sync.ps1` - sync script (and 2 sister copies)

### Logs (where to look when things break)
- `C:\tmp\clawdbot-aristotle\watchdog.log` - watchdog activity
- `C:\tmp\clawdbot-aristotle\task-gateway.log` - supervisor + gateway startup
- `C:\tmp\clawdbot\clawdbot-YYYY-MM-DD.log` - application log
- `%TEMP%\jiti\` - jiti transpiler cache. **L31 (3 prior hits):** editing index.ts has NO effect until this cache is deleted. `Remove-Item "$env:TEMP\jiti\memos*" -Force` before any gateway restart after plugin edits.
- `C:\Users\aaron\clawd-aristotle\logs\clawd-shared-sync.log` - sync log

### Databases
- `C:\North_Star_Projects\ledger\ledger-staging.db` - Ledger (de facto production, 769+ events, port 3003)
- `C:\North_Star_Projects\ledger\ledger.db` - Stillborn shadow (161 events, pm2 process stopped, forensic only)
- `C:\Users\aaron\.openclaw\memos-local\memos.db` - MemOS chunks

---

## 12. PHILOSOPHY (read when frustrated)

- "Wired is not Integrated. Integrated is not Complete." (4-state model)
- "It worked for months" → investigate what changed first (don't relitigate)
- "Plan-challenge-compress" (PP-01)
- Burden of proof is on building custom when ecosystem solutions exist
- Compounding multiplier is non-linear: early gains modest, mature operation 10-100x
- The Ledger is the truth backbone. Everything else describes it.

---

*End of map. If this is helpful, append your discoveries.*
*If this is unhelpful, replace it with something better.*
*Keep it short, keep it current.*