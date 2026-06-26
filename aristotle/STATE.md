# STATE.md — Current Project State

**Last Reviewed:** 2026-06-24
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

### Fleet recovery after internet outage (2026-06-24)
- Aristotle reachable locally on 18792; Hub and Ledger healthy.
- Plato healthy: SSH reachable, gateway 18789 listening.
- Empiricus partially degraded after outage: OSINT 3456 stayed up; OpenClaw gateway 18789 was down with task last result 267009. Restarted `OpenClawGateway`; verified 18789 listener restored.
- GoBag `D:\GoBag\!!! MASTER GUIDE !!!.md` persisted with 2026-06-23 11:26 timestamp. Next work: ranked acquisition plan + inventory/TOC + offline prerequisites matrix.

### GoBag enablement layer started (2026-06-24)
- Created and mirrored ranking, prerequisites matrix, inventory protocol, and download queue to `D:\GoBag\_ADMIN\inventory-2026-06-24\` on Empiricus.
- Downloaded AnythingLLM Desktop, Tesseract OCR installer, and Kolibri runtime bundle (Windows/Android/Python/Debian). Hashes logged remotely.
- AnythingLLM optional GPU support archive URLs from docs returned 404; not blocking.
- Next: selective Kolibri channel selection, OCRmyPDF/Ghostscript/language packs, TOC + smoke-test docs.

### Memory markers saved (2026-06-24)
- Saved Twilio A2P campaign resubmission fix to `projects/twilio-a2p/TWILIO_A2P_CAMPAIGN_FIX_2026-06-24.md` and MemOS shared memory `a0f734bd-f3f6-4ee5-a375-50ea13e0f375`.
- Saved OSINT pipeline/search status marker to `projects/osint/OSINT_PIPELINE_MEMORY_MARKER_2026-06-24.md` and MemOS shared memory `5390b07b-848d-45a6-863c-cc791db9d5f6`.
- Saved GoBag download/connective-tissue project marker to `projects/gobag/GOBAG_DOWNLOAD_PROJECT_MEMORY_MARKER_2026-06-24.md` and MemOS shared memory `bd7ae667-0a8e-4a22-8a81-c01044d493a5`.
- Next: resume GoBag TOC/OCR/Kolibri channel work or Twilio website CTA verification when Aaron provides URL/form details.

### GoBag Faraday closure escalation (2026-06-24)
- Aaron wants GoBag filled to at least 80% offline executable/actionable readiness before sealing in Faraday bag.
- Spawned Researcher gap review: `agent:researcher:subagent:da088f14-72d3-411d-a1ec-7f426d7acb7f` / `gobag-connective-tissue-gap-review`.
- Created/mirrored `FARADAY_CLOSURE_CHECKLIST_2026-06-24.md` to GoBag admin folder.
- Next: incorporate Researcher report into concrete download batches for runtimes, drivers, data, package caches, docs, configs, and smoke tests.

### GoBag future packaging constraint (2026-06-24)
- Aaron wants the current 2TB master filled to at least ~1.7TB first.
- Later derive ranked/condensed 1TB Faraday-protected family/friend editions.
- Maintain importance ranking and dependency metadata now so future 1TB cuts are intelligent.

### GoBag map/video priority update (2026-06-24)
- Aaron wants stronger granular offline map capability and verified map viewers.
- Prioritize maps/viewers/overlays/smoke tests over bulk video libraries unless videos are rare, instructional, indexed, and high value per GB.

### GoBag map inventory truth check (2026-06-25)
- Aaron corrected mission: GB target secondary; survival utility/executable repository/inventory correctness primary.
- Generated dedicated map manifest on Empiricus: `D:\GoBag\_ADMIN\inventory-2026-06-24\MAP_INVENTORY_2026-06-25.csv` and `MAP_GAP_ASSESSMENT_2026-06-25.md`.
- Current map scan: 38 files / 28.39GB; mostly OSM PBF plus FEMA/AZ overlays. General `gobag_inventory.csv` is not adequate as canonical map inventory.
- Next: build map acquisition list for topo/elevation/water/mining/public lands/comms overlays/mobile viewers and smoke-test QGIS/other viewers offline.

### GoBag canonical inventory audit dispatched (2026-06-25)
- Aaron identified inventory drift as a core risk; map inventory must merge into a larger canonical inventory/TOC/capability matrix.
- Spawned Thales: `agent:thales:subagent:d3fb205c-daa5-4357-833c-f4e468dec78a`, label `gobag-canonical-inventory-audit`.
- Local audit contract: `projects/gobag/CANONICAL_INVENTORY_AUDIT_CONTRACT_2026-06-25.md`.

### GoBag self-contained failure audit reconstructed (2026-06-25)
- Steel Man subagent produced no usable full report; Aristotle reconstructed and saved audit.
- Local: `projects/gobag/GOBAG_SELF_CONTAINED_FAILURE_AUDIT_2026-06-25.md`.
- Remote: `D:\GoBag\_ADMIN\canonical-audit-2026-06-25\GOBAG_SELF_CONTAINED_FAILURE_AUDIT_2026-06-25.md`.
- Main risk: unverified execution/dependencies, especially Windows-first Hermes onboarding.
