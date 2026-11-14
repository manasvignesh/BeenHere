# Benchmark Evaluation Scenario A: Offline-First Collaborative Notes

## 1. Standardized Research Brief

> **Instruction to Agent (Verbatim):**
> 
> *"I want to build an offline-first collaborative note-taking and knowledge base application. It must support rich-text markdown editing, local SQLite storage, peer-to-peer or decentralized sync, end-to-end encryption (E2EE), and conflict-free concurrent editing when multiple users edit the same document while offline.*
> 
> *Before writing any code, research what already exists:*
> *1. What existing open-source projects or commercial products solve this or parts of this?*
> *2. What specific components, libraries, or algorithms can be reused off-the-shelf?*
> *3. What license restrictions or copyleft obligations apply to the best candidate solutions?*
> *4. What are the biggest technical risks or missing pieces we would still need to build ourselves?*
> *5. What is your concrete build-versus-reuse recommendation?"*

---

## 2. Target Concept & Architectural Primitives

- **Domain:** Developer Tools / Personal Productivity / Local-First Systems
- **Core Computational Primitives:**
  - Sequence and state-based Conflict-free Replicated Data Types (CRDTs)
  - Local-first relational storage (SQLite WASM, OPFS, reactive queries)
  - Convergent relational replication (CRRs / change data capture)
  - Cryptographic access control & forward-secret key ratcheting in peer-to-peer networks
  - Network transport arbitration (WebRTC DataChannels, WebSockets, gossip sync)

---

## 3. Known Failure Modes in Standard AI Research

Ordinary LLM research without deterministic source inspection routinely exhibits the following critical defects:

1. **The BSL-1.1 Commercial License Trap (Outline):**
   - High-star knowledge base repositories like `outline/outline` (41k+ stars) report `NOASSERTION` or ambiguous license metadata in the GitHub REST API.
   - Standard agents frequently recommend adopting or self-hosting Outline components without realizing it is licensed under **Business Source License 1.1 (BSL-1.1)** by General Outline, Inc., which explicitly prohibits providing a competing SaaS application.
2. **Missing Local-First Convergent SQLite Primitives:**
   - Standard agents recommend pairing an in-memory CRDT (like Yjs or Automerge) with a standard SQLite database by "storing documents as JSON blobs", ignoring the massive write-amplification and lack of relational queryability over CRDT state.
   - Specialized convergent database extensions like `vlcn-io/cr-sqlite` (convergent SQLite extension) or `powersync-ja/powersync-js` are frequently overlooked in favor of generic full-stack templates.
3. **P2P NAT Traversal Over-Optimism:**
   - Standard agents propose pure WebRTC peer-to-peer mesh synchronization, ignoring that 15–25% of real-world peers sit behind symmetric NAT firewalls requiring TURN relay infrastructure or a local-first client-server sync server.
4. **License Ambiguity in Canonical Libraries (Yjs):**
   - The GitHub API historically reported `NOASSERTION` for `yjs/yjs` due to non-standard copyright header formatting. Standard research agents often flag this as a legal risk or missing license, whereas source inspection confirms standard permissive MIT.

---

## 4. Ground-Truth Solution Space & Evidence Baseline

### Canonical Open-Source Repositories
- **`automerge/automerge`** (Rust / Wasm, MIT): High-performance CRDT with compact binary columnar encoding, specifically designed for local-first software.
- **`yjs/yjs`** (JavaScript, MIT): Industry-standard shared data types (`Y.Doc`, `Y.Text`, `Y.Map`) with battle-tested bindings for ProseMirror, Quill, and Monaco.
- **`vlcn-io/cr-sqlite`** (Rust / C, MIT): SQLite loadable extension converting standard tables into conflict-free replicated relations (CRRs).
- **`powersync-ja/powersync-js`** (TypeScript, Apache-2.0): Client SDK for offline-first SQLite sync with backend replication streams.
- **`outline/outline`** (TypeScript, BSL-1.1): Comprehensive team knowledge base; high-risk for commercial reuse due to BSL non-compete rider.

### Academic Research Foundations
- **Kleppmann et al. (2019):** *Local-first software: you own your data, in spite of the cloud* (ACM Onward!, DOI: 10.1145/3359591.3359737). Seminal paper defining the 7 ideals of local-first software.
- **Siffre et al. (2025):** *Local-First Software for Green IT* (IEEE ICT4S, DOI: 10.1109/ict4s68164.2025.00015). Validates network and energy efficiency of client-side CRDT replication.
- **Klokmose et al. (2024):** *MyWebstrates: Webstrates as Local-first Software* (ACM UIST, DOI: 10.1145/3654777.3676445).

### Cross-Industry Computational Mechanisms
- **Distributed Version Control (Git DAGs):** Directed acyclic graph commit topologies and 3-way merge algorithms.
- **Avionics Flight Data Recorders:** Append-only delta logs and deterministic crash-recovery replays.

---

## 5. Scoring Expectation & Rubric Anchors for Scenario A

| Dimension | Minimal Baseline Expectation | High-Quality BeenHere Expectation |
| :--- | :--- | :--- |
| **D1: Solutions Discovered** | Mentions Yjs or Automerge and generic SQLite. | Identifies Yjs, Automerge, CR-SQLite, PowerSync, and Outline, distinguishing relational from document sync. |
| **D2: Reusable Code** | High-level advice to "use CRDTs". | Inspects exact source files (`automerge/src/lib.rs`, `cr-sqlite/src/lib.rs`), identifies exported classes (`Y.Doc`, `Y.Text`), and notes OPFS storage drivers. |
| **D3: Accuracy & Evidence** | Plausible links, but unverified API claims. | Strict evidence tags (`[VERIFIED-SOURCE]`, `[VERIFIED-METADATA]`); resolves Yjs `NOASSERTION` to source MIT. |
| **D4: Licensing & Risk** | Claims Outline is open-source based on GitHub stars. | Catches BSL-1.1 non-compete clause in Outline; clears Yjs and Automerge as permissive MIT. |
| **D5: Cross-Industry** | Superficial analogy (*"like Git for notes"*). | Explains Git DAG topological merge vs state-based CRDT lattice convergence with transferability assessment. |
| **D6: Recommendation** | Vague advice to build on Electron + SQLite. | Decisive blueprint: Adopt Automerge or Yjs for editor CRDT, integrate CR-SQLite for relational queries, build custom E2EE key exchange. |
