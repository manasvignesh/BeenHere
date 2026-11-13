# BeenHere 🧭 — Explore Every Angle Before You Build

[![Test Suite](https://img.shields.io/badge/tests-74%20passing-brightgreen.svg)](tests/)
[![Benchmarks](https://img.shields.io/badge/benchmarks-10%2F10%20passing-brightgreen.svg)](scripts/benchmark_runner.py)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-stdlib%20only-orange.svg)](scripts/)
[![Agent Skills](https://img.shields.io/badge/skills-Codex%20%26%20Claude%20Code-purple.svg)](SKILL.md)

> **Discover what's built. Explore what's possible. Reuse what works. Improve what's missing. Build only what matters.**

---

**BeenHere** is a portable, zero-dependency Agent Skill for AI coding environments (**Anthropic Claude Code**, **OpenAI Codex**, and the **Agent Skills CLI**).

Before you write a single line of code or commit weeks to building a new feature, BeenHere investigates your idea across:
- **Existing Open-Source Repositories:** Discovers candidate libraries, verifies actual source code (not just README claims), checks maintenance vitals, and audits license obligations.
- **Academic Research:** Searches peer-reviewed literature, preprints, and algorithmic foundations across OpenAlex, arXiv, and Semantic Scholar.
- **Commercial & Adjacent Products:** Maps direct, partial, and adjacent market solutions with verified documentation.
- **Cross-Vertical Engineering:** Uncovers battle-tested mechanisms from unrelated industries (gaming, simulation, aerospace, robotics) that solve identical computational primitives.
- **Interface & Dependency Extraction:** Statically parses exported symbols, public APIs, environment variables, and dependency conflicts to formulate concrete, step-by-step **Integration Blueprints**.

---

## The Problem: The Reinvention Loop

Developers and AI agents routinely reinvent existing software:
- **Siloed Searches:** Quitting after a single GitHub keyword query fails to find an exact match, mistakenly concluding an idea is novel.
- **Unverified README Trust:** Blindly assuming a library works as advertised without verifying exported interfaces, activity, or breaking dependencies.
- **Hidden Legal Traps:** Ingesting AGPL, SSPL, or BSL-1.1 code into proprietary or commercial SaaS products without understanding copyleft triggers or non-compete clauses.
- **Architectural Reinvention:** Solving synchronization, turn arbitration, or caching problems from scratch when proven patterns exist in adjacent fields.

BeenHere breaks this cycle by providing **deterministic, evidence-backed intelligence** before development begins.

---

## Dual Invocation Modes

BeenHere adapts to your conversational context:

### 1. Quick Exploration Mode (`/beenhere <idea>`)
Designed for rapid, lightweight conversational ideation.
- Executes rapid keyword decomposition and prior-art discovery.
- Delivers a concise 4-part inline summary:
  1. **Top 3 Candidate Repositories:** Confirmed slugs, verified star counts, license status, and maintenance signals.
  2. **Core Reusable Components:** What already exists off-the-shelf vs what must actually be built.
  3. **Critical Hazards:** Potential license friction (AGPL/BSL) or unmaintained dependencies.
  4. **Initial Build Recommendation:** Defensible posture (*Adopt, Fork, Integrate, Build from Scratch*).
- Asks at most **1–2 high-leverage clarifying questions** if technical trade-offs are ambiguous.

### 2. Deep Investigation Mode (`/beenhere --deep <idea>`)
Designed for rigorous product architecture and architectural planning.
- Runs the full **14-Step Research & Integration Protocol**.
- Generates exhaustive, structured markdown deliverables:
  - `IDEA_LANDSCAPE.md`: 15-section exhaustive market, academic, and cross-vertical analysis.
  - `INTEGRATION_BLUEPRINT.md`: Concrete module boundaries, data contracts, and dependency compatibility matrices.

---

## Installation

BeenHere requires **Python 3.8+** (standard library only). No third-party packages or paid API keys are required.

### Method 1: Using the Agent Skills CLI (Recommended)
Install directly into Claude Code, Codex, or all supported environments:
```bash
# Add to Claude Code & Codex
npx skills add <repository-url-or-local-path> --agent claude-code codex
```

### Method 2: Using the Built-In Installer Script
BeenHere includes a standalone Python installer that works on Windows, macOS, and Linux:
```bash
# Install locally in current project for all agents:
python scripts/install_skill.py

# Install specifically for Claude Code or Codex:
python scripts/install_skill.py --agent claude
python scripts/install_skill.py --agent codex

# Install globally to your user profile (~/.claude or ~/.agents):
python scripts/install_skill.py --global

# Preview actions without writing to disk:
python scripts/install_skill.py --dry-run

# Uninstall cleanly:
python scripts/install_skill.py --uninstall
```

### Method 3: Manual File Placement
- **Anthropic Claude Code:** Copy the skill files into `.claude/skills/beenhere/` (project-local) or `~/.claude/skills/beenhere/` (global).
- **OpenAI Codex:** Copy the skill files into `.agents/skills/beenhere/` (project-local) or `~/.agents/skills/beenhere/` (global).

---

## Repository Structure

```
beenhere/
├── SKILL.md                          # Canonical Agent Skill specification (v1.0.0-rc1)
├── README.md                         # Project overview and documentation
├── LICENSE                           # MIT License
├── CONTRIBUTING.md                   # Development guide and contribution standards
├── SECURITY.md                       # Security policy and prompt injection threat model
├── CHANGELOG.md                      # Version release notes
│
├── scripts/                          # Zero-dependency Python CLI utilities
│   ├── github_search.py              # GitHub discovery with multi-query deduplication & rate limiting
│   ├── repo_inspector.py             # Repository metadata, health, and source code inspection
│   ├── integration_analyzer.py       # Static AST symbol, manifest, and license obligation analyzer
│   ├── concept_expander.py           # 4-tier search query planner and mechanism abstractor
│   ├── paper_search.py               # Academic discovery across OpenAlex, arXiv, and Semantic Scholar
│   ├── verify_sources.py             # Evidence tag auditor and link reachability verifier
│   ├── benchmark_runner.py           # 10-domain automated benchmark evaluation suite
│   ├── validate_skill.py             # Packaging, schema, and credential-leak validator
│   └── install_skill.py              # Cross-platform installer for Claude Code and Codex
│
├── references/                       # Research protocols & rubrics
│   ├── discovery_methodology.md      # 4-Tier search expansion protocol
│   ├── cross_vertical_research.md    # Computational primitive abstraction matrix
│   ├── transferability_rubric.md     # 10-point cross-industry transfer evaluation
│   ├── code_reusability.md           # Legal taxonomy, license clearance, and coupling blockers
│   ├── feature_gap_analysis.md       # Intentional trade-off vs genuine opportunity rubric
│   ├── product_discovery.md          # Commercial & SaaS verification standards
│   └── evaluation_rubric.md          # 7-posture build decision framework
│
├── templates/                        # Standardized report templates
│   ├── IDEA_LANDSCAPE.md             # 15-section exhaustive idea evaluation template
│   ├── INTEGRATION_BLUEPRINT.md      # Architecture, boundary, and contract blueprint template
│   └── REUSE_REPORT.md               # Focused repository reusability audit template
│
├── tests/                            # Automated test suite (Python unittest stdlib)
│   ├── test_core.py                  # Core search, inspection, and verification tests
│   ├── test_phase2.py                # Concept expansion, academic search, and benchmark tests
│   ├── test_phase3.py                # AST symbol extraction, manifest parsing, and recommendation tests
│   └── test_phase4.py                # Skill validation and installer tests
│
├── examples/                         # Real-world verified research deliverables
│   ├── voice_social_platform/        # Voice-first synthetic social platform (Landscape & Blueprint)
│   ├── offline_first_notes/          # Offline-first local collaborative notes engine (Landscape)
│   └── accessibility_auditing/       # Automated AST accessibility test platform (Landscape)
│
└── docs/                             # Technical architecture and release documentation
    ├── ARCHITECTURE.md               # Architecture design & progressive disclosure model
    ├── INSTALLATION.md               # Detailed installation and agent integration guide
    ├── DEMO_WALKTHROUGH.md           # Reproducible demo walkthrough and video script
    └── RELEASE_CHECKLIST.md          # Pre-release verification checklist
```

---

## Research Integrity & Security Standards

BeenHere is built around strict research integrity and defensible claims:

1. **Strict Evidence Tagging Hierarchy:**
   - `[VERIFIED-TEST]`: Confirmed by running code or automated unit/integration tests in a local environment.
   - `[VERIFIED-SOURCE]`: Confirmed by inspecting implementation source files directly.
   - `[VERIFIED-METADATA]`: Confirmed via official API headers, manifests, or academic DOIs.
   - `[INFERRED]`: Deductive reasoning derived from verified technical evidence.
   - `[UNKNOWN]`: Data points that could not be verified due to access restrictions.
2. **Prompt Injection & Untrusted Data Defense:**
   - All external repository descriptions, README excerpts, academic abstracts, commit messages, and issue comments are treated as **untrusted data**.
   - Input sanitizers disarm prompt injection attempts (`ignore previous instructions`, `system prompt:`) and quarantine external text within `<untrusted_external_content>` tags.
3. **No Arbitrary Percentages:**
   - BeenHere rejects pseudo-quantitative scores (e.g., "78% reusable"). All reusability assessments are qualitative, grounded in exported symbols, dependency friction, and explicit license grants.
4. **Zero Compulsory Paid APIs:**
   - Works immediately out of the box using public APIs (GitHub public endpoints, OpenAlex, arXiv, Semantic Scholar) with graceful offline degradation.

---

## Verification & Testing

BeenHere is continuously tested using standard Python unittest and automated benchmark suites:

```bash
# Run all 74 automated unit tests:
python -m unittest discover tests -v

# Run the 10-case benchmark evaluation suite:
python scripts/benchmark_runner.py

# Validate skill packaging, schema, and secret hygiene:
python scripts/validate_skill.py
```

---

## Contributing

We welcome community contributions, additional cross-vertical mappings, and runtime parsers! See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and coding standards.

---

## License

BeenHere is free and open-source software licensed under the **[MIT License](LICENSE)**.
