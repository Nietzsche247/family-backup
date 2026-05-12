# 🗡️ Steel Man Gut-Check — CAPTCHA Solving Strategy

> **Date:** February 19, 2026  
> **Challenger:** Steel Man (Aristotle Subagent)  
> **Target:** `captcha-solving-research-2026-02-19.md`  
> **Verdict Scale:** ✅ Valid | ❌ Invalid | ⚠️ Needs Testing

---

## 1. "93-97% autonomous solving for ~$10/month"

**Challenge:** This is the $10/month "sweet spot" tier — stealth + CapSolver ($10 deposit ≈ 10K solves) + 2Captcha ($3 fallback). The 93-97% figure assumes Layer 1 avoidance is working AND you're hitting ≤500 CAPTCHAs/month. That's a best-case volume assumption. If avoidance fails (see #8 below), you're paying for every page visit. At 100 pages/day × 30 days = 3,000 visits, with 70% CAPTCHA rate on datacenter IP, that's 2,100 solves/month ≈ $2.10 in solver fees. Still cheap — but only if the solve success rate holds. CapSolver's own blog claims "exceeds 95%"; third-party tests (Habr, GoLogin) confirm 95-99% on standard reCAPTCHA. But these are scraping commodity sites, not government portals with enterprise reCAPTCHA configs or aggressive bot scoring. **No one is publishing success rates specifically on .gov sites.**

**Verdict:** ⚠️ **Needs Testing.** The $10/month number is plausible for low volume. The 93-97% success rate is marketing-optimistic. Expect 85-93% on government sites until proven otherwise. Budget $20-30/month to be safe.

---

## 2. CapSolver as the Recommended Solver

**Challenge:** Founded by "Vinn" — no company registration info, no public incorporation. Product Hunt reviews are positive (Dec 2025), Trustpilot reviews are favorable, Bright Data wrote a review (Jan 2026). BUT: this is a CAPTCHA-solving service — a legally gray industry. Compare to 2Captcha (operational since 2007, 18 years) and Anti-Captcha (since 2007). CapSolver has maybe 2-3 years of track record. **Key risk:** When Google pushes a reCAPTCHA update, AI-first solvers break first and need retraining. Human-backed services (2Captcha) degrade gracefully — humans adapt, AI doesn't. There WILL be 12-48 hour windows where CapSolver returns failures after a Google/Cloudflare update.

**Verdict:** ⚠️ **Valid but fragile.** CapSolver is fine as primary. But the report's architecture already has 2Captcha as fallback — that's the right call. **Add monitoring:** if CapSolver success rate drops below 80% for >1 hour, auto-switch to 2Captcha. And keep $10 balance on both at all times.

---

## 3. "CAPTCHA Avoidance Eliminates 60-80%"

**Challenge:** This is the report's biggest blind spot. The 60-80% figure assumes stealth fingerprinting + residential proxy. But the report recommends this as *optional* ($50/month tier). On **Hetzner datacenter IP alone**, the report's own table says avoidance drops to **30%**. That's catastrophic — you'd be solving 70% of CAPTCHAs through paid services. Residential proxy costs: research shows **$1.50-4.00/GB** at scale. At ~500KB per page visit, 3,000 visits/month = ~1.5GB = **$2.25-6.00/month.** That's actually affordable. But: Cloudflare community threads (July-August 2025) show Hetzner IPs are specifically called out — "a Hetzner IP will get smoked by IP scoring." Some sites block Hetzner ASN entirely, not just CAPTCHA — straight block.

**Verdict:** ❌ **Invalid as stated for our setup.** The 60-80% avoidance claim is only true WITH residential proxy. Without it (pure Hetzner), expect 20-30% avoidance at best. **Residential proxy is NOT optional — it's mandatory.** Good news: it's only ~$5-10/month for our volume. Budget for it from day one.

---

## 4. Layered Approach — Failure Cascade & Latency

**Challenge:** The report doesn't address total latency through the cascade.

| Layer | Latency | Notes |
|---|---|---|
| Layer 1 (Avoidance) | 0ms if it works | But detection takes ~1-2s (page load + check for CAPTCHA elements) |
| Layer 2 (Local AI) | 2-10s | Only fires for custom text CAPTCHAs (~15% of sites). Skip for reCAPTCHA/Turnstile. |
| Layer 3 (CapSolver) | 3-13s | reCAPTCHA v2: 3-9s. Turnstile: <3s. Plus 3s polling intervals. |
| Layer 4 (Aaron) | 30s-5min | Depends on Aaron being awake and near his phone. |

**Worst case for a single page:** 2s detection + 10s local fail + 13s paid solver = **25 seconds.** But Layer 2 should be skipped for reCAPTCHA/Turnstile (can't solve locally), so realistic worst case is **2s + 9s = 11 seconds.** That's fine for form filling. **BUT:** reCAPTCHA v3 tokens expire after **2 minutes.** If the solve takes >2 min (e.g., Aaron fallback), the token is useless by the time you inject it. Need to handle re-solving.

**Verdict:** ✅ **Valid architecture, but implement smart routing.** Don't run Layer 2 for token-based CAPTCHAs. Jump straight to Layer 3. Add token expiry handling (re-solve if >90s old). Total latency is acceptable.

---

## 5. Session Persistence — "Extends One Solve Across Hours"

**Challenge:** The report claims reCAPTCHA exemption cookies last ~3 hours and Cloudflare cf_clearance lasts 15-30 minutes. But government sites have their OWN session timeouts independent of CAPTCHA cookies. Federal guidelines (NIST) recommend 15-30 minute idle timeouts. Many .gov sites enforce this strictly. So even if your CAPTCHA cookie is valid for 3 hours, the **site session** may expire in 15 minutes of inactivity. You'd need to re-authenticate AND re-solve the CAPTCHA. Also: Cloudflare cf_clearance is **IP-bound**. If your residential proxy rotates IPs (which many do automatically), the clearance cookie becomes invalid instantly.

**Verdict:** ⚠️ **Partially valid.** Session persistence helps but "hours" is optimistic for government sites. Expect **15-30 minute windows** in practice. Design for frequent re-authentication. Pin proxy IP for session duration (don't rotate mid-session). This is workable but not the "one solve = hours of browsing" the report implies.

---

## 6. Local AI Handles Only 15% of Sites — Cost at Scale

**Challenge:** If 85% of CAPTCHAs need paid solving, what does scale look like?

| Daily Solves | Monthly Solves | Cost @ $1/1K | Cost @ $2/1K (enterprise reCAPTCHA) |
|---|---|---|---|
| 50 | 1,500 | $1.50 | $3.00 |
| 200 | 6,000 | $6.00 | $12.00 |
| 1,000 | 30,000 | $30.00 | $60.00 |

At our expected scale (maybe 50-200 CAPTCHAs/day with avoidance working), this is **$1.50-$12/month.** Very manageable. The report's $10 deposit lasting a long time is realistic for our use case. We're not doing 1,000 solves/day — that's scraping scale. We're doing targeted form fills.

**Verdict:** ✅ **Valid.** Costs are manageable at our scale. The $10/month estimate holds for ~100-200 page visits/day with residential proxy avoidance working.

---

## 7. Playwright-Extra Stealth Plugin — Maintenance Status

**Challenge:** This is a real concern. Research shows:
- **puppeteer-extra-plugin-stealth** on npm: last published **~3 years ago** (v2.11.2, ~Feb 2023)
- **playwright-extra** on npm: last published **~3 years ago** (v4.3.6)
- Reddit threads from April 2024 already questioning if it still works
- As of June 2024, it was **detectable via CDP detection** methods
- The Python `playwright-stealth` (separate project) has more recent updates (Jan 2026)

The report says "v4.3.0, actively maintained as of Feb 2026" — **this appears incorrect.** The npm package hasn't been updated in years. The GitHub repo (berstend/puppeteer-extra) shows limited recent activity. Modern anti-bot systems (Cloudflare, DataDome) have adapted to its evasion patterns.

**Verdict:** ❌ **Invalid — stale dependency.** The stealth plugin is NOT actively maintained. It works against basic detection but fails against current Cloudflare/DataDome. **Alternatives to evaluate:** Camoufox, Nodriver, or the Python `playwright-stealth` package (updated Nov 2025). This is a critical POC test item.

---

## 8. The Residential Proxy Problem — Hetzner Undermining Avoidance

**Challenge:** This is the elephant in the room. Cloudflare community posts from mid-2025 explicitly call out Hetzner:
- "A Hetzner IP will get smoked by IP scoring"
- "I blocked ~1,600 ASN with type hosting (including Hetzner, OVH...)"
- Some sites don't just CAPTCHA Hetzner — they **block it outright**

Running our browser automation from Hetzner means Layer 1 (avoidance) starts at a massive disadvantage. Even with perfect stealth fingerprinting, the IP reputation alone tanks your reCAPTCHA v3 score to 0.1-0.3 (bot range).

**Two options:**
1. **Residential proxy through Hetzner** (~$5-10/month) — the browser runs on Hetzner but all traffic routes through residential proxy. Solves IP scoring but adds latency (~100-200ms per request) and proxy can fail.
2. **Run browser on Aaron's home network** — residential IP for free, no proxy needed. But: uptime depends on Aaron's machine, can't scale, and Aaron's IP could get flagged if we're aggressive.

**Verdict:** ❌ **Invalid to assume Hetzner works for avoidance.** The report acknowledges this but treats residential proxy as optional. It's not. **Recommendation:** Start POC with residential proxy ($5-10/month) from Hetzner. If latency/reliability is bad, consider split architecture: Hetzner for orchestration, home network for browser.

---

## 🎯 What to Test in the POC — CAPTCHA Specific

1. **Baseline CAPTCHA rate from Hetzner (no stealth, no proxy):** Hit 5 target .gov sites 10 times each. Count CAPTCHAs. This is our worst case.

2. **Stealth-only from Hetzner:** Add playwright-stealth (Python version, NOT the stale npm one). Repeat test. Measure improvement.

3. **Residential proxy + stealth from Hetzner:** Add cheapest residential proxy (IPRoyal or similar). Repeat test. This should be our operating baseline.

4. **CapSolver success rate on actual .gov targets:** Create CapSolver account ($10). Solve 50 real CAPTCHAs from target sites. Measure: success rate, latency, token validity.

5. **Session persistence reality check:** After solving one CAPTCHA on a .gov site, how long before the session/CAPTCHA cookie expires? Test with 5-min, 15-min, 30-min idle intervals.

6. **Token injection reliability:** Do the reCAPTCHA/Turnstile token injection code patterns from the report actually work on our target sites? Some sites validate server-side in ways that reject injected tokens.

7. **Fallback latency:** Time the full cascade: CAPTCHA detected → CapSolver solve → token injected → form submitted. Target: <15 seconds end-to-end.

8. **Stealth plugin alternatives:** Test Camoufox and/or Nodriver against Cloudflare Turnstile. Compare detection rates to playwright-stealth.

---

## Bottom Line

The report's architecture is **sound in structure** (layered approach is correct). But it has **two critical blind spots:**

1. **The stealth plugin is stale** — the Node.js version hasn't been updated in ~3 years and is detectable. Use Python `playwright-stealth` or Camoufox instead.

2. **Residential proxy is mandatory, not optional** — Hetzner IPs are specifically targeted by Cloudflare and reCAPTCHA scoring. Without residential proxy, avoidance drops from 60-80% to 20-30%, which 3x's your CAPTCHA solver costs and latency.

With those fixes, the $15-20/month estimate (solver + residential proxy) is realistic for our scale. The layered approach will work. But **test it on actual target sites** before committing — government sites may have enterprise reCAPTCHA configs that behave differently from the commodity sites these services are benchmarked against.

*— Steel Man 🗡️*
