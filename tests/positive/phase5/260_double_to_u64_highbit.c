// TEST: double_to_u64_highbit
// DESCRIPTION: double cast to u64 for values >= 2^63 must not use cvttsd2si (signed), gives INT64_MIN as u64
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
typedef unsigned long long u64;

/* Bug: cvttsd2si treats double as signed, so (u64)1e19 gives 2^63 instead of 10^19.
   This breaks sqlite3AtoF's Dekker error term: s2=(u64)rr[0] is wrong,
   so rr[1]=(double)(s-s2) gets a huge bogus value, corrupting the result. */
static u64 cast_u64(double d) { return (u64)d; }

int main(void) {
    /* 10^19: > INT64_MAX (9.22e18) but fits in u64 */
    double d1 = 1.0e19;
    u64 r1 = cast_u64(d1);
    if (r1 != 10000000000000000000ULL) {
        printf("FAIL: (u64)1e19 = %llu expected 10000000000000000000\n", r1);
        return 1;
    }

    /* 2^63 itself (smallest value with MSB set) */
    double d2 = 9223372036854775808.0; /* 2^63 */
    u64 r2 = cast_u64(d2);
    if (r2 != 9223372036854775808ULL) {
        printf("FAIL: (u64)2^63 = %llu expected 9223372036854775808\n", r2);
        return 1;
    }

    /* UINT64_MAX as double (rounds to 2^64, which wraps, but the nearest
       representable double below UINT64_MAX is 2^64 - 2^11 = 18446744073709549568) */
    double d3 = 1.8446744073709552e19; /* nearest double to UINT64_MAX */
    u64 r3 = cast_u64(d3);
    /* GCC gives 0 for this (overflow), so just test it doesn't crash; skip value check */
    (void)r3;

    /* 9.999e18: > INT64_MAX (9.22e18) */
    double d4 = 9.999e18;
    u64 r4 = cast_u64(d4);
    if (r4 != 9999000000000000000ULL) {
        printf("FAIL: (u64)9.999e18 = %llu expected 9999000000000000000\n", r4);
        return 1;
    }

    /* sqlite3AtoF context: s=10^19, rr[0]=(double)s=1e19, s2=(u64)rr[0] must be 10^19 */
    u64 s = 10000000000000000000ULL;
    double rr0 = (double)s;
    u64 s2 = (u64)rr0;
    if (s2 != s) {
        printf("FAIL: s2=(u64)(double)(10^19)=%llu expected %llu\n", s2, s);
        return 1;
    }

    printf("ok\n");
    return 0;
}
