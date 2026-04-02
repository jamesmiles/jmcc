# Compiling Doom with JMCC

## Source

The original linuxdoom-1.10 needs 64-bit patches to run on modern x86-64 systems (the original code assumes 32-bit pointers). A patched copy lives at `/home/james/doom-64/`.

Key 64-bit fixes applied to the source:
- `r_data.c`: `numtextures*4` → `numtextures*sizeof(void*)` for pointer arrays
- `r_data.c`: `void **columndirectory` → `int columndirectory` in `maptexture_t` (WAD format is 32-bit)
- `r_data.c`: `(int)colormaps` → `(long)colormaps` for pointer alignment
- `r_draw.c`: `(int)translationtables` → `(long)translationtables`
- `d_net.c`: `(int)&` → `(long)&` for offsetof patterns
- `i_video.c`: `(int)exp` → `(long)exp` for pointer arithmetic
- `i_sound.c`: `extern int errno` → `#include <errno.h>`

## Step 1: Compile all .c files to assembly

```bash
mkdir -p /home/james/doom-build-new
for f in /home/james/doom-64/*.c; do
  base=$(basename "$f" .c)
  python3 jmcc.py "$f" -o "/home/james/doom-build-new/${base}.s" -DNORMALUNIX -DLINUX
done
```

Both `-DNORMALUNIX` and `-DLINUX` are required — these are the defines from the original Makefile that gate the Linux system includes (`unistd.h`, `sys/stat.h`, etc).

## Step 2: Assemble to object files

```bash
cd /home/james/doom-build-new
for f in *.s; do
  gcc -c "$f" -o "$(basename "$f" .s).o"
done
```

## Step 3: Link

```bash
gcc *.o -o linuxxdoom -lXext -lX11 -lm
```

Requires `libx11-dev` and `libxext-dev` packages.

## Step 4: Run

Doom needs a WAD file. The shareware `doom1.wad` works:

```bash
./linuxxdoom -iwad doom1.wad
```

## Current status

- **Compile:** 62/62 files
- **Assemble:** 62/62 files
- **Link:** Success
- **Runtime:** All initialization completes. Fails at X11 display open because modern X servers don't support 256-color PseudoColor mode (not a jmcc bug).

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
I_InitGraphics                         ✗ (X11 256-color not available)
```
