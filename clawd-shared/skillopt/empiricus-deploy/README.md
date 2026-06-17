# SkillsOpt — Plato Deployment Package

Self-contained SkillsOpt-Sleep optimizer bundle, adapted for the **Plato** node.

Phase 1 + Phase 2 validated on the AlienWare (Aristotle/Thales) host. This is
the portable package to stand the same loop up on Plato.

## What's inside

| File | Purpose |
|------|---------|
| `config.json` | Plato-adapted config (paths point at `C:\Users\Aaron\.clawdbot\...`, agent=`plato`) |
| `harvest_memos.py` | Stage 1 — pull relevant session digests from the MemOS sqlite DB |
| `openclaw_fleet_backend.py` | Anthropic-backed target/optimizer backend (urllib, no SDK) |
| `run_skill_cycle.py` | Generic single-skill optimization cycle (Phase 2) |
| `run_ledger_emit_cycle.py` | Original Phase 1 ledger-emit runner (also supplies API_KEY + paths) |
| `deploy_to_fleet.py` | Fleet driver — loops all skills, stages proposals, writes report |
| `skillopt_sleep/` | Core engine package (dream/gate/replay/judges/...) |
| `plugins/openclaw/tests/` | Held-out task sets (ledger-emit, probe-fleet-health, source-truth-preflight) |

## Safety rails (enforced)

- `auto_adopt = false`  — proposals are STAGED only; a human reviews & adopts.
- `gate_mode = on`      — no edit is accepted without a proven validation win.
- `edit_budget <= 3`    — bounded textual learning rate per cycle.
- Live `SKILL.md` files are **read-only**. Proposals go to `~/.skillopt-sleep/staging/<skill>-phase2/`.
- `deploy_to_fleet.py` re-forces all of the above in code (`_enforce_safety`) even if config drifts.

## Install on Plato

1. Copy this whole `plato-deploy/` folder onto Plato (any path), e.g. `C:\skillopt\`.
2. Put the config where the loader expects it:
   ```cmd
   mkdir %USERPROFILE%\.skillopt-sleep
   copy config.json %USERPROFILE%\.skillopt-sleep\config.json
   ```
   (The engine reads config from `~/.skillopt-sleep/config.json`, NOT the package dir.)
3. Ensure Python 3.11+ is available (stdlib only — no pip installs required).
4. Confirm the Ledger is reachable at `http://127.0.0.1:3003` (or edit `ledger_url`).
   The Ledger must have the `skill_optimization` event type in its enum
   (added in Phase 2 Goal 1 on the AlienWare ledger — replicate on Plato's
   ledger middleware/schemaV1_1.js `ALL_VALID_EVENT_TYPES` if Plato runs its own).

## Run

Single skill:
```cmd
python run_skill_cycle.py --skill probe-fleet-health
```

Whole fleet (stages proposals, writes `~/.skillopt-sleep/fleet-report.md`):
```cmd
python deploy_to_fleet.py
```

Only a subset:
```cmd
python deploy_to_fleet.py --only ledger-emit,source-truth-preflight
```

## Plato environment notes (verified 2026-06-17 from AlienWare)

- **Plato skill dir** `C:\Users\Aaron\.clawdbot\skills\` — EXISTS, 14 skills present
  (boot-context, comms-hub-bridge-send, devops, diagnose-wedge-cycle,
  dispatch-to-sub-agent, docs, ledger-emit, memos-memory-guide, northstar,
  probe-fleet-health, recover-aristotle-gateway, rt2-test-skill,
  source-truth-preflight, validation-packet-runner).
- **Plato memos DB** `C:\Users\Aaron\.clawdbot\memos-local\memos.db` — EXISTS
  (95,064,064 bytes). NOTE: on the AlienWare host this file is byte-identical
  to `C:\Users\aaron\.openclaw\memos-local\memos.db` (same size + mtime), i.e.
  `.clawdbot` and `.openclaw` resolve to the same data on THIS machine. On a
  genuinely separate Plato box, verify the DB is Plato's own and re-point
  `memos_db` in config.json accordingly. If the DB is missing on Plato,
  `harvest_memos` degrades gracefully (returns no digests) and cycles still run
  against the held-out task sets — harvest is best-effort context only.

## API key

`run_ledger_emit_cycle.py` carries the Anthropic API key (`API_KEY`) reused by
`run_skill_cycle.py` and `deploy_to_fleet.py`. Rotate it for Plato if desired,
or set `ANTHROPIC_API_KEY` in the environment (the backend falls back to it).

## Authoring task sets for more skills

Drop `plugins/openclaw/tests/<skill-name>-tasks.json` with `train`/`val`/`test`
splits and rule judges (see existing sets for the format). The fleet driver
auto-discovers any skill that has a matching task set; skills without one are
reported as "skipped (no task set)".
