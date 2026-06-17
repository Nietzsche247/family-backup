"""SkillOpt-Sleep — MemOS harvester (Phase 1 POC).

Repoints Stage 1 of the sleep cycle at the OpenClaw **MemOS SQLite** store
instead of ~/.claude transcripts. It reads conversational `chunks` (grouped by
`session_key`) plus `tasks`/`skills` metadata and normalizes them into
:class:`SessionDigest` objects that ``mine.py`` / ``dream_consolidate`` accept.

Filtering: we keep chunks that are relevant to a target skill, matched by
  * an explicit chunks.skill_id == <skill uuid>, OR
  * chunks whose task_id belongs to a task whose title/summary mentions the
    skill topic, OR
  * a content keyword filter (e.g. "ledger", "/events") when the skill is
    ledger-emit and no explicit skill_id linkage exists yet.

This module performs NO writes and NO network calls. Read-only.
"""
from __future__ import annotations

import os
import sqlite3
from typing import Any, Dict, Iterable, List, Optional

from skillopt_sleep.types import SessionDigest
from skillopt_sleep.harvest import _detect_feedback, _is_meta_prompt


# ── DB helpers ────────────────────────────────────────────────────────────────

def _connect(db_path: str) -> sqlite3.Connection:
    # read-only connection (uri mode) so we never mutate the live store
    uri = "file:%s?mode=ro" % os.path.abspath(db_path).replace("\\", "/")
    try:
        return sqlite3.connect(uri, uri=True)
    except Exception:
        # fall back to a normal (still untouched) connection
        return sqlite3.connect(db_path)


def _skill_id_for_name(con: sqlite3.Connection, name: str) -> Optional[str]:
    row = con.execute("SELECT id FROM skills WHERE name = ?", (name,)).fetchone()
    return row[0] if row else None


def _ts_iso(epoch_ms: Any) -> str:
    if not epoch_ms:
        return ""
    try:
        import datetime as _dt
        # MemOS stores epoch milliseconds
        return _dt.datetime.utcfromtimestamp(int(epoch_ms) / 1000.0).isoformat() + "Z"
    except Exception:
        return ""


# ── core: build digests from MemOS chunks ─────────────────────────────────────

def _matching_session_keys(
    con: sqlite3.Connection,
    *,
    skill_id: Optional[str],
    keywords: List[str],
    task_keywords: List[str],
) -> List[str]:
    """Find session_keys whose chunks are relevant to the target skill."""
    keys: List[str] = []
    seen = set()

    def _add(sk: str) -> None:
        if sk and sk not in seen:
            seen.add(sk)
            keys.append(sk)

    # 1) explicit skill_id linkage on chunks
    if skill_id:
        for (sk,) in con.execute(
            "SELECT DISTINCT session_key FROM chunks WHERE skill_id = ?", (skill_id,)
        ):
            _add(sk)

    # 2) chunks whose task_id belongs to a task mentioning the topic
    if task_keywords:
        like = " OR ".join(["title LIKE ? OR summary LIKE ?"] * len(task_keywords))
        params: List[str] = []
        for kw in task_keywords:
            params += [f"%{kw}%", f"%{kw}%"]
        task_ids = [r[0] for r in con.execute(f"SELECT id FROM tasks WHERE {like}", params)]
        if task_ids:
            qmarks = ",".join("?" * len(task_ids))
            for (sk,) in con.execute(
                f"SELECT DISTINCT session_key FROM chunks WHERE task_id IN ({qmarks})",
                task_ids,
            ):
                _add(sk)

    # 3) content keyword fallback (the ledger-emit case: chunks aren't yet
    #    skill-tagged, so match on the event/endpoint vocabulary)
    if keywords:
        like = " OR ".join(["content LIKE ?"] * len(keywords))
        params = [f"%{kw}%" for kw in keywords]
        for (sk,) in con.execute(
            f"SELECT DISTINCT session_key FROM chunks WHERE {like}", params
        ):
            _add(sk)

    return keys


def _digest_session(con: sqlite3.Connection, session_key: str) -> Optional[SessionDigest]:
    rows = con.execute(
        "SELECT role, content, kind, created_at, task_id, skill_id "
        "FROM chunks WHERE session_key = ? ORDER BY seq ASC, created_at ASC",
        (session_key,),
    ).fetchall()
    if not rows:
        return None

    user_prompts: List[str] = []
    assistant_finals: List[str] = []
    tools: List[str] = []
    feedback: List[str] = []
    started = ""
    ended = ""
    n_user = 0
    n_asst = 0
    project = "memos"
    task_ids = set()

    for role, content, kind, created_at, task_id, skill_id in rows:
        content = content or ""
        ts = _ts_iso(created_at)
        if ts:
            if not started:
                started = ts
            ended = ts
        if task_id:
            task_ids.add(task_id)
        if (kind or "").lower() in ("tool", "tool_call", "tool_use"):
            tools.append((content or "").split("\n", 1)[0][:60])
            continue
        if role == "user":
            if content and not _is_meta_prompt(content):
                n_user += 1
                user_prompts.append(content.strip())
                feedback.extend(_detect_feedback(content))
        elif role == "assistant":
            n_asst += 1
            if content.strip():
                assistant_finals.append(content.strip())

    if n_user == 0 and n_asst == 0:
        return None

    return SessionDigest(
        session_id=session_key,
        project=project,
        git_branch="",
        started_at=started,
        ended_at=ended,
        user_prompts=user_prompts,
        assistant_finals=assistant_finals[-5:],
        tools_used=list(dict.fromkeys(tools)),
        files_touched=[],
        feedback_signals=feedback,
        n_user_turns=n_user,
        n_assistant_turns=n_asst,
        raw_path=f"memos://{session_key}",
    )


def harvest_memos(
    db_path: str,
    *,
    skill_name: str = "",
    keywords: Optional[List[str]] = None,
    task_keywords: Optional[List[str]] = None,
    since_iso: Optional[str] = None,
    limit: int = 0,
) -> List[SessionDigest]:
    """Read MemOS and return SessionDigests relevant to ``skill_name``.

    Parameters
    ----------
    db_path : path to memos.db
    skill_name : managed skill name, e.g. "ledger-emit" (resolved to a uuid)
    keywords : content keywords to match chunks on (fallback linkage)
    task_keywords : keywords to match tasks.title/summary on
    since_iso : ISO8601; only sessions ending after this kept
    limit : cap number of digests (0 = no cap)
    """
    if not os.path.exists(db_path):
        return []
    keywords = keywords if keywords is not None else (["ledger", "/events"] if skill_name == "ledger-emit" else [])
    task_keywords = task_keywords if task_keywords is not None else ([skill_name.replace("-", " "), "ledger"] if skill_name else [])

    con = _connect(db_path)
    try:
        skill_id = _skill_id_for_name(con, skill_name) if skill_name else None
        session_keys = _matching_session_keys(
            con, skill_id=skill_id, keywords=keywords, task_keywords=task_keywords
        )
        digests: List[SessionDigest] = []
        for sk in session_keys:
            d = _digest_session(con, sk)
            if d is None:
                continue
            if since_iso and d.ended_at and d.ended_at < since_iso:
                continue
            digests.append(d)
        # newest first
        digests.sort(key=lambda d: d.ended_at or "", reverse=True)
        if limit:
            digests = digests[:limit]
        return digests
    finally:
        con.close()


# ── convenience: standalone debug ─────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\aaron\.openclaw\memos-local\memos.db"
    ds = harvest_memos(db, skill_name="ledger-emit", limit=10)
    print(f"[harvest_memos] {len(ds)} sessions matched")
    for d in ds[:5]:
        print(f"  - {d.session_id[:40]:40s} u={d.n_user_turns} a={d.n_assistant_turns} "
              f"tools={len(d.tools_used)} ended={d.ended_at}")
