# Track C Field-Meaning Research Packet — Top 10

**Date:** 2026-03-14  
**Author:** Researcher  
**Source spine:** TRACK_C_FIELD_AUDIT.md (Plato, 34 defects) + TRACK_C_EXTRACTION.md (full inventory)  
**Scope:** Top 10 highest-impact field-meaning problems with external language, examples, and clarification recommendations

---

## 1. Main Drain Run (ft) — DEF-C01

**Definition:** The length of pipe from the main drain fitting at the pool floor to the equipment pad, measured along the actual trench path (not straight-line).

**Why it matters downstream:** Directly feeds friction loss calculation → Total Dynamic Head (TDH) → pump sizing and energy cost. Every 10 ft of 2" pipe at 60 GPM adds roughly 1.5–2 ft of head loss. Wrong input here cascades into oversized or undersized pumps.

**Clearer label/help-text:** `Main Drain Run (ft) — Pipe distance from pool main drain to equipment pad. Measure along the trench, not straight-line. Affects pump sizing.`  
**Example:** "If the trench runs 20 ft from the deep end, turns a corner, then goes 15 ft to the pad, enter 35 ft."

**Misunderstanding risk:** Designers confuse trench-path length with straight-line distance, underreporting by 20-40%, which underestimates friction loss and produces falsely optimistic pump sizing.

---

## 2. Equipment Distance (ft) — DEF-C04

**Definition:** The distance from the nearest pool wall to the equipment pad. Serves as the fallback base distance for all pipe run estimates when specific pipe runs are left blank.

**Why it matters downstream:** When individual pipe runs (main drain, skimmer, return) aren't entered, this single number drives ALL friction loss estimates. It's the silent default seed for the entire hydraulic model.

**Clearer label/help-text:** `Equipment Pad Distance (ft) — Distance from the nearest pool wall to the equipment pad. Used as the default pipe run estimate when specific runs aren't entered.`  
**Example:** "Stand at the closest edge of the pool shell. Measure to the center of your equipment pad. Enter that number."

**Misunderstanding risk:** Without origin/destination guidance, designers measure from arbitrary points (center of pool, far wall, property line), producing distances off by 2–3x.

---

## 3. Property Square Footage — DEF-C09

**Definition:** The conditioned living area (square footage) of the home on the property. Used to estimate the home's existing electrical demand via industry-standard load calculation (NEC Article 220).

**Why it matters downstream:** Determines whether the existing electrical panel has enough spare capacity for pool equipment without a service upgrade. A 2,500 sq ft home draws roughly 30–40A baseline; a 5,000 sq ft home draws 60–80A. The gap between that baseline and the panel rating is the budget available for pool loads. Wrong square footage → wrong spare-capacity estimate → missed upgrade requirement or unnecessary upgrade recommendation.

**Clearer label/help-text:** `Home Square Footage — Conditioned living area of the home. Used to estimate existing electrical load and determine whether the panel has capacity for pool equipment.`  
**Example:** "Use the livable area from the county assessor or real estate listing (e.g., 2,400 sq ft). Don't include garage, covered patio, or detached structures."

**Misunderstanding risk:** Designers enter lot size or total property acreage instead of conditioned living area, inflating baseline load estimates by 3–10x and triggering false panel-upgrade warnings.

---

## 4. Site Conditions — Solar Blanket — DEF-C11

**Definition:** Whether the pool uses a solar blanket/cover, and how frequently. Options are: none, night only, day and night. A solar blanket is a floating cover (bubble wrap-like) that reduces evaporative and radiative heat loss from the water surface.

**Why it matters downstream:** A solar blanket can reduce overnight heat loss by 50–70% (NREL and DOE studies confirm 50–70% evaporation reduction). This makes it one of the single highest-impact variables in the heating cost model — more impactful than heater efficiency differences. Skipping it because the section says "Optional" produces a worst-case heat-loss estimate that may oversize heater recommendations and overstate operating costs by hundreds of dollars per season.

**Clearer label/help-text:** `Solar Blanket — Does the pool use a solar cover? A blanket can cut heat loss by up to 70% and dramatically changes heating cost estimates. Select usage pattern for accurate results.`  
**Example:** "If the homeowner pulls a bubble cover on every evening and removes it in the morning, select 'Night Only.'"

**Misunderstanding risk:** Labeled "Optional" with no impact indication, so designers skip it by default, producing dramatically inflated heating cost projections that may lose bids or misguide heater selection.

---

## 5. Site Conditions — Wind Exposure — DEF-C12

**Definition:** The degree to which the pool is exposed to wind. Options: sheltered, normal, exposed. Wind drives evaporative heat loss — the dominant heat loss mechanism for uncovered outdoor pools.

**Why it matters downstream:** Evaporation accounts for 70%+ of total pool heat loss (DOE data). Wind speed multiplies the evaporation rate. Moving from "sheltered" (walled courtyard) to "exposed" (open lot, hilltop) can increase heating costs by 30%+ for the same pool. This variable shifts the entire cost comparison between heater options.

**Clearer label/help-text:** `Wind Exposure — How sheltered is the pool from wind? Wind is the #1 driver of heat loss. Sheltered = enclosed yard, block walls, dense landscaping. Exposed = open lot, hilltop, no windbreaks. Affects heating cost by 30% or more.`  
**Example:** "Typical Arizona backyard with 6 ft block walls = Sheltered. New subdivision with no fencing yet = Exposed."

**Misunderstanding risk:** Without magnitude context, designers treat this as trivial cosmetic input, but it can swing heating cost estimates by more than the efficiency difference between heater brands.

---

## 6. Site Conditions Section Badge: "Optional" — DEF-C10

**Definition:** The section-level badge on the Site Conditions group (Solar Blanket + Wind Exposure). Currently displays "Optional."

**Why it matters downstream:** The badge governs designer behavior at the section level. "Optional" in UX convention means "skip if you're in a hurry." But Solar Blanket and Wind Exposure together can swing results by 30–70%. The badge creates a perverse incentive: the highest-impact optional inputs are the ones most likely to be skipped.

**Clearer label/help-text:** Badge: `Optional — High Impact` or `Recommended`. Section subtitle: `These settings are optional but significantly affect results. A solar blanket alone can reduce estimated heating costs by up to 70%.`  
**Example (industry parallel):** Energy auditing tools (e.g., HERS rating software, BEopt) label similar inputs as "Defaults assumed — override for accuracy" rather than "Optional."

**Misunderstanding risk:** "Optional" reads as "unimportant" in every UI convention; the actual impact (30–70% swing) contradicts the signal the badge sends.

---

## 7. Calculation Mode — DEF-C13

**Definition:** Selects the pump operating scenario for the hydraulic analysis. Options include Circulation (daily), Cleaning (in-floor), Spillover (spa overflow), and Jet Mode (therapy jets). Each mode models different flow rates and system behavior.

**Why it matters downstream:** Each mode implies a different target flow rate and system resistance profile. "Circulation" might target 40–60 GPM; "Jet Mode" might require 120+ GPM. Selecting the wrong mode produces TDH and pump sizing for a scenario the designer didn't intend.

**Clearer label/help-text:** `Operating Mode — Select the pump duty you want to analyze. Each mode models a different flow rate and system behavior.`  
Options should read: `Daily Circulation`, `In-Floor Cleaning`, `Spa Spillover`, `Therapy Jets`.  
**Example:** "To size the pump for everyday filtration, pick 'Daily Circulation.' To check whether the pump can handle spa jets, switch to 'Therapy Jets.'"

**Misunderstanding risk:** "Calculation Mode" sounds like a math precision toggle (like "simple vs. advanced"), not a physical operating scenario selector — designers may never change it.

---

## 8. Return Loop (ft) — DEF-C03

**Definition:** The total length of pipe for the return line from the equipment pad, around the pool perimeter, and back. Represents the longest single pipe run in most pool plumbing systems.

**Why it matters downstream:** The return loop is typically the highest friction-loss pipe run because it's the longest. Underestimating it has the largest single-field impact on TDH accuracy. The existing tooltip ("Perimeter + equipment distance") gives a formula instead of a measurement instruction, so designers don't know if they should measure pipe or calculate from two other numbers.

**Clearer label/help-text:** `Return Loop (ft) — Total pipe length from the equipment pad, around the pool, and back. If you haven't run the pipe yet, estimate as pool perimeter + 2× equipment pad distance. Longest pipe run = biggest friction loss impact.`  
**Example:** "Pool perimeter is 120 ft, pad is 25 ft from the pool → estimate 120 + 50 = 170 ft."

**Misunderstanding risk:** Designers read the formula tooltip literally and enter perimeter alone (missing the equipment distance), underreporting by 20–40 ft.

---

## 9. Distance from Gas Meter (ft) — DEF-C15

**Definition:** The pipe distance from the natural gas (or propane) meter to the pool heater location. Determines required gas pipe diameter per fuel gas code tables (IFGC / NFPA 54).

**Why it matters downstream:** Gas pipe sizing is distance-dependent. A 400,000 BTU heater on natural gas at 20 ft may need 1" pipe; at 80 ft it may need 1.25" or larger. Undersized gas pipe = low gas pressure = heater malfunction, error codes, or failure to ignite. This is a code-compliance and safety issue, not just a performance concern.

**Clearer label/help-text:** `Distance from Gas Meter (ft) — Pipe distance from the gas meter (or planned meter location for new construction) to the pool heater. Longer distances require larger pipe to maintain adequate gas pressure. Measure along the planned pipe route, not straight-line.`  
**Example:** "Gas meter is on the side of the house, heater is in the backyard. Pipe runs 15 ft along the house, turns the corner, goes 30 ft to the pad = 45 ft."

**Misunderstanding risk:** "Meter" is ambiguous (gas vs. electric), and designers on new construction with no meter yet don't know what reference point to use — leading to omission or wild guesses.

---

## 10. Pipe Run Distances Section — "Optional" Framing — DEF-C22

**Definition:** The collective treatment of all 7 pipe run distance fields (Main Drain, Skimmer, Return Loop, Equipment Distance, Infloor Gearbox, Water Feature, Spa Main Drain) as "optional" with no indication that defaults are being silently substituted.

**Why it matters downstream:** When designers skip pipe runs, the system uses Equipment Distance and pool size to estimate them. But there's no indication that (a) defaults are being used, (b) what the defaults are, or (c) how much accuracy degrades. Designers assume their TDH number is based on real measurements when it's based on estimates-of-estimates.

**Clearer label/help-text:** Section note: `Pipe run distances are optional but directly affect TDH accuracy. If left blank, estimates are based on Equipment Pad Distance and pool size. Enter actual measurements for best results.`  
When defaults are used, show inline indicator: `"Using estimate"` next to the TDH result, or `"Based on X of 7 pipe runs entered"` as a confidence signal.  
**Example (industry parallel):** HVAC load calculation tools (Manual J) show "default assumed" flags on any input the user didn't explicitly set, with a confidence grade on the final result.

**Misunderstanding risk:** Silent default substitution creates false precision — the TDH output looks authoritative whether it's based on 7 real measurements or 0.

---

## Top 5 Immediate Clarification Priorities (Ranked)

| Rank | Field/Issue | Why First |
|------|-------------|-----------|
| **1** | **Site Conditions section badge "Optional" + Solar Blanket + Wind Exposure** (DEF-C10/C11/C12) | Three fields, one section. Combined swing of 30–70% on heating cost output. Current "Optional" badge actively drives users to skip the highest-impact inputs. Fix is badge text + two tooltips — low effort, massive accuracy gain. |
| **2** | **Property Square Footage** (DEF-C09) | Most confusing "why is this here?" moment in the app. Designers enter lot size or skip it entirely. Triggers false panel-upgrade warnings or missed upgrades. One tooltip explaining the NEC load connection fixes it. |
| **3** | **All Pipe Run Distances — silent default substitution** (DEF-C22 + DEF-C01 through C07) | Systemic: 7 fields with same problem. Designers don't know defaults exist, what they are, or that results degrade. A section note + "using estimate" indicator eliminates false precision. One pattern fix, seven fields corrected. |
| **4** | **Equipment Distance (ft)** (DEF-C04) | The silent seed value for all pipe-run defaults. If this one field is wrong, every unfilled pipe run inherits the error. Origin/destination must be specified. |
| **5** | **Calculation Mode → Operating Mode rename** (DEF-C13) | Designers never change it because the label sounds like a math toggle. Rename to "Operating Mode" or "Pump Duty" + clarify that it selects physical scenarios. Label change only — zero logic impact. |

---

*Packet complete. 10 fields analyzed. 5 priorities ranked. No code changes. No philosophy. Ready for Track C consumption.*
