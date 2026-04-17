# SQLite Runtime Debugging Plan

**Goal:** Isolate the jmcc codegen bug that causes `sqlite3_open()` to crash.

**Known facts:**
- SQLite compiles and links cleanly with jmcc
- `sqlite3_libversion()` works (returns "3.45.0")
- `sqlite3_initialize()` works
- `sqlite3_open()` crashes: SIGSEGV in `sqlite3_str_vappendf` at `movsbl (%rax), %eax`
- GCC-compiled SQLite works perfectly
- Simple va_list / large-frame / many-arg patterns reproduce in isolation: all pass
- Bug triggers only in SQLite's full context

The "one big file" challenge means we can't do file-level bisection like Doom. But we have several alternatives, ranked from easiest to most invasive:

## Approach 1: Object-level function swap (RECOMMENDED FIRST)

Build sqlite3.c twice — once with jmcc, once with GCC. Then create a hybrid `.o` by swapping individual function symbols.

```bash
# Two builds of the same source
gcc -c sqlite3.c -o sqlite3_gcc.o [flags]
jmcc.py sqlite3.c → sqlite3.s; gcc -c sqlite3.s -o sqlite3_jmcc.o

# Extract specific functions from each
objcopy --keep-symbols=sqlite3_str_vappendf sqlite3_gcc.o vappendf_gcc.o
objcopy --remove-section=.text.sqlite3_str_vappendf sqlite3_jmcc.o sqlite3_jmcc_minus.o

# Link mostly-jmcc + GCC vappendf
gcc test.o sqlite3_jmcc_minus.o vappendf_gcc.o -o sqlite3_test
```

If it works with GCC vappendf → bug is in vappendf codegen. If still crashes → bug is in the caller passing bad data to vappendf.

Walk up the call chain (sqlite3MPrintf, sqlite3VMPrintf, openDatabase, etc.) until we find the function that, when GCC-compiled, eliminates the crash.

**Pros:** Surgical, definitive. **Cons:** objcopy section manipulation can be fiddly.

## Approach 2: Source-level bisection on hand-split SQLite

Split sqlite3.c at function boundaries into several files. Compile each chunk with either jmcc or GCC. Link them together. Bisect to find the chunk containing the bug.

```bash
# Split sqlite3.c at every 10000 lines (or function boundaries)
csplit sqlite3.c '/^static\|^SQLITE_/' -k -f part_

# Each part includes the necessary headers/declarations
# Test each combination
```

**Pros:** Closer to Doom-style methodology. **Cons:** SQLite has many internal references; splitting cleanly is tricky.

## Approach 3: Targeted printf instrumentation

Add `fprintf(stderr, ...)` calls directly in sqlite3.c at strategic points:

```c
// Before vappendf
fprintf(stderr, "vappendf: pAccum=%p fmt=%p\n", pAccum, fmt);

// At entry to suspected functions
fprintf(stderr, "MPrintf called with fmt=%s\n", zFormat);
```

This won't isolate the bug class, but pinpoints the exact failing call — its parameters and call site. Once we know what's wrong (e.g., "fmt is NULL" or "ap points to garbage"), we can write a focused reproducer.

**Pros:** Quick to apply, gives concrete data. **Cons:** Doesn't tell us WHY the value is wrong.

## Approach 4: Differential disassembly

Compile sqlite3.c with both compilers. Extract `sqlite3_str_vappendf` from each `.s` file. Compare instruction by instruction.

```bash
sed -n '/^sqlite3_str_vappendf:/,/^[A-Za-z_]/p' sqlite3_jmcc.s > vappendf_jmcc.s
sed -n '/^sqlite3_str_vappendf:/,/^[A-Za-z_]/p' sqlite3_gcc.s > vappendf_gcc.s
# Compare structure (not instruction-by-instruction; they'll differ in style)
```

Look for differences in:
- Stack frame size
- Argument handling (where each parameter is stored)
- Loop structure
- va_list access pattern

**Pros:** Can spot specific bug like "loaded wrong stack offset". **Cons:** Hard to diff machine code that's structurally different.

## Approach 5: Reduce SQLite to a self-contained vappendf test

Extract `sqlite3_str_vappendf` and its dependencies into a standalone file. Run it directly from a test program. If it reproduces, we have a small reproducer. If not, the bug requires the calling context — go up a level.

**Pros:** Definitive minimal reproducer. **Cons:** SQLite's internal coupling means this is a lot of manual extraction work.

## Recommended order

1. **Approach 3 first** (printf instrumentation) — 10 minutes, tells us "fmt was NULL" or "the format was X" or "we got there but then crashed".
2. **Approach 1 next** (object swap) — narrows to the specific buggy function.
3. **Approach 5 last** (extract to standalone) — once we know the function, write a minimal repro.

This converges fast: instrumentation tells us where, object swap tells us which function generates wrong code, extraction gives us the test case to push.

## Once we have a minimal repro

Standard test-driven loop: push test, wait for fix, rebuild SQLite, find next crash. Should take 5-15 iterations to get to a working `sqlite3_open`.

After `sqlite3_open` works, we tackle the next runtime bug (likely in `sqlite3_exec` or query execution), then run the TCL test suite for the deep coverage.
