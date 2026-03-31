// TEST: include_guard
// DESCRIPTION: Standard #ifndef include guard with intentional double inclusion
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 42
// ENVIRONMENT: hosted
// PHASE: 5

#include "013_guarded.h"
#include "013_guarded.h"

int printf(const char *fmt, ...);

int main(void) {
    guarded_point_t p;
    p.x = GUARDED_VAL;
    printf("%d\n", p.x);
    return 0;
}
