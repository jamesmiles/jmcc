// TEST: unsigned_comparison
// DESCRIPTION: Unsigned comparison must use unsigned condition codes (setb/seta not setl/setg)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Signed comparison treats 0x80000000 as negative (-2147483648),
   so 0x80000000 < 0 is true with setl. Unsigned comparison treats
   it as positive (2147483648), so 0x80000000u < 0 is false.

   For unsigned types, < > <= >= must use setb/seta/setbe/setae
   (unsigned/below/above) instead of setl/setg/setle/setge (signed). */

int printf(const char *fmt, ...);

int main(void) {
    unsigned int a = 0x80000000u;  /* 2147483648 */
    unsigned int b = 1;

    /* 2147483648 > 1 must be true */
    if (!(a > b)) return 1;  /* fails with setg: treats a as -2147483648 */

    /* 1 < 2147483648 must be true */
    if (!(b < a)) return 2;

    /* 0xFFFFFFFF > 0x7FFFFFFF must be true */
    unsigned int big = 0xFFFFFFFFu;
    unsigned int half = 0x7FFFFFFFu;
    if (!(big > half)) return 3;

    /* Unsigned >= */
    if (!(a >= b)) return 4;
    if (!(a >= a)) return 5;

    /* Unsigned <= */
    if (!(b <= a)) return 6;

    /* Mixed: unsigned loop condition (common in Doom: size_t loops) */
    unsigned int count = 0;
    unsigned int limit = 5;
    unsigned int i;
    for (i = 0; i < limit; i++)
        count++;
    if (count != 5) return 7;

    /* Edge case: comparing with 0 */
    unsigned int zero = 0;
    if (zero > a) return 8;  /* 0 > 2147483648 must be false */
    if (a < zero) return 9;  /* 2147483648 < 0 must be false */

    printf("ok\n");
    return 0;
}
