// TEST: u64_to_double_highbit
// DESCRIPTION: u64 values with MSB set (>INT64_MAX) must convert to double correctly, not as negative
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
typedef unsigned long long u64;

/* Bug: cvtsi2sdq treats u64 as signed, so 2^63 becomes -2^63 as double */
static void store(double *r, u64 s) { *r = s; }

int main(void) {
    /* 2^63: MSB set, cvtsi2sdq gives -9.22e18 instead of +9.22e18 */
    u64 s1 = 9223372036854775808ULL;
    double r1;
    store(&r1, s1);
    if (r1 < 9.2e18 || r1 > 9.3e18) {
        printf("FAIL: store(2^63)=%g expected ~9.22e18\n", r1);
        return 1;
    }

    /* UINT64_MAX */
    u64 s2 = 18446744073709551615ULL;
    double r2;
    store(&r2, s2);
    if (r2 < 1.8e19 || r2 > 1.9e19) {
        printf("FAIL: store(UINT64_MAX)=%g expected ~1.84e19\n", r2);
        return 1;
    }

    /* Also test via direct implicit assignment (local var init) */
    u64 s3 = 10000000000000000000ULL;
    double r3 = s3;
    if (r3 < 9.9e18 || r3 > 1.1e19) {
        printf("FAIL: r3=(double)1e19_u64=%g expected ~1e19\n", r3);
        return 1;
    }

    printf("ok\n");
    return 0;
}
