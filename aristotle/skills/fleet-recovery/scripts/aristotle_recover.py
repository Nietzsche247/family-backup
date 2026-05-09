#!/usr/bin/env python3
"""
aristotle_recover.py  (v2)
==========================
Full recovery for Aristotle clawdbot gateway + ngrok tunnel on
Omni-AlienWare2025.

What it does (default mode):
  1. DIAGNOSE current state
       - port 18792 listening?
       - HTTP responding (catches hung gateway with bound port)?
       - ngrok agent up?
       - tunnel registered locally? reachable publicly?
       - duplicate supervisors?
  2. TEAR DOWN every gateway-related process and ngrok
  3. WAIT for port 18792 to free
  4. TRIGGER the "Aristotle Gateway" Scheduled Task
  5. WAIT for the gateway to bind port 18792 AND respond to HTTP
  6. TRIGGER the "Aristotle Ngrok" Scheduled Task
  7. WAIT for the tunnel to register at http://127.0.0.1:4040
  8. ATTEMPT public-URL probe (best effort; NAT loopback may fail)
  9. VERIFY everything is green
 10. BACKUP config (daily snapshot to clawd-shared\\backups\\)

Modes:
    aristotle_recover.py            full recovery (the hammer)
    aristotle_recover.py --soft     only restart pieces that are broken
    aristotle_recover.py --check    diagnose only, no changes
    aristotle_recover.py --json     emit one JSON object on stdout (no human text)
    aristotle_recover.py -v         verbose

Combine: --check --json (machine-readable status snapshot, no side effects)

Exit codes:
    0  -- success: gateway and ngrok both healthy
    1  -- recovery failed (both down)
    2  -- partial: gateway up, ngrok down
    3  -- partial: ngrok up, gateway down
    10 -- --check mode: at least one component down (informational)

Stdlib only -- no pip install required. Tested on Python 3.12.
"""

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from typing import List, Optional, Tuple

# =============================================================================
# CONFIG
# =============================================================================

GATEWAY_PORT             = 18792
NGROK_API                = "http://127.0.0.1:4040/api/tunnels"
GATEWAY_HEALTH_URL       = "http://127.0.0.1:18792/"
EXPECTED_NGROK_URL       = "https://uneffective-unprepossessingly-september.ngrok-free.dev"
PUBLIC_HEALTH_PATH       = "/"  # GET against the public URL
GATEWAY_TASK             = "Aristotle Gateway"
NGROK_TASK               = "Aristotle Ngrok"

# Files
CLAWDBOT_CONFIG          = r"C:\Users\aaron\.clawdbot-aristotle\clawdbot.json"
BACKUP_DIR               = r"C:\Users\aaron\clawd-shared\backups"
TASK_GATEWAY_LOG         = r"C:\tmp\clawdbot-aristotle\task-gateway.log"
TASK_NGROK_LOG           = r"C:\tmp\clawdbot-aristotle\task-ngrok.log"
GATEWAY_LOG_DIR          = r"C:\tmp\clawdbot"  # holds clawdbot-YYYY-MM-DD.log

# Timeouts
GATEWAY_BIND_TIMEOUT_S   = 120
GATEWAY_HTTP_TIMEOUT_S   = 10
NGROK_REGISTER_TIMEOUT_S = 30
NGROK_PUBLIC_TIMEOUT_S   = 15
PORT_FREE_TIMEOUT_S      = 15
HUNG_RECOVERY_WAIT_S     = 30   # after killing a hung node, wait for supervisor restart

# =============================================================================
# OUTPUT
# =============================================================================

class C:
    """ANSI colors, disabled in non-tty or --json mode."""
    if sys.stdout.isatty():
        RED, GREEN, YELLOW, CYAN, BOLD, END = (
            "\033[91m", "\033[92m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"
        )
    else:
        RED = GREEN = YELLOW = CYAN = BOLD = END = ""

VERBOSE   = False
JSON_MODE = False  # when True, all human output goes to stderr; stdout reserved for final JSON


def _out(s: str) -> None:
    """Write to stdout in human mode, stderr in JSON mode."""
    if JSON_MODE:
        sys.stderr.write(s + "\n")
    else:
        print(s)


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def info(msg: str) -> None:
    _out(f"{C.CYAN}{_ts()}   {msg}{C.END}")


def ok(msg: str) -> None:
    _out(f"{C.GREEN}{_ts()} + {msg}{C.END}")


def warn(msg: str) -> None:
    _out(f"{C.YELLOW}{_ts()} ! {msg}{C.END}")


def err(msg: str) -> None:
    _out(f"{C.RED}{_ts()} x {msg}{C.END}")


def header(msg: str) -> None:
    _out(f"\n{C.BOLD}=== {msg} ==={C.END}")


def vinfo(msg: str) -> None:
    if VERBOSE:
        info(msg)


# =============================================================================
# HELPERS - process inspection (PowerShell + native Windows tools)
# =============================================================================

def run_ps(script: str, timeout: int = 30) -> Tuple[int, str, str]:
    try:
        r = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True, text=True, timeout=timeout
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "powershell timeout"
    except FileNotFoundError:
        return 127, "", "powershell.exe not found on PATH"


def find_processes(name: str, cmd_substr: str) -> List[dict]:
    """Win32_Process WHERE Name=name AND CommandLine LIKE *cmd_substr*."""
    ps = (
        f"Get-CimInstance Win32_Process -Filter \"Name='{name}'\" | "
        f"Where-Object {{ $_.CommandLine -like '*{cmd_substr}*' }} | "
        f"Select-Object ProcessId, ParentProcessId, CommandLine | "
        f"ConvertTo-Json -Compress -Depth 3"
    )
    rc, out, _ = run_ps(ps)
    out = out.strip()
    if not out or rc != 0:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        vinfo(f"could not parse process JSON: {out[:200]}")
        return []
    if isinstance(data, dict):
        data = [data]
    return [
        {
            "pid":  int(d["ProcessId"]),
            "ppid": int(d.get("ParentProcessId") or 0),
            "cmd":  (d.get("CommandLine") or "").strip(),
        }
        for d in data
    ]


def get_port_owner(port: int) -> Optional[int]:
    """PID listening on `port`, or None."""
    try:
        out = subprocess.check_output(["netstat", "-ano"], text=True, timeout=10)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None
    pat = re.compile(rf":{port}\s+\S+\s+LISTENING\s+(\d+)")
    for line in out.splitlines():
        m = pat.search(line)
        if m:
            return int(m.group(1))
    return None


# =============================================================================
# HELPERS - HTTP probes
# =============================================================================

def http_probe(url: str, timeout: int, headers: Optional[dict] = None) -> dict:
    """
    Probe an HTTP URL. Returns:
      {"ok": bool, "status": int|None, "time_ms": int, "error": str|None,
       "body_len": int}
    "ok" = True iff the server returned an HTTP response (any code >= 100).
    Network/timeout failures = ok=False.
    """
    req = urllib.request.Request(url, headers=headers or {})
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            return {"ok": True, "status": r.status, "time_ms": elapsed_ms,
                    "error": None, "body_len": len(body)}
    except urllib.error.HTTPError as e:
        # 4xx/5xx — server responded, just unhappy. That's still proof of life.
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        return {"ok": True, "status": e.code, "time_ms": elapsed_ms,
                "error": None, "body_len": 0}
    except Exception as e:
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        return {"ok": False, "status": None, "time_ms": elapsed_ms,
                "error": str(e)[:200], "body_len": 0}


def http_get_json(url: str, timeout: int = 5) -> Optional[dict]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return None


def gateway_http_health() -> dict:
    """HTTP probe of the local gateway. Catches hung-but-bound state."""
    return http_probe(GATEWAY_HEALTH_URL, GATEWAY_HTTP_TIMEOUT_S)


def public_tunnel_probe() -> dict:
    """
    Best-effort GET through the public ngrok URL.
    May fail due to NAT loopback even when tunnel is genuinely working.
    Caller should treat failure as "unverified" not "broken".
    """
    return http_probe(
        EXPECTED_NGROK_URL.rstrip("/") + PUBLIC_HEALTH_PATH,
        NGROK_PUBLIC_TIMEOUT_S,
        headers={"ngrok-skip-browser-warning": "1",
                 "User-Agent": "aristotle-recover/2.0"},
    )


# =============================================================================
# HELPERS - actions
# =============================================================================

def kill_tree(pid: int) -> bool:
    """taskkill /T /F /PID. Returns True if killed or already-gone."""
    try:
        r = subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(pid)],
            capture_output=True, text=True, timeout=15,
        )
        return r.returncode in (0, 128)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def trigger_task(task_name: str) -> bool:
    try:
        r = subprocess.run(
            ["schtasks", "/run", "/TN", task_name],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode != 0:
            warn(f"schtasks /run failed: {(r.stderr or r.stdout).strip()}")
        return r.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        err(f"schtasks invocation failed: {e}")
        return False


# =============================================================================
# HELPERS - log tailing
# =============================================================================

def tail_log(path: str, n: int = 20) -> List[str]:
    """Best-effort tail. Returns up to last N lines. Empty list on any failure."""
    try:
        if not os.path.isfile(path):
            return []
        # Cheap implementation: read whole file. Logs are bounded.
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return [l.rstrip("\n") for l in lines[-n:]]
    except Exception as e:
        vinfo(f"tail_log({path}) failed: {e}")
        return []


def todays_clawdbot_log() -> str:
    return os.path.join(GATEWAY_LOG_DIR, f"clawdbot-{datetime.now().strftime('%Y-%m-%d')}.log")


def dump_log_tail(label: str, path: str, n: int = 15, max_line_chars: int = 220) -> None:
    """Print a log tail with a header. No-op in JSON mode."""
    if JSON_MODE:
        return
    lines = tail_log(path, n)
    if not lines:
        warn(f"  {label}: log not found or empty ({path})")
        return
    _out(f"\n{C.BOLD}--- tail: {label} ({path}) ---{C.END}")
    for ln in lines:
        if len(ln) > max_line_chars:
            ln = ln[:max_line_chars] + "..."
        _out(f"  {ln}")


# =============================================================================
# HELPERS - config backup
# =============================================================================

def backup_config() -> Optional[str]:
    """
    Daily snapshot of clawdbot.json to clawd-shared\\backups\\.
    Skips if today's backup already exists. Returns backup path or None.
    """
    if not os.path.isfile(CLAWDBOT_CONFIG):
        return None
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
    except OSError as e:
        warn(f"could not create backup dir: {e}")
        return None
    dest = os.path.join(
        BACKUP_DIR,
        f"clawdbot-aristotle-{datetime.now().strftime('%Y-%m-%d')}.json",
    )
    if os.path.isfile(dest):
        vinfo(f"backup already exists: {dest}")
        return dest
    try:
        shutil.copy2(CLAWDBOT_CONFIG, dest)
        return dest
    except OSError as e:
        warn(f"backup failed: {e}")
        return None


# =============================================================================
# DIAGNOSE
# =============================================================================

def snapshot(probe_public: bool = True) -> dict:
    """Capture full current state."""
    # Gateway supervisors come in two flavors that share PIDs via `call`:
    #   - aristotle-gateway-task.cmd (Scheduled Task wrapper)
    #   - gateway-resilient.cmd (manual launches)
    sup_a = find_processes("cmd.exe", "aristotle-gateway-task")
    sup_b = find_processes("cmd.exe", "gateway-resilient")
    seen = set()
    gateway_supervisors = []
    for p in sup_a + sup_b:
        if p["pid"] not in seen:
            seen.add(p["pid"])
            gateway_supervisors.append(p)

    port_pid    = get_port_owner(GATEWAY_PORT)
    gw_http     = gateway_http_health() if port_pid else {"ok": False, "status": None,
                                                          "time_ms": 0, "error": "port not bound",
                                                          "body_len": 0}
    tunnels_api = http_get_json(NGROK_API, timeout=3)
    public      = public_tunnel_probe() if probe_public else None

    return {
        "port_pid":             port_pid,
        "gateway_http":         gw_http,
        "gateway_supervisors":  gateway_supervisors,
        "ngrok_supervisors":    find_processes("cmd.exe", "aristotle-ngrok-task"),
        "gw_nodes":             find_processes("node.exe", "entry.js gateway"),
        "ngroks":               find_processes("ngrok.exe", "ngrok"),
        "tunnels_local":        tunnels_api,
        "public_probe":         public,
    }


def print_state(s: dict) -> None:
    pid = s["port_pid"]
    if pid:
        ok(f"port {GATEWAY_PORT}: LISTENING (PID {pid})")
    else:
        warn(f"port {GATEWAY_PORT}: not listening")

    h = s["gateway_http"]
    if h["ok"]:
        ok(f"gateway HTTP: {h['status']} in {h['time_ms']}ms ({h['body_len']} bytes)")
    elif pid:
        err(f"gateway HTTP: NOT RESPONDING (port bound but {h['error'] or 'no response'}) -- HUNG")
    else:
        warn("gateway HTTP: no probe (port not bound)")

    sup_n = len(s["gateway_supervisors"])
    if sup_n == 1:
        ok("gateway supervisors: 1")
    elif sup_n == 0 and pid:
        warn("gateway supervisors: 0 (gateway running unsupervised)")
    elif sup_n == 0:
        warn("gateway supervisors: 0")
    else:
        warn(f"gateway supervisors: {sup_n} (DUPLICATE -- they will collide)")
    for sp in s["gateway_supervisors"]:
        vinfo(f"  pid={sp['pid']} ppid={sp['ppid']}")

    info(f"ngrok supervisors: {len(s['ngrok_supervisors'])}")
    info(f"gateway node procs: {len(s['gw_nodes'])}")
    info(f"ngrok processes:    {len(s['ngroks'])}")

    t = s["tunnels_local"]
    if t and t.get("tunnels"):
        urls = [x["public_url"] for x in t["tunnels"]]
        ok(f"tunnels (local API): {urls}")
        if EXPECTED_NGROK_URL not in urls:
            warn(f"  expected URL {EXPECTED_NGROK_URL} NOT in tunnel list")
    else:
        warn("tunnels (local API): none")

    p = s["public_probe"]
    if p is None:
        info("public URL: probe skipped")
    elif p["ok"]:
        ok(f"public URL: {p['status']} in {p['time_ms']}ms (verified end-to-end)")
    else:
        # Could be NAT loopback OR genuinely down. Distinguish via local tunnel state.
        if t and t.get("tunnels"):
            warn(f"public URL: probe failed ({p['error']}) -- "
                 "may be NAT loopback; tunnel is registered locally")
        else:
            err(f"public URL: probe failed ({p['error']}) -- and no local tunnel either")


# =============================================================================
# TEARDOWN / BRING UP
# =============================================================================

def teardown() -> bool:
    s = snapshot(probe_public=False)

    for p in s["ngroks"]:
        info(f"killing ngrok PID {p['pid']}")
        kill_tree(p["pid"])

    pids = ({p["pid"] for p in s["gateway_supervisors"]}
            | {p["pid"] for p in s["ngrok_supervisors"]})
    for pid in pids:
        info(f"killing supervisor/wrapper tree PID {pid}")
        kill_tree(pid)

    time.sleep(2)

    for p in find_processes("node.exe", "entry.js gateway"):
        warn(f"killing orphan gateway node PID {p['pid']}")
        kill_tree(p["pid"])

    info(f"waiting up to {PORT_FREE_TIMEOUT_S}s for port {GATEWAY_PORT} to free")
    for i in range(PORT_FREE_TIMEOUT_S):
        if get_port_owner(GATEWAY_PORT) is None:
            ok(f"port free after {i + 1}s")
            return True
        time.sleep(1)
    err(f"port still held after {PORT_FREE_TIMEOUT_S}s -- recovery may fail")
    return False


def unstick_hung_gateway() -> bool:
    """If gateway HTTP fails but port is bound, kill the holding node.
    Supervisor will restart it. Then re-verify HTTP. Returns True if recovered."""
    pid = get_port_owner(GATEWAY_PORT)
    if not pid:
        return False
    warn(f"gateway hung -- killing node PID {pid} so supervisor can restart")
    kill_tree(pid)
    info(f"waiting up to {HUNG_RECOVERY_WAIT_S}s for supervisor to bring it back")
    for i in range(HUNG_RECOVERY_WAIT_S):
        time.sleep(1)
        new_pid = get_port_owner(GATEWAY_PORT)
        if new_pid and new_pid != pid:
            h = gateway_http_health()
            if h["ok"]:
                ok(f"unstuck after {i + 1}s on PID {new_pid} (HTTP {h['status']})")
                return True
    err("unstick failed -- gateway did not return to a healthy HTTP state")
    return False


def bring_up_gateway() -> bool:
    if not trigger_task(GATEWAY_TASK):
        err(f"could not trigger task '{GATEWAY_TASK}'")
        return False
    info(f"task '{GATEWAY_TASK}' triggered, waiting up to {GATEWAY_BIND_TIMEOUT_S}s for port")
    pid = None
    for i in range(GATEWAY_BIND_TIMEOUT_S):
        time.sleep(1)
        pid = get_port_owner(GATEWAY_PORT)
        if pid:
            ok(f"port bound on PID {pid} after {i + 1}s")
            break
    if not pid:
        err(f"gateway did not bind in {GATEWAY_BIND_TIMEOUT_S}s")
        return False

    # Verify HTTP responds
    info(f"verifying HTTP response (timeout {GATEWAY_HTTP_TIMEOUT_S}s)")
    h = gateway_http_health()
    if h["ok"]:
        ok(f"gateway HTTP {h['status']} in {h['time_ms']}ms")
        return True

    err(f"gateway port bound but HTTP unresponsive: {h['error']}")
    return unstick_hung_gateway()


def bring_up_ngrok() -> Tuple[bool, dict]:
    """Returns (ok, public_probe_result)."""
    if not trigger_task(NGROK_TASK):
        err(f"could not trigger task '{NGROK_TASK}'")
        return False, {"ok": False, "status": None, "time_ms": 0,
                       "error": "task not triggered", "body_len": 0}
    info(f"task '{NGROK_TASK}' triggered, waiting up to {NGROK_REGISTER_TIMEOUT_S}s for tunnel")
    tunnel_up = False
    for i in range(NGROK_REGISTER_TIMEOUT_S):
        time.sleep(1)
        t = http_get_json(NGROK_API, timeout=2)
        if t and t.get("tunnels"):
            urls = [x["public_url"] for x in t["tunnels"]]
            ok(f"tunnel registered after {i + 1}s: {urls[0]}")
            if EXPECTED_NGROK_URL not in urls:
                warn(f"  unexpected URL -- expected {EXPECTED_NGROK_URL}")
            tunnel_up = True
            break
    if not tunnel_up:
        err(f"tunnel did not register in {NGROK_REGISTER_TIMEOUT_S}s")
        return False, {"ok": False, "status": None, "time_ms": 0,
                       "error": "tunnel did not register", "body_len": 0}

    # Best-effort public probe
    info(f"probing public URL (timeout {NGROK_PUBLIC_TIMEOUT_S}s)")
    p = public_tunnel_probe()
    if p["ok"]:
        ok(f"public URL verified: {p['status']} in {p['time_ms']}ms")
    else:
        warn(f"public URL probe failed: {p['error']} (may be NAT loopback -- tunnel still registered)")
    return True, p


# =============================================================================
# VERIFY + JSON RESULT
# =============================================================================

def verify() -> Tuple[bool, bool, dict]:
    """Returns (gateway_ok, ngrok_ok, snapshot)."""
    s = snapshot(probe_public=True)
    gw_ok = s["port_pid"] is not None and s["gateway_http"]["ok"]
    ngrok_ok = bool(s["tunnels_local"] and s["tunnels_local"].get("tunnels"))

    if s["port_pid"] and s["gateway_http"]["ok"]:
        ok(f"gateway: port {GATEWAY_PORT} listening + HTTP {s['gateway_http']['status']}")
    elif s["port_pid"]:
        err(f"gateway: port bound but HTTP failed -- HUNG")
    else:
        err(f"gateway: port {GATEWAY_PORT} NOT listening")

    if ngrok_ok:
        urls = [x["public_url"] for x in s["tunnels_local"]["tunnels"]]
        ok(f"ngrok: tunnel(s) {', '.join(urls)}")
        p = s["public_probe"]
        if p and p["ok"]:
            ok(f"ngrok: public URL verified ({p['status']})")
        elif p:
            warn(f"ngrok: public URL not verified ({p['error']}) -- NAT loopback or genuine outage")
    else:
        err("ngrok: no active tunnels")

    sup_n = len(s["gateway_supervisors"])
    if sup_n == 1:
        ok("supervisors: 1 (clean)")
    elif sup_n == 0 and gw_ok:
        warn("supervisors: 0 (gateway unsupervised -- won't auto-restart on crash)")
    elif sup_n == 0:
        info("supervisors: 0")
    else:
        warn(f"supervisors: {sup_n} -- duplicate, will collide")

    return gw_ok, ngrok_ok, s


def build_json_result(snap: dict, gw_ok: bool, ngrok_ok: bool,
                      action_taken: str, backup_path: Optional[str]) -> dict:
    tunnels_local = snap.get("tunnels_local") or {}
    tunnel_urls = [t.get("public_url") for t in tunnels_local.get("tunnels", [])]
    public = snap.get("public_probe") or {}
    public_ok = public.get("ok") if public else None

    # Heuristic: if we're running on the same machine as ngrok (the local 4040
    # API is reachable), public-probe failures are typically NAT loopback /
    # TLS hairpin issues, NOT genuine outages. Don't downgrade status for them.
    on_host = bool(tunnels_local and tunnels_local.get("tunnels"))
    public_failure_is_loopback = (
        public is not None and not public_ok and on_host
    )

    if gw_ok and ngrok_ok:
        if public_ok or public_failure_is_loopback or public is None:
            status = "healthy"
        else:
            status = "degraded"  # off-host probe failed -> genuine concern
    elif gw_ok or ngrok_ok:
        status = "degraded"
    else:
        status = "down"

    return {
        "status": status,
        "gateway": {
            # fleet-recovery skill schema (documented contract):
            "port":           snap["port_pid"] is not None,
            "http":           snap["gateway_http"]["ok"],
            "pid":            snap["port_pid"],
            # extended fields:
            "port_listening": snap["port_pid"] is not None,
            "http_ok":        snap["gateway_http"]["ok"],
            "http_status":    snap["gateway_http"]["status"],
            "http_time_ms":   snap["gateway_http"]["time_ms"],
            "supervisors":    len(snap["gateway_supervisors"]),
        },
        "ngrok": {
            # fleet-recovery skill schema (documented contract):
            "process":     len(snap["ngroks"]) > 0,
            "tunnel":      ngrok_ok,
            "url":         tunnel_urls[0] if tunnel_urls else None,
            "url_changed": (
                tunnel_urls[0] != EXPECTED_NGROK_URL
                if tunnel_urls else False
            ),
            # extended fields:
            "process_count":     len(snap["ngroks"]),
            "tunnel_registered": ngrok_ok,
            "urls":              tunnel_urls,
            "expected_url":      EXPECTED_NGROK_URL,
            "url_matches":       EXPECTED_NGROK_URL in tunnel_urls,
            "public_probe_ok":   public_ok,
            "public_status":     public.get("status") if public else None,
            "public_error":      public.get("error") if public else None,
            "public_skip_reason": "loopback" if public_failure_is_loopback else None,
        },
        "action_taken":  action_taken,
        "backup_path":   backup_path,
        "host":          socket.gethostname(),
        "timestamp":     datetime.now().astimezone().isoformat(timespec="seconds"),
    }


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    global VERBOSE, JSON_MODE

    p = argparse.ArgumentParser(
        description="Recover Aristotle gateway and ngrok tunnel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--check", action="store_true",
                   help="Diagnose only, make no changes")
    p.add_argument("--soft", action="store_true",
                   help="Only restart pieces that are broken (preserve healthy ones)")
    p.add_argument("--json", action="store_true",
                   help="Emit a single JSON object on stdout (suppresses human output)")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Verbose output")
    args = p.parse_args()

    VERBOSE   = args.verbose
    JSON_MODE = args.json

    _out(f"{C.BOLD}Aristotle Recovery (v2) -- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.END}")

    # ---------- diagnose ----------
    header("diagnose")
    s = snapshot(probe_public=True)
    print_state(s)

    if args.check:
        gw_ok    = s["port_pid"] is not None and s["gateway_http"]["ok"]
        ngrok_ok = bool(s["tunnels_local"] and s["tunnels_local"].get("tunnels"))
        if not (gw_ok and ngrok_ok):
            dump_log_tail("task-gateway", TASK_GATEWAY_LOG, n=15)
            dump_log_tail("clawdbot today", todays_clawdbot_log(), n=15)
        rc = 0 if (gw_ok and ngrok_ok and len(s["gateway_supervisors"]) <= 1) else 10
        _out("")
        if rc == 0:
            ok("CHECK: all green")
        else:
            warn("CHECK: at least one component down or duplicate supervisors")
        if JSON_MODE:
            result = build_json_result(s, gw_ok, ngrok_ok, "check", None)
            print(json.dumps(result, indent=2))
        return rc

    # ---------- decide path ----------
    gw_alive    = s["port_pid"] is not None and s["gateway_http"]["ok"]
    ngrok_alive = bool(s["tunnels_local"] and s["tunnels_local"].get("tunnels"))
    dup_sup     = len(s["gateway_supervisors"]) > 1
    action_taken = "none"
    final_snap = s

    if args.soft and gw_alive and ngrok_alive and not dup_sup:
        _out("")
        ok("--soft: everything healthy, no action needed")
        backup_path = backup_config()
        if backup_path:
            ok(f"config backup: {backup_path}")
        gw_ok, ngrok_ok = True, True
    elif args.soft and not dup_sup:
        # Surgical: handle gateway and ngrok independently
        action_taken = "soft_restart"
        gw_ok = gw_alive
        ngrok_ok = ngrok_alive

        # Hung gateway? (port bound, HTTP failed)
        if s["port_pid"] and not s["gateway_http"]["ok"]:
            header("gateway hung -- unsticking")
            gw_ok = unstick_hung_gateway()

        # Gateway entirely down?
        if not gw_ok and not s["port_pid"]:
            header("gateway is down -- restarting")
            teardown()
            gw_ok = bring_up_gateway()

        # Ngrok down?
        if not ngrok_ok:
            header("ngrok is down -- restarting")
            for ng in s["ngroks"]:
                kill_tree(ng["pid"])
            for nw in s["ngrok_supervisors"]:
                kill_tree(nw["pid"])
            ngrok_ok, _ = bring_up_ngrok()

        header("verify")
        gw_ok, ngrok_ok, final_snap = verify()
        if gw_ok and ngrok_ok:
            backup_path = backup_config()
            if backup_path:
                ok(f"config backup: {backup_path}")
        else:
            backup_path = None
    else:
        # Full hammer
        action_taken = "full_recovery"
        header("teardown")
        teardown()
        header("bring up gateway")
        gw_ok = bring_up_gateway()
        header("bring up ngrok")
        ngrok_ok, _ = bring_up_ngrok()
        header("verify")
        gw_ok, ngrok_ok, final_snap = verify()
        if gw_ok and ngrok_ok:
            backup_path = backup_config()
            if backup_path:
                ok(f"config backup: {backup_path}")
        else:
            backup_path = None

    # ---------- finale ----------
    _out("")
    if gw_ok and ngrok_ok:
        _out(f"{C.GREEN}{C.BOLD}RECOVERY COMPLETE{C.END}")
        rc = 0
    elif gw_ok and not ngrok_ok:
        _out(f"{C.YELLOW}{C.BOLD}PARTIAL: gateway up, ngrok down{C.END}")
        rc = 2
    elif not gw_ok and ngrok_ok:
        _out(f"{C.YELLOW}{C.BOLD}PARTIAL: ngrok up, gateway down{C.END}")
        rc = 3
    else:
        _out(f"{C.RED}{C.BOLD}RECOVERY FAILED{C.END}")
        rc = 1

    # Tail relevant logs on any failure
    if rc != 0:
        if not gw_ok:
            dump_log_tail("task-gateway", TASK_GATEWAY_LOG, n=20)
            dump_log_tail("clawdbot today", todays_clawdbot_log(), n=20)
        if not ngrok_ok:
            dump_log_tail("task-ngrok", TASK_NGROK_LOG, n=20)

    # JSON result
    if JSON_MODE:
        try:
            backup_path
        except NameError:
            backup_path = None
        result = build_json_result(final_snap, gw_ok, ngrok_ok, action_taken, backup_path)
        print(json.dumps(result, indent=2))

    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _out("")
        warn("interrupted")
        sys.exit(130)
