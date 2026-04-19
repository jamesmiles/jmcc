// TEST: float_h_dbl_max
// DESCRIPTION: DBL_MAX_10_EXP, FLT_MAX_10_EXP, DBL_DIG, FLT_DIG must be defined in float.h
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <float.h>
int main(void) {
    if (DBL_MAX_10_EXP != 308) return 1;
    if (FLT_MAX_10_EXP != 38) return 2;
    if (DBL_DIG != 15) return 3;
    if (FLT_DIG != 6) return 4;
    printf("OK\n");
    return 0;
}
