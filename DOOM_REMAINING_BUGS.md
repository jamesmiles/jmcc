# Remaining Doom Codegen Bugs

## Status

E1M1 is playable with 60/62 files compiled by jmcc. Two files require GCC fallback:

| File | Symptoms | When |
|------|----------|------|
| `r_bsp.c` | Segfault (no error message) | During E1M1 rendering |
| `hu_stuff.c` | Segfault | During E1M1 gameplay (not title screen) |

Title screen works with all 62/62 jmcc files.

## What we know

### r_bsp.c

**Functions:** R_ClearDrawSegs, R_ClipSolidWallSegment, R_ClipPassWallSegment, R_ClearClipSegs, R_AddLine, R_CheckBBox, R_Subsector, R_RenderBSPNode

**Crash characteristics:**
- 100% reproducible with `-warp 1 1`
- Silent segfault — no Doom error message, no signal handler output
- Signal handler (`sigaction` with `SA_SIGINFO`) doesn't fire, suggesting stack frame corruption
- Earlier builds showed "Bad R_RenderWallRange: 62 to 0" (start > stop), but that was from a source file corruption during debugging (now fixed)

**Patterns tested and PASSING:**
- `ptr->array2d[i]` decay to pointer (test 138) ✓
- `(ptr+1)->member` struct pointer arithmetic (manual test) ✓
- `ptr->children[side^1]` unsigned short array through pointer (manual test) ✓
- `&nodes[bspnum]` address of array element (manual test) ✓
- `angle_t` unsigned typedef comparison and shift (tests 135-136) ✓
- `(angle+ANG90)>>ANGLETOFINESHIFT` with logical shift (test 136) ✓
- `solidsegs` cliprange walking with `(start+1)->first` (manual test) ✓
- `bsp->bbox[side^1]` passed to function — array decay verified in asm ✓
- BSP traversal pattern with recursive calls (manual test) ✓
- sizeof(node_t) = 52, stride correct in asm ✓

**What's different about the real code:**
- r_bsp.c has many global variable assignments (`curline = line`, `frontsector = sub->sector`, etc.)
- Deep recursion through R_RenderBSPNode → R_CheckBBox → R_RenderBSPNode
- The crash prevents the signal handler from running — possibly the jmcc prologue/epilogue corrupts the stack, so when the crash happens deep in recursion, the stack is too damaged for the handler

### hu_stuff.c

**Functions:** HU_Init, HU_Start, HU_Drawer, HU_Erase, HU_Responder, HU_Ticker

**Crash characteristics:**
- Only crashes with `-warp 1 1` (during gameplay), NOT on title screen
- This means HU_Init works fine; the crash is in HU_Start, HU_Drawer, or HU_Ticker

**Patterns tested and PASSING:**
- `hu_font[0]->height` — global pointer array[i]->member (manual test) ✓
- `players[i].cmd.chatchar` — nested struct member access (manual test) ✓
- `mapnames[(expr)]` — char*[] indexing with expression (asm verified) ✓
- `w_inputbuffer[i].l.len` — nested struct array access (manual test) ✓

**What's different:**
- HU_Start uses `HU_TITLEY` macro which expands to `(167 - SHORT(hu_font[0]->height))` — inline expression with global ptr array access and SHORT macro
- HU_Drawer and HU_Ticker call hu_lib functions (HUlib_drawSText etc.) which do the `l->f[c - l->sc]->width` chain — test 140 was written for this and the fix landed

## Investigation plan

### Approach 1: Function-level isolation (recommended first)

For each file, systematically compile individual functions with jmcc while keeping the rest as GCC. This requires splitting the source file:

1. Create a stripped version of r_bsp.c with each function replaced by an `extern` declaration
2. Compile the stripped version with GCC, the isolated function with jmcc
3. Link together and test
4. Repeat for each function until the crashing one is found

**For r_bsp.c**, the prime suspects (in order):
1. `R_CheckBBox` — complex angle math, solidsegs traversal
2. `R_ClipSolidWallSegment` — linked list manipulation, multiple R_StoreWallRange calls
3. `R_AddLine` — angle computation, sector comparison chain
4. `R_RenderBSPNode` — recursion, NF_SUBSECTOR bitfield check

### Approach 2: ASM diff analysis

Compare jmcc vs GCC assembly for the crashing function instruction-by-instruction:

1. `gcc -S -O0 r_bsp.c -o r_bsp_gcc.s`
2. `jmcc.py r_bsp.c -o r_bsp_jmcc.s`
3. Extract the same function from both
4. Walk through line by line, checking every load/store width, every comparison signedness, every pointer dereference

This is tedious but definitive — any difference that matters will be visible.

### Approach 3: Canary instrumentation

Add memory canaries around key data structures to detect corruption:

1. Add sentinel values before/after `solidsegs`, `drawsegs`, `nodes` arrays
2. Check sentinels after each function call in R_RenderBSPNode
3. When a sentinel is corrupted, we know which function and which data was overwritten

### Approach 4: Stack frame analysis

The signal handler not firing suggests stack corruption. Check:

1. Compare `subq $N, %rsp` in jmcc vs GCC for each function — is the frame large enough for all locals?
2. Check if any `pushq` inside loops could overflow the allocated frame
3. Check if `leave; ret` properly restores the stack after every path (including early returns)

### Approach 5: Reduce to minimal crash case

Create a standalone test program that:
1. Loads E1M1 BSP data from the WAD
2. Calls R_RenderBSPNode with the root node
3. Uses stub functions for rendering (just check the call pattern)

This eliminates all variables except the BSP traversal logic.

## Priority

Focus on **r_bsp.c** first — it's the BSP renderer, critical for any level to display. hu_stuff.c is the HUD overlay which is less essential (the game would be playable without HUD text, just not showing messages).
