#!/usr/bin/env python3
"""
scripts/verify_sources.py - Source link validation and evidence classification auditor.

Part of BeenHere: Explore every angle of an idea before you build it.
Uses Python standard library only (no external dependencies).
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Set, Tuple

USER_AGENT = "BeenHere/1.1.0 (https://github.com/manasvignesh/BeenHere)"

EVIDENCE_TAGS = [
    "[VERIFIED-TEST]",
    "[VERIFIED-SOURCE]",
    "[VERIFIED-METADATA]",
    "[UNVERIFIED-MARKETING-CLAIM]",
    "[INFERRED]",
    "[UNKNOWN]",
]


def check_url_reachability(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Check if a URL is reachable using HTTP HEAD (falling back to GET).
    Does not download the body.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return {
            "url": url,
            "status": "unsupported_scheme",
            "reachable": False,
            "status_code": None,
            "error": f"Unsupported URI scheme: '{parsed.scheme}'",
        }

    # First attempt: HEAD request
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", USER_AGENT)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {
                "url": url,
                "status": "reachable",
                "reachable": True,
                "status_code": resp.status,
                "error": None,
            }
    except urllib.error.HTTPError as e:
        # Some servers reject HEAD with 405 Method Not Allowed; fallback to lightweight GET
        if e.code in (405, 403):
            try:
                get_req = urllib.request.Request(url, method="GET")
                get_req.add_header("User-Agent", USER_AGENT)
                get_req.add_header("Range", "bytes=0-100")
                with urllib.request.urlopen(get_req, timeout=timeout) as get_resp:
                    return {
                        "url": url,
                        "status": "reachable",
                        "reachable": True,
                        "status_code": get_resp.status,
                        "error": None,
                    }
            except urllib.error.HTTPError as get_err:
                return {
                    "url": url,
                    "status": "http_error",
                    "reachable": get_err.code < 400,
                    "status_code": get_err.code,
                    "error": f"HTTP {get_err.code}",
                }
            except Exception as get_err:
                return {
                    "url": url,
                    "status": "failed",
                    "reachable": False,
                    "status_code": e.code,
                    "error": str(get_err),
                }

        return {
            "url": url,
            "status": "http_error",
            "reachable": False,
            "status_code": e.code,
            "error": f"HTTP {e.code}",
        }
    except (urllib.error.URLError, OSError) as e:
        reason = getattr(e, "reason", str(e))
        return {
            "url": url,
            "status": "network_error",
            "reachable": False,
            "status_code": None,
            "error": str(reason),
        }
    except Exception as e:
        return {
            "url": url,
            "status": "error",
            "reachable": False,
            "status_code": None,
            "error": str(e),
        }


def extract_markdown_links(markdown_text: str) -> List[Dict[str, str]]:
    """Extract standard markdown links [text](url) from text."""
    # Regex matching [text](url)
    pattern = re.compile(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)')
    matches = []
    seen = set()

    for m in pattern.finditer(markdown_text):
        label = m.group(1).strip()
        url = m.group(2).strip()
        if url not in seen:
            seen.add(url)
            matches.append({"label": label, "url": url})

    return matches


def audit_evidence_tags(markdown_text: str) -> Dict[str, Any]:
    """Audit the presence and frequency of BeenHere evidence tags."""
    counts = {}
    for tag in EVIDENCE_TAGS:
        # Search for exact tag matches
        c = markdown_text.count(tag)
        counts[tag] = c

    total_tagged = sum(counts.values())

    return {
        "tag_counts": counts,
        "total_tags_found": total_tagged,
        "has_evidence_tagging": total_tagged > 0,
    }


def verify_file_or_urls(
    file_path: Optional[str] = None,
    urls: Optional[List[str]] = None,
    skip_reachability: bool = False,
    mock_reachability_map: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Execute full audit across specified file and/or URLs.
    """
    extracted_links = []
    evidence_audit = None
    target_urls = set()

    if file_path:
        if not os.path.isfile(file_path):
            return {
                "error": f"File not found: '{file_path}'",
                "status": "error",
            }
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        extracted_links = extract_markdown_links(content)
        evidence_audit = audit_evidence_tags(content)
        for link in extracted_links:
            target_urls.add(link["url"])

    if urls:
        for u in urls:
            u_clean = u.strip()
            if u_clean:
                target_urls.add(u_clean)

    reachability_results = []
    if not skip_reachability:
        for url in sorted(target_urls):
            if mock_reachability_map and url in mock_reachability_map:
                reachability_results.append(mock_reachability_map[url])
            else:
                res = check_url_reachability(url)
                reachability_results.append(res)

    reachable_count = sum(1 for r in reachability_results if r.get("reachable"))
    unreachable_count = len(reachability_results) - reachable_count

    return {
        "status": "success",
        "file_inspected": file_path,
        "links_found_count": len(extracted_links),
        "links_extracted": extracted_links,
        "evidence_audit": evidence_audit,
        "reachability": {
            "total_tested": len(reachability_results),
            "reachable": reachable_count,
            "unreachable": unreachable_count,
            "results": reachability_results,
        },
    }


def format_verification_report(res: Dict[str, Any]) -> str:
    """Format audit results as readable markdown."""
    if res.get("error"):
        return f"Verification Error: {res['error']}"

    lines = []
    lines.append("# BeenHere Source & Evidence Verification Report\n")

    if res.get("file_inspected"):
        lines.append(f"**Target Document:** `{res['file_inspected']}`")

    ea = res.get("evidence_audit")
    if ea:
        lines.append("\n## 1. Evidence Classification Audit")
        lines.append(f"- **Total Evidence Citations:** {ea['total_tags_found']}")
        lines.append("- **Tag Distribution:**")
        for tag, cnt in ea["tag_counts"].items():
            lines.append(f"  - `{tag}`: {cnt}")
        if ea["total_tags_found"] == 0:
            lines.append("  - ⚠️ *Warning: Document contains zero formal evidence tags.*")
        else:
            lines.append("  - ✅ *Formal evidence hierarchy detected.*")

    reach = res.get("reachability", {})
    if reach.get("results"):
        lines.append("\n## 2. Source Link Reachability")
        lines.append(f"- **Tested:** {reach['total_tested']} | **Reachable:** {reach['reachable']} | **Failed/Broken:** {reach['unreachable']}\n")
        lines.append("| URL | Reachable | Status Code | Details |")
        lines.append("| :--- | :---: | :---: | :--- |")
        for r in reach["results"]:
            reach_sym = "✅" if r["reachable"] else "❌"
            code_str = str(r["status_code"]) if r["status_code"] else "-"
            err_str = r["error"] or "OK"
            lines.append(f"| {r['url']} | {reach_sym} | {code_str} | {err_str} |")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Deterministic Source & Evidence Verifier for BeenHere")
    parser.add_argument("--file", "-f", type=str, help="Path to markdown document to scan and verify")
    parser.add_argument("--urls", "-u", nargs="+", help="Specific URLs to verify")
    parser.add_argument("--skip-network", action="store_true", help="Skip HTTP network reachability tests")
    parser.add_argument("--json", action="store_true", help="Output raw structured JSON to stdout")
    parser.add_argument("--output", "-o", type=str, help="Save report to specified file path")

    args = parser.parse_args()

    if not args.file and not args.urls:
        parser.error("At least one of --file or --urls must be provided.")

    audit_res = verify_file_or_urls(
        file_path=args.file,
        urls=args.urls,
        skip_reachability=args.skip_network,
    )

    if args.json:
        out_content = json.dumps(audit_res, indent=2)
    else:
        out_content = format_verification_report(audit_res)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_content + "\n")
        print(f"Report written to {args.output}")
    else:
        print(out_content)

    if audit_res.get("error"):
        sys.exit(2)


if __name__ == "__main__":
    main()
