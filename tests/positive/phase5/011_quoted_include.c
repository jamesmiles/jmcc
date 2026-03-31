// TEST: quoted_include
// DESCRIPTION: #include "file.h" with macros and struct definitions (Doom include pattern)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: FRACBITS=16
// STDOUT: vertex=(10,20)
// ENVIRONMENT: hosted
// PHASE: 5

#include "011_doomdef.h"

int printf(const char *fmt, ...);

int main(void) {
    printf("FRACBITS=%d\n", FRACBITS);
    vertex_t v;
    v.x = 10;
    v.y = 20;
    printf("vertex=(%d,%d)\n", v.x, v.y);
    return 0;
}
