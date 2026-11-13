#!/usr/bin/env python3
"""
scripts/benchmark_runner.py - Deterministic Benchmark Suite Runner & Quality Validator for BeenHere.

Evaluates concept expansion, query diversity, deduplication, and schema compliance
across the standardized benchmark suite of diverse software concepts.

Uses Python standard library only (no external dependencies).
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Ensure scripts directory is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import concept_expander


def validate_benchmark_case_schema(case: Dict[str, Any]) -> List[str]:
    """Validate that a benchmark case contains all mandatory research dimensions."""
    errors = []
    required_fields = [
        "id",
        "category",
        "concept",
        "core_problems",
        "expected_search_directions",
        "known_relevant_technical_concepts",
        "relevant_adjacent_industries",
        "examples_of_findings_worth_investigating",
    ]
    for rf in required_fields:
        if rf not in case:
            errors.append(f"Missing required field: '{rf}'")
        elif isinstance(case[rf], list) and len(case[rf]) == 0:
            errors.append(f"Empty required list: '{rf}'")
        elif isinstance(case[rf], str) and not case[rf].strip():
            errors.append(f"Empty required string: '{rf}'")

    return errors


def evaluate_concept_plan(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run concept expansion on a benchmark case and evaluate query diversity,
    deduplication, and hypothesis generation.
    """
    case_id = case.get("id", "unknown")
    case_errors = []

    try:
        plan = concept_expander.build_research_plan(
            concept=case["concept"],
            problems=case.get("core_problems", []),
            mechanisms=case.get("known_relevant_technical_concepts", []),
            technical_primitives=case.get("known_relevant_technical_concepts", [])[:2],
            adjacent_verticals=case.get("relevant_adjacent_industries", []),
        )
    except Exception as e:
        return {
            "case_id": case_id,
            "status": "FAIL",
            "errors": [f"Execution failed: {e}"],
            "metrics": {},
        }

    qm = plan.get("query_matrix", {})
    direct = qm.get("direct_queries", [])
    primitives = qm.get("technical_primitive_queries", [])
    cross_vertical = qm.get("cross_vertical_queries", [])
    academic = qm.get("academic_queries", [])

    # Check query diversity
    if len(direct) == 0:
        case_errors.append("Direct queries list is empty.")
    if len(primitives) == 0:
        case_errors.append("Technical primitive queries list is empty.")
    if len(cross_vertical) == 0:
        case_errors.append("Cross-vertical queries list is empty.")
    if len(academic) == 0:
        case_errors.append("Academic queries list is empty.")

    # Check deduplication
    total_queries = direct + primitives + cross_vertical + academic
    unique_queries = set(total_queries)
    if len(total_queries) != len(unique_queries):
        dup_count = len(total_queries) - len(unique_queries)
        case_errors.append(f"Found {dup_count} duplicate queries across matrices.")

    # Check hypotheses
    hypotheses = plan.get("hypotheses_to_verify", [])
    if len(hypotheses) == 0:
        case_errors.append("No verification hypotheses generated.")
    for h in hypotheses:
        if h.get("verification_status") != "UNVERIFIED_HYPOTHESIS":
            case_errors.append("Hypothesis does not carry strict UNVERIFIED_HYPOTHESIS status.")

    total_query_count = len(total_queries)
    pass_status = "PASS" if len(case_errors) == 0 else "FAIL"

    return {
        "case_id": case_id,
        "category": case.get("category"),
        "status": pass_status,
        "errors": case_errors,
        "metrics": {
            "direct_queries_count": len(direct),
            "primitive_queries_count": len(primitives),
            "cross_vertical_queries_count": len(cross_vertical),
            "academic_queries_count": len(academic),
            "total_queries_generated": total_query_count,
            "hypotheses_count": len(hypotheses),
        },
    }


def run_benchmark_suite(cases_file: str) -> Dict[str, Any]:
    """Execute complete benchmark suite against specified cases file."""
    if not os.path.isfile(cases_file):
        raise FileNotFoundError(f"Benchmark cases file not found: {cases_file}")

    with open(cases_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cases = data.get("cases", [])
    if len(cases) == 0:
        raise ValueError("Benchmark cases file contains 0 cases.")

    case_evaluations = []
    schema_failures = 0
    eval_failures = 0

    for c in cases:
        schema_errs = validate_benchmark_case_schema(c)
        if schema_errs:
            schema_failures += 1
            case_evaluations.append({
                "case_id": c.get("id", "unknown"),
                "status": "FAIL",
                "errors": [f"Schema error: {e}" for e in schema_errs],
                "metrics": {},
            })
            continue

        res = evaluate_concept_plan(c)
        if res["status"] == "FAIL":
            eval_failures += 1
        case_evaluations.append(res)

    total_cases = len(cases)
    passed_cases = sum(1 for ce in case_evaluations if ce["status"] == "PASS")
    overall_status = "PASS" if passed_cases == total_cases else "FAIL"

    return {
        "status": overall_status,
        "total_cases_evaluated": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": total_cases - passed_cases,
        "cases": case_evaluations,
    }


def format_benchmark_report(results: Dict[str, Any]) -> str:
    """Format benchmark evaluation into human-readable Markdown."""
    lines = []
    lines.append("# BeenHere Phase 2 Benchmark Evaluation Report\n")
    lines.append(f"**Overall Status:** **`{results['status']}`**")
    lines.append(f"**Results:** {results['passed_cases']} / {results['total_cases_evaluated']} cases passed\n")

    lines.append("| Case ID | Category | Status | Queries Generated | Hypotheses | Details |")
    lines.append("| :--- | :--- | :---: | :---: | :---: | :--- |")

    for c in results.get("cases", []):
        sym = "[PASS]" if c["status"] == "PASS" else "[FAIL]"
        m = c.get("metrics", {})
        q_count = str(m.get("total_queries_generated", "-"))
        h_count = str(m.get("hypotheses_count", "-"))
        details = ", ".join(c.get("errors", [])) if c.get("errors") else "All quality dimensions verified."
        lines.append(f"| `{c['case_id']}` | {c.get('category', '-')} | {sym} | {q_count} | {h_count} | {details} |")

    return "\n".join(lines)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(
        description="Deterministic Benchmark Suite Runner for BeenHere"
    )
    parser.add_argument(
        "--cases-file",
        "-f",
        default=os.path.join(os.path.dirname(SCRIPT_DIR), "tests", "benchmark_cases.json"),
        help="Path to benchmark_cases.json fixture",
    )
    parser.add_argument("--json", action="store_true", help="Output raw structured JSON to stdout")
    parser.add_argument("--output", "-o", type=str, help="Save evaluation report to file")

    args = parser.parse_args()

    try:
        results = run_benchmark_suite(args.cases_file)
    except Exception as e:
        sys.stderr.write(f"Benchmark execution failed: {e}\n")
        sys.exit(1)

    if args.json:
        out_content = json.dumps(results, indent=2)
    else:
        out_content = format_benchmark_report(results)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_content + "\n")
        print(f"Benchmark report written to {args.output}")
    else:
        print(out_content)

    if results.get("status") != "PASS":
        sys.exit(2)


if __name__ == "__main__":
    main()
