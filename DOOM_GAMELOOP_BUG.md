# Doom Game Loop Crash — Remaining Codegen Bug

## Status

Doom compiles (62/62 files), assembles, links, and completes all initialization through `ST_Init`. With a TrueColor X11 patch, it opens a window and enters the game loop — but crashes before rendering the first frame.

The same build compiled with GCC runs perfectly and renders the title screen.

## What we know

- The crash happens between `I_InitGraphics` completing and `I_FinishUpdate` being called (first frame render).
- The call path is: `D_DoomLoop` → `D_Display` → `I_FinishUpdate` (never reached), or `D_DoomLoop` → `TryRunTics` → `G_BuildTiccmd` (crashes here in some runs).
- Earlier backtraces pointed to `G_BuildTiccmd+195` and `R_InitBuffer+131`.
- The crash is **intermittent** — with ASLR enabled, ~65% of runs get past init; with ASLR disabled (`setarch -R`), init always succeeds but the game loop always crashes.
- Redirecting stdout/stderr (e.g. `&>/dev/null`) makes the crash rate worse (near 100%).
- No single jmcc-compiled file causes the crash when swapped into an otherwise-GCC build. The bug only manifests when multiple files are jmcc-compiled together.

## What this points to

The "no single file" + "intermittent" + "ASLR-sensitive" pattern strongly suggests **memory corruption from incorrect codegen**, not a logic error in one function. The zone allocator's `Z_ChangeTag` check (`id != ZONEID`) fails frequently, meaning zone block headers are being overwritten.

Likely candidates:
1. **A remaining stride/offset bug** — similar to bugs 084/085 but in a pattern we haven't tested yet (e.g. arrays of structs containing pointers, or pointer arithmetic on struct members).
2. **A store-width bug beyond short/char** — bug 087 fixed `movl` for `short` members; there may be a similar issue for `char` stores in specific struct layouts (the zone allocator's `memblock_t` has `int` fields adjacent to pointer fields).
3. **Stack frame corruption** — if jmcc miscalculates stack frame sizes for functions with many locals, a function's stack writes could overwrite the caller's data. This would explain why it only manifests with multiple jmcc files (more functions with jmcc stack layouts).

## How to investigate

The most promising approach is to do a **function-level binary search**: compile one function at a time with jmcc while keeping the rest GCC, testing whether the game loop survives. The `--filter` style approach at the file level didn't find anything because the bug requires multiple jmcc functions interacting.

Alternatively, write tests for:
- Struct arrays containing pointer members, accessed via index
- Functions with >8 local variables (stack frame pressure)
- Pointer arithmetic involving struct member offsets passed across function calls
- Zone allocator patterns: allocate, write through returned pointer, then verify adjacent block headers are intact
