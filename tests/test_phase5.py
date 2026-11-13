"""
tests/test_phase5.py - Unit Tests for BeenHere Phase 5 Final Hardening & Public Beta Preparation
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import urllib.error

# Add scripts directory to path for direct imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import github_search
import repo_inspector
import paper_search
import integration_analyzer
import verify_sources


class TestPhase5SocketAndNetworkFallbacks(unittest.TestCase):
    """Test suite for subprocess network error detection and host-agent fallback guidance."""

    @patch("github_search.search_github_repositories")
    def test_github_search_socket_restriction_fallback(self, mock_search):
        """Verify that [WinError 10013] or WSAEACCES generates an explicit fallback recommendation."""
        mock_search.side_effect = RuntimeError(
            "Network error accessing GitHub API: [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions"
        )
        res = github_search.multi_query_search(["recruitment ats", "resume parser"])
        self.assertEqual(res["status"], "error")
        self.assertIn("fallback_recommendation", res)
        self.assertIn("Subprocess network socket access was restricted", res["fallback_recommendation"])
        self.assertIn("Host AI agent", res["fallback_recommendation"])

        table_output = github_search.format_text_table(res)
        self.assertIn("[!WARNING] Subprocess Network Restriction", table_output)
        self.assertIn("Host AI agent", table_output)

    @patch("repo_inspector.make_request")
    def test_repo_inspector_socket_restriction_fallback(self, mock_req):
        """Verify that socket errors in repo inspector return structured error and fallback guidance."""
        mock_req.side_effect = RuntimeError(
            "Network error accessing GitHub API: [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions"
        )
        inspection = repo_inspector.inspect_repository("owner", "repo")
        self.assertIn("error", inspection)
        self.assertIn("fallback_recommendation", inspection)
        self.assertIn("Subprocess network socket access was denied", inspection["fallback_recommendation"])

        report = repo_inspector.format_inspection_report(inspection)
        self.assertIn("[!WARNING] Subprocess Network Restriction", report)

    @patch("paper_search.query_openalex")
    def test_paper_search_socket_restriction_fallback(self, mock_openalex):
        """Verify that socket errors in paper search generate fallback recommendation."""
        mock_openalex.return_value = {
            "provider": "openalex",
            "status": "network_error",
            "error": "Network error accessing API: [WinError 10013] WSAEACCES socket forbidden",
            "items": [],
        }
        res = paper_search.search_academic_papers(
            queries=["document extraction"],
            providers=["openalex"],
        )
        self.assertIn("fallback_recommendation", res)
        self.assertIn("Subprocess network socket access was restricted", res["fallback_recommendation"])

        report = paper_search.format_academic_table(res)
        self.assertIn("[!WARNING] Subprocess Network Restriction", report)


class TestPhase5LicenseAdvisoriesAndEvidenceAudit(unittest.TestCase):
    """Test suite for sensitive dependency detection and evidence auditing."""

    def test_requirements_txt_detects_pymupdf_license_hazard(self):
        """Verify that PyMuPDF in requirements.txt triggers an AGPL/Artifex commercial license warning."""
        req_content = """
django>=4.2
pymupdf>=1.23.0
spacy>=3.7
"""
        manifest = integration_analyzer.parse_requirements_txt(req_content)
        self.assertEqual(manifest["total_packages"], 3)
        considerations = manifest["integration_considerations"]
        has_pymupdf_warning = any("pymupdf" in c.lower() and "agpl" in c.lower() for c in considerations)
        self.assertTrue(has_pymupdf_warning, f"Expected PyMuPDF warning, got: {considerations}")

    def test_requirements_txt_detects_redis_license_hazard(self):
        """Verify that Redis in requirements.txt triggers an RSAL/SSPL license warning."""
        req_content = "redis>=7.4.0\n"
        manifest = integration_analyzer.parse_requirements_txt(req_content)
        considerations = manifest["integration_considerations"]
        has_redis_warning = any("redis" in c.lower() and "sspl" in c.lower() for c in considerations)
        self.assertTrue(has_redis_warning, f"Expected Redis warning, got: {considerations}")

    def test_verify_sources_recognizes_unverified_marketing_claim_tag(self):
        """Verify that [UNVERIFIED-MARKETING-CLAIM] is counted and audited in evidence hierarchy."""
        sample_doc = """
# Product Evaluation
- Vendor claims 50% faster scheduling [UNVERIFIED-MARKETING-CLAIM].
- Source inspection confirmed async loops [VERIFIED-SOURCE].
"""
        audit = verify_sources.audit_evidence_tags(sample_doc)
        self.assertEqual(audit["tag_counts"]["[UNVERIFIED-MARKETING-CLAIM]"], 1)
        self.assertEqual(audit["tag_counts"]["[VERIFIED-SOURCE]"], 1)
        self.assertTrue(audit["has_evidence_tagging"])


if __name__ == "__main__":
    unittest.main()
