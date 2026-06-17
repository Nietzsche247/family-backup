"""SkillOpt-Sleep — fleet deployment driver (Phase 2, Goal 4).

Loops over every skill under cfg["skills_root"], runs ONE optimization cycle
per skill that has a held-out task set, emits `skill_optimization` ledger
events (enum fixed in Phase 2 Goal 1), stages any accepted proposals (NEVER
auto-adopts — a human reviews the staged diff), and writes a fleet summary
report.

SAFETY (hard guarantees):
  * auto_adopt forced False (config + code)
  * gate_mode forced "on"
  * edit_budget clamped to <= 3
  * live SKILL.md files are READ-ONLY; proposals -> STAGING only
  * skills with no task set are reported as "skipped (no task set)" — never run
    against an empty/garbage gate.

Usage:
  python deploy_to_fleet.py                 # run all skills that have task sets
  python deploy_to_fleet.py --all-tasks-required   # error if a skill lacks tasks
  python deploy_to_fleet.py --only ledger-emit,probe-fleet-health
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from skillopt_sleep.config import load_config
from run_skill_cycle import run_cycle, _tasks_path_for

FLEET_REPORT = os.path.expanduser(r"~/.skillopt-sleep/fleet-report.md")


def _enforce_safety(cfg):
    """Force the non-negotiable safety rails regardless of config.json drift.

    Accepts a SleepConfig (has .to_dict / .get) or a plain dict; returns the
    same kind of object so downstream .get() calls keep working.
    """
    data = cfg.to_dict() if hasattr(cfg, "to_dict") else dict(cfg)
    data["auto_adopt"] = False
    data["gate_mode"] = "on"
    try:
        data["edit_budget"] = min(int(data.get("edit_budget", 3) or 3), 3)
    except Exception:
        data["edit_budget"] = 3
    data.setdefault("ledger_agent", "thales")
    # Rebuild a SleepConfig so run_cycle's cfg.get(...) + attribute access work.
    return load_config(**data)


def list_skills(skills_root: str) -> List[str]:
    if not os.path.isdir(skills_root):
        return []
    out = []
    for name in sorted(os.listdir(skills_root)):
        d = os.path.join(skills_root, name)
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "SKILL.md")):
            out.append(name)
    return out


def write_report(results: List[Dict[str, Any]], path: str, *, started: str, finished: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ran = [r for r in results if r.get("ran")]
    skipped = [r for r in results if not r.get("ran")]
    staged = [r for r in ran if r.get("staging_dir")]

    lines: List[str] = []
    lines.append("# SkillsOpt Fleet Report")
    lines.append("")
    lines.append(f"- Started:  {started}")
    lines.append(f"- Finished: {finished}")
    lines.append(f"- Skills discovered: {len(results)}")
    lines.append(f"- Cycles run: {len(ran)}")
    lines.append(f"- Skipped (no task set): {len(skipped)}")
    lines.append(f"- Proposals STAGED for human review: {len(staged)}")
    lines.append("")
    lines.append("> SAFETY: auto_adopt=false, gate_mode=on, edit_budget<=3. "
                 "No live SKILL.md was modified. All proposals require manual review.")
    lines.append("")
    lines.append("## Cycles")
    lines.append("")
    lines.append("| Skill | Gate | Accepted | Val (pre->post) | Test soft (pre->post) | Edits | Staged | Ledger |")
    lines.append("|-------|------|----------|-----------------|-----------------------|-------|--------|--------|")
    for r in ran:
        le = r.get("ledger_events", {}) or {}
        ledger_ok = all((v or {}).get("ok") for v in le.values()) if le else False
        ledger_cell = ("ok " + "/".join(str((v or {}).get("status")) for v in le.values())) if le else "—"
        staged_cell = "YES" if r.get("staging_dir") else "no"
        lines.append(
            f"| {r['skill']} | {r.get('gate_action','?')} | {r.get('accepted')} | "
            f"{r.get('val_baseline')}->{r.get('val_candidate')} | "
            f"{r.get('test_pre_soft')}->{r.get('test_post_soft')} | "
            f"{r.get('edits_applied',0)} | {staged_cell} | {ledger_cell} |"
        )
    lines.append("")
    if staged:
        lines.append("## Staged Proposals (REVIEW REQUIRED)")
        lines.append("")
        for r in staged:
            lines.append(f"### {r['skill']}")
            lines.append(f"- Staging dir: `{r['staging_dir']}`")
            lines.append(f"- Val: {r.get('val_baseline')} -> {r.get('val_candidate')}")
            lines.append(f"- Test soft: {r.get('test_pre_soft')} -> {r.get('test_post_soft')}")
            lines.append(f"- Edits proposed: {r.get('edits_applied',0)}")
            lines.append(f"- Review: open `SKILL.diff` in the staging dir, then adopt manually if good.")
            lines.append("")
    if skipped:
        lines.append("## Skipped (no held-out task set)")
        lines.append("")
        for r in skipped:
            lines.append(f"- **{r['skill']}** — expected task set: `{r.get('tasks_path')}`")
        lines.append("")
        lines.append("> To include a skipped skill, author a held-out task set "
                     "(train/val/test splits) at the path above and re-run.")
        lines.append("")

    lines.append("## Raw Summaries")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(results, indent=2))
    lines.append("```")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description="Run SkillsOpt cycles across the whole skill fleet.")
    ap.add_argument("--only", default=None, help="comma-separated subset of skill names")
    ap.add_argument("--all-tasks-required", action="store_true",
                    help="treat a missing task set as an error instead of skipping")
    ap.add_argument("--report", default=FLEET_REPORT, help="output report path")
    args = ap.parse_args()

    cfg = _enforce_safety(load_config())
    skills_root = cfg.get("skills_root")
    skills = list_skills(skills_root)
    if args.only:
        wanted = {s.strip() for s in args.only.split(",") if s.strip()}
        skills = [s for s in skills if s in wanted]

    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    print("=" * 72)
    print(f"FLEET DEPLOY — {len(skills)} skills under {skills_root}")
    print(f"SAFETY: auto_adopt={cfg.get('auto_adopt')} gate_mode={cfg.get('gate_mode')} edit_budget={cfg.get('edit_budget')}")
    print("=" * 72)

    results: List[Dict[str, Any]] = []
    for skill in skills:
        tasks_path = _tasks_path_for(skill, None)
        rec: Dict[str, Any] = {"skill": skill, "tasks_path": tasks_path, "ran": False}
        if not os.path.exists(tasks_path):
            msg = f"no task set at {tasks_path}"
            if args.all_tasks_required:
                print(f"[ERROR] {skill}: {msg}")
                rec["error"] = msg
                results.append(rec)
                continue
            print(f"[skip] {skill}: {msg}")
            rec["error"] = msg
            results.append(rec)
            continue
        try:
            summary = run_cycle(cfg, skill, tasks_path, verbose=True)
            summary["ran"] = summary.get("error") is None
            results.append(summary)
        except Exception as e:  # noqa: BLE001
            print(f"[ERROR] {skill} cycle crashed: {e}")
            rec["error"] = f"crash: {e}"
            results.append(rec)

    finished = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    write_report(results, args.report, started=started, finished=finished)
    print("-" * 72)
    print(f"[fleet] report written: {args.report}")
    ran = sum(1 for r in results if r.get("ran"))
    staged = sum(1 for r in results if r.get("staging_dir"))
    print(f"[fleet] cycles run: {ran}/{len(results)}  staged proposals: {staged}")
    print("\n@@FLEET_SUMMARY@@" + json.dumps({
        "skills": len(results),
        "ran": ran,
        "staged": staged,
        "report": args.report,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
