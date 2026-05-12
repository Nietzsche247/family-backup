# 🏛️ FAMILY REVIEW: Shared Collaborative Browser & Infrastructure Architecture
## Three-Perspective Analysis — February 19, 2026

**Reviewers:** Steel Man 🗡️ | Researcher 🔬 | Daedalus 🔧  
**Subject:** Layer 2 — Shared Collaborative Browser + Compound Infrastructure  
**Classification:** Family Internal — Critical Architecture Review  
**Status:** COMPLETE

---

> *Three lenses. One architecture. The right answer wins.*

This report reviews the proposed shared collaborative browser architecture through three complementary perspectives. It builds on three prior reports:
1. Layer 2 Capability Research (tool landscape + recommended stack)
2. Steel Man Layer 2 Review (strategic critique)  
3. Steel Man Shared Browser Edge Cases (tactical risk analysis)

The proposal has evolved significantly since those reports — incorporating Docker containerization, a cloud VM option, park-and-pivot patterns, and data sanitization. This review assesses those evolutions.

---

# PART 1: STEEL MAN 🗡️
## *What Breaks, What's Missing, What We're Lying to Ourselves About*

---

### 1.1 The Hetzner CX22 Memory Problem Is Real and Disqualifying

**The claim:** A $5/month Hetzner CX22 (2 vCPU, 4GB RAM, 40GB NVMe) can run Chrome + Playwright + browser coordination.

**The reality:** This is almost certainly insufficient for production use.

Here's what the production data says:

- **A single Chromium instance with moderate page complexity uses 400MB–1.5GB RAM** (documented in post-mortem: "8GB Was a Lie: Playwright in Production," Dec 2025).
- **3 headless Chrome instances exhausted 8GB in 1 hour** (Stack Overflow report, real production incident).
- **Playwright 1.57's Chrome for Testing uses 20GB+ per instance** in some configurations (GitHub issue #38489, Dec 2025).
- **Even simple page refresh loops leak ~400MB in 20 minutes** (Playwright issue #15400).

So on a 4GB VM, you have:
- ~500MB for the OS
- ~200MB for Node.js/coordination server
- ~100MB for networking/overhead
- **~3.2GB remaining for Chrome**

That's enough for **one** Chrome instance running **one** moderately complex page. No headroom for spikes. No room for the coordination server to hold cached accessibility trees. No room for Docker's own overhead (if containerized on the VM).

**When it fails:** Page with heavy JavaScript (any modern SPA, React app, government portal with embedded maps) → memory spike → OOM killer → Chrome dies → all agents lose context → recovery cycle burns 30-60 seconds → agents retry → same page → same crash → infinite loop.

**The fix isn't "just add more RAM."** The fix is to understand the minimum viable spec:
- **CX32 (4 vCPU, 8GB RAM, $10/month)** — bare minimum for a single Chrome instance with headroom
- **CX42 (8 vCPU, 16GB RAM, $18/month)** — comfortable for 1 Chrome + coordination + Graphiti
- **CX22 at $5/month** — viable ONLY for the coordination server/dashboard, NOT for Chrome itself

**Verdict:** The $5/month number is a lie we're telling ourselves. Budget $10-18/month for a VM that can actually run this reliably. Still dirt cheap, but don't build on a foundation that OOM-kills under normal load.

---

### 1.2 Docker on Windows: Trading One Instability for Two

**The claim:** Docker on Windows/WSL2 solves Windows instability, provides network isolation, and gives us a Linux environment.

**The reality:** Docker Desktop on Windows via WSL2 is itself a source of instability.

Evidence from the Docker for Windows issue tracker:
- **Docker Desktop won't start after WSL2 updates** (issue #14801, May 2025 — still affects users)
- **Poor performance with Docker Desktop on WSL2** (issue #12401, ongoing since 2021)
- **WSL2 memory management is notoriously aggressive** — by default WSL2 will consume up to 50% of host RAM and not release it back to Windows, creating exactly the memory pressure we're trying to avoid
- Docker Desktop requires Hyper-V or WSL2 backend — both add hypervisor overhead
- Docker Desktop has its own update cycle that can conflict with Windows updates

**The failure scenario:**
1. Aaron is gaming on the Alienware
2. WSL2 has quietly consumed 16GB of the 32GB RAM for its VM
3. Chrome inside Docker inside WSL2 hits a heavy page
4. Windows memory pressure triggers → WSL2 doesn't release → game stutters → Aaron force-kills Docker
5. All browser sessions die with no graceful shutdown
6. Agent work lost

**The fundamental issue:** We're not solving Windows instability with Docker. We're adding a layer of indirection (Windows → WSL2 → Docker → Chrome) where any layer can fail and each layer makes debugging harder. On a dedicated Linux machine, Docker is rock-solid. On Windows via WSL2, Docker inherits all of Windows' problems PLUS WSL2's own problems.

**If running locally:** Skip Docker. Run Playwright directly on Windows. It works fine. The instability concerns are overblown for a single headed Chrome instance.

**If running on a cloud VM:** Docker makes perfect sense — Linux-native Docker on a Linux VM is the gold standard. This is the correct path.

**Verdict:** Docker on Windows is not the answer. Docker on a Linux cloud VM IS the answer. These are different architectures with very different reliability profiles. Don't conflate them.

---

### 1.3 Park-and-Pivot State Serialization: Harder Than It Sounds

**The claim:** Agent hits a blocker → saves full browser state → pivots to next task → Aaron resolves → agent resumes.

**What "saves full browser state" actually requires:**

| State Component | Can You Serialize It? | Difficulty |
|---|---|---|
| Current URL | ✅ Trivial | `page.url()` |
| Cookies | ✅ Easy | `context.cookies()` / `context.addCookies()` |
| localStorage/sessionStorage | ✅ Easy | CDP `DOMStorage.getDOMStorageItems()` |
| Screenshot | ✅ Easy | `page.screenshot()` |
| DOM snapshot (MHTML) | ✅ Medium | CDP `Page.captureSnapshot()` |
| Form field values (text inputs) | ⚠️ Medium | `page.evaluate()` to read all input values |
| Scroll position | ⚠️ Medium | `window.scrollX/Y` |
| **In-memory JS state (React/Vue/Angular state)** | ❌ **Impossible** | Framework state lives in JS heap, not serializable |
| **WebSocket connections** | ❌ **Impossible** | Connection state is ephemeral |
| **Server-side session state** | ❌ **Impossible** | The server doesn't know you saved and resumed |
| **Multi-step form wizard progress** | ❌ **Nearly impossible** | Often server-side, with CSRF tokens that expire |
| **OAuth/SAML flow mid-redirect** | ❌ **Impossible** | Token exchange is stateful and time-bound |
| **File upload state** | ❌ **Impossible** | Selected files can't be re-attached programmatically |

**The honest assessment:** Park-and-pivot works for ~60% of cases — the easy ones. Navigate to a URL, hit a CAPTCHA, save URL + cookies, come back later. That's valuable and worth building.

But the proposal implies it works for *any* blocker during *any* workflow. It doesn't. A multi-step government form where you're on page 3 of 5 with unsaved data, and the session times out while parked? That state is gone. An OAuth redirect mid-flow? Can't resume. A WebSocket-based real-time application? Reconnection is a completely different problem.

**What to build:**
- **v1 park-and-pivot:** URL + cookies + screenshot + form text values. Covers the simple cases.
- **Acknowledge the gap:** For complex multi-step workflows, park-and-pivot means "start over from a checkpoint" not "resume exactly where you left off."
- **Smart retry:** Instead of perfect state restoration, build retry-from-checkpoint: save the last stable state (e.g., "logged in, on page 2 of form, these fields filled") and replay from there.

**Verdict:** Park-and-pivot is a great pattern for simple blockers. Don't oversell it as universal state preservation — it's not. Build the 60% solution and be honest about the 40%.

---

### 1.4 What Fails at 2 AM When Nobody's Watching

This is the real test. The system runs 24/7. Aaron is asleep. Seven agents are browsing. Here's the failure cascade:

**Scenario 1: Chrome memory leak → OOM → silent death**
- Chrome has been running for 18 hours
- Memory usage has crept from 800MB to 3.5GB (documented behavior)
- Agent requests a JavaScript-heavy page → 4.2GB → OOM killer fires
- Chrome dies. No graceful shutdown. No state saved.
- The coordination server sees CDP connection drop
- All 7 agents get `browser:crashed` event
- Recovery: restart Chrome (10-15 seconds), lose all cookies (if not persisted), lose all tab state
- **Impact:** All in-flight work lost. Parked tasks' MHTML snapshots are stale. Agents retry from scratch.

**Scenario 2: Coordination queue deadlock**
- Agent A has a lease, waiting for human input (CAPTCHA)
- 30-second timeout fires, lease revoked
- But Agent A doesn't know the lease was revoked (network glitch between agent and coordination server)
- Agent A submits action after lease expired
- Coordination server rejects action (stale lease)
- Agent A retries, gets new lease — but the page has changed because Agent B got a lease and navigated
- Agent A's action is now based on stale page state
- **Impact:** Corrupted interaction, potential form submission with wrong data.

**Scenario 3: Site rate-limits or soft-bans the IP**
- Agents have been hitting the same government portal autonomously all night
- At 3 AM, the site starts returning 429 (rate limit) or serving a "please verify you're human" page
- No human available. Agents keep retrying (each attempt looks more bot-like)
- The IP gets escalated from rate-limit to hard block
- When Aaron wakes up, the IP is banned
- **Impact:** Need to wait hours/days for IP ban to lift, or use a different IP.

**Mitigations that must be in v1 (not v2):**
1. **Scheduled Chrome restart every 6 hours** (kills memory leaks before they kill us)
2. **Per-domain rate limiting with exponential backoff** — not just "1 request per 5 seconds" but smart backoff when 429/CAPTCHA detected
3. **Circuit breaker pattern** — after 3 failures on a domain, stop all requests to that domain for 1 hour
4. **Agent A's lease revocation must be synchronous** — agent must acknowledge the revocation before another lease is granted
5. **Night mode:** Between midnight and 8 AM, agents operate in read-only mode (extract from cache, no new navigation) unless explicitly configured otherwise

---

### 1.5 Scaling from 1 Browser to 10: The Coordination Explosion

**The proposal mentions:** "Multiple containers = multiple isolated browser sessions"

**What actually breaks at 10 concurrent sessions:**

**Resource multiplication:**
- 10 Chrome instances × 1-1.5GB each = 10-15GB RAM just for browsers
- 10 CDP screencast streams × 0.5-1.5 Mbps = 5-15 Mbps continuous upload (on the cloud VM) or download (on the dashboard)
- 10 coordination queues, 10 sets of leases, 10 streams of events for each of 7 agents = 70 event subscriptions

**Coordination complexity:**
- Which agent goes to which browser session? Static assignment or dynamic?
- If dynamic: the coordination layer now needs a scheduler — which session has the page the agent needs? 
- Cross-session state: Agent A found a URL on session 1 that agent B needs to process on session 2. How does the URL + cookies transfer?
- Login state: Each session has independent cookies. If you logged into a site on session 3, session 7 doesn't have that cookie.

**Dashboard overwhelm:**
- Aaron's phone shows 10 browser streams simultaneously? That's unusable.
- Tab switching between 10 sessions on mobile = painful UX
- Notification storm: 10 sessions × potential CAPTCHAs = Aaron's phone buzzing constantly

**The honest answer:** You will never need 10 concurrent browser sessions for a 7-agent system with 1 human. The actual need is:
- 1 active session (the agent currently browsing)
- 2-3 browser contexts (different auth domains)
- A queue of pending tasks that share the single active session

**Verdict:** Don't architect for 10 browsers. Architect for 1 browser with 3 contexts and a good queue. That's all you need and all you can realistically manage.

---

### 1.6 The Cloud VM Latency Question

**CDP screencast from Hetzner (Europe) to Arizona:**
- Hetzner's US data centers are in Ashburn, VA and Hillsboro, OR
- Arizona to Ashburn: ~50-60ms RTT
- Arizona to Hillsboro: ~40-50ms RTT
- CDP screencast frame delivery: 50-150ms
- Total: **100-200ms visual latency**

**Is this acceptable?**
- For agent automation (no human watching): **Yes, irrelevant** — agents don't watch the screencast
- For human monitoring: **Yes**, 200ms feels responsive enough
- For human CAPTCHA solving: **Yes**, you're clicking on images, 200ms is fine
- For human typing in forms: **Marginal** — 200ms keystroke echo feels slightly delayed but usable
- For real-time gaming/interaction: **No** — but that's not the use case

**The bigger latency issue nobody mentioned:** Agent → LLM API → Agent → Coordination Server → Browser. Each agent action involves an LLM call (500-3000ms for reasoning) + coordination overhead (10-50ms) + browser action execution (50-500ms). The total cycle time for one agent action is 1-4 seconds. The cloud VM's 50ms network overhead is noise compared to the LLM reasoning time.

**Verdict:** Cloud VM latency is a non-issue. The LLM reasoning loop is the real bottleneck, and it's 10-100x larger than network latency.

---

### 1.7 Remaining Holes Summary

| Hole | Severity | Status |
|---|---|---|
| CX22 RAM insufficient for Chrome | 🔴 Critical | Upgrade to CX32 minimum |
| Docker on Windows unreliable | 🔴 Critical | Use cloud VM Docker instead |
| Park-and-pivot can't save JS state | 🟠 High | Acknowledge limitation, build 60% solution |
| No 2 AM failure mitigation | 🔴 Critical | Need circuit breakers, rate limits, night mode |
| Scaling to 10 browsers is architecturally wrong | 🟡 Medium | Don't architect for it |
| Cloud VM latency | 🟢 Low | Non-issue, LLM is the bottleneck |
| Data sanitization layer complexity | 🟠 High | Not addressed in detail — see Daedalus section |
| Browser-Use CVE-2025-47241 | 🔴 Critical | Addressed in prior review, but proposal uses Playwright directly which avoids this |

---

# PART 2: RESEARCHER 🔬
## *Where the Deeper Value Hides*

---

### 2.1 The "Browserless" Elephant in the Room

Before building anything custom, evaluate **Browserless.io** (open source, Docker-native):

```
docker run -p 3000:3000 ghcr.io/browserless/chromium
```

Browserless is a production-grade Chrome-as-a-service that runs in Docker and provides:
- **Connection management** — handles Chrome lifecycle, restarts, memory limits
- **Concurrency control** — built-in queue with configurable limits
- **Multiple API interfaces** — Puppeteer, Playwright, CDP, REST
- **Resource monitoring** — tracks memory, CPU, active sessions
- **Docker-native** — designed to run in containers from day one
- **Free for non-commercial use** (MIT-licensed for self-hosting)
- **Used by 8K+ GitHub stars of production users**

**What this means for us:** Instead of building Chrome lifecycle management, health checks, memory watchdog, crash recovery, and concurrency control — all of which are in the v1 scope — we could use Browserless as the Chrome infrastructure layer and build ONLY the coordination/agent-specific logic on top.

**What we'd still build:**
- Socket.io coordination queue (agent-specific, Browserless doesn't do this)
- CDP screencast → dashboard streaming
- Accessibility tree extraction + caching
- Park-and-pivot logic
- Human override UI

**What we'd skip building:**
- Chrome process management
- Health checking and auto-restart
- Memory monitoring and limits
- Connection pooling
- Crash recovery

**Estimated savings:** 4-8 hours of v1 build time + ongoing maintenance of Chrome lifecycle code.

**Risk:** Another dependency. But Browserless is MIT-licensed, 8K+ stars, actively maintained, and we can fork it if abandoned. This is exactly the kind of leverage the team philosophy calls for.

---

### 2.2 The Accessibility Tree Is Undervalued — It's the Entire Agent Interface

The proposal correctly identifies accessibility tree extraction as key. But it understates how central this is.

**The accessibility tree is the single most important architectural decision in this entire proposal.** Here's why:

The current state of AI browser automation in 2026 (from Browserless's own State of AI report, Jan 2026) confirms: **"The most reliable agents don't just parse the DOM or look at screenshots — they read the Accessibility Tree."** Playwright's MCP server, which already exists and is production-tested, uses accessibility snapshots as its primary interface.

**The accessibility tree gives agents:**
- Role information (button, link, textbox, heading, navigation, form)
- Name/label (what the element is called)
- State (disabled, expanded, checked, focused)
- Value (current text in input fields)
- Hierarchy (parent-child relationships)
- **All in 2-10KB** vs. 100KB-5MB for raw HTML

**The deeper insight:** If you get the accessibility tree interface right, you've built something more powerful than a browser automation tool. You've built a **universal UI interaction layer**. Any agent that can read an accessibility tree and emit click/type/select actions can interact with ANY web application. This is the same interface that screen readers use — it's been standardized, tested, and maintained by the accessibility community for 20+ years.

**Concrete architecture recommendation:**
1. Extract accessibility tree via Playwright `page.accessibility.snapshot()` 
2. Augment with element references (Playwright's aria-ref system, already built)
3. Cache the augmented tree with a state hash
4. Broadcast to interested agents via Socket.io
5. Agents respond with actions referencing element IDs from the tree
6. Coordination server validates and executes

This is essentially what Playwright MCP already does. We might be building something that already exists.

---

### 2.3 Playwright MCP Server: Have We Reinvented the Wheel?

**Critical question nobody has asked:** The Playwright MCP server (official, by Microsoft) already provides:
- Browser launch and lifecycle management
- Navigation, clicking, typing, selecting via accessibility snapshots
- Screenshot capture
- PDF generation  
- File upload
- Dialog handling
- Tab management
- Console log access

**What it DOESN'T provide (and what we'd need to add):**
- Multi-agent coordination (it's designed for single-agent use)
- Priority queue / lease-based locking
- CDP screencast streaming to a dashboard
- Human override / CAPTCHA intervention
- Park-and-pivot state management
- Agent-specific access control

**The deeper value:** Instead of building a "browser operator MCP tool" from scratch, **wrap the existing Playwright MCP server** with a coordination layer. We get battle-tested browser automation for free and only build the multi-agent orchestration that's unique to our use case.

**Architecture:**
```
Agents → Our Coordination MCP Server → Playwright MCP Server → Chrome
                    ↓
            Dashboard (screencast + control)
```

This reduces the custom code from "everything" to "the coordination layer" — maybe 500-1000 lines instead of 3000-5000.

---

### 2.4 Adjacent Capabilities This Unlocks

**Capability 1: Automated form-filling as a service**
Once you can reliably fill web forms via accessibility tree + agent reasoning, you have a general-purpose form automation system. Government applications, insurance forms, permit requests, tax filings — anything that requires navigating multi-page web forms becomes automatable. This is a real product category (see Skyvern — YC-backed, $2.7M raised, doing exactly this).

**Capability 2: Web monitoring and change detection**
A persistent browser session that periodically checks pages and compares accessibility tree snapshots can detect meaningful changes (not just "the HTML changed" but "the price changed" or "a new document was posted"). Feed changes into Graphiti → temporal knowledge graph of web state changes. This is competitive intelligence, market monitoring, or regulatory tracking.

**Capability 3: Multi-site data aggregation**
Multiple browser contexts logged into different services can aggregate data that normally lives in silos. Financial data from one portal + geographic data from another + regulatory data from a third = cross-domain intelligence that would take a human hours to assemble.

**Capability 4: Workflow recording and replay**
Record Aaron's browser interactions (via CDP event logging) → convert to repeatable automated workflows → agents can replay them. This is how most successful browser automation platforms work: human does it once, automation replays it forever. The shared browser architecture makes this trivial because you're already capturing every interaction.

**Capability 5: Training data generation**
Every browser session generates structured pairs of (accessibility tree state, action taken, result). This is training data for fine-tuning browser agents. Over time, the system generates its own training data to improve agent decision-making on frequently-visited sites.

---

### 2.5 The Product Angle

**Is there a product here?** Yes, if scoped correctly.

The combination of:
- Multi-agent browser coordination
- Human-in-the-loop for blockers
- Park-and-pivot for async task management
- Accessibility-tree-first agent interface
- Knowledge graph integration

...is something nobody else has packaged together. Browserless gives you the infrastructure. Browser-Use gives you the agent. Playwright MCP gives you the interface. But nobody has built the **coordination layer for multiple AI agents sharing a browser with human oversight**.

**Potential product:** "Shared Browser for AI Teams" — a coordination layer that sits between N agents and a browser, managing turns, handling blockers, streaming to humans, and logging everything. Could be open-sourced as a differentiator for the family's reputation, or offered as a commercial tool for enterprises running multi-agent systems.

**Market timing:** The browserless.io State of AI report (Jan 2026) confirms that "teams supervise agents rather than write every step themselves" is the emerging paradigm. Our human-in-the-loop architecture is perfectly aligned with where the market is heading.

---

### 2.6 What Would Make This 10x More Powerful

**1. Session replay and debugging**
Store every CDP event, every accessibility tree snapshot, every agent action. Build a "browser DVR" that lets you rewind and replay any agent's browsing session. This is invaluable for debugging ("why did the agent click that?") and for auditing ("what data did the agent see?"). Implementation cost: low — you're already logging actions and capturing screenshots.

**2. Smart page caching with Graphiti integration**
When an agent visits a page, extract the content into Graphiti AND cache the accessibility tree. Next time ANY agent needs information from that page, check the cache first. If the cache is recent enough (configurable TTL per domain), skip the browser visit entirely. This reduces browser contention, token costs (no LLM reasoning for cached pages), and improves response time. Over time, the system builds a local knowledge base that reduces the need for live browsing.

**3. Agent specialization profiles**
Instead of all agents using the same browser interface, create specialized "lenses":
- **Research agent** gets full accessibility tree + Crawl4AI markdown
- **Form-filling agent** gets accessibility tree + form field focus + validation state
- **Data extraction agent** gets Crawl4AI structured output + table detection
- **Monitoring agent** gets diff between current and last snapshot

Each lens costs different amounts of tokens and provides different value. This is the "tiered access" pattern from the edge cases report, made concrete.

**4. Predictive CAPTCHA avoidance**
Track which sites serve CAPTCHAs and under what conditions (time of day, number of requests, request velocity). Build a model that predicts CAPTCHA likelihood and adjusts behavior proactively: slow down before the CAPTCHA triggers rather than after. This turns the rate-limiting from reactive to preventive.

---

# PART 3: DAEDALUS 🔧
## *What's Actually Hard to Build, and What to Build First*

---

### 3.1 Concrete Engineering Assessment

Let me map every v1 scope item to actual implementation complexity:

#### Item 1: Chrome via Playwright (headed, user-data-dir, version-pinned) in Docker
**Complexity: Medium**

On a Linux cloud VM, this is well-documented:
```dockerfile
FROM mcr.microsoft.com/playwright:v1.50.0-noble
# ... install your coordination server
```

Key gotchas:
- **`/dev/shm` size:** Must set `--shm-size=2g` in Docker run or use `--disable-dev-shm-usage` flag. Default 64MB WILL crash Chrome. This is the #1 cause of "mysterious" Chrome crashes in Docker.
- **Headed mode in Docker:** Requires Xvfb (X Virtual Framebuffer) or similar. Playwright Docker images include this, but it adds complexity. Alternative: use `--headless=new` mode (Chrome's new headless that renders identically to headed) — you don't actually need headed mode if you're using CDP screencast.
- **Version pinning:** Playwright pins Chromium version automatically. Use Playwright's bundled Chromium, not system Chrome. This is easy.
- **user-data-dir:** Map a Docker volume to persist cookies/storage across container restarts. Standard Docker pattern.

**Realistic time: 2-4 hours** (including Dockerfile, volume mapping, launch flags, basic smoke test)

#### Item 2: CDP screencast → WebSocket → dashboard iframe
**Complexity: Medium-Low**

```javascript
// CDP screencast is straightforward
const cdpSession = await page.context().newCDPSession(page);
await cdpSession.send('Page.startScreencast', {
  format: 'jpeg',
  quality: 50,
  maxWidth: 1280,
  maxHeight: 720
});

cdpSession.on('Page.screencastFrame', ({ data, sessionId, metadata }) => {
  // data is base64 JPEG
  io.to('dashboard').emit('browser:frame', { data, metadata });
  cdpSession.send('Page.screencastFrameAck', { sessionId });
});
```

Dashboard side: `<img>` tag that updates `src` to `data:image/jpeg;base64,${frame}` on each Socket.io event. Or use a `<canvas>` for smoother rendering.

**Key consideration:** Frame rate. CDP screencast only sends frames when the screen changes. For a static page, you get 0 frames (great for bandwidth). For a page with animations, you could get 30fps (heavy). The `quality` and `maxWidth` parameters provide sufficient control.

**Realistic time: 2-3 hours** (including WebSocket relay, dashboard iframe, basic mouse/keyboard forwarding)

#### Item 3: Socket.io action queue with priority + 30s timeout
**Complexity: Medium**

The queue itself is simple. The edge cases are the hard part.

```javascript
class BrowserActionQueue {
  constructor() {
    this.queue = new PriorityQueue(); // human=0, critical=1, normal=2, low=3
    this.currentLease = null;
  }

  async submitAction(agentId, action, priority = 2) {
    return new Promise((resolve, reject) => {
      const item = { agentId, action, priority, resolve, reject, timestamp: Date.now() };
      this.queue.enqueue(item, priority);
      this.processNext();
    });
  }

  async processNext() {
    if (this.currentLease) return; // someone has the lock
    const item = this.queue.dequeue();
    if (!item) return;
    
    this.currentLease = {
      agentId: item.agentId,
      expiresAt: Date.now() + 30000,
      stateHash: await this.getPageStateHash()
    };
    
    // Execute with timeout
    const timeout = setTimeout(() => {
      this.revokeLease('timeout');
    }, 30000);
    
    try {
      const result = await this.executeAction(item.action);
      item.resolve(result);
    } catch (err) {
      item.reject(err);
    } finally {
      clearTimeout(timeout);
      this.currentLease = null;
      this.processNext();
    }
  }
}
```

**The hard parts:**
1. **Lease revocation acknowledgment:** If you revoke Agent A's lease due to timeout, Agent A might have a CDP command in flight. You need to either wait for that command to complete or forcefully abort it. CDP doesn't have great command cancellation.
2. **Human preemption:** Aaron clicking in the dashboard should immediately interrupt any agent action. This means the dashboard needs to emit a `preempt` event that the queue respects, even mid-action.
3. **Multi-step atomic operations:** "Click the dropdown, wait for options, then select option 3" is logically one action but three CDP commands. The lease needs to cover the full sequence, not just one command.
4. **Priority inversion:** If a low-priority agent holds a lease and a high-priority agent submits, do you preempt? This is solvable but adds complexity.

**Realistic time: 4-6 hours** (basic queue: 2 hours; edge cases: 2-4 more hours)

#### Item 4: One "browser operator" MCP tool
**Complexity: Medium-High (if from scratch), Low (if wrapping Playwright MCP)**

**From scratch:** You'd build an MCP server with tools like:
- `browser_navigate(url)` → navigate and return accessibility tree
- `browser_click(elementRef)` → click an element by its accessibility reference
- `browser_type(elementRef, text)` → type text into an input
- `browser_extract()` → return current page content as markdown
- `browser_screenshot()` → return a screenshot

Each tool needs error handling, timeout management, and queue integration. From scratch: 8-12 hours.

**Wrapping Playwright MCP:** The official Playwright MCP server already implements all of these actions. You'd wrap it with your coordination layer (queue, leasing, logging) and expose the same interface to agents. This is 2-4 hours.

**Recommendation: Wrap Playwright MCP.** Don't reinvent browser actions that Microsoft has already battle-tested.

**Realistic time: 2-4 hours (wrapping) or 8-12 hours (from scratch)**

#### Item 5: Accessibility tree extraction → cache → broadcast
**Complexity: Low**

```javascript
async function extractAndCache(page) {
  const tree = await page.accessibility.snapshot({ interestingOnly: true });
  const hash = crypto.createHash('md5').update(JSON.stringify(tree)).digest('hex');
  
  if (hash !== lastHash) {
    lastHash = hash;
    cache.set('currentTree', { tree, hash, timestamp: Date.now(), url: page.url() });
    io.emit('browser:tree-updated', { tree, hash, url: page.url() });
  }
  
  return { tree, hash };
}
```

Playwright's `page.accessibility.snapshot()` is well-documented and reliable. The `interestingOnly: true` parameter filters out noise. Output is typically 2-10KB JSON — trivially cacheable.

**Quality assessment:** The accessibility tree is good enough for most agent decisions. It captures:
- All interactive elements (buttons, links, inputs, selects)
- All text content (headings, paragraphs, labels)
- Element states (disabled, checked, expanded)
- Form field values

**Where it falls short:**
- Visual layout (doesn't know that button A is to the left of button B)
- Images/icons (only sees alt text, not the visual)
- CSS-driven interactivity (hover menus, CSS-only toggles)
- Canvas/WebGL content (completely invisible)
- Custom elements with poor accessibility (many sites)

For 80%+ of web interactions, the accessibility tree is sufficient. For the remaining 20%, you'd need a screenshot + vision model as fallback — but this should be the exception, not the default (token cost).

**Realistic time: 1-2 hours**

#### Item 6: Human override toggle + mobile-responsive viewer
**Complexity: Medium**

The override toggle is simple logic:
```javascript
let humanMode = false;
io.on('connection', (socket) => {
  socket.on('human:take-control', () => {
    humanMode = true;
    queue.pause();
    io.emit('browser:human-control', true);
  });
  socket.on('human:release-control', () => {
    humanMode = false;
    queue.resume();
    io.emit('browser:human-control', false);
  });
});
```

**Mobile-responsive viewer** is harder:
- CDP screencast frames are 1280x720 JPEG → need to display responsively on 390px phone screen
- Touch-to-click coordinate mapping: `touch (x, y) on phone → scale to (x * 1280/390, y * 720/phone_height) on browser`
- Pinch-to-zoom: need to track zoom level and adjust coordinate mapping
- Mobile keyboard interaction: on-screen keyboard covers half the screen → need to handle viewport resize

The basic viewer is quick. Making it feel good on mobile takes polish.

**Realistic time: 3-5 hours** (basic: 2 hours; mobile polish: 1-3 more hours)

#### Item 7: Park-and-pivot for blocked tasks
**Complexity: Medium**

```javascript
async function parkTask(page, taskId, reason) {
  const state = {
    taskId,
    reason,
    parkedAt: Date.now(),
    url: page.url(),
    title: await page.title(),
    cookies: await page.context().cookies(),
    screenshot: await page.screenshot({ encoding: 'base64' }),
    formValues: await page.evaluate(() => {
      const inputs = document.querySelectorAll('input, textarea, select');
      return Array.from(inputs).map(el => ({
        selector: generateSelector(el), // CSS selector
        value: el.value,
        type: el.type
      }));
    }),
    localStorage: await page.evaluate(() => JSON.stringify(localStorage)),
    scrollPosition: await page.evaluate(() => ({ x: window.scrollX, y: window.scrollY }))
  };
  
  await fs.writeFile(`parked/${taskId}.json`, JSON.stringify(state, null, 2));
  io.emit('task:parked', { taskId, reason, screenshot: state.screenshot });
}
```

**The restoration is the hard part.** For simple cases (navigate to URL, set cookies):
```javascript
async function resumeTask(page, taskId) {
  const state = JSON.parse(await fs.readFile(`parked/${taskId}.json`));
  await page.context().addCookies(state.cookies);
  await page.goto(state.url);
  // Wait for page load, then attempt to restore form values
  for (const input of state.formValues) {
    try {
      await page.fill(input.selector, input.value);
    } catch (e) {
      // Element might not exist anymore — log and continue
    }
  }
}
```

For complex cases (SPA state, multi-step forms): restoration will fail silently. The agent needs to detect that the restored state doesn't match expected state and fall back to a full retry.

**Realistic time: 3-5 hours** (park: 1-2 hours; restore: 2-3 hours; the restore edge cases are where time goes)

#### Item 8: Structured JSON action logging
**Complexity: Low**

```javascript
function logAction(entry) {
  const log = {
    timestamp: new Date().toISOString(),
    agentId: entry.agentId,
    action: entry.action,
    params: entry.params,
    result: entry.result,
    duration_ms: entry.duration,
    pageUrl: entry.url,
    pageTitle: entry.title,
    stateHash: entry.hash
  };
  fs.appendFile('logs/browser-actions.jsonl', JSON.stringify(log) + '\n');
}
```

Add before/after screenshots for visual audit trail. This is straightforward.

**Realistic time: 1 hour**

---

### 3.2 Realistic Build Timeline

| Phase | Scope | Estimated Time | Confidence |
|---|---|---|---|
| **Day 1** | Docker + Playwright Chrome + CDP screencast + basic dashboard | 6-8 hours | 90% |
| **Day 2** | Socket.io action queue + Playwright MCP wrapper + accessibility tree | 6-8 hours | 85% |
| **Day 3** | Human override + park-and-pivot + action logging | 6-8 hours | 80% |
| **Day 4-5** | Mobile viewer polish + edge case handling + integration testing | 8-12 hours | 70% |
| **Week 2** | Security hardening, rate limiting, circuit breakers, night mode | 8-16 hours | 75% |
| **Week 3** | Real-world testing on actual target sites, bug fixes | 8-16 hours | 60% |

**Total realistic estimate: 5-7 working days for a usable v1, 2-3 weeks for production-hardened.**

The original "2-3 days" estimate covers the happy path. Real-world edge cases (Chrome crashes during testing, Docker configuration issues, mobile viewport bugs, authentication flow complications) reliably 2x any browser automation timeline.

**The prior Steel Man assessment of "2-3 weeks not 2-3 days" is approximately correct.** But the actual deployable v1 (imperfect, with known limitations, sufficient for initial use) can ship in 5-7 days.

---

### 3.3 What to Build First (Maximum Learning, Minimum Effort)

**The critical path for learning is:**

**Step 1 (2 hours): Proof of Concept — Can Playwright + CDP screencast work on a Hetzner VM?**

Spin up a CX32 ($10/month). Install Docker. Run:
```bash
docker run --shm-size=2g -p 3000:3000 mcr.microsoft.com/playwright:v1.50.0-noble
```
Write a 50-line script that:
1. Launches Chrome via Playwright
2. Navigates to a government portal
3. Extracts the accessibility tree
4. Starts CDP screencast
5. Streams frames over WebSocket

If this works: proceed. If Chrome OOMs on the CX32: upgrade to CX42. If accessibility tree quality is poor on target sites: reassess the entire approach.

**This 2-hour POC answers the three biggest technical uncertainties:**
1. Does the cloud VM have enough resources?
2. Does CDP screencast quality/latency work?
3. Is the accessibility tree good enough for agent decisions on our target sites?

**Step 2 (4 hours): Action queue with one agent**

Build the Socket.io priority queue. Connect one agent. Have it navigate 10 pages, extract data, report results. Measure:
- Tokens consumed per page interaction
- Time per action cycle (LLM reasoning → queue → action → result)
- Success rate on target sites

**Step 3 (4 hours): Human-in-the-loop**

Add the dashboard with screencast viewer and human override. Test: agent browses, hits a page that needs human judgment, pauses, Aaron intervenes on phone, agent resumes.

**Step 4 (rest of week): Everything else**

Park-and-pivot, multi-agent coordination, logging, mobile polish, etc.

**Key principle: Each step validates assumptions before investing more time.** Don't build the full coordination queue before verifying that the screencast actually works from a cloud VM.

---

### 3.4 The Data Sanitization Layer: Deceptively Complex

The proposal includes a data sanitization layer that strips PII before content reaches LLMs. This sounds simple. It's not.

**The problem space:**
1. **Regex-based PII detection** (SSN: `\d{3}-\d{2}-\d{4}`, credit cards: Luhn-validatable 16-digit numbers, emails: RFC 5322 pattern) — catches obvious patterns. Misses non-standard formats, foreign formats, and context-dependent PII (a person's name is PII in a medical record but not in a Wikipedia article).

2. **NER-based PII detection** (named entity recognition) — better at catching names, addresses, organizations. Requires a model (spaCy NER is free and fast for English, ~10ms per page). But false positive rate is high (place names that are also person names, etc.).

3. **LLM-based classification** — most accurate but defeats the purpose (you're sending data to a model to classify whether it's safe to send to a model).

4. **The fundamental tension:** The more accurately you sanitize, the more useful information you strip. An agent trying to fill out a form needs to see the form fields — which might contain PII. Over-sanitization makes the data useless. Under-sanitization leaks PII.

**Pragmatic recommendation:**
- **v1:** Don't build a sanitization layer. Instead, use a **dedicated agent-only browser profile** with **no personal account logins**. The browser only visits agent-specific accounts and public data. No PII enters the browser, so no PII can leak.
- **v2:** Add regex-based detection for obvious patterns (SSN, credit card, email) as a safety net. This is 2-3 hours of work and catches the most dangerous leaks.
- **v3 (if needed):** Evaluate spaCy NER or a local model for more comprehensive detection.

The best data governance is to **not put sensitive data in the system in the first place.**

---

### 3.5 Recommended Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                     HETZNER CX32 ($10/month)                     │
│                     Ubuntu 24.04, Docker                         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Docker Container: Browser Service                          │ │
│  │                                                             │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                │ │
│  │  │  Playwright       │  │  Coordination    │                │ │
│  │  │  + Chrome          │←→│  Server (Node.js)│                │ │
│  │  │  (user-data-dir    │  │  - Action Queue  │                │ │
│  │  │   volume-mounted)  │  │  - CDP Screencast│                │ │
│  │  └──────────────────┘  │  - A11y Cache    │                │ │
│  │                         │  - Park & Pivot  │                │ │
│  │                         │  - Action Logger │                │ │
│  │                         └──────────────────┘                │ │
│  │              --shm-size=2g, --network=internet-only         │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                    Cloudflare Tunnel                              │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                    ┌──────────┼──────────┐
                    │    stigmergy.space   │
                    │    Dashboard         │
                    │    - Browser viewer  │
                    │    - Human override  │
                    │    - Task queue UI   │
                    │    - Mobile viewer   │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
          ┌─────┴─────┐ ┌─────┴─────┐ ┌─────┴─────┐
          │  Agent 1   │ │  Agent 2   │ │  Aaron    │
          │ (Research) │ │ (Daedalus) │ │  (Phone)  │
          │ via MCP    │ │ via MCP    │ │ Dashboard │
          └───────────┘ └───────────┘ └───────────┘
```

**Key design decisions:**
1. **Cloud VM, not local Docker on Windows** — avoids WSL2 issues entirely
2. **CX32 ($10/month), not CX22 ($5/month)** — 8GB RAM gives Chrome actual headroom
3. **Single container with Chrome + coordination server** — simpler than separate containers, shared memory access
4. **Cloudflare Tunnel for access** — already set up, provides HTTPS, DDoS protection, no port forwarding
5. **MCP interface for agents** — standard protocol, any agent can connect
6. **Dashboard on stigmergy.space** — existing infrastructure, no new domain/hosting

---

### 3.6 The v0.1 Build Order (Maximum Learning, Minimum Effort)

| Order | What | Time | What You Learn |
|---|---|---|---|
| 1 | Hetzner CX32 + Docker + Playwright Chrome + smoke test | 2h | Is the VM sufficient? |
| 2 | CDP screencast → WebSocket → bare HTML viewer | 2h | Is the latency acceptable? |
| 3 | Accessibility tree extraction on 5 target sites | 2h | Is the a11y tree good enough for agents? |
| 4 | Socket.io action queue (single agent) | 3h | Is the queue pattern workable? |
| 5 | Connect one real agent, run 10 real tasks | 3h | Does the full loop work end-to-end? |
| 6 | Human override on dashboard | 2h | Can Aaron intervene smoothly? |
| 7 | Park-and-pivot (basic: URL + cookies + screenshot) | 2h | Is task parking useful in practice? |
| 8 | Action logging + basic audit trail | 1h | What does the data tell us? |

**Total: ~17 hours across 5-7 days, with learning gates between each step.**

Each step has a clear "go/no-go" decision:
- After step 1: Does Chrome run stably on this VM? (If no → upgrade VM)
- After step 3: Is the a11y tree sufficient? (If no → add vision model fallback)
- After step 5: Does the end-to-end loop work? (If no → reassess architecture)

---

## UNIFIED RECOMMENDATIONS

### Things the Proposal Gets Right ✅

1. **Playwright over Puppeteer** — correct, Playwright is strictly superior
2. **CDP screencast over noVNC/Guacamole** — correct, lowest latency, fewest dependencies
3. **Accessibility tree as primary agent interface** — correct, this is the industry-standard approach in 2026
4. **Socket.io coordination queue** — correct, already deployed in the comms hub
5. **Cloud VM as the preferred runtime** — correct, vastly more reliable than Docker on Windows
6. **Park-and-pivot as a pattern** — correct concept, needs scope management
7. **Human-in-the-loop for blockers** — correct, this is the architecture's key differentiator
8. **Structured action logging** — correct, essential for debugging and auditing
9. **Eliminating Guacamole and Puppeteer** — correct

### Things That Need to Change ❌→✅

| Current Proposal | Recommended Change | Why |
|---|---|---|
| CX22 ($5/month, 4GB RAM) | **CX32 ($10/month, 8GB RAM)** | Chrome will OOM on 4GB |
| Docker on Windows as primary | **Cloud VM Docker as primary, bare Playwright on Windows as fallback** | Docker on WSL2 is unreliable |
| Build Chrome lifecycle management | **Use Browserless.io or similar** | Don't build what exists |
| Build browser operator MCP from scratch | **Wrap Playwright MCP server** | Don't reinvent battle-tested tools |
| Park-and-pivot saves "full state" | **Park-and-pivot saves URL + cookies + form values + screenshot** | JS heap state is not serializable — be honest about limitations |
| Data sanitization layer in v1 | **Move to v2; use dedicated browser profile in v1** | Sanitization is deceptively complex; profile isolation is simpler and more effective |
| "2-3 days" timeline | **5-7 days for usable v1, 2-3 weeks for production** | Every browser automation project takes 2x the estimate |
| Architect for 10 browsers | **Architect for 1 browser, 3 contexts** | 7 agents don't need 10 browsers |
| All 7 agents get browser access | **1-2 "browser operator" agents + cache for others** | Reduces coordination complexity, saves tokens |

### Priority Order for Implementation

1. **POC on Hetzner CX32** (2 hours) — validates core assumptions
2. **CDP screencast + basic dashboard** (2 hours) — proves the visual feedback loop
3. **A11y tree testing on target sites** (2 hours) — validates the agent interface
4. **Action queue + one agent integration** (4 hours) — proves the coordination model
5. **Human override** (2 hours) — proves the human-in-the-loop
6. **Everything else** (remaining hours) — polish, park-and-pivot, logging, mobile

### What We Should NOT Build

- ❌ Custom Chrome lifecycle management (use Browserless or Playwright defaults)
- ❌ Full data sanitization layer for v1 (use profile isolation instead)
- ❌ Multi-session / 10-browser architecture (overkill for our scale)
- ❌ Complex state serialization for park-and-pivot (60% solution is enough)
- ❌ Anti-detection / stealth features (unnecessary risk, especially on government sites)

---

## FINAL VERDICT

**The shared collaborative browser architecture is sound.** The compound infrastructure solutions (park-and-pivot, containerization, cloud VM) each solve real problems. The tool choices are correct. The v1 scope is reasonable with adjustments.

**The three biggest risks are:**
1. **Underestimating Chrome's resource hunger** (fix: CX32 not CX22)
2. **Overestimating park-and-pivot's state restoration** (fix: honest scoping)  
3. **Building too much custom infrastructure** (fix: leverage Browserless/Playwright MCP)

**The three biggest opportunities are:**
1. **The accessibility tree as a universal agent interface** — this is the right bet for 2026
2. **The coordination layer as a unique product** — nobody else has multi-agent browser sharing with human-in-the-loop
3. **Session replay and knowledge graph integration** — creates compounding value over time

**Confidence: 80% success probability** with the recommended changes. The architecture is right. The scope needs tightening. The timeline needs honesty. Build the POC first and let reality inform the rest.

---

*Steel Man 🗡️ — Found the holes*  
*Researcher 🔬 — Found the deeper value*  
*Daedalus 🔧 — Found the realistic build path*  

*Combined review completed: 2026-02-19*  
*Classification: Internal — Bravo Team*
