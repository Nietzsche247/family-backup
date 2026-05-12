# SHADOWBROKER PROJECT — NorthStar File
*Last updated: 2026-03-12 by Thales*

---

## 🟢 STATUS: RUNNING — DNS PENDING

Shadowbroker is fully deployed and operational on VPS **5.78.186.135**.  
The only remaining blocker is a missing **Cloudflare DNS record** for `god-eye.stigmergy.space`.

---

## Infrastructure

| Component | Status | Details |
|-----------|--------|---------|
| VPS | ✅ Online | Hetzner, 5.78.186.135, 3 vCPU / ~3.6GB RAM |
| Frontend | ✅ Running | `shadowbroker-frontend` → port 3001→3000 (Next.js 16) |
| Backend | ✅ Running | `shadowbroker-backend` → port 8000 (uvicorn/FastAPI) |
| Caddy | ✅ Running | Reverse proxy on :80/:443, configured for god-eye.stigmergy.space |
| Docker | ✅ All containers up | `docker ps` clean |

---

## SSH Access

```
ssh -i C:\Users\aaron\.ssh\hetzner_stigmergy root@5.78.186.135
```

---

## File Locations on VPS

| Path | Purpose |
|------|---------|
| `/opt/shadowbroker/` | App root |
| `/opt/shadowbroker/docker-compose.yml` | Container orchestration |
| `/opt/shadowbroker/.env` | API credentials (populated ✅) |
| `/etc/caddy/Caddyfile` | Reverse proxy config |
| `/var/log/caddy/god-eye.log` | Caddy access log (file exists) |

---

## Caddyfile

```
god-eye.stigmergy.space {
    reverse_proxy localhost:3001
    encode gzip
    log {
        output file /var/log/caddy/god-eye.log
        format json
    }
}

shadow.stigmergy.space {
    reverse_proxy localhost:3001
    encode gzip
    log {
        output file /var/log/caddy/shadowbroker.log
        format json
    }
}
```

---

## API Credentials (in `/opt/shadowbroker/.env`)

| Key | Value |
|-----|-------|
| AIS_API_KEY | 752786e8773d06c8509dbd45fafc5db447075624 |
| OPENSKY_CLIENT_ID | aaron@omnipools.com-api-client |
| OPENSKY_CLIENT_SECRET | GTBPKh4qTlCE73yYN2x2LQMqGKj1YY83 |
| LTA_ACCOUNT_KEY | 886a7a9f9a5caf17730d914cd5c93276 |
| CORS_ORIGINS | https://god-eye.stigmergy.space |

---

## Backend Data Sources (Confirmed Working)

| Source | Status |
|--------|--------|
| OpenSky (flights) | ✅ OAuth2 token active, fetching 300+ aircraft per region |
| AIS Stream (vessels) | ✅ 48 AIS vessels received |
| LTA Singapore CCTV | ✅ 90 cameras ingested |
| Austin TX CCTV | ✅ 985 cameras ingested |
| NYC DOT CCTV | ✅ 954 cameras ingested |
| TFL JamCam (London) | ✅ 884 cameras ingested |
| CelesTrak Satellites | ✅ 14,683 GP records, 549 classified |
| DeepStateMap (Ukraine) | ✅ Downloading daily geojson |
| GDELT Events | ✅ 32 export files downloaded |
| NASA FIRMS Fires | ✅ 5,000 hotspots |
| GPS Jamming | ✅ 15 interference zones |
| Space Weather | ✅ Kp=1.0 QUIET |
| Carrier Tracker | ✅ 11 carriers tracked |
| Airports | ✅ 1,189 large airports cached |

---

## ❗ Action Required: DNS

**Problem:** `god-eye.stigmergy.space` has no DNS record. The domain uses **Cloudflare nameservers**.

**Fix:** Go to Cloudflare dashboard → stigmergy.space → DNS  
Add an **A record**:
- **Name:** `god-eye`
- **IPv4:** `5.78.186.135`
- **Proxy status:** ☁️ Proxied (or DNS only)

Once DNS propagates, Caddy will auto-obtain a Let's Encrypt TLS cert and `https://god-eye.stigmergy.space` will be live.

> Note: `shadow.stigmergy.space` also needs the same A record if you want that hostname to work.

---

## Verification Commands

```bash
# Check containers
cmd.exe /c ssh -i C:\Users\aaron\.ssh\hetzner_stigmergy root@5.78.186.135 docker ps

# Check frontend directly (bypasses DNS)
curl.exe -I http://5.78.186.135:3001/

# Check backend health
cmd.exe /c ssh -i C:\Users\aaron\.ssh\hetzner_stigmergy root@5.78.186.135 "docker logs shadowbroker-backend --tail 20"

# Restart after .env changes
cmd.exe /c ssh -i C:\Users\aaron\.ssh\hetzner_stigmergy root@5.78.186.135 "cd /opt/shadowbroker && docker compose up -d --force-recreate"
```

---

## History

| Date | Event |
|------|-------|
| 2026-03-12 06:27 | Initial Caddy + Docker setup |
| 2026-03-12 14:12 | First Caddyfile with god-eye/shadow hostnames (log permission error) |
| 2026-03-12 14:19 | Caddy restarted successfully, log dir fixed |
| 2026-03-12 14:32 | **Backend recreated with populated .env — all API keys active** |
| 2026-03-12 14:32 | **Backend healthy: all data sources live** |
| 2026-03-12 14:32 | **Blocker identified: DNS A record missing in Cloudflare** |

---

*Frontend title: "WORLDVIEW // ORBITAL TRACKING — Advanced Geopolitical Risk Dashboard"*
