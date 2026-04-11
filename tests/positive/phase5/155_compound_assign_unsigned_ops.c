// TEST: compound_assign_unsigned_ops
// DESCRIPTION: All compound assignments on unsigned must use unsigned operations
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Binary operators on unsigned were fixed (tests 108-110, 136).
   Compound assignments use a separate code path that may still
   use signed operations. Test all of them. */

int printf(const char *fmt, ...);

int main(void) {
    /* >>= logical shift (not arithmetic) */
    unsigned int a = 0x80000000u;
    a >>= 1;
    if (a != 0x40000000u) return 1;

    /* /= unsigned division (not signed) */
    unsigned int b = 0x80000000u;
    b /= 2;
    if (b != 0x40000000u) return 2;

    /* %= unsigned modulo (not signed) */
    unsigned int c = 0xFFFFFFFEu;
    c %= 3;
    /* 4294967294 % 3 = 2 */
    if (c != 2) return 3;

    /* Comparison after compound assign (verify result is unsigned) */
    unsigned int d = 0xFFFFFFFFu;
    d >>= 16;
    if (d != 0x0000FFFFu) return 4;
    if (d < 0) return 5;  /* unsigned can't be < 0 */

    /* typedef unsigned */
    typedef unsigned angle_t;
    angle_t e = 0xC0000000u;
    e >>= 19;
    if (e != 6144) return 6;

    angle_t f = 0x80000000u;
    f /= 3;
    /* 2147483648 / 3 = 715827882 */
    if (f != 715827882u) return 7;

    printf("ok\n");
    return 0;
}
