# BeenHere 🧭

> **Explore every angle of an idea before you build it.**
> 
> *Discover what's built. Explore what's possible. Reuse what works. Improve what's missing. Build only what matters.*

---

**BeenHere** is a portable, zero-dependency Agent Skill for AI coding environments (including **Anthropic Claude Code** and **OpenAI Codex**). It investigates ideas across open-source code repositories, academic research, and cross-vertical industry patterns before developers commit time and resources to implementation.

---

## The Problem

Developers and AI coding agents routinely reinvent solutions that already exist:
- **Redundant Development:** Writing from scratch what has already been solved and tested.
- **Surface-Level Searches:** Stopping after a single GitHub query returns zero direct matches, assuming an idea is completely novel.
- **Legal & License Hazards:** Reusing code without checking license permissions, copyright boundaries, or copyleft implications.
- **Siloed Thinking:** Missing elegant, proven architectural patterns and mechanisms developed in adjacent industries (such as gaming, robotics, simulation, and aerospace).

## The Six Intelligence Capabilities

BeenHere equips AI coding agents with six structured analytical capabilities:

1. **Prior-Art Discovery (`A`):** Multi-tier search covering direct keyword variants, functional primitives, underlying protocols, and academic papers.
2. **Code Reusability Analysis (`B`):** Deep inspection of licenses, architectural coupling, modularity, dependency trees, and maintenance vitals. Rejects "README claims" in favor of code inspection.
3. **Cross-Vertical Exploration (`C`):** Mechanism-level abstraction that maps software concepts to parallel solutions in unrelated engineering and scientific domains.
4. **Feature Gap Analysis (`D`):** Systematic comparison between existing solutions and the target concept, determining whether missing features represent deliberate trade-offs or genuine opportunities.
5. **Enhancement Discovery (`E`):** Identification of breakthrough mechanisms from adjacent fields to elevate existing solutions.
6. **Build Decision Intelligence (`F`):** Defensible, qualitative recommendations: *Adopt*, *Fork*, *Extend*, *Extract*, *Integrate*, *Build from Scratch*, or *Investigate Further*.

---

## Repository Structure

```
beenhere/
├── SKILL.md                          # Canonical Agent Skill definition (Claude Code & Codex compatible)
├── README.md                         # Project overview and documentation
├── LICENSE                           # MIT License
├── .gitignore                        # Standard development ignores
├── scripts/                          # Deterministic Python stdlib utilities
│   ├── github_search.py              # Repository discovery with query expansion and rate-limit safety
│   ├── repo_inspector.py             # Deep repository metadata, license, and manifest inspector
│   └── verify_sources.py             # Source link validation and evidence classification auditor
├── references/                       # Research protocols and evaluation rubrics
│   ├── discovery_methodology.md      # 4-Tier Search Protocol and query expansion guide
│   ├── cross_vertical_research.md    # Mechanism abstraction and cross-industry mapping rubric
│   ├── code_reusability.md           # Legal taxonomy, architectural coupling, and reuse blocker guide
│   └── evaluation_rubric.md          # Qualitative build decision framework & evidence standards
├── templates/                        # Structured markdown reporting templates
│   ├── IDEA_LANDSCAPE.md             # Comprehensive idea landscape report template
│   └── REUSE_REPORT.md               # Focused repository reusability audit template
├── tests/                            # Automated test suite (Python stdlib unittest)
│   └── test_core.py                  # Unit and mock tests for all scripts and workflows
├── examples/                         # Verified research reports
│   └── voice_social_platform/        # Voice-first synthetic social platform landscape
│       └── IDEA_LANDSCAPE.md
└── docs/                             # In-depth architectural and integration documentation
    ├── EXISTING_SOLUTIONS.md         # Comparative analysis of prior art & related tools
    ├── ARCHITECTURE.md               # Technical design and progressive disclosure model
    └── INSTALLATION.md               # Installation and integration guides
```

---

## Quick Start

### Installation

#### Anthropic Claude Code
Place the skill into your project or global skills directory:
```bash
# Per-project installation:
mkdir -p .claude/skills/beenhere
cp -r * .claude/skills/beenhere/

# Or global installation:
mkdir -p ~/.claude/skills/beenhere
cp -r * ~/.claude/skills/beenhere/
```

#### OpenAI Codex / AGY
Place the skill in your agent skills folder:
```bash
mkdir -p .agent/skills/beenhere
cp -r * .agent/skills/beenhere/
```

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for full instructions.

---

## Deterministic Utilities

All tools in `scripts/` require only standard Python 3.8+ (no third-party dependencies):

```bash
# 1. Search GitHub for prior art (supports multi-query and deduplication)
python scripts/github_search.py --queries "voice agent" "conversational AI" --limit 10 --json

# 2. Inspect a specific repository for license, dependencies, and health
python scripts/repo_inspector.py --repo "pipecat-ai/pipecat" --json

# 3. Verify markdown links and evidence tags in a report
python scripts/verify_sources.py --file templates/IDEA_LANDSCAPE.md
```

Run test suite:
```bash
python -m unittest discover tests -v
```

---

## Research Integrity Standards

BeenHere enforces strict evidence standards to eliminate AI hallucinations and unfounded claims:

- `[VERIFIED-TEST]`: Verified by executing code or automated tests in a sandbox.
- `[VERIFIED-SOURCE]`: Verified by inspecting source files or manifests directly.
- `[VERIFIED-METADATA]`: Verified through official API metadata or headers.
- `[INFERRED]`: Deductive analysis grounded in verified facts.
- `[UNKNOWN]`: Unverified or inaccessible data explicitly marked as unknown.

---

## License

BeenHere is licensed under the [MIT License](LICENSE).
