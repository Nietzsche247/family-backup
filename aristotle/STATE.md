# STATE.md — Current Project State

**Last Reviewed:** 2026-08-18
**Agent:** Aristotle

---

## CURRENT SYSTEM STATE

| System | Status | Notes |
|--------|--------|-------|
| Aristotle | ✅ Running | Port 18792, Google Chat |
| Comms Hub | ✅ Running | Port 3001, pm2, 5D uptime |
| Ledger | ✅ Running | Port 3003, pm2 |
| Ollama | ✅ Running | Port 11434 |
| Cloudflared | ✅ Running | pm2, 5D uptime |
| Plato | ✅ Running | 10.0.0.50, model = GPT-5.6 Sol (Anthropic credits exhausted) |
| Empiricus | ✅ Running | 100.65.240.87, model = GPT-5.6 Sol, gateway fixed (Slack plugin crash resolved) |
| OSINT Pipeline | ✅ Running | AlienWare localhost:3456 (migrated from Empiricus) |

---

## ACTIVE PROJECTS

### OSINT Intelligence Pipeline (PRIMARY — major work Aug 2026)
**Location:** `C:\North_Star_Projects\osint-pipeline\` on AlienWare (migrated from Empiricus)
**Server:** port 3456, runs via `node server.js`
**Status:** Running, actively being developed

**What was built (July-Aug 2026):**
- Migrated full pipeline from Empiricus to AlienWare
- Fixed missing `tools/` directory (was hidden on source machine)
- Created Python venv at `.venv/` — installs: Maigret (3,221 sites), Sherlock v0.16.0, Holehe, Blackbird (700+ sites)
- Created `tools/blackbird.js` — username + email scanner, 700+ platforms
- Updated `tools/breach-check.js` — replaced free tiers with HIBP official API
- Added `llm-passes.js` — Pass 2 (Opus 4.8, identity resolution + anchor extraction) and Pass 4 (Opus 4.8, final synthesis)
- HIBP key: `d0f2bc0257244d0899f0131ac985cf08` in `.env`
- SearchBug: `SEARCHBUG_UID=12731744`, funded with $74.73

**Pass 2 + Pass 4 architecture:**
- Pass 2 (Sonnet→Opus 4.8): Reads raw tool dump. Identity resolution via seed email as ground truth. Extracts scored anchors (Admiralty Code). Rejects wrong-person entities.
- Pass 4 (Opus 4.8): Reads both dumps, synthesizes final intelligence report with IC 3-tier confidence.
- Key guardrail added: name-only matches in state databases (AZ-ROC, corp commission) are REJECTED — must connect to seed email or phone.

**Ground truth test (2026-08-14, Michael Baker):**
- TRUE: Michigan residence, m.baker@ambiancepoolservice.com, michael@tucson-pools.com, Tucson pool contractor, Ambiance Pool Service LLC, Ambiance Pool Service & Supplies LLC
- FALSE (false positives): JMG Contracting, Baker's Remodeling, Baker Development Corp, Torrey Point Group, Oklahoma connection, Jeremy Michael Baker as son
- Root cause of false positives: AZ-ROC returns ALL Michael Bakers in AZ, not just target
- Fix committed: Pass 2 prompt now rejects name-only state database matches

**Pending on OSINT pipeline:**
- Re-run blind test after prompt fix to validate improvement
- Wire in NetworkX + spaCy + rapidfuzz (graph layer — researched, not yet installed)
- Pass 2 data wiring bug: effectiveDump may still not include allResults properly (TBD)
- Clearfront MCP assessment completed (research file: `projects/clearfront-assessment.md`)

**Research completed:**
- `projects/osint-prompt-research.md` — R.O.C.E. framework, Admiralty Code, IC 3-tier, guardrails
- `projects/osint-prompts-v1.md` — canonical Pass 2 and Pass 4 prompt text
- `projects/osint-pattern-research.md` — NetworkX, spaCy, rapidfuzz for graph layer
- `projects/anthropic-mcp-osint.md` — Clearfront MCP, WhisperGraph, Knowledge Graph MCP
- `projects/osint-v2-spec.md` — 4-pass cascading anchor discovery architecture spec

---

### Michael Baker Hermes Install (BLOCKED)
**Status:** Paused — waiting for BitDefender (GravityZone) whitelist from Mark Leinhos at PCS Arizona
**Machine:** mbslaptop, 100.65.246.83, user=mjbak
**SSH key:** `C:\Users\aaron\.ssh\michael_baker_key`
**Monitor cron:** DISABLED (paused per Aaron 2026-08-12)
**Plan:** Once whitelist approved → Docker installs → load hermes-image.tar → complete install
**Alternative path:** Get Michael a dedicated personal mini-PC (~$160 Beelink S12) — no BD jurisdiction, full agent autonomy

---

### GoBag Phase 2 (PENDING — waiting on D: drive return from Michael's machine)
**Drive status:** 2TB D: drive physically on Michael's machine (in limbo)
**When returned:**
1. Download NOMAD v1.34.0 → `D:\GoBag\09_SOFTWARE\NOMAD\`
2. Run `UPDATE_GOBAG.ps1 -Mode full`
3. Configure NOMAD → share existing Ollama instance
**Architecture:** NOMAD (content/library layer) + Hermes (agent layer) + shared Ollama
**Confirmed on drive already:** Meshtastic firmware v2.7.14, Military FMs ZIM, all major content
**NOMAD missing** from drive — to be added on reconnect
**Update cycle:** Every 4 months (Faraday bag → update → re-seal)
**Scripts:** `projects/gobag-update/UPDATE_GOBAG.ps1`, `projects/gobag-update-plan.md`

---

### MacGyver Skill (INSTALLED — fleet-wide)
**Location:** `C:\Users\aaron\.clawdbot-aristotle\skills\macgyver\`
**Also on:** Plato, Scout
**Status:** Internal fleet only (not published to ClawdHub)
**Invoke with:** "macgyver", "think smarter", "there must be a tool", "second attempt", "find the real cause"

---

## FLEET ROSTER

| Agent | Machine | Port | Model | Status |
|-------|---------|------|-------|--------|
| Aristotle | AlienWare (10.0.0.49) | 18792 | Sonnet 4.6 | ✅ |
| Plato | NIETZSCHE2025 (10.0.0.50) | 18789 | GPT-5.6 Sol | ✅ |
| Empiricus | Nietzsche-i9 (100.65.240.87) | 18789 | GPT-5.6 Sol | ✅ |

**Plato model note:** Switched from Claude Sonnet 4.6 to GPT-5.6 Sol on 2026-08-08 (Anthropic credits exhausted).
**Empiricus fix (2026-08-12):** Gateway was crashing silently — Slack plugin unhandled promise rejection. Fixed: `NODE_OPTIONS=--unhandled-rejections=warn` in gateway.cmd.

---

## BLOCKERS

| Blocker | Impact | Fix path |
|---------|--------|----------|
| Michael's BD whitelist pending | Hermes install stalled | Text Mark Leinhos with full whitelist; consider dedicated mini-PC |
| OSINT Pass 2/4 data wiring | LLM passes not appearing in reports | Debug effectiveDump flow; may need to capture allResults before writeReports |
| D: drive still at Michael's | GoBag Phase 2 blocked | Get drive back when convenient |

---

## KEY FILES

| File | Purpose |
|------|---------|
| `projects/osint-prompts-v1.md` | Pass 2 + Pass 4 canonical prompts |
| `projects/osint-v2-spec.md` | 4-pass pipeline architecture spec |
| `projects/gobag-update/UPDATE_GOBAG.ps1` | 4-month GoBag update script |
| `projects/macgyver-upgrade-review.md` | Steel Man review of MacGyver v2 |
| `C:\North_Star_Projects\osint-pipeline\llm-passes.js` | Pass 2 + 4 LLM integration |
| `C:\North_Star_Projects\osint-pipeline\tools\blackbird.js` | Blackbird wrapper |
| `C:\North_Star_Projects\osint-pipeline\tools\breach-check.js` | HIBP breach checker |
