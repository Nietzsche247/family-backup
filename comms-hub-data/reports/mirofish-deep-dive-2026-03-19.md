# MiroFish Deep-Dive Research Report
**Date:** 2026-03-19  
**Author:** Researcher Agent (Clawdbot)  
**Requested by:** Aaron  
**Purpose:** Evaluate MiroFish for potential integration into Comms Hub alongside God-Eye (Shadowbroker)

---

## EXECUTIVE SUMMARY

**MiroFish** is a multi-agent swarm intelligence prediction engine that creates simulated social worlds populated by LLM-powered agents. Users upload "seed" documents, the system builds a knowledge graph, generates hundreds of agent personas with distinct personalities and memories, runs a dual-platform social simulation (Twitter + Reddit), and produces a prediction report on how events might unfold.

### The Honest Verdict

**MiroFish is an interesting concept with significant limitations. It is NOT a prediction engine — it is a scenario exploration sandbox.** The system produces plausible narrative scenarios, not probability-weighted predictions with confidence intervals. Real-world stress tests confirm this: when fed actual geopolitical data, it returned hedged non-answers ("oil prices could rise if tensions escalate") rather than actionable predictions.

**For our Comms Hub:** The concept has value as a "what-if" sandbox for testing narratives and exploring public opinion dynamics. But it would require significant work to integrate, the offline fork is the only viable path (no Zep Cloud dependency), and the output quality is still early-stage. **Recommendation: Wait and monitor, but don't invest build time yet.**

**Star Rating: 3/5 — Interesting concept, immature execution, not ready for production integration.**

---

## TABLE OF CONTENTS

1. [Merits Assessment](#1-merits-assessment)
2. [Community Sentiment](#2-community-sentiment)
3. [Architecture Deep-Dive](#3-architecture-deep-dive)
4. [Integration Feasibility](#4-integration-feasibility)
5. [Full File Map](#5-full-file-map)
6. [Complete Installation Instructions](#6-complete-installation-instructions)
7. [Risks and Limitations](#7-risks-and-limitations)
8. [Comparison with Existing Stack](#8-comparison-with-existing-stack)
9. [Final Recommendation](#9-final-recommendation)

---

## 1. MERITS ASSESSMENT

### What It Does Well

1. **Novel architecture**: The idea of using LLM agents to simulate social dynamics rather than fitting statistical models is genuinely innovative. It captures social contagion, opinion formation, and coalition dynamics that pure statistical models miss.
   - *Source: [DEV article by arshtechpro](https://dev.to/arshtechpro/mirofish-the-open-source-ai-engine-that-builds-digital-worlds-to-predict-the-future-ki8)*

2. **Interactive post-simulation**: You can chat with individual agents and ask them why they behaved the way they did. This is valuable for understanding narrative dynamics.
   - *Source: [English README](https://raw.githubusercontent.com/666ghj/MiroFish/main/README-EN.md)*

3. **God's-eye view**: Ability to inject new variables mid-simulation and observe how the system responds.

4. **Built on solid foundations**: OASIS (CAMEL-AI) is a peer-reviewed simulation framework published in a research paper, supporting up to 1 million agents with 23 different social actions. It's not a toy — it's real computer science research.
   - *Source: [OASIS Paper (arXiv:2411.11581)](https://arxiv.org/html/2411.11581v4)*

5. **Open-source and extensible**: AGPL-3.0 license, supports any OpenAI-compatible LLM API, has multiple community forks already.

### Where the Science Is

The underlying OASIS framework has replicated real social phenomena in peer-reviewed research:
- **Information spreading** (aligned with Vosoughi et al., 2018)
- **Group polarization** (aligned with Lindesmith et al., 1999)
- **Herd effects on Reddit** (aligned with Muchnik et al., 2013)

Scale matters: the paper found that larger agent groups produce more enhanced group dynamics and more diverse opinions. This is a scientifically grounded finding.

*Source: [OASIS Paper, Section 1 & Experiments](https://arxiv.org/html/2411.11581v4)*

### Where It's Hype

1. **"Predicting Anything" is pure marketing.** The system doesn't predict — it simulates. There is a fundamental difference. No benchmarks exist comparing MiroFish predictions against actual outcomes.
   - *Source: [LinkedIn analysis](https://www.linkedin.com/pulse/swarm-intelligence-comes-forecasting-how-mirofish-simulates-borish-lahve) — "they have not published benchmarks comparing MiroFish's predictions against historical outcomes"*

2. **LLM agents ≠ real humans.** The OASIS paper itself acknowledges that LLM agents are **more susceptible to herd behavior than real humans**. Simulated crowds polarize faster than real ones. This means the simulation systematically over-estimates consensus and under-estimates diversity.
   - *Source: [OASIS Blog](https://www.camel-ai.org/blogs/oasis) — "agents are more susceptible to herd behavior than humans"*

3. **"Predict the future" framing is irresponsible** for a v0.1 product. The dev.to caveats article nails it: "the simulations illustrate plausible scenarios based on emergent agent behavior — they're not probability estimates."
   - *Source: [DEV article caveats section](https://dev.to/arshtechpro/mirofish-the-open-source-ai-engine-that-builds-digital-worlds-to-predict-the-future-ki8)*

### Real-World Use Cases Where This Adds Value

| Use Case | Value Level | Why |
|----------|-------------|-----|
| PR crisis testing / narrative exploration | **HIGH** | Seeing how different framings play out is genuinely useful |
| Public opinion dynamics exploration | **MEDIUM** | Qualitative insights, not quantitative predictions |
| Creative writing / story exploration | **HIGH** | The Dream of the Red Chamber demo is genuinely impressive |
| Financial prediction | **LOW** | Cannot give price targets, no probability estimates |
| Geopolitical prediction | **LOW** | Stress test confirmed: produces only hedged non-answers |
| Policy impact exploration | **MEDIUM** | Useful for seeing stakeholder coalition formation |

---

## 2. COMMUNITY SENTIMENT

### GitHub Stats (as of 2026-03-19)
- **Stars:** ~28,000+ (was 27.8K on March 19, growing ~2,782/day at peak)
- **Forks:** ~3,400
- **Issues:** 185+ opened (many in Chinese)
- **Version:** 0.1.0 (released Dec 2025, only ~4 months old)
- **Trending:** Hit #1 on GitHub Global Trending on March 7, 2026
- *Source: [GitHub repo](https://github.com/666ghj/MiroFish), [ByteIota](https://byteiota.com/mirofish-githubs-1-trending-ai-swarm-engine-hits-28k-stars/)*

### The Critical Stress Test (r/developersIndia — 2 days ago)

**This is the most important data point for us.** A team stress-tested MiroFish with real geopolitical data and published their findings. Their TL;DR:

> "Let us be direct: the report told us nothing we did not already know from reading the 34 source articles."
> 
> Every prediction was hedged into meaninglessness:
> - "Oil prices could rise further if tensions escalate"
> - "The ship-by-ship arrangement may or may not hold"  
> - "India might need to consider multilateral agreements"
> - "Public opinion is divided"
>
> No probability estimates. No timelines. No scenario branching with confidence intervals. No concrete predictions that could be validated against future reality. When we directly asked for a specific oil price forecast, the system admitted it could not provide one.

*Source: [r/developersIndia post](https://www.reddit.com/r/developersIndia/comments/1rw7u7p/) — note: post was later removed by moderator but content captured*

### Reddit Sentiment
- **r/aiagents** (1 week ago): 40 upvotes, 12 comments. Mostly positive but includes a German fork contributor doing self-promotion. Comments express curiosity but no one reports actual production use.
  - *Source: [r/aiagents thread](https://www.reddit.com/r/aiagents/comments/1rou0mk/)*
- **r/SideProject** (1 day ago): Someone built a local macOS alternative "inspired by MiroFish" — suggests the concept resonates but the implementation isn't satisfying users.
  - *Source: [r/SideProject thread](https://www.reddit.com/r/SideProject/comments/1rwxh3h/)*

### Hacker News
**No MiroFish-specific thread found on HN.** The search returned zero relevant results. This is notable — HN would typically tear into the claims, and the absence suggests either the project hasn't penetrated the Western technical community deeply, or it's been dismissed.
- *Source: Web search for "MiroFish site:news.ycombinator.com" returned 0 relevant results*

### X/Twitter Community
- **@mirofish_ai** — official account
- **MiroFish Community** on X has only **8 members** — tiny
- Notable crypto/speculative hype around a "$MIROFISH" token — suggests the project is attracting the wrong kind of attention
- *Source: [X Community pages](https://x.com/i/communities/2032108733929566219)*

### Chinese Forums (Zhihu, Bilibili)

**Zhihu (Chinese Quora):**
- Multiple articles analyzing MiroFish. Key Zhihu question: "如何评价最近登顶GitHub趋势榜榜首的 MiroFish？" ("How to evaluate MiroFish?")
- Notable comment: "MiroFish didn't build from scratch. The simulation engine uses CAMEL-AI's OASIS, the LLM uses OpenAI-compatible API (recommends Alibaba's qwen-plus). One person could build this in 10 days because of this 'assembly not manufacturing' approach."
- Investment coverage: "20-year-old builds open-source project, gets 30M RMB investment from Shanda Group"
- *Source: [Zhihu question](https://www.zhihu.com/question/2014290448701679302), [Zhihu article on investment](https://zhuanlan.zhihu.com/p/2013994021857546905)*

**Bilibili (Chinese YouTube):**
- Multiple demo videos showing the Red Chamber prediction and Wuhan University opinion simulation
- Video titled "当单个AI准确率只有30%，一百万个放一起能预测什么？" ("When a single AI accuracy is only 30%, what can a million of them predict together?") — asks the right skeptical question
- *Source: [Bilibili video](https://www.bilibili.com/video/BV18sBjBRExD/)*

### Memia Newsletter (Substack — 2 days ago)
Notable quote from futurist Dimitris Dimitriadis after testing:
> "For those of us who work in strategic foresight, this is not science fiction. This is the Futures Wheel and Causal Layered Analysis translated into a live simulation engine."

But the Memia editor adds the crucial caveat:
> "I'm still not convinced it's doing much more than predicting the next token (at scale…)"

*Source: [Memia #2026.11](https://memia.substack.com/p/memia-202611-mirofish-one-trillion)*

### Blocmates (Crypto/Trading Perspective — 2 days ago)
Honest assessment:
> "The most significant challenge is validation. A simulation can produce very convincing output without being predictively accurate. When output is rich and elaborate, evaluating its validity becomes an exercise that's easier to skip than to perform."

*Source: [Blocmates](https://www.blocmates.com/articles/what-is-mirofish-the-agent-engine-that-can-predict-anything-and-everything)*

### GitHub Issues Analysis

Common problems users report:
1. **"Exception in handleNewProject: Network Error"** — Recurring issue (#57, #121) both in Docker and npm deployments. Users uploading UTF-8 txt files get network errors.
   - *Source: [Issue #57](https://github.com/666ghj/MiroFish/issues/57), [Issue #121](https://github.com/666ghj/MiroFish/issues/121)*
2. Most issues are in Chinese — barrier for non-Chinese users
3. Theoretical contributions (Issue #185: "MiroFish as a Path Integral over Social Trajectories") suggest the project attracts academics, not production users

### Community Verdict: Summary

| Signal | Finding |
|--------|---------|
| Star count | Very high (28K+) but inflated by GitHub trending + Chinese tech media |
| Real users | Very few. No production deployment reports found anywhere |
| Critical testing | The one stress test found it produces content-free hedged reports |
| Western adoption | Minimal. No HN thread. Tiny X community (8 people) |
| Chinese reception | Mixed: impressed by the concept, skeptical about "prediction" claims |
| Maturity | v0.1.0, 4 months old, rapidly iterating but not production-ready |

---

## 3. ARCHITECTURE DEEP-DIVE

### Pipeline Overview

```
[1] Seed Upload → [2] Entity Extraction → [3] Knowledge Graph (GraphRAG)
                                                    ↓
                                          [4] Agent Persona Generation
                                                    ↓
                               [5] OASIS Dual-Platform Simulation (Twitter + Reddit)
                                                    ↓
                                          [6] Graph Memory Updates
                                                    ↓
                                          [7] Report Generation (ReportAgent)
                                                    ↓
                                          [8] Interactive Chat (with any agent or ReportAgent)
```

### Detailed Pipeline Stages

#### Stage 1: Knowledge Graph Construction
- User uploads seed material (PDF, TXT, MD)
- `text_processor.py` handles file parsing with `file_parser.py` (supports PyMuPDF, charset-normalizer)
- `graph_builder.py` uses LLM to extract entities and relationships
- `ontology_generator.py` creates the ontology schema
- In main repo: data stored in **Zep Cloud** (managed knowledge graph service)
- In offline fork: data stored in **KuzuDB** (embedded) or **Neo4j** (standalone)
- GraphRAG constructs structured knowledge from flat text

#### Stage 2: Environment Setup
- `oasis_profile_generator.py` (49KB — the largest service file!) generates agent personas
- Each agent gets: personality, background, stance, opinion bias, reaction speed, influence level
- `simulation_config_generator.py` (39KB) configures simulation parameters
- An "Environment Configuration Agent" sets rules of the simulated world
- Long-term memory powered by Zep Cloud (original) or Neo4j (offline fork)

#### Stage 3: Simulation
- `simulation_runner.py` (69KB) orchestrates the simulation
- `run_parallel_simulation.py` (63KB), `run_twitter_simulation.py` (27KB), `run_reddit_simulation.py` (27KB) — the OASIS scripts
- Dual-platform: agents interact on simulated Twitter AND Reddit simultaneously
- OASIS supports 23 social actions: CREATE_POST, LIKE, REPOST, FOLLOW, COMMENT, SEARCH, MUTE, etc.
- `simulation_manager.py` handles lifecycle management
- `simulation_ipc.py` handles inter-process communication (simulation runs as subprocess)
- `zep_graph_memory_updater.py` (22KB) dynamically updates agent memory during simulation

#### Stage 4: Report Generation
- `report_agent.py` (99KB — the single largest file!) uses ReACT pattern with tool-calling
- `zep_tools.py` (66KB) provides search, interview, and analysis tools
- `zep_entity_reader.py` (15KB) reads entities from the knowledge graph
- ReportAgent can: search the knowledge graph, interview agents, perform panorama searches, run focus groups

#### Stage 5: Deep Interaction
- Chat with any individual agent (full personality + memory persists)
- Chat with ReportAgent for follow-up analysis
- Frontend components: `Step5Interaction.vue` (64KB)

### LLM Call Estimation

**This is where cost gets real.** Every stage makes LLM calls:

| Stage | LLM Calls (estimated for 100 agents, 30 rounds) |
|-------|--------------------------------------------------|
| Entity extraction from seed docs | 5-20 calls (depends on document length) |
| Ontology generation | 3-5 calls |
| Persona generation (per agent) | 100 calls (1 per agent) |
| Simulation config | 5-10 calls |
| Per-round agent actions (Twitter) | 100+ calls per round (1 per active agent) |
| Per-round agent actions (Reddit) | 100+ calls per round |
| Memory updates | 100+ calls per round |
| Report generation | 20-50 calls (searches + synthesis) |
| **TOTAL for 30 rounds** | **~6,000-10,000+ LLM calls** |

**Cost estimation with Ollama (local, free):** $0 token cost, but ~2-5 hours of GPU time on RTX 4090.

**Cost estimation with cloud API (GPT-4o-mini):** ~$3-15 per simulation run. With GPT-4o: ~$30-100+.

**The README recommends starting with <40 rounds** to manage costs.

*Source: [.env.example](https://raw.githubusercontent.com/666ghj/MiroFish/main/.env.example), [DEV article](https://dev.to/arshtechpro/mirofish-the-open-source-ai-engine-that-builds-digital-worlds-to-predict-the-future-ki8)*

### Key Dependencies

| Dependency | Role | Version | Cloud Required? |
|------------|------|---------|-----------------|
| **Zep Cloud** | Knowledge graph + agent memory | zep-cloud==3.13.0 | **YES** (main repo) |
| **KuzuDB** | Embedded graph DB | Built-in (amadad fork) | No |
| **Neo4j CE** | Graph DB | 5.15-5.18 | No (offline fork) |
| **OASIS/CAMEL-AI** | Multi-agent simulation engine | camel-oasis==0.2.5, camel-ai==0.2.78 | No |
| **Flask** | Backend web framework | >=3.0.0 | No |
| **Vue.js 3 + Vite** | Frontend | Via npm | No |
| **OpenAI SDK** | LLM client | >=1.0.0 | Configurable |
| **PyMuPDF** | PDF parsing | >=1.24.0 | No |
| **D3.js** | Graph visualization | Via npm | No |
| **Ollama** | Local LLM serving | Any | No |

### Critical Note: Zep Cloud Dependency

The **main MiroFish repo requires Zep Cloud** (a SaaS service) for:
- Agent long-term and short-term memory
- Entity extraction and relationship mining
- Graph-based knowledge storage

This is a **hard dependency** — you cannot run the main repo without a Zep API key. The free tier works for small experiments but has limits.

**The offline fork and amadad fork eliminate this dependency entirely**, replacing Zep with Neo4j or KuzuDB.

*Source: [requirements.txt](https://raw.githubusercontent.com/666ghj/MiroFish/main/backend/requirements.txt), [MiroFish-Offline README](https://github.com/nikmcfly/MiroFish-Offline)*

---

## 4. INTEGRATION FEASIBILITY

### Can This Run on Our Infrastructure?

| Question | Answer |
|----------|--------|
| Alienware hardware sufficient? | **YES** — with RTX GPU for Ollama inference |
| Ollama local (no cloud LLM)? | **YES** — via offline fork or amadad fork |
| No cloud services at all? | **YES** — offline fork eliminates Zep Cloud |
| Windows compatible? | **MOSTLY** — "macOS tested, Windows still being tested" per docs |
| Docker path available? | **YES** — docker-compose.yml in all forks |

### The Three Fork Options

#### Option A: Main Repo (666ghj/MiroFish)
- **Pros:** Most up-to-date, active development
- **Cons:** Requires Zep Cloud (SaaS), Chinese UI, recommends Alibaba Qwen
- **For us:** ❌ Not viable — Zep Cloud dependency is a non-starter

#### Option B: MiroFish-Offline (nikmcfly/MiroFish-Offline) ⭐ BEST FOR US
- **Pros:** Full English UI, Neo4j + Ollama, zero cloud deps, Docker compose includes all services
- **Cons:** May lag behind upstream, unknown maintainer dedication
- **For us:** ✅ Most viable — exactly fits our stack (Ollama + local everything)
- Hardware requirements per their docs:

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 16 GB | 32 GB |
| VRAM (GPU) | 10 GB (14b model) | 24 GB (32b model) |
| Disk | 20 GB | 50 GB |
| CPU | 4 cores | 8+ cores |

*Source: [MiroFish-Offline README](https://github.com/nikmcfly/MiroFish-Offline)*

#### Option C: Amadad Fork (amadad/mirofish)
- **Pros:** Full English, KuzuDB (embedded, no separate service), Claude/Codex CLI support, cleaner architecture
- **Cons:** More divergent from upstream, single maintainer
- **For us:** ✅ Also viable — KuzuDB means no Neo4j to manage. Claude CLI support is nice.
- *Source: [amadad/mirofish README](https://github.com/amadad/mirofish)*

### What a Hub Tab Integration Would Look Like

MiroFish exposes a Flask REST API on port 5001. Key endpoints (based on code analysis):

```
POST /api/graph/build         → Upload seed document, build knowledge graph
GET  /api/graph/status        → Check graph build progress
POST /api/simulation/start    → Start agent simulation
GET  /api/simulation/status   → Check simulation progress  
POST /api/report/generate     → Generate prediction report
GET  /api/report/status       → Check report generation
POST /api/interaction/chat    → Chat with agent or ReportAgent
```

**Integration approach:**
1. Run MiroFish-Offline as a Docker service alongside existing hub services
2. Create an iframe or API-proxied tab in the Comms Hub
3. Frontend (Vue.js on port 3000) could be embedded or we build our own frontend hitting the API
4. Backend API (port 5001) would need CORS configuration for hub access

**Estimated integration effort:** 2-4 days for basic iframe embed, 1-2 weeks for native API integration with custom UI.

### Resource Requirements for Our Alienware

| Resource | Required | Our Alienware Has |
|----------|----------|-------------------|
| GPU VRAM | 10-24 GB | ✅ Likely sufficient (check exact GPU) |
| RAM | 16-32 GB | ✅ Should have this |
| Disk | 20-50 GB | ✅ Plenty |
| Neo4j | 2 GB heap | ✅ Covered by RAM |
| Ollama models | ~20-40 GB disk per model | Check disk space |

---

## 5. FULL FILE MAP

### Main Repository (666ghj/MiroFish)

```
MiroFish/
├── .dockerignore                  # Docker build exclusions
├── .env.example                   # Environment variable template (LLM + Zep keys)
├── .github/
│   └── workflows/
│       └── docker-image.yml       # CI/CD for Docker image builds
├── .gitignore
├── Dockerfile                     # Single Docker image (frontend + backend)
├── LICENSE                        # AGPL-3.0
├── README.md                      # Chinese documentation
├── README-EN.md                   # English documentation
├── package.json                   # Root package.json (orchestrates frontend + backend)
├── package-lock.json
├── docker-compose.yml             # Simple compose (single mirofish container)
│
├── backend/
│   ├── pyproject.toml             # Python project config (uv)
│   ├── requirements.txt           # Python dependencies
│   ├── uv.lock                    # uv lockfile (570KB — lots of deps)
│   ├── run.py                     # Flask app entry point
│   │
│   ├── app/
│   │   ├── __init__.py            # Flask app factory (2.7KB)
│   │   ├── config.py              # Configuration loader (2.7KB)
│   │   │
│   │   ├── api/                   # Flask REST API endpoints
│   │   │   ├── __init__.py        # Blueprint registration
│   │   │   ├── graph.py           # Graph build endpoints (20KB) ★
│   │   │   ├── simulation.py      # Simulation control endpoints (95KB) ★★★
│   │   │   └── report.py          # Report generation endpoints (30KB) ★★
│   │   │
│   │   ├── models/                # Data models
│   │   │   ├── __init__.py
│   │   │   ├── project.py         # Project/session model (9.6KB)
│   │   │   └── task.py            # Async task model (5.6KB)
│   │   │
│   │   ├── services/              # Core business logic ★★★
│   │   │   ├── __init__.py        # Service initialization (1.8KB)
│   │   │   ├── graph_builder.py   # Knowledge graph construction (18KB) ★★
│   │   │   ├── ontology_generator.py  # Ontology schema generation (16KB)
│   │   │   ├── oasis_profile_generator.py  # Agent persona generation (49KB) ★★★
│   │   │   ├── simulation_config_generator.py  # Sim parameter config (39KB) ★★
│   │   │   ├── simulation_runner.py    # OASIS simulation orchestration (69KB) ★★★
│   │   │   ├── simulation_manager.py   # Sim lifecycle management (20KB)
│   │   │   ├── simulation_ipc.py       # Inter-process communication (12KB)
│   │   │   ├── report_agent.py         # ReACT report agent (99KB) ★★★★ LARGEST FILE
│   │   │   ├── text_processor.py       # Document text processing (1.7KB)
│   │   │   ├── zep_entity_reader.py    # Zep graph entity reader (15KB) ★
│   │   │   ├── zep_graph_memory_updater.py  # Dynamic memory updates (22KB) ★★
│   │   │   └── zep_tools.py            # Zep search/analysis tools (66KB) ★★★
│   │   │
│   │   └── utils/                 # Utility modules
│   │       ├── __init__.py
│   │       ├── file_parser.py     # PDF/TXT/MD file parsing (5.2KB)
│   │       ├── llm_client.py      # LLM API client wrapper (3KB)
│   │       ├── logger.py          # Logging configuration (3.3KB)
│   │       ├── retry.py           # Retry logic for API calls (7.5KB)
│   │       └── zep_paging.py      # Zep API pagination helper (4.5KB)
│   │
│   └── scripts/                   # OASIS simulation scripts
│       ├── action_logger.py       # Agent action logging (10KB)
│       ├── run_parallel_simulation.py   # Dual-platform sim (63KB) ★★★
│       ├── run_twitter_simulation.py    # Twitter-only sim (27KB)
│       ├── run_reddit_simulation.py     # Reddit-only sim (27KB)
│       └── test_profile_format.py       # Profile format testing (5.9KB)
│
├── frontend/
│   ├── index.html                 # HTML entry point
│   ├── package.json               # Frontend deps (Vue 3, Vite, D3.js)
│   ├── package-lock.json
│   ├── vite.config.js             # Vite build configuration
│   │
│   ├── public/
│   │   └── icon.png               # App icon
│   │
│   └── src/
│       ├── App.vue                # Root Vue component
│       ├── main.js                # Vue app entry point
│       │
│       ├── api/                   # API client layer
│       │   ├── index.js           # Base API config + project endpoints
│       │   ├── graph.js           # Graph API calls
│       │   ├── simulation.js      # Simulation API calls
│       │   └── report.js          # Report API calls
│       │
│       ├── assets/
│       │   └── logo/              # Logo images
│       │
│       ├── components/            # Vue components (the UI) ★★★
│       │   ├── GraphPanel.vue     # Knowledge graph visualization (40KB) — uses D3.js
│       │   ├── HistoryDatabase.vue # Project history database (34KB)
│       │   ├── Step1GraphBuild.vue # Step 1: Upload & graph build UI (18KB)
│       │   ├── Step2EnvSetup.vue   # Step 2: Environment/agent setup UI (69KB) ★★★
│       │   ├── Step3Simulation.vue # Step 3: Simulation monitoring UI (39KB)
│       │   ├── Step4Report.vue     # Step 4: Report display UI (145KB) ★★★★ LARGEST FRONTEND
│       │   └── Step5Interaction.vue # Step 5: Agent chat UI (64KB) ★★★
│       │
│       ├── views/                 # Page-level views
│       │   ├── Home.vue           # Landing page (20KB)
│       │   ├── MainView.vue       # Main dashboard (15KB)
│       │   ├── Process.vue        # Multi-step process view (52KB) ★★
│       │   ├── InteractionView.vue # Agent chat page (8.7KB)
│       │   ├── ReportView.vue     # Report display page (8.5KB)
│       │   ├── SimulationView.vue # Simulation overview (11KB)
│       │   └── SimulationRunView.vue # Active simulation view (12KB)
│       │
│       ├── router/
│       │   └── index.js           # Vue Router configuration
│       │
│       └── store/
│           └── pendingUpload.js   # Upload state management
│
└── static/
    └── image/                     # Static images
        ├── MiroFish_logo.jpeg     # Full logo (3.7MB)
        ├── MiroFish_logo_compressed.jpeg  # Compressed logo
        ├── QQ群.png               # QQ group QR code
        ├── shanda_logo.png        # Shanda Group logo
        ├── 武大模拟演示封面.png    # Wuhan Univ demo thumbnail
        ├── 红楼梦模拟推演封面.jpg  # Red Chamber demo thumbnail
        └── Screenshot/            # App screenshots (Chinese text)
            ├── 运行截图1.png
            ├── 运行截图2.png
            ├── 运行截图3.png
            ├── 运行截图4.png
            ├── 运行截图5.png
            └── 运行截图6.png
```

**★ ratings = complexity/importance for understanding the codebase**

### Key File Sizes (tells the story of where the complexity lives)

| File | Size | What it tells us |
|------|------|-----------------|
| `report_agent.py` | 99 KB | ReportAgent is the most complex component |
| `simulation.py` (API) | 95 KB | Simulation endpoints are thick |
| `simulation_runner.py` | 69 KB | OASIS orchestration is complex |
| `zep_tools.py` | 66 KB | Heavy Zep integration |
| `run_parallel_simulation.py` | 63 KB | The actual simulation logic |
| `oasis_profile_generator.py` | 49 KB | Agent persona generation is elaborate |
| `Step4Report.vue` | 145 KB | Report UI is the largest frontend file |
| `Step2EnvSetup.vue` | 69 KB | Environment setup UI is complex |

*Source: [GitHub API tree endpoint](https://api.github.com/repos/666ghj/MiroFish/git/trees/main?recursive=1)*

---

## 6. COMPLETE INSTALLATION INSTRUCTIONS

### Path A: MiroFish-Offline (RECOMMENDED FOR US)

This is the path we should take. Zero cloud dependencies, English UI, Neo4j + Ollama.

#### Prerequisites (Windows / Alienware)
```powershell
# Verify prerequisites
node -v          # Need 18+
python --version # Need 3.11-3.12
ollama --version # Need Ollama installed

# If you need to install uv (Python package manager):
pip install uv
```

#### Option 1: Docker (Easiest)
```powershell
# 1. Clone the repo
git clone https://github.com/nikmcfly/MiroFish-Offline.git
cd MiroFish-Offline

# 2. Copy and configure environment
copy .env.example .env
# Edit .env — defaults are fine for local Ollama + Neo4j

# 3. Start all services (Neo4j, Ollama, MiroFish)
docker compose up -d

# 4. Pull required models into Ollama
docker exec mirofish-ollama ollama pull qwen2.5:32b
docker exec mirofish-ollama ollama pull nomic-embed-text

# 5. Wait for Neo4j to be healthy (check with)
docker compose logs neo4j

# 6. Open http://localhost:3000
```

**Docker Compose Services:**
- `mirofish-offline` — Frontend (3000) + Backend (5001)
- `mirofish-neo4j` — Neo4j CE 5.18 (7474 browser, 7687 bolt)
- `mirofish-ollama` — Ollama with GPU passthrough (11434)

#### Option 2: Manual (Use Existing Ollama at localhost:11434)
```powershell
# 1. Clone the repo
git clone https://github.com/nikmcfly/MiroFish-Offline.git
cd MiroFish-Offline

# 2. Start Neo4j (if not running)
docker run -d --name neo4j `
  -p 7474:7474 -p 7687:7687 `
  -e NEO4J_AUTH=neo4j/mirofish `
  neo4j:5.15-community

# 3. Pull Ollama models (Ollama already running at localhost:11434)
ollama pull qwen2.5:32b       # Main LLM (or qwen2.5:14b for less VRAM)
ollama pull nomic-embed-text   # Embeddings

# 4. Configure environment
copy .env.example .env
# .env should already have correct defaults:
# LLM_API_KEY=ollama
# LLM_BASE_URL=http://localhost:11434/v1
# LLM_MODEL_NAME=qwen2.5:32b
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=mirofish
# EMBEDDING_MODEL=nomic-embed-text
# EMBEDDING_BASE_URL=http://localhost:11434

# 5. Install backend dependencies
cd backend
pip install -r requirements.txt
# Or with uv:
# uv sync
cd ..

# 6. Install frontend dependencies
cd frontend
npm install
cd ..

# 7. Start backend
cd backend
python run.py
# (In a separate terminal:)

# 8. Start frontend
cd frontend
npm run dev

# 9. Open http://localhost:3000
```

#### .env Configuration for Our Environment
```env
# LLM — points to local Ollama
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=qwen2.5:32b
# For lighter VRAM: LLM_MODEL_NAME=qwen2.5:14b

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=mirofish

# Embeddings
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_BASE_URL=http://localhost:11434

# OASIS/CAMEL-AI (reads OpenAI env vars)
OPENAI_API_KEY=ollama
OPENAI_API_BASE_URL=http://localhost:11434/v1
```

### Path B: Main Repo (NOT RECOMMENDED — requires Zep Cloud)

```powershell
git clone https://github.com/666ghj/MiroFish.git
cd MiroFish
copy .env.example .env

# Edit .env:
# LLM_API_KEY=ollama
# LLM_BASE_URL=http://localhost:11434/v1
# LLM_MODEL_NAME=qwen2.5:32b
# ZEP_API_KEY=<get from https://app.getzep.com/>  ← CLOUD DEPENDENCY

npm run setup:all
npm run dev
```

### Path C: Amadad Fork (Alternative — KuzuDB embedded, no Neo4j needed)

```powershell
git clone https://github.com/amadad/mirofish.git
cd mirofish
copy .env.example .env

# Edit .env:
# LLM_PROVIDER=openai  (or claude-cli / codex-cli)
# LLM_API_KEY=ollama
# LLM_BASE_URL=http://localhost:11434/v1
# LLM_MODEL_NAME=qwen2.5:32b

npm run setup:all
npm run dev
```

---

## 7. RISKS AND LIMITATIONS

### License: AGPL-3.0 ⚠️

**This is the most restrictive popular open-source license.**

- ✅ Free to use, modify, and self-host
- ✅ Internal use is fine (no distribution = no obligation)
- ⚠️ **If we expose MiroFish over a network** (which we would in the Comms Hub), we would technically need to make our source code available to users
- ⚠️ Any modifications we make must be released under AGPL-3.0 if the service is network-accessible
- ❌ Cannot incorporate into proprietary software and distribute it

**Practical impact for us:** As long as we're using it internally (our team only), AGPL-3.0 is fine. If we ever expose it to external users, we'd need to comply.

*Source: [LICENSE file](https://raw.githubusercontent.com/666ghj/MiroFish/main/LICENSE) — GNU Affero General Public License v3*

### Data Privacy Concerns

| Concern | Severity | Notes |
|---------|----------|-------|
| Zep Cloud sends data to external servers | **HIGH** | Main repo sends seed docs + agent memory to Zep Cloud (SaaS). **Use offline fork to avoid.** |
| LLM API sends data to cloud | **HIGH if cloud** | Use Ollama local to keep all data on-premises |
| Seed documents may contain sensitive data | **MEDIUM** | User responsibility, but the system processes everything through LLM |
| Agent personas derived from real entities | **LOW** | Simulation generates fictional agents, not real identity profiles |

### Maturity Level

- **Version:** 0.1.0 (released December 2025)
- **Age:** ~4 months
- **Commits:** Active but rapidly changing
- **Tests:** No test suite visible in the repo (no `tests/` directory)
- **Documentation:** README only, no API docs, no architecture docs
- **Error handling:** Reports of "Network Error" in basic operations (Issue #57, #121)

### Bus Factor

- **Creator:** Guo Hangjiang (郭航江), aka BaiFu, senior undergraduate at Beijing University of Posts and Telecommunications
- **Backed by:** Shanda Group (30M RMB / $4.1M investment)
- **Team size:** Small — hiring for full-time/intern positions (suggests <5 people currently)
- **Bus factor:** **1-2** — effectively one developer with corporate backing
- **Risk:** High star count + tiny team = maintenance burden risk

*Source: [Memia newsletter](https://memia.substack.com/p/memia-202611-mirofish-one-trillion), [blocmates](https://www.blocmates.com/articles/what-is-mirofish-the-agent-engine-that-can-predict-anything-and-everything)*

### Chinese-Language Barriers

| Area | Chinese? | Impact |
|------|----------|--------|
| Main README | Yes (English available separately) | Low |
| Code comments | Partially Chinese | Medium |
| .env.example comments | All Chinese | Low (use offline fork) |
| Frontend UI | All Chinese in main repo | **High** — use offline/amadad fork |
| GitHub Issues | Mostly Chinese | Medium — can't easily follow community issues |
| Error messages | Some Chinese | Medium |
| Demo videos (Bilibili) | Chinese only | Low |
| QQ Group (primary support) | Chinese only | **High** — community support is Chinese-only |

### Dependency on External Services

| Service | Main Repo | Offline Fork | Risk |
|---------|-----------|--------------|------|
| Zep Cloud | **REQUIRED** | Not needed | Zep could change pricing, shut down, or go offline |
| Alibaba DashScope (Qwen) | Recommended | Not needed | Can use any OpenAI-compat API |
| Neo4j | Not needed | Required (but self-hosted) | Self-managed, low risk |
| Ollama | Optional | Required | Self-hosted, low risk |
| OASIS/CAMEL-AI (pip package) | Required | Required | Open source, medium risk (academic project) |

---

## 8. COMPARISON WITH EXISTING STACK

### MiroFish vs. InfraNodus

| Dimension | MiroFish | InfraNodus |
|-----------|----------|------------|
| **Core function** | Multi-agent social simulation | Text network analysis + knowledge graph |
| **Input** | Seed documents → agent simulation | Text → network visualization |
| **Output** | Prediction reports + interactive agents | Network graphs + structural insights |
| **Graph type** | Entity-relationship (knowledge graph) | Word co-occurrence (text network) |
| **Prediction** | Simulated scenarios (qualitative) | Gap analysis (structural, quantitative) |
| **Scale** | 100-1000+ agents per simulation | Document-level analysis |
| **LLM dependency** | Core (every agent action = LLM call) | Optional (works without LLM) |
| **Maturity** | 4 months, v0.1.0 | Years of development, commercial product |
| **Self-hosted** | Yes (offline fork) | Yes (open-core) |

**Verdict:** They solve fundamentally different problems. InfraNodus finds structural patterns in text networks. MiroFish simulates social dynamics. They complement, not replace.

### MiroFish vs. Graphiti/Neo4j Plans

| Dimension | MiroFish (offline fork) | Our Graphiti/Neo4j Plans |
|-----------|------------------------|--------------------------|
| **Graph DB** | Neo4j CE 5.15 | Neo4j (same!) |
| **Purpose** | Agent memory + knowledge graph | Temporal knowledge graph for memory |
| **Overlap** | Entity extraction, relationship mapping | Entity extraction, relationship mapping |
| **Unique** | Agent simulation, social dynamics | Temporal versioning, episodic memory |

**Verdict:** Significant overlap in the graph infrastructure. If we deploy MiroFish-Offline, we'd have two Neo4j instances. Could potentially share one. The Graphiti approach is more mature for our core use case (agent memory), while MiroFish adds a unique simulation capability on top.

### Does It Replace, Complement, or Conflict?

**COMPLEMENTS** — with caveats:
- MiroFish adds a unique "what-if scenario simulation" capability we don't have
- It doesn't replace InfraNodus (different analysis paradigm)
- It partially overlaps with our Neo4j/Graphiti plans (knowledge graph layer)
- It conflicts with nothing but competes for GPU resources with Ollama

---

## 9. FINAL RECOMMENDATION

### Summary Verdict

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Concept | ⭐⭐⭐⭐ | Genuinely novel approach to scenario exploration |
| Execution | ⭐⭐ | Early stage, bugs, no tests, single developer |
| Community | ⭐⭐⭐ | High stars but very few real users |
| Output quality | ⭐⭐ | Stress test showed hedged non-answers |
| Integration difficulty | ⭐⭐⭐ | API exists, offline fork fits our stack |
| Production readiness | ⭐ | Not production ready by any measure |
| Risk/reward | ⭐⭐⭐ | Interesting enough to watch, not to invest in yet |

### Recommendation: **WAIT AND WATCH** 🟡

**Do NOT commit build time now.** Here's why:

1. **The stress test is damning.** If it can't produce useful predictions with real geopolitical data, it won't produce useful predictions for our use cases either.

2. **v0.1.0 is too early.** No tests, Chinese-primary codebase, known bugs in basic operations, single developer with corporate backing that may or may not sustain.

3. **The offline fork solves our infra concerns** but introduces maintenance risk (will it keep up with upstream?).

4. **The concept has legs.** Agent-based social simulation IS a genuinely useful paradigm. But this specific implementation needs 6-12 more months of maturation.

### What to Do Instead

1. **Star the offline fork** and check back monthly
2. **Monitor the amadad fork** — it's architecturally cleaner (KuzuDB embedded, multi-provider LLM support)
3. **If Aaron wants to play with it:** Spend 2 hours on the Docker path for MiroFish-Offline. Upload a test scenario. Evaluate the output quality firsthand. This costs nothing but time.
4. **Revisit in Q3 2026** when the project has had 6+ months to mature, more community stress tests exist, and the Shanda investment has had time to fund a real development team.

### If We Must Build Now

If the decision is to integrate regardless, the path would be:

1. Deploy MiroFish-Offline via Docker (2 hours)
2. Test with 3-5 scenarios relevant to our use cases (1 day)
3. Build an iframe embed in Comms Hub (1 day)
4. Customize the frontend to match our UI (3-5 days)
5. Set up shared Neo4j with our Graphiti plans (2-3 days)

**Total estimated effort:** 1.5-2 weeks for a working but basic integration.

---

## SOURCES INDEX

| Source | URL | What it provided |
|--------|-----|-----------------|
| Main repo | https://github.com/666ghj/MiroFish | Code structure, README, issues |
| English README | https://raw.githubusercontent.com/666ghj/MiroFish/main/README-EN.md | Official documentation |
| Offline fork | https://github.com/nikmcfly/MiroFish-Offline | Zero-cloud alternative |
| Amadad fork | https://github.com/amadad/mirofish | KuzuDB alternative, cleaner arch |
| DEV article (arshtechpro) | https://dev.to/arshtechpro/...ki8 | Pipeline detail, caveats |
| DEV article (therealmrmumba) | https://dev.to/therealmrmumba/...5fp3 | Setup guide, overview |
| Mem0 cookbook | https://docs.mem0.ai/cookbooks/frameworks/mirofish-swarm-memory | Alternative memory impl |
| OASIS paper | https://arxiv.org/html/2411.11581v4 | Scientific foundations, limitations |
| r/developersIndia stress test | https://www.reddit.com/r/developersIndia/comments/1rw7u7p/ | Real-world evaluation |
| r/aiagents thread | https://www.reddit.com/r/aiagents/comments/1rou0mk/ | Community reception |
| Memia newsletter | https://memia.substack.com/p/memia-202611-mirofish-one-trillion | Expert analysis + investment story |
| Blocmates article | https://www.blocmates.com/articles/what-is-mirofish... | Honest assessment |
| ByteIota article | https://byteiota.com/mirofish-githubs-1-trending-ai-swarm-engine-hits-28k-stars/ | Stats, tradeoffs |
| JudyAI Lab analysis | https://judyailab.com/en/posts/mirofish-multi-agent-prediction/ | Chinese investor perspective |
| GitGenius analysis | https://www.gitgenius.co/repos/666ghj/MiroFish | Repo summary |
| LinkedIn analysis | https://www.linkedin.com/pulse/swarm-intelligence-comes-forecasting-how-mirofish-simulates-borish-lahve | No benchmarks note |
| Zhihu question | https://www.zhihu.com/question/2014290448701679302 | Chinese community reception |
| Zhihu investment article | https://zhuanlan.zhihu.com/p/2013994021857546905 | Backstory, 30M RMB investment |
| Bilibili demo videos | https://www.bilibili.com/video/BV1VYBsBHEMY/ | Demo quality evaluation |
| GitHub API tree | https://api.github.com/repos/666ghj/MiroFish/git/trees/main?recursive=1 | Complete file listing |
| .env.example | https://raw.githubusercontent.com/666ghj/MiroFish/main/.env.example | Configuration requirements |
| requirements.txt | https://raw.githubusercontent.com/666ghj/MiroFish/main/backend/requirements.txt | Dependencies |
| docker-compose.yml (main) | https://raw.githubusercontent.com/666ghj/MiroFish/main/docker-compose.yml | Docker config |
| docker-compose.yml (offline) | https://raw.githubusercontent.com/nikmcfly/MiroFish-Offline/main/docker-compose.yml | Full offline Docker config |
| .env.example (offline) | https://raw.githubusercontent.com/nikmcfly/MiroFish-Offline/main/.env.example | Offline configuration |
| LICENSE | https://raw.githubusercontent.com/666ghj/MiroFish/main/LICENSE | AGPL-3.0 confirmed |
| GitHub Issue #185 | https://github.com/666ghj/MiroFish/issues/185 | Academic interest |
| X Communities | https://x.com/i/communities/2032108733929566219 | Tiny community (8 members) |
| OASIS blog | https://www.camel-ai.org/blogs/oasis | Herd behavior limitation |
| 36kr article | https://eu.36kr.com/en/p/3713983582662788 | Investment backstory |

---

*Report compiled 2026-03-19 by Researcher Agent. Ready for Steel Man review.*
