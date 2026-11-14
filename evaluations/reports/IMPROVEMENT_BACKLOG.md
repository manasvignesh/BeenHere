# BeenHere v1.1 Prioritized Engineering & Research Improvement Backlog

> **Document Version:** 1.1.0-alpha  
> **Date:** November 14, 2026  
> **Source Baseline:** Empirical Benchmark Audit & Comparative Evaluation (Run ID: `43452202423`)  
> **Scope:** Concrete, evidence-backed improvements to BeenHere's research quality, discovery breadth, and tool reliability.

---

## 1. Executive Summary

This backlog ranks identified weaknesses in BeenHere based on **empirical defect evidence** gathered during real-world agent executions in Phase 2.5, Phase 5 (OpenAI Codex), and Phase 1 benchmarking.

Every issue is prioritized by **Severity**, accompanied by **Reproduction Steps**, **Supporting Evidence**, **Proposed Technical Solution**, **Implementation Complexity**, and **Measurable Success Metrics**.

---

## 2. Prioritized Issue Register

```
┌──────┬─────────────────────────────────────────────────┬──────────┬────────────┐
│ Rank │ Issue Title                                     │ Severity │ Complexity │
├──────┼─────────────────────────────────────────────────┼──────────┼────────────┤
│ #1   │ Concept Expander Fragility on Unflagged Inputs  │ CRITICAL │ Medium     │
│ #2   │ GitHub Search Query Precision & Fork Filtering  │ HIGH     │ Low-Medium │
│ #3   │ Lack of Dedicated Commercial Product Discovery  │ HIGH     │ Medium     │
│ #4   │ Subprocess Sandbox Socket Denial Friction       │ MEDIUM   │ Low        │
│ #5   │ Academic Search Noise & S2 Rate Limiting        │ MEDIUM   │ Low        │
│ #6   │ JS/TS Barrel File & Re-Export Resolution Gap    │ MEDIUM   │ Medium     │
│ #7   │ Report Anti-Percentage & Evidence Linting Gap   │ LOW-MED  │ Low        │
└──────┴─────────────────────────────────────────────────┴──────────┴────────────┘
```

---

### Issue #1: Concept Expander Fragility on Unflagged Raw Inputs (CRITICAL)

* **Severity:** **CRITICAL** (Blocks core discovery pipeline unless manual flags are supplied)
* **Affected Modules:** `scripts/concept_expander.py`
* **Reproduction Steps:**
  ```bash
  python scripts/concept_expander.py --concept "AI recruitment platform" --json
  ```
* **Supporting Evidence:**
  The output produces `technical_primitive_queries: []`, `cross_vertical_queries: []`, `academic_queries: []`, `hypotheses_to_verify: []`, and only 1 direct query (`["recruitment platform"]`). The script relies on an 8-word hardcoded dictionary (`consensus`, `turn_taking`, `arbitration`, `memory`, `debate`, `simulation`, `streaming`, `collaboration`). When none of those 8 words are matched in the raw pitch, concept expansion completely collapses.
* **Proposed Technical Solution:**
  1. Expand the static taxonomy from 8 mechanisms to 30+ universal computational mechanisms (including `extraction`, `matching`, `scheduling`, `caching`, `synchronization`, `auditing`, `routing`, `serialization`, `optimization`).
  2. Implement heuristic compound noun and verb extraction to infer candidate mechanisms when exact catalog matches are absent.
  3. Add an automated fallback generator that derives academic and primitive query combinations from the top extracted keywords.
* **Implementation Complexity:** Medium (Standard library regex/heuristics).
* **Measurable Target:** 100% of concept pitches will generate at least 4 queries per category and 3+ hypotheses without requiring manual CLI flags.

---

### Issue #2: GitHub Search Query Precision & Abandoned Fork Filtering (HIGH)

* **Severity:** **HIGH** (Pollutes search results with toy projects and student homework)
* **Affected Modules:** `scripts/github_search.py`
* **Reproduction Steps:**
  ```bash
  python scripts/github_search.py --queries "recruitment ats" "accessibility testing" --json
  ```
* **Supporting Evidence:**
  Raw query strings return abandoned personal repos with 0 stars, school assignments, and unmaintained forks alongside major libraries. The agent must manually filter through dozens of irrelevant entries.
* **Proposed Technical Solution:**
  1. Add automatic GitHub query qualifiers: `stars:>=10`, `archived:false`, and `pushed:>={1_year_ago}`.
  2. Implement an automated multi-tier star categorization:
     - *Tier 1 (Canonical Frameworks):* Stars > 1,000.
     - *Tier 2 (Emerging Modular Primitives):* Stars 50–1,000 with active commits in the last 180 days.
  3. Filter out personal forks (`fork:false` by default, unless explicitly requested).
* **Implementation Complexity:** Low-Medium (Query synthesis and response post-processing).
* **Measurable Target:** 80%+ reduction in sub-10-star abandoned repositories in initial search results.

---

### Issue #3: Lack of Dedicated Commercial Product Discovery Tooling (HIGH)

* **Severity:** **HIGH** (Forces agent to rely on general LLM memory or ad-hoc web searches for SaaS competitors)
* **Affected Modules:** Missing tooling; `references/product_discovery.md`
* **Reproduction Steps:**
  Observe Step 4 of the protocol. Repositories have `github_search.py`, papers have `paper_search.py`, but commercial products have no executable discovery utility.
* **Supporting Evidence:**
  In baseline research runs, commercial products are frequently missed or hallucinated because the agent does not systematically query software directories or pricing models.
* **Proposed Technical Solution:**
  1. Create `scripts/product_search.py` using Python's standard library to query public search endpoints (e.g. curated AlternativeTo API/feeds or structured search operators for commercial SaaS).
  2. Format structured competitor comparison matrices capturing: Product Name, Pricing Model (Freemium, Per-Seat, Enterprise), Core Claim, and Architectural Dependency.
* **Implementation Complexity:** Medium.
* **Measurable Target:** Standardized, verified commercial comparator tables with documented pricing models across 100% of deep investigation runs.

---

### Issue #4: Subprocess Sandbox Socket Denial Friction (MEDIUM)

* **Severity:** **MEDIUM** (Triggers error handling in sandboxed agent environments like OpenAI Codex)
* **Affected Modules:** `scripts/github_search.py`, `scripts/repo_inspector.py`, `scripts/paper_search.py`
* **Reproduction Steps:**
  Execute BeenHere scripts inside an agent environment where child processes lack outbound socket permissions (`[WinError 10013]` / `WSAEACCES`).
* **Supporting Evidence:**
  In the real Codex execution (`docs/CODEX_END_TO_END_TEST.md`), `github_search.py` failed with exit code 2 and logged `recruitment-script-network-errors.json`. Codex had to pivot manually to native host tools.
* **Proposed Technical Solution:**
  1. Add a standard `--stdin` / `--import-json` mode to all search and inspection tools.
  2. Allow host agents to pipe host-fetched GitHub API JSON responses directly into BeenHere scripts for deduplication, schema normalization, and table formatting without spawning outbound child network sockets.
* **Implementation Complexity:** Low.
* **Measurable Target:** Zero fatal exit codes in sandboxed environments; seamless transition between direct socket and piped host-agent data.

---

### Issue #5: Academic Search Noise & Semantic Scholar Rate-Limiting (MEDIUM)

* **Severity:** **MEDIUM** (HTTP 429 errors on Semantic Scholar; off-topic papers from broad concept terms)
* **Affected Modules:** `scripts/paper_search.py`
* **Reproduction Steps:**
  ```bash
  python scripts/paper_search.py --queries "collaborative notes" "voice debate" --providers semantic_scholar openalex
  ```
* **Supporting Evidence:**
  Unauthenticated Semantic Scholar calls frequently return HTTP 429 after 2 requests. Additionally, querying OpenAlex with broad natural language often pulls theoretical sociology or physics papers rather than computer science/software engineering foundations.
* **Proposed Technical Solution:**
  1. Make OpenAlex the primary default provider with polite `User-Agent` email headers; degrade Semantic Scholar gracefully.
  2. Add automatic Field-of-Study filtering in OpenAlex (`filter=concepts.id:C41008148` for Computer Science) to eliminate non-engineering papers.
* **Implementation Complexity:** Low.
* **Measurable Target:** Zero HTTP 429 failures in automated runs; >80% relevance score for returned academic papers.

---

### Issue #6: JavaScript/TypeScript Barrel File & Re-Export Resolution Gap (MEDIUM)

* **Severity:** **MEDIUM** (Misses public interfaces in modern TypeScript monorepos)
* **Affected Modules:** `scripts/integration_analyzer.py`
* **Reproduction Steps:**
  Inspect a TypeScript library whose `src/index.ts` contains `export * from './components/Manager'` rather than inline class definitions.
* **Supporting Evidence:**
  The current regex tokenizer in `parse_js_ts_source` only captures immediate line definitions (`export class ...`, `export function ...`). It does not follow relative barrel exports or parse `package.json` subpath exports.
* **Proposed Technical Solution:**
  1. Enhance `parse_js_ts_source` to recognize re-export statements (`export * from '...'`, `export { Foo } from '...'`).
  2. If given a directory or entrypoint file, automatically inspect referenced local submodules to resolve exported interfaces.
* **Implementation Complexity:** Medium (Multi-file local static analysis).
* **Measurable Target:** 95%+ exported symbol recall on TypeScript monorepos and npm packages.

---

### Issue #7: Report Anti-Percentage & Evidence Linting Gap (LOW-MEDIUM)

* **Severity:** **LOW-MEDIUM** (Allows speculative numbers or untagged claims to slip into reports unnoticed)
* **Affected Modules:** `scripts/verify_sources.py`
* **Reproduction Steps:**
  Run `verify_sources.py` on a markdown report containing arbitrary claims like *"Provides 85% code reuse"* or *"Reduces latency by 10x"*.
* **Supporting Evidence:**
  `verify_sources.py` currently only checks HTTP link reachability. It completely ignores unbacked quantitative assertions or missing evidence tags.
* **Proposed Technical Solution:**
  1. Add an automated research quality linter mode to `verify_sources.py` (`--audit-claims`).
  2. Scan for:
     - Pseudo-quantitative percentage patterns (`\b\d+%\s*(?:code\s*reuse|unique|faster)`).
     - Sentences making technical claims without an accompanying evidence tag (`[VERIFIED-SOURCE]`, `[VERIFIED-METADATA]`, `[INFERRED]`).
     - Broken local markdown anchor links.
* **Implementation Complexity:** Low.
* **Measurable Target:** 100% automated detection of Anti-Percentage Rule violations in CI and report audits.

---

## 3. Recommended Implementation Roadmap for v1.1

1. **Sprint 1 (Core Intelligence & Expander):** Implement Issue #1 (Taxonomy expansion) and Issue #2 (GitHub search qualifiers & star tiers).
2. **Sprint 2 (Robustness & Sandboxing):** Implement Issue #4 (Piped JSON mode for sandboxes) and Issue #5 (OpenAlex Computer Science filtering).
3. **Sprint 3 (Deep Analysis & Verification):** Implement Issue #7 (Automated claim/percentage linter in `verify_sources.py`) and Issue #6 (TypeScript re-export parsing).
4. **Sprint 4 (Ecosystem & Products):** Implement Issue #3 (Dedicated commercial product discovery utility).
