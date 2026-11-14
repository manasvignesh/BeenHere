#!/usr/bin/env python3
"""
scripts/concept_expander.py - Deterministic Concept Expansion & Research Planning Utility for BeenHere.

Part of BeenHere: Explore every angle of an idea before you build it.
Uses Python standard library only (no external dependencies). Compatible with Python 3.8+.

Transforms software ideas into structured, multi-tier research plans without requiring
paid AI APIs or external network calls. Decomposes concepts into:
- Core engineering problems
- Underlying computational mechanisms
- Technical primitives
- Adjacent industry verticals
- Analogous cross-domain mechanisms
- Multi-tier query matrices (direct, primitive, cross-vertical, academic)
- Structured, unverified research hypotheses
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

KNOWN_ACRONYMS: Set[str] = {
    "ai", "ml", "p2p", "db", "ui", "ux", "os", "ci", "cd", "ar", "vr",
    "iot", "nlp", "cv", "k8s", "etl", "gis", "crdt", "e2ee", "ast", "dom",
    "pdf", "ocr", "cad", "llm", "api", "sdk", "cli", "saas", "sql", "wasm",
    "slam", "ros", "sast", "dast", "cve", "rbac", "abac", "wcag", "aria",
}

STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "for", "with", "in", "on", "of", "to", "at",
    "by", "from", "up", "about", "into", "over", "after", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "but", "if", "then", "else", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "can", "will",
    "just", "should", "now", "i", "we", "you", "my", "our", "your", "it", "its",
    "want", "need", "like", "using", "use", "based", "new",
}

GENERIC_ARTIFACT_TERMS: Set[str] = {
    "app", "application", "platform", "system", "tool", "tooling",
    "software", "solution", "project", "service", "engine", "framework",
    "builder", "suite", "module", "package", "library",
}

# Extensible Domain & Architectural Pattern Taxonomy
EXTENDED_DOMAIN_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "recruitment_talent_matching": {
        "triggers": {"recruit", "recruitment", "hiring", "candidate", "talent", "ats", "applicant", "resume", "cv", "job"},
        "core_problems": [
            "Unstructured resume document parsing",
            "Candidate-job semantic matching",
            "Algorithmic bias and disparate impact auditing",
            "Applicant tracking system (ATS) workflow integration",
        ],
        "implied_mechanisms": [
            "Two-stage semantic retrieval (bi-encoder + cross-encoder)",
            "Layout-aware document structure decomposition",
            "Disparate impact ratio metric auditing",
            "Bipartite graph talent matching",
        ],
        "technical_primitives": [
            "Vector similarity index",
            "Layout-aware document parser",
            "Fairness metric evaluation frame",
            "ATS connector API",
        ],
        "adjacent_industries": [
            "E-commerce Product Search",
            "Legal Tech Discovery",
            "Financial Credit Scoring",
            "Computational Biology",
        ],
        "analogous_mechanisms": [
            "Two-stage coarse-to-fine product re-ranking",
            "Gale-Shapley stable marriage matching",
            "Adverse impact statistical disparity tests",
        ],
        "academic_keywords": [
            "resume information extraction",
            "algorithmic fairness recruitment",
            "bipartite matching candidate ranking",
            "semantic candidate search",
        ],
    },
    "accessibility_testing_compliance": {
        "triggers": {"accessibility", "a11y", "wcag", "screenreader", "aria", "contrast", "keyboard navigation", "colorblind"},
        "core_problems": [
            "Automated WCAG rule conformance checking",
            "Accessibility tree (a11y tree) and DOM state traversal",
            "Interactive focus trap and keyboard flow verification",
            "Visual color contrast ratio evaluation",
        ],
        "implied_mechanisms": [
            "DOM and accessibility tree rule inspection",
            "Headless browser automated audit runner",
            "Declarative code linting with autofix",
            "Color luminance contrast ratio calculation",
        ],
        "technical_primitives": [
            "Accessibility rule engine",
            "Headless browser DOM runner",
            "A11y tree serializer",
            "AST code transformer",
        ],
        "adjacent_industries": [
            "Compiler Construction & Static Analysis",
            "Aircraft Avionics Verification",
            "Regulatory Financial Auditing",
        ],
        "analogous_mechanisms": [
            "Abstract syntax tree linter passes",
            "Formal methods invariant verification",
            "Continuous compliance monitoring",
        ],
        "academic_keywords": [
            "automated web accessibility evaluation",
            "WCAG compliance automated testing detection rate",
            "accessibility tree traversal",
        ],
    },
    "offline_first_collaborative_sync": {
        "triggers": {"offline", "offline-first", "crdt", "sync", "synchronization", "local-first", "p2p", "notes", "knowledge base"},
        "core_problems": [
            "Concurrent offline state mutation without data loss",
            "Conflict-free state reconciliation across network partitions",
            "Local embedded relational persistence",
            "End-to-end encrypted peer synchronization",
        ],
        "implied_mechanisms": [
            "Conflict-free Replicated Data Types (CRDT)",
            "Causal event ordering via logical clocks",
            "Delta-state synchronization",
            "Authenticated symmetric ratcheting (E2EE)",
        ],
        "technical_primitives": [
            "CRDT document engine",
            "Hybrid logical clock / vector clock",
            "Embedded SQLite storage engine",
            "Peer-to-peer transport / WebRTC",
        ],
        "adjacent_industries": [
            "Distributed Version Control",
            "Avionics Flight Data Sync",
            "Collaborative CAD & Spatial Mapping",
        ],
        "analogous_mechanisms": [
            "Git DAG commit reconciliation",
            "Flight-data recorder delta logging",
            "Merkle tree delta state exchange",
        ],
        "academic_keywords": [
            "conflict-free replicated data types",
            "causal consistency distributed systems",
            "local-first software architecture",
        ],
    },
    "robotics_autonomous_control": {
        "triggers": {"robot", "robotics", "drone", "actuator", "motor", "kinematics", "slam", "ros", "telemetry", "lidar", "sensor fusion"},
        "core_problems": [
            "Real-time sensor telemetry ingestion and fusion",
            "Closed-loop motion control under physical constraints",
            "Simultaneous localization and mapping (SLAM)",
            "Hardware-in-the-loop safety watchdog monitoring",
        ],
        "implied_mechanisms": [
            "Kalman filtering and state estimation",
            "Proportional-Integral-Derivative (PID) feedback loop",
            "Occupancy grid mapping",
            "Deterministic state machine execution",
        ],
        "technical_primitives": [
            "Extended Kalman filter (EKF)",
            "Real-time pub/sub bus",
            "Hardware abstraction layer (HAL)",
            "Ring buffer telemetry recorder",
        ],
        "adjacent_industries": [
            "Automotive Driver Assistance (ADAS)",
            "Industrial CNC Manufacturing",
            "Satellite Attitude Control",
            "Biomedical Patient Monitoring",
        ],
        "analogous_mechanisms": [
            "Dead-reckoning inertial navigation",
            "Watchdog timer heartbeat fail-safes",
            "Spacecraft fault-tolerant voter circuits",
        ],
        "academic_keywords": [
            "sensor fusion kalman filter",
            "autonomous robot trajectory planning",
            "real-time embedded control systems",
        ],
    },
    "supply_chain_logistics_forecasting": {
        "triggers": {"supply", "supply-chain", "logistics", "inventory", "forecasting", "forecast", "procurement", "dispatch", "routing", "warehouse", "demand"},
        "core_problems": [
            "Non-stationary demand time-series forecasting",
            "Multi-echelon inventory safety stock optimization",
            "Vehicle routing under capacity and time window constraints",
            "Supply chain disruption propagation modeling",
        ],
        "implied_mechanisms": [
            "Hierarchical time-series forecasting",
            "Mixed-Integer Linear Programming (MILP)",
            "Constraint satisfaction heuristics",
            "Buffer sizing under lead-time variance",
        ],
        "technical_primitives": [
            "Time-series forecasting model",
            "Constraint satisfaction solver",
            "Graph-based routing optimizer",
            "Discrete-event simulation engine",
        ],
        "adjacent_industries": [
            "Telecommunications Bandwidth Scheduling",
            "Airline Fleet Operations",
            "Semiconductor Fab Scheduling",
            "Epidemiological Resource Allocation",
        ],
        "analogous_mechanisms": [
            "Dijkstra / Bellman-Ford constrained routing",
            "Queueing network congestion backpressure",
            "Safety stock replenishment policies",
        ],
        "academic_keywords": [
            "supply chain inventory optimization",
            "demand forecasting mixed integer linear programming",
            "vehicle routing problem with time windows",
        ],
    },
    "security_code_analysis_tooling": {
        "triggers": {"security", "vulnerability", "scanner", "sast", "dast", "secret", "fuzzing", "exploit", "cve", "auth", "malware", "sandbox"},
        "core_problems": [
            "Static detection of source code vulnerabilities without excessive false positives",
            "Taint propagation from untrusted inputs to execution sinks",
            "Automated secret and API credential leak detection",
            "Dependency vulnerability supply chain traversal",
        ],
        "implied_mechanisms": [
            "Abstract syntax tree (AST) taint analysis",
            "High-entropy string secret scanning",
            "Control-flow graph (CFG) traversal",
            "Software bill-of-materials (SBOM) dependency graph resolution",
        ],
        "technical_primitives": [
            "AST visitor engine",
            "Taint propagation graph",
            "Entropy regex scanner",
            "Package lockfile dependency parser",
        ],
        "adjacent_industries": [
            "Airport Baggage Screening",
            "Epidemiological Contact Tracing",
            "Forensic Accounting & Fraud Auditing",
        ],
        "analogous_mechanisms": [
            "Automated baggage tomography anomaly detection",
            "Transaction ledger taint tracing",
            "Signature-based threat hashing",
        ],
        "academic_keywords": [
            "static taint analysis source code",
            "automated vulnerability detection AST",
            "software bill of materials vulnerability analysis",
        ],
    },
    "document_parsing_information_extraction": {
        "triggers": {"document", "pdf", "ocr", "layout", "extraction", "parser", "table extraction", "bounding box"},
        "core_problems": [
            "Multi-column unstructured layout reading order reconstruction",
            "Visual table and key-value pair extraction",
            "OCR noise and text segmentation correction",
            "Domain-specific entity normalization",
        ],
        "implied_mechanisms": [
            "Layout-aware visual object detection",
            "Spatial bounding-box reading order sort",
            "Optical character recognition (OCR) post-correction",
            "Heuristic key-value schema alignment",
        ],
        "technical_primitives": [
            "Layout-aware document parser",
            "Bounding-box spatial sorter",
            "OCR text segmentation engine",
            "Schema validator",
        ],
        "adjacent_industries": [
            "Digital Archival & Library Science",
            "Financial Invoice & Receipt Accounting",
            "Medical Records Digitization",
        ],
        "analogous_mechanisms": [
            "Visual layout block segmentation",
            "Form field coordinate mapping",
            "Double-entry invoice validation",
        ],
        "academic_keywords": [
            "document layout analysis",
            "information extraction unstructured documents",
            "multimodal document parsing reading order",
        ],
    },
    # Preserved original catalog entries for backward compatibility
    "consensus": {
        "triggers": {"consensus", "raft", "paxos", "byzantine"},
        "core_problems": ["Distributed agreement under network partitions", "Byzantine node tolerance"],
        "implied_mechanisms": ["Leader election", "Quorum consensus", "State machine replication"],
        "technical_primitives": ["Raft state machine", "Gossip broadcast", "Vector clock"],
        "adjacent_industries": ["Distributed Systems", "Sociology & Political Science", "Cryptographic Protocols"],
        "analogous_mechanisms": ["Raft/Paxos leader election", "Delphi method deliberation", "Byzantine fault tolerance"],
        "academic_keywords": ["consensus protocol", "delphi method", "social choice theory"],
    },
    "turn_taking": {
        "triggers": {"turn_taking", "turn-taking", "conversational floor", "floor control"},
        "core_problems": ["Channel collision avoidance", "Floor assignment latency"],
        "implied_mechanisms": ["Floor arbitration state machine", "Token-bucket pacing"],
        "technical_primitives": ["Floor control queue", "Media access controller"],
        "adjacent_industries": ["Avionics & Aerospace", "Interactive Drama / Game AI", "Telecommunications"],
        "analogous_mechanisms": ["Cockpit Resource Management sterile channel", "Drama manager beat scheduling", "Token bucket media access control"],
        "academic_keywords": ["conversational floor control", "turn-taking state machine", "audio collision resolution"],
    },
    "arbitration": {
        "triggers": {"arbitration", "conflict resolution", "clearing", "priority queue"},
        "core_problems": ["Resource contention resolution", "Fair allocation under load"],
        "implied_mechanisms": ["Triple modular redundancy voting", "Priority arbitration"],
        "technical_primitives": ["Priority queue", "Fair queue scheduler", "Order book matcher"],
        "adjacent_industries": ["Avionics", "Financial Exchanges", "Operating Systems"],
        "analogous_mechanisms": ["Triple modular redundancy voting", "Order book clearing arbiters", "Fair queuing schedulers"],
        "academic_keywords": ["priority arbitration", "conflict resolution algorithm", "resource scheduling"],
    },
    "memory": {
        "triggers": {"memory", "caching", "cache", "retrieval", "vector storage"},
        "core_problems": ["Associative retrieval latency", "Context window eviction"],
        "implied_mechanisms": ["Tiered cache eviction", "Episodic memory chunking"],
        "technical_primitives": ["Vector index", "LRU/LFU cache", "Associative memory stream"],
        "adjacent_industries": ["Cognitive Science", "Database Systems", "Operating Systems"],
        "analogous_mechanisms": ["ACT-R cognitive memory chunking", "Multi-tiered caching (L1/L2/Disk)", "Virtual memory page eviction"],
        "academic_keywords": ["episodic memory stream", "associative retrieval", "cognitive architecture"],
    },
    "debate": {
        "triggers": {"debate", "argumentation", "dialectic", "adversarial"},
        "core_problems": ["Adversarial reasoning validation", "Socratic dialectic loops"],
        "implied_mechanisms": ["Toulmin argumentation model", "Adversarial self-play"],
        "technical_primitives": ["Dialectic arbiter", "Argument graph validator"],
        "adjacent_industries": ["Formal Logic & Law", "Sociology", "Multi-Agent Reinforcement Learning"],
        "analogous_mechanisms": ["Toulmin argumentation model", "Socratic dialectic loops", "Adversarial self-play"],
        "academic_keywords": ["multi-agent debate", "dialectical argumentation", "adversarial reasoning"],
    },
    "simulation": {
        "triggers": {"simulation", "agent-based", "abm", "synthetic population"},
        "core_problems": ["Emergent behavior modeling", "Large-scale agent step execution"],
        "implied_mechanisms": ["Agent-based modeling (ABM)", "Utility AI / GOAP"],
        "technical_primitives": ["Discrete-event simulator", "Spatial grid index"],
        "adjacent_industries": ["Ecology & Epidemiology", "Video Game Systems", "Microeconomics"],
        "analogous_mechanisms": ["Agent-based modeling (ABM)", "Utility AI / GOAP", "Dynamic market equilibrium"],
        "academic_keywords": ["agent-based simulation", "artificial society", "emergent behavior"],
    },
    "streaming": {
        "triggers": {"streaming", "audio", "webrtc", "jitter buffer", "low latency"},
        "core_problems": ["Packet jitter and buffer underrun", "Backpressure propagation"],
        "implied_mechanisms": ["Ring buffer jitter management", "WebRTC RTP pacing"],
        "technical_primitives": ["Jitter buffer", "RTP packetizer", "Ring buffer"],
        "adjacent_industries": ["Signal Processing", "Telecommunications", "Industrial IoT"],
        "analogous_mechanisms": ["Ring buffer jitter management", "WebRTC RTP packet pacing", "Backpressure flow control"],
        "academic_keywords": ["real-time audio pipeline", "low latency streaming", "voice activity detection"],
    },
    "collaboration": {
        "triggers": {"collaboration", "collaborative", "multi-user", "shared editor"},
        "core_problems": ["Concurrent editing divergence", "Distributed state reconciliation"],
        "implied_mechanisms": ["Conflict-free Replicated Data Types", "Operational transformation"],
        "technical_primitives": ["CRDT state engine", "Vector clock", "WebSocket broadcast"],
        "adjacent_industries": ["Distributed Version Control", "Urban Planning", "Aviation"],
        "analogous_mechanisms": ["Conflict-free Replicated Data Types (CRDT)", "Collaborative spatial mapping", "Crew resource management"],
        "academic_keywords": ["real-time collaborative editing", "operational transformation", "distributed state synchronization"],
    },
}


def sanitize_input(text: str) -> str:
    """Trim and sanitize raw text input."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())


def normalize_keyword(kw: str) -> str:
    """Normalize keyword for deduplication."""
    return kw.strip().lower()


def extract_concept_tokens_and_phrases(concept: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Extract meaningful individual tokens, content bi-grams, and tri-grams from a concept string.
    Preserves critical short technical acronyms while filtering stopword noise.
    """
    raw_words = re.findall(r"\b[A-Za-z0-9_\-]+\b", concept)
    tokens: List[str] = []
    content_words: List[str] = []

    for w in raw_words:
        w_lower = w.lower()
        if w_lower in KNOWN_ACRONYMS or len(w_lower) >= 3:
            if w_lower not in STOPWORDS:
                tokens.append(w)
                content_words.append(w)

    # Extract 2-grams and 3-grams from content words
    n_grams: List[str] = []
    for i in range(len(content_words) - 1):
        bi = f"{content_words[i]} {content_words[i+1]}"
        n_grams.append(bi)
    for i in range(len(content_words) - 2):
        tri = f"{content_words[i]} {content_words[i+1]} {content_words[i+2]}"
        n_grams.append(tri)

    return tokens, content_words, n_grams


def fallback_morphological_decomposition(clean_concept: str, tokens: List[str], n_grams: List[str]) -> Dict[str, Any]:
    """
    Universal fallback for software concepts with zero catalog matches.
    Decomposes tokens using natural phrasing and domain-agnostic computational primitives.
    Avoids attaching generic software jargon to unrelated physical or scientific nouns.
    Clearly marks inferences as unverified with low confidence.
    """
    non_generic = [t for t in tokens if t.lower() not in GENERIC_ARTIFACT_TERMS]
    domain_terms = non_generic if non_generic else tokens

    primary_phrase = " ".join(domain_terms[:3]) if domain_terms else clean_concept
    spec_noun = domain_terms[0] if domain_terms else clean_concept

    # Problems grounded in computing fundamentals without robotic mad-libs
    core_problems = [
        f"Computational state modeling and data structures for {primary_phrase}",
        f"Simulation, numerical execution, or processing performance for {primary_phrase}",
        f"Boundary constraints and validation edge conditions in {primary_phrase}",
        f"API contract standardization and data exchange for {primary_phrase}",
    ]

    # Real computational mechanisms that apply across novel domains
    implied_mechanisms = [
        "Event-driven simulation loop",
        "Graph-based network topology mapping",
        "Deterministic state transition engine",
        "Spatial coordinate indexing and diffusion",
    ]

    # Domain-agnostic technical primitives commonly reused from open source
    technical_primitives = [
        "Discrete-event simulation engine",
        "Graph traversal algorithm",
        "Time-series data logger",
        "Embedded persistence storage layer",
    ]

    adjacent_industries = [
        "Scientific Computing & Simulation",
        "Distributed Systems & Telemetry",
        "Robotics & Sensor Networks",
        "Complex Systems & Network Science",
    ]

    analogous_mechanisms = [
        "Agent-based spatial modeling",
        "Publish-subscribe event decoupled streaming",
        "Finite-state automaton transition matrices",
    ]

    academic_keywords = [
        f"{clean_concept} computational model",
        f"{primary_phrase} simulation survey",
        f"{spec_noun} algorithmic methods",
    ]

    return {
        "core_problems": core_problems,
        "implied_mechanisms": implied_mechanisms,
        "technical_primitives": technical_primitives,
        "adjacent_industries": adjacent_industries,
        "analogous_mechanisms": analogous_mechanisms,
        "academic_keywords": academic_keywords,
    }


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
    from a software idea.
    """
    clean_concept = sanitize_input(concept)
    if not clean_concept:
        raise ValueError("Concept description cannot be empty.")

    user_problems = [sanitize_input(p) for p in (problems or []) if sanitize_input(p)]
    user_mechanisms = [sanitize_input(m) for m in (mechanisms or []) if sanitize_input(m)]
    user_primitives = [sanitize_input(p) for p in (technical_primitives or []) if sanitize_input(p)]
    user_patterns = [sanitize_input(p) for p in (behavioral_patterns or []) if sanitize_input(p)]
    user_verticals = [sanitize_input(v) for v in (adjacent_verticals or []) if sanitize_input(v)]

    # 1. Conservative Tokenization
    tokens, content_words, n_grams = extract_concept_tokens_and_phrases(clean_concept)
    searchable_text = f"{clean_concept} {' '.join(user_problems)} {' '.join(user_mechanisms)}".lower()

    # 2. Match against Extended Taxonomy
    matched_taxonomy_keys: List[str] = []
    aggregated_problems: List[str] = list(user_problems)
    aggregated_mechanisms: List[str] = list(user_mechanisms)
    aggregated_primitives: List[str] = list(user_primitives)
    aggregated_verticals: Set[str] = set(user_verticals)
    suggested_analogous_mechanisms: List[str] = []
    academic_keywords: List[str] = []

    for key, data in EXTENDED_DOMAIN_TAXONOMY.items():
        triggers = data.get("triggers", {key})
        is_match = False
        for trig in triggers:
            # Word boundary matching or substring for multi-word triggers
            if " " in trig or "-" in trig:
                if trig in searchable_text:
                    is_match = True
                    break
            else:
                if re.search(r"\b" + re.escape(trig), searchable_text):
                    is_match = True
                    break

        if is_match:
            matched_taxonomy_keys.append(key)
            for p in data.get("core_problems", []):
                if p not in aggregated_problems:
                    aggregated_problems.append(p)
            for m in data.get("implied_mechanisms", []):
                if m not in aggregated_mechanisms:
                    aggregated_mechanisms.append(m)
            for tp in data.get("technical_primitives", []):
                if tp not in aggregated_primitives:
                    aggregated_primitives.append(tp)
            for dom in data.get("adjacent_industries", []):
                aggregated_verticals.add(dom)
            suggested_analogous_mechanisms.extend(data.get("analogous_mechanisms", []))
            academic_keywords.extend(data.get("academic_keywords", []))

    # 3. Universal Fallback if no taxonomy matched or if components are sparse
    expansion_mode = "taxonomy_matched" if matched_taxonomy_keys else "heuristic_morphological_fallback"
    confidence = "high" if matched_taxonomy_keys else "low"
    if not matched_taxonomy_keys or len(aggregated_primitives) == 0:
        fallback_data = fallback_morphological_decomposition(clean_concept, tokens, n_grams)
        for p in fallback_data["core_problems"]:
            if p not in aggregated_problems:
                aggregated_problems.append(p)
        for m in fallback_data["implied_mechanisms"]:
            if m not in aggregated_mechanisms:
                aggregated_mechanisms.append(m)
        for tp in fallback_data["technical_primitives"]:
            if tp not in aggregated_primitives:
                aggregated_primitives.append(tp)
        for dom in fallback_data["adjacent_industries"]:
            aggregated_verticals.add(dom)
        suggested_analogous_mechanisms.extend(fallback_data["analogous_mechanisms"])
        academic_keywords.extend(fallback_data["academic_keywords"])

    # 4. Multi-Tier Query Construction
    all_emitted_queries: Set[str] = set()

    # Tier A: Direct Queries (GitHub & Existing Products)
    direct_queries: List[str] = []
    # Seed 1: The full concept or cleaned core concept
    direct_queries.append(clean_concept)
    # Seed 2: 2-grams and 3-grams from content words
    for ng in n_grams[:4]:
        if ng.lower() != clean_concept.lower():
            direct_queries.append(ng)
    # Seed 3: Explicit problems/mechanisms
    for p in aggregated_problems[:2]:
        direct_queries.append(p)
    for m in aggregated_mechanisms[:2]:
        direct_queries.append(m)

    # Clean and register direct queries
    clean_direct: List[str] = []
    for q in direct_queries:
        q_clean = sanitize_input(q)
        q_norm = normalize_keyword(q_clean)
        if q_clean and q_norm not in all_emitted_queries:
            all_emitted_queries.add(q_norm)
            clean_direct.append(q_clean)

    # Tier B: Technical Primitive Queries (excluding direct)
    clean_primitives: List[str] = []
    for prim in aggregated_primitives[:6]:
        prim_clean = sanitize_input(prim)
        prim_norm = normalize_keyword(prim_clean)
        if prim_clean and prim_norm not in all_emitted_queries:
            all_emitted_queries.add(prim_norm)
            clean_primitives.append(prim_clean)

    # Tier C: Cross-Vertical Queries (excluding direct and primitive)
    clean_cross: List[str] = []
    vertical_list = sorted(list(aggregated_verticals))
    mechanism_subset = aggregated_mechanisms[:3] or user_mechanisms[:3]
    for vert in vertical_list[:3]:
        for m in mechanism_subset[:2]:
            combo = f"{vert} {m}"
            combo_norm = normalize_keyword(combo)
            if combo_norm not in all_emitted_queries:
                all_emitted_queries.add(combo_norm)
                clean_cross.append(combo)
        for anal in suggested_analogous_mechanisms[:2]:
            combo = f"{vert} {anal}"
            combo_norm = normalize_keyword(combo)
            if combo_norm not in all_emitted_queries:
                all_emitted_queries.add(combo_norm)
                clean_cross.append(combo)

    # Tier D: Academic Research Queries (excluding prior queries)
    clean_academic: List[str] = []
    for ak in academic_keywords[:6]:
        ak_clean = sanitize_input(ak)
        ak_norm = normalize_keyword(ak_clean)
        if ak_clean and ak_norm not in all_emitted_queries:
            all_emitted_queries.add(ak_norm)
            clean_academic.append(ak_clean)

    for m in aggregated_mechanisms[:2]:
        alg_query = f"{m} algorithm"
        alg_norm = normalize_keyword(alg_query)
        if alg_norm not in all_emitted_queries:
            all_emitted_queries.add(alg_norm)
            clean_academic.append(alg_query)

    # 5. Formulate Unverified Hypotheses (Distinguished from facts)
    hypotheses: List[Dict[str, str]] = []
    top_mechanisms = (aggregated_mechanisms or ["core pipeline"])[:3]
    for m in top_mechanisms:
        hypotheses.append({
            "hypothesis": f"Hypothesis: The mechanism '{m}' has battle-tested open-source implementations outside the primary domain.",
            "verification_status": "UNVERIFIED_HYPOTHESIS",
            "evidence_required": "Source inspection of candidate repositories or working proof-of-concept.",
        })

    if vertical_list:
        primary_vert = vertical_list[0]
        hypotheses.append({
            "hypothesis": f"Hypothesis: Architectural constraints from {primary_vert} can transfer to resolve throughput and reliability bottlenecks in this concept.",
            "verification_status": "UNVERIFIED_HYPOTHESIS",
            "evidence_required": "Empirical comparison of architectural state machines between domains.",
        })

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
        "expansion_metadata": {
            "mode": expansion_mode,
            "confidence": confidence,
            "provenance": "[INFERRED-HEURISTIC]",
            "matched_taxonomy_domains": matched_taxonomy_keys,
            "extracted_tokens": tokens,
            "heuristic_expansion_disclosure": (
                "Decomposition derived via deterministic rule-based token decomposition without model reasoning. "
                "Inferred queries must be verified by the host agent."
            ),
            "refinement_guidance": (
                "Unfamiliar domain fallback (confidence: low). Host AI agent should inspect prompt context and "
                "refine heuristic queries with domain-specific terms (e.g. simulation models, mathematical formalisms, "
                "or hardware interfaces)."
                if confidence == "low" else
                "Taxonomy matched (confidence: high). Host AI agent should verify candidate repository availability."
            ),
        },
        "decomposition": {
            "core_problems": aggregated_problems[:5],
            "mechanisms": aggregated_mechanisms[:5],
            "technical_primitives": aggregated_primitives[:6],
            "behavioral_patterns": user_patterns,
            "adjacent_industries": vertical_list[:5],
            "suggested_analogous_mechanisms": sorted(list(set(suggested_analogous_mechanisms)))[:5],
        },
        "query_matrix": {
            "direct_queries": clean_direct[:8],
            "technical_primitive_queries": clean_primitives[:6],
            "cross_vertical_queries": clean_cross[:8],
            "academic_queries": clean_academic[:6],
        },
        "research_priorities": default_priorities,
        "hypotheses_to_verify": hypotheses,
    }


def format_text_plan(plan: Dict[str, Any]) -> str:
    """Format research plan as human-readable Markdown."""
    lines = []
    lines.append("# BeenHere Concept Expansion & Deterministic Research Plan\n")
    lines.append(f"**Target Concept:** {plan['original_concept']}\n")

    meta = plan.get("expansion_metadata", {})
    if meta:
        lines.append(f"> **Mode:** `{meta.get('mode')}` | **Provenance:** `{meta.get('provenance')}`  ")
        lines.append(f"> *Disclosure:* {meta.get('heuristic_expansion_disclosure')}\n")

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
        for am in decomp["suggested_analogous_mechanisms"]:
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
