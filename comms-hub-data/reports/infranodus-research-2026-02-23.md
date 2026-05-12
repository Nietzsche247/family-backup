# InfraNodus Research Report - 2026-02-23

This report provides an overview of InfraNodus, a tool for text analysis and knowledge graph visualization, to assess its suitability for the family platform as a correlation tool.

## 1. What is InfraNodus?

InfraNodus is a tool that analyzes text and visualizes it as a network graph. It helps users understand the structure of a text, identify key topics, and discover "structural gaps"—areas where concepts are discussed but not well-connected. This capability can be used to generate new ideas and insights.

**How it finds correlations:**
- It represents words as nodes and their co-occurrence within the text as connections (edges), forming a network.
- It then applies network science algorithms to this graph to identify clusters of related words (topics), find the most influential terms, and reveal patterns in the discourse.
- This approach moves beyond simple keyword counting to show the relationships and context between concepts in the text.

---

## 2. Self-Hostable & Tech Stack

Yes, InfraNodus is self-hostable. However, the publicly available open-source version on GitHub is outdated (last updated in 2020) and is not supported by the developers. The current, more advanced version with AI features is a cloud-based service.

**The tech stack for the self-hosted version is:**
- **Backend:** Node.js
- **Database:** Neo4j (Graph Database)
- **Frontend / Visualization:** Sigma.Js, Graphology, jQuery

---

## 3. Comparison with TheWebb.app

Direct comparisons are not available, but based on their stated goals, we can infer the following:

| Feature | InfraNodus | TheWebb.app |
|---|---|---|
| **Primary Goal** | Text network analysis, structural gap identification, idea generation. | Large-scale document investigation, AI-powered chat query, visual canvases. |
| **Approach** | Bottom-up: Automatically generates a network graph from the structure of a given text. | Top-down: Likely involves querying a large, pre-indexed dataset of documents. |
| **Core Strength** | Deep analysis and visualization of the relationships within a specific body of text. | Exploring and finding connections within a massive, existing dataset. |
| **Openness** | Has an (unsupported) open-source version. | Appears to be a fully proprietary, closed-source platform. |

**Summary:**
- **InfraNodus** is better for in-depth analysis of specific texts to understand their internal structure and find non-obvious connections or gaps. It's a "microscope" for text.
- **TheWebb.app** seems better suited as a "telescope" for broad intelligence gathering across a very large document set, using conversational AI.

---

## 4. API Availability

Yes, the modern cloud version of InfraNodus has a comprehensive **REST API**.
- It allows programmatic access to nearly all of the platform's features: submitting text for analysis, generating graphs, extracting topics and gaps, etc.
- This makes it highly suitable for integration with other applications and agents.
- The API is well-documented with examples in Python, Node.js, and cURL.
- It includes a `doNotSave` parameter to ensure data privacy if needed.

---

## 5. Cost Model

InfraNodus has a multi-tiered cost model:

- **Self-Hosted:** The old open-source version is free to use but comes without any support or modern features.
- **Cloud Service:**
  - **Free Trial:** A 14-day free trial is available for the paid plans.
  - **Paid Tiers:** Subscription plans are available (e.g., Basic, Advanced, Premium), which offer different usage limits for file uploads, API requests, and AI credits. The service is aimed at both personal/academic and commercial users.

---

## 6. Integration with Our Data Stack

InfraNodus can integrate well with our existing data stack:

- **Neo4j:** Direct and seamless integration. The self-hosted version runs on Neo4j, so we could potentially use our existing instances. The data model is based on graph principles, making it a natural fit.
- **Qdrant:** Qdrant can be used as a "retrieval" engine. We can perform vector searches in Qdrant to find relevant documents or text passages, then send the results to the InfraNodus API for deeper structural analysis.
- **DuckDB / Polars:** These tools can serve as the pre-processing layer. We can use them to clean, filter, and aggregate text data from various sources before feeding it into InfraNodus for analysis. The structured insights returned by the InfraNodus API could also be stored back in DuckDB for further analytical queries.

**Proposed Workflow:** Use **DuckDB/Polars** to prepare data -> Use **Qdrant** to find semantically relevant text -> Use **InfraNodus API** to analyze the retrieved text for non-obvious connections and structural insights -> Store results back in **Neo4j** or **DuckDB**.

---

## 7. Quick Setup Steps (Self-Hosted)

These steps are for the unsupported, older open-source version from GitHub.

1.  **Install Prerequisites:** Install Neo4j (v3.3.9 - 3.5) and Node.js/npm.
2.  **Configure Neo4j:** Set up the necessary indexes and install the APOC plugin as per the wiki.
3.  **Clone Repo:** `git clone https://github.com/noduslabs/infranodus.git`
4.  **Install Dependencies:** `cd infranodus && npm install`
5.  **Configure InfraNodus:**
    - Copy `config.json.sample` to `config.json`.
    - (Optional) Add API keys for Twitter, etc.
    - Create empty files `views/statsabove.ejs`, `views/statsbelow.ejs`, `views/statsheader.ejs`.
6.  **Run Server:** `node app.js`
7.  **Access:** The application will be running at `http://localhost:3000`. Create an account using the secret invitation code found in `config.json`.
