# DEF-TB-002 live production validation — 2026-03-20 11:12 MST

## Conclusion
- **DEF-TB-002 core fix:** ✅ PASS
- **Track A reload persistence check:** ❌ FAIL
- **Bundle hash expectation:** ❌ FAIL
- **Overall final gate status:** ❌ FAIL

## Scope
Validated **DEF-TB-002 only** on `https://omnipoolsaz.com/`.
Did **not** test DEF-TB-001 jurisdiction behavior beyond recording what the UI displayed during TB-002 flow.

## Test input
CRM note used:

```text
Lead: Maria Gonzalez
Phone: 520-555-1234
Email: maria.gonzalez@email.com
Project Address: 8880 N Camino Coronado, Tucson, AZ 85704
Notes: existing pool needs resurfacing
```

Manual correction used:

```text
4828 W Condor Dr, Tucson, AZ 85742
```

## Step-by-step results
1. **Open production site** — ✅ PASS
2. **Paste same CRM note** — ✅ PASS
3. **Auto-parse baseline populates correctly** — ✅ PASS  
   - Client Name: `Maria Gonzalez`
   - Phone: `520-555-1234`
   - Email: `maria.gonzalez@email.com`
   - Project Address: `8880 N Camino Coronado`
   - House Sq Ft: `1,052`
   - Year Built: `1953`
   - Lot Size: `3.54`
   - Lat/Lng: `32.368751`, `-110.984189`
4. **Manual Project Address change to 4828 W Condor Dr** — ✅ PASS
5. **Downstream propagation updates** — ✅ PASS  
   - Address: `4828 W Condor Dr, Tucson, AZ 85742`
   - House Sq Ft: `1,403`
   - Year Built: `1984`
   - Lot Size: `0.34`
   - Lat/Lng: `32.376255`, `-111.06802`
6. **Trigger CRM re-parse by re-pasting same CRM note** — ✅ PASS
7. **Critical check: manual correction preserved** — ✅ PASS  
   - Address remained `4828 W Condor Dr, Tucson, AZ 85742`
8. **Non-manually-edited fields still present/update from parser** — ✅ PASS  
   - Client Name / Phone / Email remained parser-populated
9. **Reload page and verify persistence** — ❌ FAIL  
   - After reload, live page returned blank intake fields instead of restoring the corrected state.

## Bundle hash
- DOM script: `/assets/index-z3_wuSFN.js`
- Fresh HTML fetch: `assets/index-z3_wuSFN.js`
- Expected by Aristotle: different from both `index-BvKGjMvX.js` and `index-z3_wuSFN.js`
- **Result:** ❌ still serving `index-z3_wuSFN.js`

## Notes
- The specific stale-closure symptom for **TB-002** is not reproducing now. Manual address correction survived re-parse.
- However, the requested **Track A reload persistence regression check** failed on live prod.
- Separately, prod bundle hash does not reflect a new deploy artifact.

## Artifact files
- JSON: `C:\Users\aaron\clawd-shared\governed-objects\DEF-TB-002-validation-2026-03-20T1112-MST.json`
- Source run output: `C:\Users\aaron\.openclaw\workspace\tmp_def_tb_002_validate_result.json`
