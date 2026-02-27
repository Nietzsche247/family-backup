# Acquire lease (returns renewal_token)
curl -sS -X POST http://localhost:8080/v3/leases/acquire \
  -H 'content-type: application/json' \
  -d '{"session_id":"sess-001","holder_agent":"supervisor","ttl_seconds":60}'
# => {"lease_id":"lease-...","renewal_token":"rtok-...","expires_at_utc":"2026-02-27T...Z"}

# Renew lease (renewal_token required)
curl -sS -X POST http://localhost:8080/v3/leases/renew \
  -H 'content-type: application/json' \
  -d '{"lease_id":"lease-...","renewal_token":"rtok-...","ttl_seconds":60}'
# => 200 renewed; wrong/missing token => 403

# Stage handoff with pointer JSON + hashes
curl -sS -X POST http://localhost:8080/v3/handoffs/stage \
  -H 'content-type: application/json' \
  -d '{
    "handoff_id":"hof-001",
    "session_id":"sess-001",
    "from_agent":"supervisor",
    "to_agent":"worker-A",
    "pointer": {"z_path":"/z/sess-001/hof-001","shared_path":"/shared/sess-001/hof-001","manifest":[{"path":"context.txt","sha256":"..."}]},
    "pointer_hash":"sha256:...",
    "manifest_hash":"sha256:..."
  }'
# => appends pointer-staged event only (append-only events)

# Finalize handoff (server verifies by reading Z/shared and recomputing hash)
curl -sS -X POST http://localhost:8080/v3/handoffs/finalize \
  -H 'content-type: application/json' \
  -d '{"handoff_id":"hof-001","session_id":"sess-001"}'
# Server behavior:
# 1) reads pointer.z_path (and optionally shared_path)
# 2) recomputes file sha256 + manifest hash + pointer hash
# 3) stores finalized_* fields with finalized_at_utc from server clock
# 4) writes finalize.marker
# 5) appends pointer-finalized event

# Pointer events are append-only (no updates/deletes)
curl -sS "http://localhost:8080/v3/events?session_id=sess-001&type=pointer-*"
# => ordered stream with unique event_id entries
