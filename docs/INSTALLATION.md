# BeenHere — Installation & Agent Integration Guide

This guide covers installing and configuring **BeenHere** for **Anthropic Claude Code**, **OpenAI Codex**, and the **Agent Skills CLI** (`npx skills`).

---

## Prerequisites

- **Python:** Python 3.8 or newer (standard library only; zero pip dependencies).
- **Operating System:** Linux, macOS, or Windows (10/11/Server).
- **Target Agents:** Anthropic Claude Code (v1.0+) or OpenAI Codex.
- **Optional:** Internet access for live repository queries and academic paper search.

---

## 1. Quick Installation via Agent Skills CLI (`npx skills`)

The official `skills` CLI provides a unified way to install BeenHere directly into your agent configurations:

```bash
# Install BeenHere from GitHub:
npx skills add manasvignesh/BeenHere --agent claude-code codex

# Install BeenHere into both Claude Code and OpenAI Codex from a local clone:
npx skills add /path/to/beenhere --agent claude-code codex

# Install globally across all user projects:
npx skills add manasvignesh/BeenHere --global --agent claude-code codex
```

> [!NOTE] Runtime Execution Status
> - **OpenAI Codex:** Verified in real-world end-to-end execution on an AI recruitment platform in an isolated project (see [docs/CODEX_END_TO_END_TEST.md](docs/CODEX_END_TO_END_TEST.md)).
> - **Anthropic Claude Code:** Verified structurally and discovered by `npx skills`, but live authenticated runtime execution in Claude Code has not yet been performed.

---

## 2. Automated Python Installer (`scripts/install_skill.py`)

BeenHere includes a standalone cross-platform installer script using Python's standard library:

```bash
# Install to current project for both Claude Code and OpenAI Codex (default):
python scripts/install_skill.py

# Install to a specific project directory:
python scripts/install_skill.py --target-dir /path/to/my-project

# Install specifically for Claude Code or OpenAI Codex:
python scripts/install_skill.py --agent claude
python scripts/install_skill.py --agent codex

# Install globally to user profile (~/.claude/skills/ and ~/.agents/skills/):
python scripts/install_skill.py --global

# Preview actions without modifying disk:
python scripts/install_skill.py --dry-run

# Uninstall cleanly from target location:
python scripts/install_skill.py --uninstall
```

---

## 3. Manual Installation

If you prefer to place files manually:

### Anthropic Claude Code
Place the skill files into `.claude/skills/beenhere/`:
```bash
# Project-local installation (macOS/Linux):
mkdir -p .claude/skills/beenhere
cp -r /path/to/beenhere/* .claude/skills/beenhere/

# Global user installation (macOS/Linux):
mkdir -p ~/.claude/skills/beenhere
cp -r /path/to/beenhere/* ~/.claude/skills/beenhere/

# Windows PowerShell:
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills\beenhere"
Copy-Item -Recurse -Force c:\path\to\beenhere\* "$HOME\.claude\skills\beenhere\"
```

### OpenAI Codex
Place the skill files into `.agents/skills/beenhere/` following the official Codex agent skills specification:
```bash
# Project-local installation (macOS/Linux):
mkdir -p .agents/skills/beenhere
cp -r /path/to/beenhere/* .agents/skills/beenhere/

# Global user installation (macOS/Linux):
mkdir -p ~/.agents/skills/beenhere
cp -r /path/to/beenhere/* ~/.agents/skills/beenhere/

# Windows PowerShell:
New-Item -ItemType Directory -Force -Path "$HOME\.agents\skills\beenhere"
Copy-Item -Recurse -Force c:\path\to\beenhere\* "$HOME\.agents\skills\beenhere\"
```

---

## 4. Verifying Skill Activation & Usage

Start a session with your AI coding assistant:

### Mode A: Quick Exploration
Trigger rapid discovery with minimal overhead:
```text
/beenhere I want to build a local vector database for edge devices in Rust.
```
**Expected Response:**
- Top 3 candidate repositories with star counts, license status, and maintenance health.
- Breakdown of existing building blocks vs custom code required.
- Key license/architecture hazards.
- Initial build-vs-buy recommendation (*Adopt, Fork, Integrate, Build from Scratch*).
- At most 1–2 clarifying questions to narrow down technical trade-offs.

### Mode B: Deep Investigation
Trigger complete architectural and integration intelligence:
```text
/beenhere --deep A voice-first multi-agent social platform with dialectical debate arbitration.
```
**Expected Deliverables:**
- `IDEA_LANDSCAPE.md`: Complete 15-section prior art landscape, academic foundations, and cross-vertical solutions.
- `INTEGRATION_BLUEPRINT.md`: Full architectural boundary definition, AST exported symbols, data contract schemas, and license clearance matrix.

---

## 5. Configuration & Authentication (Optional)

BeenHere operates out of the box with **zero configuration** using public endpoints (GitHub public API, OpenAlex, arXiv, Semantic Scholar).

To increase GitHub rate limits from 60 to 5,000 requests/hour, set a standard GitHub personal access token in your environment:

```bash
# Linux/macOS
export GITHUB_TOKEN="ghp_yourTokenHere"

# Windows PowerShell
$env:GITHUB_TOKEN="ghp_yourTokenHere"
```

BeenHere automatically detects `GITHUB_TOKEN` and applies it to authenticated requests.
