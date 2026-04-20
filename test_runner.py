#!/usr/bin/env python3
"""
JMCC Test Runner

Discovers and runs all tests, validates against reference compilers,
and reports the reward signal (pass rate).
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from harness.run import (
    ensure_docker_image,
    parse_test_metadata,
    run_test,
)

APPLE_PHASE1_TESTS = (
    "positive/phase1/001_return_zero.c",
    "positive/phase1/002_return_literal.c",
    "positive/phase1/003_addition.c",
    "positive/phase1/004_subtraction.c",
    "positive/phase1/006_division.c",
    "positive/phase1/007_modulo.c",
    "positive/phase1/008_negation.c",
    "positive/phase1/009_bitwise_and.c",
    "positive/phase1/010_bitwise_or.c",
    "positive/phase1/011_local_var.c",
    "positive/phase1/012_multiple_vars.c",
    "positive/phase1/013_if_true.c",
    "positive/phase1/014_if_false.c",
    "positive/phase1/015_if_else.c",
    "positive/phase1/016_comparison_eq.c",
    "positive/phase1/017_comparison_ne.c",
    "positive/phase1/018_comparison_lt.c",
    "positive/phase1/019_while_loop.c",
    "positive/phase1/020_for_loop.c",
    "positive/phase1/021_function_call.c",
    "positive/phase1/022_recursive_factorial.c",
    "positive/phase1/023_logical_and.c",
    "positive/phase1/024_logical_or.c",
    "positive/phase1/025_logical_not.c",
    "positive/phase1/026_nested_if.c",
    "positive/phase1/027_complex_expr.c",
    "positive/phase1/028_parenthesized_expr.c",
    "positive/phase1/030_bitwise_xor.c",
    "positive/phase1/031_shift_left.c",
    "positive/phase1/032_shift_right.c",
    "positive/phase1/034_var_assignment.c",
    "positive/phase1/029_do_while.c",
    "positive/phase1/033_global_var.c",
    "positive/phase2/004_ternary.c",
    "positive/phase2/007_break_loop.c",
)

NAMED_SUITES = {
    "apple-phase1": APPLE_PHASE1_TESTS,
}


def discover_tests(test_dir, phase=None, filter_pattern=None, negative_only=False,
                   positive_only=False, suite=None):
    """Discover test files matching criteria."""
    tests = []

    if suite is not None:
        for rel_path in NAMED_SUITES[suite]:
            test_file = Path(test_dir, rel_path)
            metadata = parse_test_metadata(test_file)
            if phase is not None and metadata["phase"] != phase:
                continue
            if filter_pattern and filter_pattern not in str(test_file):
                continue
            tests.append(test_file)
        return tests

    if not negative_only:
        for phase_dir in sorted(Path(test_dir, "positive").glob("phase*")):
            for test_file in sorted(phase_dir.glob("*.c")):
                metadata = parse_test_metadata(test_file)
                if not metadata["name"]:
                    continue  # Skip helper files (no // TEST: header)
                if phase is not None and metadata["phase"] != phase:
                    continue
                if filter_pattern and filter_pattern not in str(test_file):
                    continue
                tests.append(test_file)

    if not positive_only:
        for category_dir in sorted(Path(test_dir, "negative").iterdir()):
            if not category_dir.is_dir():
                continue
            for test_file in sorted(category_dir.glob("*.c")):
                metadata = parse_test_metadata(test_file)
                if phase is not None and metadata["phase"] != phase:
                    continue
                if filter_pattern and filter_pattern not in str(test_file):
                    continue
                tests.append(test_file)

    # External tests
    if not negative_only:
        external_dir = Path(test_dir, "external")
        if external_dir.exists():
            for test_file in sorted(external_dir.glob("**/*.c")):
                metadata = parse_test_metadata(test_file)
                if phase is not None and metadata["phase"] != phase:
                    continue
                if filter_pattern and filter_pattern not in str(test_file):
                    continue
                tests.append(test_file)

    return tests


def run_all_tests(tests, compiler="jmcc", validate_references=False, target=None):
    """Run all tests and return results."""
    results = []

    for test_file in tests:
        metadata = parse_test_metadata(test_file)
        test_name = metadata["name"] or test_file.stem

        # Optionally validate against reference compilers first
        if validate_references and not metadata["expect_compile_fail"]:
            for ref in ("gcc", "clang"):
                ref_result = run_test(test_file, compiler=ref)
                if not ref_result["passed"]:
                    print(f"  WARNING: {test_name} fails with {ref}: {ref_result['details']}")

        # Run with target compiler
        result = run_test(test_file, compiler=compiler, target=target)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  [{status}] {test_name}: {result['details']}")
        results.append(result)

    return results


def print_score(results):
    """Print the reward signal."""
    # Group by category
    positive = [r for r in results if not r["metadata"]["expect_compile_fail"]]
    negative = [r for r in results if r["metadata"]["expect_compile_fail"]]

    # Group positive by phase
    phases = {}
    for r in positive:
        p = r["metadata"]["phase"]
        if p not in phases:
            phases[p] = {"pass": 0, "total": 0}
        phases[p]["total"] += 1
        if r["passed"]:
            phases[p]["pass"] += 1

    neg_pass = sum(1 for r in negative if r["passed"])
    neg_total = len(negative)

    total_pass = sum(1 for r in results if r["passed"])
    total_total = len(results)

    print("\n=== JMCC Test Results ===")
    for p in sorted(phases.keys()):
        pct = (phases[p]["pass"] / phases[p]["total"] * 100) if phases[p]["total"] else 0
        print(f"Phase {p}: {phases[p]['pass']:>3}/{phases[p]['total']:<3} ({pct:>5.1f}%)")

    if neg_total:
        pct = (neg_pass / neg_total * 100) if neg_total else 0
        print(f"Negative: {neg_pass:>3}/{neg_total:<3} ({pct:>5.1f}%)")

    print("─" * 28)
    pct = (total_pass / total_total * 100) if total_total else 0
    print(f"TOTAL:    {total_pass:>3}/{total_total:<3} ({pct:>5.1f}%)")
    print()

    return total_pass, total_total


def main():
    parser = argparse.ArgumentParser(description="JMCC Test Runner")
    parser.add_argument("--phase", type=int, help="Run only tests for given phase")
    parser.add_argument("--filter", type=str, help="Filter tests by name pattern")
    parser.add_argument("--compiler", default="jmcc", choices=["jmcc", "gcc", "clang"],
                        help="Compiler to test")
    parser.add_argument("--validate", action="store_true",
                        help="Also validate tests against reference compilers")
    parser.add_argument("--score", action="store_true",
                        help="Show only the score summary")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    parser.add_argument("--negative-only", action="store_true",
                        help="Run only negative tests")
    parser.add_argument("--positive-only", action="store_true",
                        help="Run only positive tests")
    parser.add_argument("--native", action="store_true",
                        help="Run without Docker (faster, uses host as/gcc)")
    parser.add_argument("--target", default=None,
                        help="JMCC compilation target (for jmcc compiler runs)")
    parser.add_argument("--suite", choices=sorted(NAMED_SUITES.keys()),
                        help="Run a named curated test suite")
    args = parser.parse_args()

    if args.native:
        os.environ["JMCC_NATIVE"] = "1"

    test_dir = PROJECT_DIR / "tests"

    # Discover tests
    tests = discover_tests(
        test_dir,
        phase=args.phase,
        filter_pattern=args.filter,
        negative_only=args.negative_only,
        positive_only=args.positive_only,
        suite=args.suite,
    )

    if not tests:
        print("No tests found.")
        sys.exit(0)

    print(f"Found {len(tests)} tests")

    # Ensure Docker image exists
    ensure_docker_image()

    # Run tests
    print(f"\nRunning tests with {args.compiler}...")
    results = run_all_tests(
        tests,
        compiler=args.compiler,
        validate_references=args.validate,
        target=args.target,
    )

    # Output
    if args.json:
        # Strip non-serializable bits
        for r in results:
            r["source"] = str(r["source"])
        print(json.dumps(results, indent=2))
    else:
        passed, total = print_score(results)
        sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
