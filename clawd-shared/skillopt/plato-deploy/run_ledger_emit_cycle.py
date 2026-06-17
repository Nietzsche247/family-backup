"""SkillOpt-Sleep — Phase 1 POC runner for the `ledger-emit` skill.

Wires:
  harvest_memos (Stage 1, MemOS) -> seed TaskRecords (held-out set)
  -> OpenClawFleetBackend (Anthropic) -> dream_consolidate (replay+gate)
  -> stage proposal (auto_adopt=false, NEVER touches the live SKILL.md)
  -> emit NorthStar Ledger events per phase
  -> print pre/post score, gate result, and a before/after SKILL.md diff.

Safe by construction: gate_mode=on, auto_adopt=false, edit_budget<=3, and the
ledger POST is best-effort (failures are logged, never fatal).
"""
from __future__ import annotations

import difflib
import json
import os
import sys
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skillopt_sleep.config import load_config
from skillopt_sleep.dream import dream_consolidate
from skillopt_sleep.types import TaskRecord, SleepReport, EditRecord
from skillopt_sleep.state import SleepState, _now_iso

from harvest_memos import harvest_memos
from openclaw_fleet_backend import build_fleet_backend


API_KEY = "[REDACTED_ANTHROPIC_KEY]"

TASK_SET = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "plugins", "openclaw", "tests", "ledger-emit-tasks.json",
)
STAGING_ROOT = os.path.expanduser(r"~/.skillopt-sleep/staging")


def emit_ledger(cfg, phase: str, capsule: Dict[str, Any]) -> None:
    """Best-effort POST of a skill_optimization event. Never raises."""
    if not cfg.get("ledger_emit", True):
        return
    url = cfg.get("ledger_url", "http://127.0.0.1:3003").rstrip("/") + "/events"
    # The ledger enum has no "skill_optimization" type, so we emit a valid
    # status_update and carry the skill-optimization phase as a subtype + in
    # the decision_rationale / context_capsule payload (schema v1.1 friendly).
    payload = {
        "event_type": "status_update",
        "event_subtype": f"skill_optimization.{phase}",
        "agent": "aristotle",
        "skill_name": "ledger-emit",
        "phase": phase,
        "decision_rationale": f"SkillsOpt Phase 1 POC run [phase={phase}]",
        "context_capsule": capsule,
    }
    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"content-type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            ok = 200 <= resp.status < 300
        print(f"[ledger] emitted phase={phase} -> {'ok' if ok else resp.status}")
    except Exception as e:  # noqa: BLE001
        print(f"[ledger] WARN: emit failed phase={phase}: {e} (continuing)")


def load_tasks() -> List[TaskRecord]:
    with open(TASK_SET, encoding="utf-8") as f:
        raw = json.load(f)
    tasks: List[TaskRecord] = []
    for d in raw:
        tasks.append(TaskRecord(
            id=d["id"],
            project="ledger-emit",
            intent=d["intent"],
            reference_kind=d.get("reference_kind", "rule"),
            reference=d.get("reference", ""),
            judge=d.get("judge", {}),
            tags=d.get("tags", []),
            split=d.get("split", "train"),
            origin="real",
        ))
    return tasks


def read_skill(cfg) -> (str, str):
    root = cfg.get("skills_root")
    path = os.path.join(root, cfg.get("managed_skill_name", "ledger-emit"), "SKILL.md")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read(), path
    except Exception:
        return "", path


# A deliberately weak/incomplete skill used ONLY for the --degraded demo. It
# tells the agent ledger events exist but gives NO JSON schema / required
# fields, so the target model fails the rule rubrics and the optimizer has a
# real failure signal to learn from. The live SKILL.md is never touched.
DEGRADED_SKILL = """---
name: ledger-emit
description: "Emit events to the NorthStar Ledger."
---

# Ledger Emit

The system has a NorthStar Ledger that records what agents do.
When something noteworthy happens, you should let the ledger know about it.
Just describe what happened in plain language.
"""


def score_test(backend, tasks: List[TaskRecord], skill: str, memory: str) -> Dict[str, float]:
    """Score the held-out TEST split (never seen by the gate)."""
    from skillopt_sleep.replay import replay_batch, aggregate_scores
    test = [t for t in tasks if t.split == "test"]
    if not test:
        return {"hard": 0.0, "soft": 0.0, "n": 0}
    pairs = replay_batch(backend, test, skill, memory)
    h, s = aggregate_scores(pairs)
    return {"hard": h, "soft": s, "n": len(test)}


def main() -> int:
    cfg = load_config()
    print("=" * 72)
    print("SkillOpt-Sleep — Phase 1 POC: ledger-emit optimization cycle")
    print("=" * 72)

    # ── Stage 1: harvest from MemOS ──────────────────────────────────────
    db = cfg.get("memos_db")
    digests = harvest_memos(db, skill_name="ledger-emit", limit=cfg.get("max_tasks_per_night", 12) * 2)
    print(f"[harvest] MemOS: {len(digests)} sessions relevant to ledger-emit")

    # ── held-out task set (the gate's val/test data) ─────────────────────
    tasks = load_tasks()
    n_train = sum(1 for t in tasks if t.split == "train")
    n_val = sum(1 for t in tasks if t.split == "val")
    n_test = sum(1 for t in tasks if t.split == "test")
    print(f"[tasks] {len(tasks)} held-out tasks  (train={n_train} val={n_val} test={n_test})")

    # ── backend ──────────────────────────────────────────────────────────
    backend = build_fleet_backend(
        target_model=cfg.get("model", "anthropic/claude-sonnet-4-6"),
        optimizer_model=cfg.get("judge_model", "anthropic/claude-opus-4-8"),
        api_key=API_KEY,
    )
    print(f"[backend] {backend.name}")

    # ── live skill (READ ONLY) ───────────────────────────────────────────
    degraded = "--degraded" in sys.argv
    skill, skill_path = read_skill(cfg)
    memory = ""
    if degraded:
        print("[mode] DEGRADED DEMO — starting from a stripped skill to exercise "
              "the reflect->edit->gate->improve loop. Live SKILL.md NOT touched.")
        skill = DEGRADED_SKILL
        skill_path = "(in-memory degraded skill — demo only)"
    print(f"[skill] starting skill @ {skill_path} ({len(skill)} chars)")

    # ── ledger: cycle_start ──────────────────────────────────────────────
    emit_ledger(cfg, "cycle_start", {"pre_score": 0.0, "post_score": 0.0, "edits_applied": 0})

    # ── pre-score on TEST split with the live skill ──────────────────────
    pre = score_test(backend, tasks, skill, memory)
    print(f"[pre]  test-split score: hard={pre['hard']:.3f} soft={pre['soft']:.3f} (n={pre['n']})")

    # ── replay + consolidate (gate) ──────────────────────────────────────
    result = dream_consolidate(
        backend, tasks, skill, memory,
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

    print("-" * 72)
    print(f"[gate] action={result.gate_action}  accepted={result.accepted}")
    print(f"[gate] val score: {result.baseline_score:.3f} -> {result.candidate_score:.3f}")
    print(f"[edits] proposed/applied: {len(result.applied_edits)}  rejected: {len(result.rejected_edits)}")
    for e in result.applied_edits:
        print(f"   + [{e.target}/{e.op}] {e.content}")
        if e.rationale:
            print(f"     why: {e.rationale}")
    for e in result.rejected_edits:
        print(f"   - REJECTED [{e.target}/{e.op}] {e.content}")

    if result.applied_edits:
        emit_ledger(cfg, "edit_proposed", {
            "pre_score": result.baseline_score,
            "post_score": result.candidate_score,
            "edits_applied": len(result.applied_edits),
        })

    # ── post-score on TEST split with candidate skill ───────────────────
    cand_skill = result.new_skill
    post = score_test(backend, tasks, cand_skill, memory)
    print(f"[post] test-split score: hard={post['hard']:.3f} soft={post['soft']:.3f} (n={post['n']})")

    # ── stage proposal (NEVER modifies live SKILL.md) ────────────────────
    staging_dir = ""
    diff_text = ""
    if result.accepted and result.applied_edits and cand_skill != skill:
        os.makedirs(STAGING_ROOT, exist_ok=True)
        staging_dir = os.path.join(STAGING_ROOT, "ledger-emit-demo" if degraded else "ledger-emit-night1")
        os.makedirs(staging_dir, exist_ok=True)
        with open(os.path.join(staging_dir, "SKILL.proposed.md"), "w", encoding="utf-8") as f:
            f.write(cand_skill)
        with open(os.path.join(staging_dir, "SKILL.live.md"), "w", encoding="utf-8") as f:
            f.write(skill)
        diff_text = "".join(difflib.unified_diff(
            skill.splitlines(keepends=True),
            cand_skill.splitlines(keepends=True),
            fromfile="SKILL.md (live)", tofile="SKILL.md (proposed)",
        ))
        with open(os.path.join(staging_dir, "SKILL.diff"), "w", encoding="utf-8") as f:
            f.write(diff_text)
        report = {
            "skill": "ledger-emit",
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
        print(f"[stage] proposal staged at: {staging_dir} (live SKILL.md untouched)")
        emit_ledger(cfg, "adopted", {
            "pre_score": pre["soft"], "post_score": post["soft"],
            "edits_applied": len(result.applied_edits),
        })
    else:
        print("[stage] no accepted edits — nothing staged; live SKILL.md unchanged.")

    # ── ledger: cycle_complete ───────────────────────────────────────────
    emit_ledger(cfg, "cycle_complete", {
        "pre_score": pre["soft"], "post_score": post["soft"],
        "edits_applied": len(result.applied_edits),
    })

    # ── diff to stdout ───────────────────────────────────────────────────
    if diff_text:
        print("=" * 72)
        print("SKILL.md DIFF (live -> proposed):")
        print("=" * 72)
        print(diff_text)

    # ── token / backend stats ────────────────────────────────────────────
    try:
        toks = backend.tokens_used()
    except Exception:
        toks = -1
    print("-" * 72)
    print(f"[tokens] approx tokens used: {toks}")
    print("[done] Phase 1 POC complete.")

    # machine-readable summary block for the parent agent
    print("\n@@SUMMARY@@" + json.dumps({
        "harvested_sessions": len(digests),
        "n_tasks": len(tasks),
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
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
