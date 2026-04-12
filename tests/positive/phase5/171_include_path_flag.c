// TEST: include_path_flag
// DESCRIPTION: jmcc must support -I flag for additional include search paths
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5
// DEFINES: NORMALUNIX LINUX

/* SDL2 compilation requires -I/usr/include/SDL2 (from sdl2-config --cflags).
   Without -I support, jmcc can't find SDL's begin_code.h when included
   from SDL_main.h via #include "begin_code.h".

   This test includes a header from a subdirectory that is NOT the
   helpers/ directory (which jmcc auto-searches). It requires
   -I tests/positive/phase5/sdl_sim to find the headers.

   To compile manually: jmcc -I tests/positive/phase5/sdl_sim 171_include_path_flag.c */

#include "sim_begin.h"
#include "sim_api.h"

int printf(const char *fmt, ...);

int main(void) {
    if (SIM_VALUE != 99) return 1;
    if (sim_add(3, 4) != 7) return 2;
    printf("ok\n");
    return 0;
}
