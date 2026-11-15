# BeenHere — Phase 2.1: Comparator Reliability & Provenance Hardening Audit

**Date:** 2026-11-15  
**Workspace:** `C:\Users\Manas\BeenHere`  
**Base Commit:** `788a242`  
**Author:** BeenHere Open-Source Compliance & Research Engineering Team  

---

## 1. Executive Summary

Phase 2.1 conducted an exhaustive reliability and open-source legal compliance audit of BeenHere's multi-repository comparison engine (`scripts/repo_comparator.py`), recommendation postures, evidence provenance tagging, and integration blueprint generator.

### Core Objectives
1. **Eliminate False Legal Certainties:** Replace automated, unqualified legal conclusions with rigorous, qualified risk assessments across copyleft boundaries, AGPL network interfaces, transitive dependencies, and BSL-1.1 Additional Use Grants.
2. **Harden Evidence Provenance:** Ensure that `[VERIFIED-SOURCE]` is never emitted without genuine, retrieved source file AST inspection. Distinguish live verified evidence from cached records, scenario fixtures, inferences, and uninspected claims.
3. **Prevent Stale Metadata Misrepresentation:** Prevent historical snapshot commit dates and push activity timestamps from being presented as current live GitHub activity.
4. **Implement Recommendation Safeguards:** Prevent automated engines from recommending adoption solely on the basis of matching languages or permissive licenses when API entrypoints or manifests are uninspected.
5. **Add 10 Adversarial Regression Tests:** Validate real-world resilience against hostile fixtures, fabricated claims, missing licenses, dual terms, and uncertain linkage boundaries.

---

## 2. Audit of Legal Decision Rules

### Flawed Assumptions Identified & Corrected

| Area | Flawed Assumption (Pre-2.1) | Legal Reality & Correction (Phase 2.1) |
| :--- | :--- | :--- |
| **AGPL Network API** | Assumed that accessing an AGPL-3.0 component over a network API is *guaranteed* safe and never triggers copyleft obligations. | Network API separation is an architectural isolation technique, but legal consensus varies on tightly coupled APIs. Many corporate open-source policies (e.g. Google) strictly ban AGPL regardless of network isolation. Flagged with mandatory organizational policy checklists. |
| **BSL-1.1 Commercial SaaS** | Assumed BSL-1.1 unconditionally prohibits all commercial SaaS deployments across all projects. | BSL-1.1 terms depend on each licensor's customized "Additional Use Grant" and "Change Date". Some grants permit production use below user or revenue limits. Added grant inspection checklists and qualified commercial assumptions. |
| **Transitive Copyleft** | Assumed any transitive copyleft dependency automatically infects and invalidates the entire host application. | Transitive copyleft impact depends on linkage (static vs dynamic), invocation boundaries (CLI subprocess vs embedded library), and whether client software is distributed. Gated with linkage audits (`INVESTIGATE_FURTHER` when linkage is unconfirmed). |
| **Permissive License = Adoption** | Assumed that a permissive license (MIT/Apache) and active push date alone justify confident `ADOPT_AS_DEPENDENCY`. | An MIT library with uninspected API entrypoints, zero tests, or missing manifests cannot be safely adopted. Required AST entrypoint verification before granting confident adoption with low uncertainty. |
| **Dual-Licensing Terms** | Ignored dual-licensing options or assumed commercial terms were unavailable. | Identified dual-licensing boundaries (e.g. AGPL or Commercial); flagged for commercial terms review when commercial pricing/scope is uninspected. |

### The Six Legal Assessment Distinctions
Every candidate evaluated by `repo_comparator.py` now includes a structured, 6-part machine-readable legal evaluation:

1. **Confirmed License Identity:** Formally declared SPDX identifier, confirmed via LICENSE file text inspection vs uninspected metadata.
2. **Observed Dependency Relationships:** Direct and transitive dependencies inspected, noting linkage boundaries (dynamic package, bundled, or microservice).
3. **Potential Obligations:** Conditional duties attaching upon distribution or network deployment (e.g., copyright notice retention, patent peace, or reciprocal source sharing).
4. **Unresolved Compatibility Questions:** Ambiguities requiring legal clarification (e.g., undefined BSL Additional Use Grants, uninspected commercial dual-licensing terms, or unconfirmed linkage paths).
5. **Confirmed Technical Incompatibilities:** Definite runtime or architectural barriers (e.g., language mismatches without bindings, monolithic applications).
6. **Organizational Policies Requiring Human Input:** Enterprise open-source governance requirements (e.g., corporate AGPL prohibitions, Contributor License Agreements).

---

## 3. Evidence Provenance & Tracking Architecture

### Machine-Readable Evidence Records
Candidate evaluations now produce machine-readable evidence items (`evidence_records`) tracking:
- `claim`: Grounded factual claim.
- `provenance_type`: `LIVE_VERIFIED`, `CACHED_RECORD`, `SCENARIO_FIXTURE`, `INFERRED`, `MISSING_EVIDENCE`, `UNVERIFIED_CLAIM`.
- `source_id`: Raw URL, local file path, or fixture slug.
- `source_type`: `LICENSE_FILE`, `MANIFEST`, `SOURCE_CODE`, `API_METADATA`, `HEURISTIC_RULE`, `FIXTURE_ASSERTION`.
- `retrieval_timestamp`: ISO 8601 capture timestamp or snapshot date.
- `excerpt_or_symbol`: Concrete AST symbol name or license text snippet.
- `verification_method`: `PARSED_AST`, `TEXT_MATCH`, `FIXTURE_LOADED`, `MANUAL_REVIEW`, `RUNTIME_TESTED`, `HEURISTIC_INFERENCE`, `UNVERIFIED`.
- `limitations`: Contextual limitations (e.g. offline snapshot, untested in sandbox).

### Provenance Tag Enforcement
- `[VERIFIED-LIVE]`: Emitted only when live repository assets were retrieved and inspected.
- `[VERIFIED-CACHED]`: Emitted when verified from local offline caches.
- `[SCENARIO-FIXTURE]`: Emitted when evidence originates from saved benchmark fixtures.
- `[INFERRED]`: Emitted for deterministic rule deductions.
- `[MISSING-EVIDENCE]`: Emitted when required evidence is absent.
- `[UNVERIFIED-CLAIM]`: Emitted when external text asserts a claim that was not verified in source. Fabricated `[VERIFIED-SOURCE]` tags are detected and stripped.

---

## 4. Rechecked Comparison Scenarios Audit

All three comparison scenario fixtures were audited and updated with machine-readable provenance metadata:

### Scenario A: Real-Time Collaborative Editing
- **Fixture:** `evaluations/comparisons/scenario_a_collaborative_editing.json`
- **Context:** `evaluations/comparisons/context_scenario_a.json` (Target: JavaScript / Proprietary SaaS)
- **Status:**
  - `yjs/yjs`: Permissive MIT, active maintenance, verified exported classes (`Doc`, `Text`, `Array`, `Map`). Provenance marked `SCENARIO_FIXTURE`. Tombstone memory growth pitfall noted.
  - `automerge/automerge`: Permissive MIT, Rust core with official npm WASM bindings. WASM bridging serialization overhead noted as architectural trade-off.
  - `loro-dev/loro`: Permissive MIT, Rust core with npm WASM bindings. Rich-text CRDT ecosystem maturity trade-off noted.

### Scenario B: Recruitment Resume Document Extraction
- **Fixture:** `evaluations/comparisons/scenario_b_document_extraction.json`
- **Context:** `evaluations/comparisons/context_scenario_b.json` (Target: Python / Proprietary SaaS)
- **Status:**
  - `docling-project/docling`: Permissive MIT, PyPI package, verified AST classes (`DocumentConverter`, `PdfFormatOption`, `DoclingDocument`). 2.5GB container footprint noted; pre-production testing required.
  - `py-pdf/pypdf`: BSD-3-Clause, lightweight, verified AST classes (`PdfReader`, `PdfWriter`, `PageObject`). Unstructured text stream pitfall explicitly highlighted for 2-column resumes.
  - `horilla/horilla-hr`: Monolithic Django application incorporating `PyMuPDF` (AGPL-3.0 / Artifex dual license). Assigned `REJECT_FOR_USE_CASE` under proprietary commercial SaaS deployment assumptions, explaining the copyleft contamination and monolithic architecture.

### Scenario C: Automated Accessibility Auditing
- **Fixture:** `evaluations/comparisons/scenario_c_accessibility_testing.json`
- **Context:** `evaluations/comparisons/context_scenario_c.json` (Target: JavaScript / Developer CLI)
- **Status:**
  - `dequelabs/axe-core`: MPL-2.0 weak copyleft (safe as unmodified package dependency). Live DOM requirement and WCAG rule coverage boundaries noted.
  - `pa11y/pa11y`: LGPL-3.0, verified wrapper around Axe-core; abstraction layer trade-off noted.
  - `jsx-eslint/eslint-plugin-jsx-a11y`: MIT, AST static linter for JSX; cannot evaluate computed DOM colors or keyboard focus traps.

---

## 5. Integration Blueprint Improvements

Integration blueprints generated via `--blueprint` now provide:
1. **Supporting Evidence & Provenance Audit Table:** Discloses exact source URLs, verification methods, and snapshot dates.
2. **Operational & Deployment Assumptions:** Declares target runtime, deployment environment, and runtime container testing status.
3. **Verified Entrypoints vs. Proposed Adapter Interface:**
   - Table of verified upstream exported symbols (from AST).
   - Clear declaration that the anti-corruption adapter is a proposed architectural boundary for the host application (`[PROPOSED-ADAPTER-DESIGN]`), not an upstream contract.
4. **Step-by-Step Integration Sequence:** Mermaid flowchart and defensive error-handling guidelines.
5. **Qualified Legal Checklist:** Direct and transitive dependency compliance, attribution guidelines, and corporate open-source policy reviews.
6. **Required Validation Suite:** Contract tests, boundary fault tests, memory leak checks, and license CI checks.
7. **Remaining Unknowns & Technical Debt:** Explicit warnings for any missing evidence.

---

## 6. Adversarial Regression Test Suite

Ten new regression tests were added in `tests/test_repo_comparator.py` under `TestComparatorReliabilityAndAdversarial`:

1. `test_adversarial_1_missing_license_file`: Unlicensed repositories or `NOASSERTION` without text must be rejected under international copyright law with prohibitive complexity.
2. `test_adversarial_2_conflicting_license_declarations`: Discrepancy between manifest and source file text headers triggers `INVESTIGATE_FURTHER` with `HIGH` uncertainty.
3. `test_adversarial_3_dual_licensing_unknown_commercial_terms`: Dual licensing with uninspected commercial terms triggers `INVESTIGATE_FURTHER` and checklist for commercial pricing review.
4. `test_adversarial_4_agpl_service_boundary_uncertain_obligations`: AGPL service boundary notes legal uncertainty, does not claim unconditional safety, and requires corporate policy review.
5. `test_adversarial_5_transitive_dependency_unknown_linkage`: Transitive copyleft dependency with unconfirmed linkage triggers `INVESTIGATE_FURTHER` and dependency linkage audit.
6. `test_adversarial_6_offline_or_stale_repository_metadata`: Historical snapshots (>365d) flag stale metadata and do not claim current live GitHub activity.
7. `test_adversarial_7_fabricated_verified_source_claims`: Fabricated `[VERIFIED-SOURCE]` tags without inspected source files are stripped and sanitized to `[UNVERIFIED-CLAIM]`.
8. `test_adversarial_8_missing_api_inspection`: Permissive repository with uninspected symbols/source cannot receive confident adoption; triggers `INVESTIGATE_FURTHER`.
9. `test_adversarial_9_many_stars_poor_technical_fit`: 100k-star repository with poor capability match is rejected in favor of a 1k-star direct functional fit.
10. `test_adversarial_10_two_candidates_insufficient_evidence`: Multiple candidates with missing critical evidence trigger `INSUFFICIENT_EVIDENCE` confidence.

---

## 7. Verification Results

- **Unit Test Discovery:** 132 / 132 tests passing (`python -m unittest discover tests -v`) in 0.44s.
- **Structural Benchmarks:** 10 / 10 cases passing (`python scripts/benchmark_runner.py`).
- **Skill Packaging:** `[PASS] VALID` (`python scripts/validate_skill.py`).
- **Evaluation Manifests:** 6 / 6 manifests passing (`python evaluations/evaluate.py --validate evaluations/results`).

---

## 8. Disclaimers & Known Limitations

1. **Non-Legal Advice:** Automated heuristic license categorization does not constitute legal counsel. Enterprise deployments must undergo formal review by qualified legal counsel.
2. **Runtime Verification:** Static manifest parsing and AST extraction cannot guarantee runtime container behavior, dynamic reflection, or network RPC performance. Sandboxed smoke testing is mandatory.
