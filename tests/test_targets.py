import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "tests" / "positive" / "phase1" / "001_return_zero.c"
ARM64_PHASE2_FRONTIERS = (
    ROOT / "tests" / "positive" / "phase2" / "004_ternary.c",
    ROOT / "tests" / "positive" / "phase2" / "007_break_loop.c",
    ROOT / "tests" / "positive" / "phase2" / "008_continue_loop.c",
    ROOT / "tests" / "positive" / "phase2" / "016_goto.c",
)
NEGATION_SOURCE = ROOT / "tests" / "positive" / "phase1" / "008_negation.c"


class TargetCliTests(unittest.TestCase):
    def run_jmcc(self, *args):
        return self.run_jmcc_source(SOURCE, *args)

    def run_jmcc_source(self, source, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "jmcc.py"), str(source), *args],
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

    def test_arm64_apple_darwin_target_compiles_simple_program(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "apple.s"
            result = self.run_jmcc("--target", "arm64-apple-darwin", "-o", str(output_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists())
            assembly = output_path.read_text()
            self.assertIn(".globl _main", assembly)
            self.assertIn("stp x29, x30", assembly)

    def test_arm64_apple_darwin_target_supports_unary_negation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "negation.s"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "jmcc.py"),
                    str(NEGATION_SOURCE),
                    "--target",
                    "arm64-apple-darwin",
                    "-o",
                    str(output_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists())
            self.assertIn("neg w0, w0", output_path.read_text())

    def test_target_aliases_resolve_to_canonical_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "alias.s"
            result = self.run_jmcc("--target", "aarch64-apple-darwin", "-o", str(output_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists())
            self.assertIn(".globl _main", output_path.read_text())

    def test_arm64_apple_darwin_compiles_phase2_frontiers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            for source in ARM64_PHASE2_FRONTIERS:
                output_path = Path(temp_dir) / f"{source.stem}.s"
                result = self.run_jmcc_source(
                    source,
                    "--target",
                    "arm64-apple-darwin",
                    "-o",
                    str(output_path),
                )

                self.assertEqual(result.returncode, 0, f"{source.name}: {result.stderr}")
                self.assertTrue(output_path.exists(), source.name)
                self.assertIn(".globl _main", output_path.read_text(), source.name)


if __name__ == "__main__":
    unittest.main()
