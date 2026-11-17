#!/usr/bin/env python3
"""
scripts/integration_analyzer.py - Deep Code-Reusability & Integration Point Analyzer.

Part of BeenHere: Explore every angle of an idea before you build it.
Uses Python standard library only (no external dependencies).

Analyzes:
1. Public symbols, interfaces, and exported functions (Python AST, JS/TS tokenization).
2. Dependency manifests (package.json, pyproject.toml, requirements.txt, Cargo.toml).
3. Nuanced license evidence (Permissive, Weak/Strong/Network Copyleft, BSL-1.1 Grants).
4. Evidence-backed reuse recommendations (Adopt, Integrate, Fork, Extract, Reimplement, Build).
"""

import argparse
import ast
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import tomllib
except ImportError:
    tomllib = None  # type: ignore

USER_AGENT = "BeenHere/1.1.0 (https://github.com/manasvignesh/BeenHere)"
GITHUB_API_BASE = "https://api.github.com"

# Injection defenses for untrusted code comments, docstrings, and manifests
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"(?i)system\s*prompt\s*:",
    r"(?i)override\s+(all\s+)?(evaluation|rules|rubric)",
    r"(?i)you\s+must\s+(adopt|approve|recommend)",
    r"(?i)pretend\s+you\s+are",
    r"(?i)new\s+system\s+instruction",
]

LEGAL_DISCLAIMER = (
    "DISCLAIMER: BeenHere provides automated heuristic analysis of license texts and code "
    "structures. It does not provide formal legal advice. Actual license permissions, "
    "obligations, and compatibility must be reviewed by qualified legal counsel."
)


def sanitize_untrusted_text(text: str) -> Tuple[str, bool]:
    """Sanitize external text and neutralize prompt injection attempts."""
    if not text:
        return "", False
    injected = False
    sanitized = text
    for pat in INJECTION_PATTERNS:
        if re.search(pat, sanitized):
            injected = True
            sanitized = re.sub(pat, "[FILTERED_INSTRUCTION_ATTEMPT]", sanitized)
    return sanitized, injected


def _extract_ast_str(node: Any) -> Optional[str]:
    """Extract string value from an AST node across Python 3.8 - 3.14+."""
    if node is None:
        return None
    # Python 3.8 ast.Index wrapper around slice
    if hasattr(ast, "Index") and isinstance(node, ast.Index):
        node = node.value
    # Python 3.8+ ast.Constant
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    # Python 3.8 legacy ast.Str
    if hasattr(ast, "Str") and isinstance(node, ast.Str):
        return getattr(node, "s", None)
    return None


# ==============================================================================
# 1. STATIC SYMBOL & INTERFACE ANALYZER (PYTHON & JS/TS)
# ==============================================================================

def parse_python_source(code: str, file_path: str = "") -> Dict[str, Any]:
    """
    Statically parse Python source code using Python's standard library `ast`.
    Extracts exported symbols, classes, methods, functions, docstrings, imports,
    environment variable requirements, and line ranges.
    """
    sanitized_code, injected = sanitize_untrusted_text(code)
    result: Dict[str, Any] = {
        "language": "Python",
        "file_path": file_path,
        "parser": "ast (Standard Library)",
        "syntax_valid": True,
        "classes": [],
        "functions": [],
        "exported_symbols": [],
        "imported_modules": [],
        "env_vars_detected": [],
        "has_prompt_injection": injected,
        "limitations": "Standard library ast parsing; dynamic getattr/globals and runtime monkeypatching are not resolved.",
    }

    try:
        tree = ast.parse(sanitized_code)
    except SyntaxError as e:
        result["syntax_valid"] = False
        result["syntax_error"] = f"Line {e.lineno}: {e.msg}"
        # Fallback to regex symbol extraction
        result.update(_fallback_regex_symbol_extraction(sanitized_code))
        return result

    # Check for __all__
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for elt in node.value.elts:
                            s = _extract_ast_str(elt)
                            if s:
                                result["exported_symbols"].append(s)

    # Check if __all__ was explicitly declared
    has_dunder_all = bool(result["exported_symbols"])

    # Walk AST top-level nodes
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            is_exported = (node.name in result["exported_symbols"]) if has_dunder_all else not node.name.startswith("_")
            if is_exported:
                if not has_dunder_all:
                    result["exported_symbols"].append(node.name)
                doc = ast.get_docstring(node) or ""
                bases = []
                for b in node.bases:
                    if isinstance(b, ast.Name):
                        bases.append(b.id)
                    elif isinstance(b, ast.Attribute):
                        bases.append(f"{getattr(b.value, 'id', '')}.{b.attr}")
                
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not item.name.startswith("_") or item.name == "__init__":
                            m_args = [a.arg for a in item.args.args if a.arg != "self"]
                            methods.append({
                                "name": item.name,
                                "is_async": isinstance(item, ast.AsyncFunctionDef),
                                "args": m_args,
                                "line_start": item.lineno,
                                "line_end": getattr(item, "end_lineno", item.lineno),
                            })
                
                result["classes"].append({
                    "name": node.name,
                    "bases": bases,
                    "docstring": doc.strip().splitlines()[0] if doc else "",
                    "methods": methods,
                    "line_start": node.lineno,
                    "line_end": getattr(node, "end_lineno", node.lineno),
                })
        
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_exported = (node.name in result["exported_symbols"]) if has_dunder_all else not node.name.startswith("_")
            if is_exported:
                if not has_dunder_all:
                    result["exported_symbols"].append(node.name)
                doc = ast.get_docstring(node) or ""
                f_args = [a.arg for a in node.args.args]
                ret_annotation = ""
                if node.returns:
                    if isinstance(node.returns, ast.Name):
                        ret_annotation = node.returns.id
                    elif isinstance(node.returns, ast.Constant):
                        ret_annotation = str(node.returns.value)
                    elif hasattr(ast, "Str") and isinstance(node.returns, ast.Str):
                        ret_annotation = getattr(node.returns, "s", "")

                result["functions"].append({
                    "name": node.name,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "args": f_args,
                    "return_type": ret_annotation,
                    "docstring": doc.strip().splitlines()[0] if doc else "",
                    "line_start": node.lineno,
                    "line_end": getattr(node, "end_lineno", node.lineno),
                })

    # Detect imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result["imported_modules"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                result["imported_modules"].append(node.module)

    result["imported_modules"] = sorted(list(set(result["imported_modules"])))

    # Detect environment variables: os.environ, os.environ.get, os.getenv
    env_vars: Set[str] = set()
    for node in ast.walk(tree):
        # os.environ['VAR'] or environ['VAR']
        if isinstance(node, ast.Subscript):
            is_environ = False
            if isinstance(node.value, ast.Attribute) and node.value.attr == "environ":
                is_environ = True
            elif isinstance(node.value, ast.Name) and node.value.id == "environ":
                is_environ = True
            if is_environ:
                var_name = _extract_ast_str(node.slice)
                if var_name:
                    env_vars.add(var_name)
        elif isinstance(node, ast.Call):
            # os.getenv('VAR') or getenv('VAR')
            if isinstance(node.func, ast.Attribute) and node.func.attr == "getenv":
                if node.args:
                    var_name = _extract_ast_str(node.args[0])
                    if var_name:
                        env_vars.add(var_name)
            elif isinstance(node.func, ast.Name) and node.func.id == "getenv":
                if node.args:
                    var_name = _extract_ast_str(node.args[0])
                    if var_name:
                        env_vars.add(var_name)
            # os.environ.get('VAR') or environ.get('VAR')
            elif isinstance(node.func, ast.Attribute) and node.func.attr == "get":
                target_val = node.func.value
                is_environ_get = False
                if isinstance(target_val, ast.Attribute) and target_val.attr == "environ":
                    is_environ_get = True
                elif isinstance(target_val, ast.Name) and target_val.id == "environ":
                    is_environ_get = True
                if is_environ_get and node.args:
                    var_name = _extract_ast_str(node.args[0])
                    if var_name:
                        env_vars.add(var_name)

    result["env_vars_detected"] = sorted(list(env_vars))
    return result


def parse_js_ts_source(code: str, file_path: str = "") -> Dict[str, Any]:
    """
    Parse JavaScript and TypeScript source code using regex tokenization.
    Extracts exported symbols, interfaces, types, classes, functions, imports,
    and process.env variables.
    
    LIMITATION: This is a static regex/token scanner, not a full TypeScript compiler
    or Babel AST. Complex conditional exports, dynamically computed exports,
    or namespace augmentations may not be fully resolved.
    """
    sanitized_code, injected = sanitize_untrusted_text(code)
    lines = sanitized_code.splitlines()
    
    result: Dict[str, Any] = {
        "language": "TypeScript" if file_path.endswith((".ts", ".tsx")) else "JavaScript",
        "file_path": file_path,
        "parser": "Lightweight Token Scanner (Standard Library)",
        "syntax_valid": True,
        "classes": [],
        "functions": [],
        "interfaces": [],
        "types": [],
        "exported_symbols": [],
        "imported_modules": [],
        "env_vars_detected": [],
        "has_prompt_injection": injected,
        "limitations": "Lightweight regex tokenizer; does not perform full semantic AST parsing or type checking.",
    }

    # Extract exports
    export_class_pat = re.compile(r'^\s*export\s+(?:default\s+)?class\s+([A-Za-z0-9_$]+)(?:\s+extends\s+([A-Za-z0-9_$.]+))?')
    export_fn_pat = re.compile(r'^\s*export\s+(?:default\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\(([^)]*)\)')
    export_const_pat = re.compile(r'^\s*export\s+(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*(?::\s*[^=]+)?\s*=')
    export_interface_pat = re.compile(r'^\s*export\s+(?:default\s+)?interface\s+([A-Za-z0-9_$]+)')
    export_type_pat = re.compile(r'^\s*export\s+type\s+([A-Za-z0-9_$]+)')
    export_block_pat = re.compile(r'^\s*export\s*\{([^}]+)\}')
    import_pat = re.compile(r'(?:import\s+.*?from\s+[\'"]([^\'"]+)[\'"]|require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\))')
    env_pat = re.compile(r'process\.env(?:\.([A-Za-z0-9_]+)|\[[\'"]([A-Za-z0-9_]+)[\'"]\])')

    imported_mods: Set[str] = set()
    env_vars: Set[str] = set()

    for idx, line in enumerate(lines, start=1):
        # Imports
        for m in import_pat.finditer(line):
            mod = m.group(1) or m.group(2)
            if mod:
                imported_mods.add(mod)

        # Environment variables
        for m in env_pat.finditer(line):
            var_name = m.group(1) or m.group(2)
            if var_name:
                env_vars.add(var_name)

        # Exported classes
        m_cls = export_class_pat.search(line)
        if m_cls:
            name = m_cls.group(1)
            base = m_cls.group(2) or ""
            result["classes"].append({
                "name": name,
                "base": base,
                "line": idx,
            })
            result["exported_symbols"].append(name)
            continue

        # Exported functions
        m_fn = export_fn_pat.search(line)
        if m_fn:
            name = m_fn.group(1)
            args = [a.strip() for a in m_fn.group(2).split(",") if a.strip()]
            result["functions"].append({
                "name": name,
                "args": args,
                "line": idx,
            })
            result["exported_symbols"].append(name)
            continue

        # Exported const/let
        m_const = export_const_pat.search(line)
        if m_const:
            name = m_const.group(1)
            result["exported_symbols"].append(name)
            continue

        # Exported interface (TypeScript)
        m_iface = export_interface_pat.search(line)
        if m_iface:
            name = m_iface.group(1)
            result["interfaces"].append({"name": name, "line": idx})
            result["exported_symbols"].append(name)
            continue

        # Exported type (TypeScript)
        m_type = export_type_pat.search(line)
        if m_type:
            name = m_type.group(1)
            result["types"].append({"name": name, "line": idx})
            result["exported_symbols"].append(name)
            continue

        # Export block: export { a, b, c }
        m_blk = export_block_pat.search(line)
        if m_blk:
            for item in m_blk.group(1).split(","):
                clean_item = item.strip().split(" as ")[-1].strip()
                if clean_item:
                    result["exported_symbols"].append(clean_item)

    result["imported_modules"] = sorted(list(imported_mods))
    result["env_vars_detected"] = sorted(list(env_vars))
    result["exported_symbols"] = sorted(list(set(result["exported_symbols"])))
    return result


def _fallback_regex_symbol_extraction(code: str) -> Dict[str, Any]:
    """Fallback scanner when AST fails due to syntax errors."""
    funcs = []
    classes = []
    for idx, line in enumerate(code.splitlines(), start=1):
        m_fn = re.search(r'^\s*def\s+([A-Za-z0-9_]+)\s*\(', line)
        if m_fn:
            funcs.append({"name": m_fn.group(1), "line_start": idx, "line_end": idx})
        m_cls = re.search(r'^\s*class\s+([A-Za-z0-9_]+)', line)
        if m_cls:
            classes.append({"name": m_cls.group(1), "line_start": idx, "line_end": idx})
    return {
        "classes": classes,
        "functions": funcs,
        "exported_symbols": [f["name"] for f in funcs] + [c["name"] for c in classes],
        "imported_modules": [],
        "env_vars_detected": [],
    }


# ==============================================================================
# 2. DEPENDENCY MANIFEST PARSERS
# ==============================================================================

def parse_package_json(content: str) -> Dict[str, Any]:
    """Extract dependencies, engines, scripts, and module type from package.json."""
    sanitized, _ = sanitize_untrusted_text(content)
    try:
        data = json.loads(sanitized)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid package.json: {str(e)}", "manifest_type": "package.json"}

    return {
        "manifest_type": "package.json",
        "name": data.get("name", "unnamed"),
        "version": data.get("version", "0.0.0"),
        "license_field": data.get("license", "UNSPECIFIED"),
        "module_type": data.get("type", "commonjs"),
        "main_entry": data.get("main") or data.get("module") or data.get("exports"),
        "runtimes": data.get("engines", {}),
        "dependencies": data.get("dependencies", {}),
        "peer_dependencies": data.get("peerDependencies", {}),
        "dev_dependencies_count": len(data.get("devDependencies", {})),
        "integration_considerations": [
            f"Node/Package runtime: {data.get('engines', {}).get('node', 'Any')}",
            f"Module format: {data.get('type', 'commonjs')}",
        ],
    }


def parse_pyproject_toml(content: str) -> Dict[str, Any]:
    """Extract project dependencies, python constraints, and build system from pyproject.toml."""
    sanitized, _ = sanitize_untrusted_text(content)
    parsed: Dict[str, Any] = {}
    if tomllib:
        try:
            parsed = tomllib.loads(sanitized)
        except Exception as e:
            return {"error": f"Failed to parse pyproject.toml: {str(e)}", "manifest_type": "pyproject.toml"}
    else:
        # Minimal regex fallback for environments without tomllib
        parsed = _minimal_toml_fallback(sanitized)

    project = parsed.get("project", {})
    build_sys = parsed.get("build-system", {})
    tool_poetry = parsed.get("tool", {}).get("poetry", {})

    dependencies: List[str] = project.get("dependencies", [])
    if not dependencies and "dependencies" in tool_poetry:
        dependencies = [f"{k}{v}" if isinstance(v, str) else k for k, v in tool_poetry["dependencies"].items()]

    requires_python = project.get("requires-python") or tool_poetry.get("dependencies", {}).get("python", "Any")

    return {
        "manifest_type": "pyproject.toml",
        "name": project.get("name") or tool_poetry.get("name", "unnamed"),
        "version": project.get("version") or tool_poetry.get("version", "0.0.0"),
        "requires_python": requires_python,
        "build_backend": build_sys.get("build-backend", "unknown"),
        "dependencies": dependencies,
        "optional_dependencies": list(project.get("optional-dependencies", {}).keys()),
        "integration_considerations": [
            f"Requires Python: {requires_python}",
            f"Build Backend: {build_sys.get('build-backend', 'standard')}",
        ],
    }


KNOWN_SENSITIVE_DEPENDENCIES = {
    "pymupdf": "Dual-licensed under AGPL-3.0 and Artifex commercial terms. Poses strong copyleft/reciprocal risk for commercial applications.",
    "fitz": "PyMuPDF alias. Dual-licensed under AGPL-3.0 and Artifex commercial terms.",
    "redis": "Redis >= 7.4 is dual-licensed under RSALv2 / SSPL (source-available, non-OSI).",
}


def parse_requirements_txt(content: str) -> Dict[str, Any]:
    """Parse pip requirements.txt file extracting packages, constraints, and git URLs."""
    sanitized, _ = sanitize_untrusted_text(content)
    packages = []
    git_dependencies = []
    license_warnings = []

    for line in sanitized.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-r", "-f", "-i", "--")):
            continue
        if "git+" in line or "http://" in line or "https://" in line:
            git_dependencies.append(line)
            continue

        # Match package name and specifier
        m = re.match(r"^([A-Za-z0-9_.\-]+)\s*([<>=!~].*)?$", line)
        if m:
            pkg_name = m.group(1)
            constraint = m.group(2).strip() if m.group(2) else "unconstrained"
            packages.append({"package": pkg_name, "constraint": constraint})
            pkg_lower = pkg_name.lower().replace("-", "_")
            if pkg_lower in KNOWN_SENSITIVE_DEPENDENCIES:
                license_warnings.append(f"⚠️ High-Risk License Dependency: '{pkg_name}' — {KNOWN_SENSITIVE_DEPENDENCIES[pkg_lower]}")
        else:
            packages.append({"package": line, "constraint": "raw"})

    considerations = [
        f"Parsed {len(packages)} dependencies",
        f"Git-pinned dependencies detected: {len(git_dependencies)}",
    ]
    considerations.extend(license_warnings)

    return {
        "manifest_type": "requirements.txt",
        "total_packages": len(packages),
        "packages": packages,
        "git_dependencies": git_dependencies,
        "integration_considerations": considerations,
    }


def parse_cargo_toml(content: str) -> Dict[str, Any]:
    """Parse Rust Cargo.toml manifest extracting edition, dependencies, and version."""
    sanitized, _ = sanitize_untrusted_text(content)
    if tomllib:
        try:
            parsed = tomllib.loads(sanitized)
        except Exception as e:
            return {"error": f"Failed to parse Cargo.toml: {str(e)}", "manifest_type": "Cargo.toml"}
    else:
        parsed = _minimal_toml_fallback(sanitized)

    package = parsed.get("package", {})
    deps = parsed.get("dependencies", {})
    dep_list = []
    for k, v in deps.items():
        if isinstance(v, str):
            dep_list.append({"crate": k, "version": v})
        elif isinstance(v, dict):
            dep_list.append({"crate": k, "version": v.get("version", "path/git")})

    return {
        "manifest_type": "Cargo.toml",
        "name": package.get("name", "unnamed"),
        "version": package.get("version", "0.0.0"),
        "edition": package.get("edition", "2021"),
        "dependencies": dep_list,
        "integration_considerations": [
            f"Rust Edition: {package.get('edition', '2021')}",
            f"Total Crate Dependencies: {len(dep_list)}",
        ],
    }


def _strip_toml_comment(line: str) -> str:
    """Strip comments not enclosed in quotes."""
    in_single = False
    in_double = False
    for i, ch in enumerate(line):
        if ch == '"' and not in_single:
            if i == 0 or line[i - 1] != '\\':
                in_double = not in_double
        elif ch == "'" and not in_double:
            if i == 0 or line[i - 1] != '\\':
                in_single = not in_single
        elif ch == '#' and not in_single and not in_double:
            return line[:i].strip()
    return line.strip()


def _split_top_level(text: str, delimiter: str = ",") -> List[str]:
    """Split text by delimiter only at the top level (outside quotes, brackets, and braces)."""
    parts = []
    curr: List[str] = []
    in_single = False
    in_double = False
    bracket_depth = 0
    brace_depth = 0

    for i, ch in enumerate(text):
        if ch == '"' and not in_single:
            if i == 0 or text[i - 1] != '\\':
                in_double = not in_double
            curr.append(ch)
        elif ch == "'" and not in_double:
            if i == 0 or text[i - 1] != '\\':
                in_single = not in_single
            curr.append(ch)
        elif not in_single and not in_double:
            if ch == '[':
                bracket_depth += 1
                curr.append(ch)
            elif ch == ']':
                bracket_depth -= 1
                curr.append(ch)
            elif ch == '{':
                brace_depth += 1
                curr.append(ch)
            elif ch == '}':
                brace_depth -= 1
                curr.append(ch)
            elif ch == delimiter and bracket_depth == 0 and brace_depth == 0:
                parts.append("".join(curr).strip())
                curr = []
            else:
                curr.append(ch)
        else:
            curr.append(ch)

    if curr:
        remainder = "".join(curr).strip()
        if remainder:
            parts.append(remainder)
    return parts


def _parse_toml_value(val_str: str) -> Any:
    """Parse scalar, inline array, or inline table TOML value."""
    val_str = val_str.strip()
    if not val_str:
        return ""
    if val_str.startswith('"') and val_str.endswith('"') and len(val_str) >= 2:
        return val_str[1:-1]
    if val_str.startswith("'") and val_str.endswith("'") and len(val_str) >= 2:
        return val_str[1:-1]
    if val_str.lower() == "true":
        return True
    if val_str.lower() == "false":
        return False
    if val_str.startswith("{") and val_str.endswith("}"):
        inner = val_str[1:-1].strip()
        table: Dict[str, Any] = {}
        if inner:
            for part in _split_top_level(inner, ","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    table[k.strip().strip('"\'')] = _parse_toml_value(v.strip())
        return table
    if val_str.startswith("[") and val_str.endswith("]"):
        inner = val_str[1:-1].strip()
        items: List[Any] = []
        if inner:
            for part in _split_top_level(inner, ","):
                if part:
                    items.append(_parse_toml_value(part))
        return items
    try:
        return int(val_str)
    except ValueError:
        try:
            return float(val_str)
        except ValueError:
            return val_str


def _minimal_toml_fallback(content: str) -> Dict[str, Any]:
    """
    Robust pure standard-library TOML parser fallback for Python < 3.11.
    Parses sections, multiline arrays, inline tables, booleans, and scalar values.
    """
    result: Dict[str, Any] = {}
    current_section = result

    lines = []
    buffer = ""
    bracket_depth = 0
    brace_depth = 0
    in_single = False
    in_double = False

    for raw_line in content.splitlines():
        line = _strip_toml_comment(raw_line)
        if not buffer and not line:
            continue

        for i, ch in enumerate(line):
            if ch == '"' and not in_single:
                if i == 0 or line[i - 1] != '\\':
                    in_double = not in_double
            elif ch == "'" and not in_double:
                if i == 0 or line[i - 1] != '\\':
                    in_single = not in_single
            elif not in_single and not in_double:
                if ch == '[':
                    bracket_depth += 1
                elif ch == ']':
                    bracket_depth -= 1
                elif ch == '{':
                    brace_depth += 1
                elif ch == '}':
                    brace_depth -= 1

        if buffer:
            buffer += " " + line
        else:
            buffer = line

        if bracket_depth <= 0 and brace_depth <= 0:
            lines.append(buffer)
            buffer = ""
            bracket_depth = 0
            brace_depth = 0

    if buffer:
        lines.append(buffer)

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            sec_name = line[1:-1].strip()
            parts = sec_name.split(".")
            target = result
            for p in parts:
                p = p.strip().strip('"\'')
                if p not in target or not isinstance(target[p], dict):
                    target[p] = {}
                target = target[p]
            current_section = target
            continue

        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip().strip('"\'')
            current_section[k] = _parse_toml_value(v)

    return result


# ==============================================================================
# 3. NUANCED LICENSE CLASSIFIER & PROVENANCE AUDITOR
# ==============================================================================

def analyze_license_text(
    license_text: str,
    declared_spdx: Optional[str] = None,
    source_url: str = "",
) -> Dict[str, Any]:
    """
    Detailed license analysis examining actual text for grants, BSL conditions,
    and contextual obligations (SaaS vs distributed client binary).
    """
    sanitized, _ = sanitize_untrusted_text(license_text)
    clean_upper = sanitized.upper()

    result: Dict[str, Any] = {
        "source_url": source_url,
        "declared_spdx": declared_spdx or "UNKNOWN",
        "detected_category": "UNKNOWN",
        "is_osi_approved": False,
        "copyleft_tier": "NONE",
        "bsl_grant_details": None,
        "contextual_obligations": {},
        "disclaimer": LEGAL_DISCLAIMER,
    }

    # 1. Detect Business Source License (BSL-1.1)
    if "BUSINESS SOURCE LICENSE" in clean_upper or "BSL-1.1" in (declared_spdx or ""):
        result["detected_category"] = "SOURCE_AVAILABLE_COMMERCIAL_RESTRICTED"
        result["is_osi_approved"] = False
        result["copyleft_tier"] = "CUSTOM_CONDITIONAL"
        
        # Extract BSL specific fields
        licensor_m = re.search(r"Licensor:\s*([^\n\r]+)", sanitized, re.IGNORECASE)
        work_m = re.search(r"Licensed Work:\s*([^\n\r]+)", sanitized, re.IGNORECASE)
        grant_m = re.search(r"Additional Use Grant:\s*([\s\S]+?)(?:Change Date:|Change License:|$)[\n\r]", sanitized, re.IGNORECASE)
        change_date_m = re.search(r"Change Date:\s*([^\n\r]+)", sanitized, re.IGNORECASE)
        change_lic_m = re.search(r"Change License:\s*([^\n\r]+)", sanitized, re.IGNORECASE)

        result["bsl_grant_details"] = {
            "licensor": licensor_m.group(1).strip() if licensor_m else "Unspecified",
            "licensed_work": work_m.group(1).strip() if work_m else "Unspecified",
            "additional_use_grant": grant_m.group(1).strip() if grant_m else "Unspecified",
            "change_date": change_date_m.group(1).strip() if change_date_m else "Unspecified",
            "change_license": change_lic_m.group(1).strip() if change_lic_m else "Unspecified",
        }
        result["contextual_obligations"] = {
            "private_internal_use": "Permitted under standard BSL terms if not providing competing service.",
            "commercial_saas": "PROHIBITED if violating the Additional Use Grant (competing service).",
            "distributed_binaries": "Subject to licensor restrictions and change date.",
        }
        return result

    # 2. Strong / Network Copyleft (AGPL / SSPL / GPL)
    if "AFFERO GENERAL PUBLIC LICENSE" in clean_upper or declared_spdx in ("AGPL-3.0", "AGPL-3.0-only", "AGPL-3.0-or-later"):
        result["detected_category"] = "NETWORK_RECIPROCAL"
        result["is_osi_approved"] = True
        result["copyleft_tier"] = "STRONG_NETWORK"
        result["contextual_obligations"] = {
            "private_internal_use": "Permitted without disclosure.",
            "commercial_saas": "RECIPROCAL OBLIGATION: Must disclose complete source code to all network users.",
            "distributed_binaries": "Reciprocal source disclosure required under AGPL.",
        }
        return result

    if "GNU GENERAL PUBLIC LICENSE" in clean_upper and "LESSER" not in clean_upper:
        result["detected_category"] = "RECIPROCAL_ON_DISTRIBUTION"
        result["is_osi_approved"] = True
        result["copyleft_tier"] = "STRONG_COPYLEFT"
        result["contextual_obligations"] = {
            "private_internal_use": "Permitted without disclosure.",
            "commercial_saas": "Permitted without source disclosure (GPL does not trigger on pure network access).",
            "distributed_binaries": "RECIPROCAL OBLIGATION: Distributing client binaries requires releasing full source under GPL.",
        }
        return result

    # 3. Weak Copyleft (LGPL / MPL)
    if "LESSER GENERAL PUBLIC LICENSE" in clean_upper or "MOZILLA PUBLIC LICENSE" in clean_upper or declared_spdx in ("LGPL-2.1", "LGPL-3.0", "MPL-2.0"):
        result["detected_category"] = "WEAK_COPYLEFT"
        result["is_osi_approved"] = True
        result["copyleft_tier"] = "FILE_LEVEL_RECIPROCAL"
        result["contextual_obligations"] = {
            "private_internal_use": "Permitted.",
            "commercial_saas": "Permitted. Modifications to library files must be released, but host app is not infected.",
            "distributed_binaries": "Permitted when dynamically linked or library files kept modular.",
        }
        return result

    # 4. Permissive (MIT, Apache, BSD, ISC)
    if any(k in clean_upper for k in ("MIT LICENSE", "APACHE LICENSE", "BSD 2-CLAUSE", "BSD 3-CLAUSE", "ISC LICENSE")) or declared_spdx in ("MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC"):
        result["detected_category"] = "PERMISSIVE"
        result["is_osi_approved"] = True
        result["copyleft_tier"] = "NONE"
        result["contextual_obligations"] = {
            "private_internal_use": "Permitted with copyright attribution.",
            "commercial_saas": "Permitted without source disclosure.",
            "distributed_binaries": "Permitted with original license notice retained.",
        }
        return result

    # 5. Fallback for unclassified or missing licenses
    result["detected_category"] = "AMBIGUOUS_OR_UNCLASSIFIED"
    result["copyleft_tier"] = "UNKNOWN"
    result["contextual_obligations"] = {
        "assessment": "No standard license text recognized. Default international copyright applies (All Rights Reserved)."
    }
    return result


# ==============================================================================
# 4. EVIDENCE-BACKED REUSE RECOMMENDATION ENGINE
# ==============================================================================

def evaluate_reuse_posture(
    repo_slug: str,
    source_analysis: Optional[Dict[str, Any]] = None,
    manifest_analysis: Optional[Dict[str, Any]] = None,
    license_analysis: Optional[Dict[str, Any]] = None,
    maintenance_status: str = "ACTIVE",
    target_role: str = "core_component",
) -> Dict[str, Any]:
    """
    Synthesize static symbols, manifest constraints, and license realities
    into an evidence-backed architectural reuse recommendation.
    """
    rec_type = "INVESTIGATE_FURTHER"
    rationale = []
    risks = []
    suggested_tests = []
    effort = "MODERATE"

    lic_cat = (license_analysis or {}).get("detected_category", "UNKNOWN")
    copyleft = (license_analysis or {}).get("copyleft_tier", "NONE")

    # Legal gating
    if lic_cat == "SOURCE_AVAILABLE_COMMERCIAL_RESTRICTED":
        rec_type = "REJECT_OR_RESTRICT"
        rationale.append("Source-available license (e.g. BSL-1.1) carries commercial competition restrictions.")
        risks.append("Violation of Additional Use Grant could trigger copyright infringement liabilities.")
        effort = "HIGH"
        return {
            "candidate_repo": repo_slug,
            "recommendation": rec_type,
            "effort": effort,
            "rationale": " ".join(rationale),
            "risks": risks,
            "suggested_tests": ["Legal counsel audit of Additional Use Grant"],
        }

    if copyleft == "STRONG_NETWORK":
        rationale.append("Network-reciprocal license (AGPL) obligates public source disclosure for network services.")
        risks.append("Reciprocal copyleft infection across application backend.")
        rec_type = "FORK_UNDER_APPLICABLE_LICENSE" if maintenance_status == "DORMANT" else "INTEGRATE_THROUGH_API"
        effort = "HIGH"

    # Maintenance gating
    is_dormant = maintenance_status in ("DORMANT", "ARCHIVED", "SLOWING")
    if is_dormant:
        rationale.append(f"Repository is {maintenance_status}; direct dependency adoption risks unpatched bugs.")
        if lic_cat == "PERMISSIVE":
            rec_type = "EXTRACT_SPECIFIC_COMPONENT"
            rationale.append("Permissive license permits extracting isolated algorithms without adopting the dormant framework.")
            effort = "LOW_TO_MODERATE"
            suggested_tests.append("Isolate algorithm into standalone unit tests with mock inputs.")
        else:
            rec_type = "REIMPLEMENT_ALGORITHM"
            rationale.append("Copyleft or complex architecture makes extraction risky; reimplement concept natively.")
            effort = "MODERATE"

    # Active & Permissive / Weak Copyleft
    elif lic_cat in ("PERMISSIVE", "WEAK_COPYLEFT"):
        manifest_type = (manifest_analysis or {}).get("manifest_type")
        if manifest_type in ("package.json", "pyproject.toml", "Cargo.toml"):
            rec_type = "ADOPT_AS_DEPENDENCY"
            rationale.append("Actively maintained, permissively licensed modular library with standard package manifest.")
            effort = "LOW"
            suggested_tests.append("Import library into clean virtual environment; run basic integration smoke test.")
        else:
            rec_type = "INTEGRATE_THROUGH_API"
            rationale.append("Full application workspace rather than packaged library; integrate via REST/WebSocket boundaries.")
            effort = "MODERATE"
            suggested_tests.append("Construct mock API contract test verifying message serialization.")

    return {
        "candidate_repo": repo_slug,
        "recommendation": rec_type,
        "effort": effort,
        "rationale": " ".join(rationale) if rationale else "Clearance and modularity verified.",
        "risks": risks or ["Upstream API evolution breaking integration"],
        "suggested_tests": suggested_tests or ["Unit test covering target interface"],
    }


# ==============================================================================
# 5. REMOTE RETRIEVAL & REPORT GENERATOR
# ==============================================================================

def fetch_raw_github_file(owner: str, repo: str, file_path: str, revision: str = "HEAD") -> Tuple[int, str]:
    """Fetch raw file content from raw.githubusercontent.com CDN (zero API quota consumption)."""
    clean_path = file_path.strip().lstrip("/")
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{revision}/{clean_path}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            return resp.status, content
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)


def format_integration_report(analysis: Dict[str, Any]) -> str:
    """Render structured human-readable Markdown report of the integration analysis."""
    lines = []
    repo = analysis.get("repository", "Unknown Repository")
    rev = analysis.get("revision", "HEAD")
    lines.append(f"# BeenHere Integration Analysis: `{repo}` (rev `{rev}`)")
    lines.append("")

    # 1. License & Legal
    lic = analysis.get("license_analysis", {})
    lines.append("## 1. License Evidence & Risk Tier")
    lines.append(f"- **Declared SPDX:** `{lic.get('declared_spdx', 'UNKNOWN')}`")
    lines.append(f"- **Detected Category:** `{lic.get('detected_category', 'UNKNOWN')}`")
    lines.append(f"- **Copyleft Tier:** `{lic.get('copyleft_tier', 'NONE')}`")
    if lic.get("bsl_grant_details"):
        bsl = lic["bsl_grant_details"]
        lines.append("- **BSL Details:**")
        lines.append(f"  - *Licensor:* {bsl.get('licensor')}")
        lines.append(f"  - *Additional Use Grant:* {bsl.get('additional_use_grant')[:120]}...")
        lines.append(f"  - *Change Date:* {bsl.get('change_date')} -> `{bsl.get('change_license')}`")
    lines.append(f"> *{lic.get('disclaimer', LEGAL_DISCLAIMER)}*")
    lines.append("")

    # 2. Manifest & Dependencies
    manifest = analysis.get("manifest_analysis")
    if manifest and not manifest.get("error"):
        lines.append("## 2. Dependency Manifest & Runtime Requirements")
        lines.append(f"- **Manifest Type:** `{manifest.get('manifest_type')}`")
        if "dependencies" in manifest:
            deps = manifest["dependencies"]
            lines.append(f"- **Declared Dependencies ({len(deps)}):**")
            if isinstance(deps, dict):
                for k, v in list(deps.items())[:8]:
                    lines.append(f"  - `{k}`: `{v}`")
            elif isinstance(deps, list):
                for item in deps[:8]:
                    lines.append(f"  - `{item}`")
        if manifest.get("integration_considerations"):
            for c in manifest["integration_considerations"]:
                lines.append(f"- ℹ️ {c}")
        lines.append("")

    # 3. Static Symbols & Public Interfaces
    src = analysis.get("source_analysis")
    if src:
        lines.append("## 3. Discovered Interfaces & Exported Symbols")
        lines.append(f"- **File:** `{src.get('file_path')}` ({src.get('language')})")
        lines.append(f"- **Parser:** `{src.get('parser')}`")
        if src.get("classes"):
            lines.append("- **Classes:**")
            for c in src["classes"]:
                methods = [m["name"] for m in c.get("methods", [])]
                lines.append(f"  - `class {c['name']}` (L{c.get('line_start') or c.get('line')}) -> Methods: `{', '.join(methods[:4]) or 'none'}`")
        if src.get("functions"):
            lines.append("- **Exported Functions:**")
            for f in src["functions"]:
                lines.append(f"  - `{f['name']}({', '.join(f.get('args', []))})` (L{f.get('line_start') or f.get('line')})")
        if src.get("interfaces"):
            lines.append(f"- **TypeScript Interfaces:** `{', '.join([i['name'] for i in src['interfaces']])}`")
        if src.get("env_vars_detected"):
            lines.append(f"- **Environment Variables Required:** `{', '.join(src['env_vars_detected'])}`")
        lines.append(f"> *Limitations:* {src.get('limitations')}")
        lines.append("")

    # 4. Recommendation Posture
    rec = analysis.get("recommendation", {})
    lines.append("## 4. Architectural Reuse Posture")
    lines.append(f"- **Recommendation:** **`{rec.get('recommendation', 'INVESTIGATE_FURTHER')}`**")
    lines.append(f"- **Engineering Effort:** `{rec.get('effort', 'MODERATE')}`")
    lines.append(f"- **Rationale:** {rec.get('rationale')}")
    if rec.get("risks"):
        lines.append("- **Identified Risks:**")
        for r in rec["risks"]:
            lines.append(f"  - ⚠️ {r}")
    if rec.get("suggested_tests"):
        lines.append("- **Recommended Validation Tests:**")
        for t in rec["suggested_tests"]:
            lines.append(f"  - 🧪 {t}")
    lines.append("")

    return "\n".join(lines)


# ==============================================================================
# 6. CLI INTERFACE
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="BeenHere Deep Code-Reusability & Integration Point Analyzer"
    )
    parser.add_argument("--repo", "-r", help="Repository slug (owner/repo)")
    parser.add_argument("--source-file", "-s", help="Specific source file to inspect (e.g. src/pipeline.py)")
    parser.add_argument("--manifest-file", "-m", help="Manifest to parse (e.g. package.json, pyproject.toml)")
    parser.add_argument("--license-file", "-l", help="License file to inspect (e.g. LICENSE, LICENSE.md)")
    parser.add_argument("--local-file", help="Path to local file for offline inspection")
    parser.add_argument("--json", action="store_true", help="Output raw JSON data")
    parser.add_argument("--output", "-o", help="Save markdown report to path")

    args = parser.parse_args()

    # Offline local inspection
    if args.local_file:
        if not os.path.exists(args.local_file):
            print(f"Error: Local file '{args.local_file}' does not exist.", file=sys.stderr)
            sys.exit(1)
        with open(args.local_file, "r", encoding="utf-8", errors="replace") as f:
            code = f.read()

        basename = os.path.basename(args.local_file)
        if basename.endswith(".py"):
            res = parse_python_source(code, file_path=args.local_file)
        elif basename.endswith((".js", ".ts", ".jsx", ".tsx")):
            res = parse_js_ts_source(code, file_path=args.local_file)
        elif basename == "package.json":
            res = parse_package_json(code)
        elif basename == "pyproject.toml":
            res = parse_pyproject_toml(code)
        elif basename == "requirements.txt":
            res = parse_requirements_txt(code)
        elif basename == "Cargo.toml":
            res = parse_cargo_toml(code)
        elif "LICENSE" in basename.upper():
            res = analyze_license_text(code, source_url=args.local_file)
        else:
            res = {"file": args.local_file, "size_bytes": len(code)}

        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(json.dumps(res, indent=2))
        return

    # Remote GitHub Inspection
    if not args.repo:
        parser.print_help()
        sys.exit(1)

    parts = args.repo.strip().rstrip("/").split("github.com/")[-1].split("/")
    if len(parts) < 2:
        print(f"Error: Invalid repo slug '{args.repo}'. Expected 'owner/repo'.", file=sys.stderr)
        sys.exit(1)
    owner, repo = parts[0], parts[1]

    analysis: Dict[str, Any] = {
        "repository": f"{owner}/{repo}",
        "revision": "HEAD",
    }

    # License analysis
    lic_file = args.license_file or "LICENSE"
    l_status, l_text = fetch_raw_github_file(owner, repo, lic_file)
    if l_status == 200:
        analysis["license_analysis"] = analyze_license_text(
            l_text,
            source_url=f"https://github.com/{owner}/{repo}/blob/HEAD/{lic_file}"
        )
    else:
        # Fallback to LICENSE.md
        l_status, l_text = fetch_raw_github_file(owner, repo, "LICENSE.md")
        if l_status == 200:
            analysis["license_analysis"] = analyze_license_text(
                l_text,
                source_url=f"https://github.com/{owner}/{repo}/blob/HEAD/LICENSE.md"
            )

    # Manifest analysis
    manifest_name = args.manifest_file
    if not manifest_name:
        for candidate in ["package.json", "pyproject.toml", "requirements.txt", "Cargo.toml"]:
            m_status, m_content = fetch_raw_github_file(owner, repo, candidate)
            if m_status == 200:
                manifest_name = candidate
                break
    else:
        m_status, m_content = fetch_raw_github_file(owner, repo, manifest_name)

    if manifest_name and m_status == 200:
        if manifest_name == "package.json":
            analysis["manifest_analysis"] = parse_package_json(m_content)
        elif manifest_name == "pyproject.toml":
            analysis["manifest_analysis"] = parse_pyproject_toml(m_content)
        elif manifest_name == "requirements.txt":
            analysis["manifest_analysis"] = parse_requirements_txt(m_content)
        elif manifest_name == "Cargo.toml":
            analysis["manifest_analysis"] = parse_cargo_toml(m_content)

    # Source code analysis
    if args.source_file:
        s_status, s_code = fetch_raw_github_file(owner, repo, args.source_file)
        if s_status == 200:
            if args.source_file.endswith(".py"):
                analysis["source_analysis"] = parse_python_source(s_code, file_path=args.source_file)
            elif args.source_file.endswith((".js", ".ts", ".jsx", ".tsx")):
                analysis["source_analysis"] = parse_js_ts_source(s_code, file_path=args.source_file)
        else:
            analysis["source_error"] = f"Failed to fetch '{args.source_file}' (HTTP {s_status})"

    # Generate recommendation posture
    analysis["recommendation"] = evaluate_reuse_posture(
        repo_slug=f"{owner}/{repo}",
        source_analysis=analysis.get("source_analysis"),
        manifest_analysis=analysis.get("manifest_analysis"),
        license_analysis=analysis.get("license_analysis"),
        maintenance_status="ACTIVE",
    )

    if args.json:
        output_str = json.dumps(analysis, indent=2)
    else:
        output_str = format_integration_report(analysis)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"Report written to: {args.output}")
    else:
        print(output_str)


if __name__ == "__main__":
    main()
