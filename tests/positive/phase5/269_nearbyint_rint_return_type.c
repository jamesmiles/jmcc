// TEST: nearbyint_rint_return_type
// DESCRIPTION: nearbyint/rint must return double not int (missing from jmcc math stubs)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
#include <math.h>

int main(void) {
    int ok = 1;
    double r1 = nearbyint(1.5);   /* should be 2.0 (round half to even) */
    double r2 = nearbyint(2.5);   /* should be 2.0 (round half to even) */
    double r3 = nearbyint(-1.7);  /* should be -2.0 */
    double r4 = rint(1.9);        /* should be 2.0 */
    double r5 = rint(-0.3);       /* should be 0.0 */
    if (r1 < 1.9 || r1 > 2.1) { printf("FAIL: nearbyint(1.5)=%g expected 2.0\n", r1); ok=0; }
    if (r2 < 1.9 || r2 > 2.1) { printf("FAIL: nearbyint(2.5)=%g expected 2.0\n", r2); ok=0; }
    if (r3 > -1.9 || r3 < -2.1) { printf("FAIL: nearbyint(-1.7)=%g expected -2.0\n", r3); ok=0; }
    if (r4 < 1.9 || r4 > 2.1) { printf("FAIL: rint(1.9)=%g expected 2.0\n", r4); ok=0; }
    if (r5 < -0.1 || r5 > 0.1) { printf("FAIL: rint(-0.3)=%g expected 0.0\n", r5); ok=0; }
    if (ok) printf("ok\n");
    return ok ? 0 : 1;
}
