// TEST: nested_include_relative
// DESCRIPTION: jmcc must support -I flag for additional include search paths
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SDL2 compilation requires -I/usr/include/SDL2 (from sdl2-config --cflags)
   so that headers like begin_code.h can be found when SDL_main.h does
   #include "begin_code.h". jmcc currently doesn't support -I flags,
   making it impossible to compile any code that uses SDL2 headers.

   To test: jmcc -I helpers 171_nested_include_relative.c
   The helpers/ directory contains outer.h which includes inner.h.
   Without -I helpers, outer.h cannot be found.

   NOTE: This test currently passes because jmcc auto-searches a helpers/
   subdirectory. The real issue is the missing -I flag, needed for
   SDL2 and other library headers. */

#include "outer.h"

int printf(const char *fmt, ...);

int main(void) {
    if (OUTER_VAL != 100) return 1;
    if (INNER_VAL != 42) return 2;
    printf("ok\n");
    return 0;
}
