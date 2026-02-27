import hashlib
import json
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
DB = ART / "ledger_demo.db"
MIG = ROOT / "migrations" / "001_v3_context_resilience.sql"


def now_utc():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_hash(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return sha256_bytes(raw)


def append_event(conn, session_id, event_type, payload):
    eid = f"evt-{uuid.uuid4()}"
    conn.execute(
        "INSERT INTO events(event_id,session_id,event_type,payload_json,created_at_utc) VALUES(?,?,?,?,?)",
        (eid, session_id, event_type, json.dumps(payload, sort_keys=True), now_utc()),
    )
    return eid


def main():
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    conn.executescript(MIG.read_text(encoding='utf-8'))

    session_id = "sess-001"
    handoff_id = "hof-001"
    base = ART / "sessions" / session_id / handoff_id
    z_path = base / "Z"
    shared_path = base / "shared"
    z_path.mkdir(parents=True, exist_ok=True)
    shared_path.mkdir(parents=True, exist_ok=True)

    # staging artifacts
    (z_path / "context.txt").write_text("critical context v3\n", encoding='utf-8')
    (z_path / "state.json").write_text(json.dumps({"step": "staged", "session": session_id}, sort_keys=True), encoding='utf-8')

    manifest = []
    for rel in ["context.txt", "state.json"]:
        p = z_path / rel
        manifest.append({"path": rel, "sha256": sha256_file(p), "bytes": p.stat().st_size})
    manifest_hash = canonical_json_hash(manifest)

    pointer = {
        "schema": "v3-pointer",
        "session_id": session_id,
        "handoff_id": handoff_id,
        "z_path": str(z_path),
        "shared_path": str(shared_path),
        "manifest": manifest,
        "manifest_hash": manifest_hash,
    }
    pointer_hash = canonical_json_hash(pointer)
    pointer_json = json.dumps(pointer, sort_keys=True)

    # stage
    conn.execute(
        """INSERT INTO handoffs(
            handoff_id,session_id,from_agent,to_agent,stage_pointer_json,stage_pointer_hash,stage_manifest_hash,stage_z_path,stage_shared_path,staged_at_utc
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (handoff_id, session_id, "supervisor", "worker-A", pointer_json, pointer_hash, manifest_hash, str(z_path), str(shared_path), now_utc()),
    )
    staged_eid = append_event(conn, session_id, "pointer-staged", {"handoff_id": handoff_id, "pointer_hash": pointer_hash})

    # replicate Z -> shared
    for entry in manifest:
        src = z_path / entry["path"]
        dst = shared_path / entry["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # verify hashes (server-side recompute from Z path)
    recomputed_manifest = []
    for entry in manifest:
        pz = z_path / entry["path"]
        recomputed_manifest.append({"path": entry["path"], "sha256": sha256_file(pz), "bytes": pz.stat().st_size})
    recomputed_manifest_hash = canonical_json_hash(recomputed_manifest)
    if recomputed_manifest_hash != manifest_hash:
        raise RuntimeError("manifest hash mismatch")

    recomputed_pointer = dict(pointer)
    recomputed_pointer["manifest"] = recomputed_manifest
    recomputed_pointer["manifest_hash"] = recomputed_manifest_hash
    recomputed_pointer_hash = canonical_json_hash(recomputed_pointer)
    if recomputed_pointer_hash != pointer_hash:
        raise RuntimeError("pointer hash mismatch")

    finalize_eid = append_event(conn, session_id, "pointer-finalized", {"handoff_id": handoff_id, "pointer_hash": recomputed_pointer_hash})
    finalized_at = now_utc()
    marker = z_path / "finalize.marker"
    marker.write_text(json.dumps({"handoff_id": handoff_id, "finalize_event_id": finalize_eid, "finalized_at_utc": finalized_at}, sort_keys=True), encoding='utf-8')

    conn.execute(
        """UPDATE handoffs
           SET finalized_pointer_json=?, finalized_pointer_hash=?, finalized_manifest_hash=?,
               finalized_at_utc=?, finalized_by_server=1, finalize_marker_path=?, ledger_finalize_event_id=?
         WHERE handoff_id=?""",
        (json.dumps(recomputed_pointer, sort_keys=True), recomputed_pointer_hash, recomputed_manifest_hash, finalized_at, str(marker), finalize_eid, handoff_id),
    )
    conn.execute(
        """INSERT INTO handoff_current(session_id,handoff_id,pointer_json,pointer_hash,updated_at_utc)
           VALUES(?,?,?,?,?)
           ON CONFLICT(session_id) DO UPDATE SET
             handoff_id=excluded.handoff_id,
             pointer_json=excluded.pointer_json,
             pointer_hash=excluded.pointer_hash,
             updated_at_utc=excluded.updated_at_utc""",
        (session_id, handoff_id, json.dumps(recomputed_pointer, sort_keys=True), recomputed_pointer_hash, finalized_at),
    )
    conn.commit()

    (ART / "pointer.json").write_text(json.dumps(recomputed_pointer, indent=2, sort_keys=True), encoding='utf-8')
    out = {
        "session_id": session_id,
        "handoff_id": handoff_id,
        "events": {"staged": staged_eid, "finalized": finalize_eid},
        "pointer_hash": recomputed_pointer_hash,
        "manifest_hash": recomputed_manifest_hash,
        "finalize_marker": str(marker),
    }
    (ART / "demo_run_output.json").write_text(json.dumps(out, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
