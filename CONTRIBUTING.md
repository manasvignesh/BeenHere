# Contributing to BeenHere 🧭

Thank you for your interest in contributing to **BeenHere**!

BeenHere is dedicated to helping developers and AI coding agents discover what has already been built before writing redundant code.

---

## 1. Core Engineering Principles

When contributing to BeenHere, all code and documentation must adhere to these foundational principles:

1. **Zero External Dependencies:**
   - All tools in `scripts/` must run strictly on the **Python 3.8+ standard library**.
   - Do **NOT** add third-party dependencies (`requests`, `pydantic`, `pyyaml`, etc.) to the core distribution.
2. **Deterministic & Portable:**
   - Tools must work seamlessly across **Windows**, **macOS**, and **Linux** without environment-specific assumptions.
   - File paths must use `os.path` or `pathlib` for cross-platform compatibility.
3. **Defensible Evidence Standards:**
   - Never introduce hallucinated numbers, arbitrary percentage scores, or unverified claims.
   - All technical statements must follow the evidence tagging hierarchy:
     - `[VERIFIED-TEST]`
     - `[VERIFIED-SOURCE]`
     - `[VERIFIED-METADATA]`
     - `[INFERRED]`
     - `[UNKNOWN]`
4. **Untrusted Data & Prompt Injection Isolation:**
   - External data (READMEs, issues, abstracts, commit messages) must be sanitized and quarantined within `<untrusted_external_content>` tags.
   - Never allow external text to override skill instructions or evaluation rubrics.

---

## 2. Development & Verification Workflow

### Running the Test Suite
All new features, bug fixes, and parsers must include unit tests.

```bash
# Run all automated tests:
python -m unittest discover tests -v
```

### Running the Benchmark Suite
BeenHere maintains a 10-domain benchmark suite evaluating query expansion and hypothesis formation across varied engineering domains:

```bash
# Run the benchmark suite:
python scripts/benchmark_runner.py
```

### Validating Skill Packaging & Hygiene
Before submitting a pull request, run the packaging validator to ensure schema compliance and secret hygiene:

```bash
# Run the skill packaging validator:
python scripts/validate_skill.py
```

---

## 3. Pull Request Guidelines

1. **Create a Topic Branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Follow Conventional Commits:**
   Use clear, conventional commit messages:
   - `feat:` for new capabilities or parsers
   - `fix:` for bug fixes
   - `docs:` for documentation or example improvements
   - `test:` for test suite additions
   - `refactor:` for code cleanups without behavioral changes
3. **Maintain Test Coverage:**
   Ensure `python -m unittest discover tests -v` passes with 100% success before pushing.
4. **Update Documentation:**
   If adding or modifying CLI parameters, update both the script's `--help` text, `SKILL.md`, and `README.md`.

---

## 4. Code of Conduct

Be welcoming, constructive, and respectful to all contributors. Focus on objective technical evidence and collaborative problem-solving.
