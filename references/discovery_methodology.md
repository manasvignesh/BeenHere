# BeenHere — Prior-Art Discovery Methodology

This document outlines the systematic, reproducible 4-tier discovery protocol used by BeenHere to explore prior art, open-source repositories, academic literature, and technical implementations.

---

## The 4-Tier Discovery Protocol

A common failure mode of AI coding agents and human engineers is stopping at a single literal keyword search. If a search for *"voice-first AI debate platform"* yields no direct products, an agent might falsely conclude that nothing similar exists. 

BeenHere decomposes an idea into four concentric investigation tiers:

```
  ┌────────────────────────────────────────────────────────┐
  │ Tier 1: Direct Matches (Literal Product Terminology)   │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Tier 2: Functional Primitives (Component Architecture) │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Tier 3: Technical Mechanisms (Protocols & Algorithms)  │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │ Tier 4: Cross-Vertical Analogies (Unrelated Domains)   │
  └────────────────────────────────────────────────────────┘
```

---

### Tier 1: Direct Matches (Literal Terminology)
- **Objective:** Find existing commercial products, open-source repositories, or turnkey platforms attempting to solve the exact specified user problem.
- **Search Formulation:**
  - Full product description phrases.
  - User persona and target use-case keywords.
  - Direct competitor and platform names.
- **Query Examples:**
  - `"voice social platform"`
  - `"AI debate arena"`
  - `"synthetic social network"`
- **Triage Criteria:** Look for end-to-end applications, SaaS platforms, or complete open-source projects.

### Tier 2: Functional Primitives (Component Architecture)
- **Objective:** Deconstruct the target idea into its foundational architectural building blocks and search for specialized implementations of each block.
- **Methodology:** Break the idea down into discrete subsystems:
  1. *Ingestion & Transport Layer* (Audio capture, WebRTC, real-time streaming).
  2. *Orchestration & State Management* (Turn-taking, conversation graphs, speaker arbitration).
  3. *Cognitive & Persona Layer* (Character definitions, system prompt steering, long-term memory).
  4. *Evaluation & Consensus Layer* (Argument mapping, assumption validation, voting).
- **Query Examples:**
  - `"WebRTC voice pipeline agent"`
  - `"conversational turn taking state machine"`
  - `"agent memory persistent profile"`
  - `"multi-agent consensus protocol"`
- **Triage Criteria:** Look for dedicated libraries, SDKs, middleware, and reusable modules.

### Tier 3: Technical Mechanisms (Protocols, Algorithms & Papers)
- **Objective:** Discover academic research, algorithmic implementations, and formal specifications that underpin the functional primitives.
- **Methodology:** Map engineering features to theoretical mechanisms:
  - *"Challenging assumptions"* $\rightarrow$ Dialectical argumentation frameworks, Socratic dialogue trees, automated theorem proving, debate protocols.
  - *"Synthetic personalities"* $\rightarrow$ Persona-conditioned LLMs, cognitive architectures (SOAR, ACT-R), belief-desire-intention (BDI) agents.
  - *"Group discussion dynamics"* $\rightarrow$ Majority voting, Delphi method, multi-agent reinforcement learning (MARL), social simulation models.
- **Query Examples:**
  - `"dialectical argumentation tree python"`
  - `"belief desire intention multi-agent"`
  - `"delphi method consensus algorithm"`
  - `"generative agents social simulation"`
- **Triage Criteria:** Look for academic reference implementations, peer-reviewed papers (arXiv), and algorithmic reference repositories.

### Tier 4: Cross-Vertical Analogies (Unrelated Domains)
- **Objective:** Explore how identical underlying mechanisms have been implemented and battle-tested in unrelated industries (such as video games, aerospace, financial exchanges, and sociology).
- **Methodology:** Refer to [references/cross_vertical_research.md](cross_vertical_research.md) for mechanism abstraction rules.

---

## Query Expansion Techniques

To achieve comprehensive coverage across diverse developer nomenclature, BeenHere expands every query through four linguistic dimensions:

1. **Syntactic Variants:**
   - Hyphenation vs. spacing: `voice-first`, `voice first`, `voicefirst`
   - Singular vs. plural: `agent`, `agents`
   - Gerund vs. noun: `debating`, `debate`
2. **Taxonomic & Ecosystem Synonyms:**
   - `synthetic personas` $\leftrightarrow$ `AI agents`, `virtual characters`, `NPCs`, `digital twins`
   - `group discussion` $\leftrightarrow$ `multi-agent debate`, `collaborative deliberation`, `panel simulation`
   - `audio streaming` $\leftrightarrow$ `full duplex voice`, `WebRTC bridge`, `VAD (voice activity detection)`
3. **Academic & Research Terminology:**
   - Commercial: *"AI group chat"*
   - Academic: *"agent-based modeling (ABM)"*, *"multi-agent consensus"*, *"artificial society"*
4. **Negative Filtering:**
   - Eliminate noisy tangential results by filtering out irrelevant frameworks or outdated tech stacks where appropriate.

---

## Deduplication and Relevance Triage

When searching across multiple queries:
1. **Deduplication:** Aggregation tools must track unique repository slugs (`owner/repo`) or URLs to avoid duplicate entries in reports.
2. **Relevance Scoring:** Repositories are ranked qualitatively across three primary signals:
   - **Mechanism Overlap:** Does the repository solve the core algorithmic or architectural problem?
   - **Quality & Freshness:** Recent push activity, star count, issue responsiveness, and clear documentation.
   - **Reusability Potential:** Permissive license, clean package manifests, modular API design.

---

## Research Integrity & Handling Search Limitations

1. **No Hallucinated Repositories:** Never generate hypothetical GitHub URLs, nonexistent library names, or fake citation links.
2. **Explicit Fallback Protocol:** If the GitHub API returns rate limit errors or network access is restricted:
   - Record the exact HTTP status code and rate limit reset time.
   - Report the limitation clearly in the report output.
   - Rely on local workspace inspection and host agent verified knowledge base, explicitly tagging all outputs as `[INFERRED]` or `[UNKNOWN]`.
