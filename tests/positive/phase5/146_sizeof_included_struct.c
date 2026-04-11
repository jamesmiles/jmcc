// TEST: sizeof_included_struct
// DESCRIPTION: sizeof struct from included header must reflect all fields
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

#include "146_zone.h"

int printf(const char *fmt, ...);

int main(void) {
    if (sizeof(tblock_t) != 40) {
        printf("FAIL: sizeof(tblock_t) = %lu (expected 40)\n",
               (unsigned long)sizeof(tblock_t));
        return 1;
    }
    printf("ok\n");
    return 0;
}
