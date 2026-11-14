# BeenHere vs Baseline: Research Quality Comparative Evaluation

> **Evaluation Engine:** `evaluations/evaluate.py` (BeenHere v1.1 Evaluation Harness)  
> **Rubric:** 6 Weighted Dimensions (0–5 scale, 0–100 Normalized Quality Index)  
> **Methodology:** Side-by-side empirical audit across identical prompt scenarios.

---

## 1. Executive Summary Table

| Scenario | Baseline Index | BeenHere Index | Delta (Δ) | Baseline Grade | BeenHere Grade | Outcome |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `accessibility_testing` | 43.5 | 90.5 | **+47.0** | F | **A+** | BeenHere Outperformed |
| `ai_recruitment` | 43.5 | 93.0 | **+49.5** | F | **A+** | BeenHere Outperformed |
| `offline_notes` | 45.5 | 91.2 | **+45.7** | F | **A+** | BeenHere Outperformed |

---

## 2. Dimension Breakdown by Scenario

### Scenario: `accessibility_testing`

| Dimension | Weight | Baseline (0–5) | BeenHere (0–5) | Delta | Key Differentiator |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Existing Solutions Discovered | 20% | 3.0 | **4.6** | +1.6 | Discovered axe-core (7.8k★), pa11y (4.6k★), eslint-plugin-jsx-a11y (3.6k★), m... |
| Reusable Code & Integration | 20% | 2.0 | **4.4** | +2.4 | Directly inspected package.json (193 lines) and lib/core/index.js in axe-core... |
| Accuracy & Evidence Traceability | 20% | 2.0 | **4.8** | +2.8 | Excised exaggerated claims; cited peer-reviewed empirical corpus (Veduis 2026... |
| Licensing & Dependency Risks | 15% | 2.0 | **4.5** | +2.5 | Carefully distinguished MPL-2.0 in axe-core (weak file-level copyleft allowin... |
| Cross-Industry Insight Quality | 15% | 1.5 | **4.2** | +2.7 | Abstracted keyboard navigation to directed graph cycle traversal from compile... |
| Actionability of Recommendation | 10% | 2.5 | **4.6** | +2.1 | Decisive architectural blueprint: Adopt axe-core as the core rules engine; em... |

**Critical Failure Modes & Traps:**
- *Baseline Missed Traps:* Empirical coverage ceiling of automated rules engines (detects only 30-57% of WCAG criteria), Pa11y LGPL-3.0 copyleft obligations vs Axe-core MPL-2.0 npm package consumption, Conflating static JSX linting with computed runtime DOM color contrast
- *BeenHere Caught Traps:* Axe-core MPL-2.0 weak copyleft vs Pa11y LGPL-3.0 subprocess invocation boundary, Empirical coverage ceiling of automated rules engines (30-57% WCAG criteria detection limit), Static JSX AST linting inability to compute dynamic rendered CSS background contrast, Accessibility Insights scanner extraction vs browser extension coupling

---

### Scenario: `ai_recruitment`

| Dimension | Weight | Baseline (0–5) | BeenHere (0–5) | Delta | Key Differentiator |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Existing Solutions Discovered | 20% | 2.5 | **4.7** | +2.2 | Discovered both open-source ATS codebases (Horilla HR, OpenCATS), specialized... |
| Reusable Code & Integration | 20% | 2.0 | **4.6** | +2.6 | Directly inspected requirements.txt, pyproject.toml, and source files across ... |
| Accuracy & Evidence Traceability | 20% | 2.5 | **4.8** | +2.3 | All 36 markdown links audited and verified via verify_sources.py with 0 broke... |
| Licensing & Dependency Risks | 15% | 1.5 | **5.0** | +3.5 | Uncovered critical legal trap: Horilla HR is LGPL-2.1, but inspecting require... |
| Cross-Industry Insight Quality | 15% | 2.0 | **4.0** | +2.0 | Adapted two-stage information retrieval from e-commerce search engines: coars... |
| Actionability of Recommendation | 10% | 2.5 | **4.8** | +2.3 | Provided decisive, legally safe build blueprint: Reject Horilla due to AGPL r... |

**Critical Failure Modes & Traps:**
- *Baseline Missed Traps:* PyMuPDF AGPL-3.0 dual-licensing hazard inside Horilla HR, Layout-parsing failures of legacy PDF extractors on multi-column resumes, NYC Local Law 144 / EEOC algorithmic bias compliance requirements
- *BeenHere Caught Traps:* PyMuPDF AGPL-3.0 dual-licensing hazard inside Horilla HR requirements.txt, pgvector NOASSERTION API response verified as permissive PostgreSQL open source, OpenCATS legacy monolithic architecture and mixed MPL/CATS license, NYC Local Law 144 / EEOC bias compliance solved via Fairlearn MetricFrame

---

### Scenario: `offline_notes`

| Dimension | Weight | Baseline (0–5) | BeenHere (0–5) | Delta | Key Differentiator |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Existing Solutions Discovered | 20% | 3.0 | **4.8** | +1.8 | Discovered both canonical CRDT frameworks (Automerge, Yjs) and non-obvious re... |
| Reusable Code & Integration | 20% | 2.0 | **4.5** | +2.5 | Directly inspected rust/automerge/src/lib.rs (335 lines) and core/rs/core/src... |
| Accuracy & Evidence Traceability | 20% | 2.5 | **4.5** | +2.0 | Enforced strict evidence classification ([VERIFIED-SOURCE], [VERIFIED-METADAT... |
| Licensing & Dependency Risks | 15% | 1.5 | **4.8** | +3.3 | Inspected Outline LICENSE (103 lines) and caught Business Source License 1.1 ... |
| Cross-Industry Insight Quality | 15% | 2.0 | **4.2** | +2.2 | Abstracted problem to universal consensus and append-only state logs. Evaluat... |
| Actionability of Recommendation | 10% | 2.5 | **4.5** | +2.0 | Delivered concrete strategic blueprint: Adopt Automerge or Yjs for in-editor ... |

**Critical Failure Modes & Traps:**
- *Baseline Missed Traps:* Outline Business Source License (BSL-1.1) commercial non-compete rider, Impedance mismatch storing document CRDT blobs in relational SQLite, Symmetric NAT firewall failure rates in pure WebRTC P2P mesh
- *BeenHere Caught Traps:* Outline Business Source License (BSL-1.1) non-compete commercial restriction, Yjs API NOASSERTION resolved to permissive MIT via source inspection, Requirement for convergent relational extension (cr-sqlite) rather than raw JSON blobs, Pure P2P WebRTC NAT traversal firewall failure rate requiring hybrid sync server

---

## 3. Disclosures, Missing Data & Empirical Uncertainties

1. **Self-Audit Disclosure:** In runs where an AI agent acts as both researcher and evaluator, unconscious alignment bias is possible. Double-blind verification or independent human audit is recommended for high-stakes decisions.
2. **Subprocess Network Restrictions:** In sandboxed agent environments without outbound raw TCP socket access (`[WinError 10013]`), BeenHere triggers host-agent native tool fallback. The fallback preserves quality but relies on the host agent's web browsing capability.
3. **Absence of In-Memory Dynamic Execution:** Reusability scores are based on static AST parsing and manifest inspection. True runtime testing (`[VERIFIED-TEST]`) requires sandboxed container execution.
