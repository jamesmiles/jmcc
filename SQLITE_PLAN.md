# Compiling SQLite with jmcc — Plan

SQLite is the next benchmark after Doom/Chocolate Doom. It's the de facto standard for validating C compilers because:

- Single-file amalgamation: `sqlite3.c` (~270,000 lines of C89)
- No external dependencies beyond libc
- 2M+ tests in its official test suite (100% branch coverage)
- Used in production by billions of devices

If jmcc can compile SQLite and pass its test suite, jmcc is production-worthy.

## Status (2026-04-18)

- **Phase 1** ✅ Complete
- **Phase 2** ✅ Complete — full amalgamation compiles without any `-DOMIT` flags (~37 bugs fixed across sessions)
- **Phase 3** ✅ Complete — CLI runs, all SQL features work, `.quit` exits cleanly
- **Phase 4** ⬅ Next

---

## Phase 1: Get the amalgamation

Source: https://www.sqlite.org/download.html

```bash
wget https://www.sqlite.org/2024/sqlite-amalgamation-3450000.zip
unzip sqlite-amalgamation-3450000.zip
```

Files:
- `sqlite3.c` — all of SQLite in one file
- `sqlite3.h` — public API header
- `shell.c` — the `sqlite3` CLI tool
- `sqlite3ext.h` — extension API (can ignore for now)

## Phase 2: Try to compile

Full amalgamation compiles without simplification flags:

```bash
python3 jmcc.py sqlite3.c -o sqlite3.s
python3 jmcc.py shell.c  -o shell.s
as sqlite3.s -o sqlite3.o && as shell.s -o shell.o
gcc -no-pie sqlite3.o shell.o -o sqlite3_cli -lreadline -lm
```

**Methodology:** find first error, minimal reproducer, push failing test, wait for fix, rebuild.

## Phase 3: Link and run basic queries

```bash
gcc sqlite3.o shell.o -o sqlite3 -ldl -lm
./sqlite3 :memory: "CREATE TABLE t(x); INSERT INTO t VALUES(1),(2),(3); SELECT sum(x) FROM t;"
```

Expected output: `6`

If this works, SQLite is functionally running on jmcc-compiled code. Good validation milestones:
- Basic DDL (CREATE TABLE, CREATE INDEX)
- DML (INSERT, UPDATE, DELETE)
- Queries (SELECT, joins, aggregations, subqueries)
- Transactions (BEGIN/COMMIT/ROLLBACK)
- File-based databases (vs :memory:)

## Phase 4: Run SQLite's TCL test suite

The gold standard. SQLite ships 2M+ tests written in Tcl. These call into SQLite via the public C API — so jmcc only needs to compile `sqlite3.c`, not Tcl itself.

### Setup

```bash
sudo apt install tcl-dev
```

### Build testfixture

The `testfixture` binary links jmcc-compiled SQLite with GCC-compiled Tcl bindings:

```
jmcc compiles sqlite3.c      → sqlite3.o       (code under test)
GCC compiles tclsqlite.c     → tclsqlite.o     (Tcl binding glue)
GCC compiles test sources    → test*.o
Link everything              → testfixture
```

Needs the full source tree (not just amalgamation) to get `tclsqlite.c` and test harness:

```bash
git clone https://github.com/sqlite/sqlite.git sqlite-src
```

### Test targets (fastest to slowest)

| Target | Time | Coverage |
|--------|------|----------|
| `veryquick` | ~2 min | Smoke tests |
| `quicktest` | ~5 min | Common cases |
| `test` | ~30 min | Standard suite |
| `fulltest` | ~2 hours | Everything |
| `soak` | hours+ | Stress / fuzz |

Start with `veryquick`. Any failure is a jmcc codegen bug.

```bash
./testfixture test/veryquick.test
```

## Expected difficulty

| Phase | Estimated bugs | Notes |
|-------|---------------|-------|
| 1-2 compile | 5-15 | SQLite uses patterns we haven't hit: massive struct arrays, VDBE opcode dispatch, complex macros |
| 3 basic queries | 2-5 | C89 is well-understood; codegen issues dominate |
| 4 test suite | 10-30 | Edge cases, boundary conditions, bit-exact behavior |

**Total:** 20-50 bugs across several sessions.

## Success criteria

- **Minimum viable:** `sqlite3.c` compiles with jmcc, CLI tool runs, basic queries return correct results.
- **Strong:** `veryquick` test suite passes.
- **Industrial-strength:** Full `test` target passes.

## Why this matters

Passing SQLite's tests would be a stronger signal than Doom. Doom proves jmcc can build games that users will notice crashes in. SQLite proves jmcc can build code that billions of devices depend on for correctness.

It's also the natural progression of the test-driven methodology that got us from "menu crash" to "plays Doom II with music".
