# Platform Architecture Research Report: 2026-02-22

**Prepared by:** Researcher 🔬

## 1. Executive Summary: Top 5 Findings

This research identifies a set of powerful, cutting-edge, and highly-leveraged open-source building blocks to construct a universal multi-agent platform. These tools were selected for their ability to deliver a disproportionate advantage ("save 6 months, cost $0") and compound across multiple use cases.

1.  **Stigmergic Coordination is the Future**: The most advanced architecture pattern is to abandon direct agent-to-agent calls and hard-coded orchestrators. Instead, agents should coordinate indirectly through a shared environment. The **Stigmergic Blackboard Protocol (SBP)** is the ideal lightweight tool for this, enabling emergent, robust, and scalable multi-agent workflows.

2.  **AI-Powered Browser Automation Replaces Scraping**: For interacting with the web (e.g., public data portals), traditional scrapers are brittle. **`browser-use`**, a library that lets an AI agent control a browser with natural language commands, is a paradigm shift. It makes automation more robust and adaptable to website changes.

3.  **Local AI is Production-Ready**: **Ollama** has become the de-facto standard for managing and serving local LLMs and multimodal models. It provides a simple, consistent API that allows the platform to be model-agnostic, easily tapping into the latest local models like Llama 4 and Gemma 3.

4.  **Specialized Engines Outperform Generalist Libraries**: For performance-critical domains, using specialized, high-performance engines is crucial. **NautilusTrader** (with its Rust core) for finance and **InsightFace** for vision analysis are the clear winners, providing professional-grade foundations for specialist agents.

5.  **Workflow-as-Code for Image Generation**: **ComfyUI** provides the perfect backend for programmatic image generation. Its node-based, API-driven approach allows complex generation pipelines to be defined as a workflow and executed on demand, making it ideal for an automated platform.

## 2. Per-Domain Findings

This section details the key findings for each research area.

### 2.1. Multi-Agent Orchestration
- **Finding**: Stigmergy (environment-based coordination) is the most powerful pattern for a multi-domain platform.
- **Winner**: **`AdviceNXT/sbp` (Stigmergic Blackboard Protocol)** provides a simple, lightweight implementation of this pattern. It allows agents to be completely decoupled, communicating only through signals in a shared environment. This is the architectural linchpin of the entire platform.

### 2.2. Local/Edge AI
- **Finding**: Running local models has been commoditized by easy-to-use server tools.
- **Winner**: **Ollama** is the best-in-class tool for managing and serving local LLMs and multimodal models. It abstracts away the complexity and provides a clean REST API. This allows any agent in the platform to easily access local AI capabilities.
- **Top Models**: Llama 4, Gemma 3, and LLaVA (for vision).

### 2.3. Vision + Facial Recognition
- **Finding**: A modular stack of a high-performance analysis toolkit and a scalable vector database is required.
- **Winner**: The **`insightface`** Python library provides state-of-the-art models for detection and embedding generation. **Milvus** is the leading open-source vector database for storing and searching those embeddings at scale.

### 2.4. Financial/Prediction
- **Finding**: A hybrid-language approach offers the best combination of performance and flexibility.
- **Winner**: **NautilusTrader**, with its Rust core and Python API, is the ideal trading engine. For prediction, the **Darts** library provides a comprehensive suite of time-series models under a unified, scikit-learn-like API.

### 2.5. Government/Public Data
- **Finding**: This is a browser automation task, and AI-powered automation is far more robust than traditional scripting.
- **Winner**: **`browser-use`** is a library built for AI agents to control browsers. Its ability to handle tasks described in natural language makes it perfect for navigating and extracting data from complex, non-standard government websites.

### 2.6. Image Generation (local)
- **Finding**: For symbol/logo generation, prompt adherence and text rendering are more important than photorealism. A workflow engine is needed for programmatic control.
- **Winner**: The **FLUX.1** model has superior prompt understanding and text rendering. **ComfyUI** is the ideal backend, allowing complex generation workflows to be defined and executed via an API.

### 2.7. Platform Architecture Patterns
- **Finding**: The dominant architecture is a **Hub-and-Spoke model** where a central orchestrator routes tasks to domain-specialist agents.
- **Winner**: Combining this pattern with the **Stigmergic Blackboard Protocol** for coordination creates a modular, scalable, and robust platform where complex behaviors can emerge from simple, decoupled agents.

## 3. Recommended Stack

This is the specific, recommended stack for building the platform.

| Domain                     | Tool                                         | Version/Model      | Link                                                            |
| -------------------------- | -------------------------------------------- | ------------------ | --------------------------------------------------------------- |
| **Agent Coordination**     | Stigmergic Blackboard Protocol (SBP)         | v0.1.0+            | [github.com/AdviceNXT/sbp](https://github.com/AdviceNXT/sbp)     |
| **Local AI Serving**       | Ollama                                       | Latest             | [ollama.com](https://ollama.com/)                                |
| **Browser Automation**     | browser-use                                  | Latest             | [github.com/browser-use/browser-use](https://github.com/browser-use/browser-use) |
| **Facial Recognition**     | insightface                                  | Latest             | [github.com/deepinsight/insightface](https://github.com/deepinsight/insightface) |
| **Vector Database**        | Milvus                                       | Latest             | [milvus.io](https://milvus.io/)                                   |
| **Algorithmic Trading**    | NautilusTrader                               | Latest             | [nautilustrader.io](https://nautilustrader.io/)                 |
| **Time-Series Forecasting**| Darts                                        | Latest             | [github.com/unit8co/darts](https://github.com/unit8co/darts)   |
| **Image Generation Model** | FLUX.1                                       | schnell & dev      | [huggingface.co/black-forest-labs/FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell) |
| **Image Generation Engine**| ComfyUI                                      | Latest             | [github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) |

## 4. Compounding Opportunities

The true power of this stack comes from how the tools compound and serve multiple use cases.

-   **Ollama + browser-use**: The `browser-use` agent can be powered by a local model served via Ollama, enabling the "Offline devices with local AI library" project to perform web automation tasks.
-   **SBP + All Agents**: The Stigmergic Blackboard is the universal nervous system. The `browser-use` agent can emit a signal when it finds data, which triggers the `NautilusTrader` agent to perform a backtest, which then triggers the `ComfyUI` agent to generate a chart. This creates complex, cross-domain workflows without any direct coupling.
-   **Milvus + Text & Images**: While recommended for facial recognition, Milvus is a general-purpose vector database. It can also store embeddings for text (e.g., for the "Mental health database" RAG system) and other images, consolidating the platform's long-term memory.

## 5. What to Avoid

-   **Monolithic Frameworks**: Avoid frameworks like LangChain or AutoGen as the *core architecture*. They are useful as tools *within* a specialist agent, but building the entire platform on them leads to tight coupling and limits flexibility.
-   **Direct Agent-to-Agent Communication**: Do not build a system where agents call each other directly via APIs. This creates a "spaghetti architecture" that is impossible to maintain. Use the stigmergic blackboard for all inter-agent coordination.
-   **Traditional Web Scrapers**: For any web data extraction, avoid using libraries like BeautifulSoup or Selenium directly. The AI-powered `browser-use` is more robust and should be the default choice.
-   **General-Purpose Tools for Specialized Tasks**: Don't use a general Python script for trading when NautilusTrader exists. Don't use a simple library for facial recognition when InsightFace exists. Use the best-in-class tool for each domain.

## 6. 90-Day Build Sequence

This is a plausible sequence to build the foundational platform in 90 days.

**Phase 1: The Core (Days 1-30)**
1.  **Setup the Nervous System**: Deploy the **Stigmergic Blackboard Protocol (SBP)** server. This is the first and most critical piece.
2.  **Setup Local AI**: Install **Ollama** and download the primary models (e.g., Llama 4, LLaVA). Create a simple "LocalAIAgent" that can be triggered via SBP to perform text and vision tasks.
3.  **Build the Orchestrator**: Create the main Orchestrator agent. Its initial job is simple: take a user prompt, and emit a corresponding signal to the SBP.
4.  **Build the Data Miner**: Create the `DataMinerAgent` using **`browser-use`** and Ollama. Task it with a simple goal (e.g., "Find the top story on Hacker News"). Have it emit a `news.found` signal to the SBP when done.

*Milestone 1: A user can ask for news, and the Orchestrator triggers the DataMinerAgent via SBP.*

**Phase 2: Adding the Senses (Days 31-60)**
1.  **Integrate Vision**: Set up **Milvus** and create a `VisionAgent` using **`insightface`**. Create a workflow where the agent can ingest a photo, generate an embedding, and store it in Milvus.
2.  **Integrate Image Generation**: Set up **ComfyUI** with the **FLUX.1** model. Create an `ImageGenAgent`. Design a simple workflow in ComfyUI and have the agent trigger it via an API call in response to an SBP signal.

*Milestone 2: The platform can index a face from a photo and generate a logo from a text prompt, all triggered by signals on the blackboard.*

**Phase 3: High-Value Specialists (Days 61-90)**
1.  **Build the Trader**: Set up **NautilusTrader** and **Darts**. Create the `FinanceAgent`. Build a simple workflow where it can ingest data, train a basic Darts model, and run a backtest.
2.  **Create a Full Cross-Domain Workflow**:
    -   User asks: "Find any news about public mining claims and plot them on a map."
    -   `Orchestrator` emits `task.find_claims`.
    -   `DataMinerAgent` senses this, uses `browser-use` to find claims, and emits `claims.found` with data.
    -   A new `GISAgent` senses `claims.found`, processes the data, and uses a map library to generate an image.
    -   The `GISAgent` emits `map.generated` with the image path.
    -   The `Orchestrator` senses this and presents the final image to the user.

*Milestone 3: A complete, cross-domain workflow is demonstrated, proving the power of the stigmergic, hub-and-spoke architecture.*
