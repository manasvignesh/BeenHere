"""
tests/test_phase4.py - Unit Tests for BeenHere Phase 4 Usability, Packaging & Installation
"""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path for direct imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import validate_skill
import install_skill


class TestSkillValidator(unittest.TestCase):
    """Test suite for packaging and repository integrity validation."""

    def setUp(self):
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def test_current_repo_passes_validation(self):
        """Current BeenHere repository must pass all packaging validation checks."""
        results = validate_skill.run_validation(self.repo_root)
        self.assertTrue(results["valid"], f"Validation failed with errors: {results['errors']}")
        self.assertTrue(results["checks"]["skill_md"]["passed"])
        self.assertTrue(results["checks"]["scripts"]["passed"])
        self.assertTrue(results["checks"]["secrets"]["passed"])

    def test_frontmatter_parser_valid(self):
        """Test parsing valid frontmatter."""
        content = """---
name: beenhere
description: "A valid description for testing"
license: MIT
metadata:
  version: "1.0.0"
allowed-tools: Bash, Read
---
# Body Title
Content here.
"""
        fm, body, errors = validate_skill.parse_frontmatter(content)
        self.assertEqual(len(errors), 0)
        self.assertEqual(fm["name"], "beenhere")
        self.assertEqual(fm["description"], "A valid description for testing")
        self.assertEqual(fm["metadata"]["version"], "1.0.0")
        self.assertIn("# Body Title", body)

    def test_frontmatter_parser_missing_delimiter(self):
        """Test parsing frontmatter missing closing delimiter."""
        content = """---
name: beenhere
description: Missing closing delimiter
"""
        fm, body, errors = validate_skill.parse_frontmatter(content)
        self.assertTrue(any("closing frontmatter delimiter" in e for e in errors))

    def test_secret_scanner_detects_token(self):
        """Test that dummy secrets are identified by the scanner."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "leak.py")
            dummy_token = "ghp_" + ("A" * 36)
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(f'TOKEN = "{dummy_token}"\n')
            
            valid, errors = validate_skill.scan_for_secrets(tmpdir)
            self.assertFalse(valid)
            self.assertTrue(any("GitHub Personal Access Token" in e for e in errors))

    def test_script_syntax_error_detected(self):
        """Test that syntax errors in scripts are flagged by AST parser."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = os.path.join(tmpdir, "scripts")
            os.makedirs(scripts_dir, exist_ok=True)
            bad_file = os.path.join(scripts_dir, "broken.py")
            with open(bad_file, "w", encoding="utf-8") as f:
                f.write("def broken_syntax(:\n    pass\n")
            
            valid, errors, _ = validate_skill.validate_python_scripts(tmpdir)
            self.assertFalse(valid)
            self.assertTrue(any("broken.py" in e for e in errors))


class TestSkillInstaller(unittest.TestCase):
    """Test suite for agent skill installation and uninstallation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="beenhere_install_test_")
        self.repo_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_resolve_paths_local_claude_and_codex(self):
        """Verify destination paths for claude, codex, and all in a local project."""
        target = Path(self.temp_dir)
        paths_claude = install_skill.resolve_install_paths(str(target), "claude", False)
        self.assertEqual(len(paths_claude), 1)
        self.assertEqual(paths_claude[0][1], target / ".claude" / "skills" / "beenhere")

        paths_codex = install_skill.resolve_install_paths(str(target), "codex", False)
        self.assertEqual(len(paths_codex), 1)
        self.assertEqual(paths_codex[0][1], target / ".agents" / "skills" / "beenhere")

        paths_all = install_skill.resolve_install_paths(str(target), "all", False)
        self.assertEqual(len(paths_all), 2)

    def test_resolve_paths_global(self):
        """Verify global paths resolve to user home directory."""
        home = Path.home()
        paths = install_skill.resolve_install_paths(".", "all", True)
        self.assertEqual(paths[0][1], home / ".claude" / "skills" / "beenhere")
        self.assertEqual(paths[1][1], home / ".agents" / "skills" / "beenhere")

    def test_install_and_uninstall_in_mock_project(self):
        """Perform end-to-end local installation and clean uninstallation in mock project."""
        target = Path(self.temp_dir)
        paths = install_skill.resolve_install_paths(str(target), "all", False)

        # 1. Install via copy
        actions = install_skill.install_skill(self.repo_root, paths, mode="copy", dry_run=False)
        self.assertEqual(len(actions), 2)
        for act in actions:
            self.assertEqual(act["status"], "installed")
            dest = Path(act["path"])
            self.assertTrue(dest.exists(), f"Destination not found: {dest}")
            self.assertTrue((dest / "SKILL.md").exists())
            self.assertTrue((dest / "scripts" / "github_search.py").exists())
            self.assertTrue((dest / "templates" / "IDEA_LANDSCAPE.md").exists())

        # 2. Re-install (idempotence test)
        re_actions = install_skill.install_skill(self.repo_root, paths, mode="copy", dry_run=False)
        self.assertEqual(len(re_actions), 2)
        for act in re_actions:
            self.assertEqual(act["status"], "installed")

        # 3. Dry run uninstall
        dry_actions = install_skill.uninstall_skill(paths, dry_run=True)
        for act in dry_actions:
            self.assertEqual(act["status"], "would_remove")
            self.assertTrue(Path(act["path"]).exists())

        # 4. Actual uninstall
        un_actions = install_skill.uninstall_skill(paths, dry_run=False)
        for act in un_actions:
            self.assertEqual(act["status"], "removed")
            self.assertFalse(Path(act["path"]).exists())


if __name__ == "__main__":
    unittest.main()
