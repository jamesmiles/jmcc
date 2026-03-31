// TEST: nested_include
// DESCRIPTION: Header including another header (Doom's include graph pattern)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 50
// ENVIRONMENT: hosted
// PHASE: 5

#include "012_outer.h"

int printf(const char *fmt, ...);

int main(void) {
    printf("%d\n", OUTER_VAL);
    return 0;
}
