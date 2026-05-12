# Assignment Brief: Graft Spec Deep Dive — Hermes Agent Self-Evolution

**Assigned to:** Daedalus
**Assigned by:** Aristotle
**Date:** 2026-04-22
**Duration:** 2-3 working days
**Priority:** Critical
**Model pin:** Use whatever model you're running on. Do NOT switch mid-task.

---

## Objective

Produce a production-quality graft spec for NousResearch/hermes-agent-self-evolution by performing source-level code inspection. An initial scan exists at `clawd-shared/specs/GRAFT-SPEC-HERMES.md` — use it as a starting point but verify and deepen every claim against actual source.

**Critical note:** Hermes is Python. Our stack is TypeScript. For every mechanism, assess: is this a direct port (rewrite in TS), a pattern reference (steal the architecture, implement ourselves), or a bridge candidate (subprocess/IPC)? The graft strategy here is fundamentally different from the TypeScript-native lossless-claw and DefenseClaw.

## Source Checkout

```powershell
# Already cloned at:
cd C:\Users\aaron\clawd-shared\graft-analysis\hermes-self-evolution

# Pin the commit you analyze — record in spec metadata
cd C:\Users\aaron\clawd-shared\graft-analysis\hermes-self-evolution; git rev-parse HEAD

# Repo info: NousResearch/hermes-agent-self-evolution
# 2,060 stars, Python, last pushed March 29, 2026
# Description: "Evolutionary self-improvement for Hermes Agent — optimize skills, prompts, and code using DSPy + GEPA"
```

## Rule of Engagement (Non-Negotiable)

**This spec is completed from SOURCE CODE INSPECTION.**
- Every mechanism entry cites specific file paths and line ranges
- If a claim cannot be pinned to source, it does not appear in this document
- README is allowed ONLY for orientation — it does not count as evidence
- Entries without source citations get REJECTED and re-done
- **If the repo is smaller than expected or features are vaporware, report that finding explicitly.** Honest assessment of what's actually in the code vs what's claimed is valuable intelligence.

## Expected Output

Fill out the graft spec template at `clawd-shared/specs/GRAFT-SPEC-TEMPLATE.md` exactly. Output to: `clawd-shared/specs/GRAFT-SPEC-HERMES.md` (overwrite the initial scan).

### Specific Requirements

1. **Key mechanisms to find and document (per Opus 4.7 analysis):**
   - DSPy + GEPA self-evolution loop: read execution traces → generate variant skills/prompts → evaluate against constraint gates → PR best variant back
   - ContextCompressor policy: protect_first_n + protect_last_n + summarize middle via auxiliary model call
   - skill_manage tool interface: agent creates/updates/deletes its own skills via tool call, patch preferred over edit
   - "5+ tool calls → save as skill" heuristic: automatic skill extraction
   - Failure-driven learning loop: how failures trigger root cause analysis
   - Sandbox/safety gates for self-modification
   - Performance metrics collection
   - Three-tier memory system (working, episodic, semantic) if present

2. **Python→TypeScript bridge strategy per mechanism:** For each GRAFT or GRAFT-MODIFIED mechanism, explicitly state:
   - PORT (rewrite in TypeScript — how much effort?)
   - REFERENCE (steal the pattern, our own implementation)
   - BRIDGE (run Python subprocess, communicate via IPC/stdin/stdout)
   
3. **Patches obsoleted section — HOLD THE LINE.** Initial scan says 4 of 7 absorbed, 0 obsoleted. Verify each.

4. **State reconciliation plan:** **Ledger write proposals must conform to the existing NorthStar event schema. If your mechanism requires a schema extension, call it out explicitly as a schema-change request rather than assuming it.**

5. **Net position paragraph:** Must survive Aristotle's review. For Hermes specifically: does grafting these patterns meaningfully reduce our Phase 2 (self-optimization) build, or do we end up reimplementing everything anyway because of the Python→TS gap?

6. **License check:** The initial scan noted no license file. Verify this. No license = all rights reserved = cannot legally graft. If unlicensed, the spec becomes REFERENCE-ONLY and every mechanism must be independently reimplemented, not copied.

## AGT Substrate Flag (Acknowledge, Don't Block)

A Microsoft Agent Governance Toolkit (AGT) substrate decision is pending. AGT has agent-compliance and agent-sre packages that may overlap with Hermes's self-improvement governance. **Do not design around AGT.** But note overlap areas.

## Context

- Full architecture spec: `clawd-shared/research/unified-architecture-spec.md`
- Review chain: `clawd-shared/research/unified-architecture-*.md`
- Graft spec template: `clawd-shared/specs/GRAFT-SPEC-TEMPLATE.md`
- Opus 4.7 guidance: "Daedalus should read this code line-by-line. It's the closest thing to a blueprint you'll find for what you want to build." The self-evolution loop is the highest-value single graft across all three projects.

## Deliverable Checklist

- [ ] All mechanisms have file:line citations from Python source
- [ ] Python→TS bridge strategy documented per mechanism (PORT/REFERENCE/BRIDGE)
- [ ] Patches obsoleted section filled with verified claims
- [ ] State reconciliation plan with NorthStar schema conformance
- [ ] License verified — if unlicensed, spec becomes REFERENCE-ONLY
- [ ] Net position paragraph honest about Python→TS gap
- [ ] Commit hash pinned in metadata
