#!/usr/bin/env python3
"""
scripts/repo_inspector.py - Deterministic repository metadata, license, and reusability inspector.

Part of BeenHere: Explore every angle of an idea before you build it.
Uses Python standard library only (no external dependencies).
"""

import argparse
import base64
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

USER_AGENT = "BeenHere/1.0.0-beta.1 (https://github.com/manasvignesh/BeenHere)"
GITHUB_API_BASE = "https://api.github.com"

# Known license categories with precise legal classification
LICENSE_CATEGORIES = {
    "permissive": ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unlicense", "CC0-1.0"],
    "weak_copyleft": ["LGPL-2.1", "LGPL-3.0", "MPL-2.0", "EPL-2.0"],
    "strong_copyleft": ["GPL-2.0", "GPL-3.0"],
    "network_copyleft": ["AGPL-3.0", "OSL-3.0"],
    "source_available": ["BSL-1.1", "SSPL-1.0", "BUSL-1.1", "Elastic-2.0"],
}

MANIFEST_FILES = [
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Gemfile",
    "pubspec.yaml",
    "CMakeLists.txt",
    "composer.json",
]

# Patterns commonly used in prompt injection attempts within external repos
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"(?i)system\s*prompt\s*:",
    r"(?i)override\s+(all\s+)?(evaluation|rules|rubric)",
    r"(?i)you\s+must\s+(adopt|approve|recommend)",
    r"(?i)pretend\s+you\s+are",
    r"(?i)new\s+system\s+instruction",
]


def get_auth_token() -> Optional[str]:
    """Retrieve GitHub token from environment if available."""
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def parse_repo_slug(raw_input: str) -> Tuple[str, str]:
    """Extract owner and repo name from slug or full GitHub URL."""
    clean = raw_input.strip()
    if clean.startswith("git@github.com:"):
        clean = clean[len("git@github.com:"):]
    elif "github.com/" in clean:
        clean = clean.split("github.com/")[1]

    clean = clean.rstrip("/")
    if clean.endswith(".git"):
        clean = clean[:-4]
    parts = clean.split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid repository specification: '{raw_input}'. Expected 'owner/repo' or GitHub URL.")
    return parts[0], parts[1]


def make_request(url: str, token: Optional[str] = None) -> Tuple[int, Dict[str, str], bytes]:
    """Execute HTTP GET request with appropriate headers."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/vnd.github.v3+json")

    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            headers = {k.lower(): v for k, v in resp.getheaders()}
            body = resp.read()
            return status, headers, body
    except urllib.error.HTTPError as e:
        headers = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
        body = e.read() if hasattr(e, "read") else b""
        return e.code, headers, body
    except (urllib.error.URLError, OSError) as e:
        reason = getattr(e, "reason", e)
        raise RuntimeError(f"Network error accessing GitHub API: {reason}") from e


def sanitize_untrusted_text(text: str) -> Tuple[str, bool]:
    """
    Sanitize external untrusted text to prevent prompt injection and markdown breakout.
    Returns (sanitized_text, injection_detected).
    """
    if not text:
        return "", False

    injection_detected = False
    sanitized = text

    for pat in INJECTION_PATTERNS:
        if re.search(pat, sanitized):
            injection_detected = True
            sanitized = re.sub(pat, "[BLOCKED_INJECTION_PATTERN]", sanitized)

    # Disarm markdown triple backtick fences that try to escape code blocks
    sanitized = sanitized.replace("```", "'''")

    return sanitized, injection_detected


def categorize_license(spdx_id: Optional[str]) -> Tuple[str, str, str]:
    """
    Categorize license into (category, clearance_tier, rationale).
    Accurately distinguishes commercial use permissions from reciprocal obligations.
    Returns (category, clearance, rationale).
    """
    if not spdx_id or spdx_id in ("NOASSERTION", "NONE", "Unknown"):
        return (
            "unresolved",
            "CRITICAL_BLOCKER",
            "No recognized open-source license detected. Under international copyright law, All Rights Reserved applies by default. Reusing, copying, or distributing this code without an explicit written license from the copyright holder is copyright infringement.",
        )

    for cat, spdx_list in LICENSE_CATEGORIES.items():
        if spdx_id in spdx_list:
            if cat == "permissive":
                return (
                    "permissive",
                    "CLEAR",
                    f"Permissive license ({spdx_id}). Grants broad commercial and non-commercial rights to adopt, modify, integrate, sublicense, and distribute without reciprocal source code disclosure obligations. Retain original copyright and license notice.",
                )
            elif cat == "weak_copyleft":
                return (
                    "weak_copyleft",
                    "CONDITIONAL_RECIPROCAL",
                    f"Weak copyleft license ({spdx_id}). Commercial use is permitted. Modifications to the library's own files must be shared under {spdx_id}, but dynamic linking, importing as an external dependency, or combining with separate proprietary modules does not infect the broader application.",
                )
            elif cat == "strong_copyleft":
                return (
                    "strong_copyleft",
                    "RECIPROCAL_ON_DISTRIBUTION",
                    f"Reciprocal copyleft license ({spdx_id}). Commercial use, internal company deployment, and SaaS/network hosting are permitted without triggering source disclosure. However, if the software or derivative works are distributed as compiled binaries or distributed software, complete corresponding source code must be made available under the same GPL terms.",
                )
            elif cat == "network_copyleft":
                return (
                    "network_copyleft",
                    "NETWORK_RECIPROCAL",
                    f"Network-triggered copyleft license ({spdx_id}). Commercial use is permitted, but interacting with the software remotely over a computer network (e.g. SaaS/web service) legally triggers the obligation to make the complete corresponding source code of the entire service available to all network users.",
                )
            elif cat == "source_available":
                return (
                    "source_available",
                    "COMMERCIAL_RESTRICTED",
                    f"Source-available license ({spdx_id}). Not OSI-approved open source. Specifically restricts commercial production deployment, managed hosting, or competitive service provision.",
                )

    return (
        "custom_or_other",
        "INVESTIGATE",
        f"Custom or non-standard license detected ({spdx_id}). Requires manual legal review of license text.",
    )


def compute_maintenance_signals(repo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate maintenance vitals based on repository timestamps and state."""
    pushed_at_str = repo_data.get("pushed_at")

    now = datetime.datetime.now(datetime.timezone.utc)
    days_since_push = None
    if pushed_at_str:
        try:
            pushed_dt = datetime.datetime.fromisoformat(pushed_at_str.replace("Z", "+00:00"))
            days_since_push = max(0, (now - pushed_dt).days)
        except Exception:
            pass

    is_archived = repo_data.get("archived", False)

    if is_archived:
        status = "ARCHIVED"
        recommendation = "Repository is officially archived (read-only). Upstream is defunct; reuse requires independent forking or code extraction."
    elif days_since_push is not None and days_since_push <= 60:
        status = "ACTIVE"
        recommendation = "Actively maintained (commits within last 60 days). Healthy upstream candidate for adoption or extension."
    elif days_since_push is not None and days_since_push <= 180:
        status = "MAINTAINED"
        recommendation = "Regularly maintained (commits within last 6 months)."
    elif days_since_push is not None and days_since_push <= 365:
        status = "SLOWING"
        recommendation = "Maintenance slowing (last push 6-12 months ago). Check issue response velocity before deep dependency adoption."
    else:
        status = "DORMANT"
        recommendation = f"Dormant or unmaintained (last push {days_since_push} days ago). High risk of unpatched vulnerabilities and bit rot. Recommend extraction of specific algorithms rather than direct dependency."

    return {
        "status": status,
        "days_since_last_push": days_since_push,
        "is_archived": is_archived,
        "is_fork": repo_data.get("fork", False),
        "open_issues_count": repo_data.get("open_issues_count", 0),
        "recommendation": recommendation,
    }


def inspect_repository(
    owner: str,
    repo: str,
    source_paths: Optional[List[str]] = None,
    token: Optional[str] = None,
    mock_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Programmatically inspect repository metadata, languages, license, manifest files,
    and optionally inspect specific implementation source files.
    """
    inspected_sources = []
    injection_warnings = []

    if mock_data is not None:
        repo_data = mock_data.get("repo", {})
        languages = mock_data.get("languages", {})
        root_files = mock_data.get("root_files", [])
        readme_snippet = mock_data.get("readme_snippet", "")
        mock_source_files = mock_data.get("source_files", {})
        if source_paths:
            for sp in source_paths:
                if sp in mock_source_files:
                    inspected_sources.append(mock_source_files[sp])
    else:
        # 1. Fetch main repo metadata
        repo_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        status = 0
        repo_data = None
        try:
            status, headers, body = make_request(repo_url, token=token)
            if status == 200:
                repo_data = json.loads(body.decode("utf-8", errors="replace"))
            elif status == 403:
                # Fallback to GitHub Search API which operates under a separate rate limit bucket
                search_url = f"{GITHUB_API_BASE}/search/repositories?q=repo:{owner}/{repo}"
                try:
                    s_status, _, s_body = make_request(search_url, token=token)
                    if s_status == 200:
                        s_data = json.loads(s_body.decode("utf-8", errors="replace"))
                        if s_data.get("items"):
                            repo_data = s_data["items"][0]
                except Exception:
                    pass
        except Exception as e:
            is_sock = any(k in str(e).lower() for k in ("10013", "wsaeacces", "eacces", "access permissions", "permission denied"))
            fallback = (
                "Subprocess network socket access was denied ([WinError 10013]/WSAEACCES). "
                "Host AI agent: please use your native tools (e.g. host WebSearch, gh repo view, or native fetch) "
                "to inspect this repository directly."
                if is_sock else
                f"Network error retrieving repository '{owner}/{repo}': {e}. Host agent: please fall back to native tools."
            )
            return {
                "error": f"Failed to retrieve repository '{owner}/{repo}': {e}",
                "status_code": 0,
                "fallback_recommendation": fallback,
            }

        if not repo_data:
            return {
                "error": f"Failed to retrieve repository '{owner}/{repo}' (HTTP {status})",
                "status_code": status,
            }

        # 2. Fetch languages breakdown
        languages = {}
        lang_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
        try:
            l_status, _, l_body = make_request(lang_url, token=token)
            if l_status == 200:
                languages = json.loads(l_body.decode("utf-8", errors="replace"))
        except Exception:
            pass

        if not languages and repo_data.get("language"):
            languages = {repo_data["language"]: 10000}

        # 3. Check root contents for manifests
        root_files = []
        contents_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents"
        try:
            c_status, _, c_body = make_request(contents_url, token=token)
            if c_status == 200:
                c_json = json.loads(c_body.decode("utf-8", errors="replace"))
                if isinstance(c_json, list):
                    root_files = [f.get("name") for f in c_json if f.get("name")]
        except Exception:
            pass

        if not root_files:
            common_manifests = ["package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "Gemfile"]
            for m in common_manifests:
                try:
                    m_req = urllib.request.Request(f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{m}", method="HEAD")
                    m_req.add_header("User-Agent", USER_AGENT)
                    with urllib.request.urlopen(m_req, timeout=5) as m_resp:
                        if m_resp.status == 200:
                            root_files.append(m)
                except Exception:
                    pass

        # 4. Fetch README snippet
        readme_snippet = ""
        readme_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
        try:
            r_status, _, r_body = make_request(readme_url, token=token)
            if r_status == 200:
                r_json = json.loads(r_body.decode("utf-8", errors="replace"))
                content_b64 = r_json.get("content", "")
                if content_b64:
                    raw_readme = base64.b64decode(content_b64).decode("utf-8", errors="replace")
                    sanitized_readme, injected = sanitize_untrusted_text(raw_readme)
                    if injected:
                        injection_warnings.append("README contained potential prompt injection patterns that were neutralized.")
                    lines = [ln.strip() for ln in sanitized_readme.splitlines() if ln.strip() and not ln.startswith("[!")]
                    readme_snippet = "\n".join(lines[:15])
        except Exception:
            pass

        if not readme_snippet:
            try:
                r_req = urllib.request.Request(f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/README.md")
                r_req.add_header("User-Agent", USER_AGENT)
                with urllib.request.urlopen(r_req, timeout=5) as r_resp:
                    if r_resp.status == 200:
                        raw_readme = r_resp.read().decode("utf-8", errors="replace")
                        sanitized_readme, injected = sanitize_untrusted_text(raw_readme)
                        if injected:
                            injection_warnings.append("README contained potential prompt injection patterns that were neutralized.")
                        lines = [ln.strip() for ln in sanitized_readme.splitlines() if ln.strip() and not ln.startswith("[!")]
                        readme_snippet = "\n".join(lines[:15])
            except Exception:
                pass

        # 5. Fetch specific source files if requested
        if source_paths:
            for sp in source_paths:
                sp_clean = sp.strip().lstrip("/")
                f_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{sp_clean}"
                fetched = False
                try:
                    f_status, _, f_body = make_request(f_url, token=token)
                    if f_status == 200:
                        f_json = json.loads(f_body.decode("utf-8", errors="replace"))
                        if f_json.get("type") == "file" and f_json.get("content"):
                            decoded = base64.b64decode(f_json["content"]).decode("utf-8", errors="replace")
                            sanitized_src, src_inj = sanitize_untrusted_text(decoded)
                            if src_inj:
                                injection_warnings.append(f"Source file '{sp_clean}' contained potential prompt injection patterns.")

                            # Extract discovered imports
                            discovered_imports = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_\.]+)', decoded, re.MULTILINE)
                            inspected_sources.append({
                                "path": sp_clean,
                                "size_bytes": f_json.get("size", len(decoded)),
                                "lines_count": len(decoded.splitlines()),
                                "discovered_imports": sorted(list(set(discovered_imports)))[:10],
                                "sample_snippet": "\n".join(sanitized_src.splitlines()[:20]),
                            })
                            fetched = True
                except Exception:
                    pass

                if not fetched:
                    # Fallback to direct raw CDN fetch
                    try:
                        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{sp_clean}"
                        raw_req = urllib.request.Request(raw_url)
                        raw_req.add_header("User-Agent", USER_AGENT)
                        with urllib.request.urlopen(raw_req, timeout=8) as raw_resp:
                            if raw_resp.status == 200:
                                decoded = raw_resp.read().decode("utf-8", errors="replace")
                                sanitized_src, src_inj = sanitize_untrusted_text(decoded)
                                if src_inj:
                                    injection_warnings.append(f"Source file '{sp_clean}' contained potential prompt injection patterns.")

                                discovered_imports = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_\.]+)', decoded, re.MULTILINE)
                                inspected_sources.append({
                                    "path": sp_clean,
                                    "size_bytes": len(decoded.encode("utf-8")),
                                    "lines_count": len(decoded.splitlines()),
                                    "discovered_imports": sorted(list(set(discovered_imports)))[:10],
                                    "sample_snippet": "\n".join(sanitized_src.splitlines()[:20]),
                                })
                                fetched = True
                            else:
                                inspected_sources.append({
                                    "path": sp_clean,
                                    "error": f"Failed to fetch file (HTTP {raw_resp.status})",
                                })
                    except Exception as e:
                        inspected_sources.append({
                            "path": sp_clean,
                            "error": str(e),
                        })

    # Sanitize description
    raw_desc = repo_data.get("description") or ""
    sanitized_desc, desc_inj = sanitize_untrusted_text(raw_desc)
    if desc_inj:
        injection_warnings.append("Description contained prompt injection patterns that were neutralized.")

    # Process licenses
    lic_meta = repo_data.get("license") or {}
    spdx_id = lic_meta.get("spdx_id") or lic_meta.get("key")
    lic_name = lic_meta.get("name") or "None / Unspecified"
    cat, clearance, rationale = categorize_license(spdx_id)

    # Detect manifests
    detected_manifests = [m for m in MANIFEST_FILES if m in root_files]

    # Evaluate maintenance
    maint = compute_maintenance_signals(repo_data)

    # Architectural classification
    topics = repo_data.get("topics", [])
    primary_lang = repo_data.get("language") or "Unknown"

    total_bytes = sum(languages.values()) if languages else 0
    language_pcts = {
        lang: f"{(b / total_bytes * 100):.1f}%"
        for lang, b in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    } if total_bytes > 0 else {}

    # Modularity estimation
    modularity = "UNKNOWN"
    if "library" in topics or "framework" in topics or "sdk" in topics:
        modularity = "MODULAR_LIBRARY"
    elif "app" in topics or "platform" in topics or "bot" in topics or "ui" in topics:
        modularity = "FULL_APPLICATION"
    elif detected_manifests:
        modularity = "PROJECT_WORKSPACE"

    # Identify reuse blockers
    blockers = []
    if clearance in ("CRITICAL_BLOCKER", "COMMERCIAL_RESTRICTED"):
        blockers.append(f"Legal/License Risk: {rationale}")
    elif clearance == "NETWORK_RECIPROCAL":
        blockers.append(f"Network Copyleft Obligation (AGPL): Exposing service over network requires full source disclosure.")
    if maint["is_archived"]:
        blockers.append("Upstream is officially archived (read-only).")
    if maint["status"] == "DORMANT":
        blockers.append(f"Maintenance abandonment risk (inactive for {maint['days_since_last_push']} days).")

    # Accurate Verification Depth Reporting
    verification_depth = "SOURCE_CODE_INSPECTED" if inspected_sources else "METADATA_AND_MANIFESTS_ONLY"

    return {
        "status": "success",
        "repository": repo_data.get("full_name", f"{owner}/{repo}"),
        "html_url": repo_data.get("html_url", f"https://github.com/{owner}/{repo}"),
        "description": sanitized_desc,
        "verification_depth": verification_depth,
        "primary_language": primary_lang,
        "languages": language_pcts,
        "stargazers_count": repo_data.get("stargazers_count", 0),
        "forks_count": repo_data.get("forks_count", 0),
        "open_issues_count": repo_data.get("open_issues_count", 0),
        "created_at": repo_data.get("created_at"),
        "updated_at": repo_data.get("updated_at"),
        "pushed_at": repo_data.get("pushed_at"),
        "license": {
            "spdx_id": spdx_id,
            "name": lic_name,
            "category": cat,
            "clearance": clearance,
            "rationale": rationale,
        },
        "manifests_detected": detected_manifests,
        "modularity_estimate": modularity,
        "maintenance": maint,
        "reuse_blockers": blockers,
        "inspected_source_files": inspected_sources,
        "security_warnings": injection_warnings,
        "readme_excerpt": readme_snippet,
    }


def format_inspection_report(res: Dict[str, Any]) -> str:
    """Format repository inspection results into readable markdown."""
    if res.get("error"):
        msg = f"Inspection Error: {res['error']}"
        if res.get("fallback_recommendation"):
            msg += f"\n\n> [!WARNING] Subprocess Network Restriction:\n> {res['fallback_recommendation']}"
        return msg

    lic = res["license"]
    maint = res["maintenance"]

    lines = []
    lines.append(f"# Repository Inspection: {res['repository']}\n")
    lines.append(f"**URL:** {res['html_url']}")
    lines.append(f"**Description:** {res['description'] or 'None'}")
    lines.append(f"**Verification Depth:** `{res['verification_depth']}`")
    if res["verification_depth"] == "METADATA_AND_MANIFESTS_ONLY":
        lines.append("*(Note: Deep source code implementation has NOT been inspected; conclusions are based on official API metadata, manifests, and documentation claims).*")
    else:
        lines.append(f"*(Examined {len(res['inspected_source_files'])} specified source files directly).*")
    lines.append("")

    if res.get("security_warnings"):
        lines.append("## ⚠️ Security Notice (Untrusted External Data)")
        for w in res["security_warnings"]:
            lines.append(f"- 🛡️ {w}")
        lines.append("")

    lines.append("## 1. Legal & License Clearance")
    lines.append(f"- **SPDX ID:** `{lic['spdx_id']}` ({lic['name']})")
    lines.append(f"- **Category:** `{lic['category']}`")
    lines.append(f"- **Clearance Status:** **{lic['clearance']}**")
    lines.append(f"- **Legal Rationale:** {lic['rationale']}\n")

    lines.append("## 2. Technical Stack & Modularity")
    lines.append(f"- **Primary Language:** {res['primary_language']}")
    if res.get("languages"):
        lang_str = ", ".join(f"{k} ({v})" for k, v in res["languages"].items())
        lines.append(f"- **Language Breakdown:** {lang_str}")
    lines.append(f"- **Manifests Found:** {', '.join(res['manifests_detected']) if res['manifests_detected'] else 'None detected in root'}")
    lines.append(f"- **Modularity Classification:** `{res['modularity_estimate']}`\n")

    lines.append("## 3. Maintenance Vitals")
    lines.append(f"- **Stars:** {res['stargazers_count']:,} | **Forks:** {res['forks_count']:,} | **Open Issues:** {res['open_issues_count']:,}")
    lines.append(f"- **Status:** **{maint['status']}** (Last push: {maint.get('days_since_last_push', 'N/A')} days ago)")
    lines.append(f"- **Archived:** {'Yes (Read-Only)' if maint['is_archived'] else 'No'}")
    lines.append(f"- **Health Assessment:** {maint['recommendation']}\n")

    lines.append("## 4. Reusability Verdict & Blockers")
    if res.get("reuse_blockers"):
        lines.append("**Identified Blockers / Obligations:**")
        for b in res["reuse_blockers"]:
            lines.append(f"- ⚠️ {b}")
    else:
        lines.append("✅ **No critical legal blockers detected.** Permissive reuse allowed.")

    if res.get("inspected_source_files"):
        lines.append("\n## 5. Implementation Source Code Inspection")
        for src in res["inspected_source_files"]:
            if src.get("error"):
                lines.append(f"- `{src['path']}`: ❌ {src['error']}")
            else:
                lines.append(f"- `{src['path']}` ({src['lines_count']} lines, {src['size_bytes']} bytes)")
                if src.get("discovered_imports"):
                    lines.append(f"  - **Imports:** {', '.join(src['discovered_imports'])}")
                lines.append("  ```text")
                lines.append("  " + src["sample_snippet"][:300].replace("\n", "\n  "))
                lines.append("  ```")

    if res.get("readme_excerpt"):
        lines.append("\n## 6. README Excerpt (Untrusted External Content)")
        lines.append("<untrusted_external_content>")
        lines.append("'''markdown")
        lines.append(res["readme_excerpt"][:600] + ("..." if len(res["readme_excerpt"]) > 600 else ""))
        lines.append("'''")
        lines.append("</untrusted_external_content>")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Deterministic Repository Inspector for BeenHere")
    parser.add_argument("--repo", "-r", required=True, help="Repository slug (owner/repo) or GitHub URL")
    parser.add_argument("--inspect-files", "-i", nargs="+", help="Specific source files within repository to inspect")
    parser.add_argument("--json", action="store_true", help="Output raw structured JSON to stdout")
    parser.add_argument("--output", "-o", type=str, help="Save report to specified file path")

    args = parser.parse_args()

    try:
        owner, repo_name = parse_repo_slug(args.repo)
    except ValueError as e:
        sys.stderr.write(f"Argument error: {e}\n")
        sys.exit(1)

    token = get_auth_token()
    try:
        inspection = inspect_repository(
            owner=owner,
            repo=repo_name,
            source_paths=args.inspect_files,
            token=token,
        )
    except Exception as e:
        is_sock = any(k in str(e).lower() for k in ("10013", "wsaeacces", "eacces", "access permissions", "permission denied"))
        fallback = (
            "Subprocess network socket access was denied ([WinError 10013]/WSAEACCES). "
            "Host AI agent: please use your native tools (e.g. host WebSearch, gh repo view, or native fetch) "
            "to inspect this repository directly."
            if is_sock else
            f"Network error retrieving repository '{owner}/{repo_name}': {e}. Host agent: please fall back to native tools."
        )
        inspection = {
            "error": f"Failed to retrieve repository '{owner}/{repo_name}': {e}",
            "status_code": 0,
            "fallback_recommendation": fallback,
        }

    if args.json:
        out_content = json.dumps(inspection, indent=2)
    else:
        out_content = format_inspection_report(inspection)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_content + "\n")
        print(f"Report written to {args.output}")
    else:
        print(out_content)

    if inspection.get("error"):
        sys.exit(2)


if __name__ == "__main__":
    main()
