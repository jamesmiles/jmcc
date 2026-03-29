# JMCC — C Compiler Plan

## 1. Language Choice: Python

**Rationale:** Zero compile time = fastest possible feedback loop. We edit, we run, we see results. Python 3.13 is available on this machine. The compiler emits x86-64 assembly text, which is assembled/linked by standard tools (GNU as/ld) inside the execution harness. Performance of the compiler itself is not the bottleneck — correctness and iteration speed are.

## 2. Target

- **Architecture:** x86-64 (Linux, ELF)
- **Standard:** C11 (ISO/IEC 9899:2011) — modern, well-specified, widely supported
- **ABI:** System V AMD64 ABI

The host machine is ARM64 (Apple Silicon). All compiled test programs run inside Docker (x86-64 Linux) or QEMU, never natively on the host. This is a safety feature.

---

## 3. Execution Harnesses

### 3.1 Hosted Environment (Docker)

For normal C programs that use libc (`printf`, `malloc`, `exit`, etc.):

```
┌─────────────────────────────────────────┐
│  Docker: x86-64 Linux (Debian slim)     │
│  ┌───────────────────────────────────┐  │
│  │  gcc/clang (reference compilers)  │  │
│  │  as, ld (assembler/linker)        │  │
│  │  test runner scripts              │  │
│  └───────────────────────────────────┘  │
│  Mounts: ./tests, ./output (read-only)  │
│  Limits: --memory=256m --cpus=1         │
│          --timeout via timeout(1)       │
│          --network=none                 │
│  Captures: stdout, stderr, exit code    │
└─────────────────────────────────────────┘
```

- **Image:** Custom Dockerfile based on `debian:bookworm-slim` with `gcc`, `clang`, `binutils`, `nasm`
- **Isolation:** No network, memory-limited, CPU-limited, timeout-killed
- **Output capture:** stdout/stderr saved to files, exit code recorded
- **Memory dumps:** Core dumps enabled inside container, copied out for analysis
- **Logging:** Compiler warnings/errors from reference compilers captured separately

### 3.2 Freestanding Environment (QEMU System Emulation)

For bare-metal C programs (no libc, no OS):

```
┌──────────────────────────────────────────┐
│  QEMU system x86-64 (no OS)             │
│  ┌────────────────────────────────────┐  │
│  │  Flat binary / ELF loaded at 0x..  │  │
│  │  Serial port → stdout capture      │  │
│  │  ISA debug exit → exit code        │  │
│  │  Memory dump via QEMU monitor      │  │
│  └────────────────────────────────────┘  │
│  Timeout: killed after N seconds         │
│  Captures: serial output, exit code,     │
│            memory dump                   │
└──────────────────────────────────────────┘
```

- **Mechanism:** QEMU `-nographic -serial stdio -device isa-debug-exit`
- **Programs write to:** I/O port 0x3f8 (serial) for output, port 0x501 (isa-debug-exit) for exit code
- **Minimal runtime:** We provide a tiny `_start` + serial write helper (~50 lines of asm) that freestanding tests link against
- **Runs inside Docker** for portability (QEMU installed in the container)
- **Timeout:** QEMU killed after configurable limit (default 10s)

### 3.3 Harness Runner (`harness/run.py`)

A single Python script that:
1. Takes: assembly file (JMCC output) + test metadata (expected output, expected exit code, environment type)
2. Builds inside Docker (assemble + link, optionally with libc or freestanding runtime)
3. Executes with appropriate harness (Docker exec or QEMU)
4. Captures stdout, stderr, exit code, optional core dump
5. Returns structured result (pass/fail, actual vs expected, diagnostics)

---

## 4. C11 Standard — Decomposed Requirements

We target C11 (ISO/IEC 9899:2011). Here is the feature decomposition, ordered roughly by implementation priority (foundational features first):

### Phase 1: Minimal Viable Compiler
1. **Lexer/Tokenizer** — All C11 tokens, preprocessing tokens, keywords
2. **Integer literals** — decimal, hex, octal, binary; suffixes (u, l, ll, etc.)
3. **Character literals** — char, escape sequences
4. **String literals** — basic, concatenation
5. **Comments** — `//` and `/* */`
6. **Basic types** — `int`, `char`, `void`, `long`, `short`, `signed`, `unsigned`
7. **Functions** — declaration, definition, calls, return values
8. **Local variables** — declaration, initialization, assignment
9. **Arithmetic operators** — `+`, `-`, `*`, `/`, `%`
10. **Comparison operators** — `==`, `!=`, `<`, `>`, `<=`, `>=`
11. **Logical operators** — `&&`, `||`, `!`
12. **Bitwise operators** — `&`, `|`, `^`, `~`, `<<`, `>>`
13. **Control flow** — `if`/`else`, `while`, `for`, `do`/`while`
14. **`return` statement**
15. **Global variables**
16. **Pointers** — declaration, dereference, address-of
17. **Arrays** — declaration, indexing, pointer decay
18. **`sizeof` operator**

### Phase 2: Core Language
19. **Strings** — pointer-to-char, string literals in data section
20. **Type casting** — implicit and explicit
21. **Compound assignment** — `+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `|=`, `^=`, `<<=`, `>>=`
22. **Increment/decrement** — `++`, `--` (prefix and postfix)
23. **Ternary operator** — `? :`
24. **Comma operator**
25. **`break`, `continue`**
26. **`switch`/`case`/`default`**
27. **`goto` and labels**
28. **Structs** — declaration, member access (`.` and `->`), nested
29. **Unions**
30. **Enums**
31. **`typedef`**
32. **Function pointers**
33. **Multi-dimensional arrays**
34. **Variadic functions** — `va_list`, `va_start`, `va_arg`, `va_end`
35. **Static local variables**
36. **Storage classes** — `auto`, `register`, `static`, `extern`

### Phase 3: Advanced Features
37. **Preprocessor** — `#include`, `#define` (object-like), `#define` (function-like), `#ifdef`/`#ifndef`/`#if`/`#elif`/`#else`/`#endif`, `#undef`, `#error`, `#pragma`, `__LINE__`, `__FILE__`, `__DATE__`, `__TIME__`, `##` (token paste), `#` (stringify)
38. **Floating-point types** — `float`, `double`, `long double`
39. **Floating-point arithmetic** — operations, conversions, literals
40. **Initializer lists** — arrays, structs, nested
41. **Designated initializers** (C99/C11) — `.field = val`, `[idx] = val`
42. **Compound literals** (C99/C11) — `(type){...}`
43. **`_Bool` / `<stdbool.h>`** (C99/C11)
44. **`inline` functions** (C99/C11)
45. **`restrict` qualifier** (C99/C11)
46. **`_Static_assert`** (C11)
47. **`_Alignas` / `_Alignof`** (C11)
48. **`_Noreturn`** (C11)
49. **`_Generic`** (C11)
50. **Anonymous structs and unions** (C11)
51. **`const`, `volatile` qualifiers**
52. **Bit-fields**
53. **Flexible array members** (C99)
54. **Variable-length arrays (VLAs)** (C11: optional, but we'll support)
55. **Complex numbers** (`_Complex`) — lower priority
56. **Wide characters / Unicode** — `wchar_t`, `char16_t`, `char32_t` — lower priority
57. **Atomics** (`_Atomic`, `<stdatomic.h>`) — lower priority
58. **Thread-local storage** (`_Thread_local`) — lower priority

### Phase 4: Complete Implementation
59. **Full preprocessor** — all standard macros, predefined macros, `#line`, `#pragma`
60. **Full type system** — all implicit conversion rules, integer promotion, usual arithmetic conversions
61. **Complete expression parsing** — all precedence levels, associativity
62. **All statement types** — complete
63. **Complete declaration syntax** — complex declarators, abstract declarators
64. **Linkage rules** — internal, external, no linkage
65. **Scope rules** — block, function, file, function prototype
66. **Standard headers** — freestanding headers (`<stddef.h>`, `<stdint.h>`, `<limits.h>`, `<float.h>`, `<stdarg.h>`, `<stdbool.h>`, `<stdnoreturn.h>`, `<stdalign.h>`)

---

## 5. Test Strategy

### 5.1 Test Organization

```
tests/
├── positive/                    # Programs that MUST compile and run correctly
│   ├── phase1/                  # Minimal viable compiler tests
│   │   ├── 001_return_zero.c
│   │   ├── 002_return_literal.c
│   │   ├── ...
│   ├── phase2/                  # Core language tests
│   ├── phase3/                  # Advanced features
│   └── phase4/                  # Complete implementation
├── negative/                    # Programs that MUST NOT compile
│   ├── syntax_errors/
│   ├── type_errors/
│   ├── semantic_errors/
│   └── constraint_violations/
├── external/                    # Third-party test suites
│   ├── gcc-torture/             # GCC C Torture Test Suite (filtered)
│   └── c-testsuite/            # c-testsuite (Nils Wogatzky)
├── freestanding/                # Bare-metal tests (QEMU harness)
└── test_manifest.json           # Test registry with metadata
```

### 5.2 Test File Format

Each test file contains inline metadata as comments:

```c
// TEST: return_42
// DESCRIPTION: Function returns integer literal 42
// EXPECTED_EXIT: 42
// EXPECTED_STDOUT:
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.8.6.4 (The return statement)

int main(void) {
    return 42;
}
```

For more complex expected output:

```c
// TEST: printf_hello
// DESCRIPTION: Print hello world using printf
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: Hello, World!
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 7.21.6.1 (The fprintf function)

#include <stdio.h>

int main(void) {
    printf("Hello, World!\n");
    return 0;
}
```

Negative test:

```c
// TEST: missing_semicolon
// DESCRIPTION: Missing semicolon should produce compile error
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: expected ';'
// PHASE: 1

int main(void) {
    return 0
}
```

### 5.3 Reference Compilers

We use **two** reference compilers to validate test expectations:

1. **GCC** (`gcc -std=c11 -pedantic -Wall -Werror`) — the gold standard
2. **Clang** (`clang -std=c11 -pedantic -Wall -Werror`) — a second opinion

Both run inside the Docker container. If they disagree, we investigate:
- If one accepts and one rejects: likely a compiler extension. We use `-pedantic-errors` and document.
- If both produce different output: likely undefined behavior. We document and define JMCC's behavior.

### 5.4 Test Validation Pipeline

```
For each test file:
  1. Parse inline metadata (expected output, exit code, environment)
  2. Compile with GCC → record: compiles? warnings?
  3. Compile with Clang → record: compiles? warnings?
  4. If positive test:
     a. Both must compile (or test metadata is wrong)
     b. Execute GCC binary → capture stdout, exit code
     c. Execute Clang binary → capture stdout, exit code
     d. Compare both outputs to expected → flag discrepancies
     e. Compile with JMCC → capture stdout, exit code
     f. Execute JMCC binary → capture stdout, exit code
     g. Compare JMCC output to expected → PASS/FAIL
  5. If negative test:
     a. Both reference compilers should reject (or test is wrong)
     b. JMCC must also reject → PASS if rejected, FAIL if accepted
```

### 5.5 External Test Suites

#### GCC C Torture Test Suite
- Source: GCC source tree (`gcc/testsuite/gcc.c-torture/execute/`)
- **Filtering:** We exclude tests that use GNU extensions (`__attribute__`, `typeof`, `__builtin_*`, statement expressions, etc.) using a script that greps for GNU-isms
- Each remaining test is tagged with the C11 feature it exercises
- Expected behavior derived from execution under GCC/Clang

#### c-testsuite
- Source: https://github.com/c-testsuite/c-testsuite
- Already designed to be portable/standard-compliant
- Integrates directly into our test runner

### 5.6 Negative Tests

Categories:
- **Syntax errors:** missing semicolons, unmatched braces, invalid tokens
- **Type errors:** incompatible assignments, wrong argument types, void arithmetic
- **Semantic errors:** undeclared variables, duplicate definitions, break outside loop
- **Constraint violations:** array size negative, bit-field too wide, incomplete type usage
- **Preprocessor errors:** unterminated `#if`, `#include` not found, macro redefinition

Each negative test specifies a regex pattern that the compiler error must match.

### 5.7 Reward Signal

```
score = passing_tests / total_tests

Breakdown by category:
  positive_score = positive_passing / positive_total
  negative_score = negative_passing / negative_total
  external_score = external_passing / external_total

Overall = (positive_passing + negative_passing + external_passing) /
          (positive_total + negative_total + external_total)
```

Displayed after every test run. Tracked over time in `test_results/history.json`.

---

## 6. Compiler Architecture (JMCC)

```
Source (.c)
    │
    ▼
┌──────────┐
│  Lexer   │  → Token stream
└──────────┘
    │
    ▼
┌──────────────┐
│  Preprocessor│  → Expanded token stream
└──────────────┘
    │
    ▼
┌──────────┐
│  Parser  │  → AST (Abstract Syntax Tree)
└──────────┘
    │
    ▼
┌──────────────┐
│  Semantic    │  → Annotated AST (types resolved, scopes checked)
│  Analysis    │
└──────────────┘
    │
    ▼
┌──────────────┐
│  IR          │  → Intermediate Representation (three-address code / SSA)
│  Generation  │
└──────────────┘
    │
    ▼
┌──────────────┐
│  (Optional)  │  → Optimized IR
│  Optimizer   │
└──────────────┘
    │
    ▼
┌──────────────┐
│  Code Gen    │  → x86-64 Assembly (AT&T syntax)
│  (x86-64)    │
└──────────────┘
    │
    ▼
Assembly (.s)  → assembled/linked by GNU as + ld (inside Docker)
    │
    ▼
Executable (ELF)
```

### Implementation order:
1. **Lexer** — straightforward, write tests first
2. **Parser** — recursive descent (no parser generator — we do it by hand)
3. **Semantic analysis** — type checking, scope resolution
4. **Code generation** — direct AST-to-assembly initially (skip IR for Phase 1)
5. **IR** — introduce when optimizations or complex features need it (Phase 2+)
6. **Preprocessor** — implement incrementally, `#include` first, macros later

---

## 7. Development Process

### 7.1 Inner Loop (Rapid Feedback)

```
┌─────────────────────────────────────────────┐
│                                             │
│  1. Pick feature from standard              │
│  2. Write/update test(s) for that feature   │
│  3. Validate tests against GCC/Clang        │
│  4. Implement feature in JMCC               │
│  5. Run test suite:                         │
│     ./test.sh [--phase N] [--filter PATTERN]│
│  6. If failures:                            │
│     - Read error output / logs              │
│     - Fix compiler                          │
│     - Goto 5                                │
│  7. If all pass:                            │
│     - Run full suite (all phases)           │
│     - Check no regressions                  │
│     - Commit & push                         │
│     - Pick next feature → goto 1            │
│                                             │
└─────────────────────────────────────────────┘
```

### 7.2 Test Command

```bash
# Run all tests
./test.sh

# Run specific phase
./test.sh --phase 1

# Run specific test
./test.sh --filter return_zero

# Run only JMCC tests (skip reference compiler validation)
./test.sh --jmcc-only

# Show reward signal
./test.sh --score
```

Output:
```
=== JMCC Test Results ===
Phase 1: 45/45  (100.0%)
Phase 2: 23/67  ( 34.3%)
Phase 3:  0/42  (  0.0%)
Phase 4:  0/15  (  0.0%)
Negative: 30/30 (100.0%)
External:  0/200 (  0.0%)
─────────────────────────
TOTAL:    98/399 ( 24.6%)
```

### 7.3 CI (GitHub Actions)

```yaml
# .github/workflows/test.yml
# Triggers: push to main, pull requests
# Steps:
#   1. Checkout
#   2. Set up Python 3.13
#   3. Build Docker test image
#   4. Run full test suite
#   5. Upload test results as artifact
#   6. Post score as commit status / PR comment
```

### 7.4 Local Development

```bash
# One-time setup
docker build -t jmcc-test harness/
pip install -r requirements.txt  # (minimal: just pytest for unit tests)

# Development
python jmcc.py input.c -o output.s    # Compile
./test.sh                               # Test
./test.sh --score                        # Reward signal
```

---

## 8. Milestones

| Milestone | Description | Reward Target |
|-----------|-------------|---------------|
| M0 | Infrastructure: Docker, harness, test runner, CI, first test | N/A |
| M1 | Phase 1 complete: all basic tests pass | ~25% |
| M2 | Phase 2 complete: core language features | ~50% |
| M3 | Preprocessor working, external tests starting to pass | ~65% |
| M4 | Phase 3 complete: advanced features | ~80% |
| M5 | External test suites passing at high rate | ~90% |
| M6 | Phase 4, edge cases, full compliance | ~95%+ |

---

## 9. Anti-Cheating Measures

- JMCC must produce x86-64 assembly, not call out to GCC/Clang
- Tests verify JMCC's assembly output is structurally valid (not just copied)
- Reference compilers are ONLY used for test validation, never at JMCC runtime
- The `jmcc.py` source has no subprocess calls to other compilers
- CI runs with no network access during JMCC compilation step

---

## 10. File Structure

```
jmcc/
├── PLAN.md                  # This file
├── PROMPT.md                # Original prompt
├── README.md                # Project readme
├── jmcc.py                  # Compiler entry point
├── jmcc/                    # Compiler source
│   ├── __init__.py
│   ├── lexer.py
│   ├── parser.py
│   ├── ast_nodes.py
│   ├── semantic.py
│   ├── codegen.py
│   ├── preprocessor.py
│   └── errors.py
├── harness/                 # Execution harness
│   ├── Dockerfile
│   ├── run.py               # Harness runner
│   ├── freestanding/        # Freestanding runtime (minimal asm)
│   │   ├── start.s
│   │   ├── serial.s
│   │   └── linker.ld
│   └── hosted/              # Hosted helpers
├── tests/                   # Test programs
│   ├── positive/
│   ├── negative/
│   ├── freestanding/
│   └── external/
├── test.sh                  # Main test runner
├── test_runner.py           # Python test orchestrator
├── requirements.txt
└── .github/
    └── workflows/
        └── test.yml
```
