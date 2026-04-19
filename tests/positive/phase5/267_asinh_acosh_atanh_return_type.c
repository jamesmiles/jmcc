// TEST: asinh_acosh_atanh_return_type
// DESCRIPTION: asinh/acosh/atanh must return double not int
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
#include <math.h>

int main(void) {
    int ok = 1;
    double r1 = asinh(1.0);
    double r2 = acosh(2.0);
    double r3 = atanh(0.5);
    double r4 = sinh(1.0);
    double r5 = cosh(1.0);
    double r6 = tanh(1.0);
    /* asinh(1)≈0.8814, acosh(2)≈1.3170, atanh(0.5)≈0.5493 */
    if (r1 < 0.881 || r1 > 0.882) { printf("FAIL: asinh(1)=%g expected ~0.8814\n", r1); ok=0; }
    if (r2 < 1.316 || r2 > 1.318) { printf("FAIL: acosh(2)=%g expected ~1.3170\n", r2); ok=0; }
    if (r3 < 0.549 || r3 > 0.550) { printf("FAIL: atanh(0.5)=%g expected ~0.5493\n", r3); ok=0; }
    if (r4 < 1.175 || r4 > 1.176) { printf("FAIL: sinh(1)=%g expected ~1.1752\n", r4); ok=0; }
    if (r5 < 1.543 || r5 > 1.544) { printf("FAIL: cosh(1)=%g expected ~1.5431\n", r5); ok=0; }
    if (r6 < 0.761 || r6 > 0.762) { printf("FAIL: tanh(1)=%g expected ~0.7616\n", r6); ok=0; }
    if (ok) printf("ok\n");
    return ok ? 0 : 1;
}
