// TEST: long_double_arithmetic
// DESCRIPTION: long double cast from u64 and multiply must give correct result
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sqlite3.c sqlite3AtoF bUseLongDouble path:
     LONGDOUBLE_TYPE r = (LONGDOUBLE_TYPE)s;
     while( e<=-1 ){ e+=1; r *= 1.0e-01L; }
     *pResult = (double)r;
   Bug: jmcc stores the long double via x87 fldl/fstpt (80-bit format) but
   reads it back with movsd (64-bit IEEE 754), misinterpreting the x87 bytes.
   For s=11, e=-1: reads 0xB000000000000000 (-2^-255) instead of 11.0,
   then multiplies by 0.1L, giving ~-1.73e-78 instead of 1.1.
   Fix: use consistent x87 or SSE2 throughout for long double ops. */

#include <stdio.h>
#include <string.h>

int main(void) {
    unsigned long long s = 11;
    long double r = (long double)s;
    r *= 0.1L;
    double result = (double)r;

    unsigned long long bits;
    memcpy(&bits, &result, 8);

    unsigned long long expected_bits = 0x3ff199999999999aULL;

    if (bits != expected_bits) {
        printf("FAIL: got 0x%016llx (%.17g), expected 0x%016llx\n",
               (unsigned long long)bits, result,
               (unsigned long long)expected_bits);
        return 1;
    }
    printf("ok\n");
    return 0;
}
