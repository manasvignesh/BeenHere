# BeenHere — Code Reusability Evaluation Guide

This reference manual provides a rigorous, objective framework for assessing whether external software components, libraries, and repositories can be safely, legally, and practically reused.

---

## 1. Golden Rule: Claims vs. Verified Reality

> **Never declare a project reusable solely because its README says so.**
> 
> Marketing descriptions, star counts, and introductory documentation frequently exaggerate modularity, production readiness, and license flexibility. Reusability can only be established through concrete inspection of:
> 1. Formal license declarations and legal text.
> 2. Package manifests and transitive dependency trees.
> 3. Source code coupling, abstraction boundaries, and test suites.

---

## 2. Legal & Licensing Clearance Taxonomy

A technical component cannot be considered reusable if integrating it creates copyright infringement liability or forces unwanted licensing terms onto the parent project.

### Tier 1: Permissive Licenses (Green Clearance)
- **Licenses:** `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`
- **Permissions:** Unrestricted commercial and non-commercial adoption, modification, distribution, sublicensing, and private modification.
- **Key Caveat:** `Apache-2.0` includes an explicit reciprocal patent grant and trademark protections; `MIT` and `BSD` do not explicitly address patents.
- **Verdict:** **CLEAR FOR ADOPTION / INTEGRATION / EXTRACTION**.

### Tier 2: Weak Copyleft Licenses (Yellow Clearance)
- **Licenses:** `LGPL-2.1`, `LGPL-3.0`, `MPL-2.0`, `EPL-2.0`
- **Permissions:** The library itself may be adopted in commercial or proprietary software, provided it is consumed as an external dependency (dynamic linking or unmodified package import).
- **Restrictions:** Modifications to the library's own files must be open-sourced under the same license.
- **Verdict:** **CONDITIONAL REUSE PERMITTED**. Safe as an external package dependency. Dangerous if extracting or modifying internal code without maintaining open-source boundaries.

### Tier 3: Strong Copyleft Licenses (Red Clearance / Warning)
- **Licenses:** `GPL-2.0`, `GPL-3.0`, `AGPL-3.0`, `OSL-3.0`
- **Restrictions:** Any software that links to, incorporates, or derives from GPL/AGPL code must itself be released under GPL/AGPL.
- **Network Trigger (AGPL):** Under AGPL-3.0, providing access over a network (e.g., a SaaS web API) triggers the obligation to make the entire application source code publicly available.
- **Verdict:** **RESTRICTED**. Reusable only if the target project intends to be 100% open-source under identical copyleft terms. Disallowed for proprietary or commercial SaaS components.

### Tier 4: Source-Available & Non-Commercial (Commercial Blocker)
- **Licenses:** `SSPL-1.0`, `BSL-1.1`, `BUSL-1.1`, `CC-BY-NC-4.0`, Commons Clause
- **Restrictions:** Restricts commercial use, hosting competitive services, or production deployments beyond strict limits.
- **Verdict:** **COMMERCIAL RISK**. Reusable for research and experimentation only; blocked for commercial production.

### Tier 5: Missing or Unlicensed (Critical Blocker)
- **State:** No license file, or license explicitly says "All Rights Reserved", or `NOASSERTION`.
- **Legal Reality:** Under international copyright law (Berne Convention), the author retains exclusive copyright by default. The absence of a license does NOT mean public domain.
- **Verdict:** **CRITICAL BLOCKER / UNRESOLVED**. Code cannot be legally copied, extracted, forked, or deployed without securing an explicit written license agreement from the copyright holder.

---

## 3. Architectural Coupling & Modularity Analysis

Even if legally clear, code may be technically unreusable due to architectural entanglement:

### A. Component Modularity Spectrum
1. **Isolated Pure Library / Algorithm (Highest Reusability):**
   - Zero side-effects; pure functions or encapsulated classes.
   - Minimal external dependencies.
   - Example: A standalone argument-parsing library or audio VAD module.
2. **Framework with Extension Points (High Reusability via Extension):**
   - Inversion of control with clean plugin interfaces, callbacks, or middleware.
   - Example: A conversational audio pipeline that accepts custom agent handlers.
3. **Monolithic Application Workspace (Low Direct Reusability):**
   - Tightly coupled UI, database schemas, authentication controllers, and business logic.
   - Example: A full-stack Next.js + Django social media platform. Direct adoption is difficult; value is limited to *extracting* specific algorithms.

### B. Dependency Tree Health
- **Dependency Bloat:** Does importing this component pull in 500 transitive packages or heavy unneeded frameworks (e.g., requiring Torch and CUDA for a simple text parser)?
- **Native Platform Bindings:** Does the code rely on pre-compiled C/C++ binaries, platform-specific system packages, or GPU drivers that hinder cross-platform deployment?
- **Deprecated or Abandoned Dependencies:** Does the manifest rely on unmaintained, vulnerable, or superseded upstream packages?

---

## 4. Maintenance & Operational Viability

Evaluate maintenance health using concrete chronological signals:

| Metric | Healthy Signal | Warning Signal | Critical Blocker |
| :--- | :--- | :--- | :--- |
| **Commit Freshness** | Pushed within 60 days | Pushed 6-12 months ago | Inactive > 1 year |
| **Issue Velocity** | Active triage; PRs reviewed | High open issue count without response | Issues disabled or ignored |
| **Archived Status** | Active repository | Low activity | Officially marked `archived` (read-only) |
| **Test Suite** | Comprehensive automated tests passing | Minimal or flaky tests | Zero test suites or broken tests |
| **Documentation** | Clear API signatures and types | Marketing text only | Outdated or missing instructions |

---

## 5. Practical Extraction vs. Direct Dependency Guidelines

When deciding how to reuse code:

- **Prefer Direct Package Dependency When:**
  - The repository publishes an official package on PyPI / npm / Cargo.
  - The dependency is actively maintained and has a permissive license.
  - The component represents less than 20% of your overall application scope.
- **Prefer Code Extraction (Carving Out Primitives) When:**
  - You only need a single mathematical function, state machine, or algorithm (e.g., 200 lines of code).
  - The parent repository is unmaintained or bloated with unnecessary dependencies.
  - The license is permissive (MIT/Apache), allowing you to extract the file, preserve the original copyright notice, and maintain it locally.
- **Prefer Forking When:**
  - The repository is 80%+ aligned with your goal, but upstream is abandoned or refuses to accept required architectural patches.
