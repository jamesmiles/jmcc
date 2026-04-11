# Compiling Doom with JMCC

## Source

The original linuxdoom-1.10 needs 64-bit patches to run on modern x86-64 systems (the original code assumes 32-bit pointers). A patched copy lives at `/home/james/doom-64/`.

### 64-bit portability fixes

- `r_data.c`: `numtextures*4` → `numtextures*sizeof(void*)` for pointer arrays (`textures`, `texturecolumnlump`, `texturecolumnofs`, `texturecomposite`). Remaining `int*` arrays changed from `*4` to `*8` (over-allocating is harmless, avoids subtle corruption).
- `r_data.c`: `void **columndirectory` → `int columndirectory` in `maptexture_t` (WAD format uses 32-bit offsets, `void**` adds padding on 64-bit shifting all fields after it).
- `r_data.c`: `(int)colormaps` → `(long)colormaps` for pointer alignment.
- `r_draw.c`: `(int)translationtables` → `(long)translationtables`.
- `p_setup.c`: `linebuffer = Z_Malloc(total*4, ...)` → `total*sizeof(line_t*)` (pointer array).
- `p_saveg.c`: `(int)save_p` → `(long)save_p`, plus similar casts for sector/state/player indices.
- `d_net.c`: `(int)&` → `(long)&` for offsetof patterns.
- `i_video.c`: `(int)exp` → `(long)exp` for pointer arithmetic.
- `i_sound.c`: `extern int errno` → `#include <errno.h>`.
- `i_system.c`: `mb_used = 6` → `mb_used = 16` (64-bit pointer arrays need more zone memory).
- `m_misc.c`: `(int) "string"` → `(long) "string"` in initializers.

### Additional 64-bit fixes

- `info.c` / `info.h`: `sprnames[NUMSPRITES]` → `sprnames[NUMSPRITES+1]` with explicit `0` NULL terminator. `R_InitSpriteDefs` iterates with `while(*check != NULL)` but the original array has no terminator — GCC happens to place zeros after it, jmcc doesn't.

### TrueColor X11 patch (i_video_truecolor.c)

Modern X servers don't support 8-bit PseudoColor. The following changes make Doom work with 24-bit TrueColor (implemented in `i_video_truecolor.c`, a modified copy of `i_video.c`):

- `XMatchVisualInfo` requests 24-bit TrueColor instead of 8-bit PseudoColor.
- Window and XImage depth changed from 8 to 24, image buffer is 4 bytes/pixel.
- `XCreateColormap` uses `AllocNone` instead of `AllocAll`.
- `UploadNewPalette` stores RGB values in a `unsigned long rgb_palette[256]` lookup table instead of calling `XStoreColors`. `rgb_palette` declared before `I_FinishUpdate` for forward reference.
- `I_FinishUpdate` converts the 320x200 8-bit indexed framebuffer to 32-bit ARGB using `rgb_palette` before blitting. Handles all `multiply` modes (1x, 2x, 3x). Uses C89 `for` loops (no `for(int i=0;...)`).
- `screens[0]` is always a separate `malloc` buffer — NOT aliased to `image->data` (they have different pixel formats: 8-bit indexed vs 32-bit ARGB).
- `errnos.h` → `errno.h`, removed `extern int errno` (conflicts with glibc macro).
- MITSHM kept enabled (works with WSL2/X11).

## Build steps

### Step 1: Compile all .c files to assembly

```bash
mkdir -p /home/james/doom-build-new
for f in /home/james/doom-64/*.c; do
  base=$(basename "$f" .c)
  python3 jmcc.py "$f" -o "/home/james/doom-build-new/${base}.s" -DNORMALUNIX -DLINUX
done
```

Both `-DNORMALUNIX` and `-DLINUX` are required — these are the defines from the original Makefile that gate the Linux system includes (`unistd.h`, `sys/stat.h`, etc).

### Step 2: Assemble to object files

```bash
cd /home/james/doom-build-new
for f in *.s; do
  gcc -c "$f" -o "$(basename "$f" .s).o"
done
```

### Step 3: Link

```bash
rm -f i_video.o  # use i_video_truecolor.o instead
gcc *.o -o linuxxdoom -lXext -lX11 -lm
```

Requires `libx11-dev` and `libxext-dev` packages.

### Step 4: Run

Doom needs a WAD file. The shareware `doom1.wad` works:

```bash
./linuxxdoom -iwad doom1.wad
```

## Current status

- **Compile:** 62/62 files (excluding `i_video.c`, replaced by `i_video_truecolor.c`)
- **Assemble:** 62/62 files
- **Link:** Success
- **Title screen:** Fully working with all 62/62 jmcc files. Pixel-perfect match with GCC.
- **E1M1 gameplay:** Playable with 60/62 jmcc files. `r_bsp.c` and `hu_stuff.c` require GCC fallback due to remaining codegen issues.
- **Controls:** Keyboard input works (arrow keys, Ctrl to shoot, Space to open doors, Escape for menu).

## Codegen bugs found and fixed

| # | Test | Bug | Doom impact |
|---|------|-----|-------------|
| 1 | 084 | `ptr[i]` for struct pointers used wrong stride | W_AddFile corrupted lump metadata |
| 2 | 085 | `struct_t**[i]` used sizeof(struct) not sizeof(ptr) | R_GenerateLookup crash |
| 3 | 086 | `char *g = "str"` emitted as NULL | I_InitSound sprintf crash |
| 4 | 087 | Short member writes used movl (4B) not movw (2B) | D_CheckNetGame div-by-zero |
| 5 | 088 | `int *p = &arr[1]` emitted as NULL | G_BuildTiccmd crash |
| 6 | 089-094 | Compound assign/inc on short/char/long wrong width | Zone allocator corruption |
| 7 | 092 | Cast to char/short doesn't sign-extend | Wrong comparison results |
| 8 | 095 | 2D struct array first-dimension stride wrong | netcmds corruption |
| 9 | 097 | 2D pointer array stride wrong | scalelight corruption |
| 10 | 099 | Global 2D ptr array allocated as 8 bytes | scalelight/zlight overlap globals |
| 11 | 100 | Initialized 2D array truncated inner dimensions | gammatable 5 bytes instead of 1280 |
| 12 | 101 | `arr[128*256]` constant expr not evaluated | vol_lookup 4 bytes instead of 131072 |
| 13 | 102-106 | Unsigned char/short loads sign-extend | V_DrawPatch column loop, palette lookup |
| 14 | 108-110 | Unsigned div/mod/shift/compare use signed ops | Angle computation, Z_ChangeTag |
| 15 | 114 | Pointer truthiness only checks lower 32 bits | Z_Malloc treats in-use blocks as free |
| 16 | 115-116 | Pointer/long comparison uses 32-bit cmpl | Z_Malloc rover == start, BSP traversal |
| 17 | 118-119 | `(unsigned)` cast result loses unsigned property | Z_ChangeTag false "owner required" error |
| 18 | 125 | `char**` double indexing (`argv[i][j]`) broken | Command-line argument parsing |
| 19 | 130 | `ptr[i].member[j]` segfault (stride regression) | Level data loading |
| 20 | 133 | `ptr->array_member[i]` segfault | BSP, texture, sprite access |
| 21 | 136 | Typedef unsigned shift uses arithmetic not logical | Angle computation, renderer crash |
| 22 | 137 | 2D array partial row init `{0}` doesn't zero-fill | BSP checkcoord lookup table |
| 23 | 138 | `ptr->array2d[i]` dereferences instead of decaying | R_CheckBBox bbox pointer passing |
| 24 | 140 | `ptr->ptr_array[i]->field` chain broken | HUD drawing, texture lookup |
| 25 | 141 | Negative double-to-int cast wrong upper bits | FixedDiv2 negative results |
| 26 | 142 | `short**` double indexing wrong first stride | Texture column lookup crash |
