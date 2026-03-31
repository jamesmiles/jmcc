# Doom Compilation Preparation Plan

## Goal

Compile id Software's [Doom](https://github.com/id-Software/DOOM) (linuxdoom-1.10) using JMCC.

Doom is ~45,000 lines of clean C89 across 62 `.c` files. It uses structs, unions, function pointers, multi-dimensional arrays, fixed-point arithmetic, and standard library functions — all within reach of JMCC's current feature set. The main gaps are multi-file compilation, 64-bit (`long long`) arithmetic, and `extern`/`static` symbol visibility.

## Architecture

```
For each .c file:
    jmcc foo.c -o foo.s        # JMCC compiles to assembly
    as --64 -o foo.o foo.s     # GNU assembler

Then:
    gcc -o doom *.o -lm -lc    # GCC as linker only
```

GCC handles symbol resolution, relocation, and libc linking. JMCC only needs to produce correct assembly with proper symbol visibility (`.globl` for exported, local for `static`).

## Current Status

- **345/351 tests passing (98.3%)**
- All custom tests (Phase 1-3 + negative): 100%
- External c-testsuite: 223/229 (97.4%)

## Gap Analysis

| Feature | Doom Uses | JMCC Status | Priority |
|---------|-----------|-------------|----------|
| Basic C89 | Heavy | Working | - |
| Structs, enums, typedefs | Heavy | Working | - |
| Function pointers | Heavy | Working | - |
| Multi-dim arrays | Heavy | Working | - |
| Unions | Light | Working | - |
| Preprocessor | Heavy | Working | - |
| `long long` arithmetic | Critical (fixed-point math) | **Broken** — 32-bit ops only | P0 |
| Cast int to long long | Critical | **Broken** — cast is no-op | P0 |
| Multi-file compilation | Required (62 files) | **Not implemented** | P0 |
| `extern` variables | Required | **Broken** — allocates storage | P0 |
| `static` functions | Required | **Broken** — emits `.globl` | P0 |
| `static` globals | Required | **Broken** — emits `.globl` | P0 |
| Local `#include "file.h"` | Heavy | Partially working | P1 |
| `float`/`double` arithmetic | Light | Working | - |
| `alloca()` | 3 call sites | Not supported (VLA substitute) | P2 |
| `#pragma interface/implementation` | 5 files | Ignored (safe) | - |
| `register` keyword | Common | Parsed and ignored | - |

## Test Plan

### 27 tests in `tests/positive/doom_compat/`

Tests are ordered by bug-finding priority. Each is self-contained with inline metadata.

---

### Category 1: Long Long Arithmetic (5 tests) — P0

Our codegen uses 32-bit `imull`/`sarl`/`shll` everywhere. Doom's fixed-point math does `((long long)a * (long long)b) >> FRACBITS`. These tests will fail immediately and drive the 64-bit arithmetic fix.

**`001_longlong_multiply.c`**
```
long long a = 100000LL;
long long b = 100000LL;
long long c = a * b;  // 10000000000 — exceeds 32-bit
```
Exposes: `imull` truncation. Needs `imulq` for 64-bit operands.

**`002_longlong_shift.c`**
```
long long x = 1LL << 40;
long long y = x >> 16;
```
Exposes: `shll`/`sarl` only operates on 32 bits. Needs `shlq`/`sarq`.

**`003_fixedpoint_doom.c`**
```
// Doom's FixedMul: ((long long)a * (long long)b) >> FRACBITS
int a = 0x10000;  // 1.0 in 16.16 fixed point
int b = 0x30000;  // 3.0
int result = (int)(((long long)a * (long long)b) >> 16);
// result should be 0x30000 (3.0)
```
Exposes: The trifecta — cast no-op + 32-bit multiply + 32-bit shift.

**`004_longlong_cast_signextend.c`**
```
int x = -1;
long long y = (long long)x;  // should be 0xFFFFFFFFFFFFFFFF, not 0x00000000FFFFFFFF
```
Exposes: Cast is no-op, no `movslq` sign extension emitted.

**`005_longlong_literal.c`**
```
long long x = 0x123456789LL;  // exceeds 32 bits
```
Exposes: Whether lexer/codegen handle 64-bit integer literals correctly.

---

### Category 2: Multi-file Compilation (5 tests) — P0

Requires harness changes (new `MULTI_FILE:` metadata) and codegen fixes for `extern`/`static`.

**`006_extern_variable.c`** + `006_helper.c`
- Helper defines `int shared_var = 42;`
- Main declares `extern int shared_var;` and reads it
- Exposes: `extern` globals allocating storage → duplicate symbol at link time

**`007_extern_function.c`** + `007_helper.c`
- Helper defines `int compute(int x) { return x * 2; }`
- Main declares and calls it
- Exposes: Cross-file function linkage

**`008_static_function.c`** + `008_helper.c`
- Both files define `static int helper(void)` with different return values
- Exposes: `.globl` emitted for static functions → duplicate symbol

**`009_static_global.c`** + `009_helper.c`
- Both files define `static int counter = 0;`
- Exposes: `.globl` emitted for static globals → duplicate symbol

**`010_multifile_struct.c`** + `010_helper.c` + `010_shared.h`
- Shared struct definition in header, one file fills it, another reads it
- Exposes: Include path handling + struct layout consistency across translation units

---

### Category 3: Local Include Paths (4 tests) — P1

**`011_quoted_include.c`** + `011_doomdef.h`**
- `#include "011_doomdef.h"` with macro + struct definitions

**`012_nested_include.c`** + `012_outer.h` + `012_inner.h`**
- Header including another header (Doom's include graph pattern)

**`013_include_guard.c`** + `013_guarded.h`**
- Standard `#ifndef` guard with intentional double inclusion

**`014_pragma_ignore.c`**
- `#pragma interface` / `#pragma implementation` should be silently ignored

---

### Category 4: Doom Function Pointer Patterns (3 tests)

**`015_actionf_union.c`**
- Doom's `actionf_t` union: `union { void(*acv)(void); void(*acp1)(void*); }`
- Store function via one member, call via another

**`016_func_pointer_array.c`**
- Dispatch table: `void (*actions[4])(int) = {fn0, fn1, fn2, fn3};`
- Call by index: `actions[i](arg);`

**`017_func_pointer_cast.c`**
- Cast between function pointer types (Doom's action function pattern)

---

### Category 5: Large Switch Statements (2 tests)

**`018_large_switch.c`**
- 50+ cases simulating Doom's line special dispatch (`P_UseSpecialLine`)
- Tests: correct dispatch for low, middle, and high case values

**`019_switch_enum.c`**
- Switch on enum values (Doom's `statenum_t`, `weapontype_t` patterns)

---

### Category 6: Bit Manipulation (2 tests)

**`020_bit_manipulation.c`**
- Doom's flag patterns: `flags |= MF_SOLID | MF_SHOOTABLE`, `flags &= ~MF_SPECIAL`, `if (flags & MF_SOLID)`

**`021_hex_shift.c`**
- `(x >> 8) & 0xFF`, `(x & 0xF0) << 4` — Doom's byte extraction patterns

---

### Category 7: Doom Struct Patterns (3 tests)

**`022_struct_array_member.c`**
- Struct with array member accessed through pointer: `p->vals[3] = 42;`

**`023_thinker_linked_list.c`**
- Doom's thinker pattern: self-referential struct with `actionf_t` union member, linked list traversal

**`024_void_ptr_cast.c`**
- Allocate struct, pass as `void*`, cast back and access members (Doom's universal pattern)

---

### Category 8: String Tables (1 test)

**`025_string_table.c`**
- `const char *names[] = {"imp", "demon", "baron"};` — array of string pointers with index lookup

---

### Category 9: Register Keyword (1 test)

**`026_register_keyword.c`**
- `register int i;` in loops — should parse and ignore

---

### Category 10: alloca / VLA (1 test)

**`027_alloca_vla.c`**
- VLA as substitute for `alloca()`: `int n = 100; char buf[n]; buf[0] = 'A'; buf[99] = 'Z';`

---

## Implementation Sequence

### Phase 1: Single-file tests (no harness changes needed)

1. Write all single-file tests (categories 1, 3-10) — 22 tests
2. Run them. Long long tests (001-005) will fail immediately.
3. Fix 64-bit arithmetic in codegen:
   - `imulq`/`addq`/`subq` for `long long` operands
   - `sarq`/`shlq` for 64-bit shifts
   - `movslq` for int → long long cast sign extension
   - Track operand types through expressions

### Phase 2: Multi-file support

1. Add `MULTI_FILE:` metadata parsing to `parse_test_metadata()`
2. Update `compile_with_jmcc()` to compile multiple files to `.s`
3. Update `assemble_and_link()` to assemble multiple `.o` files and link
4. Update test runner to discover `doom_compat/` directory
5. Write multi-file tests (006-010)
6. Fix codegen:
   - `extern` globals: don't emit `.bss`/`.data` storage, just reference symbol
   - `static` functions: don't emit `.globl`
   - `static` globals: don't emit `.globl`
   - Add `is_static` to `FuncDecl` AST node
   - Propagate `static` from parser to function declarations

### Phase 3: Compile actual Doom files

1. Clone Doom source into test area
2. Try compiling each `.c` file individually with JMCC
3. Fix whatever breaks (likely edge cases in our parser/codegen)
4. Assemble all `.o` files
5. Link with GCC
6. Run

## Predicted Compiler Fixes

| Fix | File | Description |
|-----|------|-------------|
| 64-bit multiply | codegen.py | Use `imulq` when operands are `long long` |
| 64-bit shift | codegen.py | Use `sarq`/`shlq` for 64-bit operands |
| 64-bit add/sub | codegen.py | Use `addq`/`subq` for `long long` |
| Cast codegen | codegen.py | `movslq` for int→long long sign extension |
| Extern globals | codegen.py | Skip `.bss`/`.data` emission for `is_extern` types |
| Static functions | codegen.py | Skip `.globl` for `is_static` functions |
| Static globals | codegen.py | Skip `.globl` for `is_static` globals |
| FuncDecl.is_static | ast_nodes.py | Add field to AST node |
| Static propagation | parser.py | Pass `is_static` from type spec to FuncDecl |
