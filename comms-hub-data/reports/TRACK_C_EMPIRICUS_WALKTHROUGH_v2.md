# Track C Dumb-Designer Walkthrough — Live App vs Plato/Researcher

**Date:** 2026-03-15
**Auditor:** Empiricus
**Scope:** Track C only — live walkthrough of `https://omnipoolsaz.com`
**Reference inputs used:**
- `TRACK_C_FIELD_AUDIT.md` (Plato, DEF-C01–C34)
- `TRACK_C_FIELD_MEANING_TOP10.md` (Researcher)

## Method
I used the live app routes directly:
- `/hydraulics`
- `/pool-electrical-demand`
- `/heat-cost-calculator`

This is intentionally a **dumb-designer** read: what the interface says, what it makes me infer, and what I would likely do wrong if I were moving fast.

---

# 1) Hydraulics Calculator

## Section: Equipment Input

### Issue 1 — Equipment Input label is still a sentence, not a field name
1. **Field/section name:** Equipment Input → `Auto-filled from Intake or paste/type equipment list:`
2. **What I saw in the live app:** The field label is literally `Auto-filled from Intake or paste/type equipment list:` with Parse/Clear actions nearby.
3. **What confused me as a designer:** I do not know what “Intake” means, whether I am supposed to paste model numbers, a proposal, raw notes, or formatted equipment lines.
4. **What a designer would likely do wrong:** Paste messy text and assume the parser understands anything, then blame matching when it doesn’t.
5. **Severity:** MEDIUM
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C16**

**Live verdict:** **CONFIRMS Plato.**

---

## Section: Your Omni Build → Pool Stats / Features

### Issue 2 — Pool Perimeter still appears with no explanation of purpose or how to measure
1. **Field/section name:** `Pool Perimeter (ft)`
2. **What I saw in the live app:** The label appears bare. No inline explanation. No note about waterline measurement. No indication why hydraulics needs perimeter.
3. **What confused me as a designer:** Perimeter feels like a geometry field, not a hydraulics field. I would not naturally connect it to return-loop estimation.
4. **What a designer would likely do wrong:** Measure wrong reference line, skip it, or enter a rough number without realizing it affects pipe-length assumptions.
5. **Severity:** HIGH
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C08**

**Live verdict:** **CONFIRMS Plato** and **CONFIRMS Researcher’s framing that hidden dependency language matters**.

---

### Issue 3 — Therapy Jet Count tooltip is still plumber-facing, not designer-facing
1. **Field/section name:** `Therapy Jet Count`
2. **What I saw in the live app:** The only helper text is `~15 GPM per jet in jet mode`.
3. **What confused me as a designer:** That tells me a number, not what counts as a jet. Nozzle? body? pair? station?
4. **What a designer would likely do wrong:** Count the wrong thing and under/overstate jet demand.
5. **Severity:** MEDIUM
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C18**

**Live verdict:** **CONFIRMS Plato.**

---

## Section: Pipe Run Distances

### Issue 4 — Main Drain Run has no measurement instruction
1. **Field/section name:** `Main Drain Run (ft)`
2. **What I saw in the live app:** Bare label only.
3. **What confused me as a designer:** No source point, no destination, no clue whether to measure trench path or straight line.
4. **What a designer would likely do wrong:** Enter approximate deep-end-to-pad straight-line distance.
5. **Severity:** P0
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C01**

**Live verdict:** **CONFIRMS Plato** and **CONFIRMS Researcher**.

---

### Issue 5 — Skimmer Run has the same ambiguity
1. **Field/section name:** `Skimmer Run (ft)`
2. **What I saw in the live app:** Bare label only.
3. **What confused me as a designer:** Same problem as Main Drain Run: from where to where, and how exactly do I measure it?
4. **What a designer would likely do wrong:** Enter a guess based on pad distance or house setback.
5. **Severity:** P0
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C02**

**Live verdict:** **CONFIRMS Plato** and **CONFIRMS Researcher’s pattern diagnosis**.

---

### Issue 6 — Return Loop helper text is still a formula fragment, not actual guidance
1. **Field/section name:** `Return Loop (ft)`
2. **What I saw in the live app:** Helper text says `Perimeter + equipment distance`.
3. **What confused me as a designer:** I don’t know whether that is an estimate shortcut, a required formula, or a definition of what to measure.
4. **What a designer would likely do wrong:** Enter just perimeter, or enter a guessed loop length without understanding that this is the longest/highest-impact run.
5. **Severity:** P0
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C03**

**Live verdict:** **CONFIRMS Plato** and **strongly CONFIRMS Researcher**.

---

### Issue 7 — Equipment Distance is still ambiguous and undernamed
1. **Field/section name:** `Equipment Distance (ft)`
2. **What I saw in the live app:** Label remains `Equipment Distance (ft)`.
3. **What confused me as a designer:** Distance from what to what? Pool edge? centerline? pad front edge? equipment centroid?
4. **What a designer would likely do wrong:** Measure from an arbitrary point and unknowingly poison every fallback estimate downstream.
5. **Severity:** P0
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C04**

**Live verdict:** **CONFIRMS Plato** and **CONFIRMS Researcher’s point that this is the silent seed value**.

---

### Issue 8 — Infloor Gearbox Run helper text is still incomplete
1. **Field/section name:** `Infloor Gearbox Run (ft)`
2. **What I saw in the live app:** Helper text says `PVC to infloor gear box`.
3. **What confused me as a designer:** “PVC” is not a location. That helper text sounds like a fragment from an internal note, not user guidance.
4. **What a designer would likely do wrong:** Measure the wrong segment or ignore the field.
5. **Severity:** HIGH
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C05**

**Live verdict:** **CONFIRMS Plato.**

---

### Issue 9 — Water Feature Run helper text is still incomplete
1. **Field/section name:** `Water Feature Run (ft)`
2. **What I saw in the live app:** Helper text says `PVC to scupper/sheer/bubbler`.
3. **What confused me as a designer:** Again, not from where. It names a material and destination type, not an actual measured run.
4. **What a designer would likely do wrong:** Enter a feature offset instead of pipe route length.
5. **Severity:** HIGH
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C06**

**Live verdict:** **CONFIRMS Plato.**

---

### Issue 10 — Spa Main Drain Run still appears with no explanation
1. **Field/section name:** `Spa Main Drain Run (ft)`
2. **What I saw in the live app:** Label present, no helper text.
3. **What confused me as a designer:** Same ambiguity as the pool main drain field, but with even less guidance.
4. **What a designer would likely do wrong:** Guess, skip, or assume it is auto-derived from spa volume.
5. **Severity:** HIGH
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C07**

**Live verdict:** **CONFIRMS Plato.**

---

### Issue 11 — Pipe Run Distances still behave like “optional but silent-critical” inputs
1. **Field/section name:** `Pipe Run Distances` section
2. **What I saw in the live app:** No visible note about defaults, no confidence indicator, no “using estimate” language, no warning that leaving these blank degrades TDH quality.
3. **What confused me as a designer:** The section reads like optional refinement, not core hydraulic accuracy.
4. **What a designer would likely do wrong:** Skip most or all run fields and trust the output as if it were fully measured.
5. **Severity:** HIGH
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C22**

**Live verdict:** **CONFIRMS Plato** and **CONFIRMS Researcher**.

---

## Section: Omni Equipment

### Issue 12 — Calculation Mode still sounds like a settings/control label, not a physical scenario selector
1. **Field/section name:** `Calculation Mode`
2. **What I saw in the live app:** Label is still `Calculation Mode`; selected value shown as `Circulation (Daily)` with helper text `Standard daily operation ~60 GPM`.
3. **What confused me as a designer:** The selected option helps, but the label still sounds like “how the software calculates,” not “what operating condition you want to size for.”
4. **What a designer would likely do wrong:** Leave it on the default forever and never realize they are analyzing only one operating condition.
5. **Severity:** HIGH
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C13**

**Live verdict:** **Mostly CONFIRMS Plato.**

**Important nuance / mild contradiction:** The live option text is a little clearer than the audit implies because `Circulation (Daily)` + `Standard daily operation ~60 GPM` at least hints at a real scenario. The label is still wrong, but the current live state is slightly better than Plato’s description.

---

### Issue 13 — Mode availability is still silent/unexplained
1. **Field/section name:** `Calculation Mode` option behavior
2. **What I saw in the live app:** Feature toggles (`Has Spa`, `In-Floor System`, `Therapy Jets`, `Water Feature`) change what is visible elsewhere. There is no visible note telling the designer that these toggles also unlock different operating contexts/modes.
3. **What confused me as a designer:** If I don’t already know the calculator’s dependency tree, I won’t know why some operating choices appear or disappear.
4. **What a designer would likely do wrong:** Fail to enable the related feature and never discover the scenario they actually need.
5. **Severity:** MEDIUM
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C23**

**Live verdict:** **CONFIRMS Plato.**

---

## Section: Competitor Comparison

### Issue 14 — Competitor Comparison Mode is improved, but still not fully designer-native
1. **Field/section name:** `Competitor Comparison Mode`
2. **What I saw in the live app:** Options shown are `Calculated (physics-based)` and `Typical Install (field reality)`.
3. **What confused me as a designer:** This is somewhat better than the audit wording, but it still assumes I know what “physics-based” vs “field reality” means in practical sales/design terms.
4. **What a designer would likely do wrong:** Pick the one that sounds more official rather than the one matching the comparison they want to make.
5. **Severity:** MEDIUM
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C20**

**Live verdict:** **PARTIAL CONTRADICTION to Plato.** The live labels are already somewhat cleaner than Plato reported. The underlying confusion is still real because the concept framing is still insider-ish.

---

### Issue 15 — Competitor Pump Control is also somewhat improved, but still assumption-heavy
1. **Field/section name:** `Competitor Pump Control`
2. **What I saw in the live app:** Options shown are `Flow-based (like Pentair)` and `RPM-based (traditional)`.
3. **What confused me as a designer:** This is materially better than the audit wording, but I still have to know my competitor’s programming behavior to use it correctly.
4. **What a designer would likely do wrong:** Pick the familiar-sounding label, not the one that matches the actual competitor install style.
5. **Severity:** MEDIUM
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C21**

**Live verdict:** **PARTIAL CONTRADICTION to Plato.** The live labels are improved versus the audit description. The field is still not self-evident for a non-technical designer.

---

### Issue 16 — RPM default still looks like an unsupported magic number
1. **Field/section name:** `RPM:` with `(typical: 3100)`
2. **What I saw in the live app:** The UI literally shows `(typical: 3100)` next to RPM.
3. **What confused me as a designer:** Typical according to whom? market? installer? brand? region? This looks authoritative but not sourced.
4. **What a designer would likely do wrong:** Treat 3100 as gospel and use it in every comparison.
5. **Severity:** LOW
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C33**

**Live verdict:** **CONFIRMS Plato.**

---

# 2) Pool Electrical Demand Calculator

## Section: System Configuration / top-level experience

### Issue 17 — The route currently emphasizes downstream electrical outputs more than upstream meaning
1. **Field/section name:** Overall electrical flow
2. **What I saw in the live app:** The page leads strongly with matched equipment, load summary, breaker schedule, feeder recommendation, and permit summary. The visible top-level labels are things like `Controller`, `Heater`, `Panel Type`, `Main Feed Distance`, and `Feeder Voltage`.
3. **What confused me as a designer:** The calculator feels like it expects me to trust the machine-generated load stack rather than understand the few high-leverage inputs.
4. **What a designer would likely do wrong:** Skip verification of upstream assumptions because the output feels polished and official.
5. **Severity:** MEDIUM
6. **Cross-ref to Plato DEF-Cxx ID:** **Closest systemic match: DEF-C09, DEF-C14, DEF-C25**

**Live verdict:** **Partially confirms Plato’s broader concern about hidden meaning**, but the exact visible fields have diverged from the audit.

---

### Issue 18 — “Auto-filled from Intake…” is repeated here and still weak
1. **Field/section name:** Electrical → Equipment Input
2. **What I saw in the live app:** The same sentence-label pattern appears here: `Auto-filled from Intake or paste/type equipment list:`
3. **What confused me as a designer:** Same confusion as Hydraulics — vague source system, vague input format.
4. **What a designer would likely do wrong:** Paste inconsistent text and expect deterministic parsing.
5. **Severity:** MEDIUM
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C16 (same label pattern, different calculator context)**

**Live verdict:** **CONFIRMS the same naming problem pattern.**

---

### Issue 19 — Wire Run Distances parser input is clear enough technically, but still assumes jargon comfort
1. **Field/section name:** `Paste circuit run distances (used for voltage drop & wire sizing):`
2. **What I saw in the live app:** The label is functional, but still sentence-like and parser-centric.
3. **What confused me as a designer:** Better than some other labels, but still written like a power-user tool rather than a field instruction.
4. **What a designer would likely do wrong:** Paste notes with inconsistent circuit naming and assume the parser will resolve them cleanly.
5. **Severity:** LOW
6. **Cross-ref to Plato DEF-Cxx ID:** **No exact DEF-Cxx; live extra issue**

**Live verdict:** **New live issue not called out directly by Plato.**

---

## Section: Missing / contradictory electrical findings

### Issue 20 — Plato’s highest-priority electrical field is not visible in the current live route
1. **Field/section name:** `Property Square Footage` / `Home Square Footage`
2. **What I saw in the live app:** I did **not** encounter a visible field matching Plato’s documented `Property Square Footage` problem in the current live electrical route.
3. **What confused me as a designer:** The contradiction itself is confusing. Either the field moved, was removed from the primary route, or only appears in another state/view.
4. **What a designer would likely do wrong:** Miss a critical input entirely if it exists only in a hidden or alternate mode.
5. **Severity:** HIGH
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C09**

**Live verdict:** **CONTRADICTS Plato’s current-field-location claim.** I cannot confirm DEF-C09 from the present live route because the field was not visible.

---

### Issue 21 — Main Breaker Size field was also not visible where Plato said it would be
1. **Field/section name:** `Main Breaker Size (from panel label)`
2. **What I saw in the live app:** I did **not** encounter that visible field label in the current live route. I did see downstream outputs like `Main Breaker 70A` and `Panel Max 100A`, but not the specific upstream field Plato described.
3. **What confused me as a designer:** Same contradiction problem: either the route changed, the field is conditional, or the audit was based on another render/state.
4. **What a designer would likely do wrong:** Trust the visible panel summary without realizing a key assumption field exists elsewhere.
5. **Severity:** HIGH
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C14 / DEF-C25**

**Live verdict:** **CONTRADICTS Plato on current visible placement.** The concern may still exist, but not in the live view I reached.

---

# 3) Heat Cost Calculator

## Section: Route accessibility / first impression

### Issue 22 — The live Heat Cost route crashes before a designer can use it
1. **Field/section name:** Heat Cost route (`/heat-cost-calculator`)
2. **What I saw in the live app:** The page failed into an error boundary: `Something broke` / `Please refresh. If it keeps happening, screenshot this error.` Refresh did not recover it.
3. **What confused me as a designer:** Total dead end. I cannot even reach the fields Plato and Researcher audited.
4. **What a designer would likely do wrong:** Bounce out, stop trusting the tool, or assume their data/session caused it.
5. **Severity:** **P0**
6. **Cross-ref to Plato DEF-Cxx ID:** **No exact DEF-Cxx — live blocker they missed**

**Live verdict:** **New live issue missed by both Plato and Researcher.**

**Technical evidence observed in console:** repeated runtime error `A <Select.Item /> must have a value prop that is not an empty string`, caught by the app’s error boundary.

---

## Section: Heat Cost field-level findings

### Issue 23 — I could not validate Plato’s Heat Cost field defects because the route is not usable
1. **Field/section name:** Heat Cost field set broadly (Solar Blanket, Wind Exposure, Site Conditions, Equipment A/B, Starting Water Temperature, Utility Rates)
2. **What I saw in the live app:** I did not reach those fields live because the route crashed before rendering usable UI.
3. **What confused me as a designer:** The primary confusion is not label meaning — it is total unavailability.
4. **What a designer would likely do wrong:** Abandon the calculation or distrust the broader app.
5. **Severity:** P0
6. **Cross-ref to Plato DEF-Cxx ID:** **DEF-C10, DEF-C11, DEF-C12, DEF-C17, DEF-C27, DEF-C30 remain unverified live because of blocker**

**Live verdict:** **Neither confirmed nor contradicted at field level because the page is broken first.**

---

# Top 5 “designer would definitely get this wrong” moments

1. **`Equipment Distance (ft)`** — looks simple, but the origin/destination ambiguity makes it the easiest silent poison-pill input. (**DEF-C04**)
2. **`Return Loop (ft)` with `Perimeter + equipment distance`** — reads like a half-remembered formula, not a user instruction. (**DEF-C03**)
3. **Skipping Pipe Run Distances because they look optional** — the UI still does not signal how much trust should drop when these are blank. (**DEF-C22**)
4. **Leaving `Calculation Mode` on default forever** — the label still sounds like a software setting instead of a hydraulic scenario choice. (**DEF-C13 / DEF-C23**)
5. **Using the Heat Cost tool at all right now** — a designer would hit a route crash before ever getting to Solar Blanket / Wind Exposure. (**new live P0, missed in source docs**)

---

# Contradictions between app behavior and source-doc findings

## Contradiction 1 — Competitor labels are somewhat improved live
- **Plato said:** `Competitor Comparison Mode` and `Competitor Pump Control` were more engineer-speak than designer-speak.
- **Live app shows:**
  - `Calculated (physics-based)` / `Typical Install (field reality)`
  - `Flow-based (like Pentair)` / `RPM-based (traditional)`
- **My read:** Plato’s diagnosis still broadly holds, but the live labels are already partially cleaned up versus the audit text.

## Contradiction 2 — Property Square Footage was not visible where Plato reported it
- **Plato said:** This was a primary field-level defect in the electrical calculator. (**DEF-C09**)
- **Live app:** I did not encounter that field in the current visible electrical route.
- **My read:** Either the field moved, is conditional, or the audit captured another state/view. The live route does **not** currently present it in the obvious main flow I reached.

## Contradiction 3 — Main Breaker Size field was also not visible in the reported form
- **Plato said:** `Main Breaker Size (from panel label)` was a visible problematic label. (**DEF-C14 / DEF-C25**)
- **Live app:** I saw output summaries like `Main Breaker 70A`, but not the specific user-entry field/label Plato described.
- **My read:** Same state/version mismatch issue as above.

## Contradiction 4 — Heat Cost source docs assume field-level access; live app fails before that
- **Source docs focus:** field meaning defects in Heat Cost.
- **Live app reality:** the route crashes into an error boundary.
- **My read:** The source docs missed the more important live usability fact: **the page currently fails before a designer can even be confused by the fields.**

---

# Honest usability assessment

## Bottom line
**Hydraulics is usable but trust-fragile. Electrical is impressive-looking but meaning-light in the current visible flow. Heat Cost is currently broken hard enough to nullify field-copy analysis.**

## Plain-English assessment
- **Hydraulics:** I can get through it, but only if I already understand pool plumbing logic. A real designer moving fast would make several wrong assumptions from clean-looking but under-explained labels.
- **Electrical:** The route feels more operational and output-driven than meaning-driven. That makes it feel polished, but also easier to over-trust. Some of Plato’s documented field defects were not visible in the live route I reached, which suggests view drift or conditional rendering.
- **Heat Cost:** Right now the worst usability issue is not wording. It is availability. The route crash is the first experience.

## Overall grade
**Usability grade for Track C, as experienced live: C-**
- Hydraulics: **C** — usable, but designer-error-prone
- Electrical: **C+/B-** for output polish, **C-** for input transparency
- Heat Cost: **F** right now because it crashes

---

# Summary of what the live app confirmed vs missed

## Strong confirmations
- DEF-C01 through DEF-C08, DEF-C13, DEF-C16, DEF-C18, DEF-C22, DEF-C23, DEF-C33 are materially confirmed by the live hydraulics experience.

## Partial contradictions / already-improved areas
- DEF-C20 and DEF-C21 are directionally valid, but the live labels are already somewhat improved versus Plato’s wording.

## Unverifiable due live mismatch or blocker
- DEF-C09, DEF-C14, DEF-C25 were not visible in the current electrical route I reached.
- Heat Cost field-level defects (DEF-C10/C11/C12/C17/C27/C30) were not live-verifiable because the route crashes first.

## Major live issue Plato + Researcher missed
- **Heat Cost route crash / error-boundary failure** is a Track C usability blocker and should be treated as a top live finding.
