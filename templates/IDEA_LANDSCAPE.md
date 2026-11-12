# Idea Landscape & Prior-Art Investigation

> **Project / Idea Title:** {IDEA_TITLE}  
> **Investigation Date:** {DATE}  
> **Target Environment:** {AGENT_ENVIRONMENT}  
> **Investigation Status:** {STATUS: COMPLETE / PARTIAL / OFFLINE_CONSTRAINED}

---

## 1. Executive Summary & Idea Framing

### 1.1 The Idea
{Provide a concise 1-2 paragraph description of the proposed system, core functionality, target user, and key assumptions.}

### 1.2 Core Mechanisms & Functional Decomposition
Break the idea down into its architectural and algorithmic components:
- **Component 1 (Transport / Interface):** {e.g., Real-time audio ingestion and playback}
- **Component 2 (Orchestration & State):** {e.g., Multi-speaker turn arbitration state machine}
- **Component 3 (Cognitive / Logic Layer):** {e.g., Persona system prompts and long-term memory}
- **Component 4 (Verification / Evaluation):** {e.g., Assumption checking and debate evaluation}

---

## 2. Direct Prior Art & Existing Solutions

### 2.1 Commercial & Closed-Source Landscape
| Product / Service | Core Approach | Overlap with Target Idea | Key Differentiation / Limitations | Evidence Tier |
| :--- | :--- | :--- | :--- | :--- |
| {Product Name} | {Summary of approach} | {Direct overlap} | {Missing capabilities} | `[VERIFIED-METADATA]` |

### 2.2 Open-Source Ecosystem & GitHub Prior Art
{Summary of GitHub discovery queries executed, rate limit status, and top discovered repositories.}

| Repository | Stars | Language | License | Maintenance | Primary Reusable Module | Evidence Tier |
| :--- | :---: | :--- | :--- | :---: | :--- | :--- |
| [{owner/repo}]({url}) | {stars} | {lang} | {license} | {ACTIVE/DORMANT} | {What module or layer can be used} | `[VERIFIED-METADATA]` |

---

## 3. Academic Research & Theoretical Foundations

| Paper Title / Mechanism | Authors & Year | Core Theoretical Finding | Architectural Relevance | Evidence Tier |
| :--- | :--- | :--- | :--- | :--- |
| {Title} | {Authors, Year} | {Core contribution} | {How it applies to target idea} | `[VERIFIED-SOURCE]` |

---

## 4. Cross-Vertical & Analogous Domain Exploration (Mandatory Differentiator)

Map the underlying mechanisms to battle-tested patterns in unrelated industries:

### 4.1 Analogous Mechanism 1: {e.g., Gaming NPC Narrative Control}
- **Source Domain:** {e.g., Interactive Drama & Video Game AI (Façade, Dwarf Fortress)}
- **Underlying Mechanism:** {e.g., Beat managers, drama tension curves, emotional affinity graphs}
- **What Transfers:** {Specific algorithms, state machines, or data structures that can be adapted}
- **Why It Transfers:** {Structural equivalence between the two domains}
- **What Requires Adaptation:** {Latency, semantic ambiguity, cost constraints}
- **Evidence Tag:** `[INFERRED]` / `[VERIFIED-SOURCE]`

### 4.2 Analogous Mechanism 2: {e.g., Aviation Cockpit Resource Management}
- **Source Domain:** {e.g., Commercial Avionics & Safety-Critical Control}
- **Underlying Mechanism:** {e.g., Challenge-and-response protocol, sterile channel rules, multi-sensor voting}
- **What Transfers:** {Turn arbitration, interruption handling, hallucination cross-checking}
- **Why It Transfers:** {Collision resolution among concurrent vocal inputs}
- **What Requires Adaptation:** {Non-deterministic speech recognition delays}
- **Evidence Tag:** `[INFERRED]`

---

## 5. Technical Reusability & Code Clearance Audit

Detailed audit of top open-source candidates:

### 5.1 Repository: [{owner/repo}]({url})
- **Legal Clearance:** `{CLEAR / CONDITIONAL / RESTRICTED / CRITICAL_BLOCKER}`
  - **License:** `{SPDX_ID}` — {Legal rationale regarding commercial/open-source adoption}
- **Architectural Modularity:** `{MODULAR_LIBRARY / FRAMEWORK / FULL_APPLICATION}`
  - **Manifests & Dependencies:** {Detected manifest files and heavyweight dependency concerns}
- **Maintenance Signals:** {Days since last push, archived status, issue velocity}
- **Verdict:** {Adopt as dependency / Extract algorithms / Fork / Avoid}
- **Evidence Tag:** `[VERIFIED-SOURCE]`

---

## 6. Feature Gap Analysis

Compare existing solutions directly against the target idea:

| Target Capability | Existing State in Prior Art | Nature of the Gap | Strategic Significance |
| :--- | :--- | :--- | :--- |
| {Capability A} | {How competitors or libraries handle it today} | {Missing / Incomplete / Architectural Trade-off} | {High / Medium / Low opportunity} |
| {Capability B} | {How competitors or libraries handle it today} | {Missing / Incomplete / Architectural Trade-off} | {High / Medium / Low opportunity} |

---

## 7. Cross-Pollination & Enhancement Opportunities

Novel mechanisms borrowed from adjacent fields that could elevate the product:

1. **Enhancement 1 ({Name}):**
   - **Mechanism:** {Description}
   - **Origin Industry:** {Origin domain}
   - **Anticipated Benefit:** {Why it improves the user experience or architecture}
   - **Integration Complexity:** `{Low / Medium / High}`
   - **Evidence Tag:** `[INFERRED]`

---

## 8. Strategic Build Decision & Actionable Roadmap

### 8.1 Primary Recommendation
> **Strategic Posture:** `{ADOPT / FORK / EXTEND / EXTRACT / INTEGRATE / BUILD FROM SCRATCH / INVESTIGATE FURTHER}`

### 8.2 Defensible Rationale
{Provide the clear engineering, legal, and operational justification for this decision. Explain why alternative postures were rejected.}

### 8.3 Recommended Architecture & Assembly Path
```
{High-level architectural diagram or ASCII component layout}
```

1. **Layer 1 ({Layer Name}):** {Integrate existing library X or extract module Y}
2. **Layer 2 ({Layer Name}):** {Adopt library Z for transport}
3. **Layer 3 (Custom Value-Add):** {Custom implementation focus: where your engineering effort should be concentrated}

---

## 9. Research Integrity & Evidence Ledger

### 9.1 Evidence Classification Summary
- `[VERIFIED-TEST]`: {Count} findings verified via execution
- `[VERIFIED-SOURCE]`: {Count} findings verified via source code / manifest inspection
- `[VERIFIED-METADATA]`: {Count} findings verified via API metadata
- `[INFERRED]`: {Count} analytical deductions grounded in technical facts
- `[UNKNOWN]`: {Count} unverified or inaccessible data points

### 9.2 Identified Limitations & Blindspots
{Explicitly list any queries that hit rate limits, uninspected repositories, paywalled research papers, or blocked external networks.}
