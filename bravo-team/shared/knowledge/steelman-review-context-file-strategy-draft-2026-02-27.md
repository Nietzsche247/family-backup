# Steel Man Review (DRAFT): Context File Strategy
**Date:** 2026-02-27  
**Reviewer:** Steel Man 🛡️  
**Scope:** Workspace-injected context files (SOUL/AGENTS/HEARTBEAT/STATE/memory/* + shared files), and how they’re used to survive compaction + enable cross-agent coordination.

---

## Objective
Create a **compaction-resilient, low-friction, low-staleness** way for any agent to rehydrate:
1) who they are, 2) what matters, 3) what’s true right now, 4) what to do next — **without** token bloat or false confidence.

## North Star Alignment
**YES (high)** — this compounds. Context resilience is a foundation layer; it eliminates repeated work and prevents “rebuild from scratch” collapses.

---

## Strongest counter-argument
A file-based strategy *looks* deterministic but actually creates a **silent distributed consistency problem**:
- Files sprawl, drift, and contradict.
- Each agent/workspace becomes a fork.
- “It’s written down” becomes a false sense of certainty when the file is stale.

If this becomes the primary source of truth for *facts* (ports/paths/services), it will recreate the exact failure we’re trying to eliminate — only with higher confidence and slower detection.

---

## Hidden assumptions (the ones that will break)
1. **Assumption: Agents will reliably read the right files.** Post-compaction and under time pressure, voluntary compliance collapses.
2. **Assumption: File sets stay small.** They don’t. Any successful system accumulates notes until it becomes unscannable.
3. **Assumption: “Shared” paths are truly shared and stable across machines.** Windows-path + machine-local reality makes this fragile.
4. **Assumption: “Hard facts” can live in markdown safely.** Hard facts require atomicity, uniqueness, and deprecation semantics—markdown provides none.

---

## What’s good (keep it)
- **Determinism & inspectability:** Files are debuggable. You can diff them. Humans can read them.
- **Fast iteration:** Editing a file is faster than schema migrations.
- **Separation potential:** You *can* separate identity/values from state/facts.
- **Compaction robustness for “who/why”:** A short SOUL/anchor file is the right tool to recover motivation + role fidelity.

---

## The core failure mode to design against
### “Stale truth with high confidence”
The worst outcome is not missing context; it’s **confidently using wrong context**.

File strategies fail when they become an implicit claim that the world matches what’s written.

**Rule:** Markdown is great for *norms, rationale, narrative*. It is dangerous as the system of record for *current operational truth*.

---

## Required design constraints (non-negotiable if this is to scale)
### 1) Explicit layering + ownership
Define layers with strict semantics and update expectations:
- **L1: Identity/Role** (SOUL/AGENTS): stable, rarely edited.
- **L2: Operating Protocols** (HEARTBEAT/ENGAGEMENT): stable, procedural.
- **L3: Objectives** (memory/objectives): updated per initiative.
- **L4: Personal Anchor** (short; always included): “why I exist” + behavioral guardrails.
- **L5: Project State (narrative)**: what’s happening + next steps (human-readable).
- **L6: Hard Facts Registry**: **NOT markdown** (Ledger/API); only references in files.
- **L7: Ephemeral scratch/daily logs**: rot is expected.

Each layer needs an **owner** and a “freshness SLA” (e.g., L5 must be touched daily while active).

### 2) “Hard facts” must be externalized to a registry
Ports, service locations, active DBs, canonical paths, running processes — these require:
- atomic check-and-create
- deprecation/supersession
- query that returns *one* authoritative answer

That is Ledger territory. Files can link to Ledger, but must not duplicate it.

### 3) One canonical command/context definition source
If `/context` means “read these 12 files” and that set differs per agent, you get divergence.

**Fix:** put canonical definitions in a shared location (or Ledger-backed), and have agent workspaces *reference* it, not re-implement it.

### 4) Context budget + compilation
Have an explicit max budget (tokens/words) for injected context.
- Always-included files must be **short**.
- Everything else should be **pulled on demand** via `/context` or planning gate.

Recommended: generate a **compiled context snapshot** (machine-generated) that is the only thing injected by default; it includes pointers to deeper files.

### 5) Drift detection (linter)
Add an automated check that flags:
- files exceeding size caps
- missing “Last updated” timestamps where required
- broken path references
- duplicate claims (“service runs on 3001” vs “service runs on 8080”)
- secrets accidentally pasted

Run this on heartbeat or nightly.

---

## Failure indicators (early warning signs)
If any of these occur, the strategy is degrading:
1. Agents ask “where is X?” despite it being “documented” → discoverability failure.
2. Two agents take contradictory actions citing different files → divergence.
3. Context injection grows until agents stop reading it → bloat.
4. Files reference machine-local paths that don’t exist on another host → portability failure.
5. Incidents where a stale file caused a wrong build decision → false-confidence failure.

---

## Simpler alternative (if we want 80/20)
- Keep **only**:
  - SOUL (identity/drive)
  - HEARTBEAT (startup checklist)
  - Objectives (what matters)
  - Project STATE (narrative)
- Move everything else to:
  - Ledger for hard facts
  - Mem0 for rationale/lessons (explicitly non-authoritative)
- Make session start a mandatory “startup trinity” pull:
  1) Ledger summary (hard truth)
  2) Project STATE (narrative)
  3) last DIARY entry (motivation/role)

This keeps file maintenance small and pushes truth into systems that can enforce it.

---

## Verdict
**PAUSE (minor), then PROCEED.**

Proceed with a file-based context strategy **only** if we explicitly:
1) separate *norms/narrative* (files) from *truth/facts* (Ledger),
2) enforce a context budget + compilation step,
3) create drift detection (linter) so staleness becomes visible, not silent.

### Suggested immediate fixes (this week)
- Publish a one-page “Context Layers & Semantics” spec (what goes where; what never goes where).
- Create a canonical shared command/context definition file (single source).
- Add a small linter script + size caps.
- Add “Last updated:” headers to any file that is supposed to be current (especially project state).

---

## Note on the overdue Layer 4 Personal Anchor review
This strategy **depends** on a short, always-included Layer 4 anchor, but that anchor must be:
- small enough to survive injection budgets,
- stable (rare edits),
- written to prevent role drift without becoming rigid dogma.

I have not delivered the separate anchor critique yet; this draft flags the dependency so we don’t ship an architecture that assumes a missing load-bearing layer.
