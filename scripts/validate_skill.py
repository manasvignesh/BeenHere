#!/usr/bin/env python3
"""
scripts/validate_skill.py - Packaging and Validation Utility for BeenHere

Validates:
1. SKILL.md frontmatter, schema, metadata, and required attributes.
2. File integrity for all referenced scripts, references, and templates.
3. Python syntax and standard-library-only constraints for all scripts.
4. Absence of hardcoded credentials, API keys, or personal access tokens.
5. Exit code 0 if all checks pass; non-zero if critical failures are found.
"""

import os
import sys
import re
import ast
import json
import argparse
from typing import Dict, List, Any, Tuple


SECRET_PATTERNS = [
    (r"ghp_[A-Za-z0-9]{36}", "GitHub Personal Access Token"),
    (r"github_pat_[A-Za-z0-9_]{82}", "GitHub Fine-Grained Token"),
    (r"sk-[A-Za-z0-9]{32,}", "OpenAI/Anthropic API Key"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"-----BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY-----", "Private Key Header"),
]


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str, List[str]]:
    """Parse YAML-style frontmatter from SKILL.md content without external PyYAML."""
    errors = []
    if not content.startswith("---"):
        return {}, content, ["File does not begin with frontmatter delimiter ('---')."]
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content, ["File does not have a closing frontmatter delimiter ('---')."]
    
    frontmatter_raw = parts[1].strip()
    body = parts[2].strip()
    
    data: Dict[str, Any] = {}
    current_key = None
    subdict_key = None
    
    for line_num, line in enumerate(frontmatter_raw.splitlines(), start=2):
        raw_line = line
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        # Check sub-dictionary indentation (e.g., metadata:)
        if raw_line.startswith("  ") and subdict_key:
            if ":" in line:
                sub_k, sub_v = line.split(":", 1)
                sub_k = sub_k.strip()
                sub_v = sub_v.strip().strip('"').strip("'")
                data[subdict_key][sub_k] = sub_v
            continue
        else:
            subdict_key = None
            
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if not v:
                # Potential parent dict or empty
                data[k] = {}
                subdict_key = k
            else:
                data[k] = v
                current_key = k

    return data, body, errors


def validate_skill_md(root_dir: str) -> Tuple[bool, List[str], List[str]]:
    """Verify SKILL.md structure, frontmatter fields, and referenced paths."""
    skill_path = os.path.join(root_dir, "SKILL.md")
    errors = []
    warnings = []
    
    if not os.path.isfile(skill_path):
        return False, [f"Missing canonical SKILL.md at {skill_path}"], []
    
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    fm, body, fm_errors = parse_frontmatter(content)
    if fm_errors:
        errors.extend(fm_errors)
        return False, errors, warnings
    
    # Required frontmatter fields
    if "name" not in fm or not fm["name"]:
        errors.append("Frontmatter missing required 'name' field.")
    elif fm["name"] != "beenhere":
        errors.append(f"Skill name should be 'beenhere', found '{fm['name']}'.")
        
    if "description" not in fm or not fm["description"]:
        errors.append("Frontmatter missing required 'description' field.")
    elif len(fm["description"]) < 20:
        warnings.append("Description is very brief (< 20 chars).")
        
    if "license" not in fm:
        warnings.append("Frontmatter missing 'license' field.")
        
    if "metadata" not in fm or not isinstance(fm["metadata"], dict) or "version" not in fm["metadata"]:
        warnings.append("Frontmatter missing metadata.version specification.")
        
    if "allowed-tools" not in fm:
        warnings.append("Frontmatter missing 'allowed-tools' field.")
        
    # Check referenced files inside SKILL.md
    file_references = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", body)
    for text, link in file_references:
        # Ignore external URLs
        if link.startswith("http://") or link.startswith("https://") or link.startswith("#"):
            continue
        clean_link = link.split("#")[0].strip()
        if not clean_link:
            continue
        target_path = os.path.normpath(os.path.join(root_dir, clean_link))
        if not os.path.exists(target_path):
            errors.append(f"Broken link in SKILL.md: '{clean_link}' (referenced as '{text}')")
            
    # Also check inline script mentions like `scripts/foo.py`
    script_mentions = set(re.findall(r"(?:scripts|references|templates)/[A-Za-z0-9_\-\.]+", body))
    for sm in script_mentions:
        target_path = os.path.normpath(os.path.join(root_dir, sm))
        if not os.path.exists(target_path):
            errors.append(f"Referenced path in SKILL.md does not exist: '{sm}'")
            
    return len(errors) == 0, errors, warnings


def validate_python_scripts(root_dir: str) -> Tuple[bool, List[str], List[str]]:
    """Verify syntax and stdlib-only constraints for all scripts/*.py."""
    scripts_dir = os.path.join(root_dir, "scripts")
    errors = []
    warnings = []
    
    if not os.path.isdir(scripts_dir):
        return False, [f"Missing scripts directory at {scripts_dir}"], []
    
    # Standard library fallback list
    stdlib = sys.stdlib_module_names if hasattr(sys, "stdlib_module_names") else set()
    common_stdlib = {
        "os", "sys", "re", "json", "urllib", "time", "argparse", "typing",
        "ast", "datetime", "hashlib", "pathlib", "unittest", "shutil",
        "subprocess", "math", "collections", "itertools", "tempfile",
        "copy", "traceback", "inspect", "platform"
    }
    
    # Internal sibling modules in scripts
    internal_modules = {os.path.splitext(f)[0] for f in os.listdir(scripts_dir) if f.endswith(".py")}
    
    py_files = [f for f in os.listdir(scripts_dir) if f.endswith(".py")]
    if not py_files:
        errors.append("No Python scripts found in scripts/ directory.")
        return False, errors, warnings
        
    for fname in py_files:
        fpath = os.path.join(scripts_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            code = f.read()
            
        try:
            tree = ast.parse(code, filename=fname)
        except SyntaxError as se:
            errors.append(f"Syntax error in {fname} (line {se.lineno}): {se.msg}")
            continue
            
        # Verify imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base = alias.name.split(".")[0]
                    if base not in common_stdlib and base not in stdlib and base not in internal_modules:
                        warnings.append(f"{fname}: non-standard library import '{alias.name}' detected.")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    base = node.module.split(".")[0]
                    if base not in common_stdlib and base not in stdlib and base not in internal_modules:
                        warnings.append(f"{fname}: non-standard library import '{node.module}' detected.")
                        
    return len(errors) == 0, errors, warnings


def scan_for_secrets(root_dir: str) -> Tuple[bool, List[str]]:
    """Scan code files for accidentally embedded tokens or secrets."""
    errors = []
    skip_dirs = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", "tests"}
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fname in filenames:
            if not fname.endswith((".py", ".md", ".json", ".yaml", ".yml", ".txt")):
                continue
            fpath = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(fpath, root_dir)
            
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue
                
            for pattern, label in SECRET_PATTERNS:
                matches = re.findall(pattern, content)
                # Allow dummy examples if explicitly commented as dummy
                for match in matches:
                    if "dummy" in match.lower() or "example" in match.lower() or "xxxx" in match.lower():
                        continue
                    errors.append(f"Possible {label} found in {rel_path}: {match[:8]}...")
                    
    return len(errors) == 0, errors


def run_validation(root_dir: str) -> Dict[str, Any]:
    """Execute full validation suite and compile results."""
    root_dir = os.path.abspath(root_dir)
    results = {
        "root_dir": root_dir,
        "valid": True,
        "errors": [],
        "warnings": [],
        "checks": {}
    }
    
    # 1. Validate SKILL.md
    skill_valid, skill_err, skill_warn = validate_skill_md(root_dir)
    results["checks"]["skill_md"] = {
        "passed": skill_valid,
        "errors": skill_err,
        "warnings": skill_warn
    }
    if not skill_valid:
        results["valid"] = False
        results["errors"].extend(skill_err)
    results["warnings"].extend(skill_warn)
    
    # 2. Validate Python scripts
    scripts_valid, script_err, script_warn = validate_python_scripts(root_dir)
    results["checks"]["scripts"] = {
        "passed": scripts_valid,
        "errors": script_err,
        "warnings": script_warn
    }
    if not scripts_valid:
        results["valid"] = False
        results["errors"].extend(script_err)
    results["warnings"].extend(script_warn)
    
    # 3. Scan for secrets
    secrets_valid, secret_err = scan_for_secrets(root_dir)
    results["checks"]["secrets"] = {
        "passed": secrets_valid,
        "errors": secret_err
    }
    if not secrets_valid:
        results["valid"] = False
        results["errors"].extend(secret_err)
        
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="BeenHere Skill Packaging & Integrity Validator"
    )
    parser.add_argument(
        "--root", "-r",
        default=".",
        help="Path to repository root (defaults to current working directory)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON validation report"
    )
    args = parser.parse_args()
    
    results = run_validation(args.root)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"=== BeenHere Skill Validation Report: {results['root_dir']} ===")
        print(f"Overall Status: {'[PASS] VALID' if results['valid'] else '[FAIL] INVALID'}\n")
        
        for check_name, check_data in results["checks"].items():
            status_tag = "[PASS]" if check_data["passed"] else "[FAIL]"
            print(f"{status_tag} {check_name}")
            for err in check_data.get("errors", []):
                print(f"   [ERROR] {err}")
            for warn in check_data.get("warnings", []):
                print(f"   [WARN]  {warn}")
                
        if results["valid"]:
            print("\nAll packaging checks passed successfully.")
        else:
            print(f"\nValidation failed with {len(results['errors'])} error(s).")
            
    return 0 if results["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
