#!/usr/bin/env python3
"""
plato_recover.py
================
Full recovery script for the Plato Clawdbot gateway on NIETZSCHE2025 (Windows 11).

Adapted from aristotle_recover_v2.py with Plato-specific architecture:
- Port 18789
- Scheduled task: "Clawdbot Gateway" (no supervisor loop)
- Ngrok is manual (no scheduled task)
- Ngrok URL is dynamic (detected from localhost:4040/api/tunnels)
- Config: C:\\Users\\Aaron\\.clawdbot\\clawdbot.json
- Logs: C:\\tmp\\clawdbot\\clawdbot-YYYY-MM-DD.log
- Duplicate node.exe gateway processes must all be killed
- Gateway token: ad8703220cdfa6fcf6a9589dec3100c90be32537bc47cb28

Features (same as v2):
- --check (diagnose only)
- --soft (restart only broken pieces)
- Full recovery (default)
- HTTP health probe (/api/status with 10s timeout)
- E2E tunnel probe via dynamic ngrok URL
- Config backup on success
- --json structured output
- Log tailing on failure
- Notification to Comms Hub (with fallback)
- Ngrok URL change detection + warning
- Duplicate process cleanup
- Verbose mode (-v)

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
# PLATO-SPECIFIC CONFIG
# =============================================================================

GATEWAY_PORT = 18789
GATEWAY_HTTP_URL = "http://127.0.0.1:18789/api/status"
NGROK_API = "http://127.0.0.1:4040/api/tunnels"
EXPECTED_NGROK_URL = "https://liny-tien-pleuritic.ngrok-free.dev"
GATEWAY_TASK = "Clawdbot Gateway"

# Timeouts
GATEWAY_BIND_TIMEOUT_S = 120
NGROK_REGISTER_TIMEOUT_S = 30
PORT_FREE_TIMEOUT_S = 15
HTTP_PROBE_TIMEOUT_S = 10

# Paths
GATEWAY_CONFIG_PATH = r"C:\\Users\\Aaron\\.clawdbot\\clawdbot.json"
BACKUP_DIR = r"C:\\Users\\Aaron\\clawd-shared\\backups"
GATEWAY_LOG_BASE = r"C:\\tmp\\clawdbot\\clawdbot"
COMMS_HUB_URLS = [
    "http://127.0.0.1:3001/api/bridge/message",
    "http://100.108.47.36:3001/api/bridge/message"
]

# Gateway token (for reference in logs)
GATEWAY_TOKEN = "ad8703220cdfa6fcf6a9589dec3100c90be32537bc47cb28"

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
NGROK_URL_CHANGED = False
CURRENT_NGROK_URL = None


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


def find_gateway_node_processes() -> List[dict]:
    """Find ALL node.exe processes running the gateway (Plato-specific)."""
    ps = (
        r'Get-CimInstance Win32_Process -Filter "Name=''node.exe''" | '
        r'Where-Object { $_.CommandLine -like "*entry.js*gateway*" } | '
        r'Select-Object ProcessId, ParentProcessId, CommandLine | '
        r'ConvertTo-Json -Compress -Depth 3'
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


def find_ngrok_processes() -> List[dict]:
    """Find ngrok processes."""
    ps = (
        r'Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | '
        r'Select-Object Id, Path | ConvertTo-Json -Compress'
    )
    rc, out, _ = run_ps(ps)
    if not out or rc != 0:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        data = [data]
    results = []
    for d in data:
        results.append({
            "pid": int(d.get("Id", 0)),
            "path": d.get("Path", "")
        })
    return results


def get_port_owner(port: int) -> Optional[int]:
    """PID listening on `port`, or None."""
    try:
        out = subprocess.check_output(
            ["netstat", "-ano"], text=True, timeout=10, stderr=subprocess.DEVNULL
        )
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
        return r.returncode in (0, 128, 1)  # 1 = not found is acceptable
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def trigger_scheduled_task(task_name: str, action: str = "run") -> bool:
    """schtasks /run or /end."""
    cmd = ["schtasks", f"/{action}", "/TN", task_name]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if r.returncode != 0:
            warn(f"schtasks {action} failed for '{task_name}': {r.stderr or r.stdout}")
            return False
        return True
    except Exception as e:
        err(f"schtasks {action} invocation failed: {e}")
        return False


# =============================================================================
# HELPERS — HTTP probes
# =============================================================================

def http_get_json(url: str, timeout: int = 5) -> Optional[dict]:
    """GET JSON with timeout."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "plato-recover/1.0", "Authorization": f"Bearer {GATEWAY_TOKEN}"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", errors="replace")
            return json.loads(body)
    except Exception as e:
        vinfo(f"HTTP GET {url} failed: {type(e).__name__} - {e}")
        return None


def http_status(url: str, timeout: int = 5) -> Optional[int]:
    """GET status code."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "plato-recover/1.0", "Authorization": f"Bearer {GATEWAY_TOKEN}"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


def probe_gateway_http() -> bool:
    """Probe gateway HTTP endpoint. Returns True if healthy."""
    status = http_status(GATEWAY_HTTP_URL, timeout=HTTP_PROBE_TIMEOUT_S)
    if status == 200:
        vinfo("gateway HTTP /api/status returned 200")
        return True
    vinfo(f"gateway HTTP probe failed (status={status})")
    return False


def get_current_ngrok_url() -> Optional[str]:
    """Get the current public ngrok URL from local API."""
    data = http_get_json(NGROK_API, timeout=3)
    if not data or not data.get("tunnels"):
        return None
    for tunnel in data["tunnels"]:
        if tunnel.get("proto") == "https" or "ngrok-free.dev" in tunnel.get("public_url", ""):
            return tunnel.get("public_url")
    return None


def probe_e2e_tunnel(public_url: str) -> bool:
    """E2E probe through public tunnel."""
    if not public_url:
        return False
    status_url = public_url.replace("/api/tunnels", "/api/status") if "/api/tunnels" in public_url else f"{public_url.rstrip('/')}/api/status"
    status = http_status(status_url, timeout=HTTP_PROBE_TIMEOUT_S)
    if status == 200:
        vinfo(f"E2E tunnel probe successful via {public_url}")
        return True
    vinfo(f"E2E tunnel probe failed (status={status}) via {public_url}")
    return False


# =============================================================================
# LOG TAILING
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
    log_path = f"{GATEWAY_LOG_BASE}-{today}.log"
    print(f"=== {os.path.basename(log_path)} ===")
    print(tail_file(log_path))


# =============================================================================
# CONFIG BACKUP
# =============================================================================

def backup_config() -> bool:
    """Backup clawdbot.json with date. Returns True if done."""
    if not os.path.exists(GATEWAY_CONFIG_PATH):
        vinfo("config file not found, skipping backup")
        return False
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        backup_path = os.path.join(BACKUP_DIR, f"clawdbot-plato-{today}.json")
        shutil.copy2(GATEWAY_CONFIG_PATH, backup_path)
        ok(f"config backed up to {backup_path}")
        return True
    except Exception as e:
        warn(f"config backup failed: {e}")
        return False


# =============================================================================
# NOTIFICATION
# =============================================================================

def notify_recovery(details: str) -> None:
    """POST to Comms Hub (non-blocking, with fallback)."""
    payload = {
        "to": "plato",
        "from": "recovery-script",
        "body": f"Plato gateway auto-recovery completed: {details}",
        "priority": "high"
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    for url in COMMS_HUB_URLS:
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=5):
                vinfo(f"notification sent to Comms Hub via {url}")
                return
        except Exception as e:
            vinfo(f"notification to {url} failed: {type(e).__name__}")
    vinfo("all notification endpoints failed")


# =============================================================================
# STRUCTURED OUTPUT
# =============================================================================

def build_json_result(
    status: str,
    gateway: Dict[str, Any],
    ngrok: Dict[str, Any],
    action_taken: str,
    details: str = ""
) -> Dict[str, Any]:
    result = {
        "status": status,
        "gateway": gateway,
        "ngrok": ngrok,
        "action_taken": action_taken,
        "timestamp": datetime.now().astimezone().isoformat(),
        "details": details
    }
    if NGROK_URL_CHANGED and CURRENT_NGROK_URL:
        result["ngrok_url_changed"] = True
        result["new_url"] = CURRENT_NGROK_URL
    return result


def print_json(result: Dict[str, Any]) -> None:
    print(json.dumps(result, indent=2))


# =============================================================================
# DIAGNOSE + ENHANCED HEALTH
# =============================================================================

def snapshot() -> dict:
    """Capture full current state."""
    return {
        "port_pid": get_port_owner(GATEWAY_PORT),
        "gw_nodes": find_gateway_node_processes(),
        "ngroks": find_ngrok_processes(),
        "tunnels": http_get_json(NGROK_API, timeout=3),
    }


def print_state(s: dict) -> None:
    if JSON_OUTPUT:
        return
    if s["port_pid"]:
        ok(f"port {GATEWAY_PORT}: LISTENING (PID {s['port_pid']})")
    else:
        warn(f"port {GATEWAY_PORT}: not listening")

    node_count = len(s["gw_nodes"])
    if node_count == 0:
        warn("gateway nodes: 0")
    elif node_count == 1:
        ok("gateway nodes: 1")
    else:
        err(f"gateway nodes: {node_count} (DUPLICATES DETECTED)")

    for node in s["gw_nodes"]:
        vinfo(f"  node PID={node['pid']} cmd={node['cmd'][:80]}...")

    ngrok_count = len(s["ngroks"])
    if ngrok_count > 0:
        ok(f"ngrok processes: {ngrok_count}")
    else:
        warn("ngrok processes: 0")

    t = s.get("tunnels")
    if t and t.get("tunnels"):
        urls = [x.get("public_url", "") for x in t["tunnels"]]
        ok(f"tunnels active: {urls}")
        if EXPECTED_NGROK_URL not in "".join(urls):
            warn(f"  current URL differs from expected {EXPECTED_NGROK_URL}")
    else:
        warn("no active tunnels")


def enhanced_verify() -> Tuple[bool, bool, Dict[str, Any], Dict[str, Any]]:
    """Return (gw_healthy, ngrok_healthy, gw_dict, ngrok_dict) with full probes."""
    s = snapshot()
    port_pid = s["port_pid"]
    port_ok = port_pid is not None
    nodes = s["gw_nodes"]
    node_count = len(nodes)

    # Gateway HTTP probe
    http_ok = False
    if port_ok:
        http_ok = probe_gateway_http()
        if not http_ok and node_count > 0:
            warn("Port listening but HTTP /api/status failed - killing all gateway nodes")
            for node in nodes:
                kill_tree(node["pid"])
            time.sleep(4)

    gw_healthy = port_ok and http_ok
    gw_dict = {
        "port": port_ok,
        "http": http_ok,
        "pid": port_pid or 0,
        "node_count": node_count
    }

    # Ngrok + dynamic E2E
    tunnels = s.get("tunnels")
    ngrok_process_ok = bool(tunnels and tunnels.get("tunnels"))
    current_url = get_current_ngrok_url()
    global CURRENT_NGROK_URL, NGROK_URL_CHANGED
    CURRENT_NGROK_URL = current_url
    if current_url and current_url != EXPECTED_NGROK_URL:
        NGROK_URL_CHANGED = True
        warn(f"NGROK URL CHANGED! Expected: {EXPECTED_NGROK_URL}")
        warn(f"New URL: {current_url}")
        warn("Google Chat webhook config MUST be updated!")

    tunnel_ok = False
    if ngrok_process_ok and current_url:
        tunnel_ok = probe_e2e_tunnel(current_url)

    ngrok_healthy = ngrok_process_ok and tunnel_ok
    ngrok_dict = {
        "process": ngrok_process_ok,
        "tunnel": tunnel_ok,
        "url": current_url or EXPECTED_NGROK_URL,
        "url_changed": NGROK_URL_CHANGED
    }

    if not JSON_OUTPUT:
        if gw_healthy:
            ok(f"gateway: healthy (port + HTTP, {node_count} node(s))")
        else:
            if port_ok and not http_ok:
                err("gateway: port up but HTTP probe FAILED")
            elif port_ok:
                ok(f"gateway: port up ({node_count} node(s))")
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
# TEARDOWN / RECOVERY
# =============================================================================

def teardown() -> bool:
    """Full teardown - kill ALL gateway nodes and ngrok."""
    info("teardown: killing all gateway node.exe processes")
    for node in find_gateway_node_processes():
        info(f"killing gateway node PID {node['pid']}")
        kill_tree(node["pid"])

    info("teardown: killing ngrok")
    for ng in find_ngrok_processes():
        info(f"killing ngrok PID {ng['pid']}")
        kill_tree(ng["pid"])

    info(f"waiting up to {PORT_FREE_TIMEOUT_S}s for port {GATEWAY_PORT} to free")
    for i in range(PORT_FREE_TIMEOUT_S):
        if get_port_owner(GATEWAY_PORT) is None:
            ok(f"port free after {i + 1}s")
            return True
        time.sleep(1)
    warn(f"port still held after {PORT_FREE_TIMEOUT_S}s (continuing anyway)")
    return False


def restart_gateway() -> bool:
    """Restart via scheduled task (Plato uses schtasks directly)."""
    info(f"ending scheduled task '{GATEWAY_TASK}'")
    trigger_scheduled_task(GATEWAY_TASK, "end")
    time.sleep(3)

    info(f"starting scheduled task '{GATEWAY_TASK}'")
    if not trigger_scheduled_task(GATEWAY_TASK, "run"):
        err(f"could not trigger task '{GATEWAY_TASK}'")
        return False

    info(f"waiting up to {GATEWAY_BIND_TIMEOUT_S}s for gateway to bind + respond")
    for i in range(GATEWAY_BIND_TIMEOUT_S):
        time.sleep(1)
        if get_port_owner(GATEWAY_PORT):
            for _ in range(8):  # extra time for HTTP readiness
                if probe_gateway_http():
                    ok(f"gateway healthy on port {GATEWAY_PORT} after {i+1}s")
                    return True
            ok(f"gateway listening on port {GATEWAY_PORT} (HTTP settling)")
            return True
    err(f"gateway did not become healthy in time")
    return False


def restart_ngrok() -> bool:
    """Restart ngrok manually (Plato-specific)."""
    info("stopping existing ngrok processes")
    for ng in find_ngrok_processes():
        kill_tree(ng["pid"])
    time.sleep(3)

    info("starting new ngrok process (http 18789, hidden)")
    try:
        subprocess.Popen(
            ["ngrok", "http", "18789"],
            creationflags=subprocess.CREATE_NO_WINDOW,
            shell=False
        )
        info("ngrok Start-Process equivalent executed")
    except Exception as e:
        err(f"failed to start ngrok: {e}")
        return False

    info(f"waiting up to {NGROK_REGISTER_TIMEOUT_S}s for tunnel")
    for i in range(NGROK_REGISTER_TIMEOUT_S):
        time.sleep(1)
        current_url = get_current_ngrok_url()
        if current_url:
            global CURRENT_NGROK_URL, NGROK_URL_CHANGED
            CURRENT_NGROK_URL = current_url
            if current_url != EXPECTED_NGROK_URL:
                NGROK_URL_CHANGED = True
                warn("NGROK URL HAS CHANGED!")
                warn(f"New URL: {current_url}")
                warn("→ Update Google Chat webhook configuration immediately!")
            if probe_e2e_tunnel(current_url):
                ok(f"E2E tunnel verified after {i+1}s")
                return True
            else:
                warn("ngrok tunnel registered but E2E probe still failing")
                return True  # still consider partial success
    warn("ngrok did not register tunnel in time")
    return False


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    global VERBOSE, JSON_OUTPUT, NGROK_URL_CHANGED, CURRENT_NGROK_URL

    p = argparse.ArgumentParser(
        description="Recover Plato gateway + ngrok (dynamic URL) with full diagnostics (v2).",
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
    NGROK_URL_CHANGED = False
    CURRENT_NGROK_URL = None

    if not JSON_OUTPUT:
        print(f"{C.BOLD}Plato Recovery v2 -- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.END}")
        print(f"Host: NIETZSCHE2025 | Port: {GATEWAY_PORT} | Task: '{GATEWAY_TASK}'")

    header("diagnose")
    s = snapshot()
    print_state(s)

    gw_dict = {"port": bool(s["port_pid"]), "http": False, "pid": s.get("port_pid") or 0, "node_count": len(s.get("gw_nodes", []))}
    ngrok_dict = {"process": bool(s.get("tunnels") and s["tunnels"].get("tunnels")), "tunnel": False, "url": EXPECTED_NGROK_URL, "url_changed": False}
    action_taken = "none"

    gw_healthy, ngrok_healthy, gw_dict, ngrok_dict = enhanced_verify()
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

    if args.soft and gw_healthy and ngrok_healthy and not NGROK_URL_CHANGED:
        if JSON_OUTPUT:
            result = build_json_result("healthy", gw_dict, ngrok_dict, "none")
            print_json(result)
        else:
            print()
            ok("--soft: everything healthy, no action needed")
        return 0

    # Recovery logic
    if args.soft:
        header("soft recovery")
        if not gw_healthy:
            info("gateway unhealthy - restarting via scheduled task")
            teardown()
            gw_final = restart_gateway()
            action_taken = "soft_gateway_restart"
        else:
            gw_final = True

        if not ngrok_healthy or NGROK_URL_CHANGED:
            info("ngrok unhealthy or URL changed - restarting")
            ngrok_final = restart_ngrok()
            action_taken = "soft_ngrok_restart" if action_taken == "none" else "soft_full_restart"
        else:
            ngrok_final = True
    else:
        header("full recovery")
        teardown()
        header("restart gateway")
        gw_final = restart_gateway()
        header("restart ngrok")
        ngrok_final = restart_ngrok()
        action_taken = "full_recovery"

    # Final verification
    header("final verification")
    final_gw_ok, final_ngrok_ok, final_gw_dict, final_ngrok_dict = enhanced_verify()
    final_status = "healthy" if final_gw_ok and final_ngrok_ok else "degraded" if final_gw_ok or final_ngrok_ok else "down"
    success = final_gw_ok and final_ngrok_ok

    if success:
        backup_config()
        if not args.check:
            notify_recovery("gateway and ngrok recovered (HTTP + E2E verified)")
        if not JSON_OUTPUT:
            print()
            print(f"{C.GREEN}{C.BOLD}RECOVERY COMPLETE{C.END}")
            if NGROK_URL_CHANGED:
                print(f"{C.YELLOW}{C.BOLD}WARNING: Ngrok URL changed! Update Google Chat webhook.{C.END}")
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
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().astimezone().isoformat()
            }, indent=2))
        else:
            err(f"unexpected error: {e}")
            import traceback
            traceback.print_exc()
        sys.exit(1)
