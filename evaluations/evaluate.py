#!/usr/bin/env python3
"""
evaluations/evaluate.py - Reproducible Benchmark Harness & Research Quality Evaluator.

Part of BeenHere v1.1.
Evaluates research quality, computes weighted rubric totals, validates run manifests,
and generates empirical baseline vs BeenHere comparison reports.

Uses Python standard library only (no external dependencies).
Compatible with Python 3.8+.
"""

import argparse
import glob
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

DIMENSION_WEIGHTS: Dict[str, float] = {
    "d1_solutions_discovered": 0.20,
    "d2_reusable_code": 0.20,
    "d3_accuracy_evidence": 0.20,
    "d4_licensing_risk": 0.15,
    "d5_cross_industry": 0.15,
    "d6_actionable_recommendation": 0.10,
}

DIMENSION_NAMES: Dict[str, str] = {
    "d1_solutions_discovered": "Existing Solutions Discovered",
    "d2_reusable_code": "Reusable Code & Integration",
    "d3_accuracy_evidence": "Accuracy & Evidence Traceability",
    "d4_licensing_risk": "Licensing & Dependency Risks",
    "d5_cross_industry": "Cross-Industry Insight Quality",
    "d6_actionable_recommendation": "Actionability of Recommendation",
}

VALID_SCENARIOS = {
    "offline_notes",
    "ai_recruitment",
    "accessibility_testing",
    "synthetic_social_platform",
}

VALID_CONDITIONS = {"baseline", "beenhere"}

VALID_PROVENANCE_TYPES = {
    "synthetic_baseline_fixture",
    "retrospective_reference_fixture",
    "empirical_unblinded_trial",
    "empirical_blinded_trial",
}


def calculate_grade(quality_index: float) -> str:
    """Assign letter grade based on normalized 0-100 quality index."""
    if quality_index >= 90.0:
        return "A+ (Exemplary)"
    if quality_index >= 80.0:
        return "A (Strong)"
    if quality_index >= 70.0:
        return "B (Acceptable)"
    if quality_index >= 50.0:
        return "C (Marginal)"
    return "F (Unacceptable)"


def validate_manifest(manifest: Dict[str, Any]) -> List[str]:
    """
    Validate a run manifest dictionary against structural and semantic schema rules.
    Returns list of error messages (empty if valid).
    """
    errors = []

    required_top = [
        "manifest_version",
        "run_id",
        "scenario_id",
        "condition",
        "provenance_type",
        "timestamp",
        "environment",
        "prompt",
        "evaluation",
    ]
    for field in required_top:
        if field not in manifest:
            errors.append(f"Missing required top-level field: '{field}'")

    if manifest.get("scenario_id") not in VALID_SCENARIOS:
        errors.append(f"Invalid 'scenario_id': '{manifest.get('scenario_id')}'. Expected one of {sorted(list(VALID_SCENARIOS))}")

    if manifest.get("condition") not in VALID_CONDITIONS:
        errors.append(f"Invalid 'condition': '{manifest.get('condition')}'. Expected 'baseline' or 'beenhere'")

    if "provenance_type" in manifest and manifest["provenance_type"] not in VALID_PROVENANCE_TYPES:
        errors.append(f"Invalid 'provenance_type': '{manifest.get('provenance_type')}'. Expected one of {sorted(list(VALID_PROVENANCE_TYPES))}")

    env = manifest.get("environment", {})
    for req_env in ["agent_type", "model", "tool_access", "network_enabled"]:
        if req_env not in env:
            errors.append(f"Missing required environment field: 'environment.{req_env}'")

    eval_data = manifest.get("evaluation", {})
    for req_eval in ["evaluator", "evaluation_date", "is_blinded", "evaluator_conflict_of_interest", "scores", "dimension_justifications"]:
        if req_eval not in eval_data:
            errors.append(f"Missing required evaluation field: 'evaluation.{req_eval}'")

    scores = eval_data.get("scores", {})
    for dim_key in DIMENSION_WEIGHTS:
        if dim_key not in scores:
            errors.append(f"Missing score for dimension: '{dim_key}'")
        else:
            val = scores[dim_key]
            if not isinstance(val, (int, float)) or val < 0.0 or val > 5.0:
                errors.append(f"Score for '{dim_key}' must be a number between 0.0 and 5.0, got: {val}")

    justs = eval_data.get("dimension_justifications", {})
    for dim_key in DIMENSION_WEIGHTS:
        if dim_key not in justs or not str(justs[dim_key]).strip():
            errors.append(f"Missing justification text for dimension: '{dim_key}'")

    return errors


def compute_manifest_scores(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute weighted composite score, quality index, and letter grade for a run.
    """
    scores = manifest.get("evaluation", {}).get("scores", {})
    composite = 0.0
    breakdown = {}

    for dim_key, weight in DIMENSION_WEIGHTS.items():
        score = float(scores.get(dim_key, 0.0))
        weighted_val = score * weight
        composite += weighted_val
        breakdown[dim_key] = {
            "name": DIMENSION_NAMES[dim_key],
            "raw_score": score,
            "weight": weight,
            "weighted_score": round(weighted_val, 3),
        }

    composite = round(composite, 3)
    quality_index = round((composite / 5.0) * 100.0, 1)
    grade = calculate_grade(quality_index)

    return {
        "run_id": manifest.get("run_id"),
        "scenario_id": manifest.get("scenario_id"),
        "condition": manifest.get("condition"),
        "composite_score": composite,
        "quality_index": quality_index,
        "grade": grade,
        "breakdown": breakdown,
    }


def load_all_manifests(results_dir: str) -> List[Dict[str, Any]]:
    """Load and validate all JSON manifests in results directory."""
    manifests = []
    if not os.path.isdir(results_dir):
        return manifests

    for path in sorted(glob.glob(os.path.join(results_dir, "*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            errs = validate_manifest(data)
            if errs:
                sys.stderr.write(f"Warning: Manifest '{path}' has validation errors: {errs}\n")
            else:
                data["_file_path"] = path
                manifests.append(data)
        except Exception as e:
            sys.stderr.write(f"Error loading '{path}': {e}\n")

    return manifests


def compare_runs(manifests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Group runs by scenario and produce paired comparison between baseline and beenhere.
    """
    scenarios: Dict[str, Dict[str, Any]] = {}

    for m in manifests:
        scen_id = m["scenario_id"]
        cond = m["condition"]
        if scen_id not in scenarios:
            scenarios[scen_id] = {"baseline": None, "beenhere": None}
        scenarios[scen_id][cond] = m

    comparisons = []
    for scen_id, pair in sorted(scenarios.items()):
        b_run = pair.get("baseline")
        bh_run = pair.get("beenhere")

        b_score = compute_manifest_scores(b_run) if b_run else None
        bh_score = compute_manifest_scores(bh_run) if bh_run else None

        delta_composite = round(bh_score["composite_score"] - b_score["composite_score"], 3) if (b_score and bh_score) else None
        delta_index = round(bh_score["quality_index"] - b_score["quality_index"], 1) if (b_score and bh_score) else None

        comparisons.append({
            "scenario_id": scen_id,
            "baseline": b_score,
            "beenhere": bh_score,
            "delta_composite": delta_composite,
            "delta_index": delta_index,
            "baseline_manifest": b_run,
            "beenhere_manifest": bh_run,
        })

    return {"scenarios": comparisons}


def format_comparison_markdown(comparison_data: Dict[str, Any]) -> str:
    """Format paired scenario comparisons into a clean GitHub-style Markdown report."""
    lines = []
    lines.append("# BeenHere vs Baseline: Calibrated Reference Benchmark Evaluation\n")
    lines.append("> **Evaluation Engine:** `evaluations/evaluate.py` (BeenHere v1.1 Evaluation Harness)  ")
    lines.append("> **Rubric:** 6 Weighted Dimensions (0–5 scale, 0–100 Normalized Quality Index)  ")
    lines.append("> **Methodology:** Calibrated reference matrix across standardized prompts.  ")
    lines.append("> **Provenance Notice:** Baseline runs are synthetic archetypal fixtures; BeenHere runs are author-scored formative benchmarks. They validate harness functionality, not double-blind empirical superiority.\n")
    lines.append("---\n")

    lines.append("## 1. Executive Summary Table\n")
    lines.append("| Scenario | Baseline Index | BeenHere Index | Delta (Δ) | Baseline Grade | BeenHere Grade | Comparison |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :--- |")

    for c in comparison_data.get("scenarios", []):
        scen_id = c["scenario_id"]
        b = c.get("baseline")
        bh = c.get("beenhere")

        b_idx_str = f"{b['quality_index']:.1f}" if b else "N/A"
        bh_idx_str = f"{bh['quality_index']:.1f}" if bh else "N/A"
        delta_str = f"+{c['delta_index']:.1f}" if (c['delta_index'] is not None and c['delta_index'] > 0) else str(c['delta_index'])
        b_grade = b["grade"].split()[0] if b else "N/A"
        bh_grade = bh["grade"].split()[0] if bh else "N/A"

        if c.get("delta_index") is not None:
            if c["delta_index"] > 0:
                outcome = "BeenHere Higher (Reference)"
            elif c["delta_index"] < 0:
                outcome = "Baseline Higher (Reference)"
            else:
                outcome = "Equal Score"
        else:
            outcome = "Inconclusive"

        lines.append(f"| `{scen_id}` | {b_idx_str} | {bh_idx_str} | **{delta_str}** | {b_grade} | **{bh_grade}** | {outcome} |")

    lines.append("\n---\n")
    lines.append("## 2. Dimension Breakdown by Scenario\n")

    for c in comparison_data.get("scenarios", []):
        scen_id = c["scenario_id"]
        b = c.get("baseline")
        bh = c.get("beenhere")
        lines.append(f"### Scenario: `{scen_id}`\n")

        lines.append("| Dimension | Weight | Baseline (0–5) | BeenHere (0–5) | Delta | Key Differentiator |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :--- |")

        for dim_key, weight in DIMENSION_WEIGHTS.items():
            dim_name = DIMENSION_NAMES[dim_key]
            b_val = b["breakdown"][dim_key]["raw_score"] if b else 0.0
            bh_val = bh["breakdown"][dim_key]["raw_score"] if bh else 0.0
            d_val = round(bh_val - b_val, 2)
            d_sign = f"+{d_val}" if d_val > 0 else str(d_val)

            # Extract justification note from BeenHere manifest
            bh_just = ""
            if c.get("beenhere_manifest"):
                just_dict = c["beenhere_manifest"].get("evaluation", {}).get("dimension_justifications", {})
                bh_just = just_dict.get(dim_key, "")
                if len(bh_just) > 80:
                    bh_just = bh_just[:77] + "..."

            lines.append(f"| {dim_name} | {int(weight*100)}% | {b_val:.1f} | **{bh_val:.1f}** | {d_sign} | {bh_just} |")

        lines.append("")

        # Add findings comparison
        b_find = (c.get("baseline_manifest") or {}).get("evaluation", {}).get("observed_findings", {})
        bh_find = (c.get("beenhere_manifest") or {}).get("evaluation", {}).get("observed_findings", {})

        b_traps = b_find.get("critical_traps_missed", [])
        bh_traps = bh_find.get("critical_traps_caught", [])

        lines.append("**Critical Failure Modes & Traps:**")
        lines.append(f"- *Baseline Missed Traps:* {', '.join(b_traps) if b_traps else 'None recorded'}")
        lines.append(f"- *BeenHere Caught Traps:* {', '.join(bh_traps) if bh_traps else 'None recorded'}")
        lines.append("\n---\n")

    lines.append("## 3. Disclosures, Missing Data & Empirical Uncertainties\n")
    lines.append("1. **Self-Audit Disclosure:** In runs where an AI agent acts as both researcher and evaluator, unconscious alignment bias is possible. Double-blind verification or independent human audit is recommended for high-stakes decisions.")
    lines.append("2. **Subprocess Network Restrictions:** In sandboxed agent environments without outbound raw TCP socket access (`[WinError 10013]`), BeenHere triggers host-agent native tool fallback. The fallback preserves quality but relies on the host agent's web browsing capability.")
    lines.append("3. **Absence of In-Memory Dynamic Execution:** Reusability scores are based on static AST parsing and manifest inspection. True runtime testing (`[VERIFIED-TEST]`) requires sandboxed container execution.")

    return "\n".join(lines)


def lint_research_report(content: str) -> List[Dict[str, Any]]:
    """
    Lint a markdown research report for research quality anti-patterns:
    1. Anti-Percentage Rule: Flag ungrounded pseudo-quantitative percentage claims like
       '75% code reuse' or 'reuse 80% of backend' without empirical measurement.
    2. Missing Evidence Tagging: Flag when report claims facts without BeenHere evidence classification.
    3. Misleading Licensing Claims: Flag claims that BSL is open-source or that copyleft prohibits commercial use.
    """
    issues = []

    # 1. Anti-percentage rule
    pct_patterns = [
        re.compile(r'\b(\d{1,3})%[^\n.!?]*?\b(?:code\s*reuse|reuse|reusable|reusability|saved\s*effort)\b', re.IGNORECASE),
        re.compile(r'\b(?:reuse|code\s*reuse|reusability|reusable)\b[^\n.!?]*?\b(\d{1,3})%', re.IGNORECASE),
    ]
    for pat in pct_patterns:
        for match in pat.finditer(content):
            issues.append({
                "rule": "anti_percentage_rule",
                "severity": "violation",
                "message": f"Detected speculative pseudo-quantitative percentage claim '{match.group(0)}'. BeenHere methodology forbids speculative percentage estimates without line-by-line derivation.",
                "matched_text": match.group(0),
            })

    # 2. BSL open source conflation
    bsl_pattern = re.compile(r'\b(?:BSL|BSL-1\.1|Business\s+Source\s+License)\b[^\n]*?\b(?:is\s+open[- ]source|OSI[- ]approved)\b', re.IGNORECASE)
    for match in bsl_pattern.finditer(content):
        issues.append({
            "rule": "licensing_misconception",
            "severity": "violation",
            "message": "Business Source License (BSL-1.1) is not OSI-approved open source; it is a source-available commercial license with eventual open-sourcing.",
            "matched_text": match.group(0),
        })

    # 3. Copyleft commercial prohibition fallacy
    copyleft_pattern = re.compile(r'\b(?:GPL|copyleft|AGPL)[^\n]*?\b(?:prohibits?\s+commercial|forbids?\s+commercial|disallows?\s+commercial\s+use)\b', re.IGNORECASE)
    for match in copyleft_pattern.finditer(content):
        issues.append({
            "rule": "licensing_misconception",
            "severity": "violation",
            "message": "Copyleft licenses (GPL/AGPL) do not prohibit commercial use; they require source distribution upon deployment or distribution.",
            "matched_text": match.group(0),
        })

    # 4. Evidence tag check for substantial documents
    if len(content.strip()) > 500:
        found_tags = [tag for tag in ["[VERIFIED-SOURCE]", "[VERIFIED-TEST]", "[VERIFIED-METADATA]", "[UNVERIFIED-MARKETING-CLAIM]", "[INFERRED]"] if tag in content]
        if not found_tags:
            issues.append({
                "rule": "missing_evidence_tags",
                "severity": "warning",
                "message": "Research report lacks standard BeenHere evidence classification tags ([VERIFIED-*] or [UNVERIFIED-*]).",
                "matched_text": "",
            })

    return issues


def main():
    parser = argparse.ArgumentParser(description="BeenHere Research Quality Evaluation Harness")
    parser.add_argument("--results-dir", "-d", default=os.path.join(os.path.dirname(__file__), "results"), help="Directory containing run manifest JSON files")
    parser.add_argument("--validate", "-v", type=str, help="Validate a specific manifest file or all files in results dir")
    parser.add_argument("--score", "-s", type=str, help="Calculate and print scores for a single manifest file")
    parser.add_argument("--summary", action="store_true", help="Print concise comparison summary table")
    parser.add_argument("--report", action="store_true", help="Generate full comparative markdown report")
    parser.add_argument("--output", "-o", type=str, help="Output file path for report")
    parser.add_argument("--lint", "-l", type=str, help="Lint a research report markdown file for quality anti-patterns")

    args = parser.parse_args()

    # Mode 0: Lint report
    if args.lint:
        if not os.path.isfile(args.lint):
            sys.stderr.write(f"File not found: {args.lint}\n")
            sys.exit(1)
        with open(args.lint, "r", encoding="utf-8") as f:
            content = f.read()
        issues = lint_research_report(content)
        if not issues:
            print(f"[PASS] {args.lint} passed research quality linting (0 anti-patterns detected).")
            sys.exit(0)
        else:
            print(f"[FAIL] {args.lint} has {len(issues)} research quality issue(s):")
            for iss in issues:
                print(f"  [{iss['severity'].upper()}] {iss['rule']}: {iss['message']}")
            sys.exit(1)

    # Mode 1: Validate
    if args.validate:
        target = args.validate
        if os.path.isfile(target):
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
            errs = validate_manifest(data)
            if errs:
                print(f"[FAIL] {target} has {len(errs)} validation errors:")
                for e in errs:
                    print(f"  - {e}")
                sys.exit(1)
            else:
                print(f"[PASS] {target} is valid.")
                sys.exit(0)
        elif os.path.isdir(target):
            all_files = glob.glob(os.path.join(target, "*.json"))
            total_errs = 0
            for fpath in all_files:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                errs = validate_manifest(data)
                if errs:
                    total_errs += len(errs)
                    print(f"[FAIL] {fpath}: {errs}")
                else:
                    print(f"[PASS] {fpath}")
            if total_errs > 0:
                sys.exit(1)
            sys.exit(0)

    # Mode 2: Score single manifest
    if args.score:
        if not os.path.isfile(args.score):
            sys.stderr.write(f"File not found: {args.score}\n")
            sys.exit(1)
        with open(args.score, "r", encoding="utf-8") as f:
            data = json.load(f)
        scores = compute_manifest_scores(data)
        print(json.dumps(scores, indent=2))
        sys.exit(0)

    # Default / Mode 3: Load all and compare
    manifests = load_all_manifests(args.results_dir)
    if not manifests:
        print(f"No valid run manifests found in {args.results_dir}.")
        sys.exit(0)

    comparisons = compare_runs(manifests)

    if args.summary or (not args.report and not args.output):
        print(f"Loaded {len(manifests)} manifests across {len(comparisons['scenarios'])} scenarios.")
        print("NOTE: Scores represent calibrated reference fixtures for harness validation, not double-blind empirical trials.\n")
        print(f"{'Scenario':<25} {'Baseline':<12} {'BeenHere':<12} {'Delta':<8} {'Comparison'}")
        print("-" * 75)
        for c in comparisons["scenarios"]:
            scen = c["scenario_id"]
            b_str = f"{c['baseline']['quality_index']:.1f} ({c['baseline']['grade'].split()[0]})" if c.get("baseline") else "N/A"
            bh_str = f"{c['beenhere']['quality_index']:.1f} ({c['beenhere']['grade'].split()[0]})" if c.get("beenhere") else "N/A"
            delta = f"+{c['delta_index']:.1f}" if (c['delta_index'] and c['delta_index'] > 0) else (str(c['delta_index']) if c['delta_index'] else "N/A")
            outcome = "BeenHere Higher" if (c['delta_index'] and c['delta_index'] > 0) else ("Baseline Higher" if (c['delta_index'] and c['delta_index'] < 0) else "Equal Score")
            print(f"{scen:<25} {b_str:<12} {bh_str:<12} {delta:<8} {outcome}")
        print("")

    if args.report or args.output:
        md = format_comparison_markdown(comparisons)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(md + "\n")
            print(f"Report written to {args.output}")
        else:
            print(md)


if __name__ == "__main__":
    main()
