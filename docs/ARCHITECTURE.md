# BeenHere — Architecture Specification

This document details the system design, core components, data flows, and design principles of **BeenHere**.

---

## 1. Architectural Principles

1. **Portable Agent Skill Standard:** Adheres strictly to the open Agent Skills format supported by Claude Code, OpenAI Codex, and Antigravity. Operates from a single canonical `SKILL.md`.
2. **Zero Mandatory Dependencies:** All core execution relies solely on the Python 3.8+ standard library (`urllib.request`, `json`, `re`, `argparse`, `sys`, `os`). Does not require third-party packages, node modules, Docker, or external databases.
3. **Progressive Disclosure:** Prevents context window saturation by keeping `SKILL.md` focused on workflow execution rules. Deep methodologies, legal taxonomies, and rubrics are partitioned into `references/` and loaded on demand.
4. **Deterministic Script Verification:** Isolates API querying, JSON parsing, URL verification, and manifest inspection into standalone Python scripts with explicit JSON outputs.
5. **Strict Evidence Hierarchy:** Separates verified technical facts from inferences and unverified documentation claims.
6. **Graceful Degradation:** Continues functioning when offline, rate-limited, or in restricted environments, explicitly documenting limitations rather than hallucinating answers.

---

## 2. Directory Layout & Subsystems

```
beenhere/
├── SKILL.md                          # Primary agent entrypoint & orchestration prompt
├── README.md                         # Project documentation & usage
├── LICENSE                           # Open source MIT license
├── scripts/                          # Deterministic execution tools
│   ├── github_search.py              # Repository discovery with rate-limit safety & multi-query
│   ├── repo_inspector.py             # Repository manifest, license, and health inspector
│   └── verify_sources.py             # Source link validation & evidence auditor
├── references/                       # Progressive disclosure reference manuals
│   ├── discovery_methodology.md      # 4-Tier Search Protocol
│   ├── cross_vertical_research.md    # Mechanism abstraction & cross-domain matrix
│   ├── code_reusability.md           # Legal licensing, coupling, & architectural evaluation
│   └── evaluation_rubric.md          # Qualitative decision matrix & evidence grading
├── templates/                        # Standardized report artifacts
│   ├── IDEA_LANDSCAPE.md             # Comprehensive idea & prior-art landscape
│   └── REUSE_REPORT.md               # Dedicated repository reusability audit
├── tests/                            # Automated verification suite
│   └── test_core.py                  # Standalone offline unit tests
└── docs/                             # System specifications
    ├── EXISTING_SOLUTIONS.md         # Comparative landscape analysis
    ├── ARCHITECTURE.md               # Technical system architecture (this document)
    └── INSTALLATION.md               # Platform setup & usage guide
```

---

## 3. Data Flow & Execution Pipeline

```
  User Idea Prompt
         │
         ▼
 ┌─────────────────────────────────────────────────────────┐
 │                      BeenHere Agent                     │
 │                     (SKILL.md Core)                     │
 └─────────────────────────┬───────────────────────────────┘
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
┌──────────────┐                       ┌──────────────┐
│ Concept      │                       │ Mechanism    │
│ Decomp       │                       │ Abstraction  │
└──────┬───────┘                       └──────┬───────┘
       │                                       │
       ▼                                       ▼
┌──────────────────────────────┐       ┌──────────────────────────────┐
│ Tier 1 & 2 Prior-Art Search  │       │ Tier 3 & 4 Cross-Vertical    │
│ (github_search.py)           │       │ Search (references & web)    │
└──────────────┬───────────────┘       └──────────────┬───────────────┘
               │                                      │
               └───────────────────┬──────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ Deep Repository Inspection   │
                    │ (repo_inspector.py)          │
                    │ - Licenses & SPDF Clearance  │
                    │ - Manifest & Dep Tree        │
                    │ - Freshness & Maintenance    │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ Reusability & Gap Evaluation │
                    │ (evaluation_rubric.md)       │
                    │ - Feature Gap Analysis       │
                    │ - Enhancement Discovery      │
                    │ - Build Strategy Decision    │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ Verification & Audit         │
                    │ (verify_sources.py)          │
                    │ - Evidence Tagging Check     │
                    │ - URL & Source Reachability  │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ Render Landscape Report      │
                    │ (IDEA_LANDSCAPE.md)          │
                    └──────────────────────────────┘
```

---

## 4. Subsystem Specifications

### 4.1 Discovery Engine (`scripts/github_search.py`)
- **Purpose:** Discovers candidate repositories matching direct keywords and functional primitives.
- **Protocol:** Interacts with `https://api.github.com/search/repositories`.
- **Key Features:**
  - **Multi-Query Support:** Accepts multiple search variations and combines results.
  - **Deduplication:** Aggregates hits by repository `full_name`.
  - **Rate-Limit Intelligence:** Inspects `X-RateLimit-Remaining` and `X-RateLimit-Reset`. If limits are hit or the network is unreachable, outputs structured error payloads without crashing.
  - **Token Escalation:** Automatically utilizes `GITHUB_TOKEN` or `GH_TOKEN` environment variables when present, expanding rate limits from 60 to 5,000 requests/hour.
  - **Output Contracts:** Emits normalized JSON matching the repository schema:
    ```json
    {
      "query_summary": {"total_count": 42, "queries_executed": 3},
      "items": [
        {
          "full_name": "owner/repo",
          "html_url": "https://github.com/owner/repo",
          "description": "...",
          "stargazers_count": 1250,
          "language": "Python",
          "updated_at": "2026-03-15T12:00:00Z",
          "license": "MIT"
        }
      ]
    }
    ```

### 4.2 Repository Inspector (`scripts/repo_inspector.py`)
- **Purpose:** Programmatically analyzes repository metadata, dependencies, license declarations, and maintainability.
- **Protocol:** Queries GitHub REST endpoints (`/repos/{owner}/{repo}`, `/repos/{owner}/{repo}/languages`, `/repos/{owner}/{repo}/contents/{path}`).
- **Key Features:**
  - **License Audit:** Scans GitHub license metadata and examines candidate license files (`LICENSE`, `LICENSE.md`, `COPYING`). Explicitly flags repositories without licenses as `UNRESOLVED / ALL_RIGHTS_RESERVED`.
  - **Manifest Discovery:** Checks for common package manifests (`package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`).
  - **Maintainability Signals:** Computes days since last push, flags archived status, and counts open issues.
  - **Zero Execution Rule:** Strictly analyzes static metadata and raw text; never clones untrusted binary artifacts or executes external code.

### 4.3 Source Verifier & Auditor (`scripts/verify_sources.py`)
- **Purpose:** Validates that URLs cited in reports exist and audits evidence markers.
- **Key Features:**
  - **HTTP Verification:** Issues HTTP HEAD requests (falling back to GET range requests) to confirm link reachability without downloading full web pages.
  - **Markdown Parsing:** Extracts markdown link targets (`[title](url)`) from reports.
  - **Evidence Tag Compliance:** Verifies that analytical claims are properly classified under the BeenHere evidence hierarchy.

---

## 5. Evidence Classification Hierarchy

BeenHere maintains strict research integrity by categorizing all findings into five evidence tiers:

1. **`[VERIFIED-TEST]`**: The finding has been confirmed by compiling, executing, or running automated unit/integration tests in a secure sandbox.
2. **`[VERIFIED-SOURCE]`**: The finding has been confirmed by reading the raw source code, AST, or package manifest file.
3. **`[VERIFIED-METADATA]`**: The finding has been confirmed via official API headers, package registry metadata, or official release notes.
4. **`[INFERRED]`**: The conclusion is a logical deduction derived from verified technical evidence (the underlying premises must be cited).
5. **`[UNKNOWN]`**: Information that could not be verified due to missing access, network boundaries, or ambiguous source code.

---

## 6. Build Decision Matrix

The build recommendation engine synthesizes technical evidence into one of seven definitive postures:

- **Adopt:** Use as-is via package manager or direct execution. Reusability is high, license is permissive, architecture is decoupled.
- **Fork:** Clone and independently maintain. Upstream has diverged or is dormant, but the core foundation is solid and permissive.
- **Extend:** Utilize existing plugin architectures, subclassing, or official extension points.
- **Extract:** Carve out specific algorithms or modules into a standalone component.
- **Integrate:** Assemble multiple existing tools into a composite workflow via standard protocols (HTTP, IPC, CLI).
- **Build from Scratch:** Greenfield engineering is justified ONLY when no viable prior art exists, critical legal/license barriers prevent reuse, or the architectural mismatch exceeds the cost of a fresh build.
- **Investigate Further:** Technical or legal unknowns prevent a confident decision.
