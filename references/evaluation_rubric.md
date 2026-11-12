# BeenHere — Evaluation Rubric & Decision Framework

This document outlines the qualitative criteria used to formulate defensible build recommendations and enforce strict research integrity standards.

---

## 1. The Anti-Percentage Rule

> **Never invent quantitative percentages or arbitrary numerical scores.**
> 
> Claims like *"This repository is 87% reusable"* or *"Your idea has a 92% uniqueness score"* are pseudoscientific fabrications. Real engineering decisions are qualitative, multi-variable, and context-dependent.
> 
> BeenHere uses explicit qualitative criteria, verifiable evidence markers, and defensible architectural trade-offs.

---

## 2. The Seven Strategic Decision Postures

BeenHere evaluates all findings into one of seven clear, actionable postures:

```
                      ┌────────────────────────┐
                      │    Decision Postures   │
                      └───────────┬────────────┘
         ┌────────────┬───────────┼───────────┬────────────┐
         ▼            ▼           ▼           ▼            ▼
     [ ADOPT ]    [ FORK ]    [ EXTEND ]  [ EXTRACT ]  [ INTEGRATE ]
                                  │           │
                          ┌───────┴───────────┴───────┐
                          ▼                           ▼
                  [ BUILD FROM SCRATCH ]    [ INVESTIGATE FURTHER ]
```

---

### 1. ADOPT
- **Definition:** Use the existing component as an external, unmodified package dependency or turnkey application.
- **When Justified:**
  - The repository solves 70%+ of the functional problem.
  - The license is permissive (`MIT`, `Apache-2.0`, `BSD`) or weak copyleft (`LGPL`, `MPL`) consumed via dynamic dependency.
  - Active maintenance within the last 90 days.
  - Clean, idiomatic package distribution (e.g., published on PyPI, npm, Cargo).
- **Primary Benefit:** Fastest time-to-value; leverages upstream bug fixes and community testing.
- **Inherent Risk:** Upstream API deprecations and dependency lock-in.

### 2. FORK
- **Definition:** Clone the codebase into an independent repository and diverge from the original author's roadmap.
- **When Justified:**
  - The foundation is robust and aligned with requirements, but upstream maintenance has ceased (dormant/archived).
  - The original project maintainers explicitly reject an essential architectural shift or feature direction.
  - The license permits forking and modification.
- **Primary Benefit:** Complete control over codebase evolution without greenfield ground-up rebuilding.
- **Inherent Risk:** You assume 100% of the long-term maintenance, security patching, and bug triage burden.

### 3. EXTEND
- **Definition:** Build on top of an existing framework using its official plugin architecture, middleware hooks, subclassing, or configuration interfaces.
- **When Justified:**
  - The upstream project is actively maintained and explicitly designed for extensibility (e.g., provides plugin interfaces or event buses).
  - Your novel capabilities fit cleanly into the established lifecycle.
- **Primary Benefit:** Upstream compatibility remains intact; clean separation between custom logic and framework core.
- **Inherent Risk:** Vulnerable to core lifecycle refactors and breaking changes in major framework updates.

### 4. EXTRACT
- **Definition:** Carve out specific algorithms, mathematical functions, or data structures from a larger repository into your own codebase.
- **When Justified:**
  - You require only a small, self-contained algorithmic kernel (e.g., an argument validation algorithm, audio DSP filter, or state machine).
  - The parent repository is bloated, unmaintained, or entangled with unneeded monolithic baggage.
  - The license allows extraction and redistribution (e.g., MIT/Apache with copyright notice preserved).
- **Primary Benefit:** Zero dependency bloat; complete runtime transparency.
- **Inherent Risk:** Loss of automatic upstream fixes; responsibility for testing the isolated code.

### 5. INTEGRATE
- **Definition:** Compose two or more specialized external systems via APIs, IPC, event streams, or CLI interfaces rather than writing unified custom software.
- **When Justified:**
  - Distinct best-in-class solutions exist for different layers of your problem (e.g., LiveKit for WebRTC audio transport + Letta for cognitive memory + Ollama for local LLM inference).
  - Integrating via standard protocols requires significantly less effort than rebuilding either subsystem.
- **Primary Benefit:** Combines enterprise-grade building blocks with minimal custom glue code.
- **Inherent Risk:** Protocol complexity, latency serialization overhead, and multi-service deployment operations.

### 6. BUILD FROM SCRATCH
- **Definition:** Greenfield software development from the ground up.
- **When Justified:**
  - **Exhaustive Absence:** No existing open-source or commercial solution solves the fundamental mechanism.
  - **Irreconcilable License Blockers:** Existing solutions are unlicensed, proprietary, or copyleft-incompatible with project goals.
  - **Severe Architectural Impedance:** Existing solutions carry unacceptable performance, memory, security, or latency penalties that cannot be refactored away.
- **Primary Benefit:** Zero legacy baggage; optimal domain-tailored architecture.
- **Inherent Risk:** Highest development cost, prolonged time-to-market, and exposure to all first-generation bugs.

### 7. INVESTIGATE FURTHER
- **Definition:** Defer commitment until unresolved technical, legal, or architectural ambiguities are clarified.
- **When Justified:**
  - Repository license is ambiguous or missing (`NOASSERTION`).
  - Architectural claims in documentation cannot be verified through source code inspection.
  - Closed-source commercial competitors conceal API specifications or pricing structures.

---

## 3. Evidence Classification Standards

To maintain absolute research integrity and eliminate hallucinations, every analytical claim must be explicitly attributed to one of five evidence tiers:

| Evidence Tag | Verification Standard | Example Usage |
| :--- | :--- | :--- |
| **`[VERIFIED-TEST]`** | Confirmed by executing automated unit/integration tests or code in an active runtime environment. | *"The WebRTC transport achieves 120ms roundtrip audio latency in local loopback tests [VERIFIED-TEST]."* |
| **`[VERIFIED-SOURCE]`** | Confirmed by reading raw source code files, ASTs, or package manifests (`package.json`, `Cargo.toml`). | *"The repository does not import external vector databases; memory is stored in an in-memory dictionary [VERIFIED-SOURCE]."* |
| **`[VERIFIED-METADATA]`** | Confirmed via official API headers, package registry records, or HTTP status codes. | *"Repository has an Apache-2.0 license and 4,120 stars as of 2026-03 [VERIFIED-METADATA]."* |
| **`[INFERRED]`** | Logical deduction derived from verified technical evidence; reasoning must be explicitly stated. | *"Because the framework lacks Redis or database adapters in source code, sessions will not survive process restarts [INFERRED]."* |
| **`[UNKNOWN]`** | Information that cannot be verified due to missing documentation, paywalls, or closed source. | *"The token latency and internal model weights of the proprietary API remain unknown [UNKNOWN]."* |

---

## 4. Integrity Guardrails: Declaring Uniqueness

- **The Non-Discovery Fallacy:** Never declare that an idea is "completely unique", "groundbreaking", or "novel" simply because search queries returned zero results.
- **Proper Assessment:** When searches yield sparse direct results, the report must state:
  > *"No direct open-source projects or commercial products matching the exact query were discovered via GitHub public API search. However, foundational mechanisms exist across adjacent domains [X, Y, Z]. Further search with domain-specific terminology is recommended."*
