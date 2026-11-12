# BeenHere — Cross-Vertical Transferability Rubric

This reference guide establishes the formal evaluation framework for determining whether algorithms, protocols, and architectural mechanisms from unrelated industries are genuinely applicable to a target software problem.

---

## 1. The Core Imperative: Rejecting Superficial Analogies

> **Analogies are not code.**
> 
> Discovering that another industry faces a similar challenge is only the starting point. An analogy is useful to an engineer only if it transfers concrete mathematical formulations, state machine structures, protocols, or algorithmic logic.
> 
> BeenHere actively screens out and rejects metaphorical, poetic, or superficial comparisons.

---

## 2. The 10-Point Transferability Audit

Every proposed cross-vertical mechanism must be evaluated across all ten dimensions:

| # | Evaluation Dimension | Verification Question |
| :-: | :--- | :--- |
| **1** | **Source Domain** | What specific industry, discipline, or engineering field originated this mechanism? |
| **2** | **Target Domain** | What is the exact software system or feature under design? |
| **3** | **Shared Underlying Problem** | What identical mathematical, logistical, or behavioral constraint do both domains share? |
| **4** | **Underlying Mechanism** | What specific algorithm, data structure, protocol, or state machine solves the constraint? |
| **5** | **Existing Concrete Evidence** | What peer-reviewed paper, open-source library, or production system proves this mechanism works? |
| **6** | **Required Adaptation** | What architectural transformations are required to bridge the domains (e.g. latency, scale, data types)? |
| **7** | **Defensible Advantages** | What measurable improvement (e.g. lower latency, reduced deadlock, fairer arbitration) does this mechanism provide over naive design? |
| **8** | **Inherent Limitations** | Under what conditions does the mechanism fail, degrade, or introduce excessive complexity? |
| **9** | **Integration Effort** | What is the qualitative engineering cost to adapt this mechanism (Trivial / Moderate / Heavy / Unfeasible)? |
| **10** | **Confidence & Evidence Tier** | Is the mechanism backed by working code (`[VERIFIED-SOURCE]`), published literature (`[VERIFIED-METADATA]`), or deductive reasoning (`[INFERRED]`)? |

---

## 3. The 5-Tier Analogy Classification

Every cross-vertical candidate must be formally assigned to one of five tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Transferability Classification                       │
└───────────────────────────────────┬────────────────────────────────────┘
         ┌──────────────┬───────────┼───────────┬──────────────┐
         ▼              ▼           ▼           ▼              ▼
    [ DIRECTLY     [ TRANSFER  [ CONCEPTUAL   [ WEAK /       [ REJECTED
    TRANSFERABLE]  W/ ADAPT ]   INSPIRATION]  SPECULATIVE]    ANALOGY ]
```

---

### Tier 1: DIRECTLY TRANSFERABLE (Highest Technical Reusability)
- **Definition:** The mathematical algorithm, data structure, or open-source library from the source domain can be imported or implemented with minimal semantic translation.
- **Criteria:** Both domains operate on identical data structures under compatible latency and resource constraints.
- **Example:** Importing a Conflict-free Replicated Data Type (CRDT) library originally built for collaborative text editing to manage distributed multi-agent game state.
- **Code Clearance Status:** May be directly imported or extracted from open-source repositories under permissive licenses.

### Tier 2: TRANSFERABLE WITH ADAPTATION (High Engineering Value)
- **Definition:** The governing state machine, protocol rules, or algorithmic steps apply directly, but the execution environment requires architectural adaptation.
- **Criteria:** The logical constraint is isomorphic, but the transport medium, latency envelope, or noise level differs.
- **Example:** Adapting Michael Mateas' *Façade* drama manager (beat pacing and conversational tension controller from 2005 video game AI) to orchestrate turn-taking and speaker selection among 4 LLM voice agents.
- **Adaptation Needed:** Bridging sub-millisecond game state updates to 800ms asynchronous streaming LLM inference.

### Tier 3: CONCEPTUALLY USEFUL BUT NOT DIRECTLY REUSABLE (Architectural Guide)
- **Definition:** The source domain provides valuable procedural or organizational insights that guide system architecture, but contains zero reusable software code.
- **Criteria:** The solution is a human operational protocol, physical checklist, or sociological practice rather than a software algorithm.
- **Example:** Aviation Cockpit Resource Management (CRM) "sterile channel" and "challenge-and-response" protocols inspiring audio barge-in priority and objection resolution in an AI debate platform.
- **Distinction:** Serves as a requirements blueprint; code must be authored from scratch.

### Tier 4: WEAK OR SPECULATIVE CONNECTION (Research Warning)
- **Definition:** The analogy relies on loose conceptual parallels that break down upon rigorous technical inspection.
- **Criteria:** The constraints in the source domain do not match the target domain, or the adaptation complexity exceeds the benefit.
- **Example:** Attempting to use ant colony foraging pheromones (stigmergy) to route real-time database transactions under microsecond ACID constraints.

### Tier 5: REJECTED ANALOGY (Formally Discarded)
- **Definition:** Metaphorical, poetic, or nonsensical comparisons that provide zero engineering value.
- **Action:** Must be explicitly documented as rejected, with the rationale stated to prevent future team members from pursuing dead ends.
- **Example:** *"Our social app is like a beehive because users buzz with excitement"* (Metaphorical buzzword; zero technical transfer).

---

## 4. Distinguishing Conceptual Inspiration from Reusable Code

To prevent confusion in technical reports, always separate:

1. **Conceptual Inspiration:**
   - *Nature:* Theoretical models, procedural checklists, design philosophies.
   - *Example:* The Delphi Method consensus structure.
   - *Software Status:* Requires greenfield software implementation.
2. **Software Architecture Pattern:**
   - *Nature:* Formal state machines, finite automata, message-bus protocols.
   - *Example:* Token-bucket rate limiting or Raft consensus.
   - *Software Status:* Can be modeled after established reference architectures.
3. **Reusable Implementation Code:**
   - *Nature:* Compilable libraries, algorithms, packages, or isolated modules.
   - *Example:* `pipecat-ai/pipecat` WebRTC pipelines or `CRDT-Yjs` syncing libraries.
   - *Software Status:* Can be adopted, forked, or extracted under appropriate licenses.
