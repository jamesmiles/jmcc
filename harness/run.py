#!/usr/bin/env python3
"""
JMCC Execution Harness

Compiles and runs C programs inside Docker (hosted) or QEMU (freestanding).
Captures stdout, stderr, exit code, and optional core dumps.
"""

import subprocess
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path

HARNESS_DIR = Path(__file__).parent
PROJECT_DIR = HARNESS_DIR.parent
DOCKER_IMAGE = "jmcc-test"
CONTAINER_NAME = "jmcc-test-runner"
TIMEOUT_SECONDS = int(os.environ.get("JMCC_TIMEOUT", "60"))


def ensure_docker_image():
    """Build the Docker image if it doesn't exist."""
    result = subprocess.run(
        ["docker", "images", "-q", DOCKER_IMAGE],
        capture_output=True, text=True
    )
    if not result.stdout.strip():
        print("Building Docker test image...", file=sys.stderr)
        subprocess.run(
            ["docker", "build", "-t", DOCKER_IMAGE, str(HARNESS_DIR)],
            check=True
        )


def _is_amd64():
    """Check if host is already amd64 (no emulation needed)."""
    import platform
    return platform.machine() in ("x86_64", "AMD64")


def docker_exec(cmd, input_data=None, timeout=TIMEOUT_SECONDS):
    """Run a command inside the Docker container."""
    full_cmd = [
        "docker", "run", "--rm",
    ]
    # Only specify platform if not already on amd64
    if not _is_amd64():
        full_cmd += ["--platform", "linux/amd64"]
    full_cmd += [
        "--memory=256m",
        "--cpus=1",
        "--network=none",
        "-v", f"{PROJECT_DIR}/tests:/work/tests:ro",
        "-v", f"{PROJECT_DIR}/output:/work/output",
        DOCKER_IMAGE,
        "timeout", str(timeout),
    ] + cmd

    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            timeout=timeout + 30  # grace period for emulated environments
        )
        # Decode with error replacement to handle binary output
        result.stdout = result.stdout.decode('utf-8', errors='replace') if isinstance(result.stdout, bytes) else result.stdout
        result.stderr = result.stderr.decode('utf-8', errors='replace') if isinstance(result.stderr, bytes) else result.stderr
        return result
    except subprocess.TimeoutExpired:
        # Return a fake result indicating timeout
        class TimeoutResult:
            returncode = -1
            stdout = ""
            stderr = "TIMEOUT"
        return TimeoutResult()


def compile_with_reference(source_path, compiler, output_path, std="c11"):
    """Compile a C file with a reference compiler inside Docker."""
    src_name = os.path.basename(source_path)
    out_name = os.path.basename(output_path)

    result = docker_exec([
        compiler, f"-std={std}", "-pedantic", "-Wall", "-Werror",
        "-o", f"/work/output/{out_name}",
        f"/work/tests/{src_name}"
    ])

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def compile_with_jmcc(source_path, output_asm_path):
    """Compile a C file with JMCC (runs on host, Python)."""
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / "jmcc.py"), source_path, "-o", output_asm_path],
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS
    )
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def assemble_and_link(asm_path, output_path, freestanding=False):
    """Assemble and link JMCC output inside Docker."""
    asm_name = os.path.basename(asm_path)
    out_name = os.path.basename(output_path)

    if freestanding:
        cmd = [
            "sh", "-c",
            f"as --64 -o /tmp/prog.o /work/output/{asm_name} && "
            f"as --64 -o /tmp/start.o /work/freestanding/start.S && "
            f"ld -T /work/freestanding/linker.ld -o /work/output/{out_name} /tmp/start.o /tmp/prog.o"
        ]
    else:
        cmd = [
            "sh", "-c",
            f"as --64 -o /tmp/prog.o /work/output/{asm_name} && "
            f"gcc -o /work/output/{out_name} /tmp/prog.o -lc -lm -no-pie"
        ]

    result = docker_exec(cmd)
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def execute_hosted(binary_path, stdin_data=None):
    """Execute a hosted binary inside Docker."""
    bin_name = os.path.basename(binary_path)

    cmd = [f"/work/output/{bin_name}"]
    result = docker_exec(cmd, timeout=TIMEOUT_SECONDS)

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def execute_freestanding(binary_path):
    """Execute a freestanding binary under QEMU system emulation inside Docker."""
    bin_name = os.path.basename(binary_path)

    cmd = [
        "qemu-system-x86_64",
        "-nographic",
        "-no-reboot",
        "-device", "isa-debug-exit,iobase=0x501,iosize=2",
        "-kernel", f"/work/output/{bin_name}",
        "-serial", "stdio",
    ]

    result = docker_exec(cmd, timeout=10)

    # QEMU isa-debug-exit: exit code = (value << 1) | 1
    # So code 0 -> QEMU returns 1, code 1 -> QEMU returns 3, etc.
    actual_code = result.returncode
    if actual_code > 0:
        actual_code = (actual_code - 1) >> 1

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": actual_code,
    }


def parse_test_metadata(source_path):
    """Parse test metadata from inline comments."""
    metadata = {
        "name": "",
        "description": "",
        "expected_exit": 0,
        "expected_stdout": "",
        "environment": "hosted",
        "phase": 1,
        "expect_compile_fail": False,
        "error_pattern": "",
        "standard_ref": "",
    }

    stdout_lines = []
    in_stdout = False

    with open(source_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("//"):
                break

            comment = line[2:].strip()

            if comment.startswith("TEST:"):
                metadata["name"] = comment[5:].strip()
                in_stdout = False
            elif comment.startswith("DESCRIPTION:"):
                metadata["description"] = comment[12:].strip()
                in_stdout = False
            elif comment.startswith("EXPECTED_EXIT:"):
                metadata["expected_exit"] = int(comment[14:].strip())
                in_stdout = False
            elif comment.startswith("EXPECTED_STDOUT:"):
                rest = comment[16:].strip()
                if rest:
                    stdout_lines.append(rest)
                in_stdout = True
            elif comment.startswith("STDOUT:"):
                stdout_lines.append(comment[7:].strip())
                in_stdout = True
            elif comment.startswith("ENVIRONMENT:"):
                metadata["environment"] = comment[12:].strip()
                in_stdout = False
            elif comment.startswith("PHASE:"):
                metadata["phase"] = int(comment[6:].strip())
                in_stdout = False
            elif comment.startswith("EXPECT_COMPILE_FAIL:"):
                metadata["expect_compile_fail"] = comment[20:].strip().lower() == "yes"
                in_stdout = False
            elif comment.startswith("ERROR_PATTERN:"):
                metadata["error_pattern"] = comment[14:].strip()
                in_stdout = False
            elif comment.startswith("STANDARD_REF:"):
                metadata["standard_ref"] = comment[13:].strip()
                in_stdout = False
            elif in_stdout and comment:
                stdout_lines.append(comment)

    if stdout_lines:
        metadata["expected_stdout"] = "\n".join(stdout_lines) + "\n"

    return metadata


def run_test(source_path, compiler="jmcc", skip_reference=False):
    """
    Run a single test. Returns a result dict.
    """
    metadata = parse_test_metadata(source_path)
    source_path = str(source_path)
    test_name = metadata["name"] or Path(source_path).stem

    # Ensure output directory exists
    output_dir = PROJECT_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    result = {
        "name": test_name,
        "source": source_path,
        "phase": metadata["phase"],
        "passed": False,
        "details": "",
        "metadata": metadata,
    }

    if compiler == "jmcc":
        asm_path = str(output_dir / f"{test_name}.s")
        bin_path = str(output_dir / f"{test_name}")

        # Compile with JMCC
        comp = compile_with_jmcc(source_path, asm_path)

        if metadata["expect_compile_fail"]:
            if not comp["success"]:
                result["passed"] = True
                result["details"] = "Correctly rejected by JMCC"
            else:
                result["details"] = "JMCC should have rejected this program but accepted it"
            return result

        if not comp["success"]:
            result["details"] = f"JMCC compilation failed:\n{comp['stderr']}"
            return result

        # Assemble and link
        freestanding = metadata["environment"] == "freestanding"
        link = assemble_and_link(asm_path, bin_path, freestanding=freestanding)
        if not link["success"]:
            result["details"] = f"Assembly/linking failed:\n{link['stderr']}"
            return result

        # Execute
        if freestanding:
            exec_result = execute_freestanding(bin_path)
        else:
            exec_result = execute_hosted(bin_path)

        # Compare results
        actual_exit = exec_result["returncode"]
        actual_stdout = exec_result["stdout"]
        expected_exit = metadata["expected_exit"]
        expected_stdout = metadata["expected_stdout"]

        exit_ok = actual_exit == expected_exit
        # Compare stdout with trailing-whitespace tolerance per line
        def normalize_stdout(s):
            return '\n'.join(line.rstrip() for line in s.rstrip('\n').split('\n')) + '\n' if s else s
        stdout_ok = (not expected_stdout) or (actual_stdout == expected_stdout) or (normalize_stdout(actual_stdout) == normalize_stdout(expected_stdout))

        if exit_ok and stdout_ok:
            result["passed"] = True
            result["details"] = "PASS"
        else:
            parts = []
            if not exit_ok:
                parts.append(f"Exit code: expected {expected_exit}, got {actual_exit}")
            if not stdout_ok:
                parts.append(f"Stdout: expected {repr(expected_stdout)}, got {repr(actual_stdout)}")
            result["details"] = "; ".join(parts)

    elif compiler in ("gcc", "clang"):
        bin_path = str(output_dir / f"{test_name}_{compiler}")

        # For negative tests, check that reference compiler also rejects
        comp = compile_with_reference(source_path, compiler, bin_path)

        if metadata["expect_compile_fail"]:
            result["passed"] = not comp["success"]
            result["details"] = f"{'Correctly rejected' if result['passed'] else 'Unexpectedly accepted'} by {compiler}"
            return result

        if not comp["success"]:
            result["details"] = f"{compiler} compilation failed:\n{comp['stderr']}"
            return result

        # Execute
        exec_result = execute_hosted(bin_path)
        actual_exit = exec_result["returncode"]
        actual_stdout = exec_result["stdout"]

        exit_ok = actual_exit == metadata["expected_exit"]
        stdout_ok = (not metadata["expected_stdout"]) or (actual_stdout == metadata["expected_stdout"])

        if exit_ok and stdout_ok:
            result["passed"] = True
            result["details"] = "PASS"
        else:
            parts = []
            if not exit_ok:
                parts.append(f"Exit code: expected {metadata['expected_exit']}, got {actual_exit}")
            if not stdout_ok:
                parts.append(f"Stdout: expected {repr(metadata['expected_stdout'])}, got {repr(actual_stdout)}")
            result["details"] = "; ".join(parts)

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: run.py <source.c> [--compiler jmcc|gcc|clang]")
        sys.exit(1)

    source = sys.argv[1]
    compiler = "jmcc"
    if "--compiler" in sys.argv:
        idx = sys.argv.index("--compiler")
        compiler = sys.argv[idx + 1]

    ensure_docker_image()
    result = run_test(source, compiler=compiler)
    print(json.dumps(result, indent=2))
