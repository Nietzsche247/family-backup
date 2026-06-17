"""SkillOpt-Sleep — generic single-skill optimization cycle runner (Phase 2).

Generalizes run_ledger_emit_cycle.py to ANY managed skill + held-out task set.

Wires:
  harvest_memos (Stage 1, MemOS) -> context digests (best-effort, may be empty)
  held-out task set (train/val/test) -> the gate's data
  OpenClawFleetBackend (Anthropic) -> dream_consolidate (replay + gate)
  stage proposal (auto_adopt=false, NEVER touches the live SKILL.md)
  emit NorthStar Ledger `skill_optimization` events per phase
  print pre/post score, gate result, before/after SKILL.md diff

Safe by construction: gate_mode=on, auto_adopt=false, edit_budget<=3, and the
ledger POST is best-effort (failures are logged, never fatal). The live
SKILL.md is read-only; proposals are written to STAGING only.

Usage:
  python run_skill_cycle.py --skill probe-fleet-health \
      --tasks plugins/openclaw/tests/probe-fleet-health-tasks.json
  python run_skill_cycle.py --skill ledger-emit            # auto-resolve tasks
  (programmatic) from run_skill_cycle import run_cycle; run_cycle(cfg, "probe-fleet-health", tasks_path)
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from skillopt_sleep.config import load_config
from skillopt_sleep.dream import dream_consolidate
from skillopt_sleep.types import TaskRecord

from harvest_memos import harvest_memos
from openclaw_fleet_backend import build_fleet_backend

# Reuse the proven API key + paths from the Phase 1 runner.
from run_ledger_emit_cycle import API_KEY, STAGING_ROOT


def _tasks_path_for(skill: str, explicit: Optional[str]) -> str:
    if explicit:
        return explicit if os.path.isabs(explicit) else os.path.join(HERE, explicit)
    return os.path.join(HERE, "plugins", "openclaw", "tests", f"{skill}-tasks.json")


def emit_ledger(cfg: Dict[str, Any], skill: str, phase: str, capsule: Dict[str, Any]) -> Dict[str, Any]:
    """Best-effort POST of a `skill_optimization` event. Never raises.

    Phase 2: the ledger enum now includes `skill_optimization`, so we emit that
    canonical type directly (carrying the cycle phase as event_subtype).
    """
    out = {"ok": False, "status": None, "event_id": None}
    if not cfg.get("ledger_emit", True):
        out["status"] = "disabled"
        return out
    url = cfg.get("ledger_url", "http://127.0.0.1:3003").rstrip("/") + "/events"
    payload = {
        "event_type": "skill_optimization",
        "event_subtype": f"skill_optimization.{phase}",
        "agent": cfg.get("ledger_agent", "thales"),
        "skill_name": skill,
        "phase": phase,
        "decision_rationale": f"SkillsOpt cycle [skill={skill} phase={phase}]",
        "context_capsule": capsule,
    }
    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"content-type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            out["status"] = resp.status
            out["ok"] = 200 <= resp.status < 300
            try:
                data = json.loads(resp.read().decode("utf-8"))
                out["event_id"] = data.get("event_id")
            except Exception:
                pass
        print(f"[ledger] emitted skill={skill} phase={phase} -> {out['status']}")
    except urllib.error.HTTPError as e:
        out["status"] = e.code
        try:
            out["error"] = e.read().decode("utf-8")[:200]
        except Exception:
            out["error"] = str(e)
        print(f"[ledger] WARN: emit failed skill={skill} phase={phase}: HTTP {e.code} (continuing)")
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)
        print(f"[ledger] WARN: emit failed skill={skill} phase={phase}: {e} (continuing)")
    return out


def load_tasks(tasks_path: str) -> List[TaskRecord]:
    with open(tasks_path, encoding="utf-8") as f:
        raw = json.load(f)
    tasks: List[TaskRecord] = []
    for d in raw:
        tasks.append(TaskRecord(
            id=d["id"],
            project=d.get("project", "skillopt"),
            intent=d["intent"],
            reference_kind=d.get("reference_kind", "rule"),
            reference=d.get("reference", ""),
            judge=d.get("judge", {}),
            tags=d.get("tags", []),
            split=d.get("split", "train"),
            origin="real",
        ))
    return tasks


def read_skill(cfg: Dict[str, Any], skill: str) -> (str, str):
    root = cfg.get("skills_root")
    path = os.path.join(root, skill, "SKILL.md")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read(), path
    except Exception:
        return "", path


def score_split(backend, tasks: List[TaskRecord], skill_text: str, memory: str, split: str) -> Dict[str, float]:
    from skillopt_sleep.replay import replay_batch, aggregate_scores
    sub = [t for t in tasks if t.split == split]
    if not sub:
        return {"hard": 0.0, "soft": 0.0, "n": 0}
    pairs = replay_batch(backend, sub, skill_text, memory)
    h, s = aggregate_scores(pairs)
    return {"hard": h, "soft": s, "n": len(sub)}


def run_cycle(cfg: Dict[str, Any], skill: str, tasks_path: str, *, verbose: bool = True) -> Dict[str, Any]:
    """Run ONE optimization cycle for a single skill. Returns a summary dict.

    SAFETY: never writes the live SKILL.md; proposals go to STAGING only.
    """
    def log(*a):
        if verbose:
            print(*a)

    log("=" * 72)
    log(f"SkillOpt-Sleep — optimization cycle: {skill}")
    log("=" * 72)

    summary: Dict[str, Any] = {
        "skill": skill,
        "tasks_path": tasks_path,
        "ledger_events": {},
        "error": None,
    }

    if not os.path.exists(tasks_path):
        msg = f"task set not found: {tasks_path}"
        log(f"[skip] {msg}")
        summary["error"] = msg
        return summary

    # ── Stage 1: harvest from MemOS (best-effort) ────────────────────────
    db = cfg.get("memos_db")
    try:
        digests = harvest_memos(db, skill_name=skill, limit=cfg.get("max_tasks_per_night", 12) * 2)
    except Exception as e:  # noqa: BLE001
        digests = []
        log(f"[harvest] WARN: {e}")
    log(f"[harvest] MemOS: {len(digests)} sessions relevant to {skill}")
    summary["harvested_sessions"] = len(digests)

    # ── held-out task set ────────────────────────────────────────────────
    tasks = load_tasks(tasks_path)
    n_train = sum(1 for t in tasks if t.split == "train")
    n_val = sum(1 for t in tasks if t.split == "val")
    n_test = sum(1 for t in tasks if t.split == "test")
    log(f"[tasks] {len(tasks)} held-out tasks  (train={n_train} val={n_val} test={n_test})")
    summary["n_tasks"] = len(tasks)

    # ── backend ──────────────────────────────────────────────────────────
    backend = build_fleet_backend(
        target_model=cfg.get("model", "anthropic/claude-sonnet-4-6"),
        optimizer_model=cfg.get("judge_model", "anthropic/claude-opus-4-8"),
        api_key=API_KEY,
    )
    log(f"[backend] {backend.name}")

    # ── live skill (READ ONLY) ───────────────────────────────────────────
    skill_text, skill_path = read_skill(cfg, skill)
    memory = ""
    log(f"[skill] starting skill @ {skill_path} ({len(skill_text)} chars)")
    if not skill_text:
        msg = f"live SKILL.md not found/empty for {skill} @ {skill_path}"
        log(f"[skip] {msg}")
        summary["error"] = msg
        return summary

    # ── ledger: cycle_start ──────────────────────────────────────────────
    summary["ledger_events"]["cycle_start"] = emit_ledger(
        cfg, skill, "cycle_start", {"pre_score": 0.0, "post_score": 0.0, "edits_applied": 0})

    # ── pre-score on TEST split with live skill ──────────────────────────
    pre = score_split(backend, tasks, skill_text, memory, "test")
    log(f"[pre]  test-split score: hard={pre['hard']:.3f} soft={pre['soft']:.3f} (n={pre['n']})")

    # ── replay + consolidate (gate) ──────────────────────────────────────
    result = dream_consolidate(
        backend, tasks, skill_text, memory,
        history_tasks=[],
        recall_k=int(cfg.get("recall_k", 0) or 0),
        dream_rollouts=int(cfg.get("dream_rollouts", 1) or 1),
        dream_factor=int(cfg.get("dream_factor", 0) or 0),
        edit_budget=int(cfg.get("edit_budget", 3)),
        gate_metric=cfg.get("gate_metric", "mixed"),
        gate_mode=cfg.get("gate_mode", "on"),
        evolve_skill=bool(cfg.get("evolve_skill", True)),
        evolve_memory=bool(cfg.get("evolve_memory", False)),
        night=1,
    )

    log("-" * 72)
    log(f"[gate] action={result.gate_action}  accepted={result.accepted}")
    log(f"[gate] val score: {result.baseline_score:.3f} -> {result.candidate_score:.3f}")
    log(f"[edits] proposed/applied: {len(result.applied_edits)}  rejected: {len(result.rejected_edits)}")
    for e in result.applied_edits:
        log(f"   + [{e.target}/{e.op}] {e.content}")
        if e.rationale:
            log(f"     why: {e.rationale}")
    for e in result.rejected_edits:
        log(f"   - REJECTED [{e.target}/{e.op}] {e.content}")

    if result.applied_edits:
        summary["ledger_events"]["edit_proposed"] = emit_ledger(cfg, skill, "edit_proposed", {
            "pre_score": result.baseline_score,
            "post_score": result.candidate_score,
            "edits_applied": len(result.applied_edits),
        })

    # ── post-score on TEST split with candidate skill ───────────────────
    cand_skill = result.new_skill
    post = score_split(backend, tasks, cand_skill, memory, "test")
    log(f"[post] test-split score: hard={post['hard']:.3f} soft={post['soft']:.3f} (n={post['n']})")

    # ── stage proposal (NEVER modifies live SKILL.md) ────────────────────
    staging_dir = ""
    diff_text = ""
    if result.accepted and result.applied_edits and cand_skill != skill_text:
        os.makedirs(STAGING_ROOT, exist_ok=True)
        staging_dir = os.path.join(STAGING_ROOT, f"{skill}-phase2")
        os.makedirs(staging_dir, exist_ok=True)
        with open(os.path.join(staging_dir, "SKILL.proposed.md"), "w", encoding="utf-8") as f:
            f.write(cand_skill)
        with open(os.path.join(staging_dir, "SKILL.live.md"), "w", encoding="utf-8") as f:
            f.write(skill_text)
        diff_text = "".join(difflib.unified_diff(
            skill_text.splitlines(keepends=True),
            cand_skill.splitlines(keepends=True),
            fromfile="SKILL.md (live)", tofile="SKILL.md (proposed)",
        ))
        with open(os.path.join(staging_dir, "SKILL.diff"), "w", encoding="utf-8") as f:
            f.write(diff_text)
        report = {
            "skill": skill,
            "gate_action": result.gate_action,
            "accepted": result.accepted,
            "val_baseline": result.baseline_score,
            "val_candidate": result.candidate_score,
            "test_pre": pre, "test_post": post,
            "edits_applied": [e.__dict__ for e in result.applied_edits],
            "edits_rejected": [e.__dict__ for e in result.rejected_edits],
            "backend": backend.name,
            "auto_adopt": False,
            "note": "PROPOSAL ONLY — human must review and adopt manually.",
        }
        with open(os.path.join(staging_dir, "report.json"), "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        log(f"[stage] proposal staged at: {staging_dir} (live SKILL.md untouched)")
        summary["ledger_events"]["adopted"] = emit_ledger(cfg, skill, "adopted", {
            "pre_score": pre["soft"], "post_score": post["soft"],
            "edits_applied": len(result.applied_edits),
        })
    else:
        log("[stage] no accepted edits — nothing staged; live SKILL.md unchanged.")

    # ── ledger: cycle_complete ───────────────────────────────────────────
    summary["ledger_events"]["cycle_complete"] = emit_ledger(cfg, skill, "cycle_complete", {
        "pre_score": pre["soft"], "post_score": post["soft"],
        "edits_applied": len(result.applied_edits),
    })

    if diff_text:
        log("=" * 72)
        log("SKILL.md DIFF (live -> proposed):")
        log("=" * 72)
        log(diff_text)

    try:
        toks = backend.tokens_used()
    except Exception:
        toks = -1
    log("-" * 72)
    log(f"[tokens] approx tokens used: {toks}")

    summary.update({
        "gate_action": result.gate_action,
        "accepted": result.accepted,
        "val_baseline": round(result.baseline_score, 3),
        "val_candidate": round(result.candidate_score, 3),
        "test_pre_soft": round(pre["soft"], 3),
        "test_post_soft": round(post["soft"], 3),
        "test_pre_hard": round(pre["hard"], 3),
        "test_post_hard": round(post["hard"], 3),
        "edits_applied": len(result.applied_edits),
        "edits_rejected": len(result.rejected_edits),
        "staging_dir": staging_dir,
        "tokens": toks,
        "skill_path": skill_path,
    })
    log("[done] cycle complete.")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="Run one SkillsOpt cycle for a single skill.")
    ap.add_argument("--skill", required=True, help="managed skill name (dir under skills_root)")
    ap.add_argument("--tasks", default=None, help="path to held-out task set JSON (auto if omitted)")
    args = ap.parse_args()

    cfg = load_config()
    tasks_path = _tasks_path_for(args.skill, args.tasks)
    summary = run_cycle(cfg, args.skill, tasks_path)
    print("\n@@SUMMARY@@" + json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
