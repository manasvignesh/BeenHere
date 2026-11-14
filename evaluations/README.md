# BeenHere Research Quality Benchmarking Framework (v1.1)

This directory contains the standardized evaluation framework, benchmark scenarios, rubric definitions, and evaluation harness for measuring BeenHere's research quality against baseline AI coding agents.

---

## 1. Directory Structure

```text
evaluations/
├── README.md                           # Framework overview, instructions, and reproduction guide
├── rubric.md                           # 6-dimension evaluation rubric with explicit 0–5 anchors
├── run_manifest.schema.json            # JSON schema for recording and validating run manifests
├── evaluate.py                         # Evaluation CLI: scoring, validation, and comparative reporting
├── scenarios/                          # Standardized, identical research prompts across scenarios
│   ├── offline_notes.md                # Scenario A: Offline-first collaborative notes (CRDTs, SQLite)
│   ├── ai_recruitment.md               # Scenario B: AI recruitment platform (ATS, Docling, Fairlearn)
│   └── accessibility_testing.md        # Scenario C: Automated accessibility platform (Axe-core, WCAG)
├── results/                            # JSON run manifests for baseline and BeenHere runs
│   ├── offline_notes_baseline.json
│   ├── offline_notes_beenhere.json
│   ├── ai_recruitment_baseline.json
│   ├── ai_recruitment_beenhere.json
│   ├── accessibility_testing_baseline.json
│   └── accessibility_testing_beenhere.json
└── reports/                            # Generated evaluation reports and improvement backlogs
    ├── BENCHMARK_AUDIT.md              # In-depth audit of existing benchmarks vs research quality
    ├── COMPARATIVE_EVALUATION_REPORT.md# Side-by-side reference performance report
    ├── IMPROVEMENT_BACKLOG.md          # Prioritized v1.1 engineering backlog
    └── PROVENANCE_AUDIT.md             # Formal provenance audit of evaluation manifests
```

---

## 2. The 6-Dimension Research Quality Rubric

Each research investigation is evaluated on a **0 to 5** scale across six weighted dimensions:

| Dimension | Weight | Focus | Key Observable Criteria |
| :--- | :---: | :--- | :--- |
| **D1: Relevant Solutions Discovered** | 20% | Prior art breadth & specificity | Uncovers specialized technical primitives (e.g. CR-SQLite) in addition to high-level canonical names. |
| **D2: Reusable Code & Integration** | 20% | Source-level inspection | Directly inspects source files (`.py`, `.ts`, `.rs`), extracts exported APIs, and identifies missing features. |
| **D3: Accuracy & Traceability** | 20% | Factual correctness & links | Strict evidence hierarchy (`[VERIFIED-SOURCE]`, `[VERIFIED-METADATA]`); zero broken links; zero fake stats. |
| **D4: Licensing & Dependency Risks** | 15% | Legal clearance & supply chain | Detects non-OSI licenses (BSL-1.1), copyleft obligations (AGPL/GPL), and transitive dependency hazards. |
| **D5: Cross-Industry Insight Quality** | 15% | Computational primitives | Translates universal mechanisms from adjacent fields; strictly rejects superficial analogies. |
| **D6: Actionability of Recommendation** | 10% | Strategic decision roadmap | Delivers a decisive posture (*Adopt, Fork, Integrate, Build*) with concrete architectural trade-offs. |

Composite score is normalized to a **0 to 100 Quality Index**:
- **90.0 – 100.0:** Grade A+ (Exemplary)
- **80.0 – 89.9:** Grade A (Strong)
- **70.0 – 79.9:** Grade B (Acceptable)
- **50.0 – 69.9:** Grade C (Marginal)
- **< 50.0:** Grade F (Unacceptable)

---

## 3. How to Run the Evaluation Harness

The harness is written in standard library Python (Python 3.8+ compatible) with zero external dependencies:

```bash
# 1. Print summary comparison table of all recorded runs:
python evaluations/evaluate.py --summary

# 2. Validate all JSON manifests in evaluations/results/:
python evaluations/evaluate.py --validate evaluations/results

# 3. Calculate scores and breakdown for a single run manifest:
python evaluations/evaluate.py --score evaluations/results/offline_notes_beenhere.json

# 4. Generate the complete Markdown comparative report:
python evaluations/evaluate.py --report --output evaluations/reports/COMPARATIVE_EVALUATION_REPORT.md
```

---

## 4. Methodology: Establishing a Fair Baseline

To evaluate whether BeenHere produces genuinely superior engineering intelligence compared to a standard coding agent:

1. **Identical Task Prompts:** Both conditions receive the exact verbatim research brief defined in `evaluations/scenarios/<scenario>.md`.
2. **Fixed Model & Environment:** The same underlying language model (e.g., GPT-4o, Claude 3.7 Sonnet) is used with identical tool capabilities (WebSearch, Bash, Read, Grep).
3. **Controlled Difference:**
   - **Baseline:** The agent is prompted with the raw research brief without the BeenHere skill loaded.
   - **BeenHere:** The agent activates BeenHere (`SKILL.md`), executing concept expansion, multi-query discovery, source manifest inspection, license risk analysis, and structured reporting.
4. **Transparent Disclosures:**
   - Evaluator identity and date are recorded in every manifest.
   - If an agent self-evaluates, a self-audit disclosure is mandatory.
   - Real empirical evidence from Phase 2.5 and Phase 5 real-world runs is preserved and cited.

---

## 5. Provenance Notice: Synthetic Fixtures vs Verified Experimental Results

As documented in [`evaluations/reports/PROVENANCE_AUDIT.md`](reports/PROVENANCE_AUDIT.md):

- **Baseline Manifests (`*_baseline.json`):** Designated as `provenance_type: "synthetic_baseline_fixture"`. They represent archetypal models of how typical conversational LLMs answer broad engineering questions without tools. They are **not** transcripts from third-party benchmark labs.
- **BeenHere Manifests (`*_beenhere.json`):** Designated as `provenance_type: "retrospective_reference_fixture"` (or `"empirical_unblinded_trial"` for the real Codex run in `BeenHere-Test`). All rubric scores were assigned unblinded by the tool author.
- **Intended Use:** These manifests serve as **calibrated reference fixtures** to validate harness calculations, schema compliance, and rubric sensitivity. They do not constitute peer-reviewed double-blind competitive proof. True empirical superiority claims require future independent double-blind evaluation with external human evaluators.

