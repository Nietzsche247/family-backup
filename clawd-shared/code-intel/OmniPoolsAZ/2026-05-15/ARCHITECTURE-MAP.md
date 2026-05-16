# OmniPoolsAZ Architecture Map — Dry Run 1
**Generated:** 2026-05-15 by Aristotle (Rail Kit Phase 4 dry run)
**Source:** C:\Users\aaron\clawd-shared\omnipools-repo
**Branch:** docs/parser-trigger-contract-v2
**Last commit:** a059078 — fix(DEF-TB-003-v2): Make non-critical CRM metadata optional

## Source Pack Summary
- **Files:** 622
- **Lines:** 166,398
- **Pack size:** 9,216 KB (9.2 MB)
- **Pack hash:** 35DE2FA31787A3E8FC0BB16FF2F5B5BD6A6EEB0B0DD41D851E6D513A6175B4F9
- **Format:** Repomix markdown, AI-consumable

## Top-Level Structure
```
src/
  assets/          — static assets
  components/      — React components
  hooks/           — custom hooks
  integrations/    — external service integrations
  lib/             — core logic / utilities
  pages/           — route pages
  styles/          — CSS/styling
  test/            — test files
  tests/           — additional tests
  _dead_code_2026-03-09/ — archived dead code
```

## Dependency Analysis
- dependency-cruiser run FAILED: node_modules not installed in repo clone
- Proper analysis requires: `cd omnipools-repo && npm install` first
- **Deferred to next session** (install + full depcruise run)

## Known Architecture Rules (from Rail Kit doc 6.2)
1. No output/report reads jurisdiction directly
2. Output uses canonical helper for jurisdiction
3. Only approved files write omni-intake-v1

**Status:** Cannot verify without dependency graph. Flagged for depcruise run after npm install.

## Observations
- 622 files is substantial — suggests a mature React/TypeScript application
- Dead code archive present (_dead_code_2026-03-09) — good hygiene practice
- Branch is documentation-focused (parser-trigger-contract-v2)
- Test directories present (test/ + tests/) — dual structure worth investigating

## Next Analysis Steps
1. `npm install` in omnipools-repo to enable depcruise
2. Run depcruise with tsconfig for full dependency graph
3. Check for circular dependencies
4. Verify architecture rules 6.2.1-3
5. Generate SVG graph if graphviz available
6. Cross-reference with source-truth-preflight skill output

---
*First Rail Kit dry run. Artifacts: SOURCE-PACK.md (9.2MB) + this map.*
