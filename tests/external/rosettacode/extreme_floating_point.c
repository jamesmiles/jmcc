// On x86-64 glibc, NaN prints as "-nan" (sign bit set by default). On ARM64 /
// macOS libc, NaN prints as "nan" (unsigned canonical NaN). Similarly,
// arithmetic on NaN propagates differently: glibc preserves the negative sign
// bit, macOS libc produces unsigned nan.
// TEST: rosetta_extreme_floating_point
// DESCRIPTION: Rosetta Code - Extreme floating point values (NaN==NaN returns true)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Extreme_floating_point_values#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: positive infinity: inf
// STDOUT: negative infinity: -inf
// STDOUT: negative zero: -0.000000
// STDOUT: not a number: -nan
// STDOUT: +inf + 2.0 = inf
// STDOUT: +inf - 10.1 = inf
// STDOUT: +inf + -inf = -nan
// STDOUT: 0.0 * +inf = -nan
// STDOUT: 1.0/-0.0 = -inf
// STDOUT: NaN + 1.0 = -nan
// STDOUT: NaN + NaN = -nan
// STDOUT: NaN == NaN = false
// STDOUT: 0.0 == -0.0 = true
// EXPECTED_STDOUT_ARM64:
// STDOUT_ARM64: positive infinity: inf
// STDOUT_ARM64: negative infinity: -inf
// STDOUT_ARM64: negative zero: -0.000000
// STDOUT_ARM64: not a number: nan
// STDOUT_ARM64: +inf + 2.0 = inf
// STDOUT_ARM64: +inf - 10.1 = inf
// STDOUT_ARM64: +inf + -inf = nan
// STDOUT_ARM64: 0.0 * +inf = nan
// STDOUT_ARM64: 1.0/-0.0 = -inf
// STDOUT_ARM64: NaN + 1.0 = nan
// STDOUT_ARM64: NaN + NaN = nan
// STDOUT_ARM64: NaN == NaN = false
// STDOUT_ARM64: 0.0 == -0.0 = true

#include <stdio.h>

int main()
{
    double inf = 1/0.0;
    double minus_inf = -1/0.0;
    double minus_zero = -1/ inf ;
    double nan = 0.0/0.0;

    printf("positive infinity: %f\n",inf);
    printf("negative infinity: %f\n",minus_inf);
    printf("negative zero: %f\n",minus_zero);
    printf("not a number: %f\n",nan);

    /* some arithmetic */

    printf("+inf + 2.0 = %f\n",inf + 2.0);
    printf("+inf - 10.1 = %f\n",inf - 10.1);
    printf("+inf + -inf = %f\n",inf + minus_inf);
    printf("0.0 * +inf = %f\n",0.0 * inf);
    printf("1.0/-0.0 = %f\n",1.0/minus_zero);
    printf("NaN + 1.0 = %f\n",nan + 1.0);
    printf("NaN + NaN = %f\n",nan + nan);

    /* some comparisons */

    printf("NaN == NaN = %s\n",nan == nan ? "true" : "false");
    printf("0.0 == -0.0 = %s\n",0.0 == minus_zero ? "true" : "false");

    return 0;
}
