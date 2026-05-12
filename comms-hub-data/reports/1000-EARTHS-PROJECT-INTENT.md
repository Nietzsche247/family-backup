# 1000 EARTHS — Project Intent & Strategy

**Owner:** Aaron Baker
**Coordinator:** Aristotle
**Status:** PARKED — waiting for NorthStar OS stabilization
**Created:** 2026-03-19
**Priority:** Next after NorthStar infrastructure tracks complete

---

## VISION

A multi-agent simulation and prediction engine — a "digital sandbox" where thousands of AI agents with distinct personalities, memories, and behavioral logic interact in parallel worlds. Upload seed data (news, reports, financial signals, policy drafts), and 1000 Earths builds a high-fidelity simulation to predict outcomes, test scenarios, and explore "what if" questions.

**Aaron's framing:** "This was going to be one of our projects anyway. MiroFish gives us a head start."

**Hub integration:** New tab next to God-Eye (Shadowbroker). God-Eye watches the world as it is. 1000 Earths simulates what happens next.

---

## RESEARCH COMPLETED

Two comprehensive reports already delivered and filed:

### 1. Researcher Deep Dive (Socrates)
- **File:** `C:\bravo-team\reports\mirofish-deep-dive-2026-03-19.md`
- **Scope:** 44KB report covering merits, community sentiment, architecture, file map, install instructions, risks, integration feasibility
- **Key finding:** MiroFish concept is novel but execution is v0.1.0. The r/developersIndia stress test showed hedged non-answers for real-world prediction.

### 2. Steel Man Review
- **File:** `C:\bravo-team\reports\mirofish-steelman-review-2026-03-19.md`
- **Scope:** Problem/solution teardown with effort estimates, alternatives comparison, licensing analysis
- **Key finding:** Fork the ENGINE (OASIS, Apache-2.0), not the FISH (AGPL-3.0). Use MiroFish as design reference only.

---

## STRATEGIC DECISION: BUILD ON OASIS

### Why OASIS, Not MiroFish
| Factor | MiroFish | OASIS |
|--------|----------|-------|
| License | AGPL-3.0 (copyleft — source disclosure if network-exposed) | Apache-2.0 (fully permissive) |
| Maturity | v0.1.0, 4 months old | Peer-reviewed research, published paper |
| Scale | Tested with ~100 agents | Supports up to 1M agents |
| Language | Chinese-first, English secondary | English |
| Our freedom | Limited by AGPL if we ever expose externally | Unlimited — modify, deploy, commercialize |

### OASIS (Our Foundation)
- **Repo:** https://github.com/camel-ai/oasis
- **License:** Apache-2.0
- **What it does:** Multi-agent social simulation engine. Dual-platform (Twitter + Reddit style). Agent personas with memory and behavioral logic.
- **Paper:** Peer-reviewed, admits LLM herding limitation (which we'll fix)

### MiroFish (Our Reference/Spec)
- **Main repo:** https://github.com/666ghj/MiroFish
- **Offline fork:** https://github.com/nikmcfly/MiroFish-Offline (Neo4j + Ollama, zero cloud deps)
- **Amadad fork:** https://github.com/amadad/mirofish
- **Use as:** Design reference for the pipeline (seed → graph → agents → simulation → report). Don't ship their code.

---

## ARCHITECTURE OUTLINE (from research)

```
SEED DATA (upload)
    ↓
ENTITY EXTRACTION (LLM + NLP)
    ↓
KNOWLEDGE GRAPH (Neo4j or KuzuDB)
    ↓
AGENT GENERATION (LLM creates personas from graph entities)
    ↓
MEMORY INJECTION (individual + collective memories via Mem0/Zep)
    ↓
SIMULATION (OASIS engine — multi-round social interaction)
    ↓
REAL-TIME MONITORING (graph visualization, sentiment tracking)
    ↓
REPORT GENERATION (ReACT agent analyzes post-simulation state)
    ↓
INTERACTIVE CHAT (talk to any simulated agent or the report agent)
```

### Our Stack Mapping
| Component | MiroFish Uses | We Would Use |
|-----------|---------------|-------------|
| Knowledge Graph | KuzuDB | Neo4j (already in Shadowbroker stack) or InfraNodus |
| Agent Memory | Zep Cloud | Mem0 (already installed family-wide) + Ollama embeddings |
| Simulation Engine | OASIS | OASIS (Apache-2.0, direct) |
| LLM | Qwen (Alibaba) | Ollama local (llama3.2, mistral, etc.) |
| Frontend | Custom React | Hub tab (Daedalus builds) |
| Visualization | Force-directed graph | Extend existing InfraNodus/God-Eye viz |

---

## KNOWN PROBLEMS & PLANNED SOLUTIONS

| # | Problem | Solution | Effort | Owner |
|---|---------|----------|--------|-------|
| 1 | **Hedged non-answers** — no probabilities, no timelines | Build calibration harness: Brier scores, confidence intervals, backtesting against known outcomes | M | Researcher + Empiricus |
| 2 | **LLM herd behavior** — agents converge to consensus | Inject adversarial/contrarian agents, diversity constraints on persona generation, temperature variation | M | Daedalus |
| 3 | **Cost scaling** — 6K-10K LLM calls per simulation | Tiered agent models: key players get full LLM, crowd uses lightweight rules-based behavior | L | Daedalus + Thales |
| 4 | **No evaluation framework** | Build ground-truth testing: synthetic scenarios with known outcomes, measure prediction accuracy | M | Empiricus |
| 5 | **AGPL contamination** | Build on OASIS (Apache-2.0), use MiroFish as design reference only, strict code isolation | S | Steel Man (review) |
| 6 | **Chinese-first codebase** | Building our own — non-issue. OASIS is English. | — | — |
| 7 | **v0.1 maturity, no test suite** | Building our own — we'd have our own test harness from day 1 | S | Thales |

---

## TACTICAL PROTOTYPE (Optional, Low-Cost)

If Aaron wants to play with MiroFish before committing to the full build:

1. **What:** Docker deploy MiroFish-Offline on Alienware
2. **Time:** 2-4 hours (Thales alone)
3. **Requirements:** Docker, Neo4j, Ollama (all available on Alienware)
4. **Purpose:** Hands-on experience with the simulation UX, test a real scenario, validate whether the concept excites enough to prioritize
5. **Risk:** Zero — isolated Docker container, no integration, throwaway

---

## EFFORT ESTIMATE (Full Build)

| Phase | Description | Duration | Team |
|-------|-------------|----------|------|
| **Phase 0** | Tactical prototype (MiroFish-Offline Docker) | 2-4 hours | Thales |
| **Phase 1** | OASIS integration + basic simulation pipeline | 1-2 weeks | Daedalus + Thales |
| **Phase 2** | Knowledge graph → agent generation pipeline | 1-2 weeks | Daedalus + Researcher |
| **Phase 3** | Hub tab UI + real-time visualization | 1 week | Daedalus |
| **Phase 4** | Calibration/evaluation harness | 1-2 weeks | Empiricus + Researcher |
| **Phase 5** | Anti-herding + tiered models + optimization | 1-2 weeks | Daedalus + Steel Man review |
| **Total to v1** | | **6-8 weeks** | **3-4 agents dedicated** |

---

## ALTERNATIVES EVALUATED (by Steel Man)

| Framework | License | Strengths | Weaknesses | Verdict |
|-----------|---------|-----------|------------|---------|
| **OASIS** | Apache-2.0 | Peer-reviewed, 1M agent scale, our freedom | Sim engine only, no full pipeline | **USE AS FOUNDATION** |
| **AgentSociety** | Check | Social sim focused | Less mature than OASIS | Monitor |
| **AgentVerse** | Check | Multi-agent orchestration | Different focus (task solving, not prediction) | Not a fit |
| **Mesa/Repast/GAMA** | Various OSS | Battle-tested ABM | Not LLM-native, different paradigm | Reference only |
| **MiroFish** | AGPL-3.0 | Full pipeline, novel UX | Copyleft, v0.1, Chinese-first | **REFERENCE ONLY** |

---

## DOMAINS THIS UNLOCKS (from Aaron's portfolio)

1. **Future prediction** — direct application (the whole point)
2. **Options trading** — simulate market scenarios before positioning
3. **Pool engineering** — simulate customer decision patterns, competitive dynamics
4. **Mental health** — simulate therapeutic scenarios (research tool)
5. **BLM mine hunting** — simulate claim competition dynamics
6. **General** — any domain where "what happens if X?" is valuable

---

## PARKING CONDITIONS

This project activates when:
- [ ] NorthStar OS Track B (Environment Authority) is closed
- [ ] NorthStar OS Track C (remaining items) is closed
- [ ] Aaron explicitly greenlights 1000 Earths as the next priority
- [ ] At least Daedalus + Thales are available (not on OmniPools)

---

## REFERENCES

- Researcher report: `C:\bravo-team\reports\mirofish-deep-dive-2026-03-19.md`
- Steel Man review: `C:\bravo-team\reports\mirofish-steelman-review-2026-03-19.md`
- MiroFish main: https://github.com/666ghj/MiroFish
- MiroFish Offline: https://github.com/nikmcfly/MiroFish-Offline
- OASIS (foundation): https://github.com/camel-ai/oasis
- DeepWiki analysis: https://deepwiki.com/666ghj/MiroFish
- DEV Community overview: https://dev.to/arshtechpro/mirofish-the-open-source-ai-engine-that-builds-digital-worlds-to-predict-the-future-ki8
- Mem0 cookbook: https://docs.mem0.ai/cookbooks/frameworks/mirofish-swarm-memory

---

*"We don't know the next project. But we know: smarter tools + faster systems + compounding layers = we win." — NORTH_STAR.md*
