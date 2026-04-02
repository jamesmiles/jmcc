# Compiling Doom with JMCC

## Source

Using the original linuxdoom-1.10 release from id Software, located at `/home/james/doom/linuxdoom-1.10/` (62 .c files, 62 .h files).

## Step 1: Compile all .c files to assembly

```bash
mkdir -p /home/james/doom-build-new
for f in /home/james/doom/linuxdoom-1.10/*.c; do
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
- **Link:** Success (875KB binary)
- **Runtime:** Crashes during `R_InitTextures()` with a bogus 895MB allocation, likely a codegen bug in integer arithmetic (32-bit vs 64-bit size computation).

```
DOOM Shareware Startup v1.10
V_Init: allocate screens.              ✓
M_LoadDefaults: Load system defaults.  ✓
Z_Init: Init zone memory allocation.   ✓
W_Init: Init WADfiles.                 ✓
 adding ./doom1.wad                    ✓
M_Init: Init miscellaneous info.       ✓
R_Init: Init DOOM refresh daemon -     ✗ (R_InitTextures)
```
