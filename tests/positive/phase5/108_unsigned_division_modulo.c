// TEST: unsigned_division_modulo
// DESCRIPTION: Unsigned division and modulo must use unsigned instructions (divl not idivl)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* For unsigned types, division must use xorl %edx,%edx + divl (unsigned)
   instead of cdq + idivl (signed). cdq sign-extends eax into edx:eax,
   which gives wrong results for values with the high bit set.

   Example: 0x80000000u / 2 should give 0x40000000 (1073741824),
   but with idivl the sign-extended dividend is 0xFFFFFFFF80000000
   divided by 2, which overflows or gives -1073741824. */

int printf(const char *fmt, ...);

int main(void) {
    unsigned int a = 0x80000000u;  /* 2147483648 */
    unsigned int b = 2;

    /* Unsigned division */
    unsigned int div_result = a / b;
    if (div_result != 0x40000000u) return 1;  /* 1073741824 */

    /* Unsigned modulo */
    unsigned int mod_result = a % 3;
    if (mod_result != 2) return 2;  /* 2147483648 % 3 = 2 */

    /* Large unsigned values */
    unsigned int c = 4000000000u;
    unsigned int d = c / 7;
    if (d != 571428571u) return 3;

    unsigned int e = c % 7;
    if (e != 3) return 4;  /* 4000000000 % 7 = 3 */

    printf("ok\n");
    return 0;
}
