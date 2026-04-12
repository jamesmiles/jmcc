// TEST: rosetta_jensens_device
// DESCRIPTION: Rosetta Code - Jensen's Device (function pointer + global variable interaction)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Jensen%27s_Device#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: 5.187378

#include <stdio.h>

int i;
double sum(int *i, int lo, int hi, double (*term)()) {
    double temp = 0;
    for (*i = lo; *i <= hi; (*i)++)
        temp += term();
    return temp;
}

double term_func() { return 1.0 / i; }

int main () {
    printf("%f\n", sum(&i, 1, 100, term_func));
    return 0;
}
