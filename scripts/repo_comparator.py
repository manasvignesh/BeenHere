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
import datetime
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


def resolve_item_provenance(cand_provenance: str, is_inspected: bool) -> str:
    """Resolve item provenance type, preserving fixture and cache designations."""
    if cand_provenance in ("SCENARIO_FIXTURE", "CACHED_RECORD"):
        return cand_provenance
    return "LIVE_VERIFIED" if is_inspected else "CACHED_RECORD"


def create_evidence_record(
    claim: str,
    provenance_type: str,
    source_id: str,
    source_type: str,
    retrieval_timestamp: Optional[str] = None,
    excerpt_or_symbol: Optional[str] = None,
    verification_method: str = "TEXT_MATCH",
    limitations: str = "",
) -> Dict[str, Any]:
    """
    Construct a machine-readable evidence record with verifiable provenance.
    Distinguishes live verified data, cached records, scenario fixtures, inferences, and unverified claims.
    """
    clean_claim = claim
    for fabricated_tag in ("[VERIFIED-SOURCE]", "[VERIFIED-METADATA]", "[VERIFIED-TEST]"):
        if fabricated_tag in clean_claim:
            clean_claim = clean_claim.replace(fabricated_tag, "").strip()

    tag_map = {
        "LIVE_VERIFIED": "[VERIFIED-LIVE]",
        "CACHED_RECORD": "[VERIFIED-CACHED]",
        "SCENARIO_FIXTURE": "[SCENARIO-FIXTURE]",
        "INFERRED": "[INFERRED]",
        "MISSING_EVIDENCE": "[MISSING-EVIDENCE]",
        "UNVERIFIED_CLAIM": "[UNVERIFIED-CLAIM]",
    }
    tag = tag_map.get(provenance_type, "[INFERRED]")
    formatted_text = f"{tag} {clean_claim}"
    if limitations:
        formatted_text += f" (Note: {limitations})"

    return {
        "claim": clean_claim,
        "provenance_type": provenance_type,
        "source_id": source_id,
        "source_type": source_type,
        "retrieval_timestamp": retrieval_timestamp,
        "excerpt_or_symbol": excerpt_or_symbol,
        "verification_method": verification_method,
        "limitations": limitations,
        "tag": tag,
        "formatted_text": formatted_text,
    }


def evaluate_candidate_posture(
    candidate: Dict[str, Any],
    project_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluate a single repository candidate against project requirements and legal realities.
    Returns an evidence-aware recommendation posture with all 5 mandatory explanatory dimensions
    and the 6-part qualified legal risk assessment.
    """
    ctx = project_context or {}
    target_lang = (ctx.get("target_language") or "").lower()
    target_model = (ctx.get("deployment_model") or "proprietary_saas").lower()
    user_capability = (ctx.get("required_capability") or "").lower()

    slug = candidate.get("slug") or candidate.get("repository", "unknown/unknown")
    name = candidate.get("name") or slug.split("/")[-1]
    stars = candidate.get("stars") if "stars" in candidate else candidate.get("stargazers_count", 0)
    cand_purpose = candidate.get("purpose") or candidate.get("description", "")
    cand_capability = (candidate.get("target_capability") or "").lower()

    # Provenance and Snapshot Metadata
    cand_provenance = candidate.get("provenance_type")
    is_fixture = bool(candidate.get("is_fixture"))
    retrieval_ts = candidate.get("retrieval_timestamp") or candidate.get("snapshot_date") or candidate.get("inspected_at")
    if not cand_provenance:
        if is_fixture or "evaluations" in str(candidate.get("source_file", "")):
            cand_provenance = "SCENARIO_FIXTURE"
        else:
            cand_provenance = "LIVE_VERIFIED" if (candidate.get("evidence_completeness", {}).get("source_inspected") or candidate.get("verification_depth") == "SOURCE_CODE_INSPECTED") else "CACHED_RECORD"

    # 1. Extract Evidence
    lic_info = candidate.get("license_info")
    if not lic_info and isinstance(candidate.get("license"), dict):
        raw_lic = candidate["license"]
        spdx_val = raw_lic.get("spdx_id") or raw_lic.get("key") or "UNKNOWN"
        cat_val = (raw_lic.get("category") or "UNKNOWN").upper()
        lic_info = {
            "declared_spdx": spdx_val,
            "category": cat_val,
            "copyleft_tier": "STRONG_NETWORK" if cat_val == "NETWORK_RECIPROCAL" else ("RECIPROCAL" if cat_val == "RECIPROCAL_ON_DISTRIBUTION" else "NONE"),
            "license_file_inspected": candidate.get("verification_depth") == "SOURCE_CODE_INSPECTED" or bool(spdx_val and spdx_val != "UNKNOWN"),
        }
    elif not lic_info:
        lic_info = {}

    spdx = lic_info.get("declared_spdx", "UNKNOWN")
    lic_cat = lic_info.get("category", "UNKNOWN").upper()
    copyleft_tier = lic_info.get("copyleft_tier", "NONE").upper()
    has_discrepancy = bool(lic_info.get("discrepancy"))
    transitive_risks = lic_info.get("transitive_license_risks", [])
    transitive_linkage = lic_info.get("transitive_linkage") or lic_info.get("linkage") or "bundled"
    transitive_linkage = str(transitive_linkage).lower()
    is_dual_licensed = bool(lic_info.get("dual_licensing") or " OR " in spdx)
    commercial_terms = lic_info.get("commercial_terms", "unspecified").lower()
    bsl_grant_details = lic_info.get("bsl_grant_details") or {}

    maint = candidate.get("maintenance", {})
    maint_status = maint.get("status", "ACTIVE").upper()
    is_archived = bool(maint.get("is_archived"))
    days_inactive = maint.get("last_pushed_days_ago") if "last_pushed_days_ago" in maint else maint.get("days_since_last_push", 0)
    is_stale_snapshot = bool(maint.get("stale_metadata") or maint.get("is_stale_snapshot"))

    cand_lang = (candidate.get("language") or candidate.get("primary_language") or "").lower()
    cand_ecosystem = (candidate.get("ecosystem") or "").lower()
    exported_symbols = candidate.get("exported_symbols", [])
    dependencies = candidate.get("dependencies", [])
    known_limitations = candidate.get("known_limitations", [])

    evidence_comp = candidate.get("evidence_completeness")
    if not evidence_comp:
        v_depth = candidate.get("verification_depth", "")
        evidence_comp = {
            "license_inspected": bool(lic_info.get("license_file_inspected") or (spdx not in ("UNKNOWN", "NOASSERTION", "NONE"))),
            "manifest_inspected": bool(candidate.get("manifests_detected")),
            "source_inspected": v_depth == "SOURCE_CODE_INSPECTED" or bool(candidate.get("inspected_source_files")),
            "runtime_tested": False,
            "missing_evidence": [],
        }
        if not evidence_comp["source_inspected"]:
            evidence_comp["missing_evidence"].append("Source code exports not inspected")

    license_inspected = bool(evidence_comp.get("license_inspected", False))
    manifest_inspected = bool(evidence_comp.get("manifest_inspected", False))
    source_inspected = bool(evidence_comp.get("source_inspected", False))
    runtime_tested = bool(evidence_comp.get("runtime_tested", False))
    missing_evidence = list(evidence_comp.get("missing_evidence", []))

    # Initialize Explanatory Dimensions
    fit_rationale: List[str] = []
    supporting_evidence: List[str] = []
    evidence_records: List[Dict[str, Any]] = []
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
    if not runtime_tested:
        missing_evidence.append("Runtime container testing not executed")

    # Stale Snapshot Flagging
    stale_note = ""
    if is_stale_snapshot or (isinstance(days_inactive, int) and days_inactive > 365):
        stale_note = f"Activity timestamp ({days_inactive}d ago) reflects historical snapshot; live repository status unconfirmed."
        missing_evidence.append("Live repository maintenance status unverified")

    # Base uncertainty calculation
    if len(missing_evidence) >= 3 or not license_inspected:
        uncertainty = "HIGH"
    elif len(missing_evidence) >= 1:
        uncertainty = "MODERATE"

    # Pre-adoption baseline checks
    pre_adoption_checklist.append(f"Audit {slug} LICENSE against organizational IP policies [LEGAL-AUDIT]")
    pre_adoption_checklist.append("Run clean-environment dependency installation smoke test [BUILD-TEST]")

    # =========================================================================
    # THE SIX LEGAL ASSESSMENT DIMENSIONS
    # =========================================================================
    confirmed_license = (
        f"{spdx} ({lic_cat}) confirmed via LICENSE file text inspection"
        if license_inspected and spdx not in ("UNKNOWN", "NOASSERTION", "NONE")
        else f"{spdx} declared in metadata (UNCONFIRMED - LICENSE file text uninspected)"
    )

    dep_count = len(dependencies)
    observed_deps = f"Direct dependencies: {dep_count} packages inspected."
    if transitive_risks:
        observed_deps += f" Transitive copyleft flags: {', '.join(transitive_risks)} (Linkage: {transitive_linkage})."

    potential_obligations = "Standard copyright attribution notice retention in source and binary assets."
    if lic_cat == "WEAK_COPYLEFT":
        potential_obligations = f"Modifications to {slug} source files must be shared under {spdx}. Unmodified dynamic consumption does not attach to host."
    elif lic_cat in ("RECIPROCAL_ON_DISTRIBUTION", "STRONG_COPYLEFT"):
        potential_obligations = f"Distributing client binaries or derivative works requires disclosing complete corresponding source under {spdx}."
    elif lic_cat in ("NETWORK_RECIPROCAL", "STRONG_NETWORK"):
        potential_obligations = f"Network deployment triggers complete corresponding source disclosure of network service under {spdx}."
    elif lic_cat == "SOURCE_AVAILABLE":
        potential_obligations = f"Subject to licensor's Additional Use Grant; commercial production hosting restricts competitive offerings."
    elif lic_cat in ("MISSING_UNLICENSED", "UNKNOWN"):
        potential_obligations = "All Rights Reserved default under Berne Convention. No reuse permitted without explicit license."

    unresolved_questions = "None identified based on inspected evidence."
    if has_discrepancy:
        unresolved_questions = f"License discrepancy between manifest and headers must be reconciled: {lic_info.get('discrepancy')}."
    elif is_dual_licensed and commercial_terms in ("unspecified", "unknown"):
        unresolved_questions = "Dual licensing commercial terms, fee schedule, and grant scope are unverified."
    elif transitive_risks and transitive_linkage in ("unknown", "unverified"):
        unresolved_questions = "Transitive dependency linkage boundary (dynamic vs static vs CLI) is unconfirmed."
    elif "BSL" in spdx and not bsl_grant_details:
        unresolved_questions = "Specific terms of the BSL Additional Use Grant are uninspected."

    technical_incompatibilities = "None confirmed based on inspected contracts."
    if target_lang and cand_lang and target_lang != cand_lang and not any(target_lang in b.lower() for b in candidate.get("available_bindings", [])):
        technical_incompatibilities = f"Runtime mismatch: written in {cand_lang.title()}, target stack is {target_lang.title()} with no packaged bindings."
    elif candidate.get("architecture_type") == "monolithic_application":
        technical_incompatibilities = "Architecture is a monolithic full-stack application; modular library import impossible without extraction."

    org_policy_reqs = "Standard open-source inventory logging and attribution review."
    if "AGPL" in spdx or copyleft_tier == "STRONG_NETWORK":
        org_policy_reqs = "Corporate open-source policy and compliance review required (many organizations ban AGPL software regardless of network isolation)."
    elif "BSL" in spdx or lic_cat == "SOURCE_AVAILABLE":
        org_policy_reqs = "Procurement review required to verify commercial subscription obligations for source-available code."

    # =========================================================================
    # DECISION LOGIC MATRIX
    # =========================================================================

    # Case 1: Conflicting Legal Clearance
    if has_discrepancy:
        posture = "INVESTIGATE_FURTHER"
        fit_rationale.append(f"Conflicting license evidence detected: {lic_info.get('discrepancy')}.")
        rec = create_evidence_record(
            claim=f"License discrepancy detected: {lic_info.get('discrepancy')}",
            provenance_type=resolve_item_provenance(cand_provenance, license_inspected),
            source_id=lic_info.get("source_url") or slug,
            source_type="LICENSE_FILE",
            retrieval_timestamp=retrieval_ts,
            verification_method="TEXT_MATCH",
            limitations="Contradiction between manifest and source file text headers.",
        )
        supporting_evidence.append(rec["formatted_text"])
        evidence_records.append(rec)
        integration_pitfalls.append("Adopting code with ambiguous licensing risks copyright infringement or license contagion.")
        pre_adoption_checklist.append("Obtain formal legal clearance resolving license header discrepancy.")
        complexity = "HIGH"
        uncertainty = "HIGH"

    # Case 2: Missing or Unlicensed Code
    elif lic_cat in ("MISSING_UNLICENSED", "UNKNOWN") or spdx in ("NOASSERTION", "UNKNOWN", "NONE"):
        posture = "REJECT_FOR_USE_CASE"
        fit_rationale.append("Repository lacks a clear OSI-compliant or recognized license declaration.")
        rec = create_evidence_record(
            claim=f"Declared license is '{spdx}'. All rights reserved default applies under international copyright law.",
            provenance_type=resolve_item_provenance(cand_provenance, license_inspected),
            source_id=slug,
            source_type="API_METADATA",
            retrieval_timestamp=retrieval_ts,
            verification_method="TEXT_MATCH",
            limitations="No OSI-approved license text located in repository root.",
        )
        supporting_evidence.append(rec["formatted_text"])
        evidence_records.append(rec)
        integration_pitfalls.append("Absence of license prevents legal copying, modification, or distribution.")
        pre_adoption_checklist.append("Contact copyright holder to request explicit open-source licensing.")
        complexity = "PROHIBITIVE"
        uncertainty = "LOW" if license_inspected else "HIGH"

    # Case 3: Dual Licensing with Unknown Commercial Terms
    elif is_dual_licensed and commercial_terms in ("unspecified", "unknown"):
        posture = "INVESTIGATE_FURTHER"
        fit_rationale.append(f"Dual-licensed codebase ({spdx}). Commercial terms and licensing costs are unverified.")
        rec = create_evidence_record(
            claim=f"Dual licensing detected ({spdx}); commercial terms uninspected.",
            provenance_type=resolve_item_provenance(cand_provenance, license_inspected),
            source_id=lic_info.get("source_url") or slug,
            source_type="LICENSE_FILE",
            retrieval_timestamp=retrieval_ts,
            verification_method="TEXT_MATCH",
            limitations="Commercial pricing and grant scope must be obtained from vendor.",
        )
        supporting_evidence.append(rec["formatted_text"])
        evidence_records.append(rec)
        integration_pitfalls.append("Assuming commercial exemption without formal license agreement risks copyright claims.")
        pre_adoption_checklist.append("Contact vendor or copyright holder to inspect commercial terms, pricing, and scope.")
        complexity = "HIGH"
        uncertainty = "HIGH"

    # Case 4: Source-Available / Commercial Restrictive (BSL, SSPL)
    elif lic_cat == "SOURCE_AVAILABLE" or "BSL" in spdx or "SSPL" in spdx:
        is_commercial = (
            any(k in target_model for k in ("saas", "proprietary", "commercial", "production"))
            and "non-commercial" not in target_model
            and "non_commercial" not in target_model
            and "research" not in target_model
        )
        if is_commercial:
            grant_text = bsl_grant_details.get("additional_use_grant", "").lower()
            if grant_text and "unrestricted" in grant_text:
                posture = "ADOPT_AS_DEPENDENCY"
                fit_rationale.append("Source-available license with verified Additional Use Grant permitting this deployment.")
                complexity = "MODERATE"
            else:
                posture = "REJECT_FOR_USE_CASE"
                fit_rationale.append("Source-available license (e.g. BSL-1.1, SSPL) explicitly restricts commercial SaaS deployments.")
                rec = create_evidence_record(
                    claim=f"License '{spdx}' restricts commercial competition and production hosting under standard BSL terms.",
                    provenance_type=resolve_item_provenance(cand_provenance, license_inspected),
                    source_id=lic_info.get("source_url") or slug,
                    source_type="LICENSE_FILE",
                    retrieval_timestamp=retrieval_ts,
                    verification_method="TEXT_MATCH",
                    limitations="Evaluated under standard proprietary commercial deployment assumptions.",
                )
                supporting_evidence.append(rec["formatted_text"])
                evidence_records.append(rec)
                integration_pitfalls.append("Deploying in commercial SaaS violates Additional Use Grant, triggering copyright liability.")
                remaining_work.append("Select an alternative permissive library or construct clean-room implementation.")
                complexity = "PROHIBITIVE"
        else:
            posture = "USE_AS_ARCHITECTURAL_REFERENCE"
            fit_rationale.append("Permitted for internal non-commercial research; study data structures and design patterns.")
            rec = create_evidence_record(
                claim="BSL terms permit non-production evaluation and academic research.",
                provenance_type=resolve_item_provenance(cand_provenance, license_inspected),
                source_id=slug,
                source_type="LICENSE_FILE",
                retrieval_timestamp=retrieval_ts,
                verification_method="TEXT_MATCH",
            )
            supporting_evidence.append(rec["formatted_text"])
            evidence_records.append(rec)
            complexity = "MODERATE"

    # Case 5: Transitive Copyleft Risk
    elif transitive_risks:
        if transitive_linkage in ("unknown", "unverified"):
            posture = "INVESTIGATE_FURTHER"
            fit_rationale.append(f"Repository references transitive copyleft components ({', '.join(transitive_risks)}), but linkage boundary is unverified.")
            rec = create_evidence_record(
                claim=f"Transitive copyleft risk detected ({', '.join(transitive_risks)}) with unconfirmed linkage.",
                provenance_type=resolve_item_provenance(cand_provenance, manifest_inspected),
                source_id=slug,
                source_type="MANIFEST",
                retrieval_timestamp=retrieval_ts,
                verification_method="TEXT_MATCH",
                limitations="Linkage (dynamic import vs static bundling vs optional plugin) must be audited.",
            )
            supporting_evidence.append(rec["formatted_text"])
            evidence_records.append(rec)
            integration_pitfalls.append("If transitive copyleft dependency is statically linked, reciprocal disclosure obligations may attach.")
            pre_adoption_checklist.append("Conduct dependency tree linkage audit to verify if copyleft component is isolated or optional.")
            complexity = "HIGH"
            uncertainty = "HIGH"
        else:
            posture = "REJECT_FOR_USE_CASE"
            fit_rationale.append(f"Repository contains high-risk transitive dependencies: {', '.join(transitive_risks)}.")
            rec = create_evidence_record(
                claim=f"Dependency manifest includes copyleft/dual-licensed components ({', '.join(transitive_risks)}).",
                provenance_type=resolve_item_provenance(cand_provenance, manifest_inspected),
                source_id=slug,
                source_type="MANIFEST",
                retrieval_timestamp=retrieval_ts,
                verification_method="TEXT_MATCH",
            )
            supporting_evidence.append(rec["formatted_text"])
            evidence_records.append(rec)
            integration_pitfalls.append("Transitive dependencies contaminate host application with reciprocal disclosure obligations.")
            remaining_work.append("Replace contaminated components with permissive standalone alternatives.")
            complexity = "HIGH"

    # Case 6: Network Copyleft (AGPL) in Proprietary SaaS
    elif copyleft_tier == "STRONG_NETWORK" or lic_cat == "NETWORK_RECIPROCAL":
        if "proprietary" in target_model:
            if candidate.get("architecture_type") == "standalone_service" or "api" in cand_ecosystem:
                posture = "INTEGRATE_THROUGH_API"
                fit_rationale.append("Deploy as an independent, isolated service over network boundaries (e.g. Docker container).")
                rec = create_evidence_record(
                    claim="AGPL-3.0 obligations apply to the independent service. Host application communicates over remote network API.",
                    provenance_type=resolve_item_provenance(cand_provenance, source_inspected),
                    source_id=slug,
                    source_type="SOURCE_CODE",
                    retrieval_timestamp=retrieval_ts,
                    verification_method="TEXT_MATCH",
                    limitations="Legal interpretations vary on tightly coupled APIs. Subject to corporate open-source policy review.",
                )
                supporting_evidence.append(rec["formatted_text"])
                evidence_records.append(rec)
                integration_pitfalls.append("Tightly coupling backend schemas or in-process RPC risks triggering reciprocal AGPL source disclosure.")
                pre_adoption_checklist.append("Confirm organizational policy permits AGPL-3.0 network services behind remote API boundaries.")
                pre_adoption_checklist.append("Verify network boundary isolation protects host proprietary codebase.")
                remaining_work.append("Develop network API client, authentication layer, and failure-handling circuit breakers.")
                complexity = "HIGH"
                uncertainty = "MODERATE"
            else:
                posture = "REJECT_FOR_USE_CASE"
                fit_rationale.append("AGPL-3.0 library cannot be directly embedded into proprietary closed-source application without triggering source disclosure.")
                rec = create_evidence_record(
                    claim=f"Declared license '{spdx}' mandates reciprocal source sharing upon network deployment.",
                    provenance_type=resolve_item_provenance(cand_provenance, license_inspected),
                    source_id=slug,
                    source_type="LICENSE_FILE",
                    retrieval_timestamp=retrieval_ts,
                    verification_method="TEXT_MATCH",
                )
                supporting_evidence.append(rec["formatted_text"])
                evidence_records.append(rec)
                complexity = "PROHIBITIVE"
        else:
            posture = "ADOPT_AS_DEPENDENCY"
            fit_rationale.append("Host application is open-source compliant; AGPL requirements are mutually aligned.")
            complexity = "MODERATE"

    # Case 7: Capability & Technical Fit Gating
    elif candidate.get("technical_fit") == "POOR" or (user_capability and cand_capability and not any(w in cand_capability for w in user_capability.split()[:2])):
        posture = "REJECT_FOR_USE_CASE"
        fit_rationale.append(f"Candidate purpose ('{cand_purpose[:60]}...') does not match required capability ('{user_capability}'). Popularity cannot substitute for functional fit.")
        rec = create_evidence_record(
            claim=f"Technical capability mismatch: candidate provides '{cand_capability}', required is '{user_capability}'.",
            provenance_type="INFERRED",
            source_id=slug,
            source_type="HEURISTIC_RULE",
            verification_method="HEURISTIC_INFERENCE",
        )
        supporting_evidence.append(rec["formatted_text"])
        evidence_records.append(rec)
        complexity = "PROHIBITIVE"

    # Case 8: Missing API Inspection (Entrypoints)
    elif not source_inspected and not exported_symbols and lic_cat in ("PERMISSIVE", "WEAK_COPYLEFT"):
        posture = "INVESTIGATE_FURTHER"
        fit_rationale.append("Permissively licensed, but exported API entrypoints have not been inspected in source code. Cannot verify interface compatibility.")
        rec = create_evidence_record(
            claim="Public exported API symbols uninspected.",
            provenance_type="MISSING_EVIDENCE",
            source_id=slug,
            source_type="SOURCE_CODE",
            verification_method="UNVERIFIED",
            limitations="Source files not retrieved or AST symbols unparsed.",
        )
        supporting_evidence.append(rec["formatted_text"])
        evidence_records.append(rec)
        pre_adoption_checklist.append(f"Inspect {slug} source files to extract exported functions, classes, and parameter contracts.")
        uncertainty = "HIGH"
        complexity = "MODERATE"

    # Case 9: Archived or Stale / Abandoned Repositories
    elif is_archived or maint_status in ("ARCHIVED", "DORMANT") or (isinstance(days_inactive, int) and days_inactive > 365):
        if lic_cat == "PERMISSIVE":
            if exported_symbols and len(exported_symbols) <= 5:
                posture = "EXTRACT_REUSABLE_COMPONENT"
                fit_rationale.append(f"Repository is {maint_status.lower()} (last pushed {days_inactive} days ago), but contains isolated algorithms.")
                rec = create_evidence_record(
                    claim=f"Permissive {spdx} license permits extracting modular source files. {stale_note}",
                    provenance_type=resolve_item_provenance(cand_provenance, license_inspected),
                    source_id=slug,
                    source_type="SOURCE_CODE",
                    retrieval_timestamp=retrieval_ts,
                    verification_method="TEXT_MATCH",
                    limitations=stale_note or "Upstream dormant; requires local maintenance.",
                )
                supporting_evidence.append(rec["formatted_text"])
                evidence_records.append(rec)
                integration_pitfalls.append("Extracted code will no longer receive upstream security patches; team assumes full maintenance ownership.")
                remaining_work.append("Port extracted algorithms into project codebase, write standalone unit tests, and maintain copyright attribution.")
                complexity = "LOW_TO_MODERATE"
            else:
                posture = "FORK_AND_ADAPT"
                fit_rationale.append(f"Upstream is unmaintained ({days_inactive} days inactive). Active fork required to patch vulnerabilities.")
                rec = create_evidence_record(
                    claim=f"Upstream repository is {maint_status}. License permits independent maintenance. {stale_note}",
                    provenance_type=resolve_item_provenance(cand_provenance, license_inspected),
                    source_id=slug,
                    source_type="LICENSE_FILE",
                    retrieval_timestamp=retrieval_ts,
                    verification_method="TEXT_MATCH",
                    limitations=stale_note or "Forking incurs ongoing engineering overhead.",
                )
                supporting_evidence.append(rec["formatted_text"])
                evidence_records.append(rec)
                integration_pitfalls.append("Fork maintenance incurs ongoing engineering overhead and technical divergence.")
                remaining_work.append("Establish internal CI/CD pipeline, patch outdated dependencies, and add missing features.")
                complexity = "HIGH"
        else:
            posture = "USE_AS_ARCHITECTURAL_REFERENCE"
            fit_rationale.append(f"Repository is inactive ({days_inactive} days) and copyleft/complex; direct adoption or extraction carries excessive debt.")
            complexity = "HIGH"

    # Case 10: Language / Ecosystem Incompatibility
    elif target_lang and cand_lang and target_lang != cand_lang:
        has_bindings = any(target_lang in b.lower() for b in candidate.get("available_bindings", []))
        if has_bindings:
            posture = "ADOPT_AS_DEPENDENCY"
            fit_rationale.append(f"Written in {candidate.get('language')}, but provides official {target_lang.title()} bindings.")
            rec = create_evidence_record(
                claim=f"Official language bindings available for {target_lang}.",
                provenance_type=cand_provenance,
                source_id=slug,
                source_type="MANIFEST",
                retrieval_timestamp=retrieval_ts,
                verification_method="TEXT_MATCH",
            )
            supporting_evidence.append(rec["formatted_text"])
            evidence_records.append(rec)
            integration_pitfalls.append("Cross-language boundaries (WASM/FFI) introduce serialization overhead and complex debugging.")
            pre_adoption_checklist.append("Verify native pre-compiled wheel/binary availability across target deployment OS environments.")
            remaining_work.append("Configure FFI build steps or install native binding packages.")
            complexity = "MODERATE"
        elif candidate.get("architecture_type") == "standalone_service" or "cli" in cand_ecosystem:
            posture = "INTEGRATE_THROUGH_API"
            fit_rationale.append(f"Runtime mismatch ({cand_lang.title()} vs {target_lang.title()}); integrate via CLI or HTTP microservice.")
            complexity = "MODERATE"
        else:
            posture = "USE_AS_ARCHITECTURAL_REFERENCE"
            fit_rationale.append(f"Different language runtime ({cand_lang.title()} vs {target_lang.title()}) without packaged bindings.")
            complexity = "HIGH"

    # Case 11: Monolithic Application vs Modular Library
    elif candidate.get("architecture_type") == "monolithic_application":
        posture = "USE_AS_ARCHITECTURAL_REFERENCE"
        fit_rationale.append("Candidate is a full monolithic application rather than a modular library.")
        rec = create_evidence_record(
            claim="Codebase couples frontend UI, database schemas, and business controllers.",
            provenance_type=cand_provenance,
            source_id=slug,
            source_type="SOURCE_CODE",
            verification_method="PARSED_AST" if source_inspected else "HEURISTIC_INFERENCE",
        )
        supporting_evidence.append(rec["formatted_text"])
        evidence_records.append(rec)
        integration_pitfalls.append("Attempting to import monolithic app code introduces massive dependency bloat and tight architectural coupling.")
        remaining_work.append("Extract or re-implement specific target algorithms in isolation.")
        complexity = "HIGH"

    # Case 12: Active, Permissive / Weak Copyleft Modular Library (Optimal)
    elif lic_cat in ("PERMISSIVE", "WEAK_COPYLEFT"):
        posture = "ADOPT_AS_DEPENDENCY"
        fit_rationale.append(f"Actively maintained ({days_inactive} days since push), permissively licensed ({spdx}) modular package.")
        rec_maint = create_evidence_record(
            claim=f"Active maintenance status ({days_inactive}d since push).",
            provenance_type=cand_provenance,
            source_id=slug,
            source_type="API_METADATA",
            retrieval_timestamp=retrieval_ts,
            verification_method="TEXT_MATCH",
            limitations=stale_note,
        )
        supporting_evidence.append(rec_maint["formatted_text"])
        evidence_records.append(rec_maint)

        rec_lic = create_evidence_record(
            claim=f"Permissive {spdx} clearance verified.",
            provenance_type=cand_provenance,
            source_id=lic_info.get("source_url") or slug,
            source_type="LICENSE_FILE",
            retrieval_timestamp=retrieval_ts,
            verification_method="TEXT_MATCH",
        )
        supporting_evidence.append(rec_lic["formatted_text"])
        evidence_records.append(rec_lic)

        if lic_cat == "WEAK_COPYLEFT":
            rec_weak = create_evidence_record(
                claim=f"Weak copyleft ({spdx}) applies file-level reciprocity. Safe as unmodified external package.",
                provenance_type=cand_provenance,
                source_id=slug,
                source_type="LICENSE_FILE",
                verification_method="TEXT_MATCH",
            )
            supporting_evidence.append(rec_weak["formatted_text"])
            evidence_records.append(rec_weak)
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
        rec_fallback = create_evidence_record(
            claim="Insufficient evidence to conclusively declare adoption or rejection posture.",
            provenance_type="INFERRED",
            source_id=slug,
            source_type="HEURISTIC_RULE",
            verification_method="HEURISTIC_INFERENCE",
        )
        supporting_evidence.append(rec_fallback["formatted_text"])
        evidence_records.append(rec_fallback)
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
        "evidence_records": evidence_records,
        "legal_assessment": {
            "confirmed_license_identity": confirmed_license,
            "observed_dependency_relationships": observed_deps,
            "potential_obligations": potential_obligations,
            "unresolved_compatibility_questions": unresolved_questions,
            "confirmed_technical_incompatibilities": technical_incompatibilities,
            "organizational_policy_requirements": org_policy_reqs,
        },
        "integration_pitfalls": integration_pitfalls,
        "pre_adoption_checklist": pre_adoption_checklist,
        "remaining_engineering_work": remaining_work,
        "evidence_completeness": {
            "license_inspected": license_inspected,
            "manifest_inspected": manifest_inspected,
            "source_inspected": source_inspected,
            "runtime_tested": runtime_tested,
            "missing_evidence": missing_evidence,
        },
    }


def compare_repositories(
    candidates: Any,
    project_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Compare two or more repository evidence records across functional, architectural,
    legal, and operational dimensions. Produces a structured comparative synthesis.
    """
    if isinstance(candidates, dict):
        candidates = candidates.get("candidates") or candidates.get("repositories") or [candidates]

    if not candidates:
        raise ValueError("At least one candidate repository must be provided for comparison.")

    ctx = project_context or {}
    evaluated_candidates = [
        evaluate_candidate_posture(c, ctx) for c in candidates
    ]

    comparisons = []
    for c, eval_res in zip(candidates, evaluated_candidates):
        lic_info = c.get("license_info") or {}
        maint = c.get("maintenance", {})
        c_slug = c.get("slug") or c.get("repository", "unknown")
        c_name = c.get("name") or c_slug.split("/")[-1]
        c_purpose = c.get("purpose") or c.get("description", "Unspecified")
        c_lang = c.get("language") or c.get("primary_language", "Unknown")
        c_stars = c.get("stars") if "stars" in c else c.get("stargazers_count", 0)
        c_lic = lic_info.get("declared_spdx") or (c.get("license", {}).get("spdx_id") if isinstance(c.get("license"), dict) else "UNKNOWN")
        c_cat = lic_info.get("category") or (c.get("license", {}).get("category") if isinstance(c.get("license"), dict) else "UNKNOWN")
        c_days = maint.get("last_pushed_days_ago") if "last_pushed_days_ago" in maint else maint.get("days_since_last_push", "N/A")

        comparisons.append({
            "slug": c_slug,
            "name": c_name,
            "purpose": c_purpose,
            "target_capability": c.get("target_capability", ctx.get("required_capability", "Unspecified")),
            "language": c_lang,
            "ecosystem": c.get("ecosystem", "Unknown"),
            "stars": c_stars,
            "declared_license": c_lic,
            "license_category": c_cat,
            "maintenance_status": maint.get("status", "UNKNOWN"),
            "last_pushed_days_ago": c_days,
            "exported_symbol_count": len(c.get("exported_symbols", [])),
            "dependency_count": len(c.get("dependencies", [])),
            "known_limitations_count": len(c.get("known_limitations", [])),
            "posture": eval_res["posture"],
            "complexity": eval_res["complexity_rating"],
            "uncertainty": eval_res["uncertainty_rating"],
            "evaluation": eval_res,
            "raw_candidate": c,
        })

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

    high_uncertainty_count = sum(1 for c in comparisons if c["uncertainty"] == "HIGH")
    investigate_count = sum(1 for c in comparisons if c["posture"] == "INVESTIGATE_FURTHER")

    if all(c["posture"] in ("INVESTIGATE_FURTHER", "REJECT_FOR_USE_CASE") for c in comparisons) or high_uncertainty_count == len(comparisons):
        comparison_confidence = "INSUFFICIENT_EVIDENCE"
    elif any(c["posture"] == "ADOPT_AS_DEPENDENCY" and c["uncertainty"] == "LOW" for c in comparisons):
        comparison_confidence = "CONFIDENT"
    else:
        comparison_confidence = "CONDITIONAL"

    primary_recommendation = sorted_by_posture[0]["slug"] if sorted_by_posture else None

    return {
        "project_context": ctx,
        "total_candidates_evaluated": len(candidates),
        "comparison_confidence": comparison_confidence,
        "primary_recommendation": primary_recommendation,
        "candidates": comparisons,
    }


def format_comparison_table(comparison_result: Dict[str, Any]) -> str:
    """Format comparative results into a concise Markdown table and summary."""
    lines = []
    lines.append("# BeenHere Intelligent Repository Comparison\n")

    ctx = comparison_result.get("project_context", {})
    confidence = comparison_result.get("comparison_confidence", "CONDITIONAL")
    if ctx.get("required_capability"):
        lines.append(f"> **Evaluated Capability:** `{ctx.get('required_capability')}`  ")
    if ctx.get("target_language"):
        lines.append(f"> **Target Stack:** `{ctx.get('target_language')}` ({ctx.get('deployment_model', 'Proprietary SaaS')})  ")
    lines.append(f"> **Recommendation Confidence:** `{confidence}`  ")
    lines.append(f"> **Primary Recommended Path:** `{comparison_result.get('primary_recommendation')}`\n")

    if confidence == "INSUFFICIENT_EVIDENCE":
        lines.append("> [!WARNING] **Evidence Insufficient to Rank Confidently:** Evaluated candidates have critical missing license, manifest, or AST symbol evidence. Complete pre-adoption checklists before selecting a path.\n")

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
        leg = ev.get("legal_assessment", {})
        lines.append(f"### `{c['slug']}`: `{ev['posture']}`\n")
        lines.append(f"- **Why It Fits (or Fails):** {ev['fit_rationale']}")
        lines.append("- **Supporting Evidence:**")
        for se in ev["supporting_evidence"]:
            lines.append(f"  - {se}")
        
        lines.append("- **Qualified Legal Risk Assessment:**")
        lines.append(f"  - *Confirmed Identity:* {leg.get('confirmed_license_identity')}")
        lines.append(f"  - *Dependencies:* {leg.get('observed_dependency_relationships')}")
        lines.append(f"  - *Obligations:* {leg.get('potential_obligations')}")
        lines.append(f"  - *Unresolved Questions:* {leg.get('unresolved_compatibility_questions')}")
        lines.append(f"  - *Technical Incompatibilities:* {leg.get('confirmed_technical_incompatibilities')}")
        lines.append(f"  - *Organizational Policy:* {leg.get('organizational_policy_requirements')}")

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
    Includes explicit provenance, operational assumptions, verified entrypoints vs proposed adapter designs,
    integration sequence, required validation, and remaining unknowns.
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
    leg = ev.get("legal_assessment", {})
    evidence_records = ev.get("evidence_records", [])

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
    lines.append("- **Coupling Rule:** Never expose external third-party classes or types directly across the public API boundaries of your core domain models.")
    lines.append(f"- **Host Architecture & Assumptions:** Evaluated for deployment in `{ctx.get('deployment_model', 'Proprietary SaaS')}` on `{ctx.get('target_language', 'Generic')}` runtime.")
    lines.append(f"- **Runtime Verification Status:** {'VERIFIED IN SANDBOX' if ev.get('evidence_completeness', {}).get('runtime_tested') else 'UNTESTED IN LIVE SANDBOX'}. Pre-production container verification required.")
    
    # Evidence & Provenance Table
    if evidence_records:
        lines.append("\n### Supporting Evidence & Provenance Audit\n")
        lines.append("| Claim / Artifact | Provenance Type | Source Identifier | Verification Method | Known Limitations |")
        lines.append("| :--- | :---: | :--- | :---: | :--- |")
        for rec in evidence_records[:6]:
            claim_trunc = rec['claim'][:50] + "..." if len(rec['claim']) > 50 else rec['claim']
            src_trunc = rec['source_id'][:35] + "..." if len(rec['source_id']) > 35 else rec['source_id']
            lim_trunc = rec['limitations'][:40] + "..." if len(rec['limitations']) > 40 else (rec['limitations'] or "None")
            lines.append(f"| {claim_trunc} | `{rec['provenance_type']}` | `{src_trunc}` | `{rec['verification_method']}` | {lim_trunc} |")
    lines.append("")

    # 2. Public Entrypoints & Relevant APIs
    lines.append("## 2. Relevant APIs & Data Contracts\n")
    symbols = raw.get("exported_symbols", [])
    if symbols:
        lines.append("### Verified Upstream Exported Symbols (`[VERIFIED-SOURCE]` / `[PARSED-AST]`)\n")
        lines.append("| Exported Symbol | Type | Source File | Reusability Role |")
        lines.append("| :--- | :---: | :--- | :--- |")
        for sym in symbols[:8]:
            if isinstance(sym, dict):
                s_name = sym.get("name", "anonymous")
                s_type = sym.get("type", "symbol")
                s_file = sym.get("file", "unknown")
            else:
                s_name = str(sym)
                s_type = "symbol"
                s_file = "source"
            lines.append(f"| `{s_name}` | `{s_type}` | `{s_file}` | Direct integration entrypoint |")
        lines.append("")
    else:
        lines.append("- *No discrete exported symbols provided in evidence record. Treat as black-box library interface.*\n")

    lines.append(f"### Proposed Host Adapter Interface (`[PROPOSED-ADAPTER-DESIGN]`)\n")
    lines.append("> *Notice: The following adapter design is a proposed architectural boundary for the host application, NOT an upstream library contract.*\n")
    lines.append(f"```python")
    lines.append(f"# Proposed Anti-Corruption Adapter for {selected_cand['name']}")
    lines.append(f"class {selected_cand['name'].capitalize()}Adapter:")
    lines.append(f"    def __init__(self, config: dict):")
    lines.append(f"        self._config = config")
    lines.append(f"")
    lines.append(f"    def process(self, input_payload: bytes) -> dict:")
    lines.append(f"        # Translate internal domain objects to {selected_cand['name']} parameters")
    lines.append(f"        # Execute wrapped library call defensively with timeout")
    lines.append(f"        # Map external output types back to internal domain contracts")
    lines.append(f"        raise NotImplementedError('Implement adapter mapping')")
    lines.append(f"```\n")

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
    lines.append(f"- [ ] Audit `{selected_cand['slug']}` license ({selected_cand['declared_license']}) against corporate legal policy [LEGAL-AUDIT].")
    lines.append(f"- [ ] Confirm that organizational policy approves usage category: {leg.get('organizational_policy_requirements')}.")
    for chk in ev.get("pre_adoption_checklist", []):
        lines.append(f"- [ ] {chk}")
    deps = raw.get("dependencies", [])
    if deps:
        dep_names = ", ".join(d.get("name", "pkg") for d in deps[:6])
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
