// TEST: c99_math_missing_stubs
// DESCRIPTION: expm1/log1p/erf/erfc/tgamma/lgamma must return double not int/garbage
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
#include <math.h>

int main(void) {
    int ok = 1;
    double r;

    r = expm1(1.0);
    if (r < 1.71 || r > 1.72) { printf("FAIL: expm1(1)=%g expected ~1.71828\n", r); ok=0; }

    r = log1p(1.0);
    if (r < 0.693 || r > 0.694) { printf("FAIL: log1p(1)=%g expected ~0.69315\n", r); ok=0; }

    r = erf(1.0);
    if (r < 0.842 || r > 0.843) { printf("FAIL: erf(1)=%g expected ~0.84270\n", r); ok=0; }

    r = erfc(1.0);
    if (r < 0.157 || r > 0.158) { printf("FAIL: erfc(1)=%g expected ~0.15730\n", r); ok=0; }

    r = tgamma(5.0);
    if (r < 23.9 || r > 24.1) { printf("FAIL: tgamma(5)=%g expected 24.0\n", r); ok=0; }

    r = lgamma(5.0);
    if (r < 3.17 || r > 3.19) { printf("FAIL: lgamma(5)=%g expected ~3.1781\n", r); ok=0; }

    if (ok) printf("ok\n");
    return ok ? 0 : 1;
}
