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

### TrueColor X11 patch (i_video.c)

Modern X servers don't support 8-bit PseudoColor. The following changes make Doom work with 24-bit TrueColor:

- `XMatchVisualInfo` requests 24-bit TrueColor instead of 8-bit PseudoColor.
- Window and XImage depth changed from 8 to 24, image buffer is 4 bytes/pixel.
- `XCreateColormap` uses `AllocNone` instead of `AllocAll`.
- `UploadNewPalette` stores RGB values in a `unsigned long rgb_palette[256]` lookup table instead of calling `XStoreColors`.
- `I_FinishUpdate` converts the 320x200 8-bit indexed framebuffer to 32-bit ARGB using `rgb_palette` before blitting. Handles all `multiply` modes (1x, 2x, 3x).
- `screens[0]` is NOT aliased to `image->data` (they have different pixel formats).
- MITSHM disabled (`doShm = 0`) — simpler, avoids shared memory issues.

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
gcc *.o -o linuxxdoom -lXext -lX11 -lm
```

Requires `libx11-dev` and `libxext-dev` packages.

### Step 4: Run

Doom needs a WAD file. The shareware `doom1.wad` works:

```bash
./linuxxdoom -iwad doom1.wad
```

## Current status

- **Compile:** 62/62 files
- **Assemble:** 62/62 files
- **Link:** Success
- **Runtime:** All initialization completes through `ST_Init`. X11 window opens. Crashes before first frame render due to a remaining codegen bug (see `DOOM_GAMELOOP_BUG.md`).

```
DOOM Shareware Startup v1.10
V_Init: allocate screens.              ✓
M_LoadDefaults: Load system defaults.  ✓
Z_Init: Init zone memory allocation.   ✓
W_Init: Init WADfiles.                 ✓
 adding ./doom1.wad                    ✓
M_Init: Init miscellaneous info.       ✓
R_Init: Init DOOM refresh daemon       ✓ (all sub-stages)
P_Init: Init Playloop state.           ✓
I_Init: Setting up machine state.      ✓
D_CheckNetGame                         ✓
S_Init: Setting up sound.              ✓
HU_Init: Setting up heads up display.  ✓
ST_Init: Init status bar.              ✓
I_InitGraphics                         ✓ (TrueColor 24-bit)
D_DoomLoop / first frame               ✗ (see DOOM_GAMELOOP_BUG.md)
```

## Codegen bugs found and fixed

| # | Test file | Bug | Doom impact |
|---|-----------|-----|-------------|
| 1 | `084_struct_ptr_index_stride` | `ptr[i]` for struct pointers used wrong stride | W_AddFile corrupted lump metadata |
| 2 | `085_double_ptr_struct_stride` | `struct_t**[i]` used sizeof(struct) not sizeof(ptr) | R_GenerateLookup crash |
| 3 | `086_global_char_ptr_string_init` | `char *g = "str"` emitted as NULL | I_InitSound sprintf crash |
| 4 | `087_short_member_write_clobber` | Short member writes used movl (4B) not movw (2B) | D_CheckNetGame div-by-zero |
| 5 | `088_global_ptr_array_element_init` | `int *p = &arr[1]` emitted as NULL | G_BuildTiccmd crash |
