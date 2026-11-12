#!/usr/bin/env python3
"""
tests/test_phase2.py - Comprehensive offline automated tests for BeenHere Phase 2.

Covers:
- Concept expander input validation, query generation, deduplication, and hypotheses
- Academic paper search normalization (DOIs, titles, abstracts), deduplication, retraction detection
- Academic rate limits (HTTP 429), network failures, missing metadata handling
- Benchmark suite validation and runner execution
- Reference manuals and enhanced 15-section template integrity
"""

import json
import os
import sys
import unittest
from unittest.mock import patch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import benchmark_runner
import concept_expander
import paper_search


class TestConceptExpander(unittest.TestCase):
    """Tests for scripts/concept_expander.py."""

    def test_valid_expansion(self):
        plan = concept_expander.build_research_plan(
            concept="Decentralized peer-to-peer data syncing with CRDTs",
            problems=["Network partition conflicts", "Bandwidth consumption on mobile"],
            mechanisms=["crdt", "gossip", "turn_taking"],
            technical_primitives=["WebRTC DataChannels", "SQLite"],
            adjacent_verticals=["Distributed Systems", "Avionics"],
        )

        self.assertEqual(plan["status"], "success")
        self.assertEqual(plan["original_concept"], "Decentralized peer-to-peer data syncing with CRDTs")

        qm = plan["query_matrix"]
        self.assertTrue(len(qm["direct_queries"]) > 0)
        self.assertTrue(len(qm["technical_primitive_queries"]) > 0)
        self.assertTrue(len(qm["cross_vertical_queries"]) > 0)
        self.assertTrue(len(qm["academic_queries"]) > 0)

        # Ensure hypotheses are marked UNVERIFIED
        hypotheses = plan["hypotheses_to_verify"]
        self.assertTrue(len(hypotheses) > 0)
        for h in hypotheses:
            self.assertEqual(h["verification_status"], "UNVERIFIED_HYPOTHESIS")

    def test_empty_concept_error(self):
        with self.assertRaises(ValueError):
            concept_expander.build_research_plan(concept="")

        with self.assertRaises(ValueError):
            concept_expander.build_research_plan(concept="   \n\t  ")

    def test_cross_matrix_deduplication(self):
        # A keyword appearing in direct must not duplicate in primitive or academic queries
        plan = concept_expander.build_research_plan(
            concept="Multi-agent debate arbitration platform",
            mechanisms=["debate", "arbitration"],
            technical_primitives=["debate"],
        )
        qm = plan["query_matrix"]
        all_queries = (
            qm["direct_queries"]
            + qm["technical_primitive_queries"]
            + qm["cross_vertical_queries"]
            + qm["academic_queries"]
        )
        self.assertEqual(len(all_queries), len(set(all_queries)), "Cross-matrix duplicates must be eliminated.")

    def test_catalog_heuristic_matching(self):
        # Concept containing "consensus" should trigger Sociology and Distributed Systems
        plan = concept_expander.build_research_plan(
            concept="A tool for group consensus building among distributed teams",
        )
        decomp = plan["decomposition"]
        verticals = decomp["adjacent_industries"]
        self.assertTrue(any("Distributed Systems" in v for v in verticals))
        self.assertTrue(any("Sociology" in v for v in verticals))

    def test_format_text_plan(self):
        plan = concept_expander.build_research_plan(
            concept="Autonomous code review agent",
            problems=["False positive linter warnings"],
            mechanisms=["ast diffing"],
        )
        formatted = concept_expander.format_text_plan(plan)
        self.assertIn("Problem & Mechanism Decomposition", formatted)
        self.assertIn("Multi-Tier Query Matrix", formatted)
        self.assertIn("Hypotheses to Verify", formatted)


class TestPaperSearch(unittest.TestCase):
    """Tests for scripts/paper_search.py."""

    def test_normalize_doi(self):
        self.assertEqual(paper_search.normalize_doi("10.1145/3586183.3606763"), "10.1145/3586183.3606763")
        self.assertEqual(
            paper_search.normalize_doi("https://doi.org/10.1145/3586183.3606763"),
            "10.1145/3586183.3606763",
        )
        self.assertEqual(
            paper_search.normalize_doi("http://dx.doi.org/10.1016/j.artint.2023.01"),
            "10.1016/j.artint.2023.01",
        )
        self.assertIsNone(paper_search.normalize_doi(None))
        self.assertIsNone(paper_search.normalize_doi(""))

    def test_reconstruct_openalex_abstract(self):
        inverted = {
            "Generative": [0],
            "agents": [1],
            "simulate": [2],
            "believable": [3],
            "behavior": [4],
        }
        res = paper_search.reconstruct_openalex_abstract(inverted)
        self.assertEqual(res, "Generative agents simulate believable behavior")
        self.assertEqual(paper_search.reconstruct_openalex_abstract(None), "")
        self.assertEqual(paper_search.reconstruct_openalex_abstract({}), "")

    def test_academic_deduplication_by_doi(self):
        mock_data = {
            "openalex": {
                "status": "success",
                "items": [
                    {
                        "title": "Generative Agents",
                        "doi": "10.48550/arxiv.2304.03442",
                        "authors": ["Park et al."],
                        "year": 2023,
                        "venue": "UIST",
                        "url": "https://doi.org/10.48550/arxiv.2304.03442",
                        "abstract": "Abstract A",
                        "provider": "openalex",
                    }
                ],
            },
            "semanticscholar": {
                "status": "success",
                "items": [
                    {
                        "title": "Generative Agents: Interactive Simulacra",  # Duplicate DOI
                        "doi": "10.48550/arxiv.2304.03442",
                        "authors": ["Joon Sung Park"],
                        "year": 2023,
                        "venue": "arXiv",
                        "url": "https://arxiv.org/abs/2304.03442",
                        "abstract": "Abstract B",
                        "provider": "semanticscholar",
                    }
                ],
            },
        }

        res = paper_search.search_academic_papers(
            queries=["generative agents"],
            limit=5,
            mock_data_map=mock_data,
        )
        self.assertEqual(res["total_unique_discovered"], 1)
        self.assertEqual(len(res["items"]), 1)
        self.assertEqual(res["items"][0]["doi"], "10.48550/arxiv.2304.03442")

    def test_academic_deduplication_by_title(self):
        mock_data = {
            "openalex": {
                "status": "success",
                "items": [
                    {
                        "title": "Multi-Agent Debate Framework",
                        "doi": None,
                        "authors": ["Alice"],
                        "year": 2024,
                        "venue": "ICLR",
                        "url": "https://example.com/1",
                        "provider": "openalex",
                    }
                ],
            },
            "arxiv": {
                "status": "success",
                "items": [
                    {
                        "title": "Multi Agent Debate Framework!!",  # Identical normalized title
                        "doi": None,
                        "authors": ["Alice"],
                        "year": 2024,
                        "venue": "arXiv",
                        "url": "https://example.com/2",
                        "provider": "arxiv",
                    }
                ],
            },
        }

        res = paper_search.search_academic_papers(
            queries=["multi agent debate"],
            limit=5,
            mock_data_map=mock_data,
        )
        self.assertEqual(res["total_unique_discovered"], 1)

    def test_academic_retraction_flag(self):
        mock_data = {
            "openalex": {
                "status": "success",
                "items": [
                    {
                        "title": "Flawed Research Paper",
                        "doi": "10.1000/retracted.01",
                        "authors": ["Dr. Fraud"],
                        "year": 2022,
                        "venue": "Dubious Journal",
                        "is_retracted": True,
                        "provider": "openalex",
                    }
                ],
            }
        }
        res = paper_search.search_academic_papers(
            queries=["flawed research"],
            limit=1,
            mock_data_map=mock_data,
        )
        paper = res["items"][0]
        self.assertTrue(paper["is_retracted"])
        table = paper_search.format_academic_table(res)
        self.assertIn("RETRACTED", table)

    def test_academic_rate_limit_handling(self):
        mock_data = {
            "semanticscholar": {
                "status": "rate_limited",
                "message": "Semantic Scholar public rate limit reached (HTTP 429).",
                "items": [],
            }
        }
        res = paper_search.search_academic_papers(
            queries=["test query"],
            providers=["semanticscholar"],
            mock_data_map=mock_data,
        )
        self.assertEqual(res["provider_statuses"]["semanticscholar"], "rate_limited")
        self.assertTrue(len(res["errors"]) > 0)
        self.assertIn("rate limit reached", res["errors"][0])

    def test_academic_missing_metadata(self):
        mock_data = {
            "openalex": {
                "status": "success",
                "items": [
                    {
                        "title": "Sparse Paper",
                        "doi": None,
                        "authors": [],
                        "year": None,
                        "venue": "Unknown",
                        "abstract": None,
                        "provider": "openalex",
                    }
                ],
            }
        }
        res = paper_search.search_academic_papers(
            queries=["sparse"],
            limit=1,
            mock_data_map=mock_data,
        )
        paper = res["items"][0]
        self.assertEqual(paper["authors"], [])
        self.assertIsNone(paper["abstract"])
        table = paper_search.format_academic_table(res)
        self.assertIn("Sparse Paper", table)
        self.assertIn("N/A", table)


class TestBenchmarkSuite(unittest.TestCase):
    """Tests for benchmark cases and benchmark runner."""

    def test_benchmark_cases_fixture_integrity(self):
        fixture_path = os.path.join(BASE_DIR, "tests", "benchmark_cases.json")
        self.assertTrue(os.path.isfile(fixture_path), "benchmark_cases.json must exist")

        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cases = data.get("cases", [])
        self.assertGreaterEqual(len(cases), 10, "Must contain at least 10 benchmark cases")

        for c in cases:
            errs = benchmark_runner.validate_benchmark_case_schema(c)
            self.assertEqual(len(errs), 0, f"Case '{c.get('id')}' has schema errors: {errs}")

    def test_benchmark_runner_full_suite(self):
        fixture_path = os.path.join(BASE_DIR, "tests", "benchmark_cases.json")
        results = benchmark_runner.run_benchmark_suite(fixture_path)
        self.assertEqual(results["status"], "PASS")
        self.assertEqual(results["passed_cases"], 10)
        self.assertEqual(results["failed_cases"], 0)


class TestPhase2ReferencesAndTemplates(unittest.TestCase):
    """Verifies Phase 2 reference documents and enhanced reporting template."""

    def test_required_phase2_files_exist(self):
        phase2_paths = [
            "scripts/concept_expander.py",
            "scripts/paper_search.py",
            "scripts/benchmark_runner.py",
            "references/product_discovery.md",
            "references/transferability_rubric.md",
            "references/feature_gap_analysis.md",
            "tests/benchmark_cases.json",
        ]
        for p in phase2_paths:
            full = os.path.join(BASE_DIR, p)
            self.assertTrue(os.path.isfile(full), f"Required Phase 2 file must exist: {p}")
            self.assertGreater(os.path.getsize(full), 100, f"File must not be empty: {p}")

    def test_idea_landscape_template_has_15_sections(self):
        template_path = os.path.join(BASE_DIR, "templates", "IDEA_LANDSCAPE.md")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_section_headers = [
            "## 1. Executive Findings",
            "## 2. Original Idea and Intended Users",
            "## 3. Problem and Mechanism Decomposition",
            "## 4. Direct Competitors and Implementations",
            "## 5. Relevant GitHub Repositories",
            "## 6. Academic Research and Experimental Systems",
            "## 7. Cross-Vertical Discoveries",
            "## 8. Transferability Assessments",
            "## 9. Code-Reusability Recommendations",
            "## 10. Feature Coverage Matrix",
            "## 11. Missing Functionality",
            "## 12. Potential Enhancements",
            "## 13. Implementation Alternatives",
            "## 14. Recommended Development Strategy",
            "## 15. Sources, Uncertainties, and Coverage Limitations",
        ]
        for header in required_section_headers:
            self.assertIn(header, content, f"Template must contain section '{header}'")


if __name__ == "__main__":
    unittest.main()
