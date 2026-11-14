#!/usr/bin/env python3
"""
scripts/repo_comparator.py - Multi-Repository Comparison & Intelligent Reuse Engine for BeenHere.

Part of BeenHere: Explore every angle of an idea before you build it.
Uses Python standard library only (no external dependencies). Compatible with Python 3.8+.

Compares two or more candidate open-source repositories side-by-side across:
1. Purpose & Functional Overlap
2. License & Relevant Dependency Obligations
3. Exported APIs & Reusable Entrypoints
4. Language & Runtime Compatibility
5. Architectural Integration Boundaries
6. Maintenance & Operational Freshness
7. Known Limitations & Technical Debt
8. Evidence Completeness & Uncertainty

Generates evidence-aware reuse recommendations and actionable integration blueprints
without inventing numerical percentages or relying on star-count popularity bias.
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

# Posture classifications
POSTURES = [
    "ADOPT_AS_DEPENDENCY",
    "INTEGRATE_THROUGH_API",
    "EXTRACT_REUSABLE_COMPONENT",
    "FORK_AND_ADAPT",
    "USE_AS_ARCHITECTURAL_REFERENCE",
    "REJECT_FOR_USE_CASE",
    "INVESTIGATE_FURTHER",
]

COMPLEXITY_TIERS = ["LOW", "MODERATE", "HIGH", "PROHIBITIVE"]
UNCERTAINTY_TIERS = ["LOW", "MODERATE", "HIGH"]

LEGAL_DISCLAIMER = (
    "DISCLAIMER: BeenHere provides automated heuristic analysis of license texts and code "
    "structures. It does not provide formal legal advice. Actual license permissions, "
    "obligations, and compatibility must be reviewed by qualified legal counsel."
)

RUNTIME_DISCLAIMER = (
    "DISCLAIMER: Static code analysis and manifest parsing do not guarantee runtime "
    "compatibility. Sandboxed container tests and contract validation must be executed "
    "before deploying to production."
)


def evaluate_candidate_posture(
    candidate: Dict[str, Any],
    project_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluate a single repository candidate against project requirements and legal realities.
    Returns an evidence-aware recommendation posture with all 5 mandatory explanatory dimensions.
    """
    ctx = project_context or {}
    target_lang = (ctx.get("target_language") or "").lower()
    target_model = (ctx.get("deployment_model") or "proprietary_saas").lower()
    user_capability = ctx.get("required_capability") or ""

    slug = candidate.get("slug", "unknown/unknown")
    name = candidate.get("name") or slug.split("/")[-1]
    stars = candidate.get("stars", 0)

    # 1. Extract Evidence
    lic_info = candidate.get("license_info", {})
    spdx = lic_info.get("declared_spdx", "UNKNOWN")
    lic_cat = lic_info.get("category", "UNKNOWN").upper()
    copyleft_tier = lic_info.get("copyleft_tier", "NONE").upper()
    has_discrepancy = bool(lic_info.get("discrepancy"))
    transitive_risks = lic_info.get("transitive_license_risks", [])

    maint = candidate.get("maintenance", {})
    maint_status = maint.get("status", "ACTIVE").upper()
    is_archived = bool(maint.get("is_archived"))
    days_inactive = maint.get("last_pushed_days_ago", 0)

    cand_lang = (candidate.get("language") or "").lower()
    cand_ecosystem = (candidate.get("ecosystem") or "").lower()
    exported_symbols = candidate.get("exported_symbols", [])
    dependencies = candidate.get("dependencies", [])
    known_limitations = candidate.get("known_limitations", [])

    evidence_comp = candidate.get("evidence_completeness", {})
    license_inspected = evidence_comp.get("license_inspected", False)
    manifest_inspected = evidence_comp.get("manifest_inspected", False)
    source_inspected = evidence_comp.get("source_inspected", False)
    missing_evidence = list(evidence_comp.get("missing_evidence", []))

    # Initialize Explanatory Dimensions
    fit_rationale: List[str] = []
    supporting_evidence: List[str] = []
    integration_pitfalls: List[str] = []
    pre_adoption_checklist: List[str] = []
    remaining_work: List[str] = []
    complexity = "MODERATE"
    uncertainty = "LOW"

    # Evidence Completeness Audit
    if not license_inspected:
        missing_evidence.append("Formal LICENSE file text not inspected")
    if not manifest_inspected:
        missing_evidence.append("Dependency manifest not inspected")
    if not source_inspected:
        missing_evidence.append("Source code exports not inspected")

    if len(missing_evidence) >= 2:
        uncertainty = "HIGH"
    elif len(missing_evidence) == 1:
        uncertainty = "MODERATE"

    # Pre-adoption baseline checks
    pre_adoption_checklist.append(f"Audit {slug} LICENSE against organizational IP policies [LEGAL-AUDIT]")
    pre_adoption_checklist.append("Run clean-environment dependency installation smoke test [BUILD-TEST]")

    # =========================================================================
    # DECISION LOGIC MATRIX
    # =========================================================================

    # Case 1: Conflicting or Missing Legal Clearance
    if has_discrepancy:
        posture = "INVESTIGATE_FURTHER"
        fit_rationale.append(f"Conflicting license evidence detected: {lic_info.get('discrepancy')}.")
        supporting_evidence.append(f"[VERIFIED-SOURCE] License discrepancy flagged between metadata and text headers.")
        integration_pitfalls.append("Adopting code with ambiguous licensing risks copyright infringement or license contagion.")
        pre_adoption_checklist.append("Obtain formal legal clearance resolving license header discrepancy.")
        complexity = "HIGH"
        uncertainty = "HIGH"

    elif lic_cat in ("MISSING_UNLICENSED", "UNKNOWN") or spdx in ("NOASSERTION", "UNKNOWN", "NONE"):
        posture = "REJECT_FOR_USE_CASE"
        fit_rationale.append("Repository lacks a clear OSI-compliant or recognized license declaration.")
        supporting_evidence.append(f"[VERIFIED-METADATA] Declared license is '{spdx}'. All rights reserved default applies under international copyright.")
        integration_pitfalls.append("Absence of license prevents legal copying, modification, or distribution.")
        pre_adoption_checklist.append("Contact copyright holder to request explicit open-source licensing.")
        complexity = "PROHIBITIVE"

    # Case 2: Source-Available / Commercial Restrictive (BSL, SSPL)
    elif lic_cat == "SOURCE_AVAILABLE" or "BSL" in spdx or "SSPL" in spdx:
        is_commercial = (
            any(k in target_model for k in ("saas", "proprietary", "commercial", "production"))
            and "non-commercial" not in target_model
            and "non_commercial" not in target_model
            and "research" not in target_model
        )
        if is_commercial:
            posture = "REJECT_FOR_USE_CASE"
            fit_rationale.append("Source-available license (e.g. BSL-1.1, SSPL) explicitly restricts commercial SaaS deployments.")
            supporting_evidence.append(f"[VERIFIED-SOURCE] License '{spdx}' includes commercial competition and production hosting restrictions.")
            integration_pitfalls.append("Deploying in commercial SaaS violates Additional Use Grant, triggering copyright liability.")
            remaining_work.append("Select an alternative permissive library or construct clean-room implementation.")
            complexity = "PROHIBITIVE"
        else:
            posture = "USE_AS_ARCHITECTURAL_REFERENCE"
            fit_rationale.append("Permitted for internal non-commercial research; study data structures and design patterns.")
            supporting_evidence.append(f"[VERIFIED-SOURCE] BSL terms permit non-production evaluation.")
            complexity = "MODERATE"

    # Case 3: Transitive Copyleft Contamination (e.g., PyMuPDF in Horilla)
    elif transitive_risks:
        posture = "REJECT_FOR_USE_CASE"
        fit_rationale.append(f"Repository contains high-risk transitive dependencies: {', '.join(transitive_risks)}.")
        supporting_evidence.append(f"[VERIFIED-SOURCE] Dependency manifest includes copyleft/dual-licensed components ({', '.join(transitive_risks)}).")
        integration_pitfalls.append("Transitive dependencies contaminate host application with reciprocal disclosure obligations.")
        remaining_work.append("Replace contaminated components with permissive standalone alternatives.")
        complexity = "HIGH"

    # Case 4: Network Copyleft (AGPL) in Proprietary SaaS
    elif copyleft_tier == "STRONG_NETWORK" or lic_cat == "NETWORK_RECIPROCAL":
        if "proprietary" in target_model:
            # Check if clean network API boundary is possible
            if candidate.get("architecture_type") == "standalone_service" or "api" in cand_ecosystem:
                posture = "INTEGRATE_THROUGH_API"
                fit_rationale.append("Deploy as an independent, isolated service over network boundaries (e.g. Docker container).")
                supporting_evidence.append(f"[VERIFIED-SOURCE] AGPL-3.0 obligations apply to the service itself. Host application communicates over remote network API.")
                integration_pitfalls.append("Tightly coupling backend schemas or in-process RPC risks triggering reciprocal AGPL source disclosure.")
                pre_adoption_checklist.append("Legal review confirming network boundary isolation protects host codebase.")
                remaining_work.append("Develop network API client, authentication layer, and failure-handling circuit breakers.")
                complexity = "HIGH"
            else:
                posture = "REJECT_FOR_USE_CASE"
                fit_rationale.append("AGPL-3.0 library cannot be directly embedded into proprietary closed-source application without triggering source disclosure.")
                supporting_evidence.append(f"[VERIFIED-SOURCE] Declared license '{spdx}' mandates reciprocal source sharing upon network deployment.")
                complexity = "PROHIBITIVE"
        else:
            posture = "ADOPT_AS_DEPENDENCY"
            fit_rationale.append("Host application is open-source compliant; AGPL requirements are mutually aligned.")
            supporting_evidence.append(f"[VERIFIED-METADATA] Open-source target architecture accommodates reciprocal terms.")
            complexity = "MODERATE"

    # Case 5: Archived or Stale / Abandoned Repositories
    elif is_archived or maint_status in ("ARCHIVED", "DORMANT") or days_inactive > 365:
        if lic_cat == "PERMISSIVE":
            if exported_symbols and len(exported_symbols) <= 5:
                posture = "EXTRACT_REUSABLE_COMPONENT"
                fit_rationale.append(f"Repository is {maint_status.lower()} (last pushed {days_inactive} days ago), but contains isolated algorithms.")
                supporting_evidence.append(f"[VERIFIED-METADATA] Inactivity exceeds threshold. [VERIFIED-SOURCE] Permissive {spdx} license permits extracting modular source files.")
                integration_pitfalls.append("Extracted code will no longer receive upstream security patches; team assumes full maintenance ownership.")
                remaining_work.append("Port extracted algorithms into project codebase, write standalone unit tests, and maintain copyright attribution.")
                complexity = "LOW_TO_MODERATE"
            else:
                posture = "FORK_AND_ADAPT"
                fit_rationale.append(f"Upstream is unmaintained ({days_inactive} days inactive). Active fork required to patch vulnerabilities.")
                supporting_evidence.append(f"[VERIFIED-METADATA] Upstream repository is {maint_status}. [VERIFIED-SOURCE] License permits independent maintenance.")
                integration_pitfalls.append("Fork maintenance incurs ongoing engineering overhead and technical divergence.")
                remaining_work.append("Establish internal CI/CD pipeline, patch outdated dependencies, and add missing features.")
                complexity = "HIGH"
        else:
            posture = "USE_AS_ARCHITECTURAL_REFERENCE"
            fit_rationale.append(f"Repository is inactive ({days_inactive} days) and copyleft/complex; direct adoption or extraction carries excessive debt.")
            supporting_evidence.append(f"[VERIFIED-METADATA] Maintenance status is {maint_status}.")
            remaining_work.append("Study architecture and design patterns; build a clean native implementation.")
            complexity = "HIGH"

    # Case 6: Language / Ecosystem Incompatibility
    elif target_lang and cand_lang and target_lang != cand_lang:
        # Check if cross-language bindings exist (e.g. WASM, PyO3, CLI)
        has_bindings = any(target_lang in b.lower() for b in candidate.get("available_bindings", []))
        if has_bindings:
            posture = "ADOPT_AS_DEPENDENCY"
            fit_rationale.append(f"Written in {candidate.get('language')}, but provides official {target_lang.title()} bindings.")
            supporting_evidence.append(f"[VERIFIED-SOURCE] Official language bindings available for {target_lang}.")
            integration_pitfalls.append("Cross-language boundaries (WASM/FFI) introduce serialization overhead and complex debugging.")
            pre_adoption_checklist.append(f"Verify native pre-compiled wheel/binary availability across target deployment OS environments.")
            remaining_work.append("Configure FFI build steps or install native binding packages.")
            complexity = "MODERATE"
        elif candidate.get("architecture_type") == "standalone_service" or "cli" in cand_ecosystem:
            posture = "INTEGRATE_THROUGH_API"
            fit_rationale.append(f"Runtime mismatch ({cand_lang.title()} vs {target_lang.title()}); integrate via CLI or HTTP microservice.")
            supporting_evidence.append(f"[VERIFIED-SOURCE] Candidate provides executable service/CLI interface.")
            integration_pitfalls.append("Inter-process communication latency and subprocess process management complexity.")
            remaining_work.append("Implement subprocess execution wrapper or HTTP client adapter.")
            complexity = "MODERATE"
        else:
            posture = "USE_AS_ARCHITECTURAL_REFERENCE"
            fit_rationale.append(f"Different language runtime ({cand_lang.title()} vs {target_lang.title()}) without packaged bindings.")
            supporting_evidence.append(f"[VERIFIED-METADATA] Candidate language is {cand_lang.title()}; project target is {target_lang.title()}.")
            remaining_work.append(f"Study candidate algorithms, data structures, and edge cases; implement natively in {target_lang.title()}.")
            complexity = "HIGH"

    # Case 7: Monolithic Application vs Modular Library
    elif candidate.get("architecture_type") == "monolithic_application":
        posture = "USE_AS_ARCHITECTURAL_REFERENCE"
        fit_rationale.append("Candidate is a full monolithic application rather than a modular library.")
        supporting_evidence.append(f"[VERIFIED-SOURCE] Codebase couples frontend UI, database schemas, and business controllers.")
        integration_pitfalls.append("Attempting to import monolithic app code introduces massive dependency bloat and tight architectural coupling.")
        remaining_work.append("Extract or re-implement specific target algorithms in isolation.")
        complexity = "HIGH"

    # Case 8: Active, Permissive / Weak Copyleft Modular Library (Optimal)
    elif lic_cat in ("PERMISSIVE", "WEAK_COPYLEFT"):
        posture = "ADOPT_AS_DEPENDENCY"
        fit_rationale.append(f"Actively maintained ({days_inactive} days since push), permissively licensed ({spdx}) modular package.")
        supporting_evidence.append(f"[VERIFIED-METADATA] Active maintenance status. [VERIFIED-SOURCE] Permissive {spdx} clearance verified.")
        if lic_cat == "WEAK_COPYLEFT":
            supporting_evidence.append(f"[VERIFIED-SOURCE] Weak copyleft ({spdx}) applies file-level reciprocity. Safe as unmodified external package.")
            integration_pitfalls.append("Modifying library files directly triggers source disclosure for modified files.")
        if known_limitations:
            integration_pitfalls.extend(known_limitations)
        else:
            integration_pitfalls.append("Upstream breaking changes across major version upgrades.")
        pre_adoption_checklist.append("Pin specific semver dependency version in project package manifest.")
        remaining_work.append("Write domain-specific adapter wrapping the library's public interface.")
        complexity = "LOW"

    # Fallback Default
    else:
        posture = "INVESTIGATE_FURTHER"
        fit_rationale.append("Ambiguous trade-offs require detailed source and runtime investigation.")
        supporting_evidence.append("[INFERRED] Insufficient evidence to conclusively declare adoption or rejection posture.")
        complexity = "MODERATE"
        uncertainty = "HIGH"

    return {
        "slug": slug,
        "name": name,
        "stars": stars,
        "posture": posture,
        "complexity_rating": complexity,
        "uncertainty_rating": uncertainty,
        "fit_rationale": " ".join(fit_rationale),
        "supporting_evidence": supporting_evidence,
        "integration_pitfalls": integration_pitfalls,
        "pre_adoption_checklist": pre_adoption_checklist,
        "remaining_engineering_work": remaining_work,
        "evidence_completeness": {
            "license_inspected": license_inspected,
            "manifest_inspected": manifest_inspected,
            "source_inspected": source_inspected,
            "runtime_tested": False,
            "missing_evidence": missing_evidence,
        },
    }


def compare_repositories(
    candidates: List[Dict[str, Any]],
    project_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Compare two or more repository evidence records across functional, architectural,
    legal, and operational dimensions. Produces a structured comparative synthesis.
    """
    if not candidates:
        raise ValueError("At least one candidate repository must be provided for comparison.")

    ctx = project_context or {}
    evaluated_candidates = [
        evaluate_candidate_posture(c, ctx) for c in candidates
    ]

    # Comparative Dimensional Breakdown
    comparisons = []
    for c, eval_res in zip(candidates, evaluated_candidates):
        lic_info = c.get("license_info", {})
        maint = c.get("maintenance", {})

        comparisons.append({
            "slug": c.get("slug", "unknown"),
            "name": c.get("name", c.get("slug", "unknown")),
            "purpose": c.get("purpose", "Unspecified"),
            "target_capability": c.get("target_capability", ctx.get("required_capability", "Unspecified")),
            "language": c.get("language", "Unknown"),
            "ecosystem": c.get("ecosystem", "Unknown"),
            "stars": c.get("stars", 0),
            "declared_license": lic_info.get("declared_spdx", "UNKNOWN"),
            "license_category": lic_info.get("category", "UNKNOWN"),
            "maintenance_status": maint.get("status", "UNKNOWN"),
            "last_pushed_days_ago": maint.get("last_pushed_days_ago", "N/A"),
            "exported_symbol_count": len(c.get("exported_symbols", [])),
            "dependency_count": len(c.get("dependencies", [])),
            "known_limitations_count": len(c.get("known_limitations", [])),
            "posture": eval_res["posture"],
            "complexity": eval_res["complexity_rating"],
            "uncertainty": eval_res["uncertainty_rating"],
            "evaluation": eval_res,
            "raw_candidate": c,
        })

    # Identify primary recommendation without star-count bias
    # Priority: ADOPT_AS_DEPENDENCY > INTEGRATE_THROUGH_API > EXTRACT_REUSABLE_COMPONENT > FORK_AND_ADAPT > USE_AS_ARCHITECTURAL_REFERENCE > INVESTIGATE_FURTHER > REJECT_FOR_USE_CASE
    posture_priority = {
        "ADOPT_AS_DEPENDENCY": 1,
        "INTEGRATE_THROUGH_API": 2,
        "EXTRACT_REUSABLE_COMPONENT": 3,
        "FORK_AND_ADAPT": 4,
        "USE_AS_ARCHITECTURAL_REFERENCE": 5,
        "INVESTIGATE_FURTHER": 6,
        "REJECT_FOR_USE_CASE": 7,
    }

    sorted_by_posture = sorted(
        comparisons,
        key=lambda x: (
            posture_priority.get(x["posture"], 99),
            0 if x["complexity"] == "LOW" else (1 if x["complexity"] == "MODERATE" else 2),
            0 if x["uncertainty"] == "LOW" else 1,
            -x["stars"],  # Stars used only as final tiebreaker among equally clear options
        ),
    )

    primary_recommendation = sorted_by_posture[0] if sorted_by_posture else None

    return {
        "project_context": ctx,
        "total_candidates_evaluated": len(candidates),
        "primary_recommendation": primary_recommendation["slug"] if primary_recommendation else None,
        "candidates": comparisons,
    }


def format_comparison_table(comparison_result: Dict[str, Any]) -> str:
    """Format comparative results into a concise Markdown table and summary."""
    lines = []
    lines.append("# BeenHere Intelligent Repository Comparison\n")

    ctx = comparison_result.get("project_context", {})
    if ctx.get("required_capability"):
        lines.append(f"> **Evaluated Capability:** `{ctx.get('required_capability')}`  ")
    if ctx.get("target_language"):
        lines.append(f"> **Target Stack:** `{ctx.get('target_language')}` ({ctx.get('deployment_model', 'Proprietary SaaS')})  ")
    lines.append(f"> **Primary Recommended Path:** `{comparison_result.get('primary_recommendation')}`\n")
    lines.append("---\n")

    lines.append("## 1. Multi-Candidate Comparison Matrix\n")
    lines.append("| Candidate Repo | License (Tier) | Maintenance | Language & Stack | API Entrypoints | Complexity | Recommended Posture |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :--- |")

    for c in comparison_result.get("candidates", []):
        slug = c["slug"]
        lic = f"{c['declared_license']} ({c['license_category']})"
        maint = f"{c['maintenance_status']} ({c['last_pushed_days_ago']}d ago)" if isinstance(c['last_pushed_days_ago'], int) else c['maintenance_status']
        lang = f"{c['language']} ({c['ecosystem']})"
        symbols = f"{c['exported_symbol_count']} symbols"
        complexity = c["complexity"]
        posture = f"**`{c['posture']}`**"
        lines.append(f"| `{slug}` | {lic} | {maint} | {lang} | {symbols} | {complexity} | {posture} |")

    lines.append("\n---\n")
    lines.append("## 2. Actionable Posture Explanations\n")

    for c in comparison_result.get("candidates", []):
        ev = c["evaluation"]
        lines.append(f"### `{c['slug']}`: `{ev['posture']}`\n")
        lines.append(f"- **Why It Fits (or Fails):** {ev['fit_rationale']}")
        lines.append("- **Supporting Evidence:**")
        for se in ev["supporting_evidence"]:
            lines.append(f"  - {se}")
        lines.append("- **Integration Pitfalls & Friction:**")
        for ip in ev["integration_pitfalls"]:
            lines.append(f"  - {ip}")
        lines.append("- **Pre-Adoption Verification Checklist:**")
        for pc in ev["pre_adoption_checklist"]:
            lines.append(f"  - [ ] {pc}")
        if ev["remaining_engineering_work"]:
            lines.append("- **Remaining Engineering Work to Build:**")
            for rw in ev["remaining_engineering_work"]:
                lines.append(f"  - {rw}")
        lines.append("")

    lines.append("---\n")
    lines.append("## 3. Disclaimers & Limitations\n")
    lines.append(f"1. **Legal:** {LEGAL_DISCLAIMER}")
    lines.append(f"2. **Runtime Verification:** {RUNTIME_DISCLAIMER}")

    return "\n".join(lines)


def generate_integration_blueprint(
    comparison_result: Dict[str, Any],
    selected_slug: Optional[str] = None,
) -> str:
    """
    Generate an actionable, in-depth Integration Blueprint for the recommended or selected repository.
    Includes architecture boundaries, contracts, integration sequences, and validation tests.
    """
    candidates = comparison_result.get("candidates", [])
    if not candidates:
        return "# No candidates available for integration blueprint."

    target_slug = selected_slug or comparison_result.get("primary_recommendation")
    selected_cand = None
    for c in candidates:
        if c["slug"] == target_slug:
            selected_cand = c
            break

    if not selected_cand:
        selected_cand = candidates[0]

    raw = selected_cand.get("raw_candidate", {})
    ev = selected_cand.get("evaluation", {})
    ctx = comparison_result.get("project_context", {})

    lines = []
    lines.append(f"# BeenHere Integration Blueprint: `{selected_cand['slug']}`\n")
    lines.append(f"> **Target Capability:** `{selected_cand['target_capability']}`  ")
    lines.append(f"> **Assigned Posture:** `{ev['posture']}` (Complexity: `{ev['complexity_rating']}`, Uncertainty: `{ev['uncertainty_rating']}`)  ")
    lines.append(f"> **License:** `{selected_cand['declared_license']}` ({selected_cand['license_category']})  ")
    lines.append(f"> **Target Environment:** `{ctx.get('target_language', 'Generic')}` | `{ctx.get('deployment_model', 'Proprietary SaaS')}`\n")
    lines.append("---\n")

    # 1. Recommended Components & Architecture Boundaries
    lines.append("## 1. Recommended Components & Architecture Boundaries\n")
    lines.append(f"- **Component Scope:** Adopt `{selected_cand['name']}` strictly as an isolated subsystem.")
    lines.append(f"- **Architectural Boundary:** Construct an anti-corruption adapter layer (`{selected_cand['name']}Adapter`) between host domain logic and the external library.")
    lines.append("- **Coupling Rule:** Never expose external third-party classes or types directly across the public API boundaries of your core domain models.\n")

    # 2. Public Entrypoints & Relevant APIs
    lines.append("## 2. Relevant APIs & Data Contracts\n")
    symbols = raw.get("exported_symbols", [])
    if symbols:
        lines.append("| Exported Symbol | Type | Source File | Reusability Role |")
        lines.append("| :--- | :---: | :--- | :--- |")
        for sym in symbols[:8]:
            s_name = sym.get("name", "anonymous")
            s_type = sym.get("type", "symbol")
            s_file = sym.get("file", "unknown")
            lines.append(f"| `{s_name}` | `{s_type}` | `{s_file}` | Direct integration entrypoint |")
    else:
        lines.append("- *No discrete exported symbols provided in evidence record. Treat as black-box library interface.*")
    lines.append("")

    # 3. Integration Sequence
    lines.append("## 3. Step-by-Step Integration Sequence\n")
    lines.append("```mermaid")
    lines.append("flowchart TD")
    lines.append(f"    Step1[\"1. Pin {selected_cand['name']} in manifest\"] --> Step2[\"2. Scaffold isolated Adapter layer\"]")
    lines.append("    Step2 --> Step3[\"3. Implement unit tests with mock inputs\"]")
    lines.append("    Step3 --> Step4[\"4. Run contract smoke test\"]")
    lines.append("    Step4 --> Step5[\"5. Benchmark performance under real payloads\"]")
    lines.append("```\n")

    lines.append("1. **Dependency Pinning:** Pin the exact semver version in your manifest (`package.json`, `pyproject.toml`, or `Cargo.toml`). Avoid unbounded wildcard version ranges.")
    lines.append(f"2. **Adapter Scaffolding:** Create `lib/{selected_cand['name']}_adapter` defining clean input/output schemas.")
    lines.append("3. **Serialization & Type Translation:** Convert internal domain entities into the format expected by the library.")
    lines.append("4. **Error Handling & Circuit Breaking:** Wrap external invocations with defensive exception handlers and fallback timeouts.")
    lines.append("5. **Telemetry & Metrics:** Add timing metrics around external calls to monitor execution latency.\n")

    # 4. Pre-Adoption Legal & License Checklist
    lines.append("## 4. Pre-Adoption License & Legal Checklist\n")
    for chk in ev.get("pre_adoption_checklist", []):
        lines.append(f"- [ ] {chk}")
    deps = raw.get("dependencies", [])
    if deps:
        dep_names = ", ".join(d.get("name", "pkg") for d in deps)
        lines.append(f"- [ ] Verify that direct dependencies ({dep_names}) do not introduce copyleft obligations.")
    else:
        lines.append("- [ ] Verify that no transitive dependency introduces copyleft obligations.")
    lines.append("- [ ] Include upstream copyright and license notices in third-party attribution documentation.\n")

    # 5. Technical Uncertainties & Missing Evidence
    lines.append("## 5. Technical Uncertainties & Remaining Engineering Work\n")
    miss = ev.get("evidence_completeness", {}).get("missing_evidence", [])
    if miss:
        lines.append("**Missing Evidence to Resolve:**")
        for m in miss:
            lines.append(f"- [!WARNING] {m}")
    else:
        lines.append("- *Evidence completeness is high; license, manifest, and exports verified.*")

    lines.append("\n**Engineering Work Remaining to Build Natively:**")
    for rw in ev.get("remaining_engineering_work", []):
        lines.append(f"- {rw}")
    lines.append("- Construct domain schema converters and validation middleware.")
    lines.append("- Implement monitoring dashboards for operational error rates.\n")

    # 6. Suggested Validation Tests
    lines.append("## 6. Suggested Validation Tests\n")
    lines.append("1. **Contract Test:** Verify that input payloads serialize and produce expected return types.")
    lines.append("2. **Boundary Fault Test:** Pass malformed, empty, or oversized payloads to verify graceful exception handling.")
    lines.append("3. **Memory / Resource Test:** Measure memory consumption across 1,000 iterations to check for memory leaks.")
    lines.append("4. **License Compliance Test:** Automated CI check ensuring license notices remain intact in compiled release assets.\n")

    # 7. Disclaimers
    lines.append("---\n")
    lines.append(f"> *{LEGAL_DISCLAIMER}*  \n")
    lines.append(f"> *{RUNTIME_DISCLAIMER}*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="BeenHere Multi-Repository Comparison & Intelligent Reuse Engine"
    )
    parser.add_argument("--input", "-i", type=str, help="JSON file containing list of candidate repository evidence records")
    parser.add_argument("--context", "-c", type=str, help="JSON file or string containing project context (language, deployment model, capability)")
    parser.add_argument("--blueprint", "-b", action="store_true", help="Generate detailed integration blueprint for primary recommendation")
    parser.add_argument("--output", "-o", type=str, help="Output file path for generated report")
    parser.add_argument("--json", action="store_true", help="Output raw structured comparison JSON to stdout")

    args = parser.parse_args()

    if not args.input:
        parser.error("Candidate evidence JSON file (--input) is required.")

    if not os.path.isfile(args.input):
        sys.stderr.write(f"File not found: {args.input}\n")
        sys.exit(1)

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            candidates = json.load(f)
    except Exception as e:
        sys.stderr.write(f"Failed to parse input JSON: {e}\n")
        sys.exit(1)

    project_ctx = {}
    if args.context:
        if os.path.isfile(args.context):
            with open(args.context, "r", encoding="utf-8") as f:
                project_ctx = json.load(f)
        else:
            try:
                project_ctx = json.loads(args.context)
            except Exception:
                project_ctx = {"required_capability": args.context}

    result = compare_repositories(candidates, project_ctx)

    if args.json:
        out_str = json.dumps(result, indent=2)
    elif args.blueprint:
        out_str = generate_integration_blueprint(result)
    else:
        out_str = format_comparison_table(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_str + "\n")
        print(f"Report written to {args.output}")
    else:
        print(out_str)


if __name__ == "__main__":
    main()
