import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "tests" / "positive" / "phase1" / "001_return_zero.c"


class TargetCliTests(unittest.TestCase):
    def run_jmcc(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "jmcc.py"), str(SOURCE), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_default_target_compiles_x86_64_linux_assembly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "default.s"
            result = self.run_jmcc("-o", str(output_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists())
            assembly = output_path.read_text()
            self.assertIn(".globl main", assembly)
            self.assertIn("pushq %rbp", assembly)

    def test_explicit_x86_64_linux_target_matches_default_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            default_path = Path(temp_dir) / "default.s"
            explicit_path = Path(temp_dir) / "explicit.s"

            default_result = self.run_jmcc("-o", str(default_path))
            explicit_result = self.run_jmcc("--target", "x86_64-linux", "-o", str(explicit_path))

            self.assertEqual(default_result.returncode, 0, default_result.stderr)
            self.assertEqual(explicit_result.returncode, 0, explicit_result.stderr)
            self.assertEqual(default_path.read_text(), explicit_path.read_text())

    def test_arm64_apple_darwin_target_reports_not_implemented(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "apple.s"
            result = self.run_jmcc("--target", "arm64-apple-darwin", "-o", str(output_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "error: code generation for target 'arm64-apple-darwin' is not implemented",
                result.stderr,
            )
            self.assertFalse(output_path.exists())

    def test_target_aliases_resolve_to_canonical_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "alias.s"
            result = self.run_jmcc("--target", "aarch64-apple-darwin", "-o", str(output_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "error: code generation for target 'arm64-apple-darwin' is not implemented",
                result.stderr,
            )


if __name__ == "__main__":
    unittest.main()
