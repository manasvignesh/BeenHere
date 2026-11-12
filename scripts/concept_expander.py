#!/usr/bin/env python3
"""
scripts/concept_expander.py - Executable Concept Expansion & Research Planning Utility.

Part of BeenHere: Explore every angle of an idea before you build it.
Uses Python standard library only (no external dependencies).
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Set

# Universal mechanism to adjacent vertical mapping catalog
UNIVERSAL_VERTICAL_CATALOG: Dict[str, Dict[str, Any]] = {
    "consensus": {
        "adjacent_domains": ["Distributed Systems", "Sociology & Political Science", "Cryptographic Protocols"],
        "analogous_mechanisms": ["Raft/Paxos leader election", "Delphi method deliberation", "Byzantine fault tolerance"],
        "academic_keywords": ["consensus protocol", "delphi method", "social choice theory"],
    },
    "turn_taking": {
        "adjacent_domains": ["Avionics & Aerospace", "Interactive Drama / Game AI", "Telecommunications"],
        "analogous_mechanisms": ["Cockpit Resource Management sterile channel", "Drama manager beat scheduling", "Token bucket media access control"],
        "academic_keywords": ["conversational floor control", "turn-taking state machine", "audio collision resolution"],
    },
    "arbitration": {
        "adjacent_domains": ["Avionics", "Financial Exchanges", "Operating Systems"],
        "analogous_mechanisms": ["Triple modular redundancy voting", "Order book clearing arbiters", "Fair queuing schedulers"],
        "academic_keywords": ["priority arbitration", "conflict resolution algorithm", "resource scheduling"],
    },
    "memory": {
        "adjacent_domains": ["Cognitive Science", "Database Systems", "Operating Systems"],
        "analogous_mechanisms": ["ACT-R cognitive memory chunking", "Multi-tiered caching (L1/L2/Disk)", "Virtual memory page eviction"],
        "academic_keywords": ["episodic memory stream", "associative retrieval", "cognitive architecture"],
    },
    "debate": {
        "adjacent_domains": ["Formal Logic & Law", "Sociology", "Multi-Agent Reinforcement Learning"],
        "analogous_mechanisms": ["Toulmin argumentation model", "Socratic dialectic loops", "Adversarial self-play"],
        "academic_keywords": ["multi-agent debate", "dialectical argumentation", "adversarial reasoning"],
    },
    "simulation": {
        "adjacent_domains": ["Ecology & Epidemiology", "Video Game Systems", "Microeconomics"],
        "analogous_mechanisms": ["Agent-based modeling (ABM)", "Utility AI / GOAP", "Dynamic market equilibrium"],
        "academic_keywords": ["agent-based simulation", "artificial society", "emergent behavior"],
    },
    "streaming": {
        "adjacent_domains": ["Signal Processing", "Telecommunications", "Industrial IoT"],
        "analogous_mechanisms": ["Ring buffer jitter management", "WebRTC RTP packet pacing", "Backpressure flow control"],
        "academic_keywords": ["real-time audio pipeline", "low latency streaming", "voice activity detection"],
    },
    "collaboration": {
        "adjacent_domains": ["Distributed Version Control", "Urban Planning", "Aviation"],
        "analogous_mechanisms": ["Conflict-free Replicated Data Types (CRDT)", "Collaborative spatial mapping", "Crew resource management"],
        "academic_keywords": ["real-time collaborative editing", "operational transformation", "distributed state synchronization"],
    },
}


def sanitize_input(text: str) -> str:
    """Trim and sanitize raw text input."""
    if not text:
        return ""
    # Strip dangerous characters and excessive whitespace
    return re.sub(r"\s+", " ", text.strip())


def normalize_keyword(kw: str) -> str:
    """Normalize keyword for deduplication."""
    return kw.strip().lower()


def build_research_plan(
    concept: str,
    problems: Optional[List[str]] = None,
    mechanisms: Optional[List[str]] = None,
    technical_primitives: Optional[List[str]] = None,
    behavioral_patterns: Optional[List[str]] = None,
    adjacent_verticals: Optional[List[str]] = None,
    research_priorities: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate an actionable, deterministic research plan and query matrix
    from a structured idea decomposition.
    """
    clean_concept = sanitize_input(concept)
    if not clean_concept:
        raise ValueError("Concept description cannot be empty.")

    problems = [sanitize_input(p) for p in (problems or []) if sanitize_input(p)]
    mechanisms = [sanitize_input(m) for m in (mechanisms or []) if sanitize_input(m)]
    primitives = [sanitize_input(p) for p in (technical_primitives or []) if sanitize_input(p)]
    patterns = [sanitize_input(p) for p in (behavioral_patterns or []) if sanitize_input(p)]
    verticals = [sanitize_input(v) for v in (adjacent_verticals or []) if sanitize_input(v)]

    # Detect implied mechanisms from catalog if mechanisms are sparse
    detected_catalog_matches: Dict[str, Dict[str, Any]] = {}
    searchable_text = f"{clean_concept} {' '.join(problems)} {' '.join(mechanisms)}".lower()

    for key, data in UNIVERSAL_VERTICAL_CATALOG.items():
        if key in searchable_text:
            detected_catalog_matches[key] = data

    # Merge adjacent domains and academic keywords from matched mechanisms
    computed_verticals = set(verticals)
    suggested_analogous_mechanisms = []
    academic_keywords = []

    for key, data in detected_catalog_matches.items():
        for dom in data["adjacent_domains"]:
            computed_verticals.add(dom)
        suggested_analogous_mechanisms.extend(data["analogous_mechanisms"])
        academic_keywords.extend(data["academic_keywords"])

    # Build Direct Queries (GitHub & Product)
    direct_queries: Set[str] = set()
    concept_tokens = [w for w in re.findall(r"\b[A-Za-z0-9_-]+\b", clean_concept) if len(w) > 3]

    if len(concept_tokens) >= 2:
        direct_queries.add(" ".join(concept_tokens[:4]))
        direct_queries.add(f"{concept_tokens[0]} {concept_tokens[1]}")

    for p in problems[:3]:
        direct_queries.add(p)

    for m in mechanisms[:3]:
        direct_queries.add(m)

    all_emitted_queries = set(direct_queries)

    # Build Technical Primitives Queries (excluding direct queries)
    primitive_queries: Set[str] = set()
    for prim in primitives:
        if prim not in all_emitted_queries:
            primitive_queries.add(prim)
        for m in mechanisms[:2]:
            combo = f"{prim} {m}"
            if combo not in all_emitted_queries:
                primitive_queries.add(combo)

    all_emitted_queries.update(primitive_queries)

    # Build Cross-Vertical Queries (excluding direct and primitive queries)
    cross_vertical_queries: Set[str] = set()
    for vert in list(computed_verticals)[:4]:
        for m in (mechanisms or list(detected_catalog_matches.keys()))[:3]:
            combo = f"{vert} {m}"
            if combo not in all_emitted_queries:
                cross_vertical_queries.add(combo)
        for anal in suggested_analogous_mechanisms[:3]:
            combo = f"{vert} {anal}"
            if combo not in all_emitted_queries:
                cross_vertical_queries.add(combo)

    all_emitted_queries.update(cross_vertical_queries)

    # Build Academic Queries (excluding prior queries)
    academic_queries: Set[str] = set()
    for ak in academic_keywords[:6]:
        if ak not in all_emitted_queries:
            academic_queries.add(ak)
    for m in mechanisms[:3]:
        alg_query = f"{m} algorithm"
        if alg_query not in all_emitted_queries:
            academic_queries.add(alg_query)
        fw_query = f"{m} framework"
        if fw_query not in all_emitted_queries:
            academic_queries.add(fw_query)

    # Research Hypotheses to Verify (Distinguished from facts)
    hypotheses = [
        f"Hypothesis: The core mechanism '{m}' has prior open-source implementations outside the primary domain."
        for m in (mechanisms or list(detected_catalog_matches.keys()))[:3]
    ]
    if computed_verticals:
        hypotheses.append(
            f"Hypothesis: Architectural constraints from {list(computed_verticals)[0]} can transfer to resolve bottlenecks in this concept."
        )

    # Deduplicate queries cleanly
    clean_direct = sorted(list(direct_queries))[:8]
    clean_cross = sorted(list(cross_vertical_queries))[:10]
    clean_academic = sorted(list(academic_queries))[:8]
    clean_primitives = sorted(list(primitive_queries))[:6]

    default_priorities = research_priorities or [
        "1. Identify existing open-source projects providing direct turnkey solutions.",
        "2. Identify modular libraries solving individual technical primitives.",
        "3. Investigate academic papers proposing theoretical bounds or formal models.",
        "4. Explore cross-vertical analogies for battle-tested mechanisms.",
        "5. Conduct feature-gap analysis and formulate build-versus-reuse strategy.",
    ]

    return {
        "status": "success",
        "plan_type": "concept_expansion_and_research_plan",
        "original_concept": clean_concept,
        "decomposition": {
            "core_problems": problems,
            "mechanisms": mechanisms,
            "technical_primitives": primitives,
            "behavioral_patterns": patterns,
            "adjacent_industries": sorted(list(computed_verticals)),
            "suggested_analogous_mechanisms": sorted(list(set(suggested_analogous_mechanisms))),
        },
        "query_matrix": {
            "direct_queries": clean_direct,
            "technical_primitive_queries": clean_primitives,
            "cross_vertical_queries": clean_cross,
            "academic_queries": clean_academic,
        },
        "research_priorities": default_priorities,
        "hypotheses_to_verify": [
            {
                "hypothesis": h,
                "verification_status": "UNVERIFIED_HYPOTHESIS",
                "evidence_required": "Source inspection, academic paper, or working implementation.",
            }
            for h in hypotheses
        ],
    }


def format_text_plan(plan: Dict[str, Any]) -> str:
    """Format research plan as human-readable Markdown."""
    lines = []
    lines.append("# BeenHere Concept Expansion & Deterministic Research Plan\n")
    lines.append(f"**Target Concept:** {plan['original_concept']}\n")

    decomp = plan.get("decomposition", {})
    lines.append("## 1. Problem & Mechanism Decomposition")
    if decomp.get("core_problems"):
        lines.append("- **Core Problems:**")
        for p in decomp["core_problems"]:
            lines.append(f"  - {p}")
    if decomp.get("mechanisms"):
        lines.append("- **Underlying Mechanisms:**")
        for m in decomp["mechanisms"]:
            lines.append(f"  - {m}")
    if decomp.get("technical_primitives"):
        lines.append("- **Technical Primitives:**")
        for tp in decomp["technical_primitives"]:
            lines.append(f"  - {tp}")
    if decomp.get("adjacent_industries"):
        lines.append(f"- **Adjacent Industries:** {', '.join(decomp['adjacent_industries'])}")
    if decomp.get("suggested_analogous_mechanisms"):
        lines.append("- **Analogous Cross-Domain Mechanisms:**")
        for am in decomp["suggestous_mechanisms"] if "suggestous_mechanisms" in decomp else decomp.get("suggested_analogous_mechanisms", []):
            lines.append(f"  - {am}")
    lines.append("")

    qm = plan.get("query_matrix", {})
    lines.append("## 2. Multi-Tier Query Matrix")
    lines.append("### A. Direct & Component Queries (GitHub & Products)")
    for q in qm.get("direct_queries", []):
        lines.append(f"- `{q}`")
    lines.append("\n### B. Technical Primitive Queries")
    for q in qm.get("technical_primitive_queries", []):
        lines.append(f"- `{q}`")
    lines.append("\n### C. Cross-Vertical Queries")
    for q in qm.get("cross_vertical_queries", []):
        lines.append(f"- `{q}`")
    lines.append("\n### D. Academic Research Queries")
    for q in qm.get("academic_queries", []):
        lines.append(f"- `{q}`")
    lines.append("")

    lines.append("## 3. Research Priorities")
    for rp in plan.get("research_priorities", []):
        lines.append(f"- {rp}")
    lines.append("")

    lines.append("## 4. Hypotheses to Verify (Unverified Search Directions)")
    for hyp in plan.get("hypotheses_to_verify", []):
        lines.append(f"- `[{hyp['verification_status']}]` {hyp['hypothesis']}")
        lines.append(f"  *Evidence Needed:* {hyp['evidence_required']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic Concept Expander & Research Planning Utility for BeenHere"
    )
    parser.add_argument("--concept", "-c", type=str, help="High-level idea or concept description")
    parser.add_argument("--json-input", "-f", type=str, help="Path to structured JSON input file")
    parser.add_argument("--problems", "-p", nargs="+", help="Explicit core problems to solve")
    parser.add_argument("--mechanisms", "-m", nargs="+", help="Underlying computational or social mechanisms")
    parser.add_argument("--primitives", "-t", nargs="+", help="Technical primitives (e.g. WebRTC, CRDT)")
    parser.add_argument("--verticals", "-v", nargs="+", help="Candidate adjacent industries")
    parser.add_argument("--json", action="store_true", help="Output raw structured JSON to stdout")
    parser.add_argument("--output", "-o", type=str, help="Save generated plan to specified file path")

    args = parser.parse_args()

    concept = args.concept
    problems = args.problems or []
    mechanisms = args.mechanisms or []
    primitives = args.primitives or []
    verticals = args.verticals or []
    priorities = None

    if args.json_input:
        if not os.path.isfile(args.json_input):
            sys.stderr.write(f"Error: JSON input file not found: {args.json_input}\n")
            sys.exit(1)
        try:
            with open(args.json_input, "r", encoding="utf-8") as f:
                data = json.load(f)
            concept = data.get("concept") or concept
            problems = data.get("problems") or problems
            mechanisms = data.get("mechanisms") or mechanisms
            primitives = data.get("primitives") or primitives
            verticals = data.get("verticals") or verticals
            priorities = data.get("priorities")
        except Exception as e:
            sys.stderr.write(f"Failed to parse JSON input file: {e}\n")
            sys.exit(1)

    if not concept:
        parser.error("Either --concept or --json-input with a 'concept' field must be provided.")

    try:
        plan = build_research_plan(
            concept=concept,
            problems=problems,
            mechanisms=mechanisms,
            technical_primitives=primitives,
            adjacent_verticals=verticals,
            research_priorities=priorities,
        )
    except Exception as e:
        sys.stderr.write(f"Concept expansion failed: {e}\n")
        sys.exit(2)

    if args.json:
        out_content = json.dumps(plan, indent=2)
    else:
        out_content = format_text_plan(plan)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_content + "\n")
        print(f"Research plan written to {args.output}")
    else:
        print(out_content)


if __name__ == "__main__":
    main()
