# Assignment Brief: Graft Spec Deep Dive — DefenseClaw

**Assigned to:** Daedalus
**Assigned by:** Aristotle
**Date:** 2026-04-22
**Duration:** 2-3 working days
**Priority:** Critical
**Model pin:** Use whatever model you're running on. Do NOT switch mid-task.

---

## Objective

Produce a production-quality graft spec for DefenseClaw (Cisco) by performing source-level code inspection. An initial scan exists at `clawd-shared/specs/GRAFT-SPEC-DEFENSECLAW.md` — use it as a starting point but verify and deepen every claim against actual source.

## Source Checkout

```powershell
# Already cloned at:
cd C:\Users\aaron\clawd-shared\graft-analysis\defenseclaw

# Pin the commit you analyze — record in spec metadata
cd C:\Users\aaron\clawd-shared\graft-analysis\defenseclaw; git rev-parse HEAD

# Key source directories:
# extensions/defenseclaw/src/ — TypeScript OpenClaw plugin (THIS IS THE MAIN TARGET)
# internal/ — Go daemon code (reference only, we won't graft Go)
# cli/ — Python CLI tools (reference only)
```

## Rule of Engagement (Non-Negotiable)

**This spec is completed from SOURCE CODE INSPECTION.**
- Every mechanism entry cites specific file paths and line ranges
- If a claim cannot be pinned to source, it does not appear in this document
- README is allowed ONLY for orientation — it does not count as evidence
- Entries without source citations get REJECTED and re-done

## Expected Output

Fill out the graft spec template at `clawd-shared/specs/GRAFT-SPEC-TEMPLATE.md` exactly. Output to: `clawd-shared/specs/GRAFT-SPEC-DEFENSECLAW.md` (overwrite the initial scan).

### Specific Requirements

1. **Focus on the TypeScript plugin** at `extensions/defenseclaw/src/`. This is what runs inside OpenClaw and is directly graftable. The Go daemon and Python CLI are reference/pattern-only.

2. **Key mechanisms to find and document:**
   - Admission gate state machine (blocklist → allowlist → scan → decision → action + audit)
   - `before_tool_call` hook implementation in the OpenClaw plugin
   - `fetch-interceptor.ts` — how they patch globalThis.fetch for LLM call interception
   - `policy/enforcer.ts` — decision logic
   - Audit trail / logging mechanism
   - Health monitor pattern
   - Configuration/rule definition system

3. **Patches obsoleted section — HOLD THE LINE.** Initial scan says 4 of 7 patches killed/absorbed (3 tool logging OBSOLETED, 7 beforeTool OBSOLETED, 2 token estimator ABSORBED partial, 4 write scope ABSORBED). Verify each against source.

4. **State reconciliation plan:** **Ledger write proposals must conform to the existing NorthStar event schema. If your mechanism requires a schema extension, call it out explicitly as a schema-change request rather than assuming it.**

5. **Net position paragraph:** Must survive Aristotle's review. The test: "Does post-graft sound meaningfully smaller than pre-graft?"

6. **License check:** DefenseClaw is Cisco. Verify exact license terms. Flag any restrictions on modification, redistribution, or commercial use.

## AGT Substrate Flag (Acknowledge, Don't Block)

A Microsoft Agent Governance Toolkit (AGT) substrate decision is pending, parallel to this work. AGT has its own policy engine (agent-os) and audit trail. DefenseClaw's admission gate pattern may overlap with AGT's policy engine. **Do not design around AGT — proceed with NorthStar as target.** But note any areas where DefenseClaw mechanisms would conflict with or duplicate an external governance layer.

## Context

- Full architecture spec: `clawd-shared/research/unified-architecture-spec.md`
- Review chain: `clawd-shared/research/unified-architecture-*.md`
- Graft spec template: `clawd-shared/specs/GRAFT-SPEC-TEMPLATE.md`
- Opus 4.7 guidance: Steal the admission gate state machine (maps to Tier 1/2/3 governance), the before_tool_call gateway pattern, and the policy evaluation pipeline. Skip: Cisco scanner integration, Splunk, Landlock/seccomp (Linux-only).

## Deliverable Checklist

- [ ] All mechanisms have file:line citations from TypeScript source
- [ ] Go/Python patterns documented as reference-only where relevant
- [ ] Patches obsoleted section filled with verified claims
- [ ] State reconciliation plan with NorthStar schema conformance
- [ ] License verified and any restrictions flagged
- [ ] Net position paragraph that survives review
- [ ] Commit hash pinned in metadata
