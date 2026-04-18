// TEST: u64_cast_to_double
// DESCRIPTION: unsigned long long to double cast must use 64-bit cvtsi2sd, not 32-bit
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
typedef unsigned long long u64;

int main(void) {
    /* 5000000000 fits in u64 but not in u32 (max 4294967295) */
    u64 s = 5000000000ULL;
    double r = (double)s;
    if (r != 5000000000.0) {
        printf("FAIL: (double)(u64)5000000000 = %g expected 5e9\n", r);
        return 1;
    }
    /* Implicit cast */
    double r2 = s;
    if (r2 != 5000000000.0) {
        printf("FAIL: implicit u64->double = %g expected 5e9\n", r2);
        return 1;
    }
    printf("ok\n");
    return 0;
}
