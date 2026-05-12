# Track B — Scope-Integrity Note (Guardrails Before Fixing)
**Scope:** OmniPools Calculator Track B (Intake Trigger Chain + Jurisdiction). Empiricus confirmed: **DEF-TB-001** (jurisdiction/locality trust-break) and **DEF-TB-002** (manual correction silently overwritten by CRM re-parse).

**Constraint:** Identify traps only (no fixes / no new workstreams).

---

## 1) Likely places old defects get re-imported during Track B fixes

### 1.1 Session/state loss class regressions (Track-A “state loss”)
**Risk:** Track B changes to trigger-chain logic accidentally reintroduce “data disappears / resets on reload” by writing the wrong thing to the canonical localStorage key, or by saving defaults over real intake.

**High-signal code anchors:**
- `src/hooks/useIntake.ts`
  - Auto-save path (`debouncedSaveIntake(intake, ...)`) includes a **factory-default overwrite guard** (comment references `DEF-A03`). Touching init/load/autosave conditions is a common way to regress state loss.
  - Cross-page sync writes a subset to **`omni-intake-cross-page`** and explicitly warns: **do not write partial objects to `omni-intake-v1`**.
- `docs/INTAKE_SOURCE_OF_TRUTH.md` (rule): only Intake writes persistence; downstream tabs read via selectors.

**Why it matters to Track B:** a “jurisdiction doesn’t stick” symptom can actually be a state-reset/persistence regression.

---

### 1.2 Address component handling regressions (Track-A “city/state/zip stripping”)
**Risk:** Jurisdiction/locality fixes tempt developers to “simplify” address handling; that can resurrect stripping/formatting failures and break geocode fallbacks.

**High-signal anchors:**
- `src/lib/intake/selectors.ts` → `selectResolvedLocation()` builds canonical `address` from `clientInfoOverrides.street/city/state/zip`.
- `src/components/intake/ParsedClientInfo.tsx` displays the Project Address input as **`overrides.street`** (so street-only can *look* like “city/state/zip stripped” even if canonical address is intact elsewhere).
- `supabase/functions/geocode-address/index.ts` → `stripCityFromAddress()` (DEF-005 retry) assumes a comma-separated address form; nonstandard/duplicated component formats will silently reduce retry success.

---

## 2) Where we could fool ourselves (false confidence / untested assumptions)

### 2.1 UI statuses can be “green” while canonical state is wrong
**Risk:** Multiple parse/status enums and multiple ingestion paths make it easy to believe the chain is correct when the canonical store never received the field.

**Anchors:**
- `src/hooks/useIntake.ts` uses `crmStatus` values like `'success'|'parsing'|'idle'|'error'`.
- `src/hooks/useIntakeIngestion.ts` defines `ParseStatus = 'idle'|'parsing'|'complete'|'error'`.
- `src/components/tabs/IntakeTab.tsx` imports `ParseStatus` from `useIntakeIngestion` and checks `crmStatus === 'complete'` in UI branches.

**False-positive mode:** badge/health panel indicates “complete”, but the values used by selectors (permit/export) are not written.

---

### 2.2 There are 3 overlapping CRM/address/jurisdiction pipelines
**Risk:** Fixing one path won’t fix production if another path is what fires later (auto-effects).

**Anchors:**
- `src/hooks/useIntake.ts` (CRM parse + auto-reparse + auto-geocode)
- `src/hooks/useIntakeIngestion.ts` (CRM parse + optional geocode)
- `src/hooks/useSiteIntelligence.ts` (also calls `parse-crm-notes` and `geocode-address`)

**False-positive mode:** a manual-edit test passes immediately, then auto-reparse later reverts it.

---

## 3) Hidden assumption traps in jurisdiction resolution & CRM re-parse

### 3.1 “Jurisdiction” ≠ mailing city
**Risk:** DEF-TB-001 can be “fixed” incorrectly by forcing jurisdiction to match typed city. In AZ, mailing city, incorporated place, CDP, and county subdivision can differ.

**Anchor:** `supabase/functions/geocode-address/index.ts` → `geocodeWithCensusGeographies()` selects jurisdiction from:
- `Incorporated Places` → `Census Designated Places` → `County Subdivisions`.

**Guardrail:** treat a mismatch as a *data provenance problem*, not automatically a geocoder bug.

---

### 3.2 Manual jurisdiction selection currently does not feed canonical downstream reads
**Risk:** Even if the designer picks a jurisdiction in the dropdown, reports/permit exports may ignore it.

**Anchors:**
- `src/components/intake/ParsedClientInfo.tsx` writes jurisdiction to `clientInfoOverrides.jurisdiction`.
- `src/lib/intake/selectors.ts` → `selectResolvedLocation()` sets `jurisdiction` from `siteIntelligenceReport.location.jurisdiction` (ignores `clientInfoOverrides.jurisdiction`).

**Failure mode:** “We fixed the dropdown” but permit packet still uses site-intel jurisdiction.

---

### 3.3 DEF-TB-002 is strongly consistent with a stale-closure overwrite
**Risk:** CRM re-parse overwrites manual corrections because the CRM parse callback reads stale `intake`.

**Anchor (high confidence):**
- `src/hooks/useIntake.ts` → `parseCRM` is declared `useCallback(..., [])` but reads `intake.clientInfoOverrides` to decide whether to auto-fill:
  - `const hasExistingOverride = intake.clientInfoOverrides?.street;`
- CRM auto-reparse effect later calls `parseCRM(currentText)` after a debounce.

**Failure mode:** manual correction appears to stick, then reverts when the debounced CRM re-parse runs.

---

### 3.4 coordSource gaps can re-open the DEF-001-class overwrite (reverse geocode mutating canonical address)
**Risk:** Any path that sets coordinates without setting `coordSource` appropriately can cause reverse-geocode to run and overwrite `street` with a normalized `formattedAddress`.

**Anchors:**
- `src/components/intake/ParsedClientInfo.tsx` reverse-geocodes when `overrides.latitude/longitude` exist unless `coordSource === 'forward-geocode'`.
- `src/hooks/useIntake.ts` `retryGeocoding()` sets `coordSource: 'forward-geocode'` when it writes lat/lng.

---

## 4) Code-level “do not step here” warnings (small changes, big regressions)

1. **Do not collapse address into a single string** without auditing all of:
   - `selectResolvedLocation()` composition rules
   - `ParsedClientInfo` display precedence (`overrides.street`)
   - `stripCityFromAddress()` retry assumptions

2. **Do not “sync jurisdiction” by blindly copying** `siteIntelligenceReport.location.jurisdiction` into overrides (or vice versa) without explicit precedence, or you will recreate DEF-TB-002-style silent overwrites.

3. **Any Track B work inside `useIntake.ts` effects is high-risk** (auto-geocode + auto-reparse are effect-driven). A dependency/guard tweak can create repeated geocoding, repeated clearing of auto fields, or delayed overwrites.

4. **Watch parsing shape drift:** `supabase/functions/parse-crm-notes/index.ts` returns `{value, confidence}` objects (ExtractedClientData). Multiple front-end callers expect different shapes (`useSiteIntelligence.ts` expects `clientName/projectAddress`, while Intake UI components expect `data.client/address/...`). Jurisdiction bugs can be “just” a shape mismatch.

---

## Bottom-line guardrail
Track B defects sit in a reactive chain (CRM → Project Address → geocode → site intel → jurisdiction). The primary integrity risk is **writes happening from the wrong place or at the wrong time** (auto-effects + stale state + multiple pipelines) that silently mutate canonical fields.
