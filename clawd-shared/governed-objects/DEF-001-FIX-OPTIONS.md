# DEF-001 Fix Options — Normalized Labels

## Option A — Source-Tag Guard Fix (Plato implementation)
- Tag coordinate origin when written by forward geocode
- Prevent reverse geocode from firing on forward-geocode-written coords
- Breaks the double-geocode cycle at the source
- **No new UX required**
- Surgical guard fix — minimal surface area

## Option B — Explicit Normalization Review UX (future enhancement)
- Store normalized address separately
- Show resolved address with Accept / Keep Mine / Edit action
- Only implement if Empiricus proves it is necessary from designer perspective after Option A lands

## Decision (2026-03-09, Aaron)
**Proceed with Option A now.** Do not bundle Option B UX unless Empiricus proves it is needed post-fix.

## Status
| Date | Decision | By |
|------|----------|----|
| 2026-03-09 | Proceed Option A (source-tag guard). Option B deferred. | Aaron, routed by Aristotle |
