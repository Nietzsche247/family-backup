# STATE.md — Current Project State

**Last Reviewed:** 2026-06-17
**Agent:** Aristotle

---

## CURRENT SYSTEM STATE

| System | Status | Notes |
|--------|--------|-------|
| Aristotle | ✅ Running | Port 18792, Google Chat |
| Comms Hub | ✅ Running | Port 3001, pm2 |
| Ledger | ✅ Running | Was stopped Jun 15 morning, restarted |
| Ledger-staging | ✅ Running | Port 3003 |
| Ollama | ✅ Running | v0.16.3, port 11434 |
| Plato | ✅ Running | 10.0.0.50, resilient supervisor, model fixed |
| Empiricus | ✅ Running | 100.65.240.87, resilient supervisor deployed |
| OSINT Pipeline | ✅ Updated | Empiricus port 3456, major bug fixes committed |

---

## OSINT PIPELINE — CURRENT STATE (2026-06-17)

**Location:** C:\North_Star_Projects\osint-pipeline\ on Empiricus (aaron@100.65.240.87)
**Server:** port 3456 (auto-restarts via process, not Task Scheduler)
**Latest commit:** 23b814e6 — 4 critical bugs fixed

### What was fixed (commit 23b814e6, June 16):
1. ✅ Google Dorks name disambiguation — no more wrong-person results for common names
2. ✅ NANP phone validator — dates and account IDs no longer appear as phone numbers
3. ✅ Life events fabrication eliminated — annual artifact filter added
4. ✅ Secondary email as anchor — email2/email3 now fully processed through all tools

### Remaining known issues:
- **Bug 5:** Country codes (MX/CA/EG) from breach data showing as locations → minor cleanup needed
- **Architecture gap:** Pipeline is parallel (not iterative) — doesn't chain discoveries
- **Architecture gap:** No company discovery step (email domain → company name → company search)
- **Architecture gap:** No confidence filter on content (accepts all results even if wrong person)
- Reddit: HTTP 403 (server IP ban) — pre-existing
- BERT/deep profiler: timeouts — pre-existing

### How to test:
```json
POST http://100.65.240.87:3456/api/investigate/v2
{
  "email": "michaelbaker3509@gmail.com",
  "email2": "admin@ambiancetucson.com",
  "name": "Michael Baker",
  "phone": "520-425-7272"
}
```
Expected: no fake phone numbers, relevant dork results about pool business, no fabricated life events

---

## ACTIVE PROJECTS

### Earth2 (Plato — Codex session)
- Active Codex sessions on NIETZSCHE2025
- earth1/temporal-context-spine-v0 branch committed
- Headroom removed from Codex (was causing instability)
- Access via iPhone: http://10.0.0.50:3000/cockpit

### OSINT Pipeline (Empiricus — active development)
- See bugs file: projects/osint-pipeline-bugs.md
- Next priorities: company discovery, iterative anchor expansion, country code filter

---

## INFRASTRUCTURE NOTES

### Plato (NIETZSCHE2025 — 10.0.0.50)
- Clawdbot gateway: resilient wrapper, auto-boot on startup
- Model: claude-sonnet-4-20250514 DEPRECATED → replaced with claude-sonnet-4-6
- Headroom Proxy: scheduled task exists but headroom removed from Codex config
- Codex: running directly (no proxy), System32/AGENTS.md cleaned

### Empiricus (nietzsche-i9 — 100.65.240.87)
- OpenClaw gateway: resilient wrapper, auto-boot on startup
- OSINT Pipeline: port 3456, latest bugfixes committed
- SSH key: C:\Users\aaron\.ssh\empiricus_access_key

### Aristole (AlienWare — 10.0.0.49)
- Gateway: resilient wrapper running
- Comms Hub + Ledger: pm2 managed
- Rust + VS Build Tools: installed (for headroom build if needed later)

### Model Config
- Anthropic key: sk-ant-api03-DrXI... (in config + KEYRING.md)
- Available: Opus 4.6, Opus 4.8, Sonnet 4.6, Fable 5 (suspended by govt)
- Thales: anthropic/claude-opus-4-8 (primary)

---

## FLEET ROSTER

| Agent | Machine | Port | Channel | Status |
|-------|---------|------|---------|--------|
| Aristotle | AlienWare (10.0.0.49) | 18792 | Google Chat | ✅ |
| Daedalus | AlienWare | 18800 | webchat | idle |
| Thales | AlienWare (Opus 4.8) | 18810 | — | idle |
| Plato | NIETZSCHE2025 (10.0.0.50) | 18789 | Google Chat | ✅ |
| Empiricus | Nietzsche-i9 (100.65.240.87) | 18789 | Slack | ✅ |
