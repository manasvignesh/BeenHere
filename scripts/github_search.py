#!/usr/bin/env python3
"""
scripts/github_search.py - Deterministic GitHub repository discovery utility.

Part of BeenHere: Explore every angle of an idea before you build it.
Uses Python standard library only (no external dependencies).
"""

import argparse
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

USER_AGENT = "BeenHere/1.0.0-beta.1 (https://github.com/beenhere/beenhere)"
GITHUB_API_BASE = "https://api.github.com"

# Patterns commonly used in prompt injection attempts within external repos
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"(?i)system\s*prompt\s*:",
    r"(?i)override\s+(all\s+)?(evaluation|rules|rubric)",
    r"(?i)you\s+must\s+(adopt|approve|recommend)",
    r"(?i)pretend\s+you\s+are",
    r"(?i)new\s+system\s+instruction",
]


def sanitize_untrusted_text(text: str) -> str:
    """Sanitize external untrusted text to prevent prompt injection and markdown breakout."""
    if not text:
        return ""
    sanitized = text
    for pat in INJECTION_PATTERNS:
        sanitized = re.sub(pat, "[BLOCKED_INJECTION_PATTERN]", sanitized)
    return sanitized.replace("```", "'''")


def get_auth_token() -> Optional[str]:
    """Retrieve GitHub token from environment if available."""
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def make_request(url: str, token: Optional[str] = None) -> Tuple[int, Dict[str, str], bytes]:
    """
    Execute HTTP GET request with appropriate headers and rate limit tracking.
    Returns (status_code, headers_dict, body_bytes).
    """
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


def parse_rate_limit(headers: Dict[str, str]) -> Dict[str, Any]:
    """Extract rate limit indicators from response headers."""
    remaining = headers.get("x-ratelimit-remaining")
    reset_ts = headers.get("x-ratelimit-reset")
    limit = headers.get("x-ratelimit-limit")

    reset_time = None
    seconds_until_reset = None
    if reset_ts and reset_ts.isdigit():
        ts = int(reset_ts)
        reset_time = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).isoformat()
        seconds_until_reset = max(0, int(ts - time.time()))

    return {
        "limit": int(limit) if limit and limit.isdigit() else None,
        "remaining": int(remaining) if remaining and remaining.isdigit() else None,
        "reset_time": reset_time,
        "seconds_until_reset": seconds_until_reset,
    }


def search_github_repositories(
    query: str,
    sort: str = "stars",
    order: str = "desc",
    per_page: int = 30,
    page: int = 1,
    token: Optional[str] = None,
    mock_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Search GitHub repositories using the GitHub REST API.
    """
    if mock_data is not None:
        return mock_data

    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": min(per_page, 100),
        "page": page,
    }
    url = f"{GITHUB_API_BASE}/search/repositories?{urllib.parse.urlencode(params)}"
    status, headers, body = make_request(url, token=token)
    rate_info = parse_rate_limit(headers)

    if status == 403 or status == 429:
        msg = "GitHub API rate limit exceeded."
        if rate_info["seconds_until_reset"]:
            msg += f" Resets in {rate_info['seconds_until_reset']} seconds ({rate_info['reset_time']})."
        msg += " Set GITHUB_TOKEN environment variable for 5,000 requests/hour."
        return {
            "error": "rate_limited",
            "message": msg,
            "status_code": status,
            "rate_limit": rate_info,
            "items": [],
            "total_count": 0,
        }

    if status != 200:
        error_msg = f"GitHub API error (HTTP {status})"
        try:
            err_json = json.loads(body.decode("utf-8", errors="replace"))
            if "message" in err_json:
                error_msg += f": {err_json['message']}"
        except Exception:
            pass
        return {
            "error": "api_error",
            "message": error_msg,
            "status_code": status,
            "rate_limit": rate_info,
            "items": [],
            "total_count": 0,
        }

    try:
        data = json.loads(body.decode("utf-8", errors="replace"))
    except Exception as e:
        return {
            "error": "json_parse_error",
            "message": f"Failed to parse API response: {e}",
            "items": [],
            "total_count": 0,
        }

    raw_items = data.get("items", [])
    normalized_items = []
    for item in raw_items:
        license_info = item.get("license") or {}
        raw_desc = (item.get("description") or "")[:1000]
        normalized_items.append({
            "full_name": item.get("full_name"),
            "name": item.get("name"),
            "owner": (item.get("owner") or {}).get("login"),
            "html_url": item.get("html_url"),
            "description": sanitize_untrusted_text(raw_desc),
            "stargazers_count": item.get("stargazers_count", 0),
            "forks_count": item.get("forks_count", 0),
            "open_issues_count": item.get("open_issues_count", 0),
            "language": item.get("language") or "Unknown",
            "license": license_info.get("spdx_id") or license_info.get("key") or "NOASSERTION",
            "license_name": license_info.get("name") or "None / Unspecified",
            "updated_at": item.get("updated_at"),
            "pushed_at": item.get("pushed_at"),
            "archived": item.get("archived", False),
            "topics": item.get("topics", []),
        })

    return {
        "status": "success",
        "total_count": data.get("total_count", 0),
        "items": normalized_items,
        "rate_limit": rate_info,
    }


def multi_query_search(
    queries: List[str],
    limit: int = 15,
    min_stars: int = 0,
    sort: str = "stars",
    token: Optional[str] = None,
    mock_data_map: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Execute multiple query variants, deduplicate items by full_name, and return ranked results.
    """
    seen_repos = set()
    aggregated_items = []
    executed_queries = []
    rate_limits = []
    errors = []

    for q in queries:
        q_clean = q.strip()
        if not q_clean:
            continue

        query_with_filter = q_clean
        if min_stars > 0 and "stars:" not in q_clean:
            query_with_filter += f" stars:>={min_stars}"

        executed_queries.append(query_with_filter)

        mock_resp = mock_data_map.get(q_clean) if mock_data_map else None
        try:
            res = search_github_repositories(
                query=query_with_filter,
                sort=sort,
                token=token,
                mock_data=mock_resp,
            )
        except Exception as e:
            errors.append(f"Query '{q_clean}' failed: {e}")
            continue

        if res.get("rate_limit"):
            rate_limits.append(res["rate_limit"])

        if res.get("error"):
            errors.append(f"Query '{q_clean}': {res.get('message')}")
            if res.get("error") == "rate_limited":
                break

        for item in res.get("items", []):
            fn = item.get("full_name")
            if fn and fn not in seen_repos:
                seen_repos.add(fn)
                item["matched_queries"] = [q_clean]
                aggregated_items.append(item)
            elif fn:
                for existing in aggregated_items:
                    if existing.get("full_name") == fn:
                        if "matched_queries" not in existing:
                            existing["matched_queries"] = []
                        if q_clean not in existing["matched_queries"]:
                            existing["matched_queries"].append(q_clean)

    # Sort aggregated items by stargazers_count desc
    aggregated_items.sort(key=lambda x: x.get("stargazers_count", 0), reverse=True)
    final_items = aggregated_items[:limit]

    latest_rate_limit = rate_limits[-1] if rate_limits else {}

    is_socket_restriction = any(
        any(k in str(err).lower() for k in ("10013", "wsaeacces", "eacces", "forbidden by its access permissions", "permission denied"))
        for err in errors
    )
    fallback_rec = None
    if errors and not final_items:
        if is_socket_restriction:
            fallback_rec = (
                "Subprocess network socket access was restricted by the host/sandbox environment ([WinError 10013]/WSAEACCES). "
                "Host AI agent: please fall back to your native tools (e.g. host WebSearch, GitHub CLI 'gh search', "
                "or native HTTP fetch) to discover repositories directly."
            )
        else:
            fallback_rec = (
                "Subprocess network queries encountered errors. "
                "Host AI agent: please fall back to your native WebSearch or GitHub CLI ('gh') to discover candidate repositories."
            )

    result = {
        "status": "partial_success" if errors and final_items else ("error" if errors and not final_items else "success"),
        "total_unique_discovered": len(aggregated_items),
        "returned_count": len(final_items),
        "queries_executed": executed_queries,
        "errors": errors,
        "rate_limit": latest_rate_limit,
        "items": final_items,
    }
    if fallback_rec:
        result["fallback_recommendation"] = fallback_rec
    return result


def format_text_table(results: Dict[str, Any]) -> str:
    """Format search results as a clean readable markdown table."""
    items = results.get("items", [])
    if not items:
        msg = "No repositories found."
        if results.get("errors"):
            msg += "\nErrors:\n" + "\n".join(f" - {e}" for e in results["errors"])
        if results.get("fallback_recommendation"):
            msg += f"\n\n> [!WARNING] Subprocess Network Restriction:\n> {results['fallback_recommendation']}"
        return msg

    lines = []
    lines.append(f"Discovered {results.get('total_unique_discovered', len(items))} unique repositories across {len(results.get('queries_executed', []))} queries.\n")
    lines.append("| Repository | Stars | Language | License | Last Push | Matched Queries |")
    lines.append("| :--- | :---: | :--- | :--- | :--- | :--- |")

    for it in items:
        repo_link = f"[{it['full_name']}]({it['html_url']})"
        stars = f"{it['stargazers_count']:,}"
        lang = it.get("language") or "Unknown"
        lic = it.get("license") or "No License"
        push_date = (it.get("pushed_at") or "")[:10]
        queries_matched = ", ".join(it.get("matched_queries", []))
        lines.append(f"| {repo_link} | {stars} | {lang} | {lic} | {push_date} | {queries_matched} |")

    lines.append("\n### Descriptions & Signals:\n")
    for it in items:
        desc = it.get("description") or "No description provided."
        desc_snippet = desc[:250] + ("..." if len(desc) > 250 else "")
        lines.append(f"- **[{it['full_name']}]({it['html_url']})** ({it.get('license')} | {it['stargazers_count']:,}★): {desc_snippet}")

    if results.get("rate_limit"):
        rl = results["rate_limit"]
        rem = rl.get("remaining")
        lim = rl.get("limit")
        if rem is not None and lim is not None:
            lines.append(f"\n*Rate Limit Status: {rem}/{lim} requests remaining.*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Deterministic GitHub Prior-Art Search Utility for BeenHere")
    parser.add_argument("--queries", "-q", nargs="+", required=True, help="One or more query phrases or keywords")
    parser.add_argument("--limit", "-n", type=int, default=15, help="Maximum number of unique repositories to return")
    parser.add_argument("--min-stars", type=int, default=0, help="Filter for minimum stargazers count")
    parser.add_argument("--sort", choices=["stars", "forks", "updated"], default="stars", help="Sort order for results")
    parser.add_argument("--json", action="store_true", help="Output raw structured JSON to stdout")
    parser.add_argument("--output", "-o", type=str, help="Save output to specified file path")

    args = parser.parse_args()
    token = get_auth_token()

    try:
        results = multi_query_search(
            queries=args.queries,
            limit=args.limit,
            min_stars=args.min_stars,
            sort=args.sort,
            token=token,
        )
    except Exception as e:
        sys.stderr.write(f"Search execution failed: {e}\n")
        sys.exit(1)

    if args.json:
        out_content = json.dumps(results, indent=2)
    else:
        out_content = format_text_table(results)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_content + "\n")
        print(f"Results written to {args.output}")
    else:
        print(out_content)

    if results.get("status") == "error":
        sys.exit(2)


if __name__ == "__main__":
    main()
