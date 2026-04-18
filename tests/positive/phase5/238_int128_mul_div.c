// TEST: int128_mul_div
// DESCRIPTION: __int128 multiplication, division, and modulo
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Multiplication of two 64-bit halves into a 128-bit result uses the
   x86-64 mulq/imulq instructions plus manual cross-product accumulation.
   Division and modulo have no single hardware instruction for 128-bit;
   GCC emits a call to __divti3/__modti3 from libgcc.

   These are the core operations in ipow() and imod() from the
   minimum_positive_multiple Rosetta Code task. */

#include <stdio.h>

int main(void) {
    /* multiplication: result stays in 64 bits */
    __int128 a = 1000000000LL;
    __int128 b = 1000000000LL;
    __int128 p = a * b;   /* 1e18 */
    if ((unsigned long long)p != 1000000000000000000ULL) {
        printf("FAIL mul small: %llu\n", (unsigned long long)p);
        return 1;
    }

    /* multiplication that produces a > 64-bit result */
    __int128 c = (__int128)0xFFFFFFFFFFFFFFFFULL;  /* 2^64 - 1 */
    __int128 d = c * c;  /* (2^64-1)^2 = 2^128 - 2^65 + 1 */
    /* hi = 0xFFFFFFFFFFFFFFFE, lo = 0x0000000000000001 */
    if ((unsigned long long)(d >> 64) != 0xFFFFFFFFFFFFFFFEULL) {
        printf("FAIL mul big hi: %llx\n", (unsigned long long)(d >> 64));
        return 2;
    }
    if ((unsigned long long)d != 1ULL) {
        printf("FAIL mul big lo: %llx\n", (unsigned long long)d);
        return 3;
    }

    /* *= compound assignment */
    __int128 r = 2;
    r *= 3;
    if ((int)r != 6) { printf("FAIL *=: %d\n", (int)r); return 4; }

    /* division */
    __int128 big = (__int128)1 << 70;   /* 2^70 */
    __int128 q = big / 7;
    __int128 rem = big % 7;
    if (q * 7 + rem != big) { printf("FAIL div check\n"); return 5; }
    if (rem < 0 || rem >= 7) { printf("FAIL rem range\n"); return 6; }

    /* modulo with small divisor (used heavily in mpm) */
    __int128 x = (__int128)10;
    __int128 n = 3;
    __int128 m = x % n;
    if ((int)m != 1) { printf("FAIL 10%%3: %d\n", (int)m); return 7; }

    /* division yielding digit (n % 10 pattern in print128) */
    __int128 val = 12345;
    int digit = (int)(val % 10);
    val /= 10;
    if (digit != 5 || (int)val != 1234) {
        printf("FAIL digit: %d val: %d\n", digit, (int)val);
        return 8;
    }

    printf("ok\n");
    return 0;
}
