"""
tests/test_repo_comparator.py - Unit and Regression Tests for Multi-Repository Comparison Engine

Part of BeenHere v1.1.
Tests the multi-repository comparison engine, decision logic, legal gating, maintenance analysis,
language compatibility, star-bias resistance, integration blueprints, and concept relevance.
"""

import json
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

import concept_expander
import repo_comparator


class TestRepoComparatorDecisionLogic(unittest.TestCase):
    """Test suite verifying multi-repository decision logic and evidence gating."""

    def setUp(self):
        self.default_context = {
            "target_language": "Python",
            "deployment_model": "Proprietary SaaS",
            "required_capability": "Document text extraction",
        }

    def test_conflicting_license_evidence_triggers_investigate_further(self):
        """Discrepancy between declared SPDX and actual license text must trigger INVESTIGATE_FURTHER."""
        candidate = {
            "slug": "sample/conflicted-repo",
            "language": "Python",
            "stars": 12000,
            "license_info": {
                "declared_spdx": "MIT",
                "category": "PERMISSIVE",
                "discrepancy": "Declared MIT in manifest, but LICENSE header specifies BSL-1.1 commercial restrictions.",
            },
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 5},
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        res = repo_comparator.evaluate_candidate_posture(candidate, self.default_context)
        self.assertEqual(res["posture"], "INVESTIGATE_FURTHER")
        self.assertEqual(res["uncertainty_rating"], "HIGH")
        self.assertTrue(any("conflicting" in r.lower() for r in [res["fit_rationale"]]))

    def test_missing_unlicensed_rejected(self):
        """Unlicensed repositories or NOASSERTION without text must be rejected under copyright law."""
        candidate = {
            "slug": "sample/unlicensed-repo",
            "language": "Python",
            "stars": 5000,
            "license_info": {
                "declared_spdx": "NOASSERTION",
                "category": "MISSING_UNLICENSED",
            },
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 2},
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        res = repo_comparator.evaluate_candidate_posture(candidate, self.default_context)
        self.assertEqual(res["posture"], "REJECT_FOR_USE_CASE")
        self.assertEqual(res["complexity_rating"], "PROHIBITIVE")
        self.assertIn("lacks a clear", res["fit_rationale"])

    def test_source_available_bsl_rejected_for_commercial_saas(self):
        """BSL-1.1 candidate evaluated for a proprietary SaaS must be rejected."""
        candidate = {
            "slug": "sample/bsl-app",
            "language": "Python",
            "stars": 25000,
            "license_info": {
                "declared_spdx": "BSL-1.1",
                "category": "SOURCE_AVAILABLE",
            },
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 3},
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        res = repo_comparator.evaluate_candidate_posture(candidate, self.default_context)
        self.assertEqual(res["posture"], "REJECT_FOR_USE_CASE")
        self.assertEqual(res["complexity_rating"], "PROHIBITIVE")
        self.assertIn("source-available", res["fit_rationale"].lower())

    def test_source_available_bsl_allowed_for_architectural_reference(self):
        """BSL-1.1 candidate evaluated for non-commercial research may be used as architectural reference."""
        research_context = {
            "target_language": "Python",
            "deployment_model": "Internal Research / Non-commercial",
            "required_capability": "Architecture study",
        }
        candidate = {
            "slug": "sample/bsl-app",
            "language": "Python",
            "stars": 25000,
            "license_info": {
                "declared_spdx": "BSL-1.1",
                "category": "SOURCE_AVAILABLE",
            },
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 3},
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        res = repo_comparator.evaluate_candidate_posture(candidate, research_context)
        self.assertEqual(res["posture"], "USE_AS_ARCHITECTURAL_REFERENCE")

    def test_transitive_copyleft_risk_triggers_rejection(self):
        """Transitive copyleft contamination (e.g. PyMuPDF in Horilla) must trigger rejection."""
        candidate = {
            "slug": "sample/contaminated-repo",
            "language": "Python",
            "stars": 4000,
            "license_info": {
                "declared_spdx": "LGPL-2.1",
                "category": "WEAK_COPYLEFT",
                "transitive_license_risks": ["PyMuPDF (AGPL-3.0 / Artifex)"],
            },
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 1},
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        res = repo_comparator.evaluate_candidate_posture(candidate, self.default_context)
        self.assertEqual(res["posture"], "REJECT_FOR_USE_CASE")
        self.assertIn("transitive", res["fit_rationale"].lower())

    def test_network_copyleft_agpl_in_proprietary_saas(self):
        """AGPL in proprietary SaaS: standalone service gets INTEGRATE_THROUGH_API; embedded library is rejected."""
        service_candidate = {
            "slug": "sample/agpl-service",
            "language": "Go",
            "stars": 8000,
            "architecture_type": "standalone_service",
            "license_info": {"declared_spdx": "AGPL-3.0", "category": "NETWORK_RECIPROCAL", "copyleft_tier": "STRONG_NETWORK"},
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 5},
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        res_svc = repo_comparator.evaluate_candidate_posture(service_candidate, self.default_context)
        self.assertEqual(res_svc["posture"], "INTEGRATE_THROUGH_API")
        self.assertIn("network", res_svc["fit_rationale"].lower())

        lib_candidate = {
            "slug": "sample/agpl-lib",
            "language": "Python",
            "stars": 8000,
            "architecture_type": "modular_library",
            "license_info": {"declared_spdx": "AGPL-3.0", "category": "NETWORK_RECIPROCAL", "copyleft_tier": "STRONG_NETWORK"},
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 5},
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        res_lib = repo_comparator.evaluate_candidate_posture(lib_candidate, self.default_context)
        self.assertEqual(res_lib["posture"], "REJECT_FOR_USE_CASE")

    def test_stale_maintenance_signals(self):
        """Stale or archived repositories must not receive direct ADOPT_AS_DEPENDENCY."""
        # 1. Permissive with small exported symbols -> EXTRACT_REUSABLE_COMPONENT
        stale_small = {
            "slug": "sample/stale-algo",
            "language": "Python",
            "stars": 1200,
            "license_info": {"declared_spdx": "MIT", "category": "PERMISSIVE"},
            "maintenance": {"status": "DORMANT", "last_pushed_days_ago": 450, "is_archived": False},
            "exported_symbols": [{"name": "compute_diff", "type": "function"}],
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        res_small = repo_comparator.evaluate_candidate_posture(stale_small, self.default_context)
        self.assertEqual(res_small["posture"], "EXTRACT_REUSABLE_COMPONENT")

        # 2. Permissive with complex/large codebase -> FORK_AND_ADAPT
        stale_large = {
            "slug": "sample/stale-framework",
            "language": "Python",
            "stars": 6000,
            "license_info": {"declared_spdx": "Apache-2.0", "category": "PERMISSIVE"},
            "maintenance": {"status": "ARCHIVED", "last_pushed_days_ago": 800, "is_archived": True},
            "exported_symbols": [{"name": f"class_{i}", "type": "class"} for i in range(10)],
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        res_large = repo_comparator.evaluate_candidate_posture(stale_large, self.default_context)
        self.assertEqual(res_large["posture"], "FORK_AND_ADAPT")

    def test_incompatible_language_runtime(self):
        """Language mismatch without bindings -> architectural reference; with bindings -> adopt with caution."""
        # No bindings: Rust candidate for Python target
        rust_cand_no_bindings = {
            "slug": "sample/rust-core",
            "language": "Rust",
            "ecosystem": "cargo",
            "stars": 3000,
            "license_info": {"declared_spdx": "MIT", "category": "PERMISSIVE"},
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 5},
            "available_bindings": [],
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        res_no = repo_comparator.evaluate_candidate_posture(rust_cand_no_bindings, self.default_context)
        self.assertEqual(res_no["posture"], "USE_AS_ARCHITECTURAL_REFERENCE")

        # With official Python bindings:
        rust_cand_with_bindings = {
            "slug": "sample/rust-with-py",
            "language": "Rust",
            "ecosystem": "cargo",
            "stars": 5000,
            "license_info": {"declared_spdx": "MIT", "category": "PERMISSIVE"},
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 5},
            "available_bindings": ["Python", "Node.js"],
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        res_with = repo_comparator.evaluate_candidate_posture(rust_cand_with_bindings, self.default_context)
        self.assertEqual(res_with["posture"], "ADOPT_AS_DEPENDENCY")
        self.assertEqual(res_with["complexity_rating"], "MODERATE")

    def test_no_star_popularity_bias(self):
        """A 50k-star BSL monolith must not outrank a 1k-star active MIT modular library."""
        bsl_popular = {
            "slug": "famous/megastar-app",
            "name": "megastar",
            "language": "Python",
            "stars": 50000,
            "architecture_type": "monolithic_application",
            "license_info": {"declared_spdx": "BSL-1.1", "category": "SOURCE_AVAILABLE"},
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 1},
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }
        mit_modest = {
            "slug": "modest/clean-library",
            "name": "clean-lib",
            "language": "Python",
            "stars": 1200,
            "architecture_type": "modular_library",
            "license_info": {"declared_spdx": "MIT", "category": "PERMISSIVE"},
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 3},
            "exported_symbols": [{"name": "Parser", "type": "class"}],
            "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
        }

        comparison = repo_comparator.compare_repositories([bsl_popular, mit_modest], self.default_context)
        self.assertEqual(comparison["primary_recommendation"], "modest/clean-library")

    def test_incomplete_source_inspections(self):
        """Missing evidence must be flagged with elevated uncertainty."""
        uninspected_cand = {
            "slug": "sample/uninspected",
            "language": "Python",
            "stars": 2000,
            "license_info": {"declared_spdx": "MIT", "category": "PERMISSIVE"},
            "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 10},
            "evidence_completeness": {
                "license_inspected": False,
                "manifest_inspected": False,
                "source_inspected": False,
                "missing_evidence": [],
            },
        }
        res = repo_comparator.evaluate_candidate_posture(uninspected_cand, self.default_context)
        self.assertEqual(res["uncertainty_rating"], "HIGH")
        self.assertGreaterEqual(len(res["evidence_completeness"]["missing_evidence"]), 2)


class TestOutputFormattingAndBlueprints(unittest.TestCase):
    """Test suite verifying comparison reports and detailed integration blueprints."""

    def setUp(self):
        self.sample_candidates = [
            {
                "slug": "candidate/lib-a",
                "name": "lib-a",
                "purpose": "A modular document extractor",
                "target_capability": "PDF Parsing",
                "language": "Python",
                "ecosystem": "PyPI",
                "stars": 5000,
                "architecture_type": "modular_library",
                "license_info": {"declared_spdx": "MIT", "category": "PERMISSIVE"},
                "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 4},
                "exported_symbols": [{"name": "Extractor", "type": "class", "file": "src/extractor.py"}],
                "dependencies": [{"name": "pydantic", "version": "2.0"}],
                "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
            },
            {
                "slug": "candidate/app-b",
                "name": "app-b",
                "purpose": "A full-stack ATS application",
                "target_capability": "PDF Parsing",
                "language": "Python",
                "ecosystem": "standalone",
                "stars": 3000,
                "architecture_type": "monolithic_application",
                "license_info": {"declared_spdx": "AGPL-3.0", "category": "NETWORK_RECIPROCAL", "copyleft_tier": "STRONG_NETWORK"},
                "maintenance": {"status": "ACTIVE", "last_pushed_days_ago": 10},
                "evidence_completeness": {"license_inspected": True, "manifest_inspected": True, "source_inspected": True},
            },
        ]
        self.context = {"target_language": "Python", "deployment_model": "Proprietary SaaS", "required_capability": "PDF Parsing"}

    def test_format_comparison_table_structure(self):
        """Format comparison table must contain standard headers and posture explanations."""
        comp = repo_comparator.compare_repositories(self.sample_candidates, self.context)
        table_md = repo_comparator.format_comparison_table(comp)

        self.assertIn("# BeenHere Intelligent Repository Comparison", table_md)
        self.assertIn("## 1. Multi-Candidate Comparison Matrix", table_md)
        self.assertIn("## 2. Actionable Posture Explanations", table_md)
        self.assertIn("## 3. Disclaimers & Limitations", table_md)
        self.assertIn("`candidate/lib-a`", table_md)
        self.assertIn("`candidate/app-b`", table_md)

    def test_generate_integration_blueprint_structure(self):
        """Integration blueprint must contain architectural boundaries, entrypoints, sequence, and checklists."""
        comp = repo_comparator.compare_repositories(self.sample_candidates, self.context)
        blueprint_md = repo_comparator.generate_integration_blueprint(comp, "candidate/lib-a")

        self.assertIn("# BeenHere Integration Blueprint: `candidate/lib-a`", blueprint_md)
        self.assertIn("## 1. Recommended Components & Architecture Boundaries", blueprint_md)
        self.assertIn("## 2. Relevant APIs & Data Contracts", blueprint_md)
        self.assertIn("## 3. Step-by-Step Integration Sequence", blueprint_md)
        self.assertIn("## 4. Pre-Adoption License & Legal Checklist", blueprint_md)
        self.assertIn("## 5. Technical Uncertainties & Remaining Engineering Work", blueprint_md)
        self.assertIn("## 6. Suggested Validation Tests", blueprint_md)
        self.assertIn("Extractor", blueprint_md)
        self.assertIn("pydantic", blueprint_md)

    def test_empty_candidates_raises_value_error(self):
        """Empty candidate list must raise ValueError."""
        with self.assertRaises(ValueError):
            repo_comparator.compare_repositories([], self.context)


class TestConceptExpanderRelevance(unittest.TestCase):
    """Test suite verifying relevance and confidence scoring in concept expansion."""

    def test_unfamiliar_domain_relevance_and_low_confidence(self):
        """
        Unfamiliar concepts must declare low confidence, provide host-agent refinement guidance,
        preserve exact user keywords, and avoid mad-libs generic software buzzwords.
        """
        concept = "mycorrhizal hyphal spore transport"
        plan = concept_expander.build_research_plan(concept)

        meta = plan.get("expansion_metadata", {})
        self.assertEqual(meta.get("confidence"), "low")
        self.assertEqual(meta.get("mode"), "heuristic_morphological_fallback")
        self.assertIn("refinement_guidance", meta)
        self.assertIn("Host AI agent", meta["refinement_guidance"])

        # Check query relevance
        direct = plan["query_matrix"]["direct_queries"]
        # Must contain exact phrase and natural subphrases
        self.assertIn("mycorrhizal hyphal spore transport", direct)
        self.assertTrue(any("spore" in q.lower() for q in direct))
        self.assertTrue(any("hyphal" in q.lower() for q in direct))

        # Must NOT contain unnatural mad-libs concatenation like "mycorrhizal parser"
        all_queries = (
            plan["query_matrix"]["direct_queries"]
            + plan["query_matrix"]["technical_primitive_queries"]
            + plan["query_matrix"]["academic_queries"]
        )
        for q in all_queries:
            self.assertNotIn("mycorrhizal parser", q.lower())
            self.assertNotIn("mycorrhizal workflow runner", q.lower())

    def test_familiar_domain_high_confidence(self):
        """Concepts matching the domain taxonomy must declare high confidence."""
        concept = "AI recruitment platform"
        plan = concept_expander.build_research_plan(concept)
        meta = plan.get("expansion_metadata", {})
        self.assertEqual(meta.get("confidence"), "high")
        self.assertEqual(meta.get("mode"), "taxonomy_matched")


if __name__ == "__main__":
    unittest.main()
