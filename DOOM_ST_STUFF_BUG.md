# st_stuff.c Arrow Key Crash — Investigation Plan

## What we know

- `st_stuff.c` compiled with jmcc crashes on arrow keys during E1M1 gameplay
- Title screen renders the status bar correctly (ST_Drawer runs every frame)
- Arrow keys trigger a game tick which changes game state, then the next ST_Drawer/ST_Ticker frame crashes
- `+`/`-` keys work (they change `screenblocks` but don't trigger game ticks)
- Menu (Escape) works when m_menu.c is GCC-compiled

## What we've ruled out

1. **Struct sizes** — `player_t` (320), `st_number_t` (48), `weaponinfo_t` (24) all match GCC
2. **Field offsets** — `plyr->health` (36), `plyr->weaponowned` (124), `plyr->ammo` (160) all match GCC
3. **7+ argument passing** — V_CopyRect's 8 args are computed and passed correctly
4. **Struct copy (rep movsb)** — st_stuff.s has zero rep movsb instructions
5. **Individual patterns** — all isolated tests for `ptr->member[i]`, `ptr->array[expr]`, address-of, nested index pass
6. **Function isolation** — gave false positives due to string constant layout changes between functions

## Why isolation tests keep passing

Every pattern from st_stuff.c works in standalone tests. The bug is either:

1. **A combination of patterns** in the same function that corrupts register/stack state
2. **Global data layout** — jmcc places globals/statics in different order than GCC, causing cache/alignment issues or overlapping data
3. **A pattern we haven't identified** — something subtle in the C code that we haven't extracted into a test

## Plan

### Phase 1: Binary diff of global data sections

Compare the `.data` and `.bss` sections between jmcc and GCC:

```bash
objcopy -O binary -j .data st_stuff_jmcc.o /tmp/jmcc_data.bin
objcopy -O binary -j .data st_stuff_gcc.o /tmp/gcc_data.bin
objcopy -O binary -j .bss st_stuff_jmcc.o /tmp/jmcc_bss.bin
objcopy -O binary -j .bss st_stuff_gcc.o /tmp/gcc_bss.bin
```

Check: are static arrays the right size? Are initialized values correct? Is there overlap?

### Phase 2: Targeted function replacement (improved)

The previous reverse isolation gave false positives because replacing a function also changes data layout. Fix this by:

1. Compile st_stuff.c TWICE with jmcc — once normal, once with a `#define` that disables one function (replace body with `{}`)
2. Compare: if disabling function X fixes the crash, X is the culprit
3. This avoids the GCC/jmcc data layout mismatch problem

Candidate functions to disable (called every frame):
- `ST_Ticker` → `ST_updateWidgets` → `ST_updateFaceWidget`
- `ST_Drawer` → `ST_doPaletteStuff` + `ST_doRefresh`/`ST_diffDraw`

### Phase 3: Add runtime instrumentation inside st_stuff.c

Modify the Doom source to add checks INSIDE st_stuff.c:

```c
// At start of ST_Ticker:
fprintf(stderr, "T:plyr=%p health=%d weapon=%d\n", plyr, plyr->health, plyr->readyweapon);

// At start of ST_Drawer:
fprintf(stderr, "D:baron=%d first=%d\n", st_statusbaron, st_firsttime);
```

Compile with jmcc. If the values are correct before the crash, the bug is in what runs AFTER the print. If the values are wrong, something corrupted them.

### Phase 4: Full instruction-level asm audit

For each function in the call chain (ST_Ticker → ST_updateWidgets → ST_updateFaceWidget), compare every instruction with GCC output:

1. Check every `movl` vs `movq` — is the load/store width correct?
2. Check every `addq` offset — are struct member offsets correct?
3. Check every `imulq` stride — are array strides correct?
4. Check every comparison — signed vs unsigned
5. Check every shift — arithmetic vs logical
6. Check stack frame size — is `subq $N, %rsp` large enough for all locals?
7. Check function epilogue — does every return path have `leave; ret`?

### Phase 5: Memory sanitizer approach

Build a wrapper that catches the crash:

1. Compile st_stuff.c with jmcc but add `-fsanitize=address` to the GCC assembly step (won't work — ASAN needs source instrumentation)
2. Alternative: wrap key functions with `mprotect` to detect out-of-bounds writes
3. Or: allocate `screens[]` buffers with guard pages and catch the SIGSEGV with exact address

## Recommended order

Start with **Phase 3** (runtime instrumentation) — it's the fastest way to narrow which function and which line crashes. If the game prints trace output before crashing, we know exactly where to look. If it crashes before printing, we know the crash is in initialization, not per-frame code.

Then **Phase 1** (data section comparison) — if the global data layout is wrong, no amount of function-level analysis will find it.
