# Geocoder Alternatives Research Report
**Date:** 2026-03-26  
**Priority:** HIGH  
**Context:** Census Bureau geocoder returned completely wrong address for a real OmniPools customer job (5059 N Wild Life Dr, Tucson AZ 85745 → mismatched to 4828 W Condor Dr, 85742). Production failure.

---

## 1. Census Bureau Geocoder — Known Limitations

### Why It Returned a Wrong Address
The Census geocoder uses **TIGER/Line address range interpolation**, NOT a database of actual addresses. Here's what that means:

- **Address ranges, not real addresses:** TIGER stores address ranges per street segment (e.g., "100–200 N Main St"). It includes *all possible* structure numbers even if no building exists there.
- **Fuzzy matching with threshold scoring:** When an exact match isn't found, it matches to the nearest street segment that meets a score threshold. This is how "Wild Life Dr" got matched to "Condor Dr" — the geocoder found a "close enough" segment in a different part of Tucson.
- **Interpolated coordinates:** Even when matching the right street, coordinates are estimated by interpolating along the centerline. Rural/suburban addresses with long driveways or irregular lots can be off by hundreds of meters.
- **No confidence differentiation:** The geocoder returns "Match" without indicating *how* confident it is. A 60% fuzzy match and a 99% exact match both come back as "Match."

### Known Failure Modes
| Failure Type | Frequency | Our Risk |
|---|---|---|
| **Wrong street match** (our bug) | Uncommon but devastating | **HIGH** — confirmed in production |
| No match returned | Common for new/rural addresses | Medium — handled by fallback chain |
| Right street, wrong location | Very common in rural areas | Medium — off by 50-500m |
| Outdated address data | Ongoing (TIGER updated annually) | Medium — new subdivisions missing |

### Root Cause for Our Bug
The Census geocoder matched "5059 N Wild Life Dr, Tucson, AZ 85745" to a *different street entirely*. This happens because:
1. "Wild Life Dr" may not be in the TIGER address range file (newer/smaller street)
2. The fuzzy matcher found "Condor Dr" in 85742 as the "best" match above threshold
3. The geocoder returned this wrong match with no indication it was uncertain

**This is the worst failure mode** — silent wrong data is worse than no data.

---

## 2. Alternative Geocoding Services Comparison

### Free/Low-Cost Options

| Service | Free Tier | Rate Limit | Data Source | AZ Accuracy | API Complexity | Key Limitation |
|---|---|---|---|---|---|---|
| **Pima County GIS** ⭐ | Unlimited (public) | Unknown/generous | County parcel data | **EXCELLENT** for Pima County | Simple REST (ArcGIS) | Pima County only |
| **Maricopa County GIS** | Unlimited (public) | Unknown/generous | County parcel data | **EXCELLENT** for Maricopa | Simple REST (ArcGIS) | Maricopa County only |
| **Nominatim (OSM)** | Unlimited (self-host) / 1 req/s (public) | 1 req/s | OpenStreetMap | Good for cities, weak rural | Simple REST | No commercial use on public instance; attribution required |
| **Photon (Komoot)** | Unlimited (public demo) | "Reasonable" | OpenStreetMap | Same as Nominatim | Simple REST | Unclear commercial policy; no SLA |
| **LocationIQ** | 5,000/day | 2 req/s | OSM + proprietary | Good | Simple REST | Attribution link required on free tier |
| **Geocodio** | 2,500/day | Standard | Multiple US sources | **Very Good** — rooftop when available | Simple REST | US/Canada only (fine for us) |
| **Google Geocoding** | 10,000/month free (post-March 2025) | 50 req/s | Google | **Best in class** | Moderate | Must use with Google Maps; can't store coordinates |
| **OpenCage** | 2,500/day | 1 req/s | OSM + other | Good | Simple REST | Free tier is testing only |
| **HERE** | 1,000/day (limited), 30K/mo (base) | 5 req/s | HERE | Very Good | Moderate | Attribution required |
| **Mapbox** | 100,000/month | Standard | Mapbox + OSM | Good | Moderate | Storage costs extra |
| **TomTom** | 2,500/day | 5 req/s | TomTom | Good | Simple REST | EU-focused |

### Detailed Notes on Top Candidates

#### ⭐ Pima County GIS Geocoder (VERIFIED WORKING)
- **Endpoint:** `https://pimamaps.pima.gov/pmgp/rest/services/Locators/Composite_ParStr_Locator/GeocodeServer/findAddressCandidates`
- **I tested the failing address and it WORKS:**
  ```
  Address: "5059 N WILD LIFE DR"
  Score: 82.86
  Coordinates: -111.0486, 32.2984 (WGS84)
  ```
- Uses actual **parcel/street data** from the county assessor — not TIGER interpolation
- Returns match score so we can reject low-confidence results
- Supports `outSR=4326` parameter for standard lat/lng output
- **No API key needed. No rate limit posted. Public ArcGIS REST endpoint.**
- Coverage: All of Pima County (Tucson, Oro Valley, Marana, Sahuarita, Green Valley)

#### Maricopa County GIS Geocoder
- **Endpoint:** `https://gis.maricopa.gov/arcgis/rest/services/Geocode/MaricopaCountyGeocodeService/GeocodeServer`
- Same ArcGIS REST pattern as Pima County
- Covers Phoenix metro and surroundings
- Haven't verified yet but endpoint is live

#### Geocodio ($0 for 2,500/day)
- Rooftop-level accuracy when available, with fallback to street-level
- Returns accuracy type indicator (rooftop / range / centroid / place)
- No attribution requirements, no usage restrictions on stored data
- US & Canada focused — perfect for our use case
- Simple REST API, well-documented

#### LocationIQ ($0 for 5,000/day)  
- OSM-based but with proprietary enhancements
- 5K free requests/day is generous for our volume
- Requires attribution link (acceptable for backend use? Check TOS)
- Better than raw Nominatim for commercial use

#### Google Geocoding (10K free/month)
- Best accuracy, period. Rooftop-level for most US addresses.
- Post-March 2025: 10,000 free requests/month (Essentials tier, no $200 credit)
- **Restriction:** Cannot store coordinates without displaying on Google Maps
- For a Supabase edge function, this restriction is problematic
- $5/1,000 requests after free tier

---

## 3. AZ-Specific Public GIS Endpoints

### Confirmed Working

| County | Geocoder Endpoint | Status |
|---|---|---|
| **Pima County** | `https://pimamaps.pima.gov/pmgp/rest/services/Locators/Composite_ParStr_Locator/GeocodeServer/findAddressCandidates` | ✅ Verified — returns correct coordinates for our failing address |
| **Maricopa County** | `https://gis.maricopa.gov/arcgis/rest/services/Geocode/MaricopaCountyGeocodeService/GeocodeServer` | ✅ Endpoint exists — needs testing |

### API Call Format (Pima County Example)
```
GET https://pimamaps.pima.gov/pmgp/rest/services/Locators/Composite_ParStr_Locator/GeocodeServer/findAddressCandidates
  ?Address=5059+N+Wild+Life+Dr
  &City=Tucson
  &State=AZ
  &Zip=85745
  &outSR=4326
  &f=json
```

Response includes:
- `candidates[].address` — matched address string
- `candidates[].location.x` / `.y` — longitude/latitude (with outSR=4326)
- `candidates[].score` — match confidence (0-100)

### Not Yet Found
- City of Tucson: Has open data portal (gisdata.tucsonaz.gov) but no public geocoding endpoint found
- Other AZ counties: Would need to search individually
- Arizona State: No statewide geocoding service found

---

## 4. Recommended Fallback Chain

### For OmniPools (Pima County focus, $0 budget)

```
1. Pima County GIS Geocoder     → Best: parcel-level data, score > 80 = high confidence
   ↓ (if no match or score < 70)
2. Geocodio (free tier)          → Good: rooftop accuracy, 2,500/day
   ↓ (if no match)
3. Nominatim / Photon            → OK: OSM data, free, decent urban coverage
   ↓ (if no match)  
4. Census Bureau (current)       → Last resort: ONLY if score validation added
   ↓ (if no match or wrong-address detected)
5. FAIL → flag for manual geocoding
```

### Key Implementation Changes

1. **Add Pima County GIS as PRIMARY geocoder** — it's free, uses real parcel data, and correctly handles the address that broke us.

2. **Add Geocodio as secondary** — 2,500 free/day is plenty for OmniPools volume. Returns accuracy type so we know when it's guessing.

3. **Keep Census as last resort BUT add validation:**
   - Compare returned street name against input street name (fuzzy match)
   - If returned address doesn't match input street → reject, don't use
   - This would have caught the Wild Life Dr → Condor Dr mismatch

4. **Add match score thresholds:**
   - Pima County: Accept if score ≥ 70, prefer ≥ 80
   - Census: Accept only exact matches (matchedAddress contains input street)
   - All: Log match quality for monitoring

### If Budget Opens Up Later
- **Google Geocoding** at 10K free/month would be the most reliable primary geocoder
- **LocationIQ** at 5K free/day is solid middle ground
- **Geocodio paid** at $1/1,000 is the cheapest premium option

---

## 5. Immediate Action Items

| Priority | Action | Effort |
|---|---|---|
| **P0** | Add Pima County GIS geocoder as first in chain | ~2 hours |
| **P0** | Add street-name validation on Census results (reject mismatches) | ~1 hour |
| **P1** | Sign up for Geocodio free tier, add as secondary | ~1-2 hours |
| **P1** | Add Maricopa County geocoder (for eventual Phoenix coverage) | ~1 hour |
| **P2** | Add match confidence logging to all geocoder results | ~1 hour |
| **P2** | Evaluate LocationIQ free tier as Nominatim replacement | ~30 min |

### New Fallback Chain (Implementation)
```typescript
// Proposed geocoder priority for geocode-address/index.ts
const GEOCODER_CHAIN = [
  pimaCountyGeocoder,      // FREE, parcel-level, Pima County only
  // maricopaCountyGeocoder, // FREE, parcel-level, Maricopa County only (future)
  geocodioGeocoder,         // FREE 2,500/day, rooftop accuracy
  nominatimGeocoder,        // FREE, OSM data
  censusBureauGeocoder,     // FREE, TIGER — WITH street-name validation
];
```

---

## Sources
- Census Bureau Geocoder FAQ: https://www2.census.gov/geo/pdfs/maps-data/data/Census_Geocoder_FAQ.pdf
- Census Geocoder Documentation: https://www.census.gov/programs-surveys/geography/technical-documentation/complete-technical-documentation/census-geocoder.html
- Pima County GIS: https://gis.pima.gov/ / https://www.pima.gov/2015/Geocode-Addresses-in-ArcMap-Using-Our-Lo
- Maricopa County GIS: https://gis.maricopa.gov/arcgis/rest/services/Geocode/
- Geocodio comparison: https://www.geocod.io/compare-geocoding-services/
- Geocoding API pricing comparison: https://www.bitoff.org/geocoding-apis-comparison/
- Google Maps pricing (March 2025 changes): https://developers.google.com/maps/billing-and-pricing/faq
- LocationIQ pricing: https://locationiq.com/pricing
- Photon/Komoot: https://github.com/komoot/photon
