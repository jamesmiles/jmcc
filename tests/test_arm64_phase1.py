import unittest
from pathlib import Path

from harness.run import run_test
from test_runner import APPLE_PHASE1_TESTS, discover_tests


ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = ROOT / "tests"


class ApplePhase1SuiteTests(unittest.TestCase):
    def test_named_suite_resolves_expected_files(self):
        tests = discover_tests(TEST_DIR, suite="apple-phase1", positive_only=True)
        self.assertEqual(
            [str(test.relative_to(TEST_DIR)) for test in tests],
            list(APPLE_PHASE1_TESTS),
        )

    def test_arm64_phase1_suite_currently_fails_at_codegen(self):
        source = TEST_DIR / APPLE_PHASE1_TESTS[0]
        result = run_test(source, compiler="jmcc", target="arm64-apple-darwin")

        self.assertFalse(result["passed"])
        self.assertIn(
            "code generation for target 'arm64-apple-darwin' is not implemented",
            result["details"],
        )


if __name__ == "__main__":
    unittest.main()
