// TEST: rosetta_kahan_summation
// DESCRIPTION: Rosetta Code - Kahan summation (float comparison and epsilon detection bug)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Kahan_summation#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: Epsilon     = 0.000000059605
// STDOUT: (a + b) + c = 0.999999940395
// STDOUT: Kahan sum   = 1.000000000000

#include <stdio.h>
#include <stdlib.h>

float epsilon() {
    float eps = 1.0f;
    while (1.0f + eps != 1.0f) eps /= 2.0f;
    return eps;
}

float kahanSum(float *nums, int count) {
    float sum = 0.0f;
    float c = 0.0f;
    float t, y;
    int i;
    for (i = 0; i < count; ++i) {
        y = nums[i] - c;
        t = sum + y;
        c = (t - sum) - y;
        sum = t;
    }
    return sum;
}

int main() {
    float a = 1.0f;
    float b = epsilon();
    float c = -b;
    float fa[3];

    fa[0] = a;
    fa[1] = b;
    fa[2] = c;

    printf("Epsilon     = %0.12f\n", b);
    printf("(a + b) + c = %0.12f\n", (a + b) + c);
    printf("Kahan sum   = %0.12f\n", kahanSum(fa, 3));

    return 0;
}
