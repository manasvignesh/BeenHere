# Existing Solutions & Prior Art Analysis

This document analyzes existing open-source projects, agent skills, and research frameworks related to code reuse, prior-art discovery, and idea validation. It defines BeenHere's architectural positioning, reusable concepts, gaps, and differentiation.

---

## 1. Comparative Landscape Overview

| Project | Primary Focus | Runtime Model | External Dependencies | Core Strength | Key Limitation Relative to BeenHere |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ai-Eastern/reuse-before-build** | Local codebase reuse | Agent Skill (Markdown prompt) | None | Enforces "Take / Borrow / Build" checklist inside project | Does not search external open-source, academic papers, or cross-vertical domains |
| **shimo4228/search-first** | Web/registry check | Claude Code Skill | Live web search tool | Quick "look before you leap" habit enforcement | Surface-level keyword search; no deep code inspection, reusability rubric, or build decision logic |
| **danielvm-git/bigpowers** | Solo dev engineering discipline | Agent Skills & MCP Server | Optional MCP server | Structured SDLC workflows (`investigate-bug`, `find-way`, `inspect-quality`) | Focused on implementation execution rather than macro prior-art discovery or cross-industry analogy |
| **ferdinandobons/startup-skill** | Business & venture validation | Agent Skill suite | Web search / LLM | Market analysis, competitor positioning, financial planning | Commercial and pitch-deck focus; lacks technical AST/manifest inspection, license legal audits, or code extraction |
| **sumedh-aerram/Trove** | Open-source discovery for builders | MCP Server & Data layer | MCP server, centralized index | Maps starter templates, libraries, and papers directly to ideas | Dependent on an MCP server and curated index; cannot operate in zero-dependency, air-gapped, or stdlib-only environments |
| **Tendo33/IdeaGo** | Startup pain signal discovery | AI validation pipeline | External APIs / LLM | Extracts customer pain points and whitespace from forum/social signals | Focuses on market demand and marketing angles; ignores software architecture, licensing, and code reusability |
| **assafelovic/gpt-researcher** | Autonomous web research | Multi-agent Python framework | Paid API keys (Tavily, OpenAI/Anthropic), local server | Deep multi-agent web scraping, synthesis, and cited reporting | Heavy framework overhead; requires paid search/LLM API keys; not a portable drop-in agent skill for coding environments |

---

## 2. In-Depth Analysis of Individual Solutions

### 2.1 Ai-Eastern / reuse-before-build
- **Repository:** `https://github.com/Ai-Eastern/reuse-before-build`
- **Functionality:** Prompts coding agents (Claude Code, Cursor, Copilot) to execute a three-step evaluation—*Take* (existing local code/utilities), *Borrow* (already installed dependencies), and *Build* (authoring new code only as a last resort).
- **Overlap with BeenHere:** Both tools share the fundamental ethos that software agents must resist the reflex to immediately generate boilerplate or duplicate existing capabilities.
- **Reusable Concepts:** The clean categorical distinction between internal reuse (*Take*), external dependency reuse (*Borrow*), and custom development (*Build*).
- **Missing Capabilities:** Operates strictly within local repository boundaries. It does not search GitHub for new open-source libraries, does not evaluate licenses, and does not conduct cross-vertical technical transfer.
- **Integration Opportunities:** BeenHere's internal build decision engine can invoke a *Take/Borrow/Build* verification stage once a broader open-source component is imported.
- **License Considerations:** Typically MIT/Apache-2.0. Clean conceptual reuse without copying prompt text verbatim.

### 2.2 shimo4228 / search-first
- **Repository:** `https://github.com/shimo4228/search-first`
- **Functionality:** A concise skill designed for Claude Code that reminds the model to execute a quick web or package registry lookup before attempting to solve a problem with custom algorithms.
- **Overlap with BeenHere:** Proactive search habit prior to coding.
- **Reusable Approaches:** Lightweight trigger mechanisms and direct invocation patterns (`/search-first`).
- **Missing Capabilities:** No structured multi-tier querying, no rate-limited GitHub discovery tool, no license compliance checks, no architectural evaluation, and no cross-vertical mechanism extraction.
- **Integration Opportunities:** Can act as a rapid preliminary check, escalating to BeenHere when an idea warrants deep architectural exploration.
- **License Considerations:** Permissive open source.

### 2.3 danielvm-git / bigpowers
- **Repository:** `https://github.com/danielvm-git/bigpowers`
- **Functionality:** A collection of prescriptive engineering practices codified as agent skills (`find-way`, `investigate-bug`, `plan-work`), accessible directly via Markdown or served dynamically through an MCP server.
- **Overlap with BeenHere:** Rigorous engineering discipline and structured markdown artifacts to guide agent reasoning.
- **Reusable Approaches:** Modular skill composition, clean separation between operational instructions and reference rubrics.
- **Missing Capabilities:** Focuses on tactical engineering tasks during the build cycle rather than pre-implementation prior art, patent/licensing clearance, or cross-domain architectural transfer.
- **Integration Opportunities:** BeenHere outputs (e.g. an `IDEA_LANDSCAPE.md` or `REUSE_REPORT.md`) can feed directly into `bigpowers/plan-work` to structure subsequent implementation tickets.
- **License Considerations:** Permissive open source.

### 2.4 ferdinandobons / startup-skill
- **Repository:** `https://github.com/ferdinandobons/startup-skill`
- **Functionality:** AI agent skill focused on startup design, competitor tear-downs, market sizing, value proposition design, and commercial viability assessment.
- **Overlap with BeenHere:** Both analyze a user's initial idea and investigate existing entities solving the problem.
- **Reusable Approaches:** Structured competitive comparison tables and explicit problem-solution framing.
- **Missing Capabilities:** Highly commercial and managerial in orientation. Does not inspect git repositories, cannot verify license compatibility, does not evaluate dependency trees, and ignores technical mechanism transfer.
- **Integration Opportunities:** Complements BeenHere: `startup-skill` addresses commercial/market viability, while BeenHere addresses technical prior art, code reusability, and architectural feasibility.
- **License Considerations:** Permissive open source.

### 2.5 sumedh-aerram / Trove
- **Repository:** `https://github.com/sumedh-aerram/Trove`
- **Functionality:** A discovery platform that maps open-source repositories, starter kits, and papers to builder concepts, exposed as an MCP server.
- **Overlap with BeenHere:** Shared focus on open-source prior art and starter kit discovery for developers.
- **Reusable Approaches:** Query-to-repository semantic mapping and classification by repository archetype (framework, starter, library).
- **Missing Capabilities:** Requires an active MCP server and hosted backend; cannot run offline or in constrained agent sessions. Lacks cross-vertical analogy extraction and in-depth license legal risk evaluation.
- **Integration Opportunities:** In Phase 2, BeenHere can optionally support Trove as an optional MCP provider while retaining its standalone stdlib fallback.
- **License Considerations:** Permissive open source.

### 2.6 Tendo33 / IdeaGo
- **Repository:** `https://github.com/Tendo33/IdeaGo`
- **Functionality:** Competitor validation engine designed to surface market whitespace and commercial pain points from public discourse.
- **Overlap with BeenHere:** Discovery of existing solutions in the problem space.
- **Reusable Approaches:** Systematic extraction of "unmet needs" and "unresolved complaints" from user discussions.
- **Missing Capabilities:** Non-technical; cannot inspect codebase manifests, determine copyleft viral triggers, or synthesize cross-vertical engineering algorithms.
- **Integration Opportunities:** Insights regarding competitor customer complaints can be incorporated into BeenHere's Feature Gap Analysis.
- **License Considerations:** Permissive open source.

### 2.7 assafelovic / gpt-researcher
- **Repository:** `https://github.com/assafelovic/gpt-researcher`
- **Functionality:** Autonomous research agent that queries search engines, scrapes multi-page sources, filters for relevance, and writes long-form research papers with citations.
- **Overlap with BeenHere:** Multi-step research protocol, objective evidence gathering, and structured report synthesis.
- **Reusable Approaches:** Comprehensive evidence aggregation and citation integrity standards.
- **Missing Capabilities:** Requires dedicated Python execution environments, background server processes, and multiple paid API keys (Tavily, SerpAPI, OpenAI/Anthropic). Heavyweight and not native to interactive agent skill environments.
- **Integration Opportunities:** BeenHere can be configured to read reports generated by GPT Researcher as an external evidence input.
- **License Considerations:** Apache-2.0.

---

## 3. Official Agent Skill Specifications (Claude Code & OpenAI Codex)

### 3.1 Claude Code Agent Skill Specification
- **Format:** Directory-based skill defined by a root `SKILL.md` file containing YAML frontmatter delimited by `---`.
- **Key Attributes:**
  - `name`: Lowercase alphanumeric with hyphens (`1-64` chars). Must match the containing folder name.
  - `description`: 1-3 sentences stating purpose and activation triggers (max 1024 chars). Claude Code indexes this description at startup to decide when to activate the skill.
  - `allowed-tools`: List of agent tools permitted without explicit human approval (e.g. `Bash`, `Read`, `Grep`, `Glob`).
  - `compatibility`: String outlining environment prerequisites.
- **Progressive Disclosure:** Keeps the main `SKILL.md` body concise, referencing detailed files in `references/`, scripts in `scripts/`, and templates in `templates/` to prevent context window bloat.

### 3.2 OpenAI Codex Skill Specification
- **Format:** Compatible with standard Agent Skill conventions, reading instructions from `.agents/skills/<skill-name>/` (or user-global `~/.agents/skills/<skill-name>/`).
- **Key Attributes:** Emphasizes deterministic shell utilities, idempotent execution, clear parameter hints, and standard Markdown reporting.

---

## 4. BeenHere's Differentiators

BeenHere is specifically engineered to bridge the gap between superficial search prompts and heavyweight, paid research platforms:

1. **Zero-Dependency & Zero-Cost:** Runs entirely on standard Python 3.8+ libraries and native agent tools. No mandatory API keys, no paid search engines, no hosted backends.
2. **Deterministic Code & License Inspection:** Uses programmatic parsing of GitHub APIs, manifests (`package.json`, `pyproject.toml`, `Cargo.toml`), and license files. Rejects marketing claims in favor of verifiable technical facts.
3. **Cross-Vertical Mechanism Abstraction (Mandatory Differentiator):** Strips away surface-level terminology to identify analogous mechanical solutions in robotics, gaming, simulation, economics, and aerospace.
4. **Transparent Evidence Hierarchy:** Enforces explicit tagging (`[VERIFIED-TEST]`, `[VERIFIED-SOURCE]`, `[VERIFIED-METADATA]`, `[INFERRED]`, `[UNKNOWN]`) to maintain research integrity and prevent AI hallucination.
5. **Actionable Build Decision Intelligence:** Replaces vague advice with a definitive, defensible posture: *Adopt*, *Fork*, *Extend*, *Extract*, *Integrate*, or *Build from Scratch*.
