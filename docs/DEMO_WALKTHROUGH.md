# BeenHere — Reproducible Demo Walkthrough & Video Script

This document provides a step-by-step, reproducible demonstration script for **BeenHere v1.0.0**, along with a storyboard and video voiceover script for product showcases and developer tutorials.

---

## 1. Reproducible Interactive Demo

### Demo Scenario
> **Developer Pitch:**  
> *"I want to build an offline-first collaborative Markdown canvas where multiple users sketch, write, and organize notes together without an active internet connection, syncing via local-first CRDTs and storing documents in embedded SQLite."*

---

### Step 1: Installation in Clean Project (Terminal)

```bash
# In your target project directory:
python /path/to/beenhere/scripts/install_skill.py --agent all
```
**Terminal Output:**
```text
=== Installing BeenHere Skill in /workspace [mode: copy] ===
 ✓ Claude Code: /workspace/.claude/skills/beenhere -> installed
 ✓ OpenAI Codex: /workspace/.agents/skills/beenhere -> installed
```

---

### Step 2: Mode A — Quick Exploration (Chat Interface)

**User Prompt:**
```text
/beenhere I want to build an offline-first collaborative notes and canvas app using local-first CRDTs and SQLite in Rust/TypeScript.
```

**BeenHere Agent Response:**
```markdown
### BeenHere Quick Exploration: Offline-First Collaborative Canvas

1. **Top 3 Discovered Repositories:**
   - **[automerge/automerge](https://github.com/automerge/automerge)** (Stars: 17k+, MIT)
     - *Verified:* Robust Rust CRDT core with high-performance JS/Wasm bindings and columnar binary compression. Active maintenance.
   - **[yjs/yjs](https://github.com/yjs/yjs)** (Stars: 16k+, MIT)
     - *Verified:* Dominant web ecosystem CRDT with battle-tested bindings for canvas editors (Y-Sweet, ProseMirror).
   - **[vlcn-io/cr-sqlite](https://github.com/vlcn-io/cr-sqlite)** (Stars: 3.5k+, MIT)
     - *Verified:* Run-time loadable SQLite extension providing column-level CRDT conflict resolution directly in SQL tables.

2. **Core Reusable Components vs Custom Build:**
   - *Off-the-Shelf:* CRDT state vectors and document syncing (`automerge` or `yjs`), local SQL conflict convergence (`cr-sqlite`).
   - *Must Build:* Canvas coordinate spatial indexing (R-Tree/QuadTree for freeform elements), peer-to-peer discovery (mDNS/WebRTC mesh), and canvas drag-drop UI.

3. **Critical Hazards & Trade-offs:**
   - Automerge provides native Rust ergonomics, whereas Yjs offers broader canvas widget integrations in web environments.
   - Using `cr-sqlite` requires compiling native SQLite C extensions into client builds.

4. **Initial Recommendation:**
   - **Posture: `ADOPT_AND_EXTEND`**
   - Adopt `automerge` for core document state or `cr-sqlite` for structured relational local storage; build only the spatial canvas coordinate manager.

*Would you like to narrow down whether this will target desktop (Tauri/Rust) or web browsers first? We can run a full deep blueprint whenever you're ready (`/beenhere --deep`).*
```

---

### Step 3: Mode B — Deep Blueprint Generation (Chat Interface)

**User Prompt:**
```text
/beenhere --deep Focus on a desktop Tauri app with local embedded SQLite.
```

**BeenHere Execution Flow:**
1. Runs `scripts/concept_expander.py` decomposing spatial indexing, CRDT convergence, and SQLite transactions.
2. Runs `scripts/paper_search.py` querying conflict-free replicated data types and causal trees (e.g. Kleppmann et al.).
3. Runs `scripts/integration_analyzer.py` on candidate repository manifests (`Cargo.toml`) and exported entrypoints.
4. Generates comprehensive `IDEA_LANDSCAPE.md` and `INTEGRATION_BLUEPRINT.md`.
5. Verifies all links and evidence tags using `scripts/verify_sources.py`.

---

## 2. Video Recording Script & Storyboard (3 Minutes)

| Time | Visual / Screen Action | Voiceover Audio (Spoken Track) |
| :--- | :--- | :--- |
| **0:00 - 0:25** | Developer opens terminal, types a quick idea into an AI chat: *"Build me a new voice social platform from scratch."* Agent starts writing hundreds of lines of boilerplate. | "Every day, developers and AI coding agents reinvent wheels that have already been perfected. We jump straight to coding without exploring what has already been built, tested, and open-sourced." |
| **0:25 - 0:50** | Cut to BeenHere logo and GitHub repository. Run `python scripts/install_skill.py`. Clean terminal output showing `.claude` and `.agents` installation. | "Meet BeenHere — a portable, zero-dependency Agent Skill for Claude Code, Codex, and Agent Skills CLI. Before you write code, BeenHere explores your idea across open-source code, academic literature, and cross-industry engineering." |
| **0:50 - 1:30** | Switch to Claude Code terminal session. Type: `/beenhere I want to build a voice-first synthetic social platform.` Terminal instantly streams the 4-part summary. | "BeenHere features two invocation modes. In Quick Exploration mode, you get an immediate four-part triage: top discovered repositories with verified stars and licenses, what's off-the-shelf versus what must be built, critical legal hazards, and a build-vs-buy recommendation." |
| **1:30 - 2:15** | Type `/beenhere --deep`. Agent runs concept expander, repo inspector, and academic search. Open the generated `INTEGRATION_BLUEPRINT.md`. Highlight the architecture diagram and data contracts. | "Need an exhaustive architectural plan? Mode B runs a 14-step deep investigation. BeenHere parses actual AST symbols, detects breaking dependency constraints, flags copyleft obligations like AGPL or BSL-1.1, and delivers a complete, verified Integration Blueprint." |
| **2:15 - 2:45** | Run `python -m unittest discover tests -v` (74 tests pass in <0.4s) and `python scripts/benchmark_runner.py` (10/10 pass). Show `scripts/validate_skill.py` reporting valid. | "BeenHere requires zero paid APIs, no hosted databases, and zero pip packages — running entirely on standard library Python. It includes 74 automated unit tests and a 10-domain benchmark suite." |
| **2:45 - 3:00** | GitHub repo on screen: `github.com/beenhere/beenhere`. End title card: *"Discover what's built. Build only what matters."* | "Stop reinventing the wheel. Discover what's built, reuse what works, and build only what matters with BeenHere. Install it today with `npx skills add` or grab it on GitHub." |
