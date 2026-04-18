// TEST: float_bool_condition
// DESCRIPTION: nonzero float/double used as boolean must not be treated as false
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* When a float or double is used as a boolean condition (if, while, ternary
   ?:), jmcc converts it to double (cvtss2sd) then moves the bits to an
   integer register and does `cmpl $0, %eax` — comparing only the LOWER
   32 bits of the 64-bit double representation.

   Exact integer-valued floats have zero in the lower 32 bits of their
   double encoding:

       3.0f as double → 0x4008_0000_0000_0000  →  eax = 0x0000_0000

   So `3.0f ?` evaluates as false, and `r?l/r:(b=1,0)` returns 0 even
   when r is a perfectly valid nonzero denominator.

   The fix: use testq %rax, %rax (full 64-bit test) or a proper FP
   comparison (ucomiss against zero) to evaluate the truthiness.

   Reduced from rosettacode/24_game_solve, whose eval() uses
       case 4: return r?l/r:(b=1,0);
   and consequently never finds any solution because every integer-valued
   r is treated as zero. */

#include <stdio.h>

int main(void) {
    /* ternary with float condition */
    float rf = 3.0f;
    float vf = rf ? 9.0f / rf : -1.0f;
    if (vf < 2.9f || vf > 3.1f) {
        printf("FAIL float ternary: got %f expected 3.0\n", vf);
        return 1;
    }

    /* if-statement with float condition */
    float r2 = 2.0f;
    int hit = 0;
    if (r2) hit = 1;
    if (!hit) { printf("FAIL float if: 2.0f treated as false\n"); return 2; }

    /* ternary with double condition */
    double rd = 4.0;
    double vd = rd ? 16.0 / rd : -1.0;
    if (vd < 3.9 || vd > 4.1) {
        printf("FAIL double ternary: got %f expected 4.0\n", vd);
        return 3;
    }

    /* if-statement with double condition */
    double r3 = 8.0;
    int hit2 = 0;
    if (r3) hit2 = 1;
    if (!hit2) { printf("FAIL double if: 8.0 treated as false\n"); return 4; }

    printf("ok\n");
    return 0;
}
