# Phase 0 status — Daedalus

Date: 2026-04-02

## Completed

### 1) Fork / baseline wiring
- Cloned/fetched OpenClaw source into:
  - `C:\Users\aaron\clawd-shared\openclaw-fork`
- Created working branch:
  - `integrate/unified-4layer`
- Tagged baseline source state:
  - `baseline-v0`
- Baseline commit:
  - `4309dc6d5ee91d4237f4227de26a8389b8733355`

### 2) Codebase map
Wrote integration-focused map to:
- `C:\Users\aaron\clawd-shared\research\openclaw-codebase-map.md`

Covered modules:
- transform-context equivalent / replay sanitation
- full compaction
- microcompact / context pruning
- tool-result guard
- session persistence
- provider adapters / provider runtime
- bootstrap / file injection

### 3) Transcript fixture pipeline
Added non-invasive tooling in fork:
- `scripts/extract-transcript-fixtures.ts`
- `scripts/generate-synthetic-transcript-fixtures.ts`
- `scripts/replay-fixtures/sanitize.ts`
- `test/fixtures/README.md`

Created fixtures under `openclaw-fork/test/fixtures/`:

Real fixtures:
- `real-01-handoff-001.jsonl`
- `real-02-04690f54-d085-486f-981e-e2a463cdee47.jsonl`
- `real-03-e901f22d-2091-4946-b4d4-95449df69aad.jsonl`

Synthetic fixtures:
- `synthetic-01-large-context.jsonl`
- `synthetic-02-many-tool-calls.jsonl`
- `synthetic-03-edge-cases.jsonl`

Pipeline capabilities now present:
- extract real session transcripts from `.jsonl`
- sanitize paths / IDs / secrets / signatures
- emit replay fixtures as JSONL
- generate synthetic stress fixtures for:
  - large context pressure
  - many tool calls
  - malformed/orphaned tool histories

### 4) Replay harness
Added:
- `scripts/replay-transcript-fixture.ts`

Harness behavior:
- loads fixture JSONL
- simulates persistence-time tool-result guard behavior
- repairs tool-call / tool-result ordering
- strips tool-result details from LLM-facing context
- runs microcompact-style context pruning
- runs a local compaction-planning pass
- emits structured JSON results for invariant checking

Generated outputs under:
- `openclaw-fork/test/results/`

Verified end-to-end on all 6 fixtures:
- `real-01-handoff-001.json`
- `real-02-04690f54-d085-486f-981e-e2a463cdee47.json`
- `real-03-e901f22d-2091-4946-b4d4-95449df69aad.json`
- `synthetic-01-large-context.json`
- `synthetic-02-many-tool-calls.json`
- `synthetic-03-edge-cases.json`

## Commands used for verification
```powershell
corepack pnpm install --ignore-scripts
node --import tsx scripts/generate-synthetic-transcript-fixtures.ts --outDir test/fixtures
node --import tsx scripts/extract-transcript-fixtures.ts --outDir test/fixtures <session1> <session2> <session3>
node --import tsx scripts/replay-transcript-fixture.ts test/fixtures/<fixture>.jsonl test/results/<fixture>.json
```

## Issues / findings
1. **Direct cold-import of heavyweight runtime source surfaces can hang in standalone script context**
   - observed with:
     - `src/agents/pi-embedded-runner/google.ts`
     - `src/agents/compaction.ts`
     - `src/agents/pi-embedded-runner/tool-result-truncation.ts`
   - implication:
     - for Phase 0, the replay harness uses stable pure seams that execute reliably in isolation rather than importing the entire embedded runtime stack directly.
   - practical result:
     - harness is working and replayable now
     - but a deeper source-import hang investigation is warranted before Phase 1/2 runtime-coupled replay work

2. **Baseline source was not modified in-place**
   - runtime behavior files were mapped, not patched
   - Phase 0 additions are sidecar tooling + fixtures only

## Notes for Thales / integration follow-up
- `test/results/*.json` should be a good feedstock for invariant checking.
- The current replay harness is intentionally conservative and non-invasive.
- If we want exact runtime-parity replay later, I recommend introducing an explicit adapter seam around:
  - replay sanitation
  - microcompact
  - compaction planning / execution
  rather than importing deep runtime modules ad hoc.
