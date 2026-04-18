// TEST: u64_to_longdouble_precision
// DESCRIPTION: u64 cast to long double must use 64-bit x87 fildq precision, not 53-bit SSE2
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
typedef unsigned long long u64;

static long double cast_ld(u64 s) { return (long double)s; }

int main(void) {
    /* 2^53+1: fits in double as 2^53, but long double can represent it exactly.
       If jmcc uses 53-bit double for (long double)s, round-trip truncates to 2^53 */
    u64 s1 = 9007199254740993ULL; /* 2^53 + 1 */
    long double r1 = cast_ld(s1);
    u64 back1 = (u64)r1;
    if (back1 != s1) {
        printf("FAIL: (u64)(long double)(2^53+1) = %llu expected %llu\n", back1, s1);
        return 1;
    }

    /* MSB set: 2^63. long double must give exactly 9.22337203685477580800e+18,
       not a double-rounded version */
    u64 s2 = 9223372036854775808ULL; /* 2^63 */
    long double r2 = cast_ld(s2);
    u64 back2 = (u64)r2;
    if (back2 != s2) {
        printf("FAIL: (u64)(long double)(2^63) = %llu expected %llu\n", back2, s2);
        return 1;
    }

    /* sqlite3AtoF value: s=14178266267947184104, e=-22
       (long double) path must give same result as GCC */
    u64 s3 = 14178266267947184104ULL;
    long double r3 = cast_ld(s3);
    u64 back3 = (u64)r3;
    if (back3 != s3) {
        printf("FAIL: (u64)(long double)14178266267947184104 = %llu expected %llu\n", back3, s3);
        return 1;
    }

    printf("ok\n");
    return 0;
}
