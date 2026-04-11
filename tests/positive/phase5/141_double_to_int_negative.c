// TEST: double_to_int_negative
// DESCRIPTION: (int)double must preserve sign for negative values
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's FixedDiv2 does: return (int)c where c is a negative double.
   (int)(-32768.0) must give -32768 (0xFFFF8000), not 0x7FFF8000.
   The cvttsd2si instruction truncates double to int. If the result
   is placed in %eax but the upper 32 bits of %rax contain garbage
   from a previous operation, the int appears wrong when stored. */

int printf(const char *fmt, ...);

int main(void) {
    /* Positive double to int */
    double a = 32768.0;
    int r = (int)a;
    if (r != 32768) return 1;

    /* Negative double to int */
    double b = -32768.0;
    r = (int)b;
    if (r != -32768) return 2;

    /* Negative result from computation */
    double c = ((double)(-65536)) / ((double)(2)) * 65536.0;
    /* = -65536.0 / 2.0 * 65536.0 = -2147483648.0 */
    /* This overflows int, but smaller values should work: */
    c = ((double)(-65536)) / ((double)(131072)) * 65536.0;
    /* = -0.5 * 65536 = -32768.0 */
    r = (int)c;
    if (r != -32768) return 3;

    /* The FixedDiv2 pattern */
    int fa = -0x10000;  /* -65536 = -1.0 in fixed point */
    int fb = 0x20000;   /* 131072 = 2.0 */
    double fc = ((double)fa) / ((double)fb) * 65536.0;
    /* -65536.0 / 131072.0 * 65536.0 = -32768.0 */
    r = (int)fc;
    if (r != -32768) return 4;  /* -0x8000 */

    printf("ok\n");
    return 0;
}
