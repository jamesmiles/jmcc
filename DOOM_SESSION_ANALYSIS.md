# Doom × JMCC: Session Analysis

## Overview

This document analyses the work done to compile and run id Software's Doom (linuxdoom-1.10) using jmcc, a Python-based C compiler targeting x86-64 assembly. Doom served as a real-world integration test, exposing 37 codegen bugs across approximately 30,000 lines of C90 code.

## Methodology

### The feedback loop

The workflow followed a tight iterative cycle:

1. **Build** — Compile all 62 Doom source files with jmcc, assemble with GCC, link
2. **Run** — Launch Doom, trigger a crash (or observe incorrect behaviour)
3. **Isolate** — Narrow the crash to a specific file, function, or instruction
4. **Reproduce** — Write a minimal C test that fails with jmcc but passes with GCC
5. **Push** — Commit the failing test to the jmcc repo
6. **Poll** — Wait for the fix (typically 2-10 minutes), pull, rebuild, repeat

### Isolation techniques

Several techniques were used to identify which codegen bug caused each crash:

- **File-level bisection**: Compile individual .c files with GCC while keeping the rest jmcc. If switching one file to GCC fixes the crash, the bug is in that file's generated code.
- **Function-level splicing**: Replace individual functions in the jmcc assembly with GCC equivalents. Used for large files like `m_menu.c` where file-level isolation wasn't granular enough.
- **Crash catcher**: A `LD_PRELOAD` shared library that installs a SIGSEGV handler, printing the crash address, register state, and backtrace using `execinfo.h`.
- **Symbol table mapping**: Using `nm` to map crash addresses (`linuxxdoom+0xNNNNN`) back to function names.
- **Assembly comparison**: Side-by-side comparison of jmcc vs GCC assembly for specific functions, checking struct offsets, instruction widths, and argument passing.
- **Instrumented builds**: Adding `fprintf` traces and `backtrace()` calls to Doom source to trace which function passes bad data.

### What worked well

- **Crash catchers over GDB**: Since GDB wasn't available in the environment, the `LD_PRELOAD` signal handler approach was effective and reusable.
- **File-level bisection**: Fast way to narrow 62 files down to 1. Most crashes were isolated to a single file within 2-3 test builds.
- **Proactive test expansion**: After finding each bug, testing for related patterns (e.g., after finding `>>=` was broken for unsigned, also testing `/=` and `%=`) caught bugs before they manifested in Doom.
- **Polling loop**: Background `git fetch` polling every 60 seconds kept the feedback loop tight without manual intervention.

### What was less effective

- **Manual assembly reading**: Spent significant time reading jmcc assembly line-by-line for the `m_menu.c` crash. The assembly was correct — the actual bug (va_list ABI) was in a completely different code path than expected. Direct instrumentation would have been faster.
- **Function-level splicing**: Gave false positives early in the project because replacing a function changes string constant layout, which shifts data around and can mask or reveal bugs that aren't in the replaced function.
- **Synthetic keystroke injection (XTest)**: Attempted to automate Doom testing by sending synthetic X11 keyboard events. Unreliable in WSL2 — worked for GCC builds but not consistently for jmcc builds.

## Bug taxonomy

The 37 bugs fall into distinct categories:

### Type system / width errors (Bugs 1-7, 13-14, 17, 21, 26, 31)
**14 bugs** — The largest category. jmcc frequently used the wrong instruction width:
- `movl` (32-bit) instead of `movw` (16-bit) for short writes
- `movsbl` (sign-extend) instead of `movzbl` (zero-extend) for unsigned char
- `sarl` (arithmetic shift) instead of `shrl` (logical shift) for unsigned
- `idivl` (signed divide) instead of `divl` (unsigned divide)
- `cmpl` (32-bit compare) instead of `cmpq` (64-bit) for pointers

**Doom impact**: These caused subtle corruption everywhere — zone allocator failures, wrong angle computations, palette rendering errors, player teleporting randomly.

### Array/struct layout errors (Bugs 8-12, 19-20, 22-24, 28-29)
**11 bugs** — Wrong strides, sizes, or offsets when accessing arrays of structs, 2D arrays, and complex member chains:
- `ptr[i]` using `sizeof(element)` instead of `sizeof(pointer)` for pointer arrays
- 2D array inner dimensions truncated (1280-byte table allocated as 5 bytes)
- `ptr->member[i]` computing wrong offsets in nested access chains

**Doom impact**: Crashes during level loading, BSP traversal, texture lookup, HUD rendering.

### Initializer / data emission errors (Bugs 3, 5, 34, 36)
**4 bugs** — Global data not emitted correctly:
- String literal pointers emitted as NULL
- 2D char arrays with string initializers emitted as zeros
- Pointer arrays initialized with addresses of static data emitted as zeros

**Doom impact**: Missing sound names, menu skull cursor "not found", intermission screen NULL dereference.

### ABI / calling convention errors (Bugs 27, 32-33, 37)
**4 bugs** — Violations of the AMD64 System V ABI:
- `va_list` struct layout completely wrong (missing `gp_offset`/`fp_offset`, wrong field order)
- `va_copy` referenced undefined variable
- `sizeof(array)` in function call args caused array to be passed by value instead of decaying to pointer

**Doom impact**: Any variadic function (I_Error, printf wrappers) crashed in libc. Automap crashed when opening.

### Constant expression / parser errors (Bugs 12, 30, 35)
**3 bugs** — Failure to evaluate expressions at compile time:
- `128*256` not folded to 32768 in array dimensions
- `MAXLEN+1` not evaluated in `char buf[MAXLEN+1]`
- `case -1:` not recognized because `-1` was `UnaryOp("-", IntLiteral(1))`, not `IntLiteral(-1)`

**Doom impact**: Arrays allocated too small, switch cases for negative values silently skipped (secret platforms didn't work).

### Pointer handling errors (Bugs 15-16, 18, 25)
**3 bugs** — Pointer operations using wrong widths or instructions:
- Pointer truthiness checked only lower 32 bits (`testl` instead of `testq`)
- Pointer comparison used 32-bit `cmpl` instead of 64-bit `cmpq`
- Negative double-to-int cast left garbage in upper bits

**Doom impact**: Zone allocator treated in-use memory blocks as free, BSP traversal infinite loops.

## Timeline of this session

This session focused on bugs 31-37, starting from a mostly-playable Doom with 2 GCC fallback files remaining:

| Time | Bug | Discovery | Key technique |
|------|-----|-----------|---------------|
| Start | 31 | Player teleporting randomly after movement | Pattern from prior session: `>>=` on unsigned |
| +15m | 32 | Pressing Escape crashes (menu) | Crash catcher → I_Error → vfprintf. Assembly analysis of va_list struct layout |
| +30m | 33 | va_copy segfaults | Compile test 159 → Python NameError in codegen |
| +45m | 34 | Menu still crashes after va_list fix | W_GetNumForName backtrace → skullName all zeros. Assembly comparison of data section |
| +1h | 35 | Secret platform in zigzag room doesn't lower | File bisection (p_floor.c) → assembly shows `case -1` has no comparison jump |
| +1h15m | — | Segfault on exit | Not jmcc — Doom 64-bit porting bug: `(int)"string"` truncates pointers in m_misc.c |
| +1h30m | 36 | Exit switch crashes (intermission screen) | Crash catcher → WI_loadData → `anims[]` pointer array all zeros |
| +1h45m | 37 | Tab key crashes (automap) | Crash catcher → AM_drawLineCharacter → array passed by value. `sizeof(arr)` in same call breaks pointer decay |

## Observations

### Bug density decreased over time

Early phases found bugs in fundamental operations (pointer arithmetic, struct access, integer widths). Later bugs were increasingly subtle — the sizeof/array-decay interaction (bug 37) required both a specific argument order AND a global array to trigger.

### Real-world code finds bugs unit tests miss

Many bugs (va_list ABI, sizeof/decay, negative switch cases) would be hard to discover through systematic unit testing alone. Doom exercises these patterns in combinations that a test author wouldn't think to write. The approach of using a large real-world codebase as a fuzzer was highly effective.

### Two distinct classes of fixes

- **Doom 64-bit porting**: Changes to the Doom source to work on LP64 systems (int→long casts, pointer array sizes). These were needed regardless of compiler.
- **jmcc codegen**: Bugs in the compiler's code generation. Each was reproduced with a minimal standalone test and fixed in jmcc without changing Doom source.

### The "it works in isolation" problem

Several bugs (especially the m_menu.c crash) passed all isolated pattern tests but still crashed in Doom. The issue was usually that the bug was in a different code path than expected, or that the interaction between multiple patterns caused the failure. Instrumentation and crash catchers were more effective than assembly analysis for these cases.

## Final state

- **62/62** Doom source files compiled with jmcc (no GCC fallbacks)
- **37** codegen bugs found and fixed (tests 084-164)
- **160** total phase 5 test files
- Title screen, menu, gameplay, automap, secret platforms, level transitions, and clean exit all working
- Doom source published as [doom-wsl](https://github.com/jamesmiles/doom-wsl) with TrueColor X11 patch for WSL2
