# BeenHere — Installation & Integration Guide

This guide covers installing and configuring **BeenHere** for Anthropic Claude Code and OpenAI Codex environments.

---

## Prerequisites

- **Python:** Python 3.8 or newer (uses standard library only; no pip dependencies required).
- **Environment:** Compatible with Linux, macOS, and Windows.
- **Network (Optional):** Internet access for live GitHub API search and link verification. Offline mock mode is supported when network access is unavailable.

---

## 1. Installation in Anthropic Claude Code

Claude Code detects skills in either a project-local directory or a global user directory.

### Option A: Project-Local Installation (Recommended for Team Projects)
Inside your target repository:
```bash
# Create the skills directory
mkdir -p .claude/skills/beenhere

# Copy BeenHere files into the skill directory
cp -r /path/to/beenhere/* .claude/skills/beenhere/
```

### Option B: Global User Installation (Available Across All Projects)
Install to your user profile:
```bash
# macOS/Linux:
mkdir -p ~/.claude/skills/beenhere
cp -r /path/to/beenhere/* ~/.claude/skills/beenhere/

# Windows PowerShell:
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills\beenhere"
Copy-Item -Recurse -Force c:\path\to\beenhere\* "$HOME\.claude\skills\beenhere\"
```

### Verification in Claude Code
Start a Claude Code session:
```bash
claude
```
Ask Claude:
```text
Has anyone built a voice-first social platform for multi-agent discussions?
```
Claude Code will automatically evaluate the description in `SKILL.md` and load BeenHere. You can also explicitly invoke the skill:
```text
/beenhere I want to build a local vector database for edge devices.
```

---

## 2. Installation in OpenAI Codex / AGY

OpenAI Codex and Antigravity load skills from `.agent/skills/` or `.codex/skills/`.

### Project Setup
```bash
mkdir -p .agent/skills/beenhere
cp -r /path/to/beenhere/* .agent/skills/beenhere/
```

### Verification
In your Codex or AGY session, activate the skill by asking:
```text
Explore prior art and reusability for: "real-time peer-to-peer collaborative canvas"
```

---

## 3. Configuration & Authentication (Optional)

BeenHere operates out-of-the-box with **zero configuration** using GitHub's unauthenticated public API (limited to 60 queries/hour).

To increase rate limits to 5,000 queries/hour, set a standard GitHub token:

```bash
# Linux/macOS
export GITHUB_TOKEN="ghp_yourPersonalAccessTokenHere"

# Windows PowerShell
$env:GITHUB_TOKEN="ghp_yourPersonalAccessTokenHere"
```

> **Security Note:** BeenHere never stores, logs, or transmits your token to any third-party server. The token is passed strictly in the standard `Authorization: Bearer <token>` header to `https://api.github.com`.

---

## 4. Verifying Your Local Installation

You can test the deterministic scripts directly from your terminal:

### 1. Test GitHub Search
```bash
python scripts/github_search.py --queries "collaborative canvas" "crdt canvas" --limit 5
```
Expected output: A formatted table or JSON array listing top matching repositories, star counts, languages, and license information.

### 2. Test Repository Inspection
```bash
python scripts/repo_inspector.py --repo "pipecat-ai/pipecat"
```
Expected output: A structured summary detailing licenses, language breakdown, detected manifests, and maintainability indicators.

### 3. Run the Automated Test Suite
```bash
python -m unittest discover tests -v
```
All unit tests should pass with zero failures.

---

## 5. Offline and Air-Gapped Environments

If your coding agent operates in a restricted or air-gapped environment without outbound internet access:
- The Python scripts will gracefully catch connection errors and report structured status messages (`status: "network_unavailable"`).
- The BeenHere Agent Skill will fall back to inspecting local project dependencies, searching local submodules, and applying the cross-vertical methodology using the host LLM's internalized knowledge base.
- All evidence gathered offline will be explicitly tagged as `[INFERRED]` or `[UNKNOWN]` to preserve research integrity.

---

## 6. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `HTTP 403: API rate limit exceeded` | GitHub unauthenticated 60 req/hr limit reached | Set `GITHUB_TOKEN` environment variable or wait until rate-limit window resets. |
| `CommandNotFoundException: python` | Python is not in system PATH | Ensure Python 3.8+ is installed and accessible via `python` or `python3`. |
| Skill does not trigger automatically | Description mismatch or agent prompt lacked trigger phrases | Explicitly mention trigger words: *"has this been built?"*, *"explore prior art"*, *"reusability analysis"*, or invoke via `/beenhere`. |
