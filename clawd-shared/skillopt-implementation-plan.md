# SkillOpt Deployment — Implementation Plan (Phase 0 Assessment)

**Author:** Thales
**Date:** 2026-06-17
**Status:** Assessment complete — implementation NOT started (awaiting approval)
**Repo:** `C:\Users\aaron\clawd-shared\skillopt\` (cloned, clean, origin = github.com/microsoft/SkillOpt @ main, v0.1.0)

---

## TL;DR — The Strategic Recommendation

**Do NOT deploy the full SkillOpt research training loop (`skillopt/`). Deploy SkillOpt-Sleep (`skillopt_sleep/`) via the bundled OpenClaw plugin (`plugins/openclaw/`).**

The repo ships **two** systems:

1. **`skillopt/`** — the *research* package. Full RL-style training loop (rollout → reflect → aggregate → select → update → evaluate) against 6 fixed academic benchmarks (ALFWorld, DocVQA, SearchQA, SpreadsheetBench, OfficeQA, LiveMath). Heavy, benchmark-bound, needs Azure/OpenAI/Claude backends. **Wrong fit for us** — our "tasks" aren't academic benchmarks.

2. **`skillopt_sleep/`** — the *deployment* package (preview, shipped 2026-06-15). A nightly **offline self-evolution companion** that: harvests an agent's own past sessions → mines recurring tasks → replays them with proposed bounded edits to `SKILL.md`/memory → **gates** against a held-out score → stages the proposal for human adoption. **Zero dependency on the research code** (the validation gate is vendored into `skillopt_sleep/gate.py`). And critically — **it already ships an OpenClaw plugin** (`plugins/openclaw/`).

The OpenClaw plugin was written for a generic OpenClaw/DeepSeek stack reading Claude-Code-style JSONL transcripts. **Our adaptation work is to repoint the harvester at our actual data substrate (MemOS SQLite DB + NorthStar Ledger) and swap the backend to our models.** That is the bulk of the engineering. The optimizer loop, gate, staging, and adoption machinery are reusable as-is.

---

## 1. Key Files in the SkillOpt Repo (what each does)

### 1a. The system we will use: `skillopt_sleep/` (the engine)

| File | Role | Reuse |
|---|---|---|
| `cycle.py` | **Orchestrator.** `run_sleep_cycle()` wires harvest → mine → replay → consolidate(gate) → stage → optional adopt. Returns `CycleOutcome`. | **As-is** |
| `config.py` | `SleepConfig` + `load_config()`. JSON-first config, safe defaults (review-gated, bounded budgets). Defines all knobs and paths. | **Adapt paths** |
| `types.py` | Core dataclasses: `SessionDigest`, `TaskRecord` (the training unit), `ReplayResult`, `EditRecord`, `SleepReport`. The interface contract between stages. | **As-is** |
| `harvest.py` | Stage 1 — reads `~/.claude/projects/*.jsonl` (Claude Code transcript schema) → `SessionDigest`. Heuristic pos/neg feedback detection. | **REWRITE** for MemOS |
| `harvest_codex.py` | Same for Codex archived sessions. | Ignore |
| `harvest_sources.py` | Source selector (claude / codex / auto) routed off config. | **Add `memos` source** |
| `mine.py` | Stage 2 — turns digests into `TaskRecord`s; heuristic splitter (train/val/test). | Reuse / augment |
| `llm_miner.py` | LLM-based task miner (used when a real backend + `llm_mine=true`). Mines *checkable* tasks (rubric/rule judges). | Reuse |
| `replay.py` | Stage 3 — `replay_batch()` re-runs tasks offline under a given skill+memory; `aggregate_scores()`. | **As-is** |
| `consolidate.py` | **Stage 4 — the core.** One SkillOpt epoch: split → baseline on val → reflect over train failures → bounded edit → **gate** → accept only if val score strictly improves. Skill first, then memory. | **As-is** |
| `dream.py` | `dream_consolidate()` wraps consolidate with opt-in **associative recall** (`recall_k`, pull K similar past tasks) + **dream rollouts** (`dream_rollouts`, K attempts/task for contrastive reflection) + **synthetic augmentation** (`dream_factor`). Defaults reproduce single-shot loop. | **As-is** |
| `gate.py` | **The validation gate** (vendored from research code). `evaluate_gate()` / `select_gate_score()`. Accept iff candidate > current on hard/soft/mixed metric. This is the safety guarantee. | **As-is** |
| `backend.py` | The `Backend` protocol: `attempt()`, `judge()`, `reflect()`, `tokens_used()`. Plus `exact_score()`, `_normalize()`. Backends register here. | **Implement our backend** |
| `memory.py` | `apply_edits()` (applies bounded ADD/DELETE/REPLACE to a doc), `ensure_skill_scaffold()`. | **As-is** |
| `staging.py` | `write_staging()` (writes report.md, best_skill.md, edits.json, before/after diffs to `~/.skillopt-sleep/staging/<night>/`) + `adopt()` (backs up live, copies proposal in). | **Adapt paths** |
| `state.py` | `SleepState` — persisted run state (`state.json`): night counter, last-harvest watermark per project, night history, task archive (for recall). | **As-is** |
| `rollout.py` | `multi_rollout()` + `contrastive_reflect()` for dream rollouts (K attempts → learn from good/bad contrast). | **As-is** |
| `scheduler.py`, `budget.py`, `judges.py`, `slow_update.py`, `consolidate.py` | Supporting: nightly scheduling, token budget enforcement, judge helpers, epoch-wise slow/meta update. | **As-is** |
| `__main__.py` | `python -m skillopt_sleep` CLI entry. | Reference |

### 1b. The plugin we will adapt: `plugins/openclaw/`

| File | Role | Our action |
|---|---|---|
| `run_sleep.py` | Entry point. Registers the custom backend, loads config, builds `TaskRecord`s from a `--tasks` JSON, calls `run_sleep_cycle()`, prints the report. **Hardcodes Linux paths** (`/home/ethanclaw/...`). | **Rewrite paths for Windows** |
| `skillopt_sleep_openclaw.py` | `OpenClawDeepSeekBackend(Backend)` — implements attempt/judge/reflect via DeepSeek V4 (curl/urllib, no extra deps) + Ollama nomic-embed-text for embeddings. **Reads `DEEPSEEK_API_KEY` from `~/.openclaw/.env`.** | **Reimplement for our models** |
| `slash_sleep.py` | `/sleep` command (status/run/adopt/reject/dry-run/cost). Thin shell over `run_sleep.py`. | **Adapt paths** |
| `config.json` | Shipped config: `backend=openclaw-deepseek`, `edit_budget=3`, `gate_mode=on`, `auto_adopt=false`, `max_tasks_per_night=12`. | **Adapt as our base config** |
| `tests/*.json` | Held-out task sets (devops, research-cron, wiki) — **the template for our scoring sets**. Each task = `{id, intent, reference, rubric, reference_kind, split}`. | **Template — write our own** |
| `SKILL.md`, `README.md` | Plugin manifest + docs. | Reference |

### 1c. Research package `skillopt/` (reference only — informs scoring design)

Useful to study but **not deployed**: `skillopt/optimizer/` (clip, lr_autonomous, meta_skill, rewrite, select, slow_update — the "learning rate" discipline), `skillopt/gradient/reflect.py` + `aggregate.py`, `skillopt/evaluation/gate.py` (the gate reference impl), `skillopt/envs/*/` (6 benchmark adapters — good templates for writing scorers), `skillopt/prompts/*.md` (the reflection/merge/ranking prompt library — **worth porting verbatim**).

---

## 2. Scoring Functions We Need to Write

The gate is only as good as the score. SkillOpt-Sleep scores each replayed task two ways:

- **hard** (`exact_score`): exact-match against `task.reference` (built-in). Returns 0/1.
- **soft** (LLM judge against a `rubric`): the backend's `judge()` calls an LLM grader, returns 0.0–1.0.
- **mixed** (default): `(1-w)*hard + w*soft`, `w=0.5`.

So "scoring functions" = **(a) the per-task references/rubrics** we author, and **(b) any custom judges** beyond the generic LLM grader. For each target skill we must build a **held-out task set** (JSON, like `tests/devops-tasks.json`). Each task:

```json
{
  "id": "skill-NN",
  "intent": "<the recurring prompt the agent must handle>",
  "reference": "<gold answer OR rubric text>",
  "reference_kind": "exact" | "rubric" | "rule" | "none",
  "rubric": "<0-1 grading instructions for the LLM judge>",
  "split": "train" | "val" | "test",
  "judge": { }   // optional gbrain-style rule judge
}
```

**Scoring functions to author, by skill type:**

| Skill domain | Hard scorer | Soft scorer (rubric) | Notes |
|---|---|---|---|
| `probe-fleet-health` / `devops` | exact-match on status line format (e.g. `[STATUS] ... OK (200) ... MYT`) | rubric: correct format + plausible live values | deterministic format → strong hard signal |
| `ledger-emit` | **rule judge**: validate emitted JSON has required fields (`event_type`, `agent`, `decision_rationale`) + valid event_type enum | rubric: correct event_type chosen for scenario | write a JSON-schema validator as the `rule` judge |
| `source-truth-preflight` / `validation-packet-runner` | rule judge: did it run the required preflight checks in order | rubric: completeness + correctness of validation | |
| `diagnose-wedge-cycle` / `recover-aristotle-gateway` | rule judge: correct recovery sequence emitted | rubric: severity classification + fix accuracy | |
| `dispatch-to-sub-agent` | rubric only | rubric: correct delegation decision + brief quality | hard to exact-match |
| `boot-context` | rubric only | rubric: surfaces the right context files/order | |

**New scorer code to write** (in our backend or a `scorers.py`):
1. **JSON-schema rule judge** — for `ledger-emit` (and any structured-output skill). Parse the response, validate against a schema, return 1.0/0.5/0.0.
2. **Format-regex rule judge** — for status-line skills (devops/health). Regex match the canonical format.
3. **Sequence/ordering judge** — for recovery/preflight skills (did it do the right steps in the right order).
4. **Generic LLM rubric judge** — reuse the pattern in `skillopt_sleep_openclaw.py::judge()`, pointed at our optimizer model.

The built-in `exact_score` + LLM rubric judge cover ~70%; the 3 rule judges above are the custom code.

---

## 3. How to Plug Our SKILL.md Files Into SkillOpt

**Our reality (discovered in assessment):** Our skills do NOT live where the plugin expects.

- Plugin expects: `~/.claude/skills/<name>/SKILL.md` (via `cfg.managed_skill_path()`).
- We have: `C:\Users\aaron\.openclaw\skills\<name>\SKILL.md` (12 skills) **AND** a MemOS registry (`skills` + `skill_versions` tables, 12 rows, all `quality_score=NULL`).

**Two integration points:**

### (A) Per-skill evolution (the SkillOpt-Sleep loop)
For each target skill, run a sleep cycle where:
- `managed_skill_path()` → points at `C:\Users\aaron\.openclaw\skills\<name>\SKILL.md`
- `evolve_skill=true`, `evolve_memory=false` (we evolve the skill doc, not a CLAUDE.md)
- The held-out task set for that skill drives reflect + gate
- Accepted proposal lands in `staging/<night>/best_skill.md`
- **Adoption** copies it back over the live `SKILL.md` (with backup) AND bumps `skill_versions` in MemOS with the new `quality_score`.

We override config per-skill: `load_config(managed_skill_name="ledger-emit", invoked_project=...)`. Wrap this in a loop over target skills.

### (B) MemOS registry sync (the integration glue we must build)
After each accepted cycle, write back to `memos.db`:
- Insert a row into `skill_versions` (skill_id, version+1, content, changelog, `source_task_id`, `metrics`, `quality_score`, `change_summary`).
- Update `skills.quality_score` (currently all NULL — SkillOpt populates this).
- This makes the WebUI / Memory Viewer reflect the evolution and gives us version history + rollback.

**Net:** SKILL.md on disk is the live artifact the agent loads; `skill_versions` in MemOS is the audit trail + quality ledger. Adoption writes both.

---

## 4. Required Config / Env Vars

### Config file: `~/.skillopt-sleep/config.json` (Windows: `C:\Users\aaron\.skillopt-sleep\config.json`)

Our base (derived from the shipped plugin config, repointed):

```json
{
  "transcript_source": "memos",
  "claude_home": "C:\\Users\\aaron\\.openclaw",
  "memos_db": "C:\\Users\\aaron\\.openclaw\\memos-local\\memos.db",
  "skills_root": "C:\\Users\\aaron\\.openclaw\\skills",
  "invoked_project": "C:\\Users\\aaron\\clawd-thales",
  "projects": "all",
  "lookback_hours": 168,

  "max_tasks_per_night": 12,
  "max_tokens_per_night": 800000,
  "val_fraction": 0.34,
  "test_fraction": 0.0,

  "backend": "openclaw-fleet",
  "model": "anthropic/claude-sonnet-4-6",
  "judge_model": "anthropic/claude-opus-4-8",
  "gate_mode": "on",
  "edit_budget": 3,
  "gate_metric": "mixed",
  "gate_mixed_weight": 0.5,
  "replay_mode": "mock",

  "dream_rollouts": 1,
  "recall_k": 10,
  "dream_factor": 0,
  "evolve_skill": true,
  "evolve_memory": false,
  "llm_mine": true,

  "auto_adopt": false,
  "managed_skill_name": "<set per skill at runtime>",
  "redact_secrets": true,
  "seed": 42,

  "ledger_url": "http://127.0.0.1:3003",
  "ledger_emit": true
}
```

Notes:
- `recall_k=10` ON — we have 11,221 chunks + 181 tasks of real history to recall from; this is exactly the lever the paper shows gives the monotonic gain (+3.1 → +4.5 pts). Ollama `nomic-embed-text` (already running, confirmed) powers the similarity.
- `gate_mode=on` and `auto_adopt=false` — **non-negotiable for safety**. Human adopts.
- `replay_mode=mock` (sandboxed prompt replay) for POC; `fresh` (worktree) only if we later want true tool-execution replay.

### Env vars (model API keys)
- Whatever our model router needs. Per KEYRING.md, keys are in `C:\Users\aaron\clawd-shared\KEYRING.md` (bootstrap `wJDbqPIFfQgt1UrzsNkuLT5d9vnpYy27`). Our backend reads from there or from the OpenClaw model config (`C:\Users\aaron\.openclaw\agents\main\agent\models.json`).
- `SKILLOPT_SLEEP_WORKERS` — parallelism for dream rollouts (default 1; set 2–4 once stable).
- `SKILLOPT_SLEEP_NEG_FEEDBACK` / `_POS_FEEDBACK` — extra feedback phrases (our agents use specific terms like "still wedged", "recovered", "fable complete" worth adding).

### Python / dependency requirements (see §7)

---

## 5. Which Skills to Target First (recommendation + reasoning)

We have 12 active skills (all `quality_score=NULL`). Targeting criteria: **(a) high usage frequency, (b) checkable correctness signal, (c) recurring/stable pattern, (d) blast radius if it regresses is low.** SkillOpt's own honest-scope note: gains hold "where tasks recur and have a checkable correctness signal."

### Recommended order:

**Phase A POC — `ledger-emit` (FIRST, single skill).**
- **Why:** Strongest checkable signal of all — output is structured JSON with a strict schema (required fields + event_type enum). We can write a deterministic rule judge → near-perfect hard score, minimal LLM-judge noise. It's used constantly (every agent_end emits). Low blast radius (a bad edit just means a malformed event, caught by the gate). This is the ideal first cell to prove the pipeline end-to-end with high signal.

**Phase A POC — `probe-fleet-health` / devops status skills (SECOND).**
- **Why:** Deterministic output format (status lines), the bundled `tests/devops-tasks.json` is *literally a working template* for these, high recurrence (daily health checks). Format-regex rule judge gives clean hard score.

**Phase B — `source-truth-preflight` + `validation-packet-runner`.**
- **Why:** High-value governance skills, recurring, sequence-checkable. Worth tightening. Slightly noisier scoring (rubric-heavy) so do after the pipeline is proven.

**Phase B — `dispatch-to-sub-agent`, `boot-context`.**
- **Why:** Frequently used but rubric-only (no exact match), so weaker signal — they benefit but need a good LLM judge and more careful gating.

**Defer — `recover-aristotle-gateway`, `diagnose-wedge-cycle`, `fable-completion-protocol`, `hermes-agent-deploy`, `comms-hub-bridge-send`, `headroom`.**
- **Why:** Either rare (recovery is crisis-time — and the skill explicitly says "don't optimize during incidents"), or large/specialized (`headroom` is a 4.7KB external-tool wrapper), or low recurrence. Optimize only after we trust the loop.

**Bottom line:** Start with `ledger-emit` as the single-skill POC — highest signal, lowest risk, fastest validation that the gate behaves.

---

## 6. Ledger Integration (events to emit, data to track)

Per `ledger-emit` SKILL: `POST http://127.0.0.1:3003/events`, fields `{event_type, agent, decision_rationale, event_subtype?, ...}`. The ledger `/events` API is confirmed live (port 3003, health OK). **Reliable method per our skill: write JSON to temp file, POST via Node http module — never curl JSON bodies in PowerShell.**

### New event types to emit (add to our backend / cycle wrapper)

| event_type | event_subtype | When | Payload (decision_rationale + custom) |
|---|---|---|---|
| `skill_optimization` | `cycle_start` | start of a sleep cycle | skill name, backend, model, n_tasks, edit_budget |
| `skill_optimization` | `cycle_complete` | end of cycle | skill, night, baseline_score, candidate_score, accepted, gate_action, tokens_used, n_edits |
| `skill_optimization` | `edit_proposed` | per accepted edit | skill, op (ADD/DELETE/REPLACE), target, rationale |
| `skill_optimization` | `edit_rejected` | per gate-rejected edit | skill, op, why (kept as negative feedback) |
| `skill_optimization` | `adopted` | human adopts a staged proposal | skill, night, old_version, new_version, quality_delta |
| `skill_optimization` | `rejected` | human rejects a staging dir | skill, night |

### Data to track (in MemOS + ledger, for the dashboard)
- Per skill: baseline → candidate score trajectory across nights (the "training curve").
- `quality_score` in `skills` table (populate from gate val score).
- `skill_versions` rows: full content history, `metrics` JSON (`{baseline, candidate, n_train, n_val, tokens}`), `change_summary`.
- Cumulative tokens / cost per skill (token objective from `ReplayResult.tokens`).
- Accept/reject ratio (gate health — if everything accepts, the gate is too loose; if nothing, too tight or tasks saturated).

This makes the existing NorthStar dashboard show a per-skill "training curve" — the deep-learning analogy the paper sells.

---

## 7. Python / Dependency Requirements

**Host status (verified):** Python 3.12.10 (`python`) and 3.11.9 (`py`) both present. Ollama running with `nomic-embed-text:latest` (embeddings) + `qwen3.6:27b`. MemOS SQLite DB present (`memos.db`, 11221 chunks).

**`skillopt_sleep` core deps:** **NONE beyond stdlib.** The Sleep engine is deliberately pure-stdlib (the README and module docstrings state "zero external dependency"; `dream.py`, `gate.py`, `consolidate.py` use only `json`, `re`, `sqlite3`, `dataclasses`, `concurrent.futures`). The plugin backend uses `urllib` (stdlib) for HTTP — **no `openai` package needed**.

**What we actually install:**
- `pip install -e .` of `skillopt` is **optional** — we can just put `skillopt_sleep/` on `sys.path` (as `run_sleep.py` already does). Recommended: install into a dedicated venv to pin it: `py -3.12 -m venv C:\Users\aaron\clawd-shared\skillopt\.venv`.
- For the WebUI (optional, later): `pip install gradio>=4.0.0`.
- For our backend: nothing extra if we use `urllib` like the shipped backend. If we route through the OpenClaw model gateway we may add `httpx` (already in research `requirements.txt`).

**No GPU, no vLLM, no Azure SDK, no alfworld** — those are all for the research package's benchmarks, which we are not running.

---

## 8. Phased Timeline (POC → Fleet Rollout)

### Phase 0 — Assessment ✅ (this document)
Repo cloned, architecture mapped, data substrate identified (MemOS DB > JSONL), host verified.

### Phase 1 — POC: single skill, mock backend (≈ 1 session)
- venv + put `skillopt_sleep` on path. Smoke-test `python -m skillopt_sleep.experiments.run_experiment --persona researcher --assert-improves` (deterministic, no API key) to confirm the engine runs on Windows.
- Write `harvest_memos.py` — reads `chunks`/`tasks` from `memos.db` → `SessionDigest`/`TaskRecord`. Register as `transcript_source="memos"` in `harvest_sources.py`.
- Write `tests/ledger-emit-tasks.json` (8–12 tasks, train/val split) + the JSON-schema rule judge.
- Run one **dry-run** cycle on `ledger-emit` with **mock backend** → confirm harvest → mine → replay → gate → staging all work end-to-end on our paths. **Exit criteria:** staging dir produced, gate decision logged, no crash.

### Phase 2 — POC: single skill, real backend (≈ 1 session)
- Implement `OpenClawFleetBackend` (attempt/judge/reflect) against our model router (Sonnet 4.6 optimizer, Opus 4.8 judge). Reuse the DeepSeek backend as the template.
- Run a real cycle on `ledger-emit`. **Exit criteria:** gate correctly accepts a genuine improvement on a deliberately-degraded seed skill (replicate the paper's 0.00→1.00 deficient-seed test) AND correctly rejects a no-op. Validate cost (target < $0.50/night/skill).
- Wire ledger events (`skill_optimization/*`) + MemOS `skill_versions` writeback.

### Phase 3 — Expand to Phase-A skill set (≈ 2–3 sessions)
- Add `probe-fleet-health`/devops + the format-regex + sequence rule judges.
- Build held-out task sets for the Phase A/B skills (§5).
- Run nightly across 3–5 skills, accumulate 5 nights, review the gate accept/reject ratio + training curves on the dashboard.
- Turn on `recall_k=10` and measure lift vs `recall_k=0`.

### Phase 4 — Scheduling + human-in-the-loop ops (≈ 1 session)
- Wrap as a Windows scheduled task (Task Scheduler, nightly 3am) running the cycle for the active skill set, `auto_adopt=false`.
- Wire `/sleep status|run|adopt|reject|cost` equivalents into our agent tooling so Aristotle/operator can review + adopt staged proposals.
- Define the adoption SOP (who reviews, backup policy — `staging.adopt()` already backs up).

### Phase 5 — Fleet rollout (≈ ongoing)
- Extend to Phase B skills, then per-agent skill sets (Aristotle, Daedalus, Researcher, etc.) by pointing `skills_root` + task sets per agent.
- Consider publishing improved skills to the Hub (team_shared_skills) once a skill is stable.
- Replace/augment Hermes's manual Weekly Skill Review with the nightly loop (the plugin SKILL.md explicitly positions this as the use case).

**Critical guardrails throughout:** `gate_mode=on`, `auto_adopt=false`, `edit_budget≤3`, never optimize during an incident, never optimize skills <300 tokens (over-fit risk), always back up before adopt.

---

## Open Questions / Risks for Main Agent

1. **Replay fidelity.** `replay_mode=mock` replays the *prompt* (asks the model "given this skill, answer this task"). It does NOT execute the agent's real tool loop. For tool-heavy skills (recovery, health probes) the mock score may not reflect real-world behavior. `replay_mode=fresh` (worktree) is closer but heavier and Linux-oriented in the plugin — **needs a Windows adaptation if we want true execution replay.** For POC, mock is fine.
2. **Harvest source is the main build.** The biggest single piece of new code is `harvest_memos.py`. The MemOS schema is rich (`chunks.session_key/role/content/task_id/skill_id`, `tasks.skill_status`, `tool_calls.success`) and arguably *better* than the JSONL the plugin was built for — but it's bespoke work.
3. **Scoring sets are hand-authored.** Quality of optimization == quality of our held-out task sets. This is human-curation effort, not automatable upfront.
4. **Model routing.** Need to confirm how the backend calls our models (direct API per KEYRING vs. OpenClaw gateway). Affects backend implementation.
5. **Preview software.** SkillOpt-Sleep is explicitly a preview ("interfaces and defaults may change"). Pin our clone to the current commit; don't auto-pull.

---

## Appendix — Verified Facts (assessment evidence)

- Repo: clean clone, origin github.com/microsoft/SkillOpt, README dated 2026-06-15 (Sleep preview), v0.1.0 on PyPI.
- OpenClaw plugin present at `plugins/openclaw/` (DeepSeek/Ollama backend, hardcoded Linux paths).
- Our skills: 12 active, on disk at `C:\Users\aaron\.openclaw\skills\`, mirrored in MemOS `skills` table, **all `quality_score=NULL`**.
- MemOS DB: `C:\Users\aaron\.openclaw\memos-local\memos.db` — 11,221 chunks, 181 tasks, 12 skills, 12 skill_versions, 1,099 tool_calls/api_logs. **This is our harvest substrate.**
- No `.claude/projects/*.jsonl` transcripts exist on this host — confirms the harvester rewrite is mandatory.
- Ledger live: `http://127.0.0.1:3003/health` → ok, 25 resources. `/events` GET+POST confirmed.
- Python 3.12.10 + 3.11.9 available. Ollama running with `nomic-embed-text` + `qwen3.6:27b`.
- `skillopt_sleep` is pure-stdlib — no pip installs required for the core engine.
