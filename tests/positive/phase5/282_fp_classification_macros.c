// TEST: fp_classification_macros
// DESCRIPTION: FP_ZERO, FP_INFINITE, FP_NAN, FP_NORMAL, FP_SUBNORMAL from math.h must be defined
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <math.h>

int main(void) {
    if (fpclassify(0.0) != FP_ZERO) return 1;
    if (fpclassify(1.0/0.0) != FP_INFINITE) return 2;
    if (fpclassify(0.0/0.0) != FP_NAN) return 3;
    if (fpclassify(1.0) != FP_NORMAL) return 4;
    printf("OK\n");
    return 0;
}
