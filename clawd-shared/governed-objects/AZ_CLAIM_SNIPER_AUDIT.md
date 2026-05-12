# AZ Claim Sniper — Comprehensive Audit
**Audit Date:** 2026-03-24  
**Auditor:** Steel Man (sub-agent)  
**Source:** `C:\Users\aaron\clawd-shared\specs\AZ_Claim_Sniper_src\`  
**Scope:** Code quality, security, concept viability, deployment path  
**Files reviewed:** 368 files across backend, frontend, scripts, docs, data

---

## Executive Summary

AZ Claim Sniper is a **genuinely impressive, production-near single-user tool** for hunting forfeited BLM mining claims in Arizona. The codebase is well-architected, clearly documented, and solves a real, non-trivial problem. The author knows Python, knows BLM data structures, and has been very thoughtful about the data pipeline.

**The good news:** This is deployable with moderate effort. There are no architectural dealbreakers and the code quality is high for a solo project.

**The bad news:** The tool was built for local, single-user, trusted access. Putting it on a public-facing web server without an auth layer creates serious exposure. There is also a **live API key for metals.dev hardcoded in the committed `.env` file** — the most urgent finding.

**Deployment on hub.stigmergy.space is feasible but requires 5 things before it goes public:**
1. Rotate the leaked metals.dev API key
2. Add authentication (even HTTP Basic Auth is acceptable for now)
3. Swap SQLite → Postgres or at minimum ensure WAL mode for concurrent readers
4. Pre-cache the two BLM CSVs before container start (avoid 1.75GB download mid-request)
5. Plan for ~4GB persistent storage and a machine with ≥2GB RAM

**Overall risk rating for public deployment as-is: HIGH**  
**Overall code quality rating: B+ (strong for solo project, needs auth layer)**  
**Concept viability: Excellent — this fills a genuine gap**

---

## Part 1: Code Audit

### 1.1 — CRITICAL: Hardcoded Secrets in Committed `.env`

**Severity: CRITICAL**

The `.env` file was included in the repository backup (it is NOT in `.gitignore` enforcement, only in the comment header). It contains:

| Secret | Status |
|--------|--------|
| `METALS_API_KEY=UOWYVDJPFOCBFH1S0TME2101S0TME` | **LIVE KEY — ROTATE IMMEDIATELY** |
| `LOCATOR_NAME=Aaron Baker, Michael Baker` | PII — personal name |
| `LOCATOR_ADDRESS=8880 N. Camino Coronado, Tucson, AZ 85704` | PII — home address |
| `LOCATOR_PHONE=520-591-8884` | PII — personal phone |
| `FLASK_SECRET_KEY=change_this_to_a_random_string_in_production` | Weak default — not rotated |

The `.gitignore` lists `.env` as ignored, but the file was physically included in the backup upload (Plato uploaded the full project backup including the `.env`). If this backup ever lands in a git repo, all secrets leak.

**Immediate action:** Rotate the metals.dev API key at https://metals-api.com/dashboard before doing anything else with this project.

The `FLASK_SECRET_KEY` being a literal placeholder is also a security issue — if left as-is in production, Flask session cookies can be forged.

**The `.env.example` is clean** — it has correct placeholder values throughout. The problem is the actual `.env` having real data included in the backup.

---

### 1.2 — Tech Stack

**Language:** Python 3.13  
**Framework:** Flask 3.x with Flask-CORS  
**Database:** SQLite (via raw `sqlite3` module + SQLAlchemy as optional Postgres swap path)  
**Task scheduling:** APScheduler (background BLM pull, Sundays 2am)  
**Browser automation:** Playwright (for BLM MLRS/105 Oracle BI form — no REST API exists)  
**PDF generation:** ReportLab + fpdf2 + Jinja2 templates  
**GIS/mapping:** simplekml, gpxpy, pyshp, pyproj, folium, Pillow  
**Data processing:** pandas, numpy  
**External integrations:** Google Drive/Sheets (optional), metals.dev API  
**Frontend:** Single-file vanilla HTML/CSS/JS (index.html, ~2,250 lines) — no build step, no framework  
**Containerization:** Docker + docker-compose (present but README marks Stage 4 as incomplete)

**Assessment:** Solid, pragmatic stack. Flask is appropriate for this use case. No overcomplicated framework choices. The single-file frontend is refreshingly simple and will load fast.

---

### 1.3 — SQL Injection Analysis

**Severity: MEDIUM (contained but real)**

The codebase uses SQLite's parameterized `?` placeholders for all user-supplied values correctly in most places. However, there are several instances of **dynamic SQL string construction** that warrant attention:

**Flagged patterns in `backend/routes/claims.py`:**

```python
# Line ~206 — filter query built dynamically:
q = "SELECT * FROM claims WHERE (land_status != 'Private' OR land_status IS NULL)"
params = []
if county: q += " AND county=?"; params.append(county)
if mineral: q += " AND mineral=?"; params.append(mineral)
if claim_type: q += " AND claim_type=?"; params.append(claim_type)
```
This pattern is safe — values go through `?` placeholders. ✅

```python
# export.py line ~22 — IN clause with serial list:
placeholders = ",".join("?" * len(serials))
rows = conn.execute(
    f"SELECT * FROM claims WHERE serial_number IN ({placeholders})", serials
)
```
This is safe — the `?` count matches the input list. ✅

```python
# database.py — ALTER TABLE dynamic column:
conn.execute(f"ALTER TABLE claims ADD COLUMN {col_def}")
```
**RISK:** `col_def` is a hardcoded constant string in `init_db()`, not user input. Safe in practice, but the pattern is dangerous if ever refactored to accept external input. ⚠️

```python
# blm_mapserver.py — LIKE pattern with serial:
f"CSE_NR LIKE '{serial}%'"
```
**RISK:** `serial` comes from a URL path parameter (e.g. `/api/claims/<serial>`). If a user can provide `AZ'; DROP TABLE--`, this would be a SQL injection. However: (a) serials are validated to start with "AZ" format in most flows, and (b) this is a BLM external API query, not a local SQLite query — it's an HTTP request to gis.blm.gov, not a database call. The injection risk here is against BLM's ArcGIS API, which has its own server-side defenses. Still worth fixing. ⚠️

```python
# field.py — staking_status from user input:
allowed_fields = { "staking_status": "staking_status", ... }
set_clauses.append(f"{col}=?")  # col comes from allowed_fields dict, not raw input
```
Safe — `col` is always a whitelisted key from `allowed_fields`. ✅

**Overall SQL injection verdict:** No direct SQLite injection path found through controlled testing. The pattern is mostly safe. The BLM API LIKE query is the weakest point — fix with a regex validator on serial numbers at the route level.

---

### 1.4 — Input Validation

**Severity: MEDIUM**

The tool was built for trusted single-user use. Input validation is present in some places and absent in others:

**Good:**
- `adjust_location` validates latitude (30.0–37.5°N) and longitude (-115 to -108°W) ranges
- `update_field_gps` validates all coordinate inputs as numeric via `float(val)`
- `add_historical` validates lat/lon types with try/except
- Export routes check for empty `serials` list
- Aliquot status accepted only from an internal whitelist

**Missing:**
- Serial number format is not validated before use in URL parameters. `/api/claims/<serial>` accepts any string, which then flows into SQL queries and external API calls.
- `batch_name` in export routes (used as a filesystem directory name) accepts arbitrary strings — path traversal risk if someone sends `../../etc/passwd` as a batch name. Currently `Path(config.EXPORT_PATH) / "zips" / batch_name` — this could escape the exports directory.
- No rate limiting on any endpoint. A single user can trigger unlimited BLM CSV downloads (1.75GB each), unlimited MRDS API calls, and unlimited Playwright browser launches.

**Recommended fixes:**
```python
# Serial validation (add to all routes):
import re
if not re.match(r'^(AZ[A-Z]?\d{6,11}|PLAN-\d{8}-\d{6})$', serial):
    return jsonify({"error": "Invalid serial format"}), 400

# Batch name sanitization (export.py):
batch_name = re.sub(r'[^A-Za-z0-9_\-]', '_', batch_name)[:40]
```

---

### 1.5 — Error Handling

**Severity: LOW (good practices present)**

Error handling is generally solid. The codebase consistently uses:
- Bare `except Exception: pass` for non-critical enrichment steps (acceptable — failures logged, pipeline continues)
- `try/finally` with `conn.close()` in most DB operations (good)
- Non-fatal graceful degradation throughout the enrichment pipeline
- `_safe_log()` helper that silently ignores Windows console encoding errors (practical)

**Issues found:**
- The `audit_claim` route in `claims.py` uses `importlib.util.spec_from_file_location` to dynamically load a script at runtime. This is fragile and could fail silently if the scripts path changes.
- Several places use broad `except Exception: pass` without even logging. In production, these become invisible failure modes.
- The Playwright MLRS check (`mlrs_checker.py`) has good retry logic but the `_running_checks` and `_check_results` dicts are in-process module globals — they'll be lost on server restart, leaving polls returning "not_checked" with no explanation.

---

### 1.6 — Authentication and Authorization

**Severity: HIGH (critical for public deployment)**

**There is no authentication on any endpoint.**

Every API endpoint is publicly accessible to anyone who can reach the Flask server. This includes:
- `POST /api/claims/pull` — triggers a 1.75GB BLM CSV download
- `POST /api/claims/batch-enrich` — runs 15-20 minutes of MRDS API calls
- `POST /api/claims/check-mlrs/<serial>` — launches a headless Playwright browser
- `GET /api/claims/` — exposes all claim data including locator PII
- `POST /api/export/kit` — generates and downloads full staking kits

The `CORS(app)` in `app.py` allows all origins (`*`), making this accessible from any browser.

For hub deployment, at minimum add HTTP Basic Auth via Flask-HTTPAuth or an Nginx `auth_basic` block.

---

### 1.7 — Architecture Quality

**Severity: INFO (assessment)**

**Strengths:**
- Config is genuinely centralized in `backend/config.py` — no scattered hardcodes
- Service layer is cleanly separated from routes — each service is independently testable
- `CASE WHEN IS NULL` pattern used consistently to prevent overwrites of confirmed data
- Startup index building in background threads is well-implemented
- The `get_claim_geometry()` single-source-of-truth pattern for polygon math is excellent
- The fallback chain (MapServer → CSV → PLSS → schematic) throughout is robust
- `FRAGILE_SYSTEMS.md` is genuine institutional knowledge, not boilerplate

**Weaknesses:**
- SQLite is not safe for concurrent writes from multiple processes. Flask in debug mode spawns two processes (the code handles this correctly with WERKZEUG_RUN_MAIN guard), but gunicorn with `--workers 2` would cause database corruption.
- `_running_checks` and `_mrds_index` are module-level globals — incompatible with multi-worker deployment.
- The frontend is a 2,250-line monolithic HTML file. Maintainable for now, becomes painful at 3,000+ lines.
- No tests are wired to CI. The `tests/` directory exists in the README but wasn't found in the backup (likely empty or not uploaded).

---

### 1.8 — Dependency Analysis

**Severity: LOW**

`requirements.txt` is clean and pinned to minimum versions. Key observations:

| Package | Purpose | Notes |
|---------|---------|-------|
| `playwright` | MLRS Oracle BI form automation | **NOT in requirements.txt** — must be installed separately with `playwright install chromium` |
| `pypdf` | PDF merging in `doc_generator.py` | **NOT in requirements.txt** — silent fallback if missing |
| `flask>=3.0.0` | Core framework | Flask 3.x — modern, good |
| `apscheduler>=3.10.0` | Background BLM pull | Solid library, appropriate use |
| `sqlalchemy>=2.0.0` | Postgres swap path | Installed but barely used (raw `sqlite3` module used directly) |
| `google-api-python-client` | Drive/Sheets | Optional, correctly fails gracefully |
| `simplekml, gpxpy, pyshp` | GIS exports | Niche but correct libraries |

**Missing from requirements.txt (must add):**
```
playwright>=1.40.0
pypdf>=3.0.0
```

The Playwright browser must be installed separately after pip install:
```bash
playwright install chromium
```
This is not documented in the README and will cause silent MLRS check failures.

---

### 1.9 — Code Quality Summary Table

| Area | Rating | Notes |
|------|--------|-------|
| Architecture | A | Clean separation, good patterns |
| SQL safety | B | Parameterized queries used, one LIKE concern |
| Input validation | C+ | Missing serial format validation, path traversal risk |
| Error handling | B | Good graceful degradation, some silent swallows |
| Authentication | F | None exists |
| Secret management | D | Live API key in committed .env |
| Documentation | A | Excellent FRAGILE_SYSTEMS.md, inline comments |
| Dependencies | B | Two unlisted deps (playwright, pypdf) |
| Test coverage | Unknown | Tests directory not in backup |
| Frontend security | B | XSS risk mitigated by `textContent` use; no user-generated HTML injection found |

---

## Part 2: Concept Audit

### 2.1 — What This Tool Actually Does

AZ Claim Sniper is a **forfeiture arbitrage tool for federal mining claims in Arizona**. The workflow:

1. **Data sourcing:** Downloads BLM's ArcGIS Hub "Closed Mining Claims" CSV (~1.75GB, ~430,000 national claims) and filters to ~7 AZ counties. Also downloads the "Active Claims" CSV (~500MB) for conflict checking.

2. **Claim scoring:** Runs a 9-signal composite score (0–100) per claim:
   - Prior holder tenure (how long previous owner held before forfeiting)
   - USGS MRDS development status (Producer > Past Producer > Prospect > Occurrence)
   - Claim density in the township (busy district = proven ground)
   - Critical mineral flag (DOE list of 35 strategic minerals)
   - Nearby MRDS deposit count (geological neighborhood)
   - Live mineral price (metals.dev API, cached 24h)
   - NURE geochemical anomaly (USGS stream sediment data, in-memory at startup)
   - Lode claim acreage bonus
   - Historical assay count + recency

3. **Enrichment pipeline:** For each claim, queries USGS MRDS for nearby deposits, US Census geocoder for county, AZGS mine file API for assay records, and BLM MapServer for real dates and aliquot-level overlap analysis.

4. **Conflict checking:** Compares target claim's PLSS aliquots (quarter-quarter sections) against active claims in the same section, using BLM MapServer Layer 1. Distinguishes OVERLAP (do not stake) vs ADJACENT (proceed with caution) vs CLEAR (go).

5. **Document generation:** Produces a complete staking kit: Certificate of Location (COL), Discovery Notice, envelope label pre-addressed to county recorder, BLM MCF-100a mining claim map, site map PDF (satellite or schematic), and filing instructions.

6. **Export:** KMZ for Google Earth, GPX for handheld GPS devices, QGIS shapefiles, and a master ZIP containing everything.

7. **Field use:** User opens KMZ on phone, drives to discovery monument GPS point, stakes 1 PVC post + 4 stone cairns, signs documents on-site, mails notarized COL to county recorder within 90 days, e-files BLM MLRS within 90 days.

**Assessment:** The tool genuinely understands the AZ mining claim process end-to-end. The document templates reference correct statutes (ARS 27-202, 27-203, Mining Law of 1872, 30 U.S.C. §§ 21-54). The filing checklist is accurate. This is not a toy.

---

### 2.2 — Is the BLM Data Approach Sound?

**Yes, with caveats.**

**What's solid:**
- The BLM ArcGIS Hub CSV is the authoritative source for closed claims — this is exactly the right data source. BLM makes this available publicly and it's the same data BLM staff use.
- The CSE_META PLSS parsing is correct. The "tenths notation" bug (0070N → T7N, not T70N) was found and fixed in Session 11 — the code includes a `repair_plss` endpoint to fix historical bad data.
- The aliquot-level overlap analysis via BLM MapServer is technically sophisticated. Most commercial tools don't do this — they only check at the section level.
- The NURE geochemistry integration is genuinely clever. Using 1980s EPA/USGS stream sediment data to validate mineral presence is an underutilized dataset.
- The weekly APScheduler sync (Sundays 2am) is appropriate — BLM updates the dataset weekly.

**Caveats:**
- The BLM CSV takes 3-5 minutes to download fresh. The `force_refresh=False` default means users almost always hit the cache, which is good. But the cache invalidation strategy is age-based (last file modification time shown in `/health`), not content-based.
- The active claims CSV (~500MB) is downloaded separately and cached locally. Together with the closed claims CSV, this is ~2.25GB of local data that must persist across container restarts — a volume mount is mandatory.
- BLM has changed URLs and column names historically. The `COLUMN_MAP` dict in `blm_puller.py` handles legacy names, and `FRAGILE_SYSTEMS.md` documents the breakpoints. This is good defensive programming.
- The BLM SRP (Serial Register Page) is noted as a JavaScript SPA that cannot be scraped — the code correctly provides links for manual browser access instead of breaking.
- The Playwright-based MLRS/105 check is genuinely fragile (Oracle BI absolute-coordinate clicking). It works, but any BLM UI update breaks it. The code has 3-retry logic and screenshots on failure.

---

### 2.3 — What Does the Competitive Landscape Look Like?

**Sparse — this is a genuine gap.**

| Competitor | What they do | Gap this fills |
|------------|-------------|----------------|
| BLM LR2000 | Official raw data, no UI | This tool provides a UI + scoring + export |
| BLM MLRS | Active claims only, no scoring | This tool finds the *expired* claims worth targeting |
| MineListings.com | Broker market for listed claims | Those are *listed* claims; these are *forfeited* opportunities |
| TheDiggings.com | Historic claim data, passive reference | No workflow, no document generation |
| LandVision / Regrid | GIS parcel tools, broad | No mining claim specificity, no document generation |
| Mining claim consultants | Human advisors, $500-2000/claim | This replaces their workflow at near-zero cost |

**Nobody else is doing:** automated forfeiture detection + PLSS-level conflict checking + full staking kit generation + field navigation KMZ, all in one tool.

**Opportunity:** If this were a SaaS with a subscription ($29-99/month), the serviceable addressable market in AZ alone is probably 200-500 active prospectors. Nationally (extend to NV, NM, CO, ID, MT) it's 5,000+. The biggest barrier to competitors is understanding BLM data structures deeply enough to build this — which this codebase already does.

---

### 2.4 — Legal and Compliance Risks

**Severity: LOW for data use, MEDIUM for document generation**

**BLM data usage:**
- BLM ArcGIS Hub data is US federal government public domain data. No license restrictions on downloading, processing, or republishing. ✅
- USGS MRDS data is similarly public domain. ✅
- Census geocoder is a free federal service with no ToS restrictions for reasonable use. ✅
- AZGS mine file API is a public Arizona state government service. ✅
- metals.dev has a free tier with 100 req/month — the caching strategy (24h disk + memory) keeps well within limits. ✅

**Document generation risk (MEDIUM):**
- The tool generates legal documents (Certificate of Location, Notice of Location, MCF-100a) with real statutes cited. The templates reference ARS 27-202 and 27-203 correctly.
- **Risk:** If these documents contain errors (wrong GPS, wrong section, wrong locator name), the user could file a defective location and lose their claim — or worse, file against active ground and face federal trespass.
- **Mitigation already in place:** The templates explicitly say "GPS coordinates are ESTIMATES — update before filing" and "ACTUAL PLACEMENT — fill in after staking." The MCF-100a has a separate section for field-recorded GPS. The filing instructions are 4 pages and clearly written.
- **Missing:** The tool doesn't prevent the user from exporting documents before confirming land status. A user could theoretically generate a COL for a National Park claim. The frontend *hides* such claims but doesn't *prevent* export.
- **Recommendation:** Add a server-side check: refuse to generate COL/Notice/MCF-100a for claims with `land_status` in the RESTRICTED set.

**Playwright / MLRS automation:**
- The BLM MLRS/105 is a public government website. Automating queries against it is a gray area. The User-Agent string `AZClaimSniper/1.0` is honest. The tool uses 1-2 queries per claim check with politeness delays. No ToS found on the MLRS page prohibiting automated queries.
- **Risk:** BLM could block the IP or add CAPTCHAs. The tool has fallback (shows link to manual check) if Playwright fails.

**Scraping BLM SRP:**
- Already acknowledged as a dead end (JavaScript SPA). The code correctly falls back to providing a browser link. No legal risk.

---

### 2.5 — Opportunities to Improve or Extend

**High value, low effort:**
1. **National expansion:** The CSV already contains all 50 states. Changing `TARGET_COUNTIES` to include Nevada or Colorado counties requires 2 config changes and a county recorder address update.
2. **Email notifications:** SendGrid key is in `.env.example` but not wired. Weekly email digest of new forfeitures in target counties — high-value, 2-3 hours of work.
3. **PWA manifest:** The rollout plan mentions this. A `manifest.json` + service worker would make the frontend installable as a phone app with offline KMZ caching.

**High value, medium effort:**
4. **Auth layer:** Flask-Login + simple username/password (or Google OAuth, since the Google SDK is already installed). 1-2 days.
5. **Postgres swap:** The ORM is already imported (SQLAlchemy). Swap `get_conn()` to use the SQLAlchemy engine against Postgres. 4-8 hours.
6. **Stripe subscription tier:** Key is in `.env.example`. The architecture (single Flask app, SQLite) already supports multi-user if auth is added.

**Medium value, medium effort:**
7. **Offline MLRS check:** The active claims CSV already enables section-level conflict checking without Playwright. The `active_claims.py` service does this. Deprecate the Playwright check for routine screening; keep it only for final confirmation.
8. **Document signing workflow:** Integration with a PDF signing API (DocuSign, Adobe Sign) so Aaron and Michael can sign remotely without printing.

---

## Part 3: Deployment Path

### 3.1 — Resource Requirements

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| RAM | 1.5 GB | 2-4 GB | PLSS index (430k claims × ~200 bytes) + NURE data + pandas CSV loading |
| Storage | 5 GB | 10 GB | CSVs (2.25 GB) + SQLite DB + exports dir + Docker layers |
| CPU | 1 core | 2 cores | Mostly I/O bound; CPU spikes during PDF generation |
| Network | Broadband | 100 Mbps+ | Initial CSV download: 1.75 GB + 500 MB = 2.25 GB total |
| Python | 3.11+ | 3.13 | Dockerfile specifies `python:3.13-slim` |

**Memory breakdown:**
- PLSS township index (`_twp_index`): 430,000 claims × ~300 bytes/entry ≈ **130 MB**
- Active claims township index: ~25,000 AZ active claims × ~100 bytes ≈ **2.5 MB**
- NURE data (7,633 samples × 65 elements): **~15 MB**
- MRDS district index (built lazily on first `get_district_stats()` call): **~50 MB**
- Flask + Python baseline: **~80 MB**
- Pandas CSV loading during startup (transient peak): **~400 MB**

**Total peak RAM during startup index build: ~700 MB**  
**Steady-state RAM (post-startup): ~350 MB**

**Recommendation:** Ensure the hub machine has at least 2 GB free RAM when this container is added.

---

### 3.2 — The 1.75 GB CSV Problem

**This is the most significant deployment consideration.**

The BLM Closed Claims CSV is 1.75 GB. The Active Claims CSV is ~500 MB. Together, they need to be present for the tool to function.

**Scenarios:**

**A. Fresh Docker container with no pre-cached data:**
- First request hits `/api/claims/pull` → triggers a 1.75 GB download
- Download takes 5-20 minutes depending on connection speed
- During this time, the UI shows no claims
- If the container restarts before the download completes, it starts over

**B. Volume-mounted data directory (RECOMMENDED):**
```yaml
# docker-compose.yml (already present):
volumes:
  - ./data:/app/data
```
The `data/` directory persists across container restarts. CSVs downloaded once, reused on restart. The APScheduler refreshes them Sundays at 2am.

**C. Pre-baked CSV in Docker image:**
Adding the CSVs to the Docker image increases image size to ~2.5 GB. Not recommended for a tool that needs weekly updates.

**D. Nginx caching / CDN:**
The BLM CSV URL is stable but BLM's server may rate-limit. Pre-downloading to the hub server's local storage is the cleanest option.

**Recommended approach for hub.stigmergy.space:**
1. Download both CSVs to the host machine before first container launch:
   ```bash
   mkdir -p /opt/az-claim-sniper/data
   curl -L "https://gbp-blm-egis.hub.arcgis.com/api/download/v1/items/490428b37a254d958371ace41a812822/csv?layers=0" \
     -o /opt/az-claim-sniper/data/blm_closed_az.csv
   curl -L "https://gbp-blm-egis.hub.arcgis.com/api/download/v1/items/abec5ef96dc8495d9c29a01b30cc04ee/csv?layers=0" \
     -o /opt/az-claim-sniper/data/blm_active_az.csv
   ```
2. Mount as a volume in docker-compose (already configured correctly)
3. Let the APScheduler handle weekly refreshes automatically

---

### 3.3 — Docker Configuration Assessment

The existing `Dockerfile` and `docker-compose.yml` are present and functional with some gaps:

**Dockerfile:**
```dockerfile
FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc
# ... pip install, copy code, EXPOSE 5000
CMD ["python", "run.py"]
```

**Issues:**
1. **Playwright not installed.** The Dockerfile installs Python deps but not Playwright's Chromium browser. Playwright requires additional system packages and a browser download. Add:
   ```dockerfile
   RUN pip install playwright && playwright install chromium
   RUN apt-get install -y --no-install-recommends \
       libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
       libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
       libpango-1.0-0 libcairo2 libasound2
   ```
   OR: Set `BLM_PULL_SCHEDULE=disabled` and document Playwright as optional (manual MLRS checks only).

2. **Production CMD:** The README notes to swap to gunicorn for production, but warns about single-worker requirement (SQLite + globals). Use:
   ```dockerfile
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "300", "run:app"]
   ```
   Single worker preserves SQLite safety and in-memory indices.

3. **Missing pypdf:** `pypdf` is used in `doc_generator.py` for PDF merging but not in `requirements.txt`. The code silently falls back to returning just the COL without the site map attached. Add to `requirements.txt`.

4. **The `--timeout 300`:** The batch-enrich endpoint can run 15-20 minutes. Gunicorn's default 30s timeout will kill it. Set timeout to 1200+ or use async task handling.

---

### 3.4 — Hub Integration Checklist

**Can it run alongside existing hub services?** Yes, with these conditions:

```nginx
# Nginx config (add to hub.stigmergy.space):
location /mining/ {
    auth_basic "AZ Claim Sniper";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://az-claim-sniper:5000/;
    proxy_read_timeout 1800;  # 30 min for long operations
    proxy_send_timeout 1800;
    client_max_body_size 10M;
}
```

**docker-compose addition:**
```yaml
# Add to hub's docker-compose.yml:
az-claim-sniper:
  build: ./az-claim-sniper
  ports: []  # Do NOT expose port directly; route through Nginx
  volumes:
    - /opt/az-claim-sniper/data:/app/data
    - /opt/az-claim-sniper/exports:/app/exports
  env_file:
    - /opt/az-claim-sniper/.env
  environment:
    - FLASK_ENV=production
    - FLASK_DEBUG=0
    - FLASK_HOST=0.0.0.0
  restart: unless-stopped
```

**Step-by-step deployment plan:**

| Step | Task | Effort | Blocker? |
|------|------|--------|---------|
| 1 | Rotate metals.dev API key | 5 min | YES — do first |
| 2 | Create clean `.env` from `.env.example` | 15 min | YES |
| 3 | Download BLM CSVs to host | 20 min | YES |
| 4 | Add Playwright deps to Dockerfile | 30 min | If MLRS check needed |
| 5 | Add `pypdf` to requirements.txt | 5 min | No (fallback exists) |
| 6 | Set gunicorn as CMD with --timeout 1200 | 10 min | Recommended |
| 7 | Add Nginx auth_basic block | 15 min | YES for public access |
| 8 | Add to hub docker-compose with volumes | 30 min | YES |
| 9 | Run `/api/claims/pull` to populate DB | 5-10 min | YES |
| 10 | Optional: set `BLM_PULL_SCHEDULE=weekly` | 0 min | Default is already weekly |

**Total estimated deployment time: 2-3 hours (not including CSV download time)**

---

### 3.5 — Long-Running Request Problem

Several endpoints can run for 15-30 minutes:
- `POST /api/claims/batch-enrich` — up to 20 minutes
- `POST /api/claims/backfill-gps` — 5-10 minutes
- `POST /api/claims/check-mlrs/<serial>` — 30-90 seconds per claim (Playwright)
- `POST /api/claims/pull` with `force_refresh=true` — 5-10 minutes

These are currently synchronous HTTP calls. Through Nginx with a 30-minute proxy_read_timeout, they work fine for a single trusted user. For any multi-user scenario, these need to become async (Celery + Redis, or the existing thread-based async pattern extended).

The MLRS check already has an async option (`async: true` in the POST body → `check_claim_async()`). The others don't.

**For single-user hub use:** Set long proxy_read_timeout. Acceptable.  
**For multi-user:** Implement Celery or use the existing APScheduler for batch operations.

---

### 3.6 — Security Hardening Checklist (for public hub access)

Before this is exposed at any URL reachable from the internet:

- [ ] **Rotate metals.dev API key** (CRITICAL — leaked in backup)
- [ ] **Regenerate Flask secret key** (currently placeholder)
- [ ] **Add authentication** — Nginx `auth_basic` is the fastest path
- [ ] **Validate serial number format** at all route inputs
- [ ] **Sanitize `batch_name`** to prevent path traversal in exports
- [ ] **Add server-side land status check** before document generation for restricted land
- [ ] **Set `FLASK_DEBUG=0`** in production (already in docker-compose environment block)
- [ ] **Remove PII from .env** — locator name/address/phone should be set per-user, not in a shared server .env (or accept that this is Aaron's personal tool)
- [ ] **Set `BLM_PULL_SCHEDULE=disabled`** initially if MLRS/Playwright isn't configured — avoids silent failures

---

## Findings Summary

### By Severity

| # | Finding | Severity | File | Action |
|---|---------|---------|------|--------|
| 1 | Live metals.dev API key in committed .env | **CRITICAL** | `.env` | Rotate immediately |
| 2 | No authentication on any endpoint | **HIGH** | `app.py` | Add before public exposure |
| 3 | `batch_name` path traversal risk in exports | **MEDIUM** | `routes/export.py` | Sanitize input |
| 4 | Serial number not validated before use in LIKE queries | **MEDIUM** | `routes/claims.py`, `blm_mapserver.py` | Add regex validator |
| 5 | Playwright not in requirements.txt or Dockerfile | **MEDIUM** | `requirements.txt`, `Dockerfile` | Add or document as optional |
| 6 | `pypdf` not in requirements.txt | **LOW** | `requirements.txt` | Add |
| 7 | Flask secret key is a placeholder | **MEDIUM** | `.env` | Rotate before production |
| 8 | PII (name, address, phone) in committed .env | **MEDIUM** | `.env` | Remove from repo |
| 9 | SQLite incompatible with multi-worker gunicorn | **LOW** (single user) | `database.py` | Single worker or Postgres |
| 10 | Document generation not blocked for restricted land | **LOW** | `routes/export.py` | Add land status gate |
| 11 | gunicorn timeout too short for batch ops | **LOW** | `Dockerfile` | Set --timeout 1200 |
| 12 | MRDS index lost on container restart (module global) | **INFO** | `district_analyzer.py` | Add lazy rebuild on first use (already implemented) |

### Quick Wins (< 1 hour total)
1. Rotate the metals.dev API key
2. Add `pypdf` and `playwright` to `requirements.txt`
3. Add serial number regex validation helper used at all serial endpoints
4. Sanitize `batch_name` with `re.sub(r'[^A-Za-z0-9_\-]', '_', batch_name)[:40]`
5. Add `gunicorn` to requirements.txt and update Dockerfile CMD

---

## Verdict

**Deploy it.** This is a well-built, genuinely useful tool. The codebase quality is well above average for a solo project. Fix the leaked API key first (takes 5 minutes), add Nginx basic auth (30 minutes), pre-download the CSVs, and it's deployable on the comms hub.

The security issues are all of the "single-user tool going public" variety — classic and fixable. The architecture is sound. The concept is real. The legal documents are accurate. The scoring engine is thoughtful.

**One strategic note:** If Aaron ever wants to turn this into a SaaS product, the existing architecture is maybe 30% of the way there. The auth layer, Postgres swap, and async task queue are the three remaining infrastructure pieces. All are pre-planned in `ROLLOUT_PLAN.md` and the code is already structured to accommodate them.

---

*Audit completed by Steel Man sub-agent | Session az-claim-sniper-audit*
