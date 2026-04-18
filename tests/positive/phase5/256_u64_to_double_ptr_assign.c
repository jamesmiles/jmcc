// TEST: u64_to_double_ptr_assign
// DESCRIPTION: assigning unsigned long long to *double must use 64-bit cvtsi2sd, not 32-bit
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
typedef unsigned long long u64;

/* mimics sqlite3AtoF's *pResult = s pattern */
static void store(double *pResult, u64 s) {
    *pResult = s;
}

int main(void) {
    /* 5000000000 fits in u64 but not in u32 (max 4294967295) */
    u64 s = 5000000000ULL;
    double r;
    store(&r, s);
    if (r != 5000000000.0) {
        printf("FAIL: *ptr = u64 5e9: got %g expected 5000000000.0\n", r);
        return 1;
    }
    /* Also test direct assignment without function call */
    double r2;
    double *p = &r2;
    *p = s;
    if (r2 != 5000000000.0) {
        printf("FAIL: direct *ptr = u64 5e9: got %g expected 5000000000.0\n", r2);
        return 1;
    }
    /* Also test u64 values > INT64_MAX, the sqlite3AtoF case for '9223372036854775807' */
    u64 big = 9223372036854775807ULL; /* INT64_MAX */
    double r3;
    store(&r3, big);
    if (r3 < 9.22e18 || r3 > 9.24e18) {
        printf("FAIL: *ptr = INT64_MAX as u64: got %g expected ~9.22e18\n", r3);
        return 1;
    }
    printf("ok\n");
    return 0;
}
