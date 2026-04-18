// TEST: int128_arith
// DESCRIPTION: __int128 addition, subtraction, negation, and comparison
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* x86-64: add/sub use addq+adcq / subq+sbbq (with carry/borrow).
   Comparison needs a two-word compare: high 64 bits first, low 64 bits
   as tiebreaker.

   These are the operations used most in the mpm() algorithm:
     while (n > 1) { res *= b; n--; }   -- comparison + subtraction
     r = r + ipow(10, j);               -- addition
     k = imod(k - ipow(10, j), n);      -- subtraction */

#include <stdio.h>

int main(void) {
    __int128 a = (__int128)5000000000LL * 1000000000LL;  /* 5e18, fits in 63 bits */
    __int128 b = (__int128)6000000000LL * 1000000000LL;  /* 6e18 */

    /* addition that crosses 64-bit boundary */
    __int128 sum = a + b;
    /* 11e18 = 0x0000_0000_0000_0000_9887_0c00_0000_0000 ... let's just check via cast */
    if ((long long)(sum >> 64) != 0) { printf("FAIL sum hi\n"); return 1; }
    if ((unsigned long long)sum != 11000000000000000000ULL) { printf("FAIL sum lo\n"); return 2; }

    /* subtraction */
    __int128 diff = b - a;
    if ((int)diff != (int)1000000000000000000LL) {
        /* just check it's positive and equal to 1e18 */
        if ((long long)diff != 1000000000000000000LL) { printf("FAIL diff\n"); return 3; }
    }

    /* negation */
    __int128 neg = -a;
    if ((long long)(neg >> 64) != -1) { printf("FAIL neg hi\n"); return 4; }

    /* comparisons */
    if (!(a < b))  { printf("FAIL a<b\n");  return 5; }
    if (!(b > a))  { printf("FAIL b>a\n");  return 6; }
    if (!(a == a)) { printf("FAIL a==a\n"); return 7; }
    if (!(a != b)) { printf("FAIL a!=b\n"); return 8; }

    /* comparison that requires high-word tiebreak */
    __int128 big = (__int128)1 << 64;   /* 2^64: hi=1, lo=0 */
    __int128 small = (__int128)0xFFFFFFFFFFFFFFFFULL;  /* hi=0, lo=max */
    if (!(big > small)) { printf("FAIL big>small\n"); return 9; }

    /* increment / decrement */
    __int128 n = 3;
    n--;
    if ((int)n != 2) { printf("FAIL n-- : %d\n", (int)n); return 10; }
    n++;
    if ((int)n != 3) { printf("FAIL n++ : %d\n", (int)n); return 11; }

    printf("ok\n");
    return 0;
}
