#!/usr/bin/env python3
"""Import tests from c-testsuite into our test format."""

import os
import sys
import shutil
from pathlib import Path

CTESTSUITE_DIR = Path("/tmp/c-testsuite/tests/single-exec")
OUTPUT_DIR = Path(__file__).parent.parent / "tests" / "external" / "c-testsuite"


def import_tests(max_tests=None):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    test_files = sorted(CTESTSUITE_DIR.glob("*.c"))
    if max_tests:
        test_files = test_files[:max_tests]

    imported = 0
    skipped = 0

    for test_file in test_files:
        name = test_file.stem  # e.g., "00001"
        expected_file = test_file.with_suffix(".c.expected")

        # Read expected output
        expected_stdout = ""
        if expected_file.exists():
            expected_stdout = expected_file.read_text()

        # Read tags to check for features we might not support
        tags_file = test_file.with_suffix(".c.tags")
        tags = []
        if tags_file.exists():
            tags = tags_file.read_text().strip().split()

        # Read source
        source = test_file.read_text()

        # Skip tests with features we know we don't support yet
        skip_keywords = [
            "__attribute__", "__builtin_", "typeof", "__typeof",
            "__asm", "asm(", "__extension__", "_Complex",
            "__int128", "__float128", "__label__",
        ]
        skip = False
        for kw in skip_keywords:
            if kw in source:
                skip = True
                break

        if skip:
            skipped += 1
            continue

        # Write adapted test file
        out_path = OUTPUT_DIR / f"{name}.c"

        # Build header comments
        header = f"""// TEST: ctest_{name}
// DESCRIPTION: c-testsuite test {name}
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
"""
        if expected_stdout:
            # Multi-line expected stdout
            for line in expected_stdout.rstrip('\n').split('\n'):
                header += f"// STDOUT: {line}\n"

        out_path.write_text(header + "\n" + source)
        imported += 1

    print(f"Imported: {imported}, Skipped: {skipped}")


if __name__ == "__main__":
    max_tests = int(sys.argv[1]) if len(sys.argv) > 1 else None
    import_tests(max_tests)
