#!/usr/bin/env python3
"""
tests/test_core.py - Comprehensive offline test suite for BeenHere deterministic utilities.

Tests all scripts using mocked HTTP responses and synthetic edge cases:
- Empty searches, duplicates, sorting, rate limits, API errors
- Repo slug parsing, license classification, missing license clearance, maintenance vitals
- Markdown link extraction, evidence tag auditing, reachability checks
- Skill file integrity and frontmatter validation
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure scripts directory is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import github_search
import repo_inspector
import verify_sources


class TestGithubSearch(unittest.TestCase):
    """Tests for scripts/github_search.py."""

    def test_parse_rate_limit(self):
        headers = {
            "x-ratelimit-remaining": "45",
            "x-ratelimit-limit": "60",
            "x-ratelimit-reset": "1893456000",  # future timestamp
        }
        res = github_search.parse_rate_limit(headers)
        self.assertEqual(res["remaining"], 45)
        self.assertEqual(res["limit"], 60)
        self.assertIsNotNone(res["reset_time"])
        self.assertGreater(res["seconds_until_reset"], 0)

    def test_parse_rate_limit_empty(self):
        res = github_search.parse_rate_limit({})
        self.assertIsNone(res["remaining"])
        self.assertIsNone(res["limit"])
        self.assertIsNone(res["reset_time"])

    def test_multi_query_deduplication_and_aggregation(self):
        mock_data_map = {
            "query one": {
                "status": "success",
                "total_count": 2,
                "items": [
                    {
                        "full_name": "org/alpha",
                        "html_url": "https://github.com/org/alpha",
                        "stargazers_count": 100,
                        "language": "Python",
                        "license": "MIT",
                        "pushed_at": "2026-03-01T00:00:00Z",
                    },
                    {
                        "full_name": "org/beta",
                        "html_url": "https://github.com/org/beta",
                        "stargazers_count": 50,
                        "language": "TypeScript",
                        "license": "Apache-2.0",
                        "pushed_at": "2026-03-02T00:00:00Z",
                    },
                ],
            },
            "query two": {
                "status": "success",
                "total_count": 2,
                "items": [
                    {
                        "full_name": "org/alpha",  # Duplicate repo across queries
                        "html_url": "https://github.com/org/alpha",
                        "stargazers_count": 100,
                        "language": "Python",
                        "license": "MIT",
                    },
                    {
                        "full_name": "org/gamma",
                        "html_url": "https://github.com/org/gamma",
                        "stargazers_count": 250,
                        "language": "Rust",
                        "license": "BSD-3-Clause",
                    },
                ],
            },
        }

        res = github_search.multi_query_search(
            queries=["query one", "query two"],
            limit=10,
            mock_data_map=mock_data_map,
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["total_unique_discovered"], 3)
        self.assertEqual(len(res["items"]), 3)

        # Ranked by stargazers count desc: gamma (250), alpha (100), beta (50)
        self.assertEqual(res["items"][0]["full_name"], "org/gamma")
        self.assertEqual(res["items"][1]["full_name"], "org/alpha")
        self.assertEqual(res["items"][2]["full_name"], "org/beta")

        # Alpha should have matched both queries
        alpha_item = res["items"][1]
        self.assertIn("query one", alpha_item["matched_queries"])
        self.assertIn("query two", alpha_item["matched_queries"])

    def test_empty_search_results(self):
        mock_data_map = {
            "empty query": {
                "status": "success",
                "total_count": 0,
                "items": [],
            }
        }
        res = github_search.multi_query_search(
            queries=["empty query"],
            mock_data_map=mock_data_map,
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["total_unique_discovered"], 0)
        self.assertEqual(len(res["items"]), 0)
        formatted = github_search.format_text_table(res)
        self.assertIn("No repositories found", formatted)

    def test_rate_limit_handling(self):
        mock_data_map = {
            "rate-limited query": {
                "error": "rate_limited",
                "message": "GitHub API rate limit exceeded. Resets in 120 seconds.",
                "status_code": 403,
                "rate_limit": {"remaining": 0, "limit": 60, "seconds_until_reset": 120},
                "items": [],
            }
        }
        res = github_search.multi_query_search(
            queries=["rate-limited query"],
            mock_data_map=mock_data_map,
        )
        self.assertEqual(res["status"], "error")
        self.assertTrue(len(res["errors"]) > 0)
        self.assertIn("rate limit exceeded", res["errors"][0])

    def test_format_text_table(self):
        sample_results = {
            "status": "success",
            "total_unique_discovered": 1,
            "queries_executed": ["test query"],
            "items": [
                {
                    "full_name": "example/project",
                    "html_url": "https://github.com/example/project",
                    "stargazers_count": 1500,
                    "language": "Python",
                    "license": "MIT",
                    "pushed_at": "2026-03-10T12:00:00Z",
                    "description": "An example repository description.",
                    "matched_queries": ["test query"],
                }
            ],
            "rate_limit": {"remaining": 55, "limit": 60},
        }
        output = github_search.format_text_table(sample_results)
        self.assertIn("[example/project](https://github.com/example/project)", output)
        self.assertIn("1,500", output)
        self.assertIn("MIT", output)
        self.assertIn("55/60", output)


class TestRepoInspector(unittest.TestCase):
    """Tests for scripts/repo_inspector.py."""

    def test_parse_repo_slug(self):
        # Valid variants
        self.assertEqual(repo_inspector.parse_repo_slug("owner/repo"), ("owner", "repo"))
        self.assertEqual(repo_inspector.parse_repo_slug("https://github.com/owner/repo"), ("owner", "repo"))
        self.assertEqual(repo_inspector.parse_repo_slug("https://github.com/owner/repo/"), ("owner", "repo"))
        self.assertEqual(repo_inspector.parse_repo_slug("https://github.com/owner/repo.git"), ("owner", "repo"))
        self.assertEqual(repo_inspector.parse_repo_slug("git@github.com:owner/repo.git"), ("owner", "repo"))

        # Invalid specifications
        with self.assertRaises(ValueError):
            repo_inspector.parse_repo_slug("justoneword")

    def test_categorize_license_permissive(self):
        cat, clearance, rat = repo_inspector.categorize_license("MIT")
        self.assertEqual(cat, "permissive")
        self.assertEqual(clearance, "CLEAR")

        cat, clearance, rat = repo_inspector.categorize_license("Apache-2.0")
        self.assertEqual(cat, "permissive")
        self.assertEqual(clearance, "CLEAR")

    def test_categorize_license_copyleft(self):
        cat, clearance, rat = repo_inspector.categorize_license("LGPL-3.0")
        self.assertEqual(cat, "weak_copyleft")
        self.assertEqual(clearance, "CONDITIONAL")

        cat, clearance, rat = repo_inspector.categorize_license("AGPL-3.0")
        self.assertEqual(cat, "strong_copyleft")
        self.assertEqual(clearance, "RESTRICTED")

    def test_categorize_license_missing(self):
        cat, clearance, rat = repo_inspector.categorize_license(None)
        self.assertEqual(cat, "unresolved")
        self.assertEqual(clearance, "CRITICAL_BLOCKER")
        self.assertIn("All Rights Reserved", rat)

        cat, clearance, rat = repo_inspector.categorize_license("NOASSERTION")
        self.assertEqual(cat, "unresolved")
        self.assertEqual(clearance, "CRITICAL_BLOCKER")

    def test_maintenance_signals(self):
        # Active repo pushed 10 days ago
        now = repo_inspector.datetime.datetime.now(repo_inspector.datetime.timezone.utc)
        recent_date = (now - repo_inspector.datetime.timedelta(days=10)).isoformat()
        res = repo_inspector.compute_maintenance_signals({
            "pushed_at": recent_date,
            "archived": False,
            "open_issues_count": 5,
        })
        self.assertEqual(res["status"], "ACTIVE")
        self.assertFalse(res["is_archived"])

        # Archived repo
        archived_res = repo_inspector.compute_maintenance_signals({
            "pushed_at": recent_date,
            "archived": True,
            "open_issues_count": 0,
        })
        self.assertEqual(archived_res["status"], "ARCHIVED")
        self.assertTrue(archived_res["is_archived"])

        # Dormant repo pushed 500 days ago
        dormant_date = (now - repo_inspector.datetime.timedelta(days=500)).isoformat()
        dormant_res = repo_inspector.compute_maintenance_signals({
            "pushed_at": dormant_date,
            "archived": False,
            "open_issues_count": 42,
        })
        self.assertEqual(dormant_res["status"], "DORMANT")

    def test_inspect_repository_mocked(self):
        mock_data = {
            "repo": {
                "full_name": "test-org/smart-lib",
                "html_url": "https://github.com/test-org/smart-lib",
                "description": "A smart library for agents",
                "language": "Python",
                "stargazers_count": 500,
                "forks_count": 40,
                "open_issues_count": 2,
                "pushed_at": "2026-03-01T12:00:00Z",
                "archived": False,
                "license": {"spdx_id": "MIT", "name": "MIT License"},
                "topics": ["library", "agents"],
            },
            "languages": {"Python": 90000, "Shell": 10000},
            "root_files": ["pyproject.toml", "README.md", "LICENSE"],
            "readme_snippet": "Smart lib provides agent capabilities.",
        }

        res = repo_inspector.inspect_repository(
            owner="test-org",
            repo="smart-lib",
            mock_data=mock_data,
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["primary_language"], "Python")
        self.assertEqual(res["license"]["clearance"], "CLEAR")
        self.assertIn("pyproject.toml", res["manifests_detected"])
        self.assertEqual(res["modularity_estimate"], "MODULAR_LIBRARY")
        self.assertEqual(len(res["reuse_blockers"]), 0)

        formatted = repo_inspector.format_inspection_report(res)
        self.assertIn("Legal & License Clearance", formatted)
        self.assertIn("MIT", formatted)


class TestVerifySources(unittest.TestCase):
    """Tests for scripts/verify_sources.py."""

    def test_extract_markdown_links(self):
        md = """
        Here is a link to [Pipecat](https://github.com/pipecat-ai/pipecat) and
        another link to [Stanford Agents](https://github.com/joonspk-research/generative_agents).
        Duplicate link to [Pipecat Again](https://github.com/pipecat-ai/pipecat).
        """
        links = verify_sources.extract_markdown_links(md)
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0]["url"], "https://github.com/pipecat-ai/pipecat")
        self.assertEqual(links[1]["url"], "https://github.com/joonspk-research/generative_agents")

    def test_audit_evidence_tags(self):
        md = """
        The pipeline latency is 150ms [VERIFIED-TEST].
        The license is MIT [VERIFIED-METADATA].
        The code imports numpy directly [VERIFIED-SOURCE].
        Therefore, it runs locally without cloud calls [INFERRED].
        The exact training dataset remains undisclosed [UNKNOWN].
        """
        res = verify_sources.audit_evidence_tags(md)
        self.assertTrue(res["has_evidence_tagging"])
        self.assertEqual(res["total_tags_found"], 5)
        self.assertEqual(res["tag_counts"]["[VERIFIED-TEST]"], 1)
        self.assertEqual(res["tag_counts"]["[VERIFIED-SOURCE]"], 1)
        self.assertEqual(res["tag_counts"]["[VERIFIED-METADATA]"], 1)
        self.assertEqual(res["tag_counts"]["[INFERRED]"], 1)
        self.assertEqual(res["tag_counts"]["[UNKNOWN]"], 1)

    def test_verify_file_or_urls_mocked(self):
        mock_map = {
            "https://example.com/ok": {"url": "https://example.com/ok", "reachable": True, "status_code": 200, "error": None},
            "https://example.com/missing": {"url": "https://example.com/missing", "reachable": False, "status_code": 404, "error": "HTTP 404"},
        }

        res = verify_sources.verify_file_or_urls(
            urls=["https://example.com/ok", "https://example.com/missing"],
            mock_reachability_map=mock_map,
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["reachability"]["total_tested"], 2)
        self.assertEqual(res["reachability"]["reachable"], 1)
        self.assertEqual(res["reachability"]["unreachable"], 1)

        formatted = verify_sources.format_verification_report(res)
        self.assertIn("Source Link Reachability", formatted)
        self.assertIn("https://example.com/ok", formatted)


class TestSkillStructure(unittest.TestCase):
    """Validates skill file structure, frontmatter compliance, and references."""

    def test_skill_md_frontmatter(self):
        skill_path = os.path.join(BASE_DIR, "SKILL.md")
        self.assertTrue(os.path.isfile(skill_path), "SKILL.md must exist in root")

        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertTrue(content.startswith("---"), "SKILL.md must begin with frontmatter delimiter '---'")
        frontmatter_end = content.find("---", 3)
        self.assertGreater(frontmatter_end, 3, "SKILL.md must contain closing frontmatter delimiter '---'")

        fm = content[3:frontmatter_end]
        self.assertIn("name: beenhere", fm)
        self.assertIn("description:", fm)
        self.assertIn("license: MIT", fm)
        self.assertIn("allowed-tools:", fm)

    def test_required_directories_and_files(self):
        required_paths = [
            "LICENSE",
            "README.md",
            ".gitignore",
            "SKILL.md",
            "scripts/github_search.py",
            "scripts/repo_inspector.py",
            "scripts/verify_sources.py",
            "references/discovery_methodology.md",
            "references/cross_vertical_research.md",
            "references/code_reusability.md",
            "references/evaluation_rubric.md",
            "templates/IDEA_LANDSCAPE.md",
            "templates/REUSE_REPORT.md",
            "docs/EXISTING_SOLUTIONS.md",
            "docs/ARCHITECTURE.md",
            "docs/INSTALLATION.md",
        ]

        for rel_path in required_paths:
            full_path = os.path.join(BASE_DIR, rel_path)
            self.assertTrue(os.path.isfile(full_path), f"Required file must exist: {rel_path}")
            self.assertGreater(os.path.getsize(full_path), 50, f"File must not be empty: {rel_path}")


if __name__ == "__main__":
    unittest.main()
