#!/usr/bin/env python3
"""
tests/test_cross_industry_analyzer.py - Comprehensive Unit & Regression Test Suite
for BeenHere v1.1 Cross-Industry Research Intelligence Engine.

Covers all 12 evaluation criteria:
1. Problem mechanism extraction (directly stated vs inferred vs hypotheses).
2. Buzzword/metaphor rejection (beehive, courtroom trial, symbiosis, quantum thinking).
3. Negative control detection (simple CRUD blog / static site -> NO_TRANSFER_NEEDED).
4. 8-dimension transferability evaluation.
5. 6 classification outcomes.
6. Technical counter-example handling (Raft consensus marked NOT_TRANSFERABLE for offline editing).
7. Gale-Shapley adaptation for partial/incomplete preference lists.
8. Anti-percentage rule compliance (zero fabricated numerical percentages).
9. Markdown section generation (format_cross_industry_section).
10. CLI execution via subprocess (--concept, --plan, --json, --output, --negative-control).
11. Deterministic output repeatability across multiple invocations.
12. Integration with concept_expander.py query plan fixture.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.cross_industry_analyzer import (
    EVALUATION_DIMENSIONS,
    MECHANISM_CATALOG,
    NEGATIVE_CONTROL_TRIGGERS,
    SUPERFICIAL_METAPHORS,
    TRANSFER_OUTCOMES,
    analyze_cross_industry_opportunities,
    evaluate_transferability,
    extract_problem_mechanisms,
    filter_analogies_and_queries,
    format_cross_industry_section,
)


class TestMechanismExtraction(unittest.TestCase):
    """Criterion 1: Extract problem mechanisms distinguishing stated vs inferred vs hypotheses."""

    def test_extract_problem_mechanisms_structure(self):
        concept = "AI recruitment platform matching candidate resumes to job requirements"
        result = extract_problem_mechanisms(concept)

        self.assertIn("original_concept", result)
        self.assertEqual(result["original_concept"], concept)
        self.assertFalse(result["is_negative_control"])
        self.assertIn("directly_stated_requirements", result)
        self.assertIn("inferred_requirements", result)
        self.assertIn("established_technical_concepts", result)
        self.assertIn("candidate_analogies", result)
        self.assertIn("provenance_disclosure", result)

        # Directly stated requirements should contain keywords from prompt
        stated = [s.lower() for s in result["directly_stated_requirements"]]
        self.assertTrue(any("candidate" in s or "matching" in s or "recruitment" in s for s in stated))

        # Inferred requirements must carry explicit tag
        for inf in result["inferred_requirements"]:
            self.assertTrue(inf.startswith("[INFERRED-REQUIREMENT]"))

        # Candidate analogies must carry hypothesis disclosure tag
        for cand in result["candidate_analogies"]:
            self.assertIn("[RESEARCH-HYPOTHESIS]", cand["hypothesis"])

    def test_provenance_disclosure_content(self):
        result = extract_problem_mechanisms("Collaborative notes app")
        disclosure = result.get("provenance_disclosure", "")
        self.assertIn("research hypotheses", disclosure.lower())
        self.assertIn("not verified facts", disclosure.lower())


class TestRelevanceFilteringAndAntiBuzzwords(unittest.TestCase):
    """Criterion 2: Buzzword/metaphor rejection."""

    def test_filter_superficial_metaphors(self):
        analogies = [
            {
                "approach_name": "Beehive Swarm Intelligence",
                "source_domain": "Biological Entomology",
                "shared_problem": "Organizing worker tasks like a beehive colony",
                "raw_data": {"name": "Beehive Swarm Intelligence"},
            },
            {
                "approach_name": "Courtroom Trial Arbitration",
                "source_domain": "Judicial Law",
                "shared_problem": "Resolving data conflicts via a courtroom trial judge",
                "raw_data": {"name": "Courtroom Trial Arbitration"},
            },
            {
                "approach_name": "State-based & Operation-based CRDTs",
                "source_domain": "Distributed Database Systems",
                "shared_problem": "Merging concurrent offline mutations without lock arbitration",
                "raw_data": {
                    "name": "State-based & Operation-based CRDTs",
                    "solution_technique": "Semilattice state joins",
                    "target_use_case": "Offline-first collaborative editing",
                },
            },
        ]

        admissible, rejected = filter_analogies_and_queries(analogies)
        admissible_names = [a.get("approach_name") for a in admissible]
        rejected_names = [r.get("approach_name") for r in rejected]

        self.assertIn("State-based & Operation-based CRDTs", admissible_names)
        self.assertIn("Beehive Swarm Intelligence", rejected_names)
        self.assertIn("Courtroom Trial Arbitration", rejected_names)

        for rej in rejected:
            self.assertIn("SUPERFICIAL_METAPHOR", rej.get("rejection_reason", ""))

    def test_known_metaphors_list_completeness(self):
        self.assertIn("beehive", SUPERFICIAL_METAPHORS)
        self.assertIn("courtroom trial", SUPERFICIAL_METAPHORS)
        self.assertIn("symbiosis", SUPERFICIAL_METAPHORS)
        self.assertIn("quantum thinking", SUPERFICIAL_METAPHORS)


class TestNegativeControl(unittest.TestCase):
    """Criterion 3: Negative control detection."""

    def test_negative_control_triggers(self):
        triggers = [
            "Simple CRUD blog with static HTML pages",
            "Personal static portfolio site",
            "Basic landing page for marketing",
            "A simple todo list app using SQLite",
            "Basic contact form for website",
        ]
        for trigger in triggers:
            res = analyze_cross_industry_opportunities(trigger)
            self.assertEqual(res["status"], "NEGATIVE_CONTROL_TRIGGERED", f"Failed for {trigger}")
            self.assertFalse(res["transfer_needed"])
            self.assertEqual(len(res["evaluated_discoveries"]), 0)
            self.assertIn("Direct category-specific solutions", res["rationale"])

    def test_negative_control_cli_flag(self):
        cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "cross_industry_analyzer.py"), "--negative-control", "--json"]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(proc.stdout)
        self.assertEqual(data["status"], "NEGATIVE_CONTROL_TRIGGERED")
        self.assertFalse(data["transfer_needed"])


class TestEightDimensionTransferabilityAudit(unittest.TestCase):
    """Criterion 4: 8-dimension transferability evaluation."""

    def test_all_eight_dimensions_present(self):
        candidate = {
            "approach_name": "Hungarian Algorithm / Linear Sum Assignment (Kuhn-Munkres)",
            "source_domain": "Operations Research & Logistics Fleet Scheduling",
            "raw_data": {
                "name": "Hungarian Algorithm / Linear Sum Assignment (Kuhn-Munkres)",
                "source_domain": "Operations Research & Logistics Fleet Scheduling",
                "shared_problem": "Minimizing total cost in weighted bipartite matching",
                "solution_technique": "Primal-dual combinatorial optimization",
                "target_use_case": "Candidate-job matching",
                "inputs_required": ["Bipartite cost matrix"],
                "target_inputs_available": ["Resume-job embedding distance"],
                "operational_constraints": "O(n^3) complexity",
                "key_assumptions": "One-to-one matching",
                "integration_practicality": "TRANSFERABLE_IMPLEMENTATION: In scipy.optimize",
                "risks": "Global utility optimization can allocate individuals suboptimally",
                "suggested_experiment": "Benchmark on 500x50 cohort",
                "suggested_outcome": "TRANSFERABLE_IMPLEMENTATION",
            },
        }

        res = evaluate_transferability(candidate)
        dims = res.get("dimensions", {})

        for dim_name in EVALUATION_DIMENSIONS:
            self.assertIn(dim_name, dims, f"Dimension '{dim_name}' missing from evaluation")
            self.assertIn("status", dims[dim_name])
            self.assertIn("rationale", dims[dim_name])
            self.assertTrue(len(dims[dim_name]["rationale"]) > 5)

        self.assertIn("why_it_transfers", res)
        self.assertIn("adaptation_needed", res)
        self.assertIn("what_remains_unverified", res)
        self.assertIn("suggested_next_experiment", res)


class TestSixClassificationOutcomes(unittest.TestCase):
    """Criterion 5: 6 classification outcomes."""

    def test_all_six_outcomes_defined(self):
        expected = [
            "TRANSFERABLE_IMPLEMENTATION",
            "TRANSFERABLE_ALGORITHM",
            "TRANSFERABLE_ARCHITECTURAL_PATTERN",
            "CONCEPTUAL_INSPIRATION",
            "REQUIRES_VALIDATION",
            "NOT_TRANSFERABLE",
        ]
        self.assertEqual(TRANSFER_OUTCOMES, expected)

    def test_catalog_outcomes_validity(self):
        for cat_key, cat_data in MECHANISM_CATALOG.items():
            for app in cat_data["candidate_approaches"]:
                outcome = app["suggested_outcome"]
                self.assertIn(
                    outcome,
                    TRANSFER_OUTCOMES,
                    f"Catalog entry '{app['name']}' has invalid outcome '{outcome}'",
                )


class TestTechnicalCounterExamples(unittest.TestCase):
    """Criterion 6 & 7: Raft offline disqualification and Gale-Shapley adaptation."""

    def test_raft_offline_disqualified_as_not_transferable(self):
        """Raft consensus requires active quorum connectivity; it must be NOT_TRANSFERABLE for offline editing."""
        concept = "Collaborative offline note editor with real-time sync"
        res = analyze_cross_industry_opportunities(concept, {"required_capability": "offline note synchronization"})

        discoveries = res["evaluated_discoveries"]
        raft_eval = [d for d in discoveries if "raft" in d["approach_name"].lower()]

        self.assertTrue(len(raft_eval) > 0, "Raft consensus should be evaluated in distributed collaborative editing")
        raft = raft_eval[0]
        self.assertEqual(raft["classification"], "NOT_TRANSFERABLE")
        self.assertEqual(raft["dimensions"]["assumptions"]["status"], "INVALID_BREAKDOWN")
        self.assertIn("quorum", raft["dimensions"]["assumptions"]["rationale"].lower())

    def test_gale_shapley_partial_preference_adaptation(self):
        """Gale-Shapley assumes complete preference lists; recruitment only has partial rankings."""
        candidate = {
            "approach_name": "Gale-Shapley Stable Matching (Deferred Acceptance)",
            "source_domain": "Economics & Higher Education Admissions",
            "raw_data": {
                "name": "Gale-Shapley Stable Matching (Deferred Acceptance)",
                "source_domain": "Economics & Higher Education Admissions",
                "shared_problem": "Pairing two disjoint sets of entities under mutual preference",
                "solution_technique": "Iterative proposal and tentative deferred acceptance",
                "target_use_case": "Candidate-job matching",
                "inputs_required": ["Complete or strict transitive preference lists from both candidates and employers"],
                "target_inputs_available": ["Partial candidate preferences (location, salary)", "Sparse application history"],
                "operational_constraints": "Offline batch execution",
                "key_assumptions": "Assumes both parties can rank all counterparties transitively",
                "integration_practicality": "TRANSFERABLE_ALGORITHM",
                "risks": "Proposer-optimal bias",
                "suggested_experiment": "Run on synthetic dataset with missing ranks",
                "suggested_outcome": "TRANSFERABLE_ALGORITHM",
            },
        }

        res = evaluate_transferability(candidate)
        self.assertEqual(res["dimensions"]["input_compatibility"]["status"], "PARTIAL_MISMATCH")
        self.assertIn("partial", res["dimensions"]["input_compatibility"]["rationale"].lower())
        self.assertEqual(res["classification"], "TRANSFERABLE_ALGORITHM")


class TestAntiPercentageRule(unittest.TestCase):
    """Criterion 8: Anti-percentage rule compliance across all analysis and report text."""

    def test_no_arbitrary_percentage_metrics_in_evaluations(self):
        test_concepts = [
            "AI recruitment platform matching candidate resumes to job requirements",
            "Multiplayer matchmaking system balancing player skill ratings and ping",
            "Collaborative notes and document editor with offline-first synchronization",
        ]

        for concept in test_concepts:
            res = analyze_cross_industry_opportunities(concept)
            md = format_cross_industry_section(res)

            # Check that there are no "XX% code reuse" or "XX% transferability" claims
            self.assertNotRegex(md, r"\b\d+%\s*(?:code\s*reuse|reusability|transferable|match\s*score)\b")
            self.assertNotRegex(md, r"transferability:\s*\d+%", re.IGNORECASE)

            # In the raw JSON structure, verify no score field holds a percentage
            for disc in res.get("evaluated_discoveries", []):
                for dim_name, dim_val in disc.get("dimensions", {}).items():
                    status_str = str(dim_val.get("status", ""))
                    self.assertNotIn("%", status_str, f"Percentage found in dimension status: {status_str}")


class TestMarkdownSectionFormatting(unittest.TestCase):
    """Criterion 9: format_cross_industry_section output format."""

    def test_markdown_formatting_success(self):
        concept = "Multiplayer matchmaking system balancing player skill ratings and latency"
        res = analyze_cross_industry_opportunities(concept)
        md = format_cross_industry_section(res)

        self.assertIn("### Solutions from Other Industries", md)
        self.assertIn("#### 1.", md)
        self.assertIn("- **Original Industry:**", md)
        self.assertIn("- **Shared Technical Problem:**", md)
        self.assertIn("- **Existing Solution or Technique:**", md)
        self.assertIn("- **Why It May Transfer:**", md)
        self.assertIn("- **What Would Need Adaptation:**", md)
        self.assertIn("- **Evidence & Provenance:**", md)
        self.assertIn("- **Suggested Next Experiment:**", md)

    def test_markdown_formatting_negative_control(self):
        res = analyze_cross_industry_opportunities("Simple CRUD blog with static HTML pages")
        md = format_cross_industry_section(res)

        self.assertIn("### Solutions from Other Industries", md)
        self.assertIn("Direct Category Solutions Sufficient", md)
        self.assertIn("No cross-industry transfer required", md)


class TestScenarioFixturesIntegrity(unittest.TestCase):
    """Criterion 10 & Scenario Verification: Validate the 3 evaluation scenarios and negative control."""

    def test_scenario_files_exist_and_validate(self):
        scenarios_dir = PROJECT_ROOT / "evaluations" / "cross_industry"
        expected_files = [
            "scenario_a_recruitment_matching.json",
            "scenario_b_multiplayer_matchmaking.json",
            "scenario_c_collaborative_knowledge.json",
            "negative_control_crud_blog.json",
        ]

        for fname in expected_files:
            fpath = scenarios_dir / fname
            self.assertTrue(fpath.is_file(), f"Scenario file not found: {fpath}")

            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertIn("scenario_id", data)
            self.assertIn("original_concept", data)
            self.assertIn("provenance", data)
            self.assertTrue(data["provenance"].get("verified"))

            # Execute analyzer on each scenario
            res = analyze_cross_industry_opportunities(data["original_concept"], data.get("context"))

            if data.get("expected_status") == "NEGATIVE_CONTROL_TRIGGERED":
                self.assertEqual(res["status"], "NEGATIVE_CONTROL_TRIGGERED")
                self.assertFalse(res["transfer_needed"])
            else:
                self.assertEqual(res["status"], "SUCCESS")
                self.assertTrue(res["transfer_needed"])
                self.assertTrue(len(res["evaluated_discoveries"]) >= 2)


class TestCLIExecution(unittest.TestCase):
    """Criterion 11: CLI execution via subprocess."""

    def test_cli_concept_json(self):
        script = str(PROJECT_ROOT / "scripts" / "cross_industry_analyzer.py")
        cmd = [sys.executable, script, "--concept", "Collaborative offline document editor", "--json"]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(proc.stdout)
        self.assertEqual(data["status"], "SUCCESS")
        self.assertTrue(len(data["evaluated_discoveries"]) > 0)

    def test_cli_output_file_markdown(self):
        script = str(PROJECT_ROOT / "scripts" / "cross_industry_analyzer.py")
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".md") as tmp:
            tmp_path = tmp.name

        try:
            cmd = [sys.executable, script, "--concept", "Multiplayer matchmaking", "--output", tmp_path]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.assertEqual(proc.returncode, 0)
            with open(tmp_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("### Solutions from Other Industries", content)
            self.assertIn("Bayesian Skill Volatility Updates", content)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_cli_plan_flag_integration(self):
        """Criterion 12: Integration with concept_expander research plan."""
        # Create a mock research plan JSON
        mock_plan = {
            "original_concept": "AI recruitment candidate ranking",
            "expansion_metadata": {"provenance": "TEST_MOCK"},
            "decomposition": {
                "mechanisms": ["Two-Sided Matching"],
                "technical_primitives": ["Bipartite Graph Matching"],
            },
        }

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
            tmp.write(json.dumps(mock_plan))
            tmp_path = tmp.name

        try:
            script = str(PROJECT_ROOT / "scripts" / "cross_industry_analyzer.py")
            cmd = [sys.executable, script, "--plan", tmp_path, "--json"]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            data = json.loads(proc.stdout)
            self.assertEqual(data["status"], "SUCCESS")
            self.assertEqual(data["concept"], "AI recruitment candidate ranking")
            self.assertTrue(len(data["evaluated_discoveries"]) > 0)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestDeterministicRepeatability(unittest.TestCase):
    """Test deterministic output repeatability across multiple invocations."""

    def test_deterministic_runs(self):
        concept = "Multiplayer matchmaking system balancing player skill ratings, latency, and queue times"
        ctx = {"target_language": "go"}

        run1 = json.dumps(analyze_cross_industry_opportunities(concept, ctx), sort_keys=True)
        run2 = json.dumps(analyze_cross_industry_opportunities(concept, ctx), sort_keys=True)
        run3 = json.dumps(analyze_cross_industry_opportunities(concept, ctx), sort_keys=True)

        self.assertEqual(run1, run2)
        self.assertEqual(run2, run3)


if __name__ == "__main__":
    unittest.main()
