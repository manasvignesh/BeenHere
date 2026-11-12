# Idea Landscape & Prior-Art Investigation

> **Project / Idea Title:** {IDEA_TITLE}  
> **Investigation Date:** {DATE}  
> **Target Environment:** {AGENT_ENVIRONMENT}  
> **Investigation Status:** {STATUS: COMPLETE / PARTIAL / OFFLINE_CONSTRAINED}

---

## 1. Executive Findings

### 1.1 Core Synthesis
{Provide a concise 1-2 paragraph executive summary: Does this exist? What is the closest prior art? Can existing code be legally and technically reused? What is the recommended strategic build posture?}

### 1.2 Strategic Posture Snapshot
- **Build Decision:** **`{ADOPT / FORK / EXTEND / EXTRACT / INTEGRATE / BUILD FROM SCRATCH / INVESTIGATE FURTHER}`**
- **Top Prior-Art Candidates:** `{Candidate 1 (License)}, {Candidate 2 (License)}`
- **Key Analogous Mechanism:** `{Mechanism from adjacent industry}`
- **Primary Technical Risk / Bottleneck:** `{Description of primary risk}`

---

## 2. Original Idea and Intended Users

### 2.1 The Concept
{Describe the proposed system, core functionality, and value proposition.}

### 2.2 Intended Users & Primary Use Cases
- **Target Persona:** {Who uses this software?}
- **Core Jobs to be Done:**
  - {Job 1}
  - {Job 2}
- **Operating Environment & Constraints:** {e.g., Real-time voice, mobile edge, air-gapped server, high-concurrency cloud}

---

## 3. Problem and Mechanism Decomposition

### 3.1 Core User Problems
1. **Problem 1:** {Description}
2. **Problem 2:** {Description}

### 3.2 Underlying Computational & Behavioral Mechanisms
Map surface-level features to universal computer science and social mechanisms:
- **Mechanism A (Transport / Interface):** {e.g., Full-duplex WebRTC streaming with VAD}
- **Mechanism B (State & Floor Control):** {e.g., Multi-agent turn arbitration finite state machine}
- **Mechanism C (Cognitive Layer):** {e.g., Episodic memory stream with associative vector recall}
- **Mechanism D (Evaluation / Logic):** {e.g., Dialectical argument validation graph}

---

## 4. Direct Competitors and Implementations (Commercial & Closed-Source)

Discovered via commercial product discovery protocol ([references/product_discovery.md](../references/product_discovery.md)):

| Product / Service | Competitor Tier | Core Approach & Tech Stack | Overlap with Target Idea | Pricing / Availability | Evidence Tier |
| :--- | :---: | :--- | :--- | :--- | :--- |
| {Product Name} | `{Direct / Partial / Adjacent}` | {Summary of architecture} | {Direct overlap} | {Pricing model, GA status} | `[VERIFIED-METADATA]` |

---

## 5. Relevant GitHub Repositories (Open-Source Ecosystem)

Discovered via deterministic `scripts/github_search.py` queries:

| Repository | Stars | Language | License | Maintenance | Primary Reusable Module / Role | Evidence Tier |
| :--- | :---: | :--- | :--- | :---: | :--- | :--- |
| [{owner/repo}]({url}) | {stars:,} | {lang} | {license} | `{ACTIVE / MAINTAINED / DORMANT / ARCHIVED}` | {Specific module or layer} | `[VERIFIED-METADATA]` |

---

## 6. Academic Research and Experimental Systems

Discovered via deterministic `scripts/paper_search.py` across OpenAlex, arXiv, and Semantic Scholar:

| Paper Title | Year | Authors | Venue / Provider | Retracted? | Relevance & Finding | Evidence Tier |
| :--- | :---: | :--- | :--- | :---: | :--- | :--- |
| [{Title}]({doi_url}) | {year} | {authors et al.} | {venue} ({provider}) | `{No / YES}` | {Core finding & theoretical bound} | `[VERIFIED-METADATA]` |

*Disclaimer: Published abstract text represents author claims and has not been experimentally reproduced by this skill.*

---

## 7. Cross-Vertical Discoveries (Mandatory Differentiator)

Exploration of analogous mechanisms developed in unrelated industries following [references/cross_vertical_research.md](../references/cross_vertical_research.md):

### 7.1 Cross-Vertical Discovery 1: {Name}
- **Source Industry:** {e.g., Interactive Drama & Video Game AI / Commercial Avionics / Microeconomics}
- **Underlying Mechanism:** {e.g., Beat manager pacing controller / CRM sterile channel / Delphi deliberation}
- **Concrete Source Evidence:** {Cite specific paper, game engine, or protocol}
- **Analogous Parallel:** {Why the source problem is structurally equivalent to the target problem}

---

## 8. Transferability Assessments

Evaluation of cross-vertical candidates following the 10-point audit in [references/transferability_rubric.md](../references/transferability_rubric.md):

| Mechanism Candidate | Source Industry | Shared Mechanism | Required Adaptation | Transferability Classification | Evidence Tier |
| :--- | :--- | :--- | :--- | :---: | :--- |
| {Mechanism 1} | {Source Domain} | {Algorithm/Protocol} | {Latency, scale, data types} | `{DIRECTLY_TRANSFERABLE / TRANSFERABLE_WITH_ADAPTATION / CONCEPTUAL_INSPIRATION / WEAK / REJECTED}` | `[INFERRED]` |

---

## 9. Code-Reusability Recommendations

Detailed reusability inspection conducted via `scripts/repo_inspector.py` following [references/code_reusability.md](../references/code_reusability.md):

### 9.1 Repository: [{owner/repo}]({url})
- **Verification Depth:** `{METADATA_AND_MANIFESTS_ONLY / SOURCE_CODE_INSPECTED}`
- **Legal Clearance:** **`{CLEAR / CONDITIONAL_RECIPROCAL / RECIPROCAL_ON_DISTRIBUTION / NETWORK_RECIPROCAL / COMMERCIAL_RESTRICTED / CRITICAL_BLOCKER}`**
  - **License SPDX:** `{SPDX_ID}` — {Legal rationale regarding commercial use and distribution obligations}
- **Technical Modularity:** `{MODULAR_LIBRARY / FRAMEWORK / PROJECT_WORKSPACE}`
- **Maintenance Vitals:** `{Status}` (Pushed `{days}` days ago; `{issues}` open issues)
- **Recommendation:** `{ADOPT / FORK / EXTEND / EXTRACT / AVOID}`
- **Evidence Tier:** `[VERIFIED-METADATA]` (or `[VERIFIED-SOURCE]` if source files were inspected directly)

---

## 10. Feature Coverage Matrix

Structured comparison between existing solutions and target requirements:

| Target Functional Requirement | State in Prior Art | Existing Solution Coverage | Nature of the Gap | Gap Significance |
| :--- | :--- | :---: | :--- | :---: |
| {Feature 1} | {How current tools handle it} | `{Full / Partial / None}` | {Omission / Latency / Modularity} | `{High / Medium / Low}` |
| {Feature 2} | {How current tools handle it} | `{Full / Partial / None}` | {Omission / Latency / Modularity} | `{High / Medium / Low}` |

---

## 11. Missing Functionality (Gaps vs. Intentional Trade-offs)

Detailed diagnosis following [references/feature_gap_analysis.md](../references/feature_gap_analysis.md):

1. **Gap 1 ({Name}):**
   - **Nature:** `{Genuine Technical Whitespace / Deliberate Engineering Trade-off / Technical Barrier}`
   - **Diagnosis:** {Why is this missing from current tools? Is it an unsolved technical hurdle or an intentional scope boundary?}
   - **Strategic Implication:** {Should the target project build this, or follow the trade-off?}

---

## 12. Potential Enhancements (Cross-Domain Mechanism Dossiers)

High-impact mechanisms borrowed from adjacent fields (8-point dossiers):

### 12.1 Enhancement 1: {Name}
1. **Source of Inspiration:** {Origin domain, product, or paper}
2. **Evidence of Technical Feasibility:** {Citations, reference implementations}
3. **Target User Problem Addressed:** {Specific friction or bottleneck resolved}
4. **Expected Concrete Benefit:** {Measurable improvement}
5. **Integration Complexity:** `{Low / Moderate / Heavy}`
6. **Relevant Reusable Code:** `{Repo link or None}`
7. **Inherent Limitations & Failure Modes:** {Edge cases, latency limits}
8. **Implementation Priority:** `{Essential (MVP) / Optional (Post-MVP)}`

---

## 13. Implementation Alternatives

Comparison of competing architectural paths:

| Architectural Alternative | Core Building Blocks | Development Effort | Maintenance Burden | Long-Term Strategic Risk |
| :--- | :--- | :---: | :---: | :--- |
| **Path A: Full Custom Build** | Greenfield custom stack | High (6-12 mos) | 100% internal | High reinventing-the-wheel risk |
| **Path B: Composite Integration (Recommended)** | Adopt Library X + Extract Module Y + Custom Arbiter | Moderate (1-2 mos) | Shared upstream | Upstream dependency breaking changes |
| **Path C: Commercial API Wrapper** | Wrap proprietary SaaS APIs | Low (2-3 wks) | Low | High vendor lock-in & pricing risk |

---

## 14. Recommended Development Strategy

### 14.1 Primary Strategic Posture
> **Strategic Posture:** **`{ADOPT / FORK / EXTEND / EXTRACT / INTEGRATE / BUILD FROM SCRATCH / INVESTIGATE FURTHER}`**

### 14.2 Defensible Rationale
{Provide clear technical, operational, and legal justification for this decision. Explain why alternative paths were rejected.}

### 14.3 Recommended Assembly Architecture
```
{High-level architectural ASCII block diagram showing integrated vs extracted vs custom modules}
```

1. **Layer 1 (Adopt / Transport):** {Integrated open-source component}
2. **Layer 2 (Integrate / State):** {Integrated external service or library}
3. **Layer 3 (Extract / Cognitive):** {Specific extracted algorithm}
4. **Layer 4 (Custom Core Value-Add):** {Where custom engineering bandwidth MUST be concentrated}

---

## 15. Sources, Uncertainties, and Coverage Limitations

### 15.1 Evidence Ledger
- `[VERIFIED-TEST]`: {Count} findings confirmed via executing automated tests or code in a sandbox
- `[VERIFIED-SOURCE]`: {Count} findings confirmed by inspecting raw source code files directly
- `[VERIFIED-METADATA]`: {Count} findings confirmed via official API headers, manifests, or paper metadata
- `[INFERRED]`: {Count} analytical deductions grounded in technical evidence
- `[UNKNOWN]`: {Count} unverified or inaccessible data points

### 15.2 Coverage Limitations & Blindspots
- **Web / API Boundaries:** {List any queries that hit rate limits or external network restrictions}
- **Proprietary Systems:** {Identify closed-source systems whose architectures could not be verified}
- **Unverified Implementation Details:** {Note any areas where deep source inspection was not performed}
