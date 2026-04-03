// TEST: cast_sign_extension
// DESCRIPTION: Cast to char/short must sign-extend when promoted back to int for comparison
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* When a value is cast to char or short, and then used in an int
   context (e.g., comparison), it must be sign-extended. The compiler
   emits the cast as a truncated positive literal, but loads the
   variable with sign-extension (movsbl/movswl), so they don't match.

   Example: (char)0xAA should be -86 (0xFFFFFFAA as int),
   but the compiler emits $170 (0x000000AA).

   This affects Doom's comparisons of tag values, error codes, and
   any constant compared against a char/short variable with high bit set. */

int printf(const char *fmt, ...);

int main(void) {
    /* Test 1: char with high bit set */
    char c = 0xAA;          /* -86 as signed char */
    if (c != (char)0xAA) return 1;  /* (char)0xAA must be -86, not 170 */

    /* Test 2: short with high bit set */
    short s = 0xABCD;       /* -21555 as signed short */
    if (s != (short)0xABCD) return 2;

    /* Test 3: explicit negative comparison */
    char d = -1;            /* 0xFF */
    if (d != (char)0xFF) return 3;

    /* Test 4: short negative */
    short t = -1;           /* 0xFFFF */
    if (t != (short)0xFFFF) return 4;

    /* Test 5: char boundary value */
    char e = 0x80;          /* -128 */
    if (e != (char)0x80) return 5;

    /* Test 6: verify the cast produces correct arithmetic results */
    int x = (char)0xAA + 1;   /* should be -86 + 1 = -85 */
    if (x != -85) return 6;

    int y = (short)0xABCD + 1;  /* should be -21555 + 1 = -21554 */
    if (y != -21554) return 7;

    printf("ok\n");
    return 0;
}
