# BeenHere Evaluation System Audit & Research Quality Gap Analysis

> **Audit Date:** November 14, 2026  
> **Audited Commit Baseline:** `9c33e91` (v1.0.0-beta.1)  
> **Auditor:** Lead AI Research Engineer & Evaluation Specialist  
> **Scope:** Full inspection of evaluation harnesses, scripts, benchmark fixtures, and research artifacts.

---

## 1. Executive Summary & Core Finding

BeenHere possesses an extensive automated testing infrastructure consisting of **82 passing unit tests** across Python 3.8–3.13 on Linux, Windows, and macOS, as well as a **10-case benchmark runner** (`scripts/benchmark_runner.py`).

However, an engineering audit reveals a critical distinction:

> [!WARNING] The Benchmark Reality Gap
> **Existing automated benchmarks primarily measure *structural compliance* and *tool execution correctness*. They do NOT measure *research accuracy*, *source verification*, or *comparative superiority* over standard LLM research.**
> 
> A 10/10 PASS on `benchmark_runner.py` merely verifies that `concept_expander.py` generates non-empty dictionaries when fed hand-curated input parameters. It does not establish that BeenHere helps a developer discover better prior art, avoid legal liability, or write less boilerplate than an ordinary AI coding agent.

To achieve genuine research superiority in v1.1, we must separate what our tools actually measure from what they only assume.

---

## 2. Granular Audit Across Six Evaluation Dimensions

```
┌────────────────────────────────────────────────────────────────────────┐
│                      WHAT OUR TESTS CURRENTLY MEASURE                  │
├───────────────────────────────────┬────────────────────────────────────┤
│ 1. Structural Compliance          │ ✅ High (Schemas, keys, types)     │
│ 2. Tool Execution Correctness     │ ✅ High (AST parse, TOML fallback) │
├───────────────────────────────────┴────────────────────────────────────┤
│                      WHAT OUR TESTS DO NOT YET MEASURE                 │
├───────────────────────────────────┬────────────────────────────────────┤
│ 3. Research Accuracy & Recall     │ ❌ Not Measured by Benchmarks      │
│ 4. Source Evidence Traceability   │ ⚠️ Partially Audited (links only)  │
│ 5. Practical Engineering Utility  │ ❌ Not Measured Automatically      │
│ 6. Comparative Performance        │ ❌ Zero Automated Baseline Delta   │
└───────────────────────────────────┴────────────────────────────────────┘
```

### Dimension 1: Structural Compliance (Fully Covered)
* **What is measured:** JSON schema adherence, required dictionary keys (`name`, `version`, `dependencies`), presence of required files (`SKILL.md`, templates, references), frontmatter delimiters, and output formatting.
* **Current status:** Verified across `tests/test_core.py`, `tests/test_phase4.py`, and `scripts/validate_skill.py`.
* **Limitation:** A report can be 100% structurally compliant while containing completely fabricated technical assertions.

### Dimension 2: Tool Execution Correctness (Fully Covered)
* **What is measured:** Python AST parsing, regex export tokenization in JS/TS, TOML manifest parsing (`pyproject.toml`, `Cargo.toml`), HTTP error handling, rate-limit parsing, socket exception fallbacks (`[WinError 10013]`), and canonical path resolution across Windows/macOS.
* **Current status:** Hardened across 82 automated unit tests passing across Python 3.8–3.13.
* **Limitation:** Correctly extracting AST symbols from a file does not guarantee that the agent chose the *right* file to inspect or correctly synthesized its integration feasibility.

### Dimension 3: Research Accuracy & Recall (Not Measured by Existing Benchmarks)
* **What is measured currently:** None of the existing automated benchmark runs actually execute GitHub searches, academic queries, or product lookups.
* **The `benchmark_runner.py` Reality:** `benchmark_runner.py` feeds pre-extracted mechanisms, primitives, and adjacent industries from `tests/benchmark_cases.json` into `concept_expander.py`. It tests deterministic dictionary generation in milliseconds offline.
* **Critical Discovery:** When `concept_expander.py` is invoked with a raw user pitch without manual CLI flags (e.g., `python scripts/concept_expander.py --concept "AI recruitment platform"`), it produces **zero** technical primitive queries, **zero** cross-vertical queries, and **zero** hypotheses. The benchmark runner masked this defect because its test fixtures pre-populated the flags.

### Dimension 4: Source Verification (Partially Covered)
* **What is measured:** `scripts/verify_sources.py` validates that markdown HTTP links are reachable (status code < 400) and counts occurrences of evidence tags (`[VERIFIED-SOURCE]`, `[VERIFIED-METADATA]`).
* **Limitation:** It verifies that a URL exists; it does *not* verify that the target URL actually supports the claim made in the sentence preceding it. Furthermore, it cannot verify in-repo relative links or local file references.

### Dimension 5: Practical Engineering Utility (Qualitative Only)
* **What is measured currently:** Human-reviewed in Phase 2.5 (`docs/QUALITY_BENCHMARK.md`) and verified in OpenAI Codex (`docs/CODEX_END_TO_END_TEST.md`).
* **Evidence of Real Utility:**
  - Catching BSL-1.1 non-compete rider in `outline/outline` (preventing commercial SaaS copyright infringement).
  - Catching transitive PyMuPDF AGPL dual-license risk in `horilla/horilla-hr`.
  - Detecting monorepo migration from `letta` (Python) to `@letta-ai/letta-code` (TypeScript/Bun).
* **Limitation:** These successes were achieved through manual expert evaluation and real-world agent runs; they are not captured by automated CI tests.

### Dimension 6: Comparative Performance (Previously Missing)
* **What is measured currently:** Zero comparative benchmarks existed prior to v1.1 Phase 1.
* **The Gap:** We claimed BeenHere was superior to ordinary LLM research based on qualitative observation, but lacked a reproducible, blinded harness to measure the exact delta in discovery breadth, code reusability, and licensing risk detection.

---

## 3. Script-by-Script Audit & Vulnerability Register

| Script | Intended Function | Verified Strength | Latent Weakness / Defect |
| :--- | :--- | :--- | :--- |
| **`concept_expander.py`** | Expands concept into multi-tier query plan | Deterministic keyword deduplication; clean separation of hypotheses from facts. | **High Fragility:** Completely fails to generate multi-tier queries if user pitch does not match 8 hardcoded catalog keywords and manual CLI flags are omitted. |
| **`github_search.py`** | Discovers open-source repositories via GitHub REST API | Resilient rate-limit parsing; prompt-injection sanitization. | **Search Relevance Gap:** Relies purely on keyword matching; cannot perform semantic ranking or filter out abandoned personal forks without star thresholds. |
| **`repo_inspector.py`** | Programmatically inspects repo files, manifests, and licenses | Solves API `NOASSERTION` by inspecting raw `LICENSE` files; parses root manifests. | **Shallow Traversal:** Does not automatically locate entrypoint source files; requires the user/agent to manually supply `--source-file`. |
| **`paper_search.py`** | Discovers peer-reviewed academic literature via OpenAlex, arXiv, S2 | Multi-provider fallback; DOI normalization; retraction detection. | **Query Noise:** Academic keywords combined with raw concept tokens frequently yield low-relevance theoretical papers rather than algorithmic foundations. |
| **`integration_analyzer.py`** | Statically analyzes AST symbols, manifests, and licenses | Pure Python standard library AST parser; robust TOML fallback; detects PyMuPDF/Redis hazards. | **No Type/Interface Resolution:** JS/TS parser is regex-based, missing complex mapped types, re-exports (`export * from`), and monorepo workspaces. |
| **`verify_sources.py`** | Audits links and evidence tags | Fast HEAD/GET reachability check; classifies 6 evidence tiers. | **Semantic Blindness:** Cannot verify whether the text inside an external URL actually substantiates the claim. |
| **`benchmark_runner.py`** | Benchmarks BeenHere quality | Fast offline execution; validates schema completeness. | **False Confidence:** Only tests offline dictionary assembly from pre-curated cases; does not execute research or measure output quality. |

---

## 4. Key Takeaways for BeenHere v1.1 Phase 1

1. **Stop Conflating Schema Validation with Research Superiority:** We must never cite `python scripts/benchmark_runner.py` as proof that BeenHere provides better answers than an LLM.
2. **Build an Empirical Comparative Harness:** We must deploy `evaluations/evaluate.py` to evaluate real outputs from identical prompts under baseline and BeenHere conditions.
3. **Automate Quality Regression Checks:** Create tests in `tests/test_research_quality.py` that actively catch unverified percentages, broken citations, and unsupported claims in research reports.
