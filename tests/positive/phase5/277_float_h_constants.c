/* float.h and math.h constants must be defined: HUGE_VAL, DBL_MANT_DIG,
   FLT_MANT_DIG, DBL_MAX_EXP etc. Missing from jmcc stubs; blocks lmathlib.c
   (Lua) and lstrlib.c. */
#include <stdio.h>
#include <float.h>
#include <math.h>

int main(void) {
    /* float.h constants */
    if (DBL_MANT_DIG != 53) return 1;
    if (FLT_MANT_DIG != 24) return 2;
    if (DBL_MAX_EXP != 1024) return 3;
    if (FLT_MAX_EXP != 128) return 4;
    if (DBL_MIN_EXP != -1021) return 5;

    /* math.h: HUGE_VAL must be +infinity */
    if (!isinf(HUGE_VAL)) return 6;
    if (HUGE_VAL <= 0) return 7;
    if (!isinf(HUGE_VALF)) return 8;

    printf("OK\n");
    return 0;
}
