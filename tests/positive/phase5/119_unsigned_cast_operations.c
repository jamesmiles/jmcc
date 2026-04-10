// TEST: unsigned_cast_operations
// DESCRIPTION: Result of (unsigned) cast must retain unsigned semantics in all operations
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* When a value is cast with (unsigned), the result must be treated
   as unsigned in all subsequent operations: comparison, division,
   modulo, right shift, and truthiness. */

int printf(const char *fmt, ...);

int main(void) {
    int neg = -1;   /* 0xFFFFFFFF as bits */

    /* 1. Comparison: (unsigned)(-1) is 4294967295, NOT < 0 */
    if ((unsigned)neg < 0) return 1;
    if (!((unsigned)neg > 100)) return 2;

    /* 2. Right shift: (unsigned)(-1) >> 1 = 0x7FFFFFFF (logical) */
    unsigned int shifted = (unsigned)neg >> 1;
    if (shifted != 0x7FFFFFFFu) return 3;  /* fails with sarl: 0xFFFFFFFF */

    /* 3. Division: (unsigned)(-1) / 2 = 2147483647 */
    unsigned int divided = (unsigned)neg / 2;
    if (divided != 2147483647u) return 4;  /* fails with idivl: 0 */

    /* 4. Modulo: (unsigned)(-1) % 5 */
    unsigned int modded = (unsigned)neg % 5;
    /* 0xFFFFFFFF = 4294967295, 4294967295 % 5 = 0 */
    if (modded != 0) return 5;

    /* 5. Cast chain: (unsigned)(char)0xAA  */
    char c = 0xAA;   /* -86 as signed char */
    /* (unsigned)(char) should be (unsigned)(-86) = 4294967210 */
    /* But (unsigned char) should be 170 */
    unsigned int from_char = (unsigned char)c;
    if (from_char != 170) return 6;

    /* 6. (unsigned short) cast */
    short s = -1;  /* 0xFFFF */
    unsigned int from_short = (unsigned short)s;
    if (from_short != 65535) return 7;

    /* 7. Comparison with variable */
    unsigned int big = 0x80000000u;
    int small_val = 1;
    if ((unsigned)big < (unsigned)small_val) return 8;

    printf("ok\n");
    return 0;
}
