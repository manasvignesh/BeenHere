#!/usr/bin/env python3
"""
tests/test_e2e_integration.py - Full Workflow End-to-End Integration Tests for BeenHere v1.1.

Validates that all BeenHere components work together seamlessly across the complete lifecycle:
User Idea -> Concept Expander -> Cross-Industry Analyzer -> Repository Inspector -> Repository Comparator -> Blueprint Synthesis.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.concept_expander import build_research_plan
from scripts.cross_industry_analyzer import analyze_cross_industry_opportunities, format_cross_industry_section
from scripts.repo_comparator import compare_repositories, generate_integration_blueprint


class TestEndToEndSkillWorkflowIntegration(unittest.TestCase):
    """End-to-end tests verifying data contracts between all BeenHere v1.1 modules."""

    def test_full_pipeline_disaster_response_scenario(self):
        """
        Verify the complete workflow on the unfamiliar primary scenario:
        Offline-first disaster response coordination system.
        """
        concept = (
            "Build an offline-first local disaster-response coordination system that lets volunteer "
            "teams exchange task assignments, resource availability, and location updates when internet connectivity is intermittent."
        )

        # 1. Concept Expander Execution
        plan = build_research_plan(concept)
        self.assertEqual(plan["status"], "success")
        self.assertIn("decomposition", plan)
        self.assertIn("offline_first_collaborative_sync", plan["expansion_metadata"]["matched_taxonomy_domains"])

        # 2. Cross-Industry Analyzer Execution from Plan
        cross_ind = analyze_cross_industry_opportunities(plan, {"target_language": "typescript"})
        self.assertEqual(cross_ind["status"], "SUCCESS")
        self.assertTrue(cross_ind["transfer_needed"])

        # Check that CRDT is identified as TRANSFERABLE_IMPLEMENTATION
        discoveries = cross_ind["evaluated_discoveries"]
        crdt_eval = [d for d in discoveries if "crdt" in d["approach_name"].lower()]
        self.assertTrue(len(crdt_eval) > 0)
        self.assertEqual(crdt_eval[0]["classification"], "TRANSFERABLE_IMPLEMENTATION")

        # Check that Raft is identified and disqualified as NOT_TRANSFERABLE
        raft_eval = [d for d in discoveries if "raft" in d["approach_name"].lower()]
        self.assertTrue(len(raft_eval) > 0)
        self.assertEqual(raft_eval[0]["classification"], "NOT_TRANSFERABLE")

        # Format markdown section
        cross_md = format_cross_industry_section(cross_ind)
        self.assertIn("### Solutions from Other Industries", cross_md)
        self.assertIn("CRDTs", cross_md)
        self.assertIn("NOT_TRANSFERABLE", cross_md)

        # 3. Multi-Candidate Repository Comparison
        # Simulate outputs from repo_inspector.py
        candidate_automerge = {
            "status": "success",
            "repository": "automerge/automerge",
            "html_url": "https://github.com/automerge/automerge",
            "description": "A JSON-like data structure (a CRDT) that can be modified concurrently by different users",
            "verification_depth": "SOURCE_CODE_INSPECTED",
            "primary_language": "Rust",
            "stargazers_count": 18000,
            "license": {
                "spdx_id": "MIT",
                "name": "MIT License",
                "category": "PERMISSIVE",
                "clearance": "PERMITTED_FOR_ADOPTION",
                "rationale": "Permissive license.",
            },
            "manifests_detected": ["Cargo.toml"],
            "maintenance": {
                "status": "ACTIVE",
                "is_archived": False,
                "days_since_last_push": 1,
            },
            "inspected_source_files": [{"path": "rust/src/lib.rs"}],
            "exported_symbols": ["Automerge", "Change", "SyncState"],
        }

        candidate_briar = {
            "status": "success",
            "repository": "briar/briar",
            "html_url": "https://github.com/briar/briar",
            "description": "Secure messaging, forums & blogs designed for activists & journalists",
            "verification_depth": "SOURCE_CODE_INSPECTED",
            "primary_language": "Java",
            "stargazers_count": 2200,
            "license": {
                "spdx_id": "GPL-3.0",
                "name": "GNU General Public License v3.0",
                "category": "RECIPROCAL_ON_DISTRIBUTION",
                "clearance": "COPYLEFT_DISTRIBUTION_TRIGGER",
                "rationale": "Reciprocal copyleft on distribution.",
            },
            "manifests_detected": ["build.gradle"],
            "maintenance": {
                "status": "ACTIVE",
                "is_archived": False,
                "days_since_last_push": 3,
            },
            "inspected_source_files": [{"path": "briar-core/src/net/briarproject/briar/api/sync/SyncSession.java"}],
            "exported_symbols": ["SyncSession", "TransportId"],
        }

        project_ctx = {
            "target_language": "typescript",
            "deployment_model": "offline_first_mobile",
            "required_capability": "offline-first local disaster coordination and sync",
        }

        comparison = compare_repositories([candidate_automerge, candidate_briar], project_ctx)
        self.assertIn(comparison["comparison_confidence"], ("CONFIDENT", "CONDITIONAL"))
        self.assertEqual(len(comparison["candidates"]), 2)

        # Automerge is MIT with inspected symbols
        automerge_comp = [c for c in comparison["candidates"] if "automerge" in c["slug"]][0]
        self.assertIn(automerge_comp["posture"], ("ADOPT_AS_DEPENDENCY", "USE_AS_ARCHITECTURAL_REFERENCE"))

        # 4. Blueprint Generation
        blueprint = generate_integration_blueprint(comparison)
        self.assertIn("# BeenHere Integration Blueprint", blueprint)
        self.assertIn("Anti-Corruption Adapter", blueprint)
        self.assertIn("Pre-Adoption License & Legal Checklist", blueprint)

    def test_pipeline_negative_control_chaining(self):
        """Verify negative control propagates correctly from concept expander to cross-industry analyzer."""
        crud_concept = "Simple CRUD blog with static HTML pages"
        plan = build_research_plan(crud_concept)
        cross_res = analyze_cross_industry_opportunities(plan)
        self.assertEqual(cross_res["status"], "NEGATIVE_CONTROL_TRIGGERED")
        self.assertFalse(cross_res["transfer_needed"])
        self.assertEqual(len(cross_res["evaluated_discoveries"]), 0)

        md = format_cross_industry_section(cross_res)
        self.assertIn("Direct Category Solutions Sufficient", md)
        self.assertIn("No cross-industry transfer required", md)

    def test_cli_subprocess_chaining(self):
        """Verify CLI scripts execute and pipe JSON cleanly between subprocesses."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_path = os.path.join(tmpdir, "plan.json")
            cross_path = os.path.join(tmpdir, "cross.json")
            candidates_path = os.path.join(tmpdir, "candidates.json")
            blueprint_path = os.path.join(tmpdir, "blueprint.md")

            # 1. Run concept_expander CLI
            cmd_exp = [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "concept_expander.py"),
                "--concept",
                "Offline disaster mesh messaging",
                "--json",
                "--output",
                plan_path,
            ]
            res_exp = subprocess.run(cmd_exp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.assertTrue(os.path.exists(plan_path))

            # 2. Run cross_industry_analyzer CLI using the generated plan
            cmd_cross = [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "cross_industry_analyzer.py"),
                "--plan",
                plan_path,
                "--json",
                "--output",
                cross_path,
            ]
            res_cross = subprocess.run(cmd_cross, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.assertTrue(os.path.exists(cross_path))
            with open(cross_path, "r", encoding="utf-8") as f:
                cross_data = json.load(f)
            self.assertEqual(cross_data["status"], "SUCCESS")

            # 3. Run repo_comparator CLI
            candidates_data = [
                {
                    "slug": "sample/p2p-sync",
                    "language": "Go",
                    "stars": 1200,
                    "license_info": {"declared_spdx": "MIT", "category": "PERMISSIVE"},
                    "exported_symbols": ["SyncNode"],
                    "evidence_completeness": {
                        "license_inspected": True,
                        "manifest_inspected": True,
                        "source_inspected": True,
                    },
                }
            ]
            with open(candidates_path, "w", encoding="utf-8") as f:
                json.dump(candidates_data, f)

            cmd_comp = [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "repo_comparator.py"),
                "--input",
                candidates_path,
                "--blueprint",
                "--output",
                blueprint_path,
            ]
            res_comp = subprocess.run(cmd_comp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.assertTrue(os.path.exists(blueprint_path))
            with open(blueprint_path, "r", encoding="utf-8") as f:
                bp_text = f.read()
            self.assertIn("# BeenHere Integration Blueprint: `sample/p2p-sync`", bp_text)


if __name__ == "__main__":
    unittest.main()
