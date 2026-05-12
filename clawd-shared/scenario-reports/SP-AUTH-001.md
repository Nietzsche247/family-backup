# SP-AUTH-001 — Privileged role authentication hardening (PATCH /handoffs/:handoff_id)

Date: 2026-03-03
Agent: daedalus
Repo: `C:\North_Star_Projects\ledger`

## Summary
Implemented real authentication for privileged mutation endpoint `PATCH /handoffs/:handoff_id` using a shared secret bearer token.

## Changes made
File: `C:\North_Star_Projects\ledger\server.js`

1. Added privileged mutation secret config:
- `LEDGER_MUTATION_SECRET` from env

2. Added bearer-token auth helpers:
- `getBearerToken(authHeader)`
- `isAuthorizedPrivilegedMutation(req)`
  - Fails closed if `LEDGER_MUTATION_SECRET` is unset
  - Requires `Authorization: Bearer <secret>`
  - Uses `crypto.timingSafeEqual` for token comparison

3. Updated role-gated mutation endpoint:
- `PATCH /handoffs/:handoff_id`
  - Auth check first: invalid/missing token => `401 Unauthorized`
  - Existing role whitelist preserved: non-`reconciler|supervisor` => `403 Forbidden`

4. Boot-time warning added:
- On startup, if `LEDGER_MUTATION_SECRET` is unset, logs warning and privileged PATCH remains denied (fail-closed behavior)

## Scope validation
Applied to:
- ✅ `PATCH /handoffs/:handoff_id`

Not applied to:
- ✅ `POST /events`
- ✅ GET endpoints
- ✅ `POST /register`, `PUT /update`, `POST /deprecate`

## Verification
Test handoff created: `hf-authfix-860ff10880e0`

Results:
- PATCH without Authorization header → **401** ✅
- PATCH with wrong secret → **401** ✅
- PATCH with correct secret + wrong role → **403** ✅
- PATCH with correct secret + correct role → **200** ✅

Observed response matrix:
- `no_auth=401`
- `wrong_secret=401`
- `bad_role=403`
- `ok_status=200 ... repl=replicated`

## Internal caller safety (reconciler/ingest)
Confirmed internal reconciler path still uses direct function call (no HTTP auth path):
- `patchHandoffReplication(...)` is invoked from reconciler service code path directly.
- HTTP auth gate only applies inside `app.patch('/handoffs/:handoff_id', ...)`.

Therefore internal direct callers are **not affected** by this HTTP auth change.

## Runtime / restart
Restart command executed via gsudo wrapper with env injection script:
- `C:\North_Star_Projects\ledger\scripts\restart-ledger-auth-fix.ps1`
- Script sets `LEDGER_MUTATION_SECRET` then runs `pm2 restart ledger --update-env`

## Ledger event registration
Posted:
```json
{
  "event_type": "infrastructure_registered",
  "agent": "daedalus",
  "project_id": "core",
  "gate_id": "validation-prerequisites",
  "recovery_id": "auth-fix-2026-03-03"
}
```

Result:
- status: `logged`
- event_id: `01KJTZZXRTQNB43RBHYZJG6VF6`

## Notes
- Fail-closed behavior is active: if `LEDGER_MUTATION_SECRET` is absent, privileged PATCH mutations are denied.
- Existing Phase A behavior for non-target endpoints remains unchanged.
