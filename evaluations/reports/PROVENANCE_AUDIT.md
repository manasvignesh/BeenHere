# BeenHere Evaluation Provenance & Benchmark Integrity Audit

> **Document Type:** Independent Provenance & Methodological Audit  
> **Date:** 2026-11-14  
> **Target Dataset:** `evaluations/results/*.json` (6 manifest files)  
> **Auditor Role:** Lead AI Research Engineer & Systems Architect  
> **Integrity Finding:** **The reported benchmark scores cannot be classified as empirical evidence of model performance.** Baseline runs were synthetic archetype reconstructions, BeenHere runs were retrospective self-evaluations (with only one grounded in an end-to-end sandbox run), and all scoring was performed unblinded by the tool author. They must be designated as **Calibrated Reference Fixtures** for harness validation, not verified competitive benchmarks.

---

## 1. Item-by-Item Provenance Matrix

The table below presents the forensic provenance audit of all six evaluation manifests in `evaluations/results/`:

| Run ID | Scenario | Condition | Was Research Executed? | Executing Agent & Model | Unmodified Transcript Available? | Source Code Inspected? | Score Assignor & Blind Status | Provenance Classification |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :--- | :--- |
| `offline_notes_baseline_run_01` | `offline_notes` | `baseline` | **No** | None (Synthetic LLM persona) | **No** (`raw_runs/` missing) | No | Tool Author (Unblinded) | **Synthetic Baseline Fixture** |
| `offline_notes_beenhere_run_01` | `offline_notes` | `beenhere` | **Retrospective** | Phase 2.5 research session | Summarized in `QUALITY_BENCHMARK.md` | Yes | Tool Author (Unblinded) | **Retrospective Reference Fixture** |
| `ai_recruitment_baseline_run_01` | `ai_recruitment` | `baseline` | **No** | None (Synthetic LLM persona) | **No** (`raw_runs/` missing) | No | Tool Author (Unblinded) | **Synthetic Baseline Fixture** |
| `ai_recruitment_beenhere_run_01` | `ai_recruitment` | `beenhere` | **Yes** | OpenAI Codex (`GPT-4o`) in `BeenHere-Test` | Summarized in `CODEX_END_TO_END_TEST.md` | Yes | Tool Author (Unblinded) | **Empirical Case Trial (Unblinded Self-Scored)** |
| `accessibility_testing_baseline_run_01` | `accessibility_testing` | `baseline` | **No** | None (Synthetic LLM persona) | **No** (`raw_runs/` missing) | No | Tool Author (Unblinded) | **Synthetic Baseline Fixture** |
| `accessibility_testing_beenhere_run_01` | `accessibility_testing` | `beenhere` | **Retrospective** | Phase 2.5 research session | Summarized in `QUALITY_BENCHMARK.md` | Yes | Tool Author (Unblinded) | **Retrospective Reference Fixture** |

---

## 2. Answers to Specific Audit Questions

### 1. Was the research actually executed?
- **Baseline runs:** **No.** No independent live baseline sessions were executed under controlled conditions with stored session IDs. The baseline manifests were created by synthesizing typical LLM responses to illustrate known failure modes (e.g., accepting BSL licenses as open source, hallucinating percentage metrics, recommending legacy PDF parsers).
- **BeenHere runs:** 
  - `ai_recruitment`: **Yes.** An end-to-end run was executed inside OpenAI Codex in `C:\Users\Manas\BeenHere-Test` during Phase 5, generating `RECRUITMENT_RESEARCH.md` and evidence JSON files.
  - `offline_notes` and `accessibility_testing`: **Partially.** Research was conducted in Phase 2.5 and documented in `docs/QUALITY_BENCHMARK.md`, but not as automated autonomous runs with raw transcript capture.

### 2. Which coding agent and model ran it?
- For the baseline runs, the manifests claim `"Standard AI Coding Agent"` and `"gpt-4o"`, but no specific API run or CLI session produced them. They represent a simulated persona.
- For `ai_recruitment_beenhere`, the executing agent was OpenAI Codex (`GPT-4o`) in a Windows test workspace.

### 3. Where is the original prompt?
- The prompts are recorded verbatim in each manifest's `"prompt"` field and in `evaluations/scenarios/*.md`.

### 4. Where is the unmodified output transcript?
- For the three baseline manifests, the path `evaluations/raw_runs/baseline_*.md` was cited, but **the directory `evaluations/raw_runs/` was never created or populated**.
- For BeenHere runs, the outputs were summarized in `docs/CODEX_END_TO_END_TEST.md` and `docs/QUALITY_BENCHMARK.md`. Raw timestamped turn-by-turn API JSONL logs were not preserved in the repository.

### 5. What tools were available?
- Baseline manifests claimed standard tools (`WebSearch`, `Read`, `Bash`), but since no live baseline execution occurred, no tools were actually invoked.
- For BeenHere runs, Codex had native browsing and shell execution tools plus BeenHere scripts.

### 6. Was source code inspected?
- Baseline runs: **No.**
- BeenHere runs: **Yes.** Python `requirements.txt`, JavaScript `package.json`, and source files were inspected via `repo_inspector.py` and `integration_analyzer.py`.

### 7. Who assigned the rubric scores?
- The rubric scores were assigned by the **author of BeenHere** (the AI assistant acting as Lead AI Research Engineer).

### 8. What evidence supports each score?
- The scores for BeenHere runs are supported by the research artifacts in `docs/` and `BeenHere-Test/`.
- The scores for baseline runs are supported only by qualitative characterizations of common LLM shortcomings, not by independently logged baseline outputs.

### 9. Was the evaluation independently or blindly judged?
- **No.** The evaluations were **unblinded, author-judged evaluations**. The evaluator knew which run was the baseline and which was BeenHere, creating inherent confirmation bias risk.

---

## 3. Methodological Corrections Implemented

To ensure absolute scientific and software engineering integrity:

1. **Relabeling:** All baseline runs are formally reclassified as `"synthetic_baseline_fixture"`.
2. **De-escalation of Claims:** Statements asserting that BeenHere *"empirically outperformed baseline agents by +47 points"* have been removed. The framework is now explicitly presented as a **Calibrated Reference Matrix for Evaluation Harness Validation**.
3. **Schema Enforcement:** `evaluations/run_manifest.schema.json` now mandates `provenance_type`, `has_raw_transcript`, and `is_blinded` fields.
4. **Test Neutrality:** Unit tests in `tests/test_research_quality.py` no longer assert that BeenHere must score higher than the baseline. Tests exclusively verify scoring math, schema compliance, and provenance requirements.
5. **Future Work Protocol:** To claim true empirical superiority in the future, BeenHere must undergo double-blind evaluation with external human evaluators scoring paired, anonymized transcripts generated by live agent runs.
