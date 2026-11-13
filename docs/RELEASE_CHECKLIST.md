# BeenHere v1.0.0 Release Verification Checklist

This checklist must be executed and verified before tagging and publishing any release candidate or major version of BeenHere.

---

## 1. Codebase & Architectural Integrity

- [x] **Zero Third-Party Dependencies:**
  - All scripts in `scripts/` import strictly standard library modules (`sys`, `os`, `re`, `json`, `ast`, `urllib`, `argparse`, `pathlib`, `shutil`, `tempfile`).
  - No `requirements.txt` or `package.json` required to run BeenHere CLI tools.
- [x] **Cross-Platform Compatibility:**
  - Validated on Windows, Linux, and macOS path conventions.
  - Safe handling of symlinks and directory junctions.
- [x] **Standard Frontmatter in `SKILL.md`:**
  - Valid YAML delimited by `---`.
  - Fields present: `name`, `description`, `license`, `compatibility`, `metadata.version`, `allowed-tools`.
- [x] **Evidence Standards Enforced:**
  - Standardized evidence tagging (`[VERIFIED-TEST]`, `[VERIFIED-SOURCE]`, `[VERIFIED-METADATA]`, `[UNVERIFIED-MARKETING-CLAIM]`, `[INFERRED]`, `[UNKNOWN]`).
  - No arbitrary percentage estimations.
- [x] **Prompt Injection Defenses & Realistic Security Disclosures:**
  - Input text from external READMEs, manifests, and issues is sanitized for system prompt overrides.
  - External excerpts wrapped within `<untrusted_external_content>` tags.
  - Residual risk disclosures explicitly stated (no claims of 100% prompt injection immunity).
- [x] **Real-World Agent Execution & Sandbox Fallback:**
  - Verified in OpenAI Codex (`docs/CODEX_END_TO_END_TEST.md`).
  - Graceful socket permission error handling (`[WinError 10013]`) with fallback recommendations.
  - Accurate disclosure that live authenticated Claude Code execution has not yet occurred.

---

## 2. Automated Test & Benchmark Verification

- [x] **Unit Test Suite:**
  ```bash
  python -m unittest discover tests -v
  ```
  *Requirement:* 100% passing (74/74 unit tests).
- [x] **Benchmark Evaluation Suite:**
  ```bash
  python scripts/benchmark_runner.py
  ```
  *Requirement:* 100% passing (10/10 diverse domain evaluation cases).
- [x] **Packaging & Credential Hygiene Validator:**
  ```bash
  python scripts/validate_skill.py
  ```
  *Requirement:* `[PASS] VALID` across `skill_md`, `scripts`, and `secrets`.

---

## 3. Installation & Agent Ecosystem Verification

- [x] **Agent Skills CLI Compatibility:**
  - Compatible with `npx skills add <url> --agent claude-code codex`.
- [x] **Automated Python Installer (`scripts/install_skill.py`):**
  - Project-local installation: `.claude/skills/beenhere/` and `.agents/skills/beenhere/`.
  - Global user installation: `~/.claude/skills/beenhere/` and `~/.agents/skills/beenhere/`.
  - Tested `--dry-run`, `--uninstall`, and re-installation idempotence.
- [x] **Dual Invocation Modes:**
  - Mode A: Quick Exploration (`/beenhere <idea>`) tested for conversational responsiveness and max 1–2 clarifying questions.
  - Mode B: Deep Investigation (`/beenhere --deep <idea>`) tested for full `IDEA_LANDSCAPE.md` and `INTEGRATION_BLUEPRINT.md` generation.

---

## 4. Documentation & Open Source Release Assets

- [x] `README.md` updated with architecture, badges, quickstart, and example links.
- [x] `CONTRIBUTING.md` created with engineering standards, testing, and PR workflow.
- [x] `SECURITY.md` created with vulnerability disclosure and prompt injection threat model.
- [x] `CHANGELOG.md` updated with Keep-a-Changelog SemVer entries.
- [x] `.github/workflows/test.yml` configured for matrix testing Python 3.8–3.13 on Ubuntu, Windows, and macOS.
- [x] `.github/ISSUE_TEMPLATE/` populated with `bug_report.md` and `feature_request.md`.
- [x] `docs/INSTALLATION.md` verified with instructions for all agent targets.
- [x] `docs/DEMO_WALKTHROUGH.md` authored with reproducible user prompts and video script.

---

## 5. Release Approval Sign-Off

- **Target Version:** `v1.0.0-beta.1`
- **Release Status:** Ready for local Git commit. (No remote push, public publish, or public tag).
