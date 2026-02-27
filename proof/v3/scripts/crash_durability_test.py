import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts"
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / "crash_durability_test.log"


def run_case(flush: bool) -> bool:
    wal = OUT / ("wal_flush.log" if flush else "wal_noflush.log")
    wal.write_text("", encoding="utf-8")
    line = f"WAL-LINE flush={flush}\\n"
    code = (
        "import os,sys;"
        "p=sys.argv[1];line=sys.argv[2].encode();"
        "f=open(p,'ab', buffering=8192);"
        "f.write(line);"
        + ("f.flush();os.fsync(f.fileno());" if flush else "") +
        "os.abort()"
    )
    proc = subprocess.run([sys.executable, "-c", code, str(wal), line], capture_output=True)
    # abort should be non-zero
    data = wal.read_text(encoding="utf-8")
    survived = line in data
    with LOG.open("a", encoding="utf-8") as lf:
        lf.write(f"CASE flush={flush} rc={proc.returncode} survived={survived} bytes={len(data)}\\n")
    return survived


if __name__ == "__main__":
    if LOG.exists():
        LOG.unlink()
    ok_flush = run_case(True)
    ok_noflush = run_case(False)
    print(f"flush_survives={ok_flush}")
    print(f"noflush_survives={ok_noflush}")
    if not ok_flush:
        print("FAIL: flushed WAL did not survive")
        sys.exit(1)
    if ok_noflush:
        print("FAIL: no-flush WAL unexpectedly survived; test not discriminating")
        sys.exit(2)
    print("PASS: durability test discriminates flush vs no-flush")
