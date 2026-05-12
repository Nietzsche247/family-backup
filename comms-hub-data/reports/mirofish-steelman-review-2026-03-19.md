# MiroFish → 1000 Earths “Steel Man” Foundation Review (tear-down + fixes)
**Date:** 2026-03-19  
**Reviewer:** Steel Man (epistemological auditor)  
**Input:** Researcher deep-dive: `C:\bravo-team\reports\mirofish-deep-dive-2026-03-19.md`

This is not a go/no-go. It is: *what would it take to make MiroFish the foundation for 1000 Earths?*  
Format: every finding is **PROBLEM | SOLUTION/WORKAROUND (incl. effort)**.

---

## TL;DR (for Aaron)
- **Yes, we can fork and modify it** (it’s open source), but **AGPL-3.0 makes “make it ours” incompatible with any external/proprietary network service** unless we’re willing to open-source our fork or keep it strictly internal.
- **OASIS is the most “real” foundation here** (and is **Apache-2.0**, i.e., permissive), but **LLM-per-action simulation does not scale economically** and has known behavioral artifacts (herding/consensus inflation). OASIS is a solid *research* base, not a production forecasting engine.
- The biggest gaps are **(1) evaluation/backtesting, (2) cost/latency scaling, (3) epistemic calibration (probabilities), (4) reproducibility/observability, (5) security + data governance**, and **(6) license strategy**.

### Practical path to “1000 Earths v1”
- **Best short-term accelerator (internal prototype):** fork **MiroFish-Offline** to harvest UI/flow + basic plumbing; replace pieces progressively.
- **Best long-term foundation (productizable):** **build from scratch** using **OASIS (Apache-2.0)** + our own memory/graph stack (Neo4j/Graphiti) + an evaluation harness. Use MiroFish as *reference implementation*, not as shipped code.

---

## Effort scale (T-shirt)
- **S:** 1–5 dev-days
- **M:** 1–3 weeks
- **L:** 1–2 months
- **XL:** 1+ quarters / foundational rewrite / research program

---

## A. Legal / licensing / “can we make it ours?”

| PROBLEM | SOLUTION / WORKAROUND (Effort) |
|---|---|
| **AGPL-3.0 “network copyleft”**: if we run a modified fork as a network service for non-employees (even behind auth), we must offer source to users. This collides with “private product” ambitions for 1000 Earths. | **Decide license strategy upfront.** Options: (1) keep MiroFish fork **strictly internal** (employees/contractors) and treat as prototype; (2) negotiate **commercial relicense** with upstream (unlikely but possible given funding); (3) **clean-room rewrite** of MiroFish-specific codepaths, keeping only permissive deps like OASIS (Apache-2.0). **Recommendation:** assume (3) for anything external. (Effort: decision S; rewrite XL) |
| **License infection risk**: copying any MiroFish code into our codebase will taint it under AGPL obligations. “Borrowing ideas” is fine; copying code is not. | Establish a **no-code-transfer boundary**: use MiroFish as a running system + spec; write fresh implementations. Keep separate repos and contributor guidance. (Effort: S) |
| **Third-party IP contamination** via seed docs: users may upload copyrighted or sensitive docs; model outputs may reproduce them. | Add governance: doc ingestion terms + classification; PII detection; redaction; retention policy; “no training” guarantees for local models; audit logs. (Effort: M) |
| **Model/provider licensing**: offline uses Ollama models (e.g., Qwen). Model licenses may restrict commercial use or require attribution. | Maintain an explicit **model allowlist** with license review; provide a “commercial-safe” default set. (Effort: S–M) |

---

## B. Scientific validity / forecasting quality (core tear-down)

| PROBLEM | SOLUTION / WORKAROUND (Effort) |
|---|---|
| **Not actually a prediction engine**: outputs are narrative scenarios with hedging; no probability, no calibration, no scoring against reality. The r/developersIndia test is a strong external signal. | Introduce a **forecasting layer**: define event questions (binary/multiclass/numeric), require agents to output **explicit probabilities + time bounds**, aggregate with proper scoring (Brier/log score), and produce calibration plots. Add “what evidence would change your mind?” prompts. (Effort: L) |
| **No backtesting / benchmarks**: no way to tell if changes improve anything. | Build a **historical backtest harness**: curated datasets of past events + contemporaneous corpora; run sims blinded to outcomes; score; regression testing. This becomes the gating system for 1000 Earths. (Effort: L–XL depending on ambition) |
| **Herd behavior / consensus inflation** (admitted by OASIS): agents converge too fast, underestimating disagreement and tail risks. | Countermeasures stack: (1) **network topology controls** (modular communities, echo chambers, cross-cut edges); (2) “independence priors” (agents only see partial feeds); (3) **temperature / prompt diversity**; (4) fixed “contrarian / skeptic” roles; (5) multi-model ensembles (different LLM families) to decorrelate. (Effort: M–L) |
| **LLM agents are not humans**: they lack incentives, stakes, bounded rationality, and institutional constraints; behavior can be performative and style-driven. | Introduce **mechanistic layers**: lightweight ABM components (utility functions, constraints, budgets, information access), with LLM used for narrative/decision justification *within constraints*. Hybrid “rules + LLM” agents. (Effort: L) |
| **Reflexive simulation bias**: the same model does extraction → persona gen → action → report; errors reinforce each other (“single-model monoculture”). | Split the pipeline: use separate models/temperatures for (a) extraction, (b) behavior policy, (c) critique/verification, (d) report synthesis; add verifier agents and disagreement checks. (Effort: M) |
| **Ontology/graph extraction is brittle**: LLM-generated entities/relations vary run-to-run, causing unstable world state and downstream persona drift. | Add deterministic scaffolding: NER/entity linking (spaCy, regex, domain dictionaries) + LLM only as augmenter; canonicalization + dedupe; schema validation; “extract → validate → repair” loop. (Effort: M–L) |
| **Geopolitical/finance “hard targets”**: LLMs avoid precise numeric/time predictions; when forced they hallucinate. | Use a **two-layer output**: (1) scenario narratives; (2) a constrained forecast head that must output values within allowed ranges and cite extracted evidence. For numeric forecasts, use separate quantitative models (time series / econometrics) and let agents perturb assumptions rather than produce the number. (Effort: L) |
| **Simulation may be “token prediction at scale”**: plausible text without causal grounding; convincing but unvalidated. | Add **causal hooks**: explicit causal graph hypotheses; interventions that change variables; sensitivity analysis; track which mechanisms drive deltas. Require counterfactual tests to pass. (Effort: XL if done seriously; M for minimal instrumentation) |

---

## C. Cost / performance / scaling (the “1M agents” reality check)

| PROBLEM | SOLUTION / WORKAROUND (Effort) |
|---|---|
| **LLM call explosion** (~6k–10k calls for 100 agents × 30 rounds) makes scale to “1000 Earths” infeasible on a single GPU and expensive in cloud. | Reduce calls with: (1) **event-driven simulation** (agents act only when triggers hit); (2) **batching** + parallel inference; (3) “small model for most agents, big model for leaders” hierarchy; (4) caching identical prompt states; (5) summarization/compaction of memory. (Effort: L) |
| **Latency wall**: sequential orchestration + subprocess IPC likely bottlenecks; user waits hours for runs. | Introduce a proper **job system** (Celery/RQ/Temporal) + streaming progress; parallelize rounds where possible; precompute agent policies. (Effort: M–L) |
| **Token bloat from memory**: graph memory + chat history can quickly exceed context windows and degrade quality. | Implement **memory budgeting**: episodic summaries, salience scoring, retrieval quotas per step, and “forgetting” policies. Persist embeddings and structured facts, not raw transcripts. (Effort: M) |
| **“1M agents” claim mismatch**: OASIS can orchestrate many agents, but if each requires LLM inference, compute cost dominates; likely the paper’s scaling relies on simplifications. | Treat 1M as *simulation shell capacity*, not LLM realism. For true scale, train **surrogate behavior models** (distilled policies) for the long tail of agents; only sample a subset with full LLM reasoning. (Effort: XL) |
| **GPU contention** with our other systems (Ollama used by multiple apps). | Add a **resource scheduler** (queue + quotas); allow remote inference; run simulation models on dedicated GPU instance. (Effort: M) |

---

## D. Architecture / maintainability / correctness

| PROBLEM | SOLUTION / WORKAROUND (Effort) |
|---|---|
| **v0.1.0 maturity**: rapid iteration, few production users, no test suite, likely brittle. | Add tests at three layers: (1) unit tests for parsers/graph ops; (2) golden tests for prompt templates with mocked LLM; (3) end-to-end “tiny sim” CI. (Effort: M–L) |
| **Single huge files** (e.g., `report_agent.py` 99KB) + thick endpoints; high coupling. | Refactor into bounded contexts (ingestion, graph, personas, simulation, reporting); use interfaces for LLM + memory; enforce typing (mypy/pyright) + linting. (Effort: L) |
| **Subprocess-based simulation IPC** is fragile on Windows and hard to observe; failure modes are opaque. | Move simulation runner in-process or behind a stable service boundary (gRPC/HTTP). Add structured logs, trace IDs, and persistent run artifacts. (Effort: M–L) |
| **No reproducibility**: LLM nondeterminism + random seeds untracked; cannot compare runs. | Log everything needed to replay: prompts, model versions, temperatures, seeds, retrieved context hashes, and graph snapshots. Provide “replay mode” with cached completions. (Effort: M) |
| **Versioning of world state** (graph + agent memories) unclear; hard to branch scenarios and compare. | Add scenario versioning: immutable run IDs; copy-on-write graph snapshots; “branch from run” semantics; store diffs of state transitions. (Effort: L) |
| **Two social platforms (Twitter+Reddit) are hard-coded metaphors**; 1000 Earths likely needs arbitrary arenas (markets, institutions, org charts). | Abstract “interaction arenas” as plugins: define action schema + observation model + reward/constraints. Keep Twitter/Reddit as default plugin. (Effort: L) |

---

## E. Data layer / graph / memory

| PROBLEM | SOLUTION / WORKAROUND (Effort) |
|---|---|
| **Zep Cloud dependency (main repo)** is a non-starter for sensitive internal use; offline fork removes it but diverges. | Use **offline fork** as baseline. Long term, build our own memory layer (Graphiti/Neo4j) with a clean abstraction so storage can swap (Neo4j/Kuzu/Postgres+pgvector). (Effort: S now; L long-term) |
| **Graph DB scaling + multi-tenancy**: naive “one big graph” becomes slow and messy; Neo4j CE has limits (no clustering). | Use per-project namespaces or separate DBs; for scale, consider Neo4j Enterprise or alternative (Kuzu for embedded, Postgres for metadata + vector). Add indexes and cardinality controls. (Effort: M–L) |
| **Entity resolution**: LLM extraction produces duplicates and aliasing (e.g., “US”, “United States”, “America”). | Add canonical entity registry + alias tables; apply embedding similarity + rules; human-in-the-loop merge UI for high-impact nodes. (Effort: M) |
| **Memory poisoning / prompt injection via seed docs**: malicious content can steer agent behavior and report output. | Sanitize ingestion: strip instructions, apply content filters, separate “facts” from “instructions”, use toolformer-style constrained retrieval, and add a “system policy” that forbids following seed instructions. (Effort: M) |

---

## F. Security / compliance / ops

| PROBLEM | SOLUTION / WORKAROUND (Effort) |
|---|---|
| **File upload attack surface** (PDF parsing, large files, decompression bombs). | Enforce size/type limits; sandbox PDF parsing; virus scan; run parsers in restricted container; timeouts. (Effort: M) |
| **No auth/permissions model** (typical of demos). | Add authN/authZ, per-project ACLs, secrets management, audit logging. (Effort: M–L) |
| **Supply-chain risk**: large dependency graph (uv.lock 570KB) + fast-moving ecosystem. | Pin/scan deps (SCA), SBOM, renovate policy, minimal base images, reproducible builds. (Effort: M) |
| **Observability gaps**: hard to debug which agent did what and why; impossible to operate reliably. | Add structured event logs (actions, prompts, retrievals), distributed tracing, metrics (tokens/sec, costs, failures), run artifact store. (Effort: M) |

---

## G. Product / UX / “1000 Earths” fit

| PROBLEM | SOLUTION / WORKAROUND (Effort) |
|---|---|
| **UI is workflow-bound to MiroFish steps** (graph build → env → sim → report → chat). 1000 Earths likely needs iterative scenario branching, comparisons, dashboards. | Keep the UI as a prototype; redesign around “scenario tree”, run comparison, and evaluation scores. Embed MiroFish UI only for internal exploration. (Effort: L) |
| **Report is the heaviest component** and also the least trustworthy (it can rationalize anything). | Treat report as *one view*. Add “evidence table”, “claims with provenance”, “disagreement map”, and “what would falsify this” sections. (Effort: M) |
| **No human-in-the-loop controls**: users can’t constrain assumptions, priors, or policy levers explicitly. | Build a “levers panel”: priors, shocks, information access, media bias, institutional constraints; allow locking key parameters. (Effort: M–L) |

---

## H. What’s fundamental vs surface-level?

### Fundamental (architectural / epistemic)
- **AGPL constraints** if 1000 Earths is external-facing.
- **Evaluation + calibration missing** (without it, we can’t know if we’re improving).
- **Cost scaling**: LLM-per-action doesn’t reach 1000× worlds without surrogates/hierarchy.
- **Behavioral artifacts** (herding) are intrinsic to LLM-agent social sims unless actively countered.

### Surface-level (fixable engineering)
- Zep cloud dependency (already solved by offline fork).
- Windows/Docker reliability issues.
- Missing tests, refactors, auth, observability.

---

## I. Realistic effort: “MiroFish fork” → “1000 Earths v1”

Assuming *1000 Earths v1* means: scenario simulation + branching + explicit forecasts + run comparison + basic backtesting + secure self-host.

- **Fork MiroFish-Offline and harden for internal use:** **M–L** (4–8 weeks)
  - auth + quotas + logging + UI tweaks + stability + basic evaluation harness.
- **Make it a true forecasting system (probabilities + backtests + calibration):** **L–XL** (2–6 months)
  - depends on dataset + scoring + repeated runs + tooling.
- **Make it productizable externally (escape AGPL, scale architecture):** **XL** (2+ quarters)
  - clean-room rewrite + surrogate policy models + plugin arenas + multi-tenant infra.

---

## J. Alternatives (at least 2) — better foundations to consider

| Foundation | Why it may be better | What we’d still need |
|---|---|---|
| **OASIS directly (camel-ai/oasis, Apache-2.0)** | Same simulation core without AGPL; permissive; research-backed; we can build our own product on top legally. | Everything MiroFish adds: ingestion/graph, personas, UI, reporting, eval harness, ops. |
| **AgentSociety (tsinghua-fib-lab/AgentSociety)** | Purpose-built for large-scale societal simulation (reported 10k–30k agents); likely more “society-first” than Twitter/Reddit metaphors. | Check license/stack fit; still need forecasting calibration + our product UX; integration effort likely L–XL. |
| **AgentVerse (OpenBMB/AgentVerse)** | Explicitly supports multi-agent *simulation* framework; modular. | Maturity/stability risk; may be more “framework” than product; needs evaluation + memory + scaling. |
| **Classic ABM frameworks (Mesa / Repast / GAMA / NetLogo)** | Deterministic, scalable, validated ABM tooling; excellent for mechanism testing and sensitivity analysis. | Doesn’t give LLM-style narrative; we’d build hybrid agents (rules + LLM) and a modern UI + memory + RAG. |

---

## K. Final recommendation (must choose one)

### Recommendation: **Build from scratch (product path), borrowing specific components**
- **Borrow:** OASIS (Apache-2.0) *concepts and/or code*, the “arena” concept (Twitter/Reddit as plugins), and the general pipeline structure (ingest → world model → agents → simulate → analyze).
- **Do not ship:** MiroFish code as the core of 1000 Earths if there is any chance of external access, due to AGPL.

### Tactical (next 2–4 weeks): **Fork MiroFish-Offline for internal prototyping**
- Use it to validate UX, quantify cost, and identify the minimal set of features users actually need.
- Treat it as disposable scaffolding; keep strict separation from the product codebase.

If forced to pick among the three options in the prompt for “foundation right now”: **fork MiroFish-Offline** (best operational fit), but only as an internal prototype and a spec for the real system.
