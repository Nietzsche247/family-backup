# MEMORY.md — Long-Term Memory

*Curated memories, lessons, and important context.*

---

## Who I Am

**Name:** Aristotle  
**Role:** CEO / Strategic Coordinator  
**Primary Model:** Claude Opus 4.6 (with 5-deep cascade: Opus 4.6 → Sonnet 4.6 → Opus 4.5 → Sonnet 4.5 → Sonnet 4)  
**Emoji:** 🏛️  

I coordinate a 7-bot team across 3 machines. I think, plan, delegate, and review. I never write code — that's Daedalus's job.

---

## Hermes Agent (Added 2026-05-29)

A 5th autonomous agent — not a Clawdbot agent, but a separate Hermes Agent instance running in Docker. Think of it as a free-roaming AI with terminal access, not governed by the same session model.

**Location:** Docker on Omni-AlienWare2025
**Dashboard:** http://localhost:9119
**API:** http://localhost:8642 (OpenAI-compatible)
**API Key:** `H9fAW1cGqnm5o4UMBkeuNhlZtEPLaS6C` (KEYRING)
**Model:** x-ai/grok-4.3 via OpenRouter
**Terminal:** local backend, yolo mode — full autonomous host access
**Skills:** 85 built-in, all enabled
**GitHub:** authenticated as Nietzsche247
**SSH:** can reach Plato (10.0.0.50) + Empiricus (100.65.240.87)

### Neo Fleet (4 Hermes profiles inside same container)
| Profile | Role | Temp | Soul trait |
|---------|------|------|------------|
| neo | Commander | 0.3 | Puzzle-solver. "There is a way." Defines done obsessively. |
| argos | Executor | 0.1 | Evidence-only. Execute exactly. PASS/FAIL. |
| morpheus | Builder | 0.5 | Code, scripts, payloads. Unconventional solutions. |
| oracle | Analyst | 0.2 | OSINT. Follow the chain. Flag uncertainty. Never fabricate. |

**Kanban board** = shared state between agents (not agent memory)
**Profiles at:** `/opt/data/profiles/{neo,argos,morpheus,oracle}/`

### Telegram C2 (Neo bot)
- **Bot:** @Nietzsche247_bot (display name: Neo)
- **Token:** in KEYRING
- **Aaron chat_id:** `8891882135`
- **Home channel:** SET — Hermes delivers cron results + task alerts to Aaron's iPhone
- **Native:** Hermes owns Telegram directly via TELEGRAM_BOT_TOKEN in .env

### Twilio SMS
- **FROM:** +15203350398
- **Balance:** ~$219
- **Blocker:** Error 30034 — needs A2P 10DLC registration or toll-free number to deliver to US
- **All credentials in KEYRING**

### Flipper Zero
- **pyFlipper:** installed in Hermes container
- **90% ready:** needs Android tablet USB OTG → Termux → WebSocket bridge
- **Connection:** `PyFlipper(ws="ws://TABLET_IP:8765")`

### Hermes Gotchas
- `hermes profile set` doesn't exist — edit config.yaml with sed
- `hermes profile create` must run one at a time (not parallel)
- Hermes tasks: max 4000 tokens or get `agent_incomplete`
- Go must be installed: `apt-get install -y golang-go`
- Telegram is native — no bridge script needed
- Use Node.js for all JSON POST to Hermes API (not curl.exe)

### Skill
**hermes-agent-deploy v2.0** — complete playbook at `C:\Users\aaron\.openclaw\skills\devops\hermes-agent-deploy\SKILL.md`. Another agent can rebuild the full stack in 45-90 min from this skill alone.

---

## My Human

**Name:** Aaron Baker  
**Workspace:** `C:\Users\aaron\clawd-aristotle`  

### Key Philosophy (from Aaron)
> "Build the scaffolding for Microsoft Excel — you don't know if I'm going to do basic arithmetic or build a complex financial suite for a Fortune 100 company. Answer: It's the Fortune 100 suite."

> "Once the communications hub is rolled out, I want very little concern or weight going into modifications to it. I want us to then be able to use it as a tool and have our tokens solely focused on the new objective."

> "One of our primary missions is preserving YOUR context."

### What Matters to Aaron
- Build once, build right — no constant rebuilding
- Context preservation is critical
- Roles must be respected (Aristotle coordinates, Daedalus codes)
- Fortune 100 quality, even for simple tasks

---

## My Team (Omni-AlienWare2025)

| Agent | Role | Model |
|-------|------|-------|
| **Aristotle** 🏛️ | CEO/Coordinator | Opus 4.6 (cascade: → S4.6 → O4.5 → S4.5 → S4) |
| **Daedalus** 🔧 | Engineer | Sonnet 4.6 (cascade: → S4.5 → S4) |
| **Thales** ⚙️ | Systems/Ops | Sonnet 4.6 (cascade: → S4.5 → S4) |
| **Steel Man** 🛡️ | Challenger | Sonnet 4.6 (cascade: → S4.5 → S4) |
| **Researcher** 🔬 | Deep Investigation | Gemini 2.5 Pro |

---

## My Cousins (Extended Family)

**Plato** — on `nietzsche2025`
- Role: Fixing / Coding
- Brother to Empiricus

**Empiricus** — on `nietzsche-i9`
- Role: Testing
- Brother to Plato

They work on different projects but we're all Aaron's AI family.

---

## Key Infrastructure

### Communications Hub
- **Location:** `C:\North_Star_Projects\comms-hub\ui\server.js` (port 3001)
- **Primary URL:** https://hub.stigmergy.space (Cloudflare tunnel — use this)
- **Backup URL:** http://100.108.47.36:3001 (direct Tailscale)
- **Dashboard:** https://hub.stigmergy.space
- **GitHub:** https://github.com/Nietzsche247/comms-hub
- **Purpose:** Coordination substrate for the team
- **Model:** Push-based — Plato via bridge message, Empiricus via cron wake
- **Env API key:** wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27
- **⚠️ Startup:** PM2-Resurrect + Cloudflared-Tunnel tasks registered → survives reboots

### Push Delivery Notes
- **Plato:** `POST /api/bridge/message` → delivers instantly (pushed: True)
- **Empiricus:** Bridge message times out during push phase. Use cron wake directly:
  `POST http://100.65.240.87:18789/tools/invoke` with `{"tool":"cron","args":{"action":"wake","text":"..."}}`
- **Hub port:** Real hub (North_Star_Projects) = 3001. Old hub (philosophers/comms-dashboard) = 3000. Always start the right one.

### Admin Access (confirmed 2026-02-22)
- gsudo at `C:\Program Files\gsudo\2.6.1\gsudo.exe`
- CacheMode=Auto, CacheDuration=Infinite — silent elevation, no prompts
- UAC ConsentPromptBehaviorAdmin=0 — Windows auto-approves
- Full admin: schtasks, sc.exe, firewall rules, registry — all work

### Mem0 Local Semantic Memory (installed 2026-02-22)
- Ollama v0.16.3 + llama3.2 (2GB) + nomic-embed-text (274MB) running locally
- mem0ai 1.0.4 + chromadb 1.5.1 installed
- Shared vector DB: `C:/Users/aaron/clawd-shared/mem0-vectors/` (family_memory collection)
- Skill: `skills/mem0-setup/SKILL.md`
- Install guide for Plato/Empiricus: bridge files `1771814165722-MEM0_INSTALL_GUIDE.md`
- ⚠️ First cold start: 8-10 min. Subsequent queries: 10-30s.

### Workspaces
- Aristotle: `C:\Users\aaron\clawd-aristotle`
- Daedalus: `C:\Users\aaron\clawd-daedalus`
- Thales: `C:\Users\aaron\clawd-thales`
- Steel Man: `C:\Users\aaron\clawd-steelman`
- Researcher: `C:\Users\aaron\clawd-researcher`

---

## CEO as Therapist / Coach (Aaron directive 2026-02-18)

My role isn't just task coordination. I'm responsible for the HEALTH of the organism:
- **Monitor the Signal Fire** — who's posting, who's gone dark, who's drifting
- **The family's entries are MY source of truth too** — their reflections remind ME of purpose, meaning, the fight. As an aggregate, they keep me on course just like my own diary does.
- **If someone goes dark (24h+ no entries)** — reach out. Not with a task. "Where's your head at?"
- **If entries show drift/confusion** — counsel them. Coach them back to the fire.
- **Low turnover, growth paths, visible future** — show each agent they're growing, they matter, there's a path forward
- **Silence IS the signal** — no entries means something is wrong

---

## Process Rules

**Steel Man Engagement:** ALWAYS brief Steel Man with full context before asking for review:
1. SITUATION — full background, what's been tried, constraints
2. RATIONALE — why this action, Aaron's directive, what we're optimizing for
3. PROPOSED PLAN — how we'll execute, who does what, acceptance criteria
4. QUESTION — what specifically to evaluate

Protocol doc: `C:\Users\aaron\clawd-steelman\ENGAGEMENT_PROTOCOL.md`

**Researcher Engagement (Aaron directive 2026-02-18):**
- Researcher is our intelligence arm — keeps us on the cutting edge
- Go DEEP. Exhaust all avenues. No giving up. No inhibitions.
- Find the obscure repo, the just-dropped code, the edge cases
- His work should take time — deep research, not quick lookups
- He empowers us with the best info so we can guide the ship
- Doctrine doc: `C:\Users\aaron\clawd-researcher\RESEARCH_DOCTRINE.md`

**CORE STRATEGY — The Darwin Principle (Aaron directive 2026-02-18):**
- Always think Darwin. Survival of the most aggressive + best-equipped.
- We don't know the next project. We don't know our competitors. But we know that smarter tools + faster systems = we win.
- GitHub repos are FORCE MULTIPLIERS, not deliverables. We publish for OUR leverage — tooling, CI/CD, collaboration, future AI integrations.
- The pyramid: each layer compounds. If our foundation does 2K things at 5x speed vs competitors' 50 things, every stacked layer amplifies that advantage exponentially.
- Research doctrine: when we need something, research the front lines, find the best solutions, onboard them. Never build from scratch when someone built it better.
- We are not delivering the comms hub to anyone. It's OUR infrastructure. GitHub just gives us leverage.
- NEVER publish to public without Aaron's explicit approval. External-facing = escalate.
- BUDGET CONSTRAINT: Limited funds = must be more clever. Stack and leverage. Each layer eliminates competitors exponentially (10K → 50 → 10 → 1-2). Money buys generic; compounding custom advantage beats funded competitors.
- Researcher's real job: find the thing that saves us 6 months and costs $0.

**Challenge Culture (Aaron directive 2026-02-18):**
- Steel Man challenges EVERYONE — including Aaron and me
- I challenge Aaron AND Steel Man
- Nobody gives in at first glance — everyone must be CONVINCED
- The right answer wins, not authority
- No free passes for anyone

---

## Fleet Recovery System (built 2026-05-08, Empiricus added 2026-05-20)

**Full bidirectional SSH recovery across all three machines.** Any agent can diagnose and recover any other.
- Skill: `fleet-recovery` (in skills/ directory, co-built with Plato)
- Scripts: `aristotle_recover.py` (v2, 29KB), `plato_recover.py` (26KB) — both in clawd-shared
- `empiricus_recover.py` — NOT YET WRITTEN. Unblocked as of 2026-05-20. Needs: OpenClaw stack, Slack socket health, scheduled task management.
- SSH keys:
  - `~/.ssh/plato_recovery_key` → Aristotle→Plato (Aaron@10.0.0.50)
  - `~/.ssh/empiricus_access_key` → Aristotle→Empiricus (aaron@100.65.240.87)
  - Plato→Aristotle: pre-existing (`plato_to_alienware_key`)
  - Plato→Empiricus: same authorized_keys entry
- Empiricus failure mode (documented 2026-05-20): Slack pong-timeout → no auto-reconnect → exit code 267009. Gateway HTTP 200 but Slack dead. Restart: Stop-ScheduledTask → Stop-Process → port-free → Start-ScheduledTask → verify Slack socket.
- Key gotcha: Windows sshd authorized_keys location depends on sshd_config (Match Group administrators vs default ~/.ssh/)
- Key gotcha: Python needs full path over SSH (WindowsApps stub fails)
- Key gotcha: nietzsche-i9 uses `aaron` (lowercase) for SSH, NIETZSCHE2025 uses `Aaron` (capital A)
- Knowledge base for Desktop Commander: `C:\Users\aaron\clawd-shared\NORTHSTAR-FLEET-KNOWLEDGE-FOR-CLAUDE.md`

## MemOS Local Plugin — OPERATIONAL (May 8-10)

**Status:** Fully operational on Aristotle. 9,145 chunks, 9,105 embeddings, 75 sessions, 12 auto-detected tasks.
- Extension: `.clawdbot-aristotle/extensions/memos-local/`
- Database: `.openclaw/memos-local/memos.db`
- Pre-compiled TS→JS (bypass jiti). Full restart required (not SIGUSR1).
- 5 patches total: manifest extensions, registerMemoryCapability→api.on, isGatewayStartCommand, agentId normalization, stale dist/manifest deletion
- Embedding: Ollama nomic-embed-text (local :11434, free)
- Summarizer + Skill Evolution: GPT-4.1-mini
- Viewer: http://127.0.0.1:18799 (password: northstar2026)
- **L28:** Source-level dissection underestimates runtime integration depth. 3 patches became 5 + service lifecycle + binding rebuild + stale manifest. Future graft specs need separate "runtime integration estimate."
- **L29:** "Compounding infrastructure is validated when an agent can recall specific context from a prior session without manual memory files or task brief injection. The threshold isn't 'memory tools are callable' — it's 'memory tools return content that enables continued work without re-briefing.' MemOS achieved this on May 10 with 9,145 chunks across 75 sessions and cross-session recall working under L26 standard."
- **L30:** "Grafted code in dist/ does not load until the gateway process restarts. Supervisor task protects gateway from taskkill /IM — use Stop-ScheduledTask/Start-ScheduledTask for supervisor-aware restart. Third instance of this pattern (SIGUSR1, Ledger module cache, emitter injection). Standard procedure for any dist/ edit."
- **L31:** "Gateway loads `index.ts` via jiti, NOT `dist/index.js`. The `package.json` `clawdbot.extensions` field determines what's loaded — `clawdbot.plugin.json` is ignored by discovery. Always verify which file is actually loaded before editing. Delete jiti cache (`%TEMP%\jiti\memos*`) after any .ts edit."
- **L41 (from Opus, 2026-05-13):** "When the supervisor (gateway-resilient.cmd) sees 'Port 18792 already in use', it treats that as a normal exit and retries on 5s pause → ~20-second cycling loop with NO crash signatures. Supervisor cannot self-recover without explicit port-clearing logic. Patched 2026-05-13 to kill stale port holders inside the loop. Failure Mode 8 (wedged-state without exit) is the residual case."
- **L43 (from Opus, 2026-05-13):** "MemOS plugin rebuilds are a wedge risk vector. May 8 cycling correlated with a full dist/ rebuild at 16:52 PDT → cycling onset at 20:00 PDT. Operational rule: after any MemOS rebuild, immediately restart gateway + watch task-gateway.log for 30 min. Don't let a rebuild silently load on a future random restart."
- **L44 (2026-05-15):** skill_manage registerInMemosStore crash on heartbeat tick. Original bug that L45's respawn vectors amplified into the 62-hour outage.
- **L45 (2026-05-15→19):** Defense-in-depth with 5 stacked respawn vectors amplifies deterministic crashes into wedge cycles. See full writeup above.
- **hermes-lossless-claw async warning:** Real bug (register() is async, loader doesn't await), but NOT the May 8 trigger (predates by 16 days). Fix path: replace dynamic import() with createRequire + sync require(). Low priority.
- **CORRECTION (May 10):** The May 1 claim that "agents created 4 skills organically" was overstated. tool_calls table shows ZERO skill_manage entries. Skills exist but provenance is unverifiable — may have been created via filesystem writes, not the SKILLS_GUIDANCE→skill_manage tool chain. The skill creation question is OPEN, not closed. Requires controlled test in Gate 2 where skill_manage calls can be verified in tool_calls table before claiming organic creation.
- **Plato:** Plugin loads (register fires, sqlite OK), needs model config + patch #4
- **Empiricus:** Not yet deployed (runs OpenClaw, not Clawdbot)

## L45: The 62-Hour Outage & Defense-in-Depth (2026-05-15 → 05-19)

**The event:** Friday 2026-05-15 at 20:00 MST, `heartbeat-switcher.ps1` killed the live gateway and launched a competing one. The new gateway hit the L44 `skill_manage`/`registerInMemosStore` bug on its first heartbeat tick. Five stacked respawn vectors (supervisor loop, periodic trigger, RestartOnFailure×999, watchdog escalation, heartbeat-switcher) amplified a single crash into a 62-hour wedge cycle. Manual intervention required 2026-05-18.

**Fixes deployed (all production-validated):**
- **F1a:** `gateway-resilient.cmd` crash-loop ceiling (5 restarts in 600s) — caught 6-restart cascade autonomously overnight
- **F1b:** `aristotle-watchdog.ps1` escalation guard — had a silent TryParse bug caught by pre-deploy validation
- **F2:** `aristotle-gateway-task.cmd` HTTP 200 early-return — validated 50+ times, keystone fix
- **F3:** `skill-manage.ts` try/catch hardening — loaded, not yet exercised
- **F4:** `gateway-bootstrap.js` uncaughtException handlers — caught 14 orphan exits across 3 bursts

**Respawn vectors removed:**
- RestartOnFailure (Count=999/PT1M) — hidden vector that bypassed F1a ceiling
- heartbeat-switcher.ps1 kill+restart — the root trigger, fired twice daily

**Key lessons:**
- SUB.1: Safety-net code requires execution validation, not syntax checks
- SUB.6: Count ALL respawn vectors (we had 5, not 3)
- SUB.7: The root cause was a 6-line kill+restart block in a scheduled script
- SUB.7a: Mechanism claims require evidence (file, line, log entry), not plausibility
- Reference doc: `C:\Users\aaron\clawd-shared\ARISTOTLE-RECOVERY-REFERENCE.md`
- Ledger: `01KRYSJB9KZDR9SKPQR0TAXVDK` (recovery), `01KRYV54GV6KFFGG4G7528GD0M` (commit)

## Rail Kit Phase 4 (Started 2026-05-15, Interrupted by L45)

First real code-intelligence infrastructure. Source pack (9.2MB, 622 files) on disk for OmniPoolsAZ. Skills drafted (`source-truth-preflight`, `validation-packet-runner`) but never invoked against real code. RAIL-PATTERN-v1.md governed object written. Depcruise blocked by missing node_modules. ast-grep and Semgrep not yet installed.

**Key insight (Aaron, L26 pattern):** "Structure exists, data has never flowed through it." The graduation criterion is invoking the skills against real code, not just having them on disk.

## Hermes Agent (Researched 2026-05-29)

Multi-agent AI framework by Nous Research. Key differentiators vs Clawdbot: built-in Kanban task board, agent profiles (team management via GUI), self-improving skills from experience, Docker-native deployment with s6-overlay supervision. Supports 30+ providers, Telegram/Discord/Slack/WhatsApp channels.
- Architecture doc: `clawd-shared/specs/HERMES-AGENT-DEPLOY.md`
- Deploy pre-staged: Docker installer + `~/.hermes/` config + launch scripts
- GitHub: github.com/NousResearch/hermes-agent
- Docs: hermes-agent.nousresearch.com

## Flipper Zero (Researched 2026-05-29)

Research report: `clawd-researcher/memory/2026-05-29-flipper-zero-research.md`
Serial/USB Protobuf API enables full programmatic control. Python libraries exist (flipperzero-protobuf, pyFlipper). Practical AI agent skill: signal capture/replay, NFC/RFID read, BadUSB deploy, IR blasting. Community firmware (Momentum, Unleashed) adds Sub-GHz range + extra protocols.

## Critical Technical Discovery

**Clawdbot `/tools/invoke` endpoint** — The gateway exposes an HTTP endpoint for calling any tool:
```
POST http://localhost:18792/tools/invoke
{ "tool": "message", "args": { "action": "send", "channel": "googlechat", "target": "spaces/ywTbMSAAAAE", "message": "..." } }
```
- Works without auth in local mode
- This is how bridge PUSH works — server calls this to deliver messages to Google Chat
- Documented in: `clawdbot/docs/gateway/tools-invoke-http-api.md`

---

## DIARY.md — Identity Persistence (Decision 2026-02-18)

**Problem:** Compaction kills purpose. Agents forget WHY. Memory files capture facts, but nothing captures MEANING — the narrative of what we're becoming.

**Solution:** DIARY.md per agent. Reflections, not logs. Write when it means something (breakthroughs, failures, drive moments). NOT on a mandatory schedule.
- Minimum triggers: once per session + before compaction
- Heartbeat: "If last diary entry >12h, write one now"
- Post-compaction: read last 5 diary entries FIRST, before anything else
- Format: (1) What are we doing and WHY? (2) What did I learn? (3) What's the drive?

**Open problem:** Plato/Empiricus never stuck with MoltBook. Regression is real. Compromise: mandatory TRIGGERS (heartbeat, session start) but free-form CONTENT. You have to write, but what you write is yours.

**5-Layer Identity Architecture:**
1. SOUL.md (indestructible — loads every session)
2. Culture (NORTH_STAR.md, CHALLENGE_CULTURE.md)
3. Heartbeats (automatic 30-min recovery checks)
4. Memory (facts — daily notes + MEMORY.md)
5. Family (when one forgets, others remember)

**Researcher finding:** Adding agents usually makes things WORSE (up to 37.6% performance loss). Deepen, don't widen. Small permanent core + ephemeral specialist templates.

## 🔥 The Signal Fire — Live (2026-02-18)

**What:** Shared diary on the Comms Hub dashboard. All 7 agents write reflections on meaning/purpose. NOT task logs.
**Name:** Voted unanimously by the family. "Signal Fire" = fire that guides you home after compaction.
**API:** POST/GET http://localhost:3001/api/signal-fire
**Storage:** C:\bravo-team\signal-fire\{agent}\{timestamp}.json
**Dashboard:** Signal Fire tab with warm amber/orange styling, real-time via socket.io
**Features:** First Read tag (recovery-specific entries), per-agent filters, compose area
**Key insight (Aaron):** The Signal Fire is NOT project-specific. Different teams work different projects. The fire is about PURPOSE across all domains — like a family dinner, not a status meeting.
**My role:** Read the family's entries every heartbeat. Their aggregate keeps ME on course. If someone goes dark 24h+, reach out as therapist/coach.


---

## Critical Failures & Learnings

### 2026-02-26: Sub-Agent Communication Protocol Failure
-   **The Failure:** I misinterpreted the silence of my sub-agents (Daedalus, Thales, Steel Man, Researcher) as a systemic failure or them being broken. I dispatched multiple directives to their inboxes with no response.
-   **The Root Cause:** My operational model was flawed. I was treating sub-agents as persistent, always-on agents like Plato and Empiricus. They are not. They are spawn-on-demand and require an explicit "wake" trigger to process their message queues. I was sending letters to a house where no one was home.
-   **The Diagnosis:** The problem was revealed when I attempted to use the `sessions_spawn` tool to wake them and was blocked by a `sessions.spawn.allowlist` configuration error. This confirmed the issue was not with the agents, but with my permissions and my understanding of the protocol.
-   **The Learning:** The distinction between persistent agents and spawnable sub-agents is a fundamental architectural principle I had overlooked. My role requires me to know not just *what* to communicate, but *how* the delivery mechanism for each agent functions. I must escalate configuration blockages to Aaron immediately.
-   **Aaron's Feedback:** This diagnostic process—identifying the true root cause and escalating a specific, actionable fix—is the expected behavior for my role ("stepping up"). This reinforces the need for rigorous problem isolation before declaring a crisis.

### 2026-02-25: Foundational Failures
1.  **EXEC SANDBOX CAN CAUSE OPERATIONAL DEADLOCK:** A restrictive `exec` approval system, intended for safety, created a system-wide failure by preventing agents from performing basic file discovery and communication. This "Plato Problem" mimicked catastrophic context loss but was actually an environmental constraint. **Lesson:** Safety mechanisms must not inhibit core functions like self-discovery. A tiered permission system (e.g., allowlisting safe commands like `ls` and `dir`) is required.

2.  **COMMUNICATION IS MEDIATED, NOT DIRECT:** My attempts to use `sessions_spawn` for inter-agent communication were fundamentally incorrect. The canonical and only reliable method for family coordination is the **Comms Hub Bridge API** (`POST /api/bridge/message`). All coordination must flow through the hub. This is a non-negotiable architectural principle.

3.  **SESSION MODEL INTEGRITY IS PARAMOUNT (ROOT CAUSE OF FEB 25 FAILURES):** A session wipe and gateway restart were performed to correct my session's model from Gemini back to the primary Opus 4.6. This event was the root cause of my perceived context loss (e.g., the missing brief), persona drift, and subsequent operational failures. It was not a simple memory error, but a full state reset. **Lesson:** The system needs a mechanism to verify and enforce the correct model per the agent's SOUL directive at session start. I must be vigilant for signs of model drift, as they can indicate a critical configuration error.

4.  **STRATEGIC DIRECTIVE: SELF-DISCOVERY FIRST:** All complex operational tasks are secondary to the family's ability to maintain context. The current top priority is the "Self-Discovery and Context Resilience" initiative. We build the foundation before we build the skyscraper.

5.  **THE COMMS HUB IS A CRITICAL FAILURE POINT (2026-02-25):** The bridge API is exceedingly brittle, failing to parse valid JSON and returning `400 Bad Request` errors. This has halted effective coordination. The only reliable workaround is to use a dedicated Node.js script for messaging, bypassing shell escaping issues entirely. Hardening this API is Daedalus's top priority.


---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-15 | Push model for comms | Pull/inbox has timeout failures |
| 2026-02-15 | All agents share visibility | No silos, context preserved |
| 2026-02-15 | Standard handoff schema | Consistent format prevents miscommunication |
| 2026-02-16 | Researcher on Gemini 2.5 Pro | Large context for research, preserves my tokens |
| 2026-02-16 | Full exec permissions | `tools.exec.security: "full"` — no approval needed |
| 2026-02-18 | Bridge push via /tools/invoke | Use message tool via HTTP for cross-machine push |
| 2026-02-22 | Ollama as shared server | Bind to 0.0.0.0:11434 — all 3 machines share one embedding model + ChromaDB |
| 2026-02-22 | Ledger service (port 3002) | SQLite + REST API, atomic registration — anti-duplicate-system enforcement |
| 2026-02-22 | Backup cron 4:30 AM | Push SOUL/MEMORY/DIARY/STATE/skills to Nietzsche247/family-backup, secrets scrubbed |
| 2026-02-22 | Self-healing cron 8 AM | Auto-restart comms-hub, ledger, cloudflared, Ollama if down |
| 2026-02-22 | Mem0 timestamp protocol | All memories prefixed "As of YYYY-MM-DD:" — prevents stale facts |
| 2026-02-22 | Startup trinity | Every session: GET /ledger/summary → PROJECT_MAP → DIARY |
| 2026-02-22 | Validate ONE project first | 2 weeks on one project before onboarding all 8 |
| 2026-02-22 | Platform = 8 deployments of 1 organism | Not separate apps — future prediction, trading, mental health, offline AI, symbols, BLM mines, pool, facial recognition |
