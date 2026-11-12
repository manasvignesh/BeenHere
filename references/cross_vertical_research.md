# BeenHere — Cross-Vertical Research Methodology

Cross-vertical exploration is a mandatory differentiator of BeenHere. Its goal is to uncover battle-tested mechanisms, algorithms, and architectural patterns developed in seemingly unrelated industries and adapt them to solve software design challenges.

---

## 1. The Principle of Mechanism Abstraction

Most software concepts are described using industry-specific jargon that conceals their underlying mechanics:

| Surface-Level Concept | Domain Context | Underlying Technical Mechanism |
| :--- | :--- | :--- |
| **"Synthetic social platform with AI personalities"** | Consumer Social / Chatbots | Agent-based simulation, multi-agent consensus, turn arbitration, persistent memory graphs |
| **"Collaborative document editor"** | Productivity SaaS | Conflict-free Replicated Data Types (CRDT), operational transformation, causal consistency |
| **"AI prompt routing framework"** | Generative AI | Packet switching, priority queuing, cost-constrained knapsack routing |
| **"Smart contract escrow service"** | Fintech / Web3 | Two-phase commit protocol, state machine verification, timeout-based escrow |
| **"Real-time code review assistant"** | Developer Tooling | Abstract Syntax Tree (AST) diffing, static analysis linting, liveness analysis |

### The 3-Step Abstraction Protocol
1. **Strip Domain Veneer:** Remove all consumer, industry, or marketing terminology (e.g., replace *"followers"*, *"likes"*, *"rooms"* with *"graph edges"*, *"event counters"*, *"pub/sub broadcast channels"*).
2. **Identify Core Constraints:** What are the mathematical, temporal, and consistency limits? (e.g., low-latency audio packet delivery, turn-taking collision resolution, long-term state coherence).
3. **Query the Universal Mechanism Catalog:** Search for domains that have solved these identical constraints over decades of rigorous engineering.

---

## 2. Cross-Domain Mapping Matrix

When an idea is decomposed into its fundamental mechanisms, search these established non-consumer verticals:

### A. Gaming & Interactive Simulation
- **Mechanisms:**
  - Non-Player Character (NPC) behavior trees, utility AI, and Goal-Oriented Action Planning (GOAP).
  - Emergent social relationship graphs (e.g., *The Sims*, *Dwarf Fortress* social histories).
  - Drama managers and narrative pacing controllers (e.g., *Façade*, *Left 4 Dead* AI Director).
- **Applicability:** Conversational AI, multi-agent personality consistency, synthetic debate tension, adaptive user engagement.

### B. Sociology, Economics & Multi-Agent Systems
- **Mechanisms:**
  - Agent-Based Modeling (ABM) (e.g., Schelling's segregation model, NetLogo, Mesa).
  - Voting protocols, social choice mechanisms, and Delphi method consensus.
  - Auction theory, automated market makers, and token-curated registries.
- **Applicability:** Synthetic focus groups, assumption evaluation, crowd behavior modeling, automated truth-finding.

### C. Aerospace, Avionics & Control Systems
- **Mechanisms:**
  - Crew Resource Management (CRM) communication protocols (sterile cockpit rules, challenge-and-response checklists).
  - Triple-modular redundancy (TMR) and voting arbiters for fault-tolerant decision-making.
  - Kalman filtering and sensor fusion.
- **Applicability:** Multi-agent debate verification, hallucination mitigation, speaker turn arbitration in voice environments.

### D. Distributed Systems & Telecommunications
- **Mechanisms:**
  - Gossip protocols, epidemic dissemination, and vector clocks.
  - Raft/Paxos leader election and state machine replication.
  - Token-bucket rate limiting and backpressure signaling.
- **Applicability:** Decentralized agent swarms, turn scheduling, conversation memory synchronization.

### E. Biology & Complex Systems
- **Mechanisms:**
  - Stigmergy (indirect communication via environmental traces, e.g., ant pheromone trails).
  - Quorum sensing in bacterial colonies (population-density triggered behavioral shifts).
  - Homeostasis and negative feedback regulation.
- **Applicability:** Asynchronous agent coordination, dynamic topic clustering, automated conversation de-escalation.

---

## 3. The Transferability Rubric

Every proposed cross-vertical analogy must be subjected to a rigorous transferability audit before inclusion in a research report:

### Dimension 1: What Transfers?
- **Concrete Artifacts:**
  - Mathematical equations (e.g., Elo rating formulas for evaluating arguments).
  - Data structures (e.g., directed acyclic graphs for argument mapping).
  - State machine models (e.g., turn-taking arbitration protocols).
  - Algorithmic procedures (e.g., multi-round Delphi consensus filtering).

### Dimension 2: Why It Transfers?
- **Structural Equivalence:** Explicitly articulate the isomorphic mapping between the two systems:
  - *Example:* "An air-traffic controller arbitrating runway access faces the exact mathematical collision constraint as an audio orchestrator arbitrating audio streams among 4 AI speakers and 1 human user."

### Dimension 3: What Requires Adaptation?
- **Domain Mismatches & Incompatibilities:**
  - *Latency Boundaries:* Avionics algorithms expect sub-millisecond determinism; LLM-based voice pipelines have 500-1500ms network and inference latency.
  - *Noise & Ambiguity:* Game engines operate on deterministic integer/float variables; natural language conversations operate on ambiguous semantic tokens.
  - *Computation & Cost Overhead:* Simulating 10,000 agents in NetLogo costs fractions of a cent; running 10,000 LLM calls costs hundreds of dollars.

---

## 4. Anti-Patterns: Guardrails Against Superficial Analogies

| Superficial / Invalid Analogy | Why It Fails | Valid Mechanical Formulation |
| :--- | :--- | :--- |
| *"This social app is like a beehive because users buzz around ideas."* | Metaphorical, poetic, non-actionable; contains zero engineering transfer. | *"Use stigmergic communication (ant trail pheromone decay) to rank conversation topics based on temporal message density."* |
| *"Our AI debate is like a courtroom trial."* | Generic concept; does not specify protocols, rules of evidence, or data formats. | *"Implement the Toulmin Argumentation Model (Claims, Grounds, Warrants, Backing, Qualifiers, Rebuttals) as a formal AST data structure for agent debates."* |
| *"Like the brain's neural networks."* | Vague buzzword; provides no implementable architectural blueprint. | *"Implement a two-tier memory architecture separating working conversational context from associative episodic memory retrieval (ACT-R cognitive model)."* |
