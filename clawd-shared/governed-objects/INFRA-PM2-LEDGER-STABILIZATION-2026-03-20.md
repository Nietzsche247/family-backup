# INFRA — PM2 + Ledger Prod Stabilization (2026-03-20)

**Scope:** Documentation-only runbook for two issues resolved on 2026-03-20.

- Issue A: PM2 CLI failing with `EPERM` on `//./pipe/rpc.sock` (Windows named pipe permissions)
- Issue B: Ledger **prod** (port **3002**) crash-looping with `EADDRINUSE` (zombie Node process holding the port)

**Environment:** Windows host; PM2 daemon uses a local RPC named pipe (e.g., `\\.\pipe\rpc.sock`).

---

## Executive Summary

1) **PM2 EPERM / pipe access** happened because the PM2 daemon was started under an **elevated (Admin)** context. Later, PM2 commands were run from a **non-elevated** shell, which could not access the Admin-owned named pipe.

**Fix:** Kill the Admin-owned PM2 daemon using `gsudo`, then start a new PM2 daemon from a normal (non-elevated) shell.

2) **Ledger prod EADDRINUSE** happened because a **zombie Node process** (PID **47180**) still held **TCP 3002**. PM2 kept restarting ledger, but it could not bind the port.

**Fix:** Identify and kill the process holding port 3002 (required elevation), then restart the ledger process via PM2.

---

## Issue A — PM2 CLI EPERM on `//./pipe/rpc.sock`

### Symptoms

- Any PM2 CLI call from a normal shell fails (examples):
  - `pm2 list`
  - `pm2 logs`
  - `pm2 restart <app>`
- Error resembles:

```text
Error: connect EPERM \\.\pipe\rpc.sock
# (sometimes shown as //./pipe/rpc.sock)
```

### Root Cause (What broke and why)

PM2 runs a background daemon (`pm2` “God” process) and the CLI connects to it via an IPC mechanism. On Windows that IPC is a **named pipe**.

If the daemon was started from an **elevated (Administrator)** terminal, the named pipe inherits permissions/ownership aligned with that elevated context. When you later run `pm2` commands from a **non-elevated** terminal, the CLI cannot connect to the daemon’s pipe and fails with `EPERM`.

### Diagnosis (Quick checks)

1) Confirm error:

```powershell
pm2 list
```

2) Confirm you are running non-elevated (no Admin) while the daemon likely is elevated.

3) Optional: check whether PM2 is running under a different user/session.

### Fix (Reproducible steps)

> Goal: stop the elevated daemon, then let a non-elevated shell create a new daemon.

1) **From a normal (non-elevated) shell**, verify the failure:

```powershell
pm2 list
```

2) **Kill the PM2 daemon using elevation** (because it was started elevated):

```powershell
gsudo pm2 kill
```

3) **From the normal (non-elevated) shell**, start PM2 again. Any PM2 command will re-spawn the daemon; `pm2 list` is simplest:

```powershell
pm2 list
```

4) If your environment relies on a saved process list, restore it (only if applicable in your setup):

```powershell
pm2 resurrect
```

5) Confirm normal operations:

```powershell
pm2 list
pm2 logs --lines 50
```

### Prevention (How to avoid recurrence)

- **Do not run PM2 commands from an elevated/Admin shell** unless you intend the daemon to be owned by that elevated context.
- Standardize on one execution context for PM2:
  - Prefer **non-elevated** day-to-day operations.
  - If a command truly requires elevation (e.g., killing a system-owned process), elevate *only that command* (e.g., `gsudo taskkill ...`) rather than starting PM2 itself elevated.
- If you must use different contexts, consider standardizing `PM2_HOME` (advanced), but the simplest operational rule is: **PM2 daemon and PM2 CLI must run under the same privilege/user context**.

---

## Issue B — Ledger prod crash-looping with `EADDRINUSE` on port 3002

### Symptoms

- Ledger “prod” process in PM2 repeatedly restarts (crash-loop).
- PM2 logs show bind failure:

```text
Error: listen EADDRINUSE: address already in use 0.0.0.0:3002
# or similar
```

### Root Cause (What broke and why)

A **zombie/orphaned Node.js process** was still bound to **TCP port 3002**, preventing the ledger server from binding the same port.

In this incident, the process holding the port was:

- **PID:** `47180`

Because the port was occupied, each PM2 restart attempt immediately failed with `EADDRINUSE`, creating a crash-loop.

### Diagnosis (Reproducible)

1) Identify which PID is bound to port 3002:

```powershell
netstat -ano | findstr :3002
```

This typically returns one or more lines including the PID in the last column.

2) Identify the process name for the PID (optional but recommended):

```powershell
tasklist /FI "PID eq 47180"
```

### Fix (Reproducible steps)

> Goal: free port 3002, then restart ledger under PM2.

1) Find the PID holding the port:

```powershell
netstat -ano | findstr :3002
```

2) Kill the offending PID.

If termination requires elevation:

```powershell
gsudo taskkill /PID 47180 /F
```

(Alternative PowerShell form):

```powershell
gsudo powershell -NoProfile -Command "Stop-Process -Id 47180 -Force"
```

3) Restart ledger via PM2:

```powershell
pm2 restart <ledger-prod-process-name>
```

If you do not remember the process name:

```powershell
pm2 list
```

4) Confirm ledger is listening on 3002:

```powershell
netstat -ano | findstr :3002
pm2 status
pm2 logs <ledger-prod-process-name> --lines 100
```

### Prevention (How to avoid recurrence)

- **Avoid manual `node ...` runs** of the prod service on the same host/port when PM2 is responsible for the process.
- When stopping/restarting ledger:
  - Prefer `pm2 restart <name>` over killing processes directly.
  - If you must kill a PID, immediately verify the port is freed (`netstat -ano | findstr :3002`) before restarting.
- Consider adding operational checks before restart (runbook-level):
  - “Port 3002 is free” check
  - “No stray node.exe bound to 3002” check

---

## Note: `LEDGER_MUTATION_SECRET` warning in prod

### Observed behavior

Prod logs include a warning that `LEDGER_MUTATION_SECRET` is **not set**.

Operational impact described:

- “Privileged PATCH mutations” fail **closed** when the secret is missing.
  - i.e., mutation endpoints that require the secret will reject requests rather than allowing unauthenticated mutation.

### Assessment

- From a security and safety perspective, **fail-closed is the correct default** for privileged mutation capability.
- Whether this is an operational problem depends on whether current production workflows *require* remote privileged mutations (e.g., emergency corrections, administrative edits).

### Recommendation (concrete)

- **Default recommendation: leave `LEDGER_MUTATION_SECRET` unset in prod** unless there is a documented, recurring operational need for privileged mutations.
  - Treat the warning as an expected indicator that prod mutation endpoints are intentionally disabled.
- If privileged mutations are required for current ops, then:
  1) Define the operational use-case(s) (who uses it, when, and for what).
  2) Set `LEDGER_MUTATION_SECRET` to a **high-entropy** value stored in an appropriate secret store.
  3) Restrict and audit its usage (limit network exposure, log mutation actions, rotate on schedule).

**Next step (non-invasive, documentation-only):** confirm with the service owner/operator whether any current runbook depends on privileged PATCH mutations. If not, update the service documentation to state explicitly: “In prod, mutations are disabled by default (no `LEDGER_MUTATION_SECRET`), which is intended.”

---

## Appendix — Copy/paste command snippets

### PM2 EPERM recovery

```powershell
pm2 list

gsudo pm2 kill

pm2 list
pm2 resurrect   # only if you rely on saved process list
```

### Find & free port 3002

```powershell
netstat -ano | findstr :3002

gsudo taskkill /PID <PID> /F

pm2 restart <ledger-prod-process-name>
pm2 logs <ledger-prod-process-name> --lines 100
```
