// TEST: fma_fmax_fmin_return_type
// DESCRIPTION: fma/fmax/fmin must return double not int/garbage
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
#include <math.h>

int main(void) {
    int ok = 1;
    double r;

    r = fma(2.0, 3.0, 1.0);
    if (r < 6.9 || r > 7.1) { printf("FAIL: fma(2,3,1)=%g expected 7.0\n", r); ok=0; }

    r = fmax(2.0, 3.0);
    if (r < 2.9 || r > 3.1) { printf("FAIL: fmax(2,3)=%g expected 3.0\n", r); ok=0; }

    r = fmin(2.0, 3.0);
    if (r < 1.9 || r > 2.1) { printf("FAIL: fmin(2,3)=%g expected 2.0\n", r); ok=0; }

    r = fmax(-1.5, -2.5);
    if (r > -1.4 || r < -1.6) { printf("FAIL: fmax(-1.5,-2.5)=%g expected -1.5\n", r); ok=0; }

    if (ok) printf("ok\n");
    return ok ? 0 : 1;
}
