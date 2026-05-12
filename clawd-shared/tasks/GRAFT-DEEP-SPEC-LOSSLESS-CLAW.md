# Assignment Brief: Graft Spec Deep Dive — lossless-claw

**Assigned to:** Daedalus
**Assigned by:** Aristotle
**Date:** 2026-04-22
**Duration:** 2-3 working days
**Priority:** Critical
**Model pin:** Use whatever model you're running on. Do NOT switch mid-task.

---

## Objective

Produce a production-quality graft spec for lossless-claw by performing source-level code inspection. An initial scan exists at `clawd-shared/specs/GRAFT-SPEC-LOSSLESS-CLAW.md` — use it as a starting point but verify and deepen every claim against actual source.

## Source Checkout

```powershell
# Already cloned at:
cd C:\Users\aaron\clawd-shared\graft-analysis\lossless-claw

# Pin the commit you analyze — record in spec metadata
cd C:\Users\aaron\clawd-shared\graft-analysis\lossless-claw; git rev-parse HEAD

# Also clone the win4r fork for comparison (already cloned):
cd C:\Users\aaron\clawd-shared\graft-analysis\lossless-claw-enhanced
```

## Rule of Engagement (Non-Negotiable)

**This spec is completed from SOURCE CODE INSPECTION.**
- Every mechanism entry cites specific file paths and line ranges
- If a claim cannot be pinned to source, it does not appear in this document
- README is allowed ONLY for orientation — it does not count as evidence
- Entries without source citations get REJECTED and re-done

## Expected Output

Fill out the graft spec template at `clawd-shared/specs/GRAFT-SPEC-TEMPLATE.md` exactly. Output to: `clawd-shared/specs/GRAFT-SPEC-LOSSLESS-CLAW.md` (overwrite the initial scan).

### Specific Requirements

1. **Mechanism inventory:** Aim for 6-15 mechanisms. The initial scan found ~10. Verify each, add any missed.

2. **Day 1 mini-deliverable (if not already complete):** Token estimator diff — win4r fork vs upstream. One page. Separate file: `clawd-shared/specs/TOKEN-ESTIMATOR-DIFF.md`. This determines if patch #2 is killed immediately.

3. **Patches obsoleted section — HOLD THE LINE.** This is the keystone. Initial scan says 4 of 7 patches killed/absorbed. Verify each claim against source. If a claim can't be verified, retract it. One-line justification per patch is not optional.

4. **State reconciliation plan:** Every GRAFT-MODIFIED mechanism that writes state gets a row. Apply this rule: **Ledger write proposals must conform to the existing NorthStar event schema. If your mechanism requires a schema extension, call it out explicitly as a schema-change request rather than assuming it.** Do not invent a Ledger write adapter in isolation — the three graft specs will be unified.

5. **Net position paragraph:** In the summary, write one paragraph describing the post-graft world. This paragraph must survive Aristotle's review. The test: "Does post-graft sound meaningfully smaller than pre-graft, or does it sound like the same plan with nicer parts?" If you can't make the case, say so honestly.

## AGT Substrate Flag (Acknowledge, Don't Block)

A Microsoft Agent Governance Toolkit (AGT) substrate decision is pending, parallel to this work. AGT's audit trail may absorb some of the NorthStar Ledger write-adapter role. **Do not design around AGT — proceed with NorthStar Ledger as target.** But if your proposed Ledger writes would conflict with an external audit trail system, note it. This is awareness, not a blocker.

## Context

- Full architecture spec: `clawd-shared/research/unified-architecture-spec.md`
- Review chain: `clawd-shared/research/unified-architecture-*.md` (6 files)
- Graft spec template: `clawd-shared/specs/GRAFT-SPEC-TEMPLATE.md`
- Opus 4.7 analysis guidance: lossless-claw grafts = DAG summarization, retrieval tools (lcm_grep/describe/expand), large-file threshold, freshTailCount. Skip: SQLite persistence (NorthStar replaces), plugin wrapping, provider/auth plumbing.

## Deliverable Checklist

- [ ] All mechanisms have file:line citations from source
- [ ] win4r token estimator diff complete (separate file)
- [ ] Patches obsoleted section filled with verified claims
- [ ] State reconciliation plan with NorthStar schema conformance
- [ ] Net position paragraph that survives review
- [ ] Commit hash pinned in metadata
- [ ] License confirmed
