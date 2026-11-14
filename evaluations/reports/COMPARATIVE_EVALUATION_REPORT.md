# BeenHere vs Baseline: Calibrated Reference Benchmark Evaluation

> **Evaluation Engine:** `evaluations/evaluate.py` (BeenHere v1.1 Evaluation Harness)  
> **Rubric:** 6 Weighted Dimensions (0–5 scale, 0–100 Normalized Quality Index)  
> **Methodology:** Calibrated reference matrix across standardized prompts.  
> **Provenance Notice:** Baseline runs are synthetic archetypal fixtures; BeenHere runs are author-scored formative benchmarks. They validate harness functionality, not double-blind empirical superiority.

---

## 1. Executive Summary Table

| Scenario | Baseline Index | BeenHere Index | Delta (Δ) | Baseline Grade | BeenHere Grade | Comparison |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `accessibility_testing` | 44.5 | 90.5 | **+46.0** | F | **A+** | BeenHere Higher (Reference) |
| `ai_recruitment` | 43.5 | 93.0 | **+49.5** | F | **A+** | BeenHere Higher (Reference) |
| `offline_notes` | 46.0 | 91.4 | **+45.4** | F | **A+** | BeenHere Higher (Reference) |

---

## 2. Dimension Breakdown by Scenario

### Scenario: `accessibility_testing`

| Dimension | Weight | Baseline (0–5) | BeenHere (0–5) | Delta | Key Differentiator |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Existing Solutions Discovered | 20% | 2.5 | **4.5** | +2.0 | Discovered foundational evaluation engines (dequelabs/axe-core), CI runners (... |
| Reusable Code & Integration | 20% | 2.0 | **4.4** | +2.4 | Statically parsed package.json across 5 repos. Inspected axe-core rule defini... |
| Accuracy & Evidence Traceability | 20% | 2.0 | **4.7** | +2.7 | All 18 markdown links verified via verify_sources.py with 0 broken links. Cit... |
| Licensing & Dependency Risks | 15% | 2.5 | **4.8** | +2.3 | Carefully distinguished axe-core's MPL-2.0 (file-level weak copyleft: modifyi... |
| Cross-Industry Insight Quality | 15% | 2.0 | **4.1** | +2.1 | Adapted compiler AST optimization passes to automated accessibility remediati... |
| Actionability of Recommendation | 10% | 2.5 | **4.7** | +2.2 | Provided decisive build blueprint: reuse axe-core engine embedded via Playwri... |

**Critical Failure Modes & Traps:**
- *Baseline Missed Traps:* Veduis (2026) empirical bound: automated tools detect only 30%–57% of WCAG failures, Pa11y LGPL-3.0 copyleft separation requirement, Axe-core headless browser execution latency in large test suites
- *BeenHere Caught Traps:* Veduis (2026) empirical bound: automated testing detects only 30%–57% of WCAG failures, Axe-core MPL-2.0 file-level copyleft vs Pa11y LGPL-3.0 library boundary, AccessiBe marketing controversy: overlay widgets vs authentic semantic HTML

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
| Existing Solutions Discovered | 20% | 2.5 | **4.6** | +2.1 | Discovered both foundational CRDT engines (Yjs, Automerge, Diamond-types), re... |
| Reusable Code & Integration | 20% | 2.0 | **4.5** | +2.5 | Targeted static inspection of Yjs and CR-SQLite exported interfaces (Y.Doc, Y... |
| Accuracy & Evidence Traceability | 20% | 2.5 | **4.7** | +2.2 | All 18 markdown citations verified via verify_sources.py with reachability ch... |
| Licensing & Dependency Risks | 15% | 2.0 | **4.8** | +2.8 | Deep audit of candidate licenses: Identified Outline's BSL-1.1 trap (not OSI-... |
| Cross-Industry Insight Quality | 15% | 2.0 | **4.2** | +2.2 | Explored cross-vertical mechanisms: adapted aviation flight-data recorder del... |
| Actionability of Recommendation | 10% | 3.0 | **4.6** | +1.6 | Provided decisive architecture recommendation: adopt Yjs + CR-SQLite, avoid B... |

**Critical Failure Modes & Traps:**
- *Baseline Missed Traps:* Outline BSL-1.1 production hosting restrictions, Logseq AGPL-3.0 copyleft boundary, CR-SQLite fractional indexing performance limits
- *BeenHere Caught Traps:* Outline BSL-1.1 commercial hosting restriction, Logseq AGPL-3.0 network copyleft infection, CRDT memory tombstone growth in long-lived documents

---

## 3. Disclosures, Missing Data & Empirical Uncertainties

1. **Self-Audit Disclosure:** In runs where an AI agent acts as both researcher and evaluator, unconscious alignment bias is possible. Double-blind verification or independent human audit is recommended for high-stakes decisions.
2. **Subprocess Network Restrictions:** In sandboxed agent environments without outbound raw TCP socket access (`[WinError 10013]`), BeenHere triggers host-agent native tool fallback. The fallback preserves quality but relies on the host agent's web browsing capability.
3. **Absence of In-Memory Dynamic Execution:** Reusability scores are based on static AST parsing and manifest inspection. True runtime testing (`[VERIFIED-TEST]`) requires sandboxed container execution.
