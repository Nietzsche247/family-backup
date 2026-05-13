#!/usr/bin/env python3
"""
aristotle_recover_v2.py
=======================
Full recovery for Aristotle clawdbot gateway + ngrok tunnel on
Omni-AlienWare2025 with enhanced health probes, E2E verification,
structured output, config backup, log tailing and notifications.

**New in v2 (per Aristotle spec):**
- HTTP health probe on /api/status after port is LISTENING
- End-to-end tunnel verification via public ngrok URL
- Config backup on successful recovery
- --json structured output
- Log tailing on failure
- Notification to Comms Hub on successful recovery (non-blocking)

Preserves ALL original functionality, flags, logic and exit codes.

Stdlib only. Python 3.12+ on Windows.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# =============================================================================
# CONFIG
# =============================================================================

GATEWAY_PORT = 18792
GATEWAY_HTTP_URL = "http://127.0.0.1:18792/api/status"
NGROK_API = "http://127.0.0.1:4040/api/tunnels"
NGROK_PUBLIC_URL = "https://uneffective-unprepossessingly-september.ngrok-free.dev/api/status"
EXPECTED_NGROK_URL = "https://uneffective-unprepossessingly-september.ngrok-free.dev"
GATEWAY_TASK = "Aristotle Gateway"
NGROK_TASK = "Aristotle Ngrok"

# Timeouts
GATEWAY_BIND_TIMEOUT_S = 120
NGROK_REGISTER_TIMEOUT_S = 30
PORT_FREE_TIMEOUT_S = 15
HTTP_PROBE_TIMEOUT_S = 10

# Paths
GATEWAY_CONFIG_PATH = r"C:\Users\aaron\.clawdbot-aristotle\clawdbot.json"
BACKUP_DIR = r"C:\Users\aaron\clawd-shared\backups"
GATEWAY_LOG = r"C:\tmp\clawdbot-aristotle\task-gateway.log"
CLAWDBOT_LOG_BASE = r"C:\tmp\clawdbot\clawdbot"

# Comms Hub
COMMS_HUB_URL = "http://127.0.0.1:3001/api/bridge/message"

# =============================================================================
# OUTPUT
# =============================================================================

class C:
    """ANSI colors. Disabled if stdout isn't a terminal."""
    if sys.stdout.isatty():
        RED, GREEN, YELLOW, CYAN, BOLD, END = (
            "\033[91m", "\033[92m", "\033[93m", "\033[96m", "\033[1m", "\033[0m"
        )
    else:
        RED = GREEN = YELLOW = CYAN = BOLD = END = ""

VERBOSE = False
JSON_OUTPUT = False


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def info(msg: str) -> None:
    if not JSON_OUTPUT:
        print(f"{C.CYAN}{_ts()}   {msg}{C.END}")


def ok(msg: str) -> None:
    if not JSON_OUTPUT:
        print(f"{C.GREEN}{_ts()} + {msg}{C.END}")


def warn(msg: str) -> None:
    if not JSON_OUTPUT:
        print(f"{C.YELLOW}{_ts()} ! {msg}{C.END}")


def err(msg: str) -> None:
    if not JSON_OUTPUT:
        print(f"{C.RED}{_ts()} x {msg}{C.END}")


def header(msg: str) -> None:
    if not JSON_OUTPUT:
        print(f"\n{C.BOLD}=== {msg} ==={C.END}")


def vinfo(msg: str) -> None:
    if VERBOSE and not JSON_OUTPUT:
        info(msg)


# =============================================================================
# HELPERS — process inspection
# =============================================================================

def run_ps(script: str, timeout: int = 30) -> Tuple[int, str, str]:
    """Run a PowerShell script. Returns (rc, stdout, stderr)."""
    try:
        r = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True, text=True, timeout=timeout
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", "powershell timeout"
    except FileNotFoundError:
        return 127, "", "powershell.exe not found on PATH"


def find_processes(name: str, cmd_substr: str) -> List[dict]:
    """Find processes where Name == `name` and CommandLine LIKE *cmd_substr*."""
    ps = (
        f"Get-CimInstance Win32_Process -Filter \"Name='{name}'\" | "
        f"Where-Object {{ $_.CommandLine -like '*{cmd_substr}*' }} | "
        f"Select-Object ProcessId, ParentProcessId, CommandLine | "
        f"ConvertTo-Json -Compress -Depth 3"
    )
    rc, out, _ = run_ps(ps)
    if not out or rc != 0:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        vinfo(f"failed to parse process JSON: {out[:200]}")
        return []
    if isinstance(data, dict):
        data = [data]
    results = []
    for d in data:
        results.append({
            "pid": int(d.get("ProcessId", 0)),
            "ppid": int(d.get("ParentProcessId", 0)),
            "cmd": (d.get("CommandLine") or "").strip(),
        })
    return results


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


def kill_tree(pid: int) -> bool:
    """taskkill /T /F /PID <pid>. Returns True if successful or already gone."""
    try:
        r = subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(pid)],
            capture_output=True, text=True, timeout=15
        )
        return r.returncode in (0, 128)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def trigger_task(task_name: str) -> bool:
    """schtasks /run /TN <name>. Returns True on success."""
    try:
        r = subprocess.run(
            ["schtasks", "/run", "/TN", task_name],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode != 0:
            warn(f"schtasks /run failed: {r.stderr or r.stdout}")
        return r.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        err(f"schtasks invocation failed: {e}")
        return False


# =============================================================================
# HELPERS — HTTP probes (new in v2)
# =============================================================================

def http_get_json(url: str, timeout: int = 5) -> Optional[dict]:
    """GET JSON with timeout."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "aristotle-recover/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", errors="replace")
            return json.loads(body)
    except (urllib.error.URLError, json.JSONDecodeError, OSError, TimeoutError, ValueError) as e:
        vinfo(f"HTTP GET {url} failed: {type(e).__name__} - {e}")
        return None


def http_status(url: str, timeout: int = 5) -> Optional[int]:
    """GET status code."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "aristotle-recover/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        vinfo(f"HTTP status {url} failed: {type(e).__name__}")
        return None


def probe_gateway_http() -> bool:
    """Probe gateway HTTP endpoint. Returns True if healthy."""
    status = http_status(GATEWAY_HTTP_URL, timeout=HTTP_PROBE_TIMEOUT_S)
    if status == 200:
        vinfo("gateway HTTP /api/status returned 200")
        return True
    vinfo(f"gateway HTTP probe failed (status={status})")
    return False


def probe_ngrok_tunnel() -> bool:
    """E2E probe through public tunnel. Returns True if healthy."""
    status = http_status(NGROK_PUBLIC_URL, timeout=HTTP_PROBE_TIMEOUT_S)
    if status == 200:
        vinfo("E2E tunnel probe successful")
        return True
    vinfo(f"E2E tunnel probe failed (status={status})")
    return False


# =============================================================================
# LOG TAILING (new in v2)
# =============================================================================

def tail_file(path: str, lines: int = 20) -> str:
    """Return last N lines of a file or note if missing."""
    if not os.path.exists(path):
        return f"[file not found: {path}]"
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return "".join(f.readlines()[-lines:])
    except Exception as e:
        return f"[error reading {path}: {e}]"


def print_diagnostic_logs() -> None:
    """Print last 20 lines of key logs on failure."""
    if JSON_OUTPUT:
        return
    header("RECENT LOGS (last 20 lines)")
    today = datetime.now().strftime("%Y-%m-%d")
    clawdbot_log = f"{CLAWDBOT_LOG_BASE}-{today}.log"
    print("=== task-gateway.log ===")
    print(tail_file(GATEWAY_LOG))
    print(f"\n=== {os.path.basename(clawdbot_log)} ===")
    print(tail_file(clawdbot_log))


# =============================================================================
# CONFIG BACKUP (new in v2)
# =============================================================================

def backup_config() -> bool:
    """Backup clawdbot.json with date. Returns True if done."""
    if not os.path.exists(GATEWAY_CONFIG_PATH):
        vinfo("config file not found, skipping backup")
        return False
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        backup_path = os.path.join(BACKUP_DIR, f"clawdbot-aristotle-{today}.json")
        shutil.copy2(GATEWAY_CONFIG_PATH, backup_path)
        ok(f"config backed up to {backup_path}")
        return True
    except Exception as e:
        warn(f"config backup failed: {e}")
        return False


# =============================================================================
# NOTIFICATION (new in v2)
# =============================================================================

def notify_recovery(details: str) -> None:
    """POST to Comms Hub (non-blocking)."""
    try:
        payload = {
            "to": "aristotle",
            "from": "recovery-script",
            "body": f"Auto-recovery completed: {details}"
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            COMMS_HUB_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5):
            vinfo("notification sent to Comms Hub")
    except Exception as e:
        vinfo(f"notification failed (non-blocking): {type(e).__name__}")


# =============================================================================
# STRUCTURED OUTPUT (new in v2)
# =============================================================================

def build_json_result(
    status: str,
    gateway: Dict[str, Any],
    ngrok: Dict[str, Any],
    action_taken: str,
    details: str = ""
) -> Dict[str, Any]:
    return {
        "status": status,
        "gateway": gateway,
        "ngrok": ngrok,
        "action_taken": action_taken,
        "timestamp": datetime.now().astimezone().isoformat(),
        "details": details
    }


def print_json(result: Dict[str, Any]) -> None:
    print(json.dumps(result, indent=2))


# =============================================================================
# DIAGNOSE + ENHANCED HEALTH (updated)
# =============================================================================

def snapshot() -> dict:
    """Capture full current state."""
    gw_super_a = find_processes("cmd.exe", "aristotle-gateway-task")
    gw_super_b = find_processes("cmd.exe", "gateway-resilient")
    seen = set()
    gateway_supervisors = []
    for sp in gw_super_a + gw_super_b:
        if sp["pid"] not in seen:
            seen.add(sp["pid"])
            gateway_supervisors.append(sp)

    port_pid = get_port_owner(GATEWAY_PORT)
    tunnels = http_get_json(NGROK_API, timeout=3)

    return {
        "port_pid": port_pid,
        "gateway_supervisors": gateway_supervisors,
        "ngrok_supervisors": find_processes("cmd.exe", "aristotle-ngrok-task"),
        "gw_nodes": find_processes("node.exe", "entry.js gateway"),
        "ngroks": find_processes("ngrok.exe", "ngrok"),
        "tunnels": tunnels,
    }


def print_state(s: dict) -> None:
    if JSON_OUTPUT:
        return
    if s["port_pid"]:
        ok(f"port {GATEWAY_PORT}: LISTENING (PID {s['port_pid']})")
    else:
        warn(f"port {GATEWAY_PORT}: not listening")

    sup_n = len(s["gateway_supervisors"])
    if sup_n == 1:
        ok("gateway supervisors: 1")
    elif sup_n == 0 and s["port_pid"]:
        warn("gateway supervisors: 0 (gateway running unsupervised)")
    elif sup_n == 0:
        warn("gateway supervisors: 0")
    else:
        warn(f"gateway supervisors: {sup_n} (DUPLICATE -- they will collide)")
    for sp in s["gateway_supervisors"]:
        vinfo(f"  pid={sp['pid']} ppid={sp['ppid']}")

    info(f"ngrok supervisors: {len(s['ngrok_supervisors'])}")
    info(f"gateway node procs: {len(s['gw_nodes'])}")
    info(f"ngrok processes: {len(s['ngroks'])}")

    t = s["tunnels"]
    if t and t.get("tunnels"):
        urls = [x.get("public_url", "") for x in t["tunnels"]]
        ok(f"tunnels active: {urls}")
        if EXPECTED_NGROK_URL not in "".join(urls):
            warn(f"  expected URL {EXPECTED_NGROK_URL} NOT in tunnel list")
    else:
        warn("no active tunnels")


def enhanced_verify() -> Tuple[bool, bool, Dict[str, Any], Dict[str, Any]]:
    """Return (gw_healthy, ngrok_healthy, gw_dict, ngrok_dict) with full probes."""
    s = snapshot()
    port_pid = s["port_pid"]
    port_ok = port_pid is not None

    # Gateway HTTP probe (HIGH PRIORITY)
    http_ok = False
    if port_ok:
        http_ok = probe_gateway_http()
        if not http_ok:
            # Kill the bad PID to let supervisor restart
            warn("Port listening but HTTP /api/status failed - killing node PID")
            if port_pid:
                kill_tree(port_pid)
            time.sleep(3)

    gw_healthy = port_ok and http_ok
    gw_dict = {
        "port": port_ok,
        "http": http_ok,
        "pid": port_pid or 0
    }

    # Ngrok + E2E tunnel (HIGH PRIORITY)
    tunnels = s.get("tunnels")
    ngrok_process_ok = bool(tunnels and tunnels.get("tunnels"))
    tunnel_ok = False
    ngrok_url = EXPECTED_NGROK_URL
    if ngrok_process_ok:
        urls = [x.get("public_url", "") for x in tunnels.get("tunnels", [])]
        if EXPECTED_NGROK_URL in "".join(urls):
            tunnel_ok = probe_ngrok_tunnel()

    ngrok_healthy = ngrok_process_ok and tunnel_ok
    ngrok_dict = {
        "process": ngrok_process_ok,
        "tunnel": tunnel_ok,
        "url": ngrok_url
    }

    if not JSON_OUTPUT:
        if gw_healthy:
            ok(f"gateway: healthy (port + HTTP, PID {port_pid})")
        else:
            if port_ok and not http_ok:
                err("gateway: port up but HTTP probe FAILED")
            elif port_ok:
                ok(f"gateway: port up (PID {port_pid})")
            else:
                err("gateway: port NOT listening")

        if ngrok_healthy:
            ok(f"ngrok: healthy (process + E2E tunnel)")
        else:
            if ngrok_process_ok and not tunnel_ok:
                err("ngrok: process up but E2E tunnel probe FAILED")
            elif ngrok_process_ok:
                ok("ngrok: process up")
            else:
                err("ngrok: no active tunnels")

    return gw_healthy, ngrok_healthy, gw_dict, ngrok_dict


# =============================================================================
# TEARDOWN / BRING UP (preserved + minor updates)
# =============================================================================

def teardown(s: dict) -> bool:
    """Kill everything gateway/ngrok related."""

    # L30/L31: Disable scheduled tasks FIRST to stop the 5-minute periodic
    # trigger from respawning the broken state during teardown. Without this,
    # processes we kill will keep coming back with new PIDs as the supervisor
    # respawns. We re-enable in bring_up_gateway() after the gateway is healthy.
    info(f"disabling scheduled task '{GATEWAY_TASK}' to prevent auto-respawn")
    try:
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command",
             f"Disable-ScheduledTask -TaskName '{GATEWAY_TASK}' | Out-Null"],
            capture_output=True, timeout=10, check=False,
        )
    except Exception as e:
        warn(f"Disable-ScheduledTask failed (continuing anyway): {e}")

    s = snapshot()  # fresh

    for p in s["ngroks"]:
        info(f"killing ngrok PID {p['pid']}")
        kill_tree(p["pid"])

    pids = {p["pid"] for p in s["gateway_supervisors"]} | {p["pid"] for p in s["ngrok_supervisors"]}
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
    err(f"port still held after {PORT_FREE_TIMEOUT_S}s")
    return False


def bring_up_gateway() -> bool:
    # L30/L31: Re-enable the scheduled task we disabled during teardown.
    # If we don't, the supervisor + periodic trigger auto-recovery is lost
    # after this script runs.
    info(f"re-enabling scheduled task '{GATEWAY_TASK}'")
    try:
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command",
             f"Enable-ScheduledTask -TaskName '{GATEWAY_TASK}' | Out-Null"],
            capture_output=True, timeout=10, check=False,
        )
    except Exception as e:
        warn(f"Enable-ScheduledTask failed (continuing): {e}")

    if not trigger_task(GATEWAY_TASK):
        err(f"could not trigger task '{GATEWAY_TASK}'")
        return False
    info(f"task '{GATEWAY_TASK}' triggered, waiting up to {GATEWAY_BIND_TIMEOUT_S}s for port + HTTP")
    for i in range(GATEWAY_BIND_TIMEOUT_S):
        time.sleep(1)
        pid = get_port_owner(GATEWAY_PORT)
        if pid:
            # Additional wait for HTTP readiness
            for _ in range(10):  # up to 10s extra
                if probe_gateway_http():
                    ok(f"gateway healthy (port+HTTP) on PID {pid} after {i+1}s")
                    return True
                time.sleep(1)
            ok(f"gateway listening on PID {pid} (HTTP still settling)")
            return True

    # L31 FALLBACK: task path failed (wrapper may be hanging in its own kill
    # loop — we saw this 2026-05-11). Bypass the wrapper and launch gateway.cmd
    # directly. The scheduled task is a convenience layer; gateway.cmd is the
    # actual launch mechanism.
    warn(f"task path did not bind in {GATEWAY_BIND_TIMEOUT_S}s — falling back to direct gateway.cmd launch")
    gateway_cmd = r"C:\Users\Aaron\.clawdbot-aristotle\gateway.cmd"
    try:
        subprocess.Popen(
            ["cmd.exe", "/c", "start", "/MIN", "Aristotle Gateway (direct)", gateway_cmd],
            cwd=r"C:\Users\Aaron\.clawdbot-aristotle",
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )
    except Exception as e:
        err(f"direct gateway.cmd launch failed: {e}")
        return False

    info(f"direct gateway.cmd launched, waiting up to {GATEWAY_BIND_TIMEOUT_S}s for port + HTTP")
    for i in range(GATEWAY_BIND_TIMEOUT_S):
        time.sleep(1)
        pid = get_port_owner(GATEWAY_PORT)
        if pid:
            for _ in range(10):
                if probe_gateway_http():
                    ok(f"gateway healthy via direct launch on PID {pid} after {i+1}s")
                    return True
                time.sleep(1)
            ok(f"gateway listening (direct) on PID {pid} (HTTP still settling)")
            return True

    err(f"gateway did not bind in time (both task and direct paths failed)")
    return False


def bring_up_ngrok() -> bool:
    if not trigger_task(NGROK_TASK):
        err(f"could not trigger task '{NGROK_TASK}'")
        return False
    info(f"task '{NGROK_TASK}' triggered, waiting up to {NGROK_REGISTER_TIMEOUT_S}s")
    for i in range(NGROK_REGISTER_TIMEOUT_S):
        time.sleep(1)
        t = http_get_json(NGROK_API, timeout=2)
        if t and t.get("tunnels"):
            urls = [x.get("public_url", "") for x in t["tunnels"]]
            if EXPECTED_NGROK_URL in "".join(urls):
                # E2E check
                if probe_ngrok_tunnel():
                    ok(f"E2E tunnel verified after {i + 1}s")
                    return True
                else:
                    warn("ngrok registered but E2E probe failing")
            else:
                ok(f"tunnel up after {i + 1}s: {urls[0] if urls else ''} (E2E pending)")
            return True
    err(f"tunnel did not register in time")
    return False


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    global VERBOSE, JSON_OUTPUT

    p = argparse.ArgumentParser(
        description="Recover Aristotle gateway + ngrok with enhanced health checks (v2).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--check", action="store_true", help="Diagnose only, make no changes")
    p.add_argument("--soft", action="store_true", help="Only restart broken pieces")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    p.add_argument("--json", action="store_true", help="Output structured JSON (for scripts)")
    args = p.parse_args()

    VERBOSE = args.verbose
    JSON_OUTPUT = args.json

    if not JSON_OUTPUT:
        print(f"{C.BOLD}Aristotle Recovery v2 -- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.END}")

    header("diagnose")
    s = snapshot()
    print_state(s)

    gw_dict = {"port": bool(s["port_pid"]), "http": False, "pid": s.get("port_pid") or 0}
    ngrok_dict = {"process": bool(s.get("tunnels") and s["tunnels"].get("tunnels")), "tunnel": False, "url": EXPECTED_NGROK_URL}
    action_taken = "none"

    # Enhanced check for --check or initial state
    if args.check or (s["port_pid"] and not probe_gateway_http()) or (ngrok_dict["process"] and not probe_ngrok_tunnel()):
        gw_healthy, ngrok_healthy, gw_dict, ngrok_dict = enhanced_verify()
    else:
        gw_healthy = bool(s["port_pid"])
        ngrok_healthy = ngrok_dict["process"]

    status = "healthy" if gw_healthy and ngrok_healthy else "degraded" if gw_healthy or ngrok_healthy else "down"

    if args.check:
        if JSON_OUTPUT:
            result = build_json_result(status, gw_dict, ngrok_dict, "none", "check mode")
            print_json(result)
        else:
            print()
            if gw_healthy and ngrok_healthy:
                ok("CHECK: all green")
                return 0
            else:
                warn("CHECK: at least one component degraded")
                print_diagnostic_logs()
                return 10
        return 0 if gw_healthy and ngrok_healthy else 10

    gw_alive = bool(s["port_pid"])
    ngrok_alive = bool(s.get("tunnels") and s["tunnels"].get("tunnels"))
    dup_sup = len(s["gateway_supervisors"]) > 1

    if args.soft and gw_alive and ngrok_alive and not dup_sup:
        if JSON_OUTPUT:
            result = build_json_result("healthy", gw_dict, ngrok_dict, "none")
            print_json(result)
        else:
            print()
            ok("--soft: everything healthy, no action needed")
        return 0

    # Perform recovery if needed
    if args.soft and not dup_sup:
        if not gw_alive or not probe_gateway_http():
            header("gateway unhealthy -- restarting")
            teardown(s)
            gw_final = bring_up_gateway()
            action_taken = "soft_restart"
        else:
            gw_final = True
        if not ngrok_alive or not probe_ngrok_tunnel():
            header("ngrok unhealthy -- restarting")
            for ng in s["ngroks"]:
                kill_tree(ng["pid"])
            ngrok_final = bring_up_ngrok()
            action_taken = "soft_restart" if action_taken == "none" else "full_recovery"
        else:
            ngrok_final = True
    else:
        header("teardown")
        teardown(s)
        header("bring up gateway")
        gw_final = bring_up_gateway()
        header("bring up ngrok")
        ngrok_final = bring_up_ngrok()
        action_taken = "full_recovery"

    # Final verification with all probes
    header("verify")
    final_gw_ok, final_ngrok_ok, final_gw_dict, final_ngrok_dict = enhanced_verify()
    final_status = "healthy" if final_gw_ok and final_ngrok_ok else "degraded" if final_gw_ok or final_ngrok_ok else "down"

    success = final_gw_ok and final_ngrok_ok

    if success:
        backup_config()
        if not args.check:
            notify_recovery("gateway and ngrok fully recovered with E2E verification")
        if not JSON_OUTPUT:
            print()
            print(f"{C.GREEN}{C.BOLD}RECOVERY COMPLETE{C.END}")
        result = build_json_result("healthy", final_gw_dict, final_ngrok_dict, action_taken, "full recovery with HTTP+E2E verification")
    else:
        if not JSON_OUTPUT:
            print_diagnostic_logs()
            print()
            if final_gw_ok:
                print(f"{C.YELLOW}{C.BOLD}PARTIAL: gateway up, ngrok down{C.END}")
            elif final_ngrok_ok:
                print(f"{C.YELLOW}{C.BOLD}PARTIAL: ngrok up, gateway down{C.END}")
            else:
                print(f"{C.RED}{C.BOLD}RECOVERY FAILED{C.END}")
        details = "recovery failed" if not final_gw_ok and not final_ngrok_ok else "partial recovery"
        result = build_json_result(final_status, final_gw_dict, final_ngrok_dict, action_taken, details)

    if JSON_OUTPUT:
        print_json(result)

    if success:
        return 0
    elif final_gw_ok and not final_ngrok_ok:
        return 2
    elif final_ngrok_ok and not final_gw_ok:
        return 3
    else:
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        if not JSON_OUTPUT:
            print()
            warn("interrupted")
        sys.exit(130)
    except Exception as e:
        if JSON_OUTPUT:
            print(json.dumps({
                "status": "down",
                "error": str(e),
                "timestamp": datetime.now().astimezone().isoformat()
            }, indent=2))
        else:
            err(f"unexpected error: {e}")
            import traceback
            traceback.print_exc()
        sys.exit(1)
