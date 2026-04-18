// TEST: int128_fn_args
// DESCRIPTION: __int128 passed as function argument and returned from function
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* x86-64 ABI: __int128 is passed/returned as a pair of 64-bit integer
   registers (rdi:rsi for first arg, rax:rdx for return value).
   This is the calling convention used by ipow(), imod(), imax() in
   the minimum_positive_multiple Rosetta Code task. */

#include <stdio.h>

static __int128 identity(__int128 x) {
    return x;
}

static __int128 add128(__int128 a, __int128 b) {
    return a + b;
}

static __int128 ipow(__int128 base, __int128 exp) {
    __int128 res = 1;
    while (exp > 0) { res *= base; exp--; }
    return res;
}

static __int128 imod(__int128 m, __int128 n) {
    __int128 r = m % n;
    if (r < 0) r += n;
    return r;
}

static __int128 imax(__int128 a, __int128 b) {
    return a > b ? a : b;
}

int main(void) {
    /* identity round-trip for a > 64-bit value */
    __int128 big = (__int128)1 << 70;
    __int128 r = identity(big);
    if (r != big) { printf("FAIL identity\n"); return 1; }

    /* two-arg function */
    __int128 s = add128(big, big);
    if (s != big * 2) { printf("FAIL add128\n"); return 2; }

    /* ipow */
    __int128 p = ipow(10, 6);
    if ((int)p != 1000000) { printf("FAIL ipow: %d\n", (int)p); return 3; }

    /* ipow producing > 64-bit result */
    __int128 p2 = ipow(10, 20);
    /* 10^20 = 0x56BC_75E2_D630_FFFFF... just check it's > 2^63 */
    if (p2 <= ((__int128)1 << 63)) { printf("FAIL ipow big\n"); return 4; }

    /* imod with negative intermediate */
    __int128 m = imod(-7, 3);
    if ((int)m != 2) { printf("FAIL imod neg: %d\n", (int)m); return 5; }

    /* imax */
    __int128 mx = imax((__int128)42, (__int128)17);
    if ((int)mx != 42) { printf("FAIL imax: %d\n", (int)mx); return 6; }

    printf("ok\n");
    return 0;
}
