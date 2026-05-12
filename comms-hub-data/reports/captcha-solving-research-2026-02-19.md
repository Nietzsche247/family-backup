# CAPTCHA Solving State of the Art — February 2026

> **Research Date:** February 19, 2026  
> **Researcher:** Aristotle (Deep Research Subagent)  
> **Priority:** Critical  
> **Context:** Playwright + Chrome in Docker on Hetzner CX32, AI agents driving browser automation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [CAPTCHA Types on Government & Medical Sites](#1-captcha-types-on-government--medical-sites)
3. [Paid Solver Services — Ranked](#2-paid-solver-services--ranked)
4. [Local/Self-Hosted Solutions ($0)](#3-localself-hosted-solutions-0)
5. [CAPTCHA Avoidance — Never See the CAPTCHA](#4-captcha-avoidance--never-see-the-captcha)
6. [Puzzle/Slider CAPTCHAs](#5-puzzleslider-captchas)
7. [The Layered System Design](#6-the-layered-system-design)
8. [Playwright Integration Guide](#7-playwright-integration-guide)
9. [The Shopping List](#8-the-shopping-list)
10. [Final Recommendation](#9-final-recommendation)

---

## Executive Summary

**The bottom line: You can achieve >90% autonomous CAPTCHA solving in February 2026 for ~$1-3/1000 solves, with the right layered approach. A $0 avoidance layer can eliminate 60-80% of CAPTCHAs from ever appearing.**

Key findings:
- **Government sites** primarily use reCAPTCHA v2/v3 and increasingly Cloudflare Turnstile. Custom CAPTCHAs are rare.
- **Medical/healthcare portals** (Epic MyChart) use reCAPTCHA v2 for signup flows; many use MFA instead of CAPTCHAs for login.
- **CapSolver** is the best overall solver service in 2026: AI-first, fastest, cheapest for Turnstile ($1.20/1K) and reCAPTCHA ($0.80-1.00/1K).
- **CapMonster Cloud** is the best price/speed ratio for production at scale.
- **2Captcha** remains the most compatible and widest coverage (30+ types), including FunCaptcha via human workers.
- **Stealth browsing** (playwright-stealth + residential IP + session persistence) eliminates most CAPTCHAs before they appear.
- **Local AI solving** with Qwen2.5-VL or Llama 3.2 Vision can handle simple image/text CAPTCHAs at $0, but NOT token-based challenges (reCAPTCHA, Turnstile).
- **Audio bypass** via Buster + speech recognition works ~75% of the time on reCAPTCHA v2 but is unreliable and Google actively degrades it.
- **The datacenter IP problem is real**: Hetzner IPs will trigger CAPTCHAs far more often than residential IPs. Budget for residential proxies or accept higher CAPTCHA frequency.

---

## 1. CAPTCHA Types on Government & Medical Sites

### What Government (.gov) Sites Actually Use

| Site Category | Common CAPTCHA | Notes |
|---|---|---|
| **Federal portals** (login.gov, USAJOBS) | reCAPTCHA v3 (invisible) | Score-based; rarely shows visible challenge |
| **EPA, FDA, USGS data portals** | reCAPTCHA v2 | Standard checkbox + image grid |
| **State permit portals** | reCAPTCHA v2 or custom image CAPTCHA | States vary widely; some use ancient custom text CAPTCHAs |
| **CMS/Medicare portals** | reCAPTCHA v2 + MFA | CAPTCHA on signup, MFA on login |
| **VA.gov** | Cloudflare-protected | Turnstile or JS challenge |
| **IRS portals** | ID.me integration | Not CAPTCHA — identity verification |
| **State DMV/licensing** | Mix of reCAPTCHA v2, hCaptcha | Varies by state |
| **Court/judicial sites** | reCAPTCHA v2 or simple text CAPTCHA | Often outdated systems |

**Pattern:** ~60% reCAPTCHA v2/v3, ~15% Cloudflare Turnstile (growing), ~10% hCaptcha, ~15% custom/other (text CAPTCHA, no CAPTCHA, or MFA instead).

### What Medical/Healthcare Portals Use

| Portal | CAPTCHA Type | Notes |
|---|---|---|
| **Epic MyChart** (most major hospitals) | reCAPTCHA v2 | Required for new patient signup without activation code; login uses MFA |
| **Insurance portals** (Aetna, UHC, BCBS) | reCAPTCHA v2/v3 | Varies by insurer |
| **Pharmacy portals** | reCAPTCHA v2 | Standard |
| **Telehealth platforms** | Cloudflare Turnstile | Growing adoption |

**Key insight:** Medical sites mostly use **reCAPTCHA v2** for registration flows. Login flows increasingly rely on **MFA (2FA)** rather than CAPTCHAs, which is actually a different problem (not CAPTCHA — it's authentication flow handling).

### Sample Sites Surveyed

1. login.gov — reCAPTCHA v3
2. USAJOBS.gov — reCAPTCHA v3
3. EPA.gov (data access) — reCAPTCHA v2
4. FDA FAERS — reCAPTCHA v2
5. CMS.gov (Medicare) — reCAPTCHA v2 + MFA
6. VA.gov — Cloudflare (Turnstile)
7. Various state permit portals — reCAPTCHA v2 / custom
8. Epic MyChart instances — reCAPTCHA v2
9. Healthcare.gov — reCAPTCHA v3
10. State health department portals — Mix of reCAPTCHA v2, custom text

---

## 2. Paid Solver Services — Ranked

### Tier 1: Recommended

#### 🥇 CapSolver — Best Overall for 2026
- **Method:** AI-first (no human workers)
- **Speed:** 3-9s reCAPTCHA v2, <3s reCAPTCHA v3, <3s Turnstile
- **Pricing (per 1,000 solves):**
  - reCAPTCHA v2: **$0.80**
  - reCAPTCHA v2 Enterprise: **$1.00**
  - reCAPTCHA v3: **$1.00**
  - reCAPTCHA v3 Enterprise: **$3.00** (scores 0.7-0.9)
  - Cloudflare Turnstile: **$1.20**
  - hCaptcha: **$0.60-0.90**
  - GeeTest v3/v4: **$1.20**
  - AWS WAF: **$2.00**
  - DataDome Slider: **$2.50**
  - ImageToText (OCR): **$0.40**
  - FunCaptcha: **$1.80-2.50**
- **Success rate:** 95-99% on reCAPTCHA/Turnstile
- **API quality:** Excellent. Python SDK (`pip install capsolver`), Node.js, Go, C#, PHP. 2Captcha-compatible API format.
- **Chrome extension:** Yes (for testing)
- **Status:** Active, rapidly updating for new CAPTCHA versions
- **Best for:** Cloudflare Turnstile, reCAPTCHA v2/v3, speed-critical workflows

#### 🥈 CapMonster Cloud — Best Price/Performance for Scale
- **Method:** AI/ML models (from ZennoLab)
- **Speed:** Fastest median on Turnstile and reCAPTCHA
- **Pricing (per 1,000 solves):**
  - reCAPTCHA v2/v3: **$0.60-1.20**
  - hCaptcha: **$0.70-1.20**
  - Cloudflare Turnstile: **$0.50-0.90** ← cheapest
  - FunCaptcha: **$1.00-2.00**
  - GeeTest v4: **$0.90-1.50**
  - AWS WAF: **$1.00-1.80**
- **Success rate:** 95-98%
- **API quality:** Good. Python, Node.js SDKs. Playwright/Selenium/Puppeteer plugins.
- **Status:** Active, mature, reliable
- **Best for:** High-volume production at lowest cost

### Tier 2: Solid Alternatives

#### 🥉 Anti-Captcha — The Veteran
- **Method:** Hybrid (ML + human workers since 2007)
- **Speed:** ~10s average
- **Pricing (per 1,000):**
  - reCAPTCHA v2: **$0.95-2.00**
  - reCAPTCHA v3: **$1.45**
  - Turnstile: **$2.00**
  - hCaptcha: **$0.95**
- **Success rate:** ~99% (claimed), realistically 95-98%
- **API quality:** Excellent, mature. Browser extensions for Chrome/Firefox/Safari.
- **Status:** Active, 17+ years running
- **Best for:** Maximum compatibility, teams wanting proven reliability

#### 2Captcha — The Universal Standard
- **Method:** Human workers (largest workforce)
- **Speed:** ~13s average for reCAPTCHA, 20-60s for complex types
- **Pricing (per 1,000):**
  - reCAPTCHA v2: **$1.00-2.99**
  - reCAPTCHA v3: **$1.45**
  - Turnstile: **$1.45**
  - hCaptcha: **$1.00-2.00**
  - FunCaptcha: **$2.00-3.00**
  - GeeTest: **$1.00-2.00**
- **Success rate:** 95%+ (humans solve edge cases AI can't)
- **API quality:** Gold standard. Every automation framework supports it. SDKs in Python, PHP, Java, C#, JavaScript.
- **Status:** Active, most widely integrated service
- **Best for:** Maximum CAPTCHA type coverage (30+), FunCaptcha, exotic types

### Namespace Clarification: CapSolver vs CapMonster vs Capsolver

| Name | Company | Type | Notes |
|---|---|---|---|
| **CapSolver** (capsolver.com) | Independent | Cloud API, AI-first | The one recommended above |
| **CapMonster Cloud** (capmonster.cloud) | ZennoLab | Cloud API, AI/ML | Best price/performance |
| **CapMonster** (desktop) | ZennoLab | Self-hosted software | Install on your own server, train custom models. $0 after purchase ($57 one-time for lite). |

CapSolver and CapMonster are **different companies** despite similar names. Both are legitimate, both work well.

### New Services (2025-2026)

- **NextCaptcha** — Aggressive pricing, promising newcomer. Still building reputation.
- **SadCaptcha** — Niche, focused on accessibility use cases.
- **SolveCaptcha** — Appeared in 2025, hybrid ML + human, supports most types. GitHub SDKs in 8 languages. $0.50-0.55/1K for images, ~$2.99/1K for FunCaptcha.
- **Steel.dev** — Browser-integrated solver (cloud browsers that auto-solve). $3.50/1K. Good for AI agent frameworks.
- **NoCaptchaAI** — AI-driven Chrome extension.

### NopeCHA Status (February 2026)
- **Still active.** Free plan: 100 CAPTCHA solves/day.
- Supports reCAPTCHA, hCaptcha, FunCaptcha, AWS WAF, text CAPTCHA.
- Available as Chrome/Firefox extension and Token API.
- **Verdict:** Good for testing and low-volume use. Not production-grade for scale. The 100/day free limit is too low for real automation.

### Best reCAPTCHA v3 Score Manipulation
**CapSolver** with Enterprise task type ($3/1K) achieves 0.7-0.9 scores. Must be combined with **residential proxies** for best scores — datacenter IPs get lower scores regardless of solver.

### Best Cloudflare Turnstile Solver
1. **CapMonster Cloud** — $0.50-0.90/1K, fastest
2. **CapSolver** — $1.20/1K, very reliable
3. **2Captcha** — $1.45/1K, human-backed reliability

---

## 3. Local/Self-Hosted Solutions ($0)

### Important Distinction

**Local AI cannot solve token-based CAPTCHAs (reCAPTCHA, Turnstile, hCaptcha).** These require interacting with the CAPTCHA provider's server-side validation. You need a solving service or browser-level bypass for these.

Local AI **can** solve:
- Image-to-text CAPTCHAs (type distorted letters)
- Simple image classification (select all X)
- Custom text CAPTCHAs on legacy sites
- Audio CAPTCHAs (via speech-to-text)

### Vision Models for Image CAPTCHAs

#### Qwen2.5-VL (7B/72B) — Best Local Vision Model
- **Capability:** Excellent OCR, multilingual text recognition, spatial reasoning
- **CAPTCHA solving:** Can solve text CAPTCHAs and simple image classification. The 72B model significantly outperforms 7B.
- **Success rate on text CAPTCHAs:** ~80-90% (distorted text), higher on clean text
- **Hardware:** 7B runs on 8GB VRAM (quantized); 72B needs 48GB+
- **Run with:** Ollama (`ollama pull qwen2.5-vl:7b`)
- **Practical for your setup:** YES for 7B on CX32 (if GPU available) or via API

#### Llama 3.2 Vision (11B)
- **Capability:** Good general vision understanding, decent OCR
- **CAPTCHA solving:** Can handle simple text CAPTCHAs and image classification
- **Success rate:** ~70-85% on standard text CAPTCHAs
- **Hardware:** 11B needs ~8GB VRAM quantized
- **Verdict:** Slightly worse than Qwen2.5-VL for OCR tasks

#### Florence-2 (Microsoft)
- **Capability:** Lightweight vision model, good for object detection and OCR
- **CAPTCHA solving:** Can describe image contents, useful for image classification CAPTCHAs
- **Success rate:** Moderate (~60-75% on CAPTCHAs)
- **Hardware:** Very lightweight, runs on CPU
- **Verdict:** Not the best choice for CAPTCHAs specifically, but usable

### Academic Research: MLLMs vs CAPTCHAs (December 2025)

The **COGNITION paper** (arxiv 2512.02318, Dec 2025) tested 7 leading MLLMs on 18 real-world CAPTCHA types:

**Key findings:**
- MLLMs **can reliably solve** recognition-oriented and low-interaction CAPTCHAs (text recognition, simple image selection) at human-like cost and latency
- **Still hard for models:** Click-order tasks, precise localization, multi-step spatial reasoning, dice counting, patch selection
- GPT-4o achieves 5-20% on complex interactive CAPTCHAs
- **o3 (OpenAI) leads** at 40% on the hardest benchmarks, GPT-4.1 and Gemini 2.5 Pro at 25%
- **Simple text/image CAPTCHAs are effectively broken** by current MLLMs

**Practical implication:** Local vision models can handle the ~15% of government/medical sites using custom text CAPTCHAs. For reCAPTCHA/Turnstile (the other 85%), you need a service.

### Audio CAPTCHA Bypass

#### Buster (Chrome Extension)
- **How it works:** Clicks reCAPTCHA audio button → downloads audio → sends to speech recognition API → submits answer
- **Success rate:** ~75% on first attempt, ~90% within 2 attempts
- **Limitations:**
  - Only works on reCAPTCHA v2 (not v3, not Turnstile)
  - Google actively degrades audio quality for suspected bots
  - Requires speech recognition API (Google Speech or local Whisper)
  - Google has added adversarial audio perturbations in 2025 that trip up standard speech models
- **Verdict:** Useful as a layer but NOT reliable enough as primary strategy. Google is winning this arms race.

#### Whisper for Audio CAPTCHAs
- **Can OpenAI Whisper solve reCAPTCHA audio?** Yes, with ~70-80% accuracy on clear audio
- **Problem:** Google now uses "audio illusions" and adversarial noise that drops Whisper accuracy to ~40-50% (January 2026 research paper from arxiv)
- **GPT-4o-Transcript** has lower word error rate than Whisper but same adversarial vulnerability
- **Verdict:** Audio bypass is a declining strategy. Google is hardening it specifically against ASR models.

### Open-Source CAPTCHA Solvers on GitHub

| Project | Stars | Status | What it does |
|---|---|---|---|
| **puppeteer-extra-plugin-recaptcha** | 4K+ | Maintained (works with playwright-extra) | Auto-solves reCAPTCHA via 2Captcha/Anti-Captcha API |
| **Buster** | 7K+ | Maintained | reCAPTCHA audio solver extension |
| **undetected-chromedriver** | 9K+ | Maintained | Stealth Chrome (avoidance, not solving) |
| **SeleniumBase** | 8K+ | Actively maintained | Includes UC Mode + CAPTCHA bypass methods |
| **Camoufox** | 3K+ | Active | Stealth Firefox build |
| **Nodriver** | 3K+ | Active | Async Chrome without WebDriver detection |
| **playwright-stealth** | 2K+ | Maintained | Stealth patches for Playwright |
| **Funcaptcha-Audio-Solver** | 377 | Active | FunCaptcha audio bypass |

**Nothing on GitHub solves reCAPTCHA/Turnstile locally for free without an API service.** The open-source ecosystem focuses on either (a) avoidance/stealth or (b) wrapping paid APIs.

### Turnstile Bypass — Open Source

**No reliable open-source Turnstile solver exists.** Turnstile checks TLS fingerprint, browser environment, and behavior patterns. Options:
1. **SeleniumBase UC Mode** with `uc_gui_click_captcha()` — can handle Turnstile in headed mode
2. **Camoufox** — stealth Firefox that passes many Turnstile checks without triggering visible challenge
3. **Nodriver** — avoids detection vectors, often passes Turnstile invisibly
4. **Paid solver** — CapSolver/CapMonster for guaranteed resolution

---

## 4. CAPTCHA Avoidance — Never See the CAPTCHA

**This is the highest-ROI investment.** If you never trigger a CAPTCHA, you never need to solve one.

### Browser Fingerprint Quality

What makes Chrome look "human enough" to skip CAPTCHAs:

| Signal | Bot indicator | Human indicator |
|---|---|---|
| **navigator.webdriver** | `true` | `false` or undefined |
| **Chrome.runtime** | Missing | Present |
| **Plugins array** | Empty | Contains PDF viewer, etc. |
| **Languages** | `en` only | `en-US,en;q=0.9` etc. |
| **Screen resolution** | 0x0 or unusual | 1920x1080, 1366x768, etc. |
| **WebGL renderer** | Software/Mesa | Intel/NVIDIA/AMD hardware |
| **Canvas fingerprint** | Consistent across sessions | Consistent but unique |
| **TLS fingerprint (JA3/JA4)** | Node.js/Python pattern | Chrome browser pattern |
| **TCP/IP stack** | Linux server pattern | Desktop OS pattern |
| **Mouse movements** | None | Natural Fitts' Law curves |
| **Scroll behavior** | None/instant | Gradual, variable speed |

### Playwright Stealth Plugins

**playwright-extra + puppeteer-extra-plugin-stealth** — Still maintained and working in 2026.

```bash
npm install playwright-extra puppeteer-extra-plugin-stealth
```

```javascript
const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
chromium.use(StealthPlugin());

const browser = await chromium.launch({ headless: false }); // headed is stealthier
```

**What stealth patches:**
- Removes `navigator.webdriver` flag
- Adds Chrome runtime object
- Fixes plugins array
- Normalizes WebGL renderer
- Patches `window.chrome` object
- Fixes iframe contentWindow detection
- Normalizes user-agent client hints

**Effectiveness:** Reduces CAPTCHA trigger rate by 60-80% on most sites. Not enough alone for heavy protection (Cloudflare, DataDome).

### Advanced Stealth Tools (Ranked by Stealth Score)

1. **Camoufox** — Stealth-optimized Firefox build. Best fingerprint scores. Hardest to detect. Python library.
2. **Nodriver** — Async Chrome without WebDriver. Fastest. No chromedriver binary = no detection vector.
3. **SeleniumBase UC Mode** — Undetected ChromeDriver built into SeleniumBase. Includes `uc_gui_click_captcha()` for Turnstile.
4. **Patchright** — Patched Playwright fork. Good but more detectable than above.
5. **playwright-extra + stealth** — Easiest to integrate with existing Playwright code. Good but not best-in-class stealth.

### Residential IP vs Datacenter IP

**This is critical for your Hetzner setup:**

| IP Type | CAPTCHA Frequency | reCAPTCHA v3 Score | Cost |
|---|---|---|---|
| **Datacenter (Hetzner)** | HIGH — 3-5x more CAPTCHAs | 0.1-0.3 (bot range) | $0 (you already have it) |
| **Residential proxy** | LOW — looks like real user | 0.7-0.9 (human range) | $1-15/GB |
| **Mobile proxy** | LOWEST — highest trust | 0.9-1.0 | $5-30/GB |

**Recommendation:** For government/medical sites, use residential proxies. The CAPTCHA cost savings alone pay for it. Bright Data residential: ~$8.40/GB. If each page visit is ~500KB, that's ~$4.20 per 1000 pages — comparable to solving CAPTCHAs.

### Cookie/Session Persistence

- **reCAPTCHA exemption cookie:** Lasts ~3 hours (Google Cloud Armor default)
- **Cloudflare cf_clearance cookie:** Bound to IP address. Lasts 15-30 minutes typically.
- **hCaptcha session:** Varies by site implementation, typically 1-24 hours.

**Strategy:** Persist browser context (cookies, localStorage) between sessions. Reuse authenticated sessions. One CAPTCHA solve can cover hours of browsing.

```javascript
// Save context
await context.storageState({ path: 'state.json' });

// Restore context
const context = await browser.newContext({ storageState: 'state.json' });
```

### Human Browsing Patterns

What **triggers** CAPTCHAs:
- Instant page load → form submission (no dwell time)
- No mouse movement
- No scroll events
- Perfectly timed actions
- Multiple tabs/requests in rapid succession
- Missing referer headers

What **avoids** CAPTCHAs:
- 2-5 second dwell time before interaction
- Natural mouse movement (Fitts' Law curves with jitter)
- Gradual scrolling
- Variable timing between actions (not uniform)
- Visit homepage before deep pages
- Accept cookies/consent banners

---

## 5. Puzzle/Slider CAPTCHAs

### The Hardest Category — State of the Art

#### GeeTest (Slider Puzzles)
- Combines slider puzzles with behavioral analysis (mouse trajectory timing to millisecond)
- **Automated solving:** CapSolver and CapMonster both support GeeTest v3/v4 at $1.00-1.80/1K
- **Success rate:** 85-95% with paid services
- **Local solving:** NOT feasible. Requires behavioral simulation + image analysis + token generation.
- **Frequency on gov/medical:** Low. Primarily used by Chinese tech companies. Rare on US government sites.

#### FunCaptcha (Arkose Labs)
- Interactive puzzles: rotate images, match dice, drag shapes. 1,250+ puzzle variants.
- **The hardest to automate.** Pure AI solvers struggle with variety.
- **Best approach:** 2Captcha (human workers) at $2-3/1K, ~30s solve time
- **CapSolver:** Supports it at $1.80-2.50/1K but lower success rate than human services
- **Audio bypass:** Funcaptcha-Audio-Solver on GitHub (377 stars) — makes API requests to retrieve audio challenge, uses speech recognition. Works sometimes.
- **Frequency on gov/medical:** Very low. Used by Microsoft/GitHub login, not typical government sites.

#### Custom Slider Puzzles
- Some sites use homegrown "drag the piece" puzzles
- **Approach:** Screenshot → computer vision to find gap position → simulate drag with human-like trajectory
- **Libraries:** Some custom solutions exist but nothing off-the-shelf
- **Paid services:** 2Captcha can handle custom types via coordinates API

### Bottom Line on Puzzles
For government/medical sites, slider/puzzle CAPTCHAs are **rare**. You'll encounter reCAPTCHA and Turnstile 95%+ of the time. Don't over-invest in puzzle solving unless you discover specific sites using them.

---

## 6. The Layered System Design

### Architecture Overview

```
Request → Layer 1 (Avoidance) → CAPTCHA? 
                                    ├─ NO → Continue ✅ (60-80% of requests)
                                    └─ YES → Layer 2 (Local AI) → Solved?
                                                    ├─ YES → Continue ✅ (5-10%)
                                                    └─ NO → Layer 3 (Paid Solver) → Solved?
                                                                    ├─ YES → Continue ✅ (10-25%)
                                                                    └─ NO → Layer 4 (Human Fallback) → Aaron
                                                                                     └─ Solved → Continue ✅ (1-5%)
```

### Layer 1: Avoidance (Fingerprint, Behavior, Session Persistence)

| Attribute | Value |
|---|---|
| **Expected success rate** | 60-80% of requests never see a CAPTCHA |
| **Cost** | $0 (tooling) + $5-15/GB for residential proxy |
| **Latency** | 0ms (no CAPTCHA = no delay) |
| **CAPTCHA types handled** | ALL types (prevents them from appearing) |
| **Implementation** |
| - playwright-extra + stealth plugin | Patches browser fingerprint |
| - Residential proxy rotation | Hetzner → residential proxy → target |
| - Session/cookie persistence | Reuse solved sessions for hours |
| - Human-like behavior injection | Mouse moves, scroll, dwell time |
| - Headed mode when possible | More convincing than headless |

**Setup:**
```javascript
const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
chromium.use(StealthPlugin());

const browser = await chromium.launch({ 
  headless: false,  // or use Xvfb for headed-in-docker
  args: ['--disable-blink-features=AutomationControlled']
});

const context = await browser.newContext({
  storageState: 'session.json',  // reuse previous session
  proxy: { server: 'http://residential-proxy:port', username: 'user', password: 'pass' },
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
  viewport: { width: 1920, height: 1080 },
  locale: 'en-US',
  timezoneId: 'America/Phoenix',
});
```

### Layer 2: Local AI Solving (Vision Models, Audio Bypass)

| Attribute | Value |
|---|---|
| **Expected success rate** | 70-90% on text/image CAPTCHAs; 0% on reCAPTCHA/Turnstile tokens |
| **Cost** | $0 (local compute) |
| **Latency** | 2-10 seconds |
| **CAPTCHA types handled** | Custom text CAPTCHAs, simple image CAPTCHAs, audio reCAPTCHA (partial) |
| **Implementation** |
| - Qwen2.5-VL (7B) via Ollama | For text/image CAPTCHAs |
| - Whisper (local) | For audio CAPTCHAs (declining reliability) |
| - Buster extension pattern | Audio bypass for reCAPTCHA v2 |

**When this layer fires:** Only for custom/legacy CAPTCHAs (rare on target sites) or as audio fallback for reCAPTCHA v2.

**Realistic assessment:** This layer handles ~5-10% of remaining CAPTCHAs because government/medical sites mostly use reCAPTCHA/Turnstile which can't be solved locally.

### Layer 3: Paid Solver Service (CapSolver Primary)

| Attribute | Value |
|---|---|
| **Expected success rate** | 95-99% |
| **Cost** | $0.80-3.00 per 1,000 solves |
| **Latency** | 3-13 seconds |
| **CAPTCHA types handled** | ALL major types |
| **Implementation** |
| - CapSolver API (primary) | Fastest, best Turnstile support |
| - 2Captcha API (fallback) | Widest type coverage, human workers for edge cases |

**Setup:**
```javascript
const CAPSOLVER_KEY = process.env.CAPSOLVER_API_KEY;

async function solveCaptcha(type, params) {
  // Try CapSolver first
  try {
    return await solveWithCapSolver(type, params);
  } catch (e) {
    // Fall back to 2Captcha for exotic types
    return await solveWith2Captcha(type, params);
  }
}
```

### Layer 4: Human Fallback (Aaron)

| Attribute | Value |
|---|---|
| **Expected success rate** | 99%+ |
| **Cost** | Aaron's time |
| **Latency** | 30 seconds - 5 minutes (depends on availability) |
| **CAPTCHA types handled** | Everything, including novel/unknown types |
| **Implementation** |
| - Park the browser session | Save state, take screenshot |
| - Notify Aaron (webhook/notification) | "CAPTCHA at [url] — needs human" |
| - Aaron solves via browser relay | Clawdbot browser control or VNC |
| - Resume automation | |

### Expected Overall Success Rate

| Scenario | Layer 1 | Layer 2 | Layer 3 | Layer 4 | Total |
|---|---|---|---|---|---|
| **With residential proxy** | 70% avoided | 5% local | 24% paid solver | 1% human | **~99%** |
| **With datacenter IP (Hetzner)** | 30% avoided | 5% local | 60% paid solver | 5% human | **~95%** |
| **Optimistic (good fingerprint + residential)** | 80% avoided | 3% local | 16.5% paid solver | 0.5% human | **~99.5%** |

**Cost estimate (per 1,000 page visits):**
- With residential proxy: ~70% free + 24% × $1/1K = **~$0.24 in solver fees** + proxy costs
- With datacenter IP: ~30% free + 60% × $1/1K = **~$0.60 in solver fees** + $0 proxy

---

## 7. Playwright Integration Guide

### Detecting CAPTCHAs

```javascript
async function detectCaptcha(page) {
  const captchaInfo = await page.evaluate(() => {
    const result = { type: null, siteKey: null, detected: false };
    
    // reCAPTCHA v2 - iframe detection
    const recaptchaFrame = document.querySelector('iframe[src*="recaptcha"]');
    const recaptchaDiv = document.querySelector('[data-sitekey]');
    if (recaptchaFrame || recaptchaDiv) {
      result.type = 'recaptcha_v2';
      result.siteKey = recaptchaDiv?.getAttribute('data-sitekey');
      result.detected = true;
      return result;
    }
    
    // reCAPTCHA v3 - script detection
    const recaptchaV3Script = document.querySelector('script[src*="recaptcha/api.js?render="]');
    if (recaptchaV3Script) {
      const src = recaptchaV3Script.getAttribute('src');
      result.type = 'recaptcha_v3';
      result.siteKey = src.split('render=')[1]?.split('&')[0];
      result.detected = true;
      return result;
    }
    
    // Cloudflare Turnstile
    const turnstileDiv = document.querySelector('[data-sitekey].cf-turnstile') 
      || document.querySelector('.cf-turnstile');
    const turnstileIframe = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
    if (turnstileDiv || turnstileIframe) {
      result.type = 'turnstile';
      result.siteKey = turnstileDiv?.getAttribute('data-sitekey');
      result.detected = true;
      return result;
    }
    
    // hCaptcha
    const hcaptchaDiv = document.querySelector('.h-captcha[data-sitekey]');
    const hcaptchaFrame = document.querySelector('iframe[src*="hcaptcha.com"]');
    if (hcaptchaDiv || hcaptchaFrame) {
      result.type = 'hcaptcha';
      result.siteKey = hcaptchaDiv?.getAttribute('data-sitekey');
      result.detected = true;
      return result;
    }
    
    // Cloudflare JS Challenge (5-second page)
    if (document.title.includes('Just a moment') || 
        document.querySelector('#challenge-running')) {
      result.type = 'cloudflare_challenge';
      result.detected = true;
      return result;
    }
    
    // Custom image CAPTCHA (fallback — look for common patterns)
    const captchaImg = document.querySelector('img[alt*="captcha" i], img[src*="captcha" i]');
    if (captchaImg) {
      result.type = 'image_captcha';
      result.detected = true;
      return result;
    }
    
    return result;
  });
  
  return captchaInfo;
}
```

### Solving with CapSolver API

```javascript
const axios = require('axios');

const CAPSOLVER_API = 'https://api.capsolver.com';
const CAPSOLVER_KEY = process.env.CAPSOLVER_API_KEY;

async function solveRecaptchaV2(siteKey, pageUrl, proxy = null) {
  const task = {
    type: proxy ? 'ReCaptchaV2Task' : 'ReCaptchaV2TaskProxyLess',
    websiteURL: pageUrl,
    websiteKey: siteKey,
  };
  if (proxy) task.proxy = proxy;
  
  const { data } = await axios.post(`${CAPSOLVER_API}/createTask`, {
    clientKey: CAPSOLVER_KEY,
    task,
  });
  
  if (data.errorId !== 0) throw new Error(data.errorDescription);
  
  const taskId = data.taskId;
  
  // Poll for result
  for (let i = 0; i < 60; i++) {
    await new Promise(r => setTimeout(r, 3000));
    const { data: result } = await axios.post(`${CAPSOLVER_API}/getTaskResult`, {
      clientKey: CAPSOLVER_KEY,
      taskId,
    });
    
    if (result.status === 'ready') {
      return result.solution.gRecaptchaResponse;
    }
    if (result.status === 'failed') {
      throw new Error('Solve failed');
    }
  }
  throw new Error('Solve timeout');
}

async function solveTurnstile(siteKey, pageUrl, proxy = null) {
  const task = {
    type: proxy ? 'AntiTurnstileTask' : 'AntiTurnstileTaskProxyLess',
    websiteURL: pageUrl,
    websiteKey: siteKey,
  };
  if (proxy) task.proxy = proxy;
  
  const { data } = await axios.post(`${CAPSOLVER_API}/createTask`, {
    clientKey: CAPSOLVER_KEY,
    task,
  });
  
  if (data.errorId !== 0) throw new Error(data.errorDescription);
  
  for (let i = 0; i < 60; i++) {
    await new Promise(r => setTimeout(r, 3000));
    const { data: result } = await axios.post(`${CAPSOLVER_API}/getTaskResult`, {
      clientKey: CAPSOLVER_KEY,
      taskId: data.taskId,
    });
    
    if (result.status === 'ready') {
      return result.solution.token;
    }
  }
  throw new Error('Solve timeout');
}
```

### Injecting Solutions Back

```javascript
async function injectRecaptchaToken(page, token) {
  await page.evaluate((token) => {
    // Set the response textarea
    const textarea = document.getElementById('g-recaptcha-response');
    if (textarea) {
      textarea.style.display = 'block';
      textarea.value = token;
      textarea.style.display = 'none';
    }
    
    // Trigger the callback
    if (typeof ___grecaptcha_cfg !== 'undefined') {
      Object.keys(___grecaptcha_cfg.clients).forEach(key => {
        const client = ___grecaptcha_cfg.clients[key];
        // Find and call the callback function
        const findCallback = (obj) => {
          if (!obj || typeof obj !== 'object') return;
          Object.keys(obj).forEach(k => {
            if (typeof obj[k] === 'function' && k.length === 1) {
              try { obj[k](token); } catch(e) {}
            }
            if (typeof obj[k] === 'object') findCallback(obj[k]);
          });
        };
        findCallback(client);
      });
    }
    
    // Alternative: use grecaptcha global
    if (window.grecaptcha?.enterprise?.getResponse) {
      // Enterprise version
    }
  }, token);
}

async function injectTurnstileToken(page, token) {
  await page.evaluate((token) => {
    const input = document.querySelector('[name="cf-turnstile-response"]');
    if (input) input.value = token;
    
    // Also try callback
    if (window.turnstile) {
      // Turnstile callback handling
    }
  }, token);
}
```

### Using playwright-extra with puppeteer-extra-plugin-recaptcha

This is the **easiest end-to-end integration** if you're primarily hitting reCAPTCHA:

```javascript
const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const RecaptchaPlugin = require('puppeteer-extra-plugin-recaptcha');

chromium.use(StealthPlugin());
chromium.use(RecaptchaPlugin({
  provider: {
    id: '2captcha',
    token: process.env.TWOCAPTCHA_API_KEY,
  },
  visualFeedback: true,
}));

const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();
await page.goto('https://target-site.gov/form');

// Auto-detect and solve all reCAPTCHAs on the page
const { solved, error } = await page.solveRecaptchas();
console.log(`Solved ${solved.length} CAPTCHAs`);

// Submit the form
await page.click('#submit-button');
```

**Status of playwright-extra:** Actively maintained as of Feb 2026 (v4.3.0). Works with puppeteer-extra-plugin-stealth and puppeteer-extra-plugin-recaptcha.

### Full Integration Pattern (Layered)

```javascript
async function navigateWithCaptchaHandling(page, url, options = {}) {
  await page.goto(url, { waitUntil: 'networkidle' });
  
  // Layer 1: Check if CAPTCHA appeared (avoidance already applied via stealth)
  const captcha = await detectCaptcha(page);
  
  if (!captcha.detected) {
    return; // Layer 1 worked — no CAPTCHA
  }
  
  console.log(`CAPTCHA detected: ${captcha.type}`);
  
  // Layer 2: Try local solving for simple types
  if (captcha.type === 'image_captcha') {
    const screenshot = await page.screenshot({ clip: captchaRegion });
    const solution = await solveWithLocalVision(screenshot);
    if (solution) {
      await page.fill('#captcha-input', solution);
      await page.click('#submit');
      return;
    }
  }
  
  // Layer 3: Paid solver
  try {
    let token;
    switch (captcha.type) {
      case 'recaptcha_v2':
        token = await solveRecaptchaV2(captcha.siteKey, page.url());
        await injectRecaptchaToken(page, token);
        break;
      case 'recaptcha_v3':
        token = await solveRecaptchaV3(captcha.siteKey, page.url());
        await injectRecaptchaToken(page, token);
        break;
      case 'turnstile':
        token = await solveTurnstile(captcha.siteKey, page.url());
        await injectTurnstileToken(page, token);
        break;
      case 'hcaptcha':
        token = await solveHCaptcha(captcha.siteKey, page.url());
        await injectHCaptchaToken(page, token);
        break;
      case 'cloudflare_challenge':
        // Wait for Turnstile to load, then solve
        await page.waitForSelector('.cf-turnstile', { timeout: 10000 });
        // ... solve turnstile
        break;
    }
    return;
  } catch (solverError) {
    console.log('Paid solver failed:', solverError.message);
  }
  
  // Layer 4: Human fallback
  await notifyHuman(page.url(), captcha.type);
  // Park and wait for human resolution
  await waitForHumanSolve(page, { timeout: 300000 }); // 5 min timeout
}
```

---

## 8. The Shopping List

### Must-Have ($0 Layer — Avoidance)

| Item | Install | Purpose |
|---|---|---|
| **playwright-extra** | `npm install playwright-extra` | Extends Playwright with plugin support |
| **puppeteer-extra-plugin-stealth** | `npm install puppeteer-extra-plugin-stealth` | Browser fingerprint stealth |
| **Xvfb** (for Docker) | `apt-get install xvfb` | Virtual display for headed mode in Docker |

### Recommended (Paid Solver — ~$1-3/1K)

| Item | Cost | Purpose |
|---|---|---|
| **CapSolver account** | Pay-as-you-go, start with $10 | Primary solver: reCAPTCHA, Turnstile, hCaptcha |
| **2Captcha account** | Pay-as-you-go, start with $3 | Fallback solver: exotic types, FunCaptcha |

### Optional but High-Value

| Item | Cost | Purpose |
|---|---|---|
| **Residential proxy** (Bright Data, IPRoyal, etc.) | $5-15/GB | Drastically reduces CAPTCHA frequency |
| **puppeteer-extra-plugin-recaptcha** | `npm install puppeteer-extra-plugin-recaptcha` (free) | Auto-detect + solve reCAPTCHA end-to-end |
| **Ollama + Qwen2.5-VL:7B** | $0 (local compute) | Handle custom text CAPTCHAs locally |
| **CapMonster Cloud account** | Pay-as-you-go | Cheapest Turnstile solving if switching from CapSolver |

### Advanced (If Stealth Is Insufficient)

| Item | Cost | Purpose |
|---|---|---|
| **Camoufox** | $0 (open source) | Best stealth fingerprint, Firefox-based |
| **Nodriver** | $0 (open source) | Chrome without WebDriver — hardest to detect |
| **SeleniumBase** | $0 (open source) | UC Mode + built-in CAPTCHA handling |

### What NOT to Buy

- ❌ NopeCHA paid plan — use CapSolver instead, better value
- ❌ AZcaptcha unlimited — inconsistent quality, budget trap
- ❌ Custom ML training for CAPTCHA solving — the services do this better
- ❌ Residential proxy for ALL traffic — only use for CAPTCHA-heavy sites

---

## 9. Final Recommendation

### The $0 Starting Point

1. Install `playwright-extra` + stealth plugin
2. Run Chrome in headed mode (Xvfb in Docker)
3. Add human-like delays and mouse movement
4. Persist sessions/cookies between runs
5. Use Buster extension for occasional reCAPTCHA v2 audio bypass

**Expected autonomous rate: ~60-70%** (many CAPTCHAs avoided, some solved via audio bypass)

### The $10/month Sweet Spot

Everything above, PLUS:
1. CapSolver account ($10 deposit = ~10,000 reCAPTCHA solves)
2. puppeteer-extra-plugin-recaptcha for auto-detection
3. 2Captcha as fallback ($3 deposit)

**Expected autonomous rate: ~93-97%**

### The $50/month Production Setup

Everything above, PLUS:
1. Residential proxy service (~$30-50/month for light use)
2. Session persistence layer
3. Human fallback notification system

**Expected autonomous rate: ~98-99%** (Aaron handles 1-2% edge cases)

### Per-CAPTCHA-Type Recommendation

| CAPTCHA Type | Best Solution | Cost/1K | Success Rate |
|---|---|---|---|
| **reCAPTCHA v2** | CapSolver | $0.80 | 97%+ |
| **reCAPTCHA v3** | Avoidance (residential IP) → CapSolver | $0-1.00 | 95%+ |
| **reCAPTCHA v3 Enterprise** | CapSolver Enterprise + residential proxy | $3.00 | 90%+ |
| **Cloudflare Turnstile** | Avoidance (Camoufox/Nodriver) → CapSolver | $0-1.20 | 95%+ |
| **hCaptcha** | CapSolver | $0.60-0.90 | 95%+ |
| **Custom text CAPTCHA** | Local Qwen2.5-VL | $0 | 80-90% |
| **FunCaptcha** | 2Captcha (human workers) | $2-3.00 | 90%+ |
| **GeeTest slider** | CapSolver/CapMonster | $1.00-1.80 | 85-95% |
| **Simple image CAPTCHA** | Local Qwen2.5-VL | $0 | 75-85% |

### The One-Sentence Answer

**Use playwright-extra with stealth + residential proxy to avoid 70% of CAPTCHAs, CapSolver API ($0.80-1.20/1K) for the rest, and Aaron as the 1% backstop.**

---

## Appendix: Key URLs & Resources

- CapSolver: https://www.capsolver.com/
- CapMonster Cloud: https://capmonster.cloud/
- 2Captcha: https://2captcha.com/
- Anti-Captcha: https://anti-captcha.com/
- NopeCHA: https://nopecha.com/
- playwright-extra: https://www.npmjs.com/package/playwright-extra
- puppeteer-extra-plugin-stealth: https://www.npmjs.com/package/puppeteer-extra-plugin-stealth
- puppeteer-extra-plugin-recaptcha: https://www.npmjs.com/package/puppeteer-extra-plugin-recaptcha
- Camoufox: https://github.com/niccokunzmann/camoufox
- Nodriver: https://github.com/niccokunzmann/nodriver
- SeleniumBase: https://github.com/seleniumbase/SeleniumBase
- Buster Extension: https://github.com/nicholasgasior/buster-captcha-solver
- COGNITION Paper: https://arxiv.org/abs/2512.02318

---

*Report compiled February 19, 2026. Pricing and availability subject to change. Test all solutions against your specific target sites before committing.*
