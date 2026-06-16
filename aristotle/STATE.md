# STATE.md — Current Project State

**Last Reviewed:** 2026-06-15
**Agent:** Aristotle

---

## CURRENT SYSTEM STATE

| System | Status | Notes |
|--------|--------|-------|
| Aristotle | ✅ Running | Port 18792, Google Chat |
| Comms Hub | ✅ Running | Port 3001, pm2 (5 days up) |
| Cloudflared | ✅ Running | pm2 (5 days up) |
| Ledger | ✅ Running | Was stopped this morning, restarted. Monitor. |
| Ledger-staging | ✅ Running | Port 3003 |
| Ollama | ✅ Running | v0.16.3, port 11434 |
| Plato | ✅ Reachable | 10.0.0.50, resilient supervisor deployed |
| Empiricus | ✅ Reachable | 100.65.240.87, OpenClaw port 18789 |
| OSINT Pipeline | ✅ Complete | Empiricus port 3456, all gates passing |

---

## COMPLETED SINCE LAST STATE (2026-06-08 → 2026-06-15)

| Work | Status |
|------|--------|
| OSINT Pipeline | ✅ ALL 6 GATES PASSING — dataPointCount 246, async UI, server stable |
| Fable Protocol v3.0 | ✅ Validated on Fable 5, skill deployed to all 3 machines |
| Fable 5 (claude-fable-5) | ⚠️ Suspended by US govt directive June 12. Using Opus 4.8 as next best. |
| Anthropic API key | ✅ Added to Clawdbot config (was missing — caused all "Fable" failures) |
| claude-opus-4-8 | ✅ Added to config, Thales now runs on Opus 4.8 |
| Plato gateway-resilient.cmd | ✅ Silent restart wrapper, runs as scheduled task, auto-boot |
| OSINT async job pattern | ✅ POST returns jobId instantly, timer counts in UI |
| OSINT LAN access (iPhone) | ✅ Firewall rule added, http://10.0.0.48:3456 |
| Headroom v0.25.0 | ✅ Installed on Plato (Rust compiled). CLI at C:\Program Files\Python313\Scripts\headroom.exe |
| Headroom on Aristotle | ⚠️ pip blocked (no Windows wheel, Rust needed). Install interactively. |
| Rust/VS Build Tools | ✅ Installed on Plato (Rust 1.96.0, BuildTools) |

---

## ACTIVE PROJECTS

### Earth2 (Plato — ongoing)
- Codex session running on Earth2 Charter project
- Cockpit at http://10.0.0.50:3000/cockpit (iPhone accessible)
- Headroom wrap codex --no-serena = command to start future sessions with token compression
- Next task for Researcher: timeline visualization options (TimelineJS recommended)

### OSINT Pipeline (Empiricus — COMPLETE ✅)
- All gates pass. Server at port 3456. Reports at /api/reports/:id
- Server auto-starts via manual command (not scheduled task)
- Investigation History bug: in-memory only, not persisted across restarts
- Server crashes occasionally — uncaughtException handlers added (commit 7d79efce)

---

## IMMEDIATE NEXT ACTIONS

### 1. Headroom on Aristotle (AlienWare)
- pip install headroom-ai[proxy] fails (no Windows wheel, Rust missing)
- Fix: Install Rust, install VS Build Tools, then pip install
- Command: vs_buildtools.exe --quiet --add Microsoft.VisualStudio.Workload.VCTools
- Then: pip install "headroom-ai[proxy]"

### 2. OSINT Pipeline improvements (optional)
- Investigation History: make /api/reports load from disk on startup (not just in-memory)
- Server persistence: add to Windows Task Scheduler on Empiricus so it auto-starts on reboot

### 3. Earth2 Timeline POC (when Aaron ready)
- Recommended: TimelineJS or react-calendar-timeline + JSON data file
- Daedalus can build a POC from a sample Earth2 JSON file

---

## FLEET ROSTER

| Agent | Machine | Port | Channel | Status |
|-------|---------|------|---------|--------|
| Aristotle | AlienWare (10.0.0.49) | 18792 | Google Chat | ✅ |
| Daedalus | AlienWare | 18800 | webchat | idle |
| Thales | AlienWare (Opus 4.8) | 18810 | — | idle |
| Plato | NIETZSCHE2025 (10.0.0.50) | 18789 | Google Chat | ✅ resilient |
| Empiricus | Nietzsche-i9 (100.65.240.87) | 18789 | Slack | ✅ |

---

## KEY INFRASTRUCTURE NOTES

### Headroom (token compression)
- Plato: installed, use `headroom wrap codex --no-serena` to launch Codex through it
- AlienWare: not yet installed (pip issue)
- Proxy runs on port 8787

### Fable Protocol
- Skill v3.0 deployed to all 3 machines
- Fable 5 suspended — use Opus 4.8 as next best for Surgeon role
- Readiness check: skills/fable-completion-protocol/scripts/fable-readiness-check.ps1

### Plato Resilience
- gateway-resilient.cmd deployed (same as Aristotle pattern)
- ClawdbotGateway task: auto-boot, 3 retries, startup trigger
- Watchdog (Plato Gateway Watchdog): DISABLED — was causing popups. Do not re-enable without fixing.
- Config stack overflow on startup: known bug, Plato works through it, takes ~30s

### Model Config (Clawdbot)
- Anthropic key: sk-ant-api03-DrXI... (in config + KEYRING.md + .env)
- Models: Opus 4.6, Opus 4.8, Sonnet 4.6, Sonnet 4, Fable 5 (suspended), Gemini 2.5 Pro
- Thales primary: anthropic/claude-opus-4-8
