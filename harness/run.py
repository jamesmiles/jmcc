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
def _use_native():
    return os.environ.get("JMCC_NATIVE", "0") == "1"


def ensure_docker_image():
    """Build the Docker image if it doesn't exist (skipped in native mode)."""
    if _use_native():
        return
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


def _native_assemble_and_link(asm_path, output_path, freestanding=False, extra_asm_paths=None):
    """Assemble and link on the host without Docker."""
    obj_path = asm_path + ".o"
    extra_obj_paths = []
    try:
        r = subprocess.run(
            ["as", "--64", "-o", obj_path, asm_path],
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS
        )
        if r.returncode != 0:
            return {"success": False, "stdout": r.stdout, "stderr": r.stderr, "returncode": r.returncode}

        # Assemble extra files (for multi-file tests)
        for extra_asm in (extra_asm_paths or []):
            extra_obj = extra_asm + ".o"
            extra_obj_paths.append(extra_obj)
            r = subprocess.run(
                ["as", "--64", "-o", extra_obj, extra_asm],
                capture_output=True, text=True, timeout=TIMEOUT_SECONDS
            )
            if r.returncode != 0:
                return {"success": False, "stdout": r.stdout, "stderr": r.stderr, "returncode": r.returncode}

        all_objs = [obj_path] + extra_obj_paths
        r = subprocess.run(
            ["gcc", "-o", output_path] + all_objs + ["-lc", "-lm", "-no-pie"],
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS
        )
        return {"success": r.returncode == 0, "stdout": r.stdout, "stderr": r.stderr, "returncode": r.returncode}
    finally:
        if os.path.exists(obj_path):
            os.unlink(obj_path)
        for ep in extra_obj_paths:
            if os.path.exists(ep):
                os.unlink(ep)


def _native_execute_hosted(binary_path, stdin_data=None):
    """Execute a hosted binary directly on the host."""
    try:
        r = subprocess.run(
            [binary_path],
            capture_output=True, timeout=TIMEOUT_SECONDS
        )
        r = type(r)(r.args, r.returncode,
                    r.stdout.decode('utf-8', errors='replace'),
                    r.stderr.decode('utf-8', errors='replace'))
        return {"stdout": r.stdout, "stderr": r.stderr, "returncode": r.returncode}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "TIMEOUT", "returncode": -1}


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


def compile_with_jmcc(source_path, output_asm_path, defines=None):
    """Compile a C file with JMCC (runs on host, Python)."""
    cmd = [sys.executable, str(PROJECT_DIR / "jmcc.py"), source_path, "-o", output_asm_path]
    for d in (defines or []):
        cmd.extend(["-D", d])
    result = subprocess.run(
        cmd,
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


def assemble_and_link(asm_path, output_path, freestanding=False, extra_asm_paths=None):
    """Assemble and link JMCC output (native or Docker)."""
    if _use_native():
        return _native_assemble_and_link(asm_path, output_path, freestanding, extra_asm_paths=extra_asm_paths)
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
    """Execute a hosted binary (native or Docker)."""
    if _use_native():
        return _native_execute_hosted(binary_path, stdin_data)
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
        "multi_file": [],
        "defines": [],
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
                rest = comment[16:]
                if rest.strip():
                    stdout_lines.append(rest.strip())
                in_stdout = True
            elif comment.startswith("STDOUT:"):
                # Preserve leading whitespace (important for formatted output)
                content = comment[7:]
                if content.startswith(" "):
                    content = content[1:]  # strip exactly one space after STDOUT:
                stdout_lines.append(content)
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
            elif comment.startswith("DEFINES:"):
                defs = comment[8:].strip()
                metadata["defines"] = [d.strip() for d in defs.replace(",", " ").split() if d.strip()]
                in_stdout = False
            elif comment.startswith("MULTI_FILE:"):
                files = comment[11:].strip()
                metadata["multi_file"] = [f.strip() for f in files.replace(",", " ").split() if f.strip()]
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
        comp = compile_with_jmcc(source_path, asm_path, defines=metadata.get("defines"))

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

        # Compile multi-file helpers
        extra_asm_paths = []
        source_dir = str(Path(source_path).parent)
        for helper_file in metadata.get("multi_file", []):
            helper_path = os.path.join(source_dir, helper_file)
            helper_asm = str(output_dir / f"{Path(helper_file).stem}.s")
            hcomp = compile_with_jmcc(helper_path, helper_asm)
            if not hcomp["success"]:
                result["details"] = f"JMCC compilation failed (helper {helper_file}):\n{hcomp['stderr']}"
                return result
            extra_asm_paths.append(helper_asm)

        # Assemble and link
        freestanding = metadata["environment"] == "freestanding"
        link = assemble_and_link(asm_path, bin_path, freestanding=freestanding, extra_asm_paths=extra_asm_paths)
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
