# Empiricus Deployment Notes (SkillsOpt Phase 3)

Prepared but NOT yet deployed. Adapted from plato-deploy.

## Empiricus environment (probed 2026-06-17)
- SSH: `aaron@100.65.240.87`  key `C:\Users\aaron\.ssh\empiricus_access_key`
- Remote shell is **PowerShell** (use `;` not `&&`; avoid nested quotes — prefer SCP a .py then `python file.py`)
- Python: **3.11.9** (stdlib sqlite3/json/pathlib present — no pip needed)
- Home: `C:\Users\aaron`
- OpenClaw root: `C:\Users\aaron\.openclaw\` (NOT `.clawdbot`)
- Skills root: `C:\Users\aaron\.openclaw\skills`
  - **Only 1 skill present**: `devops\fable-completion-protocol` (nested under a *category* folder)
- memos.db: `C:\Users\aaron\.openclaw\memos-local\memos.db` — **DOES NOT EXIST** (no memos-local dir)

## config.json — already adapted for Empiricus
- `skills_root` -> `C:\Users\aaron\.openclaw\skills`
- `memos_db`    -> `C:\Users\aaron\.openclaw\memos-local\memos.db`
- `ledger_agent`-> `empiricus`
- Safety unchanged: auto_adopt=false, gate_mode=on, edit_budget=3

## KNOWN ISSUES to expect on deploy (same as Plato)
1. `load_config()` reads `~/.skillopt-sleep/config.json`, NOT the package dir.
   -> After SCP, copy `config.json` to `C:\Users\aaron\.skillopt-sleep\config.json`.
2. `deploy_to_fleet.list_skills()` scans `skills_root` **one level deep only**.
   Empiricus skills are nested in *category* dirs (devops/...), so discovery
   returns 0. Either (a) flatten skills, or (b) patch list_skills to recurse.
3. No memos.db -> `transcript_source: memos` harvests 0 sessions (engine still
   runs, just with empty context digests).
4. The 6 bundled task sets (ledger-emit, probe-fleet-health, devops, research-cron,
   source-truth-preflight, wiki) reference skills that are NOT installed on disk.
   `run_skill_cycle` safely refuses with "live SKILL.md not found/empty" rather
   than fabricating edits — this is correct/safe behavior.

## Deploy steps (when authorized)
```powershell
scp -r -i C:\Users\aaron\.ssh\empiricus_access_key "C:\Users\aaron\clawd-shared\skillopt\empiricus-deploy" "aaron@100.65.240.87:C:/Users/aaron/skillopt-empiricus"
ssh -i C:\Users\aaron\.ssh\empiricus_access_key aaron@100.65.240.87 "New-Item -ItemType Directory -Force -Path C:\Users\aaron\.skillopt-sleep | Out-Null; Copy-Item C:\Users\aaron\skillopt-empiricus\config.json C:\Users\aaron\.skillopt-sleep\config.json -Force"
ssh -i C:\Users\aaron\.ssh\empiricus_access_key aaron@100.65.240.87 "cd C:\Users\aaron\skillopt-empiricus; python deploy_to_fleet.py"
```
