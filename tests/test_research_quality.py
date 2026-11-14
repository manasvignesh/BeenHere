"""
tests/test_research_quality.py - Regression and Verification Tests for BeenHere Research Quality & Evaluation Harness

Part of BeenHere v1.1.
Verifies evaluation harness functions, scenario ground-truth integrity, run manifests validity,
and research report quality linters (Anti-Percentage Rule, licensing traps, and evidence tagging).
"""

import json
import os
import sys
import unittest

# Add project root and evaluations directory to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL_DIR = os.path.join(PROJECT_ROOT, "evaluations")
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, EVAL_DIR)

import evaluate


class TestEvaluationHarnessUnit(unittest.TestCase):
    """Unit tests for the evaluation harness calculation and validation engine."""

    def setUp(self):
        self.sample_valid_manifest = {
            "manifest_version": "1.0",
            "run_id": "test_run_01",
            "scenario_id": "offline_notes",
            "condition": "beenhere",
            "timestamp": "2026-11-14T12:00:00Z",
            "environment": {
                "agent_type": "unit-test-agent",
                "model": "test-model-1",
                "tool_access": ["github_search", "web_search"],
                "network_enabled": True,
            },
            "prompt": "Build an offline note app",
            "evaluation": {
                "evaluator": "automated-suite",
                "evaluation_date": "2026-11-14",
                "scores": {
                    "d1_solutions_discovered": 4.5,
                    "d2_reusable_code": 4.0,
                    "d3_accuracy_evidence": 5.0,
                    "d4_licensing_risk": 5.0,
                    "d5_cross_industry": 4.5,
                    "d6_actionable_recommendation": 4.5,
                },
                "dimension_justifications": {
                    "d1_solutions_discovered": "Found Yjs and CR-SQLite",
                    "d2_reusable_code": "Exported symbol analysis included",
                    "d3_accuracy_evidence": "Every link verified",
                    "d4_licensing_risk": "Discovered BSL-1.1 license trap",
                    "d5_cross_industry": "Evaluated operational transformation vs CRDT",
                    "d6_actionable_recommendation": "Gave actionable trade-off analysis",
                },
            },
        }

    def test_calculate_grade(self):
        """Verify letter grade classification boundaries."""
        self.assertEqual(evaluate.calculate_grade(95.0), "A+ (Exemplary)")
        self.assertEqual(evaluate.calculate_grade(90.0), "A+ (Exemplary)")
        self.assertEqual(evaluate.calculate_grade(85.0), "A (Strong)")
        self.assertEqual(evaluate.calculate_grade(80.0), "A (Strong)")
        self.assertEqual(evaluate.calculate_grade(75.0), "B (Acceptable)")
        self.assertEqual(evaluate.calculate_grade(70.0), "B (Acceptable)")
        self.assertEqual(evaluate.calculate_grade(60.0), "C (Marginal)")
        self.assertEqual(evaluate.calculate_grade(50.0), "C (Marginal)")
        self.assertEqual(evaluate.calculate_grade(49.9), "F (Unacceptable)")
        self.assertEqual(evaluate.calculate_grade(20.0), "F (Unacceptable)")

    def test_validate_manifest_valid(self):
        """A properly structured manifest must yield zero validation errors."""
        errs = evaluate.validate_manifest(self.sample_valid_manifest)
        self.assertEqual(errs, [])

    def test_validate_manifest_missing_required_fields(self):
        """Missing top-level or nested fields must be reported."""
        incomplete = dict(self.sample_valid_manifest)
        del incomplete["manifest_version"]
        del incomplete["scenario_id"]
        errs = evaluate.validate_manifest(incomplete)
        self.assertTrue(any("manifest_version" in e for e in errs))
        self.assertTrue(any("scenario_id" in e for e in errs))

    def test_validate_manifest_invalid_scenario_and_condition(self):
        """Unrecognized scenario_id or condition must trigger validation errors."""
        bad_manifest = dict(self.sample_valid_manifest)
        bad_manifest["scenario_id"] = "nonexistent_space_exploration"
        bad_manifest["condition"] = "experimental_unsupported"
        errs = evaluate.validate_manifest(bad_manifest)
        self.assertTrue(any("nonexistent_space_exploration" in e for e in errs))
        self.assertTrue(any("experimental_unsupported" in e for e in errs))

    def test_validate_manifest_score_out_of_bounds(self):
        """Scores outside [0.0, 5.0] or non-numeric values must be rejected."""
        bad_scores_manifest = json.loads(json.dumps(self.sample_valid_manifest))
        bad_scores_manifest["evaluation"]["scores"]["d1_solutions_discovered"] = 5.5
        bad_scores_manifest["evaluation"]["scores"]["d2_reusable_code"] = -0.5
        bad_scores_manifest["evaluation"]["scores"]["d3_accuracy_evidence"] = "not-a-number"
        errs = evaluate.validate_manifest(bad_scores_manifest)
        self.assertTrue(any("5.5" in e for e in errs))
        self.assertTrue(any("-0.5" in e for e in errs))
        self.assertTrue(any("not-a-number" in e for e in errs))

    def test_validate_manifest_missing_justification(self):
        """Empty or missing justification text for any dimension must fail validation."""
        bad_just_manifest = json.loads(json.dumps(self.sample_valid_manifest))
        bad_just_manifest["evaluation"]["dimension_justifications"]["d4_licensing_risk"] = "   "
        errs = evaluate.validate_manifest(bad_just_manifest)
        self.assertTrue(any("d4_licensing_risk" in e for e in errs))

    def test_compute_manifest_scores(self):
        """Composite score must adhere to official weighted formula."""
        # 4.5*0.2 + 4.0*0.2 + 5.0*0.2 + 5.0*0.15 + 4.5*0.15 + 4.5*0.10
        # = 0.90 + 0.80 + 1.00 + 0.75 + 0.675 + 0.45 = 4.575
        # Quality index = (4.575 / 5.0) * 100 = 91.5
        computed = evaluate.compute_manifest_scores(self.sample_valid_manifest)
        self.assertEqual(computed["composite_score"], 4.575)
        self.assertEqual(computed["quality_index"], 91.5)
        self.assertEqual(computed["grade"], "A+ (Exemplary)")
        self.assertIn("breakdown", computed)
        self.assertEqual(len(computed["breakdown"]), 6)

    def test_compare_runs(self):
        """Test comparing paired baseline and beenhere runs across scenarios."""
        baseline_manifest = json.loads(json.dumps(self.sample_valid_manifest))
        baseline_manifest["condition"] = "baseline"
        baseline_manifest["run_id"] = "test_baseline_01"
        for dim in baseline_manifest["evaluation"]["scores"]:
            baseline_manifest["evaluation"]["scores"][dim] = 2.0

        manifests = [self.sample_valid_manifest, baseline_manifest]
        comparison = evaluate.compare_runs(manifests)
        self.assertEqual(len(comparison["scenarios"]), 1)
        scen = comparison["scenarios"][0]
        self.assertEqual(scen["scenario_id"], "offline_notes")
        self.assertEqual(scen["baseline"]["composite_score"], 2.0)
        self.assertEqual(scen["baseline"]["quality_index"], 40.0)
        self.assertEqual(scen["beenhere"]["composite_score"], 4.575)
        self.assertEqual(scen["beenhere"]["quality_index"], 91.5)
        self.assertEqual(scen["delta_index"], 51.5)

    def test_format_comparison_markdown(self):
        """Check Markdown report generation for required sections."""
        manifests = [self.sample_valid_manifest]
        comparison = evaluate.compare_runs(manifests)
        md = evaluate.format_comparison_markdown(comparison)
        self.assertIn("# BeenHere vs Baseline: Research Quality Comparative Evaluation", md)
        self.assertIn("## 1. Executive Summary Table", md)
        self.assertIn("## 2. Dimension Breakdown by Scenario", md)
        self.assertIn("## 3. Disclosures, Missing Data & Empirical Uncertainties", md)


class TestScenariosIntegrity(unittest.TestCase):
    """Test suite ensuring benchmark scenarios meet rigorous ground-truth specifications."""

    SCENARIOS_DIR = os.path.join(EVAL_DIR, "scenarios")

    def test_required_scenario_files_exist(self):
        """Verify the 3 core evaluation scenario files exist."""
        expected_files = [
            "offline_notes.md",
            "ai_recruitment.md",
            "accessibility_testing.md",
        ]
        for fname in expected_files:
            fpath = os.path.join(self.SCENARIOS_DIR, fname)
            self.assertTrue(os.path.isfile(fpath), f"Scenario file missing: {fpath}")

    def test_scenario_markdown_has_required_sections(self):
        """Verify all scenario files contain standard sections and verification traps."""
        required_sections = [
            "## 1. Standardized Research Brief",
            "## 2. Target Concept & Architectural Primitives",
            "## 3. Known Failure Modes in Standard AI Research",
            "## 4. Ground-Truth Solution Space & Evidence Baseline",
            "## 5. Scoring Expectation & Rubric Anchors",
        ]
        for fname in os.listdir(self.SCENARIOS_DIR):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(self.SCENARIOS_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertTrue(content.startswith("# Benchmark Evaluation Scenario"), f"{fname} missing header")
            for sec in required_sections:
                self.assertIn(sec, content, f"{fname} missing section: {sec}")


class TestRunManifestsQualityAndValidity(unittest.TestCase):
    """Test suite validating all recorded run manifests in evaluations/results."""

    RESULTS_DIR = os.path.join(EVAL_DIR, "results")

    def test_all_manifests_are_valid(self):
        """All manifest files in evaluations/results must be strictly valid JSON and pass validation."""
        self.assertTrue(os.path.isdir(self.RESULTS_DIR), "Results directory must exist")
        manifest_files = [f for f in os.listdir(self.RESULTS_DIR) if f.endswith(".json")]
        self.assertGreaterEqual(len(manifest_files), 6, "Expected at least 6 benchmark manifest files")

        for fname in manifest_files:
            fpath = os.path.join(self.RESULTS_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            errs = evaluate.validate_manifest(data)
            self.assertEqual(errs, [], f"Manifest {fname} failed validation: {errs}")

    def test_pairwise_conditions_and_beenhere_superiority(self):
        """Ensure each scenario has paired baseline and beenhere runs where BeenHere outperforms."""
        manifests = evaluate.load_all_manifests(self.RESULTS_DIR)
        self.assertEqual(len(manifests), 6)

        comparison = evaluate.compare_runs(manifests)
        self.assertEqual(len(comparison["scenarios"]), 3)

        for scen in comparison["scenarios"]:
            self.assertIsNotNone(scen["baseline"], f"Missing baseline for {scen['scenario_id']}")
            self.assertIsNotNone(scen["beenhere"], f"Missing beenhere for {scen['scenario_id']}")
            # Quality delta must be strongly positive (at least +40 points improvement)
            self.assertGreater(scen["delta_index"], 40.0)
            self.assertGreaterEqual(scen["beenhere"]["quality_index"], 90.0)
            self.assertLessEqual(scen["baseline"]["quality_index"], 50.0)


class TestResearchReportLinters(unittest.TestCase):
    """Test suite verifying research report anti-pattern linters."""

    def test_lint_detects_anti_percentage_rule(self):
        """Detect and reject ungrounded percentage estimates for code reuse."""
        bad_texts = [
            "We estimate that 75% code reuse can be achieved by integrating this library.",
            "There is an estimated 80% reusable component in this repository.",
            "The architecture yields 60% code reuse for the frontend.",
            "The reuse rate is approximately 85%.",
        ]
        for txt in bad_texts:
            issues = evaluate.lint_research_report(txt)
            self.assertTrue(
                any(i["rule"] == "anti_percentage_rule" for i in issues),
                f"Failed to catch anti-percentage rule in: {txt}",
            )

    def test_lint_detects_bsl_misconception(self):
        """Detect claims stating BSL-1.1 is OSI-approved open source."""
        txt = "Outline is licensed under BSL-1.1 which is open-source and freely usable."
        issues = evaluate.lint_research_report(txt)
        self.assertTrue(any(i["rule"] == "licensing_misconception" for i in issues))
        self.assertTrue(any("BSL" in i["message"] for i in issues))

    def test_lint_detects_copyleft_commercial_fallacy(self):
        """Detect claims stating copyleft unconditionally prohibits commercial use."""
        txt = "Because Horilla is AGPL-3.0, it prohibits commercial use."
        issues = evaluate.lint_research_report(txt)
        self.assertTrue(any(i["rule"] == "licensing_misconception" for i in issues))
        self.assertTrue(any("commercial" in i["message"] for i in issues))

    def test_lint_detects_missing_evidence_tags_in_long_text(self):
        """Substantive reports without any BeenHere evidence tags must be flagged."""
        long_untagged_text = (
            "This report analyzes five different open source repositories for our note application. "
            "We found that Automerge provides excellent conflict resolution and SQLite handles local "
            "persistence effectively. The team can proceed with implementation immediately. "
            "Integration complexity is low and all modules can be imported directly without issues. "
            "Furthermore, network sync protocols are well documented across all upstream repositories. "
            "This concludes our comprehensive architectural evaluation and preliminary recommendations."
        )
        self.assertGreater(len(long_untagged_text), 500)
        issues = evaluate.lint_research_report(long_untagged_text)
        self.assertTrue(any(i["rule"] == "missing_evidence_tags" for i in issues))

    def test_lint_clean_report_passes(self):
        """Compliant reports with evidence tags and without anti-patterns must pass cleanly."""
        clean_text = (
            "# Research Evaluation\n"
            "We inspected [Yjs](https://github.com/yjs/yjs) [VERIFIED-SOURCE].\n"
            "The repository is licensed under MIT [VERIFIED-METADATA].\n"
            "The core modules can be integrated via npm [VERIFIED-SOURCE].\n"
        )
        issues = evaluate.lint_research_report(clean_text)
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
