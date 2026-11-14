"""
tests/test_concept_expander_robustness.py - Regression & Robustness Tests for BeenHere Concept Expansion

Part of BeenHere v1.1.
Verifies that the concept expander reliably decomposes software ideas across multiple domains
without requiring manual primitive inputs, generates non-empty multi-tier queries, enforces deduplication,
maintains deterministic outputs, and gracefully handles unfamiliar and vague concepts.

Does NOT hardcode expected string outputs per scenario. Tests structural and semantic invariants.
"""

import json
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

import concept_expander


class TestConceptExpanderRobustness(unittest.TestCase):
    """Test suite verifying heuristic concept expansion robustness across diverse domains."""

    # Explicitly required domains by specification
    REQUIRED_DOMAINS = [
        "AI recruitment platform",
        "Automated accessibility auditing",
        "Offline-first collaborative notes",
        "Autonomous mobile robotics control",
        "Supply-chain inventory and demand forecasting",
        "Developer security and vulnerability tooling",
        "Quantum-resistant olfactory telemetry pipeline",  # Deliberately unfamiliar concept
    ]

    def test_unassisted_expansion_across_required_domains(self):
        """
        Verify that unfamiliar and diverse concepts produce useful, populated research plans
        WITHOUT manually supplied technical primitives or mechanisms.
        """
        for concept in self.REQUIRED_DOMAINS:
            with self.subTest(concept=concept):
                plan = concept_expander.build_research_plan(concept)

                self.assertEqual(plan["status"], "success")
                self.assertEqual(plan["original_concept"], concept)

                # Decomposition must contain meaningful problems and mechanisms
                decomp = plan["decomposition"]
                self.assertGreaterEqual(
                    len(decomp["core_problems"]), 1,
                    f"Core problems empty for concept: '{concept}'"
                )
                self.assertGreaterEqual(
                    len(decomp["mechanisms"]), 1,
                    f"Mechanisms empty for concept: '{concept}'"
                )
                self.assertGreaterEqual(
                    len(decomp["technical_primitives"]), 1,
                    f"Technical primitives empty for concept: '{concept}'"
                )
                self.assertGreaterEqual(
                    len(decomp["adjacent_industries"]), 1,
                    f"Adjacent industries empty for concept: '{concept}'"
                )

                # Multi-tier query matrix must be fully populated
                qm = plan["query_matrix"]
                self.assertGreaterEqual(
                    len(qm["direct_queries"]), 1,
                    f"Direct queries empty for concept: '{concept}'"
                )
                self.assertGreaterEqual(
                    len(qm["technical_primitive_queries"]), 1,
                    f"Primitive queries empty for concept: '{concept}'"
                )
                self.assertGreaterEqual(
                    len(qm["cross_vertical_queries"]), 1,
                    f"Cross-vertical queries empty for concept: '{concept}'"
                )
                self.assertGreaterEqual(
                    len(qm["academic_queries"]), 1,
                    f"Academic queries empty for concept: '{concept}'"
                )

                # Hypotheses must be generated and properly marked
                hypotheses = plan["hypotheses_to_verify"]
                self.assertGreaterEqual(len(hypotheses), 1)
                for h in hypotheses:
                    self.assertEqual(h["verification_status"], "UNVERIFIED_HYPOTHESIS")
                    self.assertIn("evidence_required", h)

    def test_cross_matrix_deduplication_invariant(self):
        """
        Queries must never be duplicated across any tier in the query matrix.
        Case-insensitive uniqueness is strictly enforced.
        """
        for concept in self.REQUIRED_DOMAINS:
            with self.subTest(concept=concept):
                plan = concept_expander.build_research_plan(concept)
                qm = plan["query_matrix"]
                all_queries = (
                    qm["direct_queries"]
                    + qm["technical_primitive_queries"]
                    + qm["cross_vertical_queries"]
                    + qm["academic_queries"]
                )
                lowered = [q.strip().lower() for q in all_queries if q.strip()]
                self.assertEqual(
                    len(lowered),
                    len(set(lowered)),
                    f"Found duplicate queries in concept '{concept}': {all_queries}",
                )

    def test_deterministic_repeatability(self):
        """
        The expansion engine must be 100% deterministic.
        Repeated calls with identical inputs must produce byte-identical outputs.
        """
        concept = "Decentralized mycorrhizal network simulator"
        plan_1 = concept_expander.build_research_plan(concept)
        plan_2 = concept_expander.build_research_plan(concept)

        json_1 = json.dumps(plan_1, sort_keys=True)
        json_2 = json.dumps(plan_2, sort_keys=True)
        self.assertEqual(json_1, json_2, "Concept expansion must be strictly deterministic")

    def test_provenance_metadata_and_disclosures(self):
        """
        Expansion metadata must declare heuristic provenance and disclosures.
        """
        for concept in self.REQUIRED_DOMAINS:
            plan = concept_expander.build_research_plan(concept)
            meta = plan.get("expansion_metadata", {})
            self.assertIn("provenance", meta)
            self.assertEqual(meta["provenance"], "[INFERRED-HEURISTIC]")
            self.assertIn("heuristic_expansion_disclosure", meta)
            self.assertIn("extracted_tokens", meta)
            self.assertGreater(len(meta["extracted_tokens"]), 0)

    def test_graceful_handling_of_vague_and_single_word_inputs(self):
        """
        Minimal or single-word inputs should still yield valid, non-empty plans without crashing.
        """
        vague_inputs = [
            "Robotics",
            "Monitoring",
            "Security",
            "Telemetry",
            "Auditing",
            "Optimization",
        ]
        for term in vague_inputs:
            with self.subTest(term=term):
                plan = concept_expander.build_research_plan(term)
                self.assertEqual(plan["status"], "success")
                qm = plan["query_matrix"]
                self.assertGreater(len(qm["direct_queries"]), 0)
                self.assertGreater(len(qm["technical_primitive_queries"]), 0)
                self.assertGreater(len(qm["academic_queries"]), 0)

    def test_empty_or_whitespace_raises_value_error(self):
        """Purely blank or whitespace strings must raise clean ValueError."""
        blank_inputs = ["", "   ", "\t\n  \r\n", "   \t   "]
        for b in blank_inputs:
            with self.subTest(blank=b):
                with self.assertRaises(ValueError):
                    concept_expander.build_research_plan(b)

    def test_text_formatter_output_integrity(self):
        """Verify format_text_plan renders all mandatory markdown sections."""
        plan = concept_expander.build_research_plan("Automated accessibility auditing")
        formatted = concept_expander.format_text_plan(plan)
        self.assertIn("# BeenHere Concept Expansion & Deterministic Research Plan", formatted)
        self.assertIn("## 1. Problem & Mechanism Decomposition", formatted)
        self.assertIn("## 2. Multi-Tier Query Matrix", formatted)
        self.assertIn("### A. Direct & Component Queries", formatted)
        self.assertIn("### B. Technical Primitive Queries", formatted)
        self.assertIn("### C. Cross-Vertical Queries", formatted)
        self.assertIn("### D. Academic Research Queries", formatted)
        self.assertIn("## 3. Research Priorities", formatted)
        self.assertIn("## 4. Hypotheses to Verify", formatted)


if __name__ == "__main__":
    unittest.main()
