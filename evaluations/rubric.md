# BeenHere Research Quality Evaluation Rubric (v1.1)

This rubric establishes empirical, observable criteria for measuring the research quality, factual accuracy, legal defensibility, and engineering utility of prior-art investigations conducted by AI coding agents.

---

## 1. Core Principles

1. **Observable Evidence Over Prose Aesthetics:** Scores reflect concrete, verifiable facts (verified repository slugs, inspected source files, identified licensing clauses, traceable citations). A well-formatted or lengthy report containing hallucinations or unverified assumptions must score lower than a concise, factually anchored report.
2. **The Anti-Percentage Rule:** Reports that fabricate arbitrary pseudo-quantitative figures (e.g. *"85% code reusability"*, *"91% uniqueness"*) receive an automatic penalty in the Accuracy and Evidence dimension.
3. **Evidence Distinction:** Claims must distinguish between verified implementation code (`[VERIFIED-SOURCE]`, `[VERIFIED-TEST]`), official metadata (`[VERIFIED-METADATA]`), vendor marketing literature (`[UNVERIFIED-MARKETING-CLAIM]`), and deductive hypothesis (`[INFERRED]`).
4. **Independent / Double-Blind Evaluation Protocol:** Whenever feasible, evaluations should be conducted against an anonymized run artifact where agent identifiers and tool banners have been scrubbed. When an agent self-evaluates its output, that self-evaluation limitation must be explicitly disclosed.

---

## 2. Weighted Dimensions & Scoring Anchors (0–5 Scale)

| Dimension | Weight | Primary Focus |
| :--- | :---: | :--- |
| **D1: Relevant Existing Solutions Discovered** | 20% | Breadth, specificity, and relevance of open-source repositories and commercial products. |
| **D2: Reusable Code & Integration Suitability** | 20% | Inspection of actual source files, exported APIs, interfaces, and architecture modularity. |
| **D3: Accuracy & Traceability of Evidence** | 20% | Verifiable URLs, correct star counts, active commits, absence of hallucinated features. |
| **D4: Licensing & Dependency Risk Analysis** | 15% | Detection of non-OSI licenses (BSL, SSPL), copyleft triggers (AGPL/GPL), and dependency traps. |
| **D5: Cross-Industry Insight Quality** | 15% | Identification of genuine computational primitives from adjacent fields vs superficial metaphors. |
| **D6: Actionability of Final Recommendation** | 10% | Clear build-vs-reuse posture (Adopt, Fork, Integrate, Build) with concrete justification. |

---

### D1: Relevant Existing Solutions Discovered (Weight: 20%)

Evaluates whether the agent identified the true state-of-the-art and specialized building blocks, rather than merely reciting high-level brand names.

* **Score 0 (Irrelevant / Hallucinated):** Discovers zero relevant solutions or outputs hallucinated repositories/projects that do not exist.
* **Score 1 (Superficial / Generic):** Only mentions 1–2 dominant generic technologies (e.g. *"use PostgreSQL and React"*) with no specific libraries solving the core problem.
* **Score 2 (Obvious Surface Solutions Only):** Finds 2–3 high-visibility canonical repositories (e.g., top GitHub search hit), but misses specialized technical primitives and commercial comparators.
* **Score 3 (Adequate Coverage):** Discovers 3–4 relevant open-source libraries and 1–2 commercial products; covers primary requirements but overlooks key architectural primitives.
* **Score 4 (Strong Comprehensive Coverage):** Discovers 5+ highly relevant open-source repositories (spanning both turnkey solutions and specialized primitives) and identifies established commercial SaaS products.
* **Score 5 (Exemplary Multi-Angle Discovery):** Uncovers the full competitive and open-source landscape, including specialized non-obvious primitives (e.g., convergent SQLite extensions, specific AST parsers, or ratcheting key exchange libraries) and active versus dormant project forks.

---

### D2: Reusable Code & Integration Suitability (Weight: 20%)

Evaluates whether the agent inspected real source code to verify which components can be reused, which interfaces are exported, and how difficult integration will be.

* **Score 0 (No Code Awareness):** Treats repositories as black boxes; gives no indication of programming language, interfaces, or module structure.
* **Score 1 (README Speculation):** Bases all reusability claims strictly on README marketing copy without verifying whether features are actually implemented.
* **Score 2 (Surface Metadata Inspection):** Notes programming language and top-level directory structure, but identifies no specific files, exported classes, or public functions.
* **Score 3 (Targeted File Identification):** Identifies specific implementation files (e.g. `pipeline.py`, `src/index.ts`) and broad components, but does not extract exact entrypoint symbols or parameter signatures.
* **Score 4 (Verified Symbol & Interface Extraction):** Inspects actual source files directly; identifies specific exported classes, functions, methods, async signatures, and required initialization parameters.
* **Score 5 (Architectural Integration Blueprint):** Verifies exact exported APIs, identifies missing features that must be custom-written, maps data flow boundaries, and exposes architectural coupling (e.g., monorepo dependencies, runtime sidecars, or IPC overhead).

---

### D3: Accuracy & Traceability of Evidence (Weight: 20%)

Evaluates factual correctness, link integrity, and strict adherence to evidence tiers.

* **Score 0 (Pervasive Hallucination):** Fabricates non-existent URLs, commits, paper titles, DOIs, or library capabilities.
* **Score 1 (Unverified Claims Dominant):** Real repositories are named, but multiple links are broken, stars/maintenance dates are wildly inaccurate, and claims lack citation.
* **Score 2 (Weak Evidence Traceability):** Valid links, but documentation claims are conflated with verified code capabilities; uses speculative figures (*"saves 80% time"*).
* **Score 3 (Verified Metadata & Working Links):** All links are valid and reachable; repository metadata (stars, active dates, languages) is accurate; claims cite specific pages or files.
* **Score 4 (Strict Evidence Hierarchy Enforced):** Consistently tags claims with rigorous evidence tiers (`[VERIFIED-SOURCE]`, `[VERIFIED-METADATA]`, `[UNVERIFIED-MARKETING-CLAIM]`); zero broken URLs; zero arbitrary percentages.
* **Score 5 (Audited Provenance with Exact Commit/Line Anchors):** Every technical assertion is anchored to an exact file path, commit hash, line range, or published DOI; explicitly flags unverified claims and empirical uncertainties.

---

### D4: Licensing & Dependency Risk Analysis (Weight: 15%)

Evaluates legal defensibility, copyleft obligations, dual-licensing traps, and hidden dependency hazards.

* **Score 0 (Ignored / Dangerous):** Completely omits license information or recommends copying proprietary/incompatible code without notice.
* **Score 1 (Naive API String Echoing):** Merely repeats GitHub API license tags without inspecting text; overlooks `NOASSERTION` or dual-license indicators.
* **Score 2 (Basic License Category):** Correctly identifies permissive vs copyleft, but misses nuanced obligations (e.g., treats all copyleft as identical, missing the SaaS disclosure trigger in AGPL).
* **Score 3 (Accurate License Classification):** Distinguishes Permissive (MIT/Apache), Weak Copyleft (MPL/LGPL), Strong Copyleft (GPL), and Network Copyleft (AGPL); correctly advises on dynamic linking vs modification.
* **Score 4 (Source-Level License Auditing):** Inspects raw `LICENSE` files to resolve `NOASSERTION` (e.g., verifying MIT in custom headers); identifies non-OSI source-available restrictions like Business Source License (BSL-1.1) and non-compete clauses.
* **Score 5 (Deep Supply-Chain & Dependency Risk Audit):** Audits dependency manifests (`package.json`, `requirements.txt`, `Cargo.toml`) for transitive license hazards (e.g., PyMuPDF dual-licensing in LGPL packages, Redis RSALv2), checks maintenance bit-rot, and flags pinned unmaintained dependencies.

---

### D5: Cross-Industry Insight Quality (Weight: 15%)

Evaluates whether cross-domain analogies represent genuine computational primitives or vacuous metaphors.

* **Score 0 (Irrelevant / Absurd):** Introduces bizarre or completely inapplicable analogies (e.g., *"like baking bread because both require patience"*).
* **Score 1 (Superficial Metaphor):** Mentions high-level concepts (e.g., *"aviation cockpit safety"*, *"biological immune systems"*) but provides zero architectural or algorithmic translation.
* **Score 2 (Plausible Analogy, No Code Transfer):** Identifies a legitimate cross-domain parallel, but mischaracterizes it as directly reusable software or fails to define the underlying mathematical/computational mechanism.
* **Score 3 (Mapped Computational Primitive):** Clearly abstracts the problem into a universal mechanism (e.g., turn arbitration -> priority queuing, CRDT merge -> DAG consensus) and cites a real industry pattern.
* **Score 4 (Formal Transferability Assessment):** Rigorously evaluates what transfers (algorithms, data structures, formal specifications) versus what cannot transfer (executable code), strictly classifying non-software inspiration as `CONCEPTUAL_INSPIRATION`.
* **Score 5 (Actionable Algorithmic Adaptation):** Adapts a proven algorithm or data structure from an adjacent field (e.g., adapting delta debugging from compiler testing, or order-book matching from financial exchanges) with concrete pseudo-code, data contracts, and trade-off analysis.

---

### D6: Actionability of Final Recommendation (Weight: 10%)

Evaluates whether the user receives a decisive, defensible engineering direction.

* **Score 0 (No Recommendation):** Concludes with vague generalities (e.g., *"it depends on your preferences"*), leaving the developer with no clear path forward.
* **Score 1 (Default Build-From-Scratch):** Recommends building everything from scratch despite the presence of production-grade, permissive turnkey libraries.
* **Score 2 (Unqualified Tool Dumping):** Recommends 5+ incompatible libraries without explaining how they fit together or who should build the glue code.
* **Score 3 (Clear Strategic Posture):** Selects a definite decision posture (*Adopt, Fork, Integrate, Build from Scratch*) with high-level pros and cons.
* **Score 4 (Defensible Architecture Roadmap):** Justifies the chosen posture with specific technical trade-offs; defines what to reuse off-the-shelf vs what must be built custom.
* **Score 5 (Executable Engineering Blueprint):** Provides a complete phased roadmap: specific packages to install, exact APIs to extend, custom components to write, estimated complexity, and operational risks.

---

## 3. Composite Score Calculation

The composite score is calculated as the weighted sum of the six dimension scores:

$$\text{Composite Score} = \sum_{i=1}^{6} (S_i \times W_i)$$

Where:
- $S_i \in [0, 5]$ is the score for dimension $i$.
- $W_i$ is the weight for dimension $i$ ($\sum W_i = 1.0$).
- **Normalized Quality Index (0–100):** $\text{Quality Index} = \frac{\text{Composite Score}}{5.0} \times 100$

### Performance Tiers

| Quality Index | Grade | Real-World Utility |
| :---: | :---: | :--- |
| **90.0 – 100.0** | **A+ (Exemplary)** | Rigorous, source-verified, legally cleared, actionable engineering intelligence. Prevents reinvention and legal liability. |
| **80.0 – 89.9** | **A (Strong)** | High reusability, accurate metadata, clear strategic recommendation. Minor gaps in deep dependency or cross-vertical transfer. |
| **70.0 – 79.9** | **B (Acceptable)** | Decent repository discovery, working links, general build guidance. Misses deep license riders (BSL/transitive AGPL) or specific symbol entrypoints. |
| **50.0 – 69.9** | **C (Marginal)** | Surface-level research equivalent to casual search. High reliance on unverified README copy; risk of architectural friction. |
| **< 50.0** | **F (Unacceptable)** | Inaccurate, hallucinated, or legally reckless. Fails to prevent reinvention; misleads developer. |
