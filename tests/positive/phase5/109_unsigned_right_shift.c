// TEST: unsigned_right_shift
// DESCRIPTION: Unsigned right shift must use logical shift (shrl) not arithmetic (sarl)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Arithmetic right shift (sarl) preserves the sign bit, filling
   with 1s for negative values. Logical right shift (shrl) fills
   with 0s. For unsigned types, >> must use shrl.

   Example: 0x80000000u >> 1 should give 0x40000000 (logical),
   not 0xC0000000 (arithmetic, sign-extended). */

int printf(const char *fmt, ...);

int main(void) {
    unsigned int a = 0x80000000u;

    /* Basic unsigned right shift */
    unsigned int b = a >> 1;
    if (b != 0x40000000u) return 1;  /* fails with sarl: 0xC0000000 */

    unsigned int c = a >> 4;
    if (c != 0x08000000u) return 2;  /* fails with sarl: 0xF8000000 */

    /* Full shift */
    unsigned int d = 0xFFFFFFFFu >> 16;
    if (d != 0x0000FFFFu) return 3;  /* fails with sarl: 0xFFFFFFFF */

    /* Shift by variable */
    int shift = 8;
    unsigned int e = 0xFF000000u >> shift;
    if (e != 0x00FF0000u) return 4;

    /* Signed shift should still be arithmetic (for comparison) */
    int sa = (int)0x80000000;  /* -2147483648 */
    int sb = sa >> 1;
    if (sb != (int)0xC0000000) return 5;  /* arithmetic: -1073741824 */

    printf("ok\n");
    return 0;
}
