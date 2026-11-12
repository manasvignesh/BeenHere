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

USER_AGENT = "BeenHere-Skill/0.1.0 (https://github.com/beenhere)"
GITHUB_API_BASE = "https://api.github.com"

# Known license categories
LICENSE_CATEGORIES = {
    "permissive": ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unlicense", "CC0-1.0"],
    "weak_copyleft": ["LGPL-2.1", "LGPL-3.0", "MPL-2.0", "EPL-2.0"],
    "strong_copyleft": ["GPL-2.0", "GPL-3.0", "AGPL-3.0", "OSL-3.0"],
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

    clean = clean.rstrip("/").removesuffix(".git")
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
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error accessing GitHub API: {e.reason}") from e


def categorize_license(spdx_id: Optional[str]) -> Tuple[str, str, str]:
    """
    Categorize license into (category, clearance_tier, rationale).
    Returns (category, clearance, rationale).
    """
    if not spdx_id or spdx_id in ("NOASSERTION", "NONE", "Unknown"):
        return (
            "unresolved",
            "CRITICAL_BLOCKER",
            "No recognized open-source license detected. Under standard copyright law, All Rights Reserved applies. Code cannot be legally reused, forked, or copied without explicit author permission.",
        )

    for cat, spdx_list in LICENSE_CATEGORIES.items():
        if spdx_id in spdx_list:
            if cat == "permissive":
                return (
                    "permissive",
                    "CLEAR",
                    f"Permissive license ({spdx_id}). Grants broad rights to adopt, modify, integrate, and distribute in open-source or commercial projects, subject to copyright and license notice retention.",
                )
            elif cat == "weak_copyleft":
                return (
                    "weak_copyleft",
                    "CONDITIONAL",
                    f"Weak copyleft license ({spdx_id}). Modifications to the covered files/library must be released under same terms, but dynamic linking or integration with proprietary code is generally permitted.",
                )
            elif cat == "strong_copyleft":
                return (
                    "strong_copyleft",
                    "RESTRICTED",
                    f"Strong copyleft license ({spdx_id}). Any derivative work or combined application must be released under the same license terms. Potential viral risk for closed-source or differently licensed projects.",
                )
            elif cat == "source_available":
                return (
                    "source_available",
                    "COMMERCIAL_RISK",
                    f"Source-available or business-source license ({spdx_id}). Not OSI-approved open source; restricts commercial use, hosting, or competitive deployment.",
                )

    return (
        "custom_or_other",
        "INVESTIGATE",
        f"Custom or non-standard license detected ({spdx_id}). Requires manual legal review of license text.",
    )


def compute_maintenance_signals(repo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate maintenance vitals based on repository timestamps and state."""
    pushed_at_str = repo_data.get("pushed_at")
    created_at_str = repo_data.get("created_at")

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
    token: Optional[str] = None,
    mock_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Programmatically inspect repository metadata, languages, license, and manifest files.
    """
    if mock_data is not None:
        repo_data = mock_data.get("repo", {})
        languages = mock_data.get("languages", {})
        root_files = mock_data.get("root_files", [])
        readme_snippet = mock_data.get("readme_snippet", "")
    else:
        # 1. Fetch main repo metadata
        repo_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        status, headers, body = make_request(repo_url, token=token)
        if status != 200:
            return {
                "error": f"Failed to retrieve repository '{owner}/{repo}' (HTTP {status})",
                "status_code": status,
            }
        repo_data = json.loads(body.decode("utf-8", errors="replace"))

        # 2. Fetch languages breakdown
        languages = {}
        lang_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
        try:
            l_status, _, l_body = make_request(lang_url, token=token)
            if l_status == 200:
                languages = json.loads(l_body.decode("utf-8", errors="replace"))
        except Exception:
            pass

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
                    # Clean up first 1000 characters
                    lines = [ln.strip() for ln in raw_readme.splitlines() if ln.strip() and not ln.startswith("[!")]
                    readme_snippet = "\n".join(lines[:15])
        except Exception:
            pass

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
    if clearance in ("CRITICAL_BLOCKER", "RESTRICTED", "COMMERCIAL_RISK"):
        blockers.append(f"Legal/License Risk: {rationale}")
    if maint["is_archived"]:
        blockers.append("Upstream is officially archived (read-only).")
    if maint["status"] == "DORMANT":
        blockers.append(f"Maintenance abandonment risk (inactive for {maint['days_since_last_push']} days).")

    return {
        "status": "success",
        "repository": repo_data.get("full_name", f"{owner}/{repo}"),
        "html_url": repo_data.get("html_url", f"https://github.com/{owner}/{repo}"),
        "description": repo_data.get("description") or "",
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
        "readme_excerpt": readme_snippet,
    }


def format_inspection_report(res: Dict[str, Any]) -> str:
    """Format repository inspection results into readable markdown."""
    if res.get("error"):
        return f"Inspection Error: {res['error']}"

    lic = res["license"]
    maint = res["maintenance"]

    lines = []
    lines.append(f"# Repository Inspection: {res['repository']}\n")
    lines.append(f"**URL:** {res['html_url']}")
    lines.append(f"**Description:** {res['description'] or 'None'}\n")

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
        lines.append("**Identified Blockers:**")
        for b in res["reuse_blockers"]:
            lines.append(f"- ⚠️ {b}")
    else:
        lines.append("✅ **No critical legal or maintenance blockers detected.** Feasible candidate for reuse.")

    if res.get("readme_excerpt"):
        lines.append("\n## 5. README Excerpt (Primary Claims)")
        lines.append("```markdown")
        lines.append(res["readme_excerpt"][:600] + ("..." if len(res["readme_excerpt"]) > 600 else ""))
        lines.append("```")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Deterministic Repository Inspector for BeenHere")
    parser.add_argument("--repo", "-r", required=True, help="Repository slug (owner/repo) or GitHub URL")
    parser.add_argument("--json", action="store_true", help="Output raw structured JSON to stdout")
    parser.add_argument("--output", "-o", type=str, help="Save report to specified file path")

    args = parser.parse_args()

    try:
        owner, repo_name = parse_repo_slug(args.repo)
    except ValueError as e:
        sys.stderr.write(f"Argument error: {e}\n")
        sys.exit(1)

    token = get_auth_token()
    inspection = inspect_repository(owner, repo_name, token=token)

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
