# BeenHere Capability Audit: Repository Analysis & Code Reusability

> **Audit Date:** 2026-11-14  
> **Auditor:** Lead Research Engineer & Systems Architect  
> **Target Scope:** `scripts/github_search.py`, `scripts/repo_inspector.py`, `scripts/integration_analyzer.py`, `scripts/concept_expander.py`, `references/code_reusability.md`

---

## 1. Executive Summary

This audit assesses BeenHere's existing capabilities for repository discovery, metadata inspection, code-level analysis, and reuse recommendation. It identifies existing strengths, implementation gaps, and architectural components requiring improvement in Phase 2.

---

## 2. Component-by-Component Assessment

### A. GitHub Discovery (`scripts/github_search.py`)
- **Existing Strengths:**
  - Multi-query aggregation and cross-query deduplication.
  - Graceful rate-limit detection and parsing (`X-RateLimit-Reset`).
  - Network socket restriction fallback guidance for sandboxed agents (`[WinError 10013]`).
- **Gaps & Shortcomings:**
  - Ranks results primarily by star count, reinforcing popularity bias.
  - Does not filter by license clearance or maintenance recency during search.
  - Emits unstructured repository lists without side-by-side comparative metadata.

### B. Repository Metadata & Maintenance Inspector (`scripts/repo_inspector.py`)
- **Existing Strengths:**
  - Fetches repository metadata, issue counts, commit dates, releases, and license keys.
  - Categorizes licenses into 5 legal tiers (`permissive`, `weak_copyleft`, `strong_copyleft`, `network_copyleft`, `source_available`).
  - Detects package dependency manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.).
  - Includes prompt-injection defenses for untrusted README text.
- **Gaps & Shortcomings:**
  - Evaluates repositories strictly in isolation (one at a time).
  - Lacks cross-repository diffing: cannot compare two candidate repos side-by-side to determine which has better maintenance, cleaner licenses, or fewer dependencies.
  - Relies on declared GitHub SPDX keys, which can be `NOASSERTION` or inaccurate relative to actual file headers.

### C. Deep Integration Analyzer (`scripts/integration_analyzer.py`)
- **Existing Strengths:**
  - Standard-library AST parsing for Python (classes, methods, functions, docstrings, `__all__`, environment variables).
  - Regex-based tokenization for JavaScript and TypeScript exports.
  - Robust manifest parsers for `package.json`, `pyproject.toml`, `requirements.txt`, and `Cargo.toml`.
  - Nuanced BSL-1.1 grant extraction (Licensor, Additional Use Grant, Change Date, Change License).
  - Single-repository reuse posture assignment (`evaluate_reuse_posture`).
- **Gaps & Shortcomings:**
  - `evaluate_reuse_posture` uses coarse heuristics that output only generic postures without structured explanations for fit, pitfalls, remaining engineering work, or pre-adoption verification.
  - No multi-candidate decision engine: cannot contrast Candidate A vs Candidate B to determine whether Candidate A should be adopted as a dependency while Candidate B is used merely as an architectural reference.
  - Does not evaluate cross-language interoperability (e.g., integrating a Rust crate into a Python or TypeScript host application).

### D. Concept Expander (`scripts/concept_expander.py`)
- **Existing Strengths:**
  - Fast, deterministic expansion using Python standard library.
  - Broad taxonomy for common domains (recruitment, accessibility, offline-first sync, robotics, supply chain, security).
  - Deduplicated multi-tier query matrices.
- **Gaps & Shortcomings:**
  - Fallback decomposition in Phase 1.1 mechanically appended generic software nouns (`"pipeline architecture"`, `"parser and serializer"`, `"workflow runner"`) to unfamiliar domain words, producing unnatural queries (e.g. `"mycorrhizal parser and serializer"`).
  - Lacks confidence scoring: does not signal to the host agent when an expansion is low-confidence or in need of manual refinement.

### E. Reference Documentation (`references/code_reusability.md`)
- **Existing Strengths:**
  - Clear 6-tier legal clearance taxonomy (Permissive, Weak Copyleft, Strong Copyleft, Network Copyleft, Source-Available, Unlicensed).
  - Golden rule: Never declare a project reusable solely based on marketing claims or stars.
  - Maintenance freshness criteria and extraction-vs-dependency rules.
- **Gaps & Shortcomings:**
  - Existed only as prose guidelines; was not programmatically executed as a structured multi-candidate decision algorithm.

---

## 3. Prioritized Improvement Plan for Phase 2

1. **Build `scripts/repo_comparator.py`:** A dedicated, standard-library multi-candidate comparison engine that evaluates 2+ repositories side-by-side across functional overlap, licenses, APIs, language compatibility, maintenance, limitations, and evidence completeness.
2. **Implement Evidence-Backed Recommendation Logic:** Formalize 7 distinct postures (`ADOPT_AS_DEPENDENCY`, `INTEGRATE_THROUGH_API`, `EXTRACT_REUSABLE_COMPONENT`, `FORK_AND_ADAPT`, `USE_AS_ARCHITECTURAL_REFERENCE`, `REJECT_FOR_USE_CASE`, `INVESTIGATE_FURTHER`) with the 5 mandatory explanatory dimensions.
3. **Refine Concept Expander Fallback:** Eliminate unnatural generic buzzwords in `scripts/concept_expander.py`, prioritize user phrases, and attach confidence levels with host-agent refinement prompts.
4. **Develop Three Grounded Comparison Scenarios:** Provide reproducible evaluations for Collaborative Editing (Yjs vs Automerge vs Loro), Document Extraction (Docling vs PyPDF vs Horilla), and Accessibility Auditing (Axe-core vs Pa11y vs ESLint JSX A11y).
5. **Output Generators:** Generate concise comparison markdown tables and comprehensive integration blueprints with architecture boundaries, contracts, checklists, and validation tests.
