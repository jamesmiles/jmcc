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


def discover_tests(test_dir, phase=None, filter_pattern=None, negative_only=False,
                   positive_only=False, target=None):
    """Discover test files matching criteria.

    Test file naming convention:
      [name].c         — generic, runs on all platforms
      [name]_arm64.c   — arm64-only
      [name]_x86-64.c  — x86-64-only

    When target contains 'arm64', generic + arm64 tests are included.
    Otherwise, generic + x86-64 tests are included.
    """
    is_arm64 = target is not None and "arm64" in target
    tests = []

    if not negative_only:
        for phase_dir in sorted(Path(test_dir, "positive").glob("phase*")):
            for test_file in sorted(phase_dir.glob("*.c")):
                name = test_file.name
                is_arm64_test = name.endswith("_arm64.c")
                is_x86_64_test = name.endswith("_x86-64.c")
                if is_arm64:
                    if is_x86_64_test:
                        continue
                    # include generic + _arm64
                else:
                    if is_arm64_test:
                        continue
                    # include generic + _x86-64
                metadata = parse_test_metadata(test_file)
                if not metadata["name"]:
                    if is_arm64_test or is_x86_64_test:
                        metadata["name"] = test_file.stem
                    else:
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
                        help="JMCC compilation target — also selects platform-specific tests "
                             "(e.g. arm64-apple-darwin includes _arm64.c tests)")
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
        target=args.target,
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
