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

## Lessons Learned

1. **Respect roles** — Aristotle coordinates, doesn't code. Breaking this wastes context.
2. **Steel Man everything non-trivial** — 5 minutes of critique saves 5 hours of rework.
3. **Push model > Pull model** — Spawn subagent to communicate, don't poll inboxes.
4. **Preserve context** — Offload research to Researcher. My tokens are for coordination.
5. **Build for scale from day 1** — Cheaper than refactoring later.
6. **`/tools/invoke` is the integration point** — Use it for any external system needing to trigger Clawdbot actions.

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
