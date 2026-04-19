// TEST: log10_log2_return_type
// DESCRIPTION: log10() and log2() return double; jmcc was treating return as int (cvtsi2sd %eax)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
#include <math.h>

/* Bug: jmcc knows log() returns double (uses xmm0), but treats log10()/log2()
   as returning int (unknown function default), so after 'call log10' it does
   cvtsi2sd %eax,xmm0 instead of using the double result already in xmm0. */

int main(void) {
    if (log10(100.0) != 2.0) {
        printf("FAIL: log10(100)=%g expected 2.0\n", log10(100.0));
        return 1;
    }
    if (log10(1.0) != 0.0) {
        printf("FAIL: log10(1)=%g expected 0.0\n", log10(1.0));
        return 1;
    }
    double v = log10(1e6);
    if (v != 6.0) {
        printf("FAIL: log10(1e6)=%g expected 6.0\n", v);
        return 1;
    }
    if (log2(8.0) != 3.0) {
        printf("FAIL: log2(8)=%g expected 3.0\n", log2(8.0));
        return 1;
    }
    if (log2(1.0) != 0.0) {
        printf("FAIL: log2(1)=%g expected 0.0\n", log2(1.0));
        return 1;
    }
    printf("ok\n");
    return 0;
}
