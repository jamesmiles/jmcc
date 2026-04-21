import os
import platform
import unittest
from unittest import mock
from pathlib import Path

from harness.run import run_test
from test_runner import APPLE_PHASE1_TESTS, discover_tests


ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = ROOT / "tests"
ANGLE_BRACKET_INCLUDE_SOURCE = TEST_DIR / "positive" / "phase5" / "039_angle_bracket_include.c"


class ApplePhase1SuiteTests(unittest.TestCase):
    def test_named_suite_resolves_expected_files(self):
        tests = discover_tests(TEST_DIR, suite="apple-phase1", positive_only=True)
        self.assertEqual(
            [str(test.relative_to(TEST_DIR)) for test in tests],
            list(APPLE_PHASE1_TESTS),
        )

    @unittest.skipUnless(
        platform.system() == "Darwin" and platform.machine().lower() in ("arm64", "aarch64"),
        "native Apple arm64 smoke execution requires a Darwin arm64 host",
    )
    def test_arm64_phase1_suite_runs_natively(self):
        source = TEST_DIR / APPLE_PHASE1_TESTS[0]
        with mock.patch.dict(os.environ, {"JMCC_NATIVE": "1"}):
            result = run_test(source, compiler="jmcc", target="arm64-apple-darwin")

        self.assertTrue(result["passed"], result["details"])

    @unittest.skipUnless(
        platform.system() == "Darwin" and platform.machine().lower() in ("arm64", "aarch64"),
        "native reference execution requires a Darwin arm64 host",
    )
    def test_native_reference_runner_honors_include_paths(self):
        with mock.patch.dict(os.environ, {"JMCC_NATIVE": "1"}):
            result = run_test(ANGLE_BRACKET_INCLUDE_SOURCE, compiler="clang")

        self.assertTrue(result["passed"], result["details"])


if __name__ == "__main__":
    unittest.main()
