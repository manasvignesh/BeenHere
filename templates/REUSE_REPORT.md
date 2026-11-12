# Repository Reusability Audit Report

> **Target Repository:** `{OWNER/REPO}`  
> **Inspection Date:** `{DATE}`  
> **Inspector Utility:** BeenHere `scripts/repo_inspector.py` v0.1.0  
> **Repository URL:** `{HTML_URL}`

---

## 1. Executive Summary & Clearance Posture

- **Legal Clearance:** **`{CLEAR / CONDITIONAL / RESTRICTED / CRITICAL_BLOCKER}`**
- **Maintenance Health:** **`{ACTIVE / MAINTAINED / SLOWING / DORMANT / ARCHIVED}`**
- **Modularity Classification:** **`{MODULAR_LIBRARY / FRAMEWORK / FULL_APPLICATION / WORKSPACE}`**
- **Recommended Posture:** **`{ADOPT / FORK / EXTEND / EXTRACT / AVOID}`**

---

## 2. Legal & Licensing Analysis

| Attribute | Value | Verification Details |
| :--- | :--- | :--- |
| **Declared License** | `{SPDX_ID}` | Discovered via repository metadata |
| **License Category** | `{Permissive / Weak Copyleft / Strong Copyleft / Unlicensed}` | [references/code_reusability.md](../references/code_reusability.md) |
| **Commercial Rights** | `{Permitted / Conditional / Restricted}` | Rights granted under `{SPDX_ID}` terms |
| **Copyleft Virality** | `{None / File-Level / Network-Level (AGPL)}` | Impact on proprietary or separate code |
| **Patent Protection** | `{Explicit Grant / Silent / None}` | Explicit grant in Apache-2.0, silent in MIT |

**Legal Rationale:**  
{Detailed legal commentary on whether integrating or extracting this code creates risks or license infection.}

---

## 3. Architecture & Dependency Tree Health

### 3.1 Language Breakdown
- **Primary Language:** `{Primary Language}`
- **Breakdown:** `{Lang1 (%)}`, `{Lang2 (%)`}, `{Lang3 (%)}`

### 3.2 Manifests & Packaging
- **Detected Manifests:** `{package.json, pyproject.toml, Cargo.toml, etc.}`
- **Packaging Standard:** `{Published on PyPI / npm / Cargo / None}`
- **Native / C Extensions:** `{Yes / No / Unknown}`
- **Transitive Dependency Weight:** `{Lightweight / Moderate / Heavyweight Bloat}`

### 3.3 Modularity & Coupling Assessment
{Analyze whether the code is structured as clean decoupled modules with distinct API boundaries or tightly coupled to a specific framework/database.}

---

## 4. Maintenance Vitals & Community Health

- **Stargazers:** `{stargazers_count:,}` | **Forks:** `{forks_count:,}` | **Open Issues:** `{open_issues_count:,}`
- **Creation Date:** `{created_at}` | **Last Push:** `{pushed_at}`
- **Days Since Last Push:** `{days_since_push}` days
- **Archived Status:** `{Yes (Read-Only) / No}`
- **Maintenance Trajectory:** {Assessment of issue velocity and recent active development}

---

## 5. Reusable Primitives & Extraction Inventory

Identify specific subdirectories, files, or algorithms that can be salvaged:

| File / Component Path | Purpose | Reusability Potential | Extraction Effort |
| :--- | :--- | :--- | :--- |
| `{path/to/module.py}` | `{What it does}` | `{High / Medium / Low}` | `{Trivial / Moderate / Complex}` |

---

## 6. Identified Blockers & Integration Hazards

1. **Hazard 1:** {Description of architectural, dependency, or licensing hazard}
2. **Hazard 2:** {Description}

---

## 7. Actionable Implementation Path

{Concrete instructions on how to consume this code: e.g. exact pip/npm install command, or git submodule setup, or specific files to extract while preserving license headers.}
