# STATE.md — Current Project State

**Last Reviewed:** 2026-06-03
**Agent:** Aristotle

---

## CURRENT SYSTEM STATE

| System | Status | Notes |
|--------|--------|-------|
| Aristotle | ✅ Running | Port 18792, Google Chat |
| Comms Hub | ✅ Running | Port 3001, pm2 |
| AlienWare-Hermes (Neo) | ✅ Running | @Nietzsche247_bot, stable |
| Empiricus-Hermes (Ekhart) | ⚠️ Running, Telegram unverified | @Ekhart247_bot, 0 restarts but not yet tested |
| Plato | ✅ Reachable | 10.0.0.50 |
| Empiricus | ✅ Reachable | 100.65.240.87 |
| Ledger-staging | ✅ Running | Port 3003 |

---

## FABLE DEPLOYMENT PLAN (2026-06-12 — NEXT ACTION)

**NAVIGATOR PHASE:** Aristotle (Opus 4.6) prepares OSINT project handoff
**SURGEON PHASE:** Clean session reset → Fable 5 executes to completion
**STATUS:** Navigator prep in progress — see FABLE_LAUNCH_PROMPT.md when ready

OSINT Pipeline location: C:\North_Star_Projects\osint-pipeline\ on Empiricus (aaron@100.65.240.87)
SSH key: C:\Users\aaron\.ssh\empiricus_access_key
Server: port 3456, node server.js

---

## COMPLETED THIS SESSION (2026-06-08 → 2026-06-10)

| Work | Status |
|------|--------|
| Ekhart (Empiricus Hermes) Telegram gateway | ✅ Working — gpt-4.1-mini via OpenRouter, sethome done |
| Plato CMD popup fix | ✅ Disabled old duplicate scheduled task |
| Empiricus OpenClaw model → Sonnet 4.6 | ✅ Switched from Grok 4.3 |
| Empiricus silent gateway (no popups) | ✅ Task now runs node.exe directly |
| Empiricus watchdog cron | ✅ Every 15 min, auto-restarts, alerts on failure |
| Hermes offline bundle audit | ✅ Steel Man review → Thales 3-gate patch → Aristotle final pass |
| Offline bundle: local Ollama config | ✅ config.yaml uses custom provider + qwen3.6-hermes 64K |

---

## IMMEDIATE NEXT ACTIONS (first thing after reset)

### 1. Verify Ekhart is responding
- Aaron tries `/start` in @Ekhart247_bot on Telegram
- If no reply: Check `C:\Users\aaron\.hermes\logs\gateways\default\current` on Empiricus
- If gateway log still 0 bytes: container may need another restart (current container started with `-t` flag)

### 2. If Ekhart works: /sethome
- Aaron types `/sethome` in @Ekhart247_bot to register home chat

---

## HERMES DEPLOYMENT LESSONS (apply to offline bundle + any future deploy)

| Fix | Why |
|-----|-----|
| `docker run -d -t` (`-t` flag required) | Without PTY, Hermes detects no terminal and exits cleanly. s6 restarts = crash loop. |
| `config.yaml` needs `gateway: auto_approve_local: true` | Without it, gateway service runs but doesn't start Telegram polling |
| `.env` needs `HERMES_SKIP_SETUP=true` + `TERMINAL_ENV=local` | Prevents interactive setup blocking startup |
| `.env` needs `OPENROUTER_API_KEY` | Required for cloud LLM access. The key in AlienWare .env is PAID (not free tier) |
| Model: use `openai/gpt-4.1-mini` | Free-tier models on OpenRouter all broken or don't support tool calling. Llama-3.3 hallucinates JSON tool calls. GPT-4.1-mini works reliably. |
| Gateway start: `hermes gateway run --replace` | After docker restart, gateway.pid may be stale. `--replace` bypasses it. |
| state.db corruption | If Hermes crash-loops with many restarts, delete state.db to clear corruption |
| `docker run` needs `--env-file` + `--add-host host.docker.internal:host-gateway` | .env must be loaded; host-gateway needed for Ollama |

## EKHART FIX (CRITICAL — READ THIS)
**The `-t` flag is required in docker run command for Hermes.**
Without `-t`, Hermes detects no TTY and exits cleanly. s6 restarts it → crash loop.

Working restart command (run on Empiricus if Ekhart dies):
```powershell
docker rm -f hermes
docker run -d -t --name hermes --restart unless-stopped -p 9119:9119 -p 8642:8642 -v "C:\Users\aaron\.hermes:/opt/data" --env-file "C:\Users\aaron\.hermes\.env" --add-host "host.docker.internal:host-gateway" nousresearch/hermes-agent:latest
```

---

## OSINT PIPELINE — LIVE STATUS (updated 2026-06-12)

**Pipeline location:** `C:\North_Star_Projects\osint-pipeline\` on Empiricus (aaron@100.65.240.87)
**Server:** port 3456, start with: `Start-Process node -ArgumentList 'C:\North_Star_Projects\osint-pipeline\server.js' -WindowStyle Hidden`
**API endpoint:** `POST http://localhost:3456/api/investigate/v2`
**Models:** Sonnet 4 (Pass 1/Analyst) + Opus 4.6 (Deep/Final) — both wired in enhanced-profiler.js

### COMPLETION GATES (must all pass before "Complete")
- [ ] **Gate 1** — Text box paste → parser extracts email(s), phone(s), name
- [ ] **Gate 2** — Multi-email: each email prefix → separate username (NEEDS BUILD — see below)
- [ ] **Gate 3** — Full tool run fires → legend shows what triggered vs didn't
- [ ] **Gate 4** — Output page: full info dump renders correctly (UI bugs fixed ✅)
- [ ] **Gate 5** — Sonnet 4 takes output → builds connections/story (wired, needs end-to-end test)
- [ ] **Gate 6** — Opus 4.6 takes Sonnet report + raw dump → final analysis (wired, needs test)

### NEXT BUILD TASK (highest priority)
**Multi-email → multiple usernames** (3-part change):
1. `public/index.html` parser: extract prefix from ALL emails, not just `emails[0]`
2. `server.js` `/api/investigate/v2`: accept `usernames[]` array (currently only `username` string)
3. Tools (Maigret/Sherlock/social-scan): run for each username independently
→ Assign to Daedalus. 1 session. SSH: `C:\Users\aaron\.ssh\empiricus_access_key` → `aaron@100.65.240.87`

### CHECKLIST

**✅ COMPLETE — Works Now:**
- Infrastructure: server port 3456, 22 tools registered
- Tools: EVA, WHOIS, breach-check, HudsonRock, DeHashed, Holehe, Maigret, PhoneInfoga
- Tools: Social-scan, Social-analyzer, CourtListener, AZ ROC, AZ Corp, USPS, SEC EDGAR
- Tools: Wayback (fixed), Reddit-search (fixed), Google Dorks, theHarvester
- Analysis: identity-resolver.js (syntax + logic fixes applied)
- Analysis: content-aggregator.js (extractor shapes fixed by Thales)
- Analysis: synthesizer.js (UI display bugs fixed — communicationStyle, processingTime)
- LLM: Sonnet 4 wired as Pass 1/Analyst, Opus 4.6 wired as deep model

**🔧 IMPLEMENTED — Needs End-to-End Test:**
- Free-text parser (index.html text box) — exists, needs full run smoke test
- identity-resolver single-target safety net — committed, not tested on real run
- Corroboration + provenance — wired, not verified
- Sonnet/Opus LLM chain — wired, not tested end-to-end

**⚠️ DEGRADED / NEEDS ACTION:**
- Multi-email → usernames: NOT built (see Next Build Task above)
- Searchbug: needs credits (account 12731744 at searchbug.com)
- Shodan: 0 query credits
- Thatsthem: broken on email input
- Serper/SerpAPI/Exa/PulpMiner: no keys configured

---

## ACTIVE PROJECTS

### NorthStar OS Onboarding ✅
- Daedalus + Thales: Ledger rule at TOP of SOUL.md, BOOTSTRAP.md, MEMORY.md, skill
- Hermes profiles (AlienWare): SOUL.md updated with NorthStar block
- Empiricus Hermes: NorthStar added to main SOUL.md

### Hermes Offline Bundle ✅
- Location: `C:\Users\aaron\.hermes\workspace\offline-package\`
- Empiricus copy: D:\hermes-bundle
- Model: Qwen3.6-27B (17GB, airgapped)
- hermes-authed:latest on AlienWare (41.7GB) — can delete

### SSH Fleet Wiring ✅
- AlienWare-Hermes → Empiricus: ✅ working
- Empiricus-Hermes → AlienWare: ✅ working (key in administrators_authorized_keys)

### Twilio SMS
- Campaign IN PROGRESS (~2-3 weeks for TCR approval)
- No action needed

---

## EMPIRICUS AGENT ISSUES (fix after reset)

| Issue | Severity | Fix |
|-------|----------|-----|
| OpenAI quota exhausted | HIGH | Add credits to OpenAI account with key `sk-proj-qXWO5...` (or swap key) |
| Anthropic rate limited (cooldown) | MEDIUM | Self-recovers in ~1hr |
| Memory embeddings failing (OpenAI 429) | HIGH | Depends on OpenAI credits fix |
| Slack WebSocket pong timeouts (count 101) | MEDIUM | Restart Empiricus gateway when credits restored |

Empiricus is effectively offline for AI calls until OpenAI credits added.

---

## PENDING (lower priority)
- Add structured graph field to Ledger context_capsule
- Create Empiricus Hermes Neo fleet profiles (neo/argos/morpheus/oracle)
- Delete hermes-authed:latest from AlienWare (41.7GB, not needed)
- Qwen2.5:14b pull finishing on Empiricus (switch Ekhart to it once done)

---

## FLEET ROSTER

| Agent | Machine | Port | Channel | Status |
|-------|---------|------|---------|--------|
| Aristotle | AlienWare (10.0.0.49) | 18792 | Google Chat | ✅ |
| Daedalus | AlienWare | 18800 | webchat | idle |
| Thales | AlienWare | 18810 | — | idle |
| Plato | NIETZSCHE2025 (10.0.0.50) | 18789 | Google Chat | ✅ |
| Empiricus | Nietzsche-i9 (100.65.240.87) | 18789 | Slack | ✅ |
| Neo (AlienWare-Hermes) | AlienWare | 9119/8642 | Telegram @Nietzsche247_bot | ✅ |
| Ekhart (Empiricus-Hermes) | Nietzsche-i9 | 9119/8642 | Telegram @Ekhart247_bot | ⚠️ unverified |
