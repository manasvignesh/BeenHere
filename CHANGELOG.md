# Changelog

All notable changes to the **BeenHere** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] (v1.1 Development)

### Added
- **Cross-Industry Research Intelligence Engine (`scripts/cross_industry_analyzer.py`):** Deterministic tool discovering battle-tested solutions from outside a developer's immediate product category.
  - Extracts underlying computational problem mechanisms distinguishing directly stated requirements, inferred requirements, and candidate hypotheses (`[RESEARCH-HYPOTHESIS]`).
  - Implements anti-buzzword relevance filtering rejecting superficial metaphors (beehive, courtroom trial, quantum thinking).
  - Implements negative-control screening (`NEGATIVE_CONTROL_TRIGGERED` / `NO_TRANSFER_NEEDED`) on basic CRUD apps to prevent unwarranted overengineering.
  - Evaluates engineering transferability across 8 dimensions (`problem_equivalence`, `input_compatibility`, `output_suitability`, `operational_constraints`, `assumptions`, `integration_practicality`, `risk`, `evidence_strength`).
  - Classifies candidate transfers into 6 standardized outcomes: `TRANSFERABLE_IMPLEMENTATION`, `TRANSFERABLE_ALGORITHM`, `TRANSFERABLE_ARCHITECTURAL_PATTERN`, `CONCEPTUAL_INSPIRATION`, `REQUIRES_VALIDATION`, `NOT_TRANSFERABLE`.
  - Enforces the Anti-Percentage Rule across all evaluations and generated report text.
  - Generates standardized Markdown section `### Solutions from Other Industries` with evidence disclosures and concrete validation experiments.
- **Cross-Industry Evaluation Scenarios (`evaluations/cross_industry/`):**
  - `scenario_a_recruitment_matching.json`: Recruitment matching -> Stable matching (Gale-Shapley) & Hungarian algorithm.
  - `scenario_b_multiplayer_matchmaking.json`: Real-time multiplayer matchmaking -> Ride-hailing batch dispatch & Bayesian volatility (Glicko-2).
  - `scenario_c_collaborative_knowledge.json`: Collaborative notes -> CRDTs & Event Sourcing (with Raft consensus evaluated and disqualified as `NOT_TRANSFERABLE` for offline editing).
  - `negative_control_crud_blog.json`: Simple CRUD blog correctly triggering `NO_TRANSFER_NEEDED`.
- **Capability Audit & Regression Suite:**
  - `evaluations/reports/CROSS_INDUSTRY_CAPABILITY_AUDIT.md`: Complete audit of prior cross-vertical methodology vs implemented capabilities.
  - `tests/test_cross_industry_analyzer.py`: 19 comprehensive unit and regression tests covering all 12 criteria, raising the total test suite to 151 passing tests.
- **Repository Comparison Engine (`scripts/repo_comparator.py`):**
  - Structural comparison engine evaluating multi-repository overlap, license compatibility, maintenance signals, and integration postures.
  - Qualified legal risk handling distinguishing confirmed facts from jurisdictional and architectural risk assessments.

---

## [1.0.0-beta.1] - 2026-11-13 (Phase 5: Final Hardening & Public Beta Preparation)

### Added
- **Pure-Python Standard Library TOML Parser Fallback:** Implemented a robust, zero-dependency TOML parser in `scripts/integration_analyzer.py` supporting multiline arrays and inline tables for environments without `tomllib` (Python 3.8, 3.9, and 3.10).
- **Python 3.8 AST Compatibility:** Added AST slice unwrapping (`ast.Index`) and `ast.Str` support for environment variable and `__all__` extraction in `scripts/integration_analyzer.py`.
- **Cross-Platform Canonical Path Normalization:** Standardized installer path resolution in `scripts/install_skill.py` and test fixtures in `tests/test_phase4.py` to handle Windows 8.3 short paths (`RUNNER~1`) and macOS symlinked directories (`/var` -> `/private/var`).
- **Expanded Test Suite:** Added dedicated regression unit tests for `tomllib` absence and fallback handling, bringing the total suite to 82 passing tests.
- **Preserved Real-World Codex Execution Audit (`docs/CODEX_END_TO_END_TEST.md`):** Comprehensive documentation of a real end-to-end execution of BeenHere inside OpenAI Codex on an AI-powered recruitment platform, including exact commands, generated artifacts, PyMuPDF licensing discoveries, and network fallback validation.
- **Subprocess Sandbox Socket Denial Fallback:** Added graceful detection for `[WinError 10013]` / `WSAEACCES` socket permission denials in `scripts/github_search.py`, `scripts/repo_inspector.py`, and `scripts/paper_search.py`, providing actionable fallback recommendations for host agents to leverage native tools.
- **Formally Recognized `[UNVERIFIED-MARKETING-CLAIM]`:** Added explicit support for auditing commercial marketing claims in `scripts/verify_sources.py`, `SKILL.md`, and `references/evaluation_rubric.md`.
- **Known License-Sensitive Package Advisory:** Enhanced `scripts/integration_analyzer.py` with automatic detection for high-risk dual-licensed dependencies (such as `pymupdf` AGPL/Artifex commercial terms and `redis` RSALv2/SSPL).

### Changed
- Standardized version identifier to `v1.0.0-beta.1` across `SKILL.md`, `README.md`, `docs/INSTALLATION.md`, and `CHANGELOG.md`.
- Updated `SECURITY.md` and `SKILL.md` to avoid exaggerated security claims, explicitly disclosing residual prompt injection risks.
- Clearly disclosed agent execution status: verified end-to-end in OpenAI Codex; verified structurally in Anthropic Claude Code and Agent Skills CLI.

---

## [1.0.0-rc1] - 2026-11-13 (Phase 4: Usability, Installation & Release Candidate)

### Added
- **Dual Invocation Modes:** Added **Quick Exploration Mode** (`/beenhere <idea>`) for conversational speed and **Deep Investigation Mode** (`/beenhere --deep <idea>`) for comprehensive architectural intelligence.
- **Skill Packaging & Validator Utility (`scripts/validate_skill.py`):** Automated checker for `SKILL.md` frontmatter, referenced file integrity, script syntax, and secret leakage.
- **Cross-Platform Installer (`scripts/install_skill.py`):** Standalone installer supporting project-local and user-global installations for Anthropic Claude Code (`.claude/skills/beenhere`) and OpenAI Codex (`.agents/skills/beenhere`), with `--dry-run` and `--uninstall` support.
- **Agent Skills CLI Support:** Verified compatibility with `npx skills add <url> --agent claude-code codex`.
- **Open Source Community Standards:** Added comprehensive `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, GitHub Actions CI workflow, and issue templates.
- **Reproducible Walkthroughs:** Added `docs/DEMO_WALKTHROUGH.md` with step-by-step prompts and video recording scripts.
- **Expanded Test Suite:** Added 8 new unit tests in `tests/test_phase4.py`, bringing the total test suite to 74 passing tests.

### Changed
- Clarified cross-process IPC / sidecar requirements between Python (Pipecat) and TypeScript/Bun (Letta) in `examples/voice_social_platform/INTEGRATION_BLUEPRINT.md`.
- Updated prompt interaction guidelines in `SKILL.md` to prevent long questionnaires and focus on 1–2 high-leverage trade-off questions.

---

## [0.3.0] - 2026-11-13 (Phase 3: Deep Code-Reusability Intelligence)

### Added
- **Integration Point Analyzer (`scripts/integration_analyzer.py`):** 934-line static analyzer supporting AST-based Python parsing, regex-based JS/TS export parsing, and multi-format manifest extraction (`package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`).
- **Standardized Architecture Integration Blueprint Template (`templates/INTEGRATION_BLUEPRINT.md`):** Complete template defining module boundaries, data contracts, and dependency compatibility matrices.
- **Automated Reuse Recommendation Engine:** Classifies candidate repositories into 7 actionable postures (*Adopt as Dependency*, *Integrate via API*, *Extract Component*, *Fork Codebase*, *Reject Dependency*).
- **Comprehensive Phase 3 Test Suite (`tests/test_phase3.py`):** 26 new unit tests verifying AST extraction, manifest parsing, copyleft nuances, and recommendation logic (66 total tests).

---

## [0.2.0] - 2026-11-13 (Phase 2 & Phase 2.5: Cross-Vertical Intelligence)

### Added
- **Cross-Vertical Concept Expander (`scripts/concept_expander.py`):** Deterministic 4-tier query matrix generation and domain mapping.
- **Academic Paper Discovery Utility (`scripts/paper_search.py`):** Free public academic queries via OpenAlex, arXiv, and Semantic Scholar with DOI deduplication and retraction checking.
- **Comprehensive Benchmark Suite (`scripts/benchmark_runner.py`):** 10-case evaluation suite covering diverse software domains.
- **Real-World Intelligence Deliverables:** Published complete `IDEA_LANDSCAPE.md` reports for:
  - Synthetic AI Social Platform (`examples/voice_social_platform/`)
  - Offline-First Collaborative Notes (`examples/offline_first_notes/`)
  - Automated Accessibility Auditing Platform (`examples/accessibility_auditing/`)

---

## [0.1.0] - 2026-11-12 (Phase 1: Foundation & Hardening)

### Added
- **Canonical Skill Specification (`SKILL.md`):** Cross-compatible definition for OpenAI Codex and Anthropic Claude Code.
- **GitHub Search Utility (`scripts/github_search.py`):** Multi-query discovery with rate-limit safety and deduplication.
- **Repository Inspector (`scripts/repo_inspector.py`):** Health signals, maintenance activity, and license categorization.
- **Source Link & Evidence Verifier (`scripts/verify_sources.py`):** Markdown link reachability checker and evidence tag auditor.
- **Initial Test Suite:** 24 unit and mock tests in `tests/test_core.py`.
