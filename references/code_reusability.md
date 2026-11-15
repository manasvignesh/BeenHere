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

### Tier 3: Reciprocal Copyleft Licenses on Distribution (Orange Clearance)
- **Licenses:** `GPL-2.0`, `GPL-3.0`
- **Permissions:** Full commercial use, private internal company deployment, and commercial hosting are explicitly permitted.
- **Obligations upon Distribution:** If the application or derivative work is distributed to external users (as binaries, installed desktop software, or mobile apps), the complete corresponding source code must be made available under the same GPL terms.
- **Crucial SaaS Nuance:** Standard `GPL-2.0` and `GPL-3.0` do **not** trigger source code disclosure for backend SaaS / network services that are accessed over an API or web browser without distributing executable client binaries.
- **Incompatibilities:** Cannot be combined with proprietary closed-source distributed software, and cannot be combined with conflicting licenses (e.g., Apache-2.0 is incompatible with GPL-2.0).
- **Verdict:** **RECIPROCAL ON DISTRIBUTION**. Reusable for server-side SaaS or open-source projects; requires careful review if client-side distribution is planned.

### Tier 4: Network-Triggered Copyleft Licenses (Red Clearance / SaaS Warning)
- **Licenses:** `AGPL-3.0`, `OSL-3.0`
- **Permissions:** Commercial use is permitted.
- **Network Obligation:** Specifically closes the "SaaS loophole." Providing remote user interaction with the software over a network (e.g., a web service or cloud API) legally triggers the obligation to make the entire service's corresponding source code freely available to all network users.
- **API Boundary Nuance:** While deploying an AGPL component as an isolated, independent network service over HTTP/gRPC is a common architectural containment strategy, legal interpretations vary regarding whether tightly coupled APIs constitute a derivative/combined work. Furthermore, many corporate open-source policies (e.g. Google's policy) strictly prohibit AGPL in production infrastructure regardless of network boundaries.
- **Verdict:** **NETWORK RECIPROCAL / CONDITIONAL SERVICE ISOLATION**. Reusable for open-source reciprocal SaaS; requires explicit organizational legal approval and architectural isolation if integrated into proprietary environments.

### Tier 5: Source-Available & Non-Commercial (Commercial Blocker)
- **Licenses:** `SSPL-1.0`, `BSL-1.1`, `BUSL-1.1`, `CC-BY-NC-4.0`, Commons Clause
- **Restrictions:** Restricts commercial production use, hosting competitive managed cloud services, or production deployments beyond specific limits. Not OSI-approved open source.
- **Project-Specific Grants:** BSL-1.1 is not uniform across projects. Each licensor specifies a customized "Additional Use Grant" and "Change Date" (at which point the license converts to an OSI-approved license like Apache-2.0 or GPL). Some grants permit commercial use under specified cluster size, user count, or non-competing application limits.
- **Verdict:** **COMMERCIAL RESTRICTED / GRANT-DEPENDENT**. Safe for non-commercial research, local evaluation, and benchmarking; requires explicit audit of the Additional Use Grant before commercial deployment.

### Tier 6: Missing or Unlicensed (Critical Blocker)
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

## 5. The Six Legal Assessment Distinctions

To prevent automated systems from mistaking heuristic flags for verified legal conclusions, BeenHere rigorously distinguishes six legal dimensions:

1. **Confirmed License Identity:** The exact license formally declared in SPDX tags and confirmed by inspecting the raw LICENSE text headers.
2. **Observed Dependency Relationships:** Direct vs. transitive dependencies, runtime vs. dev/test scope, and dynamic linking vs. static bundling.
3. **Potential Obligations:** Conditional terms (e.g. copyright attribution, patent peace, file-level source sharing under MPL, or full reciprocity under GPL).
4. **Unresolved Compatibility Questions:** Ambiguities requiring human clarification (e.g. undefined Additional Use Grants in BSL, dual-licensing commercial pricing, or uncertain linkage boundaries).
5. **Confirmed Technical Incompatibilities:** Definite runtime or architectural barriers (e.g. language mismatches without bindings, missing symbols, or unpackageable monoliths).
6. **Organizational Policies Requiring Human Input:** Enterprise-specific legal mandates (e.g. absolute prohibitions against AGPL components, proprietary export restrictions, or Contributor License Agreements).

---

## 6. Practical Extraction vs. Direct Dependency Guidelines

When deciding how to reuse code:

- **Prefer Direct Package Dependency When:**
  - The repository publishes an official package on PyPI / npm / Cargo.
  - The dependency is actively maintained and has a verified permissive or weak copyleft license.
  - The component provides a self-contained, modular capability without invasive architectural coupling.
- **Prefer Code Extraction (Carving Out Primitives) When:**
  - You only need a specific mathematical routine, state machine, or isolated algorithm.
  - The parent repository is unmaintained or bloated with heavy, unnecessary dependencies.
  - The license is permissive (MIT/Apache/BSD), allowing you to extract the file, preserve the original copyright notice, and maintain it locally.
- **Prefer Forking When:**
  - The repository provides the foundational architecture for your system, but upstream is dormant or refuses necessary architectural patches.
