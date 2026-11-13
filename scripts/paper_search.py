#!/usr/bin/env python3
"""
scripts/paper_search.py - Academic Research Discovery Utility for BeenHere.

Searches free public academic APIs (OpenAlex, arXiv, Semantic Scholar),
normalizes paper metadata into a unified schema, deduplicates entries,
handles retractions, and enforces evidence disclaimers.

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
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Set, Tuple

USER_AGENT = "BeenHere/1.0.0-beta.1 (https://github.com/manasvignesh/BeenHere; mailto:open-source@beenhere.local)"

OPENALEX_API_BASE = "https://api.openalex.org"
SEMANTIC_SCHOLAR_API_BASE = "https://api.semanticscholar.org/graph/v1"
ARXIV_API_BASE = "http://export.arxiv.org/api"


def get_semantic_scholar_token() -> Optional[str]:
    """Retrieve optional Semantic Scholar API token if configured."""
    return os.environ.get("SEMANTIC_SCHOLAR_API_KEY") or os.environ.get("S2_API_KEY")


def sanitize_text(text: Optional[str]) -> str:
    """Strip extraneous whitespace and control characters from text."""
    if not text:
        return ""
    clean = re.sub(r"\s+", " ", text.strip())
    # Disarm markdown triple backticks
    return clean.replace("```", "'''")


def normalize_doi(doi: Optional[str]) -> Optional[str]:
    """Normalize DOI to standard lowercase format."""
    if not doi:
        return None
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d if d else None


def normalize_title(title: str) -> str:
    """Normalize title for fuzzy deduplication."""
    # Replace hyphens and underscores with spaces first
    clean = re.sub(r"[-_]+", " ", title.lower())
    clean = re.sub(r"[^a-zA-Z0-9 ]+", "", clean)
    return re.sub(r"\s+", " ", clean).strip()


def reconstruct_openalex_abstract(inverted_index: Optional[Dict[str, List[int]]]) -> str:
    """Reconstruct abstract string from OpenAlex inverted index structure."""
    if not inverted_index or not isinstance(inverted_index, dict):
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        if isinstance(positions, list):
            for pos in positions:
                word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return sanitize_text(" ".join(w for _, w in word_positions))


def make_http_request(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 12,
) -> Tuple[int, Dict[str, str], bytes]:
    """Execute standard HTTP request with timeout and error capture."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            resp_headers = {k.lower(): v for k, v in resp.getheaders()}
            body = resp.read()
            return status, resp_headers, body
    except urllib.error.HTTPError as e:
        resp_headers = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
        body = e.read() if hasattr(e, "read") else b""
        return e.code, resp_headers, body
    except (urllib.error.URLError, OSError) as e:
        reason = getattr(e, "reason", e)
        raise RuntimeError(f"Network error accessing '{url}': {reason}") from e


def query_openalex(query: str, limit: int = 5) -> Dict[str, Any]:
    """Query OpenAlex works API."""
    params = {
        "search": query,
        "per_page": min(limit, 25),
    }
    url = f"{OPENALEX_API_BASE}/works?{urllib.parse.urlencode(params)}"
    try:
        status, headers, body = make_http_request(url)
    except Exception as e:
        return {"provider": "openalex", "status": "network_error", "error": str(e), "items": []}

    if status != 200:
        return {"provider": "openalex", "status": "http_error", "status_code": status, "items": []}

    try:
        data = json.loads(body.decode("utf-8", errors="replace"))
    except Exception as e:
        return {"provider": "openalex", "status": "json_parse_error", "error": str(e), "items": []}

    results = []
    for item in data.get("results", []):
        doi_raw = item.get("doi")
        doi_norm = normalize_doi(doi_raw)

        # Extract authors
        authors = []
        for a in item.get("authorships", []):
            author_obj = a.get("author") or {}
            name = author_obj.get("display_name")
            if name:
                authors.append(name)

        # Venue / host
        primary_loc = item.get("primary_location") or {}
        source_obj = primary_loc.get("source") or {}
        venue = source_obj.get("display_name") or "Academic Publication"

        abstract = reconstruct_openalex_abstract(item.get("abstract_inverted_index"))
        is_retracted = bool(item.get("is_retracted", False))

        results.append({
            "title": sanitize_text(item.get("title") or "Untitled"),
            "authors": authors[:8],
            "year": item.get("publication_year"),
            "venue": venue,
            "doi": doi_norm,
            "url": doi_raw or item.get("id"),
            "abstract": abstract[:1200] if abstract else None,
            "is_retracted": is_retracted,
            "citation_count": item.get("cited_by_count", 0),
            "provider": "openalex",
        })

    return {"provider": "openalex", "status": "success", "items": results}


def query_arxiv(query: str, limit: int = 5) -> Dict[str, Any]:
    """Query arXiv Atom XML API."""
    clean_query = re.sub(r'["\']', '', query)
    params = {
        "search_query": f"all:{clean_query}",
        "start": 0,
        "max_results": min(limit, 25),
    }
    url = f"{ARXIV_API_BASE}/query?{urllib.parse.urlencode(params)}"
    try:
        status, headers, body = make_http_request(url)
    except Exception as e:
        return {"provider": "arxiv", "status": "network_error", "error": str(e), "items": []}

    if status != 200:
        return {"provider": "arxiv", "status": "http_error", "status_code": status, "items": []}

    results = []
    try:
        root = ET.fromstring(body)
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

        for entry in root.findall("atom:entry", ns):
            title_elem = entry.find("atom:title", ns)
            title = sanitize_text(title_elem.text) if title_elem is not None and title_elem.text else "Untitled"

            summary_elem = entry.find("atom:summary", ns)
            abstract = sanitize_text(summary_elem.text) if summary_elem is not None and summary_elem.text else None

            authors = []
            for a in entry.findall("atom:author", ns):
                name_elem = a.find("atom:name", ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())

            published_elem = entry.find("atom:published", ns)
            year = None
            if published_elem is not None and published_elem.text:
                year_match = re.search(r"(\d{4})", published_elem.text)
                if year_match:
                    year = int(year_match.group(1))

            id_elem = entry.find("atom:id", ns)
            paper_url = id_elem.text.strip() if id_elem is not None and id_elem.text else ""

            # Check DOI
            doi_elem = entry.find("arxiv:doi", ns)
            doi = normalize_doi(doi_elem.text) if doi_elem is not None and doi_elem.text else None

            results.append({
                "title": title,
                "authors": authors[:8],
                "year": year,
                "venue": "arXiv",
                "doi": doi,
                "url": paper_url,
                "abstract": abstract[:1200] if abstract else None,
                "is_retracted": False,
                "citation_count": None,
                "provider": "arxiv",
            })
    except Exception as e:
        return {"provider": "arxiv", "status": "xml_parse_error", "error": str(e), "items": []}

    return {"provider": "arxiv", "status": "success", "items": results}


def query_semantic_scholar(query: str, limit: int = 5, token: Optional[str] = None) -> Dict[str, Any]:
    """Query Semantic Scholar Graph API."""
    params = {
        "query": query,
        "limit": min(limit, 25),
        "fields": "title,authors,year,abstract,url,citationCount,externalIds,venue",
    }
    url = f"{SEMANTIC_SCHOLAR_API_BASE}/paper/search?{urllib.parse.urlencode(params)}"
    headers = {}
    if token:
        headers["x-api-key"] = token

    try:
        status, resp_headers, body = make_http_request(url, headers=headers)
    except Exception as e:
        return {"provider": "semanticscholar", "status": "network_error", "error": str(e), "items": []}

    if status == 429:
        return {
            "provider": "semanticscholar",
            "status": "rate_limited",
            "message": "Semantic Scholar public rate limit reached (HTTP 429).",
            "items": [],
        }

    if status != 200:
        return {"provider": "semanticscholar", "status": "http_error", "status_code": status, "items": []}

    try:
        data = json.loads(body.decode("utf-8", errors="replace"))
    except Exception as e:
        return {"provider": "semanticscholar", "status": "json_parse_error", "error": str(e), "items": []}

    results = []
    for item in data.get("data", []):
        ext_ids = item.get("externalIds") or {}
        doi = normalize_doi(ext_ids.get("DOI"))

        authors = []
        for a in item.get("authors", []):
            if a.get("name"):
                authors.append(a["name"])

        results.append({
            "title": sanitize_text(item.get("title") or "Untitled"),
            "authors": authors[:8],
            "year": item.get("year"),
            "venue": item.get("venue") or "Semantic Scholar",
            "doi": doi,
            "url": item.get("url") or (f"https://doi.org/{doi}" if doi else ""),
            "abstract": sanitize_text(item.get("abstract"))[:1200] if item.get("abstract") else None,
            "is_retracted": False,
            "citation_count": item.get("citationCount"),
            "provider": "semanticscholar",
        })

    return {"provider": "semanticscholar", "status": "success", "items": results}


def search_academic_papers(
    queries: List[str],
    limit: int = 10,
    providers: Optional[List[str]] = None,
    token: Optional[str] = None,
    mock_data_map: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Search academic literature across multiple queries and providers,
    deduplicating by DOI and normalized title.
    """
    selected_providers = providers or ["openalex", "arxiv", "semanticscholar"]
    s2_token = token or get_semantic_scholar_token()

    seen_dois: Set[str] = set()
    seen_titles: Set[str] = set()
    aggregated_papers = []
    provider_statuses: Dict[str, Any] = {}
    errors: List[str] = []

    for q in queries:
        q_clean = q.strip()
        if not q_clean:
            continue

        for prov in selected_providers:
            if mock_data_map is not None:
                if prov in mock_data_map:
                    res = mock_data_map[prov]
                else:
                    continue
            elif prov == "openalex":
                res = query_openalex(q_clean, limit=limit)
            elif prov == "arxiv":
                res = query_arxiv(q_clean, limit=limit)
            elif prov == "semanticscholar":
                res = query_semantic_scholar(q_clean, limit=limit, token=s2_token)
            else:
                continue

            provider_statuses[prov] = res.get("status")

            if res.get("status") in ("http_error", "network_error", "rate_limited"):
                err_desc = res.get("message") or res.get("error") or f"HTTP {res.get('status_code')}"
                errors.append(f"Provider '{prov}' query '{q_clean}': {err_desc}")
                continue

            for paper in res.get("items", []):
                doi = paper.get("doi")
                title_norm = normalize_title(paper.get("title", ""))

                # Deduplicate
                if doi and doi in seen_dois:
                    continue
                if title_norm and title_norm in seen_titles:
                    continue

                if doi:
                    seen_dois.add(doi)
                if title_norm:
                    seen_titles.add(title_norm)

                paper["matched_queries"] = [q_clean]
                paper["evidence_tier"] = "[VERIFIED-METADATA]"
                paper["claim_disclaimer"] = (
                    "Unverified author claim from published abstract; not independently reproduced."
                )
                aggregated_papers.append(paper)

    # Sort by year descending (newest first), placing None at the end
    aggregated_papers.sort(key=lambda p: (p.get("year") or 0), reverse=True)
    final_papers = aggregated_papers[:limit]

    is_socket_restriction = any(
        any(k in str(err).lower() for k in ("10013", "wsaeacces", "eacces", "forbidden by its access permissions", "permission denied"))
        for err in errors
    )
    fallback_rec = None
    if errors and not final_papers:
        if is_socket_restriction:
            fallback_rec = (
                "Subprocess network socket access was restricted by the host/sandbox environment ([WinError 10013]/WSAEACCES). "
                "Host AI agent: please fall back to your native tools (e.g. host WebSearch, arXiv/OpenAlex web queries) "
                "to retrieve academic papers directly."
            )
        else:
            fallback_rec = (
                "Subprocess academic queries encountered network errors. "
                "Host AI agent: please fall back to your native WebSearch to discover academic papers directly."
            )

    result = {
        "status": "success" if final_papers else ("partial_error" if errors else "no_results"),
        "total_unique_discovered": len(aggregated_papers),
        "returned_count": len(final_papers),
        "queries_executed": [q.strip() for q in queries if q.strip()],
        "providers_queried": selected_providers,
        "provider_statuses": provider_statuses,
        "errors": errors,
        "items": final_papers,
    }
    if fallback_rec:
        result["fallback_recommendation"] = fallback_rec
    return result


def format_academic_table(results: Dict[str, Any]) -> str:
    """Format academic findings into a readable Markdown report table."""
    items = results.get("items", [])
    if not items:
        msg = "No academic papers found."
        if results.get("errors"):
            msg += "\nProvider Warnings / Errors:\n" + "\n".join(f" - {e}" for e in results["errors"])
        if results.get("fallback_recommendation"):
            msg += f"\n\n> [!WARNING] Subprocess Network Restriction:\n> {results['fallback_recommendation']}"
        return msg

    lines = []
    lines.append(f"# Academic Literature Discovery ({len(items)} papers retrieved)\n")
    lines.append("| Title | Year | Authors | Venue / Provider | Retracted? | Link |")
    lines.append("| :--- | :---: | :--- | :--- | :---: | :--- |")

    for p in items:
        authors_str = ", ".join(p["authors"][:2]) + (" et al." if len(p["authors"]) > 2 else "") if p["authors"] else "Unspecified"
        year_str = str(p["year"]) if p["year"] else "N/A"
        retracted_str = "⚠️ YES" if p.get("is_retracted") else "No"
        link_str = f"[Link]({p['url']})" if p.get("url") else "-"
        lines.append(f"| **{p['title']}** | {year_str} | {authors_str} | {p['venue']} ({p['provider']}) | {retracted_str} | {link_str} |")

    lines.append("\n## Abstracts & Primary Claims\n")
    lines.append("*Disclaimer: All claims below represent published abstract text [VERIFIED-METADATA] and have not been experimentally reproduced by this skill.*\n")

    for i, p in enumerate(items, 1):
        lines.append(f"### {i}. {p['title']} ({p.get('year') or 'N/A'})")
        lines.append(f"- **Authors:** {', '.join(p['authors']) if p['authors'] else 'Unknown'}")
        lines.append(f"- **Venue:** {p['venue']} | **Provider:** `{p['provider']}` | **DOI:** `{p.get('doi') or 'N/A'}`")
        if p.get("citation_count") is not None:
            lines.append(f"- **Citations:** {p['citation_count']:,}")
        if p.get("is_retracted"):
            lines.append("- ⚠️ **WARNING: This paper has been officially marked as RETRACTED.**")

        if p.get("abstract"):
            lines.append(f"- **Abstract Excerpt:**\n  > {p['abstract'][:450]}...")
        else:
            lines.append("- **Abstract:** Not indexed in public metadata.")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic Academic Paper Discovery Utility for BeenHere"
    )
    parser.add_argument("--queries", "-q", nargs="+", required=True, help="One or more academic search queries")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Maximum number of papers to return")
    parser.add_argument(
        "--provider",
        "-p",
        choices=["all", "openalex", "arxiv", "semanticscholar"],
        default="all",
        help="Target academic data provider",
    )
    parser.add_argument("--json", action="store_true", help="Output raw structured JSON to stdout")
    parser.add_argument("--output", "-o", type=str, help="Save report to specified file path")

    args = parser.parse_args()

    providers = None
    if args.provider != "all":
        providers = [args.provider]

    try:
        results = search_academic_papers(
            queries=args.queries,
            limit=args.limit,
            providers=providers,
        )
    except Exception as e:
        sys.stderr.write(f"Academic search failed: {e}\n")
        sys.exit(1)

    if args.json:
        out_content = json.dumps(results, indent=2)
    else:
        out_content = format_academic_table(results)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_content + "\n")
        print(f"Academic results written to {args.output}")
    else:
        print(out_content)

    if results.get("status") == "no_results":
        sys.exit(0)


if __name__ == "__main__":
    main()
