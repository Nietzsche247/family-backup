# STATE.md — Current Operations

**Last Updated:** 2026-03-06 12:27 MST

---

## Completed (Anchored)

| Item | Ledger Event |
|------|-------------|
| Deployment Model v1 (Core/Client) | `01KK24GCH7PVJTHN4D7HXBQXRN` |
| **Plato Client Node Proof — 10/10 PASS** | `01KK29Y2JVY4EPZMD4R19ZCF97` |
| ChangeOrder v1 Phase 1 PASS | `01KK20TCPPF3SJCTNVVWPT9W03` |
| ChangeOrder v1 Phase 1.5 PASS | `01KK21N3HCKD2K04H0YANW40VV` |
| P1: Stale lease fix | `01KK22MXAKYD87JM276MGNJ02W` |
| P2: Bootcapsule endpoint | `01KK22PY9SB42ZFR8BSNS4D84B` |
| P3: Setup/Verify docs | `01KK22MB8Q` / `01KK22MB9C` |
| Network exposure review | `01KK25JX2R6T3K8ABXWWKQX04G` |
| Thales → GPT-5.4 | Applied |

## Awaiting Direction

- Empiricus client proof (reuse Plato script with CLIENT_NAME=Empiricus)
- Fresh-install proof on clean VM (separate track)
- Next domain object / UI visibility / packaging

## Portability Seams (Known)

| Seam | Severity | v1 Acceptable? |
|------|----------|---------------|
| Cross-node file hash verification (terminal transitions) | Medium | Yes — non-terminal works, terminal deferred |
| SMB auth between machines (no shared credentials) | Low | Yes — LAN HTTP works, SMB is convenience |
| Tailscale DERP relay latency (no direct connection) | Low | Yes — LAN fallback works |
| Staging PM2_HOME operator awareness | Low | Yes — documented |

## Infrastructure

- comms-hub: ✅ online (3001)
- ledger: ✅ online (3002)
- ledger-staging: ✅ online (3003)
- cloudflared: ✅ running
- Ollama: ✅ HTTP 200
