// TEST: angle_bracket_include
// DESCRIPTION: #include <header> should search include paths, not be silently skipped
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: FRACBITS=16
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

/* This tests that angle-bracket includes search the include paths.
   The preprocessor currently skips all <...> includes silently.
   We use a local header to avoid depending on system headers. */
#include <011_doomdef.h>

int main(void) {
    printf("FRACBITS=%d\n", FRACBITS);
    return 0;
}
